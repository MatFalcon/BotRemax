import time
from pathlib import PurePath, Path
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import pandas as pd
import os
import pygetwindow as gw
import pyautogui
import re
import openpyxl
import warnings

# Desactivar todas las advertencias de Pandas
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)
options = Options()
options.add_argument("--start-maximized")

driver = ""
edge_driver_path = 'C:\\Users\\ACER\\Documents\\Bots\\pythonProject\\prueba_inicial_remax\\driver\\msedgedriver.exe'
#driver = webdriver.Edge(executable_path=edge_driver_path, options=options)



mail_actual = "matuasfalcon123@gmail.com"
contrasena_actual = "lafranja1902"


RUTA_BOT = PurePath(Path().absolute())
RUTA_DATOS = PurePath(RUTA_BOT, "datos")
RUTA_DRIVER = f"{PurePath(RUTA_BOT, "driver")}\\msedgedriver.exe"
RUTA_ARCHIVO_CSV = PurePath(RUTA_BOT,'driver','remax_propiedades.csv')


var_validaciones = {
    'set_titulo': False,
    'set_descripcion': False,
    'set_precio': False,
    'set_ciudad': False,
    'set_imagenes': False,
    'set_check': False,
}



# paths para inicio de sesion hendyla
path_boton_ingresar = "/html/body/div/header/div/div/ul/li[4]/ul/li[2]/div/a[1]"
path_mail = "/html/body/div[1]/div[3]/div/div/div/div/form/div[2]/input"
path_contrasena = "/html/body/div[1]/div[3]/div/div/div/div/form/div[3]/input"
path_boton_iniciar = "/html/body/div[1]/div[3]/div/div/div/div/form/div[4]/input[3]"

#paths para inciar a publicar
path_boton_publicar = "/html/body/div/header/div/div/ul/li[4]/ul/li[1]/a"

#paths de publicacion
path_campo_titulo = "/html/body/div[2]/section/form/div[2]/div[2]/div[3]/div[1]/input"
path_categoria_inmueble = "/html/body/div[2]/section/form/div[2]/div[2]/div[3]/div[2]/div/div/ul/li[14]/a/p/span"
path_seleccion_categoria = ["/html/body/div[2]/section/form/div[2]/div[2]/div[3]/div[2]/div[2]/div/ul/li[", "]/a"]
path_boton_continuar = "/html/body/div[2]/section/form/div[2]/div[2]/div[3]/div[2]/div[3]/div/div/div/a"

path_check_venta = "/html/body/div[2]/section/form/div[3]/div[1]/div[3]/div/div/div/label[2]/input"

path_campo_descripcion = "/html/body/div[2]/section/form/div[3]/div[1]/div[5]/textarea"
path_campo_precio = "/html/body/div[2]/section/form/div[3]/div[1]/div[7]/div/div/div/div[1]/input"
path_campo_celular = "/html/body/div[2]/section/form/div[3]/div[1]/div[5]/textarea"
path_campo_titulo = "/html/body/div[2]/section/form/div[2]/div[2]/div[3]/div[1]/input"
path_seleccion_img = "/html/body/div[2]/section/form/div[3]/div[1]/div[1]/div[1]/div/div/ul/li/div"
path_boton_realizar_publicacion = "/html/body/div[2]/section/form/div[3]/div[3]/button"
path_campo_ciudad = "/html/body/div[2]/section/form/div[3]/div[1]/div[11]/div/div/div[1]/div/input[1]"
path_error = "/html/body/div[2]/section/form/div[1]/div/strong"
CATEGORIAS = {
        "Residencia": 2,
        "Departamento": 4,
        "Casa": 2,
        "Terreno": 10,
        "Duplex": 6,
        "Edificio": 8,
        "Depósito": 5,
        "Local Comercial": 8,
        "Oficina": 8,
        "Casa de Verano": 2,
        "Chalet":2,
        "Atypical": 2,
        "Bloque de departamentos": 4,
        "Business": 8,
        "Casa de campo": 2,
        "Condominio de Lujo": 2,
        "Departamento con servicio de Hotel": 4,
        "Habitación": 4,
        "Health Clinic": 8,
        "Hotel": 4,
        "Industria": 8,
        "Nueva Construcción": 4,
        "Quinta": 2,
        "Triplex": 6
    }

def iniciar_sesion_hendyla(navegador, credenciales):

    navegador.get("https://www.hendyla.com/")
    # dar click en el boton de ingresar para que se abra el login de hendyla

    try:
        navegador.find_element(By.XPATH, path_boton_ingresar).click()
        time.sleep(1)
    except:
        print("No se encontro el boton de ingresar en el inicio de la pagina Hendyla.com")
        time.sleep(30)

    # rellenar campos

    #campo mail
    try:
        navegador.find_element(By.XPATH, path_mail).send_keys(credenciales["correo"])
    except:
        print("No se pudo rellenar el campo de mail al iniciar sesion")
        time.sleep(30)

    # campo contrasena
    try:
        navegador.find_element(By.XPATH, path_contrasena).send_keys(credenciales["contra"])
        time.sleep(1)
    except:
        print("No se pudo rellenar el campo de contrasena al iniciar sesion")
        time.sleep(30)

    # click al boton para ingresar nuesteas credendciales
    try:
        navegador.find_element(By.XPATH, path_boton_iniciar).click()
        time.sleep(3)
    except:
        print("No se pudo dar click al boton de iniciar sesion luego de ingresar las credenciales")
        time.sleep(30)

def reiniciar_publicar(navegador):
    try:
        navegador.get("https://www.hendyla.com/")
        time.sleep(1)
    except:
        time.sleep(3)
        navegador.get("https://www.hendyla.com/")
        time.sleep(1)

def inciar_a_publicar_hendyla(navegador):

    navegador.find_element(By.XPATH,path_boton_publicar).click()
    print("Boton clickeado")
    time.sleep(3)

def obtener_ide_para_publicar_clasipar():
    base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))
    ide = base_remax.loc[(base_remax['publicado_hendyla'].isna()) & (pd.notna(base_remax['ide']))]['ide'].to_list()
    print('A publicar', len(ide))
    base_remax = ""
    return ide

def elejir_categoria_formulario(tipo_propiedad,navegador):

    try:
        navegador.find_element(By.XPATH, path_categoria_inmueble).click()
        time.sleep(0.5)
    except:
        print("Funcion: elejir_categoria_formulario()")
        print("No se pudo seleccionar una categoria o tipo de propiedad")



    try:
        navegador.find_element(By.XPATH,f"{path_seleccion_categoria[0]}{CATEGORIAS[tipo_propiedad]}{path_seleccion_categoria[1]}").click()
        time.sleep(0.5)
    except:

        print("Funcion: elejir_categoria_formulario()")
        print("No se pudo seleccionar una categoria o tipo de propiedad")

    try:
        navegador.find_element(By.XPATH, path_boton_continuar).click()
        time.sleep(0.5)
    except:

        print("Funcion: elejir_categoria_formulario()")
        print("No se pudo clickear en el boton publicar")


def insertar_imagenes_hendyla(ide, navegador):
    global var_validaciones

    navegador.find_element(By.XPATH, path_seleccion_img).click()
    time.sleep(3)
    # se crea una lista con las carpetas desde C: hasta llegar a la carpetacorrespondiente al inmueble
    carpetas_hasta_datos = str(PurePath(RUTA_BOT, RUTA_DATOS, ide)).split('\\')
    # lista los nombres de las imagenes almacenadas dentro de la carpeta img del inmueble
    nombre_imgs = os.listdir(PurePath(RUTA_BOT, RUTA_DATOS, ide, 'img'))
    print(carpetas_hasta_datos)
    # Encuentra la ventana emergente por su título
    print(gw.getWindowsWithTitle("Abrir"))
    file_dialog = gw.getWindowsWithTitle("Abrir")[0]  # Cambia "Abrir" al título correcto de la ventana
    time.sleep(2)
    # Activa la ventana emergente
    file_dialog.activate()

    for car in carpetas_hasta_datos:
        # Envía la ruta del archivo
        pyautogui.write(car)  # Cambia la ruta y el nombre del archivo según tus necesidades
        pyautogui.press("enter")
        time.sleep(0.5)

    pyautogui.write("img")  # Cambia la ruta y el nombre del archivo según tus necesidades
    pyautogui.press("enter")
    lista_final_imagenes = ''
    # se genera un texto con todas las imagenes para ingresarlas de una ya que estamos ubicados en la carpeta img
    contador_imagenes = 0
    for img in nombre_imgs:
        lista_final_imagenes += f'"{img}" '
        contador_imagenes += 1
        if contador_imagenes > 8:  # clasipar solo admite 9 imagenes
            break


    pyautogui.write(lista_final_imagenes)  # Cambia la ruta y el nombre del archivo según tus necesidades
    pyautogui.press("enter")
    time.sleep(0.6)
    lista_ventanas_final = gw.getWindowsWithTitle("Abrir")

    if len(lista_ventanas_final) > 0:
        var_validaciones['set_imagenes'] = False
        print("Se encontro un error al querer cargar las imagenes, no se realizar la publicacion")
        for ventana in lista_ventanas_final:
            ventana.close()
        return

    # pyautogui.press("enter")
    var_validaciones['set_imagenes'] = True
    time.sleep(5)

def rellenar_titulo_hendyla(titulo, navegador):

    global var_validaciones
    titulo = titulo.strip().lstrip()
    try:
        navegador.find_element(By.XPATH, path_campo_titulo).send_keys(titulo)
        set_titulo = True
        var_validaciones['set_titulo'] = True
    except:
        print("Se encontro un error en la funcion rellenar_titulo_clasipar")
        var_validaciones['set_titulo'] = False

def check_venta_hendyla(navegador):
    global var_validaciones
    try:
        navegador.find_element(By.XPATH, path_check_venta).click()
        set_check = True
        var_validaciones['set_check'] = True
    except:
        print(
            "Se encontro un error al intentar seleccionar el check de venta en la  funcion check_venta_hendyla")
        var_validaciones['set_check'] = False
def filtrar_caracteres_bmp(texto):
    # Expresión regular para encontrar caracteres fuera del BMP
    bmp_regex = re.compile(r'[^\u0000-\uFFFF]')
    # Filtrar caracteres fuera del BMP y retornar el texto modificado
    return bmp_regex.sub('', texto)

def rellenar_descripcion_hendyla(descripcion, navegador):
    global set_descripcion
    global var_validaciones
    try:
        try:
            navegador.find_element(By.XPATH, path_campo_descripcion).send_keys(descripcion)
        except:
            navegador.find_element(By.XPATH, path_campo_descripcion).send_keys(filtrar_caracteres_bmp(descripcion))

        var_validaciones['set_descripcion'] = True
    except Exception as e:
        print("Se encontro un erorr en la funcion rellenar_descripcion_hendyla")
        var_validaciones['set_descripcion'] = False
        print(e)
        time.sleep(2000)

def elejir_precio_clasipar(lista_precio, navegador):

    global var_validaciones
    print(lista_precio)
    if lista_precio[1] == "USD":
        script = ("var selectElement = document.getElementById('currency');"
                  "var event = new Event('mousedown');"
                  "selectElement.dispatchEvent(event);"
                  "selectElement.options[1].selected = true;")
        navegador.execute_script(script)
        print("Se cambio el tipo de moneda")

        var_validaciones['set_precio'] = True
    try:
        navegador.find_element(By.XPATH, path_campo_precio).send_keys(lista_precio[0])
        print(lista_precio[0])
        var_validaciones['set_precio'] = True
    except:
        print("Se encotro un error al intentar establecer el precio", lista_precio[1],"\n en la funcion elejir_precio_clasipar")

        var_validaciones['set_precio'] = False

def elejir_ciudad_clasipar(ciudad, navegador):
    global var_validaciones

    if ciudad == "Asuncion":
        ciudad = "Asuncion"
    elif ciudad == "Sanber":
        ciudad = "San Bernardino"
    elif ciudad == "Fernando":
        ciudad = "Fernando de la Mora"
    elif ciudad == "Sanlo":
        ciudad = "San Lorenzo"
    elif ciudad == "Luque":
        ciudad = "Luque"

    try:
        script = "var ci = document.getElementById(\"project\");\n"
        script += f"ci.value = '{ciudad}'"
        navegador.execute_script(script)

        #navegador.find_element(By.XPATH, path_campo_ciudad).send_keys(ciudad)

        var_validaciones['set_ciudad'] = True
        time.sleep(0.5)
    except Exception as ex:
        print("No se pudo cambiar la ciudad de la publicacion en hendyla")
        print(ex)
        var_validaciones['set_ciudad'] = False

def realizar_publicacion(navegador):
    time.sleep(3)
    try:
        navegador.find_element(By.XPATH, path_boton_realizar_publicacion).click()
        time.sleep(1)

    except Exception as ex:
        #print(ex)
        print("No se pudo dar click al boton de publicar en la funcion realizar_publicacion()")

def obtener_ide_para_publicar_hendyla(numero_usuario):
    base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))
    ide = base_remax.loc[(base_remax[f'{numero_usuario}publicado_hendyla']!= "1") & (pd.notna(base_remax['ide']))]['ide'].to_list()
    print('A publicar', len(ide))
    base_remax = ""
    return ide



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
    var_validaciones['set_titulo'] = False
    var_validaciones['set_descripcion'] = False
    var_validaciones['set_precio'] = False
    var_validaciones['set_ciudad'] = False
    var_validaciones['set_imagenes'] = False
    var_validaciones['set_check'] = False


def recorrer_resultados_pendientes_a_publicar_hendyla(navegador, numero_usuario, telefono):
    ides_pendientes = obtener_ide_para_publicar_hendyla(numero_usuario)
    ides_pendientes = ides_pendientes[0:60]
    # abrir csv que contiene todos los datos
    print(PurePath(RUTA_BOT, "driver"))
    global VAR_VALIDACIONES

    contador = 1
    for ide in ides_pendientes:
        if validar_existencia_imagenes(ide):
            base_remax = pd.read_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))
            resetear_variables_validacion()


            reiniciar_publicar(navegador)
            tipo = base_remax.loc[base_remax['ide'] == ide]['tipo'].to_list()[0]
            titulo = base_remax.loc[base_remax['ide'] == ide]['titulo'].to_list()[0]
            descripcion = base_remax.loc[base_remax['ide'] == ide]['descripcion'].to_list()[0]
            ciudad = base_remax.loc[base_remax['ide'] == ide]['ciudad'].to_list()[0]
            precio = base_remax.loc[base_remax['ide'] == ide]['precio'].to_list()[0]
            precio = precio.strip().lstrip()
            tipo_moneda = precio.split(" ")[1]
            precio = int(precio.split(" ")[0].replace(",", ""))

            contador += 1
            inciar_a_publicar_hendyla(navegador)
            # inciar setear campos
            rellenar_titulo_hendyla(titulo, navegador)
            elejir_categoria_formulario(tipo, navegador)
            insertar_imagenes_hendyla(ide, navegador)
            if var_validaciones['set_imagenes']:

                check_venta_hendyla(navegador)
                rellenar_descripcion_hendyla(descripcion, navegador)
                elejir_precio_clasipar([precio, tipo_moneda], navegador)
                elejir_ciudad_clasipar(ciudad, navegador) # cambiar el 1 por una consulta a la base


                se_puede_publicar = True
                print("=" * 80)
                for key in var_validaciones:
                    print(key, '\t', var_validaciones[key])
                    if var_validaciones[key] == False:
                        se_puede_publicar = False
                print('Se puede publicar', se_puede_publicar)
                print("=" * 80)


                if se_puede_publicar:
                    realizar_publicacion(navegador)
                    try:
                        navegador.find_element(By.XPATH, path_error).text
                        print("Posible error de hendyla")

                    except:
                        print("No hay error")
                        print('insertado')

                        indice = base_remax.loc[base_remax['ide'] == ide].index[0]
                        base_remax.loc[indice, f'{numero_usuario}publicado_hendyla'] = '1'
                        try:
                            base_remax.to_excel(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.xlsx'), index=False)
                        except:
                            pass
                        base_remax.to_csv(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'), index=False)

                else:# si no se seteo bien las imagenes
                    print("No se pudo setear las imagenes por algun error, pasando a la siguiente propiedad")

def procesar_hendyla(navegador, numero_usuario, credenciales):

    iniciar_sesion_hendyla(navegador, credenciales[numero_usuario])
    recorrer_resultados_pendientes_a_publicar_hendyla(navegador, numero_usuario)



"""iniciar_sesion_hendyla(driver)

# lo que debe ir en el bucle
recorrer_resultados_pendientes_a_publicar_hendyla(driver)
time.sleep(10)
driver.close()

print("Fin")"""