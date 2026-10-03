"""Láminas por faceta (v5): cada lámina muestra un aspecto distinto de la planta, no la misma planta repetida.

FL_PI_02  Flujos de materiales y de operaciones (MP, SE, PT, scrap, efluentes; ASME y cursogramas)
FL_PI_03  Personal, evacuación y señalización (DIR, sendas, medios de escape, IRAM 10005, accesibilidad)
FL_PI_04  Logística de MP y de PT (detalles 1:50, descarga y carga a máquina, políticas de stock, expedición)
FL_PI_05  Servicios, administración y apoyo a la línea (todo en planta baja, 1:50)
"""

import math

from ezdxf.enums import TextEntityAlignment

from . import layout as L
from . import calculos as C
from . import dibujo as D
from . import planos as PL
from . import formal as FO
from .planos import f, hoja, titulo_hoja, Columna, leyenda_flujos, globo, globo_papel, simbolo

A = TextEntityAlignment


# ================================================================ utilidades
def detalle(h, k, win, p0, titulo, eq_h=2.2, exterior=True, sectores=True, extra=None):
    """Planta de detalle de la ventana `win` (x0, y0, x1, y1 en m) a escala 1:k, recortada y enmarcada.
    Los rellenos se recortan primero (quedan debajo); `extra(pl)` dibuja flujos u otros agregados."""
    xa, ya, xb, yb = win
    pl = D.Plano(h, k, (xa, ya), p0)
    antes = D.handles(pl.m)
    if sectores:
        D.sectores(pl, relleno=True)
    D.locales(pl, rotulos=False, relleno=True)
    D.recortar(pl, antes, xa, ya, xb, yb)
    antes = D.handles(pl.m)
    D.pasillos(pl, demarcacion=True, rotulos=True, h=eq_h * 0.8)
    D.equipos(pl, rotulos=True, h=eq_h, fino=True)
    D.vehiculos(pl)
    D.muros(pl)
    D.puertas(pl, etiquetas=True, h=eq_h)
    D.ejes(pl, r_glob=3.5, sobresale=2.0, completo=False)
    if exterior:
        for cod, nom, r, tipo in L.EXTERIOR:
            if r.x1 < xa or r.x0 > xb or r.y1 < ya or r.y0 > yb:
                continue
            pl.rect(r, "A-EXTERIOR")
            pl.texto(f"{cod} {nom}", (r.c[0], r.c[1]), eq_h * 0.8, A.MIDDLE_CENTER)
    for s in L.SECTORES + L.LOCALES:
        r = s.rect
        if xa <= r.x0 and r.x1 <= xb + 2 and ya - 2 <= r.y0 and r.y1 <= yb + 2:
            pl.texto(f"{s.cod} {s.nombre}" if r.w > 6 else s.cod, (r.x0 + 0.2, r.y1 - 0.2), eq_h * 0.8,
                     A.TOP_LEFT, "A-SECTOR-TXT")
    if extra:
        extra(pl)
    D.recortar(pl, antes, xa, ya, xb, yb)
    a, b = pl.P(xa, ya), pl.P(xb, yb)
    pl.m.add_lwpolyline([a, (b[0], a[1]), b, (a[0], b[1])], close=True, dxfattribs={"layer": "A-TEXTO"})
    pl.texto(titulo, (a[0], b[1] + 3.0), 4.0, A.BOTTOM_LEFT, papel=True)
    return pl


def pasos_papel(pl, x, y, pasos, titulo, ancho=118, h=2.3):
    """Lista numerada (globo + texto) en papel; devuelve la y final."""
    pl.texto(titulo, (x, y), 3.2, A.BOTTOM_LEFT, papel=True)
    y -= 6.0
    for n, txt in pasos:
        globo_papel(pl, n, (x + 3, y), 2.2)
        lineas = _cortar(txt, int(ancho / (h * 0.62)))
        for i, ln in enumerate(lineas):
            pl.texto(ln, (x + 8, y - i * h * 1.5), h, A.MIDDLE_LEFT, papel=True)
        y -= 5.2 + (len(lineas) - 1) * h * 1.5
    return y


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


# ================================================================ FL_PI_02 flujos y operaciones
def fl_pi_02(doc, ox):
    h, pl = PL.lamina_flujo(doc, ox, "FL_PI_02", "FL_PI_02 - FLUJOS DE MATERIALES Y DE OPERACIONES",
                            "Flujos y operaciones", "MP, SE, PT, scrap y efluentes; ASME y cursogramas - año 10",
                            "Diagrama de flujo y de proceso")
    PL.fondo(pl, relleno=True, rot_eq=False)
    PL.flujos_materiales(pl)
    for e in L.EQUIPOS:
        t = PL.ASME.get(e.cod)
        if t:
            simbolo(pl, t, e.rect.c, 1.1)
    for s in L.SECTORES:
        if s.cod in PL.ALMACENES:
            simbolo(pl, "A", s.rect.c, 1.3)
    D.rotulos_sector(pl, h=1.6, areas=False)
    for n, xy, txt in PL.MARCAS_03:
        globo(pl, n, xy)
    col = Columna(h, pl)
    x, y = col.x, col.y
    y = leyenda_flujos(pl, x, y, ["MP", "SE", "RET", "PT", "SCRAP", "EFL-L", "EFL-G"])
    y -= 3
    pl.texto("Flujos numerados", (x, y), 3.2, A.BOTTOM_LEFT, papel=True)
    y -= 5.0
    for n, xy, txt in PL.MARCAS_03:
        globo_papel(pl, n, (x + 3, y))
        pl.texto(txt, (x + 8, y), 2.0, A.MIDDLE_LEFT, papel=True)
        y -= 4.4
    y -= 2
    pl.texto("Símbolos ASME", (x, y), 3.2, A.BOTTOM_LEFT, papel=True)
    y -= 6
    for i, (t, txt) in enumerate((("O", "Operación"), ("I", "Inspección"), ("OI", "Operación e inspección"),
                                  ("T", "Transporte"), ("D", "Demora / pulmón"), ("A", "Almacenamiento"))):
        xx = x + (i % 3) * 92
        simbolo(pl, t, (xx + 3, y), 1.8, papel=True)
        pl.texto(txt, (xx + 8, y), 2.2, A.MIDDLE_LEFT, papel=True)
        if i % 3 == 2:
            y -= 5.5
    y = pl.parrafo(["Criterio: cada MP entra por el portón más cercano a la máquina que la transforma; recorrido en U",
                    "con 0 cruces entre MP, SE y PT (verificado sobre el modelo). Las líneas de MP que se tocan dentro",
                    "del almacén son maniobras del mismo autoelevador, no cruces de tránsito. Pintura según el esquema",
                    "cotizado por Electricolor (carga, cabina, 2 hornos, descarga); no lleva túnel de pretratamiento."],
                   x, y - 1, 2.0)
    y -= 6
    xx, fila_alta = x, 0
    for i, (nom, pasos) in enumerate(PL.CURSOGRAMAS.items()):
        if i == 3:
            y -= fila_alta + 12
            xx, fila_alta = x, 0
        cols = [("", 7, "c"), ("Paso", 57, "l"), ("Dónde", 25, "c")]
        filas = [["", d, w] for t, d, w in pasos]
        yb = pl.tabla(xx, y, cols, filas, 3.5, 1.7, nom if len(nom) < 44 else nom[:42] + "…", h_tit=2.4)
        for j, (t, d, w) in enumerate(pasos):
            simbolo(pl, t, (xx + 3.5, y - (j + 1.5) * 3.5), 1.2, papel=True)
        cuenta = {t: sum(1 for p in pasos if p[0] == t) for t in ("O", "I", "OI", "T", "D", "A")}
        pl.texto("O {O} · I {I} · O/I {OI} · T {T} · D {D} · A {A}".format(**cuenta), (xx, yb - 2.0), 1.9,
                 A.TOP_LEFT, papel=True)
        fila_alta = max(fila_alta, y - yb)
        xx += 92
    return h


# ================================================================ FL_PI_03 personal, evacuación y señalización
SENAL_TXT = {"obl": "Obligación (azul, círculo)", "adv": "Advertencia (amarillo, triángulo)",
             "pro": "Prohibición (rojo, círculo con barra)", "sal": "Salvamento y evacuación (verde)"}


def fl_pi_03(doc, ox):
    h, pl = PL.lamina_flujo(doc, ox, "FL_PI_03", "FL_PI_03 - PERSONAL, EVACUACIÓN Y SEÑALIZACIÓN",
                            "Personal y seguridad", "DIR, medios de escape, protección contra incendio, IRAM 10005",
                            "Plano de seguridad e higiene")
    PL.fondo(pl, relleno=False, rot_eq=False)
    for fl in L.FLUJOS:
        pl.pl(fl.pts, "F-RET")
    for pts in PL.TRONCOS.values():
        pl.pl(pts, "F-PERSONAL")
    grupos = []
    for nom, main, br in L.HILOS:
        pl.pl(main, "F-PERSONAL")
        mx = 0.0
        for a, b, c_, d in br:
            pl.pl([(a, b), (c_, d)], "F-PERSONAL")
            pl.relleno(PL.circ_pts((c_, d), 0.3), D.RGB_FLUJO["PER"], "F-PERSONAL")
            mx = max(mx, math.dist((a, b), (c_, d)))
        grupos.append((nom, C.largo(main) + mx, main))
    # protección contra incendio, salidas y señalización
    ext = C.extintores()
    for i, c in enumerate(ext["puntos"] + FO.EXT_ANEXOS):
        FO.extintor(pl, c, i + 1, r=0.45)
    for p in L.PUERTAS:
        if p.tipo == "emergencia":
            m = (p.a + p.b) / 2
            d = {"N": (0, 1), "S": (0, -1), "O": (-1, 0), "E": (1, 0)}[p.muro]
            o = {"N": (m, L.NAVE_A - 1.2), "S": (m, 1.2), "O": (1.2, m), "E": (L.NAVE_L - 1.2, m)}[p.muro]
            FO.salida(pl, o, d)
    D.senales(pl, h=1.2, r=0.55)
    pr = next(r for c, n, r, t in L.EXTERIOR if c == "PR")
    pl.rect(pr, "S-ESCAPE")
    pl.texto("PUNTO DE REUNIÓN", pr.c, 1.8, A.MIDDLE_CENTER, "S-ESCAPE")
    D.rotulos_sector(pl, h=1.5, areas=False)
    # columna de referencias
    col = Columna(h, pl)
    x, y = col.x, col.y
    pl.texto("Referencias", (x, y), 3.5, A.BOTTOM_LEFT, papel=True)
    y -= 6
    pl.m.add_lwpolyline([(x, y), (x + 16, y)], dxfattribs={"layer": "F-PERSONAL"})
    pl.texto("Hilo de personal (DIR) y puesto de trabajo", (x + 20, y), 2.2, A.MIDDLE_LEFT, papel=True)
    y -= 5
    pl.texto("X1..: senda peatonal (cebra) donde un hilo cruza un flujo", (x + 20, y), 2.2, A.MIDDLE_LEFT, papel=True)
    y -= 5
    pl.texto("Punto rojo numerado: extintor ABC 10 kg   BIE: boca de incendio equipada   □: pulsador de alarma",
             (x, y), 2.1, A.MIDDLE_LEFT, papel=True)
    y -= 6
    pl.texto("Señales (IRAM 10005-1: formas y colores de seguridad)", (x, y), 2.8, A.BOTTOM_LEFT, papel=True)
    y -= 5
    vistos = {}
    for tipo, cod, *_r, txt in L.SENALES:
        vistos.setdefault((tipo, cod), txt)
    for (tipo, cod), txt in sorted(vistos.items()):
        pl.texto(f"{SENAL_TXT[tipo].split(' (')[0]} · {cod}: {txt}", (x + 2, y), 2.0, A.MIDDLE_LEFT, papel=True)
        y -= 3.6
    e = C.escape()
    y -= 9
    cols = [("Medios de escape (Dec. 351/79 anexo VII)", 112, "l"), ("Valor", 40, "c")]
    filas = [["Recorrido máximo real a una salida (grilla 0,5 m, tabiques y equipos)", f"{f(e['peor_m'], 1)} m ≤ 40"],
             ["Ocupación (16 m² por persona en la nave)", f"{e['N']} personas"],
             ["Unidades de ancho de salida / ancho mínimo", f"{e['unidades']} / {f(e['ancho_min'], 2)} m"],
             ["Salidas de emergencia de 1,10 m con barral antipánico", str(e["salidas_emergencia"])],
             ["Extintores ABC 10 kg (1 cada 200 m², recorrido ≤ 20 m)", str(len(ext['puntos']) + len(FO.EXT_ANEXOS))],
             ["Bocas de incendio equipadas / pulsadores de alarma", f"{len(L.BIE)} / {len(L.PULSADORES)}"],
             ["Sanitario accesible con ducha (bloque de servicios)", "1"]]
    y = pl.tabla(x, y, cols, filas, 4.0, 2.0, "Evacuación y protección contra incendio")
    cols = [("Hilo (grupo de puestos)", 70, "l"), ("Desde PP-1 (m)", 26, "c")]
    filas = [[nom, f(lg, 0)] for nom, lg, main in grupos]
    yb = pl.tabla(x, y - 10, cols, filas, 4.0, 2.0, "Longitud de los hilos")
    san = C.sanitarios()
    cols3 = [("Artefacto", 36, "l"), ("H req.", 15, "c"), ("H proy.", 15, "c"), ("M req.", 15, "c"), ("M proy.", 15, "c")]
    filas3 = [[k.capitalize(), san["req_H"][k], san["proy"]["H"][k], san["req_M"][k], san["proy"]["M"][k]]
              for k in ("inodoros", "lavabos", "orinales", "duchas")]
    filas3.append(["Armarios (art. 50)", san["armarios_req"]["H"], san["armarios_proy"]["H"], san["armarios_req"]["M"],
                   san["armarios_proy"]["M"]])
    pl.tabla(x + 104, y - 10, cols3, filas3, 4.0, 2.0, f"Sanitarios de vestuarios (art. 49): {san['H']} H y {san['M']} M")
    pl.parrafo(["Además: sanitarios de planta (este) sólo de hombres (2 inodoros, 2 mingitorios, 2 lavabos)",
                "y de mujeres (1 + 1), a < 25 m de pintura, terminación y PT. Lockers: 1 por empleado.",
                "Cada operario tiene 1,0 m libre detrás de su puesto: ninguna calle ni material ajeno pasa",
                "por su espalda (verificado). Mamparas ignífugas en todos los puestos de soldadura."],
               x, yb - 6, 2.0)
    return h


# ================================================================ FL_PI_04 logística de MP y PT
PASOS_MP = [
    (1, "Camión en el alero norte (semi 18,6 m o chasis): entró por G1, se pesó en la báscula y se controla el remito."),
    (2, "Paquetes de hojas (≤ 2 t): autoelevador de MP (3 t, prolongaciones de horquilla) por el lado largo "
        "(c = 0,75 m). Sin puente grúa: 1,5 paquetes/día no lo justifican."),
    (3, "Paquete a su posición: 4 formatos de alto consumo en AL-1H frente a A2; el LAC 4,75 de carros en AL-1L (A1). "
        "Un formato por posición, 4 alturas sobre tacos, FIFO con tarjeta de color."),
    (4, "Del AL-1H a la mesa elevadora de la guillotina: el autoelevador cruza A2 y apoya el paquete; las hojas se "
        "deslizan sobre la mesa de bolas (no se levantan a mano)."),
    (5, "Rollos de fleje: pluma del autoelevador con gancho C (ojo vertical) a la cuna de AL-1F (3 niveles) por A1."),
    (6, "Rollo al desbobinador SHIMEQ de 2 mandriles: se carga el mandril libre mientras el otro trabaja."),
    (7, "Atados de caño 6 m (≤ 600 kg): el autoelevador entra por P1 (7,20 m de ancho) con el atado atravesado y lo "
        "apoya en el cantiléver interior desde AN. El caño nunca queda afuera."),
    (8, "Carro porta-tubos de 6,5 m: del cantiléver por AN, A2 y PO-L a los caballetes (esquina AN-A2: 5,0 + 3,6 m "
        "-> 12,1 m; A2-PO-L: 3,6 + 1,4 m -> 6,8 m; ambas > 6,5 m)."),
    (9, "Cuellos y roscas (cajas) y alambre MAG en la pared oeste (A1); salen con la zorra del milk run a los puestos."),
    (10, "Arcal 21: baterías a la jaula ventilada AL-GS; la que se conecta va al colector de la sala SC por el patio "
         "norte (puerta PG). El N₂ no entra acá: va al almacén previo a la carga (SP-1)."),
    (11, "Scrap: contenedor en cada puesto que lo genera (guillotina, láseres, prensa); el autoelevador de MP lo lleva "
         "al volquete junto a P1, la salida más cercana a los tres. Nada de scrap queda en el almacén."),
    (12, "Nafta e insumos del autoelevador de MP en el armario de inflamables al final del pasillo central (AL-1N)."),
]
PASOS_PT = [
    (1, "Palletizado en T08-T10 (fin de terminación) por SKU: 360 u de 1 kg o 84 de 5 kg por pallet."),
    (2, "Envolvedora EDOS PS5 (T11) y etiqueta de pallet con lote y destino."),
    (3, "Autoelevador de PT por T3 al rack RK3 de alta rotación (1 y 5 kg)."),
    (4, "Stock de temporada (oct-nov para diciembre) en RK2 y cara este de RK1, por T1 y T2 desde el pasillo central."),
    (5, "Pedido del día: se arma en la calle EX frente al muelle único P3 (8 pallets por camión)."),
    (6, "Muelle P3: expedición de 13 a 17 h (7 camiones por semana en 2035) y recepción de 7 a 10 h, así entrada y "
        "salida no se cruzan en EX."),
    (7, "Recepción por P3: válvulas, manómetros y pescantes a AL-2; polvos, agentes y N₂ por AT al almacén previo a la "
        "carga (SP-1); embalaje a EMB; casquetes a RK1 (se toman desde S3); revendidos a S4."),
    (8, "Carros: salen al pintor y vuelven por la calle PO-C; los terminados salen de S-TC por EX al muelle."),
    (9, "Embalaje diferenciado: matafuegos nuevos y revendidos en EMB; carros en S-TC; recargas en RC-RD. Precintos "
        "como insumo de PT en los tres."),
    (10, "Las recargas no usan el muelle: entran y salen en utilitarios por su portón P2 (milk run)."),
]


def fl_pi_04(doc, ox):
    h = hoja(doc, "A0", ox, "Logística de MP y de PT", "Descarga, almacén, carga a máquina, políticas de stock y "
             "expedición", "FL_PI_04", 1, 2, "1:50", "Plano de detalle")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI_04 - LOGÍSTICA DE MATERIA PRIMA Y DE PRODUCTO TERMINADO",
                "Detalles 1:50 del almacén de MP y de la expedición, con la secuencia de cada movimiento. "
                "Flota calculada por métodos y tiempos.")
    # ---- detalle MP
    win = (-1.5, 18.8, 23.0, 49.0)                      # almacén de MP, carga a máquina, scrap y alero de P1
    p0 = (h.fx0 + 8, h.fy1 - 36 - (win[3] - win[1]) * 20)
    def _mp(p):
        for fl in L.FLUJOS:
            if fl.cat in ("MP", "SCRAP", "SE"):
                p.flujo(fl.pts, fl.cat, cada=8.0, largo=3.0, ancho=1.6)
    pm = detalle(h, 50, win, p0, "DETALLE 1 - ALMACÉN DE MP Y CARGA A MÁQUINA - 1:50", extra=_mp)
    for n, xy in ((1, (14.0, 49.5)), (2, (10.9, 45.2)), (3, (8.2, 33.5)), (4, (11.6, 27.2)), (5, (3.8, 31.0)),
                  (6, (12.0, 36.6)), (7, (7.5, 41.0)), (8, (8.0, 39.6)), (9, (3.0, 29.0)), (10, (3.6, 42.6)),
                  (11, (20.8, 26.0)), (12, (1.2, 18.4))):
        globo(pm, n, xy, 3.0)
    pm.cota((2.0, 24.0), (5.6, 24.0), -2.0, True, texto="A1 <>")
    pm.cota((9.1, 24.0), (12.7, 24.0), -2.0, True, texto="A2 <>")
    # ---- detalle PT
    win2 = (33.5, -3.0, 51.5, 20.0)
    p02 = (p0[0] + (win[2] - win[0]) * 20 + 14, h.fy1 - 36 - (win2[3] - win2[1]) * 20)
    def _pt(p):
        for fl in L.FLUJOS:
            if fl.cat in ("PT", "MP"):
                p.flujo(fl.pts, fl.cat, cada=8.0, largo=3.0, ancho=1.6)
    pt = detalle(h, 50, win2, p02, "DETALLE 2 - ALMACÉN DE PT Y EXPEDICIÓN - 1:50", extra=_pt)
    for n, xy in ((1, (51.0, 7.0)), (2, (49.0, 12.0)), (3, (46.75, 15.5)), (4, (37.1, 15.5)), (5, (44.0, 4.6)),
                  (6, (42.1, -1.5)), (7, (35.9, -1.5)), (8, (34.5, 19.4))):
        globo(pt, n, xy, 3.0)
    for c_ in ("T1", "T2", "T3", "EX"):
        p = next(p for p in L.PASILLOS if p.cod == c_)
        r = p.rect
        if r.w < r.h:
            pt.cota((r.x0, r.y1 - 2.0), (r.x1, r.y1 - 2.0), 0.0, True, texto=f"{c_} <>")
        else:
            pt.cota((r.x1 - 1.5, r.y0), (r.x1 - 1.5, r.y1), 0.0, False, texto=f"{c_} <>")
    # ---- textos y tablas
    # debajo del detalle 2: flota y métodos y tiempos (izquierda), secuencias (derecha)
    xr = p02[0] + 160
    y = p02[1] - 10
    y = pasos_papel(pt, xr, y, PASOS_MP, "Secuencia de la MP (detalle 1)", ancho=h.fx1 - xr - 10)
    y = pasos_papel(pt, xr, y - 4, PASOS_PT, "Secuencia del PT (detalle 2)", ancho=h.fx1 - xr - 10)
    xr, y = p02[0], p02[1] - 14 - 8 * 3.6 - 14
    M_ = C.manejo()
    cols = [("Unidad de carga", 50, "l"), ("Medio", 24, "l"), ("Viajes/día", 15, "c"), ("m", 10, "c"),
            ("min/día", 14, "c")]
    filas = [[r_["carga"][:34], r_["medio"], f(r_["viajes"], 1), f(r_["dist"], 0), f(r_["min_dia"], 0)]
             for r_ in M_["filas"]]
    y = pt.tabla(xr, y - 6, cols, filas, 3.4, 1.65, "Métodos y tiempos (día pico 2035)")
    oc = M_["ocup"]
    y = pt.parrafo([f"Ocupación de un turno: autoelevador de MP {f(oc['Autoelevador MP'] * 100, 0)} %, de carros y "
                    f"recargas {f(oc['Autoelevador carros'] * 100, 0)} %, de PT {f(oc['Autoelevador PT'] * 100, 0)} %.",
                    "Uno por frente (MP, carros y recargas, PT): ninguno cruza el frente de otro;",
                    "el de MP lleva prolongaciones, pluma con percha (balancín) y gancho C."], xr, y - 2, 1.9)
    # políticas de stock debajo del detalle 1
    yb = p0[1] - 14
    cols = [("Artículo", 58, "l"), ("Consumo", 26, "c"), ("Unidad de compra", 46, "l"), ("Sistema", 58, "l"),
            ("Se pide", 44, "l"), ("Stock máx.", 18, "c")]
    filas = [[r_["sku"], r_["consumo"], r_["unidad"], r_["sistema"], r_["pedido"], r_["max"]]
             for r_ in C.politicas_stock()]
    yb = pm.tabla(p0[0], yb, cols, filas, 3.6, 1.75, "Políticas de stock por tipo de chapa, fleje y caño (2035)")
    pm.parrafo([
        "Distribución en AL-1H (de sur a norte, el más usado junto a la mesa elevadora): 1) LAF 1,6 × 1000 × 2000 (5 kg);",
        "2) LAF 1,25 × 1220 × 2440 (2,5 kg); 3) LAF 2,0 × 1500 × 3000 (10 kg); 4) LAC 3,2 × 1500 × 3000 (25-50 kg).",
        "El LAC 4,75 × 1500 × 3000 (70-100 kg, 1 paquete cada 2 meses) en AL-1L. Un formato por posición.",
        "Entregas quincenales de Pradecon (17,6 t) en lugar de una mensual de 35 t: baja el stock máximo a la mitad.",
        "Flejes de bajo consumo (2,0 × 249 y 2,0 × 300 mm): rollos de 250-300 kg para no tener 5 meses de stock.",
        "Semáforo de antigüedad: verde < 4 semanas, amarillo 4-6, rojo > 6 (se usa primero y se inspecciona óxido)."],
        p0[0], yb - 4, 2.0)
    # flota
    cols = [("Equipo de manipulación", 70, "l"), ("Cant.", 12, "c"), ("Dónde", 60, "l")]
    filas = [["Autoelevador de MP 3 t a nafta, mástil triplex", "1", "Almacén de MP, carga a máquina, scrap"],
             ["  prolongaciones 2,4 m, pluma con percha y gancho C", "1", "Hojas, rollos y atados de caño"],
             ["Autoelevador de carros y recargas 2,5 t a nafta", "1", "Muelle P3, calle PO-C, carros y recargas"],
             ["Autoelevador de PT 2,5 t a nafta, mástil triplex", "1", "Racks de PT, muelle P3, AL-2 y SP-1"],
             ["Transpaletas manuales 2,5 t", "2", "P4 (pintura y granalla) y terminación"],
             ["Carros porta-cilindros / zorras / porta-tubos", "26 / 5 / 1", "Línea, milk run y caños"],
             ["Carros de scrap 0,5 m³ / contenedor 1 m³", "3 / 1", "Láseres y prensa / guillotina"],
             ["Armarios de nafta e insumos", "2", "AL-1N (MP) y AL-PN (PT y carros)"]]
    pt.tabla(p02[0], p02[1] - 14, cols, filas, 3.6, 1.75, "Flota (dibujada = calculada)")
    return h


# ================================================================ FL_PI_05 servicios, oficinas y apoyo a la línea
def fl_pi_05(doc, ox):
    h = hoja(doc, "A0", ox, "Servicios, oficinas y apoyo", "Bloque de servicios y administración, fila central "
             "(mantenimiento, calidad, supervisor, PCP), sanitarios de planta y sala de compresores", "FL_PI_05", 1, 1,
             "1:50", "Plano de detalle", "Mampostería / estructura metálica")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI_05 - SERVICIOS AL PERSONAL, OFICINAS Y APOYO A LA LÍNEA",
                "Todo en planta baja (sin entrepiso). Circuito del personal, vestuarios con 1 locker por empleado y "
                "sanitarios (Dec. 351/79 arts. 49-50), accesibilidad (Ley 24.314), supervisor y PCP sobre la línea.")
    # ---- detalle 1: bloque de servicios y administración
    win = (-18.6, 18.4, 0.8, 35.8)
    p0 = (h.fx0 + 8, h.fy1 - 36 - (win[3] - win[1]) * 20)
    pl = detalle(h, 50, win, p0, "DETALLE 1 - SERVICIOS Y ADMINISTRACIÓN - 1:50", eq_h=2.4, sectores=False)
    for s in L.LOCALES:
        r = s.rect
        if r.x1 < 0.5 and s.cat != "CIRC":
            pl.texto(s.cod, (r.x0 + 0.15, r.y1 - 0.15), 2.6, A.TOP_LEFT)
            pl.texto(f"{f(r.area, 1)} m²", (r.x1 - 0.15, r.y0 + 0.15), 2.2, A.BOTTOM_RIGHT)
    pl.texto("VENTANA A LA NAVE (vista del pasillo central)", (-0.4, 20.2), 1.9, A.MIDDLE_CENTER, rot=90)
    xs = sorted({round(v, 2) for s in L.LOCALES if s.rect.x1 < 0.5 and s.rect.y0 < 23.0 for v in (s.rect.x0, s.rect.x1)})
    pl.cadena(xs, 19.0, -3.0, True)
    ys = sorted({round(v, 2) for s in L.LOCALES if s.rect.x0 < -17 for v in (s.rect.y0, s.rect.y1)})
    pl.cadena(ys, -18.0, -3.0, False)
    # ---- detalle 2: fila central (mantenimiento + pañol, calidad, cuarentena, supervisor y PCP)
    win2 = (40.4, 24.0, 69.0, 33.8)
    p02 = (p0[0] + (win[2] - win[0]) * 20 + 16, h.fy1 - 36 - (win2[3] - win2[1]) * 20)
    pa = detalle(h, 50, win2, p02, "DETALLE 2 - FILA CENTRAL: MANTENIMIENTO, PAÑOL, CALIDAD, SUPERVISOR Y PCP - 1:50",
                 eq_h=2.2)
    for cod in ("MT", "PÑL", "Q", "QR", "SUP", "PCP"):
        r = next(s_.rect for s_ in L.SECTORES if s_.cod == cod)
        pa.texto(f"{f(r.area, 1)} m²", (r.x1 - 0.15, r.y0 + 0.15), 2.0, A.BOTTOM_RIGHT)
    pa.cota((41.2, 24.8), (68.4, 24.8), -6.0, True)
    # ---- detalle 3: sanitarios de planta y ducha de emergencia
    win3 = (69.8, 6.2, 75.0, 19.6)
    p03 = (p02[0], p02[1] - 30 - (win3[3] - win3[1]) * 20)
    ps = detalle(h, 50, win3, p03, "DETALLE 3 - SANITARIOS DE PLANTA (H Y M) - 1:50", eq_h=2.4, sectores=False)
    for s in L.LOCALES:
        if s.cod.startswith("SN-"):
            ps.texto(s.cod, (s.rect.x0 + 0.1, s.rect.y1 - 0.1), 2.4, A.TOP_LEFT)
    # ---- detalle 4: sala de compresores y colectores
    win4 = (47.4, 39.2, 66.2, 44.6)
    p04 = (p03[0] + (win3[2] - win3[0]) * 20 + 70, p02[1] - 30 - (win4[3] - win4[1]) * 20)
    pc = detalle(h, 50, win4, p04, "DETALLE 4 - COMPRESORES Y COLECTORES DE GASES DE SOLDADURA - 1:50", eq_h=2.2)
    G = C.colector_gases()
    pc.texto(f"Colector al extremo oeste: {f(G['sc'], 0)} m de cañería a las 9 soldadoras "
             f"(en el centro de la sala serían {f(G['centro'], 0)} m)", (47.6, 39.5), 2.0, A.BOTTOM_LEFT)
    # ---- textos
    xr = p04[0]
    y = p04[1] - 22
    y = pasos_papel(pc, xr, y, [
        (1, "Ingreso por SV-1 (camino peatonal desde G4 y la garita); fichado en el hall."),
        (2, "Pasillo limpio: al sur limpieza, higiene y seguridad (con EPP y primeros auxilios), hall y administración; "
            "al norte vestuarios, sanitario accesible y comedor."),
        (3, "Vestuario: 1 locker por empleado (bloques de 10 columnas × 3 filas). Duchas en su propio local, "
            "separadas de inodoros y mingitorios; todo sólo desde el vestuario."),
        (4, "Duchas, inodoros, mingitorios y lavabos: cada grupo alineado sobre una misma pared húmeda."),
        (5, "Sanitario accesible con ducha a nivel donde estaba limpieza; se entra por el pasillo PS, que termina en "
            "la salida de emergencia SV-2."),
        (6, "Comedor: el office (bacha y lavamanos sobre la misma pared) junto a la puerta; las mesas al fondo."),
        (7, "Administración (compras, ventas, RRHH) contra la nave: ventana a lo largo del pasillo central y PP-1 a 6 m."),
        (8, "Supervisor en oficina propia y PCP separado, los dos con ventana a la línea; mantenimiento con su pañol "
            "pegado; calidad y cuarentena (con muestras y archivo) juntas."),
    ], "Circuito y criterios", ancho=h.fx1 - xr - 10)
    filas = [[f"{s.cod} {s.nombre}"[:46], f(s.rect.area, 1), s.nota[:70]] for s in L.LOCALES
             if s.cat != "CIRC" and not s.cod.startswith("RC")]
    filas += [[f"{s.cod} {s.nombre}"[:46], f(s.rect.area, 1), s.nota[:70]] for s in L.SECTORES
              if s.cod in ("MT", "PÑL", "Q", "QR", "SUP", "PCP", "SC")]
    pl.tabla(p0[0], p0[1] - 26, [("Local", 74, "l"), ("m²", 14, "r"), ("Equipamiento / criterio", 112, "l")], filas,
             3.6, 1.75, "Locales de servicios, administración y apoyo a la línea")
    return h
