"""Payme webhook — JSON-RPC 2.0 (merchant API).

Payme HTTP Basic auth bilan keladi: login "Paycom", parol — kassa kaliti
(PAYME_KEY). Javob doim HTTP 200, ichida result yoki error (Payme talabi).
"""
import base64
import binascii

from fastapi import APIRouter, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.payme import ERR_AUTH, PaymeError, handle
from app.services.payme import _msg  # uch tilli xabar

from fastapi import Depends

router = APIRouter(prefix="/payme", tags=["payme"])


def _check_auth(request: Request) -> bool:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header[6:]).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return False
    # "Paycom:<key>"
    _, _, key = decoded.partition(":")
    return bool(settings.payme_key) and key == settings.payme_key


@router.post("")
async def payme_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    req_id = body.get("id")

    if not settings.payme_enabled:
        return {"error": {"code": ERR_AUTH, "message": _msg("Payme o'chirilgan")}, "id": req_id}

    if not _check_auth(request):
        return {"error": {"code": ERR_AUTH, "message": _msg("Avtorizatsiya xatosi")}, "id": req_id}

    method = body.get("method", "")
    params = body.get("params", {}) or {}

    try:
        result = await handle(db, method, params)
        return {"result": result, "id": req_id}
    except PaymeError as exc:
        err: dict = {"code": exc.code, "message": exc.message}
        if exc.data is not None:
            err["data"] = exc.data
        return {"error": err, "id": req_id}
