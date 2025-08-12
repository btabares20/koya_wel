# Use a small Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Run your script
CMD ["python", "bot.py"]
