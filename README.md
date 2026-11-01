# Agente de jornalización

Convierte la **jornalización de un parcial** en **un solo documento final**,
con el mismo diseño exacto (logos, encabezado del instituto). La IA (Claude)
solo entra como respaldo, cuando el documento no viene ya en el formato de
tabla que usa el instituto.

```
entrada/jornalizacion.docx → ¿trae el formato de tabla estándar?
                                 │
                    sí ─────────┼───────── no
                     │                      │
            se copia tal cual      extractor (IA) → revision/*.json
            (gratis, instantáneo)              ↓ (se revisa)
                     │               plantilla_oficial.docx → llenador
                     └──────────┬───────────────┘
                                ▼
                 salida/<Asignatura>/<Parcial>.docx   (un solo archivo)
```

## Estructura

```
Proyecto-AgentD/
├── app.py                  # interfaz web (streamlit run app.py)
├── main.py                 # comandos de la terminal
├── requirements.txt        # dependencias
├── .env.example             # copiar a .env y poner la clave
├── entrada/                 # el docente deja aquí la jornalización
├── plantillas/
│   └── plantilla_oficial.docx  # encabezado real (logos), cuerpo vacío —
│                                 # base para la vía con IA
├── revision/                # JSON intermedio para revisar antes de generar
├── salida/                  # <Asignatura>/<Parcial>.docx (un archivo final)
├── src/
│   ├── config.py                    # rutas y modelo
│   ├── esquema.py                   # campos (Jornalizacion, PlanGrado, BloqueSemana)
│   ├── nombres.py                   # detectar el parcial, limpiar nombres
│   ├── generador_tal_cual.py        # vía principal (copia el documento, sin IA)
│   ├── extractor.py                 # ÚNICA pieza que usa la IA
│   ├── llenador.py                  # arma el documento final (vía IA)
│   ├── agente.py                    # une todo el flujo
│   ├── lectores/                    # docx / xlsx / pdf → texto, y el
│   │   └── jornalizacion_tabla.py   # detector/lector del formato de tabla
│   └── prompts/                     # instrucciones de la IA (editables)
└── tests/
```

## Instalación

```powershell
# 1. (recomendado) crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. instalar dependencias
pip install -r requirements.txt

# 3. configurar la clave de la API (solo hace falta para la vía con IA)
copy .env.example .env
# luego edita .env y pon tu ANTHROPIC_API_KEY
```

La clave se obtiene en https://console.anthropic.com (se paga por uso, aparte de
cualquier suscripción de Claude.ai). Conviene poner un límite de gasto mensual
en la consola.

## Uso — interfaz web (recomendado para el día a día)

```powershell
streamlit run app.py
```

Abre `http://localhost:8501` en el navegador. Ahí se sube la jornalización
(`.docx`), se procesa con un clic y se descarga el documento final. No hace
falta usar la terminal para nada más.

## Uso — línea de comandos

```powershell
# Vía principal (sin IA, gratis): si el documento ya trae el formato de
# tabla estándar, lo copia tal cual a salida/
python main.py dividir entrada\jornalizacion.docx

# Hace lo mismo, y si el formato no se reconoce, usa IA automáticamente
python main.py todo entrada\jornalizacion.docx
```

Si el documento viene en texto libre (sin esa tabla), se puede forzar la
vía con IA, con un paso de revisión manual antes de generar:

```powershell
python main.py extraer entrada\jornalizacion.docx   # -> revision\jornalizacion.json
#  (revisar/corregir el JSON si hace falta)
python main.py generar revision\jornalizacion.json  # -> salida\...
```

## El formato esperado

El programa reconoce automáticamente una jornalización con estas columnas
(cada fila es una semana):

| Expectativas de logro | Tema | Actividades Generales | Fecha de ejecución | Recursos | Evaluación |
|---|---|---|---|---|---|

El documento puede traer una tabla así por cada grado. Si la trae, el
resultado es **un solo archivo, copiado tal cual** del original (mismo
formato, fuente, viñetas) — sin usar la IA, y 100% idéntico (se verificó
byte a byte). Si el documento no tiene ese formato, se usa la IA para
extraer los datos y armar un documento con la misma estructura, a partir
de [plantillas/plantilla_oficial.docx](plantillas/plantilla_oficial.docx).
Por esta vía se admite `.docx`, `.xlsx`/`.xlsm` y `.pdf`.

Si el documento trae **varias asignaturas** (ej. una jornalización general
con un espacio pedagógico por materia), cada asignatura sale en su propio
archivo — todos los grados de una misma asignatura se juntan en uno solo
(`salida/<Asignatura>/<Parcial>.docx`), sin mezclarse con otras materias.
Para documentos `.docx` con varias tablas, la IA se llama **una vez por
tabla/asignatura** (no todo el documento de un tirón), así la respuesta
nunca se corta sin importar cuántas materias traiga el documento.

### Reglas de negocio de los campos que no vienen en el documento

- **Recursos**: si el documento no especifica recursos para una semana, se
  usa siempre el mismo texto estándar del instituto
  (`config.RECURSOS_POR_DEFECTO`) — nunca lo inventa la IA.
- **Actividades Generales**: si no viene explícita, la IA sugiere una
  actividad acorde al tema, marcada con el prefijo `[Sugerido]` para que
  quede claro que no vino del documento original.

### El diseño sale idéntico (logos, encabezado del instituto)

La vía sin IA simplemente copia el archivo: es la forma más simple de
garantizar que el diseño (logos, encabezado, estilos) quede exactamente
igual. La vía con IA usa la misma plantilla oficial como base (conserva su
encabezado de página con los logos) y solo construye el cuerpo.

### Carpeta de salida

```
salida/<Asignatura>/<Parcial>.docx
```

El "Parcial" (I, II, III, IV) se detecta automáticamente del nombre del
archivo de entrada (por ejemplo, "... II parcial ..." -> `II_Parcial.docx`).
Si no se encuentra, se usa el nombre del archivo original.

## Cambiar de modelo

En `.env`, la variable `MODELO_CLAUDE` controla qué modelo se usa (solo
aplica a la vía con IA):

- `claude-haiku-5-5` — el más barato
- `claude-sonnet-5-5` — equilibrio (por defecto)
- `claude-opus-5-5` — el más capaz

## Pruebas

```powershell
pytest
```

Las pruebas incluidas no consumen la API (usan datos y plantillas de prueba).
