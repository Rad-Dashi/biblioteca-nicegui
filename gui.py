from nicegui import ui
from db import db_read_books


def render_ui():
    ui.label('Mi Colección de Libros').classes('text-2xl font-bold my-4')

    columns = [
        {'name': 'cover', 'label': 'Portada', 'field': 'cover', 'align': 'center'},
        {'name': 'title', 'label': 'Título', 'field': 'title', 'align': 'left', 'sortable': True},
        {'name': 'author', 'label': 'Autor', 'field': 'author', 'align': 'left', 'sortable': True},
        {'name': 'publisher', 'label': 'Editorial', 'field': 'publisher', 'align': 'left'},
        {'name': 'category', 'label': 'Categorías', 'field': 'category', 'align': 'left'},
        {'name': 'status', 'label': 'Estado', 'field': 'status', 'align': 'center'},
    ]

    # List books from the database
    books = db_read_books()

    # Render table
    table = ui.table(
        columns=columns,
        rows=books,
        row_key='id',
        pagination=25
    ).classes('w-full')

    # Custom slot: Cover
    table.add_slot(
        'body-cell-cover',
        '''
        <q-td :props="props">
            <div class="flex justify-center items-center">
                <img :src="props.value" class="h-32 w-20 object-cover rounded shadow-md" v-if="props.value" />
                <span v-else class="text-xs text-gray-400 italic">Sin portada</span>
            </div>
        </q-td>
        ''',
    )

    # Custom slot: Title
    table.add_slot(
        'body-cell-title',
        '''
        <q-td :props="props">
            <div class="max-w-xs line-clamp-2 whitespace-normal font-medium">
                {{ props.value }}
                <q-tooltip>{{ props.value }}</q-tooltip>
            </div>
        </q-td>
        ''',
    )