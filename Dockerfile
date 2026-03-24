FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && pip install .

# Expose the HTTP port
EXPOSE 8000
ENV PORT=8000

# Start server in streamable-http mode (shell form to expand $PORT)
CMD freshdesk-mcp --transport streamable-http --port ${PORT:-8000}
