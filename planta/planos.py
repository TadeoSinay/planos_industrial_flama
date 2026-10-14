"""Láminas de la planta industrial: FL_PI_01 a FL_PI_05."""

import math
from datetime import date

from ezdxf.enums import TextEntityAlignment

from . import layout as L
from . import calculos as C
from . import dibujo as D
from .lamina import Hoja, FORMATOS

A = TextEntityAlignment
FECHA = date.today().strftime("%d/%m/%Y")
PROYECTO = "Planta industrial de extintores FLAMA S.A. - año 10 (2035)"


def f(v, d=1):
    """número con coma decimal."""
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def hoja(doc, fmt, ox, titulo, sub, codigo, n, tot, escala, tipo="Plano de planta", material="-", unidades="Cotas en m"):
    h = Hoja(doc, fmt, ox)
    h.formato()
    h.rotulo({"titulo": titulo, "subtitulo": sub, "codigo": codigo, "hoja": n, "hojas": tot, "escala": escala,
              "material": material, "edicion": "0", "fecha": FECHA, "dibujo": "Claude Code", "reviso": "",
              "aprobo": "", "tipo_doc": tipo, "empresa": "FLAMA S.A.", "tol_titulo": "Unidades",
              "tolerancias": unidades})
    return h


def titulo_hoja(pl, h, texto, sub=None):
    pl.texto(texto, (h.fx0 + 8, h.fy1 - 8), 7.0, A.TOP_LEFT, papel=True)
    if sub:
        pl.texto(sub, (h.fx0 + 8, h.fy1 - 18), 3.5, A.TOP_LEFT, papel=True)


def leyenda_flujos(pl, x, y, cats, titulo="Referencias", w=70):
    nombres = {"MP": "MP: materia prima (azul)", "SE": "SE: semielaborado (naranja)",
               "TL": "Riel aéreo de pintura: cilindros colgados (SE)", "RET": "Retorno de ganchos vacíos del riel (aéreo)",
               "PT": "PT: producto terminado (verde)", "SCRAP": "Scrap y retal (gris)",
               "PER": "Hilos de personal (magenta)", "EFL-L": "Efluentes líquidos (marrón)",
               "EFL-G": "Emisiones gaseosas: captación y salida por techo (cian)"}
    pl.texto(titulo, (x, y), 3.5, A.BOTTOM_LEFT, papel=True)
    yy = y - 6
    for c in cats:
        pl.m.add_lwpolyline([(x, yy), (x + 16, yy)], dxfattribs={"layer": D.COLOR_FLUJO[c]})
        pl.punta((x + 16, yy), (1, 0), 3.0, 1.5, D.RGB_FLUJO[c], D.COLOR_FLUJO[c], papel=True)
        pl.texto(nombres[c], (x + 20, yy), 2.5, A.MIDDLE_LEFT, papel=True)
        yy -= 5.5
    return yy


def base_planta(pl, relleno=True, eq_rotulos=True, fino=True, ejes=True, h_eq=1.2):
    """Nave, anexos, sectores, pasillos, equipos y aberturas (fondo común de los planos de flujo)."""
    D.sectores(pl, relleno=relleno)
    D.locales(pl, rotulos=False, relleno=relleno)
    if relleno:
        for s in L.ANEXOS:
            if s.cod == "RC":
                pass
    D.pasillos(pl, demarcacion=True, h=1.6)
    D.equipos(pl, rotulos=eq_rotulos, h=h_eq, fino=fino)
    D.muros(pl)
    D.puertas(pl, etiquetas=True, h=1.6)
    if ejes:
        D.ejes(pl, r_glob=3.0, sobresale=3.0)


def emisiones(pl):
    for x, y, nom in L.EMISIONES:
        r = 0.7
        pl.circulo((x, y), r, "F-EFL-GAS")
        pl.linea((x - r * 0.7, y - r * 0.7), (x + r * 0.7, y + r * 0.7), "F-EFL-GAS")
        pl.linea((x - r * 0.7, y + r * 0.7), (x + r * 0.7, y - r * 0.7), "F-EFL-GAS")


# ================================================================ composición común de los planos de flujo
VENTANA = (L.TERRENO[0], -64.0, L.TERRENO[2], L.TERRENO[3])     # terreno completo + vereda y calle


def lamina_flujo(doc, ox, cod, titulo, denom, sub, tipo, n=1, tot=1):
    h = hoja(doc, "A0", ox, denom, sub, cod, n, tot, "1:200", tipo)
    k = 200
    x0, y0, x1, y1 = VENTANA
    alto = (y1 - y0) * 1000 / k
    pl = D.Plano(h, k, (x0, y0), (h.fx0 + 10, h.fy1 - 34 - alto))
    titulo_hoja(pl, h, titulo, "Planta industrial FLAMA S.A. - Parque Industrial Villa de Luján, Sarandí (Avellaneda) - "
                "dimensionada al año 10 (2035). Escala 1:200. Norte arriba; la calle de acceso está al sur.")
    return h, pl


def norte(pl, xy, r=3.0):
    c = pl.P(*xy)
    rr = 2 * r
    pl.m.add_circle(c, rr, dxfattribs={"layer": "A-TEXTO"})
    pts = [(c[0], c[1] + rr), (c[0] - rr * 0.35, c[1] - rr * 0.6), (c[0], c[1] - rr * 0.3)]
    hh = pl.m.add_hatch(dxfattribs={"layer": "A-TEXTO"})
    hh.set_solid_fill(rgb=(0, 0, 0))
    hh.paths.add_polyline_path(pts, is_closed=True)
    pl.m.add_lwpolyline([(c[0], c[1] + rr), (c[0] + rr * 0.35, c[1] - rr * 0.6), (c[0], c[1] - rr * 0.3)],
                        dxfattribs={"layer": "A-TEXTO"})
    pl.texto("N", (c[0], c[1] + rr + 1.5), 3.5, A.BOTTOM_CENTER, papel=True)


def sitio(pl, rotulos=True, estacionamiento=True):
    """Terreno, línea municipal, calles internas, portones, estacionamiento y elementos exteriores."""
    x0, y0, x1, y1 = L.TERRENO
    pl.pl([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "A-EXTERIOR", True, lineweight=70)
    # calle pública y vereda
    pl.linea((x0 - 2, y0 - 3.0), (x1 + 2, y0 - 3.0), "A-EXTERIOR")
    pl.texto("VEREDA", ((x0 + x1) / 2, y0 - 1.5), 2.0, A.MIDDLE_CENTER)
    pl.texto("CALLE (acceso) - Gral. Heredia, Parque Industrial Villa de Luján", ((x0 + x1) / 2 - 30, y0 - 3.8),
             2.2, A.TOP_CENTER)
    pl.linea((x0, y0 + L.RETIRO_FRENTE), (x1, y0 + L.RETIRO_FRENTE), "A-SECTOR")
    pl.texto("Retiro de frente parquizado 10 m (verificar con el reglamento del parque)", (x0 + 48, y0 + 5), 1.8,
             A.MIDDLE_CENTER)
    for r in L.CALLES:
        pl.rect(r, "A-EXTERIOR")
    pl.texto("Calle interna de camiones 7 m (sentido: entra por G1 con báscula, sale por G3)", (45.0, 59.8), 2.0,
             A.MIDDLE_CENTER)
    for cod, a, b, uso in L.PORTONES_TERRENO:
        pl.linea((a, y0), (b, y0), "A-ABERTURA")
        pl.linea((a, y0 + 0.4), (b, y0 + 0.4), "A-ABERTURA")
        if rotulos:
            pl.texto(cod, ((a + b) / 2, y0 + 1.6), 2.0, A.MIDDLE_CENTER)
    for cod, nom, r, tipo in L.EXTERIOR:
        if tipo == "reserva":
            pl.rayado(r.pts(), "A-EXTERIOR", 6.0, 45)
        pl.rect(r, "A-EXTERIOR")
        if rotulos:
            pl.texto(cod, (r.x0 + 0.5, r.y1 - 0.5), 1.6, A.TOP_LEFT)
    if estacionamiento:
        # dos filas de cocheras de 2,50 × 5,00 y calle de 6 m; 2 accesibles de 3,50 junto al camino peatonal
        est = next(r for c, n, r, t in L.EXTERIOR if c == "EST")
        xs = [est.x0 + 7.5 + 2.5 * i for i in range(19)]
        for yb, yt in ((est.y1 - 5.0, est.y1), (est.y0 + 6.0, est.y0 + 11.0)):
            for x in xs:
                pl.linea((x, yb), (x, yt), "A-EXTERIOR")
            pl.linea((xs[0], yb), (xs[-1], yb), "A-EXTERIOR")
        for x in (est.x0 + 0.5, est.x0 + 4.0, est.x0 + 7.5):
            pl.linea((x, est.y1 - 5.0), (x, est.y1), "A-EXTERIOR")
        pl.texto("2 accesibles 3,50 m", (est.x0 + 4.0, est.y1 - 2.5), 1.4, A.MIDDLE_CENTER)
        pl.texto("38 cocheras 2,50 × 5,00", est.c, 1.8, A.MIDDLE_CENTER)
        # camino peatonal desde G4 (garita) al hall de servicios (SV-1), sin cruzar calles de camiones
        pl.pl(L.CAMINO_PEATONAL, "A-PASILLO")
        pl.texto("Camino peatonal G4 -> SV-1", (L.CAMINO_PEATONAL[0][0] + 1.0, -40.0), 1.6, A.MIDDLE_LEFT, rot=90)
    pl.texto("Calle de camiones al muelle P3 (entra por G1, sale por G3)", (75.0, -12.5), 2.0,
             A.MIDDLE_CENTER)
    norte(pl, (112.0, -50.0))


def fondo(pl, relleno=True, rot_eq=True, h_eq=1.2, sitio_=True):
    """Nave, anexos, sectores, pasillos, equipos, aberturas y exterior."""
    if sitio_:
        sitio(pl)
    D.sectores(pl, relleno=relleno)
    D.locales(pl, rotulos=False, relleno=relleno)
    D.pasillos(pl, demarcacion=True, h=1.6)
    D.equipos(pl, rotulos=rot_eq, h=h_eq, fino=True)
    D.vehiculos(pl)
    D.muros(pl)
    D.puertas(pl, etiquetas=True, h=1.6)
    D.ejes(pl, r_glob=2.6, sobresale=1.6, completo=False)


class Columna:
    """Cursor para ir apilando bloques en la columna derecha de la lámina."""

    def __init__(self, h, pl, x0=None):
        self.pl = pl
        self.x = x0 if x0 is not None else pl.P(L.TERRENO[2], 0)[0] + 12
        self.y = h.fy1 - 34
        self.w = h.fx1 - 6 - self.x

    def bajar(self, d):
        self.y -= d




# ================================================================ FL_PI_03 flujo de materiales
MARCAS_03 = [
    (1, (8.5, 50.0), "MP-1 una sola recepción: alero norte -> P1 -> cuarentena AL-CU -> calles A1, A2 y A3"),
    (2, (55.0, -8.0), "MP-2 muelle P3 (7 a 10 h): polvo, pintura en polvo, embalaje y revendidos"),
    (3, (55.5, 45.8), "Gases: packs de Arcal 21 y N₂ y CO₂ de recargas en la jaula exterior JG -> reguladores CG1"),
    (4, (57.5, 3.1), "Big bags y pintura: muelle -> AT -> depósito DP -> carga, carros (PO-CN) y tolvas (PO-PI)"),
    (5, (16.0, 46.6), "Scrap: contenedor en cada puesto que lo genera -> volquete junto a P1"),
    (6, (37.5, 25.5), "SE chapa: guillotina (rampa trasera) -> cilindrado -> sold. longitudinal (FCHP)"),
    (7, (30.0, 38.3), "SE láser 1 kg: carros de cajones «en llenado» / «vacío» -> encastre"),
    (8, (40.0, 39.8), "SE embutido -> cúpulas -> muesca, numerado y soldadura de cuello -> sold. circ.; fondos al encastre"),
    (9, (57.0, 34.1), "SE línea principal: encastre -> bordoneado -> sold. circ. -> espesor -> PH -> secado -> granallado"),
    (10, (83.0, 29.0), "Riel aéreo: detección -> precalentamiento -> cabina -> curado (2 hornos) -> descarga"),
    (11, (77.5, 12.0), "Descarga: vacíos a su mesa de encajonado; terminados por PO-PI y AT2 a la carga"),
    (12, (66.0, 14.3), "Terminación: carga -> ensamblaje -> presurización -> pérdidas -> etiquetado -> encajonado"),
    (13, (30.0, 13.7), "SE carros: marcado -> U de carros (puestos 3 a 8) -> PH -> secado -> pulmón al muelle"),
    (14, (41.7, 12.5), "Carros pintados: vuelven por P3 y PO-CN a la terminación -> pulmón del muelle"),
    (15, (45.2, 13.0), "PT: envolvedora -> AT -> T2 -> racks de 5 niveles -> T1 -> EX -> muelle P3 (13 a 17 h)"),
    (16, (19.6, 13.0), "Barras de carros: cantiléver -> PC -> PO-CW -> rack del puesto 8.1"),
    (17, (73.0, -30.0), "Efluentes líquidos a tratamiento PTE y colectora"),
    (18, (-5.0, 3.0), "Recargas: P2 -> recepción -> inspección -> recinto de polvo -> PH -> armado -> despacho -> P2"),
    (19, (72.0, 41.5), "Corregidos y a re-granallar: de las jaulas vuelven a los rodillos de la granalladora"),
]


def flujos_materiales(pl):
    camion(pl, (3.5, 48.2), 18.6, "Semi 30 t", horiz=True)
    camion(pl, (3.5, 52.6), 10.0, "Chasis 16 t", horiz=True)
    camion(pl, (40.9, -20.0), 18.6, "Semi PT / chasis", horiz=False)
    camion(pl, (54.0, 48.6), 9.5, "Packs de gases", horiz=True)
    camion(pl, (1.0, -6.4), 6.0, "Utilitario", horiz=False)
    for fl in L.FLUJOS:
        pl.flujo(fl.pts, fl.cat, cada=22.0 if fl.cat in ("TL", "SE") else 26.0,
                 largo=2.6 if fl.cat != "TL" else 3.4, ancho=1.3 if fl.cat != "TL" else 1.9)
    pl.flujo(L.RC_FLUJO, "SE", cada=22.0, largo=2.6, ancho=1.3)
    for fl in L.EFLUENTES:
        pl.flujo(fl.pts, fl.cat, cada=30.0, largo=2.4, ancho=1.2)
    emisiones(pl)


def fl_pi_03(doc, ox):
    h, pl = lamina_flujo(doc, ox, "FL_PI_03", "FL_PI_03 - FLUJO DE MATERIALES: MP, SE, PT, SCRAP Y EFLUENTES",
                         "Flujo de materiales", "MP, SE, PT, scrap y manejo de materiales - año 10", "Diagrama de flujo", 1, 1)
    fondo(pl)
    flujos_materiales(pl)
    D.rotulos_sector(pl, h=1.7, areas=False)
    for n, xy, txt in MARCAS_03:
        globo(pl, n, xy)
    col = Columna(h, pl)
    x = col.x
    y = leyenda_flujos(pl, x, col.y, ["MP", "SE", "TL", "RET", "PT", "SCRAP", "EFL-L", "EFL-G"])
    y -= 3
    pl.texto("Flujos numerados", (x, y), 3.5, A.BOTTOM_LEFT, papel=True)
    y -= 5.5
    for n, xy, txt in MARCAS_03:
        globo_papel(pl, n, (x + 3, y))
        pl.texto(txt, (x + 8, y), 2.2, A.MIDDLE_LEFT, papel=True)
        y -= 5.0
    y = pl.parrafo(["Criterios: una sola recepción de MP con cuarentena (P1); polvo, embalaje y revendidos por",
                    "el muelle P3; recorrido en el orden de los procesos con 0 cruces entre MP, SE y PT (verificado",
                    "por cálculo); scrap a volquete exterior junto a P1. Jerarquía de circulación:",
                    "1) pasillo central PC 3,80 m y calles de MP de 5,0 m: autoelevador doble sentido;",
                    "2) senda peatonal PP 1,20 m separada por defensa, cruces sólo en cebras X1, X2...;",
                    "3) calles de carros y operarios PO 1,0-1,4 m al norte: ZONA SIN AUTOELEVADOR;",
                    "4) calles de autoelevador de PT y transpaleta en terminación, embalaje y expedición."], x, y - 2, 2.2)
    M_ = C.manejo()
    cols = [("Unidad de carga", 56, "l"), ("Medio", 26, "l"), ("Recorrido", 50, "l"), ("Viajes/día", 16, "c"),
            ("m", 11, "c"), ("min/viaje", 15, "c"), ("min/día", 15, "c")]
    filas = [[r["carga"], r["medio"], r["ruta"], f(r["viajes"], 1), f(r["dist"], 0), f(r["t_viaje"], 1),
              f(r["min_dia"], 0)] for r in M_["filas"]]
    y = pl.tabla(x, y - 12, cols, filas, 4.0, 1.9,
                 "Manejo de materiales: métodos y tiempos (día pico 2035, 1.184 cilindros/día)")
    oc = M_["ocup"]
    y = pl.parrafo([
        f"Tiempo por viaje = 2 × distancia / velocidad + tiempo fijo (autoelevador 1,5 m/s y 1,5 min; transpaleta y",
        f"carro 0,8 m/s y 1,0 / 0,5 min). Turno útil 408 min (8 h - 15 % de suplementos).",
        f"Autoelevador de MP: {f(oc['Autoelevador MP'] * 100, 0)} % de un turno; de PT {f(oc['Autoelevador PT'] * 100, 0)} %; "
        f"de carros {f(oc['Autoelevador carros'] * 100, 0)} %.",
        f"Carros FCHP20505: {M_['carros_dia']} carros/día por tramo; cada carro lo empuja el operario que cierra el lote",
        "(W-MAN: puestos pegados con un carro entre cada par): no hace falta tren logístico. El riel aéreo lleva el",
        "cilindro de la detección a la descarga. Un abastecedor hace el milk run de consumibles desde AL-CA."],
        x, y - 3, 2.1)
    cols = [("Portón", 20, "l"), ("Qué entra o sale", 84, "l"), ("Vehículo", 34, "l"), ("Frecuencia", 40, "l"),
            ("Horario", 34, "l")]
    y = pl.tabla(x, y - 12, cols, [list(r) for r in C.PORTONES], 4.0, 1.9,
                 "Portones: función y frecuencia (3 portones: el ex P4 se suprimió, la pintura en polvo va al depósito DP)")
    cols = [("Proveedor / material", 58, "l"), ("t/entr.", 14, "c"), ("Entr./año", 15, "c"),
            ("Vehículo", 56, "l"), ("Portón", 36, "c"), ("Destino", 25, "c")]
    filas = [[g, f(t, 1), f(n, 1), v, p, d] for g, t, n, v, p, d in C.ENTREGAS]
    y = pl.tabla(x, y - 12, cols, filas, 4.0, 1.9, "Recepción de MP por entrega (año 10)")
    return h


def fl_pi_03b(doc, ox):
    h, pl = lamina_flujo(doc, ox, "FL_PI_03", "FL_PI_03 - REDES: ELECTRICIDAD, AIRE, GASES Y EFLUENTES",
                         "Redes e instalaciones", "Tendidos mínimos desde la sala técnica", "Plano de instalaciones",
                         2, 2)
    fondo(pl, relleno=False, rot_eq=True)
    D.rotulos_sector(pl, h=1.7, areas=False)
    R_ = C.redes()
    tg = C.TGBT
    for sec, kw, (cx, cy), lg in R_["elec"]:
        pts = [tg, (tg[0], 21.4), (cx, 21.4), (cx, cy)]
        pl.pl(pts, "I-ELEC")
        pl.circulo((cx, cy), 0.6, "I-ELEC")
        pl.texto(f"TS {sec}", (cx + 0.8, cy + 0.6), 1.6, A.BOTTOM_LEFT, "I-ELEC")
    for t in C.AIRE:
        pl.pl(t, "I-AIRE")
    for cod, lg in R_["sold"]:
        e = next(x for x in L.EQUIPOS if x.cod == cod)
        yy = 39.6 if e.rect.c[1] > 24 else 21.0
        pl.pl([C.JGS, (C.JGS[0], yy), (e.rect.c[0], yy), e.rect.c], "I-SOLD")
    for cod, lg in R_["n2"]:
        e = next(x for x in L.EQUIPOS if x.cod == cod)
        pl.pl([C.JGN, (C.JGN[0] + 0.4, C.JGN[1]), (C.JGN[0] + 0.4, 21.4), (e.rect.c[0], 21.4), e.rect.c], "I-N2")
    for cod, lg in R_["gas"]:
        e = next(x for x in L.EQUIPOS if x.cod == cod)
        if e.rect.c[1] > 24:
            pts = [C.ERM, (88.2, C.ERM[1]), (88.2, 39.9), (e.rect.c[0], 39.9), e.rect.c]
        elif e.rect.c[0] > 60:
            pts = [C.ERM, (e.rect.c[0], C.ERM[1]), e.rect.c]
        else:
            pts = [C.ERM, (88.2, C.ERM[1]), (88.2, 0.8), (e.rect.c[0], 0.8), e.rect.c]
        pl.pl(pts, "I-GAS")
    for fl in L.EFLUENTES:
        pl.flujo(fl.pts, fl.cat, cada=30.0, largo=2.4, ancho=1.2)
    emisiones(pl)
    col = Columna(h, pl)
    x, y = col.x, col.y
    pl.texto("Referencias", (x, y), 3.5, A.BOTTOM_LEFT, papel=True)
    y -= 6
    for capa, txt in (("I-ELEC", "Alimentador eléctrico TGBT -> tablero seccional (TS)"),
                      ("I-AIRE", "Aire comprimido: anillo con bajadas FRL cada 8 m"),
                      ("I-SOLD", "Gas de soldadura Ar/CO₂ (ARCAL 21): pack en la jaula JG -> CG1"),
                      ("I-N2", "Nitrógeno para presurización: pack en la jaula JG -> CG1"),
                      ("I-GAS", "Gas natural a los hornos desde la regulación ERM"),
                      ("F-EFL-LIQ", "Efluentes líquidos a PTE (enterrado, por gravedad)"),
                      ("F-EFL-GAS", "Captación localizada y salida por techo")):
        pl.m.add_lwpolyline([(x, y), (x + 16, y)], dxfattribs={"layer": capa})
        pl.texto(txt, (x + 20, y), 2.3, A.MIDDLE_LEFT, papel=True)
        y -= 5.5
    y = pl.parrafo(["Criterio 4 (minimizar tendidos): la sala técnica ST (transformador, TGBT y compresores) está en",
                    "el centro de cargas, sobre la fachada norte; la jaula exterior de gases JG, detrás de la sala SC",
                    "(reguladores CG1); la PTE, al sur junto a la colectora. Los procesos con efluente líquido (PH,",
                    "ensayo de pérdidas y recargas) van a la cámara de decantación y por cañería enterrada a la PTE.",
                    "Recargas tiene tablero propio y manifold de CO₂ (trasvasadora, W-REC).",
                    f"Potencia instalada de equipos: {f(R_['kw_total'], 0)} kW; con simultaneidad 0,6 -> transformador de",
                    "315 kVA (verificar con el relevamiento de cargas definitivo)."], x, y - 3, 2.2)
    cols = [("Tablero seccional", 44, "l"), ("kW", 16, "c"), ("Largo desde TGBT m", 34, "c")]
    filas = [[s_, f(k, 1), f(lg, 1)] for s_, k, c_, lg in R_["elec"]]
    filas.append(["Total", f(R_["kw_total"], 1), f(sum(r[3] for r in R_["elec"]), 1)])
    yb = pl.tabla(x, y - 12, cols, filas, 4.3, 2.1, "Alimentadores (recorrido ortogonal)")
    x2 = x + 104
    yy = y - 12
    for tit, datos in (("Agua de PH y pérdidas a PTE", R_["agua"]), ("Gas natural a hornos", R_["gas"]),
                       ("Nitrógeno", R_["n2"]), ("Gas de soldadura", R_["sold"])):
        yy = pl.tabla(x2, yy, [("Punto", 36, "l"), ("Largo m", 22, "c")],
                      [[c_, f(l_, 1)] for c_, l_ in datos] + [["Total", f(sum(l_ for c_, l_ in datos), 1)]],
                      4.1, 2.1, tit) - 11
    pl.parrafo([f"Anillo de aire comprimido: {f(R_['aire_anillo_m'], 0)} m.",
                "Compresores a tornillo, pulmón y secador frigorífico en la sala SC.",
                "N₂: manifold con conmutación automática, regulador y detector de fugas."], x2 + 66, y - 12, 2.1)
    return h


# ================================================================ FL_PI_01 DIR
TRONCOS = {
    # garita (G4) -> hall y fichado -> pasillo limpio -> vestuario -> duchas o sanitarios -> PP-1
    "hombres": list(L.CAMINO_PEATONAL) + [(-9.0, 20.0), (-8.0, 20.0), (-8.0, 23.75), (-14.15, 23.75),
                                          (-14.15, 27.0), (-12.0, 27.0), (-12.0, 29.5)],
    "a planta": [(-12.0, 27.3), (-14.4, 27.3), (-14.4, 24.1), (0.0, 24.1)],
    "mujeres": [(-8.0, 23.75), (-8.0, 26.6), (-9.65, 26.6), (-9.65, 28.6)],
    "comedor": [(-6.3, 24.1), (-6.3, 25.75), (-3.0, 25.75), (-3.0, 28.0)],
    "administración": [(-8.0, 20.35), (-6.0, 20.35)],
}


def fl_pi_01(doc, ox):
    h, pl = lamina_flujo(doc, ox, "FL_PI_01", "FL_PI_01 - DIAGRAMA DE RECORRIDO DE HILOS DEL PERSONAL (DIR)",
                         "DIR hilos de personal", "Recorridos del personal - año 10", "Diagrama de recorrido")
    fondo(pl, relleno=True, rot_eq=True)
    for fl in L.FLUJOS:
        pl.pl(fl.pts, "F-RET")
    for s_ in L.LOCALES:
        pl.texto(s_.cod, s_.rect.c, 1.3, A.MIDDLE_CENTER)
    for pts in TRONCOS.values():
        pl.pl(pts, "F-PERSONAL")
    grupos = []
    for nom, main, br in L.HILOS:
        pl.pl(main, "F-PERSONAL")
        mx = 0.0
        for a, b, c_, d in br:
            pl.pl([(a, b), (c_, d)], "F-PERSONAL")
            pl.relleno(circ_pts((c_, d), 0.35), D.RGB_FLUJO["PER"], "F-PERSONAL")
            mx = max(mx, math.dist((a, b), (c_, d)))
        if not br:
            pl.relleno(circ_pts(main[-1], 0.35), D.RGB_FLUJO["PER"], "F-PERSONAL")
        grupos.append((nom, C.largo(main) + mx, main))
    for cod, r, nota in L.SENDAS:
        globo(pl, cod, (r.c[0] - 3.5, r.c[1]), 3.0)
    D.rotulos_sector(pl, h=1.6, areas=False)
    col = Columna(h, pl)
    x, y = col.x, col.y
    pl.texto("Referencias", (x, y), 3.5, A.BOTTOM_LEFT, papel=True)
    y -= 6
    pl.m.add_lwpolyline([(x, y), (x + 16, y)], dxfattribs={"layer": "F-PERSONAL"})
    pl.texto("Hilo de personal (magenta, trazos)", (x + 20, y), 2.3, A.MIDDLE_LEFT, papel=True)
    y -= 5.5
    pl.m.add_circle((x + 8, y), 0.9, dxfattribs={"layer": "F-PERSONAL"})
    pl.texto("Puesto de trabajo", (x + 20, y), 2.3, A.MIDDLE_LEFT, papel=True)
    y -= 5.5
    pl.m.add_lwpolyline([(x, y), (x + 16, y)], dxfattribs={"layer": "F-RET"})
    pl.texto("Flujos de materiales, de fondo (ver FL_PI_03)", (x + 20, y), 2.3, A.MIDDLE_LEFT, papel=True)
    y -= 5.5
    for k in range(4):
        pl.m.add_lwpolyline([(x + k * 4, y - 1.2), (x + k * 4 + 2, y - 1.2), (x + k * 4 + 2, y + 1.2), (x + k * 4, y + 1.2)],
                            close=True, dxfattribs={"layer": "A-SENDA"})
    pl.texto("Senda peatonal señalizada: único cruce de hilo y flujo", (x + 20, y), 2.3, A.MIDDLE_LEFT, papel=True)
    y = pl.parrafo([
        "",
        "Recorrido: estacionamiento -> G4 -> SV-1 hall y fichado -> pasillo limpio -> vestuario (armario",
        "doble: ropa de calle / de trabajo) -> sanitarios y duchas (sólo desde el vestuario) -> pasillo",
        "limpio -> PP-1 -> senda peatonal PP (separada del autoelevador por defensa) -> puesto.",
        "El PC corre entre las dos bandas de la U: los operarios de la banda norte trabajan del lado sur",
        "de sus máquinas y los de la banda sur del lado norte, de modo que llegan al puesto sin cruzar el",
        "recorrido de las piezas. La línea de carros es una horquilla con su calle de operarios adentro.",
        "Donde un hilo corta un flujo (cuerpos de carros, cúpulas, láser, riel de pintura) hay una",
        "senda peatonal X demarcada (cebra amarilla IRAM 10005, espejo y prioridad peatonal).",
        f"Cruces de hilos con flujos verificados por cálculo sobre el modelo: todos en {len(L.SENDAS)} sendas.",
        "Recargas ocupa el ángulo SO de la nave: su personal entra por el PC y el corredor RC-N y usa los",
        "sanitarios del bloque de servicios. Los utilitarios usan su portón P2: el público no entra a la planta.",
    ], x, y - 2, 2.2)
    cols = [("Hilo (grupo de puestos)", 64, "l"), ("Desde PP-1 (m)", 26, "c"), ("A sanitario (m)", 26, "c")]
    filas = []
    for nom, lg, main in grupos:
        fin = main[-1]
        d1 = abs(fin[0]) + abs(fin[1] - 23.7)
        filas.append([nom, f(lg, 0), f(d1 + 21.5, 0)])
    yb1 = pl.tabla(x, y - 12, cols, filas, 4.3, 2.1, "Longitud de los hilos (turno mañana)")
    ops = {}
    for e in L.EQUIPOS:
        ops.setdefault(e.sector, [0, 0])
        ops[e.sector][0] += 1 if e.op else 0
        ops[e.sector][1] += e.op
    nombre = {s_.cod: s_.nombre for s_ in L.SECTORES}
    cols2 = [("Sector", 88, "l"), ("Puestos", 16, "c"), ("Operarios", 18, "c")]
    filas2 = [[f"{k} {nombre.get(k, '')}", v[0], v[1]] for k, v in ops.items() if v[1]]
    filas2.append(["Total de puestos (la DT, con coef. hombre-máquina, da 30 operarios)", "",
                   sum(v[1] for v in ops.values())])
    yb2 = pl.tabla(x + 126, y - 12, cols2, filas2, 4.0, 2.0, "Puestos con operario en la nave")
    y = min(yb1, yb2)
    san = C.sanitarios()
    cols3 = [("Artefacto", 36, "l"), ("H req.", 16, "c"), ("H proy.", 16, "c"), ("M req.", 16, "c"),
             ("M proy.", 16, "c")]
    filas3 = [[k.capitalize(), san["req_H"][k], san["proy"]["H"][k], san["req_M"][k], san["proy"]["M"][k]]
              for k in ("inodoros", "lavabos", "orinales", "duchas")]
    filas3.append(["Armarios (art. 50)", san["armarios_req"]["H"], san["armarios_proy"]["H"], san["armarios_req"]["M"],
                   san["armarios_proy"]["M"]])
    filas3.append(["Sanitario accesible", "-", str(san["proy"]["accesibles"]), "-", "unisex"])
    yb = pl.tabla(x, y - 12, cols3, filas3, 4.3, 2.1,
                  f"Sanitarios (Dec. 351/79 art. 49): {san['H']} H y {san['M']} M en el turno más numeroso")
    pl.parrafo([
        "Turno mañana: 53 personas + 8 choferes que inician",
        "y terminan en planta; 10 % mujeres (DT 2035).",
        "Núcleo sanitario en servicios, junto a PP-1, con",
        "H, M y sanitario accesible (Ley 24.314, Dec. 914/97);",
        "el PC lleva a todos los puestos sin cruzar flujos",
        "fuera de las sendas.",
        "Vestuario de mujeres al 20 % de la dotación para no",
        "condicionar la incorporación de personal femenino.",
        "Lactario (Ley 26.873) y primeros auxilios en servicios.",
        "Espacio de cuidado (Dec. 144/2022): no obligatorio",
        "con menos de 100 personas (dotación 71).",
    ], x + 112, y - 12, 2.1)
    return h


def circ_pts(c, r, n=16):
    return [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ================================================================ FL_PI_02 flujo de operaciones
ASME = {}
for _c in ("M04", "M16", "M06", "M07", "M08", "M09a", "M09b", "M10", "M11", "B02", "B03", "E09", "B04", "A06", "B06",
           "B14a", "B14b", "B14c", "B14d", "B08", "B10", "P01", "P04", "P03", "P06", "P08", "T01", "T03", "T05", "T07",
           "T09", "T08", "T11", "MK1", "C01", "C02a", "C02b", "C04", "C06", "C05", "C08", "C81", "C10", "T02", "T12",
           "T13"):
    ASME[_c] = "O"
for _c in ("Q01", "B09", "P09", "T06", "C09"):
    ASME[_c] = "I"
for _c in ("A07", "B07", "C07"):
    ASME[_c] = "OI"
for _c in ("C12",):
    ASME[_c] = "D"
ALMACENES = ("AL-MM", "AL-ID", "AL-MC", "AL-CU", "AL-CH", "AL-FL", "AL-SS", "AL-CC", "AL-CT", "AL-CQ", "AL-PR", "AL-PT", "AL-PK", "DP",
             "AL-EB", "AL-3", "S4")

CURSOGRAMAS = {
    "S2 - Matafuegos ABC 2,5 / 5 / 10 kg": [
        ("A", "Chapa LAF (cuarentena -> AL-CH -> mesa elevadora)", "AL-CH"), ("O", "1 Corte de desarrollos", "M04"),
        ("D", "Carro de plataforma junto a la roladora", "PU-D"), ("O", "6 Cilindrado", "B02"),
        ("D", "FCHP con virolas", "PU-V1"), ("O", "7 Soldadura longitudinal", "B03"),
        ("D", "FCHP con cuerpos soldados", "PU-V2/V3"), ("O", "9 Encastre de fondo", "E09"),
        ("O", "10 Bordoneado", "B04"), ("O", "11 Soldadura circ. (con la cúpula)", "A06/B06"),
        ("I", "12 Control de espesor", "Q01"), ("D", "FCHP «espesor OK»", "PU-S"),
        ("OI", "13 Prueba hidráulica", "A07/B07"), ("D", "Probados en sus carros", "PU-6"),
        ("O", "14 Secado", "B14a-d"), ("D", "Secos con tapón", "PU-7"), ("O", "15 Granallado de rodillos", "B08"),
        ("I", "16 Detección de defectos", "B09"), ("O", "17 Corrección (jaula «a corregir»)", "B10"),
        ("T", "Riel aéreo (cuelga en la detección)", "-"), ("O", "18 Pintura en polvo y descarga", "P01-P08"),
        ("D", "Terminados pintados", "PU-TP"), ("O", "19-23 Terminación (ver S1)", "T01-T07"),
        ("O", "24 Encajonado y envolvedora", "T09/T11"), ("A", "Almacén de PT", "AL-3"),
        ("T", "Expedición por el muelle", "P3")],
    "S1 - Matafuegos ABC 1 kg (fabricados)": [
        ("A", "Caño Ø76,2 en el cantiléver", "AL-CT"), ("T", "Atado al cajón de alimentación (pluma)", "CJ1"),
        ("O", "2 Corte láser de tubo", "M16"), ("D", "Carros de cajones «en llenado» / «vacío»", "PU-T1"),
        ("T", "Carro de tramos al encastre", "PU-T2"), ("O", "9-17 Línea común (igual que S2)", "E09-B10"),
        ("O", "18 Pintura en polvo (riel aéreo)", "P01-P08"), ("D", "Terminados pintados", "PU-TP"),
        ("O", "19 Carga de polvo (big bag ABC 60)", "BB1/T01"), ("O", "20 Ensamblaje", "T03"),
        ("O", "21 Presurización con N₂", "T05"), ("I", "22 Ensayo de pérdidas", "T06"), ("O", "23 Etiquetado", "T07"),
        ("O", "24 Encajonado (armadora de cajas)", "AC1/T09"), ("O", "Envolvedora", "T11"),
        ("A", "Almacén de PT", "AL-3"), ("T", "Expedición por el muelle", "P3")],
    "Subconjunto cúpulas y fondos 1-10 kg": [
        ("A", "Rollos de fleje en el porta-flejes", "AL-FL"), ("T", "Rollo al desbobinador (espolón)", "-"),
        ("O", "3 Desbobinado, enderezado y embutido", "M06-M08"), ("D", "Carros de cajones en llenado", "PU-K"),
        ("D", "Zona de fondos", "PU-FO"), ("T", "Fondos al encastre (paso 9)", "-"),
        ("D", "Zona de cúpulas", "PU-CU"), ("O", "4 Preparación de cuello: muesca", "M09a/b"),
        ("O", "5 Numerado de la cúpula", "M10"), ("O", "8 Soldadura de cuello", "M11"),
        ("D", "Cúpulas con cuello", "PU-CC2/CC"), ("T", "A la soldadura circ. (paso 11)", "-")],
    "S3 - Matafuegos ABC rodantes 25 / 50 / 70 / 100 kg": [
        ("A", "Chapa LAC (calle de chapa)", "AL-CC"), ("O", "1 Corte (guillotina compartida)", "M04"),
        ("O", "C2.1 Marcado del cuerpo", "MK1"), ("D", "EFE 600 / mesa móvil", "PU-M/CI"),
        ("O", "C3 Cilindrado", "C01"), ("D", "Cuerpos rolados", "PU-CR"), ("O", "C4 Punteo (2 viradores)", "C02a/b"),
        ("D", "Cuerpos punteados", "PU-CP"), ("O", "C5 Soldadura longitudinal", "C04"),
        ("O", "C6 Soldadura de cupla en la cúpula", "C06"), ("O", "C7 Armado y soldadura circ.", "C05"),
        ("O", "C8.1 Fabricación de accesorios", "C81"), ("O", "C8 Soldadura de accesorios", "C08"),
        ("I", "Inspección de costuras", "C09"), ("OI", "C9 Prueba hidráulica", "C07"), ("O", "Secado", "C10"),
        ("D", "Pulmón de despacho a pintura", "C12"), ("T", "Pintura tercerizada (muelle P3)", "-"),
        ("O", "Carga de polvo (big bag ABC 90)", "BB2/T02"), ("O", "Armado de válvula y manguera", "T12"),
        ("O", "Presurización y etiquetado", "T13"), ("T", "Expedición por el muelle", "P3")],
    "S4 - Tercerizados revendidos (CO₂, agua, AFFF, K, agente limpio)": [
        ("T", "Recepción por el muelle", "P3"), ("I", "Control de recepción y sello IRAM", "REC"), ("A", "Stock", "S4"),
        ("T", "Expedición con el pedido", "P3")],
    "RC - Recargas (servicio, W-REC)": [
        ("T", "Recepción y registro (portón P2)", "R01"), ("I", "R2 Inspección visual", "R19a/b"),
        ("O", "R3 Descarga (recinto de polvo)", "R02a-e"), ("O", "R4 Desarme y limpieza", "R04a-c"),
        ("I", "R5 Laboratorio: Puffer y mufla", "R23"), ("OI", "R6 Prueba hidráulica", "R07"),
        ("O", "R7 Secado y cámara", "R08"), ("O", "R8 Pintura (retoque)", "R20a/b"), ("O", "R9 Carga", "R09a-c"),
        ("O", "R10 Ensamblaje y marbete", "R10a-c"), ("O", "R11 Presurización", "R11a/b"),
        ("I", "R12 Ensayo de pérdidas", "R12"), ("I", "R13 Peso, precinto y etiquetado", "R22/R21"),
        ("A", "Para entregar", "RC-RD"), ("T", "Despacho (portón P2)", "R17a/b")],
}


def simbolo(pl, tipo, c, r=1.7, papel=False):
    """Símbolos ASME: O operación, I inspección, OI combinada, D demora, A almacenamiento, T transporte."""
    p = c if papel else pl.P(*c)
    m = pl.m
    at = {"layer": "A-TEXTO"}
    if tipo == "O":
        m.add_circle(p, r, dxfattribs=at)
    elif tipo == "I":
        m.add_lwpolyline([(p[0] - r, p[1] - r), (p[0] + r, p[1] - r), (p[0] + r, p[1] + r), (p[0] - r, p[1] + r)],
                         close=True, dxfattribs=at)
    elif tipo == "OI":
        m.add_lwpolyline([(p[0] - r, p[1] - r), (p[0] + r, p[1] - r), (p[0] + r, p[1] + r), (p[0] - r, p[1] + r)],
                         close=True, dxfattribs=at)
        m.add_circle(p, r * 0.8, dxfattribs=at)
    elif tipo == "D":
        m.add_lwpolyline([(p[0] - r * 0.8, p[1] - r), (p[0], p[1] - r), (p[0], p[1] + r), (p[0] - r * 0.8, p[1] + r)],
                         dxfattribs=at)
        m.add_arc(p, r, 270, 90, dxfattribs=at)
    elif tipo == "A":
        m.add_lwpolyline([(p[0] - r, p[1] + r * 0.8), (p[0] + r, p[1] + r * 0.8), (p[0], p[1] - r)],
                         close=True, dxfattribs=at)
    elif tipo == "T":
        m.add_lwpolyline([(p[0] - r, p[1] - r * 0.35), (p[0] + r * 0.2, p[1] - r * 0.35), (p[0] + r * 0.2, p[1] - r * 0.8),
                          (p[0] + r, p[1]), (p[0] + r * 0.2, p[1] + r * 0.8), (p[0] + r * 0.2, p[1] + r * 0.35),
                          (p[0] - r, p[1] + r * 0.35)], close=True, dxfattribs=at)


def fl_pi_02(doc, ox):
    h, pl = lamina_flujo(doc, ox, "FL_PI_02", "FL_PI_02 - FLUJO DE OPERACIONES Y PROCESOS POR SECCIÓN",
                         "Flujo de operaciones", "Secuencia de operaciones por sección - año 10", "Diagrama de proceso")
    fondo(pl, relleno=True, rot_eq=False)
    for fl in L.FLUJOS:
        if fl.cat in ("SE", "TL", "PT"):
            pl.flujo(fl.pts, fl.cat, cada=24.0, largo=2.4, ancho=1.2)
    pl.flujo(L.RC_FLUJO, "SE", cada=24.0, largo=2.4, ancho=1.2)
    for e in L.EQUIPOS:
        t = ASME.get(e.cod)
        if t:
            simbolo(pl, t, e.rect.c, 1.5)
            pl.texto(e.cod, (e.rect.c[0], e.rect.c[1] - 0.9), 1.1, A.TOP_CENTER)
    for s in L.SECTORES + L.LOCALES:
        if s.cod in ASME:
            simbolo(pl, ASME[s.cod], s.rect.c, 1.5)
        if s.cod in ALMACENES:
            simbolo(pl, "A", s.rect.c, 1.6)
    for s in L.LOCALES:
        if s.cat == "RC":
            pl.texto(s.cod, (s.rect.x0 + 0.4, s.rect.y1 - 0.4), 1.4, A.TOP_LEFT)
    D.rotulos_sector(pl, h=1.7, areas=False)
    # secciones (S1..S4, RC) con recuadro rotulado
    for cod, nom, r in (("S1", "S1 1 kg (corte de tubo)", L.R(24.6, 29.7, 28.9, 37.2)),
                        ("S2", "S2 2,5-10 kg (cuerpo)", L.R(24.6, 24.5, 39.9, 29.7)),
                        ("S12", "S1 + S2 línea común", L.R(33.5, 34.6, 79.1, 39.3)),
                        ("S3", "S3 rodantes", L.R(18.0, 0.2, 41.0, 19.2)), ("S4", "S4 tercerizados", L.R(41.0, 0.2, 46.8, 2.4)),
                        ("RC", "RC recargas", L.R(0.3, 0.3, 18.0, 19.0))):
        pl.rect(r, "F-TL")
        pl.texto(nom, (r.x1 - 0.4, r.y0 + 0.5), 2.2, A.BOTTOM_RIGHT, "F-TL")
    col = Columna(h, pl)
    x, y = col.x, col.y
    pl.texto("Símbolos (ASME)", (x, y), 3.5, A.BOTTOM_LEFT, papel=True)
    y -= 7
    for t, txt in (("O", "Operación"), ("I", "Inspección / control"), ("OI", "Operación e inspección combinadas"),
                   ("T", "Transporte (autoelevador o carro de pulmón)"), ("D", "Demora: pulmón o supermercado"),
                   ("A", "Almacenamiento")):
        simbolo(pl, t, (x + 4, y), 2.0, papel=True)
        pl.texto(txt, (x + 10, y), 2.4, A.MIDDLE_LEFT, papel=True)
        y -= 6.0
    y = leyenda_flujos(pl, x + 140, col.y, ["SE", "PT"], "Flujos")
    y = pl.parrafo(["Secciones: S1 1 kg fabricado; S2 manuales 2,5-10 kg;", "S3 rodantes 25-100 kg; S4 tercerizados revendidos",
                    "(sin transformación); RC recargas (servicio, ángulo SO).",
                    "Pintura y terminación son comunes a S1 y S2; los carros",
                    "se pintan afuera. El 1 kg no se granalla."], x + 140, y - 3, 2.1)
    y = col.y - 46
    fila_alta = 0
    xx = x
    for i, (nom, pasos) in enumerate(CURSOGRAMAS.items()):
        if i == 3:
            y -= fila_alta + 18
            xx = x
            fila_alta = 0
        cols = [("", 7, "c"), ("Paso", 57, "l"), ("Dónde", 25, "c")]
        filas = [["", d, w] for t, d, w in pasos]
        yb = pl.tabla(xx, y, cols, filas, 3.9, 1.9, nom if len(nom) < 44 else nom[:42] + "…", h_tit=2.6)
        for j, (t, d, w) in enumerate(pasos):
            simbolo(pl, t, (xx + 3.5, y - (j + 1.5) * 3.9), 1.35, papel=True)
        cuenta = {t: sum(1 for p in pasos if p[0] == t) for t in ("O", "I", "OI", "T", "D", "A")}
        pl.texto("O {O} · I {I} · O/I {OI} · T {T} · D {D} · A {A}".format(**cuenta), (xx, yb - 2.5), 2.1,
                 A.TOP_LEFT, papel=True)
        fila_alta = max(fila_alta, y - yb)
        xx += 92
    return h


def camion(pl, p, largo, rot, horiz=True):
    if horiz:
        r = L.R(p[0], p[1], p[0] + largo, p[1] + 2.6)
    else:
        r = L.R(p[0], p[1], p[0] + 2.6, p[1] + largo)
    pl.rect(r, "A-EXTERIOR")
    if horiz:
        pl.linea((p[0] + 2.3, p[1]), (p[0] + 2.3, p[1] + 2.6), "A-EXTERIOR")
    else:
        pl.linea((p[0], p[1] + largo - 2.3), (p[0] + 2.6, p[1] + largo - 2.3), "A-EXTERIOR")
    pl.texto(rot, r.c, 1.5, A.MIDDLE_CENTER, rot=0 if horiz else 90)


def globo(pl, n, xy, r=2.2):
    pl.m.add_circle(pl.P(*xy), r, dxfattribs={"layer": "A-TEXTO"})
    pl.texto(str(n), xy, 2.0, A.MIDDLE_CENTER)


def globo_papel(pl, n, p, r=2.2):
    pl.m.add_circle(p, r, dxfattribs={"layer": "A-TEXTO"})
    pl.texto(str(n), p, 2.0, A.MIDDLE_CENTER, papel=True)
