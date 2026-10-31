from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings

JWT_ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except ValueError:  # e.g. passwords longer than bcrypt's 72-byte limit
        return False


# Computed at import so even the first unknown-user login costs one bcrypt check, not two.
_DUMMY_HASH = hash_password("timing-equaliser")


def burn_password_check(plain: str) -> None:
    """Spend the same time as a real check, so unknown usernames are not revealed by timing."""
    verify_password(plain, _DUMMY_HASH)


def create_access_token(subject: str, expires_in: timedelta | None = None) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + (expires_in or timedelta(hours=settings.jwt_expire_hours))
    return jwt.encode(
        {"sub": subject, "exp": expires_at}, settings.jwt_secret, algorithm=JWT_ALGORITHM
    )


def decode_access_token(token: str) -> str | None:
    """Return the token's subject, or None if it is invalid or expired."""
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
