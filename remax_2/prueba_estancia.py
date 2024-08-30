from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service as EdgeService
from pathlib import PurePath, Path
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time
from para_log import escribir_en_log    
from selenium import webdriver
import pygetwindow as gw
import pyautogui
from selenium.webdriver.common.keys import Keys
options = Options()
options.add_argument("--start-maximized")


# rutas relativas para el bot
RUTA_BOT = PurePath(Path().absolute())
RUTA_DATOS = PurePath(RUTA_BOT, "datos")
print(RUTA_DATOS)
RUTA_DRIVER = f"{PurePath(RUTA_BOT, "driver")}\\msedgedriver.exe"
print(RUTA_DRIVER)
print(PurePath(RUTA_BOT, 'driver', 'remax_propiedades.csv'))
# Obtener la fecha y hora actual


url = "https://www.remax.com.py/"
# path para inicio
path_campo_ciudad = "/html/body/form/div[3]/div[3]/div[1]/div/div[3]/div/div/div/div[2]/div[2]/input"
path_boton_siguiente = "/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[3]/div[2]/div[1]/div[3]/div[2]/div/nav/ul/li[7]/a"
# para el bucle en el que quita los datos de cada propiedad

def configurar_filtro(navegador):
    path_opciones = "/html/body/div[1]/form/div[3]/div[5]/div/div[1]/div/div/div/div[5]/button[1]"
    path_region = "/html/body/div[1]/form/div[3]/div[5]/div/div[6]/form/div[2]/div/div[2]/div/div[2]/div[1]/div[7]/div/div[1]/div[1]/span"
    path_check_region = "/html/body/div[1]/form/div[3]/div[5]/div/div[6]/form/div[2]/div/div[2]/div/div[2]/div[1]/div[7]/div/div[1]/div[2]/div[2]/div[1]/ul/li/label/div"
    path_boton_comercial = "/html/body/div[1]/form/div[3]/div[5]/div/div[6]/form/div[2]/div/div[2]/div/div[2]/div[1]/div[2]/div/label[2]/span"
    path_check_terreno_estancia = "/html/body/div[1]/form/div[3]/div[5]/div/div[6]/form/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[1]/ul/li"
    path_boton_filtrar = "/html/body/div[1]/form/div[3]/div[5]/div/div[6]/form/div[2]/div/div[3]/button[2]"
    path_zoom_mas = "/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[3]/div[1]/div/div/div[2]/div[2]/div[1]/div/a[1]"
    path_zoom_menos = "/html/body/div[1]/form/div[3]/div[5]/div/div[8]/div/div[3]/div/div/div[3]/div[1]/div/div/div[2]/div[2]/div[1]/div/a[2]"

    navegador.find_element(By.XPATH, path_opciones).click()
    time.sleep(3)
    #navegador.find_element(By.XPATH, path_region).click()
    #time.sleep(3)
    #navegador.find_element(By.XPATH, path_check_region).click()
    #time.sleep(3)
    navegador.find_element(By.XPATH, path_boton_comercial).click()
    time.sleep(3)
    navegador.find_element(By.XPATH, path_check_terreno_estancia).click()
    time.sleep(3)
    navegador.find_element(By.XPATH, path_boton_filtrar).click()
    time.sleep(5)
    for path in [path_zoom_mas, path_zoom_mas,path_zoom_mas, path_zoom_menos, path_zoom_menos, path_zoom_menos]:
        navegador.find_element(By.XPATH, path).click()
        time.sleep(3)
    time.sleep(20)
def buscar_ciudad(ciudad, navegador):
    navegador.get(url)
    """script = ("var campo_ciudad = document.getElementById(\"geolocctrl\");"
              "campo_ciudad.value = ''")
    navegador.execute_script(script)"""
    hay_resultados = True
   
    if ciudad == "Paraguay":
        # ejecuta un script para seleccionar la categoria que requiere
        navegador.find_element(By.XPATH, path_campo_ciudad).send_keys("Paraguay")
        time.sleep(3)
        #navegador.find_element(By.XPATH, path_campo_ciudad).send_keys(Keys.ENTER)
    # click para realizar la busqueda
    navegador.find_element(By.XPATH, "/html/body/form/div[3]/div[3]/div[1]/div/div[3]/div/div/div/div[7]/button").click()
    

edge_driver_path = 'C:\\Users\\ACER\\Documents\\Bots\\pythonProject\\prueba_inicial_remax\\driver\\msedgedriver.exe'
edge_service = EdgeService(executable_path=edge_driver_path)

driver = webdriver.Edge(service=edge_service, options=options)


buscar_ciudad("Paraguay", driver)
if True:
    configurar_filtro(driver)


time.sleep(560)