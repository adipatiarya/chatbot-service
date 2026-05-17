
from sqlmodel import Session
from app.models import UserCreate, User
from app.core.security import get_password_hash

def create_user(*, session: Session, user_create: UserCreate) -> User:
    try:
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)}
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    except Exception as e:
        session.rollback()   # penting: balikin transaksi kalau gagal
        print(f"Error saat create_user: {e}")
        raise  # lempar lagi supaya bisa ditangani di level atas
