FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install pandas numpy

# Copy worker code
COPY worker.py /app/worker.py

CMD ["python", "worker.py"]
