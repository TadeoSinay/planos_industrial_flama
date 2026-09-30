"""Dibujo de planta a escala sobre una lámina IRAM (espacio modelo en mm de papel).

Plano(hoja, k, (wx0, wy0), (px0, py0)) transforma coordenadas del modelo en metros a mm de papel:
    papel = origen_papel + (mundo - origen_mundo) · 1000 / k
"""

import math
import shapely.geometry as sg
from shapely.ops import unary_union
from ezdxf.enums import TextEntityAlignment

from . import layout as L

A = TextEntityAlignment

# capas del plano de planta: (ACI, espesor 1/100 mm, tipo de línea, rgb o None, descripción)
CAPAS_PLANTA = {
    "A-MURO": (7, 50, "CONTINUOUS", None, "Muros y cerramientos (línea gruesa, relleno)"),
    "A-COLUMNA": (7, 50, "CONTINUOUS", None, "Columnas"),
    "A-EJE": (1, 18, "IRAM-F-TRAZO-PUNTO", None, "Ejes estructurales"),
    "A-ABERTURA": (7, 25, "CONTINUOUS", None, "Puertas, portones y muelles"),
    "A-EQUIPO": (7, 35, "CONTINUOUS", None, "Equipos (contorno)"),
    "A-EQUIPO-FINO": (8, 13, "CONTINUOUS", None, "Detalle de equipos, racks y carros"),
    "A-SECTOR": (8, 18, "IRAM-E-TRAZOS", None, "Límite de sector"),
    "A-PASILLO": (2, 35, "CONTINUOUS", (215, 165, 0), "Demarcación de pasillos (amarillo IRAM 10005)"),
    "A-SENDA": (2, 25, "CONTINUOUS", (215, 165, 0), "Sendas peatonales (cebra)"),
    "A-TEXTO": (7, 18, "CONTINUOUS", None, "Textos"),
    "A-RELLENO": (9, 13, "CONTINUOUS", None, "Rellenos de sectores"),
    "A-COTA": (7, 18, "CONTINUOUS", None, "Cotas IRAM 4513"),
    "A-EXTERIOR": (8, 25, "CONTINUOUS", None, "Terreno, calles, playas y veredas"),
    "A-LOCAL": (7, 25, "CONTINUOUS", None, "Tabiques de locales de servicio"),
    "A-SANITARIO": (8, 13, "CONTINUOUS", None, "Artefactos sanitarios y mobiliario"),
    "F-MP": (5, 70, "CONTINUOUS", None, "Flujo de materia prima (azul)"),
    "F-SE": (30, 70, "CONTINUOUS", None, "Flujo de semielaborado (naranja)"),
    "F-TL": (30, 100, "CONTINUOUS", None, "Tren logístico de un sentido (SE)"),
    "F-PT": (3, 70, "CONTINUOUS", None, "Flujo de producto terminado (verde)"),
    "F-SCRAP": (8, 50, "IRAM-F-TRAZO-PUNTO", None, "Scrap y retal (gris)"),
    "F-PERSONAL": (6, 35, "FLUJO-TRAZOS", None, "Hilos de personal (magenta)"),
    "F-EFL-LIQ": (34, 35, "FLUJO-TRAZOS", None, "Efluentes líquidos (marrón)"),
    "F-EFL-GAS": (4, 35, "FLUJO-TRAZOS", None, "Efluentes gaseosos (cian)"),
    "F-RET": (8, 18, "FLUJO-TRAZOS", None, "Retorno vacío del tren logístico"),
    "I-ELEC": (1, 35, "CONTINUOUS", None, "Alimentadores eléctricos"),
    "I-AIRE": (4, 35, "CONTINUOUS", None, "Aire comprimido"),
    "I-N2": (6, 35, "CONTINUOUS", None, "Nitrógeno"),
    "I-GAS": (40, 35, "CONTINUOUS", None, "Gas natural"),
    "I-SOLD": (211, 35, "CONTINUOUS", None, "Gas de soldadura Ar/CO₂"),
    "S-INCENDIO": (1, 25, "CONTINUOUS", None, "Extintores y protección contra incendio"),
    "S-ESCAPE": (3, 35, "CONTINUOUS", None, "Medios de escape y salidas"),
}

COLOR_FLUJO = {"MP": "F-MP", "SE": "F-SE", "PT": "F-PT", "SCRAP": "F-SCRAP", "PER": "F-PERSONAL",
               "EFL-L": "F-EFL-LIQ", "EFL-G": "F-EFL-GAS", "TL": "F-TL", "RET": "F-RET"}
RGB_FLUJO = {"MP": (0, 70, 200), "SE": (235, 120, 0), "PT": (0, 150, 60), "SCRAP": (120, 120, 120),
             "PER": (200, 0, 170), "EFL-L": (140, 80, 30), "EFL-G": (0, 170, 200), "TL": (235, 120, 0),
             "RET": (150, 150, 150)}

RELLENO = {  # color de fondo por categoría de sector (suave, para los planos de flujo)
    "MP": (205, 225, 245), "PROD": (253, 228, 200), "PINT": (250, 215, 205), "TERM": (215, 238, 210),
    "PT": (200, 232, 200), "CAL": (228, 225, 240), "AUX": (232, 232, 232), "SERV": (255, 248, 205),
    "RC": (240, 225, 195), "CIRC": (245, 245, 245),
}


def capas_planta(doc):
    if "FLUJO-TRAZOS" not in doc.linetypes:
        doc.linetypes.add("FLUJO-TRAZOS", pattern=[4.0, 2.5, -1.5], description="Trazos de flujo __ __ __")
    for n, (c, lw, lt, rgb, desc) in CAPAS_PLANTA.items():
        if n in doc.layers:
            continue
        ly = doc.layers.add(n, color=c, lineweight=lw, linetype=lt)
        if rgb:
            ly.rgb = rgb
        ly.description = desc


class Plano:
    def __init__(self, hoja, k, mundo0, papel0):
        self.h = hoja
        self.m = hoja.msp
        self.k = k
        self.s = 1000.0 / k
        self.w0 = mundo0
        self.p0 = papel0

    # ------------------------------------------------------------ transformación
    def P(self, x, y):
        return (self.p0[0] + (x - self.w0[0]) * self.s, self.p0[1] + (y - self.w0[1]) * self.s)

    def Ps(self, pts):
        return [self.P(x, y) for x, y in pts]

    def mm(self, metros):
        return metros * self.s

    # ------------------------------------------------------------ primitivas
    def pl(self, pts, capa, cerrada=False, **kw):
        at = {"layer": capa}
        at.update(kw)
        return self.m.add_lwpolyline(self.Ps(pts), close=cerrada, dxfattribs=at)

    def rect(self, r, capa, **kw):
        return self.pl(r.pts(), capa, True, **kw)

    def relleno(self, pts, rgb, capa="A-RELLENO"):
        h = self.m.add_hatch(dxfattribs={"layer": capa})
        h.set_solid_fill(rgb=rgb)
        h.paths.add_polyline_path(self.Ps(pts), is_closed=True)
        return h

    def rayado(self, pts, capa="A-RELLENO", esp=1.5, ang=45, rgb=None):
        h = self.m.add_hatch(dxfattribs={"layer": capa})
        h.set_pattern_fill("ANSI31", scale=esp / 3.175, angle=ang)
        if rgb:
            h.rgb = rgb
        h.paths.add_polyline_path(self.Ps(pts), is_closed=True)
        return h

    def texto(self, s, xy, h=2.5, al=A.MIDDLE_CENTER, capa="A-TEXTO", rot=0, papel=False):
        p = xy if papel else self.P(*xy)
        t = self.m.add_text(s, height=h, rotation=rot, dxfattribs={"layer": capa, "style": "ISO3098"})
        t.set_placement(p, align=al)
        return t

    def linea(self, a, b, capa):
        return self.m.add_line(self.P(*a), self.P(*b), dxfattribs={"layer": capa})

    def circulo(self, c, r, capa):
        return self.m.add_circle(self.P(*c), r * self.s, dxfattribs={"layer": capa})

    def arco(self, c, r, a0, a1, capa):
        return self.m.add_arc(self.P(*c), r * self.s, a0, a1, dxfattribs={"layer": capa})

    def punta(self, tip, d, largo=3.0, ancho=1.4, rgb=(0, 0, 0), capa="A-TEXTO", papel=False):
        """Punta de flecha llena (mm de papel)."""
        tp = tip if papel else self.P(*tip)
        px, py = -d[1], d[0]
        b = (tp[0] - d[0] * largo, tp[1] - d[1] * largo)
        pts = [tp, (b[0] + px * ancho / 2, b[1] + py * ancho / 2), (b[0] - px * ancho / 2, b[1] - py * ancho / 2)]
        h = self.m.add_hatch(dxfattribs={"layer": capa})
        h.set_solid_fill(rgb=rgb)
        h.paths.add_polyline_path(pts, is_closed=True)

    def flujo(self, pts, cat, cada=40.0, largo=3.2, ancho=1.6, rotulo=None, h_txt=1.8, fin=True):
        """Polilínea de flujo con puntas intermedias cada `cada` mm de papel y punta final."""
        capa = COLOR_FLUJO[cat]
        rgb = RGB_FLUJO[cat]
        self.pl(pts, capa)
        pp = self.Ps(pts)
        acum = 0.0
        for a, b in zip(pp, pp[1:]):
            L_ = math.dist(a, b)
            if L_ < 1e-6:
                continue
            d = ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_)
            s = cada - acum
            while s < L_ - largo * 1.5:
                tip = (a[0] + d[0] * (s + largo / 2), a[1] + d[1] * (s + largo / 2))
                self.punta(tip, d, largo, ancho, rgb, capa, papel=True)
                s += cada
            acum = (acum + L_) % cada
        if fin and len(pp) >= 2:
            a, b = pp[-2], pp[-1]
            L_ = math.dist(a, b)
            if L_ > 1e-6:
                self.punta(b, ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_), largo, ancho, rgb, capa, papel=True)
        if rotulo:
            i = max(range(len(pp) - 1), key=lambda j: math.dist(pp[j], pp[j + 1]))
            a, b = pp[i], pp[i + 1]
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            if ang > 90 or ang < -90:
                ang += 180
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            n = (-(b[1] - a[1]) / math.dist(a, b), (b[0] - a[0]) / math.dist(a, b))
            if n[1] < 0 or (abs(n[1]) < 1e-6 and n[0] < 0):
                n = (-n[0], -n[1])
            self.texto(rotulo, (mid[0] + n[0] * 1.6, mid[1] + n[1] * 1.6), h_txt, A.BOTTOM_CENTER, capa, ang,
                       papel=True)

    # ------------------------------------------------------------ cotas
    def cota(self, a, b, desplaz, horizontal=True, texto=None):
        """Cota lineal en metros con 2 decimales (DIMLFAC = k/1000)."""
        p1, p2 = self.P(*a), self.P(*b)
        if horizontal:
            base = (p1[0], p1[1] + desplaz)
            ang = 0
        else:
            base = (p1[0] + desplaz, p1[1])
            ang = 90
        ov = {"dimlfac": self.k / 1000.0, "dimdec": 2, "dimzin": 0, "dimtxt": 2.2, "dimasz": 2.2,
              "dimexe": 1.2, "dimexo": 1.0}
        d = self.m.add_linear_dim(base=base, p1=p1, p2=p2, angle=ang, dimstyle="FLAMA-IRAM", override=ov,
                                  text=texto if texto else "<>", dxfattribs={"layer": "A-COTA"})
        d.render()
        return d

    def cadena(self, xs, y_ref, desplaz, horizontal=True):
        """Cadena de cotas entre posiciones consecutivas (x para horizontal, y para vertical)."""
        xs = sorted(set(round(v, 3) for v in xs))
        for a, b in zip(xs, xs[1:]):
            if b - a < 0.05:
                continue
            if horizontal:
                self.cota((a, y_ref), (b, y_ref), desplaz, True)
            else:
                self.cota((y_ref, a), (y_ref, b), desplaz, False)

    # ------------------------------------------------------------ tablas en papel
    def tabla(self, x0, y_top, cols, filas, h_fila=4.2, h_txt=2.0, titulo=None, h_tit=3.0, capa="A-TEXTO"):
        """cols: [(encabezado, ancho_mm, 'l'|'c'|'r')]; filas: listas de str. Devuelve y inferior."""
        m = self.m
        W = sum(c[1] for c in cols)
        y = y_top
        if titulo:
            self.texto(titulo, (x0, y + 1.5), h_tit, A.BOTTOM_LEFT, capa, papel=True)
        filas_all = [[c[0] for c in cols]] + filas
        n = len(filas_all)
        y_bot = y - n * h_fila
        m.add_lwpolyline([(x0, y), (x0 + W, y), (x0 + W, y_bot), (x0, y_bot)], close=True,
                         dxfattribs={"layer": "A-COTA", "lineweight": 35})
        for i in range(1, n):
            yy = y - i * h_fila
            m.add_line((x0, yy), (x0 + W, yy), dxfattribs={"layer": "A-COTA", "lineweight": 35 if i == 1 else 13})
        xx = x0
        for c in cols[:-1]:
            xx += c[1]
            m.add_line((xx, y), (xx, y_bot), dxfattribs={"layer": "A-COTA", "lineweight": 13})
        for i, fila in enumerate(filas_all):
            yy = y - (i + 0.5) * h_fila
            xx = x0
            for (enc, w, al), val in zip(cols, fila):
                s = str(val)
                hh = h_txt
                while len(s) * hh * 0.62 > w - 1.2 and hh > 1.3:
                    hh -= 0.1
                if al == "l":
                    self.texto(s, (xx + 0.8, yy), hh, A.MIDDLE_LEFT, capa, papel=True)
                elif al == "r":
                    self.texto(s, (xx + w - 0.8, yy), hh, A.MIDDLE_RIGHT, capa, papel=True)
                else:
                    self.texto(s, (xx + w / 2, yy), hh, A.MIDDLE_CENTER, capa, papel=True)
                xx += w
        return y_bot

    def parrafo(self, lineas, x0, y_top, h=2.2, interl=1.55, capa="A-TEXTO"):
        y = y_top
        for ln in lineas:
            self.texto(ln, (x0, y), h, A.TOP_LEFT, capa, papel=True)
            y -= h * interl
        return y


# ================================================================ elementos de la planta
def muros(pl, detalle=True):
    """Cerramiento de la nave (0,20 m por fuera de la cara de columnas) con los vanos de puertas y los
    muros de los anexos."""
    e = L.MURO
    X, Y = L.NAVE_L, L.NAVE_A
    ext = sg.box(-0.2 - e, -0.2 - e, X + 0.2 + e, Y + 0.2 + e)
    inn = sg.box(-0.2, -0.2, X + 0.2, Y + 0.2)
    anillo = ext.difference(inn)
    vanos = []
    for p in L.PUERTAS:
        if p.muro == "N":
            vanos.append(sg.box(p.a, Y - 1, p.b, Y + 1))
        elif p.muro == "S":
            vanos.append(sg.box(p.a, -1, p.b, 1))
        elif p.muro == "O":
            vanos.append(sg.box(-1, p.a, 1, p.b))
        elif p.muro == "E":
            vanos.append(sg.box(X - 1, p.a, X + 1, p.b))
    anillo = anillo.difference(unary_union(vanos))
    # anexos: muros de 0,20 m (medianeros con la nave: se usa el cerramiento de la nave)
    for s in L.ANEXOS:
        r = s.rect
        a_ext = sg.box(r.x0 - 0.1, r.y0 - 0.1, r.x1 + 0.1, r.y1 + 0.1)
        a_in = sg.box(r.x0 + 0.1, r.y0 + 0.1, r.x1 - 0.1, r.y1 - 0.1)
        anillo = anillo.union(a_ext.difference(a_in).difference(sg.box(-1, -0.25, X + 1, Y + 1)))
    vanos2 = []
    for cod, a, b, tipo, uso in L.PUERTAS_ANEXOS:
        if abs(a[0] - b[0]) < 1e-6:
            vanos2.append(sg.box(a[0] - 0.4, min(a[1], b[1]), a[0] + 0.4, max(a[1], b[1])))
        else:
            vanos2.append(sg.box(min(a[0], b[0]), a[1] - 0.4, max(a[0], b[0]), a[1] + 0.4))
    anillo = anillo.difference(unary_union(vanos2))
    for g in (anillo.geoms if hasattr(anillo, "geoms") else [anillo]):
        pts = list(g.exterior.coords)[:-1]
        h = pl.m.add_hatch(dxfattribs={"layer": "A-MURO"})
        h.set_solid_fill(rgb=(70, 70, 70))
        h.paths.add_polyline_path(pl.Ps(pts), is_closed=True)
        for it in g.interiors:
            h.paths.add_polyline_path(pl.Ps(list(it.coords)[:-1]), is_closed=True, flags=0)
        pl.pl(pts, "A-MURO", True)
    # columnas
    c = L.COL / 2
    for x in L.EJES_X:
        for y in L.EJES_Y:
            q = [(x - c, y - c), (x + c, y - c), (x + c, y + c), (x - c, y + c)]
            pl.relleno(q, (0, 0, 0), "A-COLUMNA")
    # columnas de frontis cada 6 m en los testeros
    for x in (0.0, L.NAVE_L):
        for y in (6.0, 12.0, 18.0, 24.0, 30.0):
            q = [(x - 0.15, y - 0.15), (x + 0.15, y - 0.15), (x + 0.15, y + 0.15), (x - 0.15, y + 0.15)]
            pl.relleno(q, (0, 0, 0), "A-COLUMNA")


def ejes(pl, r_glob=4.0, sobresale=6.0, cotas=True, completo=True):
    """Ejes estructurales con globos (números en X, letras en Y). completo=False: sólo marcas en el
    borde norte (planos de flujo)."""
    X, Y = L.NAVE_L, L.NAVE_A
    rg = r_glob / pl.s
    if not completo:
        for i, x in enumerate(L.EJES_X):
            pl.linea((x, Y + 0.4), (x, Y + sobresale), "A-EJE")
            pl.circulo((x, Y + sobresale + rg), rg, "A-EJE")
            pl.texto(str(i + 1), (x, Y + sobresale + rg), r_glob * 0.9, A.MIDDLE_CENTER, "A-TEXTO")
        return
    for i, x in enumerate(L.EJES_X):
        pl.linea((x, -sobresale), (x, Y + sobresale), "A-EJE")
        for yy, sg_ in ((Y + sobresale + rg, 1), (-sobresale - rg, -1)):
            pl.circulo((x, yy), rg, "A-EJE")
            pl.texto(str(i + 1), (x, yy), r_glob * 0.9, A.MIDDLE_CENTER, "A-TEXTO")
    for j, y in enumerate(L.EJES_Y):
        pl.linea((-sobresale, y), (X + sobresale, y), "A-EJE")
        for xx in (-sobresale - rg, X + sobresale + rg):
            pl.circulo((xx, y), rg, "A-EJE")
            pl.texto("AB"[j], (xx, y), r_glob * 0.9, A.MIDDLE_CENTER, "A-TEXTO")


def puertas(pl, etiquetas=True, h=1.8):
    X, Y = L.NAVE_L, L.NAVE_A
    for p in L.PUERTAS:
        a, b = p.a, p.b
        w = b - a
        if p.muro in ("N", "S"):
            y = Y + 0.3 if p.muro == "N" else -0.3
            sgn = 1 if p.muro == "N" else -1
            if p.tipo in ("emergencia", "peatonal"):
                # hoja que abre hacia afuera (emergencia) o hacia el pasillo
                piv = (a, y)
                pl.linea(piv, (a, y + sgn * w), "A-ABERTURA")
                pl.arco(piv, w, 0 if sgn > 0 else 270, 90 if sgn > 0 else 360, "A-ABERTURA")
            else:
                pl.linea((a, y), (b, y), "A-ABERTURA")
                pl.linea((a, y + sgn * 0.6), (b, y + sgn * 0.6), "A-ABERTURA")
            if etiquetas:
                pl.texto(p.cod, ((a + b) / 2, y + sgn * (1.3 if p.tipo != "emergencia" else w + 0.9)), h,
                         A.MIDDLE_CENTER, "S-ESCAPE" if p.tipo == "emergencia" else "A-TEXTO")
        else:
            x = X + 0.3 if p.muro == "E" else -0.3
            sgn = 1 if p.muro == "E" else -1
            if p.tipo in ("emergencia", "peatonal"):
                piv = (x, a)
                pl.linea(piv, (x + sgn * w, a), "A-ABERTURA")
                pl.arco(piv, w, 0 if sgn > 0 else 90, 90 if sgn > 0 else 180, "A-ABERTURA")
            else:
                pl.linea((x, a), (x, b), "A-ABERTURA")
                pl.linea((x + sgn * 0.6, a), (x + sgn * 0.6, b), "A-ABERTURA")
            if p.tipo == "muelle":
                # rampa niveladora (2,0 × 3,0 m) dentro de la nave y sello de muelle afuera
                pl.rect(L.R(X - 3.0, a + 0.4, X - 0.2, b - 0.4), "A-ABERTURA")
                pl.rect(L.R(X + 0.2, a - 0.3, X + 0.8, b + 0.3), "A-ABERTURA")
            if etiquetas:
                pl.texto(p.cod, (x + sgn * (2.2 if p.tipo != "emergencia" else w + 1.2), (a + b) / 2), h,
                         A.MIDDLE_CENTER, "S-ESCAPE" if p.tipo == "emergencia" else "A-TEXTO")
    for cod, a, b, tipo, uso in L.PUERTAS_ANEXOS:
        if tipo == "peatonal":
            if abs(a[0] - b[0]) < 1e-6:
                w = abs(b[1] - a[1])
                pl.linea(a, (a[0] + w, a[1]), "A-ABERTURA")
                pl.arco(a, w, 0, 90, "A-ABERTURA")
            else:
                w = abs(b[0] - a[0])
                pl.linea(a, (a[0], a[1] - w), "A-ABERTURA")
                pl.arco(a, w, 270, 360, "A-ABERTURA")
        else:
            pl.linea(a, b, "A-ABERTURA")
        if etiquetas:
            off = (1.6, 0) if abs(a[0] - b[0]) < 1e-6 else (0, -1.4)
            pl.texto(cod, ((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1]), h * 0.9, A.MIDDLE_CENTER)


def equipos(pl, rotulos=True, h=1.5, fino=False):
    for e in L.EQUIPOS:
        r = e.rect
        capa = "A-EQUIPO-FINO" if fino else "A-EQUIPO"
        if e.forma == "circ":
            pl.circulo(r.c, r.w / 2, capa)
            radio = 4.0
            pl.circulo(r.c, radio, "A-EQUIPO-FINO")
        else:
            pl.rect(r, capa)
            if e.forma == "rack":
                pl.linea((r.x0, r.y0), (r.x1, r.y1), "A-EQUIPO-FINO")
                pl.linea((r.x0, r.y1), (r.x1, r.y0), "A-EQUIPO-FINO")
        if rotulos:
            rot = 90 if r.h > r.w * 1.8 else 0
            pl.texto(e.cod, r.c, h, A.MIDDLE_CENTER, "A-TEXTO", rot)


def sectores(pl, relleno=True, rotulos=True, h=2.0, areas=True, cats=None):
    for s in L.SECTORES:
        if cats and s.cat not in cats:
            continue
        if relleno:
            pl.relleno(s.rect.pts(), RELLENO.get(s.cat, (240, 240, 240)))
        pl.rect(s.rect, "A-SECTOR")
    for s in L.ANEXOS:
        if relleno and s.cod != "ST":
            pass
        if relleno and s.cod == "ST":
            pl.relleno(s.rect.pts(), RELLENO["AUX"])


def rotulos_sector(pl, h=2.0, areas=True, excluir=()):
    for s in L.SECTORES:
        if s.cod in excluir:
            continue
        r = s.rect
        x, y = r.x0 + 0.4, r.y1 - 0.4
        pl.texto(s.cod, (x, y), h, A.TOP_LEFT, "A-TEXTO")
        if areas:
            pl.texto(f"{r.area:.1f} m²".replace(".", ","), (x, y - h / pl.s * 1.5), h * 0.75, A.TOP_LEFT,
                     "A-TEXTO")


def pasillos(pl, demarcacion=True, rotulos=False, h=1.6):
    for p in L.PASILLOS:
        r = p.rect
        if demarcacion:
            pl.linea((r.x0, r.y0), (r.x1, r.y0), "A-PASILLO")
            pl.linea((r.x0, r.y1), (r.x1, r.y1), "A-PASILLO")
            pl.linea((r.x0, r.y0), (r.x0, r.y1), "A-PASILLO")
            pl.linea((r.x1, r.y0), (r.x1, r.y1), "A-PASILLO")
        if rotulos:
            rot = 90 if r.h > r.w else 0
            pl.texto(f"{p.cod} {p.ancho:.2f} m".replace(".", ","), r.c, h, A.MIDDLE_CENTER, "A-TEXTO", rot)
    for cod, r, nota in L.SENDAS:
        # cebra: franjas de 0,5 m
        x = r.x0
        while x < r.x1 - 0.1:
            pl.relleno([(x, r.y0), (x + 0.4, r.y0), (x + 0.4, r.y1), (x, r.y1)], (215, 165, 0), "A-SENDA")
            x += 0.8
        pl.texto(cod, (r.c[0], r.y1 + 0.8), h, A.MIDDLE_CENTER, "A-TEXTO")


def locales(pl, rotulos=True, h=1.6, relleno=False):
    for s in L.LOCALES:
        if relleno:
            pl.relleno(s.rect.pts(), RELLENO.get(s.cat, (240, 240, 240)))
        pl.rect(s.rect, "A-LOCAL")
        if rotulos:
            pl.texto(s.cod, s.rect.c, h, A.MIDDLE_CENTER, "A-TEXTO")


def exterior(pl, h=2.0, rotulos=True):
    x0, y0, x1, y1 = L.TERRENO
    pl.pl([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "A-EXTERIOR", True, lineweight=50)
    for cod, nom, r, tipo in L.EXTERIOR:
        if tipo == "reserva":
            pl.rayado(r.pts(), "A-EXTERIOR", 4.0, 45)
        pl.rect(r, "A-EXTERIOR")
        if rotulos:
            pl.texto(cod, r.c, h, A.MIDDLE_CENTER)


# ================================================================ recorte de una ventana de dibujo
def handles(msp):
    return {e.dxf.handle for e in msp}


def recortar(pl, antes, xa, ya, xb, yb):
    """Recorta a la ventana del modelo [xa, xb] × [ya, yb] (m) todo lo dibujado después de `antes`.
    Líneas, polilíneas y rellenos se cortan geométricamente; textos, círculos, arcos y cotas se
    conservan sólo si su punto de inserción cae dentro."""
    msp = pl.m
    p0, p1 = pl.P(xa, ya), pl.P(xb, yb)
    caja = sg.box(p0[0], p0[1], p1[0], p1[1])
    nuevos = [e for e in msp if e.dxf.handle not in antes]
    for e in nuevos:
        t = e.dxftype()
        at = {"layer": e.dxf.layer}
        for k in ("linetype", "lineweight", "color", "true_color"):
            if e.dxf.hasattr(k):
                at[k] = e.dxf.get(k)
        try:
            if t == "LINE":
                g = sg.LineString([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)])
                if caja.contains(g):
                    continue
                r = g.intersection(caja)
                for gg in _lineas(r):
                    msp.add_line(gg.coords[0], gg.coords[-1], dxfattribs=at)
                msp.delete_entity(e)
            elif t == "LWPOLYLINE":
                pts = [(p[0], p[1]) for p in e.get_points()]
                if e.closed:
                    pts.append(pts[0])
                if len(pts) < 2:
                    continue
                g = sg.LineString(pts)
                if caja.contains(g):
                    continue
                r = g.intersection(caja)
                for gg in _lineas(r):
                    msp.add_lwpolyline(list(gg.coords), dxfattribs=at)
                msp.delete_entity(e)
            elif t == "HATCH":
                polys = []
                for path in e.paths:
                    if hasattr(path, "vertices"):
                        polys.append(sg.Polygon([(v[0], v[1]) for v in path.vertices]))
                if not polys:
                    continue
                g = polys[0]
                for q in polys[1:]:
                    g = g.difference(q)
                if caja.contains(g):
                    continue
                r = g.intersection(caja)
                for gg in (r.geoms if hasattr(r, "geoms") else [r]):
                    if gg.geom_type != "Polygon" or gg.area < 1e-4:
                        continue
                    hh = msp.add_hatch(dxfattribs={"layer": e.dxf.layer})
                    if e.dxf.solid_fill:
                        if e.rgb:
                            hh.set_solid_fill(rgb=e.rgb)
                        else:
                            hh.set_solid_fill(color=e.dxf.color)
                    else:
                        hh.set_pattern_fill(e.dxf.pattern_name, scale=e.dxf.pattern_scale, angle=e.dxf.pattern_angle)
                        if e.rgb:
                            hh.rgb = e.rgb
                    hh.paths.add_polyline_path(list(gg.exterior.coords)[:-1], is_closed=True)
                    for it in gg.interiors:
                        hh.paths.add_polyline_path(list(it.coords)[:-1], is_closed=True, flags=0)
                msp.delete_entity(e)
            elif t in ("TEXT", "MTEXT"):
                p = e.dxf.align_point if (t == "TEXT" and e.dxf.hasattr("align_point")) else e.dxf.insert
                if not caja.contains(sg.Point(p.x, p.y)):
                    msp.delete_entity(e)
            elif t in ("CIRCLE", "ARC"):
                if not caja.contains(sg.Point(e.dxf.center.x, e.dxf.center.y)):
                    msp.delete_entity(e)
            elif t == "DIMENSION":
                ok = all(caja.contains(sg.Point(e.dxf.get(k).x, e.dxf.get(k).y))
                         for k in ("defpoint2", "defpoint3") if e.dxf.hasattr(k))
                if not ok:
                    msp.delete_entity(e)
        except Exception as ex:  # noqa: BLE001 - una entidad rara no debe frenar la lámina
            print("recortar:", t, ex)
            continue


def _lineas(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if hasattr(g, "geoms"):
        out = []
        for x in g.geoms:
            out += _lineas(x)
        return out
    return []
