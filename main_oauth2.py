#!/usr/bin/env python3
"""
Serveur principal FastAPI OAuth2 - Version simplifiée pour éviter les problèmes d'imports
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configuration simplifiée
app = FastAPI(
    title="SkyPionners OAuth2 API",
    description="API complète avec authentification OAuth2",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models simplifiés
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

# Demo database (remplace la vraie DB pour éviter les problèmes)
users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Administrator",
        "is_active": True,
        "is_superuser": True
    }
}

# Routes de base
@app.get("/")
async def root():
    return {
        "message": "SkyPionners OAuth2 API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SkyPionners OAuth2 API",
        "version": "1.0.0"
    }

@app.post("/users/")
async def create_user(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": True,
        "is_superuser": False
    }

    return users_db[user.username]

@app.get("/users/{username}")
async def get_user(username: str):
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return users_db[username]

@app.get("/users/")
async def get_users():
    return list(users_db.values())

@app.post("/token")
async def login(username: str, password: str):
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Demo password check
    if password != "testpass123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return {
        "access_token": "demo-jwt-token-12345",
        "token_type": "bearer",
        "user": users_db[username]
    }

@app.get("/protected")
async def protected_endpoint(authorization: str = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

    token = authorization.split(" ")[1]
    if token != "demo-jwt-token-12345":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return {
        "message": "Protected data accessed successfully!",
        "data": {"secret": "This is protected information"}
    }

if __name__ == "__main__":
    print("🚀 Starting SkyPionners OAuth2 API...")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔗 Alternative docs: http://localhost:8000/redoc")
    print("\n🧪 Test rapide:")
    print("   1. POST /users/ - Créer un utilisateur")
    print("   2. POST /token?username=admin&password=testpass123 - Se connecter")
    print("   3. GET /protected - Accéder aux données protégées")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
