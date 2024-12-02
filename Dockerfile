ARG PORT=443
FROM selenium/standalone-chrome:latest

# Switch to root user (this ensures the install commands work)
USER root

# Install python3 and python3-venv (needed to create a virtual environment)
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip

# Create and activate a virtual environment
RUN python3 -m venv /env

# Install pip inside the virtual environment
RUN /env/bin/pip install --upgrade pip

# Copy requirements.txt and install Python packages in the virtual environment
COPY requirements.txt .
RUN /env/bin/pip install -r requirements.txt

# Copy the rest of your app
COPY . .

RUN chmod +x chromedriver.exe


# Ensure the correct python and pip are used
ENV PATH="/env/bin:$PATH"

# Run the Flask app with Gunicorn on the specified port
CMD gunicorn -b 0.0.0.0:${PORT:-5000} back:app
