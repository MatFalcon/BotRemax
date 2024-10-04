import pandas as pd


def excel_to_csv():

    arch_ex = pd.read_excel("remax_propiedades.xlsx")
    arch_ex.to_csv("remax_propiedades.csv", index=False)
def csv_to_excel():
    arch_csv = pd.read_csv("remax_propiedades.csv")
    arch_csv.to_excel("remax_propiedades.xlsx", index=False)

menu = """
1. Mi EXCEL a CSV
2. Mi CSV a Excel
3. SALIR
Opcion:"""



while True:
    opcion = int(input(menu))
    if opcion == 1:
        excel_to_csv()
    elif opcion == 2:
        csv_to_excel()
    elif opcion == 3:
        break


