import os
import uuid

from nicegui import ui, app # app se usa para llamar a las imágenes en la carpeta de portadas (una suerte de backend)
from db import (
    db_leer_libros,
    db_crear_libro,
    db_actualizar_libro,
    db_borrar_libro
    )

# Carpeta local donde se guardan las portadas subidas por el usuario
PORTADAS_DIR = "portadas"
os.makedirs(PORTADAS_DIR, exist_ok=True)
app.add_static_files("/portadas", PORTADAS_DIR) # Acá entra en juego el import app de nicegui, para que pueda servir las imágenes de la carpeta portadas

# Referencia global a la tabla para poder refrescarla después de agregar, editar o borrar un libro
tabla = None

def refrescar_tabla(busqueda=None):
    global tabla
    if tabla is None:
        return
    tabla.rows = db_leer_libros(busqueda)
    tabla.update()

def renderizar_ui():
    global tabla

    with ui.row().classes("w-full items-center justify-between my-4"):
        ui.label("Gestor de Libros").classes("text-2xl font-bold")
        with ui.row().classes("items-center gap-2"):
            ui.input(
                placeholder="Buscar por título, autor, género o editorial...",
                on_change=lambda e: refrescar_tabla(e.value),
            ).props("clearable dense outlined").classes("w-72")
            ui.button(
                "Nuevo libro", icon="add", on_click=lambda: abrir_dialogo_libro()
            ).props("color=primary")
 
    columnas = [
        {"name": "portada", "label": "Portada", "field": "portada", "align": "center"},
        {"name": "titulo", "label": "Título", "field": "titulo", "align": "left", "sortable": True},
        {"name": "autor", "label": "Autor", "field": "autor", "align": "left", "sortable": True},
        {"name": "genero", "label": "Género", "field": "genero", "align": "left", "sortable": True},
        {"name": "precio", "label": "Precio", "field": "precio", "align": "right", "sortable": True},
        {"name": "anio_publicacion", "label": "Año de Publicación", "field": "anio_publicacion", "align": "center", "sortable": True},
        {"name": "editorial", "label": "Editorial", "field": "editorial", "align": "left", "sortable": True},
        {"name": "acciones", "label": "Acciones", "field": "acciones", "align": "center"},
    ]

    # Lista de libros de la base de datos
    libros = db_leer_libros()

    # Renderizar tabla
    tabla = ui.table(
        columns=columnas,
        rows=libros,
        row_key='id',
        pagination=25
    ).classes('w-full')

    # Custom slot p/ Portada
    tabla.add_slot(
        'body-cell-portada',
        '''
        <q-td :props="props">
            <div class="flex justify-center items-center">
                <img :src="props.value" class="h-32 w-20 object-cover rounded shadow-md" v-if="props.value" />
                <span v-else class="text-xs text-gray-400 italic">Sin portada</span>
            </div>
        </q-td>
        ''',
    )

    # Custom slot: Título
    tabla.add_slot(
        'body-cell-titulo',
        '''
        <q-td :props="props">
            <div class="max-w-xs line-clamp-2 whitespace-normal font-medium">
                {{ props.value }}
                <q-tooltip>{{ props.value }}</q-tooltip>
            </div>
        </q-td>
        ''',
    )

    # Custom slot: Acciones (editar/borrar)
    tabla.add_slot(
        "body-cell-acciones",
        """
        <q-td :props="props" class="text-center">
            <q-btn flat dense round icon="edit" color="primary"
                @click"() => $parent.$emit('editar', props-row)" />
            <q-btn flat dense round icon="delete" color="negative"
                @click="() => $parent.$emit('borrar', props.row)" />
        </q-td>
        """,
    )

    tabla.on("editar", lambda e: abrir_dialogo_libro(e.args))
    tabla.on("borrar", lambda e: confirmar_borrado(e.args))

def confirmar_borrado(libro):
    with ui.dialog() as dialogo, ui.card():
        ui.label(f'¿Eliminar "{libro["titulo"]}"?').classes("text-lg font-bold")
        ui.label("Esta acción no se puede deshacer.").classes("text-sm text-gray-500")
        with ui.row().classes("justify-end w-full mt-4"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def borrar():
                db_borrar_libro(libro["id"])
                refrescar_tabla()
                dialogo.close()
                ui.notify("Libro eliminado", color="negative")

            ui.button("Eliminar", color="negative", on_click=borrar)

    dialogo.open()

def abrir_dialogo_libro(libro=None):
    """Abre el formulario para crear un libro nuevo, o editar uno existente."""
    es_edicion = libro is not None
    portada_actual = (libro.get("portada") or "") if es_edicion else ""
    # Guarda la ruta de la imagen que se suba localmente (si se sube una)
    imagen_subida = {"ruta": ""}

    with ui.dialog() as dialogo, ui.card().classes("w-full max-w-md"):
        ui.label("Editar libro" if es_edicion else "Nuevo libro").classes("text-lg font-bold")

        titulo = ui.input("Título *", value=libro["titulo"] if es_edicion else "").classes("w-full")
        autor = ui.input("Autor *", value=libro["autor"] if es_edicion else "").classes("w-full")
        genero = ui.input("Género", value=libro["genero"] if es_edicion else "").classes("w-full")
        precio = ui.number("Precio", value=libro["precio"] if es_edicion else None, format="%.2f").classes("w-full")
        anio = ui.number("Año de publicación", value=libro["anio_publicacion"] if es_edicion else None, format="%.0f",).classes("w-full")
        editorial = ui.input("Editorial", value=libro["editorial"] if es_edicion else "").classes("w-full")

        ui.separator().classes("my-2")
        ui.label("Portada").classes("font-medium")

        # No cargamos la URL si la portada es un archivo local, porque en ese caso se muestra la vista previa de abajo en lugar del campo de texto
        es_local = portada_actual.startswith("/portadas/")
        portada_url = ui.input(
            "URL de la imagen (o dejar vacío para subir una imagen)",
            value="" if es_local else portada_actual,
        ).classes("w-full")

        vista_previa = ui.image(portada_actual).classes("w-24 h-32 object-cover rounded my-2") if es_local else None

        def manejar_subida(e):
            nonlocal vista_previa
            extension = os.path.splitext(e.name)[1] or ".jpg"
            nombre_archivo = f"{uuid.uuid4().hex}{extension}"
            ruta_destino = os.path.join(PORTADAS_DIR, nombre_archivo)
            with open(ruta_destino, "wb") as archivo_destino:
                archivo_destino.write(e.content.read())

            imagen_subida["ruta"] = f"/portadas/{nombre_archivo}"
            portada_url.value = "" # La subida local tiene prioridad sobre la URL
            if vista_previa is not None:
                vista_previa.delete()
            vista_previa = ui.image(imagen_subida["ruta"]).classes("w-24 h-32 object-cover rounded my-2")
            ui.notify(f'Imagen "{e.name}" cargada', color="positive")

        ui.upload(
            label="Subir imagen desde tu computadora",
            on_upload=manejar_subida,
            auto_upload=True,
        ).props('accept="image/*"').classes("w-full")

        with ui.row().classes("justify-end w-full mt-4"):
            ui.button("Cancelar", on_click=dialogo.close).props("flat")

            def guardar():
                if not titulo.value or not titulo.value.strip():
                    ui.notify("El título es obligatorio", color="warning")
                    return
                if not auto.value or not autor.value.strip():
                    ui.notify("El autor es obligatorio", color="warning")
                    return
                if imagen_subida["ruta"]:
                    portada_final = imagen_subida["ruta"]
                elif portada_url.value and portada_url.value.strip():
                    portada_final = portada_url.value.strip()
                else:
                    portada_final = portada_actual if es_edicion else ""

                datos = dict(
                    titulo=titulo.value.strip(),
                    autor=autor.value.strip(),
                    portada=portada_final,
                    genero=genero.value.strip() if genero.value else "",
                    precio=precio.value if precio.value is not None else "",
                    anio_publicacion=int(anio.value) if anio.value else "",
                    editorial=editorial.value.strip() if editorial.value else "",
                )

                if es_edicion:
                    db_actualizar_libro(id=libro["id"], **datos)
                    ui.notify("Libro actualizado", color="positive")
                else:
                    db_crear_libro(**datos)
                    ui.notify("Libro creado", color="positive")

                refrescar_tabla()
                dialogo.close()

            ui.button("Guardar", color="primary", on_click=guardar)

    dialogo.open()