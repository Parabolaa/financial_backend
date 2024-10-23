# Financial Backend Project

This project is a Django-based financial backend system, Dockerized for easy deployment. It connects to a PostgreSQL database and provides APIs for stock data fetching, backtesting, and prediction. This README will guide you through setting up the project locally and deploying it using Docker, along with instructions on how to configure and connect the PostgreSQL database.

## Table of Contents
1. [Requirements](#requirements)
2. [Setup Instructions](#setup-instructions)
    - [PostgreSQL Setup](#postgresql-setup)
    - [Django Setup](#django-setup)
    - [Docker Setup](#docker-setup)
3. [Running Migrations](#running-migrations)
4. [Running the Application](#running-the-application)
5. [Database Configuration](#database-configuration)
6. [API Endpoints](#api-endpoints)
7. [Troubleshooting](#troubleshooting)

## Requirements

To set up and run this project, ensure you have the following installed:
- Python 3.8 or later
- Docker and Docker Compose
- PostgreSQL (locally or in a Docker container)
- Git (optional for cloning the project)

## Setup Instructions

### PostgreSQL Setup

#### 1. Install PostgreSQL

For MacOS (using Homebrew):

```bash
brew install postgresql
```

#### 2. Create the Database

Once PostgreSQL is installed and running, create the financial_db database:

```bash
$ brew services start postgresql@14
$ /opt/homebrew/opt/postgresql@14/bin/createuser -s postgres
$ psql -U postgres
$ CREATE DATABASE financial_db
```

### Django Setup

#### 1. Clone the Repository
Clone the project repository (or simply place the project files in a folder):

```bash
git clone https://github.com/Parabolaa/financial_backend.git
cd financial_backend
```

#### 2. Install Project Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables

Mofidy the settings.py within Django (not recommended) or create a .env file in the project root and add your environment variables:

```bash
SECRET_KEY=your_secret_key
DEBUG=1
DB_NAME=financial_db
DB_USER=postgres
DB_PASSWORD=''
DB_HOST=db  # Set to 'localhost' if running PostgreSQL locally
DB_PORT=5432
```
Make sure SECRET_KEY is a unique value for this Django project.

### Docker Setup

This project is fully Dockerized, allowing you to run the entire application with PostgreSQL in containers.

#### 1. Build and Run Docker Containers

Make sure you are in the project root and run the following command:

```bash
docker-compose up --build
```
This will spin up the web service for the Django app and the db service for PostgreSQL.


## Running Migrations
Once the database and containers are set up, run the Django migrations:

```bash
docker-compose run web python manage.py migrate
```

This will create all the necessary database tables in the financial_db.

## Running the Application

#### 1. Start the application with Docker:
```bash
docker-compose up
```
make sure that this command is within your docker-compose.yml file:
```bash
python manage.py runserver 0.0.0.0:8000
```
or you can run it yourself in terminal.

#### 2. Open your browser and go to:
```bash
http://localhost:8000/main
```
You should see the Django application running.

## Database Configuration
Make sure the Django project is connected to the PostgreSQL database using the settings from your .env file:

In settings.py, the database settings look like this:
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```
or if you do not need an .env file and modify settings.py itself, it should be look like this:
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'financial_db',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## API Endpoints
The application exposes several API endpoints:

#### 1.	Fetch Stock Data:
	•	URL: /fetch/<str:symbol>/
	•	Fetches and displays stock data for a given symbol.
#### 2.	Backtesting Module:
	•	URL: /backtest/<str:symbol>/
	•	Allows users to backtest stock strategies.
#### 3.	Prediction Module:
	•	URL: /predict/<str:symbol>/
	•	Provides stock price predictions based on historical data.
#### 4.	Generate ML Reports:
	•	URL: /report/pdf/<str:symbol>/
	•	URL: /report/json/<str:symbol>/
	•	Generates and downloads a PDF report for machine learning predictions.
#### 5. Generate Backtest Reports:
    •	URL: /backtest/pdf/<str:symbol>/<str:initial_investment>
	•	URL: /backtest/json/<str:symbol>/<str:initial_investment>
	•	Generates and downloads a PDF report for backtest results. 

## Troubleshooting

If you encounter any issues during setup or deployment, here are some common solutions:

### 1. Database Connection Error
Ensure that your database credentials are correct in the .env file, and the PostgreSQL service is running.

### 2. Docker Issues
Make sure Docker is installed and running properly, and that you have sufficient disk space for your containers.

### 3. Migration Issues
If migrations fail, try resetting the migrations by deleting the migrations folder within the app and re-running makemigrations and migrate.
