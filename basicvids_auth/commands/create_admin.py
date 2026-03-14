import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from basicvids_auth.schemas import get_session
from basicvids_auth.schemas.users import User as UserDB
from basicvids_auth.models.users import AdminCreate
from basicvids_auth.utils.password import hash_password

from pydantic import ValidationError
from fastapi import HTTPException
from sqlmodel import select


def create_admin(username, password, email, first_name=None, last_name=None):

    data = {
        'email': email,
        'username': username,
        'password': password,
        'first_name': first_name,
        'last_name': last_name
    }

    try:
        admin = AdminCreate(**data)
    except ValidationError as e:
        print("Validation error:", e.json())
        return

    admin.password = hash_password(admin.password)

    session = next(get_session())

    # Check duplicates
    query = select(UserDB)
    for field, value in admin.model_dump(exclude={'password'}).items():
        if hasattr(UserDB, field):
            query = query.where(getattr(UserDB, field) == value)

    existing_user = session.exec(query).first()
    if existing_user:
        print('User already exists')
        return

    db_user = UserDB(
        **admin.model_dump()
    )
    session.add(db_user)
    session.commit()

    print('Admin {username} created successfully!'.format(username=username))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Admin args")

    parser.add_argument("username", type=str)
    parser.add_argument("password", type=str)
    parser.add_argument("email", type=str)
    parser.add_argument("--first_name", type=str, required=False)
    parser.add_argument("--last_name", type=str, required=False)

    args = parser.parse_args()
    args_dict = vars(args)

    create_admin(**args_dict)