"""Verificador del layout v10: geometría (superposiciones, huecos sin nombre, equipos fuera de su zona),
frente libre de cada operario, acceso del autoelevador, columnas y superficies pedidas por las fuentes."""

import shapely.geometry as sg
from shapely.ops import unary_union

from . import modelo as M

TOL = 0.02


def box(r, d=0.0):
    return sg.box(r.x0 - d, r.y0 - d, r.x1 + d, r.y1 + d)


def frente(e, prof=0.95):
    r = e.rect
    return {"S": sg.box(r.x0, r.y0 - prof, r.x1, r.y0), "N": sg.box(r.x0, r.y1, r.x1, r.y1 + prof),
            "E": sg.box(r.x1, r.y0, r.x1 + prof, r.y1), "O": sg.box(r.x0 - prof, r.y0, r.x0, r.y1)}[e.frente]


def verificar(silencioso=False):
    err, avi = [], []
    nave = sg.box(0, 0, M.LX, M.LY)
    zonas = {z.cod: z for z in M.ZONAS}
    if len(zonas) != len(M.ZONAS):
        vistos = set()
        for z in M.ZONAS:
            if z.cod in vistos:
                err.append(f"Código de zona repetido: {z.cod}")
            vistos.add(z.cod)
    # 1. zonas dentro de la nave y sin superposición
    zs = [(z, box(z.rect)) for z in M.ZONAS]
    for z, g in zs:
        if z.rect.w <= 0 or z.rect.h <= 0:
            err.append(f"Zona {z.cod} con medida nula o negativa")
        if not nave.buffer(TOL).contains(g):
            err.append(f"Zona {z.cod} fuera de la nave")
    for i in range(len(zs)):
        for j in range(i + 1, len(zs)):
            a = zs[i][1].intersection(zs[j][1]).area
            if a > 0.01:
                err.append(f"Superposición de zonas {zs[i][0].cod} y {zs[j][0].cod}: {a:.2f} m²")
    # 2. huecos sin nombre
    hueco = nave.difference(unary_union([g for _, g in zs]))
    for p in getattr(hueco, "geoms", [hueco]):
        if p.area > 0.05:
            x0, y0, x1, y1 = p.bounds
            err.append(f"Superficie sin nombre de {p.area:.2f} m² en x {x0:.2f}-{x1:.2f}, y {y0:.2f}-{y1:.2f}")
    # 3. equipos dentro de su zona y sin superposición
    eqs = [(e, box(e.rect)) for e in M.EQUIPOS]
    cods = set()
    for e, g in eqs:
        if e.cod in cods:
            err.append(f"Código de equipo repetido: {e.cod}")
        cods.add(e.cod)
        z = zonas.get(e.zona)
        if z is None:
            err.append(f"Equipo {e.cod} en zona inexistente {e.zona}")
            continue
        if not box(z.rect, TOL).contains(g):
            err.append(f"Equipo {e.cod} ({e.nombre}) sale de su zona {e.zona}")
    for i in range(len(eqs)):
        for j in range(i + 1, len(eqs)):
            a = eqs[i][1].intersection(eqs[j][1]).area
            if a > 0.005:
                err.append(f"Superposición de equipos {eqs[i][0].cod} y {eqs[j][0].cod}: {a:.2f} m²")
    # 4. frente del operario: 0,95 m libres dentro de la zona (o en un pasillo) y sin otros equipos
    pas = unary_union([box(z.rect) for z in M.ZONAS if z.tipo == "pasillo"])
    for e, g in eqs:
        if e.op <= 0:
            continue
        f = frente(e)
        z = zonas.get(e.zona)
        dentro = box(z.rect, TOL).union(pas)
        if not dentro.buffer(TOL).contains(f):
            err.append(f"Frente del operario de {e.cod} ({e.nombre}) fuera de su zona")
        for o, go in eqs:
            if o is e:
                continue
            a = f.intersection(go).area
            if a > 0.02:
                err.append(f"Frente del operario de {e.cod} ocupado por {o.cod} ({a:.2f} m²)")
    # 5. acceso del autoelevador: equipos «ae» a menos de 1,6 m (ancho de la senda) de un carril AE
    ae = unary_union([box(z.rect) for z in M.ZONAS if z.sub == "AE"])
    for e, g in eqs:
        if e.ae and g.distance(ae) > 1.6:
            err.append(f"{e.cod} ({e.nombre}) necesita autoelevador y está a {g.distance(ae):.2f} m del carril")
    # 6. columnas: no dentro de equipos ni dentro de un carril AE
    for x in M.EJES_X:
        for y in M.EJES_Y:
            c = sg.box(x - M.COL / 2, y - M.COL / 2, x + M.COL / 2, y + M.COL / 2)
            for e, g in eqs:
                if c.intersection(g).area > 0.001:
                    err.append(f"Columna ({x:.1f}, {y:.1f}) dentro del equipo {e.cod}")
            for z in M.ZONAS:
                if z.sub == "AE" and box(z.rect).buffer(-0.25).intersects(c):
                    err.append(f"Columna ({x:.1f}, {y:.1f}) dentro del carril {z.cod}")
    # 7. puertas: sin columnas en el vano y con 1,0 m libre de equipos del lado de adentro
    for pu in M.PUERTAS:
        if pu.muro in "NS":
            y = M.LY if pu.muro == "N" else 0.0
            cols = [x for x in M.EJES_X if pu.a - M.COL / 2 < x < pu.b + M.COL / 2]
            dentro = sg.box(pu.a, y - 1.0, pu.b, y) if pu.muro == "N" else sg.box(pu.a, 0, pu.b, 1.0)
        else:
            x = M.LX if pu.muro == "E" else 0.0
            cols = [y for y in M.EJES_Y if pu.a - M.COL / 2 < y < pu.b + M.COL / 2]
            dentro = sg.box(x - 1.0, pu.a, x, pu.b) if pu.muro == "E" else sg.box(0, pu.a, 1.0, pu.b)
        if cols:
            err.append(f"Puerta {pu.cod} con columna en el vano ({cols})")
        for e, g in eqs:
            if dentro.intersection(g).area > 0.01:
                err.append(f"Puerta {pu.cod} tapada por {e.cod} ({e.nombre})")
    # 8. superficie pedida por la fuente
    for z in M.ZONAS:
        if z.req and z.rect.area < 0.98 * z.req:   # W-CAR da medidas «≈»: 2 % de tolerancia
            avi.append(f"{z.cod}: {z.rect.area:.1f} m² contra {z.req:.1f} m² de la fuente")
    # 9. anexo de administración: locales sin superposición ni huecos, muebles dentro de su local, sanitarios
    anexo = sg.box(M.XA0, M.YA0, M.XA1, M.YA1)
    ad = [(z, box(z.rect)) for z in M.ADMIN]
    for i in range(len(ad)):
        for j in range(i + 1, len(ad)):
            a_ = ad[i][1].intersection(ad[j][1]).area
            if a_ > 0.01:
                err.append(f"Superposición de locales {ad[i][0].cod} y {ad[j][0].cod}: {a_:.2f} m²")
    resto = anexo.difference(unary_union([g for _, g in ad]))
    if resto.area > 0.05:
        err.append(f"Anexo: {resto.area:.2f} m² sin local")
    cuenta = {}
    mobs = [(t, box(r), fr, n) for t, r, fr, n in M.MOB]
    for t, g, fr, n in mobs:
        loc = [z for z, gz in ad if gz.buffer(TOL).contains(g)]
        if not loc:
            err.append(f"Mueble {t} en ({g.bounds[0]:.1f}, {g.bounds[1]:.1f}) fuera de los locales")
            continue
        cuenta.setdefault((loc[0].cod, t), 0)
        cuenta[(loc[0].cod, t)] += n
    for i in range(len(mobs)):
        for j in range(i + 1, len(mobs)):
            if mobs[i][1].intersection(mobs[j][1]).area > 0.01:
                err.append(f"Superposición de muebles {mobs[i][0]} y {mobs[j][0]} en {mobs[i][1].bounds[:2]}")
    pedido = {("AD-VH", "inodoro"): 2, ("AD-VH", "mingitorios"): 3, ("AD-VH", "lavabos"): 4, ("AD-VH", "duchas"): 3,
              ("AD-VH", "armarios"): 34, ("AD-VM", "inodoro"): 1, ("AD-VM", "lavabos"): 1, ("AD-VM", "duchas"): 1,
              ("AD-VM", "armarios"): 4}
    for k, v in pedido.items():
        if cuenta.get(k, 0) < v:
            err.append(f"{k[0]}: {cuenta.get(k, 0)} {k[1]} contra {v} pedidos (Dec. 351/79 art. 49 / X-DT)")
    for x, y, w, muro, abre in M.PUERTAS_ADMIN + M.PUERTAS_LOCALES:
        if w > 2.0:
            continue
        if muro == "h":
            barrido = sg.box(x, y, x + w, y + abre * w) if abre > 0 else sg.box(x, y - w, x + w, y)
        else:
            barrido = sg.box(x, y, x + abre * w, y + w) if abre > 0 else sg.box(x - w, y, x, y + w)
        for t, g, fr, n in mobs:
            if barrido.intersection(g).area > 0.005:
                err.append(f"La puerta en ({x:.1f}, {y:.1f}) barre sobre {t}")
        for e, g in eqs:
            if barrido.intersection(g).area > 0.005:
                err.append(f"La puerta en ({x:.1f}, {y:.1f}) barre sobre el equipo {e.cod}")
    for cod, muro, a_, b_, uso in M.PUERTAS_EXT_ADMIN:
        barrido = {"N": sg.box(a_, M.YA1 - (b_ - a_) / 2, b_, M.YA1), "E": sg.box(M.XA1 - (b_ - a_), a_, M.XA1, b_),
                   "O": sg.box(M.XA0, a_, M.XA0 + (b_ - a_), b_)}[muro]
        for t, g, fr, n in mobs:
            if barrido.intersection(g).area > 0.005:
                err.append(f"La puerta {cod} barre sobre {t}")
    for z in M.ZONAS:
        if z.tipo == "local":
            r = z.rect
            tiene = any((muro == "h" and abs(y - r.y0) + abs(y - r.y1) - r.h < 0.01 and min(abs(y - r.y0), abs(y - r.y1)) < 0.01
                         and r.x0 - 0.01 <= x and x + w <= r.x1 + 0.01) or
                        (muro == "v" and min(abs(x - r.x0), abs(x - r.x1)) < 0.01 and r.y0 - 0.01 <= y and y + w <= r.y1 + 0.01)
                        for x, y, w, muro, abre in M.PUERTAS_LOCALES)
            if not tiene:
                err.append(f"El local {z.cod} no tiene puerta")
    # mobiliario de los locales de la nave: dentro de su local y sin pisar el barrido de las puertas
    zon = {z.cod: z for z in M.ZONAS}
    mn = [(t, box(r), fr, n, zc) for t, r, fr, n, zc, fu in M.MOB_NAVE]
    for t, g, fr, n, zc in mn:
        if not box(zon[zc].rect, TOL).contains(g):
            err.append(f"Mueble {t} fuera de su local {zc}")
        for o in mn:
            if o[1] is not g and o[1].intersection(g).area > 0.01:
                err.append(f"Superposición de muebles {t} y {o[0]} en {zc}")
    for x, y, w, muro, abre in M.PUERTAS_LOCALES:
        if w > 2.0:
            continue
        barrido = (sg.box(x, y, x + w, y + abre * w) if abre > 0 else sg.box(x, y - w, x + w, y)) if muro == "h" else \
            (sg.box(x, y, x + abre * w, y + w) if abre > 0 else sg.box(x - w, y, x, y + w))
        for t, g, fr, n, zc in mn:
            if barrido.intersection(g).area > 0.005:
                err.append(f"La puerta en ({x:.1f}, {y:.1f}) barre sobre {t} de {zc}")
    sillas = sum(n for (c, t), n in cuenta.items() if c == "AD-CO" and t == "mesa")
    if sillas < 18:
        err.append(f"Comedor: {sillas} plazas contra 18 (X-DT)")
    for pu in M.PUERTAS:
        if pu.muro == "N" and not any(z.rect.x0 <= pu.a and pu.b <= z.rect.x1 and z.rect.y0 <= M.YA0 + 0.01
                                      for z in M.ADMIN) and M.XA0 < pu.b and pu.a < M.XA1:
            err.append(f"Puerta {pu.cod} del muro norte no cae entera en un local del anexo")
    if not silencioso:
        for s in err:
            print("ERROR  ", s)
        for s in avi:
            print("AVISO  ", s)
        print(f"{len(err)} errores, {len(avi)} avisos; {len(M.ZONAS)} zonas, {len(M.EQUIPOS)} equipos")
    return err, avi


if __name__ == "__main__":
    verificar()
