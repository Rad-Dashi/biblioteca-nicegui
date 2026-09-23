from nicegui import ui
from db import inicializar_db
from gui import renderizar_ui

# Iniciar app
if __name__ in {"__main__", "__mp_main__"}:
    inicializar_db()

# Render UI
renderizar_ui()

ui.run(title="Gestor de Libros", reload=True)