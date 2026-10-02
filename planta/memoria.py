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
             "**CC** = Comparacion_corte.xlsx, **C** = cotización de proveedor, **E** = estimado, **SUP** = supuesto a validar.\n")
    # 1 demanda
    s.append("## 1. Demanda y tasas de diseño\n")
    s.append(tabla(["Formato", "Matafuegos (u/año)", "Cilindros vendidos (u/año)"],
                   [[k, f(a, 0), f(b, 0)] for k, (a, b) in C.DEMANDA.items()]))
    s.append(f"\nRecargas en planta: {f(C.RECARGAS, 0)} u/año (DT). Tercerizados revendidos: {f(C.TERCERIZADOS, 0)} u/año "
             "(**SUP**: 12,7 % no ABC sobre las ventas de equipos; no hay dato en los Excel).\n")
    s.append(f"Mes pico = {f(C.PICO, 2)} × promedio (dic-ene). Horas productivas del mes pico: {C.DIAS} días × {C.TURNOS} "
             f"turnos × {f(C.H_TURNO, 0)} h × {f(C.EFIC, 2)} = {f(C.H_MES, 0)} h.\n")
    s.append(tabla(["Familia", "Tasa de diseño (u/h)"], [[k, f(v, 1)] for k, v in t.items()]))
    # 2 layout
    s.append("\n## 2. Nave y sectores\n")
    s.append(f"Nave de {f(L.NAVE_L, 0)} × {f(L.NAVE_A, 0)} m = {f(L.NAVE_L * L.NAVE_A, 0)} m², recorrido en U con una línea "
             f"que converge paso a paso, pórticos de dos luces (19,40 y 24,60 m) cada {f(L.MODULO, 0)} m, altura libre "
             f"{f(L.ALTURA_LIBRE, 2)} m (Dec. 351/79 exige ≥ 3 m). Recargas dentro de la nave (ángulo SO, "
             f"{f(L.ANEXOS[1].rect.area, 0)} m²). Anexos: servicios {f(L.ANEXOS[0].rect.area, 0)} m² y sala técnica "
             f"{f(L.ANEXOS[2].rect.area, 0)} m².\n")
    s.append(tabla(["Código", "Sector", "m² proyectados", "m² requeridos", "Nota"],
                   [[x.cod, x.nombre, f(x.rect.area, 1), f(x.area_req, 1) if x.area_req else "-", x.nota]
                    for x in L.SECTORES]))
    s.append("\nLos m² requeridos de MP (hoja MP Almacén) suponen almacenamiento a piso o en rack de 3 niveles con medio "
             "pasillo propio. En el layout la chapa, los flejes, el caño y los casquetes van en cantiléver y racks en "
             "altura, frente al pasillo de autoelevador AM que comparten, con las mismas posiciones: hojas 15 paquetes "
             "(3 módulos × 5 niveles), flejes 21 rollos + 6 en espera, caño 12 atados, casquetes 18 pallets.\n")
    # 3 recepción
    s.append("\n## 3. Recepción de MP y análisis de peso de la carga\n")
    s.append("Se dimensiona para la carga máxima: un semirremolque de 18,6 m y 30 t o dos chasis de 10 m en el alero "
             "de descarga norte (23 × 10,6 m), con descarga por ambos lados con autoelevador. La MP entra por P1 al "
             "pasillo AM y queda en racks frente a la máquina que la consume (chapa frente a la guillotina, caño frente "
             "a los láseres, flejes frente a la prensa). Otros ingresos, junto a su consumo: P4 al sur (polvo), muelle M2 ("
             "insumos de terminación), P3 al este (químicos y pintura), M3 (casquetes y tercerizados) y P8 (polvo, "
             "estructuras y ruedas de carros).\n")
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
    s.append("\nSe adopta autoelevador eléctrico de 3,0 t con horquillas de 1,8 m y posicionador: toma el paquete por el "
             "lado largo (2,37 t > 2 t). El de 2,5 t que proponía el Excel queda justo (1,98 t) y no sirve por el lado "
             "corto.\n")
    # 4 sobrestock
    s.append("## 4. Anti-sobrestock de chapa SAE 1010\n")
    s.append(tabla(["Formato", "Hojas/semana", "Paquete de 2 t cubre (sem)", "Paquete propuesto", "Stock máx. (sem)"],
                   [[r["formato"], f(r["hojas_sem"], 1), f(r["cob_2t"], 1),
                     f"{r['hojas_paq']} hojas ({f(r['kg_paq'], 0)} kg)", f(r["cob_max"], 1)] for r in C.sobrestock()]))
    s.append("\nReglas: un módulo del cantiléver por formato con dos posiciones (en uso y en espera) y tope pintado; si "
             "están ocupadas no se emite pedido (kanban de 2 paquetes). Paquetes chicos en los formatos de bajo consumo "
             "para que ninguno cubra más de 2 semanas. Tarjeta de color por mes de ingreso y semáforo (verde < 4 semanas, "
             "amarillo 4 a 6, rojo > 6: se consume primero y se inspecciona óxido). Hoja LAF aceitada con film VCI, "
             "descargada y guardada siempre bajo techo, lejos de la PH y del lavado.\n")
    # 5 pulmones
    s.append("## 5. Pulmones y manejo de materiales (métodos y tiempos)\n")
    s.append(tabla(["Pulmón", "Tasa (u/h)", "Cobertura (h)", "Unidades", "Carros", "Criterio"],
                   [[r["pulmon"], f(r["tasa"], 1), f(r["cob_h"], 2), f(r["u"], 0), r["carros"], r["criterio"]]
                    for r in C.pulmones()]))
    M_ = C.manejo()
    s.append("\nTiempo por viaje = 2 × distancia / velocidad + tiempo fijo de toma y entrega. Distancias medidas sobre "
             "los recorridos del modelo; día pico 2035.\n")
    s.append(tabla(["Unidad de carga", "Medio", "Recorrido", "Viajes/día", "m", "min/viaje", "min/día"],
                   [[r["carga"], r["medio"], r["ruta"], f(r["viajes"], 1), f(r["dist"], 0), f(r["t_viaje"], 1),
                     f(r["min_dia"], 0)] for r in M_["filas"]]))
    s.append(f"\nOcupación sobre un turno útil de 408 min: autoelevador {f(M_['ocup']['Autoelevador'] * 100, 0)} %, "
             f"apiladora {f(M_['ocup']['Apiladora'] * 100, 0)} %. Un autoelevador eléctrico alcanza (y descarga los "
             f"camiones). Entre pasos se mueven {M_['carros_dia']} carros por día y por tramo: los empuja el operario que "
             "cierra el lote (< 1 min por viaje), sin tren logístico ni chofer; al norte de la senda no entra el "
             "autoelevador. Un abastecedor por turno hace el milk run de consumibles desde el pañol de línea y repone "
             "carros vacíos desde el supermercado PV.\n")
    s.append(tabla(["Portón", "Qué entra o sale", "Vehículo", "Frecuencia", "Horario"], [list(r) for r in C.PORTONES]))
    s.append("\nEl antiguo portón P5 (insumos de terminación) se suprimió: recibía ≈ 1 camión por semana a 10 m de los "
             "muelles, que trabajan muy por debajo de su capacidad; ahora esos pallets bajan por la rampa del muelle M2 "
             "y van con transpaleta al rack AL-2.\n")
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
    s.append(f"Turno más numeroso: {san['H']} hombres (47 del turno mañana + 8 choferes) y {san['M']} mujeres.\n")
    s.append(tabla(["Artefacto", "H requerido", "H proyectado", "M requerido", "M proyectado"],
                   [[k, san["req_H"][k], san["proy"]["H"][k], san["req_M"][k], san["proy"]["M"][k]]
                    for k in ("inodoros", "lavabos", "orinales", "duchas")]))
    s.append(f"\nArmarios: H {san['armarios_req']['H']} requeridos / {san['armarios_proy']['H']} proyectados; M "
             f"{san['armarios_req']['M']} / {san['armarios_proy']['M']} (vestuario de mujeres al 20 % de la dotación). "
             "Dos núcleos (principal y este) con sanitario accesible cada uno (Ley 24.314, Dec. 914/97: círculo libre de "
             "Ø 1,50 m, espacio lateral de 0,80 m, barras). Lactario como buena práctica (Ley 26.873). Espacio de cuidado "
             "no obligatorio (Dec. 144/2022 exige 100 o más personas; la dotación es 71). Comedor de 30 plazas en 2 "
             "tandas (DT Servicios).\n")
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
    for tit, datos in (("Agua de PH y pretratamiento a PTE", r["agua"]), ("Gas natural a hornos", r["gas"]),
                       ("Nitrógeno", r["n2"]), ("Gas de soldadura", r["sold"])):
        s.append(f"\n**{tit}**: " + ", ".join(f"{a} {f(b, 0)} m" for a, b in datos) +
                 f" (total {f(sum(b for a, b in datos), 0)} m).")
    s.append(f"\n\nAnillo de aire comprimido: {f(r['aire_anillo_m'], 0)} m. Potencia instalada de equipos: "
             f"{f(r['kw_total'], 0)} kW.\n")
    # 12 flujos
    s.append("## 12. Longitud de los flujos\n")
    s.append(tabla(["Tipo", "Flujo", "Largo (m)"], [[a, b, f(c, 1)] for a, b, c in C.flujos()]))
    s.append("\n## 13. Supuestos a validar\n")
    s.append("- Tercerizados revendidos: volumen estimado (no figura en los Excel).\n"
             "- Retiros, FOS y FOT del parque industrial; ubicación de la celda de media tensión y de la reducción de gas.\n"
             "- Medidas de equipos marcados E (estimados): confirmar con los proveedores.\n"
             "- Textos normativos marcados como B en el README (Dec. 351/79 arts. 49, 50 y anexo VII; Res. SRT 960/2015): "
             "verificar la versión vigente en InfoLEG.\n"
             "- Recargas se incluye porque figura en el dimensionamiento técnico, aunque no estaba en la lista de secciones "
             "del pedido.\n")
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write("\n".join(s))
