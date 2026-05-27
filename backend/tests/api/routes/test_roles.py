import pytest
from httpx import AsyncClient

from app.utils import logger
from app.core.config import settings

@pytest.mark.asyncio
async def test_create_roles(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    payload = {
        'name':'roleku',
        'permission':['can_create_user', 'can_update_user'],
        'description':'sih'
    }

    r = await client.post(f"{settings.API_V1_STR}/roles", headers=superuser_token_headers, json=payload)
    resp = r.json()
    logger.info(resp)
    assert 201 == r.status_code