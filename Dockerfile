FROM python:3-slim

WORKDIR /app

# Bricktracker
COPY . .

# Fix line endings and set executable permissions for entrypoint script
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

# Python library requirements
RUN pip --no-cache-dir install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]
