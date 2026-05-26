import random
import string
from httpx import AsyncClient

from app.core.config import settings

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase,k=20))

def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com" 