"""Utilidades de nombres compartidas: detectar el parcial y limpiar
nombres para usarlos como carpeta/archivo."""

import re

_PATRON_PARCIAL = re.compile(
    r"\b([IVX]{1,4})\s*parcial\b|\bparcial\s*([IVX\d]{1,4})\b",
    re.IGNORECASE,
)


def detectar_parcial(texto: str) -> str:
    """Busca algo como 'II parcial' o 'parcial 2' en un texto (normalmente
    el nombre del archivo). Devuelve, por ejemplo, 'II Parcial', o ''."""
    m = _PATRON_PARCIAL.search(texto)
    if not m:
        return ""
    numero = (m.group(1) or m.group(2) or "").upper()
    return f"{numero} Parcial" if numero else "Parcial"


def limpiar_nombre_carpeta(texto: str) -> str:
    texto = re.sub(r"\s+", "_", texto.strip())
    return re.sub(r'[<>:"/\\|?*]', "", texto) or "sin_dato"
