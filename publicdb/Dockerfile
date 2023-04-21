FROM python:3.11-slim-buster

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

COPY . .