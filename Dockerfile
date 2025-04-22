FROM --platform=linux/arm64 python:3.11.0-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    net-tools \
    tcpdump \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy only necessary source files
COPY src/ src/
COPY entrypoint.sh .

# Final stage
FROM --platform=linux/arm64 python:3.11.0-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    net-tools \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/src/ /app/src/
COPY --from=builder /app/entrypoint.sh /app/

# Make entrypoint.sh executable
RUN chmod +x /app/entrypoint.sh

# Set up Python path
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8000
EXPOSE 8080

CMD ["./entrypoint.sh"]
