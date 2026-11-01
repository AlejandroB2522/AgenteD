"""Prueba del llenador (vía IA, respaldo). No necesita la API ni clave:
usa datos ya extraídos a mano, y una plantilla oficial de prueba (no la
real del proyecto) para no depender de un archivo externo.
"""

from docx import Document

from src import config
from src.esquema import BloqueSemana, Jornalizacion, PlanGrado
from src.llenador import generar_plan


def _crear_plantilla_oficial_de_prueba(ruta):
    """Una plantilla mínima con encabezado (header), como la real."""
    doc = Document()
    doc.sections[0].header.paragraphs[0].text = "INSTITUTO DE PRUEBA"
    doc.save(str(ruta))


def test_generar_plan_un_solo_archivo(tmp_path, monkeypatch):
    plantilla = tmp_path / "plantilla_oficial.docx"
    _crear_plantilla_oficial_de_prueba(plantilla)
    monkeypatch.setattr(config, "PLANTILLA_OFICIAL", plantilla)

    jornalizacion = Jornalizacion(
        grados=[
            PlanGrado(
                asignatura="Educación Cívica",
                docente="Ana",
                nivel="Educación Básica",
                grado="Octavo",
                duracion="2 H/C",
                bloques=[
                    BloqueSemana(
                        expectativas_logro="Identificar valores cívicos.",
                        tema="¿Qué significa ser un buen ciudadano?",
                        actividades="Lluvia de ideas",
                        fecha_ejecucion="04-08 de Mayo",
                        recursos="Pizarra",
                        evaluacion="Participación",
                    )
                ],
            ),
            PlanGrado(
                asignatura="Educación Cívica",
                docente="Ana",
                nivel="Educación Básica",
                grado="Noveno",
                duracion="2 H/C",
                bloques=[
                    BloqueSemana(
                        expectativas_logro="Reconocer derechos.",
                        tema="Derechos humanos",
                        actividades="Análisis de casos",
                        fecha_ejecucion="04-08 de Mayo",
                        recursos="Libro",
                        evaluacion="Trabajo escrito",
                    )
                ],
            ),
        ]
    )

    rutas = generar_plan(jornalizacion, "Plan civica II parcial", tmp_path / "salida")

    # Un solo archivo, con los dos grados dentro
    assert len(rutas) == 1
    assert "II_Parcial" in str(rutas[0])

    doc = Document(str(rutas[0]))
    # El encabezado (header) de la plantilla oficial se conserva
    assert "INSTITUTO DE PRUEBA" in doc.sections[0].header.paragraphs[0].text
    # Dos tablas: una por grado
    assert len(doc.tables) == 2
    texto = "\n".join(p.text for p in doc.paragraphs) + "\n".join(
        c.text for t in doc.tables for row in t.rows for c in row.cells
    )
    assert "Octavo" in texto
    assert "Noveno" in texto
    assert "buen ciudadano" in texto
    assert "Derechos humanos" in texto

    # El encabezado de cada grado usa el estilo real del instituto:
    # etiqueta en negrita, valor subrayado (como si estuviera escrito
    # sobre la línea de un formulario) — no solo guiones bajos sueltos.
    p1 = doc.paragraphs[0]
    assert "Asignatura: Educación Cívica" in p1.text
    run_etiqueta = next(r for r in p1.runs if r.text == "Asignatura: ")
    run_valor = next(r for r in p1.runs if r.text.startswith("Educación Cívica"))
    assert run_etiqueta.bold is True
    assert run_valor.underline is True
    assert "_" in run_valor.text  # relleno de la línea después del valor


def test_generar_plan_separa_por_asignatura(tmp_path, monkeypatch):
    """Si la jornalización trae varias ASIGNATURAS distintas (ej. una
    jornalización general con Economía, Biología, Cívica...), cada una
    debe salir en su propio archivo -- no se deben mezclar en uno solo.
    """
    plantilla = tmp_path / "plantilla_oficial.docx"
    _crear_plantilla_oficial_de_prueba(plantilla)
    monkeypatch.setattr(config, "PLANTILLA_OFICIAL", plantilla)

    jornalizacion = Jornalizacion(
        grados=[
            PlanGrado(
                asignatura="Introducción a la economía",
                docente="Ana",
                nivel="Educación Media",
                grado="11 BCH",
                bloques=[
                    BloqueSemana(tema="Necesidades y recursos", fecha_ejecucion="20-24 de Abril")
                ],
            ),
            PlanGrado(
                asignatura="Educación cívica",
                docente="Ana",
                nivel="Educación Básica",
                grado="7mo grado",
                bloques=[
                    BloqueSemana(tema="Buen ciudadano", fecha_ejecucion="20-24 de Abril")
                ],
            ),
        ]
    )

    rutas = generar_plan(jornalizacion, "Jornalizacion de clases ICET, II PARCIAL", tmp_path / "salida")

    assert len(rutas) == 2
    assert any("economía" in str(r) for r in rutas)
    assert any("cívica" in str(r) for r in rutas)

    # Cada archivo trae solo SU asignatura, no las dos mezcladas
    for ruta in rutas:
        doc = Document(str(ruta))
        assert len(doc.tables) == 1


def test_generar_plan_agrupa_aunque_cambien_tildes(tmp_path, monkeypatch):
    """La IA no siempre escribe la misma asignatura con las mismas tildes
    entre un bloque y otro (ej. 'Biologia' en un grado y 'Biología' en
    otro, del mismo documento) -- deben quedar en el MISMO archivo, no
    partirse en dos por una diferencia de tildes/mayúsculas."""
    plantilla = tmp_path / "plantilla_oficial.docx"
    _crear_plantilla_oficial_de_prueba(plantilla)
    monkeypatch.setattr(config, "PLANTILLA_OFICIAL", plantilla)

    jornalizacion = Jornalizacion(
        grados=[
            PlanGrado(
                asignatura="Biologia",
                grado="8vo",
                bloques=[BloqueSemana(tema="Célula", fecha_ejecucion="20-24 de Abril")],
            ),
            PlanGrado(
                asignatura="Biología",
                grado="9no",
                bloques=[BloqueSemana(tema="Genética", fecha_ejecucion="20-24 de Abril")],
            ),
        ]
    )

    rutas = generar_plan(jornalizacion, "Jornalizacion II PARCIAL", tmp_path / "salida")

    assert len(rutas) == 1
    doc = Document(str(rutas[0]))
    assert len(doc.tables) == 2
