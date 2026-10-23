"""Figuras del Word del sistema de trazabilidad (matplotlib). La geometría de cada cuerpo (etiqueta, oblea, sello,
tarjeta, etiqueta de serie, triángulos del eje y faja actual) sale de cuerpos.json, medido en el modelo 3D de los planos
(extraer_cuerpos.py). Coordenadas: u = arco sobre el cuerpo desarrollado desde el borde de costura (0 y 2πR son la
costura), z = altura desde el borde inferior del cuerpo."""
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
ROJO, GRIS, OSC, AZUL, VERDE, AMAR, NAR = "#C0392B", "#BFBFBF", "#333333", "#DDEBF7", "#E2EFDA", "#FFF2CC", "#F8CBAD"
FAJA_C, ETQ, OBL, SEL, TAR, QR = "#F5C400", "#E7E6E6", "#D9C8F0", "#F6CFE0", "#E4DDF5", "#BDD7EE"

AQUI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(AQUI, "cuerpos.json"), encoding="utf-8") as _fh:
    CUERPOS = {d["codigo"].replace("FL_MAT_ABC_", ""): d for d in json.load(_fh)}

DM_MOD, DM_CELDA = 18, 0.6           # DataMatrix ECC 200 18 × 18 módulos, celda 0,6 mm
TXT_H = 5.0                          # alto de letra del marcado (planos: MARCA_H)
DPS = (15.0, 7.0)                    # cuño DPS (Res. 349/07 anexo IV)
LUZ_FAJA = 5.0                       # luz entre la punta de la faja y la franja (criterio)
LUZ_COSTURA = 25.0                   # carros: inicio de la franja desde el borde de costura (criterio)
PROF = {"1kg": "0,08–0,10", "2.5kg": "0,20–0,25", "5kg": "0,20–0,25", "10kg": "0,20–0,25", "25kg": "0,30",
        "50kg": "0,30", "70kg": "0,40–0,45", "100kg": "0,40–0,45"}
NOMBRE = {"1kg": "1 kg", "2.5kg": "2,5 kg", "5kg": "5 kg", "10kg": "10 kg", "25kg": "25 kg", "50kg": "50 kg",
          "70kg": "70 kg", "100kg": "100 kg"}
# franja de los manuales: largo × alto y base sobre el borde inferior (1 kg: encima del fondo que monta por fuera)
FR_MAN = {"1kg": (90.0, 13.0, 14.0), "2.5kg": (130.0, 12.0, 2.0), "5kg": (130.0, 12.0, 4.5),
          "10kg": (130.0, 12.0, 2.0)}
FR_CAR = (115.0, 13.0)               # carros: dos líneas, la primera con la presión de ensayo (IRAM 3550 5.1)


def n(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def marcado(k):
    """Franja y faja propuestas de un modelo: dict con u0, u1, z0, z1, des, faja (alto y tramos en u)."""
    c = CUERPOS[k]
    des = 2 * math.pi * c["R"]
    if "triangulos" in c:
        L, h = FR_CAR
        u0, z0 = LUZ_COSTURA, c["triangulos"]["z1"] + 5.0
        t = c["triangulos"]["s"] + 2.4 + LUZ_FAJA                      # mitad del espesor 4,75 + luz
        alto = 40.0
        tramos = [(t, des - t)]                                        # abierta entre los triángulos (costura)
    else:
        L, h, z0 = FR_MAN[k]
        u0 = des / 2 - L / 2
        alto = c["faja_actual"]["alto"]
        if "tarjeta_caba" in c:
            alto = min(alto, c["tarjeta_caba"]["z0"] - 3.0)
        alto = math.floor(alto)
        tramos = [(0.0, u0 - LUZ_FAJA), (u0 + L + LUZ_FAJA, des)]      # abierta sobre la franja (lado opuesto)
    return dict(u0=u0, u1=u0 + L, z0=z0, z1=z0 + h, L=L, h=h, des=des, faja_alto=alto, tramos=tramos,
                faja_largo=sum(b - a for a, b in tramos), carro="triangulos" in c)


def _guardar(fig, ruta):
    fig.savefig(ruta, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


def _datamatrix(ax, x0, y0, celda, n_=DM_MOD, semilla=7):
    """DataMatrix ilustrativo (patrón de búsqueda en L + reloj + celdas pseudoaleatorias)."""
    import random
    rnd = random.Random(semilla)
    for i in range(n_):
        for j in range(n_):
            borde_l = i == 0 or j == 0
            reloj = (i == n_ - 1 and j % 2 == 0) or (j == n_ - 1 and i % 2 == 0)
            if borde_l or reloj or (0 < i < n_ - 1 and 0 < j < n_ - 1 and rnd.random() < 0.5):
                ax.add_patch(Rectangle((x0 + j * celda, y0 + i * celda), celda * 0.92, celda * 0.92, color="black",
                                       lw=0))


def fig_contenido(ruta):
    """Las tres franjas a escala: manuales 2,5 a 10 kg, 1 kg en dos líneas y carros con la presión de ensayo."""
    fig, axs = plt.subplots(3, 1, figsize=(9.5, 5.2), gridspec_kw={"height_ratios": [1, 1.05, 1]})
    lado = DM_MOD * DM_CELDA
    casos = [("Manuales 2,5 · 5 · 10 kg (y sus cilindros y sustitutos)", 130.0, 12.0, ["FLAMA S.A.  N° 26-000123  26"]),
             ("1 kg (Ø 76: dos líneas para no rodear medio cuerpo)", 90.0, 13.0, ["FLAMA S.A.", "N° 26-000123  26"]),
             ("Carros 25 a 100 kg (IRAM 3550 5.1 suma la presión de ensayo)", 115.0, 13.0,
              ["FLAMA S.A.  PE 4,0 MPa", "N° 26-000123  26"])]
    for ax, (tit, ancho, alto, lineas) in zip(axs, casos):
        ax.add_patch(Rectangle((0, 0), ancho, alto, fc="#F4D7D3", ec=ROJO, lw=1.2))
        _datamatrix(ax, 2.0, (alto - lado) / 2, DM_CELDA)
        x = 2.0 + lado + 3
        if len(lineas) == 1:
            ax.text(x, alto / 2, lineas[0], fontsize=10.5, va="center", family="DejaVu Sans Mono", weight="bold")
        else:
            ax.text(x, alto * 0.73, lineas[0], fontsize=10.5, va="center", family="DejaVu Sans Mono", weight="bold")
            ax.text(x, alto * 0.27, lineas[1], fontsize=10.5, va="center", family="DejaVu Sans Mono", weight="bold")
        ax.add_patch(Rectangle((ancho - DPS[0] - 2, (alto - DPS[1]) / 2), DPS[0], DPS[1], fc="white", ec="black", lw=1))
        ax.text(ancho - DPS[0] / 2 - 2, alto / 2, "DPS", ha="center", va="center", fontsize=9, weight="bold")
        kw = dict(arrowstyle="<->", lw=0.6, color=OSC)
        ax.annotate("", (0, -2.2), (ancho, -2.2), arrowprops=kw)
        ax.text(ancho / 2, -4.3, f"{n(ancho, 0)} mm", ha="center", va="top", fontsize=7)
        ax.annotate("", (ancho + 2.5, 0), (ancho + 2.5, alto), arrowprops=kw)
        ax.text(ancho + 4, alto / 2, f"{n(alto, 0)} mm", va="center", fontsize=7)
        ax.text(0, alto + 2, tit, fontsize=8, weight="bold")
        ax.set_xlim(-3, 150)
        ax.set_ylim(-9, alto + 6)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.5, 0.005, f"DataMatrix ECC 200 de {DM_MOD} × {DM_MOD} celdas de {n(DM_CELDA)} mm = {n(lado)} mm · "
                         f"letra {n(TXT_H, 0)} mm · cuño DPS {n(DPS[0], 0)} × {n(DPS[1], 0)} mm (a escala)",
             ha="center", fontsize=7.5, color=OSC)
    return _guardar(fig, ruta)


def _rect(ax, u0, u1, z0, z1, fc, ec=OSC, lw=0.5, **kw):
    ax.add_patch(Rectangle((u0, z0), u1 - u0, z1 - z0, fc=fc, ec=ec, lw=lw, **kw))


def _mapa(ax, k, faja="propuesta", textos=True):
    """Cuerpo desarrollado (la planchuela tal como sale de la guillotina, cara exterior arriba)."""
    c, m = CUERPOS[k], marcado(k)
    des, H = m["des"], c["alto"]
    _rect(ax, 0, des, 0, H, "#F7F7F7", lw=1.0)
    for u in (0, des):
        ax.plot([u, u], [0, H], color=OSC, lw=2.2)
    if c["pollera"]:
        ax.plot([0, des], [c["pollera"]] * 2, ls="--", lw=0.7, color=OSC)
    e = c["etiqueta"]
    for a, b in ((0, e["ancho"] / 2), (des - e["ancho"] / 2, des)):
        _rect(ax, a, b, e["z0"], e["z1"], ETQ, ec=GRIS)
    for key, col in (("oblea_pba", OBL), ("sello_iram", SEL), ("tarjeta_caba", TAR)):
        if key in c:
            s0, s1 = c[key]["s0"], c[key]["s1"]
            if s0 < 0 < s1:
                _rect(ax, 0, s1, c[key]["z0"], c[key]["z1"], col)
                _rect(ax, des + s0, des, c[key]["z0"], c[key]["z1"], col)
            else:
                a, b = (s0, s1) if s0 >= 0 else (des + s0, des + s1)
                _rect(ax, a, b, c[key]["z0"], c[key]["z1"], col)
    q = c["etiqueta_serie"]
    _rect(ax, des / 2 - q["ancho"] / 2, des / 2 + q["ancho"] / 2, q["z0"], q["z1"], QR)
    if "triangulos" in c:
        t = c["triangulos"]
        for u in (t["s"], des - t["s"]):
            _rect(ax, u - 2.4, u + 2.4, t["z0"], t["z1"], "#595959", ec="#595959")
        for a, b in ((0, 21), (des - 21, des)):
            _rect(ax, a, b, c["cano_eje"]["z0"], c["cano_eje"]["z1"], "none", ec="#595959", hatch="////", lw=0.4)
    if faja == "actual":
        fa = c["faja_actual"]["alto"]
        _rect(ax, 0, des, 0, fa, FAJA_C, ec="#B08900", alpha=0.92, zorder=4)
        _rect(ax, m["u0"], m["u1"], m["z0"], m["z1"], "none", ec=ROJO, lw=1.2, ls="--", zorder=5)
    else:
        for a, b in m["tramos"]:
            _rect(ax, a, b, 0, m["faja_alto"], FAJA_C, ec="#B08900", alpha=0.9, zorder=4)
        _rect(ax, m["u0"], m["u1"], m["z0"], m["z1"], "#F4D7D3", ec=ROJO, lw=1.3, zorder=5)
    if textos:
        fs = 7
        ax.text(des / 2, q["z1"] + 4, "QR de serie", ha="center", va="bottom", fontsize=fs)
        ax.text(e["ancho"] / 4, (e["z0"] + e["z1"]) / 2, "etiqueta", ha="center", va="center", fontsize=fs,
                color="#7F7F7F", rotation=90)
        rot = f"franja z {m['z0']:g}–{m['z1']:g}".replace(".", ",")
        if m["carro"]:
            ax.text(m["u1"] + 3, m["z1"] + 2, rot, fontsize=fs, color=ROJO, va="bottom")
        else:
            ax.text((m["u0"] + m["u1"]) / 2, max(m["z1"], m["faja_alto"]) + 3, rot, fontsize=fs, color=ROJO,
                    va="bottom", ha="center")
        ax.text(2, H + 4, "costura", fontsize=fs, va="bottom")
        ax.text(des - 2, H + 4, "costura", fontsize=fs, va="bottom", ha="right")
    ax.set_xlim(-10, des + 10)
    ax.set_ylim(-14, H + 16)
    ax.set_aspect("equal")
    ax.axis("off")


def fig_mapas(ruta, claves, filas, cols, tam):
    fig, axs = plt.subplots(filas, cols, figsize=tam)
    for ax, k in zip(axs.flat, claves):
        _mapa(ax, k)
        m = marcado(k)
        ax.set_title(f"{NOMBRE[k]} · cuerpo desarrollado {n(m['des'], 0)} × {n(CUERPOS[k]['alto'], 0)} mm · "
                     f"faja {n(m['faja_alto'], 0)} × {n(m['faja_largo'], 0)}", fontsize=7.5)
    return _guardar(fig, ruta)


def fig_faja(ruta):
    """5 kg: plano actual (la faja tapa la franja) contra la faja abierta propuesta."""
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    _mapa(axs[0], "5kg", "actual")
    axs[0].set_title("Plano actual del sustituto: faja de 40 mm en todo el perímetro\n→ tapa la franja (línea roja)",
                     fontsize=7.5)
    _mapa(axs[1], "5kg", "propuesta")
    axs[1].set_title("Propuesta: faja de 40 mm abierta\n5 mm antes y después de la franja", fontsize=7.5)
    return _guardar(fig, ruta)


def _x(u, uc, R):
    """Proyección en vista de frente de un punto del cuerpo a arco u, mirando el meridiano uc."""
    return R * math.sin((u - uc) / R)


def _banda(ax, u0, u1, z0, z1, uc, R, des, **kw):
    """Dibuja la parte visible (±90°) de una banda del cuerpo en la vista que mira el meridiano uc."""
    for sh in (-des, 0, des):
        a, b = max(u0 + sh, uc - math.pi * R / 2), min(u1 + sh, uc + math.pi * R / 2)
        if b <= a:
            continue
        us = [a + (b - a) * i / 24 for i in range(25)]
        pts = [(_x(u, uc, R), z0) for u in us] + [(_x(u, uc, R), z1) for u in reversed(us)]
        ax.add_patch(Polygon(pts, closed=True, **kw))


def _vista(ax, k, uc, titulo):
    c, m = CUERPOS[k], marcado(k)
    R, H, des = c["R"], c["alto"], m["des"]
    ax.add_patch(Rectangle((-R, 0), 2 * R, H, fc="#F7F7F7", ec=OSC, lw=1))
    cup = [(-R, H)] + [(R * math.cos(t), H + R * 0.45 * math.sin(t)) for t in
                       [math.pi - j * math.pi / 30 for j in range(31)]] + [(R, H)]
    ax.add_patch(Polygon(cup, closed=True, fc="#E7E6E6", ec=OSC, lw=1))
    e = c["etiqueta"]
    _banda(ax, -e["ancho"] / 2, e["ancho"] / 2, e["z0"], e["z1"], uc, R, des, fc=ETQ, ec=GRIS, lw=0.6)
    for key, col in (("oblea_pba", OBL), ("sello_iram", SEL), ("tarjeta_caba", TAR)):
        if key in c:
            _banda(ax, c[key]["s0"], c[key]["s1"], c[key]["z0"], c[key]["z1"], uc, R, des, fc=col, ec=OSC, lw=0.4)
    q = c["etiqueta_serie"]
    _banda(ax, des / 2 - 22.5, des / 2 + 22.5, q["z0"], q["z1"], uc, R, des, fc=QR, ec=OSC, lw=0.4)
    for a, b in m["tramos"]:
        _banda(ax, a, b, 0, m["faja_alto"], uc, R, des, fc=FAJA_C, ec="#B08900", lw=0.5, alpha=0.9)
    _banda(ax, m["u0"], m["u1"], m["z0"], m["z1"], uc, R, des, fc="#F4D7D3", ec=ROJO, lw=1.1)
    if "triangulos" in c:
        t = c["triangulos"]
        for s in (t["s"], -t["s"]):
            if math.cos((s - uc) / R) > 0:
                x = _x(s, uc, R)
                ax.add_patch(Polygon([(x, t["z0"]), (x, t["z1"]), (x * 1.25, t["z0"])], closed=True, fc="#595959",
                                     ec="#595959"))
    if math.cos(uc / R) > 0:
        ax.plot([_x(0, uc, R)] * 2, [0, H], color=OSC, lw=1.6, ls=(0, (4, 2)))
        ax.text(_x(0, uc, R) + 3, H * 0.9, "costura", fontsize=6, rotation=90, va="top")
    ax.set_title(titulo, fontsize=7.5)
    ax.set_xlim(-R - 30, R + 30)
    ax.set_ylim(-10, H + R * 0.5 + 10)
    ax.set_aspect("equal")
    ax.axis("off")


def fig_vistas(ruta):
    fig, axs = plt.subplots(1, 4, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1, 1, 1.6, 1.6]})
    d5 = marcado("5kg")["des"]
    _vista(axs[0], "5kg", 0.0, "5 kg · lado costura y etiqueta")
    _vista(axs[1], "5kg", d5 / 2, "5 kg · lado opuesto (pared)")
    _vista(axs[2], "25kg", 60.0, "25 kg · lado etiqueta y manija")
    _vista(axs[3], "25kg", marcado("25kg")["des"] / 2, "25 kg · lado manga")
    fig.text(0.5, 0.02, "Manuales: la franja queda del lado de la pared, bajo el QR de serie, y la faja la rodea sin "
                        "taparla. Carros: la franja va al lado de la costura, encima de los triángulos del eje; "
                        "la faja queda abajo.", ha="center", fontsize=7.5)
    return _guardar(fig, ruta)


def fig_profundidad(ruta):
    """Corte de la pared con la huella del punzón, la pintura y el límite de profundidad (criterio)."""
    fig, axs = plt.subplots(1, 3, figsize=(10, 2.8))
    casos = [("1 kg: pared a presión e 0,9", 0.9, 0.09, "≤ 10 % de e"),
             ("2,5–10 kg: pollera sin presión e 1,25–2,0", 1.6, 0.22, "≈ 3 × pintura"),
             ("Carros: pared a presión e 3,2–4,75", 3.2, 0.30, "≤ 10 % de e y ≥ 3 × pintura")]
    pint = 0.07
    for ax, (tit, e, p, crit) in zip(axs, casos):
        L = 2.4
        ax.add_patch(Rectangle((0, 0), L, e, fc="#D9D9D9", ec=OSC, lw=1))
        ax.add_patch(Rectangle((0, e), L, pint, fc=NAR, ec=ROJO, lw=0.6))
        for x in (0.6, 1.2, 1.8):
            ax.add_patch(Polygon([(x - p * 0.9, e + pint), (x, e - p), (x + p * 0.9, e + pint)], closed=True,
                                 fc="white", ec=OSC, lw=0.8))
        ax.annotate("", (2.5, e), (2.5, e - p), arrowprops=dict(arrowstyle="<->", lw=0.6))
        ax.text(2.57, e - p / 2, f"{str(p).replace('.', ',')} mm", fontsize=6.5, va="center")
        ax.text(0.05, e + pint + 0.03 * e + 0.02, "pintura 70 µm", fontsize=6, color=ROJO)
        ax.text(1.6, -0.12 * max(e, 1.6) - 0.05, f"{tit}\nprofundidad: {crit}", ha="center", va="top", fontsize=7)
        ax.set_xlim(-0.1, 3.4)
        ax.set_ylim(-0.6 * max(e, 1.6), e + 0.35)
        ax.axis("off")
    fig.text(0.5, 1.0, "Huella de la micropercusión (esquema, sin escala horizontal)", ha="center", fontsize=8.5)
    return _guardar(fig, ruta)


def _caja(ax, x, y, w, h, txt, fc, fs=7, neg=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=OSC, lw=0.9))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, weight="bold" if neg else "normal",
            wrap=True)


def _flecha(ax, p, q, txt="", color=OSC, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, lw=0.9, color=color, ls=ls))
    if txt:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.12, txt, ha="center", fontsize=6, color=color)


def fig_intraplanta(ruta):
    """Estados del recipiente en planta y compuertas (gates) que bloquean el paso si no se cumple la ficha."""
    fig, ax = plt.subplots(figsize=(11, 4.4))
    est = [("CORTADO\ny GRABADO", "G2 + Pannier"), ("CONFORMADO", "cilindrado,\nsoldaduras"),
           ("PROBADO", "PH 100 %"), ("TERMINADO\n(pintado)", "granallado,\ndefectos, pintura"),
           ("CARGADO", "polvo, válvula,\nN₂"), ("APROBADO", "pérdidas,\ncontrol final"),
           ("IDENTIFICADO", "etiqueta QR =\ngrabado"), ("EMBALADO", "caja → pallet\n(agregación)")]
    w, h, sx = 1.15, 0.75, 1.42
    for i, (e, sub) in enumerate(est):
        x = 0.2 + i * sx
        _caja(ax, x, 2.2, w, h, e, VERDE if i < 7 else AZUL, 7, True)
        ax.text(x + w / 2, 1.95, sub, ha="center", va="top", fontsize=6.2, color=OSC)
        if i:
            _flecha(ax, (x - sx + w, 2.2 + h / 2), (x, 2.2 + h / 2))
    for i in (2, 5, 6):
        x = 0.2 + i * sx + w / 2
        ax.text(x, 3.15, "GATE", ha="center", fontsize=6.5, color="white", weight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc=ROJO, ec="none"))
    # cilindro vacío y rechazos
    xc = 0.2 + 3 * sx + w / 2
    xe = 0.2 + 7 * sx + w / 2
    _caja(ax, 0.2 + 3 * sx, 0.25, w, 0.6, "CILINDRO\nVACÍO", AZUL, 6.5, True)
    _flecha(ax, (xc, 1.55), (xc, 0.85))
    ax.text(xc + 0.08, 1.2, "si se vende vacío", ha="left", va="center", fontsize=6)
    ax.plot([0.2 + 3 * sx + w, xe], [0.55, 0.55], color=OSC, lw=0.9)
    _flecha(ax, (xe, 0.55), (xe, 1.5))
    ax.text((0.2 + 3 * sx + w + xe) / 2, 0.62, "se identifica y embala igual (sin carga ni gate de pérdidas)",
            ha="center", fontsize=6)
    _caja(ax, 0.2 + 0.3 * sx, 0.25, w * 1.45, 0.6, "RECHAZO: retrabajo\no ANULADO (chatarra)", NAR, 6.5, True)
    _flecha(ax, (0.2 + 2 * sx + 0.25, 1.55), (0.2 + 0.3 * sx + w * 1.45, 0.6), color=ROJO, ls="--")
    ax.text(0.2 + 1.55 * sx, 1.25, "no aprueba un gate", ha="center", fontsize=6, color=ROJO)
    ax.text(0.2, 3.55, "Cada flecha = una lectura del grabado en el puesto. El puesto solo acepta el recipiente si "
                       "el estado anterior está aprobado y la ficha del modelo se cumple.", fontsize=7.5)
    ax.set_xlim(0, 0.2 + 8 * sx)
    ax.set_ylim(0, 3.8)
    ax.axis("off")
    return _guardar(fig, ruta)


def fig_extraplanta(ruta):
    """Cadena de custodia: cada traspaso es una doble lectura (sale / entra) con su documento."""
    fig, ax = plt.subplots(figsize=(11, 3.3))
    act = [("FLAMA\n(despacho)", AZUL), ("TRANSPORTISTA", AMAR), ("DISTRIBUIDOR /\nREVENDEDOR", AMAR),
           ("INSTALADOR", AMAR), ("CLIENTE\n(llave en mano)", VERDE)]
    docs = ["remito + factura\ncarta de porte (art. 1298)\nCOT ARBA si corresponde",
            "entrega con\nremito y guía", "remito del\ndistribuidor", "acta de entrega\ny ubicación"]
    w, h, sx = 1.55, 0.85, 2.25
    for i, (a, c) in enumerate(act):
        _caja(ax, 0.2 + i * sx, 1.6, w, h, a, c, 7.5, True)
        if i:
            x0 = 0.2 + (i - 1) * sx + w
            _flecha(ax, (x0, 2.03), (0.2 + i * sx, 2.03))
            ax.text((x0 + 0.2 + i * sx) / 2, 1.25, docs[i - 1], ha="center", va="top", fontsize=6.2)
            ax.text((x0 + 0.2 + i * sx) / 2, 2.12, "sale ✓\nentra ✓", ha="center", va="bottom", fontsize=6, color=ROJO)
    ax.text(0.2, 2.85, "Se escanea el pallet (SSCC) y el sistema sabe qué series lleva; si el pallet se abre, se "
                       "escanea cada equipo. Faltantes y daños se registran con foto en el mismo traspaso.",
            fontsize=7.5)
    ax.set_xlim(0, 0.2 + 4 * sx + w + 0.2)
    ax.set_ylim(0.55, 3.1)
    ax.axis("off")
    return _guardar(fig, ruta)


def fig_retorno(ruta):
    """Ciclo de vida en servicio: retorno, recarga con nueva revisión de ficha, devolución y baja."""
    fig, ax = plt.subplots(figsize=(11, 4.0))
    _caja(ax, 0.2, 1.6, 1.7, 0.8, "EN SERVICIO\nen la propiedad", VERDE, 7.5, True)
    _caja(ax, 2.5, 2.7, 1.9, 0.8, "RETIRO\n(se deja sustituto\ncon faja amarilla)", AMAR, 7, True)
    _caja(ax, 5.0, 2.7, 1.9, 0.8, "RECEPCIÓN en recargas\nfoto + visión + lectura", AMAR, 7, True)
    _caja(ax, 7.5, 2.7, 1.9, 0.8, "SERVICIO\nrecarga · PH · pintura", AMAR, 7, True)
    _caja(ax, 7.5, 1.2, 1.9, 0.8, "FICHA rev. n+1\n(re-especificación)", AZUL, 7, True)
    _caja(ax, 5.0, 1.2, 1.9, 0.8, "DEVOLUCIÓN\n(se retira el sustituto)", AMAR, 7, True)
    _caja(ax, 10.0, 2.7, 1.6, 0.8, "INUTILIZACIÓN\n9.12 + acta anexo G", NAR, 7, True)
    _caja(ax, 10.0, 1.2, 1.6, 0.8, "BAJA\n(serie bloqueado)", NAR, 7, True)
    _flecha(ax, (1.9, 2.25), (2.5, 3.0))
    ax.text(0.25, 2.95, "recarga anual, PH,\nuso, daño, recall", fontsize=6, color=OSC)
    _flecha(ax, (4.4, 3.1), (5.0, 3.1))
    _flecha(ax, (6.9, 3.1), (7.5, 3.1), "apto")
    _flecha(ax, (8.45, 2.7), (8.45, 2.0))
    _flecha(ax, (7.5, 1.6), (6.9, 1.6))
    _flecha(ax, (5.0, 1.6), (1.9, 1.85))
    _flecha(ax, (9.4, 3.1), (10.0, 3.1), "no apto")
    ax.plot([5.95, 5.95, 10.8], [3.5, 3.72, 3.72], color=ROJO, lw=0.9, ls="--")
    _flecha(ax, (10.8, 3.72), (10.8, 3.5), "", ROJO, "--")
    ax.text(8.45, 3.77, "no apto en recepción (corrosión, golpe, fin de vida)", ha="center", fontsize=6, color=ROJO)
    _flecha(ax, (10.8, 2.7), (10.8, 2.0))
    ax.text(0.2, 0.55, "Seguros: cada estado deja evidencia fechada (fotos, servicio vigente, ubicación) que se puede "
                       "mostrar a la aseguradora o al perito con el mismo QR.", fontsize=7.5)
    ax.set_xlim(0, 11.8)
    ax.set_ylim(0.3, 3.95)
    ax.axis("off")
    return _guardar(fig, ruta)


def _celular(ax, x0, titulo, filas, pie, color_pie):
    """Maqueta de pantalla de la app del puesto (celular en el soporte)."""
    w, h = 3.0, 5.6
    ax.add_patch(FancyBboxPatch((x0, 0), w, h, boxstyle="round,pad=0.02,rounding_size=0.25", fc="#202020", ec="none"))
    ax.add_patch(Rectangle((x0 + 0.12, 0.35), w - 0.24, h - 0.7, fc="white", ec="none"))
    ax.add_patch(Rectangle((x0 + 0.12, h - 0.95), w - 0.24, 0.6, fc="#1F4E79", ec="none"))
    ax.text(x0 + w / 2, h - 0.65, titulo, ha="center", va="center", fontsize=6.6, color="white", weight="bold")
    y = h - 1.2
    for et, val, ok in filas:
        ax.text(x0 + 0.22, y, et, fontsize=5.5, va="top", color="#595959")
        col = {True: "#2E7D32", False: ROJO, None: OSC}[ok]
        ax.text(x0 + w - 0.22, y, val, fontsize=5.7, va="top", ha="right", color=col, weight="bold")
        y -= 0.3
    ax.add_patch(FancyBboxPatch((x0 + 0.3, 0.5), w - 0.6, 0.45, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc=color_pie, ec="none"))
    ax.text(x0 + w / 2, 0.725, pie, ha="center", va="center", fontsize=6.3, color="white", weight="bold")


def fig_app(ruta):
    fig, ax = plt.subplots(figsize=(10, 5.0))
    _celular(ax, 0.2, "Puesto 14 · Prueba hidráulica", [
        ("Serie (leído del grabado)", "26-000123", None), ("Modelo", "ABC 5 kg", None),
        ("Estado anterior", "CONFORMADO ✓", True), ("Espesor (puesto 13)", "1,62 ≥ 1,60 ✓", True),
        ("Presión de ensayo (ficha)", "3,5 MPa", None), ("Presión medida (banco)", "3,52 MPa ✓", True),
        ("Tiempo a presión (ficha ≥ 60 s)", "62 s ✓", True), ("Caída de presión", "no ✓", True),
        ("Pérdidas visibles", "no ✓", True), ("Deformación permanente", "no ✓", True),
        ("Banco / patrón", "PH-1 / cal. 03/26", None), ("Operario", "legajo 112", None)], "CUMPLE → PROBADO", "#2E7D32")
    _celular(ax, 3.6, "Puesto 24 · Etiquetado", [
        ("Serie (grabado)", "26-000123", None), ("Estado anterior", "APROBADO ✓", True),
        ("Masa total (ficha 8,50 kg)", "8,62 kg ✓", True), ("Carga polvo (5,00 0/+0,30)", "5,14 kg ✓", True),
        ("Presión (1,4 MPa a 20 °C)", "1,40 ✓", True), ("Pérdidas (puesto 23)", "sin pérdida ✓", True),
        ("Etiqueta impresa", "QR 26-000123", None), ("Lectura del QR pegado", "26-000123", None),
        ("QR = grabado", "sí ✓", True), ("Sello IRAM / oblea", "A26 1111053 / 457", None),
        ("Precinto", "lote P-2603", None), ("Foto control final", "visión OK", True)],
        "CUMPLE → IDENTIFICADO", "#2E7D32")
    _celular(ax, 7.0, "Recargas · Recepción", [
        ("Serie (grabado)", "26-000123", None), ("Rev. de ficha", "3", None),
        ("Fabricado", "03/2026", None), ("Vida útil (20 años)", "hasta 03/2046 ✓", True),
        ("Última PH", "03/2026", None), ("PH vence", "03/2031", None),
        ("Agente de la ficha", "ABC (no convertir)", None), ("Corrosión (visión + operario)", "sí ✗", False),
        ("Golpe / abolladura", "no", True), ("Reparación por soldadura", "no", True),
        ("Regla IRAM 3517-2 9.7.1.3 b)", "inutilizar", False), ("Foto", "adjunta", None)],
        "NO APTO → INUTILIZACIÓN", ROJO)
    ax.text(5.15, 5.85, "La app muestra la ficha del modelo para ese puesto, toma los valores (a mano, balanza o banco) "
                        "y decide con la regla escrita en la ficha", ha="center", fontsize=7.5)
    ax.set_xlim(0, 10.2)
    ax.set_ylim(-0.1, 6.1)
    ax.set_aspect("equal")
    ax.axis("off")
    return _guardar(fig, ruta)


def fig_revendidos(ruta):
    fig, ax = plt.subplots(figsize=(11, 3.6))
    _caja(ax, 0.1, 1.5, 1.6, 0.8, "LLEGA el revendido\n(remito + lista\nde series)", AZUL, 6.5, True)
    _caja(ax, 2.3, 1.5, 1.9, 0.8, "¿Tiene grabado\nfabricante + n° + año\nlegible?", AMAR, 6.5, True)
    _caja(ax, 2.3, 0.1, 1.9, 0.75, "NO: no conforme\n(9.11 y anexo F: no se\npuede ni recargar)", NAR, 6.2, True)
    _caja(ax, 4.8, 1.5, 1.9, 0.8, "Foto + lectura\n(OCR o tipeo) del grabado\n+ cruce con la lista", AMAR, 6.5, True)
    _caja(ax, 7.3, 1.5, 1.8, 0.8, "Alta: clave =\nfabricante + n° + año\n→ ID FLAMA R-…", VERDE, 6.5, True)
    _caja(ax, 9.7, 1.5, 1.6, 0.8, "Etiqueta QR\nde vinilo destructible\n+ stock", VERDE, 6.5, True)
    _caja(ax, 4.8, 0.1, 1.9, 0.75, "Reclamo al proveedor\n(devolución o\nreemplazo)", NAR, 6.2, True)
    _flecha(ax, (1.7, 1.9), (2.3, 1.9))
    _flecha(ax, (4.2, 1.9), (4.8, 1.9), "sí")
    _flecha(ax, (3.25, 1.5), (3.25, 0.85), "")
    ax.text(3.32, 1.17, "no", fontsize=6, color=ROJO)
    _flecha(ax, (4.2, 0.48), (4.8, 0.48))
    _flecha(ax, (6.7, 1.9), (7.3, 1.9))
    _flecha(ax, (9.1, 1.9), (9.7, 1.9))
    ax.text(0.1, 2.75, "El revendido se identifica con SU grabado (el del fabricante): FLAMA no graba un recipiente "
                       "ajeno; le pone una etiqueta con QR que apunta a ese grabado.", fontsize=7.5)
    ax.set_xlim(0, 11.4)
    ax.set_ylim(0, 3.0)
    ax.axis("off")
    return _guardar(fig, ruta)


def todas(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    f = {}
    for k, fn in (("contenido", fig_contenido), ("vistas", fig_vistas), ("faja", fig_faja),
                  ("profundidad", fig_profundidad), ("intraplanta", fig_intraplanta), ("app", fig_app),
                  ("extraplanta", fig_extraplanta), ("retorno", fig_retorno), ("revendidos", fig_revendidos)):
        f[k] = fn(os.path.join(carpeta, f"{k}.png"))
    for i, par in enumerate((["1kg", "2.5kg"], ["5kg", "10kg"], ["25kg", "50kg"], ["70kg", "100kg"]), 1):
        f[f"mapas_{i}"] = fig_mapas(os.path.join(carpeta, f"mapas_{i}.png"), par, 1, 2, (11, 4.4))
    return f


if __name__ == "__main__":
    print(todas(os.path.join(AQUI, "_figs")))
