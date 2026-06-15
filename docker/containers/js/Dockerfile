FROM bughunter-base:latest

# Install JS analysis tools
# LinkFinder
RUN git clone https://github.com/GerbenJavado/LinkFinder.git /opt/LinkFinder && \
    cd /opt/LinkFinder && \
    pip3 install -r requirements.txt --break-system-packages

# SecretFinder
RUN git clone https://github.com/m4ll0k/SecretFinder.git /opt/SecretFinder && \
    cd /opt/SecretFinder && \
    pip3 install -r requirements.txt --break-system-packages

# Trufflehog (v3)
RUN curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

ENV PATH=$PATH:/usr/local/bin

CMD ["/bin/bash"]
