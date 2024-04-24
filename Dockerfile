FROM node:21-bookworm as node
WORKDIR /app
COPY assets/ package.json package-lock.json /app/
RUN --mount=type=cache,target=/app/node_modules \
    npm


FROM python:3.12-bookworm

ENV POETRY_HOME=/opt/poetry \
    POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=0 \
    PIP_VERSION=24.0

RUN --mount=type=cache,target=/root/.cache \
    pip install pip==${PIP_VERSION} && \
    curl -sSL https://install.python-poetry.org | python3 -

# build venv
RUN python -m venv /venv
ENV VIRTUAL_ENV=/venv           \
    PATH="/venv/bin:$PATH"
COPY poetry.lock pyproject.toml /
RUN --mount=type=cache,target=/root/.cache \
    /opt/poetry/bin/poetry install --no-root

RUN useradd app
COPY --chown=app . /app
WORKDIR /app
RUN python -m compileall -q . && python manage.py collectstatic --noinput --no-color
USER app
