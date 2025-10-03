from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import User, UserCreate, UserUpdate
from app.services.auth_service import (
    create_user,
    get_users,
    get_user_by_username,
    get_user_by_email,
    get_current_active_user
)
from app.services.email_service import send_welcome_email
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if user already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create the user
    db_user = create_user(db=db, user=user)

    # Send welcome email automatically
    try:
        await send_welcome_email(db_user.email, db_user.username)
        print(f"✅ Email de bienvenue envoyé à {db_user.email}")
    except Exception as e:
        print(f"⚠️ Avertissement: Email non envoyé - {e}")
        # Ne pas empêcher la création d utilisateur si l email échoue

    return db_user

@router.get("/", response_model=List[User])
def read_users(
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all users with pagination."""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=User)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user info."""
    return current_user

@router.get("/{username}", response_model=User)
def read_user(
    username: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a user by username."""
    db_user = get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.put("/{username}", response_model=User)
def update_user(
    username: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a user."""
    db_user = get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password" and value:
            from app.services.auth_service import get_password_hash
            value = get_password_hash(value)
            field = "hashed_password"
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

@router.patch("/{username}/status")
def toggle_user_status(
    username: str,
    is_active: bool,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Activate or deactivate a user account."""
    # Only superusers can manage user status
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    db_user = get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_user.is_active = is_active
    db.commit()
    db.refresh(db_user)

    status_text = "activated" if is_active else "deactivated"
    return {
        "message": f"User {username} has been {status_text}",
        "user": db_user
    }

@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    username: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a user."""
    db_user = get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
