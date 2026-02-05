FROM python:3.11-slim

WORKDIR /app

# Install dependencies including flask-cors
RUN pip install --no-cache-dir flask pandas numpy flask-cors

# Copy app
COPY app.py /app/app.py

EXPOSE 5000

CMD ["python", "app.py"]
