# this preapares the app by installing uv and compiling
FROM python:3.14-slim AS builder

WORKDIR /app

# install uv from astral(creators of uv) instead of pip which is slow plus its distroless /uv source path and /bin/uv destiation path
# contains no os shell, python making it small and secure
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# compile evry .py file to pyc(this are only uv installed pacakegs fastapi, cors) bytecode thus in production you dont have to compile again and again when cold starting
# uv to copy files instead of hard-linking them. When using Docker cache mounts, the cache and the target directory live on separate filesystems, so uv falls back to copying anyway. 
# Setting this explicitly avoids the warning message.
# if you not using docker cache mounts we set uv_no_cache as uv will try to install into its internal cache verytime so we clear them
# UV_NO_CACHE=1

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_PREFERENCE=only-system


COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

# run-time
FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY . .

# use the libraries inisde our .venv box
# print all messages 
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]