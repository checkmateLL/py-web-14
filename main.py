import logging
import sys
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from src.routes import auth, contacts
from src.services.rate_limiter import add_rate_limiting

sys.path.append("./src")

logging.basicConfig(level=logging.DEBUG)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_rate_limiting(app)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}