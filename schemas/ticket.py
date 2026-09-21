from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from models.enums import TicketPriority, TicketStatus, TicketType


# --- Image Schemas ---
class TicketImageResponse(BaseModel):
    id: int
    ticket_id: int
    image_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Base Ticket Schema ---
class TicketBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=10)
    location: str = Field(..., max_length=255)
    type: TicketType
    priority: TicketPriority = TicketPriority.MEDIUM


# --- Request Schemas ---
class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=150)
    description: Optional[str] = Field(None, min_length=10)
    location: Optional[str] = Field(None, max_length=255)
    type: Optional[TicketType] = None
    priority: Optional[TicketPriority] = None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


# --- Query Parameters for Filtering & Dynamic Pagination ---
class TicketFilterParams(BaseModel):
    status: Optional[TicketStatus] = None
    type: Optional[TicketType] = None
    priority: Optional[TicketPriority] = None
    search: Optional[str] = None
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    paginate: bool = True  


# --- Response Schemas ---
class TicketResponse(TicketBase):
    id: int
    user_id: int
    image_url: Optional[str] = None
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    images: List[TicketImageResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- Concrete Paginated Response ---
class TicketPaginatedResponse(BaseModel):
    items: List[TicketResponse]
    total: int
    page: Optional[int] = None
    limit: Optional[int] = None
    total_pages: Optional[int] = None
    has_next: bool = False
    has_prev: bool = False