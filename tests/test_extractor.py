"""Pruebas de las funciones puras de extractor.py (no necesitan la API ni
clave: no llaman a Claude)."""

from src import config
from src.esquema import BloqueSemana, PlanGrado
from src.extractor import _aplicar_recursos_por_defecto_grado, _dividir_si_es_docx


def test_aplica_recursos_por_defecto_si_falta():
    grado = PlanGrado(
        asignatura="Introducción a la economía",
        bloques=[
            BloqueSemana(tema="Economía", recursos=""),  # sin recursos
        ],
    )

    resultado = _aplicar_recursos_por_defecto_grado(grado)

    assert resultado.bloques[0].recursos == config.RECURSOS_POR_DEFECTO


def test_no_sobrescribe_recursos_que_ya_traia_el_documento():
    grado = PlanGrado(
        asignatura="Educación Cívica",
        bloques=[
            BloqueSemana(tema="Cívica", recursos="Declaración Universal impresa"),
        ],
    )

    resultado = _aplicar_recursos_por_defecto_grado(grado)

    assert resultado.bloques[0].recursos == "Declaración Universal impresa"


def test_dividir_si_es_docx_ignora_formatos_no_docx(tmp_path):
    ruta_pdf = tmp_path / "jornalizacion.pdf"
    ruta_pdf.write_bytes(b"%PDF-1.4 contenido falso")

    assert _dividir_si_es_docx(ruta_pdf) == []


def test_dividir_si_es_docx_sin_ruta():
    assert _dividir_si_es_docx(None) == []
