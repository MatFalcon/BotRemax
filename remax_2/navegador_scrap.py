
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from para_log import escribir_en_log
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
edge_driver_path = 'C:\\Users\\ACER\\Documents\\Bots\\pythonProject\\prueba_inicial_remax\\driver\\msedgedriver.exe'



class Navegador:
    def __init__(self):
        # Configura las opciones del navegador
        self.options = Options()

        self.options.add_argument("--start-maximized")  # Abrir en pantalla completa
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--log-level=3")  # para evitar las advertencias
        # Configura el servicio del navegador
        self.edge_driver_path = 'C:\\Users\\ACER\\Documents\\Bots\\pythonProject\\prueba_inicial_remax\\driver\\msedgedriver.exe'
        self.service = Service(self.edge_driver_path)
        # Inicializa el navegador
        self.driver = webdriver.Edge(service=self.service, options=self.options)

    def abrir_url(self, url):
        """
            Abre una url en el navegador

            Parameters
            ----------
            url : str
                url o ruta a la que queremos ir
        """

        self.driver.get(url)
        escribir_en_log(f"Se abre el link: {url}", 1)

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