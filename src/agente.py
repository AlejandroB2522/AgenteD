"""Orquestador: une todo el flujo. Hay dos caminos, y en AMBOS el
resultado es UN solo archivo por jornalización (parcial):

1. SIN IA (gratis, recomendado, usado automáticamente cuando se puede):
   si el documento ya trae el formato de cuadro estándar (Expectativas de
   logro | Tema | Actividades | Fecha | Recursos | Evaluación), se copia
   el documento completo tal cual a salida/ - sin pasar por la IA.

       entrada/jornalizacion.docx -> generador_tal_cual -> salida/Asignatura/Parcial.docx

2. CON IA (respaldo): si el documento viene en texto libre y no calza con
   ese formato, se usa Claude para extraer los datos a un JSON de revisión
   y luego se arma un único documento con la plantilla oficial.

       entrada/jornalizacion.docx -> extractor (IA) -> revision/jornalizacion.json
                                                            |  (se revisa)
       plantillas/plantilla_oficial.docx -> llenador -> salida/Asignatura/Parcial.docx
"""

import json
from pathlib import Path

from . import config
from .esquema import Jornalizacion
from .extractor import extraer_jornalizacion
from .generador_tal_cual import generar_tal_cual
from .lectores import leer_documento
from .llenador import generar_plan


def procesar(ruta_entrada, dir_salida_base=None):
    """Punto de entrada único: intenta primero sin IA; si el formato no se
    reconoce, usa IA automáticamente (sin pausa de revisión manual).

    Devuelve (rutas_generadas, metodo) donde metodo es "tabla" o "ia".
    """
    ruta_entrada = Path(ruta_entrada)
    dir_salida_base = Path(dir_salida_base or config.DIR_SALIDA)

    rutas = generar_tal_cual(ruta_entrada, dir_salida_base)
    if rutas:
        return rutas, "tabla"

    ruta_json, _ = extraer_a_revision(ruta_entrada)
    rutas = generar_desde_revision(ruta_json, dir_salida_base)
    return rutas, "ia"


def extraer_a_revision(ruta_entrada, ruta_json=None):
    """Lee la jornalización con IA y guarda un JSON para revisar.

    Se usa solo cuando el documento NO trae el formato de tabla estándar
    (si lo trae, usa generar_tal_cual directamente: es gratis y más fiel).
    Devuelve (ruta_json, jornalizacion).
    """
    texto = leer_documento(ruta_entrada)
    jornalizacion = extraer_jornalizacion(texto, ruta_entrada=ruta_entrada)

    config.DIR_REVISION.mkdir(parents=True, exist_ok=True)
    if ruta_json is None:
        ruta_json = config.DIR_REVISION / (Path(ruta_entrada).stem + ".json")
    ruta_json = Path(ruta_json)

    ruta_json.write_text(jornalizacion.model_dump_json(indent=2), encoding="utf-8")
    return ruta_json, jornalizacion


def generar_desde_revision(ruta_json, dir_salida_base=None):
    """Lee el JSON (ya revisado) y arma el documento final. Devuelve las
    rutas generadas (una sola, el documento con todos los grados)."""
    ruta_json = Path(ruta_json)
    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    jornalizacion = Jornalizacion.model_validate(datos)

    dir_salida_base = Path(dir_salida_base or config.DIR_SALIDA)
    return generar_plan(jornalizacion, ruta_json.stem, dir_salida_base)
