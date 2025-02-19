FROM python:3.13-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6.1 /uv /uvx /bin/
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

FROM python:3.13-slim-bookworm

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
