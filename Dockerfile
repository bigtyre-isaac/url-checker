# Use a Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install filelock flask prometheus_client requests gunicorn

# Copy application files
COPY app /app

# Expose the default port
EXPOSE 5000
EXPOSE 8001

# Start Gunicorn server with 4 worker processes and bind to port 5000
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
CMD ["sh", "-c", "python url_checker.py & gunicorn -w 4 -b 0.0.0.0:5000 main:app"]
