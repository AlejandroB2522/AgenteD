"""Vía de respaldo (con IA): construye UN solo documento con todos los
grados de la jornalización, usando la plantilla oficial (encabezado con
los logos del instituto) como base y armando las tablas directamente —
el mismo método que ya trae el documento original.

Se usa solo cuando la jornalización NO viene en el formato de tabla
estándar (si lo trae, generador_tal_cual.py copia el archivo directo, sin
pasar por IA ni por aquí).
"""

import unicodedata
from pathlib import Path
from typing import List

from docx import Document
from docx.oxml.ns import qn

from . import config
from .esquema import Jornalizacion, PlanGrado
from .nombres import detectar_parcial, limpiar_nombre_carpeta


def _normalizar_asignatura(texto: str) -> str:
    """Normaliza un nombre de asignatura para AGRUPAR (sin tildes, sin
    espacios de sobra, en minúsculas), porque la IA no siempre escribe el
    mismo nombre exactamente igual entre un bloque y otro (ej. 'Biología'
    vs 'Biologia') y eso no debe partir una asignatura en dos archivos."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return " ".join(sin_tildes.lower().split())

ENCABEZADOS_COLUMNAS = [
    "Expectativas de logro",
    "Tema",
    "Actividades Generales",
    "Fecha de ejecución",
    "Recursos",
    "Evaluación",
]


def _vaciar_cuerpo(doc: Document) -> None:
    """Borra el contenido del cuerpo sin tocar el encabezado/pie (que vive
    en la sección, definida por <w:sectPr>, el último hijo del cuerpo)."""
    body = doc.element.body
    for hijo in list(body):
        if hijo.tag != qn("w:sectPr"):
            body.remove(hijo)


def _agregar_campo_formulario(parrafo, etiqueta: str, valor: str, ancho: int = 20) -> None:
    """Agrega 'Etiqueta: valor___' al párrafo con el estilo real del
    instituto: la etiqueta en negrita, y el valor (más el relleno de la
    línea en blanco) SUBRAYADO — como si estuviera escrito sobre la línea
    de un formulario, no solo guiones bajos sueltos en el texto.
    """
    run_etiqueta = parrafo.add_run(f"{etiqueta}: ")
    run_etiqueta.bold = True

    relleno = "_" * max(ancho - len(valor), 4)
    run_valor = parrafo.add_run(f"{valor}{relleno}")
    run_valor.underline = True


def _agregar_grado(doc: Document, grado: PlanGrado) -> None:
    p1 = doc.add_paragraph()
    _agregar_campo_formulario(p1, "Asignatura", grado.asignatura)
    p1.add_run("                      ")
    _agregar_campo_formulario(p1, "Docente", grado.docente)

    p2 = doc.add_paragraph()
    _agregar_campo_formulario(p2, "Nivel", grado.nivel)
    p2.add_run("                      ")
    _agregar_campo_formulario(p2, "Grado", grado.grado)

    p3 = doc.add_paragraph()
    _agregar_campo_formulario(p3, "Duración", grado.duracion)

    tabla = doc.add_table(rows=1, cols=len(ENCABEZADOS_COLUMNAS))
    tabla.style = "Table Grid"
    for i, texto in enumerate(ENCABEZADOS_COLUMNAS):
        tabla.cell(0, i).text = texto

    for bloque in grado.bloques:
        fila = tabla.add_row()
        valores = [
            bloque.expectativas_logro,
            bloque.tema,
            bloque.actividades,
            bloque.fecha_ejecucion,
            bloque.recursos,
            bloque.evaluacion,
        ]
        for i, valor in enumerate(valores):
            fila.cells[i].text = valor

    doc.add_paragraph("")  # separación visual entre grados


def generar_plan(jornalizacion: Jornalizacion, nombre_base: str, dir_salida_base) -> List[Path]:
    """Genera un documento por cada ASIGNATURA distinta que traiga la
    jornalización, a partir de la plantilla oficial. Cada documento junta
    todos los grados de esa asignatura (como en Cívica: una asignatura,
    varios grados -> un solo archivo). Si la jornalización trae varias
    asignaturas distintas (ej. Economía, Biología, Cívica...), cada una
    sale en su propio archivo — no se mezclan en uno solo.

    `nombre_base` es el nombre del archivo original (sin extensión); de
    ahí se detecta el parcial, igual que en la vía sin IA.
    """
    parcial = detectar_parcial(nombre_base)

    grupos: "dict[str, tuple[str, list[PlanGrado]]]" = {}
    for grado in jornalizacion.grados:
        nombre = grado.asignatura or "sin_asignatura"
        clave = _normalizar_asignatura(nombre)
        if clave in grupos:
            grupos[clave][1].append(grado)
        else:
            grupos[clave] = (nombre, [grado])

    rutas: List[Path] = []
    for asignatura, grados in grupos.values():
        doc = Document(str(config.PLANTILLA_OFICIAL))
        _vaciar_cuerpo(doc)
        for grado in grados:
            _agregar_grado(doc, grado)

        carpeta = Path(dir_salida_base) / limpiar_nombre_carpeta(asignatura)
        carpeta.mkdir(parents=True, exist_ok=True)

        nombre_archivo = (
            f"{limpiar_nombre_carpeta(parcial)}.docx" if parcial
            else f"{limpiar_nombre_carpeta(nombre_base)}.docx"
        )
        ruta_destino = carpeta / nombre_archivo
        doc.save(str(ruta_destino))
        rutas.append(ruta_destino)

    return rutas
