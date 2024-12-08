FROM python:3.12-slim

WORKDIR /FinPulseR

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "fastapi:app", "--host", "0.0.0.0", "--port", "8000"]