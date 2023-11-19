# Use the base LaTeX image
FROM blang/latex:ubuntu

# Set a working directory within the container
WORKDIR /app

# Install inotify-tools for monitoring file changes
RUN apt-get update && \
    apt-get install -y inotify-tools && \
    rm -rf /var/lib/apt/lists/*

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/

# Ensure the script is executable
RUN chmod +x /app/entrypoint.sh

# This command will execute the entrypoint script
CMD ["/app/entrypoint.sh"]
