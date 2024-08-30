import os

# Cambia esta ruta a la ruta de tu escritorio
desktop_path = os.path.expanduser("\\192.168.1.5\\contabilidad")

# Palabras clave para buscar en el nombre de los archivos
keywords = ["orden", "pagos"]


def search_files(base_path, keywords):
    matches = []

    # Recorre el directorio y subdirectorios
    for root, dirs, files in os.walk(base_path):
        print(root)
        for file in files:
            if "orden" in file:
                print(file)

    return matches


# Llama a la función y guarda los resultados
found_files = search_files(desktop_path, keywords)

# Imprime los resultados
for file in found_files:
    print(file)
