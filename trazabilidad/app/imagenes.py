"""Imágenes de la app (app/img/): el matafuego del hero y la familia ABC a escala real, renderizados del modelo cadquery
de planos_flama- con el mismo rasterizador de render_3d.py (fondo transparente, sin faja de sustituto: así sale de
fábrica), y las fotos de los Word de proceso y del relevamiento de campo, reducidas a WebP. Se corre a mano solo cuando
cambian los planos o las fotos: build.py lee app/img/ y las embebe en index.html.
Uso: python3 imagenes.py <carpeta de uploads>"""
import json
import os
import sys
import zipfile
from io import BytesIO

import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import render_3d as R  # noqa: E402

IMG = os.path.join(AQUI, "img")
PX_MM = 1.6          # píxeles por mm en la familia a escala
# fotos: (archivo de uploads, miembro dentro del zip/docx, nombre de salida, ancho)
FOTOS = [("df0c3979-PROCESO_CARRO_EN_LIMPIO.docx", "word/media/image6.jpg", "despacho", 1100),
         ("df0c3979-PROCESO_CARRO_EN_LIMPIO.docx", "word/media/image11.jpg", "pallets", 900),
         ("df0c3979-PROCESO_CARRO_EN_LIMPIO.docx", "word/media/image24.jpg", "carro_cupulas", 900),
         ("df0c3979-PROCESO_CARRO_EN_LIMPIO.docx", "word/media/image25.png", "roladora", 900),
         ("df0c3979-PROCESO_CARRO_EN_LIMPIO.docx", "word/media/image22.jpg", "chapas", 900),
         ("c3dae5e3-WhatsApp_Unknown_2026-10-05_at_21.11.33.zip", "WhatsApp Image 2026-10-05 at 21.03.58 (3).jpeg",
          "campo_tarjeta", 700),
         ("c3dae5e3-WhatsApp_Unknown_2026-10-05_at_21.11.33.zip", "WhatsApp Image 2026-10-05 at 21.03.55 (1).jpeg",
          "campo_qr", 700),
         ("d578b430-WhatsApp_Unknown_2026-10-05_at_21.11.18.zip", "WhatsApp Image 2026-10-05 at 21.02.41 (2).jpeg",
          "campo_oblea", 700)]


def caras(k, faja=False):
    p, cb = R.piezas(k)
    if not faja:
        p.pop("faja", None)
    tol = max(0.25, (cb.xmax - cb.xmin) / 420)
    out = []
    for nombre, sh in p.items():
        if sh is not None:
            out += [(t, R.COL.get(nombre, R.GRIS)) for t in R._tris(sh, tol)]
    return out


def png_transparente(c, az, el, W, H, margen=0.02):
    img, _, _ = R.rasterizar(c, az, el, W=W, H=H, margen=margen)
    blanco = (img > 0.999).all(axis=2)
    a = np.where(blanco, 0, 255).astype(np.uint8)
    rgba = np.dstack([(img * 255).astype(np.uint8), a])
    im = Image.fromarray(rgba, "RGBA")
    return im.crop(im.getbbox())


def guardar(im, nombre, q=78):
    ruta = os.path.join(IMG, nombre + ".webp")
    im.save(ruta, "WEBP", quality=q, method=6)
    print(nombre, im.size, os.path.getsize(ruta) // 1024, "KB")


def posiciones():
    """Centro de cada equipo en familia.webp (fracción del ancho) para poner el rótulo debajo: img/familia.json."""
    a = np.array(Image.open(os.path.join(IMG, "familia.webp")).convert("RGBA"))[..., 3].sum(axis=0) > 0
    tramos, x0 = [], None
    for x, v in enumerate(list(a) + [False]):
        if v and x0 is None:
            x0 = x
        elif not v and x0 is not None:
            tramos.append((x0, x)) if x - x0 > 20 else None
            x0 = None
    with open(os.path.join(IMG, "familia.json"), "w") as fh:
        json.dump([round((p + q) / 2 / len(a), 4) for p, q in tramos], fh)


def main(uploads):
    os.makedirs(IMG, exist_ok=True)
    # hero: 5 kg tres cuartos del lado pared (franja grabada y QR de serie a la vista)
    guardar(png_transparente(caras("5kg"), 128, 10, 1000, 1400), "heroe_5kg", 82)
    # familia a escala: cada modelo con su altura real en píxeles, alineados por el piso
    fam = []
    for k in ["1kg", "2.5kg", "5kg", "10kg", "25kg", "50kg"]:
        c = caras(k)
        z = [v[2] for t, _ in c for v in t]
        alto = (max(z) - min(z)) * PX_MM
        fam.append((k, png_transparente(c, 120, 6, int(alto * 1.4), int(alto * 1.08), 0.0)))
    hmax = max(im.height for _, im in fam)
    W = sum(im.width for _, im in fam) + 40 * (len(fam) - 1)
    lienzo = Image.new("RGBA", (W, hmax), (0, 0, 0, 0))
    x = 0
    for _, im in fam:
        lienzo.paste(im, (x, hmax - im.height), im)
        x += im.width + 40
    guardar(lienzo, "familia", 80)
    posiciones()
    for arch, miembro, nombre, ancho in FOTOS:
        with zipfile.ZipFile(os.path.join(uploads, arch)) as z:
            m = next(n for n in z.namelist() if n.endswith(miembro))
            im = Image.open(BytesIO(z.read(m))).convert("RGB")
        im.thumbnail((ancho, ancho * 2))
        guardar(im, nombre, 72)


if __name__ == "__main__":
    main(sys.argv[1])
