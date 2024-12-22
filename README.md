# LawDesk API

A FastAPI-based REST API for Law firm management system

## Architecture Overview

The project follows a clean, modular architecture with clear separation of concerns:

### Core Components

```
src/
├── app/                   # Application Layer
│   ├── business/          # Business Domain Logic
│   └── system/            # System Management
├── common/                # Shared Components
│   ├── security/          # JWT, RBAC
│   ├── exception/         # Error handling
│   └── response/          # Response formatting
├── core/                  # Core Configuration
├── database/              # Database Connections
└── middleware/            # Request Processing
```

### Application Structure

Each domain (`business` and `system`) follows a consistent layered architecture:

- **API Layer** (`api/`): REST endpoints and route definitions
- **Service Layer** (`service/`): Business logic and domain operations
- **CRUD Layer** (`crud/`): Database operations and queries
- **Models** (`models/`): SQLAlchemy ORM models
- **Schemas** (`schema/`): Pydantic models for request/response validation

### Key Features

- **Business Domain** (`/app/business/`)

  - Legal case management
  - Client management
  - Court and judge information
  - Case type handling

- **System Management** (`/app/system/`)

  - User authentication & authorization
  - Role-based access control (RBAC)
  - Login tracking
  - System administration

- **Common Utilities** (`/common/`)
  - JWT authentication
  - RBAC security
  - Exception handling
  - Response standardization
  - Pagination support

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Poetry (for local development)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. Build and start the containers:
   ```bash
   docker compose -f "docker_compose.yml" up -d --build
   ```
2. Once the `lawdesk-api` container is up, run the following alembic migration:
   ```bash
   docker exec -it lawdesk-api poetry run alembic upgrade head
   ```
   If you need to undo all migrations, you can run:
   ```bash
   docker exec -it lawdesk-api poetry run alembic downgrade base # undo all migrations
   ```
3. Seed the database with initial data:

   First, ensure you have set up the super admin credentials in your `.env` file:

   ```env
   SUPER_ADMIN_EMAIL='admin@example.com'
   SUPER_ADMIN_PASSWORD='your_secure_password'
   SUPER_ADMIN_USERNAME='admin'
   ```

   Then you can run the seeding commands:

   ```bash
   # Seed all data (including super admin)
   docker exec -it lawdesk-api poetry run python -m src.commands.seed --all

   # Or seed specific data types:
   docker exec -it lawdesk-api poetry run python -m src.commands.seed --super-admin # Only seed super admin
   docker exec -it lawdesk-api poetry run python -m src.commands.seed --cities     # Only seed cities
   docker exec -it lawdesk-api poetry run python -m src.commands.seed --courts     # Only seed courts
   docker exec -it lawdesk-api poetry run python -m src.commands.seed --case-types # Only seed case types
   ```

   This will populate the database with:

   - Super admin user (when using --all or --super-admin)
   - Cities data (with Arabic, English, and French names)
   - Courts information
   - Case types

   > Note: Be cautious when running seed commands multiple times - especially for cities, courts, and case types as this may cause data duplication. The --super-admin flag can be used multiple times with different .env credentials to create additional admin users as needed.

## 📚 API Documentation

Once the server is running, you can access:

- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`
