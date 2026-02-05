# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask pandas numpy

# Copy your Flask app
COPY app.py /app/app.py

# Expose the default Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
