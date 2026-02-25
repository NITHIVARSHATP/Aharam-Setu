from fastapi import Header, HTTPException

from .db import db
from .models import Role, User


def get_current_user(x_user_id: str = Header(default=""), x_role: str = Header(default="")) -> User:
    if not x_user_id or not x_role:
        raise HTTPException(status_code=401, detail="Missing auth headers: x-user-id and x-role")
    user = db.users.get(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.role.value != x_role:
        raise HTTPException(status_code=403, detail="Role mismatch")
    return user


def require_role(user: User, expected: Role) -> None:
    if user.role != expected:
        raise HTTPException(status_code=403, detail=f"Only {expected.value} can perform this action")
