from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SkyPionners API",
    description="API Backend avec authentification et email",
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

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "skypionners-api"}

@app.get("/")
def read_root():
    return {"message": "SkyPionners API is running!"}

print("✅ Application minimale créée")
