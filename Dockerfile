FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Default command: run tests with coverage
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=scripts", "--cov-report=term-missing", "--cov-fail-under=90"]
