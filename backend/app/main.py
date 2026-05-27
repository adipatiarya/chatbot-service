from fastapi import FastAPI
from app.api.main import api_router
from app.core.config import settings
from app.core.exception import DuplicateEntryError
from app.exception import duplicate_entry_handler, global_exception_handler

app = FastAPI(openapi_url=f"{settings.API_V1_STR}/openapi.json")


app.add_exception_handler(DuplicateEntryError, duplicate_entry_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)

