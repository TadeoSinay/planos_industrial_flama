"""Láminas por faceta (v5): cada lámina muestra un aspecto distinto de la planta, no la misma planta repetida.

FL_PI_02  Flujos de materiales y de operaciones (MP, SE, PT, scrap, efluentes; ASME y cursogramas)
FL_PI_03  Personal, evacuación y señalización (DIR, sendas, medios de escape, IRAM 10005, accesibilidad)
FL_PI_04  Logística de MP y de PT (detalles 1:50, descarga y carga a máquina, políticas de stock, expedición)
FL_PI_05  Servicios al personal, oficinas y PCP (planta baja 1:50, entrepiso 1:50, núcleo sanitario de planta)
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
             ["Sanitarios accesibles (servicios, planta y entrepiso)", "3"]]
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
    pl.parrafo(["Además: núcleo sanitario de planta (este) con 2 inodoros, 2 mingitorios, 2 lavabos H,",
                "1 inodoro M, sanitario accesible y sala de limpieza, a < 25 m de pintura, terminación y PT.",
                "Cada operario tiene 1,0 m libre detrás de su puesto: ninguna calle ni material ajeno pasa",
                "por su espalda (verificado). Mamparas ignífugas en todos los puestos de soldadura."],
               x, yb - 6, 2.0)
    return h


# ================================================================ FL_PI_04 logística de MP y PT
PASOS_MP = [
    (1, "Camión en el alero norte (semi 18,6 m o chasis). Se pesa en la balanza de plataforma y se controla el remito."),
    (2, "Paquetes de hojas (≤ 2 t): autoelevador 3 t con prolongaciones de horquilla, por el lado largo (c = 0,75 m). "
        "Sin puente grúa: 1,5 paquetes/día no lo justifican."),
    (3, "Paquete a su posición de AL-1H (un formato por posición, 4 alturas sobre tacos, FIFO con tarjeta de color)."),
    (4, "Del AL-1H a la mesa elevadora de la guillotina: el autoelevador cruza A2 y apoya el paquete; las hojas se "
        "deslizan sobre la mesa de bolas (no se levantan a mano)."),
    (5, "Rollos de fleje: pluma del autoelevador con gancho C (ojo vertical) a la cuna de AL-1F, por ancho y espesor."),
    (6, "Rollo al desbobinador SHIMEQ de 2 mandriles: se carga el mandril libre mientras el otro trabaja (sin parar la prensa)."),
    (7, "Atados de caño 6 m (≤ 600 kg): el autoelevador los apoya, de costado y al aire libre, en el cantiléver CT del alero."),
    (8, "Carro porta-tubos (2 boguies): 1-2 viajes/día por P1-A2-PO-L a los caballetes de los láseres "
        "(gira de A2 a PO-L: un caño de 6,5 m pasa la esquina de 3,6 + 1,4 m)."),
    (9, "Insumos pesados (alambre MIG, cuplas, asientos) al rack de PÑ por A1; de ahí, el milk run al pañol de línea."),
    (10, "Basculantes de scrap de la guillotina y la prensa: el autoelevador los vuelca en el volquete del alero por P2."),
]
PASOS_PT = [
    (1, "Palletizado en T08-T10 (fin de terminación) por SKU: 360 u de 1 kg o 84 de 5 kg por pallet."),
    (2, "Envolvedora EDOS PS5 (T11) y etiqueta de pallet con lote y destino."),
    (3, "Apiladora por T3 al rack RK3 de alta rotación (1 y 5 kg)."),
    (4, "Stock de temporada (oct-nov para diciembre) en RK2 y cara este de RK1, por T1 y T2 desde el pasillo central."),
    (5, "Pedido del día: se arma en la calle EX frente al muelle asignado (8 pallets por camión)."),
    (6, "Carga por la rampa niveladora de M1 o M2 con transpaleta / autoelevador (7 camiones por semana en 2035)."),
    (7, "M3 recibe tercerizados (S4) y casquetes de carros (al rack pasante RK1: se toman desde S3 por la cara oeste)."),
    (8, "Las recargas no usan estos muelles: entran por RC-1 y salen en utilitarios por RC-2 (milk run)."),
]


def fl_pi_04(doc, ox):
    h = hoja(doc, "A0", ox, "Logística de MP y de PT", "Descarga, almacén, carga a máquina, políticas de stock y "
             "expedición", "FL_PI_04", 1, 2, "1:50", "Plano de detalle")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI_04 - LOGÍSTICA DE MATERIA PRIMA Y DE PRODUCTO TERMINADO",
                "Detalles 1:50 del almacén de MP y de la expedición, con la secuencia de cada movimiento. "
                "Flota calculada por métodos y tiempos.")
    # ---- detalle MP
    win = (-1.5, 23.0, 22.5, 49.0)
    p0 = (h.fx0 + 8, h.fy1 - 36 - (win[3] - win[1]) * 20)
    def _mp(p):
        for fl in L.FLUJOS:
            if fl.cat in ("MP", "SCRAP", "SE"):
                p.flujo(fl.pts, fl.cat, cada=8.0, largo=3.0, ancho=1.6)
    pm = detalle(h, 50, win, p0, "DETALLE 1 - ALMACÉN DE MP Y CARGA A MÁQUINA - 1:50", extra=_mp)
    for n, xy in ((1, (8.0, 48.4)), (2, (10.9, 45.2)), (3, (8.2, 39.0)), (4, (11.6, 27.2)), (5, (5.0, 36.5)),
                  (6, (12.0, 37.0)), (7, (17.3, 46.0)), (8, (12.0, 33.6)), (9, (3.8, 30.0)), (10, (3.0, 44.0))):
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
    xr = p02[0] + (win2[2] - win2[0]) * 20 + 12
    y = h.fy1 - 34
    y = pasos_papel(pt, xr, y, PASOS_MP, "Secuencia de la MP (detalle 1)", ancho=h.fx1 - xr - 10)
    y = pasos_papel(pt, xr, y - 4, PASOS_PT, "Secuencia del PT (detalle 2)", ancho=h.fx1 - xr - 10)
    M_ = C.manejo()
    cols = [("Unidad de carga", 50, "l"), ("Medio", 24, "l"), ("Viajes/día", 15, "c"), ("m", 10, "c"),
            ("min/día", 14, "c")]
    filas = [[r_["carga"][:34], r_["medio"], f(r_["viajes"], 1), f(r_["dist"], 0), f(r_["min_dia"], 0)]
             for r_ in M_["filas"]]
    y = pt.tabla(xr, y - 6, cols, filas, 3.4, 1.65, "Métodos y tiempos (día pico 2035)")
    oc = M_["ocup"]
    y = pt.parrafo([f"Autoelevador {f(oc['Autoelevador'] * 100, 0)} % y apiladora {f(oc['Apiladora'] * 100, 0)} % de un turno:",
                    "1 de cada uno (más 3 transpaletas manuales). El autoelevador lleva",
                    "prolongaciones, pluma con percha (balancín) y gancho C."], xr, y - 2, 1.9)
    # políticas de stock debajo del detalle 1
    yb = p0[1] - 14
    cols = [("Artículo", 58, "l"), ("Consumo", 26, "c"), ("Unidad de compra", 46, "l"), ("Sistema", 58, "l"),
            ("Se pide", 44, "l"), ("Stock máx.", 18, "c")]
    filas = [[r_["sku"], r_["consumo"], r_["unidad"], r_["sistema"], r_["pedido"], r_["max"]]
             for r_ in C.politicas_stock()]
    yb = pm.tabla(p0[0], yb, cols, filas, 3.6, 1.75, "Políticas de stock por tipo de chapa, fleje y caño (2035)")
    pm.parrafo([
        "Distribución en AL-1H (de sur a norte, el más usado junto a la mesa elevadora): 1) LAF 1,6 × 1000 × 2000 (5 kg);",
        "2) LAF 1,25 × 1220 × 2440 (2,5 kg); 3) LAF 2,0 × 1500 × 3000 (10 kg); 4) LAC 3,2 × 1500 × 3000 (25-50 kg);",
        "5) LAC 4,75 × 1500 × 3000 (70-100 kg). Un formato por posición: no se mezclan espesores (error de corte).",
        "Entregas quincenales de Pradecon (17,6 t) en lugar de una mensual de 35 t: baja el stock máximo a la mitad.",
        "Flejes de bajo consumo (2,0 × 249 y 2,0 × 300 mm): rollos de 250-300 kg para no tener 5 meses de stock.",
        "Semáforo de antigüedad: verde < 4 semanas, amarillo 4-6, rojo > 6 (se usa primero y se inspecciona óxido)."],
        p0[0], yb - 4, 2.0)
    # flota
    cols = [("Equipo de manipulación", 70, "l"), ("Cant.", 12, "c"), ("Dónde", 60, "l")]
    filas = [["Autoelevador eléctrico 3 t, mástil triplex", "1", "MP, PT y descarga de camiones"],
             ["  prolongaciones de horquilla 2,4 m", "1", "Paquetes de hoja por el lado largo"],
             ["  pluma con percha (balancín 4 m) y gancho C", "1", "Rollos de fleje y atados de caño"],
             ["Apiladora eléctrica de conductor acompañante 1,2 t", "1", "Rack de alta rotación RK3 (T3)"],
             ["Transpaletas manuales 2,5 t", "3", "Muelles, insumos y granalla"],
             ["Carros porta-cilindros / zorras / porta-tubos", "26 / 5 / 1", "Línea, milk run y caños"],
             ["Estación de carga de baterías", "1", "AL-C, sobre el pasillo central"]]
    pt.tabla(p02[0], p02[1] - 14, cols, filas, 3.6, 1.75, "Flota (dibujada = calculada)")
    return h


# ================================================================ FL_PI_05 servicios, oficinas y PCP
def fl_pi_05(doc, ox):
    h = hoja(doc, "A0", ox, "Servicios, oficinas y PCP", "Planta baja de servicios, entrepiso de oficinas y núcleo "
             "sanitario de planta", "FL_PI_05", 1, 1, "1:50", "Plano de detalle", "Mampostería / estructura metálica")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI_05 - SERVICIOS AL PERSONAL, OFICINAS Y PCP",
                "Circuito del personal, vestuarios y sanitarios (Dec. 351/79 arts. 49-50), oficinas con vista y acceso "
                "directo a producción, accesibilidad (Ley 24.314).")
    # ---- servicios en planta baja
    win = (-18.6, 18.4, 0.8, 38.4)
    p0 = (h.fx0 + 8, h.fy1 - 36 - (win[3] - win[1]) * 20)
    pl = detalle(h, 50, win, p0, "DETALLE 1 - BLOQUE DE SERVICIOS (PLANTA BAJA) - 1:50", eq_h=2.4, sectores=False)
    for s in L.LOCALES:
        r = s.rect
        if r.x1 < 0.5 and s.cat != "CIRC":
            pl.texto(s.cod, (r.x0 + 0.15, r.y1 - 0.15), 2.6, A.TOP_LEFT)
            pl.texto(f"{f(r.area, 1)} m²", (r.x1 - 0.15, r.y0 + 0.15), 2.2, A.BOTTOM_RIGHT)
    xs = sorted({round(v, 2) for s in L.LOCALES if s.rect.x1 < 0.5 and s.rect.y0 < 23.0 for v in (s.rect.x0, s.rect.x1)})
    pl.cadena(xs, 19.0, -3.0, True)
    ys = sorted({round(v, 2) for s in L.LOCALES if s.rect.x0 < -17 for v in (s.rect.y0, s.rect.y1)})
    pl.cadena(ys, -18.0, -3.0, False)
    # ---- entrepiso
    win2 = (40.8, 24.2, 68.9, 33.8)
    p02 = (p0[0] + (win[2] - win[0]) * 20 + 16, h.fy1 - 36 - (win2[3] - win2[1]) * 20)
    pa = D.Plano(h, 50, (win2[0], win2[1]), p02)
    antes = D.handles(pa.m)
    D.planta_alta(pa)
    for s in L.LOCALES_PA:
        if s.cat != "CIRC":
            pa.texto(s.nombre if len(s.nombre) < 34 else s.nombre[:32] + "…", (s.rect.c[0], s.rect.y0 + 0.35), 1.9,
                     A.MIDDLE_CENTER)
            pa.texto(f"{f(s.rect.area, 1)} m²", (s.rect.c[0], s.rect.y0 + 0.75), 1.9, A.MIDDLE_CENTER)
    pa.texto("VIDRIO CORRIDO: VISTA A LA LÍNEA (N4 Y PV)", (55.0, 29.75), 2.4, A.BOTTOM_CENTER)
    pa.texto("VIDRIO CORRIDO: VISTA AL PASILLO CENTRAL, PT Y TERMINACIÓN", (55.0, 24.55), 2.4, A.TOP_CENTER)
    pa.texto("Escalera y plataforma: bajan a la calle PO-1 y a la senda (30 s a la línea)", (42.5, 33.4), 2.0,
             A.TOP_LEFT)
    pa.cota((win2[0] + 0.4, 24.8), (68.4, 24.8), -6.0, True)
    pa.cota((68.4, 24.8), (68.4, 29.4), 4.0, False)
    D.recortar(pa, antes, *win2)
    a, b = pa.P(win2[0], win2[1]), pa.P(win2[2], win2[3])
    pa.m.add_lwpolyline([a, (b[0], a[1]), b, (a[0], b[1])], close=True, dxfattribs={"layer": "A-TEXTO"})
    pa.texto(f"DETALLE 2 - ENTREPISO DE OFICINAS +{f(L.Z_ENTREPISO, 2)} SOBRE LA FILA CENTRAL - 1:50",
             (a[0], b[1] + 3.0), 4.0, A.BOTTOM_LEFT, papel=True)
    # ---- núcleo sanitario de planta
    win3 = (69.8, 6.2, 75.0, 19.6)
    p03 = (p02[0], p02[1] - 30 - (win3[3] - win3[1]) * 20)
    ps = detalle(h, 50, win3, p03, "DETALLE 3 - NÚCLEO SANITARIO DE PLANTA - 1:50", eq_h=2.4, sectores=False)
    for s in L.LOCALES:
        if s.cod.startswith("SN-"):
            ps.texto(s.cod, (s.rect.x0 + 0.1, s.rect.y1 - 0.1), 2.4, A.TOP_LEFT)
    # ---- corte por el entrepiso
    pc = D.Plano(h, 100, (-2.0, -1.0), (p03[0] + 140, p03[1] + 40))
    corte_entrepiso(pc)
    # ---- textos
    xr = p03[0] + 130
    y = p02[1] - 22
    y = pasos_papel(pa, xr + 140, y, [
        (1, "Ingreso por SV-1 desde el estacionamiento; fichado en el hall (reloj biométrico)."),
        (2, "Pasillo limpio: a la izquierda vestuarios, a la derecha oficinas de servicio y capacitación."),
        (3, "Vestuario: armario doble (ropa de calle / de trabajo). Duchas y sanitarios sólo desde el vestuario."),
        (4, "Inodoros, mingitorios y lavabos sobre la misma pared húmeda (montante único de agua y cloaca)."),
        (5, "PP-1: entrada a la senda peatonal separada del autoelevador por la defensa."),
        (6, "Comedor a 6 m de PP-1 con lavamanos en la entrada (refrigerio de 30 min en 2 tandas)."),
        (7, "Administración, PCP y jefatura en el entrepiso: ven toda la línea y bajan a ella en 30 s."),
        (8, "Supervisión de turno en planta baja (fila central) con ventana a la línea."),
    ], "Circuito y criterios", ancho=h.fx1 - xr - 150)
    filas = [[f"{s.cod} {s.nombre}"[:46], f(s.rect.area, 1), s.nota[:70]] for s in L.LOCALES + L.LOCALES_PA
             if s.cat != "CIRC" and not s.cod.startswith("RC")]
    pl.tabla(p0[0], p0[1] - 14, [("Local", 74, "l"), ("m²", 14, "r"), ("Equipamiento / criterio", 112, "l")], filas,
             3.6, 1.75, "Locales de servicios, oficinas y núcleo sanitario")
    return h


def corte_entrepiso(pc):
    """Corte transversal B-B por x = 55 m (norte-sur): nave de dos luces, entrepiso de oficinas a +3,50."""
    W = L.NAVE_A
    ejes = L.EJES_Y
    pc.linea((-2.0, 0.0), (W + 2.0, 0.0), "A-EXTERIOR")
    for x in ejes:
        pc.rect(L.R(x - 0.2, 0.0, x + 0.2, 8.0), "A-MURO")
    for a, b in zip(ejes, ejes[1:]):
        m = (a + b) / 2
        hl = 1.6 * (b - a) / 25.0
        pc.pl([(a - 0.3, 8.0), (m, 8.0 + hl), (b + 0.3, 8.0)], "A-MURO")
    e0, e1 = L.ENTREPISO.y0, L.ENTREPISO.y1
    pc.rect(L.R(e0, L.Z_ENTREPISO, e1, L.Z_ENTREPISO + 0.25), "A-MURO")
    pc.rect(L.R(e0, L.Z_ENTREPISO + 0.25, e1, L.Z_ENTREPISO + 2.9), "A-LOCAL")
    for y_ in (e0, e1):
        pc.linea((y_, L.Z_ENTREPISO + 1.0), (y_, L.Z_ENTREPISO + 2.4), "A-VENTANA")
    pc.texto("Oficinas +3,50", ((e0 + e1) / 2, L.Z_ENTREPISO + 1.5), 2.0, A.MIDDLE_CENTER)
    pc.texto("Q / SUP / EPP (PB)", ((e0 + e1) / 2, 1.5), 1.8, A.MIDDLE_CENTER)
    pc.cota((e1 + 1.0, 0.0), (e1 + 1.0, L.Z_ENTREPISO), 8.0, False)
    pc.cota((W, 0.0), (W, 8.0), 6.0, False)
    pc.texto("CORTE B-B POR EL ENTREPISO (x = 55 m) - 1:100", pc.P(-2.0, 11.5), 3.0, A.BOTTOM_LEFT, papel=True)
    pc.texto("S", pc.P(0.0, -2.0), 2.5, A.MIDDLE_CENTER, papel=True)
    pc.texto("N", pc.P(W, -2.0), 2.5, A.MIDDLE_CENTER, papel=True)
