# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-editable

FROM cgr.dev/chainguard/python:latest

# Place executables in the environment at the front of the path and include other binaries
ENV PATH="/app/.venv/bin:$PATH:/usr/sbin"

# Get the project from the uv layer
COPY --from=uv --chown=nonroot:nonroot /app/.venv /app/.venv

# Copy configuration files needed at runtime
COPY --from=uv --chown=nonroot:nonroot /app/agent.md    /app/agent.md
COPY --from=uv --chown=nonroot:nonroot /app/mcp-servers /app/mcp-servers

# Project got copied to here
WORKDIR /app

# Run as non-root
USER nonroot

# Expose ports for MCP (8080), A2A (9000), and FastAPI (3000)
EXPOSE 8080 9000 3000

ENTRYPOINT [ "agent" ]
