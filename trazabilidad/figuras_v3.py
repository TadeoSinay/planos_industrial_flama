"""Figuras de la versión 3 del sistema de trazabilidad: profundidad a escala real, planta angular, hoja de ruta del
lote, etiquetas con QR reales (segno), arquitectura, pasos intra y extraplanta, pantallas y vida de la etiqueta."""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import segno  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle, Wedge  # noqa: E402

import figuras_trazabilidad as FT  # noqa: E402

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
OSC, ROJO, AZUL, VERDE, AMAR, NAR, GRIS = "#333333", "#C0392B", "#DDEBF7", "#E2EFDA", "#FFF2CC", "#F8CBAD", "#BFBFBF"
AZ_O, VE_O = "#1F4E79", "#2E7D32"
URL = "https://trazabilidad-flama.vercel.app/m/"     # dominio de la app (fase 1); el QR lleva URL + serie


def _g(fig, ruta):
    fig.savefig(ruta, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


def _qr(ax, texto, x, y, lado, borde=True):
    """QR real (segno) dibujado en (x, y) con lado en unidades del eje; se puede escanear desde el Word."""
    q = segno.make(texto, error="m")
    m = q.matrix
    n = len(m)
    c = lado / n
    if borde:
        ax.add_patch(Rectangle((x, y), lado, lado, fc="white", ec="none"))
    for i, fila in enumerate(m):
        for j, v in enumerate(fila):
            if v:
                ax.add_patch(Rectangle((x + j * c, y + (n - 1 - i) * c), c * 1.02, c * 1.02, color="black", lw=0))


def _caja(ax, x, y, w, h, txt, fc, fs=7, neg=False, ec=OSC, color="black"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=0.9))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, weight="bold" if neg else "normal",
            color=color)


def _fl(ax, p, q, txt="", color=OSC, ls="-", fs=6, dy=0.1):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, lw=0.9, color=color, ls=ls))
    if txt:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, txt, ha="center", fontsize=fs, color=color)


# ----------------------------------------------------------------------------------------------- profundidad
def fig_profundidad(ruta):
    """Corte de pared a escala real ampliada 25:1: pared, pintura y tres huellas del punzón por caso."""
    casos = [("1 kg · pared a presión", 0.9, 0.09, "10 %"), ("2,5 a 10 kg · pollera (5 kg: e 1,6)", 1.6, 0.22, "14 %"),
             ("25 / 50 kg · pared a presión", 3.2, 0.30, "9 %"), ("70 / 100 kg · pared a presión", 4.75, 0.45, "9 %")]
    fig, axs = plt.subplots(1, 4, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1, 1, 1, 1]})
    pint, celda = 0.07, 0.6
    for ax, (tit, e, p, pct) in zip(axs, casos):
        L = 2.4
        ax.add_patch(Rectangle((0, -e), L, e, fc="#CFCFCF", ec=OSC, lw=1))
        ax.text(L / 2, -e / 2, f"chapa {FT.n(e, 2)} mm", ha="center", va="center", fontsize=7, color="#555555")
        ax.add_patch(Rectangle((0, 0), L, pint, fc="#B3201E", ec="none"))
        for k in range(3):
            xc = 0.6 + k * celda
            r = celda * 0.42                                     # huella de ~0,5 mm en una celda de 0,6 mm
            ax.add_patch(Polygon([(xc - r, pint), (xc - r * 0.85, 0), (xc, -p), (xc + r * 0.85, 0), (xc + r, pint)],
                                 closed=True, fc="#B3201E", ec=OSC, lw=0.6))
        ax.annotate("", (2.25, 0), (2.25, -p), arrowprops=dict(arrowstyle="<->", lw=0.8, color=ROJO))
        ax.text(2.31, -p / 2, f"{FT.n(p, 2)} mm", fontsize=7, color=ROJO, va="center")
        ax.annotate("", (0.6, pint + 0.18), (1.2, pint + 0.18), arrowprops=dict(arrowstyle="<->", lw=0.6))
        ax.text(0.9, pint + 0.24, "0,6 mm (celda)", ha="center", fontsize=6)
        ax.text(0.05, pint + 0.02, "pintura 0,07", fontsize=5.5, color="#B3201E", va="bottom")
        queda = e - p
        ax.text(L / 2, -e - 0.25, f"{tit}\nperfora {FT.n(p, 2)} de {FT.n(e, 2)} mm ({pct})\nquedan "
                                  f"{FT.n(queda, 2)} mm de pared", ha="center", va="top", fontsize=7.2)
        ax.set_xlim(-0.05, 3.0)
        ax.set_ylim(-5.9, 0.6)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.5, 0.97, "Corte de la pared A ESCALA (los cuatro con la misma escala, ampliados ≈ 25 veces): la huella "
                        "es un cráter de ~0,5 mm de diámetro por celda del DataMatrix", ha="center", fontsize=8.5)
    return _g(fig, ruta)


# ----------------------------------------------------------------------------------------------- planta angular
def fig_planta(ruta):
    """Vista desde arriba: en qué ángulo va cada cosa (costura a 0°, la franja enfrente, etc.)."""
    fig, axs = plt.subplots(1, 3, figsize=(11, 4.2))
    for ax, k in zip(axs, ["1kg", "5kg", "25kg"]):
        c, m = FT.CUERPOS[k], FT.marcado(k)
        R = c["R"]

        def ang(u):                        # grados de la vista superior: costura arriba (90°), sentido antihorario
            return 90 - math.degrees(u / R)

        def arco(u0, u1, r0, r1, col, txt=None, rt=None):
            a0, a1 = sorted((ang(u0), ang(u1)))
            ax.add_patch(Wedge((0, 0), r1, a0, a1, width=r1 - r0, fc=col, ec=OSC, lw=0.5))
            if txt:
                am = math.radians((a0 + a1) / 2)
                rr = rt or r1 + R * 0.28
                ax.text(rr * math.cos(am), rr * math.sin(am), txt, ha="center", va="center", fontsize=6.6)

        ax.add_patch(Circle((0, 0), R, fc="#F2F2F2", ec=OSC, lw=1.2))
        e = c["etiqueta"]
        arco(-e["ancho"] / 2, e["ancho"] / 2, R, R * 1.07, "#E7E6E6", f"etiqueta\n{FT.n(e['ancho'] / R * 57.3, 0)}°")
        arco(m["des"] / 2 - 22.5, m["des"] / 2 + 22.5, R, R * 1.07, "#7FB2E5", "QR de serie", R * 0.72)
        arco(m["u0"], m["u1"], R * 1.07, R * 1.16, "#111111",
             f"franja {FT.n(m['L'] / R * 57.3, 0)}°", R * 1.42 if not m["carro"] else R * 1.5)
        for a, b in m["tramos"]:
            arco(a, b, R * 1.16, R * 1.22, FT.FAJA_C)
        if "triangulos" in c:
            for s in (c["triangulos"]["s"], -c["triangulos"]["s"]):
                a = math.radians(ang(s))
                ax.plot([R * math.cos(a), R * 1.35 * math.cos(a)], [R * math.sin(a), R * 1.35 * math.sin(a)],
                        color="#595959", lw=3)
        ax.plot([0, 0], [R * 0.8, R * 1.0], color=ROJO, lw=2)
        ax.text(0, R * 0.68, "costura\n(0°)", ha="center", va="top", fontsize=6.6, color=ROJO)
        lado = "pared / manga" if True else ""
        ax.text(0, -R * 1.75, ("lado pared (180°)" if not m["carro"] else "lado manga (180°)"), ha="center",
                fontsize=6.8)
        ax.text(0, R * 1.85, "lado etiqueta (0°)", ha="center", fontsize=6.8)
        ax.set_title(f"{FT.NOMBRE[k]} visto desde arriba (Ø {FT.n(2 * R, 0)})", fontsize=8)
        ax.set_xlim(-R * 2.0, R * 2.0)
        ax.set_ylim(-R * 2.0, R * 2.1)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.5, 0.0, "Negro: franja grabada · amarillo: faja de sustituto/reserva (abierta) · gris: etiqueta del "
                       "fabricante (envuelve la costura) · celeste: QR de serie · gris oscuro: triángulos del eje",
             ha="center", fontsize=7)
    return _g(fig, ruta)


# ----------------------------------------------------------------------------------------------- hoja de ruta
def fig_hoja_ruta(ruta):
    """Hoja de ruta A4 del lote (la imprime PCP y viaja en el carro): formato con la OP 26-10-08 del Plan mensual; los
    campos se completan en planta."""
    fig, ax = plt.subplots(figsize=(8.27, 11.69))
    W, H = 210, 297
    ax.add_patch(Rectangle((0, 0), W, H, fc="white", ec=OSC, lw=1))
    ax.text(12, 284, "FLAMA S.A. · HOJA DE RUTA DEL LOTE", fontsize=13, weight="bold")
    ax.text(12, 276, "OP 26-10-08 · ABC 5 kg · 48 u · series 26-005480 a 26-005527 · partida P-26-10-C1", fontsize=9.5)
    ax.text(12, 270, "Chapa: lote ________ colada ________ · emitida por PCP al liberar · viaja en el carro", fontsize=8)
    _qr(ax, "OP:26-10-08", 176, 262, 24)
    ax.text(188, 259, "QR del lote", ha="center", fontsize=7)
    # bloque por puesto
    y = 250
    ax.text(12, y + 2, "1) PUESTOS (una firma por lote; insumo: pegar la etiqueta del lote o anotar su número)",
            fontsize=8, weight="bold")
    filas = [("2 Corte G2 + Pannier", "grabados 005480–005527", ""), ("4–7 Cúpulas y cuellos", "lote de cúpulas", "CU-____"),
             ("8–12 Cilindrado y soldaduras", "alambre / gas", "AL-____ / G-__"),
             ("16–19 Granallado y pintura", "lote de pintura", "PP-____"),
             ("20–22 Carga y presurización", "polvo / válv.", "PO-___ / VA-___"),
             ("25 Embalaje", "cajas", "C-____ a C-____")]
    ax.add_patch(Rectangle((12, y - 4 - 8 * len(filas)), 186, 8 * len(filas) + 2, fc="none", ec=OSC, lw=0.6))
    for i, (p, ins, ej) in enumerate(filas):
        yy = y - 10 - 8 * i
        ax.text(14, yy, p, fontsize=7.5)
        ax.text(70, yy, ins + ": " + ej, fontsize=7.5)
        ax.text(132, yy, "fecha __/__", fontsize=7.5)
        ax.text(158, yy, "firma ________", fontsize=7.5)
        ax.plot([12, 198], [yy - 3, yy - 3], color=GRIS, lw=0.4)
    # lista de series con controles al 100 %
    y2 = y - 14 - 8 * len(filas)
    ax.text(12, y2, "2) CONTROLES UNIDAD POR UNIDAD (marcar ✓ o ✗; los ✗ salen del carro con su número)",
            fontsize=8, weight="bold")
    cab = ["Serie", "Esp.", "PH", "Carga", "Pérd."]
    for col in range(3):
        x0 = 12 + col * 63
        for j, t in enumerate(cab):
            ax.text(x0 + [0, 21, 31, 41, 52][j], y2 - 7, t, fontsize=6.5, weight="bold")
        for r in range(16):
            sn = 5480 + col * 16 + r
            yy = y2 - 12 - r * 6.2
            ax.text(x0, yy, f"26-00{sn}", fontsize=6.5, family="DejaVu Sans Mono")
            for j in range(4):
                ax.add_patch(Rectangle((x0 + [21, 31, 41, 52][j], yy - 1.5), 4, 4, fc="white", ec=OSC, lw=0.5))
    y3 = y2 - 12 - 16 * 6.2 - 4
    ax.text(12, y3, "3) CIERRE (calidad): rechazos (serie y ensayo) ____________   ·   firma ______________   ·   "
                    "foto de esta hoja → sistema", fontsize=7.5, weight="bold", color=ROJO)
    ax.text(12, y3 - 7, "El sistema ya sabe qué series tiene el lote. La hoja agrega solo lo que pasa con el lote",
            fontsize=7, color="#595959")
    ax.text(12, y3 - 12, "(insumos, firmas) y las excepciones (rechazos). Series del Plan mensual de octubre de 2026.", fontsize=7,
            color="#595959")
    ax.add_patch(Rectangle((12, 12), 186, y3 - 30, fc="none", ec=OSC, lw=0.6))
    ax.text(14, y3 - 24, "4) OBSERVACIONES (retrabajos, paradas, cambios de lote de insumo a mitad de lote)",
            fontsize=7.5, weight="bold")
    ax.set_xlim(-2, W + 2)
    ax.set_ylim(-2, H + 2)
    ax.set_aspect("equal")
    ax.axis("off")
    return _g(fig, ruta)


# ----------------------------------------------------------------------------------------------- etiquetas
def fig_etiquetas(ruta):
    fig, ax = plt.subplots(figsize=(11, 4.6))

    def etiqueta(x, y, w, h, tit, lineas, qr, nota, fc="white"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.5", fc=fc, ec=OSC, lw=1))
        q = h - 6
        _qr(ax, qr, x + 3, y + 3, q)
        ax.text(x + q + 6, y + h - 4, tit, fontsize=7, weight="bold", va="top")
        yy = y + h - 10
        for t, fs, bold in lineas:
            ax.text(x + q + 6, yy, t, fontsize=fs, va="top",
                    weight="bold" if bold else "normal", family="DejaVu Sans Mono" if bold else "DejaVu Sans")
            yy -= fs * 0.62 + 2.2
        ax.text(x + w / 2, y - 3, nota, ha="center", va="top", fontsize=6.6, color="#555555")

    etiqueta(5, 50, 90, 50, "FLAMA · ABC 5 kg", [("26-005480", 12, True), ("fabricado 10/2026", 6.5, False),
                                                  ("escaneá para ver", 6, False), ("su historia", 6, False)],
             URL + "26-005480", "Etiqueta de serie 45 × 25 mm (dibujada al doble)\npoliéster, lado pared, sobre el "
                                "QR de los planos")
    etiqueta(110, 50, 90, 50, "CAJA · 1 u", [("26-005480", 12, True), ("ABC 5 kg", 6.5, False),
                                            ("OP 26-10-08", 6.5, False), ("P-26-10-C1", 6.5, False)],
             URL + "26-005480", "Etiqueta de caja (papel)\nmisma serie: une caja ↔ equipo")
    etiqueta(215, 40, 110, 60, "PALLET (SSCC)", [("(00) 0779xxx", 8, True), ("000000457 4", 8, True),
                                                 ("48 u · OP 26-10-08", 6.5, False), ("remito al despachar", 6.5, False)],
             "SSCC:00077900000004574", "Etiqueta de pallet (papel)\nun escaneo = 48 equipos")
    etiqueta(5, -25, 90, 50, "REVENDIDO · CO₂ 5 kg", [("R-26-000001", 10.5, True), ("grabado del fabr.:", 6, False),
                                                      ("marca · n° · año", 6, False), ("vinilo destructible", 6, False)],
             URL + "R-26-000001", "Revendido: apunta al grabado de SU fabricante")
    etiqueta(110, -25, 90, 50, "SERVICIO 2027", [("26-005480", 12, True), ("próx. mant. 10/2028", 6.4, False),
                                                 ("PH vence 10/2031", 6.4, False), ("recargador FLAMA", 6.4, False)],
             URL + "26-005480", "Etiqueta de servicio (IRAM 3517-2 9.4.14)\nse renueva cada año: el QR viaja con ella")
    ax.set_xlim(0, 330)
    ax.set_ylim(-42, 112)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(165, 108, "Etiquetas con QR reales (se pueden escanear): todas llevan el MISMO número que el grabado",
            ha="center", fontsize=8.5)
    return _g(fig, ruta)


# ----------------------------------------------------------------------------------------------- arquitectura
def fig_arquitectura(ruta):
    fig, ax = plt.subplots(figsize=(11, 6.6))
    _caja(ax, 0.1, 5.0, 3.1, 1.1, "GOOGLE SHEETS de producción\n(Aprovechamiento: Plan mensual,\nMRP, BOM): ya existen",
          VERDE, 6.3, True)
    _caja(ax, 4.0, 4.6, 3.2, 1.9, "APP WEB FLAMA (Vercel)\n\n· órdenes y lotes · series\n· eventos con hash · custodia\n"
                                  "· etiquetas e impresión\n· página pública del QR", AZUL, 7, True)
    _caja(ax, 4.0, 3.5, 3.2, 0.75, "BASE DE DATOS (Postgres)\n+ copia diaria a Sheets", "#D9D2E9", 6.8, True)
    _fl(ax, (3.2, 5.55), (4.0, 5.55))
    ax.text(3.6, 6.25, "lee el plan\n(API de Sheets)", ha="center", fontsize=6)
    _fl(ax, (5.6, 4.6), (5.6, 4.25))
    puestos = [("PCP (oficina)\nPC + impresora A4", "hoja de ruta + archivo de marcado", 8.2, 6.0),
               ("G2 + PANNIER\nmarcadora", "archivo de series (USB o red)", 8.2, 5.0),
               ("CALIDAD\ncelular del supervisor", "foto de la hoja firmada + rechazos", 8.2, 4.0),
               ("ETIQUETADO (24 / C-15)\nPC + impresora + lector DPM USB", "1 lectura por equipo → imprime", 8.2, 3.0),
               ("DESPACHO\nmismo lector o celular", "pallet → remito con QR", 8.2, 2.0),
               ("RECARGAS (recepción)\ntablet + impresora (ya previstas)", "lee grabado o QR", 8.2, 1.0)]
    for t, sub, x, y in puestos:
        _caja(ax, x, y - 0.35, 2.4, 0.75, t, AMAR, 6.3, True)
        ax.text(x + 2.5, y, sub, fontsize=6.2, va="center")
        _fl(ax, (7.2, 5.2), (x, y), color="#7F7F7F")
    ext = [("Chofer", 0.6), ("Distribuidor", 1.5), ("Instalador", 2.4), ("Cliente / inspector", 3.3)]
    for t, y in ext:
        _caja(ax, 0.4, y - 0.3, 2.0, 0.6, t + "\n(celular, sin app)", "#FCE4D6", 6.3, True)
        _fl(ax, (2.4, y), (4.0, 3.9), color="#7F7F7F")
    ax.text(0.4, 4.05, "escanean el QR de la etiqueta o del remito:\nabre una página web", fontsize=6.3)
    ax.text(0.2, 0.15, "Conexiones: todo por navegador (HTTPS). El lector USB escribe como un teclado (no se instala "
                       "nada). La impresora de etiquetas recibe la etiqueta desde el navegador (Zebra Browser Print o "
                       "PDF). Si se corta internet: la hoja de ruta en papel sigue y se carga al volver.",
            fontsize=6.6)
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 6.6)
    ax.axis("off")
    return _g(fig, ruta)


# ----------------------------------------------------------------------------------------------- intraplanta
def fig_intra_pasos(ruta):
    fig, ax = plt.subplots(figsize=(11, 4.6))
    pasos = [("1 PCP", "crea la OP del\nplan mensual;\nimprime hoja\nde ruta", AZUL, "1 vez por lote"),
             ("2 G2 + Pannier", "graba 26-005480\na 527 desde el\narchivo", VERDE, "0 s extra"),
             ("3 Conformado y\nsoldaduras", "firma por lote,\nanota insumos;\nrechazos con n°", AMAR, "~15 s / lote"),
             ("4 Espesor · PH", "✓ / ✗ por\nserie en la\nhoja (100 %)", AMAR, "~2 s / equipo"),
             ("5 Pintura · carga\npérdidas", "lotes de pintura,\npolvo, válvulas;\n✓ / ✗ por serie", AMAR,
              "~2 s / equipo"),
             ("6 Cierre de\nla hoja", "foto + rechazos\n(calidad, celular)", "#D9D2E9", "~1 min / lote"),
             ("7 Etiquetado", "lee el grabado →\nimprime su\netiqueta; bloquea\nrechazados", "#F4B183", "~2 s / equipo"),
             ("8 Embalaje", "caja con la\nmisma serie;\npallet SSCC", VERDE, "1 lectura / caja")]
    w, sx = 1.25, 1.42
    for i, (t, d, col, tiempo) in enumerate(pasos):
        x = 0.1 + i * sx
        _caja(ax, x, 2.2, w, 0.75, t, col, 6.8, True)
        ax.text(x + w / 2, 2.05, d, ha="center", va="top", fontsize=6.2)
        ax.text(x + w / 2, 1.2, tiempo, ha="center", fontsize=6.3, color=ROJO, weight="bold")
        if i:
            _fl(ax, (x - sx + w, 2.57), (x, 2.57))
    ax.text(0.1, 3.35, "Lo que viaja con el carro: la HOJA DE RUTA del lote. Lo que se lee con un lector: solo en "
                       "ETIQUETADO (equipo por equipo) y en EMBALAJE / DESPACHO.", fontsize=7.6)
    ax.text(0.1, 0.85, "Rojo: tiempo agregado al operario (estimado, criterio). Sin tablets en los puestos: el papel "
                       "firmado es el registro de cada puesto y el sistema lo recibe en el cierre.", fontsize=7)
    ax.set_xlim(0, 0.1 + 8 * sx)
    ax.set_ylim(0.75, 3.6)
    ax.axis("off")
    return _g(fig, ruta)


# ----------------------------------------------------------------------------------------------- extraplanta
def fig_extra_pasos(ruta):
    fig, ax = plt.subplots(figsize=(11, 6.0))
    carriles = [("FLAMA despacho", 4.9), ("Transportista", 3.7), ("Distribuidor", 2.5), ("Instalador / cliente", 1.3)]
    for t, y in carriles:
        ax.add_patch(Rectangle((0, y - 0.55), 13.1, 1.1, fc="#FAFAFA", ec=GRIS, lw=0.5))
        ax.text(0.1, y, t, fontsize=7.5, weight="bold", va="center")
    pas = [(2.5, 4.9, "1 Pedido →\nremito con\nanexo de series", AZUL), (3.9, 4.9, "2 Picking:\nlee pallets /\ncajas", AZUL),
           (5.3, 4.9, "3 Carga: sujeción,\ndocumentos, COT,\ncarta de porte", AZUL),
           (6.7, 3.7, "4 Firma carta de\nporte; QR remito\n«en tránsito»", AMAR), (8.1, 3.7, "5 Viaje\n(horarios, ruta,\nmatafuego propio)", AMAR),
           (9.5, 2.5, "6 Recibe: lee QR\ndel remito, cuenta,\nfoto si hay daño", VERDE),
           (10.9, 2.5, "7 Vende: lee el QR\ndel equipo\n(activa garantía)", VERDE),
           (12.3, 1.3, "8 Instala: altura,\nseñal, acta con\nubicación y foto", "#FCE4D6")]
    for i, (x, y, t, col) in enumerate(pas):
        _caja(ax, x - 0.65, y - 0.42, 1.3, 0.84, t, col, 6.0, False)
        if i:
            px, py = pas[i - 1][0], pas[i - 1][1]
            _fl(ax, (px + 0.65, py), (x - 0.65, y))
    _caja(ax, 9.5 - 0.65, 1.3 - 0.42, 1.3, 0.84, "6' Venta directa:\ncliente recibe y\nlee el QR", "#FCE4D6", 6.0)
    _fl(ax, (8.1 + 0.65, 3.7), (9.5 - 0.65, 1.3), ls="--")
    ax.text(0.1, 5.75, "Cada flecha que cruza de carril es un TRASPASO: sale de uno (lectura) y entra al otro "
                       "(lectura o firma). Lo que no se lee queda en el último que lo tuvo.", fontsize=7.6)
    ax.text(0.1, 0.3, "Restricciones: UN 1044 clase 2.2 (Res. 195/97: verificar cantidad exenta y requisitos) · COT de "
                      "ARBA según umbrales · CABA: carga y descarga en carriles exclusivos solo 21 a 07 h · equipos de "
                      "pie, sujetos y con seguro puesto.", fontsize=6.8, color=ROJO)
    ax.set_xlim(0, 13.7)
    ax.set_ylim(0.1, 6.0)
    ax.axis("off")
    return _g(fig, ruta)


# ----------------------------------------------------------------------------------------------- pantallas
def _pantalla(ax, x, y, w, h, tit, filas, boton=None, col_boton=VE_O, celu=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.18" if celu else
                                "round,pad=0.01,rounding_size=0.05", fc="#202020", ec="none"))
    m = 0.1
    ax.add_patch(Rectangle((x + m, y + m), w - 2 * m, h - 2 * m, fc="white", ec="none"))
    ax.add_patch(Rectangle((x + m, y + h - m - 0.42), w - 2 * m, 0.42, fc=AZ_O, ec="none"))
    ax.text(x + w / 2, y + h - m - 0.21, tit, ha="center", va="center", fontsize=6.4, color="white", weight="bold")
    yy = y + h - m - 0.62
    for t, fs, color, bold in filas:
        ax.text(x + m + 0.12, yy, t, fontsize=fs, va="top", color=color, weight="bold" if bold else "normal")
        yy -= fs * 0.042 + 0.07
    if boton:
        ax.add_patch(FancyBboxPatch((x + m + 0.2, y + m + 0.15), w - 2 * m - 0.4, 0.38,
                                    boxstyle="round,pad=0.01,rounding_size=0.08", fc=col_boton, ec="none"))
        ax.text(x + w / 2, y + m + 0.34, boton, ha="center", va="center", fontsize=6.2, color="white", weight="bold")


def fig_pantallas(ruta):
    fig, ax = plt.subplots(figsize=(11, 7.2))
    _pantalla(ax, 0, 3.7, 5.2, 3.3, "PCP · Nueva orden desde el Plan mensual", [
        ("Semana 10 · Plan: ABC 5 kg 192 u (Aprovechamiento, fila del mes)", 6.4, OSC, False),
        ("Lotes propuestos: 4 × 48", 6.4, OSC, False),
        ("OP 26-0412   series 26-000101 … 148   chapa H-0412", 6.6, OSC, True),
        ("OP 26-0413   series 26-000149 … 196   chapa H-0413", 6.6, OSC, True),
        ("OP 26-0414 · OP 26-0415 …", 6.4, "#7F7F7F", False),
        ("☑ archivo Pannier  ☑ hoja de ruta A4 con QR", 6.4, OSC, False)], "Confirmar e imprimir")
    _pantalla(ax, 5.6, 3.7, 5.2, 3.3, "Etiquetado · puesto 24", [
        ("Lote abierto: OP 26-0412 (ABC 5 kg) · 47 de 48 aptos", 6.4, OSC, False),
        ("LEÉ EL GRABADO", 12, AZ_O, True),
        ("Último: 26-005480 → etiqueta impresa ✓", 7, VE_O, True),
        ("26-000117 → BLOQUEADO (rechazo PH) ✗", 7, ROJO, True),
        ("Impresos 31 / 47 · faltan 16", 6.4, OSC, False),
        ("(el lector escribe el número solo; la pantalla", 6.0, "#7F7F7F", False),
        (" no necesita que el operario toque nada)", 6.0, "#7F7F7F", False)])
    _pantalla(ax, 0.2, 0, 2.4, 3.4, "Remito R-0001-4521", [
        ("FLAMA → Matafuegos Sur", 6.0, OSC, True), ("3 pallets · 144 equipos", 6.0, OSC, False),
        ("Chofer: J. P. · AB123CD", 6.0, OSC, False), ("¿Llegó todo?", 7.5, AZ_O, True),
        ("☐ faltantes  ☐ daños", 6.0, OSC, False), ("Recibe: nombre, DNI, foto", 6.0, OSC, False)],
              "Confirmar recepción", celu=True)
    _pantalla(ax, 2.9, 0, 2.4, 3.4, "Instalación", [
        ("26-005480 · ABC 5 kg", 6.2, OSC, True), ("Dirección: Av. X 123", 6.0, OSC, False),
        ("Sector: planta baja, hall", 6.0, OSC, False), ("Altura sup. ≤ 1,5 m ✓", 6.0, VE_O, False),
        ("Señal a 2–2,5 m ✓", 6.0, VE_O, False), ("[foto colgado]", 6.0, "#7F7F7F", False)],
                    "Firmar acta", celu=True)
    _pantalla(ax, 5.6, 0, 2.4, 3.4, "QR · solapa comercial", [
        ("ABC 5 kg · 26-005480", 6.6, OSC, True), ("VIGENTE", 9, VE_O, True), ("Próx. mantenimiento 03/2027", 6.0, OSC, False),
        ("PH vence 03/2031", 6.0, OSC, False), ("Historia: 4 eventos", 6.0, OSC, False),
        ("Pedir recarga · Garantía", 6.0, AZ_O, True)], "Ver historia", celu=True)
    _pantalla(ax, 8.4, 0, 2.4, 3.4, "QR · solapa técnica", [
        ("Fabricado 03/2026 · OP 26-0412", 5.8, OSC, False), ("PH fábrica 3,5 MPa ✓", 5.8, OSC, False),
        ("Polvo lote PO-2603 · 5,14 kg", 5.8, OSC, False), ("Válvula HZ lote VA-118", 5.8, OSC, False),
        ("Servicios: 0 · Custodia: cliente", 5.8, OSC, False), ("hash ✓ cadena íntegra", 5.8, VE_O, True)],
                    "Solo usuarios habilitados", AZ_O, celu=True)
    ax.text(5.4, 7.25, "Pantallas de la app (maqueta, datos inventados): arriba en PC, abajo en celular",
            ha="center", fontsize=8.5)
    ax.set_xlim(-0.1, 10.9)
    ax.set_ylim(-0.1, 7.4)
    ax.set_aspect("equal")
    ax.axis("off")
    return _g(fig, ruta)


# ----------------------------------------------------------------------------------------------- vida etiqueta
def fig_vida_etiqueta(ruta):
    fig, ax = plt.subplots(figsize=(11, 2.9))
    hitos = [(0, "Fabricación\netiqueta de serie\n(poliéster)"), (1, "1er servicio\netiqueta nueva\n(9.4.14)"),
             (2, "2do servicio\netiqueta nueva"), (3, "repintado (9.10):\nse va la etiqueta;\nse reimprime del grabado"),
             (4, "…"), (5, "PH 5 años\netiqueta nueva"), (20, "fin de vida útil:\ninutilización")]
    ax.plot([0, 6.4], [1, 1], color=OSC, lw=2)
    for i, (a, t) in enumerate(hitos):
        x = min(i, 6.2)
        ax.add_patch(Circle((x, 1), 0.09, fc=AZ_O if i != 6 else ROJO, ec="none"))
        ax.text(x, 1.25, f"año {a}", ha="center", fontsize=6.8, weight="bold")
        ax.text(x, 0.75, t, ha="center", va="top", fontsize=6.4)
    ax.add_patch(Rectangle((0, 1.55), 1, 0.12, fc="#7FB2E5", ec="none"))
    ax.text(0.5, 1.75, "cada etiqueta necesita durar ~1 año", ha="center", fontsize=6.8, color=AZ_O)
    ax.add_patch(Rectangle((0, 1.95), 6.4, 0.12, fc="#111111", ec="none"))
    ax.text(3.2, 2.15, "el grabado dura toda la vida útil: es el ancla", ha="center", fontsize=6.8)
    ax.set_xlim(-0.6, 6.8)
    ax.set_ylim(-0.1, 2.35)
    ax.axis("off")
    return _g(fig, ruta)


def todas(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    f = {}
    for k, fn in (("prof_escala", fig_profundidad), ("planta", fig_planta), ("hoja_ruta", fig_hoja_ruta),
                  ("etiquetas", fig_etiquetas), ("arquitectura", fig_arquitectura), ("intra_pasos", fig_intra_pasos),
                  ("extra_pasos", fig_extra_pasos), ("pantallas", fig_pantallas), ("vida_etiqueta", fig_vida_etiqueta)):
        f[k] = fn(os.path.join(carpeta, f"{k}.png"))
    return f


if __name__ == "__main__":
    print(todas(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figs3")))
