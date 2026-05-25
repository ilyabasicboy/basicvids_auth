import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlmodel import Session

from basicvids_auth.schemas import create_db_and_tables, engine
from basicvids_auth.schemas.users import Avatar, User
from basicvids_auth.settings import settings
from basicvids_auth.storage import build_storage


def migrate(source_database: Path, source_files: Path) -> tuple[int, int]:
    create_db_and_tables()
    storage = build_storage()
    migrated = 0
    skipped = 0

    with sqlite3.connect(source_database) as source_connection:
        rows = source_connection.execute(
            "SELECT user_id, storage_key, content_type, size_bytes, created_at, updated_at FROM avatar"
        ).fetchall()

    with Session(engine) as session:
        for user_id, storage_key, content_type, size_bytes, created_at, updated_at in rows:
            source_path = source_files / storage_key
            if not session.get(User, user_id) or not source_path.exists():
                skipped += 1
                continue

            old_avatar = session.get(Avatar, user_id)
            stored_file = storage.save_file(source_path, source_path.suffix, settings.MAX_AVATAR_SIZE_BYTES)
            created = datetime.fromisoformat(created_at) if isinstance(created_at, str) else created_at
            updated = datetime.fromisoformat(updated_at) if isinstance(updated_at, str) else updated_at
            if old_avatar:
                storage.delete(old_avatar.storage_key)
                old_avatar.storage_backend = storage.name
                old_avatar.storage_key = stored_file.key
                old_avatar.content_type = content_type
                old_avatar.size_bytes = stored_file.size_bytes
                old_avatar.updated_at = updated
                avatar = old_avatar
            else:
                avatar = Avatar(
                    user_id=user_id,
                    storage_backend=storage.name,
                    storage_key=stored_file.key,
                    content_type=content_type,
                    size_bytes=stored_file.size_bytes,
                    created_at=created,
                    updated_at=updated,
                )
            session.add(avatar)
            migrated += 1
        session.commit()

    return migrated, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Import user avatars previously stored by basicvids_storage.")
    parser.add_argument("source_database", type=Path, help="Path to the basicvids_storage SQLite database.")
    parser.add_argument("source_files", type=Path, help="Path to the basicvids_storage videos directory.")
    args = parser.parse_args()
    migrated, skipped = migrate(args.source_database, args.source_files)
    print(f"Migrated avatars: {migrated}; skipped: {skipped}")


if __name__ == "__main__":
    main()
