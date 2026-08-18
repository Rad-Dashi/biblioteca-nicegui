from nicegui import ui
from db import db_initialize
from gui import render_ui

# Start app
if __name__ in {"__main__", "__mp_main__"}:
    db_initialize()

# Render UI
render_ui()

ui.run(title="Mi Biblioteca", reload=True)