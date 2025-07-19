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
RUN pip install torch transformers datasets peft accelerate bitsandbytes sentencepiece s3fs boto3

WORKDIR /app

# Copy script
COPY fine_tune.py /app/fine_tune.py

# Run the fine-tuning script
CMD ["python", "fine_tune.py"]
