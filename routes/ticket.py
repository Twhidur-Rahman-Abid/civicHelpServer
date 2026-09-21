from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query, File, Form, UploadFile, status

from dependencies.auth import  CurrentUser
from models.enums import TicketType, TicketPriority, TicketStatus
from schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketStatusUpdate,
    TicketFilterParams,
    TicketResponse,
    TicketPaginatedResponse,
)
from services import ticket_services
from db.db import db_dependency

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ticket with mandatory cover image and optional additional images",
)
def create_ticket(
    db: db_dependency,
    current_user: CurrentUser,
    title: str = Form(..., min_length=3, max_length=150),
    description: str = Form(..., min_length=10),
    location: str = Form(..., max_length=255),
    type: TicketType = Form(...),
    priority: TicketPriority = Form(TicketPriority.MEDIUM),
    image: UploadFile = File(...),  
    images: Optional[List[UploadFile]] = File(None), 
):
    ticket_in = TicketCreate(
        title=title,
        description=description,
        location=location,
        type=type,
        priority=priority,
    )
    return ticket_services.create_ticket(
        db=db,
        user_id=current_user.id,
        ticket_in=ticket_in,
        image=image,
        images=images,
    )


@router.get(
    "/",
    response_model=Union[TicketPaginatedResponse, List[TicketResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get all tickets with filters, search, and dynamic pagination",
)
def get_all_tickets(
    db: db_dependency,
    ticket_status: Optional[TicketStatus] = Query(None, alias="status"),
    ticket_type: Optional[TicketType] = Query(None, alias="type"),
    priority: Optional[TicketPriority] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    paginate: bool = Query(True),
):
    params = TicketFilterParams(
        status=ticket_status,
        type=ticket_type,
        priority=priority,
        search=search,
        page=page,
        limit=limit,
        paginate=paginate,
    )
    return ticket_services.get_tickets(db=db, params=params)


@router.get(
    "/my-tickets",
    response_model=Union[TicketPaginatedResponse, List[TicketResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get current user's submitted tickets",
)
def get_my_tickets(
    db: db_dependency,
    current_user: CurrentUser,
    ticket_status: Optional[TicketStatus] = Query(None, alias="status"),
    ticket_type: Optional[TicketType] = Query(None, alias="type"),
    priority: Optional[TicketPriority] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    paginate: bool = Query(True),
):
    params = TicketFilterParams(
        status=ticket_status,
        type=ticket_type,
        priority=priority,
        search=search,
        page=page,
        limit=limit,
        paginate=paginate,
    )
    return ticket_services.get_tickets(db=db, params=params, user_id=current_user.id)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a ticket by ID",
)
def get_ticket(ticket_id: int, db: db_dependency):
    return ticket_services.get_ticket_by_id(db=db, ticket_id=ticket_id)


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a ticket (Owner only)",
)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: db_dependency,
    current_user: CurrentUser,
):
    return ticket_services.update_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
        ticket_update=ticket_update,
    )


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Update ticket status",
)
def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    db: db_dependency,
    current_user: CurrentUser,
):
    return ticket_services.update_ticket_status(
        db=db,
        ticket_id=ticket_id,
        new_status=status_update.status,
    )


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a ticket (Owner only)",
)
def delete_ticket(
    ticket_id: int,
    db: db_dependency,
    current_user: CurrentUser,
):
    return ticket_services.delete_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
    )