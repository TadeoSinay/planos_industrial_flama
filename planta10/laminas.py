"""Láminas del layout v10 (DXF para AutoCAD + PDF), formato y rótulo IRAM.

FL_PI10_01  Planta general, implantación y tabla de áreas (1:200)
FL_PI10_02  Puestos y equipos (1:100)
FL_PI10_03  Circulación y flujos de materiales y de personas (1:100)
FL_PI10_04  Almacén de MP, recepción y servicios del ángulo SO (1:50)
FL_PI10_05  Administración y servicios al personal (1:50)
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
        if rotulos and z.tipo != "pasillo" and r.w * r.h >= 4.0:
            hh = h if min(r.w, r.h) > 2.2 else h * 0.75
            pl.texto(z.cod, (r.x0 + 0.15, r.y1 - 0.15), hh, A.TOP_LEFT, "A-SECTOR-TXT")
            if nombres and r.w > 3.0 and r.h > 2.4:
                n_car = int(r.w * pl.s / (hh * 0.62 * 0.8)) - 2
                for i, ln in enumerate(_cortar(_corto(z.nombre, 90), max(n_car, 12))[:2]):
                    pl.texto(ln, (r.x0 + 0.15, r.y1 - 0.15 - (i + 1) * hh * 1.5 / pl.s), hh * 0.8, A.TOP_LEFT,
                             "A-SECTOR-TXT")
            if areas and r.w > 2.0:
                pl.texto(f"{f(r.w * r.h)} m²", (r.x1 - 0.15, r.y0 + 0.15), hh * 0.8, A.BOTTOM_RIGHT, "A-SECTOR-TXT")


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
        if rotulos and max(r.w, r.h) > 6:
            ang = 0 if r.w >= r.h else 90
            txt = f"{z.cod}  {_corto(z.nombre, 40)}  {f(min(r.w, r.h), 1)} m"
            pl.texto(txt, r.c, h, A.MIDDLE_CENTER, "A-TEXTO", ang)
    # baranda entre el carril del autoelevador y la senda del pasillo principal, con cruces
    cruces = [(3.0, 4.6), (12.4, 14.0), (16.4, 18.0), (35.3, 36.8), (57.3, 58.8), (62.0, 64.0), (70.0, 71.6)]
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
        vanos.append(sg.box(a, M.YA1 - 1, b, M.YA1 + 1) if muro == "N" else sg.box(M.XA1 - 1, a, M.XA1 + 1, b))
    anillo = anillo.difference(unary_union(vanos))
    _macizo(pl, anillo, "A-MURO", (70, 70, 70))
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


def puertas(pl, h=1.6, etiquetas=True):
    X, Y = M.LX, M.LY
    for p in M.PUERTAS:
        if p.muro in "NS":
            y = Y if p.muro == "N" else 0.0
            s = 1 if p.muro == "N" else -1
            a, b = (p.a, y), (p.b, y)
            if p.tipo == "porton":
                pl.linea((p.a, y + s * 0.1), (p.b, y + s * 0.1), "A-ABERTURA")
                pl.linea((p.a, y + s * 0.25), (p.b, y + s * 0.25), "A-ABERTURA")
            else:
                w = p.b - p.a
                pl.linea(a, (p.a, y - s * w), "A-ABERTURA")
                pl.arco(a, w, -90 if s > 0 else 0, 0 if s > 0 else 90, "A-ABERTURA")
            if etiquetas:
                pl.texto(p.cod, ((p.a + p.b) / 2, y + s * 1.4), h, A.MIDDLE_CENTER, "A-TEXTO")
        else:
            x = X if p.muro == "E" else 0.0
            s = 1 if p.muro == "E" else -1
            if p.tipo == "porton":
                pl.linea((x + s * 0.1, p.a), (x + s * 0.1, p.b), "A-ABERTURA")
                pl.linea((x + s * 0.25, p.a), (x + s * 0.25, p.b), "A-ABERTURA")
            else:
                w = p.b - p.a
                pl.linea((x, p.a), (x - s * w, p.a), "A-ABERTURA")
                pl.arco((x, p.a), w, 0 if s < 0 else 90, 90 if s < 0 else 180, "A-ABERTURA")
            if etiquetas:
                pl.texto(p.cod, (x + s * 1.6, (p.a + p.b) / 2), h, A.MIDDLE_CENTER, "A-TEXTO", 90)
    for x, y, w, muro, abre in M.PUERTAS_ADMIN + M.PUERTAS_LOCALES:
        if w > 2.0:
            if muro == "h":
                pl.linea((x, y - 0.05 * abre), (x + w, y - 0.05 * abre), "A-ABERTURA")
            else:
                pl.linea((x - 0.05 * abre, y), (x - 0.05 * abre, y + w), "A-ABERTURA")
        else:
            MO.puerta_int(pl, x, y, w, muro, abre)
    for cod, muro, a, b, uso in M.PUERTAS_EXT_ADMIN:
        if muro == "N":
            pl.linea((a, M.YA1), (a, M.YA1 - (b - a) / 2), "A-ABERTURA")
            pl.linea((b, M.YA1), (b, M.YA1 - (b - a) / 2), "A-ABERTURA")
            pl.arco((a, M.YA1), (b - a) / 2, 270, 360, "A-ABERTURA")
            pl.arco((b, M.YA1), (b - a) / 2, 180, 270, "A-ABERTURA")
        else:
            pl.linea((M.XA1, a), (M.XA1 - (b - a), a), "A-ABERTURA")
            pl.arco((M.XA1, a), b - a, 90, 180, "A-ABERTURA")
        if etiquetas:
            pl.texto(cod, ((a + b) / 2, M.YA1 + 1.2) if muro == "N" else (M.XA1 + 1.2, (a + b) / 2), h,
                     A.MIDDLE_CENTER, "A-TEXTO")


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
    """Línea Firesafer: envolvente, riel en lazo, cabina, horno, enfriamiento y puntos de cuelgue y descarga."""
    e = next(q for q in M.EQUIPOS if q.cod == "M19-1")
    r = e.rect
    pl.relleno(r.pts(), (255, 248, 240), "A-EQUIPO-RELLENO")
    pl.rect(r, "A-EQUIPO")
    partes = [("Enfriamiento", 21.4, 26.0, (220, 235, 250)), ("Horno de curado", 26.4, 38.4, (250, 215, 200)),
              ("Cabina de polvo y recuperación", 38.8, 43.0, (232, 238, 222))]
    for nom, y0, y1, rgb in partes:
        q = M.R(r.x0 + 1.6, y0, r.x1 - 1.6, y1)
        pl.relleno(q.pts(), rgb, "A-EQUIPO-RELLENO")
        pl.rect(q, "A-EQUIPO-FINO")
        pl.texto(nom, q.c, h, A.MIDDLE_CENTER, "A-TEXTO", 90)
    lazo = [(r.x0 + 0.8, 43.6), (r.x0 + 0.8, 21.6), (r.x1 - 0.8, 21.6), (r.x1 - 0.8, 45.4), (r.x0 + 0.8, 45.4),
            (r.x0 + 0.8, 43.6)]
    pl.pl(lazo, "A-EQUIPO-OCULTO")
    for y in (43.0, 28.0):
        pl.circulo((r.x0 + 0.8, y), 0.35, "A-EQUIPO")
    pl.texto("Cuelgue", (r.x0 + 1.3, 43.0), h * 0.8, A.MIDDLE_LEFT, "A-TEXTO")
    pl.texto("Descarga", (r.x0 + 1.3, 28.0), h * 0.8, A.MIDDLE_LEFT, "A-TEXTO")
    pl.texto("Riel aéreo en lazo (ganchos)", (r.c[0], 45.0), h * 0.8, A.MIDDLE_CENTER, "A-TEXTO")


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
        else:
            S.dibujar(pl, SimpleNamespace(rect=_r(r), nombre=e.nombre, tipo=e.tipo, frente=e.frente, op=e.op,
                                          espejo=e.espejo), operarios)
        if rotulos and (r.w >= 0.9 or r.h >= 0.9) and not e.cod.startswith(("R1-", "R2-", "PTM-", "FL-", "HO-")):
            pl.texto(e.cod, (r.c[0], r.c[1]), h, A.MIDDLE_CENTER, "A-TEXTO", 90 if r.h > 2.2 * r.w else 0)


def muebles(pl):
    for t, r, fr, n in M.MOB:
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


def exterior(pl, h=1.8):
    for cod, nom, r in M.EXTERIOR:
        if cod == "CALLE":
            pl.relleno(r.pts(), (215, 215, 215), "A-EXTERIOR")
        pl.rect(r, "A-EXTERIOR")
        pl.texto(_corto(nom, 70), (r.x0 + 0.4, r.y1 - 0.4), h, A.TOP_LEFT, "A-TEXTO")
    pl.pl(M.CAMINO_CAMIONES, "A-ZONA-LOG")
    pl.texto("Circuito de camiones (entra y sale por la calle)", (M.CAMINO_CAMIONES[1][0] + 1, 40.0), h, A.MIDDLE_LEFT,
             "A-TEXTO", 90)


def base(pl, win=None, rot_eq=True, h_eq=1.1, h_z=1.8, pasos=True):
    zonas(pl, h=h_z)
    tabiques(pl, [z for z in M.ZONAS if z.tipo == "local"], 0.10)
    tabiques(pl, M.ADMIN, 0.10)
    pasillos(pl, h=h_z * 0.85)
    equipos(pl, rotulos=rot_eq, h=h_eq, win=win)
    muros(pl)
    puertas(pl, h=h_z)


# ================================================================ cursores de texto en papel
class Col:
    def __init__(self, pl, x, y):
        self.pl, self.x, self.y = pl, x, y

    def titulo(self, t, hh=3.5):
        self.pl.texto(t, (self.x, self.y), hh, A.BOTTOM_LEFT, papel=True)
        self.y -= hh + 2.5

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
        nom = {"AE": "Carril del autoelevador (5,0 m)", "SP": "Senda peatonal demarcada",
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
             "FL_PI10_01", 1, 5, "1:200", "Plano de planta")
    win = (-27.0, -22.5, 104.0, 77.0)
    pl = D.Plano(h, 200, (win[0], win[1]), (h.fx0 + 12, h.fy0 + 262))
    titulo_hoja(pl, h, "FL_PI10_01 - PLANTA GENERAL E IMPLANTACIÓN, ZONAS Y SUPERFICIES",
                "Calle al norte: administración y servicios al personal al norte de la nave (croquis del usuario). "
                "Cada m² de la nave tiene código y nombre (verificado).")
    exterior(pl, 1.6)
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
    c3 = Col(pl, h.fx0 + 375, h.fy0 + 240)
    c3.titulo("Criterios")
    c3.parrafo([
        "Nave de " + f(M.LX) + " × " + f(M.LY) + " m, 10 vanos de 7,6 m; pórticos de 18,5 + 28,5 m con la fila de",
        "columnas en el borde norte del carril del autoelevador (ninguna columna dentro de un carril).",
        "Pasillo principal: carril de 5,0 m (Heli CPCD50, W-CAR) + senda de 1,5 m con baranda y cruces.",
        "Almacén con dos pasillos de 5,0 m (AL-A junto a las máquinas de corte, AL-B entre racks).",
        "Puertas: P1 MP (oeste), P4 despacho de PT de manuales y camión de pintura de carros (este, al final",
        "del pasillo principal: W-CAR 11 «más el de la planta»), P2 despacho de carros (sur), P5 patio de",
        "ensayos; salidas de emergencia PE y puertas PN entre la administración y la planta.",
        "Reservas (RV y LB): lugar para la máquina siguiente de los puestos de manuales al 92-97 % en 2035",
        "(X-MAN) y el espacio libre del croquis. El largo de la nave lo fijan la fila de carros más la",
        "terminación y la pintura (norte) y los puestos 11 a 17 de carros más el PT (sur).",
    ], 2.15)
    return h


# ================================================================ FL_PI10_02
TABLA_EQ = ["M4-1", "M4-2", "M4-3", "M3-2", "M5-1", "M6-1", "M7-1", "M8-1", "M9-1", "M10-1", "M11-1", "M12-1",
            "M13-1", "M14-1", "M15-1", "M16-1", "M17-1", "M18-1", "M19-1", "M20-1", "M20-2", "M21-1", "M22-1",
            "M23-1", "M24-1", "M25-3", "M25-4", "C2-1", "C2-2", "C21-1", "C3-1", "C4-1", "C5-1", "C6-1", "C7-1",
            "C8-1", "C81-2", "C9-1", "C13-2", "C13-3", "C17-1", "RE-1", "CA-1", "PQ-1"]


def fl_02(doc, ox):
    h = hoja(doc, "A0", ox, "Puestos y equipos", "Layout 2035 v10 - máquinas de X-MAN y X-CAR con su medida",
             "FL_PI10_02", 2, 5, "1:100", "Plano de planta")
    pl = D.Plano(h, 100, (-4.0, -6.0), (h.fx0 + 18, h.fy0 + 150))
    titulo_hoja(pl, h, "FL_PI10_02 - PUESTOS Y EQUIPOS (MANUALES, CARROS, PINTURA, TERMINACIÓN Y ALMACENES)",
                "Máquina de cada puesto según X-MAN y W-CAR; medida de la tabla de áreas v10 (cotización > ET > Word > "
                "criterio). Operario dibujado al frente con 0,95 m libres (verificado).")
    antes = D.handles(pl.m)
    base(pl, rot_eq=True, h_eq=0.9, h_z=1.5)
    D.recortar(pl, antes, -12.0, -12.0, M.LX + 6.0, M.LY + 1.5)
    ejes(pl, 3.0, 3.5)
    cotas(pl, 4.5)
    c = Col(pl, h.fx0 + 850, h.fy1 - 30)
    filas = []
    eqs = {e.cod: e for e in M.EQUIPOS}
    for k in TABLA_EQ:
        e = eqs[k]
        filas.append([e.cod, e.zona, _corto(e.nombre, 50), f"{f(e.rect.w, 2)} × {f(e.rect.h, 2)}",
                      _corto(e.fuente, 40)])
    c.tabla([("Cód.", 13, "l"), ("Zona", 13, "l"), ("Equipo", 98, "l"), ("Planta (m)", 22, "c"),
             ("Fuente de la medida", 80, "l")], filas, 4.3, 2.0, "Equipos principales y su medida en planta")
    c.titulo("Pulmones (sólo los de W-MAN y W-CAR)", 3.0)
    c.parrafo([
        "Carro FCHP20505 (1280 × 610 mm, W-MAN 6) o carro de 12 cajones (1200 × 800 mm, W-MAN 2), en violeta.",
        "PU-K, PU-CU, PU-FO cúpulas y fondos (W-MAN 3); PU-T tramos de 1 kg (W-MAN 2); PU-D, PU-V1 a V3 y PU-FX",
        "cuerpos (W-MAN 6 y 7); PU-CC2 y PU-CC cúpulas con cuello (W-MAN 8); PU-E, PU-B (W-MAN 9 y 10); PU-S y PU-RT",
        "(W-MAN 12); PU-6 y PU-7 (W-MAN 13 y 14); PU-CO (W-MAN 16); PU-TP y PU-F1 a F5 (W-MAN 18 a 24).",
    ], 2.0)
    c.titulo("Notas", 3.0)
    c.parrafo([
        "Corte de chapa común (C-02): la mesa elevadora mira al pasillo principal; la zona trasera entrega los",
        "desarrollos de manuales hacia el norte (C-02N) y los cuerpos de carros al marcado (2.1, pegado a la rampa).",
        "Corte de tubo norte-sur: el cajón del atado mira al pasillo AL-A, frente al cantiléver (atado con la pluma).",
        "Desbobinador contra AL-A (bobina con el espolón). Contenedores de scrap del corte y del láser contra AL-A.",
        "Granalladora Airblast G-100: los rodillos de entrada y salida están dentro de los 4,5 m (cotización).",
        "Pintura: cuelgue al norte desde la detección y descarga al sur hacia la terminación (riel en lazo).",
        "Carros 11 y 12 sobre el pasillo principal: el camión de la pintura carga y descarga por P4 (W-CAR 11).",
        "Sin medida en ningún presupuesto (criterio, marcado): desbobinador, alimentador Cena PRE-1, soldadora",
        "circunferencial FS-SWH, jaulas, estación de big bag; armadora de cajas sin cotizar (referencia FS-DDP50).",
    ], 2.0)
    return h


# ================================================================ FL_PI10_03 circulación y flujos
def _p(cod):
    z = next((q for q in M.ZONAS if q.cod == cod), None)
    return z.rect.c


FLUJOS = [
    # materia prima (autoelevador)
    ("MP", [(-6.0, 16.0), (3.7, 16.0), (3.7, 30.0)], "MP a racks (AL-B)"),
    ("MP", [(3.7, 16.0), (12.9, 16.0), (12.9, 44.5)], "Chapa, atados y bobinas (AL-A)"),
    ("MP", [(4.2, 16.0), (4.2, 13.6)], "Cuarentena"),
    ("MP", [(12.9, 16.6), (18.3, 16.6), (18.3, 19.9)], "Chapa a la guillotina"),
    ("MP", [(12.9, 33.0), (15.4, 33.0)], "Atado"),
    ("MP", [(12.9, 43.3), (15.5, 43.3)], "Bobina"),
    ("MP", [(15.4, 13.6), (15.4, 14.6), (50.2, 14.6), (50.2, 13.6)], "Big bag"),
    ("MP", [(50.2, 14.6), (65.0, 14.6), (65.0, 19.9)], "Big bag"),
    ("MP", [(21.3, 16.0), (21.3, 13.6)], "Fleje y polvo"),
    # manuales (semielaborado)
    ("SE", [(21.6, 42.3), (31.4, 42.3)], "Cúpulas"),
    ("SE", [(32.4, 41.5), (32.4, 40.0), (34.6, 40.0), (34.6, 37.0)], ""),
    ("SE", [(24.5, 41.1), (24.5, 38.9)], "Fondos"),
    ("SE", [(16.8, 36.2), (16.8, 37.6), (21.5, 37.6)], "Tramos 1 kg"),
    ("SE", [(19.0, 27.4), (19.0, 31.6), (30.2, 31.6), (30.2, 34.0), (22.1, 34.0), (22.1, 37.3)], "Cuerpos 2,5 a 10 kg"),
    ("SE", [(22.7, 38.0), (28.4, 38.0)], ""),
    ("SE", [(30.2, 38.0), (31.8, 38.0), (31.8, 36.0)], ""),
    ("SE", [(33.6, 36.0), (36.0, 36.0), (36.0, 40.0), (38.2, 40.0), (38.2, 42.2)], ""),
    ("SE", [(39.4, 42.2), (64.8, 42.2), (66.4, 43.0)], "Soldados -> espesor -> PH -> secado -> granallado -> detección"),
    ("SE", [(66.4, 28.0), (65.2, 28.6), (59.6, 28.6), (59.6, 23.0), (61.4, 23.0), (62.5, 22.0), (62.5, 21.4)],
     "Terminación"),
    ("PT", [(62.5, 20.0), (62.5, 16.4), (71.0, 16.4), (71.0, 13.6)], "PT de manuales"),
    ("PT", [(71.0, 16.4), (76.6, 16.4)], "P4"),
    # carros
    ("SE", [(20.6, 25.8), (22.3, 27.0), (24.0, 26.6), (24.0, 23.0), (26.6, 22.9), (32.3, 26.0), (32.3, 23.0),
            (34.8, 22.4), (39.6, 22.4), (46.0, 22.4), (48.8, 22.6), (53.0, 25.6), (53.3, 21.2)], "Carros"),
    ("SE", [(38.5, 26.6), (38.5, 24.6)], "Cúpula con cupla"),
    ("SE", [(47.0, 25.4), (47.0, 24.6)], "Kits"),
    ("SE", [(53.3, 20.0), (53.3, 15.2), (64.5, 15.2), (64.5, 13.6)], "Secos al pulmón de despacho"),
    ("SE", [(66.0, 13.6), (66.0, 15.2), (76.6, 15.2)], "A la pintura (P4)"),
    ("SE", [(76.6, 17.6), (58.3, 17.6), (58.3, 13.6)], "Pintados (P4)"),
    ("SE", [(56.0, 9.0), (49.0, 9.0), (46.0, 6.0), (42.2, 6.0)], "Carga y pérdidas"),
    ("SE", [(43.0, 4.5), (43.0, 3.3)], "Muestra"),
    ("SE", [(42.2, 9.0), (42.2, 11.5), (33.0, 11.5)], "Etiquetado -> depósito"),
    ("PT", [(29.0, 8.0), (27.7, 3.5), (27.7, -1.0)], "Despacho de carros (P2)"),
]
HILOS = [
    [(47.7, M.YA0 + 2.0), (47.7, 46.2), (47.7, 45.6), (36.0, 45.6), (36.0, 20.0), (36.0, 19.2)],
    [(36.0, 19.2), (36.0, 13.5)],
    [(47.7, 45.6), (58.0, 45.6), (58.0, 19.2)],
    [(20.3, M.YA0 + 1.0), (20.3, 46.0)],
    [(25.2, M.YA0 + 1.0), (25.2, 46.0)],
]


def fl_03(doc, ox):
    h = hoja(doc, "A0", ox, "Circulación y flujos", "Layout 2035 v10 - pasillos, materiales y personas",
             "FL_PI10_03", 3, 5, "1:100", "Plano de circulación")
    pl = D.Plano(h, 100, (-8.0, -6.0), (h.fx0 + 12, h.fy0 + 150))
    titulo_hoja(pl, h, "FL_PI10_03 - CIRCULACIÓN, FLUJOS DE MATERIALES Y RECORRIDOS DEL PERSONAL",
                "Carriles del autoelevador, sendas peatonales y pasillos de operarios con su ancho; flujo de MP, de "
                "semielaborado y de PT; hilos del personal desde los vestuarios.")
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
    c = Col(pl, h.fx0 + 850, h.fy1 - 30)
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
        "Un solo autoelevador (Heli CPCD50, W-MAN y W-CAR): circula sólo por A2, AL-A y AL-B (5,0 m) y entra a los",
        "puestos únicamente donde la máquina mira al carril: mesa elevadora, cajón del atado, desbobinador,",
        "contenedores de scrap, big bags (terminación y carro 13), envolvedora, calles de PT y carros 11 y 12.",
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


def fl_04(doc, ox):
    h = hoja(doc, "A0", ox, "Almacén de MP y recepción", "Layout 2035 v10 - X-ALM v5 con el autoelevador de W-CAR",
             "FL_PI10_04", 4, 5, "1:50", "Plano de detalle")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI10_04 - ALMACÉN DE MATERIA PRIMA, RECEPCIÓN Y LOCALES DEL "
                "ÁNGULO SUDOESTE", "Racks, cantiléver, chapa y fleje con su posición; cuarentena de W-CAR (7 pallets).")

    def dib(pl):
        base(pl, rot_eq=True, h_eq=1.2, h_z=2.2)
        cotas_alm(pl)

    win1 = (-1.0, 18.0, 16.0, 48.0)
    pl1 = D.Plano(h, 50, (win1[0], win1[1]), (h.fx0 + 15, h.fy0 + 25))
    _ventana(pl1, win1, dib)
    pl1.texto("Almacén de MP (x 0 a 15,4; y 20 a 47)", pl1.P(win1[0], win1[3]), 4.0, A.BOTTOM_LEFT, papel=True)
    win2 = (-1.0, -1.0, 26.0, 14.0)
    pl2 = D.Plano(h, 50, (win2[0], win2[1]), (h.fx0 + 400, h.fy0 + 490))
    _ventana(pl2, win2, dib)
    pl2.texto("Recepción, cuarentena, polvo, fleje y locales del ángulo SO (x 0 a 24,7; y 0 a 13,5)",
              pl2.P(win2[0], win2[3]), 4.0, A.BOTTOM_LEFT, papel=True)
    c = Col(pl2, h.fx0 + 400, h.fy0 + 470)
    filas = [
        ["Rack R1 + R2", "128 posiciones (16 módulos de 2,7 m × 4 niveles × 2 pallets)", "128 pos.", "X-ALM"],
        ["Hojas de manuales", "7 pilas (5 de 1000 × 2000, 1 de 1220 × 2440, 1 de 1500 × 3000)", "17,5 m²", "X-ALM P02-P04"],
        ["Calle de chapa de carros", "3 posiciones de 3,0 × 1,5 m, 2 paquetes de alto", "9,0 m²", "W-CAR 1 / X-ALM"],
        ["Cantiléver", "frente de 12,4 m, 5 niveles, brazos de 1,2 m", "11 pos.", "X-ALM"],
        ["Bobinas de fleje", "21 posiciones en 7 calles de 3 (pallet en piso, 1 nivel)", "25,2 m²", "X-ALM P05-P11"],
        ["Polvo químico y pintura", "rack pesado de big bags + pallets, local cerrado", "8,4 m²", "X-ALM"],
        ["Identificación", "estantería de 5 niveles bajo llave", "3,0 m²", "X-ALM"],
        ["Cuarentena", "7 posiciones de pallet en fila sobre el pasillo principal", "8,4 m²", "W-CAR 1"],
        ["Retenidos de MP", "3 pallets en jaula roja", "3,6 m²", "W-CAR 1"],
        ["Recepción", "balanza 1,20 × 1,20 m y mesa de inspección 1,2 × 0,6 m", "6,8 m²", "W-MAN 1 / W-CAR 1"],
        ["Carros de abastecimiento", "2 carros FCEP10520 (3 × 1 m)", "3,0 m²", "W-CAR 1"],
        ["Jaula de gases (exterior)", "packs de Arcal 21 y de N₂ con manifold, al sur", "10,5 m²", "X-ALM"],
    ]
    c.tabla([("Sección", 50, "l"), ("Cómo se guarda", 150, "l"), ("Neto", 22, "r"), ("Fuente", 36, "l")], filas, 5.0,
            2.5, "Almacenamiento (medida neta de la fuente)")
    c.parrafo([
        "Pasillos de 5,0 m para el Heli CPCD50 (W-CAR); X-ALM supone circulación × 1,5 sin layout. Con el",
        "autoelevador real la circulación es mayor, pero AL-A sirve además a las tres máquinas que se cargan con",
        "autoelevador (mesa elevadora, cajón del atado y desbobinador). Revendidos, embalaje e insumos de las dos líneas",
        "van en los racks. El procesado y los insumos de recargas de X-ALM no van (tabla de áreas v10).",
        "Paquetes de chapa y atados se controlan en su lugar del almacén con tarjeta de cuarentena (W-MAN 1).",
    ], 2.6)
    return h


def cotas_alm(pl):
    pl.cadena([0, 1.2, 6.2, 7.3, 10.4, 15.4], 47.0, 6.0, True)
    pl.cadena([20.0, 30.8, 33.6, 47.0], 0.0, -6.0, False)
    pl.cadena([0, 8.0, 9.5, 12.8, 13.0, 17.8, 24.7], 0.0, -4.0, True)
    pl.cadena([0, 8.4, 9.9, 13.5, 18.5, 20.0], 0.0, -8.0, False)


# ================================================================ FL_PI10_05 administración
def fl_05(doc, ox):
    h = hoja(doc, "A0", ox, "Administración y servicios al personal",
             "Layout 2035 v10 - dotación de la X-DT sin recargas", "FL_PI10_05", 5, 5, "1:50", "Plano de detalle")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI10_05 - ADMINISTRACIÓN Y SERVICIOS AL PERSONAL (ANEXO NORTE)",
                "Locales dimensionados con la dotación 2035 sin recargas (X-DT); sanitarios por el Dec. 351/79 art. 49 "
                "con las fórmulas de la X-DT.")
    win = (15.0, 43.0, 54.0, 61.0)
    pl = D.Plano(h, 50, (win[0], win[1]), (h.fx0 + 15, h.fy0 + 380))

    def dib(p):
        zonas(p, lista=M.ADMIN, h=2.4, areas=True)
        zonas(p, h=2.4, areas=False)
        tabiques(p, M.ADMIN, 0.10)
        pasillos(p, h=2.0)
        equipos(p, rotulos=False, win=win)
        muebles(p)
        muros(p)
        puertas(p, h=2.2)
        p.cadena([z.rect.x0 for z in M.ADMIN if z.rect.y0 < M.YA0 + 0.1] + [M.XA1], M.YA0, -9.0, True)
        p.cadena([z.rect.x0 for z in M.ADMIN if z.rect.y1 > M.YA1 - 0.1] + [M.XA1], M.YA1, 4.0, True)
        p.cadena([M.YA0, M.Y_PC0, M.Y_PC1, M.YA1], M.XA1, 5.0, False)

    _ventana(pl, win, dib)
    c = Col(pl, h.fx0 + 15, h.fy0 + 350)
    filas = [["Turno mañana: operarios de producción", "30", "X-DT Dotación: 46 − 16 de recargas"],
             ["Turno mañana: encargado de turno", "1", "X-DT Servicios y Oficinas fila 35"],
             ["Turno mañana: oficina (jefe de planta, calidad, ventas y cobranzas, compras, PCP)", "5",
              "X-DT filas 21 a 26, sin «atención de recargas»"],
             ["Turno tarde: operarios de producción", "6", "X-DT Dotación fila 104"],
             ["Turno tarde: encargado y administrativo", "2", "X-DT filas 27 y 39"],
             ["Turno más numeroso (mañana): 32 varones y 4 mujeres", "36", "10 % de mujeres, redondeado arriba (X-DT)"],
             ["Personal de planta en los dos turnos (armarios): 34 varones y 4 mujeres", "38", "Operarios + encargados"]]
    c.tabla([("Dotación 2035 sin recargas", 190, "l"), ("Personas", 22, "r"), ("Fuente", 110, "l")], filas, 5.2, 2.6,
            "Dotación")
    c2 = Col(pl, h.fx0 + 360, h.fy0 + 350)
    filas = [["Inodoros", "2", "2", "1", "1"], ["Orinales", "3", "3", "-", "-"], ["Lavabos", "4", "4", "1", "1"],
             ["Duchas", "3", "3", "1", "1"], ["Armarios dobles", "34", "34", "4", "4"]]
    c2.tabla([("Artefacto", 50, "l"), ("Pide H", 22, "r"), ("Hay H", 22, "r"), ("Pide M", 22, "r"),
              ("Hay M", 22, "r")], filas, 5.2, 2.6, "Sanitarios y vestuarios (Dec. 351/79 art. 49, fórmulas X-DT)")
    c2.parrafo([
        "Comedor: 36 personas del turno mañana en 2 tandas de 30 minutos = 18 plazas (3 mesas de 6, X-DT).",
        "Oficinas: 6 puestos (X-DT celda B9): jefatura (1), sala técnica (calidad, PCP y encargado: 3),",
        "administración (ventas y cobranzas, compras; el administrativo de la tarde comparte escritorio: 2).",
        "No se agregan gerencia ni RRHH: la X-DT no tiene esos puestos.",
        "Accesos separados: visitas y oficinas por el hall (norte, rampa accesible); operarios por el vestíbulo",
        "lateral (reloj) -> vestuarios -> paso de personal -> planta (PN-3). Sala técnica y primeros auxilios",
        "con puerta directa a la senda norte de la planta (PN-1 y PN-2); pañol de EPP con ventanilla.",
    ], 2.6)
    return h
