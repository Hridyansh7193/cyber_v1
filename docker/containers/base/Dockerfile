FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV GOPATH=/root/go
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    wget \
    git \
    golang-go && \
    rm -rf /var/lib/apt/lists/*

# Set up shared workspace directory
WORKDIR /data
