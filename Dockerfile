# Use the official Python image from the Docker Hub
FROM public.ecr.aws/docker/library/python:3.11

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install

# Expose the port the app runs on
EXPOSE 8000