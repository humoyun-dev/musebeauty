"""Admin: rasm yuklash — mahsulot rasmlari uchun.

POST /api/admin/upload (multipart) → {"url": "/media/products/<...>.jpg"}.
Admin panel shu URL'ni product.image_url ga yozadi.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.api.admin.deps import get_current_admin
from app.core.storage import UploadError, save_image

router = APIRouter(tags=["admin-upload"], dependencies=[Depends(get_current_admin)])


@router.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()
    try:
        url = await save_image(content, file.filename or "image")
    except UploadError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"url": url}
