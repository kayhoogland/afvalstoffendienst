FROM python:3.10-slim as requirements-stage

WORKDIR /tmp

RUN pip install --upgrade pip && pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.10-slim

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .


CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]
