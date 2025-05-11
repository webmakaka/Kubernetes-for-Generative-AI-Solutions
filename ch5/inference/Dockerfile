FROM nvidia/cuda:12.8.1-runtime-ubuntu24.04

# Environment config
ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python and necessary dependencies
RUN apt-get update && apt-get install -y python3.12 python3.12-venv python3-pip && rm -rf /var/lib/apt/lists/*

# Set Python3 as default
RUN python3.12 -m venv $VIRTUAL_ENV && $VIRTUAL_ENV/bin/pip install --upgrade pip

# Install necessary packages
RUN pip install torch transformers peft accelerate bitsandbytes sentencepiece fastapi uvicorn

WORKDIR /app

# Expose port for the FastAPI app
EXPOSE 80

# Copy model files and FastAPI app to the container
COPY model-assets/ /app/model-assets
COPY main.py /app/main.py

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
