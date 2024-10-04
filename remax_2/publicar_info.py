import os
import time
import re
import warnings
import pyautogui
import pandas as pd
import pygetwindow as gw
from pathlib import PurePath, Path
from para_log import escribir_en_log
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

# Desactivar todas las advertencias de Pandas
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

# Configuracion del driver
options = Options()
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--log-level=3")

edge_driver_path = 'C:\\Users\\ACER\\Documents\\Bots\\pythonProject\\prueba_inicial_remax\\driver\\msedgedriver.exe'


driver = ""

# Rutas
RUTA_BOT = PurePath(Path().absolute())
RUTA_DATOS = PurePath(RUTA_BOT, "datos")
RUTA_DRIVER = f"{PurePath(RUTA_BOT, "driver")}\\msedgedriver.exe"
RUTA_ARCHIVO_CSV = PurePath(RUTA_BOT,'driver','remax_propiedades.csv')

# Categorias y validaciones
CATEGORIAS = {
    "Residencia": 1, "Departamento": 2, "Casa": 1, "Terreno": 3, "Duplex": 5, "Edificio": 10,
    "Depósito": 11, "Local Comercial": 4, "Oficina": 6, "Casa de Verano": 1, "Chalet": 1,
    "Atypical": 1, "Bloque de departamentos": 2, "Business": 10, "Casa de campo": 1, "Condominio de Lujo": 1,
    "Departamento con servicio de Hotel": 2, "Habitación": 2, "Health Clinic": 4, "Hotel": 10, "Industria": 4,
    "Nueva Construcción": 10, "Quinta": 1, "Triplex": 5,"Espacio de estacionamiento":3,"Sin Tipo":1,"Accommodation":1,
    "Villa": 1, "Sports Centre": 1
}
VAR_VALIDACIONES = {
    'set_titulo': False, 'set_descripcion': False, 'set_precio': False, 'set_ciudad': False,
    'set_imagenes': False, 'set_barrio': False, 'set_banios': False, 'set_habitaciones': False,
    'set_estado': False, 'set_seguridad': False, 'set_metros': False,
}

# Xpaths
path_boton_ingresar1 = "/html/body/div[2]/div[6]/div/ul[2]/li[4]/a/span"
path_boton_ingresar = "/html/body/div/div/header/div[1]/button"
path_campo_correo = "/html/body/div[11]/div/div[2]/form/div[1]/input"
path_boton_continuar = "/html/body/div[11]/div/div[2]/form/div[1]/div[2]"
path_campo_contrasenia = "/html/body/div[11]/div/div[2]/form/div[2]/input"
path_boton_enviar = "/html/body/div[11]/div/div[2]/form/div[2]/div[2]"
path_boton_publicar = "/html/body/div[1]/div[6]/div/ul[2]/li[4]/a/span"
path_boton_publicar2 = "/html/body/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div[2]/a"
# variables para publicaciones
path_campo_titulo = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[1]/div[1]/input[1]"
path_campo_precio = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[4]/div[2]/div[1]/input"
path_campo_ciudad = '/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[6]/div[3]/div[2]/input'
path_dormitorio = ["/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[2]/div/div[", "]/div"]
path_banios = ["/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[3]/div/div[","]/div"]
path_estado = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[5]/div/div[3]/div"
path_descripcion = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[2]/div[5]/div[3]/div[2]/div[1]"
path_seleccion_img = "/html/body/div[1 n]/div[8]/div[2]/div[2]/form/div[2]/div[2]/div[1]/div[2]/ul/li[2]/input"
path_seleccion_tipo_propiedad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[6]/div[2]/div/div[1]/a"
path_seleccion_tipo_propiedad2 = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[6]/div[2]/div/div[1]/i"
path_tipo_propiedad = ["/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[6]/div[2]/div/div[2]/ul/li[","]"]

def esperarPorObjeto(navegador_abierto, tiempo, tipoObjeto, identificadorObjeto, nombre, numero_usuario, ide):
    """
        Espera que se cargue el objeto de la pagina
        :return
        bool
    """
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Esperando que cargue la ventana {nombre}", 2)
    try:
        WebDriverWait(navegador_abierto, tiempo).until(
            expected_conditions.presence_of_element_located((tipoObjeto, identificadorObjeto)))
        return True
    except:
        escribir_en_log(f"No cargo la ventana {nombre}", 2)
        return False
def iniciar_sesion_infocasas(navegador, numero_usuario, credenciales):
        """Inicia sesion en el sitio de Infocasas"""

        navegador.get("https://www.infocasas.com.py/soyinmobiliaria")

        esperarPorObjeto(navegador, 10, By.XPATH, path_boton_ingresar1, "Boton Iniciar sesion", 1, 1)

        navegador.find_element(By.XPATH, path_boton_ingresar1).click()
        time.sleep(0.5)

        esperarPorObjeto(navegador, 3, By.XPATH, path_campo_correo, "Campo correo", 1, 1)

        navegador.find_element(By.XPATH, path_campo_correo).send_keys(credenciales[numero_usuario]["correo"])
        time.sleep(1)

        navegador.find_element(By.XPATH, path_boton_continuar).click()
        time.sleep(1)

        navegador.find_element(By.XPATH, path_campo_contrasenia).send_keys(credenciales[numero_usuario]["contra"])
        time.sleep(1)
        navegador.find_element(By.XPATH, path_boton_enviar).click()
        time.sleep(5)

contador_reinicio = 1

def comenzar_a_publicar(navegador, numero_usuario, ide):
    """
        Inicia el proceso de publicación en el sitio web. Intenta hacer clic en el botón de publicar y
        maneja fallos potenciales reiniciando el proceso hasta 5 veces.

        Parámetros:
            navegador (webdriver): El controlador del navegador Selenium.
        """
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se intenta clickear el boton publicar", 1)
    global contador_reinicio
    max_intentos = 5

    def intentar_clic(xpath):
        try:
            navegador.find_element(By.XPATH, xpath).click()
            time.sleep(2)
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se clickeo el boton Iniciar a publicar", 1)
            return True
        except Exception as e:
            escribir_en_log(f"[usuario:{numero_usuario}][intento:{contador_reinicio}]No se pudo clickear el boton Iniciar a publicar", 1)
            #print(f"Error al intentar hacer clic en el botón con XPATH: {xpath}. Excepción: {e}")
            return False

    esperarPorObjeto(navegador, 10, By.XPATH, path_boton_publicar, "Iniciar publicacion", numero_usuario, ide)
    if not intentar_clic(path_boton_publicar):
        if not intentar_clic(path_boton_publicar2):
            contador_reinicio += 1
            if contador_reinicio < max_intentos:

                reiniciar_publicar_info(navegador)
                comenzar_a_publicar(navegador, numero_usuario, ide)
            else:
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][intentos:{contador_reinicio}]No se pudo inciar la publicacion", 3)

                return
    # se cierran las ventanas de continuar o seguir la publicacion en caso que la anterior no se halla publicado
    try:
        navegador.find_element(By.XPATH, "/html/body/div[14]/div/div[2]/div[2]").click()
        time.sleep(2)
    except Exception as e:
        pass
        #print(f"No se pudo cerrar la ventana modal. Excepción: {e}")


    try:
        navegador.find_element(By.XPATH, "/html/body/div[14]/div/div[2]/div[2]").click()
        time.sleep(2)
    except:
        pass

def reiniciar_publicar_info(navegador):
    try:
        time.sleep(2)
        navegador.get("https://www.infocasas.com.py/sitio/index.php?mid=inmobiliarias&func=panel")
        time.sleep(5)
    except:
        time.sleep(2)
        navegador.get("https://www.infocasas.com.py/soyinmobiliaria")
        time.sleep(5)

def obtener_ide_para_publicar_info(numero_usuario):

    base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))
    columna = f"{numero_usuario}publicado_info"
    try:
        ide = base_remax.loc[(base_remax[columna].isna()) & (pd.notna(base_remax['ide'])) & (base_remax["intentos_info"] < 3)]['ide'].to_list()
    except:
        base_remax["intentos_info"] = 1
        ide = \
        base_remax.loc[(base_remax[columna].isna()) & (pd.notna(base_remax['ide'])) & (base_remax["intentos_info"] < 3)][
            'ide'].to_list()
    base_remax = ""

    return ide

def rellenar_titulo_info(titulo, navegador, numero_usuario):
    global VAR_VALIDACIONES
    #titulo = titulo["titulo"].to_list()[0]
    titulo = titulo.strip().lstrip()

    try:
        navegador.find_element(By.XPATH, path_campo_titulo).send_keys(titulo)
        VAR_VALIDACIONES['set_titulo'] = True
        escribir_en_log(f"[usuario:{numero_usuario}]Se seteo el titulo [titulo:{titulo}]", 1)
    except:
        escribir_en_log(f"[usuario:{numero_usuario}][titulo:{titulo}]No se seteo el titulo", 3)

        VAR_VALIDACIONES['set_titulo'] = False

def elejir_precio_info(lista_precio, navegador, numero_usuario, ide):
    global VAR_VALIDACIONES
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se va a setear el precio [{lista_precio[0]}-{lista_precio[1]}]", 1)
    if lista_precio[1] == "USD":
        navegador.find_element(By.XPATH,
                               "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[4]/div[2]/div[2]/div[1]/a").click()
        time.sleep(0.5)
        navegador.find_element(By.XPATH, "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[4]/div[2]/div[2]/div[2]/ul/li[2]").click()
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se cambio el tipo de moneda a USD", 1)

    try:
        navegador.find_element(By.XPATH,
                               path_campo_precio).send_keys(lista_precio[0])
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo el precio", 1)
        VAR_VALIDACIONES["set_precio"] = True
    except:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear el precio", 3)

        VAR_VALIDACIONES["set_precio"] = False

    time.sleep(0.5)

def setear_zona_barrio(navegador, ciudad, numero_usuario, ide):
    """
    Setea el campo barrio dependiendo de la ciudad proporcionada.

    Parámetros:
        navegador (webdriver): El controlador del navegador Selenium.
        ciudad (str): La ciudad para la cual se debe setear el barrio.

    Maneja:
        - Asunción
        - San Bernardino
        - Fernando de la Mora
        - Luque
        - San Lorenzo
    """
    global VAR_VALIDACIONES
    ciudades_zonas = {
        "Asuncion": "Asunción, Asunción\t",
        "Sanber": "San Bernardino, Cordillera\t",
        "Fernando": "Fernando de la Mora, Central\t",
        "Luque": "Luque, Central\t",
        "Sanlo": "San Lorenzo, Central\t",
        "Lamba": "Lambaré, Central\t",
        "Aregua":"Areguá, Central\t",
        "Altos": "Altos, Cordillera\t",
        "VillaElisa":"Villa Elisa, Central\t",
        "Presidente": "Villa Hayes, Presidente Hayes\t",
        "Ñemby": "Ñemby, Central\t",
        "Capiata": "Capiatá, Central\t"
    }

    palabra = ciudades_zonas.get(ciudad, "")
    try:
        navegador.find_element(By.XPATH, path_campo_ciudad).send_keys(palabra)
        VAR_VALIDACIONES["set_barrio"] = True
        VAR_VALIDACIONES["set_ciudad"] = True
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo la zona de la propiedad", 2)
    except NoSuchElementException:
        VAR_VALIDACIONES["set_barrio"] = False
        VAR_VALIDACIONES["set_ciudad"] = False
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear la zona de la propiedad", 2)

    time.sleep(0.5)


def setear_dormitorio_banios(navegador, base, numero_usuario, ide):
    """
    Setea el número de dormitorios y baños dependiendo de los datos en la base.

    Parámetros:
        navegador (webdriver): El controlador del navegador Selenium.
        base (DataFrame): El DataFrame con los datos de propiedades.
        ide (str): El identificador de la propiedad en la base de datos.
    """
    global VAR_VALIDACIONES

    def seleccionar_elemento(xpath):
        try:
            navegador.find_element(By.XPATH, xpath).click()
            return True
        except NoSuchElementException:
            escribir_en_log(f"No se encotro el [path:{xpath}]", 2)

        except Exception as e:
            pass
        return False

    # Obtener valores de habitaciones y baños
    habitaciones = base.loc[base['ide'] == ide, 'habitaciones'].values[0]
    banios = base.loc[base['ide'] == ide, 'banio'].values[0]
    # Setear habitaciones
    if pd.notna(habitaciones):
        if habitaciones <= 5:
            xpath_habitaciones = f"{path_dormitorio[0]}{habitaciones + 1}{path_dormitorio[1]}"
        else:
            xpath_habitaciones = f"{path_dormitorio[0]}6{path_dormitorio[1]}"

        VAR_VALIDACIONES["set_habitaciones"] = seleccionar_elemento(xpath_habitaciones)
    else:
        # entonces seteamos por default el minimo para que pueda publicarse
        seleccionar_elemento("/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[2]/div/div[1]/div")
        VAR_VALIDACIONES["set_habitaciones"] = True
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo habitaciones", 1)
    time.sleep(0.5)

    # Setear baños
    if pd.notna(banios):
        if banios <= 3:
            xpath_banios = f"{path_banios[0]}{banios}{path_banios[1]}"
        else:
            xpath_banios = f"{path_banios[0]}3{path_banios[1]}"

        VAR_VALIDACIONES["set_banios"] = seleccionar_elemento(xpath_banios)
    else:
        # entonces seteamos por default el minimo para que pueda publicarse
        seleccionar_elemento("/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[3]/div/div[1]/div")
        VAR_VALIDACIONES["set_banios"] = True
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo banios", 1)

    # Si fallaron ambas validaciones iniciales, intentar de nuevo para habitaciones
    if not VAR_VALIDACIONES["set_habitaciones"] and not VAR_VALIDACIONES["set_banios"]:
        if pd.notna(habitaciones):
            if habitaciones <= 5:
                xpath_habitaciones = f"{path_dormitorio[0]}{habitaciones + 1}{path_dormitorio[1]}"
            else:
                xpath_habitaciones = f"{path_dormitorio[0]}6{path_dormitorio[1]}"

            VAR_VALIDACIONES["set_habitaciones"] = seleccionar_elemento(xpath_habitaciones)
            if not VAR_VALIDACIONES["set_habitaciones"]:
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][habitaciones:{habitaciones}][banios:{banios}]", 1)
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear las habitaciones", 2)

    time.sleep(0.5)


def setear_estado(navegador, numero_usuario, ide):
    global VAR_VALIDACIONES
    try:
        navegador.find_element(By.XPATH, path_estado).click()
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo estado", 1)
        VAR_VALIDACIONES["set_estado"] = True
    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear el estado de la propiedad", 1)
        VAR_VALIDACIONES["set_estado"] = False

def filtrar_caracteres_bmp(texto):
    # Expresión regular para encontrar caracteres fuera del BMP
    bmp_regex = re.compile(r'[^\u0000-\uFFFF]')
    # Filtrar caracteres fuera del BMP y retornar el texto modificado
    return bmp_regex.sub('', texto)

def rellenar_descripcion_info(descripcion, navegador, numero_usuario, ide):
    #print(descripcion)
    global VAR_VALIDACIONES
    time.sleep(0.5)
    try:
        try:
            navegador.find_element(By.XPATH,path_descripcion).send_keys(descripcion)
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo la descripcion sin filtrar caracteres", 1)
        except:
            navegador.find_element(By.XPATH, path_descripcion).send_keys(filtrar_caracteres_bmp(descripcion))
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo la descripcion sin filtrando caracteres", 1)
        VAR_VALIDACIONES['set_descripcion'] = True
    except Exception as e:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se encontro un error al querer setear la descripcion", 3)
        VAR_VALIDACIONES['set_descripcion'] = False

    time.sleep(0.5)

def obtener_datos_propiedad(ide, base_remax):
    """
    Obtiene los datos de una propiedad según su ide.

    Parámetros:
        ide (int): El identificador de la propiedad.
        base_remax (pd.DataFrame): DataFrame que contiene la información de todas las propiedades.

    Retorna:
        dict: Diccionario con los datos de la propiedad.
    """
    propiedad = {}
    # procesar precio
    precio_valor = base_remax.loc[base_remax['ide'] == ide]['precio'].to_list()[0]

    precio_valor = precio_valor.strip().lstrip()
    precio_valor = precio_valor.split(" ")
    tipo_moneda = precio_valor[1]
    precio = int(float(precio_valor[0].replace(",", "")))  # inicialmente estaba convertido a float

    propiedad["tipo_moneda"] = tipo_moneda
    propiedad["precio"] = precio

    propiedad['tipo'] = base_remax.loc[base_remax['ide'] == ide]['tipo'].to_list()[0]
    propiedad['titulo'] = base_remax.loc[base_remax['ide'] == ide]['titulo'].to_list()[0]
    propiedad['descripcion'] = base_remax.loc[base_remax['ide'] == ide]['descripcion'].to_list()[0]
    propiedad['ciudad'] = base_remax.loc[base_remax['ide'] == ide]['ciudad'].to_list()[0]
    propiedad['mts'] = base_remax.loc[base_remax['ide'] == ide]['mts'].to_list()[0]
    try:
        propiedad['area'] = base_remax.loc[base_remax['ide'] == ide]['area'].to_list()[0]
    except:
        propiedad["area"] = 0
    if pd.isna(propiedad["area"]):
        propiedad["area"] = 0

    if pd.isna(propiedad["mts"]):
        propiedad["mts"] = 0

    return propiedad
def insertar_imagenes_info(ide, navegador, numero_usuario):
    global VAR_VALIDACIONES
    se_abrio_ventana_archivos = False
    script = (
        "var selectElement = document.evaluate(\"/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[2]/div[1]/div[2]/ul/li[2]/div\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
        "var event = new Event('mousedown');"
        "selectElement.dispatchEvent(event);"
        "selectElement.click();")
    time.sleep(1)
    try:
        # ejecuta el script para dar click en donde se deben insertar las imagenes
        navegador.execute_script(script)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se ejecuto el script para abrir la ventana para insertar las imagenes", 1)
    except:

        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo abrir la ventana para cargar las imagenes", 2)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se va a reiniciar el proceso", 2)
        # setear validaciones en false
        resetear_variables_validacion()
        comenzar_a_publicar(navegador, numero_usuario, ide)

        # recorrer_resultados_pendientes_a_publicar_info(driver)
        base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))

        datos_propiedad = obtener_datos_propiedad(ide, base_remax)

        tipo = datos_propiedad['tipo']
        titulo = datos_propiedad['titulo']
        descripcion = datos_propiedad['descripcion']
        ciudad = datos_propiedad['ciudad']
        precio = datos_propiedad['precio']
        tipo_moneda = datos_propiedad['tipo_moneda']
        mts = datos_propiedad['mts']

        rellenar_titulo_info(titulo, navegador, numero_usuario)
        se_abrio_ventana_archivos = False
        script = (
            "var selectElement = document.evaluate(\"/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[2]/div[1]/div[2]/ul/li[2]/div\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
            "var event = new Event('mousedown');"
            "selectElement.dispatchEvent(event);"
            "selectElement.click();")
        time.sleep(1)
        try:
            navegador.execute_script(script)
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se ejecuto el script para abrir la ventana para insertar las imagenes", 1)

        except:
            VAR_VALIDACIONES['set_imagenes'] = False
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear las imagenes", 3)
            return False

    time.sleep(5)
    # se crea una lista con las carpetas desde C: hasta llegar a la carpetacorrespondiente al inmueble
    carpetas_hasta_datos = str(PurePath(RUTA_BOT, RUTA_DATOS, ide)).split('\\')
    carpetas_hasta_datos = ["\\".join(carpetas_hasta_datos[0:len(carpetas_hasta_datos)-2])]+carpetas_hasta_datos[len(carpetas_hasta_datos)-2:len(carpetas_hasta_datos)]
    
    # lista los nombres de las imagenes almacenadas dentro de la carpeta img del inmueble
    nombre_imgs = os.listdir(PurePath(RUTA_BOT, RUTA_DATOS, ide, 'img'))
    try:
        # se obtiene la ventana emegente
        file_dialog = gw.getWindowsWithTitle("Abrir")[0]
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se obtienen las ventanas abiertas", 1)
        # Activa la ventana emergente
        file_dialog.activate()
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se activo la ventana abierta", 1)
    except:
        time.sleep(3)
        try:
            # En caso que halla tardado
            file_dialog = gw.getWindowsWithTitle("Abrir")[0]
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se obtienen las ventanas abiertas", 1)
            # Activa la ventana emergente
            file_dialog.activate()
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se activo la ventana abierta", 1)
        except:

            navegador.execute_script(script)
            escribir_en_log(
                f"[usuario:{numero_usuario}][ide:{ide}]Se ejecuto el script para abrir la ventana para insertar las imagenes", 1)
            try:
                file_dialog = gw.getWindowsWithTitle("Abrir")[0]  # Cambia "Abrir" al título correcto de la ventana
                # Activa la ventana emergente
                file_dialog.activate()
                se_abrio_ventana_archivos = True
            except:
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear las imagenes", 3)

                se_abrio_ventana_archivos = False


    time.sleep(2)
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Comienza a escribirse la direccion de la carpeta", 1)
    for car in carpetas_hasta_datos:

        # Envía la ruta del archivo
        pyautogui.write(car)  # Cambia la ruta y el nombre del archivo según tus necesidades
        pyautogui.press("enter")
        if car == "datos":
            time.sleep(2)
        else:
            time.sleep(0.5)

    pyautogui.write("img")  # Cambia la ruta y el nombre del archivo según tus necesidades
    pyautogui.press("enter")
    time.sleep(1)
    lista_final_imagenes = ''
    # se genera un texto con todas las imagenes para ingresarlas de una ya que estamos ubicados en la carpeta img
    contador_imagenes = 0
    for img in nombre_imgs:
        lista_final_imagenes += f'"{img}" '
        contador_imagenes += 1
        if contador_imagenes > 9:  # infocasas solo admite 14 imagenes
            break
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se inserta los nombres de las imagenes", 1)
    pyautogui.write(lista_final_imagenes)  # Cambia la ruta y el nombre del archivo según tus necesidades
    pyautogui.press("enter")
    time.sleep(0.6)
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se valida que se hallan insertado bien", 1)
    lista_ventanas_final = gw.getWindowsWithTitle("Abrir")
    if len(lista_ventanas_final) > 0:
        VAR_VALIDACIONES['set_imagenes'] = False
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se econtro que la ventana para insertar imagenes sigue abierta", 3)

        for ventana in lista_ventanas_final:
            ventana.close()
        return

    # pyautogui.press("enter")
    set_imagenes = True

    VAR_VALIDACIONES['set_imagenes'] = True

    time.sleep(5)

def seleccionar_tipo_info(tipo, navegador, numero_usuario, ide):
    global VAR_VALIDACIONES
    time.sleep(1)
    try:
        navegador.find_element(By.XPATH, path_seleccion_tipo_propiedad).click()

    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][funcion:seleccionar_tipo_info][intento:1]Error al queres seleccionar el tipo ", 2)

        time.sleep(2)
        try:
            navegador.find_element(By.XPATH, path_seleccion_tipo_propiedad2).click()
        except:
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][funcion:seleccionar_tipo_info][intento:2]Error al queres seleccionar el tipo", 2)

    time.sleep(1)
    try:
        navegador.find_element(By.XPATH, f"{path_tipo_propiedad[0]}{CATEGORIAS[tipo]}{path_tipo_propiedad[1]}").click()
    except:
        print("Se encontro un error al querer cambiar la categoria: ", tipo)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][funcion:seleccionar_tipo_info][intento:1][cat:{tipo}]Error al querer seleccionar categoria", 2)
        time.sleep(1)
        try:
            navegador.find_element(By.XPATH,
                                   f"{path_tipo_propiedad[0]}{CATEGORIAS[tipo]}{path_tipo_propiedad[1]}").click()
        except:
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][funcion:seleccionar_tipo_info][intento:2][cat:{tipo}]Error al querer seleccionar categoria", 2)
def obtener_entero(dato):
    if pd.notna(dato):
        if "," in str(dato):
            if "." not in str(dato):
                mts = str(dato).replace(",", "")
                mts = int(mts)
            else:
                mts = str(dato).replace(",", "")
                mts = float(mts)
                mts = int(mts)
        else:
            mts = float(dato)
            mts = int(mts)
    else:
        mts = 1

    return mts
def setear_mts(navegador, construccion, tipo, numero_usuario, ide):

    path_mts_edificados = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[11]/div/input"
    path_mts_terreno = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[2]/div[1]/div/input"

    mts = construccion[0]
    area = construccion[1]
    global VAR_VALIDACIONES
    # convertir a entero
    mts = obtener_entero(mts)
    area = obtener_entero(area)

    if tipo == "Terreno":
        path_mts_terreno = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[2]/div[1]/div/input"

    try:
        navegador.find_element(By.XPATH, path_mts_terreno).send_keys(mts)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][mts:{mts}]Se seteo los metros de la propiedad", 1)
        VAR_VALIDACIONES['set_metros'] = True
    except:

        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][metros:{mts}]No se pudo setear los metros cuadrados de la propiedad", 3)
        VAR_VALIDACIONES['set_metros'] = False
    try:
        navegador.find_element(By.XPATH, path_mts_edificados).send_keys(area)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][mts:{area}]Se seteo los metros de la propiedad", 1)
        VAR_VALIDACIONES['set_metros'] = True

    except:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][metros:{area}]No se pudo setear los metros cuadrados de la propiedad", 3)


def setear_comodidad_seguridad(navegador, tipo, numero_usuario, ide):
    path_comodidad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[6]/div[2]/div/div/div[1]/a"
    path_seleccion_comodidad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[6]/div[2]/div/div/div[2]/ul[1]/li[1]"
    path_seguridad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[7]/div[2]/div/div[1]/a"
    parh_seleccion_seguridad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[7]/div[2]/div/div[2]/ul/li[6]"

    if tipo == "Departamento":
        path_seleccion_comodidad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[6]/div[2]/div/div/div[2]/ul/li[3]/ul/li[1]"

    try:
        navegador.find_element(By.XPATH, path_comodidad).click()
        time.sleep(1)
        navegador.find_element(By.XPATH, path_seleccion_comodidad).click()
        VAR_VALIDACIONES['set_seguridad'] = True
    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear comodidad", 2)

    # para cerrar u ocultar panel de seleccion
    try:
        navegador.find_element(By.XPATH, path_comodidad).click()
    except:
        pass
    time.sleep(1)
    navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Esperar un momento para que cargue el contenido adicional (si lo hay)
    # Hacer scroll hacia arriba
    navegador.execute_script("window.scrollTo(0, 0);")
    try:
        navegador.find_element(By.XPATH, path_seguridad).click()
        time.sleep(1)
        navegador.find_element(By.XPATH, parh_seleccion_seguridad).click()
        VAR_VALIDACIONES['set_seguridad'] = True
    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear seguridad", 2)

    try:
        navegador.find_element(By.XPATH, path_seguridad).click()

    except:
        pass

    if tipo == "Edificio":

        VAR_VALIDACIONES['set_seguridad'] = True


def corregir_validacion(tipo_propiedad):
    # esta funcion cambia a true los campos que estan en false
    # por que no son obligatorios completar para hacer una publicacion
    # entonces no va a generar error alguno
    global CATEGORIAS, VAR_VALIDACIONES
    try:
        numero = CATEGORIAS[tipo_propiedad]
    except KeyError:
        numero = 1
    if numero == 1 or numero == 4 or numero == 5:
        VAR_VALIDACIONES['set_descripcion'] = True
    elif numero == 3 or numero == 10:
        VAR_VALIDACIONES['set_habitaciones'] = True
        VAR_VALIDACIONES['set_banios'] = True
        VAR_VALIDACIONES['set_descripcion'] = True
        VAR_VALIDACIONES['set_estado'] = True
        VAR_VALIDACIONES['set_metros'] = True

    elif numero == 6:
        VAR_VALIDACIONES['set_descripcion'] = True
        VAR_VALIDACIONES['set_habitaciones'] = True
        VAR_VALIDACIONES['set_banio'] = True
        VAR_VALIDACIONES['set_estado'] = True
        VAR_VALIDACIONES['set_metros'] = True




def validar_existencia_imagenes(ide, numero_usuario):
    """
        valida que se hallan descargado imagenes para la propiedad
        Args:
            ide (str): ide de la propiedad y nombre de la carpeta.
        Returns:
            boolean: Verdadero si existe
    """

    # lista datos/ide/
    carpetas_dentro_datos = os.listdir(RUTA_DATOS)
    # valida si existe la carpeta datos/ide
    if ide in carpetas_dentro_datos:
        # valida que haya imagenes dentro
        imagenes_dentro_propiedad = os.listdir(PurePath(RUTA_DATOS, ide))
        if len(imagenes_dentro_propiedad) > 0:
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][tiene_imagenes:True]", 1)
            return True
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][tiene_imagenes:False]", 1)
        return False
    else:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][tiene_imagenes:False]No existe la carpeta con el ide", 1)
        return False

def resetear_variables_validacion():

    """
        resetea el estado de las variables de validacion,
        se debe realizar al comenzar a publicar
    """
    global VAR_VALIDACIONES
    # variables de validacion para corroborar que se hallan seteado todos los campos correctamente
    VAR_VALIDACIONES['set_titulo'] = False
    VAR_VALIDACIONES['set_descripcion'] = False
    VAR_VALIDACIONES['set_precio'] = False
    VAR_VALIDACIONES['set_ciudad'] = False
    VAR_VALIDACIONES['set_imagenes'] = False
    VAR_VALIDACIONES['set_barrio'] = False
    VAR_VALIDACIONES['set_banios'] = False
    VAR_VALIDACIONES['set_habitaciones'] = False
    VAR_VALIDACIONES['set_estado'] = False
    VAR_VALIDACIONES['set_seguridad'] = True
    VAR_VALIDACIONES['set_metros'] = False


def recorrer_resultados_pendientes_a_publicar_info(navegador, numero_usuario, cantidad_a_publicar):
    """
        Procesa y publica propiedades pendientes de publicación en infocasas.

        Parámetros:
            navegador (webdriver): El controlador del navegador Selenium.
            numero_usuario (str): El identificador del usuario.
            cantidad_a_publicar (int): La cantidad de propiedades a publicar.
        """
    global VAR_VALIDACIONES
    # para contar iteraciones
    contador = 1
    contador_publicados = 0
    # obtener ides de propiedades pendientes a publicar
    ides_pendientes = obtener_ide_para_publicar_info(numero_usuario)

    #ides_pendientes = ["143059035-33"]
    escribir_en_log(f"[usuario:{numero_usuario}]Se debe realizar {cantidad_a_publicar} publicaciones", 1)
    escribir_en_log(f"[usuario:{numero_usuario}] {len(ides_pendientes)} ides pendientes para este usuario", 1)
    # Cargar datos de propiedades


    for ide in ides_pendientes:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][Intento actual:{contador}]", 1)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][contador_publicados:{contador_publicados}]", 1)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Comienza a publicarse ", 1)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se valida que tenga imagenes en su carpeta", 1)

        if validar_existencia_imagenes(ide, numero_usuario):
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][validar_existencia_imagenes:True]", 1)
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Inicia setear campos", 1)
            # Resetear validaciones
            resetear_variables_validacion()
            # recorrer_resultados_pendientes_a_publicar_info(driver)
            base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))
            comenzar_a_publicar(navegador, numero_usuario, ide)
            # obtener los datos de la propiedad segun su ide
            datos_propiedad = obtener_datos_propiedad(ide, base_remax)
            tipo = datos_propiedad['tipo']
            titulo = datos_propiedad['titulo']
            descripcion = datos_propiedad['descripcion']
            ciudad = datos_propiedad['ciudad']
            precio = datos_propiedad['precio']
            tipo_moneda = datos_propiedad['tipo_moneda']
            mts = datos_propiedad['mts']
            try:
                area = datos_propiedad["area"]
            except:
                area = 0

            construccion = [mts, area]

            # comenzamos a rellenar los campos en el formulario de publicacion
            rellenar_titulo_info(titulo, navegador, numero_usuario)
            insertar_imagenes_info(ide, navegador, numero_usuario)
            if VAR_VALIDACIONES['set_imagenes']:
                elejir_precio_info([precio, tipo_moneda], navegador, numero_usuario, ide)
                setear_zona_barrio(navegador, ciudad, numero_usuario, ide)
                seleccionar_tipo_info(tipo, navegador, numero_usuario, ide)
                setear_dormitorio_banios(navegador, base_remax, numero_usuario,ide)
                setear_estado(navegador, numero_usuario, ide)
                rellenar_descripcion_info(descripcion, navegador, numero_usuario, ide)
                setear_mts(navegador, construccion, tipo, numero_usuario, ide)
                setear_comodidad_seguridad(navegador, tipo, numero_usuario, ide)
                corregir_validacion(tipo)
                publicar = True
                try:

                    if tipo == "Depósito" or CATEGORIAS[tipo] == 10:
                        VAR_VALIDACIONES["set_estado"] = True
                        VAR_VALIDACIONES["set_estado"] = True
                        VAR_VALIDACIONES["set_metros"] = True
                except:
                    if tipo == "Deposito":
                        VAR_VALIDACIONES["set_estado"] = True
                        VAR_VALIDACIONES["set_estado"] = True
                        VAR_VALIDACIONES["set_metros"] = True


                for key in VAR_VALIDACIONES:

                    if VAR_VALIDACIONES[key] == False:
                        publicar = False
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][se_puede_publicar:{publicar}]", 1)

                if publicar:

                    try:
                        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se intenta clickear el boton para publicar", 2)
                        navegador.find_element(By.XPATH, "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[3]").click()
                        indice = base_remax.loc[base_remax['ide'] == ide].index[0]
                        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Esperando que cargue la ventana publicado", 2)
                        publicado = esperarPorObjeto(navegador, 5, By.XPATH, "/html/body/div/div/div/div[1]/div[2]/div/div[2]/div[1]", "Publicado", numero_usuario, ide)
                        if publicado:

                            base_remax.loc[indice, f'{numero_usuario}publicado_info'] = '1'
                            contador_publicados += 1
                            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Publicado!", 1)
                            # se actualiza la base
                            base_remax.to_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'), index=False)
                            try:
                                base_remax.to_excel(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.xlsx'), index=False)
                            except Exception as ex:
                                pass
                            if contador_publicados >= cantidad_a_publicar:
                                escribir_en_log(f"[usuario:{numero_usuario}][publicados:{contador_publicados}]Se alcanzo la cantidad de publicaciones establecida", 1)
                                break
                    except:
                        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Por algun motivo no se pudo publicar la propiedad", 3)
                        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}] {VAR_VALIDACIONES}", 3)
                        pass

                else:
                    escribir_en_log(
                        f"[usuario:{numero_usuario}][ide:{ide}]Por algun motivo no se pudo publicar la propiedad", 3)
                    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}] {VAR_VALIDACIONES}", 3)
                    reiniciar_publicar_info(navegador)
                    # se incrementa el contador de intentos para tener un control y desactivar la propiedad si es que falla muchas veces
                    indice = base_remax.loc[base_remax['ide'] == ide].index[0]
                    contador_intentos_publicar = base_remax.loc[base_remax["ide"] == ide]["intentos_info"].to_list()[0]
                    if pd.notna(contador_intentos_publicar):
                        base_remax.loc[indice, "intentos_info"] = contador_intentos_publicar + 1
                    else:
                        base_remax.loc[indice, "intentos_info"] = 1
                    base_remax.to_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'), index=False)
                    try:
                        base_remax.to_excel(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.xlsx'), index=False)
                    except:
                        pass
                reiniciar_publicar_info(navegador)

            else:
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear las imagenes", 3)
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Reiniciando proceso", 2)
                reiniciar_publicar_info(navegador)

        contador += 1