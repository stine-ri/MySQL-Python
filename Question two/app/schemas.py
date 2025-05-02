# app/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date
from enum import Enum

# Enums for validation
class BookStatus(str, Enum):
    available = "available"
    checked_out = "checked_out"
    lost = "lost"

class MemberStatus(str, Enum):
    active = "active"
    expired = "expired"
    suspended = "suspended"

class LoanStatus(str, Enum):
    active = "active"
    returned = "returned"
    overdue = "overdue"

# Base schemas for creation/update
class BookBase(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=20, example="978-0451524935")
    title: str = Field(..., min_length=1, max_length=200, example="1984")
    publication_year: Optional[int] = Field(None, ge=1800, le=date.today().year)
    genre: Optional[str] = Field(None, max_length=50, example="Dystopian")
    total_copies: int = Field(1, ge=1)
    available_copies: int = Field(1, ge=0)

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    publication_year: Optional[int] = Field(None, ge=1800, le=date.today().year)
    genre: Optional[str] = Field(None, max_length=50)
    total_copies: Optional[int] = Field(None, ge=1)
    available_copies: Optional[int] = Field(None, ge=0)

class MemberBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, example="John")
    last_name: str = Field(..., min_length=1, max_length=50, example="Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, example="+1234567890")

class MemberCreate(MemberBase):
    pass

class MemberUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)

class LoanBase(BaseModel):
    book_id: int = Field(..., gt=0, example=1)
    member_id: int = Field(..., gt=0, example=1)

class LoanCreate(LoanBase):
    pass

# Response schemas
class BookResponse(BookBase):
    book_id: int
    status: Optional[BookStatus] = None

    class Config:
        orm_mode = True

class MemberResponse(MemberBase):
    member_id: int
    join_date: date
    membership_status: MemberStatus

    class Config:
        orm_mode = True

class LoanResponse(LoanBase):
    loan_id: int
    loan_date: date
    due_date: date
    return_date: Optional[date] = None
    status: LoanStatus

    class Config:
        orm_mode = True

# Relationship schemas
class BookWithLoans(BookResponse):
    loans: list["LoanResponse"] = []

class MemberWithLoans(MemberResponse):
    loans: list["LoanResponse"] = []

class LoanWithDetails(LoanResponse):
    book: BookResponse
    member: MemberResponse

# Update forward references for recursive models
BookWithLoans.update_forward_refs()
MemberWithLoans.update_forward_refs()