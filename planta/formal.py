"""FL_PI_04 - Plano formal normalizado en UNA lámina 2A0: planta 1:100 de la nave y los anexos con todo el
equipamiento y el mobiliario, acotada; implantación 1:500; corte 1:200; cuadros de superficies, equipos y locales."""

import math

from ezdxf.enums import TextEntityAlignment

from . import layout as L
from . import calculos as C
from . import dibujo as D
from . import planos as PL
from .planos import f, hoja, titulo_hoja

A = TextEntityAlignment
TOT = 1


# ================================================================ símbolos de seguridad
def extintor(pl, c, n, r=0.3):
    """Extintor ABC 10 kg: círculo rojo lleno con número (IRAM 10005: rojo de seguridad)."""
    pl.relleno(PL.circ_pts(c, r), (210, 0, 0), "S-INCENDIO")
    pl.texto(str(n), (c[0] + r + 0.25, c[1]), 1.6, A.MIDDLE_LEFT, "S-INCENDIO")


def salida(pl, p, d, texto="SALIDA"):
    """Flecha verde de salida de emergencia (sentido de evacuación)."""
    tip = (p[0] + d[0] * 2.2, p[1] + d[1] * 2.2)
    pl.linea(p, tip, "S-ESCAPE")
    pl.punta(tip, d, 2.6, 1.4, (0, 150, 60), "S-ESCAPE")


EXT_ANEXOS = [(-0.6, 21.6), (-5.6, 30.0), (-12.0, 23.8), (-17.4, 32.0), (41.0, 47.0), (52.0, 46.4)]


def _ext(cod):
    return next(r for c, n, r, t in L.EXTERIOR if c == cod)


# ================================================================ implantación 1:500 (recuadro)
def implantacion(pl):
    x0, y0, x1, y1 = L.TERRENO
    PL.sitio(pl, rotulos=False)
    D.sectores(pl, relleno=True, rotulos=False)
    D.locales(pl, rotulos=False, relleno=True)
    D.muros(pl, detalle=False)
    for cod, nom, r, tipo in L.EXTERIOR:
        pl.texto(cod, r.c, 1.8, A.MIDDLE_CENTER)
    for cod, a, b, uso in L.PORTONES_TERRENO:
        pl.texto(cod, ((a + b) / 2, y0 - 4.0), 1.8, A.MIDDLE_CENTER)
    pl.texto("NAVE 88,00 × 44,00", (44.0, 22.0), 2.5, A.MIDDLE_CENTER)
    pl.cota((x0, y1), (x1, y1), 8, True)
    pl.cota((x1, y0), (x1, y1), 8, False)
    pl.cota((x0, 0.0), (0.0, 0.0), -10, True)
    pl.cota((88.0, 0.0), (x1, 0.0), -10, True)
    pl.cota((88.0, 44.0), (88.0, y1), 6, False)
    pl.cota((88.0, y0), (88.0, 0.0), 6, False)
    pl.texto("IMPLANTACIÓN GENERAL - 1:500", pl.P(x0, y1 + 14), 3.5, A.BOTTOM_LEFT, papel=True)


# ================================================================ planta 1:100 completa
def planta(pl, xa, xb, y0, y1):
    antes = D.handles(pl.m)
    D.sectores(pl, relleno=False)
    D.locales(pl, rotulos=False)
    D.pasillos(pl, demarcacion=True, rotulos=False)
    D.equipos(pl, rotulos=True, h=1.6, fino=False)
    D.vehiculos(pl)
    D.muros(pl)
    D.puertas(pl, etiquetas=True, h=2.0)
    D.ejes(pl, r_glob=4.0, sobresale=4.5, completo=True)
    for cod, nom, r, tipo in L.EXTERIOR:
        if r.x1 < xa or r.x0 > xb or r.y1 < y0 or r.y0 > y1:
            continue
        pl.rect(r, "A-EXTERIOR")
        pl.texto(f"{cod} {nom}" if r.w > 8 else cod, (r.c[0], r.c[1]), 1.8, A.MIDDLE_CENTER)
    # sectores y locales: código, nombre corto y superficie
    for s in L.SECTORES:
        r = s.rect
        pl.texto(s.cod, (r.x0 + 0.3, r.y1 - 0.3), 2.2, A.TOP_LEFT)
        pl.texto(f"{f(r.area, 1)} m²", (r.x0 + 0.3, r.y1 - 0.6 - 2.6 / pl.s), 1.6, A.TOP_LEFT)
    for cod, r, nota in L.LIBRES:
        pl.texto(f"{cod} LIBRE {f(r.area, 1)} m² (a debatir)", r.c, 2.2, A.MIDDLE_CENTER)
    for s in L.LOCALES:
        r = s.rect
        if s.cat == "CIRC" and min(r.w, r.h) < 1.6:
            continue
        rot = 90 if r.h > r.w * 1.5 and r.w < 3.0 else 0
        pl.texto(s.cod, (r.x0 + 0.2, r.y1 - 0.2) if not rot else (r.x0 + 0.2, r.y0 + 0.2), 1.8,
                 A.TOP_LEFT if not rot else A.BOTTOM_LEFT, rot=rot)
        pl.texto(f"{f(r.area, 1)} m²", (r.x1 - 0.2, r.y0 + 0.2), 1.4, A.BOTTOM_RIGHT)
    # matafuegos y salidas
    ext = C.extintores()
    for i, c in enumerate(ext["puntos"] + EXT_ANEXOS):
        extintor(pl, c, i + 1)
    for p in L.PUERTAS:
        if p.tipo == "emergencia":
            m = (p.a + p.b) / 2
            if p.muro == "N":
                salida(pl, (m, L.NAVE_A - 1.2), (0, 1))
            elif p.muro == "S":
                salida(pl, (m, 1.2), (0, -1))
            elif p.muro == "O":
                salida(pl, (1.2, m), (-1, 0))
            else:
                salida(pl, (L.NAVE_L - 1.2, m), (1, 0))
    # cotas: ejes y vanos (norte y sur), alto de nave y vanos (oeste y este)
    xs = list(L.EJES_X)
    pl.cadena(xs, L.NAVE_A, 9.0, True)
    pl.cota((xs[0], L.NAVE_A), (xs[-1], L.NAVE_A), 14.0, True)
    vn = sorted(set([v for p in L.PUERTAS if p.muro == "N" for v in (p.a, p.b)] + xs))
    pl.cadena(vn, L.NAVE_A, 4.5, True)
    vs = sorted(set([v for p in L.PUERTAS if p.muro == "S" for v in (p.a, p.b)] + xs))
    pl.cadena(vs, -6.5, -3.0, True)
    pl.cota((L.NAVE_L, 0.0), (L.NAVE_L, L.NAVE_A), 9.0, False)
    ve = sorted([0.0, L.NAVE_A] + [v for p in L.PUERTAS if p.muro == "E" for v in (p.a, p.b)])
    pl.cadena(ve, L.NAVE_L, 5.0, False)
    vo = sorted([0.0, L.NAVE_A] + [v for p in L.PUERTAS if p.muro == "O" for v in (p.a, p.b)])
    pl.cadena(vo, -18.0, -5.0, False)
    pl.cota((-18.0, 0.0), (-18.0, L.NAVE_A), -10.0, False)
    sv = next(s.rect for s in L.ANEXOS if s.cod == "SV")
    xsv = sorted({round(v, 2) for s_ in L.LOCALES if s_.rect.x1 < 0.5 and s_.rect.y0 < 23.0
                  for v in (s_.rect.x0, s_.rect.x1)})
    pl.cadena([sv.x0] + xsv[1:-1] + [sv.x1], sv.y0, -3.0, True)
    pl.cota((sv.x0, sv.y1), (sv.x1, sv.y1), 3.0, True)
    st = next(s.rect for s in L.ANEXOS if s.cod == "ST")
    pl.cota((st.x0, st.y1), (st.x1, st.y1), 3.0, True)
    # anchos de pasillos
    for p in L.PASILLOS:
        r = p.rect
        if r.w >= r.h:
            xm = r.x0 + 6.0 if p.cod == "PC" else r.x0 + min(2.0, r.w / 2)
            pl.cota((xm, r.y0), (xm, r.y1), 0.0, False, texto=f"{p.cod} <>")
        else:
            ym = r.y0 + min(3.0, r.h / 2)
            pl.cota((r.x0, ym), (r.x1, ym), 0.0, True, texto=f"{p.cod} <>")
    D.recortar(pl, antes, xa, y0, xb, y1)


# ================================================================ lámina única
def fl_pi_01(doc, ox, n=1):
    h = hoja(doc, "2A0", ox, "Plano formal: planta general acotada",
             "Nave, servicios y recargas con equipos y mobiliario; implantación y corte", "FL_PI_01", 1, TOT,
             "1:100", "Plano de planta", "Estructura metálica / mampostería")
    xa, xb, y0, y1 = -31.0, 97.0, -13.0, 57.0
    k = 100
    pl = D.Plano(h, k, (xa, y0), (h.fx0 + 4, h.fy1 - 34 - (y1 - y0) * 1000 / k))
    titulo_hoja(pl, h, "FL_PI_01 - PLANO GENERAL FORMAL NORMALIZADO: PLANTA ACOTADA 1:100",
                "Nave 88 × 44 m, servicios al personal, recargas y sala técnica, con cada máquina, puesto, "
                "pulmón, mueble y artefacto a escala. Cotas en metros. Ejes 1 a 12 cada 8,00 m y A-B-C.")
    planta(pl, xa, xb, y0, y1)
    PL.norte(pl, (xb - 5.0, y1 - 6.0))
    # ---- columna derecha: equipos
    xt = pl.P(xb, 0)[0] + 6
    yt = h.fy1 - 12
    G = C.guerchet()
    gq = {r["cod"]: r for r in G["filas"]}
    cols = [("Paso", 10, "c"), ("Cód.", 10, "c"), ("Equipo", 64, "l"), ("Medida m", 21, "c"),
            ("Fuente de la medida", 70, "l"), ("Op.", 7, "c"), ("Ss", 11, "c"), ("St", 11, "c")]
    filas = []
    for e in L.EQUIPOS:
        g = gq.get(e.cod)
        fu = (e.fuente.replace("C ", "Cotiz. ", 1) if e.fuente.startswith("C ") else
              e.fuente[2:] if e.fuente.startswith("D ") else e.fuente)
        filas.append([e.paso or "-", e.cod, e.nombre[:42], f"{f(e.rect.w, 2)} × {f(e.rect.h, 2)}", fu[:46],
                      e.op or "-", f(g["ss"], 1) if g else "-", f(g["st"], 1) if g else "-"])
    y = pl.tabla(xt, yt, cols, filas, 3.3, 1.5, "Equipos: medida (cotización o criterio de diseño) y superficie de Guerchet (m²)")
    cols = [("Sector", 18, "l"), ("St Guerchet", 22, "c"), ("Dibujado", 20, "c"), ("Holgura", 20, "c")]
    filas = [[r["sector"], f(r["st"], 0), f(r["area"], 0), f(r["area"] - r["st"], 0)]
             for r in sorted(G["sectores"], key=lambda r: r["sector"]) if r["area"]]
    y = pl.tabla(xt, y - 8, cols, filas, 3.3, 1.5, f"Guerchet por sector: St = Ss + Sg + Se, k = {f(G['k'], 2)}")
    pl.parrafo(["Sg = Ss × N (lados de operación); Se = k (Ss + Sg), k = h móviles / (2 h fijos)",
                f"= 1,65 / (2 × {f(G['h_fijo'], 2)}). La holgura incluye pulmones, calles y estanterías:",
                "donde es grande (N2, N3, AL-3, S-T) queda espacio liberado por las medidas reales",
                "de las cotizaciones, para debatir (achicar la nave o reservar ampliación)."], xt, y - 4, 1.9)
    # ---- franja inferior: implantación, corte, superficies y locales
    yb = pl.P(0, y0)[1] - 8
    pi = D.Plano(h, 500, (L.TERRENO[0], L.TERRENO[1]), (h.fx0 + 12, h.fy0 + 18))
    implantacion(pi)
    pc = D.Plano(h, 200, (-4.0, -1.0), (h.fx0 + 400, h.fy0 + 150))
    corte(pc)
    x0_, y0_, x1_, y1_ = L.TERRENO
    sup_t = (x1_ - x0_) * (y1_ - y0_)
    nave = L.NAVE_L * L.NAVE_A
    anex = sum(s.rect.area for s in L.ANEXOS if s.cod != "RC")
    cub = nave + anex + _ext("PL-N").area
    cols = [("Concepto", 64, "l"), ("m²", 20, "r"), ("%", 14, "r")]
    filas = [["Terreno 170,00 × 125,00", f(sup_t, 0), "100,0"],
             ["Nave industrial 88,00 × 44,00", f(nave, 0), f(nave / sup_t * 100, 1)],
             ["  incluye recargas (ángulo SO)", f(L.ANEXOS[1].rect.area, 0), ""],
             ["Servicios al personal y oficinas", f(L.ANEXOS[0].rect.area, 0), f(L.ANEXOS[0].rect.area / sup_t * 100, 1)],
             ["Sala técnica norte", f(L.ANEXOS[2].rect.area, 0), f(L.ANEXOS[2].rect.area / sup_t * 100, 1)],
             ["Alero de descarga de MP", f(_ext("PL-N").area, 0), f(_ext("PL-N").area / sup_t * 100, 1)],
             ["Superficie cubierta total", f(cub, 0), f(cub / sup_t * 100, 1)],
             ["FOS = cubierta / terreno", "", f(cub / sup_t, 2)]]
    xs2 = h.fx0 + 400
    ys2 = h.fy0 + 128
    y2 = pl.tabla(xs2, ys2, cols, filas, 4.2, 2.0, "Cuadro de superficies")
    pl.parrafo(["Nave: pórticos metálicos de dos luces (19,40 y 24,60 m) cada 8 m; altura libre 8,00 m;",
                "zócalo de bloque 2,40 m y chapa; anexos de mampostería. Pisos de hormigón llaneado con",
                "demarcación IRAM 10005; sanitarios con revestimiento hasta 2,10 m (Dec. 351/79 cap. 5)."],
               xs2, y2 - 3, 2.0)
    # locales (servicios, recargas y apoyo)
    cols = [("Local", 70, "l"), ("m²", 14, "r"), ("Equipamiento / función", 128, "l")]
    sel = [s for s in L.LOCALES if s.cat != "CIRC"] + [s for s in L.SECTORES if s.cat in ("AUX", "CAL")]
    filas = [[f"{s.cod} {s.nombre}"[:44], f(s.rect.area, 1), s.nota[:84]] for s in sel]
    xl = h.fx0 + 640
    pl.tabla(xl, pl.P(0, y0)[1] - 6, cols, filas, 3.5, 1.6, "Locales y su equipamiento (ningún local vacío)")
    return h


def corte(pc):
    """Corte transversal A-A de la nave (norte-sur, por el eje 4), dos luces, 1:100."""
    y0 = 0.0
    W = L.NAVE_A
    ejes = L.EJES_Y
    pc.linea((-4.0, y0), (W + 10.0, y0), "A-EXTERIOR")
    for x in ejes:
        pc.rect(L.R(x - 0.2, 0.0, x + 0.2, 8.0), "A-MURO")
    for a, b in zip(ejes, ejes[1:]):
        m = (a + b) / 2
        hl = 1.6 * (b - a) / 25.0
        pc.pl([(a - 0.3, 8.0), (m, 8.0 + hl), (b + 0.3, 8.0)], "A-MURO")
        pc.pl([(a + 0.2, 7.2), (m, 7.2 + hl * 0.94), (b - 0.2, 7.2)], "A-EQUIPO")
        n = max(4, int((b - a) / 2.5))
        for i in range(1, n):
            x = a + i * (b - a) / n
            yt = 8.0 + hl * (1 - abs(x - m) / ((b - a) / 2))
            yb = 7.2 + hl * 0.94 * (1 - abs(x - m) / ((b - a) / 2))
            pc.linea((x, yb), (x, yt), "A-EQUIPO-FINO")
    pc.rect(L.R(ejes[1] - 0.6, 8.2, ejes[1] + 0.6, 8.5), "A-EQUIPO")
    # sala técnica y alero al norte
    pc.rect(L.R(W + 0.2, 0.0, W + 6.0, 4.0), "A-LOCAL")
    pc.texto("ST", (W + 3.1, 2.0), 2.2, A.MIDDLE_CENTER)
    pc.linea((-0.6, 2.4), (-0.2, 2.4), "A-EQUIPO")
    pc.texto("Zócalo de bloque 2,40", (-0.8, 1.2), 2.0, A.MIDDLE_RIGHT)
    for a, b in zip(ejes, ejes[1:]):
        pc.cota((a, 0.0), (b, 0.0), -6, True)
    pc.cota((W, 0.0), (W, 8.0), 14, False)
    pc.cota((W, 8.0), (W, 9.6), 14, False)
    pc.texto("NPT ±0,00", (0.6, 0.4), 2.2, A.BOTTOM_LEFT)
    pc.texto("Altura libre bajo cercha 8,00 m", (ejes[1] / 2, 5.0), 2.5, A.MIDDLE_CENTER)
    pc.texto("Pasillo central", (21.5, 0.4), 2.0, A.BOTTOM_CENTER)
    pc.texto("Banda sur: recargas, carros, PT, terminación", (ejes[1] / 2, 2.0), 2.0, A.MIDDLE_CENTER)
    pc.texto("Banda norte: MP, corte y línea", ((ejes[1] + W) / 2 + 2, 2.0), 2.0, A.MIDDLE_CENTER)
    pc.texto("CORTE TRANSVERSAL A-A (por eje 4) - 1:200", pc.P(0.0, 11.5), 3.0, A.BOTTOM_LEFT, papel=True)
    pc.texto("S", pc.P(0.0, -2.5), 2.5, A.MIDDLE_CENTER, papel=True)
    pc.texto("N", pc.P(W, -2.5), 2.5, A.MIDDLE_CENTER, papel=True)


