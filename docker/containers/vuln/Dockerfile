FROM bughunter-base:latest

# Install vulnerability scanners
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install -v github.com/hahwul/dalfox/v2@latest && \
    go install -v github.com/ffuf/ffuf/v2@latest && \
    go install -v github.com/PentestPad/subzy@latest

ENV PATH=$PATH:/root/go/bin

CMD ["/bin/bash"]
