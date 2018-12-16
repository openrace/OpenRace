# Use an official Python runtime as a parent image
FROM python:3-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
COPY ./setup.py /

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN pip install -e /setup.py

# Make port 80 available to the world outside this container
# EXPOSE 80

# Run app.py when the container launches
CMD ["openrace", "--device", "/dev/ttyACM0"]
