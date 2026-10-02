FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container
COPY backend/ ./backend/

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
# We use $PORT if available (Render provides this), otherwise default to 8000
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
