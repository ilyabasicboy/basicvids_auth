# BasicVids Auth

Authentication microservice for BasicVids.

## Stack

- Gunicorn
- FastAPI
- SQLModel
- Redis
- python-jose

## Development

Use a virtual environment:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Run locally:

```bash
uvicorn basicvids_auth.main:app --reload
```

## Container

```bash
mkdir -p data
cp .env.example data/.env
# Replace SECRET_KEY and adjust DATABASE_URL if needed.
docker compose up -d --build
```

The service is available through the shared gateway at:

```text
http://localhost:8080/api/v1/auth/
http://localhost:8080/api/v1/users/
http://localhost:8080/api/v1/avatars/
```

## Configuration

Project environment is loaded from:

```text
./data/.env
```

Start from:

```text
./.env.example
```

Database examples:

```env
# SQLite default
# DATABASE_URL=sqlite:///./data/database.db

# PostgreSQL example
DATABASE_URL=postgresql://basicvids_auth_user:change_me@host.docker.internal:5432/basicvids_auth
```

Important variables:

| Variable | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | required | JWT signing key |
| `DATA_PATH` | `./data` | Data storage directory |
| `DATABASE_URL` | `sqlite:///./data/database.db` | Metadata database URL |
| `REDIS_URL` | `redis://localhost:6379/2` | Redis connection |
| `AVATAR_STORAGE_DIR` | `avatars` | Avatar directory inside `DATA_PATH` |
| `MAX_AVATAR_SIZE_BYTES` | `524288` | Maximum user avatar size |
| `REFRESH_TOKEN_CLEANUP_CRON` | `0 8 * * *` | Refresh token cleanup schedule |
| `CUSTOM_HOST` | `host.docker.internal` | Host gateway alias used in Docker |

## Healthcheck

```text
http://localhost:8080/auth/health
```

## Admin And Maintenance

Create admin:

```bash
docker compose exec basicvids_auth python3 basicvids_auth/commands/create_admin.py username password email --first_name first_name --last_name last_name
```

Cleanup commands:

```bash
docker compose exec basicvids_auth python3 basicvids_auth/commands/delete_expired_email_codes.py
docker compose exec basicvids_auth python3 basicvids_auth/commands/delete_unconfirmed_users.py
```

To import avatar records and files previously owned by `basicvids_storage`, run before removing old storage data:

```bash
venv/bin/python -m basicvids_auth.commands.migrate_avatars_from_storage \
  ../basicvids_storage/data/database.db ../basicvids_storage/data/videos
```

## API Notes

User avatar API is owned by this service:

- `POST /api/v1/avatars/users/{user_id}/registration/`
- `PUT /api/v1/avatars/me/`
- `GET /api/v1/avatars/users/{user_id}/image/`
- `DELETE /api/v1/avatars/me/`
