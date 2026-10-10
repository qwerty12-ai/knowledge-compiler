ARG PYTHON_VERSION=3.14.4

FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=backend/requirements.txt,target=/tmp/requirements.txt \
    /opt/venv/bin/python -m pip install -r /tmp/requirements.txt

COPY compiler/ /tmp/compiler/

RUN --mount=type=cache,target=/root/.cache/pip \
    /opt/venv/bin/python -m pip install /tmp/compiler

FROM base AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/* \
    && adduser \
        --disabled-password \
        --gecos "" \
        --home /home/appuser \
        --uid 10001 \
        appuser

COPY --from=builder /opt/venv /opt/venv

COPY --chown=appuser:appuser backend/ /app/backend/

USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]