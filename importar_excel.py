import os
import django
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tripadvisor.settings')  # Cambia 'mi_proyecto'
django.setup()

from tags_tripadvisor.models import TagsTripadvisor  # Cambia 'tags_tripadvisor' si tu app se llama diferente

# Leer el archivo Excel
archivo_excel = 'categorias.xlsx'  # Reemplaza con la ruta real
df = pd.read_excel(archivo_excel, engine='openpyxl')

# Iterar filas e insertar
for index, row in df.iterrows():
    TagsTripadvisor.objects.create(
        place=row.get('place'),
        category=row.get('category'),
        tag=row.get('tag'),
        id_element_html=row.get('id_element_html'),
        id_element=row.get('id_element'),
        id_element_html_modal=row.get('id_element_html_modal'),
        category_url=row.get('category_url')
    )

print("Importación completa.")
