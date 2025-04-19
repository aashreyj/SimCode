from typing import Optional

from app.models.role_model import Role
from app.models.user_model import User
from sqlalchemy.orm import Session


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def is_valid_role(db: Session, role_name: str) -> bool:
    return db.query(Role).filter(Role.role_type == role_name).first() is not None

def create_user(db: Session, username: str, email: str, hashed_password: str, role: str) -> User:
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role_of_user=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_default_roles(db: Session):
    roles = ["viewer", "editor", "host"]
    for role_name in roles:
        if not db.query(Role).filter(Role.role_type == role_name).first():
            role = Role(role_type=role_name)
            db.add(role)
            print(f"{role} added")
        else:
            print(f"{role_name} role already present in db")
            
    db.commit()
