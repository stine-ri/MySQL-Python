from pydantic import BaseModel
from typing import Optional
from datetime import date

# Base models with validation
class BookBase(BaseModel):
    isbn: str
    title: str
    publication_year: Optional[int] = None
    genre: Optional[str] = None
    total_copies: int = 1
    available_copies: int = 1

    class Config:
        schema_extra = {
            "example": {
                "isbn": "978-0451524935",
                "title": "1984",
                "publication_year": 1949,
                "genre": "Dystopian",
                "total_copies": 5,
                "available_copies": 3
            }
        }

class MemberBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

class LoanBase(BaseModel):
    book_id: int
    member_id: int

# Response models
class Book(BookBase):
    book_id: int
    
    class Config:
        orm_mode = True

class Member(MemberBase):
    member_id: int
    join_date: date
    membership_status: str
    
    class Config:
        orm_mode = True

class Loan(LoanBase):
    loan_id: int
    loan_date: date
    due_date: date
    return_date: Optional[date] = None
    status: str
    
    class Config:
        orm_mode = True