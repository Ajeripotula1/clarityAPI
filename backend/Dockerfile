# Clarity API — build from backend/:  docker build -t clarity-api .
FROM python:3.12-slim-bookworm

WORKDIR /app

# System deps for psycopg, PDF parsing, and common wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
