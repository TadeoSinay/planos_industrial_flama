"""Genera docs/MEMORIA_DE_CALCULO.md a partir del modelo y de los cálculos (se regenera con generar.py)."""

import math

from . import layout as L
from . import calculos as C


def f(v, d=1):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tabla(cols, filas):
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in filas:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def generar(ruta):
    t = C.tasas()
    s = []
    s.append("# Memoria de cálculo del layout - planta industrial FLAMA S.A. (año 10 = 2035)\n")
    s.append("Se genera desde `planta/calculos.py` y `planta/layout.py` (`python generar.py`). Cada número indica su "
             "fuente: **DT** = Dimensionamiento_TecnicoV2.xlsx, **MP** = MP_Abastecimiento_Almacenamiento_FLAMA_OpcionD.xlsx, "
             "**CC** = Comparacion_corte.xlsx, **X-ALM** = Dimensionamiento_Almacenes_MP_v5.xlsx (MRP del grupo), **W-MAN**, "
             "**W-CAR** = Word de proceso de manuales y de carros, **C** = cotización de proveedor, "
             "**E** = estimado, **SUP** = supuesto a validar.\n")
    # 1 demanda
    s.append("## 1. Demanda y tasas de diseño\n")
    s.append(tabla(["Formato", "Matafuegos (u/año)", "Cilindros vendidos (u/año)"],
                   [[k, f(a, 0), f(b, 0)] for k, (a, b) in C.DEMANDA.items()]))
    s.append(f"\nRecargas: {f(C.RECARGAS, 0)} u/año (DT), fuera de esta planta desde la v9. Tercerizados revendidos: "
             f"{f(C.TERCERIZADOS, 0)} u/año "
             "(**SUP**: 12,7 % no ABC sobre las ventas de equipos; no hay dato en los Excel).\n")
    s.append(f"Mes pico = {f(C.PICO, 2)} × promedio (dic-ene). Horas productivas del mes pico: {C.DIAS} días × {C.TURNOS} "
             f"turnos × {f(C.H_TURNO, 0)} h × {f(C.EFIC, 2)} = {f(C.H_MES, 0)} h.\n")
    s.append(tabla(["Familia", "Tasa de diseño (u/h)"], [[k, f(v, 1)] for k, v in t.items()]))
    # 2 layout
    s.append("\n## 2. Nave y sectores\n")
    s.append(f"Nave de {f(L.NAVE_L, 0)} × {f(L.NAVE_A, 0)} m = {f(L.NAVE_L * L.NAVE_A, 0)} m², puestos en el orden y la "
             f"disposición de los Word de proceso (W-MAN, W-CAR), pórticos de dos luces (19,40 y 24,60 m) cada {f(L.MODULO, 0)} m, altura libre "
             f"{f(L.ALTURA_LIBRE, 2)} m (Dec. 351/79 exige ≥ 3 m). Recargas se hace fuera de esta planta: en su lugar "
             "(ángulo SO) van las oficinas de planta, y administración pasa al lado este, lejos de P1. Anexos: servicios "
             f"{f(next(a.rect.area for a in L.ANEXOS if a.cod == 'SV'), 0)} m² y sala técnica "
             f"{f(next(a.rect.area for a in L.ANEXOS if a.cod == 'ST'), 0)} m². La nave sigue en 88 × 44: lo que libera "
             "recargas (≈ 330 m²) lo ocupan los puestos 10 a 17 de carros (W-CAR: ≈ 520 m² entre secado, pulmón de "
             "despacho, cambio de juego, carga, pérdidas, etiquetado, depósito y ensayos) y la calle de PT de 5 m; "
             "no alcanza para sacar un módulo de 8 m (352 m²).\n")
    s.append(tabla(["Código", "Sector", "m² proyectados", "m² requeridos", "Nota"],
                   [[x.cod, x.nombre, f(x.rect.area, 1), f(x.area_req, 1) if x.area_req else "-", x.nota]
                    for x in L.SECTORES]))
    s.append("\nAlmacenes: los dimensiona el grupo en el MRP (X-ALM v5, con la planilla de plazos de entrega); el plano "
             "ubica cada sección con al menos su superficie neta o sus posiciones. Una sola recepción de MP con cuarentena "
             "compartida con carros (W-MAN, W-CAR). Calles de 5,0 m para el Heli CPCD50 (W-CAR tabla 5).\n")
    s.append(tabla(["Sección (X-ALM)", "Posiciones", "m² netos", "m² brutos", "Sector del plano", "m² en el plano",
                    "Cómo se guarda"],
                   [[r["seccion"], r["pos"], f(r["neta"], 1), f(r["bruta"], 1), r["sectores"], f(r["plano"], 1), r["como"]]
                    for r in C.almacenes_xalm()]))
    s.append("\nX-ALM redondea cada ítem a lugares enteros (sin compartir columna). Donde el plano tiene menos m² netos "
             "(fleje, insumos de carros, identificación) las posiciones entran igual: el fleje va en "
             "porta-flejes de 3 niveles en lugar de pallets a piso, y los ítems chicos comparten columna de rack o "
             "estantería. El área bruta de X-ALM (× 1,5 de circulación) queda reemplazada por las calles de 5 m del "
             "plano, por eso el almacén de MP ocupa más que la suma de las áreas brutas.\n")
    # 3 recepción
    s.append("\n## 3. Recepción de MP y análisis de peso de la carga\n")
    s.append("Se dimensiona para la carga máxima: un semirremolque de 18,6 m y 30 t o dos chasis de 10 m en el alero "
             "de descarga norte (32 × 11,6 m), playos y con el costado libre (W-CAR), con descarga por ambos lados con "
             "el autoelevador. La nave tiene dos portones: P1 de 7,0 m (toda la MP de manuales y carros, también "
             "polvo, pintura, embalaje y revendidos, con una sola cuarentena, W-MAN; el atado de 6 m entra atravesado y "
             "se apoya en el cantiléver sin girar) y el muelle único P3 (sólo despacho: PT, carros al pintor y "
             "liberados, 13 a 17 h). P2 (recargas) se suprimió con recargas. Los packs de gases se cambian desde el "
             "patio norte en la jaula exterior JG. Los camiones entran por G1 (garita y báscula) y salen por G3.\n")
    s.append(tabla(["Formato", "Largo (m)", "Carga útil (t)", "PBT (t)", "Descarga"],
                   [[a, f(b, 1), f(c, 1), f(d, 1), e] for a, b, c, d, e in C.CAMIONES]))
    s.append("\n" + tabla(["Proveedor / material", "t por entrega", "Entregas/año", "Vehículo", "Portón", "Destino"],
                          [[a, f(b, 2), f(c, 1), d, e, g] for a, b, c, d, e, g in C.ENTREGAS]))
    p = C.semi_vs_chasis()
    s.append(f"\nPradecon entrega {f(p['t_mes'], 1)} t por mes (hojas + fleje 0,9): supera la carga útil de un semi. Se "
             f"parte en 2 entregas quincenales de {f(p['quincenal_t'], 1)} t, que entran en un chasis con balancín y bajan "
             "el stock máximo de chapa medio mes.\n")
    s.append("Capacidad residual del autoelevador con un paquete de hoja de 1500 × 3000 mm y 2 t "
             "(Q = Qn · (cn + d) / (c + d), d = 0,45 m):\n")
    s.append(tabla(["Nominal (c = 500 mm)", "Por el lado largo (c = 750 mm)", "Por el lado corto (c = 1500 mm)"],
                   [[f"{f(q, 1)} t", f"{f(a, 2)} t", f"{f(b, 2)} t"] for q, a, b in C.analisis_peso()]))
    s.append("\nSe adopta el autoelevador de W-MAN: Heli CPCD50 K2 diésel de 5 t, compartido entre la MP de manuales "
             "y la de carros, con uñas largas, prolongadores para los atados, espolón para los rollos y pluma para los big "
             "bags y los atados (Mecánica Porta). Con 5 t nominales toma el paquete de 2 t por cualquier lado. Es el único "
             "autoelevador de la planta (W-CAR: compartido): también ubica el PT en los racks de 5 niveles y carga en el "
             "muelle. El embalaje tiene una transpaleta eléctrica con una manual de respaldo (W-MAN).\n")
    # 4 política de stock (X-ALM)
    s.append("## 4. Política de stock de chapa, fleje y caño (MRP del grupo)\n")
    s.append(tabla(["Artículo", "Consumo (día pico)", "Unidad de compra", "Punto de pedido y plazo", "Se pide",
                    "Stock máximo"],
                   [[r["sku"], r["consumo"], r["unidad"], r["sistema"], r["pedido"], r["max"]] for r in C.politicas_stock()]))
    s.append("\nFuente: X-ALM v5, hoja Política de stock (stock máximo = stock de seguridad + una compra). Hoja LAF "
             "aceitada con film VCI, siempre bajo techo y lejos de la PH; FIFO por tarjeta de color del mes de ingreso.\n")
    # 5 pulmones
    s.append("## 5. Pulmones y manejo de materiales (métodos y tiempos)\n")
    s.append("Sólo los pulmones y almacenes intermedios que figuran en W-MAN y W-CAR, con la capacidad que dan los "
             "Word; no se agregó ninguno (se quitaron el almacén de procesado y el de vacíos de la v8).\n")
    s.append(tabla(["Pulmón", "Qué guarda", "De", "A", "Carros / u. de manejo", "m²", "Fuente"],
                   [[r["pulmon"], r["guarda"], r["viene"], r["va"], r["carros"], f(r["m2"], 1), r["fuente"]]
                    for r in C.pulmones()]))
    M_ = C.manejo()
    s.append("\nTiempo por viaje = 2 × distancia / velocidad + tiempo fijo de toma y entrega. Distancias medidas sobre "
             "los recorridos del modelo; día pico 2035.\n")
    s.append(tabla(["Unidad de carga", "Medio", "Recorrido", "Viajes/día", "m", "min/viaje", "min/día"],
                   [[r["carga"], r["medio"], r["ruta"], f(r["viajes"], 1), f(r["dist"], 0), f(r["t_viaje"], 1),
                     f(r["min_dia"], 0)] for r in M_["filas"]]))
    oc = M_["ocup"]
    s.append(f"\nOcupación sobre un turno útil de 408 min: autoelevador (único) "
             f"{f(oc['Autoelevador'] * 100, 0)} %, transpaleta "
             f"{f(oc['Transpaleta'] * 100, 0)} %. Entre pasos se mueven {M_['carros_dia']} carros FCHP20505 por día y por "
             "tramo: W-MAN pone un carro entre cada par de puestos y lo empuja el operario que cierra el lote, sin tren "
             "logístico; al norte de la senda no entra el autoelevador. El riel aéreo lleva el cilindro de la detección a "
             f"la descarga de pintura ({f(C.riel()['cargado_m'], 0)} m cargado, que pasa dos veces por el único horno, "
             f"y {f(C.riel()['retorno_m'], 0)} m de retorno de ganchos vacíos). Los carros rodantes ruedan sobre sus "
             "ruedas: del pulmón PU-11 cruzan el PC por la senda y bajan por la calle T al muelle P3. W-CAR supone una "
             "planta sin muelle (tarima con topes y autoelevador); con el muelle P3 suben rodando, y la tarima queda "
             "para camiones que no lleguen al muelle. El abastecedor hace el milk run con los 2 carros "
             "de abastecimiento (AL-CA, W-CAR) una vez por turno.\n")
    s.append(tabla(["Portón", "Qué entra o sale", "Vehículo", "Frecuencia", "Horario"], [list(r) for r in C.PORTONES]))
    G = C.colector_gases()
    s.append(f"\nGases (W-MAN): packs de 12 cilindros de Arcal 21 y de N₂ con manifold en la jaula exterior JG, detrás "
             f"de la sala SC; los reguladores CG1 están en el extremo oeste de la sala: {f(G['sc'], 0)} m de cañería "
             f"(recorrido ortogonal) a las {G['n']} soldadoras, contra {f(G['centro'], 0)} m desde el centro de la sala. "
             "La carga de carros (W-CAR 13) tiene su propia batería de N₂ en jaula.\n")
    s.append(tabla(["Soldadora", "m desde los reguladores CG1"], [[c, f(d, 1)] for c, d in G["filas"]]))
    # 6 cruces
    s.append("## 6. Cruces de flujos y de hilos\n")
    from shapely.geometry import LineString, Point
    fl = [(x.cat, x.rot, LineString(x.pts)) for x in L.FLUJOS]
    n = 0
    for i in range(len(fl)):
        for j in range(i + 1, len(fl)):
            a, b = fl[i][2], fl[j][2]
            if a.intersects(b):
                g = a.intersection(b)
                pts = [g] if g.geom_type == "Point" else list(getattr(g, "geoms", [g]))
                ends = [Point(a.coords[0]), Point(a.coords[-1]), Point(b.coords[0]), Point(b.coords[-1])]
                for q in pts:
                    if q.geom_type == "Point" and any(q.distance(e) < 0.05 for e in ends):
                        continue
                    n += 1
    s.append(f"Cruces entre flujos de MP, SE y PT (verificación geométrica sobre el modelo): **{n}**. Cruces de hilos de "
             f"personal con flujos: todos dentro de las **{len(L.SENDAS)}** sendas peatonales señalizadas (X1 a "
             f"X{len(L.SENDAS)}).\n")
    # 7 sanitarios
    san = C.sanitarios()
    s.append("## 7. Sanitarios, vestuarios y servicios (Dec. 351/79 arts. 49 y 50)\n")
    s.append(f"Turno más numeroso: {san['H']} hombres ({C.PERSONAL['turno mañana']['H']} del turno mañana + "
             f"{C.PERSONAL['choferes']} choferes) y {san['M']} mujeres. Fuente: DT Servicios y oficinas y Dotación "
             "planta 2035, menos los 16 operarios de recargas del turno mañana, los 2 del turno tarde y la atención de "
             "recargas (el proceso va fuera de esta planta).\n")
    s.append(tabla(["Artefacto", "H requerido", "H proyectado", "M requerido", "M proyectado"],
                   [[k, san["req_H"][k], san["proy"]["H"][k], san["req_M"][k], san["proy"]["M"][k]]
                    for k in ("inodoros", "lavabos", "orinales", "duchas")]))
    s.append(f"\nArmarios: H {san['armarios_req']['H']} requeridos / {san['armarios_proy']['H']} proyectados; M "
             f"{san['armarios_req']['M']} / {san['armarios_proy']['M']} (vestuario de mujeres al 20 % de la dotación). "
             "Lockers individuales, 1 por empleado, en bloques de 7 columnas × 3 filas. El bloque de servicios quedó "
             "con holgura al salir recargas (podría achicarse un bloque de lockers y una ducha). Un sanitario accesible "
             "con ducha en el bloque de servicios y otro en administración (Ley 24.314, Dec. 914/97: círculo libre de Ø 1,50 m, espacio lateral de 0,80 m, "
             "barras); los sanitarios de planta (banda sur, sobre la calle AT2) son de hombres y de mujeres. Espacio de "
             "cuidado "
             f"no obligatorio (Dec. 144/2022 exige 100 o más personas; la dotación es {C.PERSONAL['total']}). Comedor de "
             "30 plazas (DT Servicios); sin recargas alcanzaría con 18 por tanda.\n")
    s.append(tabla(["Local", "m²"], [[f"{x.cod} {x.nombre}", f(x.rect.area, 1)] for x in L.LOCALES]))
    # 8 escape
    e = C.escape()
    s.append("\n## 8. Medios de escape (Dec. 351/79 anexo VII)\n")
    s.append(f"Factor de ocupación industrial 16 m²/persona: N = {e['N']} personas teóricas; n = N/100 -> "
             f"{e['unidades']} unidades de ancho de salida ({f(e['ancho_min'], 2)} m mínimos). Proyectado: "
             f"{e['salidas_emergencia']} salidas de emergencia de 1,10 m ({f(e['ancho_emergencia'], 2)} m) con barral "
             "antipánico, más los portones con puerta de hombre y el paso a servicios.\n")
    s.append(f"Recorrido real máximo hasta una salida, calculado sobre una grilla de 0,5 m que rodea los equipos: "
             f"**{f(e['peor_m'], 1)} m** (punto x = {f(e['punto'][0], 1)}, y = {f(e['punto'][1], 1)}), por debajo de los "
             "40 m que se toman como límite (verificar el artículo vigente).\n")
    # 9 extintores
    ex = C.extintores()
    s.append("## 9. Protección contra incendio\n")
    s.append(f"Extintores ABC de 10 kg en la nave: **{ex['cant']}** (mínimo por superficie 1 cada 200 m² = "
             f"{ex['minimo_sup']}), ubicados por cálculo para que ningún punto quede a más de 20 m de recorrido "
             "(IRAM 3517-2:2020, fuego clase A). Se suman 10 en anexos y exteriores, CO₂ junto a tableros y un carro de "
             "50 kg ABC en pintura y en la sala de polvo. Señalización con chapa baliza y cartel en altura (IRAM 3517-2 "
             "cap. 7). La reserva de agua contra incendio y la red de hidrantes quedan previstas en el terreno y se "
             "confirman con el estudio de carga de fuego.\n")
    # 10 iluminación
    s.append("## 10. Iluminación (método de los lúmenes)\n")
    lm = C.LUMINARIA
    s.append(f"Luminaria LED de {lm['potencia_w']} W y {f(lm['flujo_lm'], 0)} lm; factor de utilización {f(lm['UF'], 2)}; "
             f"mantenimiento {f(lm['MF'], 2)}. Niveles: nave 300 lx, depósitos 150 lx, pintura 500 lx, laboratorio 750 lx; "
             "soldadura y montaje fino 500 lx y líquidos penetrantes 750 lx con iluminación localizada.\n")
    il = C.iluminacion()
    s.append(tabla(["Sector", "lx", "m²", "Luminarias", "kW"],
                   [[f"{a} {b}", c, f(d, 0), e_, f(g, 2)] for a, b, c, d, e_, g in il]))
    s.append(f"\nTotal: {sum(r[4] for r in il)} luminarias, {f(sum(r[5] for r in il), 1)} kW.\n")
    # 11 redes
    r = C.redes()
    s.append("## 11. Redes: longitud de tendidos (criterio 4)\n")
    s.append(tabla(["Tablero seccional", "kW", "Largo desde el TGBT (m)"],
                   [[a, f(b, 1), f(d, 1)] for a, b, c, d in r["elec"]]))
    for tit, datos in (("Agua de PH y pérdidas a PTE", r["agua"]), ("Gas natural al horno y secadoras", r["gas"]),
                       ("Nitrógeno", r["n2"]), ("Gas de soldadura", r["sold"])):
        s.append(f"\n**{tit}**: " + ", ".join(f"{a} {f(b, 0)} m" for a, b in datos) +
                 f" (total {f(sum(b for a, b in datos), 0)} m).")
    s.append(f"\n\nAire comprimido (anillo, ramales y bajadas de 6 m): {f(r['aire_anillo_m'], 0)} m. Potencia "
             "instalada de equipos: "
             f"{f(r['kw_total'], 0)} kW.\n")
    # 12 flujos
    s.append("## 12. Longitud de los flujos\n")
    s.append(tabla(["Tipo", "Flujo", "Largo (m)"], [[a, b, f(c, 1)] for a, b, c in C.flujos()]))
    s.append("\n## 13. Supuestos a validar\n")
    s.append("- Tercerizados revendidos: volumen estimado (no figura en los Excel).\n"
             "- Retiros, FOS y FOT del parque industrial; ubicación de la celda de media tensión y de la reducción de gas.\n"
             "- Medidas de diseño (marcadas D con su criterio): confirmar con los proveedores al cotizar.\n"
             "- Textos normativos marcados como B en el README (Dec. 351/79 arts. 49, 50 y anexo VII; Res. SRT 960/2015): "
             "verificar la versión vigente en InfoLEG.\n"
             "- Recargas va fuera de esta planta (pedido v9): su dotación, sus insumos y su portón P2 se quitaron.\n"
             "- Muelle P3 contra W-CAR 11 (que supone planta sin muelle): a confirmar con el grupo.\n")
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write("\n".join(s))
