"""Prueba del lector/generador determinista (sin IA), con un documento
construido para imitar la forma real: encabezado de página (header, con
logos/nombre de instituto), párrafo de datos del grado + tabla con las 6
columnas estándar, repetido para dos grados.
"""

from docx import Document

from src.generador_tal_cual import generar_tal_cual
from src.lectores.jornalizacion_tabla import (
    dividir_en_bloques_de_tabla,
    parsear_jornalizacion,
)
from src.nombres import detectar_parcial


def _agregar_grado(doc, grado, filas):
    doc.add_paragraph(
        f"Asignatura: EDUCACION CIVICA___      Docente: Ana Garcia___\n"
        f"Nivel: Educacion Basica___      Grado: {grado}___\n"
        f"Duracion: 2 H/C___"
    )
    doc.add_paragraph("VB:____________________")

    tabla = doc.add_table(rows=1 + len(filas), cols=6)
    encabezados = [
        "Expectativas de logro", "Tema", "Actividades Generales",
        "Fecha de ejecución", "Recursos", "Evaluación",
    ]
    for i, texto in enumerate(encabezados):
        tabla.cell(0, i).text = texto
    for fila_i, fila in enumerate(filas, start=1):
        for col_i, valor in enumerate(fila):
            tabla.cell(fila_i, col_i).text = valor


def _crear_documento_ejemplo(ruta, con_header=False):
    doc = Document()
    if con_header:
        header = doc.sections[0].header
        header.paragraphs[0].text = "INSTITUTO DE PRUEBA"
        header.add_paragraph("Planificación Parcial")

    _agregar_grado(doc, "Octavo", [
        ["Identificar valores cívicos.", "Buen ciudadano", "Lluvia de ideas",
         "04-08 de Mayo", "Pizarra", "Participación"],
        ["Reconocer derechos.", "Derechos humanos", "Análisis de casos",
         "11-15 de Mayo", "Libro de texto", "Trabajo escrito"],
    ])
    _agregar_grado(doc, "Séptimo", [
        ["", "", "Lluvia de ideas", "04-08 de Mayo", "Pizarra", "Participación"],
    ])
    doc.save(str(ruta))


def test_parsear_jornalizacion(tmp_path):
    ruta = tmp_path / "jornalizacion.docx"
    _crear_documento_ejemplo(ruta)

    jornalizacion = parsear_jornalizacion(ruta)

    assert jornalizacion is not None
    assert len(jornalizacion.grados) == 2

    octavo = jornalizacion.grados[0]
    assert octavo.grado == "Octavo"
    assert octavo.docente == "Ana Garcia"
    assert len(octavo.bloques) == 2
    assert octavo.bloques[0].tema == "Buen ciudadano"
    assert octavo.bloques[1].fecha_ejecucion == "11-15 de Mayo"

    septimo = jornalizacion.grados[1]
    assert septimo.grado == "Séptimo"
    assert len(septimo.bloques) == 1  # fila con tema vacío pero datos igual


def test_parsear_documento_no_reconocido(tmp_path):
    ruta = tmp_path / "otro.docx"
    doc = Document()
    doc.add_paragraph("Esto no es una jornalización en formato de tabla.")
    doc.save(str(ruta))

    assert parsear_jornalizacion(ruta) is None


def test_generar_tal_cual_un_solo_archivo(tmp_path):
    """Debe generar UN solo archivo (copia completa), no uno por semana."""
    ruta = tmp_path / "jornalizacion.docx"
    _crear_documento_ejemplo(ruta)

    rutas = generar_tal_cual(ruta, tmp_path / "salida")

    assert len(rutas) == 1
    ruta_salida = rutas[0]
    assert "EDUCACION_CIVICA" in str(ruta_salida)

    # Es una copia completa: trae los dos grados, tal cual
    doc = Document(str(ruta_salida))
    assert len(doc.tables) == 2
    texto = "\n".join(c.text for t in doc.tables for row in t.rows for c in row.cells)
    assert "Buen ciudadano" in texto
    assert "Derechos humanos" in texto


def test_generar_tal_cual_ignora_archivos_no_docx(tmp_path):
    """Un PDF (o cualquier formato que no sea .docx) debe devolver []
    de inmediato, sin intentar abrirlo como Word, para que el llamador
    pueda usar la vía con IA."""
    ruta_pdf = tmp_path / "jornalizacion.pdf"
    ruta_pdf.write_bytes(b"%PDF-1.4 contenido falso")

    assert generar_tal_cual(ruta_pdf, tmp_path / "salida") == []


def test_generar_tal_cual_formato_no_reconocido(tmp_path):
    ruta = tmp_path / "otro.docx"
    doc = Document()
    doc.add_paragraph("Texto libre, sin tabla.")
    doc.save(str(ruta))

    rutas = generar_tal_cual(ruta, tmp_path / "salida")
    assert rutas == []


def test_detectar_parcial():
    assert detectar_parcial("Plan cívica II parcial, 7, 8, 9") == "II Parcial"
    assert detectar_parcial("jornalizacion parcial 3") == "3 Parcial"
    assert detectar_parcial("jornalizacion semana 10") == ""


def test_generar_tal_cual_organiza_por_parcial(tmp_path):
    ruta = tmp_path / "Plan civica II parcial.docx"
    _crear_documento_ejemplo(ruta)

    rutas = generar_tal_cual(ruta, tmp_path / "salida")

    assert len(rutas) == 1
    assert "II_Parcial" in str(rutas[0])
    assert "EDUCACION_CIVICA" in str(rutas[0])


def test_dividir_en_bloques_de_tabla_con_formato_distinto(tmp_path):
    """dividir_en_bloques_de_tabla debe funcionar con CUALQUIER tabla, no
    solo con las columnas de Cívica — ej. el formato Estándares/
    Contenidos/H-C/Fecha/Evaluación de una jornalización general."""
    ruta = tmp_path / "jornalizacion_general.docx"
    doc = Document()

    doc.add_paragraph("Espacio Pedagógico: Introducción a la economía   Curso: 11 BCH")
    tabla1 = doc.add_table(rows=2, cols=5)
    for i, texto in enumerate(["Estándares", "Contenidos", "H/C", "Fecha", "Evaluación"]):
        tabla1.cell(0, i).text = texto
    tabla1.cell(1, 0).text = "Comprender la economía."
    tabla1.cell(1, 1).text = "Introducción a la economía."
    tabla1.cell(1, 2).text = "2"
    tabla1.cell(1, 3).text = "20-24 de Abril"
    tabla1.cell(1, 4).text = "Participación en clase."

    doc.add_paragraph("Espacio Pedagógico: Educación cívica   Curso: 7mo grado")
    tabla2 = doc.add_table(rows=2, cols=5)
    for i, texto in enumerate(["Estándares", "Contenidos", "H/C", "Fecha", "Evaluación"]):
        tabla2.cell(0, i).text = texto
    tabla2.cell(1, 0).text = "Analizar la relación entre seres bióticos y abióticos."
    tabla2.cell(1, 1).text = "Seres bióticos y abióticos."
    tabla2.cell(1, 2).text = "3"
    tabla2.cell(1, 3).text = "20-24 de Abril"
    tabla2.cell(1, 4).text = "Elaboración de cuadros comparativos."

    doc.save(str(ruta))

    bloques = dividir_en_bloques_de_tabla(ruta)

    assert len(bloques) == 2
    assert "Introducción a la economía" in bloques[0]
    assert "Comprender la economía" in bloques[0]
    # El segundo bloque NO debe traer nada del primero (están bien separados)
    assert "economía" not in bloques[1].lower()
    assert "Educación cívica" in bloques[1]
    assert "Seres bióticos" in bloques[1]


def test_dividir_en_bloques_de_tabla_sin_tablas(tmp_path):
    ruta = tmp_path / "sin_tablas.docx"
    doc = Document()
    doc.add_paragraph("Texto libre, sin ninguna tabla.")
    doc.save(str(ruta))

    assert dividir_en_bloques_de_tabla(ruta) == []


def test_generar_tal_cual_conserva_encabezado_de_pagina(tmp_path):
    """El encabezado de página (header: logos, nombre de instituto) del
    documento original debe quedar igual en el cuadro generado (al ser una
    copia literal del archivo)."""
    ruta = tmp_path / "jornalizacion.docx"
    _crear_documento_ejemplo(ruta, con_header=True)

    rutas = generar_tal_cual(ruta, tmp_path / "salida")
    assert len(rutas) == 1

    doc = Document(str(rutas[0]))
    texto_header = "\n".join(p.text for p in doc.sections[0].header.paragraphs)
    assert "INSTITUTO DE PRUEBA" in texto_header
    assert "Planificación Parcial" in texto_header
