FROM python:3.13.7-alpine3.22

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache \
  build-base \
  postgresql-dev \
  curl

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

COPY . .

ENV SECRET_KEY=build-time-secret-key \
  DEBUG=False \
  ALLOWED_HOSTS=* \
  DATABASE_URL=sqlite:///tmp/build.db

RUN python manage.py collectstatic --noinput

RUN adduser -D -u 1000 app && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"]