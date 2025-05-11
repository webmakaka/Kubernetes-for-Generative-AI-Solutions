# Use an official Python runtime as a parent image
FROM python:slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Gradio runs on
EXPOSE 7860

COPY gradio-app.py /app

ENTRYPOINT ["python", "gradio-app.py"]
