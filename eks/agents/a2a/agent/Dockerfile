ARG RUNTAG=latest
FROM cgr.dev/chainguard/python:latest-dev AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Prefer the system python
ENV UV_PYTHON_PREFERENCE=only-system

# Run without updating the uv.lock file like running with `--frozen`
ENV UV_FROZEN=true

# Copy the required files first
COPY pyproject.toml uv.lock ./

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-editable

FROM cgr.dev/chainguard/python:${RUNTAG}

# Project got copied to here
WORKDIR /app

# Place executables in the environment at the front of the path and include other binaries
ENV PATH="/app/.venv/bin:$PATH"

# Get the project from the uv layer
COPY --from=uv  /app/.venv .venv
