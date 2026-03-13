from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import equipment, batteries, measurements, incidents, reports

app = FastAPI(
    title="Battery Monitoring System API",
    description="API для системы мониторинга состояния батарей автономного оборудования",
    version="1.0.0"
)

# CORS middleware - дозволяємо ВСІ origins для ngrok
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(equipment.router)
app.include_router(batteries.router)
app.include_router(measurements.router)
app.include_router(incidents.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {
        "message": "Battery Monitoring System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
