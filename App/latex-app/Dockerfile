# Use the base LaTeX image
FROM blang/latex:ubuntu

# Set a working directory within the container
WORKDIR /app

# Install inotify-tools for monitoring file changes
RUN apt-get update && \
    apt-get install -y inotify-tools apt-transport-https ca-certificates gnupg curl sudo && \
    rm -rf /var/lib/apt/lists/*

# Add the Cloud SDK distribution URI as a package source
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

# Update and install the Cloud SDK
RUN apt-get update && apt-get install -y google-cloud-cli

# Copy the entrypoint script into the container
COPY entrypoint_final_v2.sh upload_script.py /app/

# Ensure the script is executable
RUN chmod +x /app/entrypoint_final_v2.sh

# This command will execute the entrypoint script
CMD ["/app/entrypoint_final_v2.sh"]
