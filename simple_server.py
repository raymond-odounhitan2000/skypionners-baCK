#!/usr/bin/env python3
"""
Serveur FastAPI OAuth2 Ultra-Simple
"""

from fastapi import FastAPI

app = FastAPI(title="SkyPionners API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "SkyPionners OAuth2 API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/docs")
async def docs():
    return {"message": "Documentation available at /docs"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting simple API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
