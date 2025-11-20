from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import auth, organization, analytics

app = FastAPI(title="Full-Stack SaaS Dashboard", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"service": "Full-Stack SaaS Dashboard", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(organization.router, tags=["organizations"])
app.include_router(analytics.router, tags=["analytics"])
