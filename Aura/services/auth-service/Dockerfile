# Build stage
FROM python:3.10-slim as builder

WORKDIR /app

# Install poetry
RUN pip install poetry==1.5.1

# Copy project files
COPY pyproject.toml .
COPY ../../libs/common /libs/common

# Configure poetry to not use virtualenvs
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Runtime stage
FROM python:3.10-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8007

# Expose the application port
EXPOSE 8007

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"] 