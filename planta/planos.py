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
               "TL": "Tren logístico de un sentido (SE)", "RET": "Retorno de ganchos vacíos del lazo de pintura (aéreo)",
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
    pl.texto("Calle interna de camiones 7 m (sentido: entra por G1, sale por G3)", (45.0, 59.8), 2.0, A.MIDDLE_CENTER)
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
        # dos filas de cocheras de 2,50 × 5,00 y calle de 6 m; 2 accesibles de 3,50 junto al ingreso peatonal
        xs = [-26.0 + 2.5 * i for i in range(21)]
        for yb, yt in ((-27.0, -22.0), (-39.0, -34.0)):
            for x in xs:
                pl.linea((x, yb), (x, yt), "A-EXTERIOR")
            pl.linea((xs[0], yb), (xs[-1], yb), "A-EXTERIOR")
        for x in (24.0, 27.5):
            pl.linea((x, -27.0), (x, -22.0), "A-EXTERIOR")
        pl.texto("2 accesibles 3,50 m", (25.8, -24.5), 1.4, A.MIDDLE_CENTER)
        pl.texto("40 cocheras 2,50 × 5,00", (0.0, -30.5), 1.8, A.MIDDLE_CENTER)
        # camino peatonal desde G4 al hall de servicios (SV-1)
        pl.pl([(22.5, -62.0), (22.5, -46.0), (32.0, -46.0), (32.0, -14.0), (-1.8, -14.0), (-1.8, 19.0)], "A-PASILLO")
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
    (1, (5.0, 53.0), "MP-1 chapa, caño, flejes e insumos: alero de descarga norte, entran por P1"),
    (2, (35.4, -9.0), "MP-2 casquetes de carros y tercerizados revendidos (M3)"),
    (3, (65.5, -9.0), "MP-3 polvo químico en big bags (P4)"),
    (4, (49.5, -9.0), "MP-4 válvulas, manómetros, etiquetas y embalaje (por el muelle M2)"),
    (5, (93.0, 29.5), "MP-5 químicos de pretratamiento y pintura en polvo (P3)"),
    (6, (26.7, -9.0), "MP-6 carros pintados, polvo, estructuras y ruedas (P8)"),
    (7, (30.6, 29.0), "SE fila N1: guillotina -> numerado -> cilindrado -> soldadura longitudinal"),
    (8, (31.4, 31.6), "SE láser 1 kg -> encastre"),
    (9, (33.0, 42.4), "SE cúpulas y fondos: embutido -> cuello -> soldadura circunferencial"),
    (10, (53.0, 33.6), "SE línea principal: encastre -> bordoneado -> sold. circ. -> PH -> secado -> granallado"),
    (11, (79.0, 11.0), "SE lazo de pintura: carga -> pretratamiento -> cabina -> hornos -> descarga"),
    (12, (57.0, 11.6), "SE terminación: carga de polvo -> ensamblaje -> presurización -> embalaje"),
    (13, (20.2, -9.0), "SE carros a pintura tercerizada (P6); vuelven pintados por P8"),
    (14, (44.7, -9.0), "PT a expedición por los muelles M1 y M2"),
    (15, (31.4, -9.0), "PT carros terminados (P9)"),
    (16, (-6.0, 44.0), "Scrap a volquete (P2)"),
    (17, (73.0, -30.0), "Efluentes líquidos a tratamiento PTE y colectora"),
    (18, (-8.0, 10.0), "Recargas: RC-1 -> descarga -> PH -> recarga -> despacho RC-2"),
    (19, (56.0, 17.8), "PT cilindros vendidos vacíos: almacén de cilindros -> PT"),
]


def flujos_materiales(pl):
    camion(pl, (0.5, 46.0), 18.6, "Semi 30 t", horiz=True)
    camion(pl, (0.5, 50.6), 10.0, "Chasis 16 t", horiz=True)
    camion(pl, (19.0, -14.0), 9.5, "Pintor", horiz=False)
    camion(pl, (41.2, -14.0), 9.5, "PT", horiz=False)
    camion(pl, (45.6, -14.0), 9.5, "PT", horiz=False)
    camion(pl, (35.2, -14.0), 9.5, "Tercerizados", horiz=False)
    camion(pl, (63.2, -14.0), 9.5, "Polvo", horiz=False)
    camion(pl, (88.6, 26.2), 9.5, "Químicos", horiz=True)
    camion(pl, (-20.0, 1.6), 6.0, "Utilitario", horiz=True)
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
    y = leyenda_flujos(pl, x, col.y, ["MP", "SE", "RET", "PT", "SCRAP", "EFL-L", "EFL-G"])
    y -= 3
    pl.texto("Flujos numerados", (x, y), 3.5, A.BOTTOM_LEFT, papel=True)
    y -= 5.5
    for n, xy, txt in MARCAS_03:
        globo_papel(pl, n, (x + 3, y))
        pl.texto(txt, (x + 8, y), 2.2, A.MIDDLE_LEFT, papel=True)
        y -= 5.0
    y = pl.parrafo(["Criterios: cada MP entra por el portón más cercano a la máquina que la transforma;",
                    "recorrido en U con 0 cruces entre MP, SE y PT (verificado por cálculo); scrap por portón",
                    "propio a volquete exterior (el chatarrero no entra). Jerarquía de circulación:",
                    "1) pasillo central PC 3,80 m: autoelevador doble sentido, único lugar donde circula;",
                    "2) senda peatonal PP 1,20 m separada por defensa, cruces sólo en cebras X1, X2...;",
                    "3) calles de carros y operarios PO 0,90-1,60 m al norte: ZONA SIN AUTOELEVADOR;",
                    "4) calles de transpaleta y apiladora en PT, terminación y expedición."], x, y - 2, 2.2)
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
        f"Autoelevador: {f(M_['min']['Autoelevador'], 0)} min/día = {f(oc['Autoelevador'] * 100, 0)} % de un turno: "
        f"con 1 unidad alcanza y sobra para descargar camiones (≈ 45 min por semi).",
        f"Apiladora del PT: {f(oc['Apiladora'] * 100, 0)} %. Carros: {M_['carros_dia']} carros/día por tramo; cada carro "
        f"lo empuja el operario que cierra el lote (≈ 0,7 min,",
        "< 3 % de su jornada): no hace falta tren logístico ni chofer. Un abastecedor por turno hace el milk run",
        "de consumibles desde el pañol de línea (2 vueltas por turno, 24 puestos) y repone carros vacíos (PV)."],
        x, y - 3, 2.1)
    cols = [("Portón", 20, "l"), ("Qué entra o sale", 84, "l"), ("Vehículo", 34, "l"), ("Frecuencia", 40, "l"),
            ("Horario", 34, "l")]
    y = pl.tabla(x, y - 12, cols, [list(r) for r in C.PORTONES], 4.0, 1.9,
                 "Portones: función y frecuencia (no hay portón sin uso; el ex P5 se suprimió: sus insumos llegan por M2)")
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
    pl.pl([(41.0, 44.2), (41.0, 24.4), (2.0, 24.4), (2.0, 19.6), (69.8, 19.6), (69.8, 24.4), (41.0, 24.4)], "I-AIRE")
    for cod, lg in R_["sold"]:
        e = next(x for x in L.EQUIPOS if x.cod == cod)
        yy = 39.2 if e.rect.c[1] > 24 else 21.0
        pl.pl([C.JGS, (C.JGS[0], yy), (e.rect.c[0], yy), e.rect.c], "I-SOLD")
    for cod, lg in R_["n2"]:
        e = next(x for x in L.EQUIPOS if x.cod == cod)
        pl.pl([C.JGN, (C.JGN[0], 2.8), (e.rect.c[0], 2.8), e.rect.c], "I-N2")
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
                      ("I-SOLD", "Gas de soldadura Ar/CO₂ (ARCAL 21) desde la jaula JG-S"),
                      ("I-N2", "Nitrógeno para presurización desde la jaula JG-N"),
                      ("I-GAS", "Gas natural a los hornos desde la regulación ERM"),
                      ("F-EFL-LIQ", "Efluentes líquidos a PTE (enterrado, por gravedad)"),
                      ("F-EFL-GAS", "Captación localizada y salida por techo")):
        pl.m.add_lwpolyline([(x, y), (x + 16, y)], dxfattribs={"layer": capa})
        pl.texto(txt, (x + 20, y), 2.3, A.MIDDLE_LEFT, papel=True)
        y -= 5.5
    y = pl.parrafo(["Criterio 4 (minimizar tendidos): la sala técnica ST (transformador, TGBT y compresores) está en",
                    "el centro de cargas, sobre la fachada norte; las jaulas de gases, junto a sus consumos; la PTE,",
                    "al sur junto a la colectora. Los procesos con efluente líquido (PH, pretratamiento y lavado de",
                    "recargas) bajan por una cañería enterrada a lo largo del pasillo central hasta la PTE.",
                    "Recargas tiene tableros propios, manifold de N₂ y cámara de decantación.",
                    f"Potencia instalada de equipos: {f(R_['kw_total'], 0)} kW; con simultaneidad 0,6 -> transformador de",
                    "315 kVA (verificar con el relevamiento de cargas definitivo)."], x, y - 3, 2.2)
    cols = [("Tablero seccional", 44, "l"), ("kW", 16, "c"), ("Largo desde TGBT m", 34, "c")]
    filas = [[s_, f(k, 1), f(lg, 1)] for s_, k, c_, lg in R_["elec"]]
    filas.append(["Total", f(R_["kw_total"], 1), f(sum(r[3] for r in R_["elec"]), 1)])
    yb = pl.tabla(x, y - 12, cols, filas, 4.3, 2.1, "Alimentadores (recorrido ortogonal)")
    x2 = x + 104
    yy = y - 12
    for tit, datos in (("Agua de PH y pretratamiento a PTE", R_["agua"]), ("Gas natural a hornos", R_["gas"]),
                       ("Nitrógeno", R_["n2"]), ("Gas de soldadura", R_["sold"])):
        yy = pl.tabla(x2, yy, [("Punto", 36, "l"), ("Largo m", 22, "c")],
                      [[c_, f(l_, 1)] for c_, l_ in datos] + [["Total", f(sum(l_ for c_, l_ in datos), 1)]],
                      4.1, 2.1, tit) - 11
    pl.parrafo([f"Anillo de aire comprimido: {f(R_['aire_anillo_m'], 0)} m.",
                "Compresor a tornillo, tanque pulmón y secador frigorífico en ST.",
                "N₂: manifold con conmutación automática, regulador y detector de fugas."], x2 + 66, y - 12, 2.1)
    return h


# ================================================================ FL_PI_01 DIR
TRONCOS = {
    # garita -> hall y fichado -> pasillo limpio -> vestuario -> sanitarios y duchas -> PP-1
    "hombres": [(22.5, -62.0), (22.5, -46.0), (32.0, -46.0), (32.0, -14.0), (-1.8, -14.0), (-1.8, 19.0),
                (-1.8, 20.4), (-0.7, 21.2), (-0.7, 23.6), (-12.55, 23.6), (-12.55, 28.6), (-12.45, 33.4)],
    "a planta": [(-12.25, 28.6), (-12.25, 23.9), (0.0, 23.9)],
    "mujeres": [(-7.8, 23.6), (-7.8, 27.0), (-9.8, 30.5)],
    "comedor": [(-5.6, 23.9), (-5.6, 25.45), (-3.0, 25.45), (-3.0, 30.0)],
    "oficinas": [(-9.1, 23.6), (-9.1, 21.2), (-12.0, 21.2)],
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
        "Donde un hilo corta un flujo (cuerpos de carros, cúpulas, láseres, lazo de pintura) hay una",
        "senda peatonal X demarcada (cebra amarilla IRAM 10005, espejo y prioridad peatonal).",
        f"Cruces de hilos con flujos verificados por cálculo sobre el modelo: todos en {len(L.SENDAS)} sendas.",
        "Recargas ocupa el ángulo SO de la nave: su personal entra por el PC y usa los sanitarios del",
        "bloque de servicios. El mostrador tiene portón propio (RC-1): el público no entra a la planta.",
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
for _c in ("M04", "M15", "M16", "M06", "M08", "M09", "M10", "M11", "M12", "C01", "C02", "C03", "C04", "C05", "C08",
           "B01", "B01b", "B02", "B03", "E09a", "E09b", "E09c", "B04", "A06", "B06", "B14", "A11", "B08", "B10",
           "P01", "P02", "P03", "P04", "P06", "P08", "T01", "T02", "T03", "T04", "T05", "T07", "T08", "T09", "T10",
           "T11", "T12", "T13"):
    ASME[_c] = "O"
for _c in ("C06", "B09", "P09", "T06", "Q01", "C09"):
    ASME[_c] = "I"
for _c in ("A07", "B07", "C07"):
    ASME[_c] = "OI"
for _c in ("C12", "P07"):
    ASME[_c] = "D"
ALMACENES = ("AL-1H", "AL-1R", "PÑ", "AL-2", "QP", "AL-3", "S4", "AL-C", "RC-DP")

CURSOGRAMAS = {
    "S2 - Matafuegos ABC 2,5 / 5 / 10 kg": [
        ("A", "Hojas LAF (rack frente a la guillotina)", "AL-1R"), ("O", "1 Corte de cuerpo", "M04"),
        ("D", "Pulmón de cuerpos cortados", "PU-1"), ("O", "2 Numerado", "B01"), ("D", "Pulmón", "PU-2"),
        ("O", "3 Cilindrado", "B02"), ("D", "Pulmón", "PU-3"), ("O", "4 Soldadura longitudinal", "B03"),
        ("D", "Pulmón", "PU-4"), ("O", "9 Encastre de fondo", "E09"), ("O", "10 Bordoneado", "B04"),
        ("O", "11 Soldadura circ. (con la cúpula)", "A06/B06"), ("D", "Pulmón", "PU-5"),
        ("OI", "12 Prueba hidráulica 100 %", "A07/B07"), ("D", "Pulmón", "PU-6"), ("O", "13 Secado", "B14/A11"),
        ("D", "Pulmón", "PU-7"), ("O", "14 Granallado", "B08"), ("I", "15 Detección de defectos", "B09"),
        ("O", "16 Corrección (sólo defectuosos)", "B10"), ("D", "Pulmón a pintura", "PU-8"),
        ("O", "17 Pintura en polvo (lazo)", "P01-P08"), ("D", "Pulmón de pintados", "PU-9"),
        ("O", "18-23 Terminación (ver S1)", "T01-T10"), ("O", "24 Envolvedora", "T11"),
        ("A", "Almacén de PT", "AL-3"), ("T", "Expedición", "M1/M2")],
    "S1 - Matafuegos ABC 1 kg (fabricados)": [
        ("A", "Caño en cantiléver (frente al láser)", "AL-1R"), ("O", "5 Corte láser de caño", "M15/M16"),
        ("D", "Pulmón", "PU-L"), ("O", "9-17 Línea común (igual que S2)", "E09-P08"),
        ("O", "18 Carga de polvo", "T01"), ("O", "19 Ensamblaje", "T03/T04"), ("O", "20 Presurización con N₂", "T05"),
        ("I", "21 Hermeticidad", "T06"), ("O", "22 Etiquetado", "T07"), ("O", "23 Embalaje y palletizado", "T08/T09"),
        ("O", "24 Envolvedora", "T11"), ("A", "Almacén de PT", "AL-3"), ("T", "Expedición", "M1/M2")],
    "Subconjunto cúpulas y fondos 1-10 kg": [
        ("A", "Flejes (porta-flejes frente a la prensa)", "AL-1R"),
        ("O", "6 Desbobinado, enderezado y embutido", "M06-M08"), ("D", "Fondos al pulmón", "PU-K"),
        ("T", "Fondos al encastre (paso 9)", "-"), ("O", "7 Preparación de cuello", "M09/M10"),
        ("O", "8 Soldadura de cuello en la cúpula", "M11/M12"), ("D", "Cúpulas con cuello", "PU-C"),
        ("T", "Cúpulas a la soldadura circ. (paso 11)", "-")],
    "S3 - Matafuegos ABC rodantes 25 / 50 / 70 / 100 kg": [
        ("O", "1 Corte de cuerpo (guillotina)", "M04"), ("D", "Pulmón", "PU-1"), ("T", "Cruce al sector de carros", "-"),
        ("O", "C1 Cilindrado 4 rodillos", "C01"), ("O", "C2 Punteo, refuerzo y estructura", "C02/C03"),
        ("O", "C3 Soldadura longitudinal", "C04"), ("O", "C4 Soldadura circ. (casquetes)", "C05"),
        ("I", "C5 Inspección de costuras", "C06"), ("OI", "C6 Prueba hidráulica 4,0 MPa", "C07"),
        ("O", "C7 Marcado", "C08"), ("D", "Espera del pintor", "C12"), ("T", "Pintura tercerizada (P6 -> P8)", "-"),
        ("O", "C8 Carga de polvo", "T02"), ("O", "C9 Armado de ruedas y manguera", "T12"),
        ("O", "C10 Presurización y etiquetado", "T13"), ("T", "Expedición", "P9")],
    "S4 - Tercerizados revendidos (CO₂, agua, AFFF, K, agente limpio)": [
        ("T", "Recepción", "M3"), ("I", "Control de recepción y sello IRAM", "S4"), ("A", "Stock", "S4"),
        ("T", "Expedición con el pedido", "M1/M2")],
    "RC - Recargas (servicio)": [
        ("T", "Recepción", "RC-1"), ("I", "R1 Clasificación e inspección visual", "RC-RE"), ("O", "R4 Desarme", "RC-DE"),
        ("OI", "R2 Descarga y ensayo de funcionamiento", "RC-DC"), ("OI", "R7 PH, secado y Puffer", "RC-PH"),
        ("O", "R3 / R12-R14 Recarga por familia", "RC-PV/GA/LQ"), ("O", "R9 Ensamblaje y R10 presurización", "RC-EN"),
        ("I", "R22 Peso y R11 hermeticidad", "RC-EN"), ("O", "R20 Retoque y R21 etiquetado", "RC-EN/RP"),
        ("A", "Para entregar", "RC-DP"), ("T", "R17 Despacho", "RC-2")],
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
    for cod, nom, r in (("S1", "S1 1 kg (corte de caño)", L.R(16.6, 29.6, 29.5, 35.0)),
                        ("S2", "S2 2,5-10 kg (cuerpo)", L.R(16.6, 24.6, 39.3, 29.6)),
                        ("S12", "S1 + S2 línea común", L.R(34.3, 34.9, 87.8, 39.8)),
                        ("S3", "S3 rodantes", L.R(18.1, 0.1, 34.2, 19.4)), ("S4", "S4 tercerizados", L.R(34.1, 0.1, 40.1, 6.7)),
                        ("RC", "RC recargas", L.R(0.1, 0.1, 18.1, 19.4))):
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
