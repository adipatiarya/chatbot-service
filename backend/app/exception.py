from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exception import DuplicateEntryError
from app.core.config import settings


async def duplicate_entry_handler(_, exc: DuplicateEntryError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

async def global_exception_handler(request: Request, exc: Exception):
    if settings.ENV != "prod":
        # tampilkan semua detail error (traceback, type, dll)
        return JSONResponse(
            status_code=500,
            content={
                "error_type": exc.__class__.__name__,
                "detail": str(exc),
                "path": request.url.path
            }
        )
    else:
        # production → pesan aman
        return JSONResponse(
            status_code=500,
            content={"detail": "Terjadi kesalahan internal"}
        )