FROM python:3.9-slim

# Set environment variables to prevent writing .pyc files and buffer
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Create a non-root user and group for security
RUN groupadd -r python && useradd -r -g python python

# Copy the requirements file to install dependencies
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Change ownership of files to non-root user
RUN chown -R python:python /app

# Switch to non-root user
USER python

# Expose the port the app runs on
EXPOSE 5000

# Command to run the app
CMD ["python", "main.py"]
