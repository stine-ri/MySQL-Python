-- library_management.sql
-- Library Management Database System
-- Author: Christine Nyambwari
-- Date: 2/05/25

-- Create the database
DROP DATABASE IF EXISTS library_management;
CREATE DATABASE library_management;
USE library_management;

-- Members table (1-to-Many with Loans)
CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    join_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    membership_status ENUM('active', 'expired', 'suspended') DEFAULT 'active'
);

-- Books table (Many-to-Many with Authors through book_authors)
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    publication_year INT,
    genre VARCHAR(50),
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    CHECK (available_copies <= total_copies AND available_copies >= 0)
);

-- Authors table
CREATE TABLE authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_year INT,
    nationality VARCHAR(50)
);

-- Junction table for Many-to-Many relationship between books and authors
CREATE TABLE book_authors (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE
);

-- Loans table (Connects members and books)
CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    loan_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    due_date DATE NOT NULL DEFAULT (DATE_ADD(CURRENT_DATE, INTERVAL 14 DAY)),
    return_date DATE,
    status ENUM('active', 'returned', 'overdue') DEFAULT 'active',
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    CHECK (return_date IS NULL OR return_date >= loan_date)
);

-- Insert sample data
INSERT INTO members (first_name, last_name, email, phone, join_date) VALUES
('John', 'Smith', 'john.smith@email.com', '555-0101', '2022-01-15'),
('Sarah', 'Johnson', 'sarah.j@email.com', '555-0102', '2022-03-22'),
('Michael', 'Brown', 'michael.b@email.com', NULL, '2022-05-10');

INSERT INTO authors (first_name, last_name, birth_year, nationality) VALUES
('George', 'Orwell', 1903, 'British'),
('J.K.', 'Rowling', 1965, 'British'),
('Stephen', 'King', 1947, 'American');

INSERT INTO books (isbn, title, publication_year, genre, total_copies, available_copies) VALUES
('978-0451524935', '1984', 1949, 'Dystopian', 5, 3),
('978-0743477106', 'Harry Potter and the Philosopher''s Stone', 1997, 'Fantasy', 3, 1),
('978-1501142970', 'The Shining', 1977, 'Horror', 4, 4);

INSERT INTO book_authors (book_id, author_id) VALUES
(1, 1), -- 1984 by George Orwell
(2, 2), -- Harry Potter by J.K. Rowling
(3, 3); -- The Shining by Stephen King

INSERT INTO loans (book_id, member_id, loan_date, due_date, return_date, status) VALUES
(1, 1, '2023-01-10', '2023-01-24', NULL, 'active'),
(2, 2, '2023-01-05', '2023-01-19', '2023-01-18', 'returned'),
(1, 3, '2023-01-15', '2023-01-29', NULL, 'active');