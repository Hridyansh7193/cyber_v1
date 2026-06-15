FROM bughunter-base:latest

# Install API utilities
RUN pip3 install --break-system-packages inql

# Install graphql-cop
RUN git clone https://github.com/dolevf/graphql-cop.git /opt/graphql-cop && \
    cd /opt/graphql-cop && \
    pip3 install --break-system-packages -r requirements.txt && \
    chmod +x graphql-cop.py && \
    ln -s /opt/graphql-cop/graphql-cop.py /usr/local/bin/graphql-cop

CMD ["/bin/bash"]
