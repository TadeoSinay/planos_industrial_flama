"""Memoria de cálculo del layout (año 10 = 2035).

Los datos de entrada salen de los Excel de la cátedra (referencias/Dimensionamiento_TecnicoV2.xlsx y
MP_Abastecimiento_Almacenamiento_FLAMA_OpcionD.xlsx) y de las cotizaciones de equipos; las geometrías,
del modelo planta/layout.py. Cada resultado indica su fuente o criterio.
"""

import math
from collections import deque

from . import layout as L

# ================================================================ datos 2035
DEMANDA = {  # matafuegos terminados y cilindros vendidos (u/año) - DT_2035
    "1 kg": (32073, 170548), "2,5 kg": (7425, 6669), "5 kg": (30751, 32915), "10 kg": (1841, 2011),
    "25 kg": (453, 322), "50 kg": (997, 708), "70 kg": (218, 155), "100 kg": (145, 102),
}
RECARGAS = 128800            # recargas en la planta industrial (DT Análisis de recargas)
TERCERIZADOS = 10700         # SUPUESTO: 12,7 % no ABC sobre las ventas de equipos (sin dato en los Excel)
PICO = 1.40                  # diciembre-enero sobre el promedio mensual (DT Parámetros)
DIAS, TURNOS, H_TURNO, EFIC = 22, 2, 8.0, 0.85
H_MES = DIAS * TURNOS * H_TURNO * EFIC   # horas productivas del mes pico

PERSONAL = {  # DT Servicios y oficinas, año 2035
    "turno mañana": {"H": 47, "M": 6, "total": 53},
    "turno tarde": {"H": 9, "M": 1, "total": 10},
    "choferes": 8, "armarios": {"H": 56, "M": 7},
    "total": 71,
}


def tasas():
    """Tasa horaria del mes pico por familia (u/h)."""
    anual = {k: sum(v) for k, v in DEMANDA.items()}
    f1 = anual["1 kg"]
    f2 = anual["2,5 kg"] + anual["5 kg"] + anual["10 kg"]
    f3 = anual["25 kg"] + anual["50 kg"] + anual["70 kg"] + anual["100 kg"]
    return {k: v / 12 * PICO / H_MES for k, v in (("1 kg", f1), ("2,5-10 kg", f2), ("carros", f3))}


# ================================================================ 1. recepción de MP y análisis de peso
CAMIONES = [
    # formato, largo total (m), carga útil (t), PBT (t), dónde se descarga
    ("Semirremolque playo 3+3 ejes", 18.6, 30.0, 45.0,
     "Alero de descarga norte: autoelevador por los dos lados; entra al almacén de MP por P1"),
    ("Camión chasis con balancín (3 ejes)", 11.0, 16.0, 26.0,
     "Alero de descarga norte (junto al semi): autoelevador por los dos lados, bajo techo"),
    ("Camión chasis 2 ejes", 9.5, 9.0, 16.5, "Alero norte, muelles M1-M3, P4, P3 o P8 según el material"),
    ("Utilitario / furgón", 6.0, 1.5, 3.5, "Portones de cada sector; recargas por RC-1"),
]
# Ley 24.449 y Dec. 779/95: ancho 2,60 m, alto 4,10 m, largo máx. 18,60 m (semi); PBT según ejes

ENTREGAS = [
    # grupo (proveedor), t por entrega, entregas/año, formato asignado, portón, destino
    ("Pradecon: hojas + fleje 0,9", 35.26, 18.1, "Semi (máx.) o 2 chasis quincenales", "Alero + P1", "AL-1H, AL-1R"),
    ("Pacheco: flejes 1,25-2,0", 5.05, 29.3, "Chasis 2 ejes", "Alero + P1", "AL-1R"),
    ("Metalprisa: caño Ø76,2", 4.23, 28.9, "Chasis 2 ejes", "Alero + P1", "AL-1R"),
    ("Casquetes de carros", 5.93, 4.1, "Chasis 2 ejes", "M3", "AL1C"),
    ("Eli-Met: cuplas y asientos", 3.68, 5.6, "Chasis 2 ejes", "Alero + P1", "PÑ"),
    ("Soldadura: alambre y consumibles", 1.89, 8.1, "Chasis 2 ejes", "Alero + P1", "PÑ"),
    ("CYM: granalla", 3.11, 2.0, "Chasis 2 ejes", "P3", "GR"),
    ("Air Liquide: gases", 7.64, 31.3, "Chasis 2 ejes (baterías)", "Jaulas JG-S y JG-N", "Exterior"),
    ("Polvo químico (Polvex / DEMSA)", 13.13, 31.0, "Chasis con balancín", "P4 (1-10 kg) y P8 (carros)", "SP-1, SP-2"),
    ("Válvulas y componentes", 8.16, 8.3, "Chasis con balancín", "Muelle M2", "AL-2"),
    ("Estructuras y ruedas de carros", 5.52, 15.1, "Chasis 2 ejes", "P8", "S-TC"),
    ("Pintura en polvo", 0.79, 8.3, "Utilitario", "P3", "QP"),
    ("Químicos de pretratamiento", 0.46, 1.8, "Utilitario", "P3", "QP"),
    ("Embalaje, pallets e imprenta", 4.61, 15.3, "Chasis 2 ejes", "Muelle M2", "AL-2"),
    ("Agentes para recargas", 2.87, 8.2, "Chasis 2 ejes", "RC-1", "RC"),
    ("Tercerizados revendidos", 3.0, 24.0, "Chasis 2 ejes (SUPUESTO)", "M3", "S4"),
]


def autoelevador(q_nom, c_nom, c_real, d=0.45):
    """Capacidad residual por corrimiento del centro de carga:
    Q = Qn (cn + d) / (c + d), d = talón de horquilla a eje delantero (≈ 0,45 m)."""
    return q_nom * (c_nom + d) / (c_real + d)


def analisis_peso():
    filas = []
    # paquete de hoja 1500 × 3000 de 2 t tomado por el lado largo (centro de carga 0,75 m) o por el corto (1,5 m)
    for q in (2.5, 3.0, 3.5):
        filas.append((q, autoelevador(q, 0.5, 0.75), autoelevador(q, 0.5, 1.5)))
    return filas


def semi_vs_chasis():
    """La entrega mensual de Pradecon (35,3 t) supera la carga útil de un semi (30 t): se parte en dos
    entregas quincenales de ≈ 17,6 t (chasis con balancín), que además baja el stock máximo de chapa."""
    t = 35.26
    return {"t_mes": t, "semis": math.ceil(t / 30.0), "quincenal_t": t / 2, "chasis_ok": t / 2 <= 16.0 * 1.12}


# ================================================================ 2. anti-sobrestock de chapa (SAE 1010)
HOJAS = [
    # formato, hojas/año 2035, kg por hoja (MP Corte opción D, CC Nesting)
    ("LAF 1,25 × 1220 × 2440 (2,5 kg)", 522, 29.28),
    ("LAF 1,6 × 1000 × 2000 (5 kg)", 5306, 25.18),
    ("LAF 2,0 × 1500 × 3000 (10 kg)", 256.8, 70.83),
    ("LAC 3,2 × 1500 × 3000 (25 y 50 kg)", 370.3, 113.3),
    ("LAC 4,75 × 1500 × 3000 (70 y 100 kg)", 165.2, 168.2),
]
SEMANAS = 48
COBERTURA_MAX = 6.0          # semanas: tope de antigüedad (semáforo rojo)


def sobrestock():
    """Cobertura en semanas de un paquete de 2 t y tamaño de paquete propuesto para que un paquete no
    cubra más de 2 semanas (entregas quincenales) ni menos de 1 hoja."""
    out = []
    for nom, hojas, kg in HOJAS:
        sem = hojas / SEMANAS
        h2t = int(2000 // kg)
        cob2t = h2t / sem
        h_prop = max(1, min(h2t, math.ceil(sem * 2)))
        stock_max = h_prop * 2       # un paquete en uso + uno en espera (FIFO)
        out.append({"formato": nom, "hojas_sem": sem, "hojas_2t": h2t, "cob_2t": cob2t, "hojas_paq": h_prop,
                    "kg_paq": h_prop * kg, "cob_max": stock_max / sem, "stock_max_kg": stock_max * kg})
    return out


# ================================================================ 3. pulmones y tren logístico
def pulmones():
    t = tasas()
    filas = [
        # pulmón, tasa (u/h), cobertura (h), u por carro 1,2 × 0,8, criterio
        ("PU-G cuerpos 2,5-10 kg y carros", t["2,5-10 kg"] + t["carros"], 8.0, 60,
         "La guillotina corta por tandas de un formato: 1 turno de consumo"),
        ("M17 cuerpos 1 kg (láser)", t["1 kg"], 0.5, 150, "Un viaje del tren logístico + cambio de barra"),
        ("SM-K cúpulas y fondos (pares)", t["1 kg"] + t["2,5-10 kg"], 4.0, 400,
         "Cambio de troquel de la prensa (≈ 30 min) cada medio turno"),
        ("A00 kanban celda 1 kg", t["1 kg"], 0.5, 150, "2 carros: uno en uso y otro en reposición"),
        ("B00 supermercado celda 2,5-10 kg", t["2,5-10 kg"], 1.0, 60, "2 carros por formato en curso"),
        ("A08 y B11 a pintura", t["1 kg"] + t["2,5-10 kg"], 0.75, 110,
         "Parada de cambio de color / limpieza de cabina (≈ 45 min) sin detener las celdas"),
        ("PU a terminación (tren de descarga)", t["1 kg"] + t["2,5-10 kg"], 0.5, 110, "Carga de polvo por lote"),
    ]
    out = []
    for nom, tasa, cob, upc, crit in filas:
        u = tasa * cob
        out.append({"pulmon": nom, "tasa": tasa, "cob_h": cob, "u": u, "carros": math.ceil(u / upc) + 1,
                    "criterio": crit})
    return out


def tren_logistico():
    xs = L.TL
    largo = sum(math.dist(a, b) for a, b in zip(xs, xs[1:]))
    v = 1.0                   # m/s dentro de la nave (3,6 km/h, convive con autoelevador)
    paradas = 7               # PU-G, M17, SM-K, A, A, B, pintura
    t_ciclo = largo / v + paradas * 60
    t = tasas()
    u_h = t["1 kg"] + t["2,5-10 kg"]
    cap_viaje = 3 * 110       # 3 carros por tren
    return {"largo_m": largo, "ciclo_min": t_ciclo / 60, "viajes_h_max": 3600 / t_ciclo,
            "viajes_h_nec": u_h / cap_viaje * 2, "u_h": u_h}


# ================================================================ 4. sanitarios y vestuarios (Dec. 351/79)
def art49(n):
    """Por sexo y por turno: hasta 5 -> 1+1+1; 6 a 10 -> 1+1+1; más de 10: inodoro c/20, lavabo c/10,
    orinal c/10, ducha c/20 (texto a verificar en InfoLEG)."""
    if n <= 10:
        return {"inodoros": 1 if n else 0, "lavabos": 1 if n else 0, "orinales": 0, "duchas": 1 if n else 0}
    return {"inodoros": math.ceil(n / 20), "lavabos": math.ceil(n / 10), "orinales": math.ceil(n / 10),
            "duchas": math.ceil(n / 20)}


def sanitarios():
    tm = PERSONAL["turno mañana"]
    ch = PERSONAL["choferes"]
    h = tm["H"] + ch            # los choferes arrancan y terminan su jornada en planta (se suman al turno)
    m = tm["M"]
    req_h, req_m = art49(h), art49(m)
    req_m["orinales"] = 0
    from .mobiliario import SANITARIOS

    def contar(locales):
        c = {"inodoros": 0, "lavabos": 0, "orinales": 0, "duchas": 0, "armarios": 0}
        for mb in L.MOBILIARIO:
            k = SANITARIOS.get(mb.tipo)
            if k and any(_dentro(mb.rect, s.rect) for s in L.LOCALES if s.cod in locales):
                c[k] += mb.n * (2 if k == "armarios" else 1)
        return c
    ch_, cm_ = contar(("SV-VH", "SV-SH")), contar(("SV-VM", "SV-SM"))
    proy = {"H": {k: ch_[k] for k in ("inodoros", "lavabos", "orinales", "duchas")},
            "M": {k: cm_[k] for k in ("inodoros", "lavabos", "orinales", "duchas")},
            "accesibles": sum(1 for mb in L.MOBILIARIO if mb.tipo == "inodoro_acc")}
    return {"H": h, "M": m, "req_H": req_h, "req_M": req_m, "proy": proy,
            "armarios_req": {"H": PERSONAL["armarios"]["H"], "M": PERSONAL["armarios"]["M"]},
            "armarios_proy": {"H": ch_["armarios"], "M": cm_["armarios"]}}


def _dentro(a, b, tol=0.05):
    return a.x0 >= b.x0 - tol and a.y0 >= b.y0 - tol and a.x1 <= b.x1 + tol and a.y1 <= b.y1 + tol


# ================================================================ 5. grilla, medios de escape y extintores
PASO = 0.5


def _grilla():
    nx, ny = int(L.NAVE_L / PASO), int(L.NAVE_A / PASO)
    libre = [[True] * ny for _ in range(nx)]
    for e in list(L.EQUIPOS) + [mb for mb in L.MOBILIARIO if mb.rect.x0 >= 0]:
        r = e.rect
        for i in range(max(0, int(r.x0 / PASO)), min(nx, int(math.ceil(r.x1 / PASO)))):
            for j in range(max(0, int(r.y0 / PASO)), min(ny, int(math.ceil(r.y1 / PASO)))):
                libre[i][j] = False
    return nx, ny, libre


def _bfs(fuentes, nx, ny, libre):
    INF = 1e9
    d = [[INF] * ny for _ in range(nx)]
    q = deque()
    for i, j in fuentes:
        if 0 <= i < nx and 0 <= j < ny:
            d[i][j] = 0.0
            q.append((i, j))
    pasos = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414),
             (-1, -1, 1.414)]
    while q:
        i, j = q.popleft()
        for di, dj, c in pasos:
            a, b = i + di, j + dj
            if 0 <= a < nx and 0 <= b < ny and libre[a][b]:
                nd = d[i][j] + c * PASO
                if nd < d[a][b] - 1e-9:
                    d[a][b] = nd
                    q.append((a, b))
    return d


def _celdas_puerta(p, nx, ny):
    out = []
    if p.muro in ("N", "S"):
        j = ny - 1 if p.muro == "N" else 0
        for x in frange(p.a, p.b):
            out.append((int(x / PASO), j))
    else:
        i = nx - 1 if p.muro == "E" else 0
        for y in frange(p.a, p.b):
            out.append((i, int(y / PASO)))
    return out


def frange(a, b, s=PASO / 2):
    x = a
    while x <= b:
        yield x
        x += s


def escape():
    """Distancia real de recorrido (grilla de 0,5 m que rodea equipos) desde cada punto de la nave a la
    salida más cercana. Salidas: SE-*, PP-1 y portones con puerta de hombre."""
    nx, ny, libre = _grilla()
    fuentes = []
    for p in L.PUERTAS:
        if p.tipo in ("emergencia", "peatonal", "porton", "muelle"):
            fuentes += _celdas_puerta(p, nx, ny)
    d = _bfs(fuentes, nx, ny, libre)
    peor, donde = 0.0, None
    for i in range(nx):
        for j in range(ny):
            if libre[i][j] and d[i][j] < 1e8 and d[i][j] > peor:
                peor, donde = d[i][j], (i * PASO, j * PASO)
    # Dec. 351/79 anexo VII: factor de ocupación industrial 16 m²/persona; unidades de ancho de salida
    sup = L.NAVE_L * L.NAVE_A
    N = math.ceil(sup / 16)
    n = max(2, math.ceil(N / 100))
    ancho = 1.10 if n <= 2 else 1.10 + 0.45 * (n - 2)
    salidas = [p for p in L.PUERTAS if p.tipo == "emergencia"]
    return {"peor_m": peor, "punto": donde, "N": N, "unidades": n, "ancho_min": ancho,
            "salidas_emergencia": len(salidas), "ancho_emergencia": len(salidas) * 1.10}


EXT_RECORRIDO = 20.0          # IRAM 3517-2:2020 6.2.4: fuego clase A, recorrido máximo 20 m
EXT_SUP = 200.0               # 1 extintor cada 200 m² (Dec. 351/79 anexo VII)


def extintores():
    """Ubicación de extintores ABC 10 kg: candidatos junto a columnas, muros y pasillos; se eligen en forma
    voraz hasta que todo punto libre quede a ≤ 20 m de recorrido de un extintor y haya 1 cada 200 m²."""
    nx, ny, libre = _grilla()
    cand = []
    for x in L.EJES_X:
        for y in (0.6, L.NAVE_A - 0.6):
            cand.append((min(max(x, 0.6), L.NAVE_L - 0.6), y))
    for p in L.PASILLOS:
        r = p.rect
        for x in frange(r.x0 + 1, r.x1 - 1, 6.0):
            cand.append((x, r.c[1]))
        for y in frange(r.y0 + 1, r.y1 - 1, 6.0):
            cand.append((r.c[0], y))
    cand = [c for c in cand if libre[min(nx - 1, int(c[0] / PASO))][min(ny - 1, int(c[1] / PASO))]]
    dist = {}
    for c in cand:
        dd = _bfs([(int(c[0] / PASO), int(c[1] / PASO))], nx, ny, libre)
        dist[c] = {(i, j) for i in range(nx) for j in range(ny) if dd[i][j] <= EXT_RECORRIDO}
    objetivo = {(i, j) for i in range(nx) for j in range(ny) if libre[i][j]}
    elegidos, cubierto = [], set()
    while objetivo - cubierto:
        mejor = max(cand, key=lambda c: len(dist[c] - cubierto))
        if not dist[mejor] - cubierto:
            break
        elegidos.append(mejor)
        cubierto |= dist[mejor]
    minimo = math.ceil(L.NAVE_L * L.NAVE_A / EXT_SUP)
    # completar por superficie repartiendo sobre los pasillos
    resto = [c for c in cand if c not in elegidos]
    while len(elegidos) < minimo and resto:
        c = max(resto, key=lambda c: min(math.dist(c, e) for e in elegidos))
        elegidos.append(c)
        resto.remove(c)
    return {"puntos": elegidos, "minimo_sup": minimo, "cant": len(elegidos)}


# ================================================================ 6. iluminación (método de los lúmenes)
LUX = {  # nivel medio de servicio (lx): docx Dimensionamiento Técnico / Dec. 351/79 anexo IV
    "MP": 150, "PROD": 300, "PINT": 500, "TERM": 300, "PT": 150, "CAL": 750, "AUX": 300, "RC": 300,
}
LUX_ESPECIAL = {"B09": 750, "C06": 500, "C04": 500, "C05": 500, "A06": 500, "B03": 500, "B06": 500}
LUMINARIA = {"flujo_lm": 21000, "potencia_w": 150, "UF": 0.65, "MF": 0.80}


def iluminacion():
    out = []
    for s in L.SECTORES:
        e = LUX.get(s.cat, 300)
        n = math.ceil(e * s.rect.area / (LUMINARIA["flujo_lm"] * LUMINARIA["UF"] * LUMINARIA["MF"]))
        out.append((s.cod, s.nombre, e, s.rect.area, n, n * LUMINARIA["potencia_w"] / 1000))
    return out


# ================================================================ 7. redes: longitud de tendidos
TGBT = (41.0, 44.2)            # sala técnica norte (centro de cargas)
PTE_P = (70.0, -19.0)
JGS = (52.0, 44.4)
JGN = (53.0, -1.0)
ERM = (88.6, 5.5)


def _manh(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def redes():
    sub = {}
    for e in L.EQUIPOS:
        if e.kw:
            sub.setdefault(e.sector, []).append(e)
    elec = []
    for sec, eqs in sub.items():
        kw = sum(e.kw for e in eqs)
        cx = sum(e.rect.c[0] * e.kw for e in eqs) / kw
        cy = sum(e.rect.c[1] * e.kw for e in eqs) / kw
        elec.append((sec, kw, (cx, cy), _manh(TGBT, (cx, cy))))
    # la PH de carros (C07) trabaja en circuito cerrado con tanque propio: no se conecta a la PTE
    agua = [(e.cod, _manh(e.rect.c, PTE_P)) for e in L.EQUIPOS if e.agua and e.cod != "C07"]
    gas = [(e.cod, _manh(e.rect.c, ERM)) for e in L.EQUIPOS if e.gas]
    n2 = [(e.cod, _manh(e.rect.c, JGN)) for e in L.EQUIPOS if e.n2]
    sold = [(e.cod, _manh(e.rect.c, JGS)) for e in L.EQUIPOS if e.polvo and "Soldadura" in e.nombre]
    aire = 2 * 70.0 + 2 * 24.0 + 14 * 6.0   # anillo sobre el pasillo central + 14 bajadas a la línea
    return {"elec": elec, "agua": agua, "gas": gas, "n2": n2, "sold": sold, "aire_anillo_m": aire,
            "kw_total": sum(e.kw for e in L.EQUIPOS)}


# ================================================================ 8. áreas y distancias de flujos
def areas():
    out = []
    for s in L.SECTORES + L.LOCALES:
        out.append((s.cod, s.nombre, s.rect.area, s.area_req))
    return out


def largo(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def flujos():
    return [(f.cat, f.rot, largo(f.pts)) for f in L.FLUJOS]


def resumen():
    return {
        "tasas": tasas(), "peso": analisis_peso(), "pradecon": semi_vs_chasis(), "sobrestock": sobrestock(),
        "pulmones": pulmones(), "tren": tren_logistico(), "sanitarios": sanitarios(), "escape": escape(),
        "iluminacion": iluminacion(), "redes": redes(),
    }


# ================================================================ manejo de materiales: métodos y tiempos
# velocidad media (m/s, ida cargado y vuelta vacío) y tiempo fijo por viaje (min: tomar, dejar, maniobrar)
MEDIOS = {"Autoelevador": (1.5, 1.5), "Apiladora": (1.0, 1.5), "Transpaleta": (0.8, 1.0),
          "Carro a mano": (0.8, 0.5), "Zorra milk run": (0.8, 0.5)}
MIN_TURNO = 480.0 * 0.85          # 8 h con 15 % de suplementos (OIT)
CIL_DIA = 1184                    # cilindros 1-10 kg por día en el mes pico 2035 (Dimensionamiento, hoja 2035)
CIL_1KG = 0.80                    # participación del 1 kg en los cilindros
CARROS_DIA = round(CIL_DIA * CIL_1KG / 80 + CIL_DIA * (1 - CIL_1KG) / 24)   # carro: 80 u de 1 kg o 24 u de 5 kg
MILK_RUN = [(53.0, 40.0), (17.5, 40.0), (17.5, 39.4), (40.2, 39.4), (40.2, 34.2), (82.0, 34.2), (82.0, 40.0),
            (53.0, 40.0)]


def _largo(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def _lf(desc):
    """Largo dentro de la nave (y del alero) del flujo cuya descripción empieza con `desc`."""
    fl = next(f for f in L.FLUJOS if f.rot.startswith(desc))
    pts = [(x, max(y, 0.0)) if y < 0 else (x, y) for x, y in fl.pts]
    pts = [(x, min(y, 52.0)) for x, y in pts]
    return _largo(pts)


def manejo():
    """Tabla de manejo de materiales: unidad de carga, medio, recorrido, viajes por día, tiempo y ocupación."""
    tramos_linea = 9
    filas = [
        # unidad de carga, medio, de -> a, viajes/día, distancia (m)
        ("Paquete de hojas ≤ 2 t", "Autoelevador", "Alero -> rack guillotina (P1)", 1.5, _lf("Chapa")),
        ("Rollo de fleje 0,5-1 t", "Autoelevador", "Alero -> porta-flejes (P1)", 0.8, _lf("Flejes")),
        ("Atado de caño 6 m", "Autoelevador", "Alero -> cantiléver láser (P1)", 0.6, _lf("Caño")),
        ("Pallet de insumos pesados", "Autoelevador", "Alero -> pañol PÑ (P1)", 0.5, _lf("Insumos al pañol")),
        ("Big bag de polvo 1 t", "Autoelevador", "P4 -> estación de descarga", 1.7, _lf("Polvo químico")),
        ("Pallet de válvulas / cajas", "Transpaleta", "Muelle M2 -> rack AL-2", 1.3, _lf("Válvulas")),
        ("Tambor / cajas de pintura", "Transpaleta", "P3 -> QP", 0.3, _lf("Químicos y pintura")),
        ("Carro de cuerpos 2,5-10 kg (24 u)", "Carro a mano", "PU-4 -> 9 encastre", 14, _lf("Cuerpos 2,5-10")),
        ("Carro de cuerpos 1 kg (80 u)", "Carro a mano", "PU-L2 -> 9 encastre", 12, _lf("Cuerpos 1 kg al")),
        ("Carro de fondos (150 u)", "Carro a mano", "PU-K -> 9 encastre", 8, _lf("Fondos al encastre")),
        ("Carro de cúpulas con cuello (60 u)", "Carro a mano", "PU-C -> 11 sold. circ.", 20,
         _lf("Cúpulas a la soldadura circ")),
        (f"Carro de cilindros, {tramos_linea} tramos 9 -> 16", "Carro a mano", "entre pasos (prom. por tramo)",
         CARROS_DIA * tramos_linea, _lf("Línea principal") / tramos_linea),
        ("Carro de cilindros controlados", "Carro a mano", "PU-8 -> 17 carga de pintura", CARROS_DIA,
         _lf("A la carga de pintura")),
        ("Carro de cilindros pintados", "Carro a mano", "PU-9 -> 18 carga de polvo", CARROS_DIA,
         _lf("A la carga de polvo")),
        ("Zorra de consumibles (vuelta)", "Zorra milk run", "PÑL -> 24 puestos -> PÑL", 4, _largo(MILK_RUN) / 2),
        ("Pallet de PT", "Apiladora", "Envolvedora -> rack AL-3", 7.2, _lf("Almacén de PT")),
        ("Pallet de PT", "Autoelevador", "Rack AL-3 -> muelle M1 / M2", 7.2, _lf("Expedición M1")),
        ("Pallet de cilindros vacíos", "Autoelevador", "AL-C -> rack AL-3", 2.8, _lf("Cilindros vendidos")),
        ("Contenedor de scrap 1 m³", "Autoelevador", "SCR -> volquete (P2)", 0.6, _lf("Scrap a volquete")),
    ]
    out, uso = [], {}
    for u, m, ruta, n, d in filas:
        v, t0 = MEDIOS[m]
        t = 2 * d / v / 60.0 + t0
        out.append({"carga": u, "medio": m, "ruta": ruta, "viajes": n, "dist": d, "t_viaje": t, "min_dia": n * t})
        uso[m] = uso.get(m, 0.0) + n * t
    ocup = {m: uso[m] / MIN_TURNO for m in uso}
    return {"filas": out, "min": uso, "ocup": ocup, "carros_dia": CARROS_DIA}


PORTONES = [
    # portón, qué pasa, vehículo, frecuencia (2035), horario
    ("P1 + alero", "Entra MP: chapa, caño, flejes, insumos pesados", "Semi / chasis", "≈ 2,4 por semana", "7 a 10 h"),
    ("P2", "Sale scrap a volquete (el chatarrero no entra)", "Volquete 6 m³", "≈ 1 por semana", "Libre"),
    ("P3", "Entran químicos, pintura en polvo y granalla", "Utilitario / chasis", "≈ 0,3 por semana", "7 a 10 h"),
    ("P4", "Entra polvo químico en big bags", "Chasis con balancín", "≈ 0,65 por semana", "7 a 10 h"),
    ("M1 / M2", "Sale PT; M2 recibe válvulas, cajas, etiquetas y film", "Semi / chasis", "7 PT + 0,5 insumos por semana",
     "PT 13 a 17 h; insumos 7 a 10 h"),
    ("M3", "Entran tercerizados revendidos y casquetes de carros", "Chasis", "≈ 0,6 por semana", "7 a 10 h"),
    ("P6", "Salen carros al pintor y vuelven pintados (mismo viaje)", "Chasis del pintor", "≈ 1 por semana",
     "Coordinado"),
    ("P8", "Entran estructuras, ruedas y polvo de carros", "Chasis", "≈ 0,3 por semana", "7 a 10 h"),
    ("P9", "Salen carros terminados", "Chasis", "≈ 1 por semana", "13 a 17 h"),
    ("RC-1 / RC-2", "Recargas: entran y salen equipos de clientes", "Utilitarios de reparto (8)",
     "2 vueltas por día", "Milk run mañana y tarde"),
    ("PP-1", "Personal: vestuarios <-> senda de la nave", "A pie", "63 personas, 2 turnos", "Entrada y salida"),
]
