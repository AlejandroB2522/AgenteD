"""Lee un PDF y devuelve su texto.

Nota: funciona con PDF de texto. Si el PDF es una imagen escaneada, no
tendrá texto extraíble y habría que añadir OCR más adelante.
"""

import pdfplumber


def leer_pdf(ruta) -> str:
    partes = []
    with pdfplumber.open(str(ruta)) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text() or ""
            if texto.strip():
                partes.append(texto)
    return "\n".join(partes)
