# ────────🔧 Base Builder Stage ────────
FROM python:3.12-slim AS builder


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    build-essential \
    default-libmysqlclient-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /usr/src/app


COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ────────📦 Final Runtime Stage ────────
FROM python:3.12-slim AS final


RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*





COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin


COPY ./api .
COPY .env .


EXPOSE 5000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]