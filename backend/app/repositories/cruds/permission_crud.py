
from .crud import Crud
from app.models.permission import Permission

class PermissionCrud(Crud[Permission]):
    def __init__(self, session):
        super().__init__(session, Permission)

    async def roles(self):
        pass