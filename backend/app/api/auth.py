from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.security import burn_password_check, create_access_token, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, Me, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, db: DbSession) -> Token:
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None:
        burn_password_check(payload.password)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )
    return Token(access_token=create_access_token(user.username))


@router.get("/me")
def me(user: CurrentUser) -> Me:
    return Me(id=user.id, username=user.username)
