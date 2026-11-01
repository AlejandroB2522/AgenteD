"""Lectores: convierten la jornalización (Word, Excel o PDF) a texto plano."""

from pathlib import Path

from .docx_reader import leer_docx
from .pdf_reader import leer_pdf
from .xlsx_reader import leer_xlsx


def leer_documento(ruta) -> str:
    """Lee el documento según su extensión y devuelve su texto."""
    ext = Path(ruta).suffix.lower()
    if ext == ".docx":
        return leer_docx(ruta)
    if ext in (".xlsx", ".xlsm"):
        return leer_xlsx(ruta)
    if ext == ".pdf":
        return leer_pdf(ruta)
    raise ValueError(
        f"Formato no soportado: '{ext}'. Usa .docx, .xlsx o .pdf."
    )
