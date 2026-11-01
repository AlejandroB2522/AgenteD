"""Punto de entrada por línea de comandos.

En ambas vías el resultado es UN solo archivo por jornalización (parcial),
guardado en salida/<Asignatura>/<Parcial>.docx.

Uso:
    python main.py dividir entrada/jornalizacion.docx
        -> vía principal (sin IA, gratis): si el documento ya trae el
           formato de tabla estándar, lo copia tal cual a salida/.

    python main.py todo entrada/jornalizacion.docx
        -> intenta "dividir" primero; si el formato no se reconoce, usa
           IA automáticamente (sin pausa de revisión manual).

    python main.py extraer entrada/jornalizacion.docx
        -> fuerza la vía con IA: lee -> guarda un JSON en revision/ para
           revisar a mano. Útil solo si el documento viene en texto libre.

    python main.py generar revision/jornalizacion.json
        -> JSON ya revisado -> documento final en salida/ (vía con IA).
"""

import argparse

from src import agente, config
from src.generador_tal_cual import generar_tal_cual


def main():
    parser = argparse.ArgumentParser(
        description="Convierte la jornalización en un cuadro final por parcial."
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_div = sub.add_parser(
        "dividir",
        help="Sin IA: copia el documento tal cual (requiere formato de tabla estándar)",
    )
    p_div.add_argument("archivo", help="Ruta de la jornalización (.docx)")

    p_todo = sub.add_parser(
        "todo", help="Igual que 'dividir'; si no reconoce el formato, usa IA automáticamente"
    )
    p_todo.add_argument("archivo", help="Ruta de la jornalización (.docx, .xlsx o .pdf)")

    p_ext = sub.add_parser(
        "extraer", help="Fuerza la vía con IA: guarda un JSON en revision/ para revisar"
    )
    p_ext.add_argument("archivo", help="Ruta de la jornalización (.docx, .xlsx o .pdf)")

    p_gen = sub.add_parser(
        "generar", help="Genera el documento final desde un JSON ya revisado (vía IA)"
    )
    p_gen.add_argument("json", help="Ruta del JSON ya revisado")

    args = parser.parse_args()

    if args.comando == "dividir":
        rutas = generar_tal_cual(args.archivo, config.DIR_SALIDA)
        if not rutas:
            print(
                "No se reconoció el formato de tabla estándar en ese documento.\n"
                "Prueba con:  python main.py todo " + args.archivo
            )
            return
        for ruta in rutas:
            print(f"Generado: {ruta}")

    elif args.comando == "todo":
        rutas, metodo = agente.procesar(args.archivo)
        etiqueta = "sin IA (copiado tal cual)" if metodo == "tabla" else "con IA"
        print(f"Procesado {etiqueta}:")
        for ruta in rutas:
            print(f"Generado: {ruta}")

    elif args.comando == "extraer":
        ruta_json, _ = agente.extraer_a_revision(args.archivo)
        print(f"Datos extraidos -> {ruta_json}")
        print("Revisa y corrige ese archivo, luego:")
        print(f"    python main.py generar {ruta_json}")

    elif args.comando == "generar":
        rutas = agente.generar_desde_revision(args.json)
        for ruta in rutas:
            print(f"Generado: {ruta}")


if __name__ == "__main__":
    main()
