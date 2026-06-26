# Stage 1: Builder (Golang tools)
FROM golang:1.21-alpine AS builder

RUN apk add --no-cache git build-base

# Install core tools
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
RUN go install -v github.com/projectdiscovery/katana/cmd/katana@latest
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Stage 2: Minimal Production (Core only)
FROM python:3.11-slim AS minimal

WORKDIR /app
COPY --from=builder /go/bin/subfinder /usr/local/bin/
COPY --from=builder /go/bin/httpx /usr/local/bin/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENTRYPOINT ["python", "main.py"]

# Stage 3: Full Production (All plugins)
FROM python:3.11-slim AS full

WORKDIR /app
COPY --from=builder /go/bin/* /usr/local/bin/

RUN apt-get update && apt-get install -y git jq curl nmap wget && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENTRYPOINT ["python", "main.py"]
