import enum
from datetime import datetime, timezone
from sqlalchemy import String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from .base import Base
from .enums import TicketType, TicketPriority, TicketStatus

if TYPE_CHECKING:
    from .user import User


class TicketImage(Base):
    __tablename__ = "ticket_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    ticket: Mapped["Ticket"] = relationship(back_populates="images")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    type: Mapped[TicketType] = mapped_column(
        Enum(TicketType, native_enum=False),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)



    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority, native_enum=False),
        default=TicketPriority.MEDIUM,
        nullable=False
    )

    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, native_enum=False),
        default=TicketStatus.PENDING,
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="tickets")

    
    images: Mapped[List["TicketImage"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan"
    )