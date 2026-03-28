from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserProfileUpdate


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def update_user_profile(db: Session, user: User, body: UserProfileUpdate) -> User:
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

