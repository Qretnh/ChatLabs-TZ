FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install wheel && \
    pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
