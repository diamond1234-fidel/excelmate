FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install flask pandas numpy

# Copy app
COPY app.py /app/app.py

EXPOSE 5000

CMD ["python", "app.py"]
