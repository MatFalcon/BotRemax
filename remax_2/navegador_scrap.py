from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from para_log import escribir_en_log
from pathlib import PurePath, Path

# Obtener la ruta del driver de Edge de forma dinámica
RUTA_BOT = PurePath(Path().absolute())
edge_driver_path = f"{PurePath(RUTA_BOT, 'driver')}\\msedgedriver.exe"



class Navegador:
    def __init__(self):
        # Configura las opciones del navegador Edge
        self.options = Options()

        self.options.add_argument("--start-maximized")  # Abrir en pantalla completa
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-software-rasterizer') # Evita warnings D3D12
        self.options.add_argument("--log-level=3")  # para evitar las advertencias
        # Configura el servicio del navegador Edge
        self.edge_driver_path = edge_driver_path
        # Servicio Edge
        self.service = EdgeService(executable_path=self.edge_driver_path)

        # Inicialización del navegador Edge
        self.driver = webdriver.Edge(service=self.service, options=self.options)

    def abrir_url(self, url, intentos=3):
        """
            Abre una url en el navegador con reintentos para manejar timeouts
            
            Parameters
            ----------
            url : str
                url o ruta a la que queremos ir
            intentos : int
                cantidad de intentos en caso de error
        """
        for i in range(intentos):
            try:
                self.driver.set_page_load_timeout(60) # Timeout de 60 segundos
                self.driver.get(url)
                escribir_en_log(f"Se abre el link: {url}", 1)
                return True
            except Exception as e:
                escribir_en_log(f"Error al abrir URL (intento {i+1}/{intentos}): {str(e)}", 2)
                try:
                    # Si falla, intentar detener la carga o refrescar
                    self.driver.execute_script("window.stop();")
                except:
                    pass
                
                if i == intentos - 1:
                    escribir_en_log(f"No se pudo cargar la URL después de {intentos} intentos", 3)
                    return False
                pass

    def obtener_elemento(self, by, value):
        try:
            elemento = self.driver.find_element(by, value)

            return elemento
        except Exception as e:
            return None

    def click_elemento(self,  path):
        """
        Clickea un elemento en el navegador abierto

        Parameters
        ----------
        path: str
            ruta html del elemento a clickear

        """
        try:
            elemento = self.obtener_elemento(By.XPATH, path)
            print(f"Elemento :{[elemento]}")
            if elemento:
                elemento.click()
                escribir_en_log(f"Elemento clickeado", 1)
        except:
            escribir_en_log(f"No se pudo clickear un elemento", 3)

    def rellenar_elemento(self, path, texto):
        """
            Rellena campos de paginas

            Parameters
            ----------
            path: str
                ruta html del elemento o campo a rellenar
            texto: str
                texto con el cual se rellenara el campo
        """
        try:
            elemento = self.obtener_elemento(By.XPATH, path)
            elemento.send_keys(texto)
            escribir_en_log(f"Se relleno un campo con texto", 1)
            return True
        except:
            return False

    def cerra_navegador(self):
        """Cierra el navegador instanciado"""
        self.driver.quit()
        escribir_en_log(f"Se cerro el navegador", 1)

    def esperarPorObjeto(self, navegador, tiempo, identificadorobjeto, nombre):
        """
        Espera la carga de un objeto un maximo de segundos

        Parameters
        ----------
        navegador : webdriver
            navegador que vamos a manipular.
        tiempo : int or float
            segundos maximo de espera.
        identificadorobjeto: str
            path del elemento que esperamos en la pagina

        Returns
        -------
        bool
            retorna False si no carga el elemento caso contrario True.
        """

        try:
            WebDriverWait(navegador, tiempo).until(
                expected_conditions.presence_of_element_located((By.XPATH, identificadorobjeto)))
            escribir_en_log(f"Cargo el objeto {nombre}", 1)
            return True
        except:
            escribir_en_log(f"No cargo el objeto {nombre}", 3)
            return False

    def obtener_atributo_elemento(self, elemento, atributo):
        """
            Obtiene los atributos de las etiquetas

            Parameters
            ----------
            elemento : html
                elemento que se obtuvo con obtener_elemento()
            atributo : str
                un atributo eje: href

            Returns
            -------
            str or int
                valor del atributo
        """
        try:
            valor_atributo = elemento.get_attribute(atributo)
            return valor_atributo
        except:
            return None

    def ejecutar_script(self, script, nombre):

        escribir_en_log(f"Se ejecuto el script con exito {nombre}", 1)
        try:
            self.driver.execute_script(script)
            escribir_en_log(f"Se ejecuto el script con exito {nombre}", 1)
            return True
        except Exception as ex:
            escribir_en_log(f"No se pudo ejecutar el script {nombre}", 3)
            print(ex)
            return False