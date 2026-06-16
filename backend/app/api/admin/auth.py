"""Admin autentifikatsiya endpointlari: login, me."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import get_current_admin
from app.core.database import get_db
from app.core.security import create_access_token
from app.models import Admin
from app.schemas.admin import AdminOut, LoginIn, TokenOut
from app.services import admin as admin_service

router = APIRouter(prefix="/auth", tags=["admin-auth"])


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)):
    admin = await admin_service.authenticate(db, body.username, body.password)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login yoki parol noto'g'ri",
        )
    token = create_access_token(admin.id, {"role": admin.role})
    return TokenOut(access_token=token)


@router.get("/me", response_model=AdminOut)
async def me(admin: Admin = Depends(get_current_admin)):
    return admin
