FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && pip install .

# Default HTTP port for Railway or local streamable-http runs
EXPOSE 8000

# Runtime transport is selected by the application based on PORT/MCP_TRANSPORT.
CMD ["freshdesk-mcp"]
