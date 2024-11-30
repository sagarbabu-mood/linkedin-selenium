# Use the official Python image from DockerHub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV DISPLAY=:99

# Install dependencies
RUN apt-get update \
    && apt-get install -y \
    wget \
    curl \
    unzip \
    ca-certificates \
    gnupg \
    libx11-dev \
    libx11-6 \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libgbm-dev \
    libasound2 \
    libnspr4 \
    libxtst6 \
    libnss3 \
    libxrandr2 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libatk1.0-0 \
    libpango-1.0-0 \
    libgtk-3-0 \
    --no-install-recommends \
    && apt-get clean

# Install Chrome
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && apt-get -y install -f

# Verify the Chrome installation
RUN google-chrome-stable --version

# Install necessary Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the Flask app code into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Expose port 5000 (default Flask port)
EXPOSE 5000

# Start the Flask app
CMD ["python", "back.py"]
