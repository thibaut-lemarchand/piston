# Use Python 3.12 to match the requirements
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /piston

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application when the container launches
CMD ["python", "main.py"]