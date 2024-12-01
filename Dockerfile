ARG PORT=443
FROM selenium/standalone-chrome:latest

# Switch to root user (this ensures the install commands work)
USER root

# Install python3
RUN apt-get update && apt-get install python3 -y

# Verify python3 installation
RUN echo $(python3 -m site --user-base)

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN apt-get install -y python3-pip && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of your app
COPY . .

# Run your app
CMD uvicorn back:app --host 0.0.0.0 --port ${PORT}
