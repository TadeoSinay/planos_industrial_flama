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
  tercerizada (P3 salida y P6 regreso). Los lugares de carros rodantes salen de la demanda pico 2035 (X-CAR).
* Mantenimiento, calidad, compresores y espacio libre en el ángulo SO.

Fuentes (las mismas de la tabla Dimensionamiento_de_areas_v10.xlsx)
-------------------------------------------------------------------
W-MAN  Proceso de manuales (Word).          X-MAN  Dimensionamiento Manuales (máquina y cantidad 2035).
W-CAR  Proceso de carros (Word, v10).       X-CAR  Dimensionamiento Carros.
X-ALM  Dimensionamiento Almacenes MP v5.    X-DT   Dimensionamiento_TecnicoV2 (dotación, servicios, PT).
ET     ET´s Máquinas.                       Presupuestos y catálogos de la carpeta INVESTIGACION PROVEEDORES.
"""

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


# ================================================================ bandas
Y_S = 13.5          # banda sur: almacén complementario, servicios, carros 11 a 17, PT
Y_AE = 18.5         # carril del autoelevador del pasillo principal (13,5 a 18,5)
Y_A2 = 20.0         # senda peatonal del pasillo principal (18,5 a 20,0)
Y_CN = 29.0         # fila de fabricación de carros (20,0 a 29,0)
Y_M = 45.0          # manuales (29,0 a 45,0)
X_AL = 15.4         # ancho del almacén de MP (oeste)
X_PINT = 66.0       # pintura (66 a 76, de 20 a 47)

_AE = "Heli CPCD50 (W-MAN y W-CAR): radio de giro 2,93 m + pallet 1,2 m + 0,8 m de margen = 5,0 m (W-CAR, tabla 5)"

# ================================================================ DEMANDA PICO 2035 (para dimensionar los lugares de carros)
# X-CAR (Dimensionamiento Carros), hoja «Plan mensual», año 2035: el mes pico (marzo a mayo, julio y agosto) tiene
# 279 recipientes: 163,2 carros terminados y 115,8 cilindros vendidos vacíos. Hoja «parametros_carros»: 20 días
# hábiles por mes, es decir 4 semanas de 5 días.
PICO_MES = {"25 kg": (40.77, 28.98), "50 kg": (89.73, 63.72), "70 kg": (19.62, 13.95), "100 kg": (13.05, 9.18)}
DIAS_MES, SEMANAS_MES = 20, 4


def por_semana(mod=None, cil=True, mat=True):
    ks = [mod] if mod else list(PICO_MES)
    return sum((PICO_MES[k][0] if mat else 0.0) + (PICO_MES[k][1] if cil else 0.0) for k in ks) / SEMANAS_MES


def por_dia(mod=None, cil=True, mat=True):
    return por_semana(mod, cil, mat) * SEMANAS_MES / DIAS_MES


# lugares de carros rodantes: (código, puesto, qué guarda, criterio, cuenta, lugares)
STOCK_CARROS = [
    ("C-11", "11 Pulmón de despacho a la pintura", "Carros secos (matafuegos y cilindros) hasta que sale el camión",
     "W-CAR 11: 2 viajes por semana en el pico; croquis del usuario: medio lote = 3 días del pico",
     "3 × %.2f = %.1f" % (por_dia(), 3 * por_dia()), 48),
    ("C-12", "12 Pulmón de pintados", "Matafuegos pintados hasta la carga (los cilindros siguen al depósito 16)",
     "Lo que trae un viaje de vuelta: 3 días de matafuegos",
     "3 × %.2f = %.1f" % (por_dia(cil=False), 3 * por_dia(cil=False)), 25),
    ("C-14", "14 Sala de pérdidas", "Muestra del lote durante 7 días",
     "Croquis del usuario (W-CAR 14: 30 con 100 carros por semana)", "%.0f matafuegos por semana" % por_semana(cil=False),
     20),
    ("C-16", "16 Retenidos (amarillo)", "Matafuegos esperando la liberación del lote",
     "W-CAR 16: el lote de una semana se libera al final de la semana siguiente: hasta 1,75 semanas",
     "1,75 × %.1f = %.1f" % (por_semana(cil=False), 1.75 * por_semana(cil=False)), 80),
    ("C-16", "16 Liberados (verde)", "Matafuegos liberados y cilindros pintados, hasta el despacho",
     "W-CAR 16: una semana de producción", "%.1f + %.1f = %.1f" % (por_semana(cil=False), por_semana(mat=False),
                                                                   por_semana()), 80),
]

STOCK_CARROS = [k[:4] + (k[4].replace(".", ","),) + k[5:] for k in STOCK_CARROS]

# ================================================================ PASILLOS
Z("A2", "Pasillo principal: carril del autoelevador", R(0, Y_S, LX, Y_AE), "CIRC", _AE, tipo="pasillo", sub="AE")
Z("A2-S", "Pasillo principal: senda peatonal", R(0, Y_AE, LX, Y_A2), "CIRC",
  "Senda demarcada de 1,5 m, separada del carril por baranda con cruces (croquis del usuario, lámina de accesos)",
  tipo="pasillo", sub="SP")
Z("AL-A", "Almacén: pasillo AL-A (máquinas de corte y embutido)", R(10.4, Y_A2, X_AL, LY), "CIRC", _AE,
  tipo="pasillo", sub="AE")
Z("AL-B", "Almacén: pasillo AL-B (racks)", R(1.2, Y_A2, 6.2, LY), "CIRC", _AE, tipo="pasillo", sub="AE")
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
Z("PS-2", "Paso peatonal norte-sur entre carros 9/10 y la terminación", R(57.3, Y_A2, 58.8, Y_CN), "CIRC",
  "1,5 m", tipo="pasillo", sub="SP")
Z("PO-N2", "Pasillo norte-sur de operarios (detección y cuelgue)", R(57.3, Y_CN, 58.8, Y_M), "CIRC",
  "1,5 m: continúa la senda PS-2 hasta la senda norte", tipo="pasillo", sub="PO")
Z("PS-S", "Senda de los locales del sur (mantenimiento, calidad, compresores)", R(0, 8.4, 24.7, 9.9), "CIRC",
  "1,5 m", tipo="pasillo", sub="SP")
Z("PS-3", "Paso peatonal de la senda sur al pasillo principal", R(8.0, 9.9, 9.5, Y_S), "CIRC", "1,5 m",
  tipo="pasillo", sub="SP")

# ================================================================ ALMACÉN DE MP (oeste)
_XALM = "X-ALM v5, hoja Resumen"
Z("AL-R1", "Rack selectivo R1, 4 niveles: 10 módulos × 8 = 80 posiciones", R(0.1, Y_A2, 1.2, LY), "MP",
  _XALM + ": 128 posiciones de rack (insumos de montaje de las dos líneas, embalaje, soldadura y superficie, "
  "casquetes y cuplas, revendidos)")
Z("AL-W", "Franja del muro oeste", R(0, Y_A2, 0.1, LY), "MP", "Separación del rack al muro")
Z("AL-R2", "Rack selectivo R2, 4 niveles: 6 módulos × 8 = 48 posiciones", R(6.2, 30.8, 7.3, LY), "MP", _XALM)
Z("AL-AB", "Carros de abastecimiento, identificación y retenidos de MP", R(6.2, Y_A2, 7.3, 30.8), "MP",
  "W-CAR 1 tabla 5 (2 carros: 3 × 1 m; retenidos: 3 pallets); X-ALM (identificación: 3,0 m² netos)")
Z("AL-HO", "Hojas de chapa: manuales (7 pilas) y carros (3 posiciones)", R(7.3, Y_A2, 10.4, 33.6), "MP",
  "X-ALM: hojas de manuales 17,5 m² netos (P02 a P04) y calle de chapa de carros 9 m² netos (P12 y P13)", 26.5)
Z("AL-CA", "Cantiléver de caños y barras (5 niveles)", R(7.3, 33.6, 10.4, LY), "MP",
  "X-ALM: 11 posiciones (30 m² netos con 3 niveles); con 5 niveles basta un frente de 12,4 m")

for i in range(10):
    E(f"R1-{i + 1}", "Rack 4 niveles (2 pallets por nivel)", Rw(0.1, 20.1 + i * 2.67, 1.1, 2.67), "AL-R1", "rack",
      "E", 0, "X-ALM: pallet 1200 × 1000, 4 niveles", ae=True)
for i in range(6):
    E(f"R2-{i + 1}", "Rack 4 niveles (2 pallets por nivel)", Rw(6.2, 30.9 + i * 2.67, 1.1, 2.67), "AL-R2", "rack",
      "O", 0, "X-ALM", ae=True)
E("AB-1", "Estacionamiento de los 2 carros de abastecimiento (FCEP10520)", R(6.3, 20.2, 7.3, 23.2), "AL-AB",
  "carro_plat", "O", 0, "W-CAR 1 tabla 5: 3 × 1 m")
E("AB-2", "Estantería de identificación (5 niveles, bajo llave)", R(6.3, 23.5, 7.3, 26.5), "AL-AB", "estanteria",
  "O", 0, "X-ALM: identificación 3,0 m² netos")
E("AB-3", "Retenidos de MP (3 pallets, jaula roja)", R(6.2, 26.9, 7.3, 30.5), "AL-AB", "jaula", "O", 0,
  "W-CAR 1 tabla 5: 3 pallets", ae=True)
y = 20.2
for i, (w, d, n) in enumerate([(1.0, 2.0, "Hoja LAF 1,6 × 1000 × 2000")] * 5 + [(1.22, 2.44, "Hoja LAF 1,25 × 1220 × 2440"),
                                                                             (1.5, 3.0, "Hoja LAF 2,0 × 1500 × 3000")]):
    E(f"HO-{i + 1}", f"Pila de chapa (manuales): {n}", R(10.35 - d, y, 10.35, y + w), "AL-HO", "paquetes",
      "E", 0, "X-ALM: P02 a P04, 2 de alto", ae=True)
    y += w + 0.1
for i in range(3):
    E(f"CC-{i + 1}", "Calle de chapa de carros: paquete 1500 × 3000 (2 de alto)", R(7.35, y, 10.35, y + 1.5),
      "AL-HO", "paquetes", "E", 0, "W-CAR 1 tabla 5 y X-ALM: 3 posiciones de 3,0 × 1,5 m", ae=True)
    y += 1.6
E("CA-1", "Cantiléver simple, 5 niveles, brazos de 1,2 m (caños de 6 m y barras)", R(8.8, 34.0, 10.4, 46.4), "AL-CA",
  "cantilever", "E", 0, "X-ALM: 11 posiciones", ae=True)

# ================================================================ BANDA SUR OESTE: recepción, almacén complementario y servicios
Z("SR-CU", "Cuarentena de MP (7 pallets)", R(0.4, 12.3, 8.0, Y_S), "MP",
  "W-CAR 1 tabla 5: 7 pallets; tabla v10: 8,4 m² netos (los paquetes de chapa y los atados se controlan en su lugar "
  "del almacén, con tarjeta de cuarentena, W-MAN 1)", 8.4)
Z("SR-CU0", "Franja libre detrás de la cuarentena (maniobra del operario de recepción)", R(0, 9.9, 8.0, 12.3), "MP",
  "Paso del inspector detrás de los pallets")
Z("SR-CU1", "Franja del muro oeste junto a la cuarentena", R(0, 12.3, 0.4, Y_S), "MP", "Separación al muro")
Z("SR-RE", "Recepción: balanza de plataforma y mesa de inspección", R(9.5, 11.3, 12.8, Y_S), "MP",
  "W-MAN 1 y W-CAR 1: balanza 1,20 × 1,20 m y mesa 1,2 × 0,6 m", 6.8)
Z("SR-RE0", "Franja detrás de la recepción", R(9.5, 9.9, 12.8, 11.3), "MP", "Paso del inspector")
Z("SR-PQ", "Depósito de polvo químico y pintura en polvo (cerrado, zona seca)", R(13.0, 10.7, 17.8, Y_S), "MP",
  "X-ALM: 11 posiciones, 8,4 m² netos; rack pesado de big bags y pallets de bolsas y pintura", 12.6, tipo="local")
Z("SR-PQ0", "Franjas junto al depósito de polvo", R(12.8, 9.9, 13.0, Y_S), "MP", "")
Z("SR-PQ1", "Franja al sur del depósito de polvo", R(13.0, 9.9, 17.8, 10.7), "MP", "")
Z("SR-FL", "Bobinas de fleje (21 posiciones en 7 calles de 3)", R(17.8, 9.9, 24.7, Y_S), "MP",
  "X-ALM: chapa y fleje, bobinas sobre pallet en piso (1 nivel), 21 lugares", 25.2)
E("CU-1", "Cuarentena: 7 posiciones de pallet 1200 × 1000", R(0.6, 12.3, 7.9, Y_S), "SR-CU", "pallets_q", "N", 0,
  "W-CAR 1", ae=True)
E("RE-1", "Balanza de plataforma 1,20 × 1,20 m, 1.500 kg", R(9.7, 12.2, 10.9, 13.4), "SR-RE", "balanza", "N", 0,
  "W-MAN 1 / W-CAR 1", ae=True)
E("RE-2", "Mesa de inspección de recepción", R(11.3, 12.6, 12.5, 13.2), "SR-RE", "banco", "S", 1, "W-CAR 1 tabla 5")
E("PQ-1", "Rack pesado de big bags (4 niveles) y pallets de pintura en polvo", R(13.2, 10.9, 17.6, 12.1), "SR-PQ",
  "rack", "N", 0, "X-ALM", ae=True)
for i in range(7):
    E(f"FL-{i + 1}", "Calle de 3 bobinas de fleje sobre pallet", Rw(18.0 + i * 0.95, 9.95, 0.85, 3.5), "SR-FL",
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
Z("SV-CA", "Calidad: metrología, instrumentos patrón y contramuestras", R(16.6, 0, 21.4, 8.4), "AUX",
  "Croquis del usuario (calidad en el ángulo SO); W-CAR: técnico de calidad", 0, tipo="local")
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
Z("C-03", "3 Cilindrado", R(21.8, Y_A2, 28.8, 25.0), "CAR", _W + " 3: ≈ 7,0 × 5,0 m", 35)
Z("C-03N", "Paso de la mesa móvil del marcado al cilindrado", R(21.3, 25.0, 28.8, 26.4), "CAR",
  "W-CAR 2.1 y 3: EFE 600 y mesa móvil entre el marcado y la roladora")
Z("C-03W", "Franja entre el corte y el cilindrado", R(21.3, Y_A2, 21.8, 25.0), "CAR", "")
Z("C-03E", "Paso de los carros del marcado al cilindrado", R(24.8, 26.4, 28.8, Y_CN), "CAR",
  "W-CAR 2.1: los carros llenos esperan al costado de la mesa de marcado")
Z("C-05", "5 Soldadura longitudinal", R(29.3, Y_A2, 34.8, 24.0), "CAR", _W + " 5: ≈ 5,5 × 4,0 m", 22)
Z("C-04", "4 Punteo del cuerpo", R(29.3, 24.5, 35.3, Y_CN), "CAR", _W + " 4: ≈ 6,0 × 4,5 m", 27)
Z("C-45", "Cortina de soldadura entre 3 y 4/5", R(28.8, Y_A2, 29.3, Y_CN), "CAR", "W-CAR 4: cortina de soldadura")
Z("C-45b", "Cortina de soldadura entre 4 y 5", R(29.3, 24.0, 35.3, 24.5), "CAR", "W-CAR 4: cortina de soldadura")
Z("C-45c", "Franja al este de la soldadura longitudinal", R(34.8, Y_A2, 35.3, 24.0), "CAR", "")
Z("C-07", "7 Armado y soldadura circunferencial", R(36.8, Y_A2, 42.8, 24.5), "CAR", _W + " 7: ≈ 6,0 × 4,5 m", 27)
Z("C-06", "6 Soldadura de cupla en la cúpula", R(36.8, 25.5, 41.3, Y_CN), "CAR", _W + " 6: ≈ 4,5 × 3,5 m", 16)
Z("C-67", "Paso del carro canasto de cúpulas de 6 a 7", R(36.8, 24.5, 42.8, 25.5), "CAR", "W-CAR 6 y 7")
Z("C-67b", "Franja al este de la cupla", R(41.3, 25.5, 42.8, Y_CN), "CAR", "")
Z("C-08", "8 Soldadura de accesorios", R(43.3, Y_A2, 49.8, 24.5), "CAR", _W + " 8: ≈ 6,5 × 4,5 m", 29)
Z("C-081", "8.1 Fabricación de accesorios", R(43.3, 25.0, 51.3, Y_CN), "CAR", _W + " 8.1: ≈ 8,0 × 4,0 m", 32)
Z("C-78", "Cortina de soldadura entre 7 y 8", R(42.8, Y_A2, 43.3, Y_CN), "CAR", "W-CAR 8: cortina de soldadura")
Z("C-88", "Cortina entre 8 y 8.1", R(43.3, 24.5, 51.3, 25.0), "CAR", "W-CAR 8: cortina de soldadura")
Z("C-08E", "Salida de los carros sobre su juego provisorio", R(49.8, Y_A2, 51.3, 24.5), "CAR",
  "W-CAR 8: salida demarcada en amarillo")
Z("C-10", "10 Secado", R(51.8, Y_A2, 54.8, 22.5), "CAR", _W + " 10: ≈ 3,0 × 2,5 m", 7.5)
Z("C-09", "9 Prueba hidráulica", R(51.3, 25.0, 57.3, Y_CN), "CAR", _W + " 9: ≈ 5,5 × 4,0 m", 22)
Z("C-910a", "Paso de la prueba hidráulica al secado", R(51.3, 22.5, 57.3, 25.0), "CAR", "W-CAR 9 y 10")
Z("C-910b", "Franja junto al secado (lado oeste)", R(51.3, Y_A2, 51.8, 22.5), "CAR", "")
Z("C-910c", "Salida del secado hacia el pulmón de despacho", R(54.8, Y_A2, 57.3, 22.5), "CAR",
  "W-CAR 10: los carros secos van al puesto 11, al otro lado del pasillo")

# ---- 2 corte (W-CAR 2)
E("C2-1", "Mesa elevadora de tijera SJG3.0-1.6 (2600 × 1800, 3 t)", R(17.0, 20.1, 19.6, 21.9), "C-02", "mesa_tijera",
  "S", 0, "W-CAR 2: 2,6 × 1,8 m, 1 m de paso hasta la guillotina", ae=True)
E("C2-2", "Guillotina hidráulica CENA 8 × 3200", R(16.4, 22.95, 20.3, 25.05), "C-02", "guillotina", "S", 1,
  "W-CAR 2: ≈ 3,9 × 2,1 m")
E("C2-3", "Rampa trasera de salida (pulmón de cuerpos cortados)", R(16.4, 25.1, 20.3, 25.7), "C-02",
  "mesa_rodillos", "N", 0, "W-CAR 2: zona trasera de 3,9 × 2,5 m")
E("C2-4", "Contenedor de scrap 1.000 L con volcador", R(15.45, 25.9, 16.92, 27.32), "C-02", "contenedores", "O", 0,
  "W-CAR 2: 1470 × 1420 mm, detrás de la guillotina", ae=True)
E("C2-5", "Carro de salida: desarrollos de manuales en llenado", R(17.3, 26.1, 18.4, 26.8), "C-02", "carro_plat",
  "N", 0, "W-CAR 2: carro de salida 1,1 × 0,7 m; W-MAN 2")
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
# ---- 9 prueba hidráulica y 10 secado
E("C9-1", "Puesto de prueba 1: bandeja con rejilla y rampa", R(52.0, 26.75, 53.2, 27.95), "C-09", "bandeja", "S", 0,
  "W-CAR 9: 1,2 × 1,2 m")
E("C9-2", "Puesto de prueba 2: bandeja con rejilla y rampa", R(53.5, 26.75, 54.7, 27.95), "C-09", "bandeja", "S", 0,
  "W-CAR 9: 1,2 × 1,2 m, 0,3 m entre los dos")
E("C9-3", "Canaleta tapada con rejilla", R(52.0, 28.05, 54.7, 28.25), "C-09", "canaleta", "S", 0,
  "W-CAR 9: 2,7 × 0,2 m")
E("C9-4", "Pozo de dos cámaras", R(54.8, 28.05, 55.3, 28.4), "C-09", "pozo", "S", 0, "W-CAR 9: 0,5 × 0,35 m")
E("C9-5", "Pantalla rebatible de policarbonato", R(51.85, 26.5, 54.85, 26.62), "C-09", "pantalla", "S", 0,
  "W-CAR 9: 3,0 m")
E("C9-6", "Máquina de prueba Yukon M-000200 sobre su mesa", R(52.6, 26.0, 53.65, 26.4), "C-09", "ph", "S", 1,
  "W-CAR 9: 1,05 × 0,40 m")
E("C9-7", "Tanque de 1.000 L con cesto filtro", R(55.6, 27.35, 57.16, 28.91), "C-09", "tanque", "S", 0,
  "W-CAR 9: Ø 1,56 m")
E("C9-8", "Bomba periférica con filtro Y y de cartucho", R(55.7, 26.7, 56.45, 27.15), "C-09", "bomba", "S", 0,
  "W-CAR 9: 0,75 × 0,45 m")
E("C9-9", "Planilla, manómetros patrón y cabezales de vaciado", R(55.0, 25.1, 55.95, 25.65), "C-09", "planilla", "S",
  0, "W-CAR 9: 0,95 × 0,55 m")
E("C9-10", "Zona de no conforme de la prueba hidráulica (roja)", R(56.0, 23.0, 57.1, 23.7), "C-910a", "nc", "S", 0,
  "W-CAR 9 y 10")
E("C10-1", "Espera de carros mojados (2 carros)", R(52.8, 22.65, 54.0, 23.65), "C-910a", "rodantes", "S", 0,
  "W-CAR 10: 1,2 × 1,0 m", n=2, grid=(2, 1), dem="AM")
E("C10-2", "Secadora Melisam MR011", R(52.0, 21.6, 52.6, 22.1), "C-10", "secadora", "E", 0, "W-CAR 10: ≈ 0,6 × 0,5 m")
E("C10-3", "Lugar del carro que se seca", R(52.8, 21.2, 54.0, 22.2), "C-10", "lugar", "S", 0,
  "W-CAR 10: 1,2 × 1,0 m")
E("C10-4", "Estante de cinta y planilla", R(54.2, 20.1, 54.6, 20.9), "C-10", "estanteria", "O", 0,
  "W-CAR 10: 0,8 × 0,4 m")

# ================================================================ MANUALES (29,0 a 45,0) y su ala este
_M = "W-MAN; máquina de X-MAN; medida de la tabla de áreas v10"
# fila A (41 a 45): embutido, numerado, cúpulas, soldadura de cuello y preparación de cuello
Z("M-04", "4 Corte de disco y embutido (desbobinador, alimentador y prensa)", R(X_AL, 41.0, 25.4, Y_M), "MAN", _M, 26.0)
Z("M-06", "6 Numerado de cúpula", R(25.4, 41.0, 28.0, Y_M), "MAN", _M, 2.3)
Z("M-PCU", "Zona de cúpulas (5 carros de 12 cajones)", R(28.0, 41.0, 30.9, Y_M), "MAN", "W-MAN 3: 3 a 5 carros")
Z("M-07", "7 Soldadura del cuello a la cúpula", R(30.9, 41.0, 33.4, Y_M), "MAN", _M, 5.3)
Z("M-05", "5 Preparación de cuello (2 prensas de banco)", R(33.4, 41.0, 35.3, Y_M), "MAN", _M, 4.5)
# fila B (35 a 39): corte de tubo (vertical), tramos, encastre, fondos, bordoneado
Z("M-03", "3 Corte de tubo 1 kg (láser Leapion, orientado norte-sur)", R(X_AL, 27.4, 18.0, Y_M - 4.0), "MAN", _M, 25.5)
Z("M-PT", "Tramos 1 kg (4 carros de 12 cajones)", R(18.0, 35.0, 21.0, 39.0), "MAN", "W-MAN 2: PU-T1 y PU-T2")
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
carros_fila("PU-K", "Cúpulas y fondos en llenado", 23.9, 41.2, 2, "M-04", CAJ, True, "W-MAN 3")
E("M6-1", "Micropercusión Pannier ADP120160D sobre banco", R(26.1, 43.4, 27.3, 44.0), "M-06", "marcadora", "S", 1,
  "Mesa 1,2 × 0,6 (W-CAR 1)")
for i in range(5):
    E(f"PU-CU.{i + 1}", "Zona de cúpulas: carro de 12 cajones", Rw(28.1 + (i % 2) * 1.35, 41.2 + (i // 2) * 1.2, 1.2, 0.8),
      "M-PCU", "carro_caj", "S", 0, "W-MAN 3")
E("M7-1", "Soldadora de cuello Firesafer FS-HFM1", R(31.5, 43.2, 32.7, 44.6), "M-07", "sold_circ", "S", 1,
  "Catálogo Firesafer FS Cylinder Production, pág. 8: 1200 × 1400 × 1580 mm")
carros_fila("PU-CC2", "Cúpulas con cuello en llenado", 31.0, 41.1, 1, "M-07", CAJ, fuente="W-MAN 8")
E("M5-1", "Prensa Pannier MarkFirst MB-21 sobre banco", R(33.5, 43.0, 34.1, 44.2), "M-05", "torno", "E", 1,
  "ET: cabezal 210 × 132 mm; banco 1,2 × 0,6")
E("M5-2", "Prensa Pannier MarkFirst MB-21 sobre banco", R(33.5, 41.3, 34.1, 42.5), "M-05", "torno", "E", 1,
  "ET: cabezal 210 × 132 mm; banco 1,2 × 0,6")
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
for i in range(4):
    E(f"PU-T.{i + 1}", "Tramos 1 kg: carro de 12 cajones", Rw(18.2 + (i % 2) * 1.35, 35.3 + (i // 2) * 1.0, 1.2, 0.8),
      "M-PT", "carro_caj", "S", 0, "W-MAN 2")
E("M10-1", "Prensa hidráulica Del Fabro 30 t (encastre)", R(21.6, 37.4, 22.6, 38.55), "M-10", "encastre", "S", 1,
  "ET: 1000 × 1150 × 1800 mm")
for i in range(5):
    E(f"PU-FO.{i + 1}", "Zona de fondos: carro de 12 cajones", Rw(23.2 + (i % 2) * 1.35, 35.2 + (i // 2) * 1.0, 1.2, 0.8),
      "M-10", "carro_caj", "S", 0, "W-MAN 3")
carros_fila("PU-E", "Encastre -> bordoneado", 26.8, 38.2, 1, "M-11", fuente="W-MAN 9")
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
carros_fila("PU-V3", "Cuerpos soldados junto al encastre", 29.6, 31.9, 1, "M-PV", fuente="W-MAN 7")
carros_fila("PU-FX", "Carros del cambio de formato", 29.6, 29.2, 3, "M-PV", vertical=False, fuente="W-MAN 7")


# columna este (croquis del usuario: la soldadura circunferencial baja por control de espesor, prueba hidráulica y
# secado; el granallado y la detección siguen hacia el este hasta el cuelgue de la pintura)
_SAT = ("X-MAN 2035, aprovechamiento: sold. longitudinal 97 %, encastre, sold. circunferencial y prueba hidráulica "
        "94 %, secado, preparación de cuello y etiquetado 92 %")
Z("M-12", "12 Soldadura circunferencial (2 máquinas)", R(36.8, 40.5, 43.8, Y_M), "MAN", _M, 17.5)
Z("M-13", "13 Control de espesor", R(36.8, 38.0, 43.8, 40.5), "MAN", _M + "; W-MAN 12: PU-S y 2 PU-RT", 2.3)
Z("M-14", "14 Prueba hidráulica (2 bancos)", R(36.8, 33.5, 43.8, 38.0), "MAN", _M + "; W-MAN 13: 2 PU-6", 14.1)
Z("M-15", "15 Secado (4 secadoras)", R(36.8, Y_CN, 43.8, 33.5), "MAN", _M + "; W-MAN 14: 2 PU-7", 6.0)
Z("M-16", "16 Granallado", R(45.3, Y_CN, 51.8, 34.0), "MAN", _M, 27.4)
Z("M-17", "17 y 18 Detección y corrección de defectos", R(51.8, Y_CN, 57.3, 34.0), "MAN",
  _M + "; W-MAN 16 y 17 (3 jaulas y carro de corregibles)", 9.2)
Z("M-18", "19 Cuelgue en el riel de la pintura", R(58.8, Y_CN, X_PINT, 34.0), "MAN",
  "W-MAN 18: carga de la línea; carros móviles y ganchos por formato")
Z("RV-M", "Reserva de ampliación de manuales (junto a la columna de puestos saturados)", R(45.3, 34.0, 57.3, Y_M),
  "LIB", "Lugar para la máquina siguiente de los puestos saturados en 2035. " + _SAT)
Z("RV-T", "Reserva de la pintura y del granallado", R(58.8, 34.0, X_PINT, Y_M), "LIB", _SAT)

E("M12-1", "Soldadora circunferencial Firesafer FS-SWH", R(37.3, 43.3, 39.3, 44.7), "M-12", "sold_circ", "S", 1,
  _T + " (criterio)")
E("M12-2", "Soldadora circunferencial Firesafer FS-SWH", R(40.6, 43.3, 42.6, 44.7), "M-12", "sold_circ", "S", 1,
  _T + " (criterio)")
E("M13-1", "Medidor de espesor por ultrasonido Melisam MR017 sobre mesa", R(38.0, 39.7, 39.2, 40.3), "M-13",
  "mesa_control", "S", 1, "Mesa 1,2 × 0,6 (W-CAR 1)")
carros_fila("PU-S", "«Espesor OK» -> prueba hidráulica", 39.7, 39.6, 1, "M-13", fuente="W-MAN 12")
carros_fila("PU-RT", "Retenidos del control de espesor", 41.4, 38.8, 2, "M-13", vertical=True, fuente="W-MAN 12")
E("M14-1", "Banco de prueba hidráulica Firesafer FS-JD12A", R(37.2, 36.6, 39.25, 37.7), "M-14", "ph", "S", 1,
  "Catálogo Firesafer, pág. 11: 2050 × 1100 × 1350 mm")
E("M14-2", "Banco de prueba hidráulica Firesafer FS-JD12A", R(40.4, 36.6, 42.45, 37.7), "M-14", "ph", "S", 1,
  "Catálogo Firesafer, pág. 11: 2050 × 1100 × 1350 mm")
carros_fila("PU-6", "Probados (mojados) -> secado", 37.4, 33.7, 2, "M-14", fuente="W-MAN 13")
E("M14-3", "Cámara de decantación y separador de aceites (compartidos con pérdidas)", R(42.4, 33.7, 43.6, 34.5),
  "M-14", "pozo", "S", 0, "W-MAN 13")
for i in range(4):
    E(f"M15-{i + 1}", "Secadora de cilindros Yukon", Rw(37.2 + i * 1.0, 31.8, 0.70, 0.68), "M-15", "secadora", "S",
      1 if i % 2 == 0 else 0, "ET: 700 × 680 × 1750 mm")
carros_fila("PU-7", "Secos con tapón -> granallado", 41.6, 29.2, 2, "M-15", vertical=True, fuente="W-MAN 14")
E("M16-1", "Granalladora de rodillos Airblast G-100 (rodillos de entrada y salida incluidos)", R(46.3, 31.2, 50.8, 32.5),
  "M-16", "granalladora", "N", 1, "Cotización Airblast: 4500 × 1300 × 2200 mm")
E("M17-1", "Mesa de inspección iluminada (a la salida de la granalladora)", R(52.0, 31.3, 53.2, 31.9), "M-17",
  "inspeccion", "N", 1, "W-MAN 16")
for i in range(3):
    E(f"M17-J{i + 1}", "Jaula «a corregir» / «re-granallar» / «descarte»", Rw(53.8 + i * 1.1, 29.2, 1.0, 1.0), "M-17",
      "jaula", "N", 0, "W-MAN 16")
E("M18-1", "Mesa de corrección con amoladora y extracción", R(55.3, 32.2, 56.5, 32.8), "M-17", "banco_sold", "N", 1,
  "W-MAN 17")
carros_fila("PU-CO", "Carro de corregibles", 53.7, 32.3, 1, "M-17", fuente="W-MAN 16")
carros_fila("PU-G", "Carro móvil: inspeccionados -> cuelgue", 56.0, 30.6, 1, "M-17", fuente="W-MAN 18 (carros móviles)")
E("M19-C", "Puesto de cuelgue en el riel (ganchos por formato y tapones)", R(64.6, 30.4, 65.9, 32.6), "M-18", "banco",
  "O", 1, "W-MAN 18: carga de la línea")
carros_fila("PU-G2", "Carro móvil en el cuelgue", 62.2, 30.8, 1, "M-18", fuente="W-MAN 18 (carros móviles)")
E("M19-G", "Estantería de ganchos por formato y tapones de silicona", R(59.0, 33.3, 62.0, 33.9), "M-18",
  "estanteria", "S", 0, "W-MAN 15 y 18: tapones-gancho y ganchos por formato")

# ================================================================ PINTURA (66 a 76, 20 a 47)
Z("M-19", "19 Pintura en polvo + horno (línea Firesafer)", R(X_PINT, Y_A2, LX, LY), "PINT",
  "ET: 25000 × 8000 × 4000 mm; W-MAN 18 y X-MAN 19; franja de servicio de 1 m", 270)
E("M19-1", "Línea de recubrimiento en polvo Firesafer (riel, cabina, horno, enfriamiento)", R(67.0, 21.0, 75.0, 46.0),
  "M-19", "horno", "O", 0, "ET: 25 × 8 × 4 m")

# ================================================================ TERMINACIÓN DE MANUALES (58,8 a 66, 20 a 29)
Z("M-20", "20 a 25 Terminación: carga, ensamblaje, presurización, pérdidas, etiquetado y embalaje",
  R(58.8, Y_A2, X_PINT, Y_CN), "TERM", _M + " (Guerchet de los puestos 20 a 25: 42,4 m² + 6 carros pulmón)", 47.0)
# carga de polvo, al lado de la descarga de la pintura (borde este)
carros_fila("PU-TP", "Terminados pintados -> carga", 64.6, 28.2, 1, "M-20", fuente="W-MAN 18")
E("M20-2", "Cargadora por vacío Yukon M-000121", R(65.2, 26.2, 65.82, 26.71), "M-20", "carga_polvo", "O", 1,
  "Ficha Yukon: 620 × 510 × 1200 mm")
E("M20-1", "Estación de big bag ABC 60 (bastidor, polipasto y transporte por vacío a la cargadora)",
  R(64.3, Y_A2, 65.8, 21.5), "M-20", "tanque", "S", 0, _T + " (criterio)", ae=True)
carros_fila("PU-F1", "Carga -> ensamblaje", 63.0, 26.0, 1, "M-20", fuente="W-MAN 19 a 24")
# fila norte: ensamblaje y presurización
E("M21-1", "Mesa de ensamblaje con llave dinamométrica", R(62.0, 28.2, 63.2, 28.8), "M-20", "ensamble", "S", 1,
  "Mesa 1,2 × 0,6")
carros_fila("PU-F2", "Ensamblaje -> presurización", 60.6, 27.4, 1, "M-20", fuente="W-MAN 19 a 24")
E("M22-1", "Pinza Yukon M-000150 sobre mesa (N₂ por cañería desde la jaula exterior)", R(59.2, 28.2, 60.4, 28.8),
  "M-20", "presurizacion", "S", 1, "Mesa 1,2 × 0,6")
carros_fila("PU-F3", "Presurización -> pérdidas", 59.0, 25.6, 1, "M-20", (0.61, 1.28), fuente="W-MAN 19 a 24")
# columna oeste: pérdidas
E("M23-1", "Tanque de inmersión inoxidable Firesafer FS-SS100", R(59.0, 23.3, 60.0, 25.1), "M-20", "hermeticidad",
  "E", 1, "Catálogo Filling Line, pág. 44: 1000 × 1800 × 900 mm")
carros_fila("PU-F4", "Pérdidas -> etiquetado", 59.0, 22.4, 1, "M-20", fuente="W-MAN 19 a 24")
# centro: etiquetado y embalaje
E("M24-1", "Dispensador de etiquetas y Zebra ZD421 sobre mesa", R(61.0, 24.2, 62.2, 24.8), "M-20", "etiquetadora", "N",
  1, "Mesa 1,2 × 0,6")
carros_fila("PU-F5", "Etiquetado -> embalaje", 62.6, 24.2, 1, "M-20", fuente="W-MAN 19 a 24")
E("M25-1", "Mesa de encajonado (terminados)", R(61.0, 21.8, 62.2, 22.4), "M-20", "palletizado", "N", 1,
  "X-MAN: 2 puestos; mesa 1,2 × 0,6")
E("M25-2", "Mesa de encajonado (cilindros vacíos)", R(62.5, 21.8, 63.7, 22.4), "M-20", "palletizado", "N", 1,
  "X-MAN: 2 puestos; mesa 1,2 × 0,6")
E("M25-3", "Armadora automática de cajas", R(58.9, Y_A2, 60.92, 21.42), "M-20", "palletizado", "N", 0,
  "Sin cotizar; referencia FS-DDP50: 2020 × 1420 mm")
E("M25-4", "Envolvedora EDOS PS5 (pallet listo para el autoelevador)", R(61.2, Y_A2, 63.75, 21.5), "M-20",
  "envolvedora", "S", 0, "Plano de cotas EDOS 26880: 2550 × 1500 mm", ae=True)
E("M25-5", "Pila de pallets vacíos 1200 × 1000", R(64.6, 22.4, 65.8, 23.4), "M-20", "pallets_q", "S", 0, "W-MAN 25")

# ================================================================ BANDA SUR: carros 11 a 17 y depósitos de PT
# Cantidad de carros de cada pulmón: STOCK_CARROS (demanda pico 2035 de X-CAR). Lugar de cada carro parado sobre sus
# ruedas y su pata: 0,68 × 0,75 m; filas enfrentadas de a dos con la manija hacia el pasillo de 1,0 m.
X16, X13, X11, XPT = 24.7, 39.7, 55.2, 67.6
X12 = X11 + 6.2
_STK = "Lugares de STOCK_CARROS (demanda pico 2035, X-CAR)"
Z("C-16", "16 Depósito de PT de carros: retenidos (amarillo) y liberados (verde)", R(X16, 3.5, X13, Y_S), "PT",
  _W + " 16 (zonas por modelo y lote, pasillo hasta la puerta); " + _STK)
Z("C-16P", "16 Carga del despacho de carros (P2) y rechazados (rojo)", R(X16, 0, X13, 3.5), "PT",
  "W-CAR 16: tarima de carga del puesto 11; zona de rechazados ≈ 5 × 3 m")
Z("C-17", "17 Ensayos de lote (recinto de descarga, balanza y mesa)", R(X13, 0, X13 + 15.5, 4.5), "CAR",
  _W + " 17: ≈ 15,5 × 4,5 m (el patio de rodadura va afuera)", 70)
Z("C-14", "14 Sala del ensayo de pérdidas (paneles aislantes, split)", R(X13, 4.5, X13 + 5.0, 9.5), "CAR",
  _W + " 14: 5,0 × 5,0 m", 25, tipo="local")
Z("C-15", "15 Etiquetado e inspección final", R(X13, 9.5, X13 + 5.0, Y_S), "CAR",
  _W + " 15: ≈ 3,5 × 2,5 m, más el paso de los carros al depósito 16", 9)
Z("C-13", "13 Carga, armado y presurización", R(X13 + 5.0, 7.0, X11, Y_S), "CAR", _W + " 13: ≈ 10 × 6 m", 60)
Z("C-1314", "Paso de la carga a la sala de pérdidas y a los ensayos", R(X13 + 5.0, 4.5, X11, 7.0), "CAR",
  "W-CAR 13, 14 y 17: recorrido de los carros de la muestra; estanterías del puesto 13")
Z("C-12", "12 Recepción de pintados: cambio de juego y pulmón de pintados", R(X11, 3.3, X12, Y_S), "CAR",
  _W + " 12: cambio de juego al bajar del camión y pulmón al lado del puesto 13; " + _STK)
Z("C-12C", "12 Descarga del camión de la pintura (tarima, P6)", R(X11, 0, X12, 3.3), "CAR",
  "W-CAR 12: la descarga es la carga del puesto 11 al revés, con la tarima y el autoelevador")
Z("C-11", "11 Pulmón de despacho a la pintura tercerizada", R(X12, 3.3, XPT, Y_S), "CAR",
  _W + " 11: filas por modelo y lote demarcadas en amarillo; " + _STK)
Z("C-11C", "11 Carga del camión de la pintura (tarima, P3)", R(X12, 0, XPT, 3.3), "CAR",
  "W-CAR 11: tarima de carga con topes al lado de la puerta; el autoelevador la sube a la caja desde la playa")
Z("PT-M", "Depósito de PT de manuales: 7 calles de 10 posiciones (pallets de a 2)", R(XPT, 0, LX, Y_S), "PT",
  "X-DT Almacén PT filas 127-128: 56 + 72 pallets de a 2 = 64 posiciones (115,2 m² con su pasillo)", 84)


def fila(cod, nombre, r, zona, nu, nv, dem, fuente):
    E(cod, nombre, r, zona, "rodantes", "S", 0, fuente, n=nu * nv, grid=(nu, nv), dem=dem)


# 11 pulmón de despacho: 48 lugares en 4 pares de filas de 6 (25 kg 12, 50 kg 24, 70 kg 6, 100 kg 6)
_F11 = "STOCK_CARROS: 48 lugares ≥ 3 días del pico (%.1f)" % (3 * por_dia())
fila("C11-1", "Filas de 25 kg (12 lugares)", R(62.0, 10.8, 66.08, 12.3), "C-11", 6, 2, "AM", _F11)
fila("C11-2", "Filas de 50 kg (12 lugares)", R(62.0, 8.3, 66.08, 9.8), "C-11", 6, 2, "AM", _F11)
fila("C11-3", "Filas de 50 kg (12 lugares)", R(62.0, 5.8, 66.08, 7.3), "C-11", 6, 2, "AM", _F11)
fila("C11-4", "Filas de 70 kg (6) y de 100 kg (6)", R(62.0, 3.35, 66.08, 4.85), "C-11", 6, 2, "AM", _F11)
E("C11-T", "Tarima de carga con topes y rampa (el autoelevador la sube a la caja)", R(63.4, 1.1, 64.6, 2.1), "C-11C",
  "tarima", "N", 0, "W-CAR 11: 1,2 × 1,0 m, al lado de la puerta")
# 12 recepción de pintados
E("C12-T", "Tarima de descarga (la del puesto 11)", R(57.0, 1.1, 58.2, 2.1), "C-12C", "tarima", "N", 0,
  "W-CAR 12: la descarga usa la tarima del puesto 11")
E("C12-1", "Lugar de cambio de juego 1: crique, zorra de retorno y cajones de ejes y ruedas", R(55.4, 3.5, 57.4, 5.0),
  "C-12", "cambio_juego", "N", 1, "W-CAR 12: 2,0 × 1,5 m, al lado de la puerta")
E("C12-2", "Lugar de cambio de juego 2", R(57.6, 3.5, 59.6, 5.0), "C-12", "cambio_juego", "N", 1,
  "W-CAR 12: 2,0 × 1,5 m")
E("C12-3", "Rechazados del pintor (rojo)", R(59.8, 3.5, 61.3, 5.5), "C-12", "nc", "N", 0, "W-CAR 12: ≈ 2 × 1,5 m")
_F12 = "STOCK_CARROS: 25 lugares ≥ 3 días de matafuegos (%.1f)" % (3 * por_dia(cil=False))
fila("C12-4", "Pulmón de pintados: matafuegos (10 lugares)", R(55.4, 11.0, 58.8, 12.5), "C-12", 5, 2, "AM", _F12)
fila("C12-5", "Pulmón de pintados: matafuegos (10 lugares)", R(55.4, 8.5, 58.8, 10.0), "C-12", 5, 2, "AM", _F12)
fila("C12-6", "Pulmón de pintados: matafuegos (5 lugares)", R(55.4, 6.75, 58.8, 7.5), "C-12", 5, 1, "AM", _F12)
# 13 carga, armado y presurización
E("C13-1", "Estación A: lugar del carro (cinta y control del interior)", R(52.6, 8.3, 55.0, 10.5), "C-13", "lugar",
  "N", 1, "W-CAR 13: 2,4 × 2,2 m, del lado del pulmón de pintados")
E("C13-2", "Estación B: balanza de 300 kg con rampa y cargadora por vacío Yukon M-000121", R(48.6, 8.0, 51.6, 10.6),
  "C-13", "carga_polvo", "S", 1, "W-CAR 13: 3,0 × 2,6 m")
E("C13-3", "Bastidor de descarga del big bag con tolva (alto 2,8 m)", R(49.3, 12.2, 50.9, 13.4), "C-13", "bastidor",
  "N", 0, "W-CAR 13: 1,6 × 1,2 m, con acceso para el autoelevador", ae=True)
E("C13-4", "Estación C: lugar del carro (manga, traba, precinto y tarjeta)", R(45.2, 8.3, 47.5, 10.5), "C-13",
  "lugar", "N", 1, "W-CAR 13: 2,3 × 2,2 m, del lado del etiquetado")
E("C13-5", "Batería de nitrógeno (11 tubos de 50 L) en jaula, con manifold", R(52.6, 12.45, 55.2, 13.35), "C-13",
  "bateria_gas", "N", 0, "W-CAR 13: 2,6 × 0,9 m")
E("C13-6", "Colector de polvo de 3 HP (aspiración localizada en la boca)", R(51.7, 11.6, 52.5, 12.4), "C-13",
  "colector10", "N", 0, "W-CAR 13: equipos y herramientas")
E("C13-7", "Estanterías de válvulas, mangas, ruedas y ejes, con cajones", R(46.0, 4.55, 52.0, 5.05), "C-1314",
  "estanteria", "N", 0, "W-CAR 13: 3 × (2,0 × 0,5 m)")
# 14 sala de pérdidas
_F14 = "STOCK_CARROS: 20 lugares (croquis del usuario)"
fila("C14-1", "Muestra en la sala: 10 lugares numerados", R(40.0, 7.1, 43.4, 8.6), "C-14", 5, 2, "AM", _F14)
fila("C14-2", "Muestra en la sala: 10 lugares numerados", R(40.0, 4.65, 43.4, 6.15), "C-14", 5, 2, "AM", _F14)
E("C14-3", "Split frío/calor BGH 3000F y registrador", R(39.75, 6.4, 40.0, 7.4), "C-14", "split", "E", 0,
  "W-CAR 14: en la pared")
# 15 etiquetado
E("C15-1", "Lugares de los 2 carros que se etiquetan", R(42.4, 10.6, 44.4, 11.4), "C-15", "lugar", "S", 1,
  "W-CAR 15: 2 × (1,0 × 0,8 m)")
E("C15-2", "Mesa con calcomanías, plantillas y alcohol", R(40.8, 10.7, 42.0, 11.3), "C-15", "etiquetadora", "S", 0,
  "W-CAR 15: 1,2 × 0,6 m")
E("C15-3", "Zona de no conforme (roja)", R(39.9, 9.6, 41.4, 10.6), "C-15", "nc", "N", 0, "W-CAR 15: 1,5 × 1,0 m")
# 16 depósito de PT de carros: liberados (oeste, hacia P2) y retenidos (este, a la salida del etiquetado)
_F16R = "STOCK_CARROS: 80 lugares ≥ 1,75 semanas de matafuegos (%.1f)" % (1.75 * por_semana(cil=False))
_F16L = "STOCK_CARROS: 80 lugares ≥ 1 semana del pico (%.1f)" % por_semana()
for k, (yy, mod) in enumerate([(11.05, "25 kg"), (8.55, "50 kg"), (6.05, "50 kg"), (3.55, "70 kg (10) y 100 kg (10)")]):
    fila(f"C16-L{k + 1}", f"Liberados {mod} (20 lugares)", R(24.85, yy, 31.65, yy + 1.5), "C-16", 10, 2, "VE", _F16L)
    fila(f"C16-R{k + 1}", f"Retenidos {mod} (20 lugares)", R(32.85, yy, 39.65, yy + 1.5), "C-16", 10, 2, "AM", _F16R)
E("C16-T", "Tarima de carga con topes (despacho por P2)", R(27.1, 1.2, 28.3, 2.2), "C-16P", "tarima", "N", 0,
  "W-CAR 16: las del puesto 11")
E("C16-X", "Zona de rechazados (roja)", R(34.6, 0.25, 39.6, 3.25), "C-16P", "nc", "N", 0, "W-CAR 16: ≈ 5 × 3 m")
# 17 ensayos de lote
E("C17-1", "Colector de polvo con filtro de mangas (fondo del recinto)", R(39.9, 1.25, 40.9, 2.25), "C-17",
  "colector10", "E", 0, "W-CAR 17: ≈ 1,0 × 1,0 m")
E("C17-2", "Recinto de descarga cerrado (alto 3 m), piso marcado cada 0,5 m y ventana", R(40.9, 0.25, 51.9, 3.25),
  "C-17", "recinto", "N", 0, "W-CAR 17: 12 × 3 m con el colector")
E("C17-3", "Balanza de plataforma con rampa (en la puerta del recinto)", R(52.2, 0.3, 53.4, 1.5), "C-17", "balanza",
  "N", 0, "W-CAR 17: 1,2 × 1,2 m")
E("C17-4", "Mesa de medición, perchero de mangas y planillas", R(52.3, 3.55, 54.3, 4.35), "C-17", "banco", "S", 1,
  "W-CAR 17: 2,0 × 0,8 m")
# PT de manuales: 7 calles de 10 pallets de fondo, con la boca sobre el pasillo principal
for i in range(7):
    E(f"PTM-{i + 1}", "Calle de 10 posiciones de piso (2 pallets apilados por posición)",
      Rw(XPT + 0.2 + i * 1.15, 0.25, 1.05, 12.6), "PT-M", "pallets_pt", "N", 0, "X-DT Almacén PT", ae=True)

# ================================================================ PUERTAS DE LOS LOCALES DENTRO DE LA NAVE
# (x, y, ancho, muro 'h' o 'v', abre +1/-1); el ancho mayor a 2 m es una cortina enrollable
PUERTAS_LOCALES = [
    (5.0, 3.8, 1.0, "v", 1),          # compresores -> mantenimiento
    (1.4, 8.4, 0.9, "h", -1),         # tablero general -> senda sur
    (8.0, 8.4, 1.6, "h", -1),         # mantenimiento (doble hoja) -> senda sur
    (13.6, 8.4, 1.0, "h", -1),        # pañol -> senda sur
    (18.0, 8.4, 0.9, "h", -1),        # calidad -> senda sur
    (13.6, Y_S, 3.6, "h", 1),         # depósito de polvo: cortina hacia el pasillo principal
    (44.7, 5.2, 1.0, "v", 1),         # sala de pérdidas -> paso de carga
]

# ================================================================ ADMINISTRACIÓN Y SERVICIOS AL PERSONAL (anexo norte)
# Disposición: croquis del usuario «Área administrativa y de servicios al personal» (27,6 × 14,3 m, calle al norte):
# fila norte de oficinas y hall, pasillo único de 1,6 m, fila sur de servicios con puertas directas a la planta.
# Dotación 2035 sin recargas (X-DT): turno mañana 36 personas (32 H y 4 M). Sanitarios (Dec. 351/79 art. 49 con las
# fórmulas de la X-DT): H 2 inodoros, 3 orinales, 4 lavabos y 3 duchas; M 1, 1 y 1. Armarios: 34 H y 4 M.
# Comedor: 36 personas en 2 tandas = 18 plazas (el croquis tiene 24).
XA0 = 16.0
XA1 = XA0 + 27.6
YA0, YA1 = LY + MURO, LY + MURO + 14.3
Y_PC0, Y_PC1 = YA0 + 8.2, YA0 + 9.8             # pasillo único de 1,6 m
Y_PL0, Y_PL1 = YA0 + 4.9, YA0 + 5.2             # plenum sanitario
ADMIN = []                                      # locales del anexo (misma clase Zona)
MOB = []                                        # muebles: (tipo de planta/mobiliario.py, R, frente, n)


def A(cod, nombre, r, fuente="", req=0.0, cat="ADM"):
    ADMIN.append(Zona(cod, nombre, r, cat, fuente, req, "local"))


def MB(tipo, r, frente="S", n=1):
    MOB.append((tipo, r, frente, n))


_CR = "Croquis del usuario (área administrativa 27,6 × 14,3 m)"
_DT = "X-DT hoja Servicios y Oficinas, 2035 sin recargas"
x = XA0
A("AD-GE", "Gerencia", R(x, Y_PC1, x + 4.0, YA1), _CR + ": 4,0 × 4,5 m")
A("AD-SR", "Sala de reuniones (12 personas)", R(x + 4.0, Y_PC1, x + 9.4, YA1), _CR + ": 5,4 × 4,5 m")
A("AD-HA", "Hall de recepción y espera de visitas", R(x + 9.4, Y_PC1, x + 14.4, YA1), _CR + ": 5,0 × 4,5 m",
  cat="CIRC")
A("AD-PE", "Pasillo de emergencia (1,5 m) a la calle", R(x + 14.4, Y_PC1, x + 15.9, YA1), _CR, cat="CIRC")
A("AD-AD", "Administración (ventas y cobranzas, compras, administrativo)", R(x + 15.9, Y_PC1, x + 20.9, YA1),
  _CR + ": 5,0 × 4,5 m; " + _DT)
A("AD-RH", "RRHH (legajos)", R(x + 20.9, Y_PC1, x + 24.0, YA1), _CR + ": 3,1 × 4,5 m")
A("AD-VE", "Vestíbulo de personal (reloj de fichado y cartelera)", R(x + 24.0, Y_PC0, XA1, YA1),
  _CR + ": ingreso de operarios lateral este", cat="CIRC")
A("AD-PC", "Pasillo único (1,6 m)", R(x, Y_PC0, x + 24.0, Y_PC1), _CR, cat="CIRC")
A("AD-ST", "Sala técnica y supervisión (calidad, ingeniería, PCP y supervisores)", R(x, YA0, x + 4.8, Y_PC0),
  _CR + ": 4,8 × 8,2 m, vidrio a la planta; " + _DT)
A("AD-HS", "Seguridad e Higiene", R(x + 4.8, Y_PL1, x + 8.2, Y_PC0), _CR)
A("AD-EN", "Enfermería (primeros auxilios)", R(x + 4.8, YA0, x + 7.0, Y_PL1), _CR + "; Dec. 1338/96")
A("AD-EP", "Pañol de EPP (ventanilla a la planta)", R(x + 7.0, YA0, x + 8.2, Y_PL1), _CR)
A("AD-BA", "Baño para personas con discapacidad", R(x + 8.2, Y_PL1, x + 11.6, Y_PC0), _CR + "; Ley 24.314",
  cat="SAN")
A("AD-BM", "Baño de mujeres (oficinas)", R(x + 11.6, Y_PL1, x + 13.6, Y_PC0), _CR, cat="SAN")
A("AD-AC", "Acceso al comedor", R(x + 13.6, Y_PL0, x + 15.4, Y_PC0), _CR, cat="CIRC")
A("AD-BH", "Baño de varones (oficinas)", R(x + 15.4, Y_PL1, x + 18.0, Y_PC0), _CR, cat="SAN")
A("AD-LI", "Limpieza y termotanque", R(x + 18.0, Y_PL1, x + 19.5, Y_PC0), _CR)
A("AD-VM", "Vestuario y sanitarios de mujeres", R(x + 19.5, Y_PL1, x + 25.8, Y_PC0),
  _CR + ": 6,1 × 3,0 m; " + _DT + ": 4 mujeres", cat="SAN")
A("AD-CO", "Comedor (24 lugares, 2 tandas) con office", R(x + 8.2, YA0, x + 16.3, Y_PL0),
  _CR + ": 8,0 × 4,9 m; " + _DT + ": 18 plazas")
A("AD-VH", "Vestuario y sanitarios de varones", R(x + 16.3, YA0, x + 25.8, Y_PL0),
  _CR + ": 9,4 × 4,9 m; " + _DT + ": 32 varones", cat="SAN")
A("AD-PP", "Paso de personal a la planta", R(x + 25.8, YA0, XA1, Y_PC0), _CR, cat="CIRC")
A("AD-PL1", "Plenum sanitario", R(x + 8.2, Y_PL0, x + 13.6, Y_PL1), _CR + ": plenum único", cat="SAN")
A("AD-PL2", "Plenum sanitario", R(x + 15.4, Y_PL0, x + 25.8, Y_PL1), _CR + ": plenum único", cat="SAN")

# puertas del anexo: (x, y, ancho, muro 'h' o 'v', hacia dónde abre +1/-1)
PUERTAS_ADMIN = [
    (x + 2.6, Y_PC1, 0.9, "h", 1), (x + 4.4, Y_PC1, 0.9, "h", 1), (x + 12.6, Y_PC1, 0.9, "h", 1),
    (x + 16.2, Y_PC1, 0.9, "h", 1), (x + 21.2, Y_PC1, 0.9, "h", 1),
    (x + 3.7, Y_PC0, 0.9, "h", -1), (x + 7.0, Y_PC0, 1.1, "h", -1), (x + 5.0, Y_PL1, 1.1, "h", -1),
    (x + 7.1, Y_PL1, 0.8, "h", -1), (x + 9.2, Y_PC0, 0.9, "h", -1), (x + 12.0, Y_PC0, 0.8, "h", -1),
    (x + 13.9, Y_PL0, 1.0, "h", -1), (x + 15.8, Y_PC0, 0.8, "h", -1), (x + 18.3, Y_PC0, 0.8, "h", -1),
    (x + 24.6, Y_PC0, 0.9, "h", -1), (x + 25.8, YA0 + 0.8, 1.0, "v", -1),
]
# puertas exteriores del anexo: (código, muro, a, b, uso); a y b en x (muros N y S) o en y (muros E y O)
PUERTAS_EXT_ADMIN = [("H1", "N", x + 11.1, x + 12.7, "Ingreso de visitas, gerencia y oficinas (rampa y plataforma)"),
                     ("H2", "N", x + 14.5, x + 15.8, "Salida de emergencia del pasillo de emergencia"),
                     ("H3", "E", Y_PC1 + 0.3, Y_PC1 + 1.5, "Ingreso de operarios (lateral este, rampa accesible)"),
                     ("H4", "O", Y_PC0 + 0.1, Y_PC1 - 0.1, "Ingreso de supervisión, PCP, calidad y HyS (oeste)"),
                     ("H5", "E", YA0 + 1.2, YA0 + 2.4, "Salida de emergencia del paso de personal")]
VENTANAS_ADMIN = [((x + 1.4, YA0), (x + 4.6, YA0))]        # vidrio de la sala técnica a la planta

# mobiliario (planta/mobiliario.py), según el croquis
MB("escritorio", R(x + 1.2, YA1 - 1.9, x + 2.8, YA1 - 1.0), "S")
MB("sillas", R(x + 1.3, Y_PC1 + 1.3, x + 2.7, Y_PC1 + 1.8), "N", 2)
MB("archivo", R(x + 0.05, YA1 - 1.6, x + 0.6, YA1 - 0.2), "E", 2)
MB("mesa", R(x + 4.8, Y_PC1 + 1.2, x + 8.6, Y_PC1 + 3.3), "S", 12)
MB("pizarra", R(x + 9.05, Y_PC1 + 1.3, x + 9.35, Y_PC1 + 3.3), "O")
MB("mostrador", R(x + 12.4, YA1 - 2.2, x + 14.2, YA1 - 1.3), "S")
MB("sillas", R(x + 9.5, Y_PC1 + 1.2, x + 10.0, Y_PC1 + 3.2), "E", 4)
MB("estanteria", R(x + 9.6, YA1 - 0.8, x + 11.0, YA1 - 0.2), "S")
for k in range(3):
    MB("escritorio", R(x + 16.0 + k * 1.6, YA1 - 1.0, x + 17.6 + k * 1.6, YA1 - 0.1), "S")
MB("archivo", R(x + 20.3, Y_PC1 + 0.7, x + 20.85, Y_PC1 + 2.6), "O", 3)
MB("escritorio", R(x + 21.4, YA1 - 2.0, x + 23.0, YA1 - 1.1), "S")
MB("archivo", R(x + 23.4, YA1 - 1.9, x + 23.95, YA1 - 0.2), "O", 3)
MB("reloj", R(x + 24.05, Y_PC1 + 1.6, x + 24.35, Y_PC1 + 2.6), "E")
MB("pizarra", R(x + 24.05, Y_PC1 + 3.0, x + 24.35, YA1 - 0.2), "E")
MB("escritorio", R(x + 0.6, Y_PC0 - 2.0, x + 2.2, Y_PC0 - 1.1), "S")
MB("escritorio", R(x + 2.4, Y_PC0 - 2.0, x + 4.0, Y_PC0 - 1.1), "S")
MB("escritorio", R(x + 0.6, YA0 + 3.8, x + 2.2, YA0 + 4.7), "S")
MB("escritorio", R(x + 2.4, YA0 + 3.8, x + 4.0, YA0 + 4.7), "S")
MB("escritorio", R(x + 0.6, YA0 + 0.3, x + 2.2, YA0 + 1.2), "N")
MB("escritorio", R(x + 2.4, YA0 + 0.3, x + 4.0, YA0 + 1.2), "N")
MB("armarios", R(x + 0.05, YA0 + 1.9, x + 0.55, YA0 + 3.1), "E", 2)
MB("pizarra", R(x + 4.45, YA0 + 1.8, x + 4.75, YA0 + 4.3), "O")
MB("escritorio", R(x + 5.0, Y_PC0 - 1.0, x + 6.6, Y_PC0 - 0.1), "S")
MB("archivo", R(x + 7.6, Y_PL1 + 0.1, x + 8.15, Y_PL1 + 1.3), "O", 2)
MB("camilla", R(x + 6.2, YA0 + 0.7, x + 6.9, YA0 + 2.6), "O")
MB("botiquin", R(x + 4.85, YA0 + 1.3, x + 5.4, YA0 + 1.9), "E")
MB("lavabos", R(x + 6.4, YA0 + 3.2, x + 6.95, YA0 + 4.2), "O", 1)
MB("estanteria", R(x + 7.6, YA0 + 0.8, x + 8.15, YA0 + 4.0), "O")
MB("ventanilla", R(x + 7.1, YA0, x + 7.9, YA0 + 0.3), "S")
MB("inodoro_acc", R(x + 8.3, Y_PL1 + 0.1, x + 10.3, Y_PC0 - 0.9), "N")
MB("lavabos", R(x + 10.6, Y_PL1 + 0.1, x + 11.5, Y_PL1 + 0.65), "N", 1)
MB("inodoro", R(x + 11.7, Y_PL1 + 0.1, x + 12.6, Y_PL1 + 1.5), "N")
MB("lavabos", R(x + 12.8, Y_PL1 + 0.1, x + 13.5, Y_PL1 + 0.65), "N", 1)
MB("inodoro", R(x + 15.5, Y_PL1 + 0.1, x + 16.4, Y_PL1 + 1.5), "N")
MB("mingitorios", R(x + 16.6, Y_PL1 + 0.1, x + 17.4, Y_PL1 + 0.5), "N", 1)
MB("lavabos", R(x + 16.6, Y_PL1 + 0.9, x + 17.9, Y_PL1 + 1.45), "N", 1)
MB("lavadero", R(x + 18.1, Y_PL1 + 0.1, x + 19.1, Y_PL1 + 1.1), "N")
MB("carro_limpieza", R(x + 18.6, Y_PL1 + 1.3, x + 19.4, Y_PL1 + 2.1), "N")
MB("armarios", R(x + 19.6, Y_PC0 - 0.55, x + 23.8, Y_PC0 - 0.05), "S", 7)
MB("banco_vest", R(x + 20.0, Y_PL1 + 1.4, x + 23.0, Y_PL1 + 1.8), "N")
MB("lavabos", R(x + 19.6, Y_PL1 + 0.1, x + 21.6, Y_PL1 + 0.65), "N", 2)
MB("duchas", R(x + 22.0, Y_PL1 + 0.1, x + 22.9, Y_PL1 + 1.0), "N", 1)
MB("inodoro", R(x + 23.1, Y_PL1 + 0.1, x + 24.0, Y_PL1 + 1.5), "N")
for k in range(3):
    MB("mesa", R(x + 8.6 + k * 2.3, YA0 + 0.4, x + 10.3 + k * 2.3, YA0 + 3.8), "E", 8)
MB("mesada", R(x + 8.4, Y_PL0 - 0.65, x + 11.4, Y_PL0 - 0.05), "S", 2)
MB("heladera", R(x + 11.6, Y_PL0 - 0.75, x + 12.3, Y_PL0 - 0.05), "S")
MB("lavabos", R(x + 15.65, YA0 + 1.8, x + 16.25, YA0 + 3.8), "O", 2)
for k, xx in enumerate([16.4, 18.4, 18.9, 20.9, 21.4, 23.4, 23.9]):
    MB("armarios", R(x + xx, YA0 + 0.2, x + xx + 0.5, YA0 + 3.2), "E" if k % 2 == 0 else "O", 5)
for xx in (17.4, 19.9, 22.4):
    MB("banco_vest", R(x + xx, YA0 + 0.4, x + xx + 0.4, YA0 + 3.0), "E")
MB("duchas", R(x + 16.4, Y_PL0 - 0.95, x + 20.0, Y_PL0 - 0.05), "S", 4)
MB("inodoro", R(x + 20.1, Y_PL0 - 1.45, x + 21.0, Y_PL0 - 0.05), "S")
MB("inodoro", R(x + 21.1, Y_PL0 - 1.45, x + 22.0, Y_PL0 - 0.05), "S")
MB("mingitorios", R(x + 22.1, Y_PL0 - 0.45, x + 23.5, Y_PL0 - 0.05), "S", 3)
MB("lavabos", R(x + 23.6, Y_PL0 - 0.6, x + 25.7, Y_PL0 - 0.05), "S", 4)

# ================================================================ PUERTAS DE LA NAVE
PUERTAS += [
    Puerta("P1", "O", Y_S, Y_AE - 0.2, 4.8, "porton", "Materia prima: del playón oeste al pasillo principal"),
    Puerta("P2", "S", X16 + 1.0, X16 + 5.0, 4.5, "porton", "Despacho de carros (depósito 16, liberados)"),
    Puerta("P3", "S", X12 + 0.6, X12 + 4.6, 4.5, "porton", "Carga del camión a la pintura tercerizada (puesto 11)"),
    Puerta("P6", "S", X11 + 0.4, X11 + 4.4, 4.5, "porton", "Descarga de los carros pintados (puesto 12)"),
    Puerta("P4", "E", Y_S, Y_AE - 0.2, 4.8, "porton", "Playa este: despacho de PT de manuales (al final del pasillo)"),
    Puerta("P5", "S", X13 + 14.2, X13 + 15.3, 2.1, "peatonal", "Patio de ensayos de lote (17)"),
    Puerta("PE-1", "O", 8.6, 9.7, 2.1, "emergencia", "Salida del ángulo SO (extremo de la senda de los locales)"),
    Puerta("PE-3", "N", 3.0, 4.2, 2.1, "emergencia", "Salida del almacén (extremo norte del pasillo AL-B)"),
    Puerta("PE-4", "S", 32.0, 33.2, 2.1, "emergencia", "Salida del depósito de carros"),
    Puerta("PN-1", "N", XA0 + 0.3, XA0 + 1.3, 2.1, "peatonal", "Sala técnica: puerta directa a la planta"),
    Puerta("PN-2", "N", XA0 + 5.0, XA0 + 6.1, 2.1, "peatonal", "Enfermería (camilla, 1,10 m)"),
    Puerta("PN-3", "N", XA0 + 15.1, XA0 + 16.2, 2.1, "peatonal", "Comedor (almuerzo: cruce, lavamanos, comedor)"),
    Puerta("PN-4", "N", XA0 + 25.9, XA0 + 27.5, 2.1, "peatonal", "Paso de personal a la planta (doble hoja)"),
]

# ================================================================ EXTERIOR (calle al norte)
EXTERIOR = [
    ("CALLE", "Calle (frente norte)", R(-27.0, 71.5, 104.0, 77.0)),
    ("VE", "Vereda", R(-27.0, 69.0, 104.0, 71.5)),
    ("EST", "Estacionamiento de visitas y personal (incluye 1 cajón accesible de 3,5 × 5,0 m)", R(XA0, 63.6, 52.0, 69.0)),
    ("RA1", "Rampa accesible (≤ 8 %, 1,5 m) y plataforma a nivel", R(XA0 + 7.1, YA1, XA0 + 15.9, YA1 + 1.8)),
    ("RA2", "Rampa accesible oeste", R(XA0 - 1.8, Y_PC0 - 3.0, XA0, Y_PC1 + 0.2)),
    ("RA3", "Rampa accesible este", R(XA1, Y_PC1, XA1 + 1.8, YA1 + 1.8)),
    ("PO", "Playón oeste: descarga de MP (franja de 15 × 5 m de W-CAR) y maniobra", R(-22.0, 6.0, -0.2, 26.0)),
    ("PS", "Playa sur: despachos (P2), camión de la pintura (P3 y P6), gases y patio de ensayos",
     R(-22.0, -22.0, 98.0, -0.2)),
    ("PE", "Playa este: despacho de PT de manuales", R(LX + 0.2, 6.0, 98.0, 26.0)),
    ("PEN", "Patio de ensayos de lote (rodadura, plataforma de caída y pared)", R(42.0, -12.0, 54.0, -2.0)),
    ("JG", "Jaula de gases ventilada (Arcal 21 y N₂ en packs con manifold)", R(68.0, -4.2, 75.0, -1.2)),
    ("SC", "Contenedores de scrap y chatarra", R(-12.0, 28.0, -4.0, 32.0)),
]
CAMINO_CAMIONES = [(-26.0, 69.0), (-26.0, -18.0), (102.0, -18.0), (102.0, 69.0)]
