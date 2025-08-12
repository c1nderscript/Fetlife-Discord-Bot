# syntax=docker/dockerfile:1
FROM python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee AS builder

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee

WORKDIR /app
ENV PATH="/venv/bin:$PATH"

COPY --from=builder /venv /venv
COPY bot/ bot/
RUN rm -rf bot/tests

EXPOSE 8000
CMD ["python", "-m", "bot.main"]
