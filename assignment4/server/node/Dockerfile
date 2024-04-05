# Using python 3.12 as base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /server/

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /server/

# Create a non-root user
RUN useradd -m nonrootuser
USER nonrootuser

# Run main.py when the container launches
CMD ["python3", "./main.py"]