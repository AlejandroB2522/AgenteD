"""Rutas y configuración del proyecto, en un solo lugar."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carga las variables del archivo .env (si existe)
load_dotenv()

# Carpeta raíz del proyecto (un nivel por encima de src/)
RAIZ = Path(__file__).resolve().parent.parent

# Carpetas de trabajo
DIR_ENTRADA = RAIZ / "entrada"
DIR_PLANTILLAS = RAIZ / "plantillas"
DIR_SALIDA = RAIZ / "salida"
DIR_REVISION = RAIZ / "revision"
DIR_PROMPTS = Path(__file__).resolve().parent / "prompts"

# Plantilla oficial (encabezado con los logos del instituto, cuerpo
# vacío), usada como base en la vía de respaldo con IA.
PLANTILLA_OFICIAL = DIR_PLANTILLAS / "plantilla_oficial.docx"

# Modelo de Claude (se puede cambiar en el archivo .env)
MODELO = os.getenv("MODELO_CLAUDE", "claude-sonnet-5-5")

# Texto fijo de "Recursos" para la vía con IA: el instituto usa
# prácticamente siempre los mismos recursos, así que no varía por tema.
# Se usa solo cuando el documento de entrada no trae su propio Recursos
# (si lo trae, como en Cívica, se respeta lo que diga el documento).
RECURSOS_POR_DEFECTO = (
    "Recursos Humanos, Libro de texto, Pizarra, Lápiz y borradores, "
    "proyector, cartulinas, marcadores."
)
