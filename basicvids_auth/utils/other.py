from pydantic import EmailStr
from datetime import datetime, timezone

def is_email(value: str) -> bool:
    try:
        EmailStr._validate(value)
        return True
    except Exception:
        return False
    

def utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt