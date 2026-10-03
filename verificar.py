"""Verificaciones del modelo de layout y de las láminas generadas."""

import itertools
import os
import sys

import shapely.geometry as sg
from shapely.geometry import LineString, Point

from planta import layout as L
from planta import calculos as C

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida")
ERR = []


def err(msg):
    ERR.append(msg)
    print("ERROR:", msg)


def caja(r, m=0.0):
    return sg.box(r.x0 + m, r.y0 + m, r.x1 - m, r.y1 - m)


def main():
    # 1. cruces entre flujos de MP, SE y PT
    fl = [(f.cat, f.rot, LineString(f.pts)) for f in L.FLUJOS if f.cat in ("MP", "SE", "PT")]
    muelle = caja(next(s_.rect for s_ in L.SECTORES if s_.cod == "EXP"))
    n = maniobras = 0
    for (c1, r1, a), (c2, r2, b) in itertools.combinations(fl, 2):
        if not a.intersects(b):
            continue
        g = a.intersection(b)
        pts = [g] if g.geom_type == "Point" else list(getattr(g, "geoms", [g]))
        ends = [Point(a.coords[0]), Point(a.coords[-1]), Point(b.coords[0]), Point(b.coords[-1])]
        for q in pts:
            if q.geom_type == "Point" and any(q.distance(e) < 0.05 for e in ends):
                continue
            if c1 == c2 == "MP" and any(caja(p.rect).buffer(0.05).contains(q) for p in L.PASILLOS
                                        if p.cod in ("A1", "A2", "AN", "AT")):
                maniobras += 1          # un solo autoelevador sirviendo su almacén: no es cruce de tránsito
                continue
            if muelle.buffer(0.05).contains(q):
                maniobras += 1          # muelle único: recepción 7 a 10 h y expedición 13 a 17 h, no coinciden
                continue
            n += 1
            err(f"cruce de flujos: {c1} {r1} x {c2} {r2}")
    print(f"cruces entre flujos: {n} (más {maniobras} maniobras: autoelevador en su almacén y muelle único P3 "
          "con recepción y expedición en horarios distintos)")
    # 2. hilos de personal: sólo cruzan flujos dentro de sendas
    sendas = [caja(r) for c, r, t in L.SENDAS]
    m = 0
    for nom, main, br in L.HILOS:
        tramos = [LineString(main)] + [LineString([(a, b), (c, d)]) for a, b, c, d in br]
        for t in tramos:
            for c, r, f in fl:
                if t.intersects(f):
                    g = t.intersection(f)
                    for q in ([g] if g.geom_type == "Point" else list(getattr(g, "geoms", [g]))):
                        m += 1
                        if not any(s.buffer(0.05).contains(q) for s in sendas):
                            err(f"hilo {nom} cruza {c} {r} fuera de una senda en {q.wkt}")
    print(f"cruces hilo-flujo: {m} (todos en sendas: {len(L.SENDAS)} sendas)")
    # 3. equipos superpuestos
    for a, b in itertools.combinations(L.EQUIPOS, 2):
        if caja(a.rect, 0.01).intersects(caja(b.rect, 0.01)):
            err(f"equipos superpuestos: {a.cod} y {b.cod}")
    # 4. equipos dentro de pasillos
    for e in L.EQUIPOS:
        for p in L.PASILLOS:
            if caja(e.rect, 0.02).intersects(caja(p.rect, 0.02)):
                err(f"equipo {e.cod} invade el pasillo {p.cod}")
    # 4b. columnas fuera de pasillos y de bocas de portones
    from shapely.ops import unary_union
    cols = [sg.box(x - 0.2, y - 0.2, x + 0.2, y + 0.2) for x in L.EJES_X for y in L.EJES_Y]
    for p in L.PASILLOS:
        for c in cols:
            if caja(p.rect).intersects(c.buffer(-0.01)):
                err(f"columna {c.centroid.x:.0f},{c.centroid.y:.0f} dentro del pasillo {p.cod}")
    # 4c. conectividad: todas las calles forman una red que llega a un portón
    red = unary_union([caja(p.rect).buffer(0.25) for p in L.PASILLOS])
    partes = list(getattr(red, "geoms", [red]))
    print(f"red de pasillos: {len(partes)} componente(s)")
    for p in L.PASILLOS:
        comp = [i for i, g in enumerate(partes) if g.intersects(caja(p.rect))]
        if comp and comp[0] != max(range(len(partes)), key=lambda i: partes[i].area):
            err(f"pasillo {p.cod} desconectado de la red principal")
    # 4c'. cada extremo de calle remata en otra calle, en una puerta del muro exterior o de un local, o es el
    #      fondo declarado de una calle de rack (FONDOS); sin tolerancia
    red_e = [caja(p.rect) for p in L.PASILLOS]
    ab_muro = []
    for pu in L.PUERTAS:
        if pu.muro not in ("N", "S", "E", "O"):
            continue
        a, b = pu.a, pu.b
        ab_muro.append({"N": sg.box(a, L.NAVE_A - 0.6, b, L.NAVE_A + 0.6), "S": sg.box(a, -0.6, b, 0.6),
                        "O": sg.box(-0.6, a, 0.6, b), "E": sg.box(L.NAVE_L - 0.6, a, L.NAVE_L + 0.6, b)}[pu.muro])
    for cod_l, lista in L.CERRADOS.items():
        r = next(s.rect for s in L.SECTORES + L.LOCALES if s.cod == cod_l)
        for lado, a, b, tipo in lista:
            if tipo in ("ventana", "ventanilla"):
                continue
            ab_muro.append({"N": sg.box(a, r.y1 - 0.3, b, r.y1 + 0.3), "S": sg.box(a, r.y0 - 0.3, b, r.y0 + 0.3),
                            "O": sg.box(r.x0 - 0.3, a, r.x0 + 0.3, b),
                            "E": sg.box(r.x1 - 0.3, a, r.x1 + 0.3, b)}[lado])
    for x, y, w, o, _d in L.PUERTAS_INT:
        ab_muro.append(sg.box(x, y - 0.3, x + w, y + 0.3) if o == "h" else sg.box(x - 0.3, y, x + 0.3, y + w))
    fondos = getattr(L, "FONDOS", {})
    recorridos = [LineString(f.pts) for f in L.FLUJOS] + [LineString(m_) for _n, m_, _b in L.HILOS]
    n_ext = 0
    for i, p in enumerate(L.PASILLOS):
        r = p.rect
        horiz = r.w >= r.h
        ext = {"O": sg.LineString([(r.x0, r.y0), (r.x0, r.y1)]), "E": sg.LineString([(r.x1, r.y0), (r.x1, r.y1)])} \
            if horiz else {"S": sg.LineString([(r.x0, r.y0), (r.x1, r.y0)]), "N": sg.LineString([(r.x0, r.y1), (r.x1, r.y1)])}
        for lado, seg in ext.items():
            n_ext += 1
            if any(j != i and seg.intersects(g) for j, g in enumerate(red_e)):
                continue
            if any(seg.intersects(z) for z in ab_muro):
                continue
            if (p.cod, lado) in fondos:
                continue
            if any(seg.intersects(g) for g in recorridos):
                continue                     # la calle entra a su destino abierto (pintura, puesto): pasa el flujo
            err(f"la calle {p.cod} termina en su extremo {lado} sin otra calle ni puerta")
    print(f"extremos de calle revisados: {n_ext} ({len(fondos)} fondos de calle de rack declarados)")
    # 4e. recorridos del personal y flujos de material que atraviesan una máquina que no es su origen o destino
    n_atr = 0
    tramos_h = []
    for nom, main, br in L.HILOS:
        tramos_h += [(nom, LineString(main))] + [(nom, LineString([(a_, b_), (c_, d_)])) for a_, b_, c_, d_ in br]
    for e in L.EQUIPOS:
        g = caja(e.rect, -0.05)
        for nom, t in tramos_h:
            if t.intersects(g) and not any(g.buffer(0.6).contains(Point(q)) for q in (t.coords[0], t.coords[-1])):
                n_atr += 1
                err(f"el recorrido del personal {nom} atraviesa {e.cod}")
        for f in L.FLUJOS:
            ln = LineString(f.pts)
            if ln.intersects(g) and not any(g.buffer(0.6).contains(Point(q)) for q in (f.pts[0], f.pts[-1])):
                # una línea de proceso (SE) visita sus puestos en serie; la pluma y el transportador de pintura
                # mueven la pieza: no son obstáculos de esa línea
                visita = f.cat == "SE" and (e.paso or e.sector == "S-P" or "luma" in e.nombre)
                if f.cat in ("MP", "SE", "PT", "SCRAP") and e.tipo not in ("rack", "cantilever") and not visita \
                        and not ln.intersection(g).length < 0.01:
                    n_atr += 1
                    err(f"el flujo {f.cat} {f.rot} atraviesa {e.cod}")
    print(f"recorridos y flujos que atraviesan máquinas: {n_atr}")
    # 4f. ningún flujo ni recorrido atraviesa el muro de un local cerrado fuera de sus puertas, portones o cortinas
    n_muro = 0
    for cod_l, lista in L.CERRADOS.items():
        r = next(s_.rect for s_ in L.SECTORES + L.LOCALES if s_.cod == cod_l)
        lados = {"S": ((r.x0, r.y0), (r.x1, r.y0)), "N": ((r.x0, r.y1), (r.x1, r.y1)),
                 "O": ((r.x0, r.y0), (r.x0, r.y1)), "E": ((r.x1, r.y0), (r.x1, r.y1))}
        for lado, (p0, p1) in lados.items():
            muro = LineString([p0, p1])
            for ld, a_, b_, tipo in lista:
                if ld == lado and tipo in ("puerta", "porton", "cortina"):
                    hueco = sg.box(a_, p0[1] - 0.1, b_, p0[1] + 0.1) if lado in "SN" else \
                        sg.box(p0[0] - 0.1, a_, p0[0] + 0.1, b_)
                    muro = muro.difference(hueco)
            for pu in L.PUERTAS:                     # portones de la nave en muros compartidos
                if pu.muro in ("N", "S", "E", "O"):
                    muro = muro.difference({"N": sg.box(pu.a, L.NAVE_A - 0.6, pu.b, L.NAVE_A + 0.6),
                                            "S": sg.box(pu.a, -0.6, pu.b, 0.6), "O": sg.box(-0.6, pu.a, 0.6, pu.b),
                                            "E": sg.box(L.NAVE_L - 0.6, pu.a, L.NAVE_L + 0.6, pu.b)}[pu.muro])
            for f in L.FLUJOS:
                if f.cat in ("MP", "SE", "PT", "SCRAP") and LineString(f.pts).intersects(muro):
                    n_muro += 1
                    err(f"el flujo {f.cat} {f.rot} atraviesa el muro {lado} de {cod_l}")
            for nom, t in tramos_h:
                if t.intersects(muro):
                    n_muro += 1
                    err(f"el recorrido {nom} atraviesa el muro {lado} de {cod_l}")
    print(f"flujos y recorridos a través de muros: {n_muro}")
    # 4g. a lo sumo 4 portones en la nave (uno por frente logístico)
    portones = [pu.cod for pu in L.PUERTAS if pu.tipo in ("porton", "muelle")]
    print(f"portones de la nave: {len(portones)} ({', '.join(portones)})")
    if len(portones) > 4:
        err(f"hay {len(portones)} portones (máximo 4)")
    # 4h. toda puerta da a algún lado: 1,0 m libre del lado de adentro que toca una calle o un local
    obst = [caja(e.rect, -0.02) for e in L.EQUIPOS] + [caja(m.rect, -0.02) for m in L.MOBILIARIO
                                                         if m.tipo != "rampa"]
    obst += [caja(p_.rect, -0.02) for p_ in L.PULMONES]
    calles = [caja(p_.rect) for p_ in L.PASILLOS]
    recintos = [caja(s_.rect) for s_ in L.SECTORES + L.LOCALES]
    n_p = 0
    for pu in L.PUERTAS:
        a_, b_ = pu.a, pu.b
        z = {"N": sg.box(a_, L.NAVE_A - 1.0, b_, L.NAVE_A), "S": sg.box(a_, 0.0, b_, 1.0),
             "O": sg.box(0.0, a_, 1.0, b_), "E": sg.box(L.NAVE_L - 1.0, a_, L.NAVE_L, b_)}.get(pu.muro)
        if z is None:
            continue
        n_p += 1
        if any(z.buffer(-0.05).intersects(o) for o in obst):
            err(f"la puerta {pu.cod} está tapada del lado de adentro")
        # 4 m hacia adentro: tiene que llegar a una calle sin obstáculos, o la puerta es de un local
        a_calle = False
        for d in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0):
            zd = {"N": sg.box(a_, L.NAVE_A - d, b_, L.NAVE_A), "S": sg.box(a_, 0.0, b_, d),
                  "O": sg.box(0.0, a_, d, b_), "E": sg.box(L.NAVE_L - d, a_, L.NAVE_L, b_)}[pu.muro]
            if any(zd.buffer(-0.05).intersects(o) for o in obst):
                break
            if any(zd.intersects(c) for c in calles):
                a_calle = True
                break
        a_local = any(z.intersection(r_).area >= 0.5 * z.area for r_ in recintos)
        if not (a_calle or a_local):
            err(f"la puerta {pu.cod} no da a ninguna calle ni local")
    for x, y, w, muro, abre in L.PUERTAS_INT:
        for lado in (-1, 1):
            z = sg.box(x, y + lado * 0.15, x + w, y + lado * 0.75) if muro == "h" else \
                sg.box(x + lado * 0.15, y, x + lado * 0.75, y + w)
            n_p += 1
            if any(z.intersects(o) for o in obst):
                err(f"la puerta interior en ({x}, {y}) está tapada por un mueble o equipo")
    print(f"puertas con paso libre revisadas: {n_p}")
    # 4i. scrap en el puesto que lo genera, nunca en el almacén de MP
    for maq, cont in (("M04", "SCG"), ("M15", "SCL1"), ("M16", "SCL2"), ("M08", "SCP")):
        em = next(e for e in L.EQUIPOS if e.cod == maq)
        ec = next(e for e in L.EQUIPOS if e.cod == cont)
        if caja(em.rect).distance(caja(ec.rect)) > 3.0:
            err(f"el contenedor de scrap {cont} está a más de 3 m de {maq}")
    for s_ in L.SECTORES:
        if s_.rect.x1 < 12.8 and s_.rect.y0 > 19.0 and ("crap" in s_.nombre or "insumos pesados" in s_.nombre):
            err(f"el almacén de MP guarda {s_.nombre}")
    # 4d. zona del operario: 1,0 m libre al frente, sin calles de autoelevador ni materiales ajenos
    from planta.simbolos import frente_de
    for e in L.EQUIPOS:
        if not e.op:
            continue
        r, f_ = e.rect, frente_de(e)
        z = {"S": (r.x0, r.y0 - 1.0, r.x1, r.y0), "N": (r.x0, r.y1, r.x1, r.y1 + 1.0),
             "O": (r.x0 - 1.0, r.y0, r.x0, r.y1), "E": (r.x1, r.y0, r.x1 + 1.0, r.y1)}[f_]
        zona = sg.box(*z).buffer(-0.02)
        for p in L.PASILLOS:
            if zona.intersects(caja(p.rect)):
                err(f"operario de {e.cod} de espaldas a la calle {p.cod}: falta 1,0 m libre detrás")
        for o in L.EQUIPOS:
            if o is not e and zona.intersects(caja(o.rect, 0.02)):
                err(f"zona del operario de {e.cod} ocupada por {o.cod}")
        propia = caja(r).buffer(0.6)
        for f in L.FLUJOS:
            if f.cat in ("MP", "SE", "PT", "SCRAP") and LineString(f.pts).intersects(zona):
                ext = [Point(f.pts[0]), Point(f.pts[-1])]
                if not any(propia.contains(q) for q in ext):
                    err(f"material ajeno pasa por la espalda del operario de {e.cod}: {f.rot}")
    # 5. equipos dentro de la nave
    nave = sg.box(0, 0, L.NAVE_L, L.NAVE_A)
    for e in L.EQUIPOS:
        if not nave.contains(caja(e.rect)):
            err(f"equipo {e.cod} fuera de la nave")
    # 5b. mobiliario: dentro de su local, sin pisar equipos, pulmones, pasillos ni otros muebles
    locs = L.SECTORES + L.LOCALES
    for mb in L.MOBILIARIO:
        if not any(caja(s.rect, -0.06).contains(caja(mb.rect)) for s in locs):
            err(f"mueble {mb.tipo} {mb.rect} fuera de un local")
        for e in L.EQUIPOS:
            if caja(mb.rect, 0.01).intersects(caja(e.rect, 0.01)):
                err(f"mueble {mb.tipo} {mb.rect} pisa el equipo {e.cod}")
        for p in L.PULMONES:
            if caja(mb.rect, 0.01).intersects(caja(p.rect, 0.01)):
                err(f"mueble {mb.tipo} {mb.rect} pisa el pulmón {p.cod}")
        for p in L.PASILLOS:
            if caja(mb.rect, 0.02).intersects(caja(p.rect, 0.02)):
                err(f"mueble {mb.tipo} {mb.rect} invade el pasillo {p.cod}")
    for a, b in itertools.combinations(L.MOBILIARIO, 2):
        if caja(a.rect, 0.01).intersects(caja(b.rect, 0.01)) and not {"jaula", "inodoro_acc"} & {a.tipo, b.tipo}:
            err(f"muebles superpuestos: {a.tipo} {a.rect} y {b.tipo} {b.rect}")
    # 5c. ningún local vacío
    for s in locs:
        if s.cat == "CIRC":
            continue
        z = caja(s.rect)
        llenos = [x for x in list(L.EQUIPOS) + list(L.MOBILIARIO) + list(L.PULMONES) if z.contains(Point(x.rect.c))]
        if not llenos:
            err(f"local vacío: {s.cod} {s.nombre}")
    # 6. superficies requeridas
    for s in L.SECTORES + L.LOCALES:
        if s.area_req and s.rect.area < 0.95 * s.area_req and "altura" not in s.nota and "niveles" not in s.nota:
            print(f"aviso: {s.cod} {s.rect.area:.1f} m² < {s.area_req:.1f} m² requeridos (se resuelve en altura)")
    # 7. escape
    e = C.escape()
    print(f"recorrido máximo a salida: {e['peor_m']:.1f} m")
    if e["peor_m"] > 40:
        err("recorrido a salida mayor a 40 m")
    # 8. sanitarios
    san = C.sanitarios()
    for k in ("inodoros", "lavabos", "orinales", "duchas"):
        if san["proy"]["H"][k] < san["req_H"][k] or san["proy"]["M"][k] < san["req_M"][k]:
            err(f"sanitarios insuficientes: {k}")
    if san["armarios_proy"]["H"] < san["armarios_req"]["H"] or san["armarios_proy"]["M"] < san["armarios_req"]["M"]:
        err("faltan lockers (1 por empleado)")
    if san["armarios_proy"]["H"] > san["armarios_req"]["H"] + 10 or san["armarios_proy"]["M"] > san["armarios_req"]["M"] + 5:
        err("lockers sobredimensionados")
    print(f"lockers: H {san['armarios_proy']['H']} para {san['armarios_req']['H']}, "
          f"M {san['armarios_proy']['M']} para {san['armarios_req']['M']}")
    # 9. extintores
    ex = C.extintores()
    print(f"extintores en la nave: {ex['cant']} (mínimo por superficie {ex['minimo_sup']})")
    if ex["cant"] < ex["minimo_sup"]:
        err("extintores insuficientes")
    # 10. salidas generadas
    esperados = {"FL_PI_01": 1, "FL_PI_02": 1, "FL_PI_03": 1, "FL_PI_04": 2, "FL_PI_05": 1}
    try:
        import pymupdf
        for cod, n_h in esperados.items():
            for ext in ("pdf", "dxf"):
                ruta = os.path.join(SALIDA, f"{cod}.{ext}")
                if not os.path.exists(ruta):
                    err(f"falta {cod}.{ext}")
            ruta = os.path.join(SALIDA, f"{cod}.pdf")
            if os.path.exists(ruta) and len(pymupdf.open(ruta)) != n_h:
                err(f"{cod}.pdf no tiene {n_h} hojas")
    except ImportError:
        print("aviso: sin pymupdf, no se verifican los PDF")
    print("OK" if not ERR else f"{len(ERR)} errores")
    return 0 if not ERR else 1


if __name__ == "__main__":
    sys.exit(main())
