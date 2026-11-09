# System Architecture

```mermaid
flowchart TD
    A["User / Web Browser"] -->|"HTTP: localhost:5001"| B["Docker Host Port 5001"]
    B -->|"Maps to container port 5000"| C["Web Container: Flask + Gunicorn"]
    C -->|"SQL queries via internal Docker network"| D["PostgreSQL Container: Port 5432"]
    D --> E[("Persistent Volume: postgres_data")]