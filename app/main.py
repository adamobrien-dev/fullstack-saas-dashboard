from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def root():
    return {"service": "Full-Stack SaaS Dashboard", "docs": "/docs"}
    
@app.get('/health')
def health():
    return {'status':'ok'}
