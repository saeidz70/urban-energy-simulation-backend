# Use an official Python image as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy and install dependencies first (leveraging caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the configuration file
COPY config/configuration.json /config/configuration.json

# Copy the rest of the application
COPY . .

# Expose the port that the application listens on
EXPOSE 8080

# Set environment variable for configuration
ENV CONFIG_PATH=/config/configuration.json

# Specify the command to run the application
CMD ["python", "webservice.py"]
