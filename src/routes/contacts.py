from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse
from src.repository import contacts as repository_contacts
from src.database.db import get_db
from src.services.auth import get_current_user
from src.database.models import User

router = APIRouter()

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    new_contact = await repository_contacts.create_contact(body, current_user, db)
    return new_contact

@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    contacts = await repository_contacts.get_contacts(current_user, db)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int, body: ContactUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    updated_contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if not updated_contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return updated_contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    deleted = await repository_contacts.delete_contact(contact_id, current_user, db)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")