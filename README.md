# FastAPI Migration

A project migrated from Django REST Framework to FastAPI.

## Setup

1. Create a virtual environment:
#bash
python -m venv venv

source venv/bin/activate  # Linux/macOS

venv\Scripts\activate     # Windows

2. Install dependencies:
#bash
pip install -r requirements.txt

3. Set up environment variables in .env file

Create a .env file in the root directory and configure the following variables:

RABBITMQ_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=rpc://

4. Run the application:
#bash
uvicorn app.main:app --reload

## Setting Up Celery with RabbitMQ
1. Install RabbitMQ:

* Download and install RabbitMQ from the official website.
* Ensure RabbitMQ is running. You can start it using the RabbitMQ service manager or the following command:

rabbitmq-server

2. Start the Celery Worker:

Open a new PowerShell window, activate the virtual environment, and run the following command:
#bash
celery -A app.core.celery_app.celery_app worker --loglevel=info --pool=solo

3. Start the Celery Beat Scheduler (Optional): If you are using periodic tasks, you need to start the Celery beat scheduler. Run the following command in a new PowerShell window:
#bash
celery -A app.core.celery_app.celery_app beat --loglevel=info

## Running the Application
1. Start RabbitMQ:
rabbitmq-server

2. Start the Celery worker:
celery -A app.core.celery_app.celery_app worker --loglevel=info --pool=solo

3. Run the FastAPI application:
uvicorn app.main:app --reload

## Features
* FastAPI-based backend with asynchronous support.
* Celery integration for background task processing.
* RabbitMQ as the message broker.
* Support for periodic tasks with Celery beat (optional).


## Setup Database
1. Delete and Recreate the Database:
#run SQL query
DROP DATABASE your_database_name;
CREATE DATABASE your_database_name;

2. Generate Migration Scripts:
#bash 
alembic revision --autogenerate -m "Initial migration"

3. Apply the Migrations:
#bash 
alembic upgrade head

4. Verify the Tables:
Use your database client or a SQL query to check the tables:
SHOW TABLES IN your_database_name;