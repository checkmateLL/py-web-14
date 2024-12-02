from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler for rate limit exceeded exceptions.
    """
    return HTTPException(
        status_code=429, 
        detail="Too many requests. Please try again later."
    )

def add_rate_limiting(app):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)