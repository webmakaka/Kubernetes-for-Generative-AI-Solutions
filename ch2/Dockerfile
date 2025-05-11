# Use an official Python runtime as a parent image 
FROM python 

# Set the working directory 
WORKDIR /app 

# Expose the application on port 5000 
EXPOSE 5000 

# Define environment variable 
ENV FLASK_APP=app.py 

# Install any needed packages specified in requirements.txt 
RUN pip install --no-cache-dir flask llama-cpp-python 

# Copy the current dir contents into the container at /app 
COPY . /app 

# Run app.py when the container launches 
CMD ["python", "app.py"] 