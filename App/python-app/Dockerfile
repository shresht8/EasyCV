
# Use the official Python 3.10 image as the base image
FROM python:3.10.13

# Set the working directory within the container
WORKDIR /app

# Install Google Cloud SDK
# Comment below section if deploying in google cloud
#RUN apt-get update -y && \
#    apt-get install -y curl gnupg && \
#    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
#    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
#    apt-get update -y && apt-get install -y google-cloud-sdk

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install Python packages from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python application code into the container
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Set the command to run your FastAPI application using uvicorn
CMD ["uvicorn", "python_app:app", "--host", "0.0.0.0", "--port", "8000"]
