from enum import Enum

class UserRole(str, Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"

class TicketType(str, Enum):
    COMPLAINT = "complaint"
    SERVICE_REQUEST = "service_request"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TicketStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"