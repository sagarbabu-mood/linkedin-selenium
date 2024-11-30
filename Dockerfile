# Use a base image with Python
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget gnupg2 curl unzip && \
    curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome.deb && \
    apt install -y ./google-chrome.deb && \
    rm google-chrome.deb

# Install necessary dependencies for Selenium and Chrome
RUN apt-get install -y \
    libappindicator3-1 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    fonts-liberation \
    xdg-utils \
    libgbm1 \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libepoxy0 \
    lsb-release \
    x11-utils

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set display port for headless Chrome
ENV DISPLAY=:99

# Set the working directory
WORKDIR /app
COPY . /app

# Set Chrome binary and ChromeDriver path
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Install ChromeDriver
RUN wget -q https://chromedriver.storage.googleapis.com/112.0.5615.49/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin/ && \
    rm chromedriver_linux64.zip

# Run your Flask app
CMD ["gunicorn", "-b", "0.0.0.0:10000", "back:app"]
