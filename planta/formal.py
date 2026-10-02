"""FL_PI_04 - Plano formal normalizado: implantación, planta acotada de la nave, servicios y corte."""

import math

from ezdxf.enums import TextEntityAlignment

from . import layout as L
from . import calculos as C
from . import dibujo as D
from . import planos as PL
from .planos import f, hoja, titulo_hoja

A = TextEntityAlignment
TOT = 4


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


EXT_ANEXOS = [(-1.1, 20.8), (-1.1, 29.8), (-12.0, 20.8), (-12.0, 34.6), (41.0, 47.0), (52.0, 46.4)]


def _ext(cod):
    return next(r for c, n, r, t in L.EXTERIOR if c == cod)


# ================================================================ H1 implantación
def h1_implantacion(doc, ox):
    h = hoja(doc, "A0", ox, "Implantación general", "Terreno 170 × 125 m, nave, anexos y exteriores", "FL_PI_04",
             1, TOT, "1:200", "Plano de implantación", "Estructura metálica")
    k = 200
    x0, y0, x1, y1 = L.TERRENO
    pl = D.Plano(h, k, (x0, y0 - 6), (h.fx0 + 30, h.fy1 - 40 - (y1 - y0 + 6) * 1000 / k))
    titulo_hoja(pl, h, "FL_PI_04 - PLANO FORMAL NORMALIZADO - HOJA 1: IMPLANTACIÓN GENERAL",
                "Parque Industrial Villa de Luján, Gral. Heredia 3220, Sarandí (Avellaneda). Escala 1:200. "
                "Cotas en metros. Norte arriba.")
    PL.sitio(pl, rotulos=False)
    D.sectores(pl, relleno=True)
    D.locales(pl, rotulos=False, relleno=True)
    D.muros(pl)
    D.puertas(pl, etiquetas=True, h=1.8)
    D.ejes(pl, r_glob=2.8, sobresale=2.0, completo=False)
    # nombres de los elementos exteriores
    for cod, nom, r, tipo in L.EXTERIOR:
        pl.texto(cod, (r.c[0], r.c[1] + 0.9), 2.0, A.MIDDLE_CENTER)
        if r.w > 9:
            pl.texto(nom if len(nom) < 44 else nom[:42] + "…", (r.c[0], r.c[1] - 1.0), 1.5, A.MIDDLE_CENTER)
    pl.texto("NAVE INDUSTRIAL 88,00 × 44,00 m - 3872 m² (recorrido en U)", (40.0, 21.4), 4.0, A.MIDDLE_CENTER)
    pl.texto("SERVICIOS", (-9.0, 28.4), 3.0, A.MIDDLE_CENTER, rot=90)
    pl.texto("RECARGAS", (9.2, 9.6), 3.0, A.MIDDLE_CENTER)
    for cod, a, b, uso in L.PORTONES_TERRENO:
        pl.texto(f"{cod} ({f(b - a, 2)} m)", ((a + b) / 2, y0 - 1.8), 1.8, A.MIDDLE_CENTER)
    # radios de giro de camiones (semi 12,5 m exterior) en las esquinas del anillo
    for c, a0, a1 in (((-29.0 + 12.5, 56.5 - 12.5), 90, 180), ((119.0 - 12.5, 56.5 - 12.5), 0, 90)):
        pl.arco(c, 12.5, a0, a1, "A-SECTOR")
    pl.texto("R 12,50", (-22.0, 49.0), 1.8, A.MIDDLE_CENTER)
    pl.texto("R 12,50", (114.0, 49.0), 1.8, A.MIDDLE_CENTER)
    # cotas generales del terreno y de la implantación
    pl.cota((x0, y1), (x1, y1), 12, True)
    pl.cota((x1, y0), (x1, y1), 12, False)
    pl.cota((x0, 44.0), (0.0, 44.0), 6, True)
    pl.cota((88.0, 44.0), (x1, 44.0), 6, True)
    pl.cota((0.0, 44.0), (88.0, 44.0), 16, True)
    pl.cota((88.0, 0.0), (88.0, 44.0), 10, False)
    pl.cota((88.0, 44.0), (88.0, y1), 10, False)
    pl.cota((88.0, y0), (88.0, 0.0), 10, False)
    pl.cota((-18.0, 19.0), (0.0, 19.0), -6, True)
    pl.cota((-18.0, 19.0), (-18.0, 37.8), -6, False)
    pl.cota((36.0, 50.0), (46.0, 50.0), 3, True)
    pl.cota((-36.0, 0.0), (-29.0, 0.0), -3, True)
    pl.cota((119.0, 0.0), (126.0, 0.0), -3, True)
    pl.cota((88.0, 14.0), (119.0, 14.0), 0, True)
    # cuadro de superficies
    sup_t = (x1 - x0) * (y1 - y0)
    nave = L.NAVE_L * L.NAVE_A
    anex = sum(s.rect.area for s in L.ANEXOS if s.cod != "RC")
    cub = nave + anex + _ext("PL-N").area
    xt = pl.P(x1, 0)[0] + 14
    yt = h.fy1 - 36
    cols = [("Concepto", 70, "l"), ("m²", 22, "r"), ("%", 16, "r")]
    filas = [["Terreno 170,00 × 125,00", f(sup_t, 0), "100,0"],
             ["Nave industrial 88,00 × 44,00", f(nave, 0), f(nave / sup_t * 100, 1)],
             ["  incluye recargas (ángulo SO)", f(L.ANEXOS[1].rect.area, 0), ""],
             ["Servicios al personal y oficinas", f(L.ANEXOS[0].rect.area, 0), f(L.ANEXOS[0].rect.area / sup_t * 100, 1)],
             ["Sala técnica norte", f(L.ANEXOS[2].rect.area, 0), f(L.ANEXOS[2].rect.area / sup_t * 100, 1)],
             ["Alero de descarga de MP (norte)", f(_ext("PL-N").area, 0), f(_ext("PL-N").area / sup_t * 100, 1)],
             ["Superficie cubierta total", f(cub, 0), f(cub / sup_t * 100, 1)],
             ["FOS = cubierta / terreno", "", f(cub / sup_t, 2).replace(",", ",")],
             ["Reserva de ampliación (este)", f(_ext("AMP").area, 0), ""]]
    y = pl.tabla(xt, yt, cols, filas, 5.0, 2.4, "Cuadro de superficies")
    y = pl.parrafo(["FOS, FOT, retiros y altura máxima: verificar con el reglamento del",
                    "parque industrial y el código de Avellaneda (Ley 13.744 de parques",
                    "industriales PBA; habilitación Ley 11.459)."], xt, y - 4, 2.2)
    cols2 = [("Código", 16, "c"), ("Elemento exterior", 92, "l")]
    filas2 = [[c_, n_] for c_, n_, r_, t_ in L.EXTERIOR]
    filas2 += [["G1", "Portón de camiones de MP, scrap y pintor (entrada)"],
               ["G2", "Portón de autos del personal"], ["G3", "Portón de camiones de PT y carros (salida)"],
               ["G4", "Ingreso peatonal con garita"]]
    y = pl.tabla(xt, y - 12, cols2, filas2, 4.6, 2.2, "Referencias de exteriores")
    pl.parrafo(["Circulación de camiones en anillo de un sentido (G1 -> oeste -> norte -> este -> G3):",
                "los camiones de MP descargan en la playa norte o en la bahía interior oeste y los de PT",
                "en los muelles sur sin cruzarse. Autos y peatones entran por el frente, separados",
                "de los camiones. Radio de giro exterior del semi: 12,50 m.",
                "Pavimento de hormigón en calles, playas y patios; veredas perimetrales de 1,20 m.",
                "Nave: pórticos metálicos de dos luces (19,40 y 24,60 m) cada 8 m, columnas centrales en el",
                "eje B, al borde del pasillo central; altura libre bajo",
                "cercha 8,00 m; cerramiento de zócalo de bloque de 2,40 m y chapa; cubierta de chapa",
                "con aislación y lucernarios; anexos de mampostería."], xt, y - 4, 2.2)
    return h


# ================================================================ H2 / H3 planta acotada 1:100
def planta_100(doc, ox, n, xa, xb):
    y0, y1 = -9.0, 58.0
    h = hoja(doc, "A0", ox, f"Planta de la nave {'oeste' if n == 2 else 'este'}",
             f"Ejes {1 + int(round(xa / 8)) if xa > 0 else 1} a {min(12, 1 + int(round(xb / 8)))} - acotada", "FL_PI_04",
             n, TOT, "1:100", "Plano de planta", "Estructura metálica")
    k = 100
    pl = D.Plano(h, k, (xa, y0), (h.fx0 + 22, h.fy1 - 34 - (y1 - y0) * 1000 / k))
    titulo_hoja(pl, h, f"FL_PI_04 - PLANO FORMAL NORMALIZADO - HOJA {n}: PLANTA DE LA NAVE, SECTOR "
                       f"{'OESTE' if n == 2 else 'ESTE'} (x = {f(xa, 0)} a {f(xb, 0)} m)",
                "Escala 1:100. Cotas en metros. Ejes estructurales 1 a 12 cada 8,00 m y A-B-C (luces de 19,40 y 24,60 m, "
                "columnas centrales en el eje B).")
    # se dibuja la planta completa y se recorta a la ventana de la hoja
    antes = D.handles(pl.m)
    D.sectores(pl, relleno=False)
    D.locales(pl, rotulos=True, h=1.8)
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
    # nombres de sectores con superficie
    for s in L.SECTORES:
        r = s.rect
        if r.x1 < xa or r.x0 > xb:
            continue
        pl.texto(s.cod, (r.x0 + 0.3, r.y1 - 0.3), 2.2, A.TOP_LEFT)
        pl.texto(f"{f(r.area, 1)} m²", (r.x0 + 0.3, r.y1 - 0.6 - 2.6 / pl.s * 1.0), 1.8, A.TOP_LEFT)
    for s in L.LOCALES:
        pl.texto(f"{f(s.rect.area, 1)} m²", (s.rect.c[0], s.rect.c[1] - 0.45), 1.4, A.MIDDLE_CENTER)
    # sendas, matafuegos y salidas
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
    # cotas: ejes (arriba), total y ancho de nave; cadenas de vanos en fachadas norte y sur
    xs = [x for x in L.EJES_X if xa - 0.1 <= x <= xb + 0.1]
    pl.cadena(xs, L.NAVE_A, 9.0, True)
    if len(xs) > 1:
        pl.cota((xs[0], L.NAVE_A), (xs[-1], L.NAVE_A), 14.0, True)
    vn = sorted([v for p in L.PUERTAS if p.muro == "N" for v in (p.a, p.b) if xa <= v <= xb] + xs)
    pl.cadena(vn, L.NAVE_A, 4.5, True)
    vs = sorted([v for p in L.PUERTAS if p.muro == "S" for v in (p.a, p.b) if xa <= v <= xb] + xs)
    pl.cadena(vs, -6.5, -3.0, True)
    if n == 2:
        pl.cota((0.0, 0.0), (0.0, L.NAVE_A), -10.0, False)
        vo = sorted([0.0, L.NAVE_A] + [v for p in L.PUERTAS if p.muro == "O" for v in (p.a, p.b)])
        pl.cadena(vo, 0.0, -5.5, False)
    else:
        pl.cota((L.NAVE_L, 0.0), (L.NAVE_L, L.NAVE_A), 12.0, False)
        ve = sorted([0.0, L.NAVE_A] + [v for p in L.PUERTAS if p.muro == "E" for v in (p.a, p.b)])
        pl.cadena(ve, L.NAVE_L, 6.0, False)
    # anchos de pasillos (cotas interiores)
    for p in L.PASILLOS:
        r = p.rect
        if r.x1 < xa or r.x0 > xb:
            continue
        if r.w >= r.h:
            xm = min(max(r.x0 + 2.0, xa + 2.0), xb - 2.0)
            if p.cod == "PC":
                xm = xa + 6.0
            pl.cota((xm, r.y0), (xm, r.y1), 0.0, False, texto=f"{p.cod} <>")
        else:
            ym = r.y0 + min(3.0, r.h / 2)
            pl.cota((r.x0, ym), (r.x1, ym), 0.0, True, texto=f"{p.cod} <>")
    # anexos
    for s in L.ANEXOS:
        r = s.rect
        if r.x0 >= xa - 0.1 and r.x1 <= xb + 0.1:
            if s.cod == "RC":
                continue
            if s.cod == "SV":
                pl.cota((r.x0, r.y0), (r.x1, r.y0), -4.0, True)
                pl.cota((r.x1, r.y0), (r.x1, r.y1), 4.0, False)
            else:
                pl.cota((r.x0, r.y1), (r.x1, r.y1), 3.0, True)
    # línea de continuación
    xc = xb if n == 2 else xa
    pl.linea((xc, y0 + 1), (xc, y1 - 1), "A-EJE")
    pl.texto(f"Continúa en hoja {3 if n == 2 else 2}", (xc + (-1 if n == 2 else 1), y1 - 2), 2.5,
             A.MIDDLE_RIGHT if n == 2 else A.MIDDLE_LEFT)
    D.recortar(pl, antes, xa, y0, xb, y1)
    # tabla de equipos del sector
    xt = pl.P(xb, 0)[0] + 12
    yt = h.fy1 - 36
    eqs = [e for e in L.EQUIPOS if xa <= e.rect.c[0] < xb]
    cols = [("Cód.", 11, "c"), ("Equipo", 80, "l"), ("Medidas m", 24, "c"), ("kW", 11, "c"), ("Op.", 9, "c"),
            ("Fuente", 44, "l")]
    filas = [[e.cod, e.nombre, f"{f(e.rect.w, 2)} × {f(e.rect.h, 2)}", f(e.kw, 1) if e.kw else "-", e.op or "-",
              e.fuente.replace("C ", "Cotiz. ").replace("E", "Estimado", 1) if e.fuente.startswith("E") else
              e.fuente.replace("C ", "Cotiz. ")] for e in eqs]
    y = pl.tabla(xt, yt, cols, filas, 3.9, 1.8, "Equipos (medidas en planta, largo × ancho)")
    y = pl.parrafo(["Referencias: cada equipo se dibuja en planta a escala con sus partes (bastidor, rodillos,",
                    "mordazas, motores, tableros), resguardos en rojo y operario en su puesto (magenta);",
                    "en trazos, partes elevadas; óvalo = código del equipo; círculo rojo = barrido de pluma;",
                    "líneas amarillas = demarcación de pasillos (IRAM 10005); cebra = senda peatonal;",
                    "punto rojo numerado = extintor ABC 10 kg (IRAM 3517-2, recorrido ≤ 20 m);",
                    "flecha verde = salida de emergencia 1,10 m con barral antipánico."], xt, y - 4, 2.1)
    return h


def mascara(pl, xa, xb, y0, y1):
    """Tapa con blanco lo dibujado fuera de la ventana de la hoja (izquierda y derecha)."""
    for a, b in ((xa - 80.0, xa - 0.05), (xb + 0.05, xb + 80.0)):
        pl.relleno([(a, y0 - 20), (b, y0 - 20), (b, y1 + 20), (a, y1 + 20)], (255, 255, 255), "A-RELLENO")


# ================================================================ H4 servicios 1:50, baño accesible 1:20 y corte 1:100
def artefacto(pl, tipo, c, rot=0):
    """Artefactos sanitarios y mobiliario en planta (m)."""
    x, y = c
    capa = "A-SANITARIO"
    if tipo == "inodoro":
        pl.rect(L.R(x - 0.2, y, x + 0.2, y + 0.2), capa)
        pts = PL.circ_pts((x, y + 0.45), 0.22, 20)
        pl.pl(pts, capa, True)
    elif tipo == "lavabo":
        pl.rect(L.R(x - 0.25, y, x + 0.25, y + 0.45), capa)
        pl.circulo((x, y + 0.2), 0.14, capa)
    elif tipo == "mingitorio":
        pl.rect(L.R(x - 0.2, y, x + 0.2, y + 0.35), capa)
    elif tipo == "ducha":
        pl.rect(L.R(x - 0.45, y, x + 0.45, y + 0.9), capa)
        pl.linea((x - 0.45, y), (x + 0.45, y + 0.9), capa)
        pl.circulo((x, y + 0.45), 0.05, capa)
    elif tipo == "armario":
        pl.rect(L.R(x, y, x + 0.3, y + 0.5), capa)
    elif tipo == "banco":
        pl.rect(L.R(x, y, x + 1.6, y + 0.4), capa)


def servicios_detalle(pl):
    """Distribución de artefactos y mobiliario del bloque de servicios (m)."""
    # vestuario H: 2 filas de armarios dobles (0,30 × 0,50) enfrentadas y bancos
    for i in range(24):
        artefacto(pl, "armario", (-17.6 + i * 0.3, 29.25))
        artefacto(pl, "armario", (-17.6 + i * 0.3, 24.6))
    for i in range(3):
        artefacto(pl, "banco", (-17.2 + i * 2.3, 26.9))
    pl.texto("62 armarios dobles (dos alturas)", (-14.1, 26.4), 1.2, A.MIDDLE_CENTER)
    # sanitarios H: 3 inodoros en box, 5 mingitorios, 6 lavabos, 4 duchas
    for i in range(3):
        artefacto(pl, "inodoro", (-9.7 + i * 0.95, 24.6))
        pl.rect(L.R(-10.15 + i * 0.95, 24.4, -9.25 + i * 0.95, 25.7), "A-SANITARIO")
    for i in range(5):
        artefacto(pl, "mingitorio", (-7.1 + i * 0.35, 24.6))
    for i in range(6):
        artefacto(pl, "lavabo", (-9.8 + i * 0.6, 29.3))
    for i in range(4):
        artefacto(pl, "ducha", (-7.0 + (i % 2) * 1.0, 26.4 + (i // 2) * 1.2))
    # mujeres: 14 armarios, 2 inodoros, 2 lavabos, 2 duchas
    for i in range(14):
        artefacto(pl, "armario", (-17.6 + i * 0.3, 23.65))
    artefacto(pl, "banco", (-17.0, 22.4))
    for i in range(2):
        artefacto(pl, "inodoro", (-12.6 + i * 1.0, 19.0))
        pl.rect(L.R(-13.1 + i * 1.0, 18.8, -12.1 + i * 1.0, 20.1), "A-SANITARIO")
        artefacto(pl, "lavabo", (-17.2 + i * 0.6, 19.0))
        artefacto(pl, "ducha", (-15.4 + i * 1.0, 19.0))
    # sanitario accesible: círculo Ø 1,50 m, inodoro con 0,80 m libre lateral
    artefacto(pl, "inodoro", (-9.75, 21.8))
    artefacto(pl, "lavabo", (-8.3, 23.6))
    pl.pl(PL.circ_pts((-8.9, 22.8), 0.75, 32), "A-SANITARIO", True)
    pl.texto("Ø 1,50", (-8.9, 22.8), 1.1, A.MIDDLE_CENTER)
    # lactario y primeros auxilios
    pl.rect(L.R(-9.9, 19.0, -9.1, 19.8), "A-SANITARIO")
    pl.rect(L.R(-8.6, 20.6, -8.0, 21.2), "A-SANITARIO")
    pl.rect(L.R(-7.2, 22.6, -5.2, 23.4), "A-SANITARIO")
    pl.rect(L.R(-3.4, 19.0, -2.4, 20.6), "A-SANITARIO")
    # comedor: 5 mesas de 6 plazas y office
    for i in range(5):
        x = -17.2 + (i % 3) * 3.2
        y = 13.2 if i < 3 else 11.8
        pl.rect(L.R(x, y, x + 2.0, y + 0.8), "A-SANITARIO")
    pl.rect(L.R(-7.6, 11.4, -6.4, 14.4), "A-SANITARIO")
    pl.texto("office", (-7.0, 12.9), 1.2, A.MIDDLE_CENTER, rot=90)
    # oficinas: 6 puestos
    for i in range(6):
        x = -17.4 + (i % 3) * 2.4
        y = 15.4 if i < 3 else 17.3
        pl.rect(L.R(x, y, x + 1.4, y + 0.7), "A-SANITARIO")
    # hall: mostrador y reloj de fichado
    pl.rect(L.R(-5.6, 16.4, -3.0, 17.0), "A-SANITARIO")
    pl.circulo((-2.6, 12.2), 0.15, "A-SANITARIO")


def h4_servicios(doc, ox):
    h = hoja(doc, "A0", ox, "Servicios y sanitarios", "Planta 1:50, sanitario accesible 1:20, corte 1:100",
             "FL_PI_04", TOT, TOT, "1:50", "Plano de detalle", "Mampostería / estructura metálica")
    # ---- planta de servicios 1:50 (x -18,6..0,6, y 10,4..30,6)
    P0 = (h.fx0 + 25, h.fy1 - 60 - 23 * 20)
    pl = D.Plano(h, 50, (-19.5, 16.8), P0)
    pl_old = D.Plano(h, 50, (-19.5, 9.0), P0)
    titulo_hoja(pl, h, "FL_PI_04 - PLANO FORMAL NORMALIZADO - HOJA 4: SERVICIOS, SANITARIOS Y CORTE",
                "Planta del bloque de servicios 1:50; sanitario accesible 1:20; corte transversal de la nave 1:100. "
                "Cotas en metros.")
    antes = D.handles(pl.m)
    D.locales(pl, rotulos=False)
    D.muros(pl)
    D.puertas(pl, etiquetas=True, h=2.5)
    servicios_detalle(pl_old)
    for s_ in L.LOCALES:
        if s_.rect.x1 > 0.5:
            continue
        pl.texto(s_.nombre if len(s_.nombre) < 30 else s_.nombre[:28] + "…", (s_.rect.c[0], s_.rect.y0 + 0.9),
                 2.0, A.MIDDLE_CENTER, rot=90 if s_.rect.w < 2.5 else 0)
        pl.texto(f"{f(s_.rect.area, 1)} m²", (s_.rect.c[0], s_.rect.y0 + 0.45), 1.8, A.MIDDLE_CENTER)
    D.recortar(pl, antes, -18.6, 18.2, 1.2, 38.4)
    pl.texto("NAVE: pasillo central y senda peatonal", (0.9, 28.0), 2.5, A.MIDDLE_CENTER, rot=90)
    pl.texto("BLOQUE DE SERVICIOS AL PERSONAL Y OFICINAS - 1:50", pl.P(-18.0, 40.3), 3.0, A.BOTTOM_LEFT, papel=True)
    xs = sorted({v for s_ in L.LOCALES if s_.rect.x1 < 0.5 and s_.rect.y1 > 36.8 for v in (s_.rect.x0, s_.rect.x1)})
    pl.cadena(xs, 37.8, 10.0, True)
    xs2 = sorted({v for s_ in L.LOCALES if s_.rect.x1 < 0.5 and s_.rect.y0 < 19.3 for v in (s_.rect.x0, s_.rect.x1)})
    pl.cadena(xs2, 19.0, -8.0, True)
    pl.cota((-18.0, 19.0), (0.0, 19.0), -16.0, True)
    pl.cadena([19.0, 22.4, 26.4, 32.0, 37.8], -18.0, -10.0, False)
    pl.cota((-18.0, 19.0), (-18.0, 37.8), -18.0, False)
    # ---- sanitario accesible 1:20 (dibujo de detalle en coordenadas propias del local)
    pa = D.Plano(h, 20, (57.6, -3.2), (h.fx0 + 470, h.fy1 - 60 - 70))
    pa.rect(L.R(58.0, -2.8, 60.4, -0.2), "A-LOCAL")
    pa.relleno([(57.8, -3.0), (60.6, -3.0), (60.6, -2.8), (57.8, -2.8)], (70, 70, 70), "A-MURO")
    pa.relleno([(57.8, -0.2), (60.6, -0.2), (60.6, 0.0), (57.8, 0.0)], (70, 70, 70), "A-MURO")
    pa.relleno([(57.8, -3.0), (58.0, -3.0), (58.0, 0.0), (57.8, 0.0)], (70, 70, 70), "A-MURO")
    pa.relleno([(60.4, -3.0), (60.6, -3.0), (60.6, 0.0), (60.4, 0.0)], (70, 70, 70), "A-MURO")
    pa.pl([(58.2, -0.2), (58.2, -0.6), (58.9, -0.6), (58.9, -0.2)], "A-SANITARIO", True)
    pa.pl(PL.circ_pts((58.55, -0.85), 0.22, 24), "A-SANITARIO", True)
    pa.pl(PL.circ_pts((59.35, -1.65), 0.75, 48), "A-SANITARIO", True)
    pa.rect(L.R(59.85, -3.0 + 0.2, 60.35, -2.35), "A-SANITARIO")
    pa.linea((58.05, -1.0), (58.05, -1.9), "A-EQUIPO")
    pa.linea((59.05, -0.5), (59.05, -1.3), "A-EQUIPO")
    pa.arco((58.0, -2.8), 0.9, 0, 90, "A-ABERTURA")
    pa.texto("Ø 1,50 libre", (59.35, -1.65), 2.5, A.MIDDLE_CENTER)
    pa.texto("barra fija", (58.1, -2.0), 2.0, A.TOP_LEFT)
    pa.texto("barra rebatible", (59.1, -1.35), 2.0, A.TOP_LEFT)
    pa.cota((58.0, -0.2), (58.55, -0.2), 5, True)
    pa.cota((58.55, -0.2), (60.4, -0.2), 5, True)
    pa.cota((58.0, -2.8), (60.4, -2.8), -8, True)
    pa.cota((60.4, -2.8), (60.4, -0.2), 8, False)
    pa.texto("SANITARIO ACCESIBLE SV-AC - 1:20 (Ley 24.314, Dec. 914/97)", pa.P(57.8, 0.6), 3.0, A.BOTTOM_LEFT,
             papel=True)
    pa.parrafo(["Inodoro a 0,45-0,50 m de altura; eje a 0,45 m del muro con barra fija;",
                "espacio lateral libre ≥ 0,80 m del lado de transferencia con barra rebatible;",
                "lavatorio sin pie a 0,80-0,85 m; espejo inclinado; puerta de 0,90 m que abre",
                "hacia afuera; accionamiento de canilla por palanca; timbre de emergencia."],
               pa.P(57.8, -3.4)[0], pa.P(57.8, -3.4)[1] - 14, 2.2)
    # ---- corte transversal de la nave 1:100
    pc = D.Plano(h, 100, (-4.0, -1.0), (h.fx0 + 470, h.fy0 + 90))
    corte(pc)
    # ---- tabla de locales
    xt = h.fx1 - 335
    yt = h.fy1 - 36
    cols = [("Local", 72, "l"), ("m²", 16, "r"), ("Equipamiento", 104, "l")]
    filas = [[f"{s.cod} {s.nombre}", f(s.rect.area, 1), s.nota[:62]] for s in L.LOCALES]
    y = pl.tabla(xt, yt, cols, filas, 4.2, 1.9, "Locales de servicios y recargas")
    pl.parrafo(["Pisos lavables y antideslizantes; revestimiento sanitario hasta 2,10 m; ventilación natural",
                "o mecánica; agua caliente y fría en duchas y lavabos (Dec. 351/79 cap. 5); altura mínima",
                "de locales 3,00 m; separación por sexo con acceso independiente; vestuarios contiguos",
                "a los sanitarios (art. 50). Paso a planta PP-1 directo al pasillo central de personal."],
               xt, y - 4, 2.1)
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
    pc.texto("CORTE TRANSVERSAL A-A (por eje 4) - 1:100", pc.P(0.0, 11.5), 3.0, A.BOTTOM_LEFT, papel=True)
    pc.texto("S", pc.P(0.0, -2.5), 2.5, A.MIDDLE_CENTER, papel=True)
    pc.texto("N", pc.P(W, -2.5), 2.5, A.MIDDLE_CENTER, papel=True)


def fl_pi_04(doc, ox, n):
    if n == 1:
        return h1_implantacion(doc, ox)
    if n == 2:
        return planta_100(doc, ox, 2, -20.0, 42.0)
    if n == 3:
        return planta_100(doc, ox, 3, 42.0, 104.0)
    return h4_servicios(doc, ox)
