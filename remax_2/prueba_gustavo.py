from pathlib import PurePath


carpeta_hasta_datos = str(PurePath("C:", "Users", "MSI", "Documents")).split("\\")
carpeta_hasta_datos = "\\".join(carpeta_hasta_datos)


print(carpeta_hasta_datos)