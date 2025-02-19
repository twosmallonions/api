FROM python:3.13-bookworm@sha256:2e9b5da7a9c053568b33a47e3dc99798b4b9cc7b763be4e35f452262bd57703a AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6.1@sha256:90daa0b4d74ea55c7b8e06d25d3826b1eac66e7994387248e6173dd2b66668e2 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq-dev gcc python3-dev \
  && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /bin/dbmate https://github.com/amacneil/dbmate/releases/download/v2.25.0/dbmate-linux-amd64 \
  && chmod +x /bin/dbmate

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm@sha256:ae9f9ac89467077ed1efefb6d9042132d28134ba201b2820227d46c9effd3174

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq5 ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# renovate: datasource=github-releases depName=amacneil/dbmate versioning=semver
ENV DBMATE_VERSION=v2.24.2

ADD --chmod=755 https://github.com/amacneil/dbmate/releases/download/${DBMATE_VERSION}}/dbmate-linux-amd64 /bin/dbmate

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
CMD [ "fastapi", "run", "--host", "0.0.0.0", "/app/src/tso_api/main.py" ]
