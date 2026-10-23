"""Mide en el modelo 3D de planos_flama- (cadquery) dónde caen etiqueta, oblea PBA, sello IRAM, tarjeta CABA,
etiqueta de serie, faja de sustituto y triángulos del eje de cada ABC propio, y lo guarda en cuerpos.json para las
figuras de trazabilidad. Coordenadas sobre el cuerpo desarrollado: s = arco desde la costura longitudinal (mm, positivo
hacia +X) y z = altura desde el borde inferior del cuerpo (mm). Se corre solo cuando cambian los planos."""
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(AQUI)), "planos_flama-"))

from flama import modelo3d as M  # noqa: E402
from flama import sustituto as S  # noqa: E402
from flama.bom import PROPIOS  # noqa: E402
from flama.catalogo import MODELOS  # noqa: E402

SALIDA = os.path.join(AQUI, "cuerpos.json")


def _arco(b, R, xc):
    """(s0, s1) de una pieza pegada al cuerpo del lado de la costura (-Y), a partir de su caja en X."""
    f = lambda x: R * math.asin(max(-1.0, min(1.0, (x - xc) / R)))  # noqa: E731
    return round(f(b.xmin), 1), round(f(b.xmax), 1)


def medir(m):
    p, _ = M.construir(m)
    cb = p["cuerpo"].BoundingBox()
    W, H, z0, R, xc, yc = M.placa_dim(m, p)
    z = lambda v: round(v - cb.zmin, 1)  # noqa: E731
    d = dict(codigo=m.codigo, R=round(R, 2), alto=z(cb.zmax), pollera=m.geo.get("zf_borde", 0.0) or 0.0,
             e=m.geo["t"], etiqueta=dict(ancho=round(W, 1), z0=z(z0), z1=z(z0 + H)))
    for k in ("oblea_pba", "sello_iram", "tarjeta_caba"):
        if k in p:
            b = p[k].BoundingBox()
            s0, s1 = _arco(b, R, xc)
            d[k] = dict(s0=s0, s1=s1, z0=z(b.zmin), z1=z(b.zmax))
    b = p["etiqueta_serie"].BoundingBox()
    d["etiqueta_serie"] = dict(ancho=M.ETIQUETA_SERIE[0], z0=z(b.zmin), z1=z(b.zmax))
    if "soportes_eje" in p:
        b = p["soportes_eje"].BoundingBox()
        d["triangulos"] = dict(s=round(b.xmax - xc, 1), z0=z(b.zmin), z1=z(b.zmax))
        b = p["portaeje"].BoundingBox()
        d["cano_eje"] = dict(z0=z(b.zmin), z1=z(b.zmax))
    alto, largo, _, _ = S.faja(m, p)
    d["faja_actual"] = dict(alto=round(alto, 1), largo=round(largo, 1))
    return d


if __name__ == "__main__":
    datos = [medir(m) for m in MODELOS if m.codigo in PROPIOS]
    with open(SALIDA, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=1)
    print("guardado", SALIDA, len(datos))
