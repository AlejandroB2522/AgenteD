"""Estructura de los datos de la jornalización.

Columnas basadas en el formato real del docente: Expectativas de logro,
Tema, Actividades Generales, Fecha de ejecución, Recursos, Evaluación.

Cada fila de la jornalización es una SEMANA (un bloque), no un día: el
cuadro de salida se genera uno por cada fila, tal cual viene.
"""

from typing import List

from pydantic import BaseModel, Field


class BloqueSemana(BaseModel):
    """Una fila de la jornalización: lo que corresponde a un cuadro de salida."""

    expectativas_logro: str = Field(default="", description="Expectativas de logro / objetivo")
    tema: str = Field(default="", description="Tema de la semana")
    actividades: str = Field(default="", description="Actividades generales (pueden venir en viñetas)")
    fecha_ejecucion: str = Field(default="", description="Fecha o rango de fechas de ejecución")
    recursos: str = Field(default="", description="Recursos y materiales")
    evaluacion: str = Field(default="", description="Forma de evaluación")


class PlanGrado(BaseModel):
    """Jornalización de un grado: datos generales + sus bloques semanales."""

    asignatura: str = Field(default="", description="Asignatura o materia")
    docente: str = Field(default="", description="Nombre del docente")
    nivel: str = Field(default="", description="Nivel educativo")
    grado: str = Field(default="", description="Grado o sección")
    duracion: str = Field(default="", description="Duración / horas clase por semana")
    bloques: List[BloqueSemana] = Field(default_factory=list)


class Jornalizacion(BaseModel):
    """El documento completo: puede traer uno o varios grados."""

    grados: List[PlanGrado] = Field(default_factory=list)
