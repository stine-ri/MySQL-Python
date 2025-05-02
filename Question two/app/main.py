# app/main.py
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import date, timedelta
import mysql.connector
from . import schemas, database

app = FastAPI(
    title="Library Management API",
    description="A complete CRUD API for library operations",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB connection
def get_db():
    connection = database.get_db_connection()
    try:
        yield connection
    finally:
        connection.close()

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy"}

# BOOKS ENDPOINTS
@app.post("/books/", 
          response_model=schemas.BookResponse, 
          status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, connection = Depends(get_db)):
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if ISBN already exists
        cursor.execute("SELECT book_id FROM books WHERE isbn = %s", (book.isbn,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISBN already exists"
            )

        query = """
        INSERT INTO books (isbn, title, publication_year, genre, total_copies, available_copies)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            book.isbn, book.title, book.publication_year, 
            book.genre, book.total_copies, book.available_copies
        )
        
        cursor.execute(query, values)
        connection.commit()
        book_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        new_book = cursor.fetchone()
        
        return new_book
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {err}"
        )
    finally:
        cursor.close()

@app.get("/books/", response_model=List[schemas.BookResponse])
def read_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    connection = Depends(get_db)
):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM books LIMIT %s OFFSET %s", (limit, skip))
        books = cursor.fetchall()
        return books
    finally:
        cursor.close()

@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def read_book(book_id: int, connection = Depends(get_db)):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book
    finally:
        cursor.close()

@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int, 
    book: schemas.BookUpdate, 
    connection = Depends(get_db)
):
    cursor = connection.cursor(dictionary=True)
    try:
        # Check if book exists
        cursor.execute("SELECT 1 FROM books WHERE book_id = %s", (book_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        # Build dynamic update query
        update_fields = []
        values = []
        
        if book.title is not None:
            update_fields.append("title = %s")
            values.append(book.title)
        if book.publication_year is not None:
            update_fields.append("publication_year = %s")
            values.append(book.publication_year)
        if book.genre is not None:
            update_fields.append("genre = %s")
            values.append(book.genre)
        if book.total_copies is not None:
            update_fields.append("total_copies = %s")
            values.append(book.total_copies)
        if book.available_copies is not None:
            update_fields.append("available_copies = %s")
            values.append(book.available_copies)

        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        query = f"UPDATE books SET {', '.join(update_fields)} WHERE book_id = %s"
        values.append(book_id)
        
        cursor.execute(query, values)
        connection.commit()
        
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        updated_book = cursor.fetchone()
        
        return updated_book
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {err}"
        )
    finally:
        cursor.close()

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, connection = Depends(get_db)):
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
    finally:
        cursor.close()

# MEMBERS ENDPOINTS
@app.post("/members/", 
          response_model=schemas.MemberResponse, 
          status_code=status.HTTP_201_CREATED)
def create_member(member: schemas.MemberCreate, connection = Depends(get_db)):
    cursor = connection.cursor(dictionary=True)
    try:
        # Check if email already exists
        cursor.execute("SELECT member_id FROM members WHERE email = %s", (member.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        query = """
        INSERT INTO members (first_name, last_name, email, phone)
        VALUES (%s, %s, %s, %s)
        """
        values = (
            member.first_name, member.last_name, 
            member.email, member.phone
        )
        
        cursor.execute(query, values)
        connection.commit()
        member_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
        new_member = cursor.fetchone()
        
        return new_member
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {err}"
        )
    finally:
        cursor.close()

# [Similar GET, PUT, DELETE endpoints for members would go here]

# LOANS ENDPOINTS
@app.post("/loans/", 
          response_model=schemas.LoanResponse, 
          status_code=status.HTTP_201_CREATED)
def create_loan(loan: schemas.LoanCreate, connection = Depends(get_db)):
    cursor = connection.cursor(dictionary=True)
    try:
        # Check book availability
        cursor.execute("""
            SELECT available_copies 
            FROM books 
            WHERE book_id = %s 
            FOR UPDATE
        """, (loan.book_id,))
        book = cursor.fetchone()
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        if book['available_copies'] < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available copies of this book"
            )
        
        # Check member exists
        cursor.execute("SELECT 1 FROM members WHERE member_id = %s", (loan.member_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
        
        # Create loan
        loan_date = date.today()
        due_date = loan_date + timedelta(days=14)
        
        query = """
        INSERT INTO loans (book_id, member_id, loan_date, due_date, status)
        VALUES (%s, %s, %s, %s, 'active')
        """
        values = (loan.book_id, loan.member_id, loan_date, due_date)
        
        cursor.execute(query, values)
        
        # Update book availability
        cursor.execute(
            "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s",
            (loan.book_id,)
        )
        
        connection.commit()
        loan_id = cursor.lastrowid
        
        cursor.execute("""
            SELECT l.*, b.title as book_title, 
                   CONCAT(m.first_name, ' ', m.last_name) as member_name
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
            WHERE loan_id = %s
        """, (loan_id,))
        new_loan = cursor.fetchone()
        
        return new_loan
    except mysql.connector.Error as err:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {err}"
        )
    finally:
        cursor.close()

@app.put("/loans/{loan_id}/return", response_model=schemas.LoanResponse)
def return_loan(loan_id: int, connection = Depends(get_db)):
    cursor = connection.cursor(dictionary=True)
    try:
        # Get loan details with FOR UPDATE to lock the row
        cursor.execute("""
            SELECT l.*, b.book_id 
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            WHERE loan_id = %s
            FOR UPDATE
        """, (loan_id,))
        loan = cursor.fetchone()
        
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found"
            )
        
        if loan['return_date'] is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book already returned"
            )
        
        # Update loan
        return_date = date.today()
        status = "returned"
        
        cursor.execute(
            "UPDATE loans SET return_date = %s, status = %s WHERE loan_id = %s",
            (return_date, status, loan_id)
        )
        
        # Update book availability
        cursor.execute(
            "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = %s",
            (loan['book_id'],)
        )
        
        connection.commit()
        
        cursor.execute("""
            SELECT l.*, b.title as book_title, 
                   CONCAT(m.first_name, ' ', m.last_name) as member_name
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
            WHERE loan_id = %s
        """, (loan_id,))
        updated_loan = cursor.fetchone()
        
        return updated_loan
    except mysql.connector.Error as err:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {err}"
        )
    finally:
        cursor.close()

@app.get("/loans/", response_model=List[schemas.LoanResponse])
def list_loans(
    status: Optional[schemas.LoanStatus] = None,
    overdue: Optional[bool] = None,
    connection = Depends(get_db)
):
    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT l.*, b.title as book_title, 
                   CONCAT(m.first_name, ' ', m.last_name) as member_name
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
        """
        conditions = []
        params = []
        
        if status:
            conditions.append("l.status = %s")
            params.append(status)
        
        if overdue:
            conditions.append("l.due_date < CURDATE() AND l.return_date IS NULL")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        loans = cursor.fetchall()
        
        return loans
    finally:
        cursor.close()