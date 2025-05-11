FROM nvidia/cuda:12.6.3-runtime-ubuntu24.04

# Install Python and necessary dependencies
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*

# Set Python3 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Install necessary packages
RUN pip install torch transformers accelerate sentencepiece fastapi uvicorn

WORKDIR /app

# Expose port for the FastAPI app
EXPOSE 80

# Copy model files and FastAPI app to the container
COPY main2.py /app/main.py

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
