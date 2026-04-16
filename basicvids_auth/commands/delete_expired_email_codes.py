import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sqlmodel import select

from basicvids_auth.schemas import create_db_and_tables, get_session
from basicvids_auth.schemas.users import EmailCode


def delete_expired_email_codes() -> None:
    create_db_and_tables()
    session = next(get_session())
    now = datetime.now(timezone.utc)
    expired_codes = session.exec(select(EmailCode)).all()
    deleted_count = 0

    for email_code in expired_codes:
        if email_code.expires_at.replace(tzinfo=timezone.utc) < now:
            session.delete(email_code)
            deleted_count += 1

    session.commit()
    print(f"Deleted {deleted_count} expired email codes")


if __name__ == "__main__":
    delete_expired_email_codes()
