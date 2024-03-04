# Use the base LaTeX image
FROM blang/latex:ubuntu

# Set a working directory within the container
WORKDIR /app

# Install inotify-tools for monitoring file changes
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

# Copy the entrypoint script into the container
COPY entrypoint_final.sh /app/

# Ensure the script is executable
RUN chmod +x /app/entrypoint_final.sh

# This command will execute the entrypoint script
CMD ["/app/entrypoint_final.sh"]
