import time
import numpy
import warnings
import pandas as pd
import publicar_info as pi
import remax_remast as remax
import publicar_clasipar as pp
from para_log import escribir_en_log
from credenciales import crenciales_paginas
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service as EdgeService
import scrapeador

from pathlib import PurePath, Path
# Desactivar todas las advertencias de Pandas
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)
# limpiar log
escribir_en_log("", 4)
options = Options()
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--log-level=3")

# ciudades configuradas actualmente
ciudades = ["Asuncion", "Sanber", "Fernando", "Sanlo", "Luque", "Lamba", "Aregua", "Altos", "Paraguay",
            "VillaElisa", "Presidente", "Ñemby", "Capiata"]
driver = ""
edge_driver_path = 'C:\\Users\\ACER\\Documents\\Bots\\pythonProject\\prueba_inicial_remax\\driver\\msedgedriver.exe'
escribir_en_log("Comenzo la ejecucion", 1)
edge_service = EdgeService(executable_path=edge_driver_path)



# configuracion del bot
configuraciones = remax.variables_configuracion()
cantidad_de_resultados = 26 #26
cantidad_publicar = configuraciones['cantidad_publicar']
cantidad_scrapear = configuraciones['cantidad_propiedades']
cantidad_agregar = configuraciones['cantidad_agregar']

print("="*80)
print(f"Cantidad a publicar por usuario: {cantidad_publicar}")
print(f"Cantidad a scrapear: {cantidad_scrapear}")
print(f"Cantidad links agregar {cantidad_agregar}")
print("Resultados por pestaña:", cantidad_de_resultados)
def indices_duplicados(base):
    """
        retorna los ides repetidos de la base
    """

    ides = base["ide"].to_list()
    # indices repetidos
    indices = []
    ide_duplicado = []
    for ide in ides:
        res = base[base["ide"] == ide].index.to_list()

        if len(res) > 1:
            if ide not in ide_duplicado:
                indices.append(res)
                ide_duplicado.append(ide)

    return indices
def eliminar_indices_duplicados(ind_dupli, indices_totales):

    indices_duplicados = ind_dupli  # la variable
    indices_totales = indices_totales
    for ind in indices_duplicados:  # recorrel las listas de indices
        indice_eliminar = ind[0]  # se elije uno de los duplicados para eliminar

        indices_totales.pop(indice_eliminar)

    return indices_totales

def realizar_validacion_duplicados_base(base_validar, ruta_base):
    ind_dupli = indices_duplicados(base_validar)
    base_temporal = base_validar
    indices_base_actual = base_temporal.index.to_list()
    indices_sin_duplicados = eliminar_indices_duplicados(ind_dupli, indices_base_actual)
    base_temporal = base_temporal.iloc[indices_sin_duplicados]
    base_temporal.to_csv(ruta_base, index=False)

ruta_base = PurePath(remax.RUTA_BOT, "driver", "remax_propiedades.csv")
base_remax = pd.read_csv(ruta_base)
realizar_validacion_duplicados_base(base_remax, ruta_base)


def ejecutar_por_ciudad(numero_ciudad):

    print(f"Ciudad a Scrapear: {ciudades[numero_ciudad]}\n", "="*80, "\n")
    driver = ""
    remax_ = scrapeador.RemaxScrap(ciudades[numero_ciudad], cantidad_agregar, cantidad_scrapear)
    remax_.instanciar_navegador()
    remax_.abrir_navegador()
    remax_.abrir_base()
    if cantidad_agregar > 0:

        remax_.buscar_ciudad()
        remax_.recorrer_ventanas()

    time.sleep(5)
    if cantidad_scrapear > 0:
        remax_.scrapear_propiedades_pendientes()
    remax_.navegador.cerra_navegador()


def validar_columna_usuario(credenciales):
    """"
        valida que existan las columnas suficientes para cada usuario
    """
    base = pd.read_csv(remax.RUTA_DF)
    columnas = base.columns

    for numero_usuario in credenciales:
        if f"{numero_usuario}publicado_info" in columnas:
            pass
        else:
            base[f"{numero_usuario}publicado_info"] = numpy.nan

        if f"{numero_usuario}publicado_clasipar" in columnas:
            pass
        else:
            base[f"{numero_usuario}publicado_clasipar"] = numpy.nan

    base.to_csv(remax.RUTA_DF, index=False)

def realizar_publicaciones():
    driver = ""
    credenciales_clasipar = crenciales_paginas()["clasi"]
    credenciales_info = crenciales_paginas()["info"]
    credenciales_hendy = crenciales_paginas()["hendy"]
    validar_columna_usuario(credenciales_info)
    validar_columna_usuario(credenciales_clasipar)

    # comienza a realizar las publicaciones en clasipar
    for numero_usuario in credenciales_clasipar:

        if credenciales_clasipar[numero_usuario]["ingresa"] == "Si":
            driver = remax.webdriver.Edge(service=edge_service, options=options)
            pp.procesar_clasipar(driver, numero_usuario, credenciales_clasipar, cantidad_publicar)
            try:
                driver.close()
            except:
                pass

    if driver != "":
        try:
            driver.close()
        except:
            pass

    # comienza a hacer als publicaciones en infocasas
    for numero_usuario in credenciales_info:
        if credenciales_info[numero_usuario]["ingresa"] == "Si":
            driver = remax.webdriver.Edge(service=edge_service, options=options)
            pi.iniciar_sesion_infocasas(driver, numero_usuario, credenciales_info)
            pi.recorrer_resultados_pendientes_a_publicar_info(driver, numero_usuario, cantidad_publicar)

            driver.close()
    """
    # comienza a hacer las publicaciones en hendyla
    for numero_usuario in credenciales_hendy:
        if credenciales_hendy[numero_usuario]["ingresa"] == "Si":
            # abrir el navegador
            driver = remax.webdriver.Edge(service=edge_service, options=options)
            # iniciar sesion en la pagina
            ph.iniciar_sesion_hendyla(driver, credenciales_hendy[numero_usuario])
            # realizar las publicaciones pendientes
            ph.recorrer_resultados_pendientes_a_publicar_hendyla(driver, numero_usuario)
            # cerrar navegador
            driver.close()
    """
#0"Asuncion", 1"Sanber", 2"Fernando", 3"Sanlo", 4"Luque" , 5 "Lambare", 6 "Aregua", 7 "Alto", 8 "Paraguay"
#9 "Villa Elisa", 10 "Presidente Hayes", 11 "Ñemby", 12 "Capiata"
ejecutar_por_ciudad(12)

if cantidad_publicar > 0:
    realizar_publicaciones()

escribir_en_log(f"Fin del proceso", 1)
var = input("Presionar Enter")


