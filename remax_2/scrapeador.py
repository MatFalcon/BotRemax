import os
import ssl
import time
import openpyxl
import warnings
import variables
import pandas as pd
import urllib.request
from datetime import datetime
from selenium import webdriver
from pathlib import PurePath, Path
from para_log import escribir_en_log
from navegador_scrap import Navegador
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

# Desactivar todas las advertencias de Pandas
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

# configuraciones para ignorar los certificados ssl para descargar las imagenes
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def esperarPorObjeto(navegador_abierto, tiempo, tipoObjeto, identificadorObjeto, nombre):
    """
        Espera que se cargue el objeto de la pagina
        :return
        bool
    """
    escribir_en_log(f"Esperando {tiempo}seg por: {nombre}", 1)
    try:
        WebDriverWait(navegador_abierto, tiempo).until(
            expected_conditions.presence_of_element_located((tipoObjeto, identificadorObjeto)))
        return True
    except Exception as ex:
        escribir_en_log(f"No se cargo {nombre}", 2)
        return False
class BaseRemax:

    def __init__(self):
        tabla = ""

    def abrir_base(self):
        self.tabla = pd.read_csv(variables.RUTA_DF)

    def validacion_link(self, link):
        """
        Validad la si ya existe un registro con el mismo link

        Parameters
            ----------
        link : str
            link que se va a validar

        Returns
        -------
        bool
        """
        validacion = len(self.tabla.loc[self.tabla['link'] == link]) > 0
        escribir_en_log(f"Existe link: {validacion}", 1)
        return validacion

    def guardar_base(self):
        """sobreescribe la base y actualiza"""

        escribir_en_log(f"Se actualizo la base", 1)
        self.tabla.to_csv(variables.RUTA_DF, index=False)
        try:
            self.tabla.to_excel(variables.RUTA_EXCEL, index=False)
        except:
            pass
        self.abrir_base()

    def obtener_columnas(self):

        return self.tabla.columns

    def crear_nueva_fila(self, tipo_propiedad, link, ciudad):

        modelo_fila = [{'titulo': '', 'tipo': tipo_propiedad, 'precio': '',
                        'descripcion': '', 'link': link, 'ide': '',
                        'ciudad': ciudad, 'publicado_facebook': '',
                        'fecha_inserion': datetime.now().strftime("%d/%m/%Y"),
                        'publicado_clasipar': '', 'publicado_info': '',
                        'publicado_hendyla': '', 'intentos':1}]
        modelo_DF = pd.DataFrame(modelo_fila)
        self.tabla = pd.concat([self.tabla, modelo_DF], ignore_index=True)
        escribir_en_log(f"Nuevo registro para el link: {link}", 1)
        self.guardar_base()

    def obtener_links(self):

        return self.tabla.loc[(self.tabla['titulo'].isna()) | (self.tabla['descripcion'] == "")]['link']

    def obtener_fila(self, ide):
        return self.tabla.loc[self.tabla['ide'] == ide]

    def actualizar_columna(self, link, columna, dato):
        """actualiza una fila segun el link"""
        self.tabla.loc[self.tabla['link'] == link, columna] = dato
        self.guardar_base()

class RemaxScrap:

    def __init__(self, ciudad, propiedades_agregar, propiedades_scrapear):
        self.url_pagina = "https://www.remax.com.py/"
        self.propiedades_agregar = propiedades_agregar
        self.navegador = None
        self.ciudad = ciudad
        self.ciudad_campo = {
            "Asuncion": "Asuncion",
            "Sanber": "San Ber",
            "Fernando": "Fer",
            "Sanlo": "San Lo",
            "Luque": "Luque",
            "Lamba": "Lamba",
            "Altos": "Altos",
            "Aregua": "Aregua",
            "VillaElisa": "Villa Eli",
            "Presidente": "Presidente",
            "Ñemby": "Ñemby",
            "Capiata": "Capiata"
        }
        self.hay_resultados = True
        self.resultados_esperados_por_pag = 26
        self.base = None
        self.links_extraidos = 0
        self.resultado_comun = ""
        self.propiedades_scrapear = propiedades_scrapear
        self.link_descargando = ""
        self.ide_descargando = "Sin Ide"
        self.link_intentos = {}
    def abrir_base(self):
        """abre la base para validaciones"""
        base = BaseRemax()
        base.abrir_base()
        self.base = base

    def instanciar_navegador(self):
        """
            Crea o abre un navegador para nuestro objeto
        """
        self.navegador = Navegador()

    def abrir_navegador(self):
        """
            Abre la pagina de remax
        """
        escribir_en_log(f"Se abre la pagina de remax", 1)
        self.navegador.abrir_url(self.url_pagina)

    def buscar_ciudad(self):
        """
            Rellenar el campo de ciudad, luego realiza la busqueda
        """
        if self.propiedades_agregar > 0:
            if self.navegador.rellenar_elemento(variables.path_campo_ciudad, self.ciudad_campo[self.ciudad]):
                time.sleep(3)
                escribir_en_log(f"Se realizar la busqueda de las propiedades de la ciudad {self.ciudad}", 1)
                self.navegador.click_elemento(variables.path_boton_buscar)

                time.sleep(10)
                # espera que cargue  algun elemento de la pagina, en este caso el boton para pasar a los siguientes resultados
                self.navegador.esperarPorObjeto(self.navegador, 3, variables.path_boton_siguiente, "boton siguiente")
                elemento_boton = self.navegador.obtener_elemento(By.XPATH, variables.path_boton_siguiente)
                if elemento_boton is None:
                    variables.path_boton_siguiente = "/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[2]/div/div[3]/div[2]/div/nav/ul/li[7]/a"


    def extraer_links_ventana_actual(self):
        """Extrae los links de los resultados disponibles en la vista actual"""

        for indice in range(1, self.resultados_esperados_por_pag):
            escribir_en_log(f"Se quita datos del resultado: {indice}", 1)
            # inicializacion de los paths de los elementos que vamos a extraer
            path_resultado = f"{variables.path_resultado[0]}{indice}{variables.path_resultado[1]}"
            path_resultado2 = f"{variables.path_resultado2[0]}{indice}{variables.path_resultado2[1]}"
            path_tarjeta = f"{variables.path_tarjeta[0]}{indice}{variables.path_tarjeta[1]}"
            path_tipo_propiedad = f"{variables.path_tipo_propiedad[0]}{indice}{variables.path_tipo_propiedad[1]}"
            path_tipo_propiedad2 = f"{variables.path_tipo_propiedad2[0]}{indice}{variables.path_tipo_propiedad2[1]}"
            path_tipo_propiedad3 = f"{variables.path_tipo_propiedad3[0]}{indice}{variables.path_tipo_propiedad3[1]}"
            # estado y tipo de propiedad
            try:
                estado_propiedad = self.navegador.obtener_elemento(By.XPATH, path_tarjeta).text
            except:
                estado_propiedad = "Sin Estado"
            try:
                tipo_propiedad = self.navegador.obtener_elemento(By.XPATH, path_tipo_propiedad).text
            except:
                tipo_propiedad = "Sin Tipo"

            if tipo_propiedad == "Sin Tipo":
                try:
                    tipo_propiedad = self.navegador.obtener_elemento(By.XPATH, path_tipo_propiedad2).text
                except:
                    try:
                        tipo_propiedad = self.navegador.obtener_elemento(By.XPATH, path_tipo_propiedad3).text
                    except:
                        tipo_propiedad = "Sin Tipo"


            escribir_en_log(f"[Estado:{estado_propiedad}][Tipo:{tipo_propiedad}]", 1)
            # validar que sean propiedades disponibles
            if estado_propiedad not in variables.tipo_propiedad_excluir:
                # se obtiene el link
                elemento_link = self.navegador.obtener_elemento(By.XPATH, path_resultado)
                if elemento_link is None:
                    variables.path_resultado = variables.path_resultado2
                    elemento_link = self.navegador.obtener_elemento(By.XPATH, path_resultado2)

                link_propiedad = self.navegador.obtener_atributo_elemento(elemento_link, "href")
                if link_propiedad is None:
                    variables.path_resultado = ["/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[2]/div/div[1]/div/div[", "]/div[2]/div/div[1]/div/div[3]/a"]
                escribir_en_log(f"[link:{link_propiedad}]", 1)
                # se valida que no exista en la base para no duplicar el scrapeo
                if link_propiedad != None:
                    if link_propiedad not in self.link_intentos.keys():
                        self.link_intentos[link_propiedad] = 1
                    else:
                        self.link_intentos[link_propiedad] += 1
                    if self.link_intentos[link_propiedad] > 6:
                        self.hay_resultados = False
                        escribir_en_log(f"Se alcanzo el final de los resultados disponibles", 2)

                    if not self.base.validacion_link(link_propiedad):
                        if self.propiedades_agregar >= self.links_extraidos:
                            self.base.crear_nueva_fila(tipo_propiedad, link_propiedad, self.ciudad)

                            self.links_extraidos += 1
                            escribir_en_log(f"[links_extraidos:{self.links_extraidos}]", 1)

    def recorrer_ventanas(self):
        if self.propiedades_agregar > 0:
            while self.hay_resultados:
                recorrido = 0
                # esperar que cargue almenos una propiedad
                esperarPorObjeto(self.navegador.driver, 10,
                                 By.XPATH,
                                 f"{variables.path_resultado[0]}5{variables.path_resultado[1]}",
                                 "Algun resultado")
                # se recorre dos veces por que a veces se salta alguna propiedad
                escribir_en_log(f"Recorrido: {recorrido}", 1)
                while recorrido < 2:

                    self.extraer_links_ventana_actual()


                    if self.links_extraidos > self.propiedades_agregar:

                        escribir_en_log(f"Se alcanzo la cantidad a agregar: {self.propiedades_agregar}", 1)
                        return

                    recorrido += 1

                resultado_comun_actual = self.navegador.obtener_elemento(By.XPATH, variables.path_resultado_comun)
                resultado_comun_actual = self.navegador.obtener_atributo_elemento(resultado_comun_actual, "href")

                # para validar que no se halla quedado colgada la pagina
                if resultado_comun_actual != self.resultado_comun:
                    self.resultado_comun = resultado_comun_actual
                else:
                    self.navegador.click_elemento(variables.path_boton_siguiente)
                    self.extraer_links_ventana_actual()

                boton_siguiente = self.navegador.esperarPorObjeto(self.navegador.driver, 5,
                                                                  variables.path_boton_siguiente, "Boton siguiente")

                if boton_siguiente:
                    self.navegador.click_elemento(variables.path_boton_siguiente)
                else:
                    escribir_en_log(f"Se llego al final de los resultados disponibles", 1)
                    self.hay_resultados = False

    def validacion_para_descarga(self, link):

        return len(self.base.tabla.loc[(self.base.tabla['link'] == link) & (self.base.tabla['titulo'] == "")].index) < 1

    def validar_pagina_existe(self):
        mensaje = ""
        eliminar = True
        path_mensaje = "/html/body/form/div[3]/div[5]/div/div/div/div[1]/div[1]/div[1]/h1"
        path_mensaje2 = "/html/body/div[1]/div[3]/div[4]/div/div/div/h1"
        mensaje = self.navegador.obtener_elemento(By.XPATH, path_mensaje)

        if mensaje is not None:


            if "Envíenos un mensaje" in mensaje.text:
                escribir_en_log(f"Ya se elimino la propiedad", 2)
                eliminar = False
        else:
            mensaje = self.navegador.obtener_elemento(By.XPATH, path_mensaje2)
            if mensaje is not None:

                if "404 PAGINA NO ENCONTRADA" in mensaje.text:
                    escribir_en_log(f"Ya se elimino la propiedad", 2)
                    eliminar = False

        if not eliminar:
            for columna in self.base.obtener_columnas():
                if "publicado" in columna:
                    self.base.actualizar_columna(self.link_descargando, columna, 1)
                    self.base.actualizar_columna(self.link_descargando, "descripcion", "Eliminado")
                    self.base.actualizar_columna(self.link_descargando, "titulo", "Eliminado")

        escribir_en_log(f"Existe la propiedad: {eliminar}", 1)
        return eliminar

    def extraer_titulo(self):
        """Extrae el titulo de la propiedad que se encuentra en la ventana"""
        titulo = self.navegador.obtener_elemento(By.XPATH, variables.path_titulo).text
        escribir_en_log(f"Se obtuvo el titulo: {titulo}", 1)
        self.base.actualizar_columna(self.link_descargando, 'titulo', titulo)
        escribir_en_log(f"Se actualizo el titulo: {titulo}", 1)
    def extraer_precio(self):
        """Extrae el precio de la propiedad que se encuentra en la ventana"""
        precio = "₲"
        for path_precio in [variables.path_precio, variables.path_precio2]:
            try:
                precio = self.navegador.driver.find_element(By.XPATH, path_precio).text
                break
            except:
                pass

        if "₲" in precio:
            precio = precio.replace("₲", "").replace(",", "").rstrip().lstrip() + " GS"
        else:
            precio = precio.replace(",", "").rstrip().lstrip()
        escribir_en_log(f"Se obtuvo el precio y tipo de moneda: {precio}", 1)

        self.base.actualizar_columna(self.link_descargando, "precio", precio)
        escribir_en_log(f"Columna Precio: {precio}", 1)

    def extraer_id(self):
        escribir_en_log(f"Se intentara sacar el ide entre los indices 3 y 11", 1)
        indice = 0
        id = 1
        for indice in range(3, 11):
            path_id = f"{variables.path_id[0]}{indice}{variables.path_id[1]}"
            id = self.navegador.obtener_elemento(By.XPATH, path_id)
            if id is not None:
                id = id.text
                if "ID:" in id:
                    id = id.replace("ID:", "").rstrip().lstrip()
                    escribir_en_log(f"[indice:{indice}]Se encontro el id", 1)
                    break
        if indice != 10 and id != 1:
            escribir_en_log(f"Se extrajo el [ide:{id}]", 1)
            self.base.actualizar_columna(self.link_descargando, "ide", id)
            escribir_en_log(f"Columna Ide {id}", 1)
            self.ide_descargando = id

    def extraer_descripcion(self):
        descripcion = ""
        for path_descri in variables.lista_path_descripcion:
            descriweb = self.navegador.obtener_elemento(By.XPATH, path_descri)
            if descriweb is not None:
                descripcion = descriweb.text
                escribir_en_log(f"Se extrae la descripcion", 1)
                break
        self.base.actualizar_columna(self.link_descargando, "descripcion", descripcion)
        try:
            escribir_en_log(f"Se actualizo la descripcion {descripcion[0:30].lstrip().rstrip()}...", 1)
        except:
            pass
    def extraer_agente_inmobiliario(self):
        agenteweb = self.navegador.obtener_elemento(By.XPATH, variables.path_agente)
        agente = agenteweb.text
        escribir_en_log(f"Se obtiene el agente: {agente}", 1)
        self.base.actualizar_columna(self.link_descargando, "agente_remax", agente)
        escribir_en_log(f"Se actualizo el agente: {agente}", 1)
    def extraer_atributos_tabla(self):

        continuar = True
        indice = 1


        while continuar:
            path_nombre = f"{variables.path_atributo[0]}{indice}{variables.path_atributo[1]}"
            path_valor = f"{variables.path_valor[0]}{indice}{variables.path_valor[1]}"
            nombreweb = self.navegador.obtener_elemento(By.XPATH, path_nombre)
            valorweb = self.navegador.obtener_elemento(By.XPATH, path_valor)
            mts = False
            if nombreweb is not None:
                if valorweb is not None:
                    if nombreweb.text == 'Nº de Dormitorios:':
                        self.base.actualizar_columna(self.link_descargando, "habitaciones", valorweb.text)
                        escribir_en_log(f"Se actualizo la columna habitaciones: {valorweb.text}", 1)
                    elif nombreweb.text == 'Baños:':
                        self.base.actualizar_columna(self.link_descargando, "banio", valorweb.text)
                        escribir_en_log(f"Se actualizo la columna banio: {valorweb.text}", 1)
                    elif nombreweb.text == "Sup. Lote (m²)":
                        self.base.actualizar_columna(self.link_descargando, "mts", valorweb.text)
                        escribir_en_log(f"Se actualizo la columna mts: {valorweb.text}", 1)
                        mts = True
                    elif nombreweb.text == "Area de Construcción (m²)":
                        self.base.actualizar_columna(self.link_descargando, "area", valorweb.text)
                        escribir_en_log(f"Se actualizo la columna area: {valorweb.text}", 1)
            else:
                continuar = False
            if not mts:
                if nombreweb is not None:
                    if valorweb is not None:
                        if nombreweb.text == "Total Mts²":
                            self.base.actualizar_columna(self.link_descargando, "mts", valorweb.text)
                            escribir_en_log(f"Se actualizo la columna mts: {valorweb.text}", 1)
            indice += 1
        escribir_en_log(f"Se quitaron los datos extras de la propiedad: ", 1)


    def extraer_ruta_imagenes(self):
        seguir = True
        indice = 1
        imagenes = []
        while seguir:
            path_ruta_imagen = f"{variables.path_imagen[0]}{indice}{variables.path_imagen[1]}"
            rutaweb = self.navegador.obtener_elemento(By.XPATH, path_ruta_imagen)
            if rutaweb is not None:
                ruta = self.navegador.obtener_atributo_elemento(rutaweb, "src")
                imagenes.append(ruta)
                if len(imagenes) > 8:
                    seguir = False
            else:
                seguir = False
            indice += 1
        return imagenes

    def descargar_imagenes(self):

        # crear carpeta para descargar las imagenes
        ruta_carpeta = Path(PurePath(variables.RUTA_DATOS, self.ide_descargando))
        ruta_carpeta.mkdir(parents=True, exist_ok=True)
        # crear la carpeta img
        ruta_carpeta = Path(PurePath(ruta_carpeta, "img"))
        ruta_carpeta.mkdir(parents=True, exist_ok=True)

        contador = 1
        for ruta in self.extraer_ruta_imagenes():
            inicio_descarga = time.time()
            nombre_imagen = PurePath(ruta_carpeta, f"{contador}_img_{self.ide_descargando.split('-')[0]}.jpg")
            with urllib.request.urlopen(ruta, context=ctx) as u, open(nombre_imagen, "wb") as f:
                escribir_en_log(f"Se descargo la imagen {nombre_imagen}", 1)
                f.write(u.read())
                fin_descarga = time.time()
                duracion_descarga = fin_descarga - inicio_descarga
                escribir_en_log(f"Tiempo descarga {duracion_descarga:.2f}", 1)
                contador += 1

    def scrapear_propiedades_pendientes(self):
        if self.propiedades_scrapear > 0:
            escribir_en_log(f"Funcion scrapear_propiedades_pendientes", 1)
            resultados_validos_descargador = 0
            contador = 1
            contador_proceso = 1
            links_disponibles = self.base.obtener_links()
            escribir_en_log(f"Se debe scrapear {self.propiedades_scrapear} propieades", 1)
            escribir_en_log(f"Links Disponibles: {links_disponibles}", 1)
            for link in links_disponibles:
                escribir_en_log(f"Procesando {contador_proceso} de {self.propiedades_scrapear}", 1)

                if self.validacion_para_descarga(link):
                    escribir_en_log(f"Se abre el link: {link}", 1)
                    self.link_descargando = link
                    self.navegador.abrir_url(link)
                    self.navegador.esperarPorObjeto(self.navegador, 10, variables.path_titulo, "Titulo Propiedad")
                    # funcion para extraer todos los campos
                    if self.validar_pagina_existe():
                        self.extraer_titulo()
                        self.extraer_precio()
                        self.extraer_id()
                        self.extraer_descripcion()
                        self.extraer_agente_inmobiliario()
                        self.extraer_atributos_tabla()
                        self.descargar_imagenes()

                        resultados_validos_descargador += 1

                    if resultados_validos_descargador >= self.propiedades_scrapear:
                        break

                contador_proceso += 1





