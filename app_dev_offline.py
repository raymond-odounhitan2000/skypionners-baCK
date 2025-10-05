from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import uvicorn
import json
from datetime import datetime

# Modèles de données temporaires
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_verified: bool
    created_at: str

# Stockage temporaire en mémoire (au lieu de la base de données)
users_db = []
next_id = 1

# Créer l application
app = FastAPI(
    title="Skypionners Backend API (Mode Développement)",
    description="Version temporaire sans connexion réseau externe",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "API Skypionners en mode développement",
        "status": "active",
        "mode": "offline_development",
        "users_in_memory": len(users_db)
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "database": "memory_only",
        "network": "offline"
    }

# Endpoint pour créer un utilisateur (simulation)
@app.post("/api/v1/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    global next_id
    
    # Vérifier si l utilisateur existe déjà
    for existing_user in users_db:
        if existing_user["email"] == user.email or existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Utilisateur existe déjà")
    
    # Créer le nouvel utilisateur
    new_user = {
        "id": next_id,
        "username": user.username,
        "email": user.email,
        "is_verified": False,
        "created_at": datetime.now().isoformat()
    }
    
    users_db.append(new_user)
    next_id += 1
    
    return UserResponse(**new_user)

# Endpoint pour lister les utilisateurs
@app.get("/api/v1/users/", response_model=list[UserResponse])
async def get_users():
    return [UserResponse(**user) for user in users_db]

# Endpoint pour tester les emails (simulation)
@app.post("/api/v1/test-email")
async def test_email_endpoint():
    return {
        "message": "Email envoyé avec succès (simulation)",
        "recipient": "kevine.idohou@gmail.com",
        "note": "En mode développement, pas d envoi réel",
        "timestamp": datetime.now().isoformat()
    }

# Documentation
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return {
        "message": "Documentation disponible",
        "docs_url": "http://localhost:8000/docs",
        "note": "Utilisez /docs pour voir l interface Swagger"
    }

if __name__ == "__main__":
    print("🚀 Démarrage de l API en mode développement...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
