import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models import User

SECRET_KEY = "cffeab7273c7c06fc2b3acb3ce1f7968de183fccb1aa4d42290944fd98a0476c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


def hash_password(password: str) -> str:
    # bcrypt only uses the first 72 bytes of a password
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        return None


class NotAuthenticated(Exception):
    pass


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise NotAuthenticated()

    payload = decode_access_token(token)
    if not payload:
        raise NotAuthenticated()

    user_id = payload.get("sub")
    if not user_id:
        raise NotAuthenticated()

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise NotAuthenticated()

    return user