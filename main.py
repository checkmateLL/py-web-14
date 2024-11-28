import logging

from fastapi import FastAPI
from src.routes import auth, contacts

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(debug=True)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])