"""Script to create sample Excel files with GBM portfolio data."""
import openpyxl
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "gbm")

def create_nacional():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Portafolio Nacional"

    # Header
    ws.append(["App GBM Portfolio"])
    ws.append([])
    ws.append(["Mercado de Capitales Nacional"])
    headers = ["Emisora/Fondo", "Títulos", "Costo promedio", "Precio mercado", "PPP", "Valor mercado", "P / M", "% Var. Hist.", "% Var. Dia.", "Imp X Cto", "% Cartera"]
    ws.append(headers)

    data = [
        ["ALSEA *", 1, 57.90, 52.18, 0.00, 52.18, -5.72, "-", 2.55, "-", 16.76],
        ["AMX B", 1, 23.20, 23.12, 0.00, 23.12, -0.08, "-", -0.30, "-", 7.43],
        ["CEMEX CPO", 1, 19.71, 21.87, 0.00, 21.87, 2.16, "-", 2.24, "-", 7.02],
        ["FMX 23", 1, 27.52, 28.60, 0.00, 28.60, 1.07, "-", 0.03, "-", 9.19],
        ["FSHOP 13", 1, 10.63, 12.80, 0.00, 12.80, 2.16, "-", 2.40, "-", 4.11],
        ["FUNO 11", 1, 29.19, 29.27, 0.00, 29.27, 0.08, "-", -0.27, "-", 9.40],
        ["GFINBUR O", 1, 43.64, 42.86, 0.00, 42.86, -0.78, "-", 0.14, "-", 13.77],
        ["LAB B", 1, 16.57, 15.89, 0.00, 15.89, -0.68, "-", -0.31, "-", 5.10],
        ["VOLAR A", 2, 13.26, 11.54, 0.00, 23.08, -3.45, "-", 6.16, "-", 7.41],
    ]
    for row in data:
        ws.append(row)

    ws.append([])
    ws.append(["Fondos de Inversión Deuda"])
    ws.append(headers)
    ws.append(["GBMRETO BF", 26, 1.85, 1.86, 0.00, 48.36, 0.013, "-", 0.00, "-", 15.53])

    ws.append([])
    ws.append(["Efectivo"])
    ws.append(headers)
    ws.append(["EFEC.  MISMO DIA", 0, 0.00, 0.00, 0.00, 13.30, 0.00, "-", 0.00, "-", 4.27])

    filepath = os.path.join(DATA_DIR, "portafolio-nacional.xlsx")
    wb.save(filepath)
    print(f"Created: {filepath}")


def create_usa():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Portafolio USA"

    ws.append(["App GBM Portfolio"])
    ws.append([])
    ws.append(["Mercado de Capitales USA"])
    headers = ["Emisora/Fondo", "Títulos", "Costo promedio", "Precio mercado", "PPP", "Valor mercado", "P / M", "% Var. Hist.", "% Var. Dia.", "Imp X Cto", "% Cartera"]
    ws.append(headers)

    data = [
        ["QQQ", 0.00813158, 708.35, 713.15, "-", 5.80, 0.04, 0.69, 1.66, 5.76, 37.61],
        ["SOXL", 0.02162928, 130.84, 173.20, "-", 3.75, 0.92, 32.50, 14.02, 2.83, 24.32],
        ["V", 0.00901432, 325.04, 330.75, "-", 2.98, 0.05, 1.70, 0.25, 2.93, 19.33],
        ["VOO", 0.00423439, 673.06, 681.57, "-", 2.89, 0.04, 1.40, 1.03, 2.85, 18.74],
    ]
    for row in data:
        ws.append(row)

    ws.append([])
    ws.append(["Liquidez"])
    ws.append(headers)
    ws.append(["efectivo", "-", "-", "-", "-", 0.00, "-", "-", "-", "-", 0.00])

    filepath = os.path.join(DATA_DIR, "portafolio-usa.xlsx")
    wb.save(filepath)
    print(f"Created: {filepath}")


if __name__ == "__main__":
    create_nacional()
    create_usa()
    print("Done!")
