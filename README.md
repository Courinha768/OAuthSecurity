# OAuthSecurity

## Description

OAuthSecurity is a robust authentication and authorization service built using Django. It leverages OAuth 2.0 protocols to provide secure access to your applications. This project is designed to be easily deployable using Docker, with support for PostgreSQL as the database and Redis as an optional caching layer.

## Features

- OAuth 2.0 compliant authentication
- User management and role-based access control
- Dockerized setup for easy deployment
- PostgreSQL as the primary database
- Optional Redis caching for improved performance

## Sequence Diagram

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation and Running the Project](#installation-and-running-the-project)
  - [Docker Compose Setup](#docker-compose-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Endpoints](#endpoints)

## Installation and Running the Project

### Docker Compose Setup

The easiest way to run the OAuthSecurity project is by using Docker Compose. Below is an example configuration that sets up PostgreSQL as the database and Redis as the cache.

**Note:** Currently, only PostgreSQL is supported. Redis is optional, and the project will function without it.

```yaml
networks:
  security:
    name: security-network
    driver: bridge

volumes:
  security-volume:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: path_to_volume
  cache:
    driver: local

services:
  # Database Service
  security-database:
    container_name: 'Security-postgresql'
    image: postgres:13
    environment:
      POSTGRES_DB: 'DATABASE_NAME'
      POSTGRES_USER: 'USER'
      POSTGRES_PASSWORD: 'PASSWORD'
    volumes:
      - security-volume:/var/lib/postgresql/data
    networks:
      - security
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U courinha -d security"]
      interval: 10s
      retries: 5
      start_period: 30s
      timeout: 10s
    restart: unless-stopped

  # Cache Service
  security-cache:
    image: redis:6.2-alpine
    restart: always
    command: redis-server --save 20 1 --loglevel warning
    volumes:
      - cache:/data
    networks:
      - security
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 5
      start_period: 10s

  # OAuth Security Service
  security-service:
    container_name: 'OAuthSecurity'
    image: courinha/oauthsecurity
    environment:
      DJANGO_SECRET_KEY: 'SECRET_KEY'
      POSTGRES_DB: 'DATABASE_NAME'
      POSTGRES_USER: 'USER'
      POSTGRES_PASSWORD: 'PASSWORD'
      POSTGRES_HOST: 'security-database'
      POSTGRES_PORT: 5432
      LOG_LEVEL: 'INFO'
      LOG_DIR: '/var/log/django'
      REDIS_HOST: 'security-cache'
      REDIS_PORT: 6379
    volumes:
      - .logs:/var/log/django
    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'
    ports:
      - "8000:8000"
    networks:
      - security
    depends_on:
      security-database:
        condition: service_healthy
        restart: true
      security-cache:
        condition: service_healthy
        restart: true
    restart: unless-stopped
```

## Configuration

Before running the project, make sure to update the following environment variables in the docker-compose.yml file:

- DATABASE_NAME: The name of your PostgreSQL database.
- USER: The PostgreSQL user.
- PASSWORD: The password for the PostgreSQL user.
- SECRET_KEY: A secret key for your Django application.

## Usage

After setting up the Docker Compose file, you can start the services by running:

```bash
docker-compose up -d
```

To stop the services, use:

```bash
docker-compose down
```

## Endpoints
