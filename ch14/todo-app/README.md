# Simple TODO Application

A lightweight TODO application that allows you to create, view, update, and delete tasks.

## Features

- Create new tasks with title and description
- Mark tasks as complete/incomplete
- Delete tasks
- View all tasks
- In-memory storage (no database required)

## Technical Details

- Built with Python and Flask
- Single-page application with RESTful API
- Containerized with Docker

## Running Locally

### Without Docker

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Access the application at http://localhost:5000

### With Docker

1. Build the Docker image:
   ```
   docker build -t todo-app .
   ```

2. Run the container:
   ```
   docker run -p 5000:5000 todo-app
   ```

3. Access the application at http://localhost:5000

## API Endpoints

- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/<task_id>` - Get a specific task
- `PUT /api/tasks/<task_id>` - Update a task
- `DELETE /api/tasks/<task_id>` - Delete a task

## Docker Best Practices Used

- Uses a slim base image to reduce size
- Creates a non-root user for security
- Sets appropriate environment variables
- Uses multi-stage build for efficiency
- Properly exposes the application port
- Uses gunicorn for production deployment
