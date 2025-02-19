FROM selenium/standalone-chrome:latest

USER root
WORKDIR /app

# Install Python and venv
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set Chrome options
ENV CHROME_OPTIONS="--no-sandbox --headless --disable-dev-shm-usage --disable-gpu --user-data-dir=/tmp/chrome-data"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.senate_scraper"]