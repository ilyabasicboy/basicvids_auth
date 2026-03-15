# BasicVids Auth

Authentication universal microservice.

## Stack
* Nginx
* Gunicorn
* FastAPI
* SQLModel
* Python-jose

## Requirements

* Docker
* Docker Compose

## Quick start

Clone the repository:

```bash
git clone https://github.com/ilyabasicboy/basicvids_auth.git
cd basicvids_auth
```

Create data directory:

```bash
mkdir -p data
```

Run the service:

```bash
docker compose up -d
```

The service will be available at:

```
http://localhost:8080
```

## Image Configuration

Environment variables:

| Variable    | Default              | Description            |
| ----------- | -------------------- | ---------------------- |
| PORT        | 8080                 | HTTP port              |
| DATA_PATH   | ./data               | Data storage directory |
| CUSTOM_HOST | host.docker.internal | Host gateway           |

Example:

```bash
PORT=9000 docker compose up -d
```

## Project Configuration

Create DATA_PATH/.env file # (./data/.env by default)

Environment variables:

SECRET_KEY=random secret string # for jwt encoding

ACCESS_TOKEN_EXPIRE_MINUTES=INT # (default=15)

REFRESH_TOKEN_EXPIRE_DAYS=INT # (default=7)

DATABASE_URL=postgresql://basicvids_auth_user:basicvidsauthpassword@host.docker.internal:5432/basicvids_auth # (default=sqlite:///./data/database.db)

## Healthcheck

Service health endpoint:

```
http://localhost:8000/health
```

## Logs

View logs:

```bash
docker compose logs -f
```

## Stop

```bash
docker compose down
```

## Create admin

```bash
docker compose exec basicvids_auth python3 basicvids_auth/commands/create_admin.py username password email --first_name first_name --last_name last_name
```

## API Documentation

### Health Check

- **GET** `/health`
  - **Response:** `{ "status": "ok" }`

### Authentication

#### Login

- **POST** `/auth/login/`
- **Body:**
  - `identifier` (string) — username or email
  - `password` (string)
- **Response:**
  - `access_token` (string)
  - `refresh_token` (string)
  - `token_type` ("bearer")

#### Refresh

- **POST** `/auth/refresh/`
- **Body:**
  - `refresh_token` (string)
- **Response:**
  - `access_token` (string)
  - `refresh_token` (string)
  - `token_type` ("bearer")

#### Logout

- **POST** `/auth/logout/`
- **Body:**
  - `refresh_token` (string)
- **Response:**
  - `{ "detail": "Logged out" }`

> **Note:** Use the `access_token` in the `Authorization` header for protected endpoints:
>
> `Authorization: Bearer <access_token>`

### Users

#### Get users (admin only)

- **GET** `/users/`
- **Query parameters (optional):**
  - `offset` (int, default: 0)
  - `limit` (int, default: 10, max: 100)
  - `id`, `username`, `email`, `first_name`, `last_name`, `is_admin` — used as filters
- **Response:** `[{ id, username, first_name, last_name, email, is_admin }, ...]`

#### Get current user

- **GET** `/users/detail/`
- **Requires:** authentication
- **Response:** `{ id, username, first_name, last_name, email, is_admin }`

#### Get user by ID (admin only)

- **GET** `/users/detail/{user_id}`
- **Response:** `{ id, username, first_name, last_name, email, is_admin }`

#### Create user

- **POST** `/users/create/`
- **Body:**
  - `username` (string)
  - `email` (string)
  - `password` (string, max 72 chars)
  - `first_name` (string, optional)
  - `last_name` (string, optional)
- **Response:** `{ id, username, first_name, last_name, email, is_admin }`

#### Create admin (admin only)

- **POST** `/users/create/admin/`
- **Requires:** admin authentication
- **Body:**
  - `username` (string)
  - `email` (string)
  - `password` (string, max 72 chars)
  - `is_admin` (bool, defaults to true)
  - `first_name` (string, optional)
  - `last_name` (string, optional)
- **Response:** `{ id, username, first_name, last_name, email, is_admin }`

#### Delete current user

- **DELETE** `/users/delete/`
- **Requires:** authentication
- **Response:** `{ "message": "User deleted successfully" }`

#### Delete user by ID (admin only)

- **DELETE** `/users/delete/{user_id}`
- **Requires:** admin authentication
- **Response:** `{ "message": "User deleted successfully" }`

