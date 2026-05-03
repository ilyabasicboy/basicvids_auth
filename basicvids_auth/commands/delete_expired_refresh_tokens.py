import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlmodel import select

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from basicvids_auth.schemas import create_db_and_tables, get_session
from basicvids_auth.schemas.auth import RefreshToken
from basicvids_auth.settings import settings


def delete_expired_refresh_tokens() -> None:
    create_db_and_tables()
    session = next(get_session())
    now = datetime.now(timezone.utc)
    revoked_cutoff = now - timedelta(days=settings.REFRESH_TOKEN_REVOKED_RETENTION_DAYS)
    tokens = session.exec(select(RefreshToken)).all()

    deleted_count = 0
    for token in tokens:
        expires_at = token.expires_at.replace(tzinfo=timezone.utc)
        revoked_at = token.revoked_at.replace(tzinfo=timezone.utc) if token.revoked_at else None

        if expires_at < now or (revoked_at and revoked_at < revoked_cutoff):
            session.delete(token)
            deleted_count += 1

    session.commit()
    print(f"Deleted {deleted_count} expired/revoked refresh tokens")


if __name__ == "__main__":
    delete_expired_refresh_tokens()
