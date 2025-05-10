FROM python:3.13-bookworm@sha256:b7ce60fbc565933c5ae088df8dbe63ffad16a634d4c575ec989e2f106f7df674 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.7.2@sha256:3b898ca84fbe7628c5adcd836c1de78a0f1ded68344d019af8478d4358417399 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq-dev gcc python3-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm@sha256:914bf5c12ea40a97a78b2bff97fbdb766cc36ec903bfb4358faf2b74d73b555b

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq5 ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# renovate: datasource=github-releases depName=amacneil/dbmate versioning=semver
ENV DBMATE_VERSION=v2.27.0

ADD --chmod=755 https://github.com/amacneil/dbmate/releases/download/${DBMATE_VERSION}/dbmate-linux-amd64 /bin/dbmate

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

ENV ENABLE_OPENAPI=false DATA_DIR=/data
CMD [ "fastapi", "run", "--host", "0.0.0.0", "/app/src/tso_api/main.py" ]
