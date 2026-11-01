"""Extractor: la ÚNICA pieza que habla con la IA (Claude).

Se usa solo cuando la jornalización NO viene en el formato de tabla
estándar (ver lectores/jornalizacion_tabla.py, que no usa IA y es gratis).
Este extractor sirve de respaldo para jornalizaciones en texto libre, o
con un formato de tabla distinto al estándar.

Si el documento Word tiene varias tablas (varias asignaturas), se procesa
UNA TABLA A LA VEZ, en vez de mandarle todo el documento a la IA de un
tirón: con muchas asignaturas, la respuesta de una sola llamada puede
superar el límite de tokens de salida y llegar cortada (JSON inválido).
Varias llamadas chicas, una por asignatura, no tienen ese problema sin
importar cuántas asignaturas traiga el documento.
"""

import os
from pathlib import Path
from typing import List, Optional

import anthropic

from . import config
from .esquema import Jornalizacion, PlanGrado
from .lectores.jornalizacion_tabla import dividir_en_bloques_de_tabla


def _leer_prompt(nombre: str) -> str:
    return (config.DIR_PROMPTS / nombre).read_text(encoding="utf-8")


def _verificar_clave() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "Este documento no tiene el formato de tabla esperado, y la "
            "función de respaldo con IA todavía no está configurada (falta "
            "ANTHROPIC_API_KEY). Pide el documento en el formato de tabla "
            "estándar, o configura la clave de la API para activar esta función."
        )


def _aplicar_recursos_por_defecto_grado(grado: PlanGrado) -> PlanGrado:
    """Si un bloque no trae Recursos explícito, se usa el estándar del
    instituto (config.RECURSOS_POR_DEFECTO) — siempre el mismo texto, no
    varía por tema. Si el documento SÍ trae su propio Recursos, se
    respeta tal cual (no se sobrescribe)."""
    for bloque in grado.bloques:
        if not bloque.recursos.strip():
            bloque.recursos = config.RECURSOS_POR_DEFECTO
    return grado


def _extraer_un_grado(
    texto_bloque: str, cliente, sistema: str, instrucciones: str, modelo: str
) -> PlanGrado:
    """Extrae UN solo grado/asignatura a partir del texto de un bloque
    (una tabla con su encabezado). Llamada chica: nunca se queda sin
    espacio, sin importar cuántas asignaturas traiga el documento completo.
    """
    respuesta = cliente.messages.parse(
        model=modelo,
        max_tokens=4000,
        system=sistema,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{instrucciones}\n\n"
                    "Este texto corresponde a UNA sola asignatura/grado "
                    "(no una lista). Devuelve solo ese grado, con sus "
                    "bloques.\n\n"
                    f"--- BLOQUE DE LA JORNALIZACIÓN ---\n{texto_bloque}"
                ),
            }
        ],
        output_format=PlanGrado,
    )
    return _aplicar_recursos_por_defecto_grado(respuesta.parsed_output)


def _dividir_si_es_docx(ruta_entrada) -> List[str]:
    """Si la entrada es un .docx con varias tablas, devuelve sus bloques
    de texto (uno por tabla). Si no, o si algo falla al leerlo, devuelve
    una lista vacía (se usa la vía de una sola llamada)."""
    if ruta_entrada is None:
        return []
    ruta_entrada = Path(ruta_entrada)
    if ruta_entrada.suffix.lower() != ".docx":
        return []
    try:
        return dividir_en_bloques_de_tabla(ruta_entrada)
    except Exception:
        return []


def extraer_jornalizacion(
    texto_documento: str, modelo: str = None, ruta_entrada=None
) -> Jornalizacion:
    """Llama a Claude y devuelve la jornalización estructurada (validada).

    `ruta_entrada` (opcional) permite dividir un .docx con varias tablas
    en bloques, para no desbordar el límite de tokens de salida cuando
    el documento trae muchas asignaturas. Sin ella (o si no aplica), se
    manda el texto completo en una sola llamada, como antes.
    """
    _verificar_clave()
    modelo = modelo or config.MODELO
    cliente = anthropic.Anthropic()  # lee la clave de ANTHROPIC_API_KEY

    sistema = _leer_prompt("sistema.md")
    instrucciones = _leer_prompt("extraccion.md")

    bloques_texto = _dividir_si_es_docx(ruta_entrada)

    if len(bloques_texto) > 1:
        grados = [
            _extraer_un_grado(bloque, cliente, sistema, instrucciones, modelo)
            for bloque in bloques_texto
        ]
        return Jornalizacion(grados=grados)

    # Un solo bloque (o no se pudo dividir): una sola llamada, como antes.
    respuesta = cliente.messages.parse(
        model=modelo,
        max_tokens=16000,
        system=sistema,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{instrucciones}\n\n"
                    f"--- JORNALIZACIÓN ---\n{texto_documento}"
                ),
            }
        ],
        output_format=Jornalizacion,
    )

    jornalizacion = respuesta.parsed_output
    for grado in jornalizacion.grados:
        _aplicar_recursos_por_defecto_grado(grado)
    return jornalizacion
