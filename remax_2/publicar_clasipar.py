import os
import re
import time
import warnings
import pyautogui
import pandas as pd
import pygetwindow as gw
from selenium import webdriver
from pathlib import PurePath, Path
from para_log import escribir_en_log
import variables_clasipar as var
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.edge.service import Service as EdgeService

# Desactivar todas las advertencias de Pandas
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)
RUTA_BOT = PurePath(Path().absolute())
RUTA_DATOS = PurePath(RUTA_BOT, "datos")
RUTA_DRIVER = f"{PurePath(RUTA_BOT, "driver")}\\msedgedriver.exe"
RUTA_ARCHIVO_CSV = PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv')
options = Options()
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--log-level=3")

edge_driver_path = 'C:\\Users\\ACER\\Documents\\Bots\\pythonProject\\prueba_inicial_remax\\driver\\msedgedriver.exe'


edge_driver_path = 'C:\\Users\\ACER\\Documents\\Bots\\pythonProject\\prueba_inicial_remax\\driver\\msedgedriver.exe'
edge_service = EdgeService(executable_path=edge_driver_path)

var_validaciones = {
    'set_categoria': False,
    'set_titulo': False,
    'set_descripcion': False,
    'set_tipo_publicacion': False,
    'set_precio': False,
    'set_departamento': False,
    'set_imagenes': False,
    'set_check': False,
    'set_contactos': False
}


def esperarPorObjeto(navegador_abierto, tiempo, tipoObjeto, identificadorObjeto, nombre, numero_usuario, ide):
    """
        Espera que se cargue el objeto de la pagina
        :return
        bool
        Parámetros:
            navegador (webdriver): El controlador del navegador Selenium.
            tiempo (int): tiempo en segundos.
            tipoObjeto: By.
            
    """
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Esperando que cargue la ventana {nombre}", 2)
    try:
        WebDriverWait(navegador_abierto, tiempo).until(
            expected_conditions.presence_of_element_located((tipoObjeto, identificadorObjeto)))
        return True
    except:
        escribir_en_log(f"No cargo la ventana {nombre}", 2)
        return False

def iniciar_sesion_clasipar(navegador, credenciales):
    escribir_en_log("Abriendo la pagina de inicio de sesion de clasipar", 1)
    navegador.get("https://clasipar.paraguay.com/iniciar-sesion")
    esperarPorObjeto(navegador, 10, By.XPATH, var.path_correo_clasipar_sesion,
                     "campo correro", 1, 1)

    # rellenar campos mail y contraseña

    navegador.find_element(By.XPATH, var.path_correo_clasipar_sesion).send_keys(credenciales["correo"])
    escribir_en_log(f"Se setea el campo de correo [correo:{credenciales["correo"]}]", 1)

    navegador.find_element(By.XPATH, var.path_contrasena_clasipar_sesion).send_keys(credenciales["contra"])
    escribir_en_log("Se setea el campo de contraseña", 1)
    # presionar boton para iniciar sesion
    navegador.find_element(By.XPATH, var.path_boton_ingresar).click()
    escribir_en_log("Se clickea el boton de iniciar sesion", 1)
    time.sleep(2)


#iniciar_sesion()

def iniciar_a_publicar(navegador, numero_usuario):
    
    escribir_en_log(f"[usuario:{numero_usuario}]Se abre la pagina publicar aviso", 1)
    navegador.get("https://clasipar.paraguay.com/publicar-aviso")
    esperarPorObjeto(navegador, 10, By.XPATH, var.path_ventana_emergente,
                     "Ventana Emergente", 1, 1)
    # saltar ventana emergente
    try:
        escribir_en_log(f"[usuario:{numero_usuario}]Se salta la ventana emergente", 1)
        navegador.find_element(By.XPATH, var.path_ventana_emergente).click()
    except:
        escribir_en_log(f"[usuario:{numero_usuario}]No se encontro la ventana emergente se reinicia el proceso", 3)
        return True

    # elejir la categoria correspondiente
    try:
        escribir_en_log(f"[usuario:{numero_usuario}]Se selecciona la categoria inmuble para la publicacion", 1)
        navegador.find_element(By.XPATH, var.path_tipo_publicacion).click()
    except:
        escribir_en_log(f"[usuario:{numero_usuario}]No se pudo elejir la categoria inmueble para la publicacion", 3)
        escribir_en_log(f"[usuario:{numero_usuario}]Se reinicia el proceso", 2)
        return True


def obtener_ide_para_publicar_clasipar(numero_usuario):
    base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))
    columna = f'{numero_usuario}publicado_clasipar'

    ide = base_remax.loc[(base_remax[columna].isna()) & (pd.notna(base_remax['ide']))]['ide'].to_list()

    base_remax = ""
    return ide


def elejir_categoria_formulario(tipo_propiedad, navegador, numero_usuario):
    global set_categoria
    global var_validaciones

    try:
        try:
            navegador.find_element(By.XPATH,
                            f"/html/body/main/div/section/div[2]/div/article/div/div[2]/div/div/select/option[{var.categorias[tipo_propiedad]}]").click()
        except KeyError:
            navegador.find_element(By.XPATH,
                                   f"/html/body/main/div/section/div[2]/div/article/div/div[2]/div/div/select/option[1]").click()
        escribir_en_log(f"[usuario:{numero_usuario}]Se selecciona la categoria {tipo_propiedad}", 1)
        set_categoria = True
        var_validaciones['set_categoria'] = True

    except Exception as ex:
        var_validaciones['set_categoria'] = False
        escribir_en_log(f"[usuario:{numero_usuario}]No se pudo seleccionar la categotria", 3)



    # click en el boton siguiente que aparece luego de elejir la opcion de tipo de inmueble
    time.sleep(1)
    path_seleccio_siguiente = "/html/body/main/div/section/div[2]/div/article/div/div[2]/div/div[2]/button"
    esperarPorObjeto(navegador, 10, By.XPATH, path_seleccio_siguiente, "boton siguiente", 1, 1)
    try:
        navegador.find_element(By.XPATH, path_seleccio_siguiente).click()
        escribir_en_log(f"[usuario:{numero_usuario}]Continuar con la publicaciones", 1)
    except:
        escribir_en_log(f"No se pudo clickear el boton siguiente luego de seleccionar la categoria", 3)



#elejir_categoria_formulario("Casa")

ruta_propiedad_prueba = "C:\\Users\\HP\\Documents\\prueba_inicial_remax\\prueba_inicial_remax\\datos\\114006028-2"
lineas_clave = ["TITULO\n", "TIPO\n", "PRECIO\n", "DESCRIPCION\n", "LINK\n"]

# venta o alquiler
def seleccionar_tipo_de_publicacion_clasipar(navegador):
    global set_tipo_publicacion
    global VAR_VALIDACIONES
    try:
        #navegador.find_element(By.XPATH, path_check_venta_alquiler).click()
        navegador.find_element(By.XPATH, var.path_check_venta_alquiler).click()
        set_tipo_publicacion = True
        var_validaciones['set_tipo_publicacion'] = True

    except:
        print("Se encontro un error en la funcion de seleccionar_tipo_de_publicacion_clasipar ")
        var_validaciones['set_tipo_publicacion'] = False




def rellenar_titulo_clasipar(titulo,navegador, numero_usuario):
    global set_titulo
    global VAR_VALIDACIONES
    titulo = titulo.strip().lstrip()
    script = f""" 
    var campo = document.getElementById('ad_title');
    campo.value = '{titulo}';
    """
    escribir_en_log(f"[usuario:{numero_usuario}][titulo:{titulo}]", 1)
    try:
        navegador.execute_script(script)
        #navegador.find_element(By.XPATH,path_campo_titulo).send_keys(titulo)
        escribir_en_log(f"[usuario:{numero_usuario}]Se seteo el titulo", 1)
        set_titulo = True
        var_validaciones['set_titulo'] = True
    except Exception as ex:
        escribir_en_log(f"No se pudo setear el titulo", 3)
        print(ex)
        
        var_validaciones['set_titulo'] = False

    
    
    
def filtrar_caracteres_bmp(texto):
    # Expresión regular para encontrar caracteres fuera del BMP
    bmp_regex = re.compile(r'[^\u0000-\uFFFF]')
    # Filtrar caracteres fuera del BMP y retornar el texto modificado
    return bmp_regex.sub('', texto)

def rellenar_descripcion_clasipar(descripcion,navegador, numero_usuario):
    global set_descripcion
    global VAR_VALIDACIONES
    time.sleep(3)
    path_campo_descripcion = "/html/body/main/div/section/div[2]/div[1]/article/form/div[2]/div/textarea"
    try:
        descripcion_filtrada = filtrar_caracteres_bmp(descripcion)
        navegador.find_element(By.XPATH, path_campo_descripcion).send_keys(descripcion_filtrada)
        escribir_en_log(f"[usuario:{numero_usuario}]Se seteo la descripcion", 1)
        set_descripcion = True
        var_validaciones['set_descripcion'] = True

    except Exception as e:
        print("Se encontro un error en la funcion rellenar_descripcion_clasipar")
        var_validaciones['set_descripcion'] = False
        escribir_en_log(f"[usuario:{numero_usuario}]No se pudo setear la descripcion", 3)

    time.sleep(2)

def elejir_precio_clasipar(lista_precio, navegador, numero_usuario):
    global set_precio
    global VAR_VALIDACIONES

    if lista_precio[1] == "USD":

        script = ("var selectElement = document.getElementById('currency');"
                  "var event = new Event('mousedown');"
                  "selectElement.dispatchEvent(event);"
                  "selectElement.options[2].selected = true;")
        try:
            navegador.execute_script(script)
        except:
            print("No se pudo setear el precio con el script")
            var_validaciones['set_precio'] = False
            return
        escribir_en_log(f"[usuario:{numero_usuario}]Se cambio el tipo de moneda a USD", 1)
        set_precio = True
        var_validaciones['set_precio'] = True

    try:
        # Intentar convertir el precio a flotante y luego a entero
        precio_final = float(lista_precio[0])
        precio_final = int(lista_precio[0])
    except ValueError:

        precio_final = 0  # o algún valor predeterminado o lógica de manejo

    try:
        navegador.find_element(By.XPATH, var.path_campo_precio).send_keys(precio_final)
        set_precio = True
        var_validaciones['set_precio'] = True
    except:
        print("Se encotro un error al intentar establecer el precio", lista_precio[1],"\n en la funcion elejir_precio_clasipar")
        set_precio = False
        var_validaciones['set_precio'] = False


def seleccionar_departamento(departamento, navegador, numero_usuario):
    global set_departamento
    global VAR_VALIDACIONES
    ciudades_central = ["Fernando", "Sanlo", "Luque", "Lamba", "VillaElisa", "Ñemby", "Capiata"]
    if departamento == "Sanber" or departamento == "Aregua" or departamento == "Altos":
        script_asu = (
            "var selectElement = document.evaluate(\"/html/body/main/div/section/div[2]/div[1]/article/form/div[7]/div[1]/div/select\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
            "var event = new Event('mousedown');"
            "selectElement.dispatchEvent(event);"
            "selectElement.options[11].selected = true;")
        set_departamento = True
        var_validaciones['set_departamento'] = True
        try:
            navegador.execute_script(script_asu)
            escribir_en_log(f"[usuario:{numero_usuario}]Se seteo el departamento [departamento:{departamento}]", 1)
        except:
            escribir_en_log(f"[usuario:{numero_usuario}]No se pudo setear el departamento [departamento:{departamento}]", 3)
    elif departamento == "Asuncion":
        script_asu = (
            "var selectElement = document.evaluate(\"/html/body/main/div/section/div[2]/div[1]/article/form/div[7]/div[1]/div/select\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
            "var event = new Event('mousedown');"
            "selectElement.dispatchEvent(event);"
            "selectElement.options[4].selected = true;")
        set_departamento = True
        var_validaciones['set_departamento'] = True

        try:
            navegador.execute_script(script_asu)
            escribir_en_log(f"[usuario:{numero_usuario}]Se seteo el departamento [departamento:{departamento}]", 1)
        except:
            escribir_en_log(f"[usuario:{numero_usuario}]No se pudo setear el departamento [departamento:{departamento}]", 3)

        # para departamento central
    elif departamento in ciudades_central:
        script_asu = (
            "var selectElement = document.evaluate(\"/html/body/main/div/section/div[2]/div[1]/article/form/div[7]/div[1]/div/select\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
            "var event = new Event('mousedown');"
            "selectElement.dispatchEvent(event);"
            "selectElement.options[9].selected = true;")
        set_departamento = True
        var_validaciones['set_departamento'] = True
        try:
            navegador.execute_script(script_asu)
            escribir_en_log(f"[usuario:{numero_usuario}]Se seteo el departamento [departamento:{departamento}]", 1)
        except:
            escribir_en_log(
                f"[usuario:{numero_usuario}]No se pudo setear el departamento [departamento:{departamento}]", 3)
            
    elif departamento == "Presidente":
        script_asu = (
            "var selectElement = document.evaluate(\"/html/body/main/div/section/div[2]/div[1]/article/form/div[7]/div[1]/div/select\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
            "var event = new Event('mousedown');"
            "selectElement.dispatchEvent(event);"
            "selectElement.options[18].selected = true;")
        set_departamento = True
        var_validaciones['set_departamento'] = True

        try:
            navegador.execute_script(script_asu)
            escribir_en_log(f"[usuario:{numero_usuario}]Se seteo el departamento [departamento:{departamento}]", 1)
        except:
            escribir_en_log(f"[usuario:{numero_usuario}]No se pudo setear el departamento [departamento:{departamento}]", 3)
     

def insertar_imagen_clasipar(ide, navegador, numero_usuario, telefono):
    escribir_en_log(f"[usuario:{numero_usuario}]Comenzo la funcion insertar imagenes", 1)
    global VAR_VALIDACIONES
    script = ("var selectElement = document.evaluate(\"/html/body/main/div/section/div[2]/div[1]/article/form/div[6]/div[1]/div[1]/span/label\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
              "var event = new Event('mousedown');"  
              "selectElement.dispatchEvent(event);"
              "selectElement.click();")
    # se crea una lista con las carpetas desde C: hasta llegar a la carpetacorrespondiente al inmueble
    carpetas_hasta_datos = str(PurePath(RUTA_BOT, RUTA_DATOS, ide)).split('\\')
    carpetas_hasta_datos = ["\\".join(carpetas_hasta_datos[0:len(carpetas_hasta_datos)-2])]+carpetas_hasta_datos[len(carpetas_hasta_datos)-2:len(carpetas_hasta_datos)]
    
    escribir_en_log(f"[usuario:{numero_usuario}]Carpeta lista: {carpetas_hasta_datos}", 1)
    
    # lista los nombres de las imagenes almacenadas dentro de la carpeta img del inmueble
    nombre_imgs = os.listdir(PurePath(RUTA_BOT, RUTA_DATOS, ide, 'img'))
    escribir_en_log(f"[usuario:{numero_usuario}]Se ejecuta el js para abrir las imagenes", 1)
    try:
        # clickea en el boton para agregar imagenes y que se abra la ventana de archivos para seleccionarlo
        navegador.execute_script(script)
        escribir_en_log(f"[usuario:{numero_usuario}]Se ejecuto con exito", 1)
    except:
        escribir_en_log(f"[usuario:{numero_usuario}]No se pudo ejecutar el script", 3)
        print("No se pudo ejecutar el script para cargar las imagenes")
        print("Reiniciando_proceso")
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo abrir la ventana para cargar las imagenes", 2)
        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se va a reiniciar el proceso", 2)

        resetear_variables_validacion()
        iniciar_a_publicar(navegador, numero_usuario)
        base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))
        # se consulta los datos de la propiedad en el csv
        tipo = base_remax.loc[base_remax['ide'] == ide]['tipo'].to_list()[0]
        titulo = base_remax.loc[base_remax['ide'] == ide]['titulo'].to_list()[0]
        descripcion = base_remax.loc[base_remax['ide'] == ide]['descripcion'].to_list()[0]
        link = base_remax.loc[base_remax['ide'] == ide]['link'].to_list()[0]
        ciudad = base_remax.loc[base_remax['ide'] == ide]['ciudad'].to_list()[0]

        precio = base_remax.loc[base_remax['ide'] == ide]['precio'].to_list()[0]
        precio = precio.strip().lstrip()
        tipo_moneda = precio.split(" ")[1]
        precio = int(float(precio.split(" ")[0].replace(",", "")))  # inicialmente estaba convertido a float

        # en la pagina inicial se elije la categoria inmueble
        elejir_categoria_formulario(tipo, navegador, numero_usuario)
        # se setean los campos
        rellenar_titulo_clasipar(titulo, navegador, numero_usuario)
        rellenar_descripcion_clasipar(descripcion, navegador, numero_usuario)
        seleccionar_tipo_de_publicacion_clasipar(navegador)
        elejir_precio_clasipar([precio, tipo_moneda], navegador, numero_usuario)
        seleccionar_departamento(ciudad, navegador, numero_usuario)
        time.sleep(3)
        try:
            # clickea en el boton para agregar imagenes y que se abra la ventana de archivos para seleccionarlo
            navegador.execute_script(script)
            escribir_en_log(f"[usuario:{numero_usuario}]Se ejecuto con exito", 1)
        except:
            var_validaciones['set_imagenes'] = False
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear las imagenes", 3)
            return
        check_particular_inmobiliaria_clasipar(navegador)
        setear_contactos_clasipar(navegador, telefono, numero_usuario)


    time.sleep(2)# podemos dismunuir el valor dependiendo del equipo, actualmente es 5s
    # Encuentra la ventana emergente por su título

    escribir_en_log(f"[usuario:{numero_usuario}]Se ejecuta la funcion para obtener las ventanas abiertas", 1)
    try:
        file_dialog = gw.getWindowsWithTitle("Abrir")[0]  # Cambia "Abrir" al título correcto de la ventana
        # Activa la ventana emergente
        escribir_en_log(f"[usuario:{numero_usuario}][ventana:{file_dialog}]", 1)
        file_dialog.activate()

        escribir_en_log(f"[usuario:{numero_usuario}]Se ingresa la ruta hasta la carpeta", 1)
        time.sleep(2)
    except:
        time.sleep(3)
        try:
            file_dialog = gw.getWindowsWithTitle("Abrir")[0]  # Cambia "Abrir" al título correcto de la ventana
            # Activa la ventana emergente
            escribir_en_log(f"[usuario:{numero_usuario}][ventana:{file_dialog}]", 1)
            file_dialog.activate()

            escribir_en_log(f"[usuario:{numero_usuario}]Se ingresa la ruta hasta la carpeta", 1)
        except:
            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo setear las imagenes", 3)
            print("No se pudo insertar las imagenes luego de varios intentos")
            var_validaciones['set_imagenes'] = False
            return
        pass
    time.sleep(1)
    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Comienza a escribirse la direccion de la carpeta", 1)
    for car in carpetas_hasta_datos:
        # Envía la ruta del archivo
        pyautogui.write(car)  # Cambia la ruta y el nombre del archivo según tus necesidades
        pyautogui.press("enter")
        if car == "datos":
            time.sleep(2)
        time.sleep(0.5)

    pyautogui.write("img")  # Cambia la ruta y el nombre del archivo según tus necesidades
    pyautogui.press("enter")
    lista_final_imagenes = ''

    # se genera un texto con todas las imagenes para ingresarlas de una ya que estamos ubicados en la carpeta img
    contador_imagenes = 0
    escribir_en_log(f"[usuario:{numero_usuario}]Se ingresan las imagenes encontradas", 1)
    for img in nombre_imgs:
        lista_final_imagenes += f'"{img}" '
        contador_imagenes += 1
        if contador_imagenes > 8:# clasipar solo admite 9 imagenes
            break

    pyautogui.write(lista_final_imagenes)  # Cambia la ruta y el nombre del archivo según tus necesidades
    pyautogui.press("enter")
    escribir_en_log(f"[usuario:{numero_usuario}]Se ingresan las imagenes",  1)

    time.sleep(1)

    lista_ventanas_final = gw.getWindowsWithTitle("Abrir")
    escribir_en_log(f"[usuario:{numero_usuario}]Ventanas (Abrir) luego de ingresar {lista_ventanas_final}", 1)

    if len(lista_ventanas_final) > 0:
        escribir_en_log(f"[usuario:{numero_usuario}]No deberia haber ninguna ventana abierta", 3)
        escribir_en_log(f"[usuario:{numero_usuario}]Se intenta cerrar todas las ventanas (Abrir) ", 3)
        var_validaciones['set_imagenes'] = False
        print("Se encontro un error al querer cargar las imagenes, no se realizar la publicacion")
        for ventana in lista_ventanas_final:
            escribir_en_log(f"[usuario:{numero_usuario}]Se cierra la ventana {ventana}", 3)
            ventana.close()
        return


    try:
        file_dialog.close()
    except:
        pass
    #pyautogui.press("enter")
    set_imagenes = True
    var_validaciones['set_imagenes'] = True
    escribir_en_log(f"[usuario:{numero_usuario}]Fin de la funcion insertar imagenes", 1)


def check_particular_inmobiliaria_clasipar(navegador):
    global set_check
    global VAR_VALIDACIONES
    try:
        navegador.find_element(By.XPATH, var.path_check_particular_inmobiliaria).click()
        set_check = True
        var_validaciones['set_check'] = True
    except:
        #print("Se encontro un error al intentar seleccionar el check de inmobiliaria en la  funcion check_particular_inmobiliaria_clasipar")
        var_validaciones['set_check'] = False

def setear_contactos_clasipar(navegador, telefono, numero_usuario):
    global set_contactos
    global VAR_VALIDACIONES
    escribir_en_log(f"[usuario:{numero_usuario}]Inicio funcion setear contactos", 1)
    try:
        escribir_en_log(f"[usuario:{numero_usuario}]Se setean los contactos",  1)
        escribir_en_log(f"[usuario:{numero_usuario}][telefono:{telefono}]", 1)
        navegador.find_element(By.XPATH, var.path_celular_clasipar).send_keys(telefono)
        navegador.find_element(By.XPATH, var.path_celular_secundario_clasipar).send_keys(telefono)
        navegador.find_element(By.XPATH, var.path_telefono_clasipar).send_keys(telefono)
        set_contactos = True
        var_validaciones['set_contactos'] = True
    except:
        print("Se encontro un error al intentar setear los numeros de contactos en la  funcion setear_contactos_clasipar")
        escribir_en_log(f"[usuario:{numero_usuario}]No se pudo setear los contactos por algun error", 3)
        var_validaciones['set_contactos'] = False
        pass

def validar_existencia_imagenes(ide):
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
            return True

        return False
    else:
        return False

def resetear_variables_validacion():

    """
        resetea el estado de las variables de validacion,
        se debe realizar al comenzar a publicar
    """
    global VAR_VALIDACIONES
    # variables de validacion para corroborar que se hallan seteado todos los campos correctamente
    var_validaciones['set_categoria'] = False
    var_validaciones['set_titulo'] = False
    var_validaciones['set_descripcion'] = False
    var_validaciones['set_tipo_publicacion'] = False
    var_validaciones['set_precio'] = False
    var_validaciones['set_departamento'] = False
    var_validaciones['set_imagenes'] = False
    var_validaciones['set_check'] = False
    var_validaciones['set_contactos'] = False
def convertir_precio(precio):
    precio_inicial = 0
    try:
        precio_inicial = float(precio)
    except ValueError:
        escribir_en_log(f"Error con el valor del precio {precio}", 2)
    
    try:
        precio_inicial = int(precio_inicial)
    except ValueError:
        escribir_en_log(f"Error al querer convertir el precio a entero {precio_inicial}", 1)

    return precio_inicial

def recorrer_resultados_pendientes_a_publicar_clasipar(navegador, numero_usuario, telefono, cantidad_a_publicar):
    # variable para validaciones
    # global para que mis funciones puedad modificarlas sin problemas
    global VAR_VALIDACIONES
    escribir_en_log(f"[usuario:{numero_usuario}]Se ejecuta la funcion obtener_ide_para_publicar_clasipar", 1)
    # obtiene ides de las propiedades que faltan publicar para este usuario
    ides_pendientes = obtener_ide_para_publicar_clasipar(numero_usuario)

    escribir_en_log(f"[usuario:{numero_usuario}][ides_pendientes:{len(ides_pendientes)}]", 1)
    # abrir csv que contiene todos los datos
    base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))

    contador = 1
    # se saca solo la cantidad establecidas de ide


    escribir_en_log(f"[usuario:{numero_usuario}][ides_pendientes:{len(ides_pendientes)}]", 1)
    contador_publicados = 0

    # se comienza a recorrer los ides
    for ide in ides_pendientes:
        escribir_en_log(f"[usuario:{numero_usuario}]Comienza a publicarse [ide:{ide}]", 1)
        escribir_en_log(f"[usuario:{numero_usuario}]Se valida que tenga imagenes en su carpeta", 1)
        # se valida que se hallan descargado las imagenes correspondientes a la propiedad con este ide
        if validar_existencia_imagenes(ide):
            escribir_en_log(f"[usuario:{numero_usuario}][validar_existencia_imagenes:True]", 1)
            # setear validaciones en false
            resetear_variables_validacion()

            proceso = iniciar_a_publicar(navegador, numero_usuario)# vuelve o carga la pagina para comenzar a publicar
            if proceso:
                return True

            # se consulta los datos de la propiedad en el csv
            tipo = base_remax.loc[base_remax['ide'] == ide]['tipo'].to_list()[0]
            titulo = base_remax.loc[base_remax['ide'] == ide]['titulo'].to_list()[0]
            descripcion = base_remax.loc[base_remax['ide'] == ide]['descripcion'].to_list()[0]

            ciudad = base_remax.loc[base_remax['ide'] == ide]['ciudad'].to_list()[0]
            precio = base_remax.loc[base_remax['ide'] == ide]['precio'].to_list()[0]
            precio = precio.strip().lstrip()
            tipo_moneda = precio.split(" ")[1]
            # inicialmente estaba convertido a float
            precio = precio.split(" ")[0].replace(",", "")
            precio = convertir_precio(precio)
            # en la pagina inicial se elije la categoria inmueble
            elejir_categoria_formulario(tipo, navegador, numero_usuario)
            # se setean los campos
            rellenar_titulo_clasipar(titulo, navegador, numero_usuario)
            rellenar_descripcion_clasipar(descripcion, navegador, numero_usuario)
            seleccionar_tipo_de_publicacion_clasipar(navegador)
            elejir_precio_clasipar([precio, tipo_moneda], navegador, numero_usuario)
            seleccionar_departamento(ciudad, navegador, numero_usuario)
            time.sleep(2)
            insertar_imagen_clasipar(ide, navegador, numero_usuario, telefono)
            check_particular_inmobiliaria_clasipar(navegador)
            setear_contactos_clasipar(navegador, telefono, numero_usuario)

            res = ""
            # se valida que se pueda publicar
            se_puede_publicar = True
            for key in var_validaciones:
                res += f"{key}:\t{var_validaciones[key]}\t"
                # si alguna de las variables es false no se podra publicar
                if var_validaciones[key] == False:
                    se_puede_publicar = False
            escribir_en_log(f"[usuario:{numero_usuario}][se_puede_publicar:{se_puede_publicar}][ide:{ide}]", 1)



            if not se_puede_publicar:
                escribir_en_log(f"[usuario:{numero_usuario}]Validaciones: {res}", 3)

            time.sleep(1)


            if se_puede_publicar:
                escribir_en_log(f"[usuario:{numero_usuario}]Se intenta clickear el boton para publicar",2)
                try:
                    # click en publicar
                    navegador.find_element(By.XPATH, var.path_boton_realizar_publicacion).click()

                    escribir_en_log(f"[usuario:{numero_usuario}]Aparentemente se clickeo con exito", 1)
                    time.sleep(1)
                    indice = base_remax.loc[base_remax['ide'] == ide].index[0]
                    encontro = esperarPorObjeto(navegador, 15, By.XPATH, var.path_anuncio_publicado, "Se publico", numero_usuario, ide)
                    
                    if encontro:
                        base_remax.loc[indice, f'{numero_usuario}publicado_clasipar'] = '1'
                        base_remax.to_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'), index=False)
                        contador_publicados += 1
                        escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Publicado!", 1)
                        escribir_en_log(f"[usuario:{numero_usuario}][contador_publicados:{contador_publicados}][ides_inicial:{len(ides_pendientes)}]", 1)
                    
                        try:
                            base_remax.to_excel(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.xlsx'), index=False)
                            escribir_en_log(f"[usuario:{numero_usuario}]Se genera excel", 1)
                        except:
                            pass

                        if contador_publicados > cantidad_a_publicar:
                            escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]Se Alcanzo la cantidad  a publicar cantidad:{cantidad_a_publicar}", 3)
                            break
                        
                        
                except Exception as ex:
                    escribir_en_log(f"[usuario:{numero_usuario}][ide:{ide}]No se pudo clickear el boton para publicar", 3)
                    

            else:
                iniciar_a_publicar(navegador, numero_usuario)
            contador += 1

    # para cortar el bucle en ejecucion bot y que no siga intentando
    return False


def procesar_clasipar(navegador, numero_usuario, credenciales, cantidad_a_publicar):
    escribir_en_log(f"[usuario:{numero_usuario}]Inicio el proceso para publicar en clasipar ", 1)
    escribir_en_log(f"[usuario:{numero_usuario}]Se ejecuta la funcion iniciar sesion", 1)
    iniciar_sesion_clasipar(navegador, credenciales[numero_usuario])
    escribir_en_log(f"[usuario:{numero_usuario}] Se inicio sesion", 1)
    escribir_en_log(
        f"[usuario:{numero_usuario}]Se ejecuta la funcion recorrer_resultados_pendientes_a_publicar_clasipar",
        1)

    proceso = recorrer_resultados_pendientes_a_publicar_clasipar(navegador, numero_usuario, str(credenciales[numero_usuario]["telefono"]).strip().lstrip() , cantidad_a_publicar)
    while proceso:
        navegador.close()
        navegador = webdriver.Edge(service=edge_service, options=options)
        iniciar_sesion_clasipar(navegador, credenciales[numero_usuario])
        proceso = recorrer_resultados_pendientes_a_publicar_clasipar(navegador, numero_usuario, credenciales[numero_usuario]["telefono"], cantidad_a_publicar)

