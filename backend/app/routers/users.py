from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserOut
from app.services.user_service import get_user_by_id

router = APIRouter()


@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/{id}", response_model=UserOut)
def get_user_by_id_endpoint(
    id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only allow access to the current user's own data.
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user = get_user_by_id(db, user_id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
