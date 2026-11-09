# Coffee Batch Inspection Log

## 1. Project Overview

Coffee Batch Inspection Log is a web-based application developed to record, manage, and retrieve coffee batch inspection information.

The application helps users organize coffee inspection records, including coffee origin, processing method, inspection date, and quality status.

## 2. Project Objectives

- Provide a centralized system for recording coffee batch inspections.
- Store inspection records in a PostgreSQL database.
- Allow users to create, view, update, and delete inspection records.
- Demonstrate containerization and service communication using Docker.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| Flask | Web framework and REST API |
| PostgreSQL | Relational database |
| HTML, CSS, JavaScript | User interface |
| Docker | Application containerization |
| Docker Compose | Managing application and database services |
| Gunicorn | Python application server |

## 4. Application Features

- Create new coffee inspection records.
- View stored inspection records.
- Update existing inspection records.
- Delete inspection records.
- Validate user input.
- Check application and database connectivity through a health endpoint.
- Store records persistently using a Docker volume.

## 5. Database Structure

The application uses a PostgreSQL database with a table named `coffee_batches`.

| Column | Description |
|---|---|
| id | Unique record identifier |
| batch_code | Unique coffee batch code |
| coffee_origin | Origin of the coffee |
| processing_method | Coffee processing method |
| inspection_date | Date of inspection |
| quality_status | Inspection result |
| notes | Additional inspection notes |
| created_at | Record creation timestamp |

## 6. System Architecture

The application consists of two main services:

1. **Web service:** Flask application served by Gunicorn.
2. **Database service:** PostgreSQL database for persistent storage.

The web service communicates with PostgreSQL through the internal Docker network.

## 7. Installation and Execution

### Requirements

- Docker Desktop
- Git

### Run the application

Clone the repository:

```bash
git clone https://github.com/lauw278/coffee-batch-inspection-log.git
cd coffee-batch-inspection-log
```

Create a local environment file by copying `.env.example` to `.env`, then configure the database credentials if needed.

Start the application:

```bash
docker compose up -d --build
```

Open the application:

http://localhost:5001

### Stop the application

```bash
docker compose down
```

The PostgreSQL data volume is preserved when containers are stopped using this command. Do not use `-v` if you want to preserve the database records.

## 8. Health Check

The application provides a health endpoint:

```text
http://localhost:5001/health
```

A successful response indicates that the application is running and connected to PostgreSQL.

## 9. API Endpoints

| Method | Endpoint | Function |
|---|---|---|
| GET | /api/batches | Retrieve all inspection records |
| POST | /api/batches | Create a new inspection record |
| PUT | /api/batches/{id} | Update an inspection record |
| DELETE | /api/batches/{id} | Delete an inspection record |
| GET | /health | Check application and database health |

## 10. Repository

GitHub: https://github.com/lauw278/coffee-batch-inspection-log

---

**Project:** Coffee Batch Inspection Log  
**Category:** Cloud Services  
**Architecture:** Flask Web Application with PostgreSQL and Docker