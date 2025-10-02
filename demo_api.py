#!/usr/bin/env python3
"""
Serveur de démonstration FastAPI OAuth2
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="SkyPionners OAuth2 API",
    description="API de démonstration avec authentification OAuth2",
    version="1.0.0"
)

# Security scheme
security = HTTPBearer()

# Demo data
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": "$demo$testpass123",
        "disabled": False,
    }
}

# Models
class User(BaseModel):
    username: str
    email: str
    full_name: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Demo functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Simple demo password verification."""
    return plain_password == "testpass123"

def get_user(username: str):
    """Get user from demo database."""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return User(**user_dict)
    return None

# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to SkyPionners OAuth2 API!",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SkyPionners OAuth2 API",
        "version": "1.0.0"
    }

@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user (demo)."""
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Add user to demo database
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": f"$demo${user.password}",
        "disabled": False,
    }

    return User(**fake_users_db[user.username])

@app.get("/users/{username}", response_model=User)
async def get_user_by_username(username: str):
    """Get a user by username."""
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(username: str, password: str):
    """OAuth2 token endpoint (demo)."""
    user = get_user(username)
    if not user or not verify_password(password, "$demo$testpass123"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return demo token
    return Token(
        access_token="demo-jwt-token-12345",
        token_type="bearer"
    )

@app.get("/protected")
async def protected_endpoint(token: str = Depends(security)):
    """Protected endpoint requiring authentication."""
    if token.credentials != "demo-jwt-token-12345":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return {
        "message": "This is protected data!",
        "user": "testuser",
        "data": {"secret": "You have access to protected resources"}
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SkyPionners OAuth2 Demo API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔗 Alternative docs: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)
