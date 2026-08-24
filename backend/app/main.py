from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import flows, statistics, alerts, policy, live
from dpi.policies.blocklist import seed_default_blocklist

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# CORS allow karo — dashboard HTML file se API calls chal sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flows.router)
app.include_router(statistics.router)
app.include_router(alerts.router)
app.include_router(policy.router)
app.include_router(live.router) 

@app.on_event("startup")
def startup_event():
    seed_default_blocklist()


@app.get("/")
def root():
    return {"message": "DPI Network Platform is running", "version": settings.APP_VERSION}


@app.get("/health")
def health():
    return {"status": "ok", "debug_mode": settings.DEBUG}