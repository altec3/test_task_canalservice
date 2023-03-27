FROM python:3.10-slim as base_image

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.4.1

WORKDIR /tmp

RUN pip install "poetry==$POETRY_VERSION"

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry export -f requirements.txt -o requirements.txt && \
    rm poetry.lock pyproject.toml && \
    pip uninstall poetry -y

WORKDIR /script

# Копирование файлов проекта
COPY config/settings.py config/
COPY secrets secrets
COPY services services
COPY run.py .

FROM base_image as image

RUN pip install -r /tmp/requirements.txt
CMD ["python3", "run.py"]
