# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
# Python output is set directly to the terminal without buffering:
ENV PYTHONUNBUFFERED 1

# do I need to create root directory for the project in the container?
# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/
COPY aws_hosted_pms/.env /app/


# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
