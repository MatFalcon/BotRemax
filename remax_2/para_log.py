import datetime
from pathlib import PurePath, Path
import os
niveles = {
    1: "INFO:\t  ",
    2: "ADVERTENCIA:",
    3: "ERROR:\t  "
}
RUTA_BOT = PurePath(Path().absolute())
ruta_archivo_log = PurePath(RUTA_BOT, "log.txt")
def escribir_en_log(mensaje, nivel_error):
    
    if nivel_error == 4:
        try:
            os.remove(ruta_archivo_log)
        except:
            pass
    if nivel_error != 4:
        
        archivo_log = open(ruta_archivo_log, "a")
        hora_fecha = datetime.datetime.now()
        hora_fecha = hora_fecha.strftime("[%Y-%m-%d %H:%M:%S]")
        texto = f"{hora_fecha} {niveles[nivel_error]} {mensaje}\n"
        archivo_log.write(texto)
        print(texto)
        archivo_log.close()
    
