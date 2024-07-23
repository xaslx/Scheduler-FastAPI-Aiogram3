FROM python:3.12.3

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /code

COPY ./pyproject.toml ./poetry.lock* /code/

RUN poetry install --no-root

COPY ./app /code/app

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
