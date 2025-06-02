FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./
COPY LICENSE README.md ./

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY rp_handler.py ./
COPY dia/ ./dia/

# Copy documentation files last since they change less frequently

CMD ["python3", "-u", "rp_handler.py"] 