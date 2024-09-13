from pathlib import PurePath, Path
import pandas as pd

# rutas relativas para el bot
RUTA_BOT = PurePath(Path().absolute())
RUTA_DATOS = PurePath(RUTA_BOT, "datos")
RUTA_DF = PurePath(RUTA_BOT, "driver", "remax_propiedades.csv")
RUTA_EXCEL = PurePath(RUTA_BOT, "driver", "remax_propiedades.xlsx")
RUTA_DRIVER = f"{PurePath(RUTA_BOT, "driver")}\\msedgedriver.exe"



url = "https://www.remax.com.py/"
# path para inicio
path_campo_ciudad = "/html/body/form/div[3]/div[3]/div[1]/div/div[3]/div/div/div/div[2]/div[2]/input"
path_boton_buscar = "/html/body/form/div[3]/div[3]/div[1]/div/div[3]/div/div/div/div[7]/button"
path_boton_siguiente = "/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[3]/div[2]/div[1]/div[3]/div[2]/div/nav/ul/li[7]/a"
path_boton_siguiente = "/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[2]/div[3]/div[2]/div/nav/ul/li[7]"

# para el bucle en el que quita los datos de cada propiedad
tipo_propiedad_excluir = ["RESERVADO", "VENDIDO"]
path_tipo_propiedad = ["/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[3]/div[2]/div[1]/div[1]/div/div[", "]/div/div[7]/span"]
path_tipo_propiedad = ["/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[2]/div[1]/div/div[", "]/div/div[7]/span"]
# paths para quitar datos por cada propiedad
path_titulo = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div[1]/h1"

path_precio = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div[3]/div/a"
path_precio2 = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div[4]/div/a"
path_direccion = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div[5]"
path_id = ["/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div[","]"]

path_atributo = ["/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[2]/div[1]/div[","]/div/div[1]/span"]
path_valor = ["/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[2]/div[1]/div[","]/div/div[2]/span"]
path_sub_atri = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/div/div[1]"
path_descripcion = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div/div"
path_descripcion2 = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[2]/div"
path_descripcion3 = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/div/div/div"
path_descripcion4 = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/div"
path_descripcion5 = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div"
path_descripcion6 = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[3]/div/div/div[1]/div[2]/div/div/div"
path_descripcion7 = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[2]/div"
path_descripcion8 = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[3]/div/div/div[1]/div[2]/div"
lista_path_descripcion = [
    path_descripcion, path_descripcion2, path_descripcion3, path_descripcion4, path_descripcion5, path_descripcion6,
    path_descripcion7, path_descripcion8
]
path_caracteristicas = ["/html/body/form/div[3]/div[5]/div[4]/div[2]/div[1]/div[1]/div/div[2]/div/div[3]/div/div[","]/span"]

path_imagen = ["/html/body/form/div[3]/div[5]/div[4]/div[1]/div/div/div/div/div[3]/div[3]/div/div[2]/div[2]/div[5]/div/div[","]/img"]
path_agente = "/html/body/form/div[3]/div[5]/div[4]/div[2]/div[2]/div[1]/div[1]/section/div/div/div/div[1]/div[2]/h4/a"

path_resultado = [f"/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[3]/div[2]/div[1]/div[1]/div/div[", "]/div/div[6]/span/a"]
path_resultado2 = [f"/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[2]/div[1]/div/div[", "]/div/div[8]/a"]
path_resultado_comun = f"/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[3]/div[2]/div[1]/div[1]/div/div[{3}]/div/div[6]/span/a"
path_tarjeta = [f"/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[3]/div[2]/div[1]/div[1]/div/div[", "]/div/div[3]/div/span"]

# variables clasipar
# inicio de sesion
clasipar_url_inicio_sesion = "https://clasipar.paraguay.com/iniciar-sesion"
clasipar_campo_correo = "/html/body/main/div/section/div[1]/div[2]/form/div[1]/input"
clasipar_campo_contrasenia = "/html/body/main/div/section/div[1]/div[2]/form/div[2]/input"
clasipar_boton_ingresar = "/html/body/main/div/section/div[1]/div[2]/form/button"

clasipar_ventana_emergente = "/html/body/div[6]/div[2]/div/div[3]/button"
clasipar_publicar_url = "https://clasipar.paraguay.com/publicar-aviso"
clasipar_check = "/html/body/main/div/section/div[2]/div[1]/article/form/span[1]/div/div/div/span[2]/div/input"
clasipar_path_precio = "/html/body/main/div/section/div[2]/div[1]/article/form/div[3]/div[2]/input"
# para publicar
clasipar_tipo_publicacion = "/html/body/main/div/section/div[2]/div/article/div[1]/div/div[2]/div/a"

clasipar_campo_titulo = "/html/body/main/div/section/div[2]/div[1]/article/form/div[1]/div/input"
clasipar_campo_descripcion = "/html/body/main/div/section/div[2]/div[1]/article/form/div[2]/div/textarea"
# variables infocasas
# inicio de sesion
info_url_inicio_sesion = "https://www.infocasas.com.py/soyinmobiliaria"
info_boton_ingresar = "/html/body/div[2]/div[6]/div/ul[2]/li[4]/a/span"
info_campo_correo = "/html/body/div[11]/div/div[2]/form/div[1]/input"
info_boton_continuar = "/html/body/div[11]/div/div[2]/form/div[1]/div[2]"
info_campo_contrasenia = "/html/body/div[11]/div/div[2]/form/div[2]/input"
info_boton_iniciar_sesion = "/html/body/div[11]/div/div[2]/form/div[2]/div[2]"

categorias = {
        "Residencia": 1,
        "Departamento": 3,
        "Casa": 1,
        "Terreno": 7,
        "Duplex": 4,
        "Edificio": 3,
        "Depósito": 6,
        "Local Comercial": 8,
        "Oficina": 8,
        "Casa de Verano": 1,
        "Chalet": 1,
        "Atypical": 1,
        "Bloque de departamentos": 3,
        "Business": 3,
        "Casa de campo": 1,
        "Condominio de Lujo": 1,
        "Departamento con servicio de Hotel": 3,
        "Habitación": 3,
        "Health Clinic": 8,
        "Hotel": 3,
        "Industria": 8,
        "Nueva Construcción": 3,
        "Quinta": 1,
        "Triplex": 4,
        "Espacio de estacionamiento": 7,
        "Sin Tipo": 1,
        "Accommodation": 1
    }


