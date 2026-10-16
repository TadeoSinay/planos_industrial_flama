"""Seguridad e higiene del layout v10 (lámina FL_PI10_07): medios de escape, matafuegos, iluminación de emergencia,
flechas de evacuación, señales y su verificación.

Grilla de 0,5 m sobre la nave. Obstáculos: equipos (salvo las marcas de piso), columnas, tabiques de los locales (con el
vano de sus puertas) y barandas de las sendas (con sus cruces). Las distancias se miden por la línea de libre trayectoria
(Dijkstra con 8 vecinos, sin cortar esquinas) desde las salidas: puertas peatonales y de emergencia de 1,10 m o más que
abren hacia afuera (Dec. 351/79, anexo VII: 2 unidades de ancho de salida de 0,55 m). Los portones de vehículos y las
puertas a la administración no se cuentan como salidas.
"""

import heapq
import math
from functools import lru_cache

from . import modelo as M

P = 0.5
NX, NY = int(round(M.LX / P)), int(round(M.LY / P))
PISO = {"zona_carga", "canaleta"}          # se camina por encima (los lugares de carros y de NC están ocupados)
ANCHO_MIN = 1.10
INF = float("inf")
VEC = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)),
       (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2))]
# barandas: (y de la línea, x desde, x hasta, aberturas)
BARANDAS = [(M.Y_AE, 0.4, M.LX - 0.4, M.CRUCES_A2), (M.Y_M, M.X_AL, M.X_PINT, M.ABERTURAS_N)]


def centro(i, j):
    return ((i + 0.5) * P, (j + 0.5) * P)


def celda(x, y):
    return min(NX - 1, max(0, int(x / P))), min(NY - 1, max(0, int(y / P)))


def zona_de(x, y):
    for z in M.ZONAS:
        r = z.rect
        if r.x0 <= x <= r.x1 and r.y0 <= y <= r.y1:
            return z
    return None


def salidas():
    """Puertas que cuentan como salida de la nave."""
    return [p for p in M.PUERTAS if p.tipo in ("emergencia", "peatonal") and not p.cod.startswith("PN")]


@lru_cache(None)
def grilla():
    libre = [[True] * NY for _ in range(NX)]

    def tapar(x0, y0, x1, y1, frac=0.3):
        for i in range(max(0, int(x0 / P)), min(NX, math.ceil(x1 / P))):
            for j in range(max(0, int(y0 / P)), min(NY, math.ceil(y1 / P))):
                a = (min(x1, (i + 1) * P) - max(x0, i * P)) * (min(y1, (j + 1) * P) - max(y0, j * P))
                if a > frac * P * P:
                    libre[i][j] = False

    for e in M.EQUIPOS:
        if e.tipo not in PISO:
            r = e.rect
            tapar(r.x0, r.y0, r.x1, r.y1)
    for x in M.EJES_X:
        for y in M.EJES_Y:
            tapar(x - M.COL / 2, y - M.COL / 2, x + M.COL / 2, y + M.COL / 2, 0.0)
    for z in M.ZONAS:                                   # tabiques de los locales con el vano de sus puertas
        if z.tipo != "local":
            continue
        r = z.rect
        lados = [("h", r.y0, r.x0, r.x1, 1), ("h", r.y1, r.x0, r.x1, -1), ("v", r.x0, r.y0, r.y1, 1),
                 ("v", r.x1, r.y0, r.y1, -1)]
        for muro, c, a, b, s in lados:
            vanos = [(x if muro == "h" else y, (x if muro == "h" else y) + w) for x, y, w, m, _ in M.PUERTAS_LOCALES
                     if m == muro and abs((y if muro == "h" else x) - c) < 0.02]
            k = int(c / P) if s > 0 else math.ceil(c / P) - 1           # fila o columna de celdas del lado interior
            if s > 0 and abs(c / P - round(c / P)) < 1e-6 and c > 0:
                k = int(round(c / P))
            if k < 0 or k >= (NY if muro == "h" else NX):
                continue
            n = NX if muro == "h" else NY
            for t in range(n):
                tc = (t + 0.5) * P
                if not (a - 0.1 <= tc <= b + 0.1):
                    continue
                if any(v0 + 0.05 <= tc <= v1 - 0.05 for v0, v1 in vanos):
                    continue
                if muro == "h":
                    libre[t][k] = False
                else:
                    libre[k][t] = False
    return libre


def _cruza(i, j, a, b):
    """True si el paso de (i, j) a (a, b) atraviesa una baranda fuera de sus aberturas."""
    for yb, xa, xb, aberturas in BARANDAS:
        kb = int(round(yb / P))
        if (j < kb <= b) or (b < kb <= j):
            xc = (i + a + 1) * P / 2
            if xa <= xc <= xb and not any(a0 <= xc <= a1 for a0, a1 in aberturas):
                return True
    return False


def _dijkstra(fuentes, lim=INF):
    libre = grilla()
    d = {}
    h = []
    for (i, j), c in fuentes:
        if libre[i][j] and c < d.get((i, j), INF):
            d[(i, j)] = c
            heapq.heappush(h, (c, i, j))
    while h:
        c, i, j = heapq.heappop(h)
        if c > d.get((i, j), INF):
            continue
        for di, dj, k in VEC:
            a, b = i + di, j + dj
            if not (0 <= a < NX and 0 <= b < NY) or not libre[a][b]:
                continue
            if di and dj and not (libre[i + di][j] and libre[i][j + dj]):
                continue
            if _cruza(i, j, a, b):
                continue
            nd = c + k * P
            if nd <= lim and nd < d.get((a, b), INF):
                d[(a, b)] = nd
                heapq.heappush(h, (nd, a, b))
    return d


def celdas_salida(p):
    out = []
    t = p.a + P / 2
    while t <= p.b - 0.05:
        if p.muro in "NS":
            out.append(celda(t, M.LY - 0.01 if p.muro == "N" else 0.01))
        else:
            out.append(celda(M.LX - 0.01 if p.muro == "E" else 0.01, t))
        t += P / 2
    return sorted(set(out))


@lru_cache(None)
def distancias():
    """Distancia por la línea de libre trayectoria de cada celda libre a la salida más cercana, y qué salida."""
    d, cual = {}, {}
    for p in salidas():
        dp = _dijkstra([(c, P / 2) for c in celdas_salida(p)])
        for c, v in dp.items():
            if v < d.get(c, INF):
                d[c], cual[c] = v, p.cod
    return d, cual


def libres():
    g = grilla()
    return [(i, j) for i in range(NX) for j in range(NY) if g[i][j]]


def bolsones():
    """Grupos de celdas libres sin salida (huecos encerrados entre equipos o pilas)."""
    d, _ = distancias()
    g = grilla()
    resto = {c for c in libres() if c not in d}
    out = []
    while resto:
        c0 = resto.pop()
        comp, pila = [c0], [c0]
        while pila:
            i, j = pila.pop()
            for di, dj, _ in VEC[:4]:
                c = (i + di, j + dj)
                if c in resto and g[c[0]][c[1]]:
                    resto.discard(c)
                    comp.append(c)
                    pila.append(c)
        out.append(comp)
    return sorted(out, key=len, reverse=True)


def descenso(c, d=None):
    """Camino de máxima pendiente desde la celda c hasta una salida (lista de puntos)."""
    d = d or distancias()[0]
    g = grilla()
    pts = [centro(*c)]
    for _ in range(4000):
        i, j = c
        mejor = None
        for di, dj, k in VEC:
            a, b = i + di, j + dj
            if (a, b) in d and g[a][b] and not (di and dj and not (g[i + di][j] and g[i][j + dj])) \
                    and not _cruza(i, j, a, b) and d[(a, b)] < d[c] - 1e-9:
                if mejor is None or d[(a, b)] < d[mejor]:
                    mejor = (a, b)
        if mejor is None:
            break
        c = mejor
        pts.append(centro(*c))
    return pts


def escape():
    """Cálculo de medios de escape del anexo VII del Dec. 351/79 y recorrido máximo."""
    area = M.LX * M.LY
    N = math.ceil(area / M.FACTOR_OCUPACION)
    n = math.ceil(N / 100)
    n_ud = max(2, n)
    ancho = 0.55 * min(n_ud, 2) + 0.45 * max(0, n_ud - 2)
    medios = 1 if n_ud <= 3 else math.ceil(n_ud / 4 + 1)
    d, cual = distancias()
    peor = max(d, key=lambda c: d[c])
    sal = []
    for p in salidas():
        m2 = sum(1 for c in cual.values() if c == p.cod) * P * P
        sal.append((p.cod, p.muro, p.b - p.a, m2, p.uso))
    return {"area": area, "N": N, "n": n, "unidades": n_ud, "ancho_min": ancho, "medios_min": medios,
            "salidas": sal, "ancho_total": sum(s[2] for s in sal), "max": d[peor], "peor": centro(*peor),
            "camino": descenso(peor, d), "bolsones": bolsones()}


# ---------------------------------------------------------------- matafuegos
def _ajustar(x, y):
    """Celda libre más cercana al punto, dentro de la misma zona (no cruza tabiques)."""
    g = grilla()
    z = zona_de(x, y)
    i0, j0 = celda(x, y)
    mejor = None
    for r in range(0, 6):
        for i in range(i0 - r, i0 + r + 1):
            for j in range(j0 - r, j0 + r + 1):
                if 0 <= i < NX and 0 <= j < NY and g[i][j] and (z is None or zona_de(*centro(i, j)) is z):
                    dd = math.dist((x, y), centro(i, j))
                    if mejor is None or dd < mejor[0]:
                        mejor = (dd, (i, j))
        if mejor:
            return mejor[1]
    return None


def _candidatos():
    """Bordes de las zonas (0,25 m adentro, cada 1,5 m; no en los carriles del autoelevador), columnas libres del eje B
    y rincones de los locales."""
    g = grilla()
    usados = {round(x - 0.35, 1) for x, y, t in M.BOTIQUINES + M.BEBEDEROS if abs(y - 18.8) < 0.01}
    pts = [(x, 18.8) for x in M.EJES_X[1:-1] if round(x, 1) not in usados]
    for z in M.ZONAS:                                   # bordes de las zonas (no en los carriles del autoelevador)
        if z.sub == "AE":
            continue
        r = z.rect
        t = r.x0 + 0.75
        while t < r.x1 - 0.5:
            pts += [(t, r.y0 + 0.25), (t, r.y1 - 0.25)]
            t += 1.5
        t = r.y0 + 0.75
        while t < r.y1 - 0.5:
            pts += [(r.x0 + 0.25, t), (r.x1 - 0.25, t)]
            t += 1.5
    for z in M.ZONAS:                                   # locales: junto al tabique, adentro
        if z.tipo == "local":
            r = z.rect
            pts += [(r.x0 + 0.4, r.y0 + 0.4), (r.x1 - 0.4, r.y1 - 0.4), (r.x0 + 0.4, r.y1 - 0.4),
                    (r.x1 - 0.4, r.y0 + 0.4)]
    out = []
    puertas = []
    for p in M.PUERTAS:
        if p.muro in "NS":
            y = M.LY if p.muro == "N" else 0.0
            puertas.append((p.a - 0.3, y - 1.2, p.b + 0.3, y + 1.2))
        else:
            x = M.LX if p.muro == "E" else 0.0
            puertas.append((x - 1.2, p.a - 0.3, x + 1.2, p.b + 0.3))
    otros = [(x, y) for x, y, t in M.BOTIQUINES + M.BEBEDEROS]
    for x, y in pts:
        i, j = celda(x, y)
        if not g[i][j] or any(a <= x <= c and b <= y <= d for a, b, c, d in puertas) or \
                any(math.dist((x, y), q) < 1.0 for q in otros):
            continue
        out.append((round(x, 2), round(y, 2)))
    return sorted(set(out))


@lru_cache(None)
def matafuegos():
    """[(código, x, y, tipo, motivo)]: los del riesgo (modelo) y los que agrega la cobertura de 15 m."""
    d, _ = distancias()
    objetivo = set(d)
    el = []
    cub = set()
    for x, y, t, mot in M.MATAFUEGOS_RIESGO:
        c = _ajustar(x, y)
        el.append((x, y, t, mot))
        if c:
            cub |= set(_dijkstra([(c, 0.0)], M.MF_RECORRIDO))
    cand = _candidatos()
    cov = {}
    while objetivo - cub:
        mejor, gan = None, 0
        for p in cand:
            if p not in cov:
                c = _ajustar(*p)
                cov[p] = set(_dijkstra([(c, 0.0)], M.MF_RECORRIDO)) if c else set()
            k = len(cov[p] - cub)
            if k > gan:
                mejor, gan = p, k
        if mejor is None:
            break
        z = zona_de(*mejor)
        el.append((mejor[0], mejor[1], "ABC 10 kg", "Cobertura de 15 m: " + (z.cod if z else "")))
        cub |= cov[mejor]
    fijos = len(M.MATAFUEGOS_RIESGO)                 # se sacan los agregados que quedaron de más
    zona = {}
    for x, y, t, mot in el:
        if (x, y) not in cov:
            c = _ajustar(x, y)
            cov[(x, y)] = set(_dijkstra([(c, 0.0)], M.MF_RECORRIDO)) if c else set()
        zona[(x, y)] = cov[(x, y)]
    while True:
        cuenta = {}
        for e in el:
            for c in zona[(e[0], e[1])]:
                cuenta[c] = cuenta.get(c, 0) + 1
        sobran = [(sum(1 for c in zona[(e[0], e[1])] if cuenta[c] == 1), k) for k, e in enumerate(el) if k >= fijos]
        sobran = [q for q in sobran if q[0] == 0]
        if not sobran:
            break
        el.pop(sobran[-1][1])
    minimo = math.ceil(M.LX * M.LY / M.MF_SUP)
    while len(el) < minimo:                          # mínimo por superficie: los más alejados de los que ya hay
        p = max(cand, key=lambda q: min(math.dist(q, (e[0], e[1])) for e in el))
        z = zona_de(*p)
        el.append((p[0], p[1], "ABC 10 kg", "1 cada 200 m²: " + (z.cod if z else "")))
    el.sort(key=lambda e: (round(-e[1] / 12), e[0]))
    return tuple((f"MF-{k + 1:02d}",) + e for k, e in enumerate(el))


def cobertura():
    """Celdas libres a más de 15 m del matafuego más cercano (deben ser 0)."""
    d, _ = distancias()
    cub = set()
    for cod, x, y, t, mot in matafuegos():
        c = _ajustar(x, y)
        if c:
            cub |= set(_dijkstra([(c, 0.0)], M.MF_RECORRIDO))
    return [c for c in d if c not in cub]


# ---------------------------------------------------------------- iluminación de emergencia, flechas y señales
@lru_cache(None)
def luces():
    """Luminarias autónomas de emergencia (Dec. 351/79 art. 76): una en cada salida y portón, cada 10 m (criterio) a lo
    largo de cada pasillo y senda, y una en cada local."""
    g = grilla()
    pts = []
    for p in M.PUERTAS:
        if p.cod.startswith("PN"):
            continue
        m = (p.a + p.b) / 2
        pts.append({"N": (m, M.LY - 0.4), "S": (m, 0.4), "E": (M.LX - 0.4, m), "O": (0.4, m)}[p.muro])
    for z in M.ZONAS:
        r = z.rect
        if z.tipo == "pasillo":
            L = max(r.w, r.h)
            n = max(1, round(L / 10.0))
            for k in range(n):
                t = (k + 0.5) * L / n
                pts.append((r.x0 + t, r.c[1]) if r.w >= r.h else (r.c[0], r.y0 + t))
        elif z.tipo == "local":
            c = _ajustar(*r.c)
            pts.append(centro(*c) if c else r.c)
    out = []
    for x, y in pts:
        if all(math.dist((x, y), q) > 2.0 for q in out):
            out.append((round(x, 2), round(y, 2)))
    _ = g
    return tuple(out)


@lru_cache(None)
def flechas():
    """Flechas de evacuación pintadas en los pasillos y sendas (Dec. 351/79 art. 80): punto y dirección de salida."""
    d, _ = distancias()
    out = []
    for z in M.ZONAS:
        if z.tipo != "pasillo":
            continue
        r = z.rect
        L = max(r.w, r.h)
        n = max(1, int(L / 6.0))
        for k in range(n):
            t = (k + 0.5) * L / n
            x, y = (r.x0 + t, r.c[1]) if r.w >= r.h else (r.c[0], r.y0 + t)
            c = celda(x, y)
            if c not in d or d[c] < 1.5:
                continue
            cam = descenso(c, d)
            if len(cam) < 3:
                continue
            q = cam[min(4, len(cam) - 1)]
            v = (q[0] - cam[0][0], q[1] - cam[0][1])
            L_ = math.hypot(*v)
            if L_ < 1e-6:
                continue
            v = (v[0] / L_, v[1] / L_)
            if r.w >= r.h and abs(v[0]) > 0.3:            # pintada a lo largo del pasillo
                v = (math.copysign(1.0, v[0]), 0.0)
            elif r.h > r.w and abs(v[1]) > 0.3:
                v = (0.0, math.copysign(1.0, v[1]))
            out.append((centro(*c), v))
    return tuple(out)


@lru_cache(None)
def senales():
    """[(tipo, texto, x, y)]: cada señal de M.SENALES_ZONA en una celda libre de su zona, cerca del borde."""
    g = grilla()
    ocup = [(e[1], e[2]) for e in matafuegos()]
    out = []
    zonas = {z.cod: z for z in M.ZONAS}
    lista = [("obl", "Protección auditiva", zc) for zc, fu in M.ZONAS_RUIDO] + list(M.SENALES_ZONA)
    for tipo, txt, zc in lista:
        r = zonas[zc].rect
        obj = (r.x0 + 0.6, r.y1 - 0.6)
        mejor = None
        for i in range(int(r.x0 / P), min(NX, math.ceil(r.x1 / P))):
            for j in range(int(r.y0 / P), min(NY, math.ceil(r.y1 / P))):
                x, y = centro(i, j)
                if not (r.x0 + 0.3 < x < r.x1 - 0.3 and r.y0 + 0.3 < y < r.y1 - 0.3) or not g[i][j]:
                    continue
                if any(math.dist((x, y), q) < 1.2 for q in ocup):
                    continue
                dd = math.dist((x, y), obj)
                if mejor is None or dd < mejor[0]:
                    mejor = (dd, (x, y))
        if mejor:
            out.append((tipo, txt, mejor[1][0], mejor[1][1]))
            ocup.append(mejor[1])
    return tuple(out)


# ---------------------------------------------------------------- verificación
def verificar():
    err, avi = [], []
    for p in salidas():
        if p.b - p.a < ANCHO_MIN - 1e-6:
            err.append(f"Salida {p.cod} de {p.b - p.a:.2f} m: menos de 2 unidades de ancho ({ANCHO_MIN} m)")
    es = escape()
    if es["max"] > M.RECORRIDO_MAX:
        x, y = es["peor"]
        err.append(f"Recorrido de escape de {es['max']:.1f} m desde ({x:.1f}, {y:.1f}): más de {M.RECORRIDO_MAX:.0f} m")
    if es["ancho_total"] < es["ancho_min"]:
        err.append(f"Ancho total de salidas {es['ancho_total']:.2f} m contra {es['ancho_min']:.2f} m")
    if len(es["salidas"]) < es["medios_min"]:
        err.append(f"{len(es['salidas'])} medios de escape contra {es['medios_min']}")
    for b in es["bolsones"]:
        if len(b) * P * P > 2.0:
            x, y = centro(*b[0])
            avi.append(f"Hueco encerrado sin salida de {len(b) * P * P:.1f} m² cerca de ({x:.1f}, {y:.1f})")
    sin = cobertura()
    if sin:
        x, y = centro(*sin[0])
        err.append(f"{len(sin)} celdas a más de {M.MF_RECORRIDO:.0f} m de un matafuego (p. ej. {x:.1f}, {y:.1f})")
    mf = matafuegos()
    if len(mf) < math.ceil(M.LX * M.LY / M.MF_SUP):
        err.append(f"{len(mf)} matafuegos contra {math.ceil(M.LX * M.LY / M.MF_SUP)} (1 cada 200 m²)")
    puntos = [(c, x, y) for c, x, y, t, m in mf] + [("BQ " + t, x, y) for x, y, t in M.BOTIQUINES] + \
             [("BE " + t, x, y) for x, y, t in M.BEBEDEROS] + [("señal " + t, x, y) for _, t, x, y in senales()]
    for c, x, y in puntos:
        for e in M.EQUIPOS:
            r = e.rect
            if r.x0 + 0.05 < x < r.x1 - 0.05 and r.y0 + 0.05 < y < r.y1 - 0.05 and e.tipo not in PISO:
                err.append(f"{c} en ({x:.1f}, {y:.1f}) cae sobre el equipo {e.cod}")
    return err, avi


if __name__ == "__main__":
    es = escape()
    print({k: v for k, v in es.items() if k not in ("camino", "bolsones")})
    print("bolsones", [(len(b), centro(*b[0])) for b in es["bolsones"][:5]])
    for m in matafuegos():
        print(m)
    print("luces", len(luces()), "flechas", len(flechas()), "señales", len(senales()))
    e, a = verificar()
    print(e, a)
