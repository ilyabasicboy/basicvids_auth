FROM python:3.10.12-slim

WORKDIR /basicvids_auth

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    less \
    nano \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy project
COPY . .
RUN chmod +x entrypoint.sh

# Expose port 
ARG APP_PORT=8000
ENV APP_PORT=${APP_PORT}
EXPOSE ${APP_PORT}