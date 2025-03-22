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
  oauth-security:
    container_name: 'OAuthSecurity'
    image: courinha/oauthsecurity
    environment:
      DJANGO_SECRET_KEY: SECRET_KEY
      POSTGRES_DB: DATABASE_NAME
      POSTGRES_USER: DATABASE_USER
      POSTGRES_PASSWORD: DATABASE_PASSWORD
      POSTGRES_HOST: DATABASE_HOST
      POSTGRES_PORT: DATABASE_PORT
      LOG_LEVEL: 'INFO / DEBUG / WARNING'
      REDIS_HOST: REDIS_HOST
      REDIS_PORT: REDIS_PORT
    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'
    ports:
      - "8000:8000"
    depends_on:
      database:
        condition: service_healthy
        restart: true
      cache:
        condition: service_healthy
        restart: true
    restart: unless-stopped
```

## Configuration

Before running the project, make sure to update the following environment variables in the docker-compose.yml file:

- DJANGO_SECRET_KEY: Django secret key.
- POSTGRES_DB: The name of your PostgreSQL database.
- POSTGRES_USER: The PostgreSQL user.
- POSTGRES_PASSWORD: The password for the PostgreSQL user.
- POSTGRES_HOST: The PostgreSQL host.
- POSTGRES_PORT: The port where your database is exposed (default is 5432).
- LOG_LEVEL: The level of logging you want.
- REDIS_HOST: The Redis host.
- REDIS_PORT: The port where your Redis cache is exposed (default is 6379).

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

TODO
