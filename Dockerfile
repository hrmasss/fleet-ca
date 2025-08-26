FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
  apt-get install -y --no-install-recommends build-essential libpq-dev curl && \
  rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi

RUN pip install --no-cache-dir gunicorn

COPY . .

ENV SECRET_KEY=build-time-secret-key \
  DEBUG=True \
  ALLOWED_HOSTS=* \
  DATABASE_URL=sqlite:///tmp/build.db

RUN python manage.py collectstatic --noinput

RUN useradd -m -u 1000 app && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"]