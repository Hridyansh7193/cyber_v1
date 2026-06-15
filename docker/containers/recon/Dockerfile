FROM bughunter-base:latest

# Install recon tools using go install
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/tomnomnom/assetfinder@latest && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install -v github.com/lc/gau/v2/cmd/gau@latest

# Run as non-root user for execution (if needed, but kept default per instructions, assuming runner will map user)
# We just ensure binaries are in path
ENV PATH=$PATH:/root/go/bin

CMD ["/bin/bash"]
