# Use Python 3.12 to match the requirements
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /piston

# Install poetry
RUN pip install uv

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN uv pip sync pyproject.toml --system

# Copy the rest of the application code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Command to run the application when the container launches
CMD ["uv", "run", "python", "main.py"]
