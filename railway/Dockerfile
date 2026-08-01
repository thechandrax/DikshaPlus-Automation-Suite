# Official Playwright Python image with Chromium pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Copy dependency requirements
COPY requirements.txt .

# Install dependencies & ensure Playwright Chromium binary is ready
RUN pip install --no-cache-dir -r requirements.txt && playwright install chromium

# Copy project source files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=True

# Default command to run non-interactive automation
CMD ["python", "main.py"]
