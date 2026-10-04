#!/usr/bin/env python3
"""Quita el fondo blanco de los sprites y copia fondos, registro e iconos.

Pensado para repetirse: si la esquina ya es transparente, el PNG se copia tal cual.
Así se puede soltar un PNG nuevo (con fondo blanco) y volver a correr el script.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent


def es_blanco(rgb: np.ndarray, minimo: int = 248, croma: int = 12) -> np.ndarray:
    mn = rgb.min(axis=2)
    mx = rgb.max(axis=2)
    return (mn >= minimo) & ((mx - mn) <= croma)


def quitar_blanco(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    arr = np.array(rgba)
    rgb = arr[:, :, :3]
    alto, ancho = rgb.shape[:2]

    candidatos = es_blanco(rgb)
    # fromarray comparte memoria y queda de solo lectura; floodfill no podría pintar.
    mascara = Image.fromarray(np.where(candidatos, np.uint8(255), np.uint8(0))).copy()
    px = mascara.load()
    assert px is not None

    def inundar(x: int, y: int) -> None:
        if px[x, y] == 255:
            ImageDraw.floodfill(mascara, (x, y), 128)

    for x in range(ancho):
        inundar(x, 0)
        inundar(x, alto - 1)
    for y in range(alto):
        inundar(0, y)
        inundar(ancho - 1, y)

    fondo = np.array(mascara) == 128

    # Tres anillos: el antialias contra blanco deja un borde claro de 1–2 px.
    cerca = fondo.copy()
    for _ in range(3):
        dilatado = cerca.copy()
        dilatado[1:] |= cerca[:-1]
        dilatado[:-1] |= cerca[1:]
        dilatado[:, 1:] |= cerca[:, :-1]
        dilatado[:, :-1] |= cerca[:, 1:]
        cerca = dilatado
    orilla = cerca & ~fondo

    salida = arr.copy()
    salida[fondo, 3] = 0
    # Evita halos si algún visor premultiplica el RGB de los píxeles invisibles.
    salida[fondo, :3] = 0

    if orilla.any():
        mn = rgb.min(axis=2).astype(np.float32)
        mx = rgb.max(axis=2).astype(np.float32)
        croma = mx - mn
        # Solo el borde casi blanco y poco saturado. Así no se comen piel ni ropa clara.
        usar = orilla & (mn >= 188) & (croma <= 48)
        # min 255 -> alpha 0; min 188 -> alpha ~1. El blanco puro ya salió en el fondo.
        alpha = np.clip((255.0 - mn) / 78.0, 0.0, 1.0)
        rgb_f = rgb.astype(np.float32)
        recuperado = (rgb_f - 255.0 * (1.0 - alpha[..., None])) / np.maximum(alpha[..., None], 1e-3)
        recuperado = np.clip(recuperado, 0, 255)
        salida[usar, :3] = recuperado[usar].astype(np.uint8)
        salida[usar, 3] = np.clip(alpha[usar] * 255.0, 0, 255).astype(np.uint8)

    return Image.fromarray(salida, "RGBA")


def esquina_opaca_blanca(im: Image.Image) -> bool:
    rgba = im.convert("RGBA")
    r, g, b, a = rgba.getpixel((0, 0))
    return a > 240 and min(r, g, b) >= 248 and (max(r, g, b) - min(r, g, b)) <= 12


def procesar_sprite(origen: Path, destino: Path) -> str:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(origen) as im:
        if esquina_opaca_blanca(im):
            quitar_blanco(im).save(destino, "PNG", optimize=True)
            return "recortado"
        im.convert("RGBA").save(destino, "PNG", optimize=True)
        return "ya-transparente"


def icono(tam: int, maskable: bool) -> Image.Image:
    im = Image.new("RGBA", (tam, tam), (14, 122, 118, 255))
    d = ImageDraw.Draw(im)
    if not maskable:
        d.rounded_rectangle((0, 0, tam - 1, tam - 1), radius=int(tam * 0.22), fill=(14, 122, 118, 255))
    cx, cy = tam // 2, int(tam * 0.46)
    # Coletas geométricas, no el logo oficial.
    cola = (8, 78, 84, 255)
    grosor = int(tam * 0.11)
    largo = int(tam * 0.34)
    d.rounded_rectangle(
        (cx - int(tam * 0.30), cy - int(tam * 0.02), cx - int(tam * 0.30) + grosor, cy - int(tam * 0.02) + largo),
        radius=grosor // 2,
        fill=cola,
    )
    d.rounded_rectangle(
        (cx + int(tam * 0.19), cy - int(tam * 0.02), cx + int(tam * 0.19) + grosor, cy - int(tam * 0.02) + largo),
        radius=grosor // 2,
        fill=cola,
    )
    radio = int(tam * 0.20)
    d.ellipse((cx - radio, cy - radio, cx + radio, cy + radio), fill=(255, 228, 206, 255))
    ojo = int(tam * 0.035)
    d.ellipse((cx - int(tam * 0.09), cy - int(tam * 0.02), cx - int(tam * 0.09) + ojo, cy - int(tam * 0.02) + ojo), fill=(20, 40, 48, 255))
    d.ellipse((cx + int(tam * 0.05), cy - int(tam * 0.02), cx + int(tam * 0.05) + ojo, cy - int(tam * 0.02) + ojo), fill=(20, 40, 48, 255))
    # Corbata pequeña.
    t = int(tam * 0.045)
    d.polygon(
        [(cx, cy + int(tam * 0.16)), (cx - t, cy + int(tam * 0.22)), (cx, cy + int(tam * 0.34)), (cx + t, cy + int(tam * 0.22))],
        fill=(255, 122, 168, 255),
    )
    return im


def generar_iconos(carpeta: Path) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    icono(192, False).save(carpeta / "icon-192.png", "PNG", optimize=True)
    icono(512, False).save(carpeta / "icon-512.png", "PNG", optimize=True)
    icono(512, True).save(carpeta / "icon-512-maskable.png", "PNG", optimize=True)
    icono(32, False).resize((32, 32), Image.Resampling.LANCZOS).save(carpeta / "favicon.png", "PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara sprites transparentes, fondos e iconos.")
    parser.add_argument("--raiz", type=Path, default=RAIZ, help="Raíz del proyecto o de la app instalada")
    parser.add_argument(
        "--destino",
        type=Path,
        default=None,
        help="Carpeta de salida (por defecto <raiz>/public, o la raíz si ya es la app servida)",
    )
    args = parser.parse_args()
    raiz: Path = args.raiz.resolve()

    registro_path = raiz / "contenido" / "mikuverse.json"
    if not registro_path.exists():
        registro_path = raiz / "mikuverse.json"
    if not registro_path.exists():
        raise SystemExit(f"No encuentro mikuverse.json en {raiz}")

    registro = json.loads(registro_path.read_text(encoding="utf-8"))
    destino = args.destino.resolve() if args.destino else (raiz / "public" if (raiz / "contenido").exists() else raiz)
    destino.mkdir(parents=True, exist_ok=True)

    fuentes_sprites = raiz / "fuentes" / "sprites"
    if not fuentes_sprites.exists():
        fuentes_sprites = raiz / "entrada"

    for variante in registro.get("variantes", []):
        nombre = Path(variante["archivo"]).name
        origen = fuentes_sprites / nombre
        if not origen.exists():
            # Ya procesado en sprites/
            origen = destino / "sprites" / nombre
        if not origen.exists():
            print(f"aviso: falta {nombre}, se omite")
            continue
        estado = procesar_sprite(origen, destino / "sprites" / nombre)
        print(f"{nombre}: {estado}")

    fuentes_fondos = raiz / "fuentes" / "fondos"
    if fuentes_fondos.exists():
        (destino / "fondos").mkdir(parents=True, exist_ok=True)
        for png in sorted(fuentes_fondos.glob("*.png")):
            shutil.copyfile(png, destino / "fondos" / png.name)
            print(f"fondo {png.name}")

    shutil.copyfile(registro_path, destino / "mikuverse.json")
    generar_iconos(destino / "icons")
    print(f"listo -> {destino}")


if __name__ == "__main__":
    main()
