#!/usr/bin/env python3
"""Copia una revisión ya descargada a la carpeta que sirve Miku.

No descarga nada. No toca el modelo Live2D ni Cubism Core: si ya están en el
destino, se conservan tal cual. Si la copia falla, el destino anterior sigue.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys

FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}\.json$")
SALTAR_DIRS = {"live2d", "cubism", ".git"}
SALTAR_ARCHIVOS = {"live2dcubismcore.min.js", "live2dcubismcore.js"}


def huella(ruta: str) -> str:
    digest = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def ignorar(directorio: str, nombres: list[str]) -> set[str]:
    salto: set[str] = set()
    for nombre in nombres:
        if nombre in SALTAR_DIRS or nombre in SALTAR_ARCHIVOS or nombre.endswith(".moc3"):
            salto.add(nombre)
    return salto


def copiar_arbol(origen: str, destino: str) -> None:
    shutil.copytree(origen, destino, ignore=ignorar, dirs_exist_ok=True, copy_function=shutil.copy2)


def escribir_manifiesto(carpeta: str) -> list[str]:
    os.makedirs(carpeta, exist_ok=True)
    nombres = sorted(nombre for nombre in os.listdir(carpeta) if FECHA.fullmatch(nombre))
    validos: list[str] = []
    for nombre in nombres:
        ruta = os.path.join(carpeta, nombre)
        try:
            with open(ruta, encoding="utf-8") as archivo:
                dato = json.load(archivo)
        except (OSError, json.JSONDecodeError):
            print(f"Ignoro {nombre}: no es JSON.", file=sys.stderr)
            continue
        if not isinstance(dato, dict) or not isinstance(dato.get("fecha"), str):
            print(f"Ignoro {nombre}: falta fecha.", file=sys.stderr)
            continue
        validos.append(nombre)
    manifiesto = os.path.join(carpeta, "manifiesto.json")
    with open(manifiesto, "w", encoding="utf-8") as archivo:
        json.dump({"paquetes": validos}, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")
    return validos


def refrescar_dias(origen_repo: str, destino: str) -> None:
    fuente = os.path.join(origen_repo, "contenido", "dias")
    if not os.path.isdir(fuente):
        return
    nueva = destino + ".dias-nueva"
    previa = destino + ".dias-previa"
    shutil.rmtree(nueva, ignore_errors=True)
    shutil.copytree(fuente, nueva, ignore=ignorar, copy_function=shutil.copy2)
    manifiesto_viejo = os.path.join(nueva, "manifiesto.json")
    if os.path.exists(manifiesto_viejo):
        os.remove(manifiesto_viejo)
    escribir_manifiesto(nueva)
    if os.path.isdir(previa) and not os.path.isdir(destino):
        os.rename(previa, destino)
    elif os.path.isdir(previa):
        shutil.rmtree(previa)
    try:
        if os.path.isdir(destino):
            os.rename(destino, previa)
        os.rename(nueva, destino)
    except OSError:
        if not os.path.isdir(destino) and os.path.isdir(previa):
            os.rename(previa, destino)
        shutil.rmtree(nueva, ignore_errors=True)
        raise
    shutil.rmtree(previa, ignore_errors=True)


def refrescar_carpeta(origen_repo: str, destino: str, nombre: str) -> None:
    """Copia contenido/<nombre> a <destino>/<nombre> de forma atómica (frases, accesorios)."""
    fuente = os.path.join(origen_repo, "contenido", nombre)
    if not os.path.isdir(fuente):
        return
    final = os.path.join(destino, nombre)
    nueva = final + ".nueva"
    previa = final + ".previa"
    shutil.rmtree(nueva, ignore_errors=True)
    shutil.copytree(fuente, nueva, ignore=ignorar, copy_function=shutil.copy2)
    shutil.rmtree(previa, ignore_errors=True)
    try:
        if os.path.isdir(final):
            os.rename(final, previa)
        os.rename(nueva, final)
    except OSError:
        if not os.path.isdir(final) and os.path.isdir(previa):
            os.rename(previa, final)
        shutil.rmtree(nueva, ignore_errors=True)
        raise
    shutil.rmtree(previa, ignore_errors=True)


def instalar_app(origen_repo: str, destino: str) -> bool:
    app = os.path.join(origen_repo, "app")
    if not os.path.isfile(os.path.join(app, "index.html")):
        return False
    version_nueva = os.path.join(app, "version.txt")
    version_vieja = os.path.join(destino, "version.txt")
    if os.path.isfile(version_nueva) and os.path.isfile(version_vieja):
        with open(version_nueva, encoding="utf-8") as archivo:
            nueva = archivo.read().strip()
        with open(version_vieja, encoding="utf-8") as archivo:
            vieja = archivo.read().strip()
        if nueva and nueva == vieja:
            return False

    modelo = os.path.join(destino, "live2d", "miku", "miku.model3.json")
    nucleo = os.path.join(destino, "cubism", "live2dcubismcore.min.js")
    firma_modelo = huella(modelo) if os.path.isfile(modelo) else ""
    firma_nucleo = huella(nucleo) if os.path.isfile(nucleo) else ""

    siguiente = destino + ".siguiente"
    previa = destino + ".previa"
    shutil.rmtree(siguiente, ignore_errors=True)
    os.makedirs(siguiente, exist_ok=True)
    copiar_arbol(app, siguiente)
    for nombre in ("live2d", "cubism"):
        prohibido = os.path.join(siguiente, nombre)
        if os.path.isdir(prohibido):
            shutil.rmtree(prohibido)
    if os.path.isdir(os.path.join(destino, "live2d")):
        shutil.copytree(os.path.join(destino, "live2d"), os.path.join(siguiente, "live2d"), copy_function=shutil.copy2)
    if os.path.isdir(os.path.join(destino, "cubism")):
        shutil.copytree(os.path.join(destino, "cubism"), os.path.join(siguiente, "cubism"), copy_function=shutil.copy2)

    modelo_nuevo = os.path.join(siguiente, "live2d", "miku", "miku.model3.json")
    nucleo_nuevo = os.path.join(siguiente, "cubism", "live2dcubismcore.min.js")
    if firma_modelo and (not os.path.isfile(modelo_nuevo) or huella(modelo_nuevo) != firma_modelo):
        shutil.rmtree(siguiente, ignore_errors=True)
        raise SystemExit("La copia iba a cambiar el modelo. Me detuve y dejé la versión anterior.")
    if firma_nucleo and (not os.path.isfile(nucleo_nuevo) or huella(nucleo_nuevo) != firma_nucleo):
        shutil.rmtree(siguiente, ignore_errors=True)
        raise SystemExit("La copia iba a cambiar Cubism Core. Me detuve y dejé la versión anterior.")
    if not os.path.isfile(os.path.join(siguiente, "index.html")) or not os.path.isfile(os.path.join(siguiente, "sw.js")):
        shutil.rmtree(siguiente, ignore_errors=True)
        raise SystemExit("La revisión nueva no trae index.html y sw.js. No la instalé.")

    dias_viejos = os.path.join(destino, "dias")
    if os.path.isdir(dias_viejos) and not os.path.isdir(os.path.join(origen_repo, "contenido", "dias")):
        shutil.copytree(dias_viejos, os.path.join(siguiente, "dias"), dirs_exist_ok=True, copy_function=shutil.copy2)

    for carpeta in ("frases", "accesorios"):
        vieja = os.path.join(destino, carpeta)
        if os.path.isdir(vieja) and not os.path.isdir(os.path.join(siguiente, carpeta)):
            shutil.copytree(vieja, os.path.join(siguiente, carpeta), copy_function=shutil.copy2)

    if os.path.isdir(previa) and not os.path.isdir(destino):
        os.rename(previa, destino)
    elif os.path.isdir(previa):
        shutil.rmtree(previa)
    try:
        if os.path.isdir(destino):
            os.rename(destino, previa)
        os.rename(siguiente, destino)
    except OSError:
        if not os.path.isdir(destino) and os.path.isdir(previa):
            os.rename(previa, destino)
        shutil.rmtree(siguiente, ignore_errors=True)
        raise
    shutil.rmtree(previa, ignore_errors=True)
    return True


def copiar_scripts(origen_repo: str, destino: str) -> None:
    scripts = os.path.join(origen_repo, "scripts")
    if not os.path.isdir(scripts):
        return
    for nombre in (
        "actualizar.sh",
        "aplicar_actualizacion.py",
        "servir.py",
        "preparar_sprites.py",
        "traer-modelo.sh",
        "activar-actualizaciones.sh",
        "instalar.sh",
        "dibujar_accesorios.py",
    ):
        fuente = os.path.join(scripts, nombre)
        if os.path.isfile(fuente):
            shutil.copy2(fuente, os.path.join(destino, nombre))
            if nombre.endswith(".sh") or nombre.endswith(".py"):
                modo = os.stat(os.path.join(destino, nombre)).st_mode
                os.chmod(os.path.join(destino, nombre), modo | 0o111)


def main() -> None:
    parser = argparse.ArgumentParser(description="Instala una revisión local de Miku en casa.")
    parser.add_argument("--origen", required=True, help="Checkout del repositorio")
    parser.add_argument("--destino", required=True, help="Carpeta servida, normalmente ~/.local/share/miku-en-casa")
    args = parser.parse_args()
    origen = os.path.abspath(args.origen)
    destino = os.path.abspath(args.destino)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if os.path.isdir(os.path.join(origen, "app")) or os.path.isdir(destino):
        os.makedirs(destino, exist_ok=True)
    cambio_app = instalar_app(origen, destino) if os.path.isdir(destino) or os.path.isdir(os.path.join(origen, "app")) else False
    if not os.path.isdir(destino):
        raise SystemExit(f"No existe el destino {destino} y el origen no trae app/.")
    refrescar_dias(origen, os.path.join(destino, "dias"))
    for carpeta in ("frases", "accesorios"):
        refrescar_carpeta(origen, destino, carpeta)
    copiar_scripts(origen, destino)
    print("app-nueva" if cambio_app else "app-igual")


if __name__ == "__main__":
    main()
