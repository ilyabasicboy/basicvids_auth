import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sqlmodel import select

from basicvids_auth.schemas import create_db_and_tables, get_session
from basicvids_auth.schemas.users import EmailCode, User


def delete_unconfirmed_users() -> None:
    create_db_and_tables()
    session = next(get_session())
    cutoff = datetime.now(timezone.utc) - timedelta(days=31)
    users = session.exec(select(User).where(User.email_confirmed == False)).all()
    deleted_count = 0

    for user in users:
        if user.created_at and user.created_at.replace(tzinfo=timezone.utc) <= cutoff:
            for email_code in session.exec(select(EmailCode).where(EmailCode.email == user.email)).all():
                session.delete(email_code)
            session.delete(user)
            deleted_count += 1

    session.commit()
    print(f"Deleted {deleted_count} unconfirmed users")


if __name__ == "__main__":
    delete_unconfirmed_users()
