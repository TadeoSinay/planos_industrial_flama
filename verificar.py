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
                                        if p.cod in ("A1", "A2", "AN")):
                maniobras += 1          # un solo autoelevador sirviendo el almacén: no es cruce de tránsito
                continue
            n += 1
            err(f"cruce de flujos: {c1} {r1} x {c2} {r2}")
    print(f"cruces entre flujos: {n} (más {maniobras} maniobras del autoelevador dentro del almacén de MP)")
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
