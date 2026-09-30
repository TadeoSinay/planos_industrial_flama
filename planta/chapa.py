"""FL_PI_05 - Aprovechamiento de chapa por formato (opción D: hojas estándar + fleje a medida + caño).

Fuente: referencias/Esquemas_de_corte_cuerpos_guillotina.docx, Comparacion_corte.xlsx (Nesting) y
MP_Abastecimiento (Corte opción D, Geometría del acero)."""

import math

from ezdxf.enums import TextEntityAlignment

from . import dibujo as D
from .planos import f, hoja, titulo_hoja

A = TextEntityAlignment

# formato, hoja (ancho, largo), espesor, franjas [(ancho, [largos de pieza])], aprovechamiento, cortes, hojas/año 2035
HOJAS = [
    ("2,5 kg", (1220, 2440), 1.25, "LAF", [(385.5, [269.5] * 9)] * 3, 94.2, 30, 522),
    ("5 kg", (1000, 2000), 1.6, "LAF", [(330, [474.5] * 4)] * 3, 94.0, 15, 5306),
    ("10 kg", (1500, 3000), 2.0, "LAF", [(495, [563] * 5)] * 3, 92.9, 18, 256.8),
    ("25 kg", (1500, 3000), 3.2, "LAC", [(490, [858] * 3)] * 3, 84.1, 12, 86.1),
    ("50 kg", (1500, 3000), 3.2, "LAC", [(640, [994] * 3)] * 2, 84.8, 8, 284.2),
    ("70 kg", (1500, 3000), 4.75, "LAC", [(680, [1212] * 2)] * 2, 73.3, 6, 0),
    ("100 kg", (1500, 3000), 4.75, "LAC", [(1212, [900] * 3)], 72.7, 4, 40.9),
    ("Mixta 70 + 100 kg", (1500, 3000), 4.75, "LAC", [(1212, [900, 680, 680, 680])], 79.2, 5, 124.4),
]
# pieza, Ø disco, espesor, ancho de fleje comprado; paso = Ø + 3 mm de puente (CC Nesting)
DISCOS = [
    ("Cúpula 1 kg", 108, 0.9, 114), ("Fondo 1 kg", 100, 0.9, 106),
    ("Cúpula 2,5 kg", 179, 1.25, 200), ("Fondo 2,5 kg", 148, 1.25, 200),
    ("Cúpula 5 kg", 221, 1.6, 250), ("Fondo 5 kg", 177, 1.6, 200),
    ("Cúpula 10 kg", 258, 2.0, 300), ("Fondo 10 kg", 205, 2.0, 249),
]
CANO = {"barra": 6000, "pieza": 255, "piezas": 23, "diam": 76.2, "esp": 1.25}


def lamina(doc, ox):
    h = hoja(doc, "A1", ox, "Aprovechamiento de chapa", "Cuerpos, discos y caño por formato - opción D",
             "FL_PI_05", 1, 1, "1:20", "Plano de corte", "SAE 1010 LAF y LAC", unidades="Cotas en mm")
    pl = D.Plano(h, 1, (0, 0), (0, 0))
    titulo_hoja(pl, h, "FL_PI_05 - APROVECHAMIENTO DE LA CHAPA POR FORMATO",
                "Cuerpos 2,5-100 kg en hojas estándar cortadas en guillotina 8 × 3200 (esc. 1:20); cúpulas y fondos en "
                "fleje a medida con troquel de una fila (esc. 1:10); cuerpo de 1 kg en caño Ø76,2 × 6 m (esc. 1:20).")
    m = pl.m
    # ---------------- hojas 1:20
    s20 = 1 / 20
    x0, ytop = h.fx0 + 10, h.fy1 - 34
    celda_w, celda_h = 194, 118
    for i, (nom, (W, Lh), e, mat, franjas, ap, cortes, n_anual) in enumerate(HOJAS):
        cx = x0 + (i % 4) * celda_w
        cy = ytop - (i // 4) * celda_h
        w, l_ = W * s20, Lh * s20
        ox_, oy_ = cx + 4, cy - 12 - w
        m.add_lwpolyline([(ox_, oy_), (ox_ + l_, oy_), (ox_ + l_, oy_ + w), (ox_, oy_ + w)], close=True,
                         dxfattribs={"layer": "A-EQUIPO"})
        yb = oy_ + w
        n_p = 0
        for fw, piezas in franjas:
            xa = ox_
            for pz in piezas:
                q = [(xa, yb - fw * s20), (xa + pz * s20, yb - fw * s20), (xa + pz * s20, yb), (xa, yb)]
                hh = m.add_hatch(dxfattribs={"layer": "A-RELLENO"})
                hh.set_solid_fill(rgb=(253, 214, 170))
                hh.paths.add_polyline_path(q, is_closed=True)
                m.add_lwpolyline(q, close=True, dxfattribs={"layer": "A-EQUIPO-FINO"})
                xa += pz * s20
                n_p += 1
            yb -= fw * s20
        # sobrante (orillas) rayado
        q1 = [(ox_, oy_), (ox_ + l_, oy_), (ox_ + l_, yb), (ox_, yb)]
        if yb - oy_ > 0.2:
            hh = m.add_hatch(dxfattribs={"layer": "A-RELLENO"})
            hh.set_pattern_fill("ANSI31", scale=0.4, angle=45)
            hh.paths.add_polyline_path(q1, is_closed=True)
        largo_util = max(sum(p for p in pz_) for fw_, pz_ in franjas) * s20
        q2 = [(ox_ + largo_util, yb), (ox_ + l_, yb), (ox_ + l_, oy_ + w), (ox_ + largo_util, oy_ + w)]
        if l_ - largo_util > 0.2:
            hh = m.add_hatch(dxfattribs={"layer": "A-RELLENO"})
            hh.set_pattern_fill("ANSI31", scale=0.4, angle=45)
            hh.paths.add_polyline_path(q2, is_closed=True)
        pl.texto(f"Cuerpo {nom} - hoja {mat} {f(e, 2)} × {W} × {Lh}", (cx + 4, cy + 1), 2.5, A.TOP_LEFT, papel=True)
        # cotas: franja y pieza
        fw0, p0 = franjas[0][0], franjas[0][1][0]
        d = m.add_linear_dim(base=(ox_ - 5, oy_ + w), p1=(ox_, oy_ + w), p2=(ox_, oy_ + w - fw0 * s20), angle=90,
                             dimstyle="FLAMA-IRAM", override={"dimlfac": 20, "dimtxt": 2.0, "dimasz": 2.0, "dimdec": 1},
                             dxfattribs={"layer": "A-COTA"})
        d.render()
        d = m.add_linear_dim(base=(ox_, oy_ + w + 4), p1=(ox_, oy_ + w), p2=(ox_ + p0 * s20, oy_ + w), angle=0,
                             dimstyle="FLAMA-IRAM", override={"dimlfac": 20, "dimtxt": 2.0, "dimasz": 2.0, "dimdec": 1},
                             dxfattribs={"layer": "A-COTA"})
        d.render()
        d = m.add_linear_dim(base=(ox_, oy_ - 5), p1=(ox_, oy_), p2=(ox_ + l_, oy_), angle=0, dimstyle="FLAMA-IRAM",
                             override={"dimlfac": 20, "dimtxt": 2.0, "dimasz": 2.0, "dimdec": 0},
                             dxfattribs={"layer": "A-COTA"})
        d.render()
        txt = [f"{len(franjas)} franja(s): {n_p} cuerpos por hoja; {cortes} cortes ({f(cortes / n_p, 2)} por cuerpo)",
               f"Aprovechamiento {f(ap, 1)} %; hojas por año (2035): {f(n_anual, 0) if n_anual else 'en hoja mixta'}"]
        pl.parrafo(txt, cx + 4, oy_ - 12, 2.1)
    # ---------------- discos en fleje 1:10
    s10 = 1 / 10
    y_d = ytop - 2 * celda_h - 12
    pl.texto("Cúpulas y fondos: discos en fleje a medida, troquel de una fila (1:10); paso = Ø + 3 mm de puente",
             (x0, y_d + 4), 3.0, A.BOTTOM_LEFT, papel=True)
    for i, (nom, D0, e, ancho) in enumerate(DISCOS):
        cx = x0 + (i % 4) * celda_w
        cy = y_d - 6 - (i // 4) * 52
        paso = D0 + 3.0
        n = 4
        Lf = n * paso + 60
        m.add_lwpolyline([(cx, cy - ancho * s10), (cx + Lf * s10, cy - ancho * s10), (cx + Lf * s10, cy), (cx, cy)],
                         close=True, dxfattribs={"layer": "A-EQUIPO"})
        for k in range(n):
            c = (cx + (30 + paso / 2 + k * paso) * s10, cy - ancho * s10 / 2)
            hh = m.add_hatch(dxfattribs={"layer": "A-RELLENO"})
            hh.set_solid_fill(rgb=(253, 214, 170))
            pts = [(c[0] + D0 / 2 * s10 * math.cos(t / 24 * 6.2832),
                    c[1] + D0 / 2 * s10 * math.sin(t / 24 * 6.2832)) for t in range(24)]
            hh.paths.add_polyline_path(pts, is_closed=True)
            m.add_circle(c, D0 / 2 * s10, dxfattribs={"layer": "A-EQUIPO-FINO"})
        ap = math.pi * D0 ** 2 / 4 / (paso * ancho) * 100
        pl.texto(f"{nom}: Ø {D0} en fleje {f(e, 2)} × {ancho} - paso {f(paso, 1)} - aprovech. {f(ap, 1)} %",
                 (cx, cy + 2), 2.1, A.BOTTOM_LEFT, papel=True)
    # ---------------- caño 1 kg 1:20
    y_c = y_d - 6 - 2 * 52 - 10
    pl.texto("Cuerpo de 1 kg: caño Ø76,2 × 1,25 × 6000 (1:20)", (x0, y_c + 4), 3.0, A.BOTTOM_LEFT, papel=True)
    Lb = CANO["barra"] * s20
    hb = CANO["diam"] * s20 * 2
    m.add_lwpolyline([(x0, y_c - hb), (x0 + Lb, y_c - hb), (x0 + Lb, y_c), (x0, y_c)], close=True,
                     dxfattribs={"layer": "A-EQUIPO"})
    for k in range(CANO["piezas"]):
        xa = x0 + (k * CANO["pieza"]) * s20
        q = [(xa, y_c - hb), (xa + CANO["pieza"] * s20, y_c - hb), (xa + CANO["pieza"] * s20, y_c), (xa, y_c)]
        hh = m.add_hatch(dxfattribs={"layer": "A-RELLENO"})
        hh.set_solid_fill(rgb=(253, 214, 170))
        hh.paths.add_polyline_path(q, is_closed=True)
        m.add_lwpolyline(q, close=True, dxfattribs={"layer": "A-EQUIPO-FINO"})
    resto = CANO["barra"] - CANO["piezas"] * CANO["pieza"]
    pl.parrafo([f"{CANO['piezas']} cuerpos de {CANO['pieza']} mm por barra; despunte {resto} mm; aprovechamiento "
                f"{f(CANO['piezas'] * CANO['pieza'] / CANO['barra'] * 100, 1)} % (corte láser de tubo, sin sierra).",
                "Altura de la barra exagerada × 2 para que se vea el corte."], x0, y_c - hb - 3, 2.1)
    # ---------------- tabla resumen
    xt = x0 + 330
    yt = y_c + 6
    cols = [("Formato", 40, "l"), ("Presentación", 58, "l"), ("Piezas", 24, "c"), ("Aprov. %", 18, "c")]
    filas = [[f"Cuerpo {n_}", f"Hoja {m_} {f(e_, 2)} × {W_} × {L__}", sum(len(p_) for fw_, p_ in fr_), f(ap_, 1)]
             for n_, (W_, L__), e_, m_, fr_, ap_, c_, na_ in HOJAS]
    filas.append(["Cuerpo 1 kg", "Caño Ø76,2 × 1,25 × 6 m", 23, f(97.8, 1)])
    pl.tabla(xt, yt, cols, filas, 3.9, 1.9, "Resumen")
    pl.parrafo(["Aprovechamiento global de chapa (2035): 82,8 % (Comparacion_corte, Resumen D).",
                "Los manuales (93-94 %) son el 96 % del volumen. Los rodantes quedan en 73-85 %: sólo",
                "se cotizaron hojas LAC de 1500 × 3000; con hojas de 1000 × 2000 el 50 kg llegaría a 95 %.",
                "El 70 kg se corta siempre en la hoja mixta (pieza de 1212 mm más larga que el tope de 1000).",
                "Un troquel de 2 filas escalonadas subiría 8-10 puntos el aprovechamiento de los discos."],
               xt + 146, yt, 2.0)
    return h
