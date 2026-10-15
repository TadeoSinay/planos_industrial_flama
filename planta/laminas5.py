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
            corto_ = nom.split(":")[0].split(" (")[0]
            pl.texto(f"{cod} {corto_}", (r.x0 + 0.2, r.y1 - 0.2), eq_h * 0.8, A.TOP_LEFT)
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
    y = leyenda_flujos(pl, x, y, ["MP", "SE", "TL", "RET", "PT", "SCRAP", "EFL-L", "EFL-G"])
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
    y = pl.parrafo(["Criterio: orden y disposición de los Word de proceso (W-MAN, W-CAR); toda la MP entra por P1 (7,0 m)",
                    "con cuarentena y P3 sólo despacha; 0 cruces entre MP, SE y PT (verificado sobre el modelo). Las líneas",
                    "de MP que se tocan dentro del almacén son maniobras del mismo autoelevador. Pintura con riel aéreo",
                    "(W-MAN): un solo horno, que el riel atraviesa dos veces (precalentamiento y curado), cabina y descarga."],
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
             ["Sanitarios accesibles (servicios, con ducha, y administración)", "2"]]
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
    pl.parrafo(["Además: sanitarios de planta (banda sur, calle AT2) de hombres (2 inodoros, 2 mingitorios, 2",
                "lavabos) y de mujeres (1 + 1), a < 25 m de pintura, terminación, embalaje y PT. Lockers: 1 por empleado.",
                "Cada operario tiene 1,0 m libre detrás de su puesto: ninguna calle ni material ajeno pasa",
                "por su espalda (verificado). Mamparas ignífugas en todos los puestos de soldadura."],
               x, yb - 6, 2.0)
    return h


# ================================================================ FL_PI_04 logística de MP y PT
PASOS_MP = [
    (1, "Camión en el alero norte (semi 18,6 m o chasis playo): entró por G1 y se pesó en la báscula; descarga de "
        "costado en la franja de 15 × 5 m (W-CAR 1). Toda la MP entra por acá, también polvo, pintura y embalaje."),
    (2, "Descarga con el único autoelevador de la planta, Heli CPCD50 de 5 t (W-MAN y W-CAR): uñas largas, espolón, "
        "prolongadores y pluma; entra por P1 (7,0 m) a la calle A1 (7,5 m)."),
    (3, "Cuarentena AL-CU (10 × 2,5 m, amarilla, compartida con carros): colada, espesor en 3 puntos y etiqueta de lote "
        "(W-MAN); lo no conforme va a retenidos AL-RE (rojo) y se reclama al proveedor."),
    (4, "Hojas aprobadas: por A1, AN y A2 a AL-CH (3 formatos LAF, paquetes de 2 alturas); el LAC de carros a la calle "
        "de chapa AL-CC, del otro lado de A2."),
    (5, "Paquete a la mesa elevadora de la guillotina: de costado por A2, AN y A3 (calles de 5 m: radio de giro del "
        "Heli + pallet + margen, W-CAR)."),
    (6, "Rollos de fleje en el porta-flejes AL-FL de 3 niveles sobre AN; el espolón lleva el rollo al carro "
        "portabobinas del desbobinador (extremo este de AN)."),
    (7, "Caños y barras de 6 m: el atado entra atravesado por P1 (7,0 m = 6 m + 0,5 m por lado), baja por A1 (7,5 m) "
        "y se apoya en el cantiléver AL-CT, al fondo de A1 y paralelo a P1, sin girar. Al láser, con la pluma, por A1, "
        "AN y A3 (3,3 atados por día en el pico, X-ALM y W-MAN)."),
    (8, "Barras de carros: de a una y a mano (W-CAR 8.1: la más pesada pesa 23,9 kg), del cantiléver al rack del "
        "puesto 8.1 por la senda PP; 8,6 barras por día en el pico."),
    (9, "Insumos de montaje (AL-MM, AL-MC), identificación (AL-ID), soldadura y granalla (AL-SS): salen una vez por "
        "turno en los 2 carros de abastecimiento (AL-CA, W-CAR)."),
    (10, "Gases: no entran al almacén; los packs de 12 cilindros de Arcal 21 y N₂ van a la jaula exterior JG, detrás de "
         "la sala SC (puerta PG), con manifold y cañería a los puestos (W-MAN)."),
    (11, "Scrap: contenedor en cada puesto que lo genera (guillotina, láser, prensa); el autoelevador lo lleva al "
         "volquete junto a P1 por A3, AN y A1. Nada de scrap queda en el almacén."),
    (12, "Gasoil e insumos del autoelevador en el armario de inflamables al final del pasillo central (AL-1N)."),
]
PASOS_PT = [
    (1, "Encajonado en EMB (W-MAN): los terminados al final de la terminación y los vacíos junto a la descarga de "
        "pintura, con la armadora de cajas AC1 y las cajas del rack AL-EB."),
    (2, "Transpaleta a la envolvedora EDOS PS5 (T11) y etiqueta de pallet con lote y destino."),
    (3, "Transpaleta por AT y la calle T hasta el pie del rack (calle T-PT, 5 m); el autoelevador lo ubica: RK1 y RK2 "
        "de 7 módulos × 2 pallets × 5 niveles = 140 posiciones (X-DT Almacén PT 2035: 128)."),
    (4, "Pedido del día: se arma en la calle T, frente al muelle P3 (8 pallets por camión)."),
    (5, "Muelle P3 (3,0 m, rampa niveladora): sólo despacho, de 13 a 17 h. La MP ya no entra por acá: P1 recibe todo."),
    (6, "Polvo, pintura, embalaje y revendidos llegan por P1 y la cuarentena; el autoelevador los trae por el pasillo "
        "central y la calle T al depósito DP, al rack AL-EB y al rack S4."),
    (7, "Carros: del pulmón PU-11 (120 carros, W-CAR 11) cruzan el PC por la senda y bajan por la calle T al muelle; "
        "vuelven pintados al cambio de juego (12) y, liberados (16), salen por el mismo muelle."),
]


def fl_pi_04(doc, ox):
    h = hoja(doc, "A0", ox, "Logística de MP y de PT", "Descarga, almacén, carga a máquina, políticas de stock y "
             "expedición", "FL_PI_04", 1, 2, "1:50", "Plano de detalle")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI_04 - LOGÍSTICA DE MATERIA PRIMA Y DE PRODUCTO TERMINADO",
                "Detalles 1:50 del almacén de MP y de la expedición, con la secuencia de cada movimiento. "
                "Flota calculada por métodos y tiempos.")
    # ---- detalle MP
    win = (-1.5, 18.8, 26.0, 49.0)                      # almacén de MP, carga a máquina, scrap y alero de P1
    p0 = (h.fx0 + 8, h.fy1 - 36 - (win[3] - win[1]) * 20)
    def _mp(p):
        for fl in L.FLUJOS:
            if fl.cat in ("MP", "SCRAP", "SE"):
                p.flujo(fl.pts, fl.cat, cada=8.0, largo=3.0, ancho=1.6)
    pm = detalle(h, 50, win, p0, "DETALLE 1 - ALMACÉN DE MP Y CARGA A MÁQUINA - 1:50", extra=_mp)
    for n, xy in ((1, (14.0, 47.5)), (2, (5.4, 41.0)), (3, (10.4, 31.0)), (4, (15.6, 35.0)), (5, (22.0, 34.5)),
                  (6, (17.0, 40.6)), (7, (5.4, 28.0)), (8, (16.0, 23.8)), (9, (3.0, 21.0)), (10, (24.0, 46.5)),
                  (11, (3.0, 47.0)), (12, (1.0, 25.4))):
        globo(pm, n, xy, 3.0)
    for c_ in ("A1", "A2", "A3"):
        r = next(p for p in L.PASILLOS if p.cod == c_).rect
        pm.cota((r.x0, 36.0), (r.x1, 36.0), 0.0, True, texto=f"{c_} <>")
    p1 = next(p for p in L.PUERTAS if p.cod == "P1")
    pm.cota((p1.a, L.NAVE_A), (p1.b, L.NAVE_A), 30.0, True, texto="P1 <>")
    # ---- detalle PT
    win2 = (30.0, -3.0, 57.0, 12.0)
    p02 = (p0[0] + (win[2] - win[0]) * 20 + 14, h.fy1 - 36 - (win2[3] - win2[1]) * 20)
    def _pt(p):
        for fl in L.FLUJOS:
            if fl.cat in ("PT", "MP"):
                p.flujo(fl.pts, fl.cat, cada=8.0, largo=3.0, ancho=1.6)
    pt = detalle(h, 50, win2, p02, "DETALLE 2 - ALMACÉN DE PT Y EXPEDICIÓN - 1:50", extra=_pt)
    for n, xy in ((1, (56.5, 9.5)), (2, (56.5, 7.5)), (3, (40.0, 3.0)), (4, (51.8, 8.5)), (5, (51.6, -1.8)),
                  (6, (55.0, 11.0)), (7, (52.6, 11.0))):
        globo(pt, n, xy, 3.0)
    for c_ in ("T", "T-PT", "AT"):
        r = next(p for p in L.PASILLOS if p.cod == c_).rect
        if r.w < r.h:
            pt.cota((r.x0, 9.0), (r.x1, 9.0), 0.0, True, texto=f"{c_} <>")
        else:
            pt.cota((min(r.x1, 57.0) - 1.5, r.y0), (min(r.x1, 57.0) - 1.5, r.y1), 0.0, False, texto=f"{c_} <>")
    p3 = next(p for p in L.PUERTAS if p.cod == "P3")
    pt.cota((p3.a, 0.0), (p3.b, 0.0), -24.0, True, texto="P3 <>")
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
    y = pt.parrafo([f"Ocupación de un turno: autoelevador {f(oc['Autoelevador'] * 100, 0)} %, "
                    f"transpaleta {f(oc['Transpaleta'] * 100, 0)} %.",
                    "W-MAN y W-CAR: un solo Heli CPCD50 para toda la planta (MP de manuales y de carros, PT,",
                    "muelle y depósito), con uñas largas, prolongadores, espolón y pluma."], xr, y - 2, 1.9)
    # políticas de stock debajo del detalle 1
    yb = p0[1] - 14
    cols = [("Artículo", 58, "l"), ("Consumo (pico)", 28, "c"), ("Unidad de compra", 40, "l"),
            ("Punto de pedido y plazo", 56, "l"), ("Se pide", 40, "l"), ("Stock máx.", 22, "c")]
    filas = [[r_["sku"], r_["consumo"], r_["unidad"], r_["sistema"], r_["pedido"], r_["max"]]
             for r_ in C.politicas_stock()]
    yb = pm.tabla(p0[0], yb, cols, filas, 3.6, 1.75,
                  "Política de stock de chapa, fleje y caño (MRP del grupo: X-ALM v5, hoja Política de stock)")
    pm.parrafo([
        "Los almacenes los dimensiona el grupo en el MRP (X-ALM v5) con los plazos de su planilla de lead times;",
        "el plano ubica cada sección con su superficie: chapa LAF (AL-CH, el formato más usado junto a A2), calle de",
        "chapa LAC de carros (AL-CC), porta-flejes de 3 niveles (AL-FL: misma capacidad en la tercera parte del frente),",
        "cantiléver de caños y barras (AL-CT), casquetes (AL-CQ) e insumos (AL-MM, AL-MC, AL-ID, AL-SS). No hay",
        "almacén de procesado: sólo los pulmones de W-MAN. Las calles de 5 m (W-CAR) suman superficie a X-ALM."],
        p0[0], yb - 4, 2.0)
    # flota
    cols = [("Equipo de manipulación", 70, "l"), ("Cant.", 12, "c"), ("Dónde", 60, "l")]
    fchp = sum(p_.carros for p_ in L.PULMONES if "FCHP" in p_.guarda)
    caj = sum(p_.carros for p_ in L.PULMONES if "cajones" in p_.guarda)
    filas = [["Autoelevador Heli CPCD50 5 t diésel (W-MAN, W-CAR)", "1", "Toda la planta: MP, carga a máquina, PT, scrap"],
             ["  uñas largas, prolongadores, espolón y pluma", "1", "Paquetes, atados, rollos y big bags"],
             ["Transpaleta eléctrica + manual de respaldo (W-MAN)", "2", "Embalaje, envolvedora, PT y big bags"],
             ["Carros FCHP20505 / de 12 cajones (en pulmones)", f"{fchp} / {caj}", "Entre puestos (pulmones de W-MAN)"],
             ["Carros de abastecimiento", "2", "Milk run (W-CAR); las barras van a mano"],
             ["Contenedores de scrap 1.000 L", "3", "Guillotina, láser y prensa"],
             ["Armario de inflamables (gasoil e insumos)", "1", "AL-1N, al final del pasillo central"]]
    pt.tabla(p02[0], p02[1] - 14, cols, filas, 3.6, 1.75, "Flota (dibujada = calculada)")
    return h


# ================================================================ FL_PI_05 servicios, oficinas y apoyo a la línea
OFICINAS = ("MT", "PÑL", "QR", "Q", "PCP", "SUP")


def fl_pi_05(doc, ox):
    h = hoja(doc, "A0", ox, "Servicios, oficinas y apoyo", "Bloque de servicios, oficinas de planta (SO), "
             "administración (E), sanitarios de planta y sala de compresores", "FL_PI_05", 1, 1,
             "1:50", "Plano de detalle", "Mampostería / estructura metálica")
    titulo_hoja(D.Plano(h, 50, (0, 0), (0, 0)), h, "FL_PI_05 - SERVICIOS AL PERSONAL, OFICINAS Y APOYO A LA LÍNEA",
                "Todo en planta baja (sin entrepiso). Vestuarios y sanitarios (Dec. 351/79 arts. 49-50), accesibilidad "
                "(Ley 24.314); oficinas de planta en el ángulo SO (ex recargas) y administración al este, lejos de P1.")
    # ---- detalle 1: bloque de servicios
    win = (-18.6, 18.4, 0.8, 35.8)
    p0 = (h.fx0 + 8, h.fy1 - 36 - (win[3] - win[1]) * 20)
    pl = detalle(h, 50, win, p0, "DETALLE 1 - SERVICIOS AL PERSONAL - 1:50", eq_h=2.4, sectores=False)
    for s_ in L.LOCALES:
        r = s_.rect
        if r.x1 < 0.5 and s_.cat != "CIRC":
            pl.texto(s_.cod, (r.x0 + 0.15, r.y1 - 0.15), 2.6, A.TOP_LEFT)
            pl.texto(f"{f(r.area, 1)} m²", (r.x1 - 0.15, r.y0 + 0.15), 2.2, A.BOTTOM_RIGHT)
    xs = sorted({round(v, 2) for s_ in L.LOCALES if s_.rect.x1 < 0.5 and s_.rect.y0 < 23.0
                 for v in (s_.rect.x0, s_.rect.x1)})
    pl.cadena(xs, 19.0, -3.0, True)
    ys = sorted({round(v, 2) for s_ in L.LOCALES if s_.rect.x0 < -17 for v in (s_.rect.y0, s_.rect.y1)})
    pl.cadena(ys, -18.0, -3.0, False)
    # ---- detalle 2: oficinas de planta en el ángulo SO
    win2 = (-0.6, 4.4, 14.6, 19.4)
    p02 = (p0[0] + (win[2] - win[0]) * 20 + 16, h.fy1 - 36 - (win2[3] - win2[1]) * 20)
    pa = detalle(h, 50, win2, p02, "DETALLE 2 - OFICINAS DE PLANTA (SO): MANTENIMIENTO, PAÑOL, CALIDAD, SUPERVISOR "
                 "Y PCP - 1:50", eq_h=2.2)
    for cod in OFICINAS:
        r = next(s_.rect for s_ in L.SECTORES if s_.cod == cod)
        pa.texto(f"{f(r.area, 1)} m²", (r.x1 - 0.15, r.y0 + 0.15), 2.0, A.BOTTOM_RIGHT)
    xs2 = sorted({round(v, 2) for c in ("MT", "PÑL", "QR") for s_ in L.SECTORES if s_.cod == c
                  for v in (s_.rect.x0, s_.rect.x1)})
    pa.cadena(xs2, 18.8, 1.2, True)
    xs3 = sorted({round(v, 2) for c in ("Q", "PCP", "SUP") for s_ in L.SECTORES if s_.cod == c
                  for v in (s_.rect.x0, s_.rect.x1)})
    pa.cadena(xs3, 5.0, -1.4, True)
    # ---- detalle 3: administración al este
    win5 = (75.8, 24.2, 88.4, 34.0)
    p05 = (p02[0] + (win2[2] - win2[0]) * 20 + 16, h.fy1 - 36 - (win5[3] - win5[1]) * 20)
    pd = detalle(h, 50, win5, p05, "DETALLE 3 - ADMINISTRACIÓN (LADO ESTE) - 1:50", eq_h=2.2)
    for s_ in L.LOCALES:
        if s_.cod.startswith("AD-"):
            pd.texto(f"{f(s_.rect.area, 1)} m²", (s_.rect.x1 - 0.15, s_.rect.y0 + 0.15), 2.0, A.BOTTOM_RIGHT)
    ad = next(s_.rect for s_ in L.LOCALES if s_.cod == "AD-OF")
    pd.cota((ad.x0, ad.y1), (ad.x1, ad.y1), 8.0, True)
    # ---- detalle 4: sanitarios de planta
    win3 = (60.5, 15.4, 72.8, 19.2)
    p03 = (p02[0], p02[1] - 30 - (win3[3] - win3[1]) * 20)
    ps = detalle(h, 50, win3, p03, "DETALLE 4 - SANITARIOS DE PLANTA (H Y M) - 1:50", eq_h=2.4, sectores=False)
    for s_ in L.LOCALES:
        if s_.cod.startswith("SN-"):
            ps.texto(s_.cod, (s_.rect.x0 + 0.1, s_.rect.y1 - 0.1), 2.4, A.TOP_LEFT)
    # ---- detalle 5: sala de compresores y colectores
    win4 = (47.4, 39.2, 72.0, 47.8)
    p04 = (p02[0], p03[1] - 30 - (win4[3] - win4[1]) * 20)
    pc = detalle(h, 50, win4, p04, "DETALLE 5 - COMPRESORES, COLECTOR Y JAULA EXTERIOR DE GASES - 1:50", eq_h=2.2)
    G = C.colector_gases()
    pc.texto(f"Reguladores CG1 al extremo oeste, detrás de la jaula JG: {f(G['sc'], 0)} m de cañería a las "
             f"{G['n']} soldadoras (en el centro de la sala serían {f(G['centro'], 0)} m)", (47.6, 39.5), 2.0,
             A.BOTTOM_LEFT)
    # ---- textos
    xr = p04[0] + (win4[2] - win4[0]) * 20 + 16
    y = p05[1] - 22
    pasos_papel(pc, xr, y, [
        (1, "Ingreso por SV-1 (camino peatonal desde G4 y la garita); fichado en el hall."),
        (2, "Pasillo limpio: al sur limpieza, higiene y seguridad (EPP y primeros auxilios), sanitario accesible y "
            "hall; al norte vestuarios y comedor."),
        (3, "Vestuario: 1 locker por empleado (bloques de 7 columnas × 3 filas). Duchas en su propio local, "
            "separadas de inodoros y mingitorios; todo sólo desde el vestuario."),
        (4, "Duchas, inodoros, mingitorios y lavabos: cada grupo alineado sobre una misma pared húmeda."),
        (5, "Comedor: abre directo al pasillo limpio (sin pasillo propio) y tiene su salida de emergencia SV-2; "
            "el office junto a la puerta y las mesas al fondo."),
        (6, "Oficinas de planta en el ángulo SO, donde estaba recargas: entrada OF-1 desde el camino peatonal y pasillo "
            "OF-C. Mantenimiento con portón al pasillo central y pañol pegado (ventanilla); calidad y retenidos (QR) "
            "juntos; supervisor con ventana a la planta y PCP al lado."),
        (7, "Administración (compras, ventas, RRHH) en el lado este, lejos del portón de MP: entrada de visitas AD-1 "
            "por la fachada este, hall, office y sanitario accesible propio; no entra nadie de afuera a la planta."),
        (8, "Sanitarios de planta sobre la calle AT2, a menos de 25 m de pintura, terminación, embalaje y PT."),
    ], "Circuito y criterios", ancho=h.fx1 - xr - 10)
    filas = [[f"{s_.cod} {s_.nombre}"[:46], f(s_.rect.area, 1), s_.nota[:70]] for s_ in L.LOCALES
             if s_.cat != "CIRC"]
    filas += [[f"{s_.cod} {s_.nombre}"[:46], f(s_.rect.area, 1), s_.nota[:70]] for s_ in L.SECTORES
              if s_.cod in OFICINAS + ("SC",)]
    pl.tabla(p0[0], p0[1] - 26, [("Local", 74, "l"), ("m²", 14, "r"), ("Equipamiento / criterio", 112, "l")], filas,
             3.6, 1.75, "Locales de servicios, oficinas, administración y apoyo a la línea")
    return h
