import random
import string
from httpx import AsyncClient

from app.core.config import settings

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase,k=20))

def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com" 

permissions_test: list[str] = ['can_create_user','can_update_user','can_create_role', 'can_view_user'] 