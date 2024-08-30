import time
import pandas as pd
from navegador_scrap import Navegador
import variables
from para_log import escribir_en_log
from scrapeador import BaseRemax
import re
from selenium.webdriver.common.by import By
class Clasipar:

    def __init__(self, cantidad_publicar, credenciales):
        self.cantidad_publicar = cantidad_publicar
        self.credenciales = credenciales
        self.navegador = Navegador()
        self.numero_usuario = 1
        self.plataforma = ""
        self.configuracion = {}
        self.propiedad_procesando = pd.DataFrame()
        self.base = BaseRemax()
        self.ide = ""

    def configurar_plataforma(self, plataforma):
        """configura las variables base para cada plataforma"""
        self.plataforma = plataforma
        if plataforma == "clasipar":
            self.configuracion = {
                "url": variables.clasipar_url_inicio_sesion,
                "campo_correo": variables.clasipar_campo_correo,
                "campo_contrasenia": variables.clasipar_campo_contrasenia,
                "boton_iniciar_sesion": variables.clasipar_boton_ingresar,
                "ventana_emergente": variables.clasipar_ventana_emergente,
                "url_publicar": variables.clasipar_publicar_url
            }
        elif plataforma == "infocasas":
            self.configuracion = {
                "url": variables.info_url_inicio_sesion,
                "campo_correo": variables.info_campo_correo,
                "campo_contrasenia": variables.info_campo_contrasenia,
                "boton_iniciar": variables.info_boton_ingresar,
                "boton_continuar": variables.info_boton_continuar,
                "boton_iniciar_sesion": variables.info_boton_iniciar_sesion
            }


    def instanciar_navegador(self):
        """inicializa el navegador"""
        self.navegador.abrir_url(self.configuracion["url"])

    def iniciar_sesion(self):
        """inicia sesion en la plataforma"""
        # una vez abierta la pagina clickeamos en iniciar sesion
        if self.plataforma == "infocasas":
            self.navegador.esperarPorObjeto(self.navegador.driver,
                                            10,
                                            self.configuracion["boton_iniciar"],
                                            "Boton Iniciar Sesion")
            self.navegador.click_elemento(self.configuracion["boton_iniciar"])
        # se completa el campo de correo
        self.navegador.esperarPorObjeto(self.navegador.driver, 10, self.configuracion["campo_correo"], "Campo Correo")
        self.navegador.rellenar_elemento(self.configuracion["campo_correo"], self.credenciales[self.numero_usuario]["correo"])
        if self.plataforma == "infocasas":
            self.navegador.click_elemento(self.configuracion["boton_continuar"])
            time.sleep(1)
        # se completa el campo contrasenia y se inicia sesion para comenzar a publicar
        self.navegador.rellenar_elemento(self.configuracion["campo_contrasenia"], self.credenciales[self.numero_usuario]["contrasenia"])
        self.navegador.esperarPorObjeto(self.navegador.driver, 2, self.configuracion["boton_iniciar_sesion"], "Boton Iniciar Sesion")
        self.navegador.click_elemento(self.configuracion["boton_iniciar_sesion"])
    def obtener_ides_pendientes(self):
        self.base.abrir_base()
        columna = f"{self.numero_usuario}publicado_{self.plataforma}"
        return self.base.tabla.loc[(self.base.tabla[columna].isna()) & (pd.notna(self.base.tabla['ide']))]['ide'].to_list()

    def setear_titulo(self):
        """Setea el titulo en el formulario para publicar"""
        titulo = self.propiedad_procesando["titulo"].to_list()[0]
        titulo = titulo.strip().lstrip()
        self.navegador.esperarPorObjeto(self.navegador.driver, 5,
                                        variables.clasipar_campo_titulo, "Campo titulo")
        self.navegador.rellenar_elemento(variables.clasipar_campo_titulo, titulo)
        # check tipo de publicacion
        time.sleep(1)
        check = self.navegador.obtener_elemento(By.XPATH, variables.clasipar_check)
        self.navegador.click_elemento(check)

    def filtrar_caracteres_bmp(self, texto):
        # Expresión regular para encontrar caracteres fuera del BMP
        bmp_regex = re.compile(r'[^\u0000-\uFFFF]')
        # Filtrar caracteres fuera del BMP y retornar el texto modificado
        return bmp_regex.sub('', texto)

    def setear_descripcion(self):

        descripcion = self.propiedad_procesando["descripcion"].to_list()[0]
        descripcion = self.filtrar_caracteres_bmp(descripcion)
        self.navegador.rellenar_elemento(variables.clasipar_campo_descripcion, descripcion)
        time.sleep(3)



    def elejir_tipo_inmueble(self):
        """Seleccion la cartergoria inmueble
            luego selecciona el tipo de propiedad ques se va a publicar
        """
        # tipo de propiedad ej: Casa
        tipo = self.propiedad_procesando["tipo"].to_list()[0]
        path_categoria = (f"/html/body/main/div/section/div[2]/div/article/div/"
                          f"div[2]/div/div/select/option[{variables.categorias[tipo]}]")

        path_categoria_siguiente = "/html/body/main/div/section/div[2]/div/article/div/div[2]/div/div[2]/button"
        # se selcciona el tipo de propiedad
        self.navegador.click_elemento(path_categoria)
        # se da click al boton siguiente luego de seleccionar el tipo
        self.navegador.esperarPorObjeto(self.navegador.driver, 5,
                                        path_categoria_siguiente, "Boton Siguiente")
        self.navegador.click_elemento(path_categoria_siguiente)

    def setear_precio(self):

        precios = self.propiedad_procesando["precio"].to_list()[0]
        moneda = precios.split(" ")[1]
        precio = precios.split(" ")[0]
        script = ("var selectElement = document.getElementById('currency');"
                  "var event = new Event('mousedown');"
                  "selectElement.dispatchEvent(event);"
                  "selectElement.options[2].selected = true;")
        if moneda == "USD":
            self.navegador.ejecutar_script(script, "Cambiar precio a dolar")

        precio = int(float(precio.split(" ")[0].replace(",", "")))
        self.navegador.rellenar_elemento(variables.clasipar_path_precio, str(precio))

    def setear_departamento(self):
        central = ["Fernando", "Sanlo", "Luque", "Lamba", "VillaElisa", "Ñemby", "Capiata"]
        cordillera = ["Sanber", "Aregua", "Altos"]
        ciudad = self.propiedad_procesando["ciudad"].to_list()[0]
        if ciudad in central:
            script = (
                "var selectElement = document.evaluate(\"/html/body/main/div/section/div[2]/div[1]/article/form/div[7]/div[1]/div/select\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
                "var event = new Event('mousedown');"
                "selectElement.dispatchEvent(event);"
                "selectElement.options[9].selected = true;")
            self.navegador.ejecutar_script(script, "Script para setear departamento o estado")
        elif ciudad in cordillera:
            script = (
                "var selectElement = document.evaluate(\"/html/body/main/div/section/div[2]/div[1]/article/form/div[7]/div[1]/div/select\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
                "var event = new Event('mousedown');"
                "selectElement.dispatchEvent(event);"
                "   ")
            self.navegador.ejecutar_script(script, "Script para setear departamento o estado")
        elif ciudad == "Asuncion":
            script = (
                "var selectElement = document.evaluate(\"/html/body/main/div/section/div[2]/div[1]/article/form/div[7]/div[1]/div/select\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
                "var event = new Event('mousedown');"
                "selectElement.dispatchEvent(event);"
                "selectElement.options[4].selected = true;")
            self.navegador.ejecutar_script(script, "Script para setear departamento o estado")

    def setear_campos(self):
        time.sleep(5)
        self.setear_titulo()
        self.setear_descripcion()
        self.setear_precio()
        self.setear_departamento()

    def iniciar_publicacion(self):

        escribir_en_log(f"Iniciar Publicacion", 1)

        ides_pendientes = self.obtener_ides_pendientes()

        for ide in ides_pendientes:
            time.sleep(3)
            self.navegador.abrir_url(variables.clasipar_publicar_url)
            # al abrir la pagina siempre salta una ventana emergente
            self.navegador.esperarPorObjeto(self.navegador.driver, 10,
                                            self.configuracion["ventana_emergente"], "Ventana emergente")
            self.navegador.click_elemento(self.configuracion["ventana_emergente"])
            # se elije la categoria inmueble
            self.navegador.click_elemento(variables.clasipar_tipo_publicacion)

            self.ide = ide
            self.propiedad_procesando = self.base.obtener_fila(ide)
            self.elejir_tipo_inmueble()
            self.setear_campos()
            input("Continuar")





#publicador = Publicador(1,  {1: {"correo":"alexavillamayorremax@gmail.com", "contrasenia": "Benjavilla1991"}})
publicador = Clasipar(1,  {1: {"correo":"matiasemmanuelfalcon@gmail.com",
                                 "contrasenia": "lafranja1902"}})
publicador.configurar_plataforma("clasipar")
publicador.instanciar_navegador()
publicador.iniciar_sesion()
publicador.iniciar_publicacion()
input("cerrar")
publicador.navegador.cerra_navegador()
