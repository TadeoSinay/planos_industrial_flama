"""Modelo del layout de la planta FLAMA S.A. al año 2035 - versión 10 (rediseño desde cero).

Medidas en METROS. Origen en la esquina SO interior de la nave; X al este, Y al norte.
Calle al NORTE: la administración y los servicios al personal van al norte de la nave (croquis del usuario).

Concepto (croquis del usuario, octubre 2026)
--------------------------------------------
* Almacén de MP al oeste, con el portón de MP (P1) en el muro oeste, a la altura del pasillo principal.
* Manuales al norte: tres filas que salen del almacén (embutido, corte de tubo, corte de chapa) hasta la columna
  este, que baja de la soldadura circunferencial al control de espesor, la prueba hidráulica y el secado; el
  granallado, la detección y el cuelgue siguen hacia el este hasta la pintura (croquis de bloques del usuario).
* Pintura al este, de norte a sur; la terminación sale de la pintura hacia el pasillo principal y el depósito de PT.
* Carros al centro: la fila de fabricación (corte a secado, W-CAR) entre los manuales y el pasillo principal, y
  sus puestos 11 a 17 al sur del pasillo, con el depósito de PT y los portones de despacho (P2) y de la pintura
  tercerizada (P3 salida y P6 regreso). Los lugares de carros rodantes son los de las tablas de W-CAR.
* Mantenimiento, calidad, compresores y espacio libre en el ángulo SO.

Fuentes (las mismas de la tabla Dimensionamiento_de_areas_v10.xlsx)
-------------------------------------------------------------------
W-MAN  Proceso de manuales (Word).          X-MAN  Dimensionamiento Manuales (máquina y cantidad 2035).
W-CAR  Proceso de carros (Word, v10).       X-CAR  Dimensionamiento Carros.
X-ALM  Dimensionamiento Almacenes MP v5.    X-DT   Dimensionamiento_TecnicoV2 (dotación, servicios, PT).
ET     ET´s Máquinas.                       Presupuestos y catálogos de la carpeta INVESTIGACION PROVEEDORES.
"""

import math
from dataclasses import dataclass

# ================================================================ nave y estructura
LX, LY = 76.0, 47.0                       # nave interior (m)
MURO = 0.20
COL = 0.40
EJES_X = [round(7.6 * i, 2) for i in range(11)]          # 0 ... 76 (10 vanos de 7,6 m)
EJES_Y = [0.0, 18.5, LY]                                 # fila intermedia en el borde norte del carril del autoelevador
ALTURA_LIBRE = 8.0


@dataclass
class R:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def w(self):
        return self.x1 - self.x0

    @property
    def h(self):
        return self.y1 - self.y0

    @property
    def area(self):
        return self.w * self.h

    @property
    def c(self):
        return ((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2)

    def pts(self):
        return [(self.x0, self.y0), (self.x1, self.y0), (self.x1, self.y1), (self.x0, self.y1)]


def Rw(x, y, w, h):
    return R(x, y, x + w, y + h)


@dataclass
class Zona:
    cod: str
    nombre: str
    rect: R
    cat: str                  # MP, MAN, CAR, PINT, TERM, PT, AUX, LIB, CIRC
    fuente: str = ""
    req: float = 0.0          # m² que pide la fuente (0 = no aplica)
    tipo: str = "area"        # area | local (cerrado con tabique) | pasillo
    sub: str = ""             # pasillos: AE (autoelevador), SP (senda peatonal), PO (operarios y carros a mano)
    nota: str = ""


@dataclass
class Equipo:
    cod: str
    nombre: str
    rect: R
    zona: str
    tipo: str = "banco"       # símbolo de planta/simbolos.py
    frente: str = "S"         # lado del operario (S, E, N, O)
    op: int = 1               # operarios dibujados al frente
    fuente: str = ""
    ae: bool = False          # necesita acceso del autoelevador (debe tocar un pasillo AE o su senda)
    espejo: bool = False
    n: int = 0                # lugares de carros rodantes (símbolo «rodantes»)
    grid: tuple = None        # (lugares por fila, filas) del símbolo «rodantes»
    dem: str = ""             # demarcación de piso: AM (amarillo), VE (verde), RO (rojo)


@dataclass
class Puerta:
    cod: str
    muro: str                 # N, S, E, O
    a: float
    b: float
    alto: float
    tipo: str                 # porton, peatonal, emergencia
    uso: str = ""


ZONAS, EQUIPOS, PUERTAS = [], [], []


def Z(cod, nombre, r, cat, fuente="", req=0.0, tipo="area", sub="", nota=""):
    ZONAS.append(Zona(cod, nombre, r, cat, fuente, req, tipo, sub, nota))


def E(cod, nombre, r, zona, tipo="banco", frente="S", op=1, fuente="", ae=False, espejo=False, n=0, grid=None, dem=""):
    EQUIPOS.append(Equipo(cod, nombre, r, zona, tipo, frente, op, fuente, ae, espejo, n, grid, dem))


FCHP = (1.28, 0.61)     # carro FCHP20505 (W-MAN 6)
CAJ = (1.2, 0.8)        # carro de 12 cajones (W-MAN 2)


def carros_fila(cod, nombre, x, y, n, zona, unidad=FCHP, vertical=False, fuente=""):
    """Pulmón de n carros en fila (separados 0,1 m)."""
    lu, lv = unidad
    for i in range(n):
        if vertical:
            r = Rw(x, y + i * (lv + 0.1), lu, lv)
        else:
            r = Rw(x + i * (lu + 0.1), y, lu, lv)
        E(f"{cod}.{i + 1}" if n > 1 else cod, nombre, r, zona, "carro_caj" if unidad == CAJ else "fchp", "S", 0,
          fuente)


def filas_carros(cod, nombre, r, zona, por_fila, n_filas, dem, fuente, frente="S", n=None):
    E(cod, nombre, r, zona, "filas", frente, 0, fuente, n=n or por_fila * n_filas, grid=(por_fila, n_filas), dem=dem)


def pares(cod, nombre, r, zona, nu, nv, dem, fuente, n=None, frente="S"):
    E(cod, nombre, r, zona, "rodantes", frente, 0, fuente, n=n or nu * nv, grid=(nu, nv), dem=dem)


# ================================================================ bandas
Y_S = 13.5          # banda sur: almacén complementario, servicios, carros 11 a 17, PT
Y_AE = 18.5         # carril del autoelevador del pasillo principal (13,5 a 18,5)
Y_A2 = 20.0         # senda peatonal del pasillo principal (18,5 a 20,0)
Y_CN = 29.0         # fila de fabricación de carros (20,0 a 29,0)
Y_M = 45.0          # manuales (29,0 a 45,0)
X_AL = 14.0         # ancho del almacén de MP (oeste)
X_PINT = 66.0       # pintura (66 a 76, de 20 a 47)

_AE = "Heli CPCD50 (W-MAN y W-CAR): radio de giro 2,93 m + pallet 1,2 m + 0,8 m de margen = 5,0 m (W-CAR, tabla 5)"
# Pasillos de racks angostos (pedido del usuario: «más angostos, no de 5 m»): el Heli CPCD50 necesita unos 4,96 m para
# apilar a 90° (ficha del CPCD50), así que los racks R1 y de PT se atienden con un autoelevador eléctrico Heli CPD15
# (1,5 t): pasillo de apilado a 90° de 3.315 mm (pallet de 1000 × 1000) a 3.515 mm (1200 × 1200), ficha Heli
# CPD15/16/18/20 (Forklift America y Heli NZ). Se toma 3,6 m. El CPCD50 sigue para chapa, big bags y camiones.
_AE15 = ("Heli CPD15 eléctrico de 1,5 t (agregado por el pasillo angosto): apilado a 90° en 3.315 a 3.515 mm según el "
         "pallet (ficha Heli CPD15-20) -> 3,6 m. El Heli CPCD50 necesitaría 4,96 m")
_PASO = "Tránsito de un solo sentido: autoelevador de 1,17 a 1,51 m de ancho + 0,75 m por lado = 3,0 m (criterio)"

# ================================================================ LUGARES DE CARROS (reglas de W-CAR con la demanda 2035) Y PT DE MANUALES
# W-CAR dimensiona cada pulmón con una regla (una semana, una semana y un día, 1,8 semanas...) aplicada a su escenario
# de 20 carros por día (X-CAR, hoja «Proceso (Word)»). Acá se aplica la MISMA regla a la demanda pico de 2035.
# Demanda: X-CAR, «Plan mensual» 2035, mes pico (9 % del año, parametros_carros fila 12): (matafuegos, cilindros
# vendidos vacíos) por mes y modelo. 20 días hábiles por mes (X-CAR, parametros_carros A2) = 4 semanas de 5 días.
def f1(v):
    return ("%.1f" % (v + 1e-9)).replace(".", ",")


PICO_2035 = {25: (40.77, 28.98), 50: (89.73, 63.72), 70: (19.62, 13.95), 100: (13.05, 9.18)}
SEMANAS_MES = 20 / 5
SEM_T = {k: v[0] / SEMANAS_MES for k, v in PICO_2035.items()}      # matafuegos por semana (25 kg: 10,2 ...)
SEM_C = {k: v[1] / SEMANAS_MES for k, v in PICO_2035.items()}      # cilindros vendidos vacíos por semana
SEMANA = sum(SEM_T.values()) + sum(SEM_C.values())                  # 69,8 recipientes por semana
DIA = SEMANA / 5                                                    # 14,0 por día
MATAF = sum(SEM_T.values())                                         # 40,8 matafuegos por semana


def _muestra(lote):
    """Carros de la muestra de un lote según la tabla de W-CAR 14 (lote hasta 15: 3 carros; 16 a 39: 8; 55: 13)."""
    return 3 if lote <= 15 else 8 if lote <= 39 else 13


# Dato del usuario (octubre 2026): el pico de carros a la pintura es de 48 por semana, con 2 envíos por semana.
# Con 2 envíos el lote pasa a ser la producción de media semana de cada modelo (un lote por envío, porque ningún carro
# sale a pintar hasta que su lote se aprueba, W-CAR 9 y 11).
PICO_PINTURA, ENVIOS = 48, 2


def _lote(s):
    """(carros del lote, semanas que junta) de un modelo con s carros por semana: lote de media semana; si tiene 5
    carros o menos se agrupa, como el 100 kg de W-CAR 14 («5 carros por semana o menos se agrupa cada dos semanas»)."""
    lote, sem = s / ENVIOS, 1 / ENVIOS
    while lote <= 5:
        lote, sem = 2 * lote, 2 * sem
    return lote, sem


# Muestra por semana (W-CAR 14): 25 kg y 50 kg, 3 carros por lote de media semana (6 + 6); 70 y 100 kg, agrupados cada
# dos semanas (1,5 + 1,5). La sala tiene 30 lugares para unos 25 por semana: el resto esperan el puesto 17 (× 30 / 25).
MUESTRA = sum(_muestra(lo) / se for lo, se in map(_lote, SEM_T.values()))                     # 15 por semana
SALA = math.ceil(MUESTRA * 30 / 25)                                                             # 18 lugares
# Retenidos: el lote de media semana se carga en 2,5 días hábiles y espera unos 5 días hábiles más (los 7 días corridos
# de la muestra en la sala, W-CAR 14) hasta que se libera; en el pico hay un lote cargándose y los anteriores esperando.
RETENIDOS = math.ceil(MATAF / 5 * (2.5 + 5))                                                    # 62
_C12 = round(PICO_PINTURA * MATAF / SEMANA)                                                     # 28
# (zona, puesto, qué guarda, regla aplicada, medida en planta, lugares)
STOCK_CARROS = [
    ("C-11", "11 Pulmón de despacho a la pintura", "Carros secos hasta que se aprueba el lote y sale el camión",
     "Dato del usuario: pico de %d carros por semana con %d envíos por semana (W-CAR 11 lo dimensionaba con 1 semana "
     "+ 1 día)" % (PICO_PINTURA, ENVIOS), "6,4 × 7,6 m", PICO_PINTURA),
    ("C-12", "12 Pulmón de pintados", "Carros pintados con las ruedas nuevas, hasta la carga (puesto 13)",
     "W-CAR 12: lo mismo que el 11, sólo lo que va al 13 (los cilindros vendidos vacíos van a liberados): %d × %s / %s"
     % (PICO_PINTURA, f1(MATAF), f1(SEMANA)), "4,5 × 3,8 m", _C12),
    ("C-14", "14 Sala de pérdidas", "Muestra de los lotes durante 7 días, con el manómetro hacia el pasillo",
     "W-CAR 14 con lotes de media semana (un lote por envío): 6 + 6 + 1,5 + 1,5 = %s por semana × 30 / 25"
     % f1(MUESTRA), "4,0 × 4,0 m", SALA),
    ("C-16", "16 Retenidos (amarillo)", "Lote cargado hasta que se decide",
     "W-CAR 16 con lotes de media semana: 2,5 días de carga + 5 días de espera de la muestra = 7,5 días × %s "
     "matafuegos por día (en el Word, 1,8 semanas)" % f1(MATAF / 5), "5,6 × 5,1 m", RETENIDOS),
    ("C-16", "16 Liberados (verde)", "Lotes liberados y cilindros vendidos vacíos hasta el despacho",
     "W-CAR 16: una semana de producción (matafuegos y cilindros vendidos vacíos). 2035: %s" % f1(SEMANA), "6,3 × 5,1 m",
     math.ceil(SEMANA)),
    ("C-16X", "16 Rechazados (rojo)", "Lote rechazado mientras se revisa al 100 %",
     "W-CAR 16: el lote rechazado entero; el mayor de 2035 es el de media semana de 50 kg (%s)" % f1(SEM_T[50] / 2),
     "3,0 × 2,4 m", math.ceil(SEM_T[50] / 2)),
]
LUGARES = {k[1]: k[5] for k in STOCK_CARROS}
# PT de manuales (W-MAN, Embalaje y paletizado): «Llevar el pallet al rack de PT o al de cilindros (mismo almacén)»;
# «el autoelevador lo ubica en altura o lo carga directo al camión». Pallets: 7,9 por día en el pico (tabla de la BOM).
# Stock: despacho semanal por pallet completo (X-DT, Almacen PT): 5 × 7,9 = 40 pallets; stock de oct-nov para
# diciembre (X-DT): 6.343 u a 211 u por pallet (1.665 recipientes ÷ 7,9 pallets, W-MAN) = 30 pallets. Total 70.
# Revendidos: la sección «Almacén de producto terminado» de X-ALM (17 posiciones de rack) va al rack de PT.
PT_MAN = {"pallets_dia": 7.9, "semana": 40, "diciembre": 30, "total": 70, "reventa": 17, "modulos": 5,
          "modulos_b": 4, "niveles": 5}
# rack A de 5 módulos y rack B de 4 (el tramo libre del rack B es la entrega de la envolvedora): 90 posiciones >= 87
PT_MAN["posiciones"] = (PT_MAN["modulos"] + PT_MAN["modulos_b"]) * PT_MAN["niveles"] * 2

# ================================================================ PASILLOS
Z("A2", "Pasillo principal: carril del autoelevador", R(0, Y_S, LX, Y_AE), "CIRC", _AE, tipo="pasillo", sub="AE")
Z("A2-S", "Pasillo principal: senda peatonal", R(0, Y_AE, LX, Y_A2), "CIRC",
  "Senda demarcada de 1,5 m, separada del carril por baranda con cruces (croquis del usuario, lámina de accesos)",
  tipo="pasillo", sub="SP")
Z("AL-A", "Almacén: pasillo AL-A (máquinas de corte y embutido)", R(9.0, Y_A2, X_AL, LY), "CIRC", _AE,
  tipo="pasillo", sub="AE")
Z("AL-B", "Almacén: pasillo AL-B (racks)", R(1.2, Y_A2, 4.8, LY), "CIRC", _AE15, tipo="pasillo", sub="AE")
Z("PN", "Senda norte: puertas de la administración a la planta", R(X_AL, Y_M, X_PINT, LY), "CIRC",
  "Senda peatonal de 2,0 m frente a todas las puertas a planta (croquis del usuario)", tipo="pasillo", sub="SP")
Z("PO-AB", "Pasillo de operarios entre las filas A y B de manuales", R(18.0, 39.0, 35.3, 41.0), "CIRC",
  "2,0 m: carro FCHP de 0,61 m + paso de dos personas", tipo="pasillo", sub="PO")
Z("PO-BC", "Pasillo de operarios entre las filas B y C de manuales", R(18.0, 33.0, 35.3, 35.0), "CIRC",
  "2,0 m: carro FCHP de 0,61 m + paso de dos personas", tipo="pasillo", sub="PO")
Z("PO-N1", "Pasillo norte-sur de operarios (filas de manuales a la columna este)", R(35.3, Y_CN, 36.8, Y_M), "CIRC",
  "1,5 m: vincula la senda norte, los pasillos de las filas y la senda del pasillo principal", tipo="pasillo", sub="PO")
Z("PO-C", "Pasillo de operarios de la columna este (soldadura circunferencial a secado)", R(43.8, Y_CN, 45.3, Y_M),
  "CIRC", "1,5 m: los carros bajan por la columna y cruzan al granallado", tipo="pasillo", sub="PO")
Z("PS-1", "Paso peatonal norte-sur entre carros 4/5 y 6/7", R(35.3, Y_A2, 36.8, Y_CN), "CIRC",
  "1,5 m", tipo="pasillo", sub="SP")
Z("PO-N2", "Pasillo norte-sur de operarios y carros a mano (pasillo principal a la senda norte)",
  R(57.3, Y_A2, 58.8, Y_M), "CIRC", "1,5 m: secos al pulmón 11, detección al cuelgue", tipo="pasillo", sub="PO")
Z("PS-S", "Senda de los locales del sur (mantenimiento, calidad, compresores)", R(0, 8.4, 24.7, 9.9), "CIRC",
  "1,5 m", tipo="pasillo", sub="SP")
Z("PS-3", "Paso peatonal de la senda sur al pasillo principal", R(10.0, 9.9, 11.5, Y_S), "CIRC", "1,5 m",
  tipo="pasillo", sub="SP")

# ================================================================ ALMACÉN DE MP (oeste)
# Secciones de la planilla de almacenes (X-ALM v5, hoja Resumen; colores de la leyenda «Sección» del croquis del
# usuario). Posiciones = stock máximo de la política del MRP, redondeado por ítem (hoja Dimensionamiento).
# (código: nombre, posiciones de X-ALM, dónde va en el plano, color)
SECCIONES_ALM = {
    "PT": ("Almacén de producto terminado (revendidos)", 17,
           "Rack de PT de matafuegos terminados (PTM-1): la sección es de producto terminado", (78, 121, 167)),
    "EMB": ("Embalaje", 50, "R1: cajas de cartón, 41 pos.; pilas de pallets vacíos en piso, 7; estantería "
            "(etiquetas de caja), 2", (242, 142, 43)),
    "MON": ("Insumos de montaje (manuales)", 31, "R1: 27 pos.; estantería (asientos M22), 4", (89, 161, 79)),
    "SOL": ("Insumos de soldadura y superficie", 12, "R1: alambre y granalla", (176, 122, 161)),
    "CAS": ("Rack de casquetes y cuplas (carros)", 11, "Rack propio de W-CAR: 12 posiciones", (118, 183, 178)),
    "ICA": ("Rack de insumos de montaje (carros)", 7, "Rack propio de W-CAR: 8 posiciones", (237, 201, 72)),
    "POL": ("Depósito de polvo químico", 8, "Local cerrado: 4 pilas de 2 big bags y 1 pila de 2 pallets de pintura "
            "(sin los polvos de recargas)", (225, 87, 89)),
    "CHF": ("Chapa y fleje (manuales)", 28, "Rack de chapas por espesor y 21 bobinas en sus calles", (156, 117, 95)),
    "CCH": ("Calle de chapa (carros)", 3, "Calle de 10 × 2 m con 3 posiciones (W-CAR)", (186, 176, 172)),
    "CAN": ("Cantilever de caños y barras", 11, "Cantiléver de 12,4 m", (47, 111, 143)),
    "IDE": ("Identificación", 9, "Estantería de cajas bajo llave", (255, 157, 167)),
    "GAS": ("Jaula de gases", 12, "Jaula exterior (packs) y jaula de tubos de la cuarentena", (211, 114, 149)),
}
# R1: 10 módulos de 2,67 m con 2 pallets por nivel y 4 niveles (8 posiciones). Cada columna de pallets (4 posiciones)
# es de una sección; la columna 11 lleva 1 posición de embalaje y 3 de montaje. Orden desde el pasillo principal:
# embalaje (el que más se mueve), montaje de manuales y soldadura.
COLUMNAS_R1 = ["EMB"] * 10 + ["EMB/MON"] + ["MON"] * 6 + ["SOL"] * 3     # 41 EMB, 27 MON (3 + 24), 12 SOL
_XALM = "X-ALM v5, hoja Resumen"
Z("AL-R1", "Rack selectivo R1, 4 niveles: 10 módulos = 80 posiciones (embalaje, montaje de manuales y soldadura)",
  R(0.1, Y_A2, 1.2, LY), "MP", _XALM + ": embalaje 41 + insumos de montaje de manuales 27 + soldadura y superficie 12 "
  "posiciones de rack (el resto de esas secciones va en piso o estantería)")
Z("AL-W", "Franja del muro oeste", R(0, Y_A2, 0.1, LY), "MP", "Separación del rack al muro")
Z("AL-AB", "Estacionamiento de los carros de abastecimiento", R(4.8, Y_A2, 6.0, 23.7), "MP",
  "W-CAR 1 tabla 5: 3 × 1 m para los 2 carros de carros; W-MAN 1: carro de abastecimiento de manuales (uno más)")
Z("AL-RC", "Racks de carros: casquetes y cuplas (12 posiciones) e insumos de montaje (8 posiciones)",
  R(4.8, 23.7, 6.0, 36.15), "MP", "W-CAR 1 tabla 5: 7,3 × 1,2 m y 4,9 × 1,2 m, alto ≈ 3 m, 2 niveles", 14.7)
Z("AL-RT", "Retenidos de MP (zona roja de 4 × 1,5 m, 3 pallets)", R(4.8, 36.15, 7.2, 40.3), "MP",
  "W-CAR 1 tabla 5: 4 × 1,5 m, rojo, 3 pallets", 6.0)
Z("AL-PV", "Pilas de pallets vacíos (sección embalaje, 7 pilas en piso)", R(4.8, 40.3, 7.2, 44.8), "MP",
  "X-ALM: pallet de madera 1200 × 1000, 7 posiciones en piso (1 nivel)")
Z("AL-ES", "Estantería de cajas: identificación (bajo llave) e insumos chicos", R(4.8, 44.8, 7.2, LY), "MP",
  "X-ALM: identificación 9 lugares + asientos M22 4 + etiquetas de caja 2, de 0,6 m² en 5 niveles")
Z("AL-HO", "Rack de chapas por espesor (manuales)", R(6.0, Y_A2, 9.0, 24.5), "MP",
  "W-MAN 1, paso 5: «racks por espesor (hojas)»; X-ALM: hojas de manuales P02 a P04")
Z("AL-CC", "Calle de chapa de carros (10 × 2 m, 3 posiciones)", R(6.0, 24.5, 9.0, 34.3), "MP",
  "W-CAR 1 tabla 5: calle de 10 × 2 m, 3 posiciones de 3,0 × 1,5 m con 2 paquetes, acceso de costado", 20.0)
Z("AL-F", "Franja detrás del cantiléver", R(6.0, 34.3, 7.2, 36.15), "MP", "")
Z("AL-CA", "Cantiléver de caños y barras (5 niveles)", R(7.2, 34.3, 9.0, LY), "MP",
  "X-ALM: 11 posiciones (30 m² netos con 3 niveles); con 5 niveles basta un frente de 12,4 m")

for i in range(10):
    secs = dict.fromkeys(s for c in COLUMNAS_R1[2 * i:2 * i + 2] for s in c.split("/"))
    E(f"R1-{i + 1}", "Rack 4 niveles: " + " y ".join(SECCIONES_ALM[s][0].lower() for s in secs),
      Rw(0.1, 20.1 + i * 2.67, 1.1, 2.67), "AL-R1", "rack", "E", 0,
      "X-ALM: pallet 1200 × 1000, 4 niveles; sección según la hoja Dimensionamiento", ae=True)
E("AB-1", "Estacionamiento de los 3 carros de abastecimiento (2 de carros y 1 de manuales, FCEP10520)",
  R(4.9, 20.1, 5.9, 23.6), "AL-AB", "carro_plat", "O", 0,
  "W-CAR 1 tabla 5: 3 × 1 m, amarillo (2 carros de 1065 × 700); un carro más para manuales (W-MAN 1)")
E("RC-1", "Rack de casquetes y cuplas de carros: 3 módulos de 2,3 m × 2 niveles = 12 posiciones",
  R(4.8, 23.8, 6.0, 31.1), "AL-RC", "rack", "O", 0, "W-CAR 1 tabla 5: 7,3 × 1,2 m, alto ≈ 3 m", ae=True)
E("RC-2", "Rack de insumos de montaje de carros (ruedas, mangas, válvulas, arandelas, alambre): 2 módulos × "
  "2 niveles = 8 posiciones", R(4.8, 31.25, 6.0, 36.15), "AL-RC", "rack", "O", 0,
  "W-CAR 1 tabla 5: 4,9 × 1,2 m, alto ≈ 3 m", ae=True)
E("RT-1", "Retenidos de MP: 3 pallets en zona demarcada en rojo", R(4.8, 36.2, 6.3, 40.2), "AL-RT", "nc", "O", 0,
  "W-CAR 1 tabla 5: 4 × 1,5 m, rojo", ae=True)
E("PV-1", "Pilas de pallets vacíos (frente)", R(4.8, 40.4, 6.0, 44.7), "AL-PV", "pallets_q", "O", 0,
  "X-ALM: 7 pilas de pallets 1200 × 1000 en piso", ae=True)
E("PV-2", "Pilas de pallets vacíos (fondo; se toman después de las del frente)", R(6.05, 40.4, 7.2, 43.6), "AL-PV",
  "pallets_q", "O", 0, "X-ALM: 7 pilas de pallets 1200 × 1000 en piso", ae=True)
E("ES-1", "Estantería de cajas, 5 niveles: identificación bajo llave (obleas, estampillas, tarjetas, etiquetas del "
  "cilindro, impresos), asientos M22 y etiquetas de caja", R(4.85, 44.9, 5.75, 46.9), "AL-ES", "estanteria", "O", 0,
  "X-ALM: 15 lugares de 0,6 m² en 5 niveles = 1,8 m²")
E("HO-1", "Rack de chapas por espesor (4 niveles): bocas de 2,0 mm (1500 × 3000), 1,25 mm (1220 × 2440) y 1,6 mm "
  "(1000 × 2000)", R(6.0, 20.15, 9.0, 24.45), "AL-HO", "rack", "E", 0,
  "W-MAN 1, paso 5: «racks por espesor (hojas)»; formatos y paquetes de W-MAN 1", ae=True)
for i, y in enumerate((24.75, 28.0, 31.25)):
    E(f"CC-{i + 1}", f"Calle de chapa de carros, posición {i + 1}: paquete 1500 × 3000 (hasta 2 de alto)",
      R(7.25, y, 8.75, y + 3.0), "AL-CC", "paquetes", "E", 0,
      "W-CAR 1 tabla 5: posición de 3,0 × 1,5 m; el autoelevador toma el paquete por el lado de 3 m", ae=True)
E("CA-1", "Cantiléver simple, 5 niveles, brazos de 1,2 m (caños de 6 m y barras)", R(7.4, 34.35, 9.0, 46.75),
  "AL-CA", "cantilever", "E", 0, "X-ALM: 11 posiciones", ae=True)

# ================================================================ BANDA SUR OESTE: recepción, almacén complementario y servicios
Z("SR-CU", "Cuarentena de MP: 7 pallets, mesa de inspección y circulación", R(0, 11.0, 10.0, Y_S), "MP",
  "W-CAR 1 tabla 5: 10 × 2,5 m (7 pallets + mesa de inspección de 1,2 × 0,6 m y 1,3 m de circulación), pegada al "
  "portón; compartida con manuales (W-MAN 1)", 25)
Z("SR-CU0", "Jaula de tubos de gas y paso detrás de la cuarentena", R(0, 9.9, 10.0, 11.0), "MP",
  "W-CAR 1 tabla 5: jaula de tubos de gas de 2 × 1 m, ventilada")
Z("SR-RE", "Recepción: balanza de plataforma", R(11.5, 9.9, 13.0, Y_S), "MP",
  "W-MAN 1 y W-CAR 1: balanza de plataforma de 1,20 × 1,20 m, 1.500 kg")
Z("SR-PQ", "Depósito de polvo químico y pintura en polvo (cerrado, zona seca): big bags en el piso, de a 2",
  R(13.0, 10.7, 18.4, Y_S), "MP",
  "W-CAR 1: big bags en el piso apilados de a 2, por fecha de envasado, en el depósito seco de la planta; X-ALM: "
  "stock máximo 5,2 big bags de manuales + 1,6 de carros (8) y 1,1 pallets de pintura (2): 5 pilas de 2",
  tipo="local")
Z("SR-PQ1", "Franja al sur del depósito de polvo", R(13.0, 9.9, 18.4, 10.7), "MP", "")
Z("SR-FL", "Bobinas de fleje (21 posiciones en 7 calles de 3)", R(18.4, 9.9, 24.7, Y_S), "MP",
  "X-ALM: chapa y fleje, bobinas sobre pallet en piso (1 nivel), 21 lugares", 22.0)
E("CU-1", "Cuarentena: 7 posiciones de pallet 1200 × 1000", R(1.05, 12.3, 8.4, Y_S), "SR-CU", "pallets_q", "N", 0,
  "W-CAR 1 tabla 5: 7 pallets; pegada al portón P1", ae=True)
E("RE-2", "Mesa de inspección de recepción", R(8.65, 12.75, 9.85, 13.35), "SR-CU", "banco", "S", 1,
  "W-CAR 1 tabla 5: 1,2 × 0,6 m, dentro de la cuarentena")
E("CU-2", "Jaula de tubos de gas (N₂ y Ar/CO₂, llenos separados de vacíos)", R(0.3, 9.95, 2.3, 10.95), "SR-CU0",
  "jaula", "N", 0, "W-CAR 1 tabla 5: 2 × 1 m, ventilada")
E("RE-1", "Balanza de plataforma 1,20 × 1,20 m, 1.500 kg", R(11.65, 12.2, 12.85, 13.4), "SR-RE", "balanza", "N", 0,
  "W-MAN 1 / W-CAR 1", ae=True)
for i in range(4):
    E(f"PQ-{i + 1}", "Pila de 2 big bags de polvo ABC de 1 t (1,0 × 1,0 × 1,2 m cada uno)", Rw(13.05 + i * 1.05, 12.4, 1.0, 1.0),
      "SR-PQ", "bigbag", "N", 0, "W-CAR 1: big bags en el piso, apilados de a 2", ae=True)
E("PQ-5", "Pila de 2 pallets de pintura en polvo", R(17.25, 12.2, 18.25, 13.4), "SR-PQ", "pallets_q", "N", 0,
  "X-ALM: pintura en polvo, 2 pallets", ae=True)
for i in range(7):
    E(f"FL-{i + 1}", "Calle de 3 bobinas de fleje sobre pallet", Rw(18.45 + i * 0.89, 9.95, 0.85, 3.5), "SR-FL",
      "portaflejes", "N", 0, "X-ALM: P05 a P11", ae=True)

# locales del ángulo SO
Z("SV-CP", "Sala de compresores y secador de aire", R(0, 0, 5.0, 5.2), "AUX",
  "Consumo de aire de pintura, láser, granalladora, cargadora y prensas (ET); sala contra muro exterior", 0,
  tipo="local")
Z("SV-TG", "Tablero general de baja tensión", R(0, 5.2, 5.0, 8.4), "AUX", "Acometida desde el muro oeste", 0,
  tipo="local")
Z("SV-MA", "Taller de mantenimiento", R(5.0, 0, 12.6, 8.4), "AUX",
  "Croquis del usuario (mantenimiento en el ángulo SO)", 0, tipo="local")
Z("SV-PA", "Pañol de herramientas y repuestos", R(12.6, 0, 16.6, 8.4), "AUX",
  "Croquis del grupo (pañol de 3,8 × 4,5 m)", 0, tipo="local")
Z("SV-CA", "Laboratorio de control de calidad: metrología, ensayo de rotura, patrones y contramuestras",
  R(16.6, 0, 21.4, 8.4), "AUX", "Croquis del usuario (calidad en el ángulo SO); W-MAN 12: «de cada lote se separa 1 "
  "cilindro para el ensayo de rotura: el inspector lo lleva al laboratorio de control de calidad»; W-CAR: técnico de "
  "calidad", 0, tipo="local")
Z("LB-1", "Libre (reserva)", R(21.4, 0, 24.7, 8.4), "LIB", "Croquis del usuario: espacio libre")
E("CP-1", "Compresor a tornillo", R(0.5, 0.5, 2.3, 1.7), "SV-CP", "compresor", "N", 0, "")
E("CP-2", "Compresor a tornillo (reserva)", R(2.7, 0.5, 4.5, 1.7), "SV-CP", "compresor", "N", 0, "")
E("CP-3", "Tanque pulmón de aire", R(0.6, 2.6, 1.6, 3.6), "SV-CP", "tanque", "N", 0, "")
E("CP-4", "Secador frigorífico y filtros", R(2.8, 2.6, 4.4, 3.4), "SV-CP", "deshumidificador", "N", 0, "")

# equipamiento de los locales del ángulo SO (mobiliario de planta/mobiliario.py, dentro de su local)
_TALLER = "Criterio: equipamiento básico de un taller de mantenimiento"
MOB_NAVE = [   # (tipo, R, frente, n, zona, fuente)
    ("banco_trabajo", R(5.3, 0.2, 7.8, 0.9), "N", 1, "SV-MA", _TALLER),
    ("torno", R(8.2, 0.2, 10.2, 1.0), "N", 1, "SV-MA", _TALLER),
    ("agujereadora", R(10.6, 0.2, 11.5, 1.0), "N", 1, "SV-MA", _TALLER),
    ("soldadora", R(11.7, 0.2, 12.5, 1.0), "N", 1, "SV-MA", _TALLER),
    ("estanteria", R(5.2, 5.0, 5.8, 7.8), "E", 1, "SV-MA", _TALLER),
    ("estanteria", R(11.9, 2.4, 12.5, 6.4), "O", 1, "SV-MA", _TALLER),
    ("estanteria", R(12.8, 0.2, 16.4, 0.8), "N", 1, "SV-PA", "Pañol: estanterías de herramientas y repuestos"),
    ("estanteria", R(12.8, 2.0, 16.4, 2.6), "S", 1, "SV-PA", "Pañol: estanterías de herramientas y repuestos"),
    ("estanteria", R(12.8, 2.6, 16.4, 3.2), "N", 1, "SV-PA", "Pañol: estanterías de herramientas y repuestos"),
    ("estanteria", R(12.8, 4.4, 16.4, 5.0), "S", 1, "SV-PA", "Pañol: estanterías de herramientas y repuestos"),
    ("mostrador", R(14.9, 6.6, 16.4, 7.4), "S", 1, "SV-PA", "Pañol: entrega con registro"),
    ("marmol", R(16.8, 0.2, 18.8, 1.2), "N", 1, "SV-CA", "W-MAN y W-CAR: calibres, micrómetros, medidor de espesor"),
    ("mesa_lab", R(19.2, 0.2, 21.2, 0.9), "N", 1, "SV-CA", "W-CAR 12: medidor de espesor de recubrimiento"),
    ("estanteria", R(16.8, 2.0, 17.4, 4.0), "E", 1, "SV-CA", "Contramuestras y probetas (W-CAR 12 y 17)"),
    ("escritorio", R(19.4, 4.6, 21.0, 5.5), "S", 1, "SV-CA", "Técnico de calidad (W-CAR)"),
    ("archivo", R(20.6, 6.2, 21.2, 7.4), "O", 2, "SV-CA", "Protocolos y certificados de lote (W-CAR 16)"),
    ("tablero_el", R(0.3, 5.4, 4.2, 6.0), "N", 3, "SV-TG", "Tablero general de baja tensión"),
]

# ================================================================ FILA DE FABRICACIÓN DE CARROS (20,0 a 29,0)
_W = "W-CAR, tabla de espacios del puesto"
Z("C-02", "2 Corte de chapa (guillotina común a manuales y carros)", R(X_AL, Y_A2, 21.3, 27.4), "CAR",
  _W + " 2: ≈ 5,9 × 7,4 m", 44)
Z("C-02N", "Salida de desarrollos de la guillotina a manuales", R(18.0, 27.4, 21.3, Y_CN), "CAR",
  "W-CAR 2: zona trasera; W-MAN 6: carro de desarrollos")
Z("C-021", "2.1 Marcado del cuerpo", R(21.3, 26.4, 24.8, Y_CN), "CAR", _W + " 2.1: ≈ 3,5 × 2,5 m", 9)
Z("C-03", "3 Cilindrado", R(21.3, Y_A2, 28.8, 25.0), "CAR", _W + " 3: ≈ 7,0 × 5,0 m", 35)
Z("C-03N", "Paso de la mesa móvil del marcado al cilindrado", R(21.3, 25.0, 28.8, 26.4), "CAR",
  "W-CAR 2.1 y 3: EFE 600 y mesa móvil entre el marcado y la roladora")
Z("C-03E", "Paso de los carros del marcado al cilindrado", R(24.8, 26.4, 28.8, Y_CN), "CAR",
  "W-CAR 2.1: los carros llenos esperan al costado de la mesa de marcado")
Z("C-05", "5 Soldadura longitudinal", R(29.3, Y_A2, 35.3, 24.0), "CAR", _W + " 5: ≈ 5,5 × 4,0 m", 22)
Z("C-04", "4 Punteo del cuerpo", R(29.3, 24.5, 35.3, Y_CN), "CAR", _W + " 4: ≈ 6,0 × 4,5 m", 27)
Z("C-45", "Cortina de soldadura entre 3 y 4/5", R(28.8, Y_A2, 29.3, Y_CN), "CAR", "W-CAR 4: cortina de soldadura")
Z("C-45b", "Cortina de soldadura entre 4 y 5", R(29.3, 24.0, 35.3, 24.5), "CAR", "W-CAR 4: cortina de soldadura")
Z("C-07", "7 Armado y soldadura circunferencial", R(36.8, Y_A2, 42.8, 24.5), "CAR", _W + " 7: ≈ 6,0 × 4,5 m", 27)
Z("C-06", "6 Soldadura de cupla en la cúpula", R(36.8, 25.5, 42.8, Y_CN), "CAR", _W + " 6: ≈ 4,5 × 3,5 m", 16)
Z("C-67", "Paso del carro canasto de cúpulas de 6 a 7", R(36.8, 24.5, 42.8, 25.5), "CAR", "W-CAR 6 y 7")
Z("C-08", "8 Soldadura de accesorios", R(43.3, Y_A2, 49.8, 24.5), "CAR", _W + " 8: ≈ 6,5 × 4,5 m", 29)
Z("C-081", "8.1 Fabricación de accesorios", R(43.3, 25.0, 51.3, Y_CN), "CAR", _W + " 8.1: ≈ 8,0 × 4,0 m", 32)
Z("C-78", "Cortina de soldadura entre 7 y 8", R(42.8, Y_A2, 43.3, Y_CN), "CAR", "W-CAR 8: cortina de soldadura")
Z("C-88", "Cortina entre 8 y 8.1", R(43.3, 24.5, 51.3, 25.0), "CAR", "W-CAR 8: cortina de soldadura")
Z("C-08E", "Salida de los carros sobre su juego provisorio", R(49.8, Y_A2, 51.3, 24.5), "CAR",
  "W-CAR 8: salida demarcada en amarillo")

# ---- 2 corte (W-CAR 2)
E("C2-1", "Mesa elevadora de tijera SJG3.0-1.6 (2600 × 1800, 3 t)", R(17.0, 20.05, 19.6, 21.85), "C-02", "mesa_tijera",
  "S", 0, "W-CAR 2: 2,6 × 1,8 m, 1 m de paso hasta la guillotina", ae=True)
E("C2-2", "Guillotina hidráulica CENA 8 × 3200", R(16.4, 22.95, 20.3, 25.05), "C-02", "guillotina", "S", 1,
  "W-CAR 2: ≈ 3,9 × 2,1 m")
E("C2-3", "Rampa trasera de salida (pulmón de cuerpos cortados)", R(16.4, 25.1, 20.3, 25.7), "C-02",
  "mesa_rodillos", "N", 0, "W-CAR 2: zona trasera de 3,9 × 2,5 m")
E("C2-4", "Contenedor de scrap 1.000 L con volcador", R(15.45, 25.9, 16.92, 27.32), "C-02", "contenedores", "O", 0,
  "W-CAR 2: 1470 × 1420 mm, detrás de la guillotina", ae=True)
E("C2-5", "Carro de salida: desarrollos de manuales en llenado", R(17.3, 26.1, 18.4, 26.8), "C-02", "carro_plat",
  "N", 0, "W-CAR 2: carro de salida 1,1 × 0,7 m; W-MAN 2")
E("C2-6", "Carro de traslado de columnas de 3,2 mm", R(14.1, 25.8, 15.1, 27.4), "C-02", "carro_plat", "E", 0,
  "W-CAR 2: carros de traslado de columnas (2, uno por espesor), plataforma de al menos 1,6 × 1,0 m, 500 kg")
E("C2-7", "Carro de traslado de columnas de 4,75 mm", R(18.55, 26.0, 20.15, 27.0), "C-02", "carro_plat", "N", 0,
  "W-CAR 2: carros de traslado de columnas (2, uno por espesor), plataforma de al menos 1,6 × 1,0 m, 500 kg")
# ---- 2.1 marcado
E("C21-1", "Mesa de marcado con marcadora DTMAQ MPE 150130 y controlador", R(21.4, 26.5, 22.8, 27.5), "C-021",
  "marcadora", "N", 1, "W-CAR 2.1: 1,4 × 1,0 m, pegada a la rampa")
E("C21-2", "Carro portaplacas EFE 600 (cuerpos de 25 y 50 kg)", R(23.0, 26.5, 24.05, 27.1), "C-021", "efe", "N", 0,
  "W-CAR 2.1: 1,05 × 0,6 m")
E("C21-3", "Mesa móvil (cuerpos de 70 y 100 kg)", R(23.2, 27.4, 24.5, 28.4), "C-021", "mesa_movil", "N", 0,
  "W-CAR 2.1: 1,3 × 1,0 m")
E("C21-4", "Tablero: planilla de trazabilidad, punzón DPS y maza", R(21.5, 28.65, 22.5, 28.95), "C-021",
  "tablero_herr", "S", 0, "W-CAR 2.1: 1,0 × 0,3 m")
# ---- 3 cilindrado
E("C3-1", "Roladora CNC 4 rodillos W12 8 × 1500 (0,8 m libres detrás)", R(23.2, 22.0, 26.4, 23.4), "C-03",
  "cilindradora", "N", 1, "W-CAR 3: ≈ 3,2 × 1,4 m")
E("C3-2", "Carro portaplacas EFE 600 (carga)", R(23.3, 24.4, 24.35, 25.0), "C-03", "efe", "N", 0, "W-CAR 3")
E("C3-3", "Mesa móvil (carga de 70 y 100 kg)", R(24.6, 25.1, 25.9, 26.1), "C-03N", "mesa_movil", "S", 0,
  "W-CAR 3: 1,3 × 1,0 m")
E("C3-4", "Salida axial y cuna volcadora", R(26.6, 22.2, 27.8, 23.2), "C-03", "cuna", "N", 0,
  "W-CAR 3: ≈ 1,2 × 1,0 m")
E("C3-5", "Pulmón de cuerpos rolados y tiras", R(26.8, 20.2, 28.6, 21.4), "C-03", "pulmon", "S", 0,
  "W-CAR 3: 1,8 × 1,2 m")
# ---- 4 punteo
E("C4-1", "Virador Serecon ZJ R-410 sobre base fija (1 m libre en cada boca)", R(31.6, 26.6, 32.8, 27.2), "C-04",
  "posicionador", "S", 1, "W-CAR 4: 1,2 × 0,6 m")
E("C4-2", "Soldadora Pampa 300 y tubo de gas", R(31.75, 27.9, 32.65, 28.4), "C-04", "soldadora", "S", 0,
  "W-CAR 4: 0,9 × 0,5 m")
E("C4-3", "Banco de trabajo con morsa", R(29.5, 27.9, 31.0, 28.6), "C-04", "banco", "S", 0, "W-CAR 4: 1,5 × 0,7 m")
E("C4-4", "Cuna volcadora (salida)", R(33.9, 26.55, 34.8, 27.25), "C-04", "cuna", "S", 0, "W-CAR 4: ≈ 0,9 × 0,7 m")
E("C4-5", "Pulmón de cuerpos punteados", R(33.5, 24.7, 35.1, 25.9), "C-04", "pulmon", "S", 0, "W-CAR 4: 1,6 × 1,2 m")
E("C4-6", "Brazo de extracción de humos con campana orientable", R(32.9, 27.4, 33.4, 27.9), "C-04", "colector10", "S", 0,
  "W-CAR: brazo de extracción de humos Nederman Original (precio a cotizar); medida: criterio")
# ---- 5 soldadura longitudinal
E("C5-1", "Soldadora longitudinal ZH-1300 Dragon Welding con su mesa", R(30.6, 21.6, 32.9, 22.74), "C-05",
  "sold_long", "N", 1, "W-CAR 5: 2,30 × 1,14 m")
E("C5-2", "Zona de carga axial (extremo libre del mandril)", R(33.0, 21.6, 34.5, 22.7), "C-05", "zona_carga", "N", 0,
  "W-CAR 5: 1,5 × 1,1 m")
E("C5-3", "Fuente MIG-350IX y tubo de gas", R(29.45, 21.3, 30.4, 22.2), "C-05", "soldadora", "E", 0,
  "W-CAR 5: 0,6 × 0,9 m + tubo")
E("C5-4", "Chiller de la torcha", R(29.45, 20.2, 30.17, 20.73), "C-05", "chiller", "N", 0, "W-CAR 5: 0,72 × 0,53 m")
E("C5-5", "Cuna volcadora (entrada desde el punteo)", R(33.2, 23.0, 34.1, 23.7), "C-05", "cuna", "N", 0,
  "W-CAR 5: ≈ 0,9 × 0,7 m")
E("C5-6", "Zona de no conforme (roja)", R(33.6, 20.2, 34.6, 21.0), "C-05", "nc", "N", 0, "W-CAR 5: 1,0 × 0,8 m")
E("C5-7", "Extracción de humos sobre la torcha", R(31.0, 20.4, 31.5, 20.9), "C-05", "colector10", "S", 0,
  "W-CAR: brazo de extracción de humos Nederman Original (precio a cotizar); medida: criterio")
# ---- 6 soldadura de cupla
E("C6-1", "Mesa Müller con posicionador VEVOR y soporte de torcha", R(38.6, 27.6, 39.5, 28.2), "C-06",
  "posicionador", "S", 1, "W-CAR 6: ≈ 0,9 × 0,6 m")
E("C6-2", "Carro 1: cúpulas y cuplas", R(37.2, 27.55, 38.27, 28.25), "C-06", "carro_plat", "S", 0,
  "W-CAR 6: 1,07 × 0,7 m")
E("C6-3", "Canasto de enfriamiento (bajo la campana)", R(39.8, 27.6, 40.4, 28.2), "C-06", "canasto", "S", 0,
  "W-CAR 6: 0,6 × 0,6 m")
E("C6-4", "Cajonera de herramientas", R(38.75, 28.35, 39.25, 28.85), "C-06", "cajonera", "S", 0,
  "W-CAR 6: ≈ 0,5 × 0,5 m")
E("C6-5", "Carro canasto de salida (hacia el puesto 7)", R(39.9, 25.7, 41.0, 26.4), "C-06", "canasto", "S", 0,
  "W-CAR 6: ≈ 1,1 × 0,7 m")
E("C6-6", "Soldadora Pampa 300 y tubo de gas", R(37.4, 25.7, 38.3, 26.2), "C-06", "soldadora", "S", 0,
  "W-CAR 6: 0,9 × 0,5 m")
E("C6-7", "Extracción con campana sobre la mesa y el canasto", R(40.6, 28.3, 41.1, 28.8), "C-06", "colector10", "S", 0,
  "W-CAR: brazo de extracción de humos Nederman Original (precio a cotizar); medida: criterio")
# ---- 7 armado y soldadura circunferencial
E("C7-1", "Virador 1.000 kg sobre base fija, con tope axial y soporte de torcha", R(38.9, 22.0, 40.5, 22.8), "C-07",
  "posicionador", "N", 1, "W-CAR 7: ≈ 1,6 × 0,8 m")
E("C7-2", "Cuna volcadora de entrada", R(36.9, 21.9, 37.8, 22.6), "C-07", "cuna", "E", 0, "W-CAR 7: ≈ 0,9 × 0,7 m")
E("C7-3", "Carro canasto de cúpulas", R(37.0, 23.5, 38.1, 24.2), "C-07", "canasto", "S", 0, "W-CAR 7: 1,1 × 0,7 m")
E("C7-4", "Carro 2: fondos", R(37.0, 20.2, 38.1, 20.9), "C-07", "carro_plat", "S", 0, "W-CAR 7: 1,1 × 0,7 m")
E("C7-5", "Cuna volcadora de salida", R(41.6, 21.9, 42.5, 22.6), "C-07", "cuna", "O", 0, "W-CAR 7: ≈ 0,9 × 0,7 m")
E("C7-6", "Pulmón de cilindros cerrados", R(41.2, 20.2, 42.7, 21.4), "C-07", "pulmon", "S", 0,
  "W-CAR 7: 1,5 × 1,2 m")
E("C7-7", "Soldadora Pampa 300 y tubo de gas", R(39.25, 23.85, 40.15, 24.35), "C-07", "soldadora", "S", 0,
  "W-CAR 7: 0,9 × 0,5 m")
E("C7-8", "Zona de no conforme de los puestos 6 y 7 (roja)", R(41.9, 23.7, 42.6, 24.3), "C-07", "nc", "S", 0,
  "W-CAR 7: 0,7 × 0,6 m")
E("C7-9", "Extracción de humos sobre el virador", R(38.9, 20.3, 39.4, 20.8), "C-07", "colector10", "S", 0,
  "W-CAR: brazo de extracción de humos Nederman Original (precio a cotizar); medida: criterio")
# ---- 8 soldadura de accesorios
E("C8-1", "Virador sobre base fija (soldadura de accesorios)", R(45.6, 22.0, 47.2, 22.8), "C-08", "posicionador",
  "N", 1, "W-CAR 8: ≈ 1,6 × 0,8 m")
E("C8-2", "Cuna de entrada (70 y 100 kg)", R(43.5, 21.9, 44.4, 22.6), "C-08", "cuna", "E", 0,
  "W-CAR 8: ≈ 0,9 × 0,7 m")
E("C8-3", "Carro de kits (del puesto 8.1)", R(43.5, 23.0, 44.55, 23.52), "C-08", "carro_plat", "S", 0,
  "W-CAR 8: 1,05 × 0,52 m")
E("C8-4", "Pulmón de juegos provisorios: 3 estanterías de ruedas", R(43.5, 20.1, 49.5, 20.6), "C-08", "estanteria",
  "N", 0, "W-CAR 8: 3 × (2,0 × 0,5 m)")
E("C8-5", "Cajones de ejes provisorios (3)", R(45.6, 20.8, 46.8, 21.2), "C-08", "cajones", "N", 0,
  "W-CAR 8: 3 × (0,4 × 0,4 m)")
E("C8-6", "Tablero de herramientas con la tabla de posiciones", R(48.6, 23.8, 49.6, 24.4), "C-08", "tablero_herr",
  "S", 0, "W-CAR 8: 1,0 × 0,6 m")
E("C8-7", "Soldadora Pampa 300 y tubo de gas", R(45.95, 23.85, 46.85, 24.35), "C-08", "soldadora", "S", 0,
  "W-CAR 8: 0,9 × 0,5 m")
E("C8-8", "Salida: carro sobre su juego provisorio (amarillo)", R(50.0, 22.0, 51.1, 22.7), "C-08E", "lugar", "N", 0,
  "W-CAR 8: 1,1 × 0,7 m")
E("C8-9", "Extracción de humos sobre el virador", R(47.5, 21.0, 48.0, 21.5), "C-08", "colector10", "S", 0,
  "W-CAR: brazo de extracción de humos Nederman Original (precio a cotizar); medida: criterio")
# ---- 8.1 fabricación de accesorios
E("C81-1", "Rack de barras (caño de 1\" y 1 1/4\", trefilado de 3/4\" y 1\")", R(43.6, 28.3, 50.1, 28.9), "C-081",
  "rack", "S", 0, "W-CAR 8.1: 6,5 × 0,6 m")
E("C81-2", "Caballetes con rodillo, sensitiva Bosch GCO 220 y tope", R(43.5, 27.3, 50.3, 27.9), "C-081",
  "caballetes", "S", 1, "W-CAR 8.1: 6,8 × 0,6 m")
E("C81-3", "Dobladora hidráulica", R(50.45, 27.1, 51.15, 28.0), "C-081", "dobladora", "O", 0,
  "W-CAR 8.1: ≈ 0,9 × 0,7 m")
E("C81-4", "Taladro de banco", R(50.5, 26.1, 51.2, 26.7), "C-081", "taladro", "O", 0, "W-CAR 8.1: ≈ 0,7 × 0,6 m")
E("C81-5", "Banco de trabajo con morsa", R(47.7, 25.2, 49.2, 25.9), "C-081", "banco", "N", 1,
  "W-CAR 8.1: 1,5 × 0,7 m")
E("C81-6", "Prensa hidráulica de 20 t", R(49.3, 25.2, 50.8, 25.8), "C-081", "prensa_h", "N", 0,
  "W-CAR 8.1: 1,5 × 0,6 m")
E("C81-7", "Banco de kits (amoladora y plantillas)", R(46.1, 25.2, 47.6, 25.8), "C-081", "banco", "N", 0,
  "W-CAR 8.1: 1,5 × 0,6 m")
E("C81-8", "Carro de cajas", R(43.5, 25.15, 44.7, 25.75), "C-081", "carro_plat", "N", 0, "W-CAR 8.1: 1,2 × 0,6 m")
E("C81-9", "Carro de kits", R(44.8, 25.15, 46.0, 25.75), "C-081", "carro_plat", "N", 0, "W-CAR 8.1: 1,2 × 0,6 m")
# ================================================================ MANUALES (29,0 a 45,0) y su ala este
_M = "W-MAN; máquina de X-MAN; medida de la tabla de áreas v10"
# fila A (41 a 45): embutido, numerado, cúpulas, soldadura de cuello y preparación de cuello
Z("M-04", "4 Corte de disco y embutido (desbobinador, alimentador y prensa)", R(X_AL, 41.0, 25.4, Y_M), "MAN", _M, 26.0)
Z("M-PCU", "Zona de cúpulas (5 carros de 12 cajones), al lado del numerado", R(25.4, 41.0, 28.3, Y_M), "MAN",
  "W-MAN 3: 3 a 5 carros, al lado del numerado y la soldadura de cuello")
Z("M-06", "6 Numerado de cúpula (pegado a la soldadura de cuello)", R(28.3, 41.0, 30.9, Y_M), "MAN",
  _M + "; W-MAN 6: la cúpula pasa a mano a la soldadura de cuello de al lado", 2.3)
Z("M-07", "7 Soldadura del cuello a la cúpula", R(30.9, 41.0, 33.4, Y_M), "MAN", _M, 5.3)
Z("M-05", "5 Preparación de cuello (2 prensas de banco)", R(33.4, 41.0, 35.3, Y_M), "MAN", _M, 4.5)
# fila B (35 a 39): corte de tubo (vertical), tramos, encastre, fondos, bordoneado
Z("M-03", "3 Corte de tubo 1 kg (láser Leapion, orientado norte-sur)", R(X_AL, 27.4, 18.0, Y_M - 4.0), "MAN", _M, 25.5)
Z("M-PT", "Tramos 1 kg: carros «en consumo» y «lleno» al lado del encastre", R(18.0, 35.0, 21.0, 39.0), "MAN",
  "W-MAN 2: al lado del encastre se demarcan dos posiciones de carro de 1,2 × 0,8 m, «en consumo» y «lleno»")
Z("M-10", "10 Encastre de fondo y zona de fondos (5 carros)", R(21.0, 35.0, 26.6, 39.0), "MAN", _M + "; W-MAN 3", 3.6)
Z("M-11", "11 Bordoneado", R(26.6, 35.0, 31.0, 39.0), "MAN", _M, 3.6)
Z("M-PB", "Pulmones del bordoneado a la soldadura circunferencial", R(31.0, 35.0, 35.3, 39.0), "MAN", "W-MAN 9 y 10")
# fila C (29 a 33): cilindrado y soldadura longitudinal
Z("M-08", "8 Cilindrado", R(18.0, Y_CN, 23.4, 33.0), "MAN", _M, 7.3)
Z("M-09", "9 Soldadura longitudinal", R(23.4, Y_CN, 29.4, 33.0), "MAN", _M, 8.4)
Z("M-PV", "Cuerpos soldados y cambio de formato", R(29.4, Y_CN, 35.3, 33.0), "MAN", "W-MAN 7: PU-V2, PU-V3, PU-FX")
# ---- equipos de manuales
_T = "Tabla de áreas v10"
E("M4-1", "Desbobinador con carro portabobinas", R(15.6, 42.6, 17.6, 44.1), "M-04", "desbobinador", "S", 0,
  _T + " (criterio)", ae=True)
E("M4-2", "Enderezador y alimentador servo Cena PRE-1", R(18.4, 42.85, 20.0, 43.85), "M-04", "alimentador", "S", 0,
  _T + " (criterio)")
E("M4-3", "Prensa embutidora Sangiacomo T 63R CE", R(20.3, 42.6, 21.61, 44.1), "M-04", "prensa", "S", 1,
  "ET: 1310 × 1500 × 2790 mm")
E("M4-4", "Contenedor del esqueleto 1.000 L (se lleva con zorra hasta AL-A)", R(21.9, 42.65, 23.37, 44.07), "M-04",
  "contenedores", "S", 0, "W-MAN 3")
E("M4-5", "Estantería de matrices (8 juegos)", R(23.8, 44.2, 25.0, 44.8), "M-04", "estanteria", "S", 0, "W-MAN 3")
E("M4-6", "Carro porta-matrices", R(24.0, 43.15, 25.0, 43.85), "M-04", "carro_plat", "S", 0,
  "W-MAN 3: «las matrices llegan en el carro porta-matrices desde su estantería, al lado de la prensa»; medida: "
  "criterio (carro de plataforma de 1,0 × 0,7 m)")
carros_fila("PU-K", "Cúpulas y fondos en llenado", 23.9, 41.2, 2, "M-04", CAJ, True, "W-MAN 3")
E("M6-1", "Micropercusión Pannier ADP120160D sobre banco", R(29.0, 43.4, 30.2, 44.0), "M-06", "marcadora", "S", 1,
  "Mesa 1,2 × 0,6 (W-CAR 1)")
for i in range(5):
    E(f"PU-CU.{i + 1}", "Zona de cúpulas: carro de 12 cajones", Rw(25.5 + (i % 2) * 1.35, 41.2 + (i // 2) * 1.2, 1.2, 0.8),
      "M-PCU", "carro_caj", "S", 0, "W-MAN 3")
E("M7-1", "Soldadora de cuello Firesafer FS-HFM1", R(31.5, 43.2, 32.7, 44.6), "M-07", "sold_circ", "S", 1,
  "Catálogo Firesafer FS Cylinder Production, pág. 8: 1200 × 1400 × 1580 mm")
carros_fila("PU-CC2", "Cúpulas con cuello en llenado", 31.0, 41.1, 1, "M-07", CAJ, fuente="W-MAN 8")
E("M7-2", "Extracción de humos de la soldadura de cuello", R(32.8, 44.1, 33.3, 44.6), "M-07", "colector10", "S", 0,
  "W-MAN: «extracción de humos» (folleto Nederman); medida: criterio")
E("M7-3", "Cortina de soldadura entre puestos (hacia la preparación de cuello)", R(33.32, 41.1, 33.4, 44.9), "M-07",
  "pantalla", "O", 0, "W-MAN, soldadura del cuello: «extracción de humos y cortina de soldadura entre puestos»")
E("M5-1", "Prensa Pannier MarkFirst MB-21 sobre banco", R(33.5, 43.0, 34.1, 44.2), "M-05", "torno", "E", 1,
  "ET: cabezal 210 × 132 mm; banco 1,2 × 0,6")
E("M5-2", "Prensa Pannier MarkFirst MB-21 sobre banco", R(33.5, 41.3, 34.1, 42.5), "M-05", "torno", "E", 1,
  "ET: cabezal 210 × 132 mm; banco 1,2 × 0,6")
E("M5-3", "Cuños de muesca, dispositivos de sujeción por diámetro y unidad de aire a 6 bar con filtro y regulador",
  R(33.5, 44.35, 34.7, 44.9), "M-05", "cajonera", "S", 0, "W-MAN, preparación de cuello: equipos y herramientas; medida: criterio")
E("M3-1", "Cajón de alimentación del atado (0,5 × 0,5 × 6,5 m)", R(15.5, 29.6, 16.0, 36.1), "M-03", "rack", "E", 0,
  "W-MAN 2", ae=True)
E("M3-2", "Láser de tubo Leapion 6012 1,5 kW", R(16.3, 29.3, 17.1, 36.15), "M-03", "laser", "E", 0,
  "Cotización Leapion: 6850 × 800 × 1200 mm")
E("M3-3", "Contenedor de recortes 1.000 L", R(15.45, 27.5, 16.92, 28.92), "M-03", "contenedores", "O", 0, "W-MAN 2",
  ae=True)
E("M3-4", "Descarga de tramos (operario)", R(16.0, 36.4, 17.6, 37.0), "M-03", "banco", "N", 1, "W-MAN 2")
E("M3-5", "Chiller S&A del láser", R(17.25, 30.0, 17.85, 30.8), "M-03", "chiller", "O", 0, "W-MAN 2: láser con chiller S&A")
E("M3-6", "Compresor de alta presión (11 a 15 bar) con secador y filtros", R(15.5, 38.2, 16.9, 39.1), "M-03",
  "compresor", "E", 0, "W-MAN 2: aire para el cabezal del láser")
E("M3-7", "Extracción de humos localizada en el cabezal del láser", R(14.3, 36.6, 15.0, 37.3), "M-03", "colector10",
  "S", 0, "W-MAN 2: «extracción de humos localizada en el cabezal (recomendada)»; medida: criterio")
# W-MAN 2: «al lado de la cortadora se demarcan en el piso dos posiciones de carro de 1,2 × 0,8 m, "en llenado" y
# "vacío", y al lado del encastre otras dos, "en consumo" y "lleno"»
for i, (nom, r, z) in enumerate([("en llenado", R(17.05, 38.1, 17.85, 39.3), "M-03"),
                                 ("vacío", R(17.05, 39.45, 17.85, 40.65), "M-03"),
                                 ("en consumo", R(19.7, 37.6, 20.9, 38.4), "M-PT"),
                                 ("lleno", R(19.7, 36.6, 20.9, 37.4), "M-PT")]):
    E(f"PU-T.{i + 1}", f"Tramos 1 kg: carro de 12 cajones «{nom}» (posición demarcada de 1,2 × 0,8 m)", r, z,
      "carro_caj", "S", 0, "W-MAN 2")
E("M10-1", "Prensa hidráulica Del Fabro 30 t (encastre)", R(21.6, 37.4, 22.6, 38.55), "M-10", "encastre", "S", 1,
  "ET: 1000 × 1150 × 1800 mm")
for i in range(5):
    E(f"PU-FO.{i + 1}", "Zona de fondos: carro de 12 cajones", Rw(23.2 + (i % 2) * 1.35, 35.2 + (i // 2) * 1.0, 1.2, 0.8),
      "M-10", "carro_caj", "S", 0, "W-MAN 3")
carros_fila("PU-E", "Encastre -> bordoneado (entre las máquinas)", 26.8, 38.2, 1, "M-11", fuente="W-MAN 9")
carros_fila("PU-E2", "Encastre -> bordoneado: carro del cambio de formato", 26.8, 35.3, 1, "M-11",
            fuente="W-MAN 9: se usan dos carros, uno entre las máquinas y otro para el cambio de formato")
E("M11-1", "Bordoneadora motorizada Pilman SWM-400", R(28.5, 37.6, 30.15, 38.3), "M-11", "bordoneadora", "S", 1,
  "Presupuesto Pilman 1310727: 1650 × 700 × 1280 mm")
carros_fila("PU-B", "Bordoneado -> soldadura circunferencial", 31.2, 35.3, 2, "M-PB", fuente="W-MAN 10")
carros_fila("PU-CC", "Cúpulas con cuello en consumo", 34.0, 36.2, 1, "M-PB", CAJ, fuente="W-MAN 8")
carros_fila("PU-D", "Desarrollos junto a la roladora", 18.6, 27.6, 1, "C-02N", fuente="W-MAN 6")
E("M8-1", "Roladora Firesafer FS-RM01", R(19.6, 29.3, 21.4, 30.6), "M-08", "cilindradora", "N", 1,
  "Catálogo Firesafer FS Cylinder Production, pág. 3: 1800 × 1300 × 1250 mm")
carros_fila("PU-V1", "Virolas -> soldadura longitudinal", 21.9, 29.2, 1, "M-08", fuente="W-MAN 6")
E("M9-1", "Soldadora longitudinal Firesafer (ref. Getweld ZF-500)", R(24.6, 29.4, 27.6, 30.3), "M-09", "sold_long",
  "N", 1, "ET Getweld ZF-500: 3000 × 900 × 1600 mm (referencia)")
carros_fila("PU-V2", "Cuerpos soldados en llenado", 27.9, 29.2, 1, "M-09", fuente="W-MAN 7")
E("M9-2", "Extracción de humos de la soldadura longitudinal", R(23.6, 29.4, 24.1, 29.9), "M-09", "colector10", "S", 0,
  "W-MAN: «extracción de humos» (folleto Nederman); medida: criterio")
carros_fila("PU-V3", "Cuerpos soldados al lado de las prensas de encastre", 21.2, 35.2, 1, "M-10",
            fuente="W-MAN 7: uno se llena en la soldadora y el otro queda al lado de las prensas de encastre")
carros_fila("PU-FX", "Carros del cambio de formato", 29.6, 29.2, 3, "M-PV", vertical=False, fuente="W-MAN 7")


# columna este (croquis del usuario: la soldadura circunferencial baja por control de espesor, prueba hidráulica y
# secado; el granallado y la detección siguen hacia el este hasta el cuelgue de la pintura)
_SAT = ("X-MAN 2035, aprovechamiento: sold. longitudinal 97 %, encastre, sold. circunferencial y prueba hidráulica "
        "94 %, secado, preparación de cuello y etiquetado 92 %")
Z("M-12", "12 Soldadura circunferencial (2 máquinas)", R(36.8, 40.5, 43.8, Y_M), "MAN", _M, 17.5)
Z("M-13", "13 Control de espesor", R(36.8, 38.0, 43.8, 40.5), "MAN", _M + "; W-MAN 12: PU-S y 2 PU-RT", 2.3)
Z("M-14", "14 Prueba hidráulica (2 bancos)", R(36.8, 33.5, 43.8, 38.0), "MAN", _M + "; W-MAN 13: 2 PU-6", 14.1)
Z("M-15", "15 Secado (4 secadoras)", R(36.8, Y_CN, 43.8, 33.5), "MAN", _M + "; W-MAN 14: 2 PU-7", 6.0)
# granallado, detección y cuelgue arriba de la prueba hidráulica y el secado (pedido del usuario: «el granallado y la
# detección van arriba; la pintura a la derecha, vertical, alineada con el granallado»). W-MAN 16: «a continuación de los
# rodillos de salida está la mesa de inspección»; la corrección (otro puesto de X-MAN, 1 turno) queda debajo, con las jaulas
Z("M-16", "16 Granallado", R(45.3, 38.0, 52.5, Y_M), "MAN", _M + "; W-MAN, granallado: carros de entrada, ciclón y bolsones", 27.4)
Z("M-17", "17 Detección de defectos (a la salida de la granalladora)", R(52.5, 36.0, 57.3, Y_M), "MAN",
  _M + "; W-MAN, detección: mesa de inspección iluminada a continuación de los rodillos de salida", 9.2)
Z("M-17C", "18 Corrección de defectos (amolado con extracción) y jaulas", R(52.5, 30.2, 57.3, 36.0), "MAN",
  "W-MAN, detección y corrección: tres jaulas identificadas al lado del puesto, carro de corregibles, extracción localizada en el "
  "amolado; X-MAN 2035: corrección en 1 turno")
Z("M-18", "19 Cuelgue en el transportador de la pintura", R(58.8, 35.5, X_PINT, Y_M), "MAN",
  "W-MAN, detección y pintura: los aprobados llegan en carros y se cuelgan en el transportador; ganchos por formato, tapones-gancho, "
  "pintura en polvo y aspiradora")

E("M12-1", "Soldadora circunferencial Firesafer FS-SWH", R(37.3, 43.3, 39.3, 44.7), "M-12", "sold_circ", "S", 1,
  _T + " (criterio)")
E("M12-2", "Soldadora circunferencial Firesafer FS-SWH", R(40.6, 43.3, 42.6, 44.7), "M-12", "sold_circ", "S", 1,
  _T + " (criterio)")
E("M12-3", "Mampara entre las dos soldadoras circunferenciales", R(39.92, 42.9, 40.0, 44.9), "M-12", "pantalla", "O", 0,
  "W-MAN, soldadura circunferencial: «extracción de humos y mamparas»")
E("M12-4", "Extracción de humos (soldadora 1)", R(39.35, 44.3, 39.85, 44.8), "M-12", "colector10", "S", 0, "W-MAN: «extracción de humos» (folleto Nederman); medida: criterio")
E("M12-5", "Extracción de humos (soldadora 2)", R(42.75, 44.3, 43.25, 44.8), "M-12", "colector10", "S", 0, "W-MAN: «extracción de humos» (folleto Nederman); medida: criterio")
E("M12-6", "Estante: boroscopio industrial, spray antisalpicaduras, cepillos y repuestos de antorcha",
  R(42.75, 43.2, 43.7, 43.6), "M-12", "estanteria", "S", 0, "W-MAN, soldadura circunferencial: equipos y herramientas")
E("M13-1", "Medidor de espesor por ultrasonido Melisam MR017 sobre mesa", R(38.3, 39.7, 39.5, 40.3), "M-13",
  "mesa_control", "S", 1, "Mesa 1,2 × 0,6 (W-CAR 1)")
carros_fila("PU-S", "«Espesor OK» -> prueba hidráulica (2,5 a 10 kg)", 39.7, 39.6, 1, "M-13", fuente="W-MAN 11 y 12")
carros_fila("PU-S1", "Cilindros de 1 kg acostados en cajones -> prueba hidráulica", 36.85, 38.05, 1, "M-13", CAJ,
            fuente="W-MAN 11: 28 por cajón, 336 por carro de 12 cajones")
carros_fila("PU-RT", "Retenidos del control de espesor", 41.4, 38.8, 2, "M-13", vertical=True, fuente="W-MAN 12")
E("M14-1", "Banco de prueba hidráulica Firesafer FS-JD12A", R(37.2, 36.6, 39.25, 37.7), "M-14", "ph", "S", 1,
  "Catálogo Firesafer, pág. 11: 2050 × 1100 × 1350 mm")
E("M14-2", "Banco de prueba hidráulica Firesafer FS-JD12A", R(40.4, 36.6, 42.45, 37.7), "M-14", "ph", "S", 1,
  "Catálogo Firesafer, pág. 11: 2050 × 1100 × 1350 mm")
carros_fila("PU-6", "Probados (mojados) -> secado", 37.4, 33.7, 2, "M-14", fuente="W-MAN 13")
E("M14-3", "Cámara de decantación y separador de aceites (compartidos con pérdidas)", R(42.4, 33.7, 43.6, 34.5),
  "M-14", "pozo", "S", 0, "W-MAN 13")
E("M14-4", "Cajón de rechazos identificado (reparación o scrap)", R(42.6, 36.75, 43.2, 37.15), "M-14", "rechazo",
  "S", 0, "W-MAN 13: «los rechazados van al cajón identificado»; cajón de 600 × 400 mm (W-MAN 2)")
for i in range(4):
    E(f"M15-{i + 1}", "Secadora de cilindros Yukon", Rw(37.2 + i * 1.0, 31.8, 0.70, 0.68), "M-15", "secadora", "S",
      1 if i % 2 == 0 else 0, "ET: 700 × 680 × 1750 mm")
carros_fila("PU-7", "Secos con tapón -> granallado", 41.6, 29.2, 2, "M-15", vertical=True, fuente="W-MAN 14")
# ---- 16 granallado (W-MAN 15): los carros del secado esperan frenados al lado de la boca de entrada (primero el que
# llegó primero); el polvo del extractor va al ciclón y a los filtros de cartucho (memoria descriptiva Airblast G-100)
E("M16-1", "Granalladora de rodillos Airblast G-100 (rodillos de entrada y salida incluidos)", R(47.0, 40.9, 51.5, 42.2),
  "M-16", "granalladora", "N", 1, "Cotización Airblast: 4500 × 1300 × 2200 mm")
carros_fila("PU-GE", "Secos con tapón esperando la granalladora (frenados, primero el que llegó primero)", 45.35, 42.45,
            1, "M-16", fuente="W-MAN, granallado: «los carros quedan al lado de la boca de entrada, con las ruedas frenadas»")
carros_fila("PU-GE2", "Secos con tapón: segundo carro de entrada", 45.35, 39.7, 1, "M-16",
            fuente="W-MAN, granallado: «se consume primero el que llegó primero»")
E("M16-2", "Ciclón y filtros de cartucho del extractor, con pulmón de sopleteo (parte de la G-100)",
  R(48.0, 43.3, 49.4, 44.7), "M-16", "colector10", "S", 0,
  "Memoria Airblast G-100: extractor centrífugo, ciclón y cartuchos lavables; medida y lugar: criterio")
E("M16-3", "Bolsones del polvo del ciclón y bolsas de granalla S330/S390 del día (≈ 133 kg)", R(49.8, 43.5, 51.0, 44.5),
  "M-16", "pallets_q", "S", 0, "W-MAN, granallado: granalla 0,08 kg por cilindro y bolsones para el polvo del ciclón")
E("M16-4", "Tablero de mando automático de la granalladora", R(46.4, 43.9, 47.4, 44.3), "M-16", "tablero_herr", "S", 0,
  "Memoria Airblast G-100: tablero de mando automático y tablero eléctrico")
E("M16-5", "Caja de tapones-gancho de silicona M22 y M30 (se verifican antes de entrar)", R(45.4, 41.2, 46.0, 41.6),
  "M-16", "rechazo", "N", 0, "W-MAN, granallado: «antes de apoyarlo, verifica que el tapón esté bien puesto»")
# ---- 17 detección (W-MAN 16): a continuación de los rodillos de salida; los aprobados van a la pintura en carros
E("M17-1", "Mesa de inspección iluminada con comparador visual Sa 2½, junto al ramal del transportador",
  R(52.6, 41.0, 53.8, 41.6), "M-17", "inspeccion", "N", 1, "W-MAN, detección; mesa 1,2 × 0,6 (W-CAR 1)")
carros_fila("PU-G", "Carro móvil: aprobados -> cuelgue (en llenado)", 54.0, 41.0, 1, "M-17",
            fuente="W-MAN, detección: «los aprobados son llevados hacia la pintura en los carros correspondientes»")
carros_fila("PU-G3", "Carro móvil: aprobados lleno, esperando el cruce al cuelgue", 55.6, 39.6, 1, "M-17",
            fuente="W-MAN, detección (carros móviles)")
E("M17-2", "Estante de machos de roscar y calibres pasa/no pasa M22 y M30, planilla de defectos",
  R(56.6, 37.0, 57.1, 38.5), "M-17", "estanteria", "O", 0, "W-MAN, detección y corrección: equipos y herramientas")
# ---- 18 corrección (W-MAN 17): las tres jaulas al lado del puesto; los corregidos vuelven a la granalladora
for i, nom in enumerate(("«a corregir»", "«a re-granallar»", "«descarte» (inutilizados, a scrap)")):
    E(f"M17-J{i + 1}", "Jaula " + nom, Rw(52.7 + i * 1.15, 34.8, 1.0, 1.0), "M-17C", "jaula", "N", 0,
      "W-MAN, detección: «hay tres jaulas identificadas al lado del puesto»")
E("M18-1", "Mesa de corrección con amoladora angular de 115 mm (disco flap)", R(53.0, 32.4, 54.2, 33.0), "M-17C",
  "banco_sold", "S", 1, "W-MAN, corrección; mesa 1,2 × 0,6")
E("M18-2", "Extracción localizada del amolado (brazo y filtro)", R(54.4, 32.3, 55.2, 33.1), "M-17C", "colector10", "S",
  0, "W-MAN, corrección: «extracción localizada en la zona de amolado»; medida: criterio")
carros_fila("PU-CO", "Carro de corregibles", 55.7, 32.45, 1, "M-17C", fuente="W-MAN, detección: carro para los corregibles")
E("M18-3", "Estante del medidor de espesores (control después de amolar)", R(56.7, 33.4, 57.2, 34.6), "M-17C",
  "estanteria", "O", 0, "W-MAN, detección: «si se amoló, control de espesor contra el plano»")
# ---- 19 cuelgue (W-MAN 18 y 19)
E("M19-C", "Puesto de cuelgue en el transportador (ganchos por formato y tapones)", R(64.6, 40.4, 65.9, 42.6), "M-18",
  "banco", "O", 1, "W-MAN, pintura: «colgar cada cilindro en un gancho del transportador, verificando el tapón»")
carros_fila("PU-G2", "Carro móvil de aprobados en el cuelgue", 62.2, 40.8, 1, "M-18", fuente="W-MAN 18 (carros móviles)")
carros_fila("PU-G4", "Carro móvil de aprobados en espera", 62.2, 39.6, 1, "M-18", fuente="W-MAN 18 (carros móviles)")
E("M19-G", "Estantería de ganchos por formato y tapones de silicona", R(59.0, 37.0, 59.6, 40.0), "M-18",
  "estanteria", "E", 0, "W-MAN 15 y 18: tapones-gancho y ganchos por formato")
E("M19-T", "Cajas de tapones-gancho de silicona que vuelven de la descarga (≈ 1.665 en circulación)",
  R(59.0, 40.3, 59.6, 41.5), "M-18", "cajones", "E", 0, "W-MAN, granallado: «unos 1.665 en circulación en el pico»")
E("M19-P", "Pallet de pintura en polvo poliéster roja 03-1-050 del turno (cajas)", R(59.1, 41.8, 60.3, 42.8), "M-18",
  "pallets_q", "E", 0, "W-MAN, pintura: entra la pintura en polvo; pallet 1200 × 1000 (X-ALM)")
E("M19-A", "Aspiradora industrial de la cabina", R(59.2, 36.0, 59.8, 36.6), "M-18", "rechazo", "N", 0,
  "W-MAN, pintura: equipos y herramientas")

# ================================================================ ALA NORESTE DE CARROS: la prueba hidráulica de carros al lado
# de la de manuales y el secado de carros al lado del de manuales (pedido del usuario: «según el Word la prueba hidráulica
# y el secado van juntos; que se combinen con lo que corresponde»). W-CAR 10: el secado «está pegado a la prueba
# hidráulica y lo atiende el mismo operario». Los carros llegan del 8 por el paso C-89, salen secos al pulmón 11 y el
# camión de la pintura (P3) se carga y se descarga con las dos tarimas de la recepción de pintados (W-CAR 11 y 12).
Z("C-09", "9 Prueba hidráulica de carros (al lado de la de manuales)", R(45.3, 33.5, 51.3, 38.0), "CAR",
  _W + " 9: ≈ 5,5 × 4,0 m", 22)
Z("C-10", "10 Secado de carros (al lado del de manuales)", R(45.3, Y_CN, 51.3, 33.5), "CAR",
  _W + " 10: ≈ 3,0 × 2,5 m, «pegado a la prueba hidráulica»; zona de no conforme de los dos puestos", 7.5)
Z("C-89", "Paso de los carros del 8 a la prueba hidráulica y de los secos al pulmón 11", R(51.3, Y_A2, 52.5, 38.0),
  "CAR", "W-CAR 8, 9 y 10: los carros ruedan sobre su juego provisorio, empujados de la manija")
Z("C-12C", "12 Recepción de pintados: 2 tarimas del camión, cambio de juego y rechazados del pintor",
  R(52.5, Y_A2, 57.3, 24.2), "CAR", "W-CAR 12: 2 lugares de cambio de juego de 2,0 × 1,5 m y rechazados ≈ 2 × 1,5 m; "
  "«la descarga usa la tarima y el pasillo del puesto 11» (W-CAR 11: 2 tarimas)")
_n12 = LUGARES["12 Pulmón de pintados"]
Z("C-12", "12 Pulmón de pintados (%d carros), enfrente del puesto 13" % _n12, R(52.5, 24.2, 57.3, Y_CN), "CAR",
  "W-CAR 12: filas por modelo y lote, al lado del puesto 13 (cruzando el pasillo); %d carros a 0,5 m²" % _n12,
  0.5 * _n12)
Z("C-1011", "Paso de los carros secos al pulmón 11", R(52.5, Y_CN, 57.3, 30.2), "CAR",
  "W-CAR 10 y 11: los trae rodando el operario de prueba hidráulica")
_n11 = LUGARES["11 Pulmón de despacho a la pintura"]
Z("C-11", "11 Pulmón de despacho a la pintura tercerizada (%d carros)" % _n11, R(58.8, 25.0, X_PINT, 35.5), "CAR",
  "Dato del usuario: %d carros por semana en el pico, 2 envíos; W-CAR 11: filas por modelo y envío demarcadas en "
  "amarillo, 0,5 m² por carro" % _n11, 0.5 * _n11)
# 9 prueba hidráulica (W-CAR 9): los dos puestos en el centro, la pantalla entre los puestos y el operario, la máquina
# detrás de la pantalla, el tanque en el rincón del fondo, la canaleta tapada con rejilla a lo largo de los puestos y la
# planilla del lado del secado. El carro entra rodando desde el paso C-89 y baja al secado.
E("C9-1", "Puesto de prueba 1: bandeja con rejilla y rampa", R(49.0, 34.6, 50.2, 35.8), "C-09", "bandeja", "E", 0,
  "W-CAR 9: 1,2 × 1,2 m")
E("C9-2", "Puesto de prueba 2: bandeja con rejilla y rampa", R(49.0, 36.1, 50.2, 37.3), "C-09", "bandeja", "E", 0,
  "W-CAR 9: 1,2 × 1,2 m, 0,3 m entre los dos")
E("C9-3", "Canaleta tapada con rejilla", R(50.25, 34.6, 50.45, 37.3), "C-09", "canaleta", "E", 0,
  "W-CAR 9: 2,7 × 0,2 m")
E("C9-4", "Pozo de dos cámaras con canasto de malla y bomba sumergible SAP 400", R(50.2, 37.4, 50.7, 37.75), "C-09",
  "pozo", "S", 0, "W-CAR 9: 0,5 × 0,35 m")
E("C9-5", "Pantalla rebatible de policarbonato", R(48.75, 34.45, 48.87, 37.45), "C-09", "pantalla", "O", 0,
  "W-CAR 9: 3,0 m")
E("C9-6", "Máquina de prueba Yukon M-000200 sobre su mesa (con unidad de filtro, regulador y lubricador)",
  R(47.35, 35.45, 47.75, 36.5), "C-09", "ph", "E", 1, "W-CAR 9: 1,05 × 0,40 m")
E("C9-7", "Tanque de 1.000 L con cesto filtro", R(45.4, 36.35, 46.96, 37.91), "C-09", "tanque", "S", 0,
  "W-CAR 9: Ø 1,56 m, en el rincón del fondo")
E("C9-8", "Bomba periférica con filtro Y y de cartucho", R(45.45, 35.55, 46.2, 36.0), "C-09", "bomba", "S", 0,
  "W-CAR 9: 0,75 × 0,45 m, al lado del tanque")
E("C9-9", "Planilla, manómetros patrón y tablero de los cabezales de vaciado", R(46.4, 33.6, 47.35, 34.15), "C-09",
  "planilla", "N", 0, "W-CAR 9: 0,95 × 0,55 m, del lado del secado")
# 10 secado
E("C9-10", "Zona de no conforme de la prueba hidráulica y del secado (roja), sobre sus ruedas",
  R(45.5, 29.2, 46.7, 30.2), "C-10", "nc", "N", 0, "W-CAR 9 y 10: los rechazados van a la zona de no conforme")
E("C10-1", "Espera de carros mojados (2 carros)", R(49.9, 32.25, 51.1, 33.25), "C-10", "rodantes", "S", 0,
  "W-CAR 10: 1,2 × 1,0 m, entre la prueba y la secadora", n=2, grid=(2, 1), dem="AM")
E("C10-2", "Secadora Melisam MR011", R(48.8, 32.6, 49.4, 33.1), "C-10", "secadora", "S", 0,
  "W-CAR 10: ≈ 0,6 × 0,5 m, al lado de la prueba hidráulica")
E("C10-3", "Lugar del carro que se seca", R(48.5, 31.3, 49.7, 32.3), "C-10", "lugar", "N", 0,
  "W-CAR 10: 1,2 × 1,0 m, frente a la secadora")
E("C10-4", "Estante de cinta y planilla", R(45.35, 31.2, 45.75, 32.0), "C-10", "estanteria", "E", 0,
  "W-CAR 10: 0,8 × 0,4 m")
# 11 pulmón de despacho: filas por modelo y envío, la manija hacia el pasillo PO-N2 (por ahí van a las tarimas)
filas_carros("C11-1", "Pulmón de despacho: 6 filas de 8 carros por modelo y envío (%d)" % _n11,
             R(59.0, 25.6, 64.12, 34.9), "C-11", 8, 6, "AM",
             "Dato del usuario: %d carros; W-CAR 11: filas por modelo y semana (acá, por envío)" % _n11, n=_n11)
E("C11-2", "Estante de fajas con criquet, cartones separadores y rampa enganchable", R(64.6, 25.2, 65.9, 25.7),
  "C-11", "estanteria", "N", 0, "W-CAR 11: fajas de amarre (unas 15), cartones separadores y rampa")
E("C11-3", "Tablero de lotes aprobados, carteles de lote y remitos", R(64.9, 34.7, 65.9, 35.3), "C-11", "planilla",
  "S", 0, "W-CAR 11: «el responsable de calidad lo indica en la planilla y en el cartel de la fila»")
# 12 recepción de pintados: las dos tarimas del camión (descarga de pintados y carga de secos), dos lugares de cambio de
# juego y los rechazados del pintor
E("C12-T", "Tarima de descarga de pintados (el autoelevador la trae desde P3)", R(52.6, 20.05, 53.8, 21.05), "C-12C",
  "tarima", "N", 0, "W-CAR 12: «la descarga usa la tarima y el pasillo del puesto 11»", ae=True)
E("C11-T", "Tarima de carga de secos con topes y rampa (el autoelevador la lleva a P3)", R(53.95, 20.05, 55.15, 21.05),
  "C-12C", "tarima", "N", 0, "W-CAR 11: tarimas de carga con topes (2), 1,2 × 1,0 m", ae=True)
E("C12-2", "Lugar de cambio de juego 1: crique, zorra de retorno y cajones de ejes y ruedas",
  R(55.25, 20.05, 57.25, 21.55), "C-12C", "cambio_juego", "N", 1, "W-CAR 12: 2,0 × 1,5 m, al lado del camión")
E("C12-3", "Lugar de cambio de juego 2", R(55.25, 22.6, 57.25, 24.1), "C-12C", "cambio_juego", "O", 1,
  "W-CAR 12: 2,0 × 1,5 m")
E("C12-4", "Rechazados del pintor (rojo)", R(52.6, 22.2, 54.25, 24.1), "C-12C", "nc", "E", 0, "W-CAR 12: ≈ 2 × 1,5 m")
filas_carros("C12-1", "Pulmón de pintados: 4 filas de 7 carros por modelo y lote (%d)" % _n12,
             R(52.65, 24.35, 57.15, 28.85), "C-12", 7, 4, "AM", "W-CAR 12 con la demanda 2035: %d carros" % _n12, n=_n12)

# ================================================================ PINTURA (66 a 76, 20 a 47) Y SU DESCARGA
Z("M-19", "19 Pintura en polvo + horno (línea Firesafer)", R(X_PINT, Y_A2, LX, LY), "PINT",
  "ET: 25000 × 8000 × 4000 mm; W-MAN, pintura, y X-MAN 19; franja de servicio de 1 m", 270)
E("M19-1", "Línea de recubrimiento en polvo Firesafer (transportador, precalentamiento, cabina, horno, enfriamiento)",
  R(67.0, 21.0, 75.0, 46.0), "M-19", "horno", "O", 0, "ET: 25 × 8 × 4 m; W-MAN, pintura")
# W-MAN 19 (salida): al final de la línea el operario de descarga descuelga; los terminados siguen con el tapón de
# silicona a la carga y a los cilindros vacíos se les cambia por el de polietileno y van al embalaje. W-MAN 25: «los
# cilindros vacíos se encajonan al lado de la descarga de la pintura» (el embalaje queda enfrente, cruzando el pasillo)
Z("M-19D", "19 Descarga de la pintura: terminados a la carga y cilindros vacíos al embalaje", R(58.8, Y_A2, X_PINT, 25.0),
  "PINT", "W-MAN, pintura (salida): descuelgue, cambio de tapón de los vacíos y control de película")
E("M19-D", "Puesto de descarga del transportador (descuelgue)", R(64.5, 21.3, 65.9, 23.7), "M-19D", "banco", "O", 1,
  "W-MAN, pintura: «el operario de descarga los descuelga del gancho»")
E("M19-D2", "Mesa de cambio de tapón: silicona -> polietileno (cilindros vacíos)", R(59.9, 23.8, 61.1, 24.4), "M-19D",
  "banco", "S", 1, "W-MAN, pintura: «se les cambia el tapón de silicona por el tapón de polietileno»")
E("M19-D3", "Mesa de control: medidor de espesor de película, adherencia y registro de temperatura del horno",
  R(61.4, 23.8, 62.6, 24.4), "M-19D", "mesa_control", "S", 1, "W-MAN, pintura: controles por muestreo y registro")
E("M19-D4", "Caja de tapones de silicona recuperados (vuelven al secado)", R(59.0, 21.6, 59.6, 22.0), "M-19D",
  "rechazo", "N", 0, "W-MAN, granallado: tapones-gancho en circulación")
carros_fila("PU-D1", "Terminados pintados con tapón -> carga (cruzan el pasillo principal)", 61.9, 20.15, 1, "M-19D",
            fuente="W-MAN, pintura: «van a la carga de polvo en los carros correspondientes»")
carros_fila("PU-D2", "Cilindros vacíos con tapón de PE -> embalaje", 60.5, 20.15, 1, "M-19D", (0.61, 1.28),
            fuente="W-MAN, pintura: «se llevan directo a la sección de embalaje»")
carros_fila("PU-D3", "Cilindros vacíos de 1 kg en cajones -> embalaje", 59.0, 20.15, 1, "M-19D", CAJ,
            fuente="W-MAN 11: el 1 kg va en cajones, carro de 12 cajones")

# ================================================================ BANDA SUR ESTE: terminación compartida y PT unificado
# Pedido del usuario: debajo de la pintura (cruzando el pasillo principal) va toda la terminación compartida (carga,
# presurización y el armado final de manuales y de carros) y debajo de la terminación, contra el muro sur, el depósito de
# PT unificado de manuales y carros. Al este del pasillo PT-MA (3,0 m, un sentido) la terminación de manuales va de 6,15
# a 13,5 y el PT de manuales de 0 a 6,15: dos racks enfrentados sobre el pasillo de 3,6 m del autoelevador eléctrico
# (1,1 + 3,6 + 1,1 m; pedido del usuario: pasillos de despacho más angostos).
Y_T = 7.95
_L = LUGARES
_n = _L["14 Sala de pérdidas"]
Z("C-17", "17 Ensayos de lote (recinto de descarga, balanza y mesa)", R(24.7, Y_T, 40.25, Y_S), "CAR",
  _W + " 17: ≈ 15,5 × 4,5 m, al lado de la sala de pérdidas (el patio de rodadura va afuera, por P5)", 70)
Z("C-1314", "Paso de la carga a la sala de pérdidas, a los ensayos y al etiquetado", R(40.25, Y_T, 44.25, 9.5), "CAR",
  "W-CAR 13, 14, 15 y 17: recorrido de los carros de la muestra")
Z("C-14", "14 Sala del ensayo de pérdidas (paneles aislantes, split)", R(40.25, 9.5, 44.25, Y_S), "CAR",
  "W-CAR 14: 25 m² para 30 lugares; con los %d de 2035, a la misma relación" % _n, 25.0 * _n / 30, tipo="local")
Z("C-13", "13 Carga, armado y presurización de carros", R(44.25, Y_T, 56.55, Y_S), "TERM", _W + " 13: ≈ 10 × 6 m", 60)
Z("C-13P", "Paso de los carros pintados y de los cilindros a la carga y al depósito 16", R(56.55, Y_T, 57.75, Y_S),
  "TERM", "W-CAR 12 y 13: los pintados cruzan el pasillo principal desde el pulmón 12")
Z("M-20", "20 a 25 Terminación de manuales: carga, ensamblaje, presurización, pérdidas, etiquetado y embalaje",
  R(60.75, 6.15, LX, Y_S), "TERM", _M + " (Guerchet de los puestos 20 a 25: 42,4 m² + 6 carros pulmón); W-MAN 25: "
  "embalaje compartido de terminados y cilindros vacíos (armadora, cajas y envolvedora); pulmón del 2.º turno", 47.0)
Z("RV-S", "Libre (reserva de ampliación del PT y de los ensayos)", R(24.7, 0, 38.25, Y_T), "LIB",
  "Lo que queda de la nave de 76 m con la demanda 2035 (la nave podría acortarse un vano de 7,6 m)")
Z("C-17P", "17 Paso de la muestra al patio de ensayos (P5)", R(38.25, 0, 40.25, Y_T), "CAR",
  "W-CAR 17: la rodadura (1 km, caída de 20 cm y choque) se hace afuera")
Z("C-15", "15 Etiquetado e inspección final", R(40.25, 3.95, 44.25, Y_T), "CAR", _W + " 15: ≈ 3,5 × 2,5 m", 9)
Z("C-16X", "16 Rechazados (rojo) y revisión al 100 %", R(40.25, 0, 44.25, 3.95), "PT",
  "W-CAR 16: rechazados, %d carros a 0,5 m²" % _L["16 Rechazados (rojo)"], 0.5 * _L["16 Rechazados (rojo)"])
Z("C-16", "16 Depósito de PT de carros: retenidos (amarillo), liberados (verde) y despacho por P2", R(44.25, 0, 57.75, Y_T),
  "PT", _W + " 16: 0,5 m² por carro y los pasillos; %d retenidos y %d liberados (demanda 2035)"
  % (_L["16 Retenidos (amarillo)"], _L["16 Liberados (verde)"]), 0.5 * (_L["16 Retenidos (amarillo)"] +
                                                                     _L["16 Liberados (verde)"]))
Z("PT-MA", "Depósito de PT unificado: pasillo del autoelevador (del pasillo principal a los racks)",
  R(57.75, 0, 60.75, Y_S), "CIRC", _PASO, tipo="pasillo", sub="AE")
_PTM = ("W-MAN 25: rack de PT y de cilindros en el mismo almacén, el autoelevador ubica el pallet en altura o lo carga "
        "directo al camión (P4); %d pallets (semana %d + diciembre %d) + %d de revendidos (X-ALM) en %d posiciones"
        % (PT_MAN["total"], PT_MAN["semana"], PT_MAN["diciembre"], PT_MAN["reventa"], PT_MAN["posiciones"]))
Z("PT-M", "Depósito de PT unificado: rack de manuales contra el muro sur", R(60.75, 0, LX, 1.35), "PT", _PTM)
Z("PT-MA2", "Depósito de PT unificado: pasillo de los racks (a P4)", R(60.75, 1.35, LX, 4.95), "CIRC", _AE15,
  tipo="pasillo", sub="AE")
Z("PT-M2", "Depósito de PT unificado: rack de manuales y entrega de la envolvedora", R(60.75, 4.95, LX, 6.15), "PT",
  _PTM)

# 13 carga, armado y presurización: A del lado del pulmón de pintados (este), C del lado del etiquetado (oeste)
E("C13-1", "Estación A: lugar del carro (cinta y control del interior)", R(53.9, 9.3, 56.3, 11.5), "C-13", "lugar",
  "N", 1, "W-CAR 13: 2,4 × 2,2 m, del lado del pulmón de pintados")
E("C13-2", "Estación B: balanza de 300 kg con rampa y cargadora por vacío Yukon M-000121", R(49.9, 9.0, 52.9, 11.6),
  "C-13", "carga_polvo", "S", 1, "W-CAR 13: 3,0 × 2,6 m")
E("C13-3", "Bastidor de descarga del big bag con tolva (alto 2,8 m)", R(50.6, 12.2, 52.2, 13.4), "C-13", "bastidor",
  "N", 0, "W-CAR 13: 1,6 × 1,2 m, con acceso para el autoelevador", ae=True)
E("C13-4", "Estación C: lugar del carro (manga, traba, precinto y tarjeta)", R(45.3, 9.3, 47.6, 11.5), "C-13",
  "lugar", "N", 1, "W-CAR 13: 2,3 × 2,2 m, del lado del etiquetado")
E("C13-5", "Batería de nitrógeno (11 tubos de 50 L) en jaula, con manifold", R(44.4, 12.55, 47.0, 13.45), "C-13",
  "bateria_gas", "N", 0, "W-CAR 13: 2,6 × 0,9 m")
E("C13-6", "Colector de polvo de 3 HP (aspiración localizada en la boca)", R(52.5, 12.4, 53.3, 13.2), "C-13",
  "colector10", "N", 0, "W-CAR 13: equipos y herramientas")
E("C13-7", "Estanterías de válvulas, mangas, ruedas y ejes, con cajones (1 y 2)", R(47.2, 12.95, 50.2, 13.45), "C-13",
  "estanteria", "S", 0, "W-CAR 13: 3 × (2,0 × 0,5 m)")
E("C13-8", "Estantería de válvulas, mangas, ruedas y ejes, con cajones (3)", R(53.4, 12.95, 56.4, 13.45), "C-13",
  "estanteria", "S", 0, "W-CAR 13: 3 × (2,0 × 0,5 m)")
# 14 sala de pérdidas: 3 filas numeradas con el manómetro hacia un pasillo; la puerta da al paso de la carga
pares("C14-1", "Muestra: lugares 1 a 6", R(40.4, 12.7, 44.1, 13.4), "C-14", 6, 1, "AM",
      "W-CAR 14 con la muestra de 2035: %d lugares de 0,5 m²" % _n, frente="N")
pares("C14-2", "Muestra: lugares 7 a %d" % _n, R(40.4, 10.4, 44.1, 11.8), "C-14", 6, 2, "AM",
      "W-CAR 14 con la muestra de 2035: %d lugares de 0,5 m²" % _n, n=_n - 6)
E("C14-3", "Split frío/calor BGH 3000F y registrador", R(40.3, 11.85, 40.55, 12.65), "C-14", "split", "E", 0,
  "W-CAR 14: en la pared")
# 15 etiquetado: entran del paso de la carga por el norte y salen al depósito 16 por el este
E("C15-1", "Lugares de los 2 carros que se etiquetan", R(42.0, 6.0, 44.0, 6.8), "C-15", "lugar", "S", 1,
  "W-CAR 15: 2 × (1,0 × 0,8 m)")
E("C15-2", "Mesa con calcomanías, plantillas y alcohol", R(40.45, 7.15, 41.65, 7.75), "C-15", "etiquetadora", "S", 0,
  "W-CAR 15: 1,2 × 0,6 m")
E("C15-3", "Zona de no conforme (roja)", R(40.45, 4.15, 41.95, 5.15), "C-15", "nc", "N", 0, "W-CAR 15: 1,5 × 1,0 m")
# 16 depósito de PT de carros: filas norte-sur; entran por el paso del norte y salen por el sur al pasillo de P2
_n = _L["16 Retenidos (amarillo)"]
filas_carros("C16-R", "Retenidos: 8 filas de 8 carros (%d)" % _n, R(44.35, 1.7, 49.95, 6.8), "C-16", 8, 8, "AM",
             "W-CAR 16 con lotes de media semana: %d carros" % _n, frente="E", n=_n)
_n = _L["16 Liberados (verde)"]
filas_carros("C16-L", "Liberados: 9 filas de 8 carros (%d)" % _n, R(50.05, 1.7, 56.35, 6.8), "C-16", 8, 9, "VE",
             "W-CAR 16 con la demanda 2035: una semana, %d carros" % _n, frente="E", n=_n)
E("C16-X", "Zona de rechazados (roja): %d carros" % _L["16 Rechazados (rojo)"], R(40.35, 0.25, 43.35, 2.65), "C-16X",
  "nc", "N", 0, "W-CAR 16: el lote de media semana de 50 kg de 2035 a 0,5 m²")
E("C16-1", "Tarjetas de RETENIDO, LIBERADO y RECHAZADO, carteles de lote, fajas, film y bolsas (estante)",
  R(56.45, 5.2, 56.95, 6.8), "C-16", "estanteria", "O", 0, "W-CAR 16: equipos y herramientas")
# 17 ensayos de lote
E("C17-1", "Colector de polvo con filtro de mangas (fondo del recinto)", R(24.9, 10.2, 25.9, 11.2), "C-17",
  "colector10", "E", 0, "W-CAR 17: ≈ 1,0 × 1,0 m")
E("C17-2", "Recinto de descarga cerrado (alto 3 m), piso marcado cada 0,5 m y ventana", R(25.9, 9.2, 36.9, 12.2),
  "C-17", "recinto", "N", 0, "W-CAR 17: 12 × 3 m con el colector")
E("C17-3", "Balanza de plataforma con rampa (en la puerta del recinto)", R(37.3, 9.4, 38.5, 10.6), "C-17", "balanza",
  "N", 0, "W-CAR 17: 1,2 × 1,2 m, del lado de la sala de pérdidas")
E("C17-4", "Mesa de medición, perchero de mangas y planillas", R(38.0, 12.4, 40.0, 13.2), "C-17", "banco", "S", 1,
  "W-CAR 17: 2,0 × 0,8 m, al lado de la sala de pérdidas")
# 20 a 25 terminación de manuales. Al oeste, frente a la descarga de la pintura (cruzando el pasillo principal), el
# embalaje compartido de terminados y cilindros vacíos (W-MAN 25: «los cilindros vacíos se encajonan al lado de la
# descarga de la pintura y los terminados al final del transportador de terminación, en la misma zona, así comparten la
# armadora, el stock de cajas y la envolvedora»), con la envolvedora en el rincón SO sobre la entrega del rack B. Al este,
# la U: carga, ensamblaje y presurización por la fila norte (la estación de big bag contra el pasillo principal, para el
# autoelevador) y pérdidas y etiquetado por la fila sur, de vuelta hacia el embalaje.
# Pulmón del 2.º turno (X-MAN 2035: pintura en 2 turnos; carga, presurización, etiquetado y embalaje en 1): lo pintado en el
# 2.º turno espera al día siguiente. Pico: 1.665 cilindros por día = unas 12,5 cargas de carro (W-MAN: 336 de 1 kg por
# carro de 12 cajones; 80 de 2,5 kg, 48 de 5 kg o 36 de 10 kg por FCHP20505) -> la mitad, 6 carros.
carros_fila("PU-TP", "Terminados pintados -> carga", 66.1, 12.8, 1, "M-20", fuente="W-MAN 19")
carros_fila("PU-T2", "Pulmón del 2.º turno: terminados pintados esperando la carga", 66.1, 10.6, 2, "M-20",
            fuente="X-MAN 2035 (pintura 2 turnos, carga 1) y W-MAN (capacidad de los carros)")
carros_fila("PU-V2T", "Pulmón del 2.º turno: cilindros vacíos esperando el embalaje", 62.6, 11.5, 2, "M-20",
            fuente="X-MAN 2035 (pintura 2 turnos, embalaje 1) y W-MAN (capacidad de los carros)")
carros_fila("PU-V3T", "Pulmón del 2.º turno: cilindros vacíos de 1 kg en cajones", 62.6, 10.3, 2, "M-20", CAJ,
            fuente="X-MAN 2035 y W-MAN 11 (336 cilindros de 1 kg por carro de 12 cajones)")
E("M20-1", "Estación de big bag ABC 60 (bastidor, polipasto y transporte por vacío a la cargadora)",
  R(67.6, 11.95, 69.1, 13.45), "M-20", "tanque", "S", 0, "W-MAN, carga de polvo: estación de descarga de big bag; medida: criterio",
  ae=True)
E("M20-3", "Extracción localizada de polvo de la carga", R(69.2, 12.65, 70.0, 13.45), "M-20", "colector10", "S", 0,
  "W-MAN, carga de polvo: «extracción localizada de polvo»; medida: criterio")
E("M20-2", "Cargadora por vacío Yukon M-000121", R(70.1, 12.9, 70.72, 13.41), "M-20", "carga_polvo", "S", 1,
  "Ficha Yukon: 620 × 510 × 1200 mm")
E("M20-4", "Balanza de verificación de 50 g con pesas patrón, picos y conos M22 y M30, caja de retorno de tapones",
  R(70.9, 12.85, 72.1, 13.45), "M-20", "mesa_control", "S", 1, "W-MAN, carga de polvo: equipos y herramientas; mesa 1,2 × 0,6")
carros_fila("PU-F1", "Carga -> ensamblaje", 72.25, 12.8, 1, "M-20", fuente="W-MAN, carga y ensamblaje")
E("M21-1", "Mesa de ensamblaje con llave dinamométrica, soporte del cilindro y grasa de silicona",
  R(73.6, 12.85, 74.8, 13.45), "M-20", "ensamble", "S", 1, "W-MAN 21; mesa 1,2 × 0,6")
E("M21-2", "Estante de cajones: válvulas, manómetros, sifones y o-rings", R(74.9, 12.75, 75.95, 13.25), "M-20",
  "cajonera", "S", 0, "W-MAN 21: «estante de cajones de cada puesto, al alcance de la mano»; medida: criterio")
carros_fila("PU-F2", "Ensamblaje -> presurización", 75.3, 10.85, 1, "M-20", (0.61, 1.28), fuente="W-MAN 21 y 22")
E("M22-1", "Pinza Yukon M-000150 sobre mesa (N₂ por cañería desde la jaula exterior, regulador con alivio)",
  R(75.35, 9.2, 75.95, 10.4), "M-20", "presurizacion", "O", 1, "W-MAN 22; mesa 1,2 × 0,6")
carros_fila("PU-F3", "Presurización -> pérdidas", 72.9, 8.65, 1, "M-20", fuente="W-MAN 22 y 23")
E("M23-1", "Tanque de inmersión inoxidable Firesafer FS-SS100 (iluminación, estante sumergido, temporizador)",
  R(73.9, 6.3, 75.7, 7.3), "M-20", "hermeticidad", "N", 1, "Catálogo Filling Line, pág. 44: 1000 × 1800 × 900 mm")
E("M23-2", "Cajón de rechazos con tarjeta roja (punto de la pérdida anotado)", R(73.2, 6.35, 73.8, 6.75), "M-20",
  "rechazo", "N", 0, "W-MAN 23: «al cajón identificado con tarjeta roja al lado del tanque»; cajón de 600 × 400 mm")
carros_fila("PU-F4", "Pérdidas -> etiquetado", 71.7, 6.35, 1, "M-20", fuente="W-MAN 23 y 24")
E("M24-1", "Dispensador de etiquetas, posicionador por formato y Zebra ZD421 sobre mesa", R(70.3, 6.35, 71.5, 6.95),
  "M-20", "etiquetadora", "N", 1, "W-MAN 24; mesa 1,2 × 0,6")
E("M24-2", "Estante del puesto: etiquetas preimpresas por formato, rollos de la impresora y paños",
  R(69.6, 6.3, 70.2, 7.2), "M-20", "cajonera", "N", 0, "W-MAN 24: «los deja en el estante del puesto»; medida: criterio")
carros_fila("PU-F5", "Etiquetado -> embalaje", 68.2, 6.35, 1, "M-20", fuente="W-MAN 24 y 25")
E("M25-1", "Mesa de encajonado (terminados)", R(63.6, 7.85, 64.8, 8.45), "M-20", "palletizado", "N", 1,
  "X-MAN: 2 puestos; mesa 1,2 × 0,6")
E("M25-2", "Mesa de encajonado (cilindros vacíos, con protocolo de ensayo)", R(64.9, 7.85, 66.1, 8.45), "M-20",
  "palletizado", "N", 1, "X-MAN: 2 puestos; mesa 1,2 × 0,6; W-MAN 25")
E("M25-3", "Armadora automática de cajas (regulada para la caja del 1 kg)", R(63.6, 6.25, 65.62, 7.67), "M-20",
  "palletizado", "N", 0, "Sin cotizar; referencia FS-DDP50: 2020 × 1420 mm")
E("M25-4", "Envolvedora EDOS PS5 (pallet listo para el autoelevador, sobre la entrega del rack B)",
  R(60.85, 6.25, 63.4, 7.75), "M-20", "envolvedora", "N", 0, "Plano de cotas EDOS 26880: 2550 × 1500 mm", ae=True)
E("M25-5", "Pila de pallets vacíos 1200 × 1000 (junto a la envolvedora)", R(60.85, 7.95, 62.05, 8.95), "M-20",
  "pallets_q", "S", 0, "W-MAN 25")
E("M25-8", "Pallet en armado sobre el piso, al lado de las mesas", R(62.2, 7.95, 63.4, 8.95), "M-20", "pallets_q", "S",
  0, "W-MAN 25: «apilar las cajas sobre el pallet según el plano de armado»")
E("M25-6", "Pallet de cajas plegadas (al lado de la armadora)", R(65.8, 6.25, 67.0, 7.18), "M-20", "pallets_q",
  "N", 0, "W-MAN 25: las cajas llegan plegadas en pallets desde el almacén")
E("M25-7", "Lugar de las transpaletas eléctrica y manual (demarcado)", R(60.85, 9.7, 62.35, 11.3), "M-20",
  "transpaleta", "S", 0, "W-MAN 25: transpaleta eléctrica y transpaleta manual de respaldo; 0,7 × 1,6 m cada una "
  "(criterio)")
E("M25-9", "Estante de film, etiquetas de caja y de pallet, protocolos y cúter", R(66.4, 8.1, 67.6, 8.6), "M-20",
  "estanteria", "N", 0, "W-MAN 25: materiales de embalaje que trae el operario de almacén")
# demarcaciones de seguridad que no son equipos: rejilla de goteo del tanque (W-MAN 23: «piso antideslizante con
# rejilla alrededor del tanque») y zona delimitada de la armadora y la envolvedora (W-MAN 25: «zona delimitada alrededor
# del plato giratorio y de la armadora, con parada de emergencia»)
REJILLAS = [R(73.8, 6.2, 75.85, 7.4)]
DELIMITADAS = [R(60.8, 6.18, 65.67, 7.72)]
# PT de manuales: rack A contra el muro sur (5 módulos) y rack B enfrentado (4 módulos); el tramo sin rack del rack B, al
# oeste, es la entrega de la envolvedora y la entrada desde el pasillo PT-MA
_RK = "%d módulos de 2,65 m × %d niveles × 2 pallets = %d posiciones"
E("PTM-1", "Rack de PT de manuales: terminados y revendidos (" + _RK % (PT_MAN["modulos"], PT_MAN["niveles"],
  2 * PT_MAN["modulos"] * PT_MAN["niveles"]) + ")", R(60.75, 0.25, 74.0, 1.35), "PT-M", "rack", "N", 0, _PTM, ae=True)
E("PTM-2", "Rack de PT de manuales: cilindros vacíos (" + _RK % (PT_MAN["modulos_b"], PT_MAN["niveles"],
  2 * PT_MAN["modulos_b"] * PT_MAN["niveles"]) + ")", R(65.4, 5.05, 76.0, 6.15), "PT-M2", "rack", "S", 0, _PTM,
  ae=True)

# ================================================================ PUERTAS DE LOS LOCALES DENTRO DE LA NAVE
# (x, y, ancho, muro 'h' o 'v', abre +1/-1); el ancho mayor a 2 m es una cortina enrollable
PUERTAS_LOCALES = [
    (5.0, 3.8, 1.0, "v", 1),          # compresores -> mantenimiento
    (1.4, 8.4, 0.9, "h", -1),         # tablero general -> senda sur
    (8.0, 8.4, 1.6, "h", -1),         # mantenimiento (doble hoja) -> senda sur
    (13.6, 8.4, 1.0, "h", -1),        # pañol -> senda sur
    (18.0, 8.4, 0.9, "h", -1),        # calidad -> senda sur
    (13.1, Y_S, 5.2, "h", 1),         # depósito de polvo: cortina frente a las 5 pilas, al pasillo principal
    (41.6, 9.5, 0.9, "h", -1),        # sala de pérdidas (pasillo sur) -> paso de la carga
]

# ================================================================ ADMINISTRACIÓN Y SERVICIOS AL PERSONAL (anexo norte)
# Copia del plano del usuario «Área administrativa y de servicios al personal» (calle al norte, planta al sur, 23,6 × 14,3 m
# ≈ 337 m²), medido sobre la imagen con su escala gráfica (60,8 px por metro). Fila norte: sala de reuniones, hall, pasillo
# de emergencia a la calle, administración, RRHH y vestíbulo de personal; pasillo único de 1,60 m; fila sur: gerencia y
# sala técnica, baño accesible, baño de mujeres y de varones de oficinas, acceso al comedor, sanitarios y vestuario de
# mujeres, comedor, sanitarios y vestuario de varones y el paso de personal a la planta. Las medidas de abajo se escriben
# como en el plano: x desde el muro oeste y d desde el muro norte (la calle).
# Dotación 2035 sin recargas (X-DT): turno mañana 36 personas (32 H y 4 M). Higiene y Seguridad y medicina laboral son
# servicios externos (X-DT, Notas M29): el plano no tiene enfermería, oficina de HyS ni pañol de EPP.
XA0 = 35.5                                      # el paso de personal da al pasillo PO-N2 y la sala técnica al PO-N1
XA1 = XA0 + 23.6
YA0, YA1 = LY + MURO, LY + MURO + 14.3
Y_PC0, Y_PC1 = YA1 - 6.1, YA1 - 4.5             # pasillo único de 1,60 m
Y_PL0, Y_PL1 = YA1 - 9.42, YA1 - 9.16           # plenum sanitario
ADMIN = []                                      # locales del anexo (misma clase Zona)
MOB = []                                        # muebles: (tipo de planta/mobiliario.py, R, frente, n)


def A(cod, nombre, r, fuente="", req=0.0, cat="ADM"):
    ADMIN.append(Zona(cod, nombre, r, cat, fuente, req, "local"))


def MB(tipo, r, frente="S", n=1):
    MOB.append((tipo, r, frente, n))


def Rd(x0, d0, x1, d1):
    """Rectángulo del plano del usuario: x desde el muro oeste del anexo, d desde el muro norte."""
    return R(XA0 + x0, YA1 - d1, XA0 + x1, YA1 - d0)


_CR = "Plano del usuario (área administrativa 23,6 × 14,3 m)"
_DT = "X-DT hoja Servicios y Oficinas, 2035 sin recargas"
A("AD-SR", "Sala de reuniones (12 personas)", Rd(0.0, 0.0, 5.4, 4.5), _CR + ": 5,4 × 4,5 = 24,3 m²")
A("AD-HA", "Hall de recepción", Rd(5.4, 0.0, 10.4, 4.5), _CR + ": 5,0 × 4,5 = 22,5 m²", cat="CIRC")
A("AD-PE", "Pasillo de emergencia (1,50 m) a la calle", Rd(10.4, 0.0, 11.9, 4.5), _CR, cat="CIRC")
A("AD-AD", "Administración", Rd(11.9, 0.0, 16.9, 4.5), _CR + ": 5,0 × 4,5 = 22,5 m²; " + _DT)
A("AD-RH", "RRHH (legajos y ventanilla)", Rd(16.9, 0.0, 20.0, 4.5), _CR + ": 3,1 × 4,5 = 14,0 m²")
A("AD-VE", "Vestíbulo de personal (reloj y cartelera de HyS)", Rd(20.0, 0.0, 23.6, 4.5),
  _CR + ": 3,6 × 4,5 = 16,2 m²; ingreso de operarios lateral este", cat="CIRC")
A("AD-PC", "Pasillo único (1,60 m)", Rd(0.0, 4.5, 21.6, 6.1), _CR, cat="CIRC")
A("AD-PP", "Paso de personal a la planta", Rd(21.6, 4.5, 23.6, 14.3), _CR, cat="CIRC")
A("AD-GE", "Gerencia", Rd(0.0, 6.1, 4.2, 9.3), _CR + ": 4,2 × 3,2 = 13,4 m²")
A("AD-ST", "Sala técnica / supervisión (3 personas)", Rd(0.0, 9.3, 4.2, 14.3),
  _CR + ": 4,2 × 5,0 = 21,0 m², vidrio a la planta; se entra por la gerencia y por la puerta a la planta")
A("AD-BA", "Baño para personas con discapacidad", Rd(4.2, 6.1, 7.6, 9.16), _CR + "; Ley 24.314", cat="SAN")
A("AD-BM", "Baño de mujeres (oficinas)", Rd(7.6, 6.1, 9.6, 9.16), _CR, cat="SAN")
A("AD-AC", "Acceso al comedor", Rd(9.6, 6.1, 11.4, 9.42), _CR, cat="CIRC")
A("AD-BH", "Baño de varones (oficinas)", Rd(11.4, 6.1, 14.05, 9.16), _CR, cat="SAN")
A("AD-SM", "Sanitarios de mujeres", Rd(14.05, 6.1, 16.4, 9.16), _CR + ": parte del vestuario de mujeres (7,6 × 3,05 m)",
  cat="SAN")
A("AD-VM", "Vestuario de mujeres (18 lockers)", Rd(16.4, 6.1, 21.6, 9.16),
  _CR + ": 7,6 × 3,05 = 23,2 m² con los sanitarios, 18 lockers (6 módulos × 3 niveles); " + _DT + ": 4 mujeres",
  cat="SAN")
A("AD-PL1", "Plenum sanitario", Rd(4.2, 9.16, 9.6, 9.42), _CR + ": plenum único", cat="SAN")
A("AD-PL2", "Plenum sanitario", Rd(11.4, 9.16, 21.6, 9.42), _CR + ": plenum único", cat="SAN")
A("AD-CO", "Comedor (24 lugares, 2 tandas) con office", Rd(4.2, 9.42, 12.2, 14.3),
  _CR + ": 8,0 × 4,9 = 39,2 m², 24 lugares; " + _DT + ": 18 plazas")
A("AD-SH", "Sanitarios de varones (2 inodoros, 4 mingitorios, 3 lavatorios)", Rd(12.2, 9.42, 16.6, 14.3),
  _CR + ": parte del vestuario de varones (9,4 × 4,9 m)", cat="SAN")
A("AD-VH", "Vestuario de varones (42 lockers)", Rd(16.6, 9.42, 21.6, 14.3),
  _CR + ": 9,4 × 4,9 = 46,1 m² con los sanitarios, 42 lockers (14 módulos × 3 niveles); " + _DT + ": 32 varones",
  cat="SAN")


def Pd(x, d):
    return (XA0 + x, YA1 - d)


# puertas del anexo: (x, y, ancho, muro 'h' o 'v', hacia dónde abre +1/-1); medidas del plano del usuario
PUERTAS_ADMIN = [
    (XA0 + 1.0, YA1 - 4.5, 0.85, "h", 1),       # sala de reuniones <- pasillo
    (XA0 + 5.4, YA1 - 4.47, 0.95, "v", 1),      # sala de reuniones -> hall
    (XA0 + 8.55, YA1 - 4.5, 0.85, "h", 1),      # hall <- pasillo
    (XA0 + 12.0, YA1 - 4.5, 0.9, "h", 1),       # administración
    (XA0 + 17.1, YA1 - 4.5, 0.8, "h", 1),       # RRHH
    (XA0 + 3.3, YA1 - 6.1, 0.85, "h", -1),      # gerencia
    (XA0 + 3.25, YA1 - 9.3, 0.85, "h", -1),     # sala técnica (desde la gerencia, como en el plano)
    (XA0 + 7.75, YA1 - 6.1, 0.8, "h", -1),      # baño de mujeres de oficinas
    (XA0 + 9.75, YA1 - 9.42, 0.85, "h", -1),    # acceso -> comedor
    (XA0 + 11.45, YA1 - 6.1, 0.85, "h", -1),    # baño de varones de oficinas
    (XA0 + 16.4, YA1 - 7.1, 0.8, "v", 1),       # sanitarios de mujeres -> vestuario
    (XA0 + 21.6, YA1 - 7.88, 0.82, "v", -1),    # vestuario de mujeres <- paso de personal
    (XA0 + 16.6, YA1 - 13.3, 0.8, "v", -1),     # vestuario de varones -> sanitarios
    (XA0 + 21.6, YA1 - 13.32, 0.85, "v", -1),   # vestuario de varones <- paso de personal
]
# puerta corrediza del baño accesible (hoja que corre dentro del muro): (x, y, ancho, muro)
CORREDIZAS_ADMIN = [(XA0 + 5.6, YA1 - 6.1, 0.9, "h")]
# lados abiertos entre locales de circulación (sin tabique): (x, y, largo, muro)
ABIERTOS_ADMIN = [(XA0 + 10.4, YA1 - 4.5, 1.5, "h"), (XA0 + 20.0, YA1 - 4.5, 3.6, "h"), (XA0 + 9.6, YA1 - 6.1, 1.8, "h"),
                  (XA0 + 21.6, YA1 - 6.1, 1.6, "v")]
# puertas exteriores del anexo: (código, muro, a, b, uso); a y b en x (muro N) o en y (muros E y O). Abren hacia afuera.
PUERTAS_EXT_ADMIN = [("H1", "N", XA0 + 7.1, XA0 + 8.7, "Acceso de visitas, gerencia y oficinas (rampa y plataforma)"),
                     ("H2", "N", XA0 + 10.5, XA0 + 11.35, "Salida de emergencia del pasillo de emergencia"),
                     ("H3", "E", YA1 - 1.93, YA1 - 1.03, "Ingreso de operarios (lateral este, rampa accesible)"),
                     ("H4", "O", YA1 - 5.97, YA1 - 4.73, "Ingreso de supervisión y salida (oeste, rampa)"),
                     ("H5", "E", YA1 - 12.13, YA1 - 11.26, "Salida de emergencia del paso de personal")]
VENTANAS_ADMIN = [((XA0 + 0.94, YA0), (XA0 + 4.1, YA0))]        # vidrio de la sala técnica a la planta

# mobiliario (planta/mobiliario.py), como en el plano
MB("mesa", Rd(1.0, 1.15, 4.4, 3.07), "S", 10)                       # sala de reuniones: 5 + 5 y una en cada punta
MB("sillas", Rd(0.4, 1.85, 0.9, 2.35), "O", 1)
MB("sillas", Rd(4.5, 1.85, 5.0, 2.35), "E", 1)
MB("pizarra", Rd(0.05, 1.3, 0.2, 2.8), "E")
MB("estanteria", Rd(5.5, 0.63, 5.92, 3.23), "E")                    # exhibición
MB("sillas", Rd(6.2, 0.55, 6.63, 2.94), "O", 5)                     # espera
MB("mostrador", Rd(8.39, 1.62, 10.29, 2.85), "N")                   # recepción con tramo bajo de 0,80 m
for k in range(3):                                                  # administración
    MB("escritorio", Rd(12.1 + k * 1.5, 0.98, 13.35 + k * 1.5, 2.3), "S")
MB("archivo", Rd(16.4, 1.93, 16.84, 3.53), "O", 3)
MB("escritorio", Rd(17.3, 1.47, 18.8, 2.7), "S")                    # RRHH
MB("sillas", Rd(17.45, 0.7, 18.65, 1.2), "N", 2)
MB("archivo", Rd(19.5, 0.12, 19.95, 2.0), "O", 3)                   # legajos
MB("ventanilla", Rd(19.75, 2.87, 20.0, 3.7), "E")
MB("pizarra", Rd(20.02, 0.37, 20.17, 2.26), "E")                    # cartelera de HyS
MB("reloj", Rd(23.3, 2.45, 23.55, 3.15), "O")                       # reloj del vestíbulo
MB("reloj", Rd(0.6, 4.52, 0.95, 4.72), "S")                         # reloj del pasillo (supervisión)
MB("archivo", Rd(0.08, 6.47, 0.5, 7.77), "E", 2)                    # gerencia
MB("escritorio", Rd(1.34, 7.36, 2.86, 8.65), "S")
MB("sillas", Rd(1.6, 6.75, 2.6, 7.25), "N", 2)
MB("archivo", Rd(0.08, 10.72, 0.5, 12.02), "E", 2)                  # sala técnica
MB("escritorio", Rd(0.76, 10.4, 2.0, 11.61), "N")
MB("escritorio", Rd(2.4, 10.4, 3.65, 11.61), "N")
MB("escritorio", Rd(1.4, 12.2, 2.8, 13.42), "N")
MB("ducha_acc", Rd(4.3, 8.2, 5.2, 9.1), "N")                        # baño accesible
MB("lavabos", Rd(5.4, 8.65, 6.1, 9.12), "N", 1)
MB("inodoro_acc", Rd(6.3, 6.45, 7.55, 9.12), "N")
MB("lavabos", Rd(7.7, 8.65, 8.3, 9.12), "N", 1)                     # baño de mujeres de oficinas
MB("inodoro", Rd(8.75, 7.6, 9.55, 9.12), "N")
MB("lavabos", Rd(11.55, 8.7, 12.05, 9.12), "N", 1)                  # baño de varones de oficinas
MB("mingitorios", Rd(12.2, 8.75, 12.7, 9.12), "N", 1)
MB("inodoro", Rd(13.0, 7.77, 14.05, 9.12), "N")
MB("lavabos", Rd(14.3, 6.15, 15.45, 6.55), "S", 2)                  # sanitarios de mujeres
MB("inodoro", Rd(14.05, 7.86, 15.96, 9.12), "N", 2)
MB("lockers", Rd(16.5, 7.68, 17.0, 9.03), "E", 3)                   # vestuario de mujeres: 6 módulos × 3 niveles
MB("lockers", Rd(18.9, 7.68, 19.4, 9.03), "O", 3)
MB("banco_vest", Rd(17.74, 7.78, 18.15, 8.92), "E")
MB("duchas", Rd(19.65, 8.16, 21.55, 9.1), "N", 2)
MB("mesada", Rd(4.6, 9.49, 8.6, 10.0), "S", 2)                      # office del comedor
MB("lavabos", Rd(10.98, 9.45, 12.1, 9.8), "S", 2)                   # lavamanos
for xx in (4.3, 6.71, 9.11):                                         # 3 mesas de 8 = 24 lugares
    MB("mesa", Rd(xx, 10.8, xx + 1.9, 13.55), "E", 8)
MB("inodoro", Rd(12.2, 9.42, 14.09, 10.85), "S", 2)                 # sanitarios de varones
MB("mingitorios", Rd(14.3, 9.45, 16.45, 9.86), "S", 4)
MB("lavabos", Rd(12.84, 13.94, 14.65, 14.28), "N", 3)
MB("duchas", Rd(17.7, 9.45, 21.3, 10.36), "S", 4)                   # vestuario de varones: 14 módulos × 3 niveles
MB("lockers", Rd(16.9, 11.37, 20.06, 11.87), "S", 7)
MB("lockers", Rd(16.9, 13.76, 20.06, 14.26), "N", 7)
MB("banco_vest", Rd(17.3, 12.6, 19.67, 13.0), "S")

# marcas del plano que no son muebles: matafuegos del pasillo único y rótulos del equipamiento
MATAFUEGOS_ADMIN = [Pd(3.0, 5.9), Pd(17.0, 5.9)]                    # los dos puntos rojos del pasillo
ROTULOS_ADMIN = [   # (texto, (x, y), giro)
    ("Reloj", Pd(0.78, 4.95), 0), ("Reloj", Pd(23.05, 2.8), 90), ("Cartelera HyS", Pd(20.4, 1.3), 90),
    ("Ventanilla", Pd(19.45, 3.3), 90), ("Legajos", Pd(19.2, 1.05), 90), ("Exhibición", Pd(5.71, 0.35), 0),
    ("Tramo bajo 0,80 m", Pd(9.3, 1.35), 0), ("Vidrio a la planta", Pd(2.5, 14.65), 0),
    ("Office: bacha, anafe, micro, heladera", Pd(6.6, 10.25), 0), ("Lavamanos", Pd(11.55, 10.05), 0),
    ("Puerta corrediza", Pd(6.05, 6.45), 0),
]
# baranda de la senda norte con cruces frente a cada puerta a la planta (plano del usuario) y aberturas en los pasillos
# de operarios que llegan a la senda
CRUCES_N = [(XA0 - 0.1, XA0 + 1.2), (XA0 + 11.0, XA0 + 12.3), (XA0 + 21.7, XA0 + 23.5)]
ABERTURAS_N = CRUCES_N + [(43.8, 45.3)]
# circuitos del personal (marcas del plano del usuario y su lámina de circulación): (n, qué, color, puntos)
_V = (Y_PC0 + Y_PC1) / 2
CIRCUITOS = [
    (1, "Llegada del operario: ingreso lateral este -> reloj -> paso de personal -> vestuario", (192, 57, 43),
     [(XA1 + 1.4, YA1 - 1.5), (XA0 + 22.6, YA1 - 1.5), (XA0 + 22.6, YA1 - 12.9), (XA0 + 20.6, YA1 - 12.9)]),
    (2, "Vestuario -> planta por el paso de personal", (230, 126, 34),
     [(XA0 + 20.6, YA1 - 13.6), (XA0 + 22.3, YA1 - 13.6), (XA0 + 22.3, LY - 1.0)]),
    (3, "Baño durante el turno: planta -> paso de personal -> vestuario -> sanitarios", (142, 68, 173),
     [(XA0 + 23.0, LY - 1.0), (XA0 + 23.0, YA1 - 12.5), (XA0 + 17.3, YA1 - 12.5), (XA0 + 15.0, YA1 - 12.9)]),
    (4, "Almuerzo: planta -> cruce -> puerta del comedor -> lavamanos -> mesa", (22, 160, 133),
     [(XA0 + 11.6, LY - 1.0), (XA0 + 11.6, YA1 - 10.2), (XA0 + 8.0, YA1 - 10.4)]),
    (5, "Llegada de supervisión: ingreso oeste -> reloj -> gerencia -> sala técnica", (46, 134, 193),
     [(XA0 - 1.6, _V), (XA0 + 3.7, _V), (XA0 + 3.7, YA1 - 10.0)]),
    (6, "Supervisores -> planta (puerta directa y cruce)", (31, 78, 121),
     [(XA0 + 2.0, YA1 - 12.9), (XA0 + 0.45, YA1 - 13.6), (XA0 + 0.45, LY - 1.0)]),
    (7, "Visitas, gerencia y oficinas: plataforma -> hall -> recepción -> sala de reuniones", (44, 62, 80),
     [(XA0 + 7.9, YA1 + 1.2), (XA0 + 7.9, YA1 - 3.2), (XA0 + 6.6, YA1 - 3.9), (XA0 + 4.4, YA1 - 3.9)]),
    (8, "Oficinas -> planta (ocasional): pasillo único -> paso de personal", (127, 140, 141),
     [(XA0 + 14.4, YA1 - 3.0), (XA0 + 14.4, _V), (XA0 + 22.0, _V), (XA0 + 22.0, LY - 1.0)]),
    (9, "Evacuación de la fila norte y del centro: pasillo único -> pasillo de emergencia -> calle", (30, 132, 73),
     [(XA0 + 5.0, _V - 0.3), (XA0 + 11.15, _V - 0.3), (XA0 + 11.15, YA1 + 1.2)]),
    (10, "Evacuación de la sala técnica y la gerencia: pasillo único -> salida oeste", (39, 174, 96),
     [(XA0 + 3.0, _V + 0.3), (XA0 - 1.6, _V + 0.3)]),
    (11, "Evacuación de los vestuarios: paso de personal -> salida este (H5)", (17, 120, 60),
     [(XA0 + 22.9, YA1 - 9.5), (XA0 + 22.9, YA1 - 11.7), (XA1 + 1.4, YA1 - 11.7)]),
]

# ================================================================ PUERTAS DE LA NAVE
PUERTAS += [
    Puerta("P1", "O", Y_AE - 5.2, Y_AE - 0.2, 4.5, "porton", "Materia prima: del playón oeste al pasillo principal"),
    Puerta("P2", "S", 53.5, 57.0, 4.5, "porton",
           "Despacho de carros: furgón Renault Master L3H2 y rampa TRAN-IN-240"),
    Puerta("P3", "E", Y_AE - 5.2, Y_AE - 0.2, 4.5, "porton",
           "Camión de la pintura: carros secos (11) y pintados (12)"),
    Puerta("P4", "E", 1.35, 4.95, 4.5, "porton", "Despacho de PT de manuales (pasillo de los racks de 3,6 m)"),
    Puerta("P5", "S", 38.55, 39.75, 2.1, "peatonal", "Patio de ensayos de lote (17): la muestra sale a la rodadura"),
    Puerta("P7", "N", 9.5, 13.5, 4.5, "porton",
           "Scrap: del pasillo AL-A a la playa con volquete"),
    Puerta("PE-1", "O", 8.6, 9.7, 2.1, "emergencia", "Salida del ángulo SO (extremo de la senda de los locales)"),
    Puerta("PE-3", "N", 3.0, 4.2, 2.1, "emergencia", "Salida del almacén (extremo norte del pasillo AL-B)"),
    Puerta("PE-4", "S", 32.0, 33.2, 2.1, "emergencia", "Salida de la banda sur (reserva y ensayos de lote)"),
    Puerta("PN-1", "N", XA0 + 0.05, XA0 + 0.85, 2.1, "peatonal", "Sala técnica: puerta directa a la planta"),
    Puerta("PN-2", "N", XA0 + 11.2, XA0 + 12.05, 2.1, "peatonal", "Comedor (almuerzo: cruce, lavamanos, comedor)"),
    Puerta("PN-3", "N", XA0 + 21.9, XA0 + 23.4, 2.1, "peatonal", "Paso de personal a la planta (doble hoja)"),
]

# ancho de los portones: croquis de circuitos de carros del usuario (portón O 5 m, E1 y E2 5 m, S despacho 4 m);
# alto de 4,5 m: criterio (camión con caja de hasta 4,1 m, Ley 24.449 art. 53)
PORTON_CORTO = {"P1": "Materia prima", "P2": "Despacho de carros (furgón y rampa)", "P3": "Camión de la pintura",
                "P4": "Despacho de PT de manuales", "P7": "Scrap (volquete)"}

# ================================================================ EXTERIOR (calle al norte)
EXTERIOR = [
    ("CALLE", "Calle (frente norte)", R(-27.0, 71.5, 104.0, 77.0)),
    ("VE", "Vereda", R(-27.0, 69.0, 104.0, 71.5)),
    ("EST", "Estacionamiento de visitas y personal", R(XA0 - 1.8, 63.6, XA1 + 1.8, 69.0)),
    ("CJ", "Cajón reservado 3,50 × 5,00 m", R(XA0 + 0.6, 63.6, XA0 + 4.1, 68.6)),
    ("RA1", "Rampa accesible norte", R(XA0 + 3.1, YA1, XA0 + 6.5, YA1 + 1.55)),
    ("PLA", "Plataforma a nivel", R(XA0 + 6.5, YA1, XA0 + 11.9, YA1 + 1.55)),
    ("RA2", "Rampa accesible oeste", R(XA0 - 1.75, YA1 - 4.12, XA0, YA1 - 0.62)),
    ("DE2", "Descanso", R(XA0 - 1.75, YA1 - 6.65, XA0, YA1 - 4.12)),
    ("RA3", "Rampa accesible este", R(XA1, YA1 - 0.95, XA1 + 1.8, YA1 + 2.47)),
    ("DE3", "Descanso", R(XA1, YA1 - 3.41, XA1 + 1.8, YA1 - 0.95)),
    ("PO", "Playón oeste: descarga de MP y maniobra", R(-22.0, 6.0, -0.2, 26.0)),
    ("PS", "Playa sur: despacho de carros (P2, furgón con rampa), patio de ensayos y gases",
     R(-22.0, -22.0, 98.0, -0.2)),
    ("PE", "Playa este: camión de la pintura (P3) y despacho de PT de manuales (P4)", R(LX + 0.2, 0.0, 98.0, 26.0)),
    ("PEN", "Patio de ensayos de lote: circuito de remolque (W-CAR 17)", R(26.0, -12.0, 38.0, -2.0)),
    ("PEN1", "Plataforma de caída 20 cm", R(28.0, -4.5, 29.5, -3.0)),
    ("PEN2", "Pared 60 cm", R(28.0, -7.0, 30.0, -6.7)),
    ("JG", "Jaula de gases ventilada (Arcal 21 y N₂ en packs con manifold)", R(68.0, -4.2, 75.0, -1.2)),
    ("PSC", "Playa de scrap (P7): volquete del chatarrero", R(4.0, 48.5, 14.0, 56.0)),
]
# despacho de PT de carros por P2 (plano de carros del usuario, rev 6): rampa portátil TRAN-IN-240 (2,4 m útiles, 820 mm
# de ancho, 23 % ≈ 13°, 350 kg, sin obra civil) y furgón Renault Master L3H2 de culo (2,07 × 6,2 m, ≈ 13 carros por
# viaje, 6 viajes por semana; carga: 2 operarios, descarga: el chofer); volquete de 5 m³ del chatarrero (2 × 3 m)
DESPACHO_CARROS = {"rampa": R(54.84, -2.4, 55.66, 0.0), "furgon": R(54.215, -8.6, 56.285, -2.4),
                   "volquete": R(7.5, 52.6, 10.5, 54.6)}
FUENTE_DESPACHO = "Plano de carros del usuario (rev 6): rampa TRAN-IN-240 y furgón Renault Master L3H2"
CAMINO_CAMIONES = [(-23.0, 69.0), (-23.0, -18.0), (99.0, -18.0), (99.0, 69.0)]
# rampas: hacia dónde apunta la flecha del croquis (al extremo que llega al nivel del terreno)
RAMPAS = {"RA1": "O", "RA2": "N", "RA3": "N"}
NOTA_RAMPA = "Pendiente ≤ 8 %, ancho libre 1,50 m, pasamanos doble a 0,75 y 0,90 m, solado antideslizante"
# franja de descarga del playón (W-CAR 1 tabla 5: 15 × 5 m, línea discontinua, frente al portón de MP)
FRANJA_DESCARGA = R(-5.2, 8.3, -0.2, 23.3)
# predio: cerco perimetral sobre la línea municipal y portones (anchos: criterio, rotulados)
PREDIO = R(-26.6, -22.3, 103.6, 69.0)
SENDAS_EXT = [R(XA0 + 1.6, YA1, XA0 + 3.1, 63.6), R(XA0 - 1.75, YA1 - 0.62, XA0, 63.6),
              R(XA1, YA1 + 2.47, XA1 + 1.8, 63.6)]
PORTONES_PREDIO = [   # (código, x desde, x hasta, uso) sobre el cerco norte
    ("PC-1", -26.5, -19.5, "Entrada de camiones, 7,0 m (criterio: semirremolque)"),
    ("PC-2", 95.5, 102.5, "Salida de camiones, 7,0 m (circuito de una mano)"),
    ("PC-3", XA0 + 9.0, XA0 + 14.5, "Estacionamiento, 5,5 m"),
    ("PC-4", XA0 + 1.6, XA0 + 3.1, "Peatonal: visitas, gerencia y oficinas"),
    ("PC-5", XA1, XA1 + 1.8, "Peatonal: operarios (ingreso lateral este)"),
    ("PC-6", XA0 - 1.75, XA0, "Peatonal: supervisión (ingreso oeste)"),
]


# ================================================================ CORTES DE LA NAVE (lámina FL_PI10_06)
# A-A: longitudinal por y = 5,6 (banda sur: locales, reserva, etiquetado, depósito 16 y rack B de PT), mira al norte.
# B-B: transversal por x = 38,4 (paso de la muestra, ensayos de lote, pasillo principal, carros 6/7, columna este de
# manuales, senda norte y anexo), mira al oeste (el norte queda a la derecha del dibujo).
# C-C: longitudinal por y = 37,65 (almacén, manuales fila B, prueba hidráulica de manuales y de carros, detección,
# cuelgue y pintura).
# D-D: transversal por x = 68,3 (racks de PT, terminación, pasillo principal y línea de pintura), mira al oeste.
# (B-B corta el anexo por la sala de reuniones, el pasillo único y la sala técnica.)
CORTES = {"A": ("y", 5.6, "N"), "B": ("x", 38.4, "O"), "C": ("y", 37.65, "N"), "D": ("x", 68.3, "O")}
ALTO_LOCAL = (3.2, "Locales de servicio de 3,20 m (tabla de áreas v10; Dec. 351/79 cap. 5: 3 m como mínimo)")
ALTURAS = {   # código o código con * o tipo de símbolo: (alto en m, fuente)
    "M4-3": (2.79, "ET Sangiacomo T 63R: 2790 mm"), "M3-2": (1.2, "Cotización Leapion: 1200 mm"),
    "M8-1": (1.25, "Catálogo Firesafer FS-RM01: 1250 mm"), "M9-1": (1.6, "ET Getweld ZF-500 (referencia): 1600 mm"),
    "M7-1": (1.58, "Catálogo Firesafer FS-HFM1: 1580 mm"), "M10-1": (1.8, "ET Del Fabro: 1800 mm"),
    "M11-1": (1.28, "Presupuesto Pilman SWM-400: 1280 mm"), "M14-*": (1.35, "Catálogo Firesafer FS-JD12A: 1350 mm"),
    "M15-*": (1.75, "ET secadora Yukon: 1750 mm"), "M16-1": (2.2, "Cotización Airblast G-100: 2200 mm"),
    "M19-1": (4.0, "ET línea Firesafer: 25 × 8 × 4 m"), "M20-2": (1.2, "Ficha Yukon M-000121: 1200 mm"),
    "M23-1": (0.9, "Catálogo Filling Line FS-SS100: 900 mm"), "C17-2": (3.0, "W-CAR 17: recinto de 3 m de alto"),
    "C13-3": (2.8, "W-CAR 13: bastidor de 2,8 m"), "RC-*": (3.0, "W-CAR 1 tabla 5: racks de carros de ≈ 3 m"),
    "R1-*": (6.0, "Criterio: la carga de arriba llega a la elevación máxima del Heli CPCD50, 6 m (W-CAR 1)"),
    "PTM-*": (6.0, "Criterio: 5 niveles hasta la elevación máxima del Heli CPCD50, 6 m (W-CAR 1)"),
    "PQ-*": (2.4, "W-CAR 1: big bag de 1,2 m de alto, apilado de a 2"),
    "filas": (1.16, "Hoja de especificaciones «Polvos carros»: carro de 50 kg, 1160 mm (25 kg 1085; 100 kg 1360)"),
    "rodantes": (1.16, "Hoja de especificaciones «Polvos carros»: carro de 50 kg, 1160 mm"),
    "lugar": (1.16, "Hoja de especificaciones «Polvos carros»: carro de 50 kg, 1160 mm"),
    "banco": (0.86, "W-CAR 1: mesa de trabajo metálica de unos 86 cm de alto"),
    "mesa_control": (0.86, "W-CAR 1: mesa de 86 cm"), "inspeccion": (0.86, "W-CAR 1: mesa de 86 cm"),
}
