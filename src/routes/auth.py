from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.users import UserCreate, UserResponse, TokenResponse, RequestEmail, SignupResponse
from src.repository import users as repository_users
from src.database.db import get_db
from src.services.auth import get_auth_service, get_current_user
from src.services.email import email_service
from src.database.models import User
from src.schemas.users import LoginForm
from fastapi import Body
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = get_auth_service()

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db)
    
):
    # Check if the user already exists
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    # Hash the password
    body.password = auth_service.get_password_hash(body.password)

    # Create the new user
    new_user = await repository_users.create_user(body, db)

    # Send welcome email
    await email_service.send_email(
    recipient=new_user.email, 
    username=new_user.username
)

    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: LoginForm = Body(...), db: AsyncSession = Depends(get_db)
):
    user = await repository_users.get_user_by_email(form_data.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    is_password_valid = auth_service.verify_password(form_data.password, user.password)
    logger.debug(f"Password valid: {is_password_valid}")  # Debug log for password validity

    if not is_password_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(
    body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    background_tasks.add_task(email_service.send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    refresh_token: str = Form(...), db: AsyncSession = Depends(get_db)
):
    email = await auth_service.get_email_from_token(refresh_token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    new_refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, new_refresh_token, db)
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.post("/reset-password")
async def reset_password(
    token: str, 
    new_password: str, 
    db: AsyncSession = Depends(get_db)
):
    try:
        # Verify the reset token
        email = await auth_service.get_email_from_token(token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid or expired reset token"
            )
        
        # Update user's password
        user = await repository_users.get_user_by_email(email, db)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        
        # Hash and update password
        hashed_password = auth_service.get_password_hash(new_password)
        user.password = hashed_password
        
        await db.commit()
        
        return {"message": "Password successfully reset"}
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Password reset failed"
        )