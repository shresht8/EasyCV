# Use the official Python 3.10 image as the base image
FROM python:3.10.13

# Set the working directory within the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install Python packages from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python application code into the container
COPY . /app

# Set the command to run your Python application
ENTRYPOINT ["python", "bot_create_cv.py"]
