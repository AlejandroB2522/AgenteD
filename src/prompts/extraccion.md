A partir de la jornalización que viene a continuación, extrae una lista de
grados. Por cada grado, extrae:

Datos generales:
- asignatura
- docente
- nivel
- grado
- duracion

Y, por cada semana de clase (bloque), un registro con:
- expectativas_logro
- tema
- actividades (puedes conservar las viñetas o separarlas con saltos de línea)
- fecha_ejecucion (tal como aparece, por ejemplo "04-08 de Mayo")
- recursos
- evaluacion

La salida SIEMPRE usa estos nombres de campo, sin importar cómo los llame
el documento de entrada. Si el documento trae sus propias etiquetas, usa
esta equivalencia:

- "Espacio Pedagógico" -> asignatura
- "Profesor" -> docente
- "Modalidad" (ej. "Educación Media", "Educación Básica") -> nivel
- "Curso" -> grado
- "Estándares" -> expectativas_logro
- "Contenidos" -> tema
- "Fecha" / "Fecha de ejecución" -> fecha_ejecucion
- "Evaluación" -> evaluacion

Campos del documento sin equivalente claro arriba (por ejemplo "H/C",
"Área curricular", "Jornada", "Parcial") NO los inventes ni los fuerces en
otro campo: ignóralos. Si "recursos" no aparece explícito en el
documento, usa cadena vacía — no lo inventes a partir de otros campos ni
mezcles contenido de un campo en otro.

Caso especial de "actividades": si el documento NO trae "Actividades
Generales" como campo explícito, propone TÚ una actividad de clase
concreta y realizable para ese bloque, basándote en el tema, las
expectativas de logro y la evaluación de esa semana (ej. "Debate guiado
sobre...", "Elaboración de un mapa conceptual sobre..."). No sea una
frase genérica ni repitas literalmente el tema. Como es una sugerencia
tuya y no algo que el docente escribió, antepón siempre "[Sugerido] " al
texto de esa actividad, para que quede claro que debe revisarla. Si el
documento SÍ trae actividades explícitas, extráelas tal cual, sin el
prefijo "[Sugerido]".

Si algún dato no está en el documento, usa cadena vacía. No agregues
semanas ni grados que no estén en la jornalización.
