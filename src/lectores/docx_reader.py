"""Lee un documento Word (.docx) y devuelve su texto, incluidas las tablas."""

from docx import Document


def leer_docx(ruta) -> str:
    doc = Document(str(ruta))
    partes = []

    # Párrafos sueltos
    for parrafo in doc.paragraphs:
        if parrafo.text.strip():
            partes.append(parrafo.text)

    # Tablas (muchas jornalizaciones vienen en forma de cuadro)
    for tabla in doc.tables:
        for fila in tabla.rows:
            celdas = [celda.text.strip() for celda in fila.cells]
            if any(celdas):
                partes.append(" | ".join(celdas))

    return "\n".join(partes)
