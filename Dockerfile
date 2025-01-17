FROM python:slim

WORKDIR /app

# Python library requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Bricktracker
COPY . .

ENTRYPOINT ["entrypoint.sh"]
