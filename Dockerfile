FROM ghcr.io/astral-sh/uv:0.8-python3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	ROOT_DIR=/app

WORKDIR /app

RUN useradd -u 10001 -m appuser \
&& chown -R 10001:10001 /app
USER 10001

COPY --chown=10001:10001 pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY --chown=10001:10001 src ./src

RUN uv sync --frozen

EXPOSE 8081

CMD ["uv", "run", "python", "-m", "rotoreader.app"]
