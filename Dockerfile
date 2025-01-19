FROM python:3-slim

WORKDIR /app

# Bricktracker
COPY . .

# Python library requirements
RUN pip --no-cache-dir install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]
