import requests
from pprint import pprint
from bs4 import BeautifulSoup
import psycopg2
import re


# TripAdvisor
TRIPADVISOR_KEY = '4DA558B86CE54BF883B26708661637C8'

# Oxylabs
USERNAME, PASSWORD = 'Liiffe_S3Q3w', 'Aliffe15464342+'

# Configuración del proxy
proxies = {
    'http': f'http://{USERNAME}:{PASSWORD}@realtime.oxylabs.io:60000',
    'https': f'https://{USERNAME}:{PASSWORD}@realtime.oxylabs.io:60000'
}

# Configuración de cabeceras para evitar detección como bot
headers = {
    'x-oxylabs-user-agent-type': 'desktop_chrome',  # Simula un navegador Chrome
    'x-oxylabs-geo-location': 'US',  # Puedes cambiar la ubicación según necesites
    'X-Oxylabs-Render': 'html',  # Descomentar si se necesita renderizado de JavaScript
}




def crearURL(ciudad, lugar, categoria, criterio):
    
    urlBase = "https://www.tripadvisor.com.mx/"
    limitacion = "&broadened=false"
    
    if lugar == 'RESTAURANTE':
        urlBase += f"FindRestaurants?geo={ciudad}&{categoria}={criterio}{limitacion}"
    
    if lugar == 'HOTEL':
        urlBase += f"Hotels-{ciudad}&{categoria}={criterio}{limitacion}"
    
    return urlBase 



def consultarLugares(category, tag, place):
    
    conexion = None
    cursor = None
    try:
        # Conexión a la base de datos
        conexion = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="12345678",
            database="liiffe"
        )
        cursor = conexion.cursor()

        
        consulta_sql = """
            SELECT id_element, category_url    
            FROM tags_tripadvisor 
            WHERE category = %s 
            AND tag = %s 
            AND place = %s;
        """
        cursor.execute(consulta_sql, (category, tag, place))  
        resultados = cursor.fetchall() 

        return resultados

    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
        return None

    finally:
     
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


def obtenerLugar(idPlace):
    
    try:
        url = f"https://api.content.tripadvisor.com/api/v1/location/{idPlace}/details?key={TRIPADVISOR_KEY}&language=es&currency=USD"

        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers)

        return response.text    
    
    except:
        return "LUGAR NO ENCONTRADO"
    


def extraerEnlaces(html_file):
    with open(html_file, "r", encoding="utf-8") as file:
        contenido = file.read()

    soup = BeautifulSoup(contenido, "lxml")

    # Lista de clases a buscar
    clases = {"BMQDV", "_F", "Gv", "wSSLS", "SwZTJ", "FGwzt", "ukgoS"}

    # Buscar todas las etiquetas <a> que contengan al menos una de esas clases
    enlaces_a = soup.find_all("a", class_=lambda c: c and any(cls in c.split() for cls in clases))

    # Extraer y filtrar los href que contengan "187497"
    enlaces_filtrados = [a["href"] for a in enlaces_a if a.has_attr("href") and "187497" in a["href"]]

    return enlaces_filtrados


def extraerIdentificadores(urls: list) -> list:

    patron = r"g\d+-d(\d+)"  # Expresión regular

    identificadores_d = [f"d{match.group(1)}" for url in urls if (match := re.search(patron, url))]

    return identificadores_d


def scrapingTripAdvisor(urlTripAdvisor):
    
    try:
        response = requests.request(
            'GET',
            urlTripAdvisor,
            headers=headers,  # Pasa las cabeceras definidas
            verify=False,  # Acepta el certificado de seguridad
            proxies=proxies,  # Usa el proxy de Oxylabs
        )


        # Guarda el HTML en un archivo para analizarlo con BeautifulSoup
        with open('tripadvisor_result.html', 'w', encoding='utf-8') as f:
            f.write(response.text)   
            return "OK"
    except:
        return "ERROR"


#-----------------------------------   EJECUCION DEL SCRIPT --------------------------------------------------------------------
lugar = "RESTAURANTE"
categoria = "ESTABLECIMIENTO"
tag = "POSTRES"
idCiudad = 187497 #BARCELONA

idTag = ""
categoriaUrl = ""



# 1. OBTIENE LOS IDENTIFICADORES DE LOS ELEMENTOS HTML 
resultados = consultarLugares(categoria, tag, lugar)
if resultados:
    for fila in resultados:        
        idTag = fila[0]
        categoriaUrl = fila[1]


# 2.- CREA LA URL A SCREAPEAR EN BASE A LOS CRITERIOS ESTABLECIDOS
urlTripAdvisor = crearURL(idCiudad, lugar, categoriaUrl, idTag)
print(urlTripAdvisor);


# 3.- REALIZA EL SCRAPING A TRIPADVISOR CON OXYLABS Y GUARDA UN CLON DE LA PAGINA EN EL ARCHIVO tripadvisor_result
scraping = scrapingTripAdvisor(urlTripAdvisor)

if(scraping=='OK'):
    print("Scraping completado. HTML guardado en 'tripadvisor_result.html'")
else:
    breakpoint


# 4.- REALIZA EL SCRAPING EN EL ARCHIVO Y EXTRE LOS ENLACES DE LOS LUGARES
archivo_html = "tripadvisor_result.html"  # Reemplaza con tu archivo
enlaces = extraerEnlaces(archivo_html)
enlaces_unicos = list(set(enlaces))


# 5.- DELIMITA LOS ENLACES OBTENIDOS A LOS QUE CORRESPONDAN DE RESTAURANTES U OTRO LUGAR ASIGANDO
enlaces_filtrados = {enlace for enlace in enlaces_unicos if "Restaurant_Review" in enlace}

# Imprimir los enlaces únicos filtrados
for enlace in enlaces_filtrados:
    print(enlace)
    



print("--------------------------------------------------------------------------")
# 6.- EXTRE LOS IDENTIFICADORES DE LOS LUGARES DE LOS ENLACES Y HACE LA PETICION A TRIP ADVISOR API PARA OBTENER EL DETALLE DE ESTOS
ids_url = extraerIdentificadores(enlaces_filtrados)
for ids in ids_url:
    idPlace = ids
    idPlace = idPlace.replace('d','')
    objPlace = obtenerLugar(idPlace)
    print(objPlace)