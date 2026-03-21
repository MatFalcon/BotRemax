import os
import re
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
    escribir_en_log(f"Entrando a funcion esperarPorObjeto", 1)
    escribir_en_log(f"Esperando {tiempo}seg por: {nombre}", 1)
    try:
        WebDriverWait(navegador_abierto, tiempo).until(
            expected_conditions.presence_of_element_located((tipoObjeto, identificadorObjeto)))
        escribir_en_log(f"Saliendo de funcion esperarPorObjeto - Exito", 1)
        return True
    except Exception as ex:
        escribir_en_log(f"No se cargo {nombre}", 2)
        escribir_en_log(f"Saliendo de funcion esperarPorObjeto - Error", 1)
        return False

class BaseCentury:

    def __init__(self):
        escribir_en_log(f"Entrando a funcion __init__ de BaseCentury", 1)
        tabla = ""
        escribir_en_log(f"Saliendo de funcion __init__ de BaseCentury", 1)

    def abrir_base(self):
        escribir_en_log(f"Entrando a funcion abrir_base", 1)
        # Leer la base desde el CSV.  Si el archivo no contiene las nuevas columnas de metros
        # (mts para terreno y mts_construccion para metros edificados), se agregan dinámicamente
        # con valores vacíos para evitar errores posteriormente al actualizar.
        self.tabla = pd.read_csv(variables.RUTA_DF)
        # Asegurar que existan las columnas necesarias para metros de terreno y construcción.
        columnas_necesarias = ["mts", "mts_construccion"]
        columnas_actuales = set(self.tabla.columns.tolist())
        columnas_faltantes = [col for col in columnas_necesarias if col not in columnas_actuales]
        if columnas_faltantes:
            for col in columnas_faltantes:
                # Agregar la columna con valores vacíos para todas las filas
                self.tabla[col] = ""
            # Guardar inmediatamente los cambios en disco para persistir la nueva estructura
            try:
                self.tabla.to_csv(variables.RUTA_DF, index=False)
                # Guardar también a Excel si existe la ruta
                try:
                    self.tabla.to_excel(variables.RUTA_EXCEL, index=False)
                except:
                    pass
            except Exception as e:
                # Registrar un error si no se pudo guardar, pero continuar para evitar bucles
                escribir_en_log(f"No se pudo agregar columnas de metros en la base: {str(e)}", 2)
        escribir_en_log(f"Saliendo de funcion abrir_base", 1)

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
        escribir_en_log(f"Entrando a funcion validacion_link", 1)
        validacion = len(self.tabla.loc[self.tabla['link'] == link]) > 0
        escribir_en_log(f"Existe link: {validacion}", 1)
        escribir_en_log(f"Saliendo de funcion validacion_link", 1)
        return validacion

    def guardar_base(self):
        """sobreescribe la base y actualiza"""
        escribir_en_log(f"Entrando a funcion guardar_base", 1)
        escribir_en_log(f"Se actualizo la base", 1)
        self.tabla.to_csv(variables.RUTA_DF, index=False)
        try:
            self.tabla.to_excel(variables.RUTA_EXCEL, index=False)
        except:
            pass
        self.abrir_base()
        escribir_en_log(f"Saliendo de funcion guardar_base", 1)

    def obtener_columnas(self):
        escribir_en_log(f"Entrando a funcion obtener_columnas", 1)
        columnas = self.tabla.columns
        escribir_en_log(f"Saliendo de funcion obtener_columnas", 1)
        return columnas

    def crear_nueva_fila(self, tipo_propiedad, link, ciudad):
        escribir_en_log(f"Entrando a funcion crear_nueva_fila", 1)
        modelo_fila = [{'titulo': '', 'tipo': tipo_propiedad, 'precio': '',
                        'descripcion': '', 'link': link, 'ide': '',
                        'ciudad': ciudad, 'publicado_facebook': '',
                        'fecha_inserion': datetime.now().strftime("%d/%m/%Y"),
                        'publicado_clasipar': '', 'publicado_info': '',
                        'publicado_hendyla': '', 'intentos':1,
                        'mts': '', 'mts_construccion': ''}]
        modelo_DF = pd.DataFrame(modelo_fila)
        self.tabla = pd.concat([self.tabla, modelo_DF], ignore_index=True)
        escribir_en_log(f"Nuevo registro para el link: {link}", 1)
        self.guardar_base()
        escribir_en_log(f"Saliendo de funcion crear_nueva_fila", 1)

    def obtener_links(self):
        escribir_en_log(f"Entrando a funcion obtener_links", 1)
        links = self.tabla.loc[(self.tabla['titulo'].isna()) | (self.tabla['descripcion'] == "")]['link']
        escribir_en_log(f"Saliendo de funcion obtener_links", 1)
        return links

    def obtener_fila(self, ide):
        escribir_en_log(f"Entrando a funcion obtener_fila", 1)
        fila = self.tabla.loc[self.tabla['ide'] == ide]
        escribir_en_log(f"Saliendo de funcion obtener_fila", 1)
        return fila

    def actualizar_columna(self, link, columna, dato, guardar=True):
        """actualiza una fila segun el link, opcionalmente guarda en disco"""
        escribir_en_log(f"Entrando a funcion actualizar_columna", 1)
        self.tabla.loc[self.tabla['link'] == link, columna] = dato
        if guardar:
            self.guardar_base()
        escribir_en_log(f"Saliendo de funcion actualizar_columna", 1)

class RemaxScrap:

    def __init__(self, ciudad, propiedades_agregar, propiedades_scrapear):
        escribir_en_log(f"Entrando a funcion __init__ de RemaxScrap", 1)
        self.url_pagina = "https://century21.com.py/"
        self.propiedades_agregar = propiedades_agregar
        self.navegador = None
        self.ciudad = ciudad
        self.ciudad_campo = {
            "Asuncion": "Asunción",
            "Sanber": "San Ber",
            "Fernando": "Fernando",
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
        self.resultados_esperados_por_pag = 10
        self.base = None
        self.links_extraidos = 0
        self.resultado_comun = ""
        self.propiedades_scrapear = propiedades_scrapear
        self.link_descargando = ""
        self.ide_descargando = "Sin Ide"
        self.link_intentos = {}
        self.pagina_actual = 1
        escribir_en_log(f"Saliendo de funcion __init__ de RemaxScrap", 1)

    def abrir_base(self):
        """abre la base para validaciones"""
        escribir_en_log(f"Entrando a funcion abrir_base", 1)
        base = BaseCentury()
        base.abrir_base()
        self.base = base
        escribir_en_log(f"Saliendo de funcion abrir_base", 1)

    def instanciar_navegador(self):
        """
            Crea o abre un navegador para nuestro objeto
        """
        escribir_en_log(f"Entrando a funcion instanciar_navegador", 1)
        self.navegador = Navegador()
        escribir_en_log(f"Saliendo de funcion instanciar_navegador", 1)

    def abrir_navegador(self):
        """
            Abre la pagina de remax
        """
        escribir_en_log(f"Entrando a funcion abrir_navegador", 1)
        escribir_en_log(f"Se abre la pagina de remax", 1)
        self.navegador.abrir_url(self.url_pagina)
        escribir_en_log(f"Saliendo de funcion abrir_navegador", 1)

    def obtener_xpath_siguiente(self):
        """
            Calcula el XPATH dinámico del botón de siguiente página según la página actual
        """
        if self.pagina_actual < 7:
            li_index = self.pagina_actual + 1
        else:
            # Desde página 7 en adelante siempre es la flecha: li[7]
            li_index = 7
        print("xpath_siguiente", f"/html/body/div/main/div/div/div[5]/nav/ul/li[{li_index}]/button")
        return f"/html/body/div/main/div/div/div[5]/nav/ul/li[{li_index}]/button"

    def buscar_ciudad(self):
        """
            Rellenar el campo de ciudad, luego realiza la busqueda
        """
        escribir_en_log(f"Entrando a funcion buscar_ciudad", 1)
        if self.propiedades_agregar > 0:
            if self.navegador.rellenar_elemento(variables.path_campo_ciudad_century, self.ciudad_campo[self.ciudad]):
                time.sleep(3)
                escribir_en_log(f"Se realizar la busqueda de las propiedades de la ciudad {self.ciudad}", 1)
                self.navegador.click_elemento(variables.path_boton_buscar_century)

                time.sleep(10)
                # espera que cargue algun elemento de la pagina, en este caso un resultado de búsqueda
                path_primer_resultado = f"{variables.path_resultado_century[0]}1{variables.path_resultado_century[1]}"
                self.navegador.esperarPorObjeto(self.navegador.driver, 3, path_primer_resultado, "primer resultado")
                # elemento_boton = self.navegador.obtener_elemento(By.XPATH, variables.path_boton_siguiente)
                # if elemento_boton is None:
                #     variables.path_boton_siguiente = "/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[2]/div/div[3]/div[2]/div/nav/ul/li[7]/a"


    def extraer_links_ventana_actual(self):
        """Extrae los links de los resultados disponibles en la vista actual"""

        for indice in range(1, self.resultados_esperados_por_pag):
            escribir_en_log(f"Se quita datos del resultado: {indice}", 1)
            # inicializacion de los paths de los elementos que vamos a extraer
            path_resultado = f"{variables.path_resultado_century[0]}{indice}{variables.path_resultado_century[1]}"

            # estado y tipo de propiedad
            estado_propiedad = "Sin Estado"

            # validar que sean propiedades disponibles
            if estado_propiedad not in variables.tipo_propiedad_excluir:
                # se obtiene el link
                elemento_link = self.navegador.obtener_elemento(By.XPATH, path_resultado)

                link_propiedad = self.navegador.obtener_atributo_elemento(elemento_link, "href")
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
                            # Abrir la página de detalle temporalmente para obtener el tipo de propiedad
                            tipo_propiedad = "Sin Tipo"
                            try:
                                # Guardar la URL actual
                                url_actual = self.navegador.driver.current_url
                                # Abrir el link de la propiedad
                                self.navegador.abrir_url(link_propiedad)
                                # El wait ya lo hace la funcion de abajo
                                # Extraer el tipo de propiedad con logica mejorada
                                tipo_propiedad = self.extraer_tipo_propiedad()
                                # Volver a la página de resultados
                                self.navegador.abrir_url(url_actual)
                                time.sleep(2)  # Esperar a que cargue la página de resultados
                            except Exception as ex:
                                escribir_en_log(f"Error al obtener tipo de propiedad para {link_propiedad}: {str(ex)}", 2)
                                # Si hay error, intentar volver a la página de resultados
                                try:
                                    self.navegador.driver.back()
                                    time.sleep(2)
                                except:
                                    pass
                            
                            # Crear la fila con el tipo de propiedad obtenido
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
                                 f"{variables.path_resultado_century}",
                                 "Algun resultado")
                # se recorre dos veces por que a veces se salta alguna propiedad
                escribir_en_log(f"Recorrido: {recorrido}", 1)
                while recorrido < 2:
                    # cuando entra en la pagina esta funcion extrae los links de los resultados disponibles en la vista actual
                    self.extraer_links_ventana_actual()


                    if self.links_extraidos > self.propiedades_agregar:

                        escribir_en_log(f"Se alcanzo la cantidad a agregar: {self.propiedades_agregar}", 1)
                        return

                    recorrido += 1

                # se obtiene el xpath del boton de siguiente pagina
                xpath_boton = self.obtener_xpath_siguiente()
                # se espera que cargue el boton de siguiente pagina
                if esperarPorObjeto(self.navegador.driver, 5, By.XPATH, xpath_boton, "Botón siguiente"):
                    self.navegador.click_elemento(xpath_boton)
                    print("Esperando 10 segundos")
                    time.sleep(3)
                    self.pagina_actual += 1
                    escribir_en_log(f"Avanzando a la página {self.pagina_actual}", 1)
                else:
                    escribir_en_log("No se encontró botón de siguiente página. Finalizando recorrido.", 2)
                    self.hay_resultados = False
                    break

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
        path_titulo_century = "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div[4]/h1"
        elemento_titulo = self.navegador.obtener_elemento(By.XPATH, path_titulo_century)
        if elemento_titulo is not None:
            titulo = elemento_titulo.text
            escribir_en_log(f"Se obtuvo el titulo: {titulo}", 1)
            self.base.actualizar_columna(self.link_descargando, 'titulo', titulo)
            escribir_en_log(f"Se actualizo el titulo: {titulo}", 1)
        else:
            escribir_en_log(f"No se pudo obtener el titulo", 2)
    def extraer_precio(self):
        """Extrae el precio de la propiedad y lo formatea para compatibilidad con publicar_info.py
        
        Formatos esperados:
        - Dólares: "US$ 85.000" → "85000 $"
        - Guaraníes: "G 1.155.428.495" → "1155428495 GS"
        """
        path_precio_century = "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div[4]/h6[1]"
        elemento_precio = self.navegador.obtener_elemento(By.XPATH, path_precio_century)
        precio_formateado = ""
        if elemento_precio is not None:
            texto_precio = elemento_precio.text.strip()
            escribir_en_log(f"Texto precio original: {texto_precio}", 1)
            
            # Verificar si hay precio en dólares (puede estar en un span dentro del h6)
            # Primero verificar si hay ambos precios (guaraníes y dólares)
            if "G " in texto_precio or "₲" in texto_precio:
                # Formato: "G 1.155.428.495 / US$ 168.000" o "₲ 1.155.428.495"
                # Extraer el número principal (antes del / si hay conversión a USD)
                texto_principal = texto_precio.split("/")[0].strip()
                # Remover "G " o "₲ " y limpiar puntos y comas
                precio_numero = texto_principal.replace("G ", "").replace("₲", "").replace(".", "").replace(",", "").strip()
                precio_formateado = f"{precio_numero} GS"
                escribir_en_log(f"Precio en guaraníes encontrado: {precio_formateado}", 1)
            elif "US$" in texto_precio or "USD" in texto_precio.upper():
                # Formato: "US$ 85.000" (solo dólares)
                # Buscar patrón US$ seguido de número con puntos
                match_usd = re.search(r'US\$\s*([\d.]+)', texto_precio)
                if match_usd:
                    precio_numero = match_usd.group(1).replace(".", "").replace(",", "")
                    precio_formateado = f"{precio_numero} $"
                    escribir_en_log(f"Precio en dólares encontrado: {precio_formateado}", 1)
                else:
                    # Si no se encuentra el patrón, intentar extraer manualmente
                    partes = texto_precio.split("US$")
                    if len(partes) > 1:
                        precio_numero = partes[1].strip().replace(".", "").replace(",", "").split()[0]
                        precio_formateado = f"{precio_numero} $"
            else:
                # Si no se identifica la moneda, intentar procesar como está
                precio_numero = texto_precio.replace(".", "").replace(",", "").replace("$", "").replace("US", "").replace("G", "").replace("₲", "").strip()
                precio_formateado = f"{precio_numero} GS"  # Por defecto guaraníes
            
            if precio_formateado:
                self.base.actualizar_columna(self.link_descargando, "precio", precio_formateado)
                escribir_en_log(f"Columna Precio actualizada: {precio_formateado}", 1)
            else:
                escribir_en_log(f"No se pudo formatear el precio correctamente", 2)
        else:
            escribir_en_log(f"No se pudo obtener el elemento del precio", 2)

    def extraer_id(self):
        """Extrae el ID de la propiedad desde el elemento específico de Century21"""
        path_id_century = "/html/body/div[1]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]"
        elemento_id = self.navegador.obtener_elemento(By.XPATH, path_id_century)
        id = "Sin Ide"
        if elemento_id is not None:
            texto_id = elemento_id.text.strip()
            # El formato es "ID: 42962" o similar, extraer solo el número
            if "ID:" in texto_id:
                # Extraer solo el número después de "ID:"
                id = texto_id.replace("ID:", "").strip()
                # Limpiar cualquier carácter adicional (como <br> tags que puedan aparecer en el texto)
                id = id.split()[0] if id.split() else "Sin Ide"
                escribir_en_log(f"Se extrajo el [ide:{id}]", 1)
                self.base.actualizar_columna(self.link_descargando, "ide", id)
                escribir_en_log(f"Columna Ide {id}", 1)
                self.ide_descargando = id
            else:
                escribir_en_log(f"No se encontró 'ID:' en el texto: {texto_id}", 2)
        else:
            escribir_en_log(f"No se pudo obtener el elemento del ID", 2)

    def extraer_descripcion(self):
        """Extrae la descripción de la propiedad"""
        path_descripcion_century = "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div[4]/p[1]"
        elemento_descripcion = self.navegador.obtener_elemento(By.XPATH, path_descripcion_century)
        descripcion = ""
        if elemento_descripcion is not None:
            descripcion = elemento_descripcion.text
            escribir_en_log(f"Se extrae la descripcion", 1)
            self.base.actualizar_columna(self.link_descargando, "descripcion", descripcion)
            try:
                escribir_en_log(f"Se actualizo la descripcion {descripcion[0:30].lstrip().rstrip()}...", 1)
            except:
                pass
        else:
            escribir_en_log(f"No se pudo obtener la descripcion", 2)
    def extraer_tipo_propiedad(self):
        """Extrae el tipo de propiedad desde la página de detalle con búsqueda robusta"""
        # Elemento base esperado (puede variar índice final)
        # /html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div[6]/span
        
        path_base = "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div"
        tipo_propiedad = "Sin Tipo"
        
        # Esperar primero a que cargue el contenedor general o el título
        esperarPorObjeto(self.navegador.driver, 5, By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div", "Contenedor Info")
        
        # Intentar buscar en los índices probables donde suele aparecer el tipo (5, 6, 7)
        indices_a_probar = [6, 5, 7] 
        
        for idx in indices_a_probar:
            xpath_candidato = f"{path_base}[{idx}]/span"
            elemento = self.navegador.obtener_elemento(By.XPATH, xpath_candidato)
            if elemento:
                texto = elemento.text.strip()
                # Validación simple: que no sea vacío y que parezca un tipo (longitud razonable)
                if texto and len(texto) < 50:
                    tipo_propiedad = texto
                    escribir_en_log(f"Se obtuvo el tipo de propiedad en div[{idx}]: {tipo_propiedad}", 1)
                    return tipo_propiedad

        escribir_en_log(f"No se pudo obtener el tipo de propiedad (probados índices {indices_a_probar})", 2)
        return tipo_propiedad

    def extraer_ano_construccion(self):
        """Extrae el año de construcción de la propiedad"""
        path_ano_century = "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div[8]/span"
        elemento_ano = self.navegador.obtener_elemento(By.XPATH, path_ano_century)
        if elemento_ano is not None:
            ano = elemento_ano.text.strip()
            escribir_en_log(f"Se obtuvo el año de construcción: {ano}", 1)
            self.base.actualizar_columna(self.link_descargando, "ano_construccion", ano)
            escribir_en_log(f"Se actualizo el año de construcción: {ano}", 1)
        else:
            escribir_en_log(f"No se pudo obtener el año de construcción", 2)
    def _limpiar_metros(self, valor_texto):
        """
        Convierte un texto de metros a entero manejando diferentes formatos:
        - "160,0 m²" → 160  (coma decimal)
        - "160.0 m²" → 160  (punto decimal)
        - "1.600,5 m²" → 1600  (punto miles, coma decimal)
        - "1,600.5 m²" → 1600  (coma miles, punto decimal)
        """
        try:
            # Quitar unidad y espacios
            valor = valor_texto.lower().replace("m²", "").replace("m2", "").replace("m\u00b2", "").strip()
            escribir_en_log(f"Limpiando metros - valor original: '{valor_texto}' → sin unidad: '{valor}'", 1)

            # Detectar el formato basándose en la posición de puntos y comas
            tiene_punto = "." in valor
            tiene_coma = "," in valor

            if tiene_punto and tiene_coma:
                # Ambos presentes: el último es el decimal
                pos_punto = valor.rfind(".")
                pos_coma = valor.rfind(",")

                if pos_coma > pos_punto:
                    # Formato europeo: 1.600,50 → punto es miles, coma es decimal
                    valor = valor.replace(".", "")  # Quitar separador miles
                    valor = valor.replace(",", ".")  # Coma a punto decimal
                else:
                    # Formato americano: 1,600.50 → coma es miles, punto es decimal
                    valor = valor.replace(",", "")  # Quitar separador miles

            elif tiene_coma:
                # Solo coma: verificar si es decimal o miles
                partes = valor.split(",")
                if len(partes) == 2 and len(partes[1]) <= 2:
                    # Es decimal: "160,0" o "160,50"
                    valor = valor.replace(",", ".")
                else:
                    # Es separador de miles: "1,600"
                    valor = valor.replace(",", "")

            elif tiene_punto:
                # Solo punto: verificar si es decimal o miles
                partes = valor.split(".")
                if len(partes) == 2 and len(partes[1]) <= 2:
                    # Es decimal: "160.0" o "160.50" - dejarlo así
                    pass
                else:
                    # Es separador de miles: "1.600"
                    valor = valor.replace(".", "")

            resultado = str(int(float(valor)))
            escribir_en_log(f"Metros procesados: '{valor_texto}' → {resultado}", 1)
            return resultado

        except Exception as ex:
            escribir_en_log(f"Error al limpiar metros '{valor_texto}': {str(ex)}", 2)
            return "1"

    def extraer_atributos_tabla(self):
        """Extrae los atributos iterando sobre los divs hijos del bloque de atributos"""
        base_path = "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div[4]/div/div"
        indice = 1
        continuar = True

        while continuar:
            path_div = f"{base_path}[{indice}]"
            elemento_div = self.navegador.obtener_elemento(By.XPATH, path_div)

            if elemento_div is not None:
                try:
                    # Buscar el span con el nombre del atributo
                    elemento_span = elemento_div.find_element(By.TAG_NAME, "span")
                    nombre_atributo = elemento_span.text.strip()

                    # Buscar el br que contiene el valor (el siguiente elemento después del span)
                    # El valor está después del <br>, así que obtenemos el texto completo y separamos
                    texto_completo = elemento_div.text
                    # El formato es: "Nombre\nValor", así que separamos por salto de línea
                    partes = texto_completo.split('\n')
                    if len(partes) >= 2:
                        valor = partes[1].strip()
                    else:
                        # Si no hay salto de línea, intentar obtener el texto después del span
                        valor = texto_completo.replace(nombre_atributo, "").strip()

                    escribir_en_log(f"Atributo encontrado: {nombre_atributo} = {valor}", 1)

                    # Mapear los nombres de atributos a las columnas.  Se normaliza el nombre
                    # del atributo para poder comparar sin acentos y evitar problemas de mayúsculas.
                    nombre_norm = nombre_atributo.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").strip()

                    if nombre_norm == "dormitorios":
                        self.base.actualizar_columna(self.link_descargando, "habitaciones", valor)
                        escribir_en_log(f"Se actualizo la columna habitaciones: {valor}", 1)
                    elif nombre_norm == "baños" or nombre_norm == "banos":
                        self.base.actualizar_columna(self.link_descargando, "banio", valor)
                        escribir_en_log(f"Se actualizo la columna banio: {valor}", 1)
                    elif nombre_norm == "terreno":
                        valor_int = self._limpiar_metros(valor)
                        self.base.actualizar_columna(self.link_descargando, "mts", valor_int)
                        escribir_en_log(f"Se actualizo la columna mts: {valor_int}", 1)
                    elif nombre_norm.startswith("construccion"):
                        valor_int = self._limpiar_metros(valor)
                        # Actualizar la nueva columna para metros de construcción
                        self.base.actualizar_columna(self.link_descargando, "mts_construccion", valor_int)
                        escribir_en_log(f"Se actualizo la columna mts_construccion: {valor_int}", 1)
                        # También actualizar la columna antigua 'area' por compatibilidad si existe
                        if "area" in self.base.tabla.columns:
                            self.base.actualizar_columna(self.link_descargando, "area", valor_int)
                            escribir_en_log(f"Se actualizo la columna area (compatibilidad): {valor_int}", 1)
                except Exception as ex:
                    escribir_en_log(f"Error al procesar atributo en div[{indice}]: {str(ex)}", 2)

                indice += 1
            else:
                continuar = False

        escribir_en_log(f"Se extrajeron los atributos de la propiedad", 1)


    def extraer_ruta_imagenes(self):
        """Extrae las rutas de las imágenes en ALTA CALIDAD abriendo el lightbox/modal"""
        imagenes = []
        max_imagenes = 6

        # XPath de la primera imagen thumbnail para hacer clic y abrir el lightbox
        path_primer_thumbnail = "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div[1]/img"

        # XPaths del lightbox (modal de imágenes en alta calidad)
        # La imagen principal del lightbox puede estar en diferentes posiciones
        paths_imagen_lightbox = [
            "/html/body/div[3]/section/div[1]/div[2]/div/img",
            "/html/body/div[3]/section/div[1]/div[3]/div/img",
            "/html/body/div[3]/section/div[1]/div/div/img",
            "//div[contains(@class,'lightbox')]//img",
            "//section//div[contains(@class,'slide')]//img"
        ]

        # XPaths posibles para el botón siguiente en el lightbox
        paths_boton_siguiente = [
            "/html/body/div[3]/section/div[1]/div[3]",  # Botón siguiente común
            "/html/body/div[3]/section/div[1]/button[2]",
            "//button[contains(@class,'next')]",
            "//div[contains(@class,'next')]",
            "//a[contains(@class,'next')]",
            "/html/body/div[3]/section/div[2]/button[2]"
        ]

        # XPaths posibles para cerrar el lightbox
        paths_cerrar_lightbox = [
            "/html/body/div[3]/section/div[1]/div[1]",  # Botón cerrar común
            "/html/body/div[3]/section/button",
            "//button[contains(@class,'close')]",
            "//div[contains(@class,'close')]",
            "//span[contains(@class,'close')]"
        ]

        try:
            # 1. Hacer clic en la primera imagen thumbnail para abrir el lightbox
            elemento_thumbnail = self.navegador.obtener_elemento(By.XPATH, path_primer_thumbnail)
            if elemento_thumbnail is None:
                escribir_en_log("No se encontró thumbnail para abrir lightbox, usando método antiguo", 2)
                return self._extraer_ruta_imagenes_fallback()

            elemento_thumbnail.click()
            escribir_en_log("Se hizo clic en thumbnail para abrir lightbox", 1)
            time.sleep(1.5)  # Esperar a que abra el lightbox

            # 2. Extraer imágenes del lightbox
            intentos_sin_nueva = 0
            max_intentos_sin_nueva = 3

            while len(imagenes) < max_imagenes and intentos_sin_nueva < max_intentos_sin_nueva:
                # Buscar la imagen actual en el lightbox
                ruta_encontrada = None
                for path_img in paths_imagen_lightbox:
                    try:
                        if path_img.startswith("//"):
                            elemento_img = self.navegador.driver.find_element(By.XPATH, path_img)
                        else:
                            elemento_img = self.navegador.obtener_elemento(By.XPATH, path_img)

                        if elemento_img:
                            ruta = elemento_img.get_attribute("src")
                            if ruta and ruta not in imagenes:
                                imagenes.append(ruta)
                                ruta_encontrada = ruta
                                escribir_en_log(f"Imagen HD encontrada [{len(imagenes)}]: {ruta[:80]}...", 1)
                                intentos_sin_nueva = 0
                                break
                    except:
                        continue

                if not ruta_encontrada:
                    intentos_sin_nueva += 1

                # 3. Intentar ir a la siguiente imagen
                siguiente_clickeado = False
                for path_sig in paths_boton_siguiente:
                    try:
                        if path_sig.startswith("//"):
                            btn_siguiente = self.navegador.driver.find_element(By.XPATH, path_sig)
                        else:
                            btn_siguiente = self.navegador.obtener_elemento(By.XPATH, path_sig)

                        if btn_siguiente:
                            btn_siguiente.click()
                            siguiente_clickeado = True
                            time.sleep(0.8)  # Esperar transición
                            break
                    except:
                        continue

                if not siguiente_clickeado:
                    escribir_en_log("No se pudo avanzar a siguiente imagen en lightbox", 2)
                    break

            # 4. Cerrar el lightbox
            for path_cerrar in paths_cerrar_lightbox:
                try:
                    if path_cerrar.startswith("//"):
                        btn_cerrar = self.navegador.driver.find_element(By.XPATH, path_cerrar)
                    else:
                        btn_cerrar = self.navegador.obtener_elemento(By.XPATH, path_cerrar)

                    if btn_cerrar:
                        btn_cerrar.click()
                        escribir_en_log("Lightbox cerrado", 1)
                        break
                except:
                    continue

            # Si no se pudo cerrar con botón, intentar con ESC
            if len(imagenes) > 0:
                try:
                    from selenium.webdriver.common.keys import Keys
                    self.navegador.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                except:
                    pass

        except Exception as ex:
            escribir_en_log(f"Error en extracción de imágenes HD: {str(ex)}", 2)
            # Fallback al método antiguo si falla
            if len(imagenes) == 0:
                return self._extraer_ruta_imagenes_fallback()

        escribir_en_log(f"Total imágenes HD encontradas: {len(imagenes)}", 1)
        return imagenes

    def _extraer_ruta_imagenes_fallback(self):
        """Método de respaldo: extrae thumbnails si falla el lightbox"""
        imagenes = []
        paths_imagenes_century = [
            "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div[1]/img",
            "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/div[1]/img",
            "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/div[2]/img",
            "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/div[3]/img",
            "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/div[4]/img",
            "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/div/div[5]/img"
        ]

        for path_imagen in paths_imagenes_century:
            elemento_imagen = self.navegador.obtener_elemento(By.XPATH, path_imagen)
            if elemento_imagen is not None:
                ruta = self.navegador.obtener_atributo_elemento(elemento_imagen, "src")
                if ruta and ruta not in imagenes:
                    imagenes.append(ruta)
                    escribir_en_log(f"Imagen fallback encontrada: {ruta}", 1)
                if len(imagenes) >= 6:
                    break

        escribir_en_log(f"Total imágenes fallback: {len(imagenes)}", 1)
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
            if ruta:  # Verificar que la ruta no esté vacía
                try:
                    inicio_descarga = time.time()
                    # Usar el ID o un identificador único para el nombre de la imagen
                    id_imagen = self.ide_descargando if self.ide_descargando != "Sin Ide" else str(time.time())
                    nombre_imagen = PurePath(ruta_carpeta, f"{contador}_img_{id_imagen.split('-')[0] if '-' in id_imagen else id_imagen}.jpg")
                    with urllib.request.urlopen(ruta, context=ctx) as u, open(nombre_imagen, "wb") as f:
                        escribir_en_log(f"Se descargo la imagen {nombre_imagen}", 1)
                        f.write(u.read())
                        fin_descarga = time.time()
                        duracion_descarga = fin_descarga - inicio_descarga
                        escribir_en_log(f"Tiempo descarga {duracion_descarga:.2f}", 1)
                        contador += 1
                except Exception as ex:
                    escribir_en_log(f"Error al descargar imagen {ruta}: {str(ex)}", 2)

    def extraer_metros(self):
        """Extrae los metros de terreno y construcción"""
        try:
            # Contenedor padre de las características
            path_contenedor = "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div[4]/div"
            contenedor = self.navegador.obtener_elemento(By.XPATH, path_contenedor)

            if contenedor:
                # Buscar todos los divs hijos directos
                divs_hijos = contenedor.find_elements(By.XPATH, "./div")

                mtrs_terreno = "1"
                mtrs_construccion = "1"

                for div in divs_hijos:
                    try:
                        # Buscar el título (Terreno o Construcción)
                        titulo_elem = div.find_element(By.XPATH, "./span")
                        titulo = titulo_elem.text.strip()

                        # Obtener el texto completo del div
                        texto_completo = div.text.strip()  # "Terreno\n500,0 m²"

                        # Extraer el valor numérico (después del título)
                        valor_raw = texto_completo.replace(titulo, "").strip()  # "500,0 m²"

                        # Usar la función de limpieza robusta
                        valor_final = self._limpiar_metros(valor_raw)

                        if "Terreno" in titulo:
                            mtrs_terreno = valor_final
                            escribir_en_log(f"Metros Terreno encontrado: {mtrs_terreno}", 1)
                            self.base.actualizar_columna(self.link_descargando, "mts", mtrs_terreno, guardar=False)

                        elif "Construcción" in titulo:
                            mtrs_construccion = valor_final
                            escribir_en_log(f"Metros Construcción encontrado: {mtrs_construccion}", 1)
                            self.base.actualizar_columna(self.link_descargando, "mts_construccion", mtrs_construccion, guardar=False)
                            
                    except Exception as e:
                        continue
                        
        except Exception as ex:
             escribir_en_log(f"Error al extraer metros: {str(ex)}", 2)

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
                    
                    # Esperar a que cargue el título usando el nuevo XPATH de Century21
                    path_titulo_century = "/html/body/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div[4]/h1"
                    
                    # Verificar si carga el título, si no, asumir que la página está rota/eliminada
                    titulo_cargado = esperarPorObjeto(self.navegador.driver, 10, By.XPATH, path_titulo_century, "Titulo Propiedad")
                    
                    if not titulo_cargado:
                         escribir_en_log(f"No cargó la página correctamente (título no encontrado). Marcando como eliminado.", 2)
                         # Marcar como eliminado para no volver a intentar
                         try:
                             # Actualizar en memoria sin guardar en disco cada vez
                             for columna in self.base.obtener_columnas():
                                 if "publicado" in columna:
                                     self.base.actualizar_columna(self.link_descargando, columna, 1, guardar=False)
                             
                             self.base.actualizar_columna(self.link_descargando, "descripcion", "Eliminado - No Carga", guardar=False)
                             # Guardar solo al final de todas las actualizaciones
                             self.base.actualizar_columna(self.link_descargando, "titulo", "Eliminado - No Carga", guardar=True)
                             
                         except Exception as ex:
                             escribir_en_log(f"Error al marcar como eliminado: {str(ex)}", 2)
                    else:
                        # funcion para extraer todos los campos
                        if self.validar_pagina_existe():
                            self.extraer_titulo()
                            self.extraer_precio()
                            self.extraer_id()
                            self.extraer_descripcion()
                            self.extraer_ano_construccion()
                            self.extraer_metros() # Nuevo metodo agregado
                            self.extraer_atributos_tabla()
                            self.descargar_imagenes()

                            resultados_validos_descargador += 1

                        if resultados_validos_descargador >= self.propiedades_scrapear:
                            break

                contador_proceso += 1


def variables_configuracion():
    """
    Lee la configuracion establecida en el archivo excel en la carpeta driver
    Pass.xlsx['Configuracion']
    """
    # abre el excel
    excel = openpyxl.load_workbook(PurePath(variables.RUTA_BOT, "driver", "Pass.xlsx"), read_only=True)
    # se saca la hoja Configuracion
    hoja = excel.worksheets[3]
    # La columna es B
    columna_valor = 2

    cantidad_propiedades = hoja.cell(row=2, column=columna_valor).value
    cantidad_publicar = hoja.cell(row=3, column=columna_valor).value
    cantidad_agregar = hoja.cell(row=4, column=columna_valor).value

    excel.close()
    return {'cantidad_propiedades': cantidad_propiedades,
            'cantidad_publicar': cantidad_publicar,
            'cantidad_agregar': cantidad_agregar}


# Código de prueba (comentado para uso en ejecucion_bot.py)
# scrapeador = RemaxScrap("Asuncion", 1000, 1000)
# scrapeador.instanciar_navegador()
# scrapeador.abrir_navegador()
# scrapeador.abrir_base()
# scrapeador.buscar_ciudad()
# scrapeador.recorrer_ventanas()
# scrapeador.scrapear_propiedades_pendientes()
# time.sleep(120)

