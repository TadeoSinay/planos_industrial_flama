"""Figuras del Word del sistema de trazabilidad (matplotlib). Medidas de los cuerpos: Excel de corte, hoja Piezas;
alto de la pollera bajo el fondo: catálogo de los planos (zf_borde)."""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
ROJO, GRIS, OSC, AZUL, VERDE, AMAR, NAR = "#C0392B", "#BFBFBF", "#333333", "#DDEBF7", "#E2EFDA", "#FFF2CC", "#F8CBAD"

# (modelo, Ø ext, espesor, alto del cuerpo, desarrollo, pollera bajo el fondo, franja: base y alto, profundidad)
MODELOS = [("1 kg", 76.2, 0.9, 263.5, 236.5, 0.0, 14.0, 13.0, "0,08–0,10"),
           ("2,5 kg", 124.0, 1.25, 267.5, 385.5, 16.0, 2.0, 12.0, "0,20–0,25"),
           ("5 kg", 153.0, 1.6, 327.5, 475.5, 21.5, 4.5, 12.0, "0,20–0,25"),
           ("10 kg", 181.5, 2.0, 493.0, 564.0, 16.5, 2.0, 12.0, "0,20–0,25"),
           ("25 / 50 kg", 276.5, 3.2, 493.0, 858.5, 0.0, 35.0, 14.0, "0,30"),
           ("70 / 100 kg", 390.0, 4.75, 680.0, 1210.5, 0.0, 35.0, 14.0, "0,40–0,45")]
DM_MOD, DM_CELDA = 18, 0.6           # DataMatrix ECC 200 18 × 18 módulos, celda 0,6 mm
TXT_H = 5.0                          # alto de letra del marcado (planos: MARCA_H)
DPS = (15.0, 7.0)                    # cuño DPS (Res. 349/07 anexo IV)


def _guardar(fig, ruta):
    fig.savefig(ruta, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


def _datamatrix(ax, x0, y0, celda, n=DM_MOD, semilla=7):
    """DataMatrix ilustrativo (patrón de búsqueda en L + reloj + celdas pseudoaleatorias)."""
    import random
    rnd = random.Random(semilla)
    for i in range(n):
        for j in range(n):
            borde_l = i == 0 or j == 0
            reloj = (i == n - 1 and j % 2 == 0) or (j == n - 1 and i % 2 == 0)
            if borde_l or reloj or (0 < i < n - 1 and 0 < j < n - 1 and rnd.random() < 0.5):
                ax.add_patch(Rectangle((x0 + j * celda, y0 + i * celda), celda * 0.92, celda * 0.92, color="black",
                                       lw=0))


def fig_contenido(ruta):
    """Distribución del marcado en la franja: DataMatrix + texto IRAM 5.1 + cuño DPS, a escala."""
    fig, ax = plt.subplots(figsize=(9.5, 2.6))
    ancho, alto = 128.0, 12.0
    ax.add_patch(Rectangle((0, 0), ancho, alto, fc="#F4D7D3", ec=ROJO, lw=1.2))
    lado = DM_MOD * DM_CELDA
    _datamatrix(ax, 2.0, (alto - lado) / 2, DM_CELDA)
    ax.text(2.0 + lado + 3, alto / 2, "FLAMA S.A.   N° 26-000123   26", fontsize=11.5, va="center",
            family="DejaVu Sans Mono", weight="bold")
    ax.add_patch(Rectangle((ancho - DPS[0] - 3, (alto - DPS[1]) / 2), DPS[0], DPS[1], fc="white", ec="black", lw=1))
    ax.text(ancho - DPS[0] / 2 - 3, alto / 2, "DPS", ha="center", va="center", fontsize=10, weight="bold")
    # cotas
    kw = dict(arrowstyle="<->", lw=0.6, color=OSC)
    ax.annotate("", (2, -2.5), (2 + lado, -2.5), arrowprops=kw)
    ax.text(2 + lado / 2, -4.6, f"{lado:.1f} mm".replace(".", ",") + f" ({DM_MOD}×{DM_MOD} celdas de {str(DM_CELDA).replace('.', ',')} mm)",
            ha="center", fontsize=7)
    ax.annotate("", (ancho - DPS[0] - 3, -2.5), (ancho - 3, -2.5), arrowprops=kw)
    ax.text(ancho - DPS[0] / 2 - 3, -4.6, "15 × 7 mm", ha="center", fontsize=7)
    ax.annotate("", (ancho + 2.5, 0), (ancho + 2.5, alto), arrowprops=kw)
    ax.text(ancho + 3.5, alto / 2, "franja 12 mm\n(14 en carros)", va="center", fontsize=7)
    ax.text(60, alto + 2.2, "letra 5 mm (fabricante · n° de recipiente · año, IRAM 3523 / 3550 5.1)", ha="center",
            fontsize=7.5, color=OSC)
    ax.set_xlim(-3, ancho + 22)
    ax.set_ylim(-7, alto + 5)
    ax.set_aspect("equal")
    ax.axis("off")
    return _guardar(fig, ruta)


def fig_ubicacion(ruta):
    """Vista de frente de cada cuerpo con la franja de marcado (rojo) y la costura atrás."""
    fig, axs = plt.subplots(1, 6, figsize=(11, 4.2), gridspec_kw={"width_ratios": [max(m[1], 170) + 60 for m in MODELOS]})
    esc = max(m[3] for m in MODELOS)
    for ax, (nom, d, e, h, des, pol, fb, fh, prof) in zip(axs, MODELOS):
        r = d / 2
        ax.add_patch(Rectangle((-r, 0), d, h, fc="#F2F2F2", ec=OSC, lw=1))
        # cúpula y fondo esquemáticos
        cup = [(-r, h)] + [(r * math.cos(t), h + r * 0.45 * math.sin(t)) for t in
                           [math.pi - k * math.pi / 30 for k in range(31)]] + [(r, h)]
        ax.add_patch(Polygon(cup, closed=True, fc="#E7E6E6", ec=OSC, lw=1))
        if pol:
            ax.plot([-r, r], [pol, pol], ls="--", lw=0.8, color=OSC)
            ax.text(0, pol / 2, "fondo", ha="center", va="center", fontsize=5.5, color=OSC)
        ax.add_patch(Rectangle((-r * 0.85, fb), r * 1.7, fh, fc=NAR, ec=ROJO, lw=1.2))
        # etiqueta (gris) en el centro
        ax.add_patch(Rectangle((-r * 0.9, h * 0.35), r * 1.8, h * 0.4, fc="white", ec=GRIS, lw=0.8, ls=":"))
        ax.text(0, h * 0.55, "etiqueta", ha="center", va="center", fontsize=6, color="#7F7F7F")
        ax.text(0, -esc * 0.045, nom, ha="center", va="top", fontsize=8.5, weight="bold")
        ax.text(0, -esc * 0.1, f"e {str(e).replace('.', ',')} mm\nprof. {prof} mm", ha="center",
                va="top", fontsize=6.5)
        lugar = "pollera (sin presión)" if pol else "franja baja del cuerpo"
        ax.text(0, -esc * 0.2, lugar, ha="center", va="top", fontsize=6.3, color=ROJO)
        ax.annotate("", (r + 6, 0), (r + 6, fb + fh), arrowprops=dict(arrowstyle="<->", lw=0.5))
        ax.text(r + 9, (fb + fh) / 2, f"{fb:g}–{fb + fh:g}".replace(".", ","), fontsize=6, va="center")
        half = max(r, 85) + 20
        ax.set_xlim(-half, half + 25)
        ax.set_ylim(-esc * 0.26, esc * 1.15)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.5, 0.97, "Vista de frente: la franja va adelante y abajo, a 180° de la costura longitudinal (atrás), "
                        "debajo de la etiqueta", ha="center", fontsize=8.5)
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
        for k, x in enumerate((0.6, 1.2, 1.8)):
            ax.add_patch(Polygon([(x - p * 0.9, e + pint), (x, e - p), (x + p * 0.9, e + pint)], closed=True,
                                 fc="white", ec=OSC, lw=0.8))
        ax.annotate("", (2.5, e), (2.5, e - p), arrowprops=dict(arrowstyle="<->", lw=0.6))
        ax.text(2.57, e - p / 2, f"{str(p).replace('.', ',')} mm", fontsize=6.5, va="center")
        ax.text(0.05, e + pint + 0.03 * e + 0.02, "pintura 70 µm", fontsize=6, color=ROJO)
        ax.text(1.6, -0.12 * max(e, 1.6) - 0.05, f"{tit}\nprofundidad: {crit}", ha="center", va="top",
                fontsize=7)
        ax.set_xlim(-0.1, 3.4)
        ax.set_ylim(-0.6 * max(e, 1.6), e + 0.35)
        ax.axis("off")
    fig.text(0.5, 1.0, "Huella de la micropercusión (esquema, sin escala horizontal)", ha="center", fontsize=8.5)
    return _guardar(fig, ruta)


def fig_planchuela(ruta):
    """Planchuela plana a la salida de la guillotina 2: posición de la franja respecto de los bordes."""
    fig, ax = plt.subplots(figsize=(8, 3.4))
    des, alto = 475.5, 327.5             # 5 kg
    ax.add_patch(Rectangle((0, 0), des, alto, fc="#F2F2F2", ec=OSC, lw=1.2))
    ax.add_patch(Rectangle((des / 2 - 64, 4.5), 128, 12, fc=NAR, ec=ROJO, lw=1.2))
    ax.text(des / 2, 26, "franja de marcado (cara exterior)", ha="center", fontsize=7.5, color=ROJO)
    for x in (0, des):
        ax.plot([x, x], [0, alto], lw=3, color="#7F7F7F")
    ax.text(4, alto / 2, "borde de costura", rotation=90, va="center", fontsize=7)
    ax.text(des - 14, alto / 2, "borde de costura", rotation=90, va="center", fontsize=7)
    kw = dict(arrowstyle="<->", lw=0.6, color=OSC)
    ax.annotate("", (0, -14), (des / 2, -14), arrowprops=kw)
    ax.text(des / 4, -32, "desarrollo / 2 (frente del matafuego)", ha="center", fontsize=7)
    ax.text(des / 2, alto + 10, "tope de la mesa de la Pannier: borde inferior y borde de costura; la franja cae "
                                "siempre adelante y abajo", ha="center", fontsize=7.5)
    ax.text(des / 2, alto / 2, "5 kg: 475,5 × 327,5 × 1,6 mm\n(se cilindra con esta cara hacia afuera)", ha="center",
            va="center", fontsize=8, color=OSC)
    ax.set_xlim(-20, des + 20)
    ax.set_ylim(-42, alto + 22)
    ax.set_aspect("equal")
    ax.axis("off")
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


def todas(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    f = {}
    for k, fn in (("contenido", fig_contenido), ("ubicacion", fig_ubicacion), ("profundidad", fig_profundidad),
                  ("planchuela", fig_planchuela), ("intraplanta", fig_intraplanta),
                  ("extraplanta", fig_extraplanta), ("retorno", fig_retorno)):
        f[k] = fn(os.path.join(carpeta, f"{k}.png"))
    return f


if __name__ == "__main__":
    print(todas(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figs")))
