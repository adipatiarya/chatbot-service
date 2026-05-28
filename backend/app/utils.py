import logging
import jwt
from datetime import timedelta, timezone, datetime
from typing import TYPE_CHECKING, Any, Dict
from pathlib import Path
from dataclasses import dataclass


from app.core.config import settings
from jinja2 import Template

import colorlog




handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(green)s%(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }
))

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)



@dataclass
class EmailData:
    html_content:str
    subject:str


def render_email_template(*, template_name:str, context:dict[str, Any]) -> str:
    path = Path(__file__).parent / "email-templates" / "build" / template_name
    template_html = path.read_text()
    html_content = Template(template_html).render(context)
    return html_content

def generate_password_reset_token(*, email:str) -> str :
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    payload = {"exp": exp, "nbf": now, "sub": email}
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def generate_reset_password_email(*, email_to:str, email:str, token:str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"

    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name":project_name, 
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link
        }
    )
    return EmailData(html_content=html_content, subject=subject)

def verify_password_reset_token(*, token:str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except jwt.exceptions.InvalidTokenError:
        return None
    
def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)

modules = ["user", "role"]

def all_perms() -> Dict[str, Dict[str, bool]]:
    actions = ["create", "view", "update", "delete"]
   
    return {
        resource: {f"can_{action}_{resource}": False for action in actions}
        for resource in modules
    }

def apply_permissions(base: Dict[str, Dict[str, bool]], allowed: list[str]) -> Dict[str, Dict[str, bool]]:
    for _, perms in base.items():
        for perm_name in perms.keys():
            if perm_name in allowed:
                perms[perm_name] = True
    return base

def extract_true_permissions(permission_dict: dict[str, dict[str, bool]]) -> list[str]:
    result = []
    for _, perms in permission_dict.items():
        for perm_name, value in perms.items():
            if value:  # hanya ambil yang True
                result.append(perm_name)
    return result

def extract_all_permissions() -> list[str]:
    result = []
    for _, perms in all_perms().items():
        for perm_name, _ in perms.items():
            result.append(perm_name)
    return result

#untuk mengatasi circullar import
if TYPE_CHECKING:
    from app.services.role_service import RoleService

async def seed_permission_all(service: "RoleService") -> None:
    
    result = []
    for _, perms in all_perms().items():
        for perm_name, _ in perms.items():
            result.append(perm_name)

    #logger.info(f'SEED DIPANGGIL {result}')
    await service.create_permissions(result)

