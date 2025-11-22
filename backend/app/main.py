from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import auth, organization, analytics, test_email

app = FastAPI(title="Full-Stack SaaS Dashboard", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",  # Allow all localhost ports for development
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
app.include_router(test_email.router, prefix="/test", tags=["testing"])
