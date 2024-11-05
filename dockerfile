# Use Python 3.12 to match the requirements
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /piston

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create a virtual environment in the container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application when the container launches
CMD ["python", "main.py"]