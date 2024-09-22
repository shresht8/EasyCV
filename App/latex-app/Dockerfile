# Stage 1: Python base image
FROM python:3.10-slim AS python-base

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM texlive/texlive:latest-small

# Set working directory
WORKDIR /app

# Install necessary tools
RUN apt-get update && \
    apt-get install -y apt-transport-https ca-certificates gnupg curl sudo && \
    rm -rf /var/lib/apt/lists/*

# Add the Cloud SDK distribution URI as a package source
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

# Update and install the Cloud SDK
RUN apt-get update && \
    apt-get install -y google-cloud-cli && \
    rm -rf /var/lib/apt/lists/*

# Copy Python from python-base stage
COPY --from=python-base /usr/local /usr/local

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/local/bin:$PATH"

# Copy required_packages.txt into the container
COPY required_packages.txt /app/

# Install LaTeX packages from required_packages.txt
RUN tlmgr update --self && \
    cat required_packages.txt | while read package; do \
        tlmgr install $package || echo "Failed to install package: $package"; \
    done && \
    tlmgr path add

# Copy the FastAPI application into the container
COPY latex_compiler_service.py /app/

# Expose the port the app runs on
EXPOSE 5000

# Expose the port the app runs on
EXPOSE 5000

# Set the command to run your FastAPI application using uvicorn
CMD ["uvicorn", "latex_compiler_service:app", "--host", "0.0.0.0", "--port", "5000"]