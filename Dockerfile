FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RECIPE_DATA_DIR=/tmp/local_data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN BACKGROUND_RECIPE_DATA_DOWNLOAD=False SECRET_KEY=build-only python manage.py collectstatic --noinput

CMD ["sh", "scripts/cloudrun_start.sh"]
