# Credit Approval System

This project is a Credit Approval System built with Django and Django REST Framework. It allows for customer registration, loan eligibility checks, and loan management, all using background task processing with Celery and Docker.


## Features

- **Customer Registration**: Register new customers and assign an approved credit limit.
- **Loan Eligibility Check**: Check loan eligibility based on historical data and credit score.
- **Loan Management**: Manage loans, calculate EMIs, and provide loan details.
- **Background Task Processing**: Data ingestion and background tasks handled by Celery with Redis.
- **Dockerized Setup**: Entire project, including PostgreSQL and Redis, runs in Docker.

## Prerequisites

- Docker and Docker Compose installed on your system.
- Basic knowledge of Django, Docker, and Celery (optional).

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd credit_approval_system

2. **Docker Setup:
     docker-compose up --build



