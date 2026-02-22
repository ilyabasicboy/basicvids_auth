FROM python:3.10.12-slim

WORKDIR /basicvids_auth

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy project
COPY . .
COPY start.sh .
RUN chmod +x start.sh

# Expose port 
EXPOSE 8000

# Run server
CMD ["./start.sh"]