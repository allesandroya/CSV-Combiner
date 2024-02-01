# Use an official Python runtime as a base image
FROM python:3.11.2

# Set the working directory inside the container
WORKDIR /app

# Install system packages required for building pandas
RUN apt-get update \
    && apt-get install -y \
        python3-dev \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app/

# Specify the command to run your application
CMD ["python", "CSV_Combiner_v4.5.py"]
