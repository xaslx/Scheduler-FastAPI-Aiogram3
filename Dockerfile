FROM python:3.12

WORKDIR /scheduler

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN alembic upgrade head

CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]

RUN celery --app=app.tasks.celery_app:celery worker -l INFO