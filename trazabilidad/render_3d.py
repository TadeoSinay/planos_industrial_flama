"""Render 3D (matplotlib) del matafuego real de los planos con la franja grabada, la etiqueta, el QR de serie, la
oblea y la faja de sustituto, para que se vea dónde va cada cosa. Usa el modelo cadquery de planos_flama- y la
geometría propuesta de figuras_trazabilidad.marcado(). Guarda PNG en trazabilidad/render/ (se commitean: el Word no
necesita cadquery). Se corre solo cuando cambian los planos o el marcado."""
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(AQUI)), "planos_flama-"))

import cadquery as cq  # noqa: E402
from flama import modelo3d as M  # noqa: E402
from flama.catalogo import MODELOS  # noqa: E402

import figuras_trazabilidad as FT  # noqa: E402

SALIDA = os.path.join(AQUI, "render")
COL = {"cuerpo": "#B3201E", "cupula": "#B3201E", "fondo": "#B3201E", "etiqueta": "#F2F2F2", "oblea_pba": "#C9B3E6",
       "sello_iram": "#F2B8CF", "tarjeta_caba": "#D9CFF0", "etiqueta_serie": "#7FB2E5", "manguera": "#202020",
       "manguera_enrollada": "#202020", "franja": "#111111", "faja": "#F5C400"}
GRIS = "#8C8C8C"
LUZ = (-0.45, -0.75, 0.5)


def _sector_u(R, u0, u1, z0, z1, xc, yc, esp=0.6):
    """Banda sobre el cuerpo entre los arcos u0 y u1 medidos desde la costura (-Y) hacia +X."""
    ancho = u1 - u0
    ang_c = -90.0 + math.degrees((u0 + u1) / 2 / R)
    return M._sector(R + 0.05, R + esp, z1 - z0, z0, ancho, xc, yc, ang_c)


def piezas(k):
    m = next(x for x in MODELOS if x.codigo == "FL_MAT_ABC_" + k)
    p, _ = M.construir(m)
    cb = p["cuerpo"].BoundingBox()
    R = (cb.xmax - cb.xmin) / 2
    xc, yc = (cb.xmax + cb.xmin) / 2, (cb.ymax + cb.ymin) / 2
    mk = FT.marcado(k)
    zb = cb.zmin
    p["franja"] = _sector_u(R, mk["u0"], mk["u1"], zb + mk["z0"], zb + mk["z1"], xc, yc, 0.9)
    fajas = None
    for a, b in mk["tramos"]:
        f = _sector_u(R, a, b, zb, zb + mk["faja_alto"], xc, yc, 0.5)
        fajas = f if fajas is None else fajas.fuse(f)
    p["faja"] = fajas
    return p, cb


def _tris(shape, tol):
    v, t = shape.tessellate(tol, 0.5)
    pts = [(q.x, q.y, q.z) for q in v]
    return [[pts[i] for i in tri] for tri in t]


def _rot(az, el):
    """Matriz de vista ortográfica: la cámara mira desde el azimut az (grados, 0 = +X, 90 = +Y) y elevación el."""
    import numpy as np
    a, e = math.radians(az), math.radians(el)
    f = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])   # hacia la cámara
    r = np.array([-math.sin(a), math.cos(a), 0.0])                                         # derecha de la imagen
    u = np.cross(f, r)                                                                      # arriba de la imagen
    return np.array([r, u, f])


def rasterizar(caras, az, el, W=900, H=1200, margen=0.06, caja=None):
    """Z-buffer propio: devuelve imagen RGB (H, W, 3) con sombreado Lambert y contornos, y la función que proyecta
    un punto 3D a píxeles (para las llamadas)."""
    import numpy as np
    Rm = _rot(az, el)
    pts = np.array([v for tri, _ in caras for v in tri]).reshape(-1, 3, 3)
    P = pts @ Rm.T
    if caja is None:
        caja = (P[..., 0].min(), P[..., 0].max(), P[..., 1].min(), P[..., 1].max())
    x0, x1, y0, y1 = caja
    esc = min(W * (1 - 2 * margen) / (x1 - x0), H * (1 - 2 * margen) / (y1 - y0))
    ox = W / 2 - esc * (x0 + x1) / 2
    oy = H / 2 + esc * (y0 + y1) / 2

    def proy(p):
        q = Rm @ np.array(p)
        return ox + esc * q[0], oy - esc * q[1]

    X = ox + esc * P[..., 0]
    Y = oy - esc * P[..., 1]
    Z = P[..., 2]
    img = np.ones((H, W, 3))
    zb = np.full((H, W), -1e18)
    luz = Rm[2] * 0.85 + Rm[1] * 0.45 - Rm[0] * 0.35
    luz = luz / np.linalg.norm(luz)
    cols = np.array([matplotlib.colors.to_rgb(c) for _, c in caras])
    n = np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1
    n /= ln[:, None]
    vista = Rm[2]
    n[(n @ vista) < 0] *= -1
    f = 0.42 + 0.58 * np.clip(n @ luz, 0, 1)
    shade = cols * f[:, None]
    for i in range(len(caras)):
        xs, ys, zs = X[i], Y[i], Z[i]
        a0, a1 = int(max(0, math.floor(xs.min()))), int(min(W - 1, math.ceil(xs.max())))
        b0, b1 = int(max(0, math.floor(ys.min()))), int(min(H - 1, math.ceil(ys.max())))
        if a1 < a0 or b1 < b0:
            continue
        gx, gy = np.meshgrid(np.arange(a0, a1 + 1) + 0.5, np.arange(b0, b1 + 1) + 0.5)
        d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(d) < 1e-12:
            continue
        l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
        l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
        l2 = 1 - l0 - l1
        dentro = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not dentro.any():
            continue
        z = l0 * zs[0] + l1 * zs[1] + l2 * zs[2]
        sub = zb[b0:b1 + 1, a0:a1 + 1]
        ok = dentro & (z > sub)
        sub[ok] = z[ok]
        img[b0:b1 + 1, a0:a1 + 1][ok] = shade[i]
    # contornos: saltos de profundidad
    fondo = zb < -1e17
    zf = np.where(fondo, zb[~fondo].min() - 50 if (~fondo).any() else 0, zb)
    gyz, gxz = np.gradient(zf)
    borde = (np.hypot(gxz, gyz) > 3.0 / esc * 6) | (fondo != np.roll(fondo, 1, 0)) | (fondo != np.roll(fondo, 1, 1))
    img[borde] = img[borde] * 0.25
    return img, proy, caja


def render(k, vistas, ruta, titulo, llamadas=True):
    """vistas: [(azimut, elevación, subtítulo)]. Llamadas con flecha sobre franja, QR, etiqueta, oblea y faja."""
    import numpy as np
    p, cb = piezas(k)
    tol = max(0.35, (cb.xmax - cb.xmin) / 300)
    caras = []
    for nombre, sh in p.items():
        if sh is None:
            continue
        col = COL.get(nombre, GRIS)
        caras += [(tri, col) for tri in _tris(sh, tol)]
    mk = FT.marcado(k)
    c = FT.CUERPOS[k]
    R = c["R"]
    xc, yc = (cb.xmax + cb.xmin) / 2, (cb.ymax + cb.ymin) / 2

    def punto(u, z, sale=1.0):
        a = -math.pi / 2 + u / R
        return (xc + (R + sale) * math.cos(a), yc + (R + sale) * math.sin(a), cb.zmin + z)

    marcas = [("franja grabada", punto((mk["u0"] + mk["u1"]) / 2, (mk["z0"] + mk["z1"]) / 2), "#111111", +1),
              ("QR de serie", punto(mk["des"] / 2, (c["etiqueta_serie"]["z0"] + c["etiqueta_serie"]["z1"]) / 2),
               "#1F5FA8", -1),
              ("etiqueta del fabricante", punto(0, (c["etiqueta"]["z0"] + c["etiqueta"]["z1"]) / 2), "#555555", -1),
              ("oblea PBA", punto(0, (c["oblea_pba"]["z0"] + c["oblea_pba"]["z1"]) / 2), "#6A4C93", +1),
              ("faja de sustituto", punto(mk["tramos"][0][0] + 30 if mk["carro"] else mk["des"] * 0.12,
                                          mk["faja_alto"] / 2), "#B08900", -1)]
    fig, axs = plt.subplots(1, len(vistas), figsize=(4.6 * len(vistas), 6.6))
    axs = np.atleast_1d(axs)
    for ax, (az, el, sub) in zip(axs, vistas):
        img, proy, _ = rasterizar(caras, az, el)
        ax.imshow(img)
        if llamadas:
            Rm = _rot(az, el)
            for txt, pt, col, lado in marcas:
                nrm = np.array([pt[0] - xc, pt[1] - yc, 0.0])
                if nrm @ Rm[2] <= 0.25 * np.linalg.norm(nrm):
                    continue                                       # del otro lado: no se ve
                px, py = proy(pt)
                tx = min(px + 230, 640) if lado > 0 else 8
                ax.annotate(txt, (px, py), (tx, py - 40), fontsize=8.5, color=col, weight="bold", ha="left",
                            arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1))
        ax.set_title(sub, fontsize=9.5)
        ax.axis("off")
    fig.suptitle(titulo, fontsize=11)
    fig.subplots_adjust(wspace=0.02, left=0.01, right=0.99, top=0.9, bottom=0.01)
    fig.savefig(ruta, dpi=150, facecolor="white")
    plt.close(fig)
    return ruta


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    print(render("5kg", [(-90, 8, "Lado etiqueta (la costura queda debajo de la etiqueta)"),
                         (90, 8, "Lado pared: franja grabada y QR de serie"),
                         (135, 18, "Tres cuartos")], os.path.join(SALIDA, "r5kg.png"),
                 "ABC 5 kg (con la faja de sustituto abierta)"))
    print(render("1kg", [(-90, 8, "Lado etiqueta"), (90, 8, "Lado opuesto: franja y QR")],
                 os.path.join(SALIDA, "r1kg.png"), "ABC 1 kg"))
    print(render("25kg", [(-90, 10, "Lado etiqueta y manija"), (-40, 18, "Tres cuartos")],
                 os.path.join(SALIDA, "r25kg.png"), "ABC 25 kg sobre ruedas"))
