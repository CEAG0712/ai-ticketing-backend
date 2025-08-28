from pydantic import BaseModel, Field

class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1, max_length=10_000)