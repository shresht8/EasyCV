# Use the smaller TeXLive image
FROM texlive/texlive:latest-small

# Set a working directory within the container
WORKDIR /app

# Install necessary tools
RUN apt-get update && \
    apt-get install -y inotify-tools apt-transport-https ca-certificates gnupg curl sudo && \
    rm -rf /var/lib/apt/lists/*

# Add the Cloud SDK distribution URI as a package source. For Local clusters ONLY
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key. For Local clusters ONLY
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

RUN apt-get update

# Update and install the Cloud SDK. For Local clusters ONLY
RUN apt-get install -y google-cloud-cli

# Copy required_packages.txt into the container
COPY required_packages.txt /app/

# Install LaTeX packages from required_packages.txt
RUN tlmgr update --self && \
    cat required_packages.txt | while read package; do \
        tlmgr install $package || echo "Failed to install package: $package"; \
    done && \
    tlmgr path add

# Copy the entrypoint script into the container
COPY entrypoint_final.sh /app/

# Ensure the script is executable
RUN chmod +x /app/entrypoint_final.sh

# This command will execute the entrypoint script
CMD ["/app/entrypoint_final.sh"]