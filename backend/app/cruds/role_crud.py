from app.models.role import Role
from backend.app.cruds.crud import Crud

class RoleCrud(Crud[Role]):
    def __init__(self, session):
        super().__init__(session, Role)
