# BasicVids Auth

Authentication universal microservice.

## Stack
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

The service is available through the shared `basicvids_gateway` project:

```
http://localhost:8080/api/v1/auth/
http://localhost:8080/api/v1/users/
```

## Image Configuration

Environment variables:

| Variable    | Default              | Description            |
| ----------- | -------------------- | ---------------------- |
| DATA_PATH   | ./data               | Data storage directory |
| AVATAR_STORAGE_DIR | avatars        | Directory inside DATA_PATH for user avatar files |
| MAX_AVATAR_SIZE_BYTES | 524288      | Maximum user avatar size |
| CUSTOM_HOST | host.docker.internal | Host gateway           |

## Project Configuration

Create DATA_PATH/.env file # (./data/.env by default)

Environment variables:

SECRET_KEY=random secret string # for jwt encoding

ACCESS_TOKEN_EXPIRE_MINUTES=INT # (default=15)

REFRESH_TOKEN_EXPIRE_DAYS=INT # (default=7)

DATABASE_URL=postgresql://basicvids_auth_user:basicvidsauthpassword@host.docker.internal:5432/basicvids_auth # (default=sqlite:///./data/database.db)
DEBUG=True # prints confirmation emails to console instead of sending real mail
EMAIL_CODE_EXPIRE_MINUTES=10
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=username
SMTP_PASSWORD=password
EMAIL_FROM=noreply@example.com

## Healthcheck

Service health endpoint:

```
http://localhost:8080/auth/health
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

## Cleanup commands

```bash
docker compose exec basicvids_auth python3 basicvids_auth/commands/delete_expired_email_codes.py
docker compose exec basicvids_auth python3 basicvids_auth/commands/delete_unconfirmed_users.py
```

User avatar API is owned by this service:

- `POST /api/v1/avatars/users/{user_id}/registration/` uploads the initial avatar after registration.
- `PUT /api/v1/avatars/me/` replaces the authenticated user's avatar.
- `GET /api/v1/avatars/users/{user_id}/image/` returns the image or the default placeholder.
- `DELETE /api/v1/avatars/me/` deletes the authenticated user's avatar.

To import avatar records and files previously owned by `basicvids_storage`, run before removing old storage data:

```bash
venv/bin/python -m basicvids_auth.commands.migrate_avatars_from_storage \
  ../basicvids_storage/data/database.db ../basicvids_storage/data/videos
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
- **Note:** users with unconfirmed email receive `403` with `Email is not confirmed`

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
- **Response:** `{ id, username, first_name, last_name, email, is_admin, email_confirmed }`

#### Get user by ID (admin only)

- **GET** `/users/detail/{user_id}`
- **Response:** `{ id, username, first_name, last_name, email, is_admin, email_confirmed }`

#### Create user

- **POST** `/users/create/`
- **Body:**
  - `username` (string)
  - `email` (string)
  - `password` (string, max 72 chars)
  - `first_name` (string, optional)
  - `last_name` (string, optional)
- **Response:** `{ id, username, first_name, last_name, email, is_admin, email_confirmed }`

#### Confirm user email

- **POST** `/users/confirm/email/`
- **Body:**
  - `email` (string)
  - `code` (string)
- **Response:** `{ id, username, first_name, last_name, email, is_admin, email_confirmed }`

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
- **Response:** `{ id, username, first_name, last_name, email, is_admin, email_confirmed }`

#### Change current user

- **PATCH** `/users/change/`
- **Requires:** authentication
- **Body:**
  - `first_name` (string or null)
  - `last_name` (string or null)
- **Response:** `{ id, username, first_name, last_name, email, is_admin, email_confirmed }`

#### Change current user password

- **PATCH** `/users/change/password/`
- **Requires:** authentication
- **Body:**
  - `old_password` (string, max 72 chars)
  - `new_password` (string, max 72 chars)
- **Response:** `{ "message": "Password changed successfully" }`

#### Delete current user

- **DELETE** `/users/delete/`
- **Requires:** authentication
- **Response:** `{ "message": "User deleted successfully" }`

#### Delete user by ID (admin only)

- **DELETE** `/users/delete/{user_id}`
- **Requires:** admin authentication
- **Response:** `{ "message": "User deleted successfully" }`
