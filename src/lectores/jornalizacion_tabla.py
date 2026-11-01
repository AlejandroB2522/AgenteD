"""Lee una jornalización que ya viene en el formato oficial más común:

    Expectativas de logro | Tema | Actividades Generales |
    Fecha de ejecución | Recursos | Evaluación

Cada fila es una semana. El documento puede traer un grado o varios (una
tabla por grado), con un párrafo de encabezado (Asignatura / Docente /
Nivel / Grado / Duración) antes de cada tabla.

Esta lectura es DETERMINISTA (sin IA): no tiene costo y es la más fiel,
porque no reescribe nada. Si el documento no coincide con este formato,
`parsear_jornalizacion` devuelve None y hay que usar el extractor con IA
(ver extractor.py).
"""

import re
from typing import List, Optional

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from ..esquema import BloqueSemana, Jornalizacion, PlanGrado

# Con que aparezcan al menos 4 de estos 6 textos en la primera fila,
# se considera que la tabla es una jornalización en este formato.
ENCABEZADOS_ESPERADOS = [
    "expectativas de logro",
    "tema",
    "actividades generales",
    "fecha de ejecuci",  # cubre "ejecución" y "ejecucion"
    "recursos",
    "evaluaci",  # cubre "evaluación" y "evaluacion"
]

_PATRON_ENCABEZADO = re.compile(
    r"(Asignatura|Docente|Nivel|Grado|Duraci[oó]n)\s*:\s*(.*?)(?="
    r"(?:Asignatura|Docente|Nivel|Grado|Duraci[oó]n)\s*:|$)",
    re.IGNORECASE | re.DOTALL,
)


def iter_bloques_documento(doc):
    """Recorre párrafos y tablas del documento en su orden real (no por
    separado como doc.paragraphs / doc.tables, que pierden el orden)."""
    for hijo in doc.element.body.iterchildren():
        if hijo.tag == qn("w:p"):
            yield Paragraph(hijo, doc)
        elif hijo.tag == qn("w:tbl"):
            yield Table(hijo, doc)


def parsear_encabezado(texto: str) -> dict:
    """Extrae Asignatura/Docente/Nivel/Grado/Duración de un bloque de texto
    como: 'Asignatura: X___   Docente: Y___\\nNivel: Z___   Grado: W___'."""
    datos = {}
    for etiqueta, valor in _PATRON_ENCABEZADO.findall(texto):
        clave = etiqueta.lower().replace("ó", "o")
        datos[clave] = valor.strip().strip("_").strip()
    return datos


def es_tabla_jornalizacion(tabla: Table) -> bool:
    """True si la primera fila trae los encabezados esperados."""
    if not tabla.rows:
        return False
    texto = " | ".join(c.text.strip().lower() for c in tabla.rows[0].cells)
    return sum(1 for esperado in ENCABEZADOS_ESPERADOS if esperado in texto) >= 4


def _bloque_desde_celdas(celdas: List[str]) -> Optional[BloqueSemana]:
    if len(celdas) < 6 or not any(celdas):
        return None
    return BloqueSemana(
        expectativas_logro=celdas[0],
        tema=celdas[1],
        actividades=celdas[2],
        fecha_ejecucion=celdas[3],
        recursos=celdas[4],
        evaluacion=celdas[5],
    )


def parsear_jornalizacion(ruta) -> Optional[Jornalizacion]:
    """Devuelve la jornalización estructurada, o None si el documento no
    tiene el formato de cuadro esperado (en ese caso, usar extractor.py)."""
    doc = Document(str(ruta))
    grados: List[PlanGrado] = []
    encabezado: dict = {}

    for item in iter_bloques_documento(doc):
        if isinstance(item, Paragraph):
            encabezado.update(parsear_encabezado(item.text))
        elif isinstance(item, Table):
            if not es_tabla_jornalizacion(item):
                continue
            bloques = []
            for fila in item.rows[1:]:
                bloque = _bloque_desde_celdas([c.text.strip() for c in fila.cells])
                if bloque:
                    bloques.append(bloque)
            if bloques:
                grados.append(
                    PlanGrado(
                        asignatura=encabezado.get("asignatura", ""),
                        docente=encabezado.get("docente", ""),
                        nivel=encabezado.get("nivel", ""),
                        grado=encabezado.get("grado", ""),
                        duracion=encabezado.get("duracion", ""),
                        bloques=bloques,
                    )
                )
            encabezado = {}  # listo para el siguiente grado

    return Jornalizacion(grados=grados) if grados else None


def dividir_en_bloques_de_tabla(ruta) -> List[str]:
    """Divide el documento en bloques de texto, uno por cada TABLA que
    tenga (con los párrafos que la preceden como contexto) — sin exigir
    que las columnas coincidan con ningún formato en particular.

    Se usa en la vía con IA para documentos con muchas asignaturas/tablas
    (ej. una jornalización general con 9 espacios pedagógicos): en vez de
    mandarle todo el documento a la IA de una sola vez (la respuesta se
    corta por el límite de tokens de salida), se manda un bloque a la vez
    y se arma un grado por cada uno.

    Si el documento no tiene ninguna tabla, devuelve una lista vacía (en
    ese caso, se manda el texto completo en una sola llamada).
    """
    doc = Document(str(ruta))
    bloques: List[str] = []
    parrafos_actuales: List[str] = []

    for item in iter_bloques_documento(doc):
        if isinstance(item, Paragraph):
            if item.text.strip():
                parrafos_actuales.append(item.text.strip())
        elif isinstance(item, Table):
            if not item.rows:
                continue
            texto_tabla = "\n".join(
                " | ".join(c.text.strip() for c in fila.cells)
                for fila in item.rows
            )
            texto_bloque = "\n".join(parrafos_actuales) + "\n\n" + texto_tabla
            bloques.append(texto_bloque.strip())
            parrafos_actuales = []

    return bloques
