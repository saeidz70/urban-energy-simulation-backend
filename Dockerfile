# Use an official Python image as the base image
# The specified version should match your local Python (e.g., 3.12)
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pass environment variables into the container
ENV CONFIG_PATH=/config/configuration.json

# Expose the port that your web application listens on
EXPOSE 8080

# Specify the command to run your application
CMD ["python", "webservice.py"]