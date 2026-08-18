import sqlite3
import csv
import os

DB_NAME = "book_collection.db"
CSV_FILE = "book_collection.csv"

def db_connect():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def db_initialize():
    """Create table if it doesn't exist and load data from CSV for the first time."""
    _create_table()
    _load_csv_into_table()

def _create_table():
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_collection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publisher TEXT,
            publishing_date TEXT,
            cover TEXT,
            category TEXT,
            isbn TEXT,
            lent_to TEXT,
            status TEXT,
            notes TEXT,
            summary TEXT
        )
    """)

    conn.commit()
    conn.close()

def _load_csv_into_table():
    conn = db_connect()
    cursor = conn.cursor()

    # Records existence verification
    cursor.execute("SELECT COUNT(*) FROM book_collection")
    cantidad = cursor.fetchone()[0]

    # If there is data or the CSV doesn't exist, we don't import again
    if cantidad > 0 or not os.path.exists(CSV_FILE):
        conn.close()
        return
    
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        next(csv_reader, None) # Skip headings

        for row in csv_reader:
            if not row or len(row) < 2: # Skip empty rows
                continue

            cursor.execute(
                """
                INSERT INTO book_collection (
                    title, author, publisher, publishing_date, cover, category, isbn, lent_to, status, notes, summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                row,
            )

    conn.commit()
    conn.close()
    print(f"Data load successfully from {CSV_FILE}.")

def db_create_book(
        title,
        author,
        publisher="",
        publishing_date="",
        cover="",
        category="",
        isbn="",
        lent_to="",
        status="",
        notes="",
        summary="",
):
    """CREATE a new book into the database."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO book_collection (
            title, author, publisher, publishing_date, cover, category, isbn, lent_to, status, notes, summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            title, 
            author, 
            publisher, 
            publishing_date, 
            cover, 
            category, 
            isbn, 
            lent_to, 
            status, 
            notes, 
            summary
        ),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def db_read_books(search=None):
    """READ books. If receives a 'search', filters by id, title, author, publisher o category."""
    conn = db_connect()
    cursor = conn.cursor()

    if not search:
        cursor.execute("SELECT * FROM book_collection ORDER BY id DESC")
    else:
        pattern = f"%{search}%"
        # If the search is an integer, allows to search also by the exact ID
        if str(search).isdigit():
            cursor.execute(
                """
                SELECT * FROM book_collection
                WHERE id = ? OR title LIKE ? OR author LIKE ? OR publisher LIKE ? OR category LIKE ?
                ORDER BY id DESC
            """,
                (int(search), pattern, pattern, pattern, pattern),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM book_collection
                WHERE title LIKE ? OR author LIKE ? OR publisher LIKE ? OR category LIKE ?
                ORDER BY id DESC
            """,
                (pattern, pattern, pattern, pattern),
            )

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def db_update_book(
    book_id,
    title,
    author,
    publisher="",
    publishing_date="",
    cover="",
    category="",
    isbn="",
    lent_to="",
    status="",
    notes="",
    summary="",
):
    """UPDATE data from an existing book."""
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE book_collection 
        SET title = ?, 
            author = ?, 
            publisher = ?, 
            publishing_date = ?, 
            cover = ?, 
            category = ?, 
            isbn = ?, 
            lent_to = ?, 
            status = ?, 
            notes = ?, 
            summary = ?
        WHERE id = ?
    """,
        (
            title, 
            author, 
            publisher, 
            publishing_date, 
            cover, 
            category, 
            isbn, 
            lent_to, 
            status, 
            notes, 
            summary,
            book_id,
        ),
    )

    conn.commit()
    conn.close()

def db_delete_book(book_id):
    """DELETE a book by ID."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM book_collection WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()