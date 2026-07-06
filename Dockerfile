FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY examples ./examples
COPY scripts ./scripts
COPY tests ./tests

RUN python -m pip install --upgrade pip \
    && python -m pip install ".[dev]"

CMD ["speculative-bench", "run", "--out", "reports"]
