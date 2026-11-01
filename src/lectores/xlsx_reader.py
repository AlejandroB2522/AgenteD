"""Lee una hoja de cálculo (.xlsx) y devuelve su contenido como texto."""

from openpyxl import load_workbook


def leer_xlsx(ruta) -> str:
    # data_only=True para obtener los valores, no las fórmulas
    libro = load_workbook(str(ruta), data_only=True)
    partes = []

    for hoja in libro.worksheets:
        partes.append(f"# Hoja: {hoja.title}")
        for fila in hoja.iter_rows(values_only=True):
            celdas = [str(valor) for valor in fila if valor is not None]
            if celdas:
                partes.append(" | ".join(celdas))

    return "\n".join(partes)
