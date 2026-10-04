#!/usr/bin/env python3
"""Dibuja los accesorios de Live2D (PNG transparentes) en contenido/accesorios/.

Arte propio, geométrico, hecho con Pillow. Se puede repetir sin problema.
  python3 scripts/dibujar_accesorios.py
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "contenido" / "accesorios"
S = 4  # supermuestreo
W, H = 512, 512


def lienzo():
    return Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))


def p(*xy):
    return [v * S for v in xy]


def terminar(im: Image.Image, nombre: str) -> None:
    sombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
    alpha = im.getchannel("A").filter(ImageFilter.GaussianBlur(6 * S))
    sombra.putalpha(alpha.point(lambda a: int(a * 0.35)))
    base = Image.new("RGBA", im.size, (0, 0, 0, 0))
    base.alpha_composite(sombra, (0, 4 * S))
    base.alpha_composite(im)
    base = base.resize((W, H), Image.Resampling.LANCZOS)
    SALIDA.mkdir(parents=True, exist_ok=True)
    base.save(SALIDA / nombre, "PNG", optimize=True)
    print("listo", SALIDA / nombre)


def estrella(d: ImageDraw.ImageDraw, cx, cy, r, color):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts += [cx + rr * math.cos(ang), cy + rr * math.sin(ang)]
    d.polygon(p(*pts), fill=color)


def sombrero_bruja() -> None:
    im = lienzo()
    d = ImageDraw.Draw(im)
    morado, morado2, borde = (52, 26, 78, 255), (78, 44, 112, 255), (24, 10, 38, 255)
    # Ala de atrás
    d.ellipse(p(18, 352, 494, 470), fill=borde)
    d.ellipse(p(24, 356, 488, 462), fill=morado)
    # Cono doblado (curva hecha con muchos puntos)
    izq, der = [], []
    for i in range(41):
        t = i / 40
        y = 410 - t * 330
        ancho = 118 * (1 - t) ** 0.9 + 4
        curva = 70 * t ** 2.4  # la punta se dobla a la derecha
        cx = 256 + curva
        izq.append((cx - ancho, y))
        der.append((cx + ancho, y))
    punta = (256 + 70 + 26, 92)  # punta caída
    cono = izq + [punta] + der[::-1]
    d.polygon(p(*[v for xy in cono for v in xy]), fill=borde)
    cono_in = [(x + (4 if x < 300 else -4), y + 3) for x, y in cono]
    d.polygon(p(*[v for xy in cono_in for v in xy]), fill=morado2)
    # Brillo lateral
    brillo = [(x + 26, y) for x, y in izq[2:28]] + [(x + 44, y) for x, y in izq[2:28]][::-1]
    d.polygon(p(*[v for xy in brillo for v in xy]), fill=(110, 70, 150, 160))
    # Cinta naranja con hebilla dorada
    d.polygon(p(140, 372, 372, 372, 362, 330, 150, 330), fill=(255, 138, 31, 255))
    d.polygon(p(140, 372, 372, 372, 370, 364, 142, 364), fill=(214, 96, 10, 255))
    d.rectangle(p(232, 326, 282, 376), fill=(255, 210, 74, 255))
    d.rectangle(p(244, 338, 270, 364), fill=(255, 138, 31, 255))
    # Ala de adelante (media elipse)
    d.chord(p(8, 360, 504, 486), 0, 180, fill=borde)
    d.chord(p(16, 362, 496, 476), 0, 180, fill=morado)
    d.arc(p(40, 372, 472, 466), 20, 160, fill=(110, 70, 150, 255), width=5 * S)
    # Estrellitas color Miku
    estrella(d, 196, 250, 16, (57, 197, 187, 255))
    estrella(d, 300, 170, 11, (57, 197, 187, 255))
    estrella(d, 236, 300, 8, (255, 230, 120, 255))
    terminar(im, "bruja.png")


def zigzag(d, x0, x1, y, alto, paso, color, grosor):
    pts = []
    x = x0
    arriba = True
    while x <= x1:
        pts += [x, y - alto / 2 if arriba else y + alto / 2]
        x += paso
        arriba = not arriba
    d.line(p(*pts), fill=color, width=grosor * S, joint="curve")


def sombrero_vueltiao() -> None:
    im = lienzo()
    d = ImageDraw.Draw(im)
    crema, crema2, negro = (240, 228, 196, 255), (222, 206, 166, 255), (28, 22, 18, 255)
    # Ala: anillos de caña flecha (crema y negro)
    cx, cy = 256, 372
    anillos = [(250, 82, crema2), (244, 78, negro), (232, 72, crema), (214, 64, negro),
               (204, 59, crema), (186, 52, negro), (176, 47, crema), (160, 41, negro), (150, 37, crema)]
    for rx, ry, col in anillos:
        d.ellipse(p(cx - rx, cy - ry, cx + rx, cy + ry), fill=col)
    # Zigzag en el ala (las "pintas")
    for rx, ry in ((223, 68), (195, 55)):
        pts = []
        for i in range(0, 361, 6):
            a = math.radians(i)
            r = 1 + (0.035 if (i // 6) % 2 else -0.035)
            pts += [cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)]
        d.line(p(*pts), fill=negro if rx > 200 else (120, 80, 40, 255), width=3 * S)
    # Copa
    copa = [(160, 372), (172, 250), (186, 214), (226, 196), (286, 196), (326, 214), (340, 250), (352, 372)]
    d.polygon(p(*[v for xy in copa for v in xy]), fill=negro)
    copa_in = [(166, 368), (178, 252), (191, 219), (228, 202), (284, 202), (321, 219), (334, 252), (346, 368)]
    d.polygon(p(*[v for xy in copa_in for v in xy]), fill=crema)
    # Franjas negras con rombos, recortadas a la forma de la copa
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    mascara = Image.new("L", im.size, 0)
    ImageDraw.Draw(mascara).polygon(p(*[v for xy in copa_in for v in xy]), fill=255)
    dc = d
    d = ImageDraw.Draw(capa)
    for y, alto in ((236, 16), (290, 22), (342, 20)):
        mitad = 92 + (y - 236) * 0.12
        d.rectangle(p(256 - mitad, y - alto / 2, 256 + mitad, y + alto / 2), fill=negro)
        x = 256 - mitad + 10
        while x < 256 + mitad - 8:
            d.polygon(p(x, y, x + 7, y - alto / 2 + 3, x + 14, y, x + 7, y + alto / 2 - 3), fill=crema)
            x += 20
    zigzag(d, 176, 336, 264, 12, 10, negro, 3)
    zigzag(d, 170, 342, 316, 12, 10, negro, 3)
    vacia = Image.new("RGBA", im.size, (0, 0, 0, 0))
    im.alpha_composite(Image.composite(capa, vacia, mascara))
    d = dc
    # Frente del ala (media elipse para que tape la base de la copa)
    for rx, ry, col in anillos:
        d.chord(p(cx - rx, cy - ry, cx + rx, cy + ry), 0, 180, fill=col)
    d.arc(p(cx - 196, cy - 56, cx + 196, cy + 56), 0, 180, fill=(120, 80, 40, 255), width=3 * S)
    # Cinta tricolor sutil
    d.rectangle(p(168, 356, 344, 362), fill=(252, 209, 22, 255))
    d.rectangle(p(168, 362, 344, 366), fill=(0, 56, 147, 255))
    d.rectangle(p(168, 366, 344, 370), fill=(206, 17, 38, 255))
    terminar(im, "colombiana.png")


if __name__ == "__main__":
    sombrero_bruja()
    sombrero_vueltiao()
