# Use the official Python image from DockerHub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV DISPLAY=:99

# Install dependencies
RUN apt-get update && apt-get install -y \
  wget \
  ca-certificates \
  curl \
  unzip \
  && apt-get install -y \
  libgconf-2-4 \
  libnss3 \
  libx11-xcb1 \
  libxtst6 \
  libxss1 \
  libappindicator3-1 \
  libasound2 \
  libatk-bridge2.0-0 \
  libgtk-3-0 \
  libdbus-glib-1-2 \
  libgdk-pixbuf2.0-0 \
  libgbm1 \
  libnss3-dev \
  libnspr4 \
  xdg-utils \
  && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get -y --fix-broken install

# Set Google Chrome binary location
ENV CHROME_BIN=/usr/bin/google-chrome-stable

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
