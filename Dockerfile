# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for database drivers)
# RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . .

# Expose the port Django will run on
EXPOSE 8000

# Define the command to run the Django development server
# In a production environment, you would use a WSGI server like Gunicorn
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]