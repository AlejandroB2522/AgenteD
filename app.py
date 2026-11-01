"""Interfaz web local (Streamlit): subir la jornalización y descargar el
cuadro final, sin usar la terminal.

Ejecutar con:
    streamlit run app.py

Abre http://localhost:8501 en el navegador.
"""

import time
from datetime import date, datetime

import streamlit as st

from src import agente, config

st.set_page_config(
    page_title="Jornalización Mágica",
    page_icon=":material/auto_awesome:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def icono(nombre: str, tamano: str = "1em") -> str:
    """HTML de un ícono Material Symbols (sirve dentro de HTML propio,
    a diferencia de la sintaxis ':material/nombre:' de Streamlit, que solo
    funciona en texto markdown plano, no dentro de <div>/<span> propios)."""
    return (
        f'<span class="jd-icono" style="font-size:{tamano}">{nombre}</span>'
    )


# ---------------------------------------------------------------------
# Estilo: tema oscuro, moderno, con gradientes y tarjetas de vidrio.
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,350,0,0&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Ícono Material como fuente real: funciona dentro de HTML propio */
    .jd-icono {
        font-family: 'Material Symbols Rounded';
        font-weight: normal;
        font-style: normal;
        line-height: 1;
        display: inline-block;
        vertical-align: -0.15em;
        font-variation-settings: 'FILL' 0, 'wght' 350, 'GRAD' 0, 'opsz' 24;
    }
    /* Íconos nativos de Streamlit (botones, alertas): mismo trazo fino */
    span[data-testid="stIconMaterial"] {
        font-variation-settings: 'FILL' 0, 'wght' 350, 'GRAD' 0, 'opsz' 24;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(124, 58, 237, 0.25), transparent 45%),
            radial-gradient(circle at 90% 10%, rgba(13, 148, 136, 0.22), transparent 40%),
            #0b1020;
    }

    #MainMenu, footer, header[data-testid="stHeader"] { background: transparent; }
    /* El menú "Deploy"/⋮ de Streamlit no aplica a una app local: se oculta
       para que se sienta como una app propia, no como un editor de Streamlit. */
    [data-testid="stToolbar"] { display: none; }

    /* ---- Pasos ("Cómo funciona") ---- */
    .jd-paso-numero {
        display: inline-flex; align-items: center; justify-content: center;
        width: 2rem; height: 2rem; border-radius: 999px;
        background: linear-gradient(135deg, #4f46e5, #0d9488);
        color: white; font-weight: 800; font-size: 0.95rem;
        margin-bottom: 0.7rem;
    }
    .jd-paso h4 { margin: 0 0 0.3rem 0; color: #f1f5f9; }
    .jd-paso p { margin: 0; color: #94a3b8; font-size: 0.88rem; line-height: 1.4; }

    /* ---- Héroe ---- */
    .jd-hero {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 45%, #0d9488 100%);
        border-radius: 28px;
        padding: 2.6rem 2.6rem;
        margin-bottom: 1.6rem;
        color: white;
        box-shadow: 0 24px 48px -16px rgba(79, 70, 229, 0.45);
        position: relative;
        overflow: hidden;
    }
    .jd-hero::after {
        content: "";
        position: absolute; inset: 0;
        background: radial-gradient(circle at 85% 20%, rgba(255,255,255,0.18), transparent 60%);
    }
    .jd-hero h1 {
        font-size: 2.3rem; font-weight: 800; margin: 0 0 .4rem 0;
        letter-spacing: -0.02em;
        display: flex; align-items: center; gap: 0.6rem;
    }
    .jd-hero h1 .jd-icono { font-size: 2rem; }
    .jd-hero p { font-size: 1.05rem; opacity: 0.93; margin: 0; max-width: 640px; }

    /* ---- Tarjetas: contenedores nativos st.container(border=True), ---- */
    /* ---- estilizados como vidrio oscuro (NO blanco) ---- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.55) !important;
        backdrop-filter: blur(10px);
        border-radius: 22px !important;
        box-shadow: 0 10px 30px -12px rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        margin-bottom: 1.4rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { padding: 1.8rem 2rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] h3,
    div[data-testid="stVerticalBlockBorderWrapper"] h4 { margin-top: 0; color: #f1f5f9; }

    /* ---- Zona de arrastrar archivo (oscura, no blanca) ---- */
    [data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(180deg, rgba(30,41,59,0.7), rgba(15,23,42,0.7)) !important;
        border: 2px dashed #7c3aed !important;
        border-radius: 18px !important;
    }
    [data-testid="stFileUploaderDropzone"] section { background: transparent !important; }

    /* ---- Botones ---- */
    .stButton > button, [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #4f46e5, #0d9488) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 20px -8px rgba(79, 70, 229, 0.55);
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .stButton > button:hover, [data-testid="stDownloadButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 24px -6px rgba(79, 70, 229, 0.6);
    }
    .stButton > button:disabled {
        background: #334155 !important; box-shadow: none; color: #94a3b8 !important;
    }

    /* ---- Insignias ---- */
    .jd-pill {
        display: inline-flex; align-items: center; gap: 0.35rem;
        padding: 0.3rem 0.9rem; border-radius: 999px;
        font-size: 0.82rem; font-weight: 700; margin-right: .4rem;
    }
    .jd-pill-fast { background: #ccfbf1; color: #0f766e; }
    .jd-pill-ia { background: #ede9fe; color: #6d28d9; }
    .jd-pill-new { background: #4f46e5; color: white; font-size: 0.65rem; padding: 0.15rem 0.6rem; }

    /* ---- Historial (sidebar) ---- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] [data-testid="stDownloadButton"] button {
        width: 100%; padding: 0.4rem 0.8rem !important; font-size: 0.82rem !important;
    }
    .jd-hist-fecha {
        display: flex; align-items: center; gap: 0.4rem;
        font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em;
        color: #94a3b8 !important; margin: 1.1rem 0 0.4rem 0; font-weight: 700;
    }
    .jd-hist-item {
        background: rgba(255,255,255,0.06); border-radius: 12px;
        padding: 0.6rem 0.8rem; margin-bottom: 0.4rem;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .jd-hist-item strong { font-size: 0.9rem; }
    .jd-hist-item small {
        color: #94a3b8 !important; display: inline-flex; align-items: center; gap: 0.3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Historial: carpetas de salida agrupadas por fecha
# ---------------------------------------------------------------------
MESES = [
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
]


def _etiqueta_fecha(mtime: float) -> str:
    dt = date.fromtimestamp(mtime)
    hoy = date.today()
    diferencia = (hoy - dt).days
    if diferencia == 0:
        return "Hoy"
    if diferencia == 1:
        return "Ayer"
    return f"{dt.day} de {MESES[dt.month - 1]} {dt.year}"


def _listar_historial():
    """Todos los cuadros generados, más reciente primero."""
    if not config.DIR_SALIDA.exists():
        return []
    archivos = [
        ruta for ruta in config.DIR_SALIDA.rglob("*.docx")
        if not ruta.name.startswith("~$")
    ]
    archivos.sort(key=lambda r: r.stat().st_mtime, reverse=True)
    return archivos


with st.sidebar:
    st.markdown(f"## {icono('history')} Historial", unsafe_allow_html=True)
    st.caption("Cuadros generados, por fecha")

    historial = _listar_historial()
    if not historial:
        st.info("Todavía no se ha generado ningún cuadro. ¡El primero queda aquí!", icon=":material/inbox:")
    else:
        fecha_mostrada = None
        for i, ruta in enumerate(historial):
            mtime = ruta.stat().st_mtime
            etiqueta = _etiqueta_fecha(mtime)
            if etiqueta != fecha_mostrada:
                st.markdown(
                    f'<div class="jd-hist-fecha">{icono("calendar_month")} {etiqueta}</div>',
                    unsafe_allow_html=True,
                )
                fecha_mostrada = etiqueta

            asignatura = ruta.parent.name.replace("_", " ")
            parcial = ruta.stem.replace("_", " ")
            hora = datetime.fromtimestamp(mtime).strftime("%H:%M")
            insignia = ' <span class="jd-pill jd-pill-new">ACTUAL</span>' if i == 0 else ""

            st.markdown(
                f'<div class="jd-hist-item">'
                f'<strong>{parcial}</strong>{insignia}<br>'
                f'<small>{icono("book_2")} {asignatura} · {icono("schedule")} {hora}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.download_button(
                "Descargar",
                data=ruta.read_bytes(),
                file_name=ruta.name,
                key=f"hist_{ruta}",
                icon=":material/download:",
            )


# ---------------------------------------------------------------------
# Héroe
# ---------------------------------------------------------------------
st.markdown(
    f"""
    <div class="jd-hero">
        <h1>{icono('auto_awesome', '2rem')} Jornalización Mágica</h1>
        <p>Sube tu jornalización y en segundos obtén el cuadro final del
        parcial — con el mismo diseño del instituto, logos incluidos.
        Acepta Word, PDF y Excel.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Cómo funciona (3 pasos)
# ---------------------------------------------------------------------
PASOS = [
    ("upload_file", "1. Sube", "Arrastra tu jornalización — Word, PDF o Excel."),
    ("bolt", "2. Se procesa", "Sin IA si ya trae el formato de tabla; con IA si no."),
    ("download", "3. Descarga", "El cuadro final, con el mismo diseño del instituto."),
]
col_p1, col_p2, col_p3 = st.columns(3)
for columna, (nombre_icono, titulo, descripcion) in zip((col_p1, col_p2, col_p3), PASOS):
    with columna:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="jd-paso">
                    <div class="jd-paso-numero">{icono(nombre_icono, "1.1rem")}</div>
                    <h4>{titulo}</h4>
                    <p>{descripcion}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------
# Tarjeta: subir y generar
# ---------------------------------------------------------------------
with st.container(border=True):
    st.markdown(f"### {icono('upload_file')} Sube tu jornalización", unsafe_allow_html=True)

    col_subida, col_boton = st.columns([3, 1], vertical_alignment="bottom")
    with col_subida:
        archivo_subido = st.file_uploader(
            "Arrastra el archivo aquí, o haz clic para elegirlo",
            type=["docx", "pdf", "xlsx"],
            label_visibility="collapsed",
        )
    with col_boton:
        generar = st.button(
            "Generar cuadro",
            type="primary",
            use_container_width=True,
            disabled=archivo_subido is None,
            icon=":material/bolt:",
        )

# ---------------------------------------------------------------------
# Procesar y mostrar resultado
# ---------------------------------------------------------------------
# El resultado se guarda en session_state (no solo en variables locales)
# para poder hacer un st.rerun() tras generar: así el Historial del
# sidebar —que ya se dibujó más arriba, antes de que este archivo
# existiera— se refresca y muestra el cuadro recién creado, en vez de
# quedarse con la lista vieja hasta la siguiente interacción.
if "resultado" not in st.session_state:
    st.session_state.resultado = None

if archivo_subido is not None and generar:
    config.DIR_ENTRADA.mkdir(parents=True, exist_ok=True)
    ruta_entrada = config.DIR_ENTRADA / archivo_subido.name
    ruta_entrada.write_bytes(archivo_subido.getvalue())

    rutas, metodo, hubo_error = [], None, False
    with st.spinner("Leyendo tu jornalización y armando el cuadro..."):
        # OneDrive (u otro antivirus/indexador) puede bloquear el archivo un
        # instante justo después de escribirlo; un par de reintentos cortos
        # evitan un error falso por esa carrera.
        for intento in range(3):
            try:
                rutas, metodo = agente.procesar(ruta_entrada)
                break
            except PermissionError:
                if intento == 2:
                    st.error(
                        "No se pudo escribir el archivo de salida: probablemente "
                        "lo tienes abierto en Word (o Excel). Ciérralo y vuelve "
                        "a intentar.",
                        icon=":material/error:",
                    )
                    hubo_error = True
                else:
                    time.sleep(0.6)
            except Exception as error:
                st.error(f"Ocurrió un error al procesar el documento: {error}", icon=":material/error:")
                hubo_error = True
                break

    if hubo_error:
        st.session_state.resultado = None
    elif not rutas:
        st.session_state.resultado = None
        st.warning(
            "No se reconoció el formato esperado. Revisa que traiga las "
            "columnas: Expectativas de logro / Tema / Actividades / "
            "Fecha de ejecución / Recursos / Evaluación.",
            icon=":material/warning:",
        )
    else:
        st.session_state.resultado = (rutas, metodo)
        st.session_state.festejar = True
        st.rerun()

if st.session_state.resultado:
    rutas, metodo = st.session_state.resultado
    if st.session_state.pop("festejar", False):
        st.balloons()

    with st.container(border=True):
        if metodo == "tabla":
            st.markdown(
                f'<span class="jd-pill jd-pill-fast">{icono("bolt")} Sin IA · copiado tal cual</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<span class="jd-pill jd-pill-ia">{icono("smart_toy")} Generado con IA</span>',
                unsafe_allow_html=True,
            )

        st.markdown(f"#### {icono('task_alt')} ¡Tu cuadro está listo!", unsafe_allow_html=True)

        for ruta in rutas:
            asignatura = ruta.parent.name.replace("_", " ")
            parcial = ruta.stem.replace("_", " ")
            st.markdown(
                f"{icono('book_2')} **{asignatura}**  ·  {icono('calendar_month')} **{parcial}**",
                unsafe_allow_html=True,
            )
            st.download_button(
                f"Descargar {ruta.name}",
                data=ruta.read_bytes(),
                file_name=ruta.name,
                key=f"out_{ruta}",
                icon=":material/download:",
            )
            st.caption(f"También queda guardado en `{ruta}`")
