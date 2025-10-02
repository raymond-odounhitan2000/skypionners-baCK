#!/usr/bin/env python3
"""
Serveur de démonstration FastAPI OAuth2 - Version simplifiée
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="SkyPionners OAuth2 API",
    description="API de démonstration avec authentification OAuth2",
    version="1.0.0"
)

# Demo data
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
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

@app.post("/users/")
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
        "disabled": False,
    }

    return {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "message": "User created successfully"
    }

@app.get("/users/{username}")
async def get_user_by_username(username: str):
    """Get a user by username."""
    if username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user = fake_users_db[username]
    return User(**user)

@app.post("/login")
async def login(username: str, password: str):
    """Simple login endpoint (demo)."""
    if username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if password != "testpass123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Return demo token
    return {
        "access_token": "demo-jwt-token-12345",
        "token_type": "bearer",
        "user": fake_users_db[username]
    }

@app.get("/protected")
async def protected_endpoint(authorization: str = None):
    """Protected endpoint requiring authentication."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]
    if token != "demo-jwt-token-12345":
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
    print("\n🧪 Test the API:")
    print("   1. Create user: POST /users/ with JSON body")
    print("   2. Login: POST /login?username=testuser&password=testpass123")
    print("   3. Access protected: GET /protected with Authorization: Bearer demo-jwt-token-12345")
    uvicorn.run(app, host="0.0.0.0", port=8000)
