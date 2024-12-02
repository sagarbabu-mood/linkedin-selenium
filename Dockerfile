# Set the port for the application
ARG PORT=443

# Use the Selenium standalone Chrome image as the base
FROM selenium/standalone-chrome:latest

# Switch to root user (this ensures the install commands work)
USER root

# Install necessary dependencies (python3, python3-venv, python3-pip, wget, unzip)
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip wget unzip

# Create and activate a virtual environment
RUN python3 -m venv /env

# Install pip inside the virtual environment
RUN /env/bin/pip install --upgrade pip

# Copy the requirements.txt and install Python packages in the virtual environment
COPY requirements.txt . 
RUN /env/bin/pip install -r requirements.txt

# Set environment variables to use the virtual environment's python and pip
ENV PATH="/env/bin:$PATH"

# Copy the rest of your app
COPY . .

# Download and unzip ChromeDriver into /usr/local/bin (where system-wide executables are stored)
RUN wget -O /chromedriver_linux64.zip https://raw.githubusercontent.com/your-username/your-repository/main/drivers/chromedriver_linux64.zip \
    && unzip /chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm /chromedriver_linux64.zip  # Remove the ZIP file after extracting

# Ensure the chromedriver binary is executable
RUN chmod +x /usr/local/bin/chromedriver

# Expose the port the application runs on
EXPOSE ${PORT}

# Run the Flask app with Gunicorn on the specified port
CMD gunicorn -b 0.0.0.0:${PORT:-5000} back:app
