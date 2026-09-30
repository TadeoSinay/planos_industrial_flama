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


EXT_ANEXOS = [(39.0, -7.0), (54.0, -7.0), (65.0, -7.0), (72.0, -14.0), (84.0, -8.7), (96.5, -8.7), (80.0, -1.0),
              (58.0, 37.2), (46.0, 42.0), (108.0, 42.0)]


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
    pl.texto("NAVE INDUSTRIAL 120,00 × 36,00 m - 4320 m²", (60.0, 18.0), 4.0, A.MIDDLE_CENTER)
    pl.texto("SERVICIOS", (52.0, -6.5), 3.0, A.MIDDLE_CENTER)
    pl.texto("RECARGAS", (84.0, -8.5), 3.0, A.MIDDLE_CENTER)
    for cod, a, b, uso in L.PORTONES_TERRENO:
        pl.texto(f"{cod} ({f(b - a, 2)} m)", ((a + b) / 2, y0 - 1.8), 1.8, A.MIDDLE_CENTER)
    # radios de giro de camiones (semi 12,5 m exterior) en las esquinas del anillo
    for c, a0, a1 in (((-13.0 + 12.5, 57.0 - 12.5), 90, 180), ((133.0 - 12.5, 57.0 - 12.5), 0, 90)):
        pl.arco(c, 12.5, a0, a1, "A-SECTOR")
    pl.texto("R 12,50", (-2.0, 50.0), 1.8, A.MIDDLE_CENTER)
    pl.texto("R 12,50", (122.0, 50.0), 1.8, A.MIDDLE_CENTER)
    # cotas generales del terreno y de la implantación
    pl.cota((x0, y1), (x1, y1), 12, True)
    pl.cota((x1, y0), (x1, y1), 12, False)
    pl.cota((x0, 36.0), (0.0, 36.0), 6, True)
    pl.cota((120.0, 36.0), (x1, 36.0), 6, True)
    pl.cota((0.0, 36.0), (120.0, 36.0), 16, True)
    pl.cota((-4.0, 0.0), (-4.0, 36.0), -4, False)
    pl.cota((-4.0, 36.0), (-4.0, y1), -4, False)
    pl.cota((-8.0, y0), (-8.0, 0.0), -8, False)
    pl.cota((38.0, -13.0), (66.0, -13.0), -6, True)
    pl.cota((70.0, -17.0), (98.0, -17.0), -6, True)
    pl.cota((101.0, -17.0), (101.0, 0.0), 4, False)
    pl.cota((36.0, -13.0), (36.0, 0.0), -4, False)
    pl.cota((-20.0, 0.0), (-13.0, 0.0), -3, True)
    pl.cota((133.0, 0.0), (140.0, 0.0), -3, True)
    pl.cota((120.0, 20.0), (133.0, 20.0), 0, True)
    # cuadro de superficies
    sup_t = (x1 - x0) * (y1 - y0)
    nave = L.NAVE_L * L.NAVE_A
    anex = sum(s.rect.area for s in L.ANEXOS)
    cub = nave + anex
    xt = pl.P(x1, 0)[0] + 14
    yt = h.fy1 - 36
    cols = [("Concepto", 70, "l"), ("m²", 22, "r"), ("%", 16, "r")]
    filas = [["Terreno 170,00 × 125,00", f(sup_t, 0), "100,0"],
             ["Nave industrial 120,00 × 36,00", f(nave, 0), f(nave / sup_t * 100, 1)],
             ["Servicios al personal y oficinas", f(L.ANEXOS[0].rect.area, 0), f(L.ANEXOS[0].rect.area / sup_t * 100, 1)],
             ["Recargas (ala propia)", f(L.ANEXOS[1].rect.area, 0), f(L.ANEXOS[1].rect.area / sup_t * 100, 1)],
             ["Sala técnica norte", f(L.ANEXOS[2].rect.area, 0), f(L.ANEXOS[2].rect.area / sup_t * 100, 1)],
             ["Superficie cubierta total", f(cub, 0), f(cub / sup_t * 100, 1)],
             ["FOS = cubierta / terreno", "", f(cub / sup_t, 2).replace(",", ",")],
             ["Reserva de ampliación (norte)", f(L.EXTERIOR[7][2].area, 0), ""]]
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
                "los camiones de MP descargan en la playa norte o en la bahía interior y los de PT en",
                "los muelles este sin cruzarse. Autos y peatones entran por el frente, separados",
                "de los camiones. Radio de giro exterior del semi: 12,50 m.",
                "Pavimento de hormigón en calles, playas y patios; veredas perimetrales de 1,20 m.",
                "Nave: estructura metálica de pórticos de 36 m de luz cada 8 m; altura libre bajo",
                "cercha 8,00 m; cerramiento de zócalo de bloque de 2,40 m y chapa; cubierta de chapa",
                "con aislación y lucernarios; anexos de mampostería."], xt, y - 4, 2.2)
    return h


# ================================================================ H2 / H3 planta acotada 1:100
def planta_100(doc, ox, n, xa, xb):
    y0, y1 = -21.0, 45.0
    h = hoja(doc, "A0", ox, f"Planta de la nave {'oeste' if n == 2 else 'este'}",
             f"Ejes {1 + int(round(xa / 8)) if xa > 0 else 1} a {min(16, 1 + int(round(xb / 8)))} - acotada", "FL_PI_04",
             n, TOT, "1:100", "Plano de planta", "Estructura metálica")
    k = 100
    pl = D.Plano(h, k, (xa, y0), (h.fx0 + 22, h.fy1 - 34 - (y1 - y0) * 1000 / k))
    titulo_hoja(pl, h, f"FL_PI_04 - PLANO FORMAL NORMALIZADO - HOJA {n}: PLANTA DE LA NAVE, SECTOR "
                       f"{'OESTE' if n == 2 else 'ESTE'} (x = {f(xa, 0)} a {f(xb, 0)} m)",
                "Escala 1:100. Cotas en metros. Ejes estructurales 1 a 16 cada 8,00 m y A-B a 36,00 m (luz única, sin "
                "columnas interiores).")
    # se dibuja la planta completa y se recorta a la ventana de la hoja
    antes = D.handles(pl.m)
    D.sectores(pl, relleno=False)
    D.locales(pl, rotulos=True, h=1.8)
    D.pasillos(pl, demarcacion=True, rotulos=False)
    D.equipos(pl, rotulos=True, h=1.6, fino=False)
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
                salida(pl, (m, 34.8), (0, 1))
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
    pl.cadena(vs, -18.0 if n == 3 else -14.0, -3.0, True)
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
            if p.cod == "PP":
                xm = xa + 6.0
            pl.cota((xm, r.y0), (xm, r.y1), 0.0, False, texto=f"{p.cod} <>")
        else:
            ym = r.y0 + min(3.0, r.h / 2)
            pl.cota((r.x0, ym), (r.x1, ym), 0.0, True, texto=f"{p.cod} <>")
    # anexos
    for s in L.ANEXOS:
        r = s.rect
        if r.x0 >= xa - 0.1 and r.x1 <= xb + 0.1:
            if s.cod in ("SV", "RC"):
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
    y = pl.parrafo(["Referencias: rectángulo = equipo (contorno de la máquina con sus accesorios);",
                    "rack con cruz = estantería o pulmón; círculo con radio = pluma giratoria;",
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
    """Distribución de artefactos del bloque de servicios y del núcleo este (m)."""
    # vestuario H: 2 filas de 31 armarios dobles (0,30 × 0,50) enfrentadas y bancos
    for i in range(18):
        artefacto(pl, "armario", (38.4 + i * 0.3, -0.8))
        artefacto(pl, "armario", (38.4 + i * 0.3, -3.3))
    for i in range(3):
        artefacto(pl, "banco", (38.8 + i * 1.8, -1.9))
    pl.texto("62 armarios dobles", (41.2, -4.4), 1.2, A.MIDDLE_CENTER)
    # sanitarios H: 3 inodoros en box, 6 mingitorios, 6 lavabos, 4 duchas
    for i in range(3):
        artefacto(pl, "inodoro", (44.9 + i * 0.95, -1.1))
        pl.rect(L.R(44.45 + i * 0.95, -1.5, 45.35 + i * 0.95, -0.2), "A-SANITARIO")
    for i in range(6):
        artefacto(pl, "mingitorio", (47.9 + i * 0.4, -0.55))
    for i in range(6):
        artefacto(pl, "lavabo", (44.9 + i * 0.6, -5.55))
    for i in range(4):
        artefacto(pl, "ducha", (48.6 + (i % 2) * 1.0, -3.9 + (i // 2) * 1.2))
    # mujeres: 14 armarios, 2 inodoros, 2 lavabos, 2 duchas
    for i in range(7):
        artefacto(pl, "armario", (52.8 + i * 0.3, -0.8))
    artefacto(pl, "banco", (53.0, -2.0))
    for i in range(2):
        artefacto(pl, "inodoro", (55.4 + i * 1.0, -1.1))
        pl.rect(L.R(54.9 + i * 1.0, -1.5, 55.9 + i * 1.0, -0.2), "A-SANITARIO")
        artefacto(pl, "lavabo", (53.3 + i * 0.6, -5.55))
        artefacto(pl, "ducha", (56.3 + i * 1.0, -4.9))
    # sanitario accesible: círculo Ø 1,50 m, inodoro con 0,80 m libre lateral
    artefacto(pl, "inodoro", (58.55, -1.0))
    artefacto(pl, "lavabo", (59.9, -2.75))
    pl.pl(PL.circ_pts((59.4, -1.6), 0.75, 32), "A-SANITARIO", True)
    pl.texto("Ø 1,50", (59.4, -1.6), 1.1, A.MIDDLE_CENTER)
    # comedor: 5 mesas de 6 plazas y office
    for i in range(5):
        x = 56.4 + (i % 3) * 3.0
        y = -9.4 if i < 3 else -11.6
        pl.rect(L.R(x, y, x + 2.0, y + 0.8), "A-SANITARIO")
    pl.rect(L.R(63.8, -12.6, 65.6, -7.8), "A-SANITARIO")
    pl.texto("office", (64.7, -10.2), 1.2, A.MIDDLE_CENTER, rot=90)
    # oficinas: 6 puestos
    for i in range(6):
        x = 43.8 + (i % 3) * 2.5
        y = -9.2 if i < 3 else -11.8
        pl.rect(L.R(x, y, x + 1.4, y + 0.7), "A-SANITARIO")
    # núcleo sanitario este
    for i in range(2):
        artefacto(pl, "inodoro", (70.8 + i * 0.95, -1.1))
        pl.rect(L.R(70.35 + i * 0.95, -1.5, 71.25 + i * 0.95, -0.2), "A-SANITARIO")
        artefacto(pl, "mingitorio", (72.9 + i * 0.45, -0.55))
        artefacto(pl, "lavabo", (70.8 + i * 0.6, -5.55))
    artefacto(pl, "inodoro", (74.4, -1.1))
    artefacto(pl, "lavabo", (72.4, -5.55))
    pl.pl(PL.circ_pts((74.9, -4.4), 0.75, 32), "A-SANITARIO", True)
    artefacto(pl, "inodoro", (74.9, -5.6))


def h4_servicios(doc, ox):
    h = hoja(doc, "A0", ox, "Servicios y sanitarios", "Planta 1:50, sanitario accesible 1:20, corte 1:100",
             "FL_PI_04", TOT, TOT, "1:50", "Plano de detalle", "Mampostería / estructura metálica")
    # ---- planta de servicios 1:50 (x 37,5..66,5, y -14..1)
    pl = D.Plano(h, 50, (37.3, -18.0), (h.fx0 + 15, h.fy1 - 55 - 19 * 20))
    titulo_hoja(pl, h, "FL_PI_04 - PLANO FORMAL NORMALIZADO - HOJA 4: SERVICIOS, SANITARIOS Y CORTE",
                "Planta del bloque de servicios y del núcleo sanitario este 1:50; sanitario accesible 1:20; corte "
                "transversal de la nave 1:100. Cotas en metros.")
    for xa, xb, pp in ((37.3, 66.7, pl), (69.6, 76.6, None)):
        if pp is None:
            pp = D.Plano(h, 50, (69.6, -18.0), (pl.P(66.7, 0)[0] + 30, pl.p0[1]))
            pn = pp
        antes = D.handles(pp.m)
        D.locales(pp, rotulos=False)
        D.muros(pp)
        D.puertas(pp, etiquetas=True, h=2.5)
        servicios_detalle(pp)
        for s_ in L.LOCALES:
            if s_.rect.x0 < xa or s_.rect.x1 > xb:
                continue
            pp.texto(s_.nombre if len(s_.nombre) < 30 else s_.nombre[:28] + "…", (s_.rect.c[0], s_.rect.y0 + 0.9),
                     2.0, A.MIDDLE_CENTER)
            pp.texto(f"{f(s_.rect.area, 1)} m²", (s_.rect.c[0], s_.rect.y0 + 0.45), 1.8, A.MIDDLE_CENTER)
        D.recortar(pp, antes, xa, -14.2 if xb < 70 else -6.6, xb, 1.2)
        pp.texto("NAVE (pasillo de personal PP)", ((xa + xb) / 2, 1.0), 2.5, A.BOTTOM_CENTER)
    pn.texto("NÚCLEO SANITARIO ESTE (ala de recargas) - 1:50", pn.P(69.6, -7.4), 3.0, A.TOP_LEFT, papel=True)
    pn.cota((70.0, -5.8), (76.0, -5.8), -6, True)
    pn.cota((76.0, -5.8), (76.0, 0.0), 6, False)
    pl.texto("BLOQUE DE SERVICIOS AL PERSONAL Y OFICINAS - 1:50", pl.P(37.3, 5.5), 3.0, A.BOTTOM_LEFT, papel=True)
    xs = sorted({s_.rect.x0 for s_ in L.LOCALES if s_.rect.y1 > -1 and s_.rect.x1 < 67} |
                {s_.rect.x1 for s_ in L.LOCALES if s_.rect.y1 > -1 and s_.rect.x1 < 67})
    pl.cadena(xs, 0.0, 12.0, True)
    xs2 = sorted({s_.rect.x0 for s_ in L.LOCALES if s_.rect.y0 < -7 and s_.rect.x1 < 67} |
                 {s_.rect.x1 for s_ in L.LOCALES if s_.rect.y0 < -7 and s_.rect.x1 < 67})
    pl.cadena(xs2, -13.0, -8.0, True)
    pl.cota((38.0, -13.0), (66.0, -13.0), -16.0, True)
    pl.cadena([-13.0, -7.4, -5.8, 0.0], 38.0, -10.0, False)
    # ---- sanitario accesible 1:20
    pa = D.Plano(h, 20, (57.6, -3.2), (h.fx0 + 30, h.fy0 + 70))
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
    pa.texto("SANITARIO ACCESIBLE - 1:20 (Ley 24.314, Dec. 914/97)", pa.P(57.8, -3.4), 3.0, A.TOP_LEFT, papel=True)
    pa.parrafo(["Inodoro a 0,45-0,50 m de altura; eje a 0,45 m del muro con barra fija;",
                "espacio lateral libre ≥ 0,80 m del lado de transferencia con barra rebatible;",
                "lavatorio sin pie a 0,80-0,85 m; espejo inclinado; puerta de 0,90 m que abre",
                "hacia afuera; accionamiento de canilla por palanca; timbre de emergencia."],
               pa.P(57.8, -3.4)[0], pa.P(57.8, -3.4)[1] - 7, 2.2)
    # ---- corte transversal de la nave y anexos 1:100
    pc = D.Plano(h, 100, (-19.0, -1.0), (h.fx0 + 330, h.fy0 + 75))
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
                "a los sanitarios (art. 50). Núcleo sanitario este con acceso desde la nave (PP-3)."], xt, y - 4, 2.1)
    return h


def corte(pc):
    """Corte transversal A-A de la nave (x fijo = eje 7) con el bloque de servicios, 1:100."""
    y0 = 0.0
    X0, X1 = -13.0, 36.0          # ancho del corte: servicios (13 m) + nave (36 m) en coordenada horizontal
    # terreno
    pc.linea((X0 - 5, y0), (X1 + 8, y0), "A-EXTERIOR")
    # nave: columnas y cercha a dos aguas
    for x in (0.0, 36.0):
        pc.rect(L.R(x - 0.2, 0.0, x + 0.2, 8.0), "A-MURO")
    pc.pl([(-0.3, 8.0), (18.0, 9.8), (36.3, 8.0)], "A-MURO")
    pc.pl([(0.2, 7.2), (18.0, 8.9), (35.8, 7.2)], "A-EQUIPO")
    for i in range(1, 12):
        x = i * 3.0
        yt = 8.0 + 1.8 * (1 - abs(x - 18.0) / 18.0)
        yb = 7.2 + 1.7 * (1 - abs(x - 18.0) / 18.0)
        pc.linea((x, yb), (x, yt), "A-EQUIPO-FINO")
    # servicios: losa a 3,20 m
    pc.rect(L.R(-13.0, 0.0, -0.2, 3.5), "A-LOCAL")
    pc.linea((-13.0, 3.2), (-0.2, 3.2), "A-LOCAL")
    # zócalo de mampostería y chapa
    pc.linea((36.2, 2.4), (36.6, 2.4), "A-EQUIPO")
    pc.texto("Zócalo de bloque 2,40", (37.0, 1.2), 2.0, A.MIDDLE_LEFT)
    # cotas
    pc.cota((0.0, 0.0), (36.0, 0.0), -6, True)
    pc.cota((-13.0, 0.0), (0.0, 0.0), -6, True)
    pc.cota((36.0, 0.0), (36.0, 8.0), 8, False)
    pc.cota((36.0, 8.0), (36.0, 9.8), 8, False)
    pc.cota((-13.0, 0.0), (-13.0, 3.2), -6, False)
    pc.texto("NPT ±0,00", (2.0, 0.4), 2.2, A.BOTTOM_LEFT)
    pc.texto("Altura libre bajo cercha 8,00 m", (18.0, 5.0), 2.5, A.MIDDLE_CENTER)
    pc.texto("PM", (33.8, 0.4), 2.0, A.BOTTOM_CENTER)
    pc.texto("PP", (1.2, 0.4), 2.0, A.BOTTOM_CENTER)
    pc.texto("Servicios h = 3,20 m", (-6.5, 1.6), 2.2, A.MIDDLE_CENTER)
    pc.texto("CORTE TRANSVERSAL A-A (por eje 7) - 1:100", pc.P(-13.0, 11.5), 3.0, A.BOTTOM_LEFT, papel=True)
    pc.texto("S", pc.P(-13.0, -2.5), 2.5, A.MIDDLE_CENTER, papel=True)
    pc.texto("N", pc.P(36.0, -2.5), 2.5, A.MIDDLE_CENTER, papel=True)


def fl_pi_04(doc, ox, n):
    if n == 1:
        return h1_implantacion(doc, ox)
    if n == 2:
        return planta_100(doc, ox, 2, -10.0, 64.0)
    if n == 3:
        return planta_100(doc, ox, 3, 64.0, 132.0)
    return h4_servicios(doc, ox)
