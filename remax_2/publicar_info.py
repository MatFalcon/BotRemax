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
from selenium.webdriver.common.keys import Keys

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

RUTA_BOT = PurePath(Path().absolute())
RUTA_DATOS = PurePath(RUTA_BOT, "datos")
RUTA_DRIVER = f"{PurePath(RUTA_BOT, "driver")}\\msedgedriver.exe"
edge_driver_path = RUTA_DRIVER

driver = ""

# Rutas
RUTA_BOT = PurePath(Path().absolute())
RUTA_DATOS = PurePath(RUTA_BOT, "datos")
RUTA_DRIVER = f"{PurePath(RUTA_BOT, "driver")}\\msedgedriver.exe"
RUTA_ARCHIVO_CSV = PurePath(RUTA_BOT,'driver','remax_propiedades.csv')

# Categorias y validaciones
CATEGORIAS = {
    "departamento":2,
    "casa":1,
    "oficinas":6,
    "departamento-en-pozo":2,
    "terreno":3,
    "Residencia": 1,
    "Departamento": 2,
    "Departamento con Jardín": 2,
    "Casa": 1,
    "Terreno": 3,
    "Duplex": 5,
    "Edificio": 10,
    "Depósito": 11,
    "Local Comercial": 4,
    "Oficina": 6,
    "Office Space":6,
    "Casa de Verano": 1,
    "Chalet": 1,
    "Atypical": 1,
    "Bloque de departamentos": 2,
    "Business": 10,
    "Casa de campo": 1,
    "Condominio de Lujo": 1,
    "Departamento con servicio de Hotel": 2,
    "Habitación": 2,
    "Health Clinic": 4,
    "Hotel": 10,
    "Industria": 4,
    "Nueva Construcción": 10,
    "Quinta": 1,
    "Triplex": 5,
    "Espacio de estacionamiento":3,
    "Sin Tipo":1,
    "Accommodation":1,
    "Villa": 1,
    "Sports Centre": 1
}
VAR_VALIDACIONES = {
    'set_titulo': False, 'set_descripcion': False, 'set_precio': False, 'set_ciudad': False,
    'set_imagenes': False, 'set_barrio': False, 'set_banios': False, 'set_habitaciones': False,
    'set_estado': False, 'set_seguridad': False, 'set_metros': False,
}

# Xpaths
path_boton_ingresar1 = "/html/body/div[1]/div[6]/div/ul[2]/li[4]/a/span"
path_boton_ingresar = "/html/body/div/div/header/div[1]/button"
path_campo_correo = "/html/body/div[5]/div/div[2]/form/div[1]/input"
path_boton_continuar = "/html/body/div[5]/div/div[2]/form/div[1]/div[2]"
path_campo_contrasenia = "/html/body/div[5]/div/div[2]/form/div[2]/input"
path_boton_enviar = "/html/body/div[5]/div/div[2]/form/div[2]/div[2]"
path_boton_publicar = "/html/body/div[1]/div[6]/div/ul[2]/li[4]/a"
path_boton_publicar2 = "/html/body/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div[2]/a"
# variables para publicaciones
path_campo_titulo = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[1]/div[1]/input[1]"
path_campo_precio = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[4]/div[3]/div[1]/input"
path_campo_ciudad = '/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[6]/div[2]/div/input'
path_campo_zona = '/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[6]/div[3]/div[2]/input'
path_dormitorio = ["/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[2]/div/div[", "]/div"]
path_banios = ["/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[3]/div/div[","]/div"]
path_estado = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[5]/div/div[3]/div"
path_descripcion = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[2]/div[4]/div[3]/div[2]/div[1]"
path_seleccion_img = "/html/body/div[1 n]/div[8]/div[2]/div[2]/form/div[2]/div[2]/div[1]/div[2]/ul/li[2]/input"
path_seleccion_tipo_propiedad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[4]/div[2]/div/div[1]/a"
path_seleccion_tipo_propiedad2 = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[6]/div[2]/div/div[1]/i"
path_tipo_propiedad = ["/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[4]/div[2]/div/div[2]/ul/li[","]"]
path_boton_guardar_publicar = '/html/body/div[1]/div[8]/div[2]/div[2]/form/div[3]'
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

        esperarPorObjeto(navegador, 10, By.XPATH, path_boton_ingresar1, "Boton Iniciar sesion test", 1, 1)

        navegador.find_element(By.XPATH, path_boton_ingresar1).click()
        time.sleep(0.5)

        esperarPorObjeto(navegador, 3, By.XPATH, path_campo_correo, "Campo correo", 1, 1)

        navegador.find_element(By.XPATH, path_campo_correo).send_keys(credenciales[numero_usuario]["correo"])
        time.sleep(1)

        navegador.find_element(By.XPATH, path_boton_continuar).click()
        time.sleep(2)

        # Esperar a que el campo de contraseña sea interactuable (visible y habilitado)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:1]Esperando que el campo de contraseña sea interactuable", 2)
        try:
            WebDriverWait(navegador, 10).until(
                expected_conditions.element_to_be_clickable((By.XPATH, path_campo_contrasenia))
            )
            escribir_en_log(f"[usuario:{numero_usuario}][ide:1]Campo de contraseña listo para interactuar", 1)
        except Exception as e:
            escribir_en_log(f"[usuario:{numero_usuario}][ide:1]El campo de contraseña no se volvió interactuable: {e}", 2)
            # Intentar hacer scroll al elemento
            try:
                elemento = navegador.find_element(By.XPATH, path_campo_contrasenia)
                navegador.execute_script("arguments[0].scrollIntoView(true);", elemento)
                time.sleep(1)
            except:
                pass

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
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se intenta clickear el boton publicar 3", 1)
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

    # Leer CSV
    base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))
    escribir_en_log(f"[usuario:{numero_usuario}] CSV cargado exitosamente", 1)
    escribir_en_log(f"[usuario:{numero_usuario}] Total de filas: {len(base_remax)}", 1)
    escribir_en_log(f"[usuario:{numero_usuario}] Columnas disponibles: {list(base_remax.columns)}", 1)
    
    # Inicializar intentos_info en 0 si está en NaN
    escribir_en_log(f"[usuario:{numero_usuario}] ANTES: intentos_info NaN: {base_remax['intentos_info'].isna().sum()}", 1)
    base_remax["intentos_info"] = base_remax["intentos_info"].fillna(0)
    escribir_en_log(f"[usuario:{numero_usuario}] DESPUÉS: intentos_info NaN: {base_remax['intentos_info'].isna().sum()}", 1)
    
    # Guardar los cambios en el CSV
    base_remax.to_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'), index=False)
    escribir_en_log(f"[usuario:{numero_usuario}] CSV actualizado con intentos_info inicializados en 0", 1)
    
    columna = f"{numero_usuario}publicado_info"
    escribir_en_log(f"[usuario:{numero_usuario}] Buscando propiedades con columna: {columna}", 1)
    
    try:
        # Verificar si la columna existe
        if columna not in base_remax.columns:
            escribir_en_log(f"[usuario:{numero_usuario}] ADVERTENCIA: Columna '{columna}' no existe", 2)
            raise KeyError(f"Columna {columna} no existe")
        
        # Log de cada condición de filtro
        cond_no_publicado = base_remax[columna].isna()
        cond_ide_valido = pd.notna(base_remax['ide'])
        cond_intentos = base_remax["intentos_info"] < 3
        
        escribir_en_log(f"[usuario:{numero_usuario}] Propiedades SIN publicar (columna vacía): {cond_no_publicado.sum()}", 1)
        escribir_en_log(f"[usuario:{numero_usuario}] Propiedades CON ide válido: {cond_ide_valido.sum()}", 1)
        escribir_en_log(f"[usuario:{numero_usuario}] Propiedades CON intentos < 3: {cond_intentos.sum()}", 1)
        
        # Aplicar todos los filtros
        ide = base_remax.loc[cond_no_publicado & cond_ide_valido & cond_intentos]['ide'].to_list()
        escribir_en_log(f"[usuario:{numero_usuario}] Propiedades que cumplen TODOS los filtros: {len(ide)}", 1)
        
    except KeyError as e:
        escribir_en_log(f"[usuario:{numero_usuario}] ERROR: Columna no existe ({e}), creando columna 'intentos_info'", 2)
        base_remax["intentos_info"] = 0
        escribir_en_log(f"[usuario:{numero_usuario}] Columna 'intentos_info' creada con valor 0", 1)
        base_remax.to_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'), index=False)
        
        # Reintentar con la columna nueva
        cond_no_publicado = base_remax[columna].isna()
        cond_ide_valido = pd.notna(base_remax['ide'])
        cond_intentos = base_remax["intentos_info"] < 3
        
        escribir_en_log(f"[usuario:{numero_usuario}] (Reintento) Propiedades SIN publicar: {cond_no_publicado.sum()}", 1)
        escribir_en_log(f"[usuario:{numero_usuario}] (Reintento) Propiedades CON ide válido: {cond_ide_valido.sum()}", 1)
        escribir_en_log(f"[usuario:{numero_usuario}] (Reintento) Propiedades CON intentos < 3: {cond_intentos.sum()}", 1)
        
        ide = base_remax.loc[cond_no_publicado & cond_ide_valido & cond_intentos]['ide'].to_list()
        escribir_en_log(f"[usuario:{numero_usuario}] (Reintento) Propiedades que cumplen TODOS los filtros: {len(ide)}", 1)
    
    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}] ERROR inesperado en obtener_ide_para_publicar_info: {ex}", 3)
        ide = []
    
    # Log final
    escribir_en_log(f"[usuario:{numero_usuario}] IDES ENCONTRADOS: {ide}", 1)
    print(f"IDES ENCONTRADOS \n{ide}")
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
        time.sleep(1)
        navegador.find_element(By.XPATH,
                               "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[4]/div[3]/div[2]/div[1]/a").click()
        time.sleep(0.5)
        navegador.find_element(By.XPATH, "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[4]/div[3]/div[2]/div[2]/ul/li[2]/a/span").click()
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se cambio el tipo de moneda a USD", 1)

    try:
        navegador.find_element(By.XPATH,
                               path_campo_precio).send_keys(lista_precio[0])
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo el precio", 1)
        VAR_VALIDACIONES["set_precio"] = True
    except Exception as ex:
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
        "Asuncion": "Asunción, Asunción, Paraguay\t",
        "Sanber": "San Bernardino, Paraguay\t",
        "Fernando": "Fernando de la Mora, Central, Paraguay\t",
        "Luque": "Luque, Central, Paraguay\t",
        "Sanlo": "San Lorenzo, Central, Paraguay\t",
        "Lamba": "Lambaré, Central, Paraguay\t",
        "Aregua":"Areguá, Central, Paraguay\t",
        "Altos": "Altos, Cordillera\t",
        "VillaElisa":"Villa Elisa, Central\t",
        "Presidente": "Villa Hayes, Presidente Hayes\t",
        "Ñemby": "Ñemby, Central\t",
        "Capiata": "Capiatá, Central\t"
    }

    palabra = ciudades_zonas.get(ciudad, "")
    try:
        navegador.find_element(By.XPATH, path_campo_ciudad).send_keys(palabra)
        time.sleep(1)
        navegador.find_element(By.XPATH, path_campo_ciudad).send_keys(Keys.ARROW_DOWN)
        time.sleep(1)
        navegador.find_element(By.XPATH, path_campo_ciudad).send_keys(Keys.ENTER)
        time.sleep(1)
        navegador.find_element(By.XPATH, path_campo_zona).send_keys(palabra[0:8])
        time.sleep(1)
        navegador.find_element(By.XPATH, path_campo_zona).send_keys(Keys.TAB)
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
    try:
        habitaciones = base.loc[base['ide'] == ide, 'habitaciones'].values[0]
    except:
        habitaciones = 1
    try:    
        banios = base.loc[base['ide'] == ide, 'banio'].values[0]
    except:
        banios = 1
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
    # selecciona garaje    
    seleccionar_elemento("/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[4]/div/div[1]/div")
    # balcon    
    seleccionar_elemento("/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[6]/div/div[1]/div/div")
    #jardin
    seleccionar_elemento("/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[11]/div/div[1]/div")
    # estado
    time.sleep(1)   
    seleccionar_elemento("/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[5]/div/div[3]/span")
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
        # Script JavaScript para hacer click en el elemento de estado
        script = (
            "var element = document.evaluate("
            "'/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[5]/div/div[3]/div',"
            "document,"
            "null,"
            "XPathResult.FIRST_ORDERED_NODE_TYPE,"
            "null"
            ").singleNodeValue;"
            "if (element) {"
            "  element.click();"
            "} else {"
            "  console.log('Elemento no encontrado.');"
            "}"
        )
        
        # Ejecutar el script JavaScript
        navegador.execute_script(script)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo estado usando JavaScript", 1)
        VAR_VALIDACIONES["set_estado"] = True
    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear el estado de la propiedad usando JavaScript", 1)
        VAR_VALIDACIONES["set_estado"] = False

def setear_conforts(navegador, numero_usuario, ide):
    """
    Setea los conforts de la propiedad usando JavaScript para hacer click en múltiples elementos.
    """
    time.sleep(1)
    
    # Script para balcón
    try:
        script_balcon = (
            "var element = document.evaluate("
            "'/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[6]/div/div[1]/div/div',"
            "document,"
            "null,"
            "XPathResult.FIRST_ORDERED_NODE_TYPE,"
            "null"
            ").singleNodeValue;"
            "if (element) {"
            "  element.click();"
            "} else {"
            "  console.log('Elemento no encontrado.');"
            "}"
        )
        navegador.execute_script(script_balcon)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo balcón usando JavaScript", 1)
    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear balcón usando JavaScript", 2)
    
    time.sleep(0.5)
    
    # Script para terraza
    try:
        script_terraza = (
            "var element = document.evaluate("
            "'/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[7]/div/div[1]/div/div',"
            "document,"
            "null,"
            "XPathResult.FIRST_ORDERED_NODE_TYPE,"
            "null"
            ").singleNodeValue;"
            "if (element) {"
            "  element.click();"
            "} else {"
            "  console.log('Elemento no encontrado.');"
            "}"
        )
        navegador.execute_script(script_terraza)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo terraza usando JavaScript", 1)
    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear terraza usando JavaScript", 2)
    
    time.sleep(0.5)
    
    # Script para jardín
    try:
        script_jardin = (
            "var element = document.evaluate("
            "'/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[11]/div/div[1]/div/div',"
            "document,"
            "null,"
            "XPathResult.FIRST_ORDERED_NODE_TYPE,"
            "null"
            ").singleNodeValue;"
            "if (element) {"
            "  element.click();"
            "} else {"
            "  console.log('Elemento no encontrado.');"
            "}"
        )
        navegador.execute_script(script_jardin)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se seteo jardín usando JavaScript", 1)
    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear jardín usando JavaScript", 2)
    
    time.sleep(1)
    return True

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
    precio_valor = base_remax.loc[base_remax['ide'] == float(ide)]['precio'].to_list()[0]
    precio_valor = precio_valor.strip().lstrip()
    precio_valor = precio_valor.split(" ")
    tipo_moneda = precio_valor[1]
    precio = int(float(precio_valor[0].replace(",", "")))  # inicialmente estaba convertido a float

    propiedad["tipo_moneda"] = tipo_moneda
    propiedad["precio"] = precio

    propiedad['tipo'] = base_remax.loc[base_remax['ide'] == float(ide)]['tipo'].to_list()[0]
    propiedad['titulo'] = base_remax.loc[base_remax['ide'] == float(ide)]['titulo'].to_list()[0]
    propiedad['descripcion'] = base_remax.loc[base_remax['ide'] == float(ide)]['descripcion'].to_list()[0]
    propiedad['ciudad'] = base_remax.loc[base_remax['ide'] == float(ide)]['ciudad'].to_list()[0]
    # Metros de terreno y construcción.  Utilizamos 'mts' para el terreno y
    # 'mts_construccion' para metros edificados.  Si alguna columna no existe
    # en la base se asigna por defecto 0 para facilitar el manejo posterior.
    try:
        propiedad['mts'] = base_remax.loc[base_remax['ide'] == float(ide)]['mts'].to_list()[0]
    except Exception:
        propiedad['mts'] = 0

    # Leer metros de construcción desde la columna nueva.  Si no existe,
    # intentar leer desde 'area' por compatibilidad.  Si ambas fallan, usar 0.
    try:
        propiedad['mts_construccion'] = base_remax.loc[base_remax['ide'] == float(ide)]['mts_construccion'].to_list()[0]
    except Exception:
        try:
            propiedad['mts_construccion'] = base_remax.loc[base_remax['ide'] == ide]['area'].to_list()[0]
        except Exception:
            propiedad['mts_construccion'] = 0

    # Normalizar valores NaN a 0 para evitar propagación de NaNs
    if pd.isna(propiedad.get('mts')):
        propiedad['mts'] = 0
    if pd.isna(propiedad.get('mts_construccion')):
        propiedad['mts_construccion'] = 0

    # Mantener también la clave 'area' para compatibilidad antigua.  Si existe
    # la columna 'area', usar ese valor; de lo contrario asignar el mismo que
    # mts_construccion para reutilizar.
    try:
        propiedad['area'] = base_remax.loc[base_remax['ide'] == ide]['area'].to_list()[0]
    except Exception:
        propiedad['area'] = propiedad['mts_construccion']
    if pd.isna(propiedad['area']):
        propiedad['area'] = propiedad['mts_construccion']

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

        # Envia la ruta del archivo
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
    
    # Asegurar scroll arriba del todo
    try:
        navegador.execute_script("window.scrollTo(0, 0);")
    except:
        pass
    time.sleep(1)
    
    dropdown_abierto = False
    
    # Función auxiliar para intentar clickear con fallback a JS
    def intentar_click_con_fallback(xpath, nombre_path):
        try:
            elemento = navegador.find_element(By.XPATH, xpath)
            try:
                # Intentar click normal primero
                elemento.click()
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Click normal exitoso en {nombre_path}", 1)
                return True
            except:
                # Si falla, intentar click con JavaScript
                navegador.execute_script("arguments[0].click();", elemento)
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Click JS exitoso en {nombre_path}", 1)
                return True
        except Exception as e:
            return False

    # Intentar abrir el dropdown
    if intentar_click_con_fallback(path_seleccion_tipo_propiedad, "dropdown tipo path 1"):
        dropdown_abierto = True
    else:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][funcion:seleccionar_tipo_info]Falló path 1, intentando path 2", 2)
        time.sleep(1)
        if intentar_click_con_fallback(path_seleccion_tipo_propiedad2, "dropdown tipo path 2"):
            dropdown_abierto = True
            
    if not dropdown_abierto:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}] ERROR CRITICO: No se pudo abrir el dropdown de tipo", 3)
        return False
    
    time.sleep(1.5)
    
    # Obtener el número de categoría, si no existe usar 1 (Casa por defecto)
    numero_categoria = CATEGORIAS.get(tipo, 1)
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Tipo '{tipo}' mapeado a categoría {numero_categoria}", 1)
    if tipo not in CATEGORIAS:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]ADVERTENCIA: El tipo '{tipo}' no existe en CATEGORIAS, usando valor por defecto (1 - Casa)", 2)
    
    # Intentar seleccionar el tipo de propiedad
    xpath_opcion = f"{path_tipo_propiedad[0]}{numero_categoria}{path_tipo_propiedad[1]}"
    if intentar_click_con_fallback(xpath_opcion, f"opcion {tipo}"):
         escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Tipo '{tipo}' seleccionado correctamente", 1)
         return True
    else:
        # Intento con JS directo si el helper falla por alguna razon (ej: no encontró elemento)
        try:
            script = f"""
            var element = document.evaluate("{xpath_opcion}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (element) {{
                element.click();
            }}
            """
            navegador.execute_script(script)
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Tipo '{tipo}' seleccionado con Script Directo", 1)
            return True
        except Exception as ex:
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}] Error al seleccionar tipo {tipo}: {ex}", 3)
            return False

def obtener_entero(mts):
    """
    Limpia una cadena de texto de metros cuadrados (e.g., "5.281,0 m²") 
    para obtener solo el valor entero.
    """
    
    # 1. Convertir a string si no lo es (para asegurar que podemos usar .replace())
    if not isinstance(mts, str):
        mts = str(mts)
        
    # 2. Eliminar el símbolo de la unidad " m²" y posibles espacios al inicio/fin
    # Nota: Usamos re.sub para manejar cualquier tipo de espacio o caracter extra
    # al final, no solo " m²". 
    # La expresión r'[^\d,.]' eliminará cualquier cosa que no sea dígito, coma o punto.
    
    # Si sabes que el formato siempre es "X.XXX,Y m²", puedes hacer:
    mts_limpio = mts.replace(" m²", "").strip()
    
    # 3. Eliminar el separador de miles (punto)
    mts_limpio = mts_limpio.replace(".", "")
    
    # 4. Eliminar la coma decimal y lo que sigue (asumiendo que solo se quiere la parte entera)
    if ',' in mts_limpio:
        mts_limpio = mts_limpio.split(',')[0]
        
    # 5. Convertir a entero
    try:
        # Aquí es donde finalmente intentamos la conversión.
        return int(mts_limpio)
    except ValueError as e:
        # En caso de que la limpieza haya fallado por un formato inesperado
        # Imprime un mensaje de error útil para debugging
        print(f"Error al convertir a entero: '{mts}' (Limpiado a: '{mts_limpio}') -> {e}")
        # Puedes retornar un valor predeterminado (ej. 0) o volver a lanzar el error
        return 0 # Devuelve 0 o maneja el error según tu lógica de negocio

def setear_mts(navegador, construccion, tipo, numero_usuario, ide):
    # struccion es una tupla o lista: [mts_terreno, mts_construccion]
    
    path_mts_edificados = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[1]/div[11]/div/input"
    path_mts_terreno = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[2]/div[1]/div/input"

    mts_terreno = str(construccion[0]) if construccion[0] and str(construccion[0]) != 'nan' else "1"
    mts_construcc = str(construccion[1]) if construccion[1] and str(construccion[1]) != 'nan' else "1"
    
    global VAR_VALIDACIONES

    # Para terreno
    try:
        navegador.find_element(By.XPATH, path_mts_terreno).send_keys(mts_terreno)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][mts_terreno:{mts_terreno}]Se seteo los metros de terreno", 1)
        VAR_VALIDACIONES['set_metros'] = True
    except:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear los metros de terreno", 2)
        VAR_VALIDACIONES['set_metros'] = False

    # Para construccion
    try:
        navegador.find_element(By.XPATH, path_mts_edificados).send_keys(mts_construcc)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}][mts_const:{mts_construcc}]Se seteo los metros edificados", 1)
        # Si al menos uno se seteo, consideramos validado (o según requerimiento estricto)
        VAR_VALIDACIONES['set_metros'] = True
    except:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear los metros edificados", 2)


def setear_comodidad_seguridad(navegador, tipo, numero_usuario, ide):
    path_comodidad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[12]/div[2]/div/div/div[1]/a"
    path_seleccion_comodidad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[12]/div[2]/div/div/div[2]/ul/li[3]/ul/li[7]/a/span"
    path_seguridad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[13]/div[2]/div/div[1]/a"
    parh_seleccion_seguridad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[13]/div[2]/div/div[2]/ul/li[2]/a/span"


    if tipo == "Departamento":
        path_seleccion_comodidad = "/html/body/div[1]/div[8]/div[2]/div[2]/form/div[2]/div[1]/div[9]/div[6]/div[2]/div/div/div[2]/ul/li[3]/ul/li[1]"

    try:
        navegador.find_element(By.XPATH, path_comodidad).click()
        time.sleep(1)
        navegador.find_element(By.XPATH, path_seleccion_comodidad).click()
        VAR_VALIDACIONES['set_seguridad'] = True
    except Exception as ex:
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear comodidad", 2)
        time.sleep(1)

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
        ide = str(ide)
        if "." in ide:
            ide = ide.split(".")[0]
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
            mts = datos_propiedad['mts'] # Metros terreno
            try:
                mts_construccion = datos_propiedad["mts_construccion"] # Metros construccion
            except:
                mts_construccion = "1"
            
            # Pasamos lista con [terreno, construccion]
            construccion = [mts, mts_construccion]

            # comenzamos a rellenar los campos en el formulario de publicacion
            rellenar_titulo_info(titulo, navegador, numero_usuario)
            insertar_imagenes_info(ide, navegador, numero_usuario)
            if VAR_VALIDACIONES['set_imagenes']:
                elejir_precio_info([precio, tipo_moneda], navegador, numero_usuario, ide)
                setear_zona_barrio(navegador, ciudad, numero_usuario, ide)
                
                # Seleccionar tipo temporal (Departamento) para que todos los campos estén visibles
                # Esto permite setear campos que se ocultan cuando el tipo es "Terreno"
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Seteando tipo temporal 'Departamento' para mostrar todos los campos", 1)
                seleccionar_tipo_info("Departamento", navegador, numero_usuario, ide)
                setear_dormitorio_banios(navegador, base_remax, numero_usuario,ide)
                setear_estado(navegador, numero_usuario, ide)
                setear_conforts(navegador, numero_usuario, ide)
                rellenar_descripcion_info(descripcion, navegador, numero_usuario, ide)
                setear_mts(navegador, construccion, tipo, numero_usuario, ide)
                setear_comodidad_seguridad(navegador, tipo, numero_usuario, ide)
                
                # Ahora cambiar al tipo correcto de propiedad
                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Cambiando al tipo correcto: {tipo}", 1)
                seleccionar_tipo_info(tipo, navegador, numero_usuario, ide)
                
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
                
                input("Publicar si o no mrd")
                if publicar:
                    
                    try:
                        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se intenta clickear el boton para publicar 222", 2)
                        # Script JavaScript para hacer click en el botón de publicar
                        # script_publicar = (
                        #     "var element = document.evaluate("
                        #     "'/html/body/div[1]/div[8]/div[2]/div[2]/form/div[3]',"
                        #     "document,"
                        #     "null,"
                        #     "XPathResult.FIRST_ORDERED_NODE_TYPE,"
                        #     "null"
                        #     ").singleNodeValue;"
                        #     "if (element) {"
                        #     "  element.click();"
                        #     "  console.log('Clic realizado.');"
                        #     "} else {"
                        #     "  console.log('Elemento no encontrado.');"
                        #     "}"
                        # )
                        # navegador.execute_script(script_publicar)
                        navegador.find_element(By.XPATH, path_boton_guardar_publicar).click()
                        print("Se Clickeo PUBLICAR")
                        
                        # Fix: búsqueda robusta del índice (intentar float primero, luego string)
                        try:
                            indice = base_remax.loc[base_remax['ide'] == float(ide)].index[0]
                        except:
                            try:
                                indice = base_remax.loc[base_remax['ide'] == str(ide)].index[0]
                            except:
                                escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}] ERROR CRITICO: No se encuentra el IDE en la base para actualizar", 3)
                                raise Exception("No se encuentra indice para actualizar")
                        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Esperando que cargue la ventana publicado 2", 2)
                        # Actualizado por cambio en la web: validamos otro elemento que confirma la publicación
                        publicado = esperarPorObjeto(navegador, 10, By.XPATH, "/html/body/div[1]/div[11]/div[1]/div[3]/span", "Publicado", numero_usuario, ide)
                        if publicado:
                            print("Indice: ", indice)
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