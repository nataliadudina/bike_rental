# Базовая система
FROM python:3.11-slim

# Установить зависимости для PostgreSQL и общие инструменты сборки
RUN apt-get update && apt-get install -y \
    gcc libpq-dev build-essential

# Установка Poetry
RUN pip install poetry

# Установка зависимостей
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Копирование кода
COPY . .
