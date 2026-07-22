"""
ServiceBot - Asistente Virtual para Negocios de Servicios
FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.whatsapp.webhook import router as webhook_router

app = FastAPI(
    title=settings.app_name,
    description="Asistente virtual inteligente para negocios de servicios vía WhatsApp",
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

# Routers
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.app_name,
        "version": "1.0.0",
        "message": "ServiceBot está funcionando correctamente 🚀"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
