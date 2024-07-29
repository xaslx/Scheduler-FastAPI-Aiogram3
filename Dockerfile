
FROM python:3.12


RUN curl -sSL https://install.python-poetry.org | python3 -


ENV POETRY_HOME="/root/.poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"


WORKDIR /scheduler


COPY pyproject.toml poetry.lock ./


RUN poetry install --no-root


COPY . .


CMD ["poetry", "run", "gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]
