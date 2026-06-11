FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || \
    pip install --no-cache-dir paho-mqtt


COPY . .


RUN mkdir -p /app/data/buffer


CMD ["python", "main.py"]