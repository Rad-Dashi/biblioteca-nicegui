import sqlite3

DB_NAME = "db_libros.db"

def connectar_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    """Crear la tabla si no existe para la primera vez."""
    _crear_tabla()

def _crear_tabla():
    conn = connectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS db_libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portada TEXT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            genero TEXT,
            precio DECIMAL(10, 2),
            anio_publicacion INTEGER,
            editorial TEXT
        )
    """)

    conn.commit()
    conn.close()

def db_crear_libro(
        titulo,
        autor,
        portada="",
        genero="",
        precio="",
        anio_publicacion="",
        editorial="",
):
    """CREAR nuevo libro en la base de datos."""
    conn = connectar_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO db_libros (
            titulo, autor, portada, genero, precio, anio_publicacion, editorial
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            titulo, 
            autor, 
            portada, 
            genero, 
            precio, 
            anio_publicacion, 
            editorial
        ),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def db_leer_libros(search=None):
    """LEER libros. Si recibe un 'search', filtra por id, título, autor, editorial o categoría."""
    conn = connectar_db()
    cursor = conn.cursor()

    if not search:
        cursor.execute("SELECT * FROM db_libros ORDER BY titulo ASC")
    else:
        pattern = f"%{search}%"
        cursor.execute(
            """
            SELECT * FROM db_libros
            WHERE titulo LIKE ? OR autor LIKE ? OR editorial LIKE ? OR genero LIKE ?
            ORDER BY titulo ASC
        """,
            (pattern, pattern, pattern, pattern),
        )

    columnas = cursor.fetchall()
    conn.close()
    return [dict(columna) for columna in columnas]

def db_actualizar_libro(
    id,
    titulo,
    autor,
    portada="",
    genero="",
    precio="",
    anio_publicacion="",
    editorial="",
):
    """UPDATE data de un libro existente."""
    conn = connectar_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE db_libros 
        SET titulo = ?, 
            autor = ?, 
            portada = ?, 
            genero = ?, 
            precio = ?, 
            anio_publicacion = ?, 
            editorial = ?
        WHERE id = ?
    """,
        (
            titulo, 
            autor, 
            portada, 
            genero, 
            precio, 
            anio_publicacion, 
            editorial,
            id,
        ),
    )

    conn.commit()
    conn.close()


def db_borrar_libro(id):
    """BORRAR un libro por ID."""
    conn = connectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM db_libros WHERE id = ?", (id,))
    conn.commit()
    conn.close()