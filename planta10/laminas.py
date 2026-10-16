"""Láminas del layout v10 (DXF para AutoCAD + PDF), formato y rótulo IRAM.

FL_PI10_01  Planta general, implantación y tabla de áreas (1:200)
FL_PI10_02  Puestos y equipos (1:100)
FL_PI10_03  Circulación y flujos de materiales y de personas (1:100)
FL_PI10_04  Almacén de MP, recepción y servicios del ángulo SO (1:50)
FL_PI10_05  Administración y servicios al personal (1:50)
FL_PI10_06  Cortes de la nave (1:100)
FL_PI10_07  Seguridad e higiene: medios de escape, matafuegos, señales, primeros auxilios, gases y residuos (1:100)
"""

import math
from types import SimpleNamespace

import shapely.geometry as sg
from shapely.ops import unary_union
from ezdxf.enums import TextEntityAlignment

from planta import dibujo as D
from planta import simbolos as S
from planta import mobiliario as MO
from planta.planos import hoja, titulo_hoja, f
from . import modelo as M
from . import simb10 as S10
from . import seguridad as SEG

A = TextEntityAlignment

RGB = {"MP": (205, 225, 245), "MAN": (253, 228, 200), "CAR": (248, 217, 192), "PINT": (246, 207, 195),
       "TERM": (215, 238, 210), "PT": (200, 232, 200), "AUX": (228, 228, 228), "LIB": (255, 255, 255),
       "ADM": (226, 236, 248), "SAN": (236, 228, 246)}
RGB_PAS = {"AE": (226, 226, 226), "SP": (255, 244, 180), "PO": (246, 246, 246)}
NOMBRE_CAT = {"MP": "Almacén de MP y recepción", "MAN": "Manuales 1 a 10 kg", "CAR": "Carros 25 a 100 kg",
              "PINT": "Pintura", "TERM": "Terminación de manuales", "PT": "Depósitos de producto terminado",
              "AUX": "Servicios técnicos (mantenimiento, calidad, aire, energía)", "LIB": "Libre / reserva",
              "CIRC": "Pasillos y sendas", "ADM": "Oficinas", "SAN": "Vestuarios y sanitarios"}


def _r(r):
    return SimpleNamespace(x0=r.x0, y0=r.y0, x1=r.x1, y1=r.y1, w=r.x1 - r.x0, h=r.y1 - r.y0,
                           c=((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2), pts=r.pts)


def _corto(nombre, n=48):
    s = nombre.split(" (")[0].split(":")[0]
    return s if len(s) <= n else s[:n - 1].rstrip() + "."


def _cortar(t, n):
    out, ln = [], ""
    for w in t.split():
        if len(ln) + len(w) + 1 > n:
            out.append(ln)
            ln = w
        else:
            ln = (ln + " " + w).strip()
    if ln:
        out.append(ln)
    return out


# ================================================================ elementos de la planta
ROTULO_BLOQUE = {"C16-L", "C16-R", "C10-1"}      # bloques de carros con rótulo propio arriba


def _ocupado(z):
    """Rectángulos de equipos y muebles dentro de la zona (para no escribir encima)."""
    r = z.rect
    out = []
    for e in M.EQUIPOS:
        q = e.rect
        if q.x1 > r.x0 and q.x0 < r.x1 and q.y1 > r.y0 and q.y0 < r.y1:
            out.append(sg.box(q.x0, q.y0, q.x1, q.y1 + (0.3 if e.cod in ROTULO_BLOQUE else 0.0)))
        if e.op > 0:                     # el operario dibujado al frente (0,95 m)
            fr = {"S": sg.box(q.x0, q.y0 - 0.95, q.x1, q.y0), "N": sg.box(q.x0, q.y1, q.x1, q.y1 + 0.95),
                  "E": sg.box(q.x1, q.y0, q.x1 + 0.95, q.y1), "O": sg.box(q.x0 - 0.95, q.y0, q.x0, q.y1)}[e.frente]
            if fr.intersects(sg.box(r.x0, r.y0, r.x1, r.y1)):
                out.append(fr)
    for t, q, fr, n in M.MOB:
        if q.x1 > r.x0 and q.x0 < r.x1 and q.y1 > r.y0 and q.y0 < r.y1:
            out.append(sg.box(q.x0, q.y0, q.x1, q.y1))
    for t, q, fr, n, zc, fu in M.MOB_NAVE:
        if zc == z.cod:
            out.append(sg.box(q.x0, q.y0, q.x1, q.y1))
    pts = [(e[1], e[2]) for e in SEG.matafuegos()] + [(x, y) for x, y, t in M.BOTIQUINES + M.BEBEDEROS] + \
        [(x, y) for t, s_, x, y in SEG.senales()]
    for x, y in pts:                     # matafuegos, botiquines, bebederos y señales (lámina de seguridad)
        if r.x0 - 0.5 < x < r.x1 + 0.5 and r.y0 - 0.5 < y < r.y1 + 0.5:
            out.append(sg.box(x - 0.45, y - 0.6, x + 0.45, y + 0.45))
    for x, y, w, muro, abre in M.PUERTAS_ADMIN + M.PUERTAS_LOCALES:      # barrido de las puertas
        if w > 2.0:
            continue
        if muro == "h":
            b = sg.box(x, y, x + w, y + abre * w) if abre > 0 else sg.box(x, y - w, x + w, y)
        else:
            b = sg.box(x, y, x + abre * w, y + w) if abre > 0 else sg.box(x - w, y, x, y + w)
        if b.intersects(sg.box(r.x0, r.y0, r.x1, r.y1)):
            out.append(b)
    return unary_union(out) if out else None


def rotulo(pl, z, h=1.8, areas=True, nombres=True):
    """Código y nombre de la zona en la esquina libre de equipos; en las franjas angostas, a lo largo (girado 90°)."""
    r = z.rect
    vert = r.h > 1.6 * r.w and r.w < 4.0
    largo, ancho = (r.h, r.w) if vert else (r.w, r.h)
    hh = min(h, max(0.7, ancho * pl.s * 0.3))
    n_car = max(6, int((largo - 0.3) * pl.s / (hh * 0.8 * 0.62)))
    if not vert:
        n_car = min(n_car, max(14, int(min(largo, 9.0) * pl.s / (hh * 0.8 * 0.62))))
    lineas = [z.cod] + (_cortar(_corto(z.nombre, 90), n_car) if nombres else [])
    max_l = max(1, int((ancho - 0.2) * pl.s / (hh * 1.45)))
    if len(lineas) > max_l:
        lineas = lineas[:max_l]
        if max_l == 1 and nombres:
            # una sola línea con el código y el nombre: se escribe con la altura del código (hh, no 0,8 hh)
            lineas = [(z.cod + " " + _corto(z.nombre, 60))[:int(n_car * 0.8)]]
    paso = hh * 1.45 / pl.s
    if vert:
        occ = _ocupado(z)
        abajo, arriba = r.h, r.h
        if occ is not None and not occ.is_empty:
            b = occ.intersection(sg.box(r.x0, r.y0, r.x1, r.y1)).bounds
            if b:
                abajo, arriba = max(0.0, b[1] - r.y0), max(0.0, r.y1 - b[3])
        arr = arriba > abajo and abajo < 2.0
        libre = max(abajo, arriba) if max(abajo, arriba) > 1.0 else r.h
        n_v = max(6, int((libre - 0.3) * pl.s / (hh * 0.8 * 0.63)))
        lineas = ([z.cod] + (_cortar(_corto(z.nombre, 90), n_v) if nombres else []))[:max_l]
        largo_t = max(len(ln) for ln in lineas) * hh * 0.63 / pl.s + 0.1
        ancho_t = len(lineas) * paso + 0.05
        caja = (sg.box(r.x0 + 0.1, r.y1 - 0.15 - largo_t, r.x0 + 0.15 + ancho_t, r.y1 - 0.1) if arr else
                sg.box(r.x0 + 0.1, r.y0 + 0.1, r.x0 + 0.15 + ancho_t, r.y0 + 0.15 + largo_t))
        if occ is not None and caja.intersection(occ).area > 1e-6:     # fondo blanco: el nombre no queda tapado
            q = list(caja.exterior.coords)[:-1]
            pl.relleno(q, (255, 255, 255), "A-SECTOR-TXT")
            pl.pl(q, "A-SECTOR-TXT", True)
        for i, ln in enumerate(lineas):
            if arr:
                pl.texto(ln, (r.x0 + 0.15 + i * paso, r.y1 - 0.15), hh if i == 0 else hh * 0.8, A.TOP_RIGHT,
                         "A-SECTOR-TXT", 90)
            else:
                pl.texto(ln, (r.x0 + 0.15 + i * paso, r.y0 + 0.15), hh if i == 0 else hh * 0.8, A.TOP_LEFT,
                         "A-SECTOR-TXT", 90)
        return
    occ = _ocupado(z)

    def medida(lns):
        an = max(len(ln) * (hh if i == 0 and len(lns) > 1 else hh * (1.0 if len(lns) == 1 else 0.8))
                 for i, ln in enumerate(lns)) * 0.63 / pl.s + 0.1
        return an, len(lns) * paso + 0.1

    def tapa(x0, y1, lns):
        an, al_ = medida(lns)
        return sg.box(x0, y1 - al_, x0 + an, y1).intersection(occ).area if occ is not None else 0.0

    def lugares(lns):
        """Esquinas, centro de los lados largos y después una grilla de 0,25 m dentro de la zona."""
        an, al_ = medida(lns)
        xs = [r.x0 + 0.1, r.x1 - 0.1 - an, r.c[0] - an / 2]
        ys = [r.y1 - 0.1, r.y0 + 0.1 + al_]
        for y1 in ys:
            for x0 in xs:
                yield x0, y1
        k = 0.25
        y1 = r.y1 - 0.1
        while y1 - al_ >= r.y0 + 0.05:
            x0 = r.x0 + 0.1
            while x0 + an <= r.x1 - 0.05:
                yield x0, y1
                x0 += k
            y1 -= k

    mejor = None
    for lns in (lineas, [z.cod]):
        for x0, y1 in lugares(lns):
            a = tapa(x0, y1, lns)
            if mejor is None or a < mejor[0] - 1e-6:
                mejor = (a, x0, y1, lns)
            if a <= 1e-6:
                break
        if mejor[0] <= 1e-6:
            break
    a, x0, y1, lineas = mejor
    an, al_ = medida(lineas)
    if a > 1e-6:          # no hay lugar libre: fondo blanco para que el nombre no quede tapado
        caja = [(x0 - 0.05, y1 - al_), (x0 + an, y1 - al_), (x0 + an, y1 + 0.05), (x0 - 0.05, y1 + 0.05)]
        pl.relleno(caja, (255, 255, 255), "A-SECTOR-TXT")
        pl.pl(caja, "A-SECTOR-TXT", True)
    for i, ln in enumerate(lineas):
        pl.texto(ln, (x0 + 0.05, y1 - 0.05 - i * paso), hh if i == 0 else hh * 0.8, A.TOP_LEFT, "A-SECTOR-TXT")
    if areas and r.w > 2.0 and r.h > 2.0 and r.w * r.h >= 6.0:
        t = f"{f(r.w * r.h)} m²"
        aw, ah = len(t) * hh * 0.8 * 0.63 / pl.s + 0.1, hh * 0.8 / pl.s * 1.3
        for (xx, yy, al) in ((r.x1 - 0.15, r.y0 + 0.15, A.BOTTOM_RIGHT), (r.x1 - 0.15, r.y1 - 0.15, A.TOP_RIGHT),
                             (r.x0 + 0.15, r.y0 + 0.15, A.BOTTOM_LEFT)):
            bx = sg.box(xx - aw if al != A.BOTTOM_LEFT else xx, yy - ah if al == A.TOP_RIGHT else yy,
                        xx if al != A.BOTTOM_LEFT else xx + aw, yy if al == A.TOP_RIGHT else yy + ah)
            libre = (occ is None or bx.intersection(occ).area < 1e-6) and \
                not bx.intersects(sg.box(x0, y1 - al_, x0 + an, y1))
            if libre:
                pl.texto(t, (xx, yy), hh * 0.8, al, "A-SECTOR-TXT")
                break


def zonas(pl, rellenos=True, rotulos=True, h=1.8, cats=None, areas=True, lista=None, nombres=True):
    for z in (lista if lista is not None else M.ZONAS):
        if cats and z.cat not in cats:
            continue
        r = z.rect
        if rellenos:
            if z.tipo == "pasillo":
                pl.relleno(r.pts(), RGB_PAS.get(z.sub, (245, 245, 245)))
            elif z.cat == "LIB":
                pl.rayado(r.pts(), "A-RELLENO", 0.9, 45, (190, 190, 190))
            else:
                pl.relleno(r.pts(), RGB.get(z.cat, (250, 250, 250)))
        if z.tipo != "pasillo":
            pl.rect(r, "A-SECTOR")
        if rotulos and z.tipo != "pasillo":
            rotulo(pl, z, h, areas, nombres)


def pasillos(pl, rotulos=True, h=1.6):
    """Demarcación IRAM 10005: líneas amarillas a los lados de los carriles y sendas; cebra en las sendas."""
    for z in M.ZONAS:
        if z.tipo != "pasillo":
            continue
        r = z.rect
        if z.sub == "AE":
            if r.w >= r.h:
                pl.linea((r.x0, r.y0 + 0.08), (r.x1, r.y0 + 0.08), "A-PASILLO")
                pl.linea((r.x0, r.y1 - 0.08), (r.x1, r.y1 - 0.08), "A-PASILLO")
            else:
                pl.linea((r.x0 + 0.08, r.y0), (r.x0 + 0.08, r.y1), "A-PASILLO")
                pl.linea((r.x1 - 0.08, r.y0), (r.x1 - 0.08, r.y1), "A-PASILLO")
        elif z.sub == "SP":
            pl.rect(r, "A-SENDA")
        elif z.sub == "PO":                 # Dec. 351/79 art. 79: dos franjas a los lados del pasillo
            if r.w >= r.h:
                pl.linea((r.x0, r.y0 + 0.05), (r.x1, r.y0 + 0.05), "A-PASILLO")
                pl.linea((r.x0, r.y1 - 0.05), (r.x1, r.y1 - 0.05), "A-PASILLO")
            else:
                pl.linea((r.x0 + 0.05, r.y0), (r.x0 + 0.05, r.y1), "A-PASILLO")
                pl.linea((r.x1 - 0.05, r.y0), (r.x1 - 0.05, r.y1), "A-PASILLO")
        if rotulos and max(r.w, r.h) > 6:
            ang = 0 if r.w >= r.h else 90
            txt = f"{z.cod}  {_corto(z.nombre, 60 if max(r.w, r.h) > 9 else 40)}  {f(min(r.w, r.h), 1)} m"
            pl.texto(txt, r.c, h, A.MIDDLE_CENTER, "A-TEXTO", ang)
    # baranda entre el carril del autoelevador y la senda del pasillo principal, con cruces
    cruces = M.CRUCES_A2
    x = 0.4
    for a, b in cruces:
        if a > x:
            pl.linea((x, M.Y_AE), (a, M.Y_AE), "A-DEFENSA")
        x = b
    pl.linea((x, M.Y_AE), (M.LX - 0.4, M.Y_AE), "A-DEFENSA")
    for a, b in cruces:
        for k in range(int((b - a) / 0.4)):
            xx = a + 0.2 + k * 0.4
            pl.linea((xx, M.Y_S + 0.2), (xx, M.Y_AE - 0.2), "A-SENDA")
    # baranda de la senda norte (croquis de oficinas) con cruces pintados frente a cada puerta a la planta
    x = M.X_AL
    for a, b in sorted(M.ABERTURAS_N):
        if a > x:
            pl.linea((x, M.Y_M), (a, M.Y_M), "A-DEFENSA")
        x = b
    pl.linea((x, M.Y_M), (M.X_PINT, M.Y_M), "A-DEFENSA")
    for a, b in M.CRUCES_N:
        for k in range(int((b - a) / 0.4)):
            xx = a + 0.2 + k * 0.4
            pl.linea((xx, M.Y_M + 0.15), (xx, M.LY - 0.15), "A-SENDA")


def _sin_huecos(g):
    """Parte un polígono con agujeros en polígonos sin agujeros (el sombreado del PDF no respeta 2 o más huecos)."""
    from shapely.ops import split
    if not g.interiors:
        return [g]
    cx = g.interiors[0].centroid.x
    out = []
    for q in split(g, sg.LineString([(cx, g.bounds[1] - 1), (cx, g.bounds[3] + 1)])).geoms:
        out += _sin_huecos(q)
    return out


def _macizo(pl, geo, capa, rgb):
    for g in (geo.geoms if hasattr(geo, "geoms") else [geo]):
        for q in _sin_huecos(g):
            pts = list(q.exterior.coords)[:-1]
            hh = pl.m.add_hatch(dxfattribs={"layer": capa})
            hh.set_solid_fill(rgb=rgb)
            hh.paths.add_polyline_path(pl.Ps(pts), is_closed=True)
        pl.pl(list(g.exterior.coords)[:-1], capa, True)
        for it in g.interiors:
            pl.pl(list(it.coords)[:-1], capa, True)


def muros(pl):
    e = M.MURO
    X, Y = M.LX, M.LY
    anillo = sg.box(-e, -e, X + e, Y + e).difference(sg.box(0, 0, X, Y))
    an = sg.box(M.XA0 - e, M.YA0 - 0.01, M.XA1 + e, M.YA1 + e).difference(sg.box(M.XA0, M.YA0, M.XA1, M.YA1))
    anillo = anillo.union(an)
    vanos = []
    for p in M.PUERTAS:
        vanos.append({"N": sg.box(p.a, Y - 1, p.b, Y + 1), "S": sg.box(p.a, -1, p.b, 1),
                      "O": sg.box(-1, p.a, 1, p.b), "E": sg.box(X - 1, p.a, X + 1, p.b)}[p.muro])
    for cod, muro, a, b, uso in M.PUERTAS_EXT_ADMIN:
        vanos.append({"N": sg.box(a, M.YA1 - 1, b, M.YA1 + 1), "E": sg.box(M.XA1 - 1, a, M.XA1 + 1, b),
                      "O": sg.box(M.XA0 - 1, a, M.XA0 + 1, b)}[muro])
    for (xa, ya), (xb, yb) in M.VENTANAS_ADMIN:
        vanos.append(sg.box(xa, ya - 0.3, xb, yb + 0.3))
    anillo = anillo.difference(unary_union(vanos))
    _macizo(pl, anillo, "A-MURO", (70, 70, 70))
    for (xa, ya), (xb, yb) in M.VENTANAS_ADMIN:
        for d in (-0.07, 0.0, 0.07):
            pl.linea((xa, ya + d + 0.1), (xb, yb + d + 0.1), "A-VENTANA")
    # columnas de pórtico y de testero
    c = M.COL / 2
    for x in M.EJES_X:
        for y in M.EJES_Y:
            pl.relleno([(x - c, y - c), (x + c, y - c), (x + c, y + c), (x - c, y + c)], (0, 0, 0), "A-COLUMNA")
    for x in (-0.1, X + 0.1):
        for y in (6.6, 25.6, 32.7, 39.9):
            pl.relleno([(x - 0.15, y - 0.15), (x + 0.15, y - 0.15), (x + 0.15, y + 0.15), (x - 0.15, y + 0.15)],
                       (0, 0, 0), "A-COLUMNA")


def tabiques(pl, lista, e=0.10):
    """Tabiques de locales cerrados (y del anexo) con los vanos de sus puertas."""
    geo = []
    for z in lista:
        r = z.rect
        geo.append(sg.box(r.x0 - e / 2, r.y0 - e / 2, r.x1 + e / 2, r.y1 + e / 2).difference(
            sg.box(r.x0 + e / 2, r.y0 + e / 2, r.x1 - e / 2, r.y1 - e / 2)))
    t = unary_union(geo)
    vanos = []
    for x, y, w, muro, abre in M.PUERTAS_ADMIN + M.PUERTAS_LOCALES:
        vanos.append(sg.box(x, y - 0.2, x + w, y + 0.2) if muro == "h" else sg.box(x - 0.2, y, x + 0.2, y + w))
    for x, y, w, muro in M.CORREDIZAS_ADMIN + M.ABIERTOS_ADMIN:
        vanos.append(sg.box(x + 0.06, y - 0.2, x + w - 0.06, y + 0.2) if muro == "h" else
                     sg.box(x - 0.2, y + 0.06, x + 0.2, y + w - 0.06))
    t = t.difference(unary_union(vanos)) if vanos else t
    _macizo(pl, t, "A-TABIQUE", (110, 110, 110))


def locales_nave(pl):
    """Locales cerrados dentro de la nave (tabique de 0,10 m) con una puerta hacia su pasillo."""
    for z in M.ZONAS:
        if z.tipo != "local":
            continue
        r = z.rect
        pl.rect(_r(sg.box(r.x0, r.y0, r.x1, r.y1) and r), "A-TABIQUE")
        pl.rect(M.R(r.x0 + 0.1, r.y0 + 0.1, r.x1 - 0.1, r.y1 - 0.1), "A-TABIQUE")


def porton(pl, p, h=1.6, etiquetas=True):
    """Portón seccional de la nave: jambas, umbral, hoja abierta proyectada (punteada) y rótulo con ancho y uso."""
    X, Y = M.LX, M.LY
    w = p.b - p.a
    # (punto del umbral, dirección hacia afuera, dirección a lo largo del vano)
    if p.muro in "NS":
        y = Y if p.muro == "N" else 0.0
        s = 1 if p.muro == "N" else -1
        P = lambda t, d: (p.a + t, y + s * d)          # t a lo largo del vano, d hacia afuera (negativo: adentro)
    else:
        x = X if p.muro == "E" else 0.0
        s = 1 if p.muro == "E" else -1
        P = lambda t, d: (x + s * d, p.a + t)
    e = M.MURO
    for t in (0.0, w):
        k = -1 if t == 0.0 else 1
        pl.relleno([P(t, -e), P(t + k * 0.25, -e), P(t + k * 0.25, e), P(t, e)], (60, 60, 60), "A-ABERTURA")
    pl.linea(P(0, 0), P(w, 0), "A-ABERTURA")
    pl.linea(P(0, -e), P(w, -e), "A-ABERTURA")
    for d in (-0.15, -0.75):                                   # hoja seccional arriba (proyección a trazos)
        t = 0.0
        while t < w:
            pl.linea(P(t, d), P(min(t + 0.35, w), d), "A-ABERTURA")
            t += 0.6
    pl.linea(P(0, -0.15), P(0, -0.75), "A-ABERTURA")
    pl.linea(P(w, -0.15), P(w, -0.75), "A-ABERTURA")
    if etiquetas:
        lineas = [f"{p.cod} · portón {f(w, 1)} × {f(p.alto, 1)} m", M.PORTON_CORTO.get(p.cod, "")]
        paso = h * 1.5 / pl.s
        for i, ln in enumerate(lineas):
            d = 16.0 / pl.s + paso * (i + 0.5)
            pl.texto(ln, P(w / 2, d), h * (1.0 if i == 0 else 0.85), A.MIDDLE_CENTER, "A-TEXTO",
                     0 if p.muro in "NS" else 90)


def puertas(pl, h=1.6, etiquetas=True):
    X, Y = M.LX, M.LY
    for p in M.PUERTAS:
        if p.tipo == "porton":
            porton(pl, p, h, etiquetas)
            continue
        # las puertas peatonales, de emergencia y de servicio abren hacia afuera (sentido de la evacuación)
        if p.muro in "NS":
            y = Y if p.muro == "N" else 0.0
            s = 1 if p.muro == "N" else -1
            a = (p.a, y)
            w = p.b - p.a
            if p.cod.startswith("PN"):          # puertas del anexo a la planta: como en el plano del usuario
                pl.linea(a, (p.a, y - s * w), "A-ABERTURA")
                pl.arco(a, w, -90 if s > 0 else 0, 0 if s > 0 else 90, "A-ABERTURA")
                if etiquetas:
                    pl.texto(p.cod, ((p.a + p.b) / 2, y + s * 1.4), h, A.MIDDLE_CENTER, "A-TEXTO")
                continue
            pl.linea(a, (p.a, y + s * w), "A-ABERTURA")
            pl.arco(a, w, 0 if s > 0 else 270, 90 if s > 0 else 360, "A-ABERTURA")
            if etiquetas:
                pl.texto(p.cod, ((p.a + p.b) / 2, y + s * (w + 0.9)), h, A.MIDDLE_CENTER, "A-TEXTO")
        else:
            x = X if p.muro == "E" else 0.0
            s = 1 if p.muro == "E" else -1
            w = p.b - p.a
            pl.linea((x, p.a), (x + s * w, p.a), "A-ABERTURA")
            pl.arco((x, p.a), w, 0 if s > 0 else 90, 90 if s > 0 else 180, "A-ABERTURA")
            if etiquetas:
                pl.texto(p.cod, (x + s * (w + 1.0), (p.a + p.b) / 2), h, A.MIDDLE_CENTER, "A-TEXTO", 90)
    for x, y, w, muro, abre in M.PUERTAS_ADMIN + M.PUERTAS_LOCALES:
        if w > 2.0:
            if muro == "h":
                pl.linea((x, y - 0.05 * abre), (x + w, y - 0.05 * abre), "A-ABERTURA")
            else:
                pl.linea((x - 0.05 * abre, y), (x - 0.05 * abre, y + w), "A-ABERTURA")
        else:
            MO.puerta_int(pl, x, y, w, muro, abre)
    for x, y, w, muro in M.CORREDIZAS_ADMIN:              # hoja corrediza dentro del muro (plano del usuario)
        pl.rect(M.R(x, y - 0.04, x + w, y + 0.04), "A-ABERTURA")
        pl.linea((x + w, y), (x + 1.9 * w, y), "A-EQUIPO-OCULTO")
    for cod, muro, a, b, uso in M.PUERTAS_EXT_ADMIN:      # abren hacia afuera (croquis)
        w = b - a
        if muro == "N" and w > 1.4:                          # doble hoja
            pl.linea((a, M.YA1), (a, M.YA1 + w / 2), "A-ABERTURA")
            pl.linea((b, M.YA1), (b, M.YA1 + w / 2), "A-ABERTURA")
            pl.arco((a, M.YA1), w / 2, 0, 90, "A-ABERTURA")
            pl.arco((b, M.YA1), w / 2, 90, 180, "A-ABERTURA")
        elif muro == "N":
            pl.linea((b, M.YA1), (b, M.YA1 + w), "A-ABERTURA")
            pl.arco((b, M.YA1), w, 90, 180, "A-ABERTURA")
        elif muro == "E":
            pl.linea((M.XA1, b), (M.XA1 + w, b), "A-ABERTURA")
            pl.arco((M.XA1, b), w, 270, 360, "A-ABERTURA")
        else:
            pl.linea((M.XA0, b), (M.XA0 - w, b), "A-ABERTURA")
            pl.arco((M.XA0, b), w, 180, 270, "A-ABERTURA")
        if etiquetas:
            pos = {"N": ((a + b) / 2, M.YA1 + 1.2), "E": (M.XA1 + 1.2, (a + b) / 2), "O": (M.XA0 - 1.2, (a + b) / 2)}
            pl.texto(cod, pos[muro], h, A.MIDDLE_CENTER, "A-TEXTO")


def _pallets(pl, e, pt=False):
    r = e.rect
    m = S.M.rect(pl, _r(r), e.frente)
    U, V = m.Lu, m.Lv
    if pt:
        n = max(1, int(V / 1.25))
        for j in range(n):
            v0, v1 = j * V / n + 0.04, (j + 1) * V / n - 0.04
            m.caja(0.03, v0, U - 0.03, v1, (238, 222, 192), S.FINO)
            m.ln((0.03, v0), (U - 0.03, v1), S.FINO)
    else:
        n = max(1, int(U / 1.05))
        for i in range(n):
            u0, u1 = i * U / n + 0.04, (i + 1) * U / n - 0.04
            m.caja(u0, 0.05, u1, V - 0.05, (238, 222, 192), S.FINO)
            for k in (0.25, 0.5, 0.75):
                m.ln((u0 + (u1 - u0) * k, 0.05), (u0 + (u1 - u0) * k, V - 0.05), S.FINO)
    m.rc(0, 0, U, V, S.CONT)
    m.fin()


def pintura(pl, h=1.6):
    """Línea Firesafer vertical (W-MAN 19): el cuelgue arriba, a la altura del granallado y la detección; el
    transportador pasa por el horno de precalentamiento, la cabina, el horno de curado y el enfriamiento hacia el sur y
    vuelve a la descarga en la punta sur, frente a la terminación (cruzando el pasillo principal)."""
    e = next(q for q in M.EQUIPOS if q.cod == "M19-1")
    r = e.rect
    pl.relleno(r.pts(), (255, 248, 240), "A-EQUIPO-RELLENO")
    pl.rect(r, "A-EQUIPO")
    partes = [("Horno de precalentamiento", 42.0, 44.6, (250, 228, 210)),
              ("Cabina de polvo y recuperación", 36.6, 41.6, (232, 238, 222)),
              ("Horno de curado a gas, 180-220 °C", 26.8, 36.2, (250, 215, 200)),
              ("Enfriamiento", 22.4, 26.4, (220, 235, 250))]
    for nom, y0, y1, rgb in partes:
        q = M.R(r.x0 + 1.6, y0, r.x1 - 1.6, y1)
        pl.relleno(q.pts(), rgb, "A-EQUIPO-RELLENO")
        pl.rect(q, "A-EQUIPO-FINO")
        pl.texto(nom, q.c, h * (0.8 if y1 - y0 < 3 else 1.0), A.MIDDLE_CENTER, "A-TEXTO", 90)
    xc = r.x0 - 2.0                      # punta del ramal del cuelgue (sobre el puesto M19-C)
    xd = r.x0 - 1.8                      # punta del ramal de la descarga (sobre el puesto M19-D)
    xi = 53.7                            # punta del ramal de la detección (W-MAN: «si está bien, colgarlo en el
    #                                      transportador»; cruza el pasillo PO-N2 por arriba)
    lazo = [(r.x0 + 0.8, 41.0), (xc, 41.0), (xc, 42.0), (r.x0 + 0.8, 42.0), (r.x0 + 0.8, 43.6), (xi, 43.6), (xi, 44.4),
            (r.x0 + 0.8, 44.4), (r.x0 + 0.8, 45.4), (r.x1 - 0.8, 45.4),
            (r.x1 - 0.8, 21.6), (r.x0 + 0.8, 21.6), (r.x0 + 0.8, 22.0), (xd, 22.0), (xd, 23.0), (r.x0 + 0.8, 23.0),
            (r.x0 + 0.8, 41.0)]
    pl.pl(lazo, "A-EQUIPO-OCULTO")
    for xy in ((xc, 41.5), (xd, 22.5), (xi, 44.0)):
        pl.circulo(xy, 0.35, "A-EQUIPO")
    pl.texto("Ramal aéreo del transportador hasta la detección (sobre el pasillo PO-N2)", (60.5, 44.6), h * 0.7,
             A.BOTTOM_CENTER, "A-TEXTO")
    pl.texto("Cuelgue", (xc, 42.3), h * 0.8, A.BOTTOM_CENTER, "A-TEXTO")
    pl.texto("Descarga", (xd - 0.5, 23.9), h * 0.8, A.BOTTOM_CENTER, "A-TEXTO")
    pl.texto("Transportador aéreo en lazo (ganchos)", (r.c[0], 45.0), h * 0.8, A.MIDDLE_CENTER, "A-TEXTO")


def equipos(pl, rotulos=True, h=1.1, operarios=True, win=None):
    for e in M.EQUIPOS:
        r = e.rect
        if win and (r.x1 < win[0] or r.x0 > win[2] or r.y1 < win[1] or r.y0 > win[3]):
            continue
        if e.cod == "M19-1":
            pintura(pl)
            continue
        if e.tipo in ("pallets_q", "pallets_pt"):
            _pallets(pl, e, e.tipo == "pallets_pt")
        elif e.tipo in ("rodantes", "filas"):
            m = S.M.rect(pl, _r(r), e.frente)
            fn = S10.filas if e.tipo == "filas" else S10.rodantes
            fn(m, e.grid[0], e.grid[1], S10.DEM.get(e.dem, "A-DEM-AM"), e.n)
            m.fin()
            if rotulos and e.cod in ROTULO_BLOQUE:
                pl.texto(_corto(e.nombre, 60), (r.x0, r.y1 + 0.06), h * 0.9, A.BOTTOM_LEFT, "A-TEXTO")
            continue
        else:
            S.dibujar(pl, SimpleNamespace(rect=_r(r), nombre=e.nombre, tipo=e.tipo, frente=e.frente, op=e.op,
                                          espejo=e.espejo), operarios)
        if rotulos and (r.w >= 0.9 or r.h >= 0.9) and not e.cod.startswith(("R1-", "R2-", "PTM-", "FL-", "HO-")):
            pl.texto(e.cod, (r.c[0], r.c[1]), h, A.MIDDLE_CENTER, "A-TEXTO", 90 if r.h > 2.2 * r.w else 0)


def _tinte(rgb, k=0.55):
    return tuple(int(c + (255 - c) * k) for c in rgb)


# sección del almacén de cada equipo de una sola sección (las columnas de R1 se pintan una por una)
SECCION_EQ = {"RC-1": "CAS", "RC-2": "ICA", "PTM-1": "PT", "HO-1": "CHF", "CC-1": "CCH", "CC-2": "CCH", "CC-3": "CCH",
              "CA-1": "CAN", "ES-1": "IDE", "CU-2": "GAS", "PV-1": "EMB", "PV-2": "EMB", "PQ-5": "POL",
              **{f"PQ-{i}": "POL" for i in range(1, 5)}, **{f"FL-{i}": "CHF" for i in range(1, 8)}}


def secciones(pl, h=1.0):
    """Secciones del almacén (X-ALM v5, leyenda «Sección» del croquis): columnas de pallets de R1 pintadas con el
    color de su sección y una marca de color en cada elemento de una sola sección."""
    paso = 2.67
    for i in range(10):
        for j in range(2):
            col = M.COLUMNAS_R1[2 * i + j]
            y0 = 20.1 + i * paso + j * paso / 2
            partes = [(col, 1.0)] if "/" not in col else [(col.split("/")[0], 0.25), (col.split("/")[1], 0.75)]
            yy = y0 + 0.12
            alto = paso / 2 - 0.24
            for sec, fr in partes:
                q = M.R(0.24, yy, 1.06, yy + alto * fr)
                pl.relleno(q.pts(), _tinte(M.SECCIONES_ALM[sec][3], 0.35), "A-RELLENO")
                pl.rect(q, "A-EQUIPO-FINO")
                if fr > 0.5:
                    pl.texto(sec, q.c, h, A.MIDDLE_CENTER, "A-TEXTO", 90)
                yy += alto * fr
    eqs = {e.cod: e for e in M.EQUIPOS}
    for cod, sec in SECCION_EQ.items():
        e = eqs.get(cod)
        if e is None:
            continue
        r = e.rect
        s = min(0.45, r.w * 0.6, r.h * 0.6)
        q = M.R(r.x1 - s - 0.03, r.y1 - s - 0.03, r.x1 - 0.03, r.y1 - 0.03)
        pl.relleno(q.pts(), _tinte(M.SECCIONES_ALM[sec][3], 0.2), "A-RELLENO")
        pl.rect(q, "A-EQUIPO-FINO")
        pl.texto(sec, q.c, h * 0.55, A.MIDDLE_CENTER, "A-TEXTO")


def demarcaciones(pl, h=1.0):
    """Calle de chapa de carros, rejilla de goteo y zonas delimitadas de seguridad (W-CAR 1, W-MAN 23 y 25)."""
    q = M.R(8.4, 24.5, 10.4, 34.5)
    pl.rect(q, "A-EQUIPO-OCULTO")
    pl.texto("Calle de chapa 10 × 2 m (blanco, posiciones numeradas)", (8.5, 29.6), h * 0.75, A.MIDDLE_CENTER,
             "A-TEXTO", 90)
    for r in M.REJILLAS:
        pl.rect(r, "A-EQUIPO-FINO")
        k = 1
        while r.x0 + k * 0.15 < r.x1:
            pl.linea((r.x0 + k * 0.15, r.y0), (r.x0 + k * 0.15, r.y1), "A-EQUIPO-FINO")
            k += 1
    for r in M.DELIMITADAS:
        pl.rect(r, "A-SEGURIDAD")


def muebles(pl):
    for t, r, fr, n in M.MOB:
        MO.dibujar(pl, SimpleNamespace(tipo=t, rect=_r(r), frente=fr, n=n))
    for t, r, fr, n, zc, fu in M.MOB_NAVE:
        MO.dibujar(pl, SimpleNamespace(tipo=t, rect=_r(r), frente=fr, n=n))


def ejes(pl, r_glob=3.0, sobresale=4.0):
    X, Y = M.LX, M.LY
    rg = r_glob / pl.s
    for i, x in enumerate(M.EJES_X):
        pl.linea((x, -sobresale), (x, Y + 0.6), "A-EJE")
        pl.circulo((x, -sobresale - rg), rg, "A-EJE")
        pl.texto(str(i + 1), (x, -sobresale - rg), r_glob * 0.9, A.MIDDLE_CENTER, "A-TEXTO")
    for j, y in enumerate(M.EJES_Y):
        pl.linea((-sobresale, y), (X + sobresale, y), "A-EJE")
        for xx in (-sobresale - rg, X + sobresale + rg):
            pl.circulo((xx, y), rg, "A-EJE")
            pl.texto("ABC"[j], (xx, y), r_glob * 0.9, A.MIDDLE_CENTER, "A-TEXTO")


def cotas(pl, d=10.0):
    pl.cadena(M.EJES_X, 0.0, -d * 1.0, True)
    pl.cota((0, 0), (M.LX, 0), -d * 1.6, True)
    pl.cadena(M.EJES_Y, 0.0, -d * 1.0, False)
    pl.cota((0, 0), (0, M.LY), -d * 1.6, False)


CHICOS = ("CJ", "RA1", "PLA", "RA2", "DE2", "RA3", "DE3")      # elementos del exterior que se rotulan aparte


def rampas(pl, h=1.6, nota=True):
    """Rampas accesibles (flecha como en el croquis), descansos, plataforma a nivel y cajón accesible."""
    ext = {c: r for c, n, r in M.EXTERIOR}
    for cod in CHICOS:
        r = ext[cod]
        pl.relleno(r.pts(), (240, 240, 240) if cod.startswith(("RA", "CJ")) else (250, 250, 250), "A-EXTERIOR")
        pl.rect(r, "A-EXTERIOR")
        if cod.startswith("RA"):
            d = M.RAMPAS[cod]
            if d in "NS":
                for k in range(1, int(r.h / 0.3)):
                    pl.linea((r.x0, r.y0 + k * 0.3), (r.x1, r.y0 + k * 0.3), "A-EQUIPO-FINO")
                a, b = (r.c[0], r.y0 + 0.4), (r.c[0], r.y1 - 0.4)
            else:
                for k in range(1, int(r.w / 0.3)):
                    pl.linea((r.x0 + k * 0.3, r.y0), (r.x0 + k * 0.3, r.y1), "A-EQUIPO-FINO")
                a, b = (r.x1 - 0.4, r.c[1]), (r.x0 + 0.4, r.c[1])
            pl.linea(a, b, "A-TEXTO")
            pl.punta(b, (b[0] - a[0], b[1] - a[1]), 2.4, 1.2)
            pl.texto("Rampa accesible", (r.c[0], r.c[1]), h * 0.8, A.MIDDLE_CENTER, "A-TEXTO", 90 if d in "NS" else 0)
        elif cod == "CJ":
            pl.rect(M.R(r.x0 + 0.1, r.y0 + 0.1, r.x1 - 0.1, r.y1 - 0.1), "A-DEM-AM")
            pl.texto("Cajón accesible", (r.c[0], r.c[1] + 0.4), h * 0.8, A.MIDDLE_CENTER, "A-TEXTO")
            pl.texto("3,50 × 5,00 m", (r.c[0], r.c[1] - 0.6), h * 0.8, A.MIDDLE_CENTER, "A-TEXTO")
        else:
            pl.texto("Plataforma a nivel" if cod == "PLA" else "Descanso", r.c, h * 0.8, A.MIDDLE_CENTER, "A-TEXTO",
                     90 if r.h > r.w else 0)
    if nota:
        r = ext["RA1"]
        pl.texto(M.NOTA_RAMPA, (r.x0, r.y1 + 0.35), h * 0.7, A.BOTTOM_LEFT, "A-TEXTO")


def predio(pl, h=1.6):
    """Cerco perimetral con sus portones de entrada, sendas peatonales exteriores y franja de descarga."""
    P = M.PREDIO
    gaps = sorted((a, b) for c, a, b, u in M.PORTONES_PREDIO)
    x = P.x0
    for a, b in gaps:
        pl.linea((x, P.y1), (a, P.y1), "A-EXTERIOR")
        x = b
    pl.linea((x, P.y1), (P.x1, P.y1), "A-EXTERIOR")
    pl.pl([(P.x1, P.y1), (P.x1, P.y0), (P.x0, P.y0), (P.x0, P.y1)], "A-EXTERIOR")
    tramos = [((P.x1, P.y1), (P.x1, P.y0)), ((P.x1, P.y0), (P.x0, P.y0)), ((P.x0, P.y0), (P.x0, P.y1))]
    xx = P.x0
    for a, b in gaps + [(P.x1, P.x1)]:
        tramos.append(((xx, P.y1), (a, P.y1)))
        xx = b
    for (xa, ya), (xb, yb) in tramos:                     # cruces del alambrado cada 4 m
        L = math.hypot(xb - xa, yb - ya)
        for k in range(1, int(L / 4.0)):
            cx, cy = xa + (xb - xa) * k * 4.0 / L, ya + (yb - ya) * k * 4.0 / L
            pl.linea((cx - 0.3, cy - 0.3), (cx + 0.3, cy + 0.3), "A-EXTERIOR")
            pl.linea((cx - 0.3, cy + 0.3), (cx + 0.3, cy - 0.3), "A-EXTERIOR")
    for cod, a, b, uso in M.PORTONES_PREDIO:
        w = b - a
        for xp in (a, b):
            pl.relleno([(xp - 0.2, P.y1 - 0.2), (xp + 0.2, P.y1 - 0.2), (xp + 0.2, P.y1 + 0.2), (xp - 0.2, P.y1 + 0.2)],
                       (60, 60, 60), "A-EXTERIOR")
        if w > 2.0:                                       # portón corredizo: hoja punteada al costado
            pl.linea((a, P.y1 - 0.35), (b, P.y1 - 0.35), "A-EQUIPO-OCULTO")
        else:
            pl.linea((a, P.y1), (a, P.y1 - w), "A-ABERTURA")
            pl.arco((a, P.y1), w, 270, 360, "A-ABERTURA")
        pl.texto(cod, ((a + b) / 2, P.y1 + 1.0), h, A.BOTTOM_CENTER, "A-TEXTO")
    for r in M.SENDAS_EXT:
        pl.rect(r, "A-SENDA")
        for k in range(1, int(r.h / 0.6)):
            pl.linea((r.x0 + 0.15, r.y0 + k * 0.6), (r.x1 - 0.15, r.y0 + k * 0.6), "A-SENDA")
    r = M.FRANJA_DESCARGA
    pl.rect(r, "A-ZONA-LOG")
    pl.texto("Franja de descarga 15 × 5 m (W-CAR 1)", (r.c[0], r.c[1]), h, A.MIDDLE_CENTER, "A-TEXTO", 90)


def despacho_carros(pl, h=1.4):
    """Rampa portátil y furgón del despacho de carros por P2, y volquete de la playa de scrap (plano de carros rev 6)."""
    d = M.DESPACHO_CARROS
    r = d["rampa"]
    pl.relleno(r.pts(), (230, 230, 230), "A-EXTERIOR")
    pl.rect(r, "A-EQUIPO")
    y = r.y0 + 0.3
    while y < r.y1:
        pl.linea((r.x0, y), (r.x1, y), "A-EQUIPO-FINO")
        y += 0.3
    f_ = d["furgon"]
    pl.relleno(f_.pts(), (250, 250, 250), "A-EXTERIOR")
    pl.rect(f_, "A-EQUIPO")
    pl.linea((f_.x0, f_.y0 + 1.7), (f_.x1, f_.y0 + 1.7), "A-EQUIPO")          # cabina hacia el sur, caja hacia P2
    pl.linea((f_.x0 + 0.2, f_.y0 + 0.9), (f_.x1 - 0.2, f_.y0 + 0.9), "A-EQUIPO-FINO")
    yc = (f_.y0 + f_.y1) / 2
    pl.texto("Rampa TRAN-IN-240 (2,4 m útiles, 23 % ≈ 13°, 350 kg, sin obra civil)", (f_.x0 - 0.5, yc + 0.6), h,
             A.MIDDLE_RIGHT, "A-TEXTO")
    pl.texto("Furgón Renault Master L3H2 de culo: ≈ 13 carros por viaje, 6 viajes por semana",
             (f_.x0 - 0.5, yc - 0.6), h, A.MIDDLE_RIGHT, "A-TEXTO")
    v = d["volquete"]
    pl.rect(v, "A-EQUIPO")
    pl.linea((v.x0, v.y0), (v.x1, v.y1), "A-EQUIPO-FINO")
    pl.linea((v.x0, v.y1), (v.x1, v.y0), "A-EQUIPO-FINO")
    pl.texto("Volquete 5 m³ del chatarrero (2 × 3 m)", (v.c[0], v.y1 + 0.4), h, A.BOTTOM_CENTER, "A-TEXTO")


def exterior(pl, h=1.8):
    for cod, nom, r in M.EXTERIOR:
        if cod in CHICOS:
            continue
        if cod == "CALLE":
            pl.relleno(r.pts(), (215, 215, 215), "A-EXTERIOR")
        pl.rect(r, "A-EXTERIOR")
        pl.texto(_corto(nom, 70), (r.x0 + 0.4, r.y1 - 0.4), h, A.TOP_LEFT, "A-TEXTO")
    rampas(pl, h * 0.8, nota=False)
    despacho_carros(pl, h * 0.8)
    predio(pl, h)
    pl.pl(M.CAMINO_CAMIONES, "A-ZONA-LOG")
    pl.texto("Circuito de camiones de una mano: entra por PC-1 y sale por PC-2", (M.CAMINO_CAMIONES[1][0] + 1, 40.0),
             h, A.MIDDLE_LEFT, "A-TEXTO", 90)


def base(pl, win=None, rot_eq=True, h_eq=1.1, h_z=1.8, pasos=True):
    zonas(pl, h=h_z, rotulos=False)
    tabiques(pl, [z for z in M.ZONAS if z.tipo == "local"], 0.10)
    tabiques(pl, M.ADMIN, 0.10)
    pasillos(pl, h=h_z * 0.85)
    demarcaciones(pl, h_eq)
    equipos(pl, rotulos=rot_eq, h=h_eq, win=win)
    secciones(pl, h_eq)
    muebles(pl)
    muros(pl)
    puertas(pl, h=h_z)
    for z in M.ZONAS:                     # rótulos al final: arriba de equipos y secciones
        if z.tipo != "pasillo":
            rotulo(pl, z, h_z)


# ================================================================ cursores de texto en papel
class Col:
    def __init__(self, pl, x, y):
        self.pl, self.x, self.y = pl, x, y

    def titulo(self, t, hh=3.5):
        self.y -= hh
        self.pl.texto(t, (self.x, self.y), hh, A.BOTTOM_LEFT, papel=True)
        self.y -= 2.5

    def parrafo(self, lineas, hh=2.2, ancho=None):
        for ln in lineas:
            for s in (_cortar(ln, int(ancho / (hh * 0.6))) if ancho else [ln]):
                self.pl.texto(s, (self.x, self.y), hh, A.TOP_LEFT, papel=True)
                self.y -= hh * 1.55
        self.y -= 2.0

    def tabla(self, cols, filas, hf=3.6, ht=1.9, titulo=None):
        self.y = self.pl.tabla(self.x, self.y, cols, filas, hf, ht, titulo, 3.0) - 6.0


def leyenda_cats(c, cats, w=7.0):
    for cat in cats:
        x, y = c.x, c.y
        if cat == "LIB":
            c.pl.m.add_lwpolyline([(x, y), (x + w, y), (x + w, y - 3.5), (x, y - 3.5)], close=True,
                                  dxfattribs={"layer": "A-SECTOR"})
            hh = c.pl.m.add_hatch(dxfattribs={"layer": "A-RELLENO"})
            hh.set_pattern_fill("ANSI31", scale=0.4)
            hh.paths.add_polyline_path([(x, y), (x + w, y), (x + w, y - 3.5), (x, y - 3.5)], is_closed=True)
        else:
            rgb = RGB.get(cat) or RGB_PAS.get(cat)
            hh = c.pl.m.add_hatch(dxfattribs={"layer": "A-RELLENO"})
            hh.set_solid_fill(rgb=rgb)
            hh.paths.add_polyline_path([(x, y), (x + w, y), (x + w, y - 3.5), (x, y - 3.5)], is_closed=True)
            c.pl.m.add_lwpolyline([(x, y), (x + w, y), (x + w, y - 3.5), (x, y - 3.5)], close=True,
                                  dxfattribs={"layer": "A-SECTOR"})
        nom = {"AE": "Carril del autoelevador (3,0 a 5,0 m)", "SP": "Senda peatonal demarcada",
               "PO": "Pasillo de operarios y carros a mano"}.get(cat, NOMBRE_CAT.get(cat, cat))
        c.pl.texto(nom, (x + w + 2.5, y - 1.75), 2.3, A.MIDDLE_LEFT, papel=True)
        c.y -= 5.2
    c.y -= 2.0


# ================================================================ resumen de superficies
def resumen():
    tot = {}
    for z in M.ZONAS:
        k = z.cat if z.tipo != "pasillo" else "CIRC"
        tot[k] = tot.get(k, 0.0) + z.rect.area
    adm = sum(z.rect.area for z in M.ADMIN)
    return tot, adm


# ================================================================ FL_PI10_01
def fl_01(doc, ox):
    h = hoja(doc, "A0", ox, "Planta general e implantación", "Layout 2035 v10 - zonas codificadas y áreas",
             "FL_PI10_01", 1, 7, "1:200", "Plano de planta")
    win = (-27.0, -22.5, 104.0, 77.0)
    pl = D.Plano(h, 200, (win[0], win[1]), (h.fx0 + 12, h.fy0 + 262))
    titulo_hoja(pl, h, "FL_PI10_01 - PLANTA GENERAL E IMPLANTACIÓN, ZONAS Y SUPERFICIES",
                "Calle al norte: administración y servicios al personal al norte de la nave (croquis del usuario). "
                "Cada m² de la nave tiene código y nombre (verificado).")
    exterior(pl, 1.6)
    pl.pl(M.CANERIA_GAS, "I-GAS")
    pl.texto("Gas natural a los hornos de pintura", (M.CANERIA_GAS[1][0] + 0.6, 58.0), 1.3, A.MIDDLE_LEFT, "I-GAS", 90)
    zonas(pl, h=1.8, areas=False)
    zonas(pl, lista=M.ADMIN, h=1.5, areas=False)
    tabiques(pl, [z for z in M.ZONAS if z.tipo == "local"], 0.10)
    tabiques(pl, M.ADMIN, 0.10)
    pasillos(pl, rotulos=False)
    muros(pl)
    puertas(pl, h=1.4)
    pintura(pl, 1.2)
    ejes(pl, 2.5, 3.0)
    cotas(pl, 7.0)
    pl.cota((M.XA0, M.YA1), (M.XA1, M.YA1), 6.0, True)
    pl.cota((M.XA1, M.YA0), (M.XA1, M.YA1), 6.0, False)
    # norte
    nx, ny = pl.P(98.0, 74.0)
    pl.m.add_lwpolyline([(nx, ny), (nx - 4, ny - 12), (nx, ny - 9), (nx + 4, ny - 12)], close=True,
                        dxfattribs={"layer": "A-TEXTO"})
    pl.texto("N", (nx, ny + 4), 5.0, A.MIDDLE_CENTER, papel=True)
    muebles(pl)
    equipos(pl, rotulos=False, operarios=False)
    for letra in M.CORTES:
        linea_corte(pl, letra, 2.4)
    # tabla de zonas (columna derecha)
    c = Col(pl, h.fx0 + 672, h.fy1 - 30)
    cols = [("Código", 17, "l"), ("Zona", 148, "l"), ("m²", 16, "r"), ("Fuente", 17, "r")]
    filas = []
    orden = ["MP", "MAN", "PINT", "TERM", "CAR", "PT", "AUX", "LIB"]
    for cat in orden:
        for z in M.ZONAS:
            if z.cat == cat and z.tipo != "pasillo":
                filas.append([z.cod, _corto(z.nombre, 88), f(z.rect.area), f(z.req) if z.req else "-"])
    for z in M.ADMIN:
        filas.append([z.cod, _corto(z.nombre, 88), f(z.rect.area), "-"])
    mitad = (len(filas) + 1) // 2
    y0 = c.y
    pl.tabla(c.x, y0, cols, filas[:mitad], 4.6, 2.3, "Zonas de la nave y del anexo (m² del plano y m² que pide la fuente)",
             3.5)
    c2x = c.x + 236
    pl.tabla(c2x, y0, cols, filas[mitad:], 4.6, 2.3, None, 3.5)
    # resumen en el pie de la planta
    tot, adm = resumen()
    c = Col(pl, h.fx0 + 12, h.fy0 + 240)
    filas = [[NOMBRE_CAT[k], f(tot.get(k, 0.0)), f(100 * tot.get(k, 0.0) / (M.LX * M.LY), 1)] for k in
             ["MP", "MAN", "PINT", "TERM", "CAR", "PT", "AUX", "LIB", "CIRC"]]
    filas.append(["TOTAL NAVE (" + f(M.LX) + " × " + f(M.LY) + " m)", f(M.LX * M.LY), "100,0"])
    filas.append(["Anexo de administración y servicios (" + f(M.XA1 - M.XA0) + " × " + f(M.YA1 - M.YA0) + " m)",
                  f(adm), "-"])
    c.tabla([("Destino", 120, "l"), ("m²", 22, "r"), ("% de la nave", 22, "r")], filas, 3.6, 2.0,
            "Superficies por destino")
    c2 = Col(pl, h.fx0 + 200, h.fy0 + 240)
    c2.titulo("Referencias")
    leyenda_cats(c2, ["MP", "MAN", "PINT", "TERM", "CAR", "PT", "AUX", "ADM", "SAN", "LIB", "AE", "SP", "PO"])
    c4 = Col(pl, h.fx0 + 672, h.fy0 + 300)
    c4.tabla([("Portón", 14, "l"), ("Uso", 120, "l"), ("Ancho (m)", 18, "r")],
             [[p.cod, p.uso, f(p.b - p.a, 1)] for p in M.PUERTAS if p.tipo == "porton"] +
             [[cod, uso, f(b - a, 1)] for cod, a, b, uso in M.PORTONES_PREDIO], 4.3, 2.1,
             "Portones de la nave y del predio")
    c3 = Col(pl, h.fx0 + 375, h.fy0 + 240)
    c3.titulo("Criterios")
    c3.parrafo([
        "Nave de " + f(M.LX) + " × " + f(M.LY) + " m, 10 vanos de 7,6 m; pórticos de 18,5 + 28,5 m con la fila de",
        "columnas en el borde norte del carril del autoelevador (ninguna columna dentro de un carril).",
        "Pasillo principal: carril de 5,0 m (Heli CPCD50, W-CAR) + senda de 1,5 m con baranda y cruces.",
        "Almacén: AL-A de 5,0 m (CPCD50: chapa, atados y bobinas) y AL-B de 3,6 m entre racks (pedido del usuario);",
        "los racks R1 y de PT los atiende un Heli CPD15 eléctrico (apilado a 90° en 3,3 a 3,5 m, ficha Heli).",
        "Portones de la nave: P1 MP 5,0 m (oeste, con la franja de descarga de 15 × 5 m y la cuarentena), P3",
        "camión de la pintura 5,0 m y P4 PT de manuales 3,6 m (este), P2 despacho de carros 3,5 m con rampa y",
        "furgón (sur), P7 scrap 4,0 m (norte del almacén, playa con volquete); P5 patio de ensayos; PE emergencia.",
        "Predio con cerco: PC-1 entrada y PC-2 salida de camiones (circuito de una mano), PC-3 estacionamiento y",
        "PC-4 a PC-6 accesos peatonales del plano de oficinas. Cortes A-A a D-D en FL_PI10_06.",
        "Carros: pico de %d por semana a la pintura con 2 envíos (dato del usuario) -> lotes de media semana:"
        % M.PICO_PINTURA,
        "%d en el pulmón de despacho, %d pintados, %d en la sala de pérdidas, %d retenidos, %d liberados"
        % tuple(k[5] for k in M.STOCK_CARROS[:5]),
        "y %d rechazados. PT unificado de manuales y carros contra el muro sur, debajo de la terminación"
        % M.STOCK_CARROS[5][5],
        "compartida (carga y presurización de manuales y carros), que queda debajo de la pintura, cruzando el",
        "pasillo; racks de manuales de %d posiciones (70 de PT y 17 revendidos de X-ALM)." % M.PT_MAN["posiciones"],
        "Prueba hidráulica de carros al lado de la de manuales y secado de carros al lado del de manuales (y",
        "pegado a su prueba, W-CAR 10); granallado, detección, corrección y cuelgue arriba; descarga de la pintura",
        "frente al embalaje. Lo que quedaba libre en el ángulo SO se usa para residuos especiales (con puerta P8 al",
        "exterior), aceites e inflamables, reciclables, limpieza y el pañol de EPP con primeros auxilios (FL_PI10_07).",
    ], 2.15)
    return h


# ================================================================ FL_PI10_02
TABLA_EQ = ["M4-1", "M4-2", "M4-3", "M3-2", "M5-1", "M6-1", "M7-1", "M8-1", "M9-1", "M10-1", "M11-1", "M12-1",
            "M13-1", "M14-1", "M15-1", "M16-1", "M17-1", "M18-1", "M19-1", "M20-1", "M20-2", "M21-1", "M22-1",
            "M23-1", "M24-1", "M25-3", "M25-4", "C2-1", "C2-2", "C21-1", "C21-2", "C21-3", "C3-1", "C3-4", "C4-1",
            "C4-2", "C5-1", "C5-3", "C5-4", "C6-1", "C7-1", "C8-1", "C8-4", "C81-2", "C81-3", "C81-4", "C81-6",
            "C9-6", "C9-7", "C10-2", "C11-T", "C12-1", "C13-2", "C13-3", "C13-5", "C17-1", "C17-2", "RE-1", "CA-1",
            "M16-2", "M18-2", "M19-D", "M20-4",
            "RC-1", "RC-2", "RT-1", "PQ-1", "PTM-1", "M4-6", "M25-7"]


def fl_02(doc, ox):
    h = hoja(doc, "A0", ox, "Puestos y equipos", "Layout 2035 v10 - máquinas de X-MAN y X-CAR con su medida",
             "FL_PI10_02", 2, 7, "1:100", "Plano de planta")
    pl = D.Plano(h, 100, (-4.0, -6.0), (h.fx0 + 18, h.fy0 + 150))
    titulo_hoja(pl, h, "FL_PI10_02 - PUESTOS Y EQUIPOS (MANUALES, CARROS, PINTURA, TERMINACIÓN Y ALMACENES)",
                "Máquina de cada puesto según X-MAN y W-CAR; medida de la tabla de áreas v10 (cotización > ET > Word > "
                "criterio). Operario dibujado al frente con 0,95 m libres (verificado).")
    despacho_carros(pl, 1.3)
    antes = D.handles(pl.m)
    base(pl, rot_eq=True, h_eq=0.9, h_z=1.5)
    D.recortar(pl, antes, -12.0, -12.0, M.LX + 6.0, M.LY + 1.5)
    ejes(pl, 3.0, 3.5)
    cotas(pl, 4.5)
    c = Col(pl, h.fx0 + 866, h.fy1 - 30)
    filas = []
    eqs = {e.cod: e for e in M.EQUIPOS}
    for k in TABLA_EQ:
        e = eqs[k]
        filas.append([e.cod, e.zona, _corto(e.nombre, 50), f"{f(e.rect.w, 2)} × {f(e.rect.h, 2)}",
                      _corto(e.fuente, 40)])
    c.tabla([("Cód.", 13, "l"), ("Zona", 13, "l"), ("Equipo", 98, "l"), ("Planta (m)", 22, "c"),
             ("Fuente de la medida", 80, "l")], filas, 4.3, 2.0, "Equipos principales y su medida en planta")
    c.y -= 5.0
    c.tabla([("Zona", 13, "l"), ("Lugares de carros", 48, "l"), ("Regla aplicada (W-CAR y dato del usuario)", 150, "l"),
             ("Medida", 20, "c"), ("Carros", 14, "r")],
            [[k[0], k[1], k[3], k[4], str(k[5])] for k in M.STOCK_CARROS], 4.3, 2.0,
            "Carros en planta: %d por semana a la pintura en 2 envíos (usuario) y reglas de W-CAR (X-CAR: %s por semana)"
            % (M.PICO_PINTURA, M.f1(M.SEMANA)))
    c.tabla([("Almacén de PT de manuales (W-MAN 25: rack de PT y rack de cilindros, pallets en altura)", 160, "l"),
             ("Pallets", 20, "r")],
            [["Pallets por día en el pico (tabla de embalaje de la BOM)", f(M.PT_MAN["pallets_dia"], 1)],
             ["Despacho semanal por pallet completo (X-DT): 5 días", str(M.PT_MAN["semana"])],
             ["Stock de oct-nov para diciembre (X-DT: 6.343 u a 211 u por pallet de W-MAN)", str(M.PT_MAN["diciembre"])],
             ["Revendidos (X-ALM, sección «almacén de producto terminado»)", str(M.PT_MAN["reventa"])],
             ["Posiciones: racks de %d y %d módulos × %d niveles × 2 pallets" % (M.PT_MAN["modulos"],
                                                                                  M.PT_MAN["modulos_b"], M.PT_MAN["niveles"]),
              str(M.PT_MAN["posiciones"])]], 4.3, 2.0)
    c.titulo("Pulmones (sólo los de W-MAN y W-CAR)", 3.0)
    c.parrafo([
        "Carro FCHP20505 (1280 × 610 mm, W-MAN 6) o carro de 12 cajones (1200 × 800 mm, W-MAN 2), en violeta.",
        "PU-K, PU-CU, PU-FO cúpulas y fondos (W-MAN 3); PU-T tramos de 1 kg (W-MAN 2); PU-D, PU-V1 a V3 y PU-FX",
        "cuerpos (W-MAN 6 y 7); PU-CC2 y PU-CC cúpulas con cuello (W-MAN 8); PU-E, PU-B (W-MAN 9 y 10); PU-S y PU-RT",
        "(W-MAN 12); PU-6 y PU-7 (W-MAN 13 y 14); PU-GE (W-MAN 15); PU-G y PU-CO (W-MAN 16); PU-D1 a D3 (descarga,",
        "W-MAN 19); PU-TP y PU-F1 a F5 (W-MAN 19 a 24); PU-T2, PU-V2T y PU-V3T: pulmón del 2.º turno (X-MAN 2035:",
        "pintura en 2 turnos, carga y embalaje en 1; 12,5 cargas de carro por día en el pico -> la mitad).",
    ], 2.0)
    c.titulo("Notas", 3.0)
    c.parrafo([
        "Corte de chapa común (C-02): la mesa elevadora mira al pasillo principal; la zona trasera entrega los",
        "desarrollos de manuales hacia el norte (C-02N) y los cuerpos de carros al marcado (2.1, pegado a la rampa).",
        "Corte de tubo norte-sur: el cajón del atado mira al pasillo AL-A, frente al cantiléver (atado con la pluma).",
        "Desbobinador contra AL-A (bobina con el espolón). Contenedores de scrap del corte y del láser contra AL-A.",
        "Granalladora Airblast G-100: los rodillos de entrada y salida están dentro de los 4,5 m (cotización);",
        "ciclón y filtros de cartucho de su extractor al lado (memoria Airblast; lugar: criterio).",
        "Columna este de manuales (croquis de bloques): soldadura circunferencial -> espesor -> prueba hidráulica",
        "-> secado; al lado, la prueba hidráulica y el secado de carros. Arriba: granallado -> detección (con la",
        "corrección y las jaulas debajo) -> cuelgue; el transportador sale a buscar las piezas al cuelgue y las",
        "devuelve a la descarga (punta sur), frente al embalaje compartido de terminados y cilindros vacíos.",
        "Carros 11 y 12: el camión de la pintura entra por P3 (muro este); las dos tarimas de W-CAR 11 quedan en la",
        "recepción de pintados (W-CAR 12: la descarga usa la tarima del 11). Despacho de carros por P2 (rev 6).",
        "Carros rodantes en filas demarcadas, uno detrás del otro, con los lugares de la tabla de arriba.",
        "Fila de fabricación con todos los elementos de la tabla de espacios de cada puesto de W-CAR.",
        "PT de manuales: rack de 5 módulos (con los revendidos) y rack de 4 (cilindros), pasillo de 3,6 m a P4.",
        "Sin medida en ningún presupuesto (criterio, marcado): desbobinador, alimentador Cena PRE-1, soldadora",
        "circunferencial FS-SWH, jaulas, estación de big bag, extracciones localizadas, ciclón de la granalladora;",
        "armadora de cajas sin cotizar (referencia FS-DDP50).",
    ], 2.0)
    return h


# ================================================================ FL_PI10_03 circulación y flujos
def _p(cod):
    z = next((q for q in M.ZONAS if q.cod == cod), None)
    return z.rect.c


FLUJOS = [
    # materia prima (autoelevador)
    ("MP", [(-6.0, 16.0), (3.0, 16.0), (3.0, 30.0)], "MP a racks (AL-B)"),
    ("MP", [(3.0, 16.0), (11.5, 16.0), (11.5, 44.5)], "Chapa, atados y bobinas (AL-A)"),
    ("MP", [(4.2, 16.0), (4.2, 13.6)], "Cuarentena"),
    ("MP", [(11.5, 16.6), (18.3, 16.6), (18.3, 19.9)], "Chapa a la guillotina"),
    ("MP", [(11.5, 33.0), (15.4, 33.0)], "Atado"),
    ("MP", [(11.5, 43.3), (15.5, 43.3)], "Bobina"),
    ("MP", [(15.4, 13.6), (15.4, 14.6), (51.4, 14.6), (51.4, 13.5)], "Big bag"),
    ("MP", [(51.4, 14.6), (68.35, 14.6), (68.35, 13.4)], "Big bag"),
    ("MP", [(21.3, 16.0), (21.3, 13.6)], "Fleje y polvo"),
    # manuales (semielaborado)
    ("SE", [(21.6, 42.3), (31.4, 42.3)], "Cúpulas"),
    ("SE", [(32.4, 41.5), (32.4, 40.0), (34.6, 40.0), (34.6, 37.2)], ""),
    ("SE", [(24.5, 41.1), (24.5, 38.9)], "Fondos"),
    ("SE", [(16.8, 36.2), (16.8, 37.6), (21.5, 37.6)], "Tramos 1 kg"),
    ("SE", [(19.0, 27.4), (19.0, 31.6), (30.2, 31.6), (30.2, 34.0), (22.1, 34.0), (22.1, 37.3)], "Cuerpos 2,5 a 10 kg"),
    ("SE", [(22.7, 38.0), (28.4, 38.0)], ""),
    ("SE", [(30.2, 38.0), (31.8, 38.0), (31.8, 36.0)], ""),
    ("SE", [(33.6, 36.0), (36.0, 36.0), (36.0, 41.8), (38.3, 41.8), (38.3, 42.3)], "A la soldadura circunferencial"),
    ("SE", [(42.6, 41.9), (43.4, 41.9), (43.4, 30.2), (44.5, 30.2), (44.5, 41.55), (46.9, 41.55)],
     "Soldados -> espesor -> PH -> secado -> granallado"),
    ("SE", [(51.5, 41.3), (52.5, 41.3)], ""),
    ("SE", [(53.2, 40.9), (53.2, 35.9)], "A corregir"),
    ("SE", [(52.7, 33.6), (51.9, 38.6), (46.0, 39.5), (46.0, 40.85)], "Corregidos a re-granallar"),
    ("SE", [(54.6, 41.7), (54.6, 42.8), (63.0, 42.8), (64.5, 41.8)], "Aprobados -> cuelgue"),
    ("SE", [(61.5, 20.1), (61.5, 12.3)], "Vacíos al embalaje"),
    ("SE", [(63.0, 20.1), (63.0, 17.0), (65.6, 17.0), (65.6, 13.45)], "Terminados a la carga"),
    ("SE", [(67.0, 12.2), (74.6, 12.2), (74.9, 10.6), (74.9, 8.5), (72.0, 8.3), (66.4, 9.0)], "Terminación"),
    ("PT", [(62.1, 6.2), (62.1, 3.2), (76.6, 3.2)], "Al rack de PT o directo al camión (P4)"),
    # carros
    ("SE", [(20.6, 25.8), (22.3, 27.0), (24.0, 26.6), (24.0, 23.0), (26.6, 22.9), (32.3, 26.0), (32.3, 23.0),
            (34.8, 22.4), (39.6, 22.4), (46.0, 22.4), (51.9, 22.4), (51.9, 35.7), (50.3, 35.7)], "Carros"),
    ("SE", [(50.75, 34.5), (50.75, 33.3)], ""),
    ("SE", [(49.9, 32.7), (49.7, 31.9)], "PH -> secado"),
    ("SE", [(49.0, 31.2), (49.0, 30.6), (51.9, 30.6), (51.9, 29.6), (58.05, 29.6), (59.0, 29.6)], "Secos al pulmón 11"),
    ("SE", [(58.05, 26.0), (58.05, 20.6), (55.2, 20.6)], "A la tarima"),
    ("SE", [(54.55, 19.9), (54.55, 16.2), (76.6, 16.2)], "A la pintura (P3)"),
    ("SE", [(76.6, 15.2), (53.2, 15.2), (53.2, 19.9)], "Pintados (P3)"),
    ("SE", [(56.25, 22.9), (56.25, 24.3)], ""),
    ("SE", [(57.0, 24.4), (57.2, 20.0), (57.2, 11.0), (56.3, 10.4)], "Pintados a la carga"),
    ("SE", [(53.8, 10.4), (53.0, 10.4)], ""),
    ("SE", [(49.8, 10.4), (47.7, 10.4)], "A -> B -> C"),
    ("SE", [(45.9, 9.2), (45.9, 8.7), (42.0, 8.7), (42.0, 9.4)], "Muestra a pérdidas"),
    ("SE", [(40.9, 9.4), (40.9, 8.3), (38.6, 8.3), (38.6, 9.3)], "Ensayos de lote"),
    ("SE", [(39.25, 7.9), (39.25, -1.0)], "Rodadura (P5)"),
    ("SE", [(44.9, 9.2), (43.0, 8.1), (43.0, 6.9)], "Etiquetado"),
    ("SE", [(43.6, 6.0), (44.2, 7.4), (46.0, 7.4), (46.0, 6.9)], "Etiquetado -> retenidos"),
    ("PT", [(48.0, 6.9), (48.0, 7.4), (53.0, 7.4), (53.0, 6.9)], "Lote liberado"),
    ("PT", [(57.4, 24.2), (57.4, 7.6), (56.8, 7.0)], "Cilindros vendidos vacíos a liberados"),
    ("PT", [(55.25, 1.6), (55.25, -1.0), (55.25, -8.0)], "Despacho de carros (P2, rampa y furgón)"),
]
HILOS = [
    [(M.XA0 + 22.6, M.YA0 + 1.0), (M.XA0 + 22.6, 46.0), (58.0, 46.0), (58.0, 19.2)],
    [(M.XA0 + 22.6, 46.0), (44.5, 46.0), (44.5, 29.5)],
    [(44.5, 46.0), (36.0, 46.0), (36.0, 20.0), (36.0, 13.5)],
    [(M.XA0 + 0.45, M.YA0 + 1.0), (M.XA0 + 0.45, 46.0)],
    [(M.XA0 + 11.6, M.YA0 + 1.0), (M.XA0 + 11.6, 46.0)],
]


def fl_03(doc, ox):
    h = hoja(doc, "A0", ox, "Circulación y flujos", "Layout 2035 v10 - pasillos, materiales y personas",
             "FL_PI10_03", 3, 7, "1:100", "Plano de circulación")
    pl = D.Plano(h, 100, (-8.0, -6.0), (h.fx0 + 12, h.fy0 + 150))
    titulo_hoja(pl, h, "FL_PI10_03 - CIRCULACIÓN, FLUJOS DE MATERIALES Y RECORRIDOS DEL PERSONAL",
                "Carriles del autoelevador, sendas peatonales y pasillos de operarios con su ancho; flujo de MP, de "
                "semielaborado y de PT; hilos del personal desde los vestuarios.")
    despacho_carros(pl, 1.3)
    antes = D.handles(pl.m)
    zonas(pl, h=1.5, areas=False)
    tabiques(pl, [z for z in M.ZONAS if z.tipo == "local"], 0.10)
    pasillos(pl, h=1.4)
    equipos(pl, rotulos=False, operarios=False)
    muros(pl)
    puertas(pl, h=1.5)
    D.recortar(pl, antes, -12.0, -12.0, M.LX + 6.0, M.LY + 1.5)
    for cat, pts, rot in FLUJOS:
        pl.flujo(pts, cat, cada=35.0, rotulo=rot or None, h_txt=1.9)
    for pts in HILOS:
        pl.flujo(pts, "PER", cada=30.0)
    c = Col(pl, h.fx0 + 866, h.fy1 - 30)
    c.titulo("Referencias")
    leyenda_cats(c, ["AE", "SP", "PO"])
    from planta.planos import leyenda_flujos
    c.y -= 6
    c.y = leyenda_flujos(pl, c.x, c.y, ["MP", "SE", "PT", "PER"], "Flujos") - 6
    filas = []
    for z in M.ZONAS:
        if z.tipo == "pasillo":
            filas.append([z.cod, _corto(z.nombre, 52), f(min(z.rect.w, z.rect.h), 1), f(max(z.rect.w, z.rect.h), 1),
                          {"AE": "Autoelevador", "SP": "Peatonal", "PO": "Operarios"}[z.sub]])
    c.tabla([("Cód.", 14, "l"), ("Pasillo", 100, "l"), ("Ancho", 16, "r"), ("Largo", 16, "r"), ("Uso", 26, "l")],
            filas, 4.3, 2.0, "Pasillos (m)")
    c.titulo("Criterios de circulación", 3.0)
    c.parrafo([
        "Heli CPCD50 (W-MAN y W-CAR): circula por A2 y AL-A (5,0 m) y entra a los puestos únicamente donde la",
        "máquina mira al carril: mesa elevadora, cajón del atado, desbobinador, contenedores de scrap (a P7), big",
        "bags (terminación y carro 13); las tarimas de los carros 11 y 12 las lleva por el pasillo principal a P3.",
        "Heli CPD15 eléctrico (agregado por los pasillos angostos que pidió el usuario): racks R1 por AL-B (3,6 m),",
        "racks de PT por PT-MA (3,0 m, un sentido) y PT-MA2 (3,6 m), envolvedora y camión de P4. Apilado a 90°:",
        "3.315 a 3.515 mm según el pallet (ficha Heli CPD15-20); el CPCD50 necesitaría 4,96 m.",
        "Los operarios caminan por las sendas (amarillas) y por los pasillos de operarios de 1,5 a 2,0 m;",
        "cruzan el carril sólo por los cruces demarcados de la baranda.",
        "Atados de 6 m: se mueven colgados de la pluma (W-MAN 1 y 2), a lo largo del pasillo.",
        "Los carros de manuales (FCHP y de 12 cajones) se empujan a mano entre puestos pegados (W-MAN).",
        "Los carros (extintores rodantes) ruedan sobre su juego provisorio desde el puesto 8 (W-CAR).",
    ], 2.0)
    return h


# ================================================================ FL_PI10_04 almacén de MP
def _ventana(pl, win, dib):
    xa, ya, xb, yb = win
    antes = D.handles(pl.m)
    dib(pl)
    D.recortar(pl, antes, xa, ya, xb, yb)
    a, b = pl.P(xa, ya), pl.P(xb, yb)
    pl.m.add_lwpolyline([a, (b[0], a[1]), b, (a[0], b[1])], close=True, dxfattribs={"layer": "A-TEXTO"})


def leyenda_secciones(c, w=8.0):
    """Referencia de colores de las secciones del almacén (X-ALM v5), con sus posiciones y dónde van."""
    c.titulo("Secciones del almacén (X-ALM v5; colores del croquis del usuario)", 3.0)
    for cod, (nom, pos, donde, rgb) in M.SECCIONES_ALM.items():
        x, y = c.x, c.y
        q = [(x, y), (x + w, y), (x + w, y - 4.0), (x, y - 4.0)]
        hh = c.pl.m.add_hatch(dxfattribs={"layer": "A-RELLENO"})
        hh.set_solid_fill(rgb=_tinte(rgb, 0.35))
        hh.paths.add_polyline_path(q, is_closed=True)
        c.pl.m.add_lwpolyline(q, close=True, dxfattribs={"layer": "A-SECTOR"})
        c.pl.texto(cod, (x + w / 2, y - 2.0), 2.0, A.MIDDLE_CENTER, papel=True)
        c.pl.texto(f"{nom} ({pos} pos.): {donde}", (x + w + 2.5, y - 2.0), 2.3, A.MIDDLE_LEFT, papel=True)
        c.y -= 5.4
    c.y -= 3.0


def fl_04(doc, ox):
    h = hoja(doc, "A0", ox, "Almacén de MP y recepción", "Layout 2035 v10 - X-ALM v5 con el autoelevador de W-CAR",
             "FL_PI10_04", 4, 7, "1:50", "Plano de detalle")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI10_04 - ALMACÉN DE MATERIA PRIMA, RECEPCIÓN Y LOCALES DEL "
                "ÁNGULO SUDOESTE", "Secciones de X-ALM v5 con su color; espacios de W-CAR 1 al pie de la letra "
                "(cuarentena, retenidos, calle de chapa, racks de carros, franja de descarga).")

    def dib(pl):
        base(pl, rot_eq=True, h_eq=1.2, h_z=2.2)
        cotas_alm(pl)

    win1 = (-1.0, 18.0, 16.0, 48.0)
    pl1 = D.Plano(h, 50, (win1[0], win1[1]), (h.fx0 + 15, h.fy0 + 25))
    _ventana(pl1, win1, dib)
    pl1.texto("Almacén de MP (x 0 a 14,0; y 20 a 47)", pl1.P(win1[0], win1[3]), 4.0, A.BOTTOM_LEFT, papel=True)
    win2 = (-6.5, -1.0, 26.0, 19.0)

    def dib2(pl):
        dib(pl)
        predio(pl, 2.2)

    pl2 = D.Plano(h, 50, (win2[0], win2[1]), (h.fx0 + 395, h.fy0 + 395))
    _ventana(pl2, win2, dib2)
    pl2.texto("Portón P1 y franja de descarga, recepción, cuarentena, polvo, fleje y locales del ángulo SO "
              "(x -6 a 26; y 0 a 19)", pl2.P(win2[0], win2[3]), 4.0, A.BOTTOM_LEFT, papel=True)
    c = Col(pl2, h.fx0 + 395, h.fy0 + 380)
    filas = [
        ["Rack R1", "80 posiciones: 10 módulos de 2,67 m × 4 niveles × 2 pallets, por secciones", "80 pos.", "X-ALM"],
        ["Racks de carros", "casquetes y cuplas 7,3 × 1,2 m (12 pos.) e insumos 4,9 × 1,2 m (8 pos.), 2 niveles",
         "20 pos.", "W-CAR 1"],
        ["Hojas de manuales", "rack por espesor, 4 niveles, 3 bocas (1,25, 1,6 y 2,0 mm)", "12 paq.", "W-MAN 1"],
        ["Calle de chapa de carros", "10 × 2 m, 3 posiciones de 3,0 × 1,5 m, 2 paquetes de alto", "20 m²",
         "W-CAR 1"],
        ["Cantiléver", "frente de 12,4 m, 5 niveles, brazos de 1,2 m", "11 pos.", "X-ALM"],
        ["Bobinas de fleje", "21 posiciones en 7 calles de 3 (pallet en piso, 1 nivel)", "21 pos.", "X-ALM P05-P11"],
        ["Polvo químico y pintura", "big bags en el piso de a 2 (4 pilas) y 1 pila de 2 pallets, local cerrado",
         "10 u", "W-CAR 1 / X-ALM"],
        ["Pallets vacíos", "7 pilas en piso (sección embalaje)", "7 pilas", "X-ALM"],
        ["Identificación e insumos chicos", "estantería de cajas de 5 niveles, identificación bajo llave", "15 lug.",
         "X-ALM"],
        ["Cuarentena", "10 × 2,5 m: 7 pallets, mesa de inspección y 1,3 m de circulación, pegada a P1", "25 m²",
         "W-CAR 1"],
        ["Retenidos de MP", "4 × 1,5 m demarcado en rojo, 3 pallets", "6 m²", "W-CAR 1"],
        ["Jaula de tubos de gas", "N₂ y Ar/CO₂, llenos separados de vacíos, ventilada", "2 m²", "W-CAR 1"],
        ["Recepción", "balanza 1,20 × 1,20 m y mesa de inspección 1,2 × 0,6 m", "6,8 m²", "W-MAN 1 / W-CAR 1"],
        ["Carros de abastecimiento", "3 carros FCEP10520 (2 de carros y 1 de manuales)", "3,5 m²",
         "W-CAR 1 / W-MAN 1"],
        ["Franja de descarga (playón)", "15 × 5 m frente a P1, línea discontinua, compartida con manuales", "75 m²",
         "W-CAR 1"],
        ["Jaula de gases (exterior)", "packs de Arcal 21 y de N₂ con manifold, al sur", "21 m²", "W-MAN 1"],
        ["Revendidos", "van al rack de PT (sección «almacén de producto terminado» de X-ALM)", "17 pos.", "X-ALM"],
    ]
    c.tabla([("Sección", 52, "l"), ("Cómo se guarda", 158, "l"), ("Cantidad", 20, "r"), ("Fuente", 32, "l")], filas,
            4.6, 2.3, "Almacenamiento (cantidades de la fuente)")
    c2 = Col(pl2, h.fx0 + 395, c.y)
    leyenda_secciones(c2)
    c2.parrafo([
        "AL-A de 5,0 m para el Heli CPCD50 (W-CAR 1) y AL-B de 3,6 m para el Heli CPD15 (pedido del usuario; ficha",
        "Heli: 3,3 a 3,5 m para apilar a 90°). Los racks de carros, los retenidos, las pilas de pallets",
        "y la estantería miran a AL-B; el rack de chapas, la calle de chapa y el cantiléver miran a AL-A (W-CAR 1:",
        "«la calle de chapa y los racks quedan del otro lado del pasillo»). El procesado de X-ALM no va al almacén:",
        "W-MAN lo guarda en los carros de 12 cajones al lado de cada puesto. Los insumos de recargas no van.",
    ], 2.4)
    return h


def cotas_alm(pl):
    pl.cadena([0, 1.2, 4.8, 6.0, 7.2, 9.0, 14.0], 47.0, 6.0, True)
    pl.cadena([20.0, 23.7, 36.15, 40.3, 44.8, 47.0], 0.0, -6.0, False)
    pl.cadena([20.0, 24.5, 34.3, 47.0], 14.0, 3.0, False)
    pl.cadena([0, 10.0, 11.5, 13.0, 18.4, 24.7], 0.0, -4.0, True)
    pl.cadena([0, 8.4, 9.9, 13.5, 18.5, 20.0], 0.0, -8.0, False)


# ================================================================ FL_PI10_05 administración
def _largo(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def _disco(pl, c, r, rgb, papel=False):
    cx, cy = c if papel else pl.P(*c)
    rr = r if papel else r * pl.s
    q = [(cx + rr * math.cos(2 * math.pi * k / 24), cy + rr * math.sin(2 * math.pi * k / 24)) for k in range(24)]
    hh = pl.m.add_hatch(dxfattribs={"layer": "A-TEXTO"})
    hh.set_solid_fill(rgb=rgb)
    hh.paths.add_polyline_path(q, is_closed=True)


def circuitos(pl, h=2.2):
    """Circuitos numerados del personal (croquis «Cómo se comunica el área administrativa con la planta»)."""
    for n, txt, rgb, pts in M.CIRCUITOS:
        e = pl.pl(pts, "A-TEXTO", lineweight=50)
        e.rgb = rgb
        a, b = pts[-2], pts[-1]
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        pl.punta(b, ((b[0] - a[0]) / L, (b[1] - a[1]) / L), 3.2, 2.0, rgb)
        _disco(pl, pts[0], 0.3, rgb)
        t = pl.texto(str(n), pts[0], h * 0.85, A.MIDDLE_CENTER, "A-TEXTO")
        t.rgb = (255, 255, 255)


def norte_escala(pl, x, y, metros=5, h=2.5):
    """Flecha de norte y escala gráfica en papel (x, y en mm de papel)."""
    pl.m.add_lwpolyline([(x, y + 14), (x - 4, y + 2), (x, y + 5), (x + 4, y + 2)], close=True,
                        dxfattribs={"layer": "A-TEXTO"})
    hh = pl.m.add_hatch(dxfattribs={"layer": "A-TEXTO"})
    hh.set_solid_fill(rgb=(0, 0, 0))
    hh.paths.add_polyline_path([(x, y + 14), (x, y + 5), (x + 4, y + 2)], is_closed=True)
    pl.texto("N", (x, y + 18), 5.0, A.MIDDLE_CENTER, papel=True)
    x0 = x + 15
    paso = pl.s
    for k in range(metros):
        q = [(x0 + k * paso, y + 4), (x0 + (k + 1) * paso, y + 4), (x0 + (k + 1) * paso, y + 6.5), (x0 + k * paso, y + 6.5)]
        if k % 2 == 0:
            hb = pl.m.add_hatch(dxfattribs={"layer": "A-TEXTO"})
            hb.set_solid_fill(rgb=(0, 0, 0))
            hb.paths.add_polyline_path(q, is_closed=True)
        pl.m.add_lwpolyline(q, close=True, dxfattribs={"layer": "A-TEXTO"})
        pl.texto(str(k), (x0 + k * paso, y + 9), h * 0.8, A.MIDDLE_CENTER, papel=True)
    pl.texto(f"{metros} m", (x0 + metros * paso, y + 9), h * 0.8, A.MIDDLE_CENTER, papel=True)
    pl.texto("Escala gráfica 1:50", (x0, y), h * 0.8, A.TOP_LEFT, papel=True)


def fl_05(doc, ox):
    h = hoja(doc, "A0", ox, "Administración y servicios al personal",
             "Layout 2035 v10 - croquis del usuario y dotación de la X-DT", "FL_PI10_05", 5, 7, "1:50",
             "Plano de detalle")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI10_05 - ADMINISTRACIÓN Y SERVICIOS AL PERSONAL (ANEXO NORTE)",
                "Copia del plano del usuario (23,6 × 14,3 m ≈ 337 m², calle al norte, planta al sur): locales, muebles, "
                "accesos, rampas, relojes, ventanilla, matafuegos, baranda con cruces y los circuitos del personal.")
    win = (M.XA0 - 4.0, 43.5, M.XA1 + 4.0, 70.5)
    pl = D.Plano(h, 50, (win[0], win[1]), (h.fx0 + 15, h.fy0 + 230))

    def dib(p):
        zonas(p, lista=M.ADMIN, h=2.4, areas=True)
        zonas(p, h=2.4, areas=False)
        tabiques(p, M.ADMIN, 0.10)
        pasillos(p, h=2.0)
        equipos(p, rotulos=False, win=win)
        muebles(p)
        rampas(p, 2.0)
        muros(p)
        puertas(p, h=2.2)
        for cod, nom, r in M.EXTERIOR:
            if cod in ("EST", "VE", "CALLE"):
                p.rect(r, "A-EXTERIOR")
                if cod == "CALLE":
                    p.relleno(r.pts(), (215, 215, 215), "A-EXTERIOR")
                p.texto(_corto(nom, 60), (r.x1 - 0.4, r.y1 - 0.4), 2.2, A.TOP_RIGHT, "A-TEXTO")
        predio(p, 2.2)
        for xy in M.MATAFUEGOS_ADMIN:
            _disco(p, xy, 0.17, (215, 30, 30))
            p.texto("Matafuego", (xy[0] + 0.3, xy[1]), 1.6, A.MIDDLE_LEFT, "A-TEXTO")
        for t, xy, rot in M.ROTULOS_ADMIN:
            p.texto(t, xy, 1.6, A.MIDDLE_CENTER, "A-SECTOR-TXT", rot)
        circuitos(p)
        abajo = sorted({round(z.rect.x0, 2) for z in M.ADMIN if z.rect.y0 < M.YA0 + 0.1} | {M.XA1})
        arriba = sorted({round(z.rect.x0, 2) for z in M.ADMIN if z.rect.y1 > M.YA1 - 0.1} | {M.XA1})
        p.cadena(abajo, M.YA0, -7.0, True)
        p.cadena(arriba, M.YA1, 3.0, True)
        p.cadena([M.YA0, M.Y_PL0, M.Y_PL1, M.Y_PC0, M.Y_PC1, M.YA1], M.XA1, 5.5, False)
        p.cota((M.XA0, M.YA1), (M.XA1, M.YA1), 4.5, True)

    _ventana(pl, win, dib)
    # artefactos que hay en cada vestuario (del mobiliario del modelo)
    cuenta = {}
    for t, r, fr, n in M.MOB:
        for z in M.ADMIN:
            if z.rect.x0 - 0.02 <= r.x0 and r.x1 <= z.rect.x1 + 0.02 and z.rect.y0 - 0.02 <= r.y0 and r.y1 <= z.rect.y1 + 0.02:
                cuenta[(z.cod, t)] = cuenta.get((z.cod, t), 0) + n
    c = Col(pl, h.fx0 + 770, h.fy1 - 40)
    filas = [["Turno mañana: operarios de producción", "30", "X-DT Dotación: 46 − 16 de recargas"],
             ["Turno mañana: encargado de turno", "1", "X-DT Servicios y Oficinas fila 35"],
             ["Turno mañana: oficina (jefe de planta, calidad, ventas y cobranzas, compras, PCP)", "5",
              "X-DT filas 21 a 26, sin «atención de recargas»"],
             ["Turno tarde: operarios de producción", "6", "X-DT Dotación fila 104"],
             ["Turno tarde: encargado y administrativo", "2", "X-DT filas 27 y 39"],
             ["Turno más numeroso (mañana): 32 varones y 4 mujeres", "36", "10 % de mujeres, redondeado arriba (X-DT)"],
             ["Personal de planta en los dos turnos (armarios): 34 varones y 4 mujeres", "38", "Operarios + encargados"]]
    c.tabla([("Dotación 2035 sin recargas", 200, "l"), ("Personas", 22, "r"), ("Fuente", 110, "l")], filas, 5.2, 2.6,
            "Dotación")
    c2 = Col(pl, c.x, c.y - 4)
    from .verificar import PEDIDO_SAN, artefactos
    H = artefactos(cuenta, PEDIDO_SAN["varones"][0])
    Mu = artefactos(cuenta, PEDIDO_SAN["mujeres"][0])
    pH, pM = PEDIDO_SAN["varones"][1], PEDIDO_SAN["mujeres"][1]
    filas = [["Inodoros", str(pH["inodoro"]), str(H.get("inodoro", 0)), str(pM["inodoro"]), str(Mu.get("inodoro", 0))],
             ["Orinales", str(pH["mingitorios"]), str(H.get("mingitorios", 0)), "-", "-"],
             ["Lavabos", str(pH["lavabos"]), str(H.get("lavabos", 0)), str(pM["lavabos"]), str(Mu.get("lavabos", 0))],
             ["Duchas", str(pH["duchas"]), str(H.get("duchas", 0)), str(pM["duchas"]), str(Mu.get("duchas", 0))],
             ["Armarios (lockers de 3 niveles)", str(pH["armarios"]), str(H.get("armarios", 0)), str(pM["armarios"]),
              str(Mu.get("armarios", 0))],
             ["Lugares del comedor (2 tandas)", "18", str(cuenta.get(("AD-CO", "mesa"), 0)), "", ""]]
    c2.tabla([("Sanitarios, vestuarios y baños de oficinas", 80, "l"), ("Pide H", 22, "r"), ("Hay H", 22, "r"),
              ("Pide M", 22, "r"), ("Hay M", 22, "r")], filas, 5.2, 2.6,
             "Sanitarios y vestuarios (Dec. 351/79 art. 49, fórmulas X-DT); más el baño accesible")
    filas = [["", txt, f"≈ {f(_largo(pts), 0)} m"] for n, txt, rgb, pts in M.CIRCUITOS]
    x0, y0 = h.fx0 + 15, h.fy0 + 218
    pl.tabla(x0, y0, [("N.º", 10, "c"), ("Circuito (croquis del usuario)", 170, "l"), ("Largo en el plano", 30, "r")],
             filas, 5.0, 2.4, "Circuitos del personal y distancias medidas sobre el plano, a eje de paso", 3.0)
    for k, (n, txt, rgb, pts) in enumerate(M.CIRCUITOS):
        cy = y0 - (k + 1.5) * 5.0
        _disco(pl, (x0 + 5, cy), 2.1, rgb, papel=True)
        t = pl.texto(str(n), (x0 + 5, cy), 2.4, A.MIDDLE_CENTER, papel=True)
        t.rgb = (255, 255, 255)
    norte_escala(pl, h.fx0 + 260, h.fy0 + 150)
    c2.parrafo([
        "Copia del plano del usuario, medido con su escala gráfica. Accesos: visitas, gerencia y oficinas por el",
        "hall (H1 de doble hoja, plataforma a nivel, rampa norte y cajón reservado de 3,50 × 5,00 m); operarios por",
        "el vestíbulo lateral este (H3, rampa, reloj y cartelera de HyS) -> vestuarios -> paso de personal -> planta",
        "(PN-3, doble hoja); supervisión por el ingreso oeste (H4, rampa y reloj del pasillo). Sala técnica (PN-1,",
        "con vidrio a la planta) y comedor (PN-2) con puerta directa a la senda norte; como en el plano, a la sala",
        "técnica se entra por la gerencia. RRHH con ventanilla al vestíbulo. Pasillo de emergencia de 1,5 m a la",
        "calle (H2) y salida del paso de personal (H5); las puertas exteriores abren hacia afuera. Baño accesible",
        "con puerta corrediza (Ley 24.314). Dos matafuegos en el pasillo único. Plenum sanitario único.",
        "Higiene y Seguridad y medicina laboral son servicios externos (X-DT, Notas M29): no hay enfermería ni pañol",
        "de EPP en el plano. Rampas: " + M.NOTA_RAMPA.lower() + ".",
    ], 2.6)
    return h


# ================================================================ FL_PI10_06 cortes de la nave
def alto_de(e):
    """(clave, alto, fuente) de un equipo según M.ALTURAS: código exacto, código con comodín o tipo de símbolo."""
    nombres = {"R1-*": "Rack R1", "PTM-*": "Racks de PT", "RC-*": "Racks de carros", "M14-*": "Prueba hidráulica",
               "M15-*": "Secadoras", "PQ-*": "Big bags", "banco": "Mesas y bancos", "mesa_control": "Mesas y bancos",
               "inspeccion": "Mesas y bancos"}
    if e.cod in M.ALTURAS:
        return (e.cod,) + M.ALTURAS[e.cod]
    for k, v in M.ALTURAS.items():
        if k.endswith("*") and e.cod.startswith(k[:-1]) and not (k == "PQ-*" and e.tipo != "bigbag"):
            return (nombres.get(k, k),) + v
    if e.tipo in M.ALTURAS:
        return (nombres.get(e.tipo, e.tipo),) + M.ALTURAS[e.tipo]
    return None


def _tramo(r, eje, v):
    """Intervalo (s0, s1) donde el rectángulo r corta el plano (eje 'y' = v → s es x; eje 'x' = v → s es y)."""
    if eje == "y":
        return (r.x0, r.x1) if r.y0 <= v <= r.y1 else None
    return (r.y0, r.y1) if r.x0 <= v <= r.x1 else None


def _carros_corte(pl, s0, s1, alto, capa="A-EQUIPO"):
    """Siluetas de carros rodantes en corte: cuerpo, cúpula, rueda y manija, uno cada 0,55 m."""
    n = max(1, int((s1 - s0) / 0.55))
    for k in range(n):
        c = s0 + (k + 0.5) * (s1 - s0) / n
        pl.rect(M.R(c - 0.15, 0.2, c + 0.15, alto - 0.25), capa)
        pl.circulo((c, 0.17), 0.17, "A-EQUIPO-FINO")
        pl.linea((c - 0.15, alto - 0.25), (c, alto), "A-EQUIPO-FINO")
        pl.linea((c + 0.15, alto - 0.25), (c, alto), "A-EQUIPO-FINO")


def dibujar_corte(pl, letra, s_min, s_max, h=1.8):
    """Corte vertical de la nave (y del anexo y el exterior cuando el plano los cruza)."""
    eje, v, mira = M.CORTES[letra]
    usados = {}
    # terreno y piso
    pl.linea((s_min, 0.0), (s_max, 0.0), "A-MURO")
    pl.relleno([(s_min, 0.0), (s_max, 0.0), (s_max, -0.25), (s_min, -0.25)], (200, 200, 200), "A-RELLENO")
    largo = M.LX if eje == "y" else M.LY
    e = M.MURO
    H = M.ALTURA_LIBRE
    # muros de la nave cortados y línea de altura libre bajo la estructura
    for s in (0.0, largo):
        k = -1 if s == 0.0 else 1
        pl.relleno([(s, 0.0), (s + k * e, 0.0), (s + k * e, H + 0.6), (s, H + 0.6)], (70, 70, 70), "A-MURO")
    pl.linea((0.0, H), (largo, H), "A-EQUIPO-OCULTO")
    pl.texto(f"Altura libre bajo la estructura {f(H, 1)} m (tabla de áreas v10)", (largo / 2, H + 0.25), h,
             A.BOTTOM_CENTER, "A-TEXTO")
    usados["Nave"] = (H, "Altura libre de la nave: 8,0 m (tabla de áreas v10; Dec. 351/79 cap. 5)")
    # columnas: las de la fila que corta el plano, en corte; las de atrás, en vista (línea fina)
    filas = M.EJES_X if eje == "y" else M.EJES_Y
    otras = M.EJES_Y if eje == "y" else M.EJES_X
    en_plano = any(abs(o - v) < M.COL / 2 for o in otras)
    for s in filas:
        if 0.0 < s < largo:
            if en_plano:
                pl.relleno(M.R(s - M.COL / 2, 0, s + M.COL / 2, H).pts(), (0, 0, 0), "A-COLUMNA")
            else:
                pl.rect(M.R(s - M.COL / 2, 0, s + M.COL / 2, H), "A-EQUIPO-OCULTO")
    # portones cortados por el plano (se ven en el muro del fondo de la vista)
    for p_ in M.PUERTAS:
        if p_.tipo != "porton":
            continue
        if eje == "y" and p_.muro in "OE" and p_.a <= v <= p_.b:
            s = 0.0 if p_.muro == "O" else largo
            pl.rect(M.R(s - 0.3, 0, s + 0.3, p_.alto), "A-ABERTURA")
    # zonas: franja bajo el piso con el código de cada una
    zs = []
    for z in M.ZONAS:
        t = _tramo(z.rect, eje, v)
        if t:
            zs.append((t, z))
    for (s0, s1), z in zs:
        pl.linea((s0, -0.25), (s0, -1.6), "A-COTA")
        if s1 - s0 > 0.9:
            pl.texto(z.cod, ((s0 + s1) / 2, -0.9), h * 0.8, A.MIDDLE_CENTER, "A-TEXTO", 90 if s1 - s0 < 2.5 else 0)
        if z.tipo == "local":
            a_, fu = (2.5, "W-CAR 14: sala de paneles de 2,5 m de alto") if z.cod == "C-14" else M.ALTO_LOCAL
            for s in (s0, s1):
                pl.relleno(M.R(s - 0.05, 0, s + 0.05, a_).pts(), (110, 110, 110), "A-TABIQUE")
            pl.linea((s0, a_), (s1, a_), "A-TABIQUE")
            usados[z.cod] = (a_, fu)
    pl.linea((min(t[0] for t, z in zs), -1.6), (max(t[1] for t, z in zs), -1.6), "A-COTA")
    # equipos cortados
    for eq in M.EQUIPOS:
        t = _tramo(eq.rect, eje, v)
        if not t:
            continue
        s0, s1 = t
        ah = alto_de(eq)
        if eq.tipo in ("filas", "rodantes", "lugar"):
            _carros_corte(pl, s0, s1, ah[1])
            usados["Carros"] = ah[1:]
            continue
        if ah is None:
            pl.rect(M.R(s0, 0.0, s1, 0.12), "A-EQUIPO")
            if s1 - s0 > 0.5:
                pl.texto(eq.cod + " s/d", ((s0 + s1) / 2, 0.3), h * 0.75, A.BOTTOM_LEFT, "A-TEXTO", 90)
            continue
        clave, a_, fu = ah
        pl.relleno(M.R(s0, 0, s1, a_).pts(), (255, 248, 240), "A-EQUIPO-RELLENO")
        pl.rect(M.R(s0, 0, s1, a_), "A-EQUIPO")
        if eq.tipo == "rack" or eq.cod.startswith("PQ-"):
            niv = 5 if eq.cod.startswith("PTM") else 4 if eq.cod.startswith("R1") else 2
            for k in range(1, niv):
                pl.linea((s0, a_ * k / niv), (s1, a_ * k / niv), "A-EQUIPO-FINO")
        pl.texto(f"{eq.cod} {f(a_, 2)} m", ((s0 + s1) / 2, a_ + 0.15), h * 0.8, A.BOTTOM_LEFT, "A-TEXTO", 90)
        usados[clave] = (a_, fu)
    # anexo de administración y exterior (corte transversal)
    if eje == "x" and M.XA0 <= v <= M.XA1:
        a_, fu = M.ALTO_LOCAL
        pl.relleno([(M.YA0, 0), (M.YA0 + e, 0), (M.YA0 + e, a_ + 0.3), (M.YA0, a_ + 0.3)], (70, 70, 70), "A-MURO")
        pl.relleno([(M.YA1 - e, 0), (M.YA1, 0), (M.YA1, a_ + 0.3), (M.YA1 - e, a_ + 0.3)], (70, 70, 70), "A-MURO")
        pl.linea((M.YA0, a_), (M.YA1, a_), "A-TABIQUE")
        pl.linea((M.YA0, a_ + 0.3), (M.YA1, a_ + 0.3), "A-TABIQUE")
        for z in M.ADMIN:
            t = _tramo(z.rect, eje, v)
            if not t:
                continue
            s0, s1 = t
            for s in (s0, s1):
                if M.YA0 + 0.1 < s < M.YA1 - 0.1:
                    pl.relleno(M.R(s - 0.05, 0, s + 0.05, a_).pts(), (110, 110, 110), "A-TABIQUE")
            if s1 - s0 > 0.9:
                pl.texto(z.cod, ((s0 + s1) / 2, -0.9), h * 0.8, A.MIDDLE_CENTER, "A-TEXTO", 90 if s1 - s0 < 2.5 else 0)
            pl.linea((s0, -0.25), (s0, -1.6), "A-COTA")
        usados["Anexo"] = (a_, fu)
        pl.cota((M.YA1 + 0.5, 0), (M.YA1 + 0.5, a_), 4.0, False)
        for cod, nom, r in M.EXTERIOR:
            t = _tramo(r, eje, v)
            if t and cod in ("EST", "VE", "CALLE"):
                pl.texto(_corto(nom, 30), ((t[0] + t[1]) / 2, 0.4), h * 0.8, A.BOTTOM_CENTER, "A-TEXTO")
                pl.linea((t[0], -0.25), (t[0], -1.0), "A-COTA")
        pl.linea((M.PREDIO.y1, 0), (M.PREDIO.y1, 1.8), "A-EXTERIOR")
        pl.texto("Cerco", (M.PREDIO.y1, 2.0), h * 0.7, A.BOTTOM_CENTER, "A-TEXTO")
    if eje == "y" and M.FRANJA_DESCARGA.y0 <= v <= M.FRANJA_DESCARGA.y1:
        r = M.FRANJA_DESCARGA
        pl.texto("Franja de descarga 15 × 5 m", ((r.x0 + r.x1) / 2, 0.4), h * 0.8, A.BOTTOM_CENTER, "A-TEXTO", 90)
    # cotas de altura
    pl.cota((largo + 1.2, 0), (largo + 1.2, H), 4.0, False)
    return usados


def fl_06(doc, ox):
    h = hoja(doc, "A0", ox, "Cortes de la nave", "Layout 2035 v10 - cortes A-A a D-D con las alturas de las fuentes",
             "FL_PI10_06", 6, 7, "1:100", "Plano de cortes")
    titulo_hoja(D.Plano(h, 100, (0, 0), (0, 0)), h, "FL_PI10_06 - CORTES DE LA NAVE A-A, B-B, C-C Y D-D",
                "Alturas con fuente (ET, cotizaciones, W-CAR, hoja de especificaciones); lo que no tiene alto en "
                "ninguna fuente va marcado «s/d». Ubicación de los cortes en la planta de la derecha y en FL_PI10_01.")
    usados = {}
    lam = [("A", -9.0, 80.0, (22, 640), "CORTE A-A  (longitudinal por y = 5,6 m, mirando al norte)"),
           ("C", -9.0, 80.0, (22, 470), "CORTE C-C  (longitudinal por y = 37,65 m, mirando al norte)"),
           ("B", -5.0, 77.5, (22, 300), "CORTE B-B  (transversal por x = 38,4 m, mirando al oeste; el norte a la derecha)"),
           ("D", -5.0, 50.0, (22, 130), "CORTE D-D  (transversal por x = 68,3 m, mirando al oeste; el norte a la derecha)")]
    for letra, s0, s1, (px, py), tit in lam:
        pc = D.Plano(h, 100, (s0, -2.5), (h.fx0 + px, h.fy0 + py))
        usados.update(dibujar_corte(pc, letra, s0, s1, 2.0))
        pc.texto(tit, pc.P(s0, 10.6), 4.2, A.BOTTOM_LEFT, papel=True)
    # planta de ubicación de los cortes (1:500)
    pk = D.Plano(h, 500, (-30.0, -25.0), (h.fx0 + 935, h.fy0 + 470))
    pk.rect(M.R(0, 0, M.LX, M.LY), "A-MURO")
    pk.rect(M.R(M.XA0, M.YA0, M.XA1, M.YA1), "A-MURO")
    pk.rect(M.PREDIO, "A-EXTERIOR")
    for z in M.ZONAS:
        if z.tipo != "pasillo":
            pk.rect(z.rect, "A-SECTOR")
    for letra in M.CORTES:
        linea_corte(pk, letra, 3.0)
    pk.texto("Ubicación de los cortes (1:500)", pk.P(-30.0, 72.0), 3.5, A.BOTTOM_LEFT, papel=True)
    # tabla de alturas usadas
    filas = [[k, f(a_, 2), fu] for k, (a_, fu) in sorted(usados.items())]
    c = Col(pk, h.fx0 + 600, h.fy0 + 245)
    c.tabla([("Elemento", 34, "l"), ("Alto (m)", 16, "r"), ("Fuente", 300, "l")], filas, 4.4, 2.2,
            "Alturas dibujadas y su fuente")
    c.parrafo([
        "Portones: 4,5 m de alto (criterio: caja de camión de hasta 4,1 m, Ley 24.449 art. 53); P1 y P3 de",
        "5,0 m de ancho, P4 de 3,6 m (pasillo de los racks), P7 de 4,0 m y P2 de 3,5 m (plano de carros, rev 6).",
        "Los equipos sin alto en ninguna fuente (guillotina, roladora W12, viradores, soldadoras, bobinas, carros de",
        "planta, pallets en piso) se marcan «s/d»: se completan con el plano del fabricante.",
    ], 2.4)
    return h


def linea_corte(pl, letra, h=3.0):
    """Línea de corte en planta con flechas hacia donde se mira y la letra en cada punta."""
    eje, v, mira = M.CORTES[letra]
    if eje == "y":
        a, b = (-4.0, v), (M.LX + 4.0, v)
        d = (0, 1) if mira == "N" else (0, -1)
    else:
        a, b = (v, -4.0), (v, M.YA1 + 3.0)
        d = (1, 0) if mira == "E" else (-1, 0)
    pl.linea(a, b, "A-EJE")
    for p_ in (a, b):
        q = (p_[0] + d[0] * 2.5, p_[1] + d[1] * 2.5)
        pl.linea(p_, q, "A-TEXTO")
        pl.punta(q, d, h * 1.2, h * 0.8)
        pl.texto(letra, (p_[0] - d[1] * 1.5 + d[0] * 1.0, p_[1] + d[0] * 1.5 + d[1] * 1.0), h * 1.4, A.MIDDLE_CENTER,
                 "A-TEXTO")


# ================================================================ FL_PI10_07 seguridad e higiene
ROJO, VERDE_S, AZUL_S, AMAR = (200, 20, 20), (0, 140, 70), (0, 90, 170), (250, 200, 0)


def _cuad(pl, x, y, a, rgb, capa, b=None):
    b = a if b is None else b
    q = [(x - a, y - b), (x + a, y - b), (x + a, y + b), (x - a, y + b)]
    pl.relleno(q, rgb, capa)
    pl.pl(q, capa, True)


def sim_mf(pl, x, y, cod, tipo, h=1.4):
    """Matafuego (IRAM 10005, señal de incendio: rojo): número adentro; rodante más grande; CO₂ rotulado."""
    a = 0.4 if "rodante" in tipo else 0.3
    _cuad(pl, x, y, a, ROJO, "S-INCENDIO")
    pl.texto(cod.split("-")[-1], (x, y), h * (0.8 if a > 0.3 else 0.65), A.MIDDLE_CENTER, "A-TEXTO")
    if "rodante" in tipo:
        pl.texto("50 kg", (x, y - a - 0.1), h * 0.55, A.TOP_CENTER, "A-TEXTO")
    elif "CO" in tipo:
        pl.texto("CO₂", (x, y - a - 0.1), h * 0.55, A.TOP_CENTER, "A-TEXTO")


def sim_bq(pl, x, y, h=1.4):
    _cuad(pl, x, y, 0.28, VERDE_S, "S-ESCAPE")
    pl.linea((x - 0.18, y), (x + 0.18, y), "A-TEXTO")
    pl.linea((x, y - 0.18), (x, y + 0.18), "A-TEXTO")


def sim_be(pl, x, y, h=1.4):
    pts = [(x + 0.24 * math.cos(t / 10 * math.pi), y + 0.24 * math.sin(t / 10 * math.pi)) for t in range(20)]
    pl.relleno(pts, AZUL_S, "S-SENAL")
    pl.texto("BE", (x, y + 0.32), h * 0.5, A.BOTTOM_CENTER, "A-TEXTO")


def sim_le(pl, x, y):
    pl.rect(M.R(x - 0.3, y - 0.12, x + 0.3, y + 0.12), "S-ESCAPE")
    pl.relleno([(x - 0.3, y - 0.12), (x, y - 0.12), (x, y + 0.12), (x - 0.3, y + 0.12)], VERDE_S, "S-ESCAPE")


def sim_senal(pl, tipo, x, y, txt=None, h=1.4, r=0.32):
    if tipo == "obl":
        pts = [(x + r * math.cos(t / 12 * math.pi), y + r * math.sin(t / 12 * math.pi)) for t in range(24)]
        pl.relleno(pts, AZUL_S, "S-SENAL")
    elif tipo == "adv":
        pts = [(x - r, y - r * 0.8), (x + r, y - r * 0.8), (x, y + r * 0.9)]
        pl.relleno(pts, AMAR, "S-SENAL")
        pl.pl(pts, "A-TEXTO", True)
    elif tipo == "pro":
        pts = [(x + r * math.cos(t / 12 * math.pi), y + r * math.sin(t / 12 * math.pi)) for t in range(24)]
        pl.pl(pts, "S-INCENDIO", True)
        pl.linea((x - r * 0.7, y + r * 0.7), (x + r * 0.7, y - r * 0.7), "S-INCENDIO")
    if txt:
        pl.texto(txt, (x, y - r - 0.08), h * 0.5, A.TOP_CENTER, "A-TEXTO")


def sim_flecha(pl, p, d, largo=1.3, capa="S-ESCAPE"):
    a = (p[0] - d[0] * largo / 2, p[1] - d[1] * largo / 2)
    b = (p[0] + d[0] * largo / 2, p[1] + d[1] * largo / 2)
    pl.linea(a, b, capa)
    pl.punta(b, d, 2.2, 1.5, VERDE_S, capa)


def salidas_seg(pl, h=1.6):
    """Cartel SALIDA adentro de cada salida y ancho de la salida afuera."""
    for p in SEG.salidas():
        w = p.b - p.a
        m = (p.a + p.b) / 2
        dentro = {"N": (m, M.LY - 1.4), "S": (m, 1.4), "E": (M.LX - 1.4, m), "O": (1.4, m)}[p.muro]
        rot = 0 if p.muro in "NS" else 90
        a, b = (0.8, 0.28) if rot == 0 else (0.28, 0.8)
        _cuad(pl, dentro[0], dentro[1], a, VERDE_S, "S-ESCAPE", b)
        pl.texto("SALIDA", dentro, h * 0.55, A.MIDDLE_CENTER, "A-TEXTO", rot)
        fuera = {"N": (m, M.LY + 2.6), "S": (m, -2.6), "E": (M.LX + 2.9, m), "O": (-2.9, m)}[p.muro]
        pl.texto(f"{f(w, 2)} m", fuera, h * 0.75, A.MIDDLE_CENTER, "S-ESCAPE", rot)


def gases(pl, h=1.4):
    """Jaula de gases exterior por sectores, cañerías de N₂ y de Arcal 21 y entrada del gas natural."""
    jg = next(r for c, n, r in M.EXTERIOR if c == "JG")
    pl.rect(jg, "A-EQUIPO")
    pl.rect(M.R(jg.x0 + 0.08, jg.y0 + 0.08, jg.x1 - 0.08, jg.y1 - 0.08), "A-EQUIPO-OCULTO")
    for nom, r in M.JG_SECTORES:
        S.dibujar(pl, SimpleNamespace(rect=_r(r), nombre=nom, tipo="bateria_gas", frente="S", op=0, espejo=False),
                  False)
        pl.texto(nom.replace("Arcal 21", "Arcal"), (r.c[0], r.y0 - 0.15), h * 0.45, A.TOP_CENTER, "A-TEXTO")
    pl.linea((jg.x0 + 2.8, jg.y0), (jg.x0 + 4.4, jg.y0), "A-ABERTURA")
    pl.texto("Puerta (autoelevador)", (jg.x0 + 3.6, jg.y0 - 0.2), h * 0.5, A.TOP_CENTER, "A-TEXTO")
    pl.texto("JG · jaula de gases: malla, techo liviano, ventilación natural, cilindros parados y encadenados, llenos "
             "separados de vacíos, bolardos (Dec. 351/79 art. 142; W-MAN)", (jg.x0, jg.y0 - 1.6), h * 0.6,
             A.TOP_LEFT, "A-TEXTO")
    pl.pl(M.CANERIA_N2, "I-N2")
    pl.texto("N₂ a la presurización M22-1 (W-MAN)", (76.9, 4.5), h * 0.55, A.MIDDLE_CENTER, "I-N2", 90)
    pl.pl(M.CANERIA_ARCAL, "I-SOLD")
    for ram in M.RAMALES_ARCAL:
        pl.pl(ram, "I-SOLD")
        pl.circulo(ram[-1], 0.15, "I-SOLD")
    pl.texto("Arcal 21: cañería aérea a los puestos de soldadura de manuales (W-MAN)", (60.4, 9.0), h * 0.55,
             A.MIDDLE_CENTER, "I-SOLD", 90)
    q = [p_ for p_ in M.CANERIA_GAS if p_[1] <= 58.0] or [M.CANERIA_GAS[-1]]
    pl.pl([(M.CANERIA_GAS[-1][0], 57.5), M.CANERIA_GAS[-1]], "I-GAS")
    pl.texto("Gas natural de la ERM a los hornos de pintura (FL_PI10_01)", (M.CANERIA_GAS[-1][0] + 0.4, 52.0),
             h * 0.55, A.MIDDLE_LEFT, "I-GAS", 90)
    _ = q


def cobertizo(pl, h=1.4):
    r = next(q for c, n, q in M.EXTERIOR if c == "CAE")
    pl.rect(r, "A-EQUIPO")
    for x0, x1, nom in ((r.x0 + 0.15, r.x0 + 2.25, "Heli CPCD50"), (r.x0 + 2.45, r.x1 - 0.2, "Heli CPD15 eléctrico")):
        q = M.R(x0, r.y0 + 0.3, x1, r.y1 - 1.0)
        pl.rect(q, "A-DEM-AM")
        pl.texto(nom, q.c, h * 0.55, A.MIDDLE_CENTER, "A-TEXTO", 90)
    MO.dibujar(pl, SimpleNamespace(tipo="cargador", rect=_r(M.R(r.x0 + 2.6, r.y1 - 0.9, r.x1 - 0.9, r.y1 - 0.15)),
                                   frente="S", n=1))
    MO.dibujar(pl, SimpleNamespace(tipo="lavaojos", rect=_r(M.R(r.x1 - 0.8, r.y1 - 0.85, r.x1 - 0.15, r.y1 - 0.2)),
                                   frente="S", n=1))
    pl.texto("CAE · cobertizo de autoelevadores: estacionamiento y carga de baterías (Res. SRT 960/15 art. 22)",
             (r.x0 - 0.4, r.c[1]), h * 0.6, A.MIDDLE_CENTER, "A-TEXTO", 90)


def encuentros(pl, h=1.4):
    for cod, nom, r in M.EXTERIOR:
        if not cod.startswith("PEU"):
            continue
        pl.rect(r, "S-ESCAPE")
        c = r.c
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a = (c[0] + d[0] * 1.8, c[1] + d[1] * 1.8)
            pl.linea((c[0] + d[0] * 0.5, c[1] + d[1] * 0.5), a, "S-ESCAPE")
            pl.punta((c[0] + d[0] * 0.5, c[1] + d[1] * 0.5), (-d[0], -d[1]), 2.2, 1.5, VERDE_S, "S-ESCAPE")
        pl.texto("PUNTO DE ENCUENTRO " + cod[-1], (c[0], r.y1 - 0.3), h * 0.75, A.TOP_CENTER, "S-ESCAPE")


def seguridad_planta(pl, h=1.4):
    """Capa de seguridad sobre la planta: zonas de ruido, salidas, flechas, recorrido máximo, luces, matafuegos,
    botiquines, bebederos y señales."""
    zon = {z.cod: z for z in M.ZONAS}
    for zc, fu in M.ZONAS_RUIDO:
        r = zon[zc].rect
        pl.rect(M.R(r.x0 + 0.12, r.y0 + 0.12, r.x1 - 0.12, r.y1 - 0.12), "A-ZONA-LOG")
    for x, y in SEG.luces():
        sim_le(pl, x, y)
    for p, d in SEG.flechas():
        sim_flecha(pl, p, d)
    es = SEG.escape()
    cam = sg.LineString(es["camino"]).simplify(0.4)
    pl.pl(list(cam.coords), "S-ESCAPE")
    x, y = es["peor"]
    pl.circulo((x, y), 0.35, "S-ESCAPE")
    pl.texto(f"Recorrido máximo {f(es['max'], 1)} m (≤ {f(M.RECORRIDO_MAX, 0)} m)", (x + 0.5, y + 0.4), h * 0.75,
             A.BOTTOM_LEFT, "S-ESCAPE")
    salidas_seg(pl, h * 1.1)
    for cod, x, y, t, mot in SEG.matafuegos():
        sim_mf(pl, x, y, cod, t, h)
    for k, (x, y, t, mot) in enumerate(M.MATAFUEGOS_EXT):
        sim_mf(pl, x, y, f"E{k + 1}", t, h)
    for k, (x, y) in enumerate(M.MATAFUEGOS_ADMIN):
        sim_mf(pl, x, y, f"A{k + 1}", "ABC", h)
    for x, y, t in M.BOTIQUINES:
        sim_bq(pl, x, y, h)
    for x, y, t in M.BEBEDEROS:
        sim_be(pl, x, y, h)
    for tipo, txt, x, y in SEG.senales():
        sim_senal(pl, tipo, x, y, txt, h)


def _leyenda_seg(h, x, y):
    """Referencias de los símbolos de la lámina (cada uno dibujado en su propio marco a 1:100)."""
    pl = D.Plano(h, 100, (0.0, 0.0), (x, y))
    pl.texto("Referencias", (0.0, 1.0), 3.5, A.BOTTOM_LEFT, "A-TEXTO")
    items = [
        (lambda q, v: sim_mf(q, 0.6, v, "MF-07", "ABC 10 kg"), "Matafuego ABC 10 kg (número de la tabla); 50 kg: rodante; CO₂: tablero"),
        (lambda q, v: sim_bq(q, 0.6, v), "Botiquín de primeros auxilios (BQ), en columna o muro"),
        (lambda q, v: sim_be(q, 0.6, v), "Bebedero de agua para uso humano (Dec. 351/79 art. 57)"),
        (lambda q, v: sim_le(q, 0.6, v), "Luminaria autónoma de emergencia (art. 76): salidas, cada 10 m y locales"),
        (lambda q, v: (_cuad(q, 0.9, v, 0.8, VERDE_S, "S-ESCAPE", 0.28),
                       q.texto("SALIDA", (0.9, v), 0.8, A.MIDDLE_CENTER, "A-TEXTO")), "Cartel de salida (IRAM 10005, salvamento)"),
        (lambda q, v: sim_flecha(q, (0.8, v), (1, 0)), "Flecha de evacuación pintada en el piso (art. 80)"),
        (lambda q, v: sim_senal(q, "obl", 0.6, v), "Obligación: protección auditiva (zona en trazo azul)"),
        (lambda q, v: sim_senal(q, "adv", 0.6, v), "Advertencia: riesgo eléctrico, superficie caliente, gas o equipo a presión"),
        (lambda q, v: sim_senal(q, "pro", 0.6, v), "Prohibido fumar y hacer fuego"),
        (lambda q, v: q.pl([(0.0, v), (1.6, v)], "I-N2"), "Cañería de N₂"),
        (lambda q, v: q.pl([(0.0, v), (1.6, v)], "I-SOLD"), "Cañería de Arcal 21 (Ar + 8 % CO₂)"),
        (lambda q, v: q.pl([(0.0, v), (1.6, v)], "I-GAS"), "Cañería de gas natural"),
    ]
    v = -0.6
    for fn, txt in items:
        fn(pl, v)
        pl.texto(txt, (2.2, v), 2.2, A.MIDDLE_LEFT, "A-TEXTO")
        v -= 0.95
    return y + v * 10 - 6


FILAS_LEGAL = [
    ["Escape", "2 unidades de ancho (1,10 m) por salida; 0,55 + 0,45 m", "Dec. 351/79 anexo VII, 3",
     "9 salidas de 1,10 a 1,20 m que abren hacia afuera", "Cumple"],
    ["Escape", "N = superficie / 16 m²; n = N / 100 unidades; n/4 + 1 medios", "Dec. 351/79 anexo VII, 3",
     "N = {N}, n = {n} -> 1 medio y {anc} m; hay 9 salidas y {tot} m", "Cumple"],
    ["Escape", "Recorrido hasta una salida", "Anexo VII: 40 m (a la caja de escalera)",
     "Máximo {max} m por la línea de libre trayectoria (grilla de 0,5 m)", "Criterio"],
    ["Escape", "Puertas en el sentido de la evacuación, sin trabas", "Dec. 351/79 anexo VII, 3",
     "Abren hacia afuera, con barral antipánico; puntos de encuentro exteriores", "Cumple"],
    ["Señales", "Vías de evacuación con líneas amarillas y flechas", "Dec. 351/79 art. 80",
     "Flechas en cada pasillo y senda hacia la salida más cercana", "Cumple"],
    ["Señales", "Colores y señales de seguridad", "Dec. 351/79 arts. 77-78; IRAM 10005",
     "SALIDA en cada salida; prohibición, advertencia y obligación por zona", "Cumple"],
    ["Pasillos", "Demarcados con dos franjas o piso pintado", "Dec. 351/79 art. 79",
     "Carriles con dos líneas, sendas en cebra, pasillos de operarios con dos líneas", "Cumple"],
    ["Iluminación", "Emergencia de 30 lx a 0,80 m en los medios de escape", "Dec. 351/79 art. 76",
     "{le} luminarias autónomas: salidas, cada 10 m de pasillo y cada local", "Verificar lux"],
    ["Iluminación", "Niveles por tarea y medición", "Dec. 351/79 anexo IV; Res. SRT 84/12",
     "Proyecto luminotécnico y medición con la planta en marcha", "A completar"],
    ["Incendio", "1 matafuego cada 200 m²", "Dec. 351/79 cap. 18 y anexo VII",
     "{sup} m² -> {mmin}; hay {mf} en la nave, 2 afuera y 2 en el anexo", "Cumple"],
    ["Incendio", "Recorrido al matafuego: 20 m (clase A), 15 m (clase B)", "Dec. 351/79 cap. 18 y anexo VII",
     "Todo punto libre de la nave a 15 m o menos (se toma clase B en todo)", "Cumple"],
    ["Incendio", "Potencial extintor y condiciones según la carga de fuego", "Dec. 351/79 anexo VII",
     "Falta el estudio de carga de fuego por sector", "A completar"],
    ["Gases", "Cilindros parados, sujetos, ventilados, llenos y vacíos aparte", "Dec. 351/79 art. 142",
     "Jaula exterior JG, jaula de tubos CU-2 y batería C13-5 encadenada", "Cumple"],
    ["Autoelevad.", "Carga de baterías en lugar designado y equipado", "Res. SRT 960/15 art. 22",
     "Cobertizo CAE: cargador, lavaojos y matafuego; estacionamiento", "Cumple"],
    ["Autoelevad.", "Señalización de las zonas de circulación", "Res. SRT 960/15",
     "Carriles demarcados, cruces de la baranda y carteles", "Cumple"],
    ["Ruido", "85 dBA en 8 h: protección auditiva y señal", "Res. MTESS 295/03; Res. SRT 85/12",
     "Zonas de protección auditiva de los puestos que la piden en los Word", "Medir"],
    ["Ventilación", "Captación de humos y polvos en la fuente", "Dec. 351/79 cap. 11",
     "Extracción en soldaduras, amolado, cargas de polvo, granallado y ensayos", "Cumple"],
    ["EPP", "Entrega con constancia firmada", "Res. SRT 299/11",
     "Pañol de EPP SV-EP con mostrador y registro", "Cumple"],
    ["Prim. auxilios", "Botiquín y atención inmediata", "Ley 19.587; Dec. 351/79",
     "Sala en SV-EP (camilla, botiquín, lavaojos) y 5 botiquines en planta", "Cumple"],
    ["Lavaojos", "Lavado de ojos (ficha de seguridad del polvo ABC)", "Criterio (W-MAN: ficha en el puesto)",
     "En las cargas y descargas de polvo, en SV-EP y en el cobertizo", "Criterio"],
    ["Agua", "Provisión y reserva para uso humano", "Dec. 351/79 art. 57",
     "4 bebederos; reserva de 50 L por persona y jornada con la dotación X-DT", "A completar"],
    ["Sanitarios", "Artefactos y armarios por sexo", "Dec. 351/79 art. 49",
     "Verificado con la dotación de X-DT (FL_PI10_05)", "Cumple"],
    ["Residuos", "Depósito transitorio, manifiesto y gestor", "Ley 24.051; Ley 11.720 (PBA)",
     "SV-RE con tambores sobre batea y puerta P8 al exterior", "Cumple"],
    ["Inflamables", "Fuera de los puestos, en local ventilado", "Dec. 351/79 cap. 18",
     "SV-IN contra el muro exterior: armario de seguridad y batea", "Cumple"],
    ["Máquinas", "Resguardos, paradas de emergencia, zonas delimitadas", "Dec. 351/79 cap. 15",
     "Los de W-MAN y W-CAR en cada puesto (zona de la envolvedora)", "Cumple"],
    ["Accesibilidad", "Baño accesible, rampas de 8 %, cajón reservado", "Ley 24.314",
     "Anexo de administración (FL_PI10_05)", "Cumple"],
    ["Gas natural", "Instalación industrial y ERM", "NAG-201 (ENARGAS)",
     "ERM en la línea municipal y cañería a los hornos de la pintura", "A completar"],
    ["Servicios", "Higiene y Seguridad y medicina laboral", "Dec. 1338/96",
     "Externos (X-DT, notas M29)", "Cumple"],
]


def fl_07(doc, ox):
    h = hoja(doc, "A0", ox, "Seguridad e higiene", "Layout 2035 v10 - escape, incendio, señales, gases y residuos",
             "FL_PI10_07", 7, 7, "1:100", "Plano de seguridad")
    pl = D.Plano(h, 100, (-6.0, -15.0), (h.fx0 + 8, h.fy0 + 8))
    titulo_hoja(pl, h, "FL_PI10_07 - SEGURIDAD E HIGIENE: MEDIOS DE ESCAPE, PROTECCIÓN CONTRA INCENDIO, SEÑALES, "
                "PRIMEROS AUXILIOS, GASES Y RESIDUOS",
                "Ley 19.587 y Dec. 351/79, Res. SRT 960/15, 295/03 y 299/11, Leyes 24.051 y 11.720; lo que piden "
                "W-MAN y W-CAR en cada puesto. Recorridos y coberturas calculados (planta10/seguridad.py).")
    antes = D.handles(pl.m)
    zonas(pl, h=1.4, areas=False)
    tabiques(pl, [z for z in M.ZONAS if z.tipo == "local"], 0.10)
    tabiques(pl, M.ADMIN, 0.10)
    pasillos(pl, rotulos=False)
    equipos(pl, rotulos=False, operarios=False)
    muebles(pl)
    muros(pl)
    puertas(pl, h=1.5)
    for cod, nom, r in M.EXTERIOR:
        if cod in ("PO", "PS", "PE", "PEN", "PSC"):
            pl.rect(r, "A-EXTERIOR")
            pl.texto(_corto(nom, 70), (r.x0 + 0.4, r.y1 - 0.4), 1.6, A.TOP_LEFT, "A-TEXTO")
    despacho_carros(pl, 1.2)
    gases(pl)
    cobertizo(pl)
    encuentros(pl)
    seguridad_planta(pl)
    for n_, txt, rgb, pts in M.CIRCUITOS:                # evacuación del anexo (plano del usuario)
        if "Evacuación" in txt:
            pl.pl(pts, "S-ESCAPE")
            a, b = pts[-2], pts[-1]
            L_ = math.dist(a, b)
            pl.punta(b, ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_), 2.4, 1.6, VERDE_S, "S-ESCAPE")
    D.recortar(pl, antes, -6.0, -15.0, 80.0, 62.0)
    # ---- columna derecha
    x0 = h.fx0 + 878
    es = SEG.escape()
    mf = SEG.matafuegos()
    c = Col(pl, x0, h.fy1 - 30)
    filas = [["Superficie de la nave", f(es["area"], 0) + " m²", "76 × 47 m"],
             ["Factor de ocupación (industria)", f(M.FACTOR_OCUPACION, 0) + " m²/pers.", "Dec. 351/79 anexo VII"],
             ["Personas N = sup. / factor", str(es["N"]), "X-DT 2035: 36 por turno en planta"],
             ["Unidades de ancho n = N / 100", str(es["n"]), "mínimo 2 unidades"],
             ["Ancho total mínimo", f(es["ancho_min"], 2) + " m", "0,55 + 0,55 + 0,45 m"],
             ["Medios de escape mínimos", str(es["medios_min"]), "n ≤ 3: 1 medio"],
             ["Salidas de la nave / ancho total", f"{len(es['salidas'])} / {f(es['ancho_total'], 2)} m",
              "≥ 1,10 m, abren hacia afuera"],
             ["Recorrido máximo a una salida", f(es["max"], 1) + " m", "criterio ≤ 40 m"]]
    c.tabla([("Medios de escape", 92, "l"), ("Valor", 34, "r"), ("Fuente o criterio", 150, "l")], filas, 4.6, 2.4,
            "Cálculo de medios de escape (Dec. 351/79, anexo VII)")
    filas = [[cod, {"O": "Oeste", "E": "Este", "N": "Norte", "S": "Sur"}[mu], f(w, 2), f(m2, 0),
              str(math.ceil(m2 / M.FACTOR_OCUPACION)), _corto(uso, 70)] for cod, mu, w, m2, uso in es["salidas"]]
    c.tabla([("Salida", 16, "l"), ("Muro", 14, "l"), ("Ancho", 14, "r"), ("m² que llegan", 24, "r"),
             ("Pers.", 14, "r"), ("Uso", 194, "l")], filas, 4.4, 2.3, "Salidas de emergencia y peatonales")
    zon = SEG.zona_de
    filas = [[cod, t, (zon(x, y).cod if zon(x, y) else ""), mot] for cod, x, y, t, mot in mf]
    filas += [[f"MF-E{k + 1}", t, "Exterior", mot] for k, (x, y, t, mot) in enumerate(M.MATAFUEGOS_EXT)]
    filas += [[f"MF-A{k + 1}", "ABC (plano)", "Anexo", "Pasillo único: los dos puntos rojos del plano del usuario"]
              for k in range(len(M.MATAFUEGOS_ADMIN))]
    c.tabla([("Cód.", 15, "l"), ("Tipo", 32, "l"), ("Zona", 18, "l"), ("Ubicación y motivo", 211, "l")], filas, 3.7,
            2.1, "Matafuegos (FLAMA ABC; 1 cada 200 m² y a 15 m o menos de todo punto)")
    datos = {"N": es["N"], "n": es["n"], "anc": f(es["ancho_min"], 2), "tot": f(es["ancho_total"], 1),
             "max": f(es["max"], 1), "le": len(SEG.luces()), "sup": f(es["area"], 0),
             "mmin": math.ceil(es["area"] / M.MF_SUP), "mf": len(mf)}
    filas = [[a, b, n_, d_.format(**datos), e] for a, b, n_, d_, e in FILAS_LEGAL]
    c.tabla([("Tema", 22, "l"), ("Requisito", 74, "l"), ("Norma", 52, "l"), ("Cómo se resuelve en el plano", 106, "l"),
             ("Estado", 22, "l")], filas, 4.3, 2.1, "Cumplimiento legal de seguridad e higiene")
    c.parrafo(["Cláusulas tomadas de copias secundarias (SRT, cámaras y colegios); el texto oficial de InfoLEG no se pudo",
               "abrir desde el entorno de trabajo: confirmarlas antes de la entrega. «Criterio»: decisión de diseño."],
              2.2)
    c.titulo("¿Dónde están los gases en uso? Sí: corresponde jaula de gases", 3.0)
    c.parrafo([
        "Manuales (W-MAN): el N₂ de la presurización y el Arcal 21 de la soldadura están EN USO en la jaula exterior JG,",
        "en packs de 12 cilindros con manifold (uno en uso y uno lleno; el Arcal, dos en uso por el consumo de 48 m³/día),",
        "y llegan a los puestos por cañería. Carros (W-CAR 13): la batería de N₂ de 11 tubos de 50 L está en uso en el",
        "puesto 13, en su jaula, contra el muro de la sala de pérdidas y encadenada (C13-5). Tubos sueltos de N₂ y Ar/CO₂",
        "de las soldadoras de carros: jaula de tubos ventilada CU-2, llenos separados de vacíos (W-CAR 1).",
        "No es un depósito cerrado: es una jaula de malla con techo liviano y ventilación natural (Dec. 351/79 art. 142).",
    ], 2.3)
    _leyenda_seg(h, x0, c.y - 16)
    return h
