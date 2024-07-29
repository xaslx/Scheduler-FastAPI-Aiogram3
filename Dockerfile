FROM python:3.12 as python-base

ENV POETRY_VERSION=1.8.2

ENV POETRY_HOME=/opt/poetry

ENV POETRY_VENV=/opt/poetry-venv

ENV POETRY_CACHE_DIR=/opt/.cache

FROM python-base as poetry-base

RUN python3 -m venv $POETRY_VENV \

&& $POETRY_VENV/bin/pip install -U pip setuptools \

&& $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

FROM python-base as example-app

COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /scheduler

COPY poetry.lock pyproject.toml /scheduler/

RUN poetry install --no-interaction --no-cache

COPY . .

CMD poetry run gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000