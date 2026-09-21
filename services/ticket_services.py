import math
from typing import List, Optional, Union
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, UploadFile

from models.ticket import Ticket, TicketImage, TicketStatus
from schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketFilterParams,
    TicketResponse,
    TicketPaginatedResponse,
)
from utils.file_upload import save_multiple_images, save_upload_image, save_upload_image


def create_ticket(
    db: Session,
    user_id: int,
    ticket_in: TicketCreate,
    image: UploadFile,  
    images: Optional[List[UploadFile]] = None  
) -> Ticket:
    try:
        # Mandatory cover/main image save
        main_image_url = save_upload_image(image, upload_subfolder="tickets")

        new_ticket = Ticket(
            user_id=user_id,
            type=ticket_in.type,
            title=ticket_in.title,
            description=ticket_in.description,
            location=ticket_in.location,
            priority=ticket_in.priority,
            image_url=main_image_url
        )
        db.add(new_ticket)
        db.flush()

        # Save optional additional gallery images to ticket_images table
        gallery_urls = save_multiple_images(images, upload_subfolder="tickets")
        for url in gallery_urls:
            ticket_img = TicketImage(
                ticket_id=new_ticket.id,
                image_url=url
            )
            db.add(ticket_img)

        db.commit()
        db.refresh(new_ticket)
        return new_ticket

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating ticket"
        ) from e


def get_tickets(
    db: Session,
    params: TicketFilterParams,
    user_id: Optional[int] = None
) -> Union[TicketPaginatedResponse, List[TicketResponse]]:
    try:
        query = db.query(Ticket)

        if user_id:
            query = query.filter(Ticket.user_id == user_id)
        if params.status:
            query = query.filter(Ticket.status == params.status)
        if params.type:
            query = query.filter(Ticket.type == params.type)
        if params.priority:
            query = query.filter(Ticket.priority == params.priority)
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    Ticket.title.ilike(search_term),
                    Ticket.description.ilike(search_term),
                    Ticket.location.ilike(search_term)
                )
            )

        query = query.order_by(Ticket.created_at.desc())

        # Pagination OFF check
        if not params.paginate:
            raw_tickets = query.all()
            return [TicketResponse.model_validate(t) for t in raw_tickets]

        # Pagination ON
        total = query.count()
        total_pages = math.ceil(total / params.limit) if total > 0 else 1
        offset = (params.page - 1) * params.limit

        tickets = query.offset(offset).limit(params.limit).all()
        ticket_items = [TicketResponse.model_validate(t) for t in tickets]

        return TicketPaginatedResponse(
            items=ticket_items,
            total=total,
            page=params.page,
            limit=params.limit,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_prev=params.page > 1
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching tickets"
        ) from e


def get_ticket_by_id(db: Session, ticket_id: int) -> Ticket:
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        return ticket
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching ticket"
        ) from e


def update_ticket(
    db: Session,
    ticket_id: int,
    user_id: int,
    ticket_update: TicketUpdate
) -> Ticket:
    ticket = get_ticket_by_id(db, ticket_id)

    if ticket.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this ticket"
        )

    try:
        update_data = ticket_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ticket, key, value)

        db.commit()
        db.refresh(ticket)
        return ticket

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating ticket"
        ) from e


def update_ticket_status(
    db: Session,
    ticket_id: int,
    new_status: TicketStatus
) -> Ticket:
    ticket = get_ticket_by_id(db, ticket_id)
    try:
        ticket.status = new_status
        db.commit()
        db.refresh(ticket)
        return ticket
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating status"
        ) from e


def delete_ticket(db: Session, ticket_id: int, user_id: int) -> dict:
    ticket = get_ticket_by_id(db, ticket_id)

    if ticket.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this ticket"
        )

    try:
        db.delete(ticket)
        db.commit()
        return {"message": "Ticket deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deleting ticket"
        ) from e