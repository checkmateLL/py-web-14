from sqlalchemy import and_, or_, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactUpdate
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)

async def create_contact(
    body: ContactCreate, 
    current_user: User, 
    db: AsyncSession
) -> Contact:
    """
    Create a new contact with error handling.
    """
    try:
        new_contact = Contact(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone=body.phone,
            birthday=body.birthday,
            additional_info=body.additional_info,
            owner_id=current_user.id
        )

        db.add(new_contact)
        await db.commit()
        await db.refresh(new_contact)
        return new_contact

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error creating contact: {e}")
        raise ValueError("Contact could not be created due to database constraints")
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error creating contact: {e}")
        raise

async def get_contacts(
    current_user: User, 
    db: AsyncSession,
    name: str = None,
    email: str = None,
    upcoming_birthdays: bool = False
) -> list[Contact]:
    """
    Retrieve contact.
    """
    try:
        query = select(Contact).filter(Contact.owner_id == current_user.id)

        # Name-based filtering
        if name:
            query = query.filter(
                or_(
                    func.lower(Contact.first_name).contains(func.lower(name)),
                    func.lower(Contact.last_name).contains(func.lower(name))
                )
            )

        # Email-based filtering
        if email:
            query = query.filter(func.lower(Contact.email).contains(func.lower(email)))

        # Upcoming birthdays filter
        if upcoming_birthdays:
            today = datetime.now()
            week_later = today + timedelta(days=7)
            query = query.filter(
                and_(
                    func.extract('month', Contact.birthday) >= today.month,
                    func.extract('day', Contact.birthday) >= today.day,
                    func.extract('month', Contact.birthday) <= week_later.month,
                    func.extract('day', Contact.birthday) <= week_later.day
                )
            )

        result = await db.execute(query)
        return result.scalars().all()

    except Exception as e:
        logger.error(f"Error retrieving contacts: {e}")
        raise