"""Vía principal (sin IA, gratis): si la jornalización ya trae el formato
de tabla estándar, se COPIA el documento completo tal cual (un solo
archivo, con sus logos y encabezado intactos) a su carpeta de salida.

Como el documento ya viene en el diseño final, no hace falta reconstruir
nada: copiar el archivo byte a byte es lo más simple y lo más fiel posible
(cero riesgo de que algo se vea distinto).
"""

import shutil
from pathlib import Path
from typing import List

from .lectores.jornalizacion_tabla import parsear_jornalizacion
from .nombres import detectar_parcial, limpiar_nombre_carpeta


def generar_tal_cual(ruta_entrada, dir_salida_base) -> List[Path]:
    """Si el documento trae el formato de tabla estándar, lo copia a
    salida/<Asignatura>/<Parcial>.docx (un solo archivo) y devuelve
    [ruta_destino]. Si no lo reconoce, devuelve [] para que quien llama
    use el extractor con IA como respaldo.
    """
    ruta_entrada = Path(ruta_entrada)
    if ruta_entrada.suffix.lower() != ".docx":
        # Esta vía solo sabe leer tablas de Word. Un PDF (o Excel) va
        # directo a la vía con IA, que sí sabe leer esos formatos.
        return []

    jornalizacion = parsear_jornalizacion(ruta_entrada)
    if jornalizacion is None:
        return []

    asignatura = next(
        (g.asignatura for g in jornalizacion.grados if g.asignatura), ""
    ) or "sin_asignatura"
    parcial = detectar_parcial(ruta_entrada.stem)

    carpeta = Path(dir_salida_base) / limpiar_nombre_carpeta(asignatura)
    carpeta.mkdir(parents=True, exist_ok=True)

    nombre_archivo = (
        f"{limpiar_nombre_carpeta(parcial)}.docx" if parcial
        else f"{limpiar_nombre_carpeta(ruta_entrada.stem)}.docx"
    )
    ruta_destino = carpeta / nombre_archivo
    shutil.copy2(ruta_entrada, ruta_destino)

    return [ruta_destino]
