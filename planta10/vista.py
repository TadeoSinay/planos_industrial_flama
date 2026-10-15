"""Vista rápida (PNG) del layout v10 para revisar la geometría mientras se diseña."""

import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from . import modelo as M

COLOR = {"CIRC": "#f0f0f0", "MP": "#cde1f5", "AUX": "#e3e3e3", "CAR": "#f8d9c0", "PINT": "#f6cfc3", "MAN": "#fde4c8",
         "TERM": "#d7eed2", "PT": "#c8e8c8", "LIB": "#ffffff"}
PAS = {"AE": "#e6e6e6", "SP": "#fff3b0", "PO": "#f7f7f7"}


def vista(ruta, zona=None, dpi=120, rotulos_eq=True):
    fig, ax = plt.subplots(figsize=(22, 14) if zona is None else (16, 12))
    for z in M.ZONAS:
        r = z.rect
        fc = PAS.get(z.sub, COLOR.get(z.cat, "#ffffff")) if z.tipo == "pasillo" else COLOR.get(z.cat, "#ffffff")
        ax.add_patch(Rectangle((r.x0, r.y0), r.w, r.h, fc=fc, ec="#c00000" if z.tipo != "pasillo" else "#b08000",
                               lw=0.8 if z.tipo != "pasillo" else 0.4, hatch="//" if z.cat == "LIB" else None))
        if r.area > 2.0:
            ax.text(r.x0 + 0.1, r.y1 - 0.1, f"{z.cod}", fontsize=5.5, va="top", ha="left", color="#a00000")
    for e in M.EQUIPOS:
        r = e.rect
        ax.add_patch(Rectangle((r.x0, r.y0), r.w, r.h, fc="#ffffff" if e.tipo != "pulmon" else "#f6e0ff",
                               ec="#d06000" if e.tipo != "pulmon" else "#a000a0", lw=0.6))
        if e.op > 0:
            fx, fy = {"S": (r.c[0], r.y0 - 0.45), "N": (r.c[0], r.y1 + 0.45), "E": (r.x1 + 0.45, r.c[1]),
                      "O": (r.x0 - 0.45, r.c[1])}[e.frente]
            ax.plot([fx], [fy], "o", ms=3, color="#c000c0")
        if rotulos_eq and (r.w > 0.9 or r.h > 0.9):
            ax.text(r.c[0], r.c[1], e.cod, fontsize=3.8, ha="center", va="center")
    for x in M.EJES_X:
        for y in M.EJES_Y:
            ax.add_patch(Rectangle((x - M.COL / 2, y - M.COL / 2), M.COL, M.COL, fc="k"))
    for p in M.PUERTAS:
        if p.muro in "NS":
            y = M.LY if p.muro == "N" else 0
            ax.plot([p.a, p.b], [y, y], lw=4, color="#00a0ff" if p.tipo == "porton" else "#00c050")
        else:
            x = M.LX if p.muro == "E" else 0
            ax.plot([x, x], [p.a, p.b], lw=4, color="#00a0ff" if p.tipo == "porton" else "#00c050")
    ax.add_patch(Rectangle((0, 0), M.LX, M.LY, fc="none", ec="k", lw=2))
    if zona:
        ax.set_xlim(zona[0], zona[2]); ax.set_ylim(zona[1], zona[3])
    else:
        ax.set_xlim(-1, M.LX + 1); ax.set_ylim(-1, M.LY + 1)
    ax.set_aspect("equal")
    ax.set_xticks(range(0, int(M.LX) + 1, 2)); ax.set_yticks(range(0, int(M.LY) + 1, 1))
    ax.tick_params(labelsize=5); ax.grid(lw=0.15)
    plt.savefig(ruta, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    z = tuple(float(v) for v in sys.argv[2:6]) if len(sys.argv) > 5 else None
    vista(sys.argv[1], z)
