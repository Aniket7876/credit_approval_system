# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the project files
COPY . .

# Run Django development server (adjust this if you use `gunicorn` in production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
