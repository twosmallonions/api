FROM python:3.13-bookworm@sha256:5d0a64b7f8333d42568ae4076242d15dc22f0cb0ae26a1750cbb8a6570e48aa5 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.7.13@sha256:6c1e19020ec221986a210027040044a5df8de762eb36d5240e382bc41d7a9043 /uv /uvx /bin/
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

FROM python:3.13-slim-bookworm@sha256:f2fdaec50160418e0c2867ba3e254755edd067171725886d5d303fd7057bbf81

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
CMD [ "fastapi", "run", "--host", "0.0.0.0", "--workers", "4", "/app/src/tso_api/main.py" ]
