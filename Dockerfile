FROM python:3-slim

WORKDIR /app

# Copy requirements first (so pip install can be cached)
COPY requirements.txt .

# Python library requirements
RUN pip install --no-cache-dir -r requirements.txt

# Bricktracker
COPY . .

# Set executable permissions for entrypoint script
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
