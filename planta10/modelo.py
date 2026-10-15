"""Modelo del layout de la planta FLAMA S.A. al año 2035 - versión 10 (rediseño desde cero).

Medidas en METROS. Origen en la esquina SO interior de la nave; X al este, Y al norte.
Calle al NORTE: la administración y los servicios al personal van al norte de la nave (croquis del usuario).

Concepto (croquis del usuario, octubre 2026)
--------------------------------------------
* Almacén de MP al oeste, con el portón de MP (P1) en el muro oeste, a la altura del pasillo principal.
* Manuales al norte: tres filas que salen del almacén (embutido, corte de tubo, corte de chapa), siguen hacia el
  este hasta la soldadura circunferencial y bajan por el este hasta la pintura (control de espesor, prueba
  hidráulica, secado, granallado y detección).
* Pintura al este, de norte a sur; la terminación sale de la pintura hacia el pasillo principal y el depósito de PT.
* Carros al centro: la fila de fabricación (corte a secado, W-CAR) entre los manuales y el pasillo principal, y
  sus puestos 11 a 17 al sur del pasillo, con el depósito de PT y los portones de despacho y de pintura.
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


def E(cod, nombre, r, zona, tipo="banco", frente="S", op=1, fuente="", ae=False, espejo=False):
    EQUIPOS.append(Equipo(cod, nombre, r, zona, tipo, frente, op, fuente, ae, espejo))


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
        E(f"{cod}.{i + 1}" if n > 1 else cod, nombre, r, zona, "pulmon", "S", 0, fuente)


# ================================================================ bandas
Y_S = 13.5          # banda sur: almacén complementario, servicios, carros 11 a 17, PT
Y_AE = 18.5         # carril del autoelevador del pasillo principal (13,5 a 18,5)
Y_A2 = 20.0         # senda peatonal del pasillo principal (18,5 a 20,0)
Y_CN = 29.0         # fila de fabricación de carros (20,0 a 29,0)
Y_M = 45.0          # manuales (29,0 a 45,0)
X_AL = 15.4         # ancho del almacén de MP (oeste)
X_PINT = 66.0       # pintura (66 a 76, de 20 a 47)

_AE = "Heli CPCD50 (W-MAN y W-CAR): radio de giro 2,93 m + pallet 1,2 m + 0,8 m de margen = 5,0 m (W-CAR, tabla 5)"

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
Z("PO-N1", "Pasillo norte-sur de operarios (oeste)", R(35.3, Y_CN, 36.8, Y_M), "CIRC",
  "1,5 m: vincula la senda norte, los pasillos de las filas y la senda del pasillo principal", tipo="pasillo", sub="PO")
Z("PS-1", "Paso peatonal norte-sur entre carros 4/5 y 6/7", R(35.3, Y_A2, 36.8, Y_CN), "CIRC",
  "1,5 m", tipo="pasillo", sub="SP")
Z("PS-2", "Paso peatonal norte-sur entre carros 9/10 y la terminación", R(57.3, Y_A2, 58.8, Y_CN), "CIRC",
  "1,5 m", tipo="pasillo", sub="SP")
Z("PO-AB2", "Pasillo de operarios del ala este de manuales", R(36.8, 39.0, 61.6, 41.0), "CIRC",
  "2,0 m", tipo="pasillo", sub="PO")
Z("PO-N2", "Pasillo norte-sur de operarios (este)", R(57.3, Y_CN, 58.8, 39.0), "CIRC",
  "1,5 m: continúa la senda PS-2 hasta el ala este", tipo="pasillo", sub="PO")
Z("PO-AB3", "Acceso a la detección y a la corrección", R(58.8, 37.0, 61.6, 39.0), "CIRC", "", tipo="pasillo", sub="PO")

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
  "carros", "O", 0, "W-CAR 1 tabla 5: 3 × 1 m")
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

# ================================================================ FILA DE FABRICACIÓN DE CARROS (20,0 a 29,0)
_W = "W-CAR, tabla de espacios del puesto"
Z("C-02", "Corte de chapa (guillotina común a manuales y carros)", R(X_AL, Y_A2, 21.3, 27.4), "CAR",
  _W + " 2: ≈ 5,9 × 7,4 m", 44)
Z("C-02N", "Salida de desarrollos de la guillotina a manuales", R(18.0, 27.4, 21.3, Y_CN), "CAR",
  "W-CAR 2: zona trasera; W-MAN 6: carro de desarrollos")
Z("C-021", "2.1 Marcado del cuerpo", R(21.3, 26.4, 24.8, Y_CN), "CAR", _W + " 2.1: ≈ 3,5 × 2,5 m", 9)
Z("C-03", "3 Cilindrado", R(21.8, Y_A2, 28.8, 25.0), "CAR", _W + " 3: ≈ 7,0 × 5,0 m", 35)
Z("C-03N", "Paso de la mesa móvil del marcado al cilindrado", R(21.3, 25.0, 28.8, 26.4), "CAR",
  "W-CAR 2.1 y 3: EFE 600 y mesa móvil entre el marcado y la roladora")
Z("C-03W", "Franja entre el corte y el cilindrado", R(21.3, Y_A2, 21.8, 25.0), "CAR", "")
Z("C-03E", "Franja al este del marcado", R(24.8, 26.4, 28.8, Y_CN), "CAR", "Pulmón de cuerpos marcados")
Z("C-05", "5 Soldadura longitudinal", R(29.3, Y_A2, 34.8, 24.0), "CAR", _W + " 5: ≈ 5,5 × 4,0 m", 22)
Z("C-04", "4 Punteo del cuerpo", R(29.3, 24.5, 35.3, Y_CN), "CAR", _W + " 4: ≈ 6,0 × 4,5 m", 27)
Z("C-45", "Separaciones del bloque 4/5", R(28.8, Y_A2, 29.3, Y_CN), "CAR", "")
Z("C-45b", "Separación entre 4 y 5", R(29.3, 24.0, 35.3, 24.5), "CAR", "")
Z("C-45c", "Franja al este de la soldadura longitudinal", R(34.8, Y_A2, 35.3, 24.0), "CAR", "")
Z("C-07", "7 Armado y soldadura circunferencial", R(36.8, Y_A2, 42.8, 24.5), "CAR", _W + " 7: ≈ 6,0 × 4,5 m", 27)
Z("C-06", "6 Soldadura de cupla en la cúpula", R(36.8, 25.5, 41.3, Y_CN), "CAR", _W + " 6: ≈ 4,5 × 3,5 m", 16)
Z("C-67", "Pulmón de cúpulas con cupla (carro canasto)", R(36.8, 24.5, 42.8, 25.5), "CAR", "W-CAR 6 y 7")
Z("C-67b", "Franja al este de la cupla", R(41.3, 25.5, 42.8, Y_CN), "CAR", "")
Z("C-08", "8 Soldadura de accesorios", R(43.3, Y_A2, 49.8, 24.5), "CAR", _W + " 8: ≈ 6,5 × 4,5 m", 29)
Z("C-081", "8.1 Fabricación de accesorios", R(43.3, 25.0, 51.3, Y_CN), "CAR", _W + " 8.1: ≈ 8,0 × 4,0 m", 32)
Z("C-78", "Separaciones entre 7 y 8", R(42.8, Y_A2, 43.3, Y_CN), "CAR", "")
Z("C-88", "Separación entre 8 y 8.1", R(43.3, 24.5, 51.3, 25.0), "CAR", "")
Z("C-08E", "Franja al este de la soldadura de accesorios", R(49.8, Y_A2, 51.3, 24.5), "CAR", "Carro de kits (W-CAR 8)")
Z("C-10", "10 Secado", R(51.8, Y_A2, 54.8, 22.5), "CAR", _W + " 10: ≈ 3,0 × 2,5 m", 7.5)
Z("C-09", "9 Prueba hidráulica", R(51.3, 25.0, 57.3, Y_CN), "CAR", _W + " 9: ≈ 5,5 × 4,0 m", 22)
Z("C-910a", "Paso de la prueba hidráulica al secado", R(51.3, 22.5, 57.3, 25.0), "CAR", "W-CAR 9 y 10")
Z("C-910b", "Franja junto al secado (lado oeste)", R(51.3, Y_A2, 51.8, 22.5), "CAR", "")
Z("C-910c", "Salida del secado hacia el pulmón de despacho", R(54.8, Y_A2, 57.3, 22.5), "CAR",
  "W-CAR 10: los carros secos van al puesto 11, al otro lado del pasillo")

# ---- equipos de carros (medidas de W-CAR)
E("C2-1", "Mesa elevadora de tijera SJG3.0-1.6 (2600 × 1800)", R(17.0, 20.1, 19.6, 21.9), "C-02", "mesa_tijera",
  "S", 0, "W-CAR 2", ae=True)
E("C2-2", "Guillotina hidráulica CENA 8 × 3200", R(16.4, 22.95, 20.3, 25.05), "C-02", "guillotina", "S", 1,
  "W-CAR 2: ≈ 3,9 × 2,1 m")
E("C2-3", "Zona trasera: rampa, carro de salida, EFE 600 y mesa móvil", R(16.9, 25.05, 21.2, 27.35), "C-02",
  "mesa_rodillos", "N", 0, "W-CAR 2: 3,9 × 2,5 m")
E("C2-4", "Contenedor de scrap 1.000 L", R(15.45, 25.1, 16.85, 26.52), "C-02", "contenedores", "O", 0,
  "W-CAR 2: 1470 × 1420 mm", ae=True)
E("C21-1", "Mesa de marcado con marcadora DTMAQ MPE 150130", R(21.6, 27.6, 23.0, 28.6), "C-021", "marcadora", "S", 1,
  "W-CAR 2.1: 1,4 × 1,0 m")
E("C21-2", "EFE 600 y mesa móvil (salida)", R(23.3, 27.0, 24.6, 28.0), "C-021", "carros", "S", 0, "W-CAR 2.1")
E("C3-1", "Roladora CNC 4 rodillos W12 8 × 1500", R(23.4, 22.2, 26.6, 23.6), "C-03", "cilindradora", "S", 1,
  "W-CAR 3: ≈ 3,2 × 1,4 m")
E("C3-2", "Salida axial y cuna volcadora", R(26.9, 22.4, 28.1, 23.4), "C-03", "carros", "S", 0, "W-CAR 3")
E("C3-3", "Pulmón de cuerpos rolados (1,8 × 1,2)", R(26.8, 20.2, 28.6, 21.4), "C-03", "pulmon", "S", 0, "W-CAR 3")
E("C3-4", "EFE 600 y mesa móvil (carga)", R(22.0, 20.2, 23.3, 21.2), "C-03", "carros", "S", 0, "W-CAR 3")
E("C4-1", "Virador sobre base fija (punteo)", R(31.6, 26.9, 32.8, 27.5), "C-04", "posicionador", "S", 1, "W-CAR 4")
E("C4-2", "Banco de trabajo con morsa", R(29.5, 27.8, 31.0, 28.5), "C-04", "banco", "S", 0, "W-CAR 4: 1,5 × 0,7 m")
E("C4-3", "Pulmón de cuerpos punteados (1,6 × 1,2)", R(33.5, 24.7, 35.1, 25.9), "C-04", "pulmon", "S", 0, "W-CAR 4")
E("C5-1", "Soldadora longitudinal ZH-1300 Dragon Welding", R(30.4, 21.8, 32.7, 22.94), "C-05", "sold_long", "S", 1,
  "W-CAR 5: 2,30 × 1,14 m")
E("C5-2", "MIG + chiller", R(33.0, 22.6, 34.4, 23.4), "C-05", "banco", "S", 0, "W-CAR 5")
E("C6-1", "Posicionador de cupla", R(38.0, 27.3, 39.1, 28.0), "C-06", "posicionador", "S", 1, "W-CAR 6")
E("C6-2", "Carro canasto de cúpulas", R(39.5, 26.0, 40.6, 26.7), "C-06", "carros", "S", 0, "W-CAR 6: 1,1 × 0,7 m")
E("C7-1", "Virador 1.000 kg con torcha fija", R(38.8, 22.2, 40.4, 23.0), "C-07", "posicionador", "S", 1,
  "W-CAR 7: ≈ 1,6 × 0,8 m")
E("C7-2", "Pulmón de cilindros (1,5 × 1,2)", R(41.1, 21.7, 42.6, 22.9), "C-07", "pulmon", "S", 0, "W-CAR 7")
E("C8-1", "Virador (soldadura de accesorios)", R(45.3, 22.2, 46.9, 23.0), "C-08", "posicionador", "S", 1, "W-CAR 8")
E("C8-2", "Estanterías de ruedas y kits", R(43.5, 23.7, 49.6, 24.3), "C-08", "estanteria", "S", 0, "W-CAR 8")
E("C81-1", "Rack de barras 6,5 × 0,6", R(43.6, 28.2, 50.1, 28.8), "C-081", "rack", "S", 0, "W-CAR 8.1")
E("C81-2", "Caballetes y sensitiva 8,8 × 0,8", R(43.4, 27.2, 51.2, 27.9), "C-081", "banco", "S", 1, "W-CAR 8.1")
E("C81-3", "Prensa 20 t y dobladora", R(45.0, 25.2, 47.6, 26.1), "C-081", "banco", "N", 1, "W-CAR 8.1")
E("C9-1", "Banco de prueba hidráulica Yukon M-000200", R(53.0, 26.6, 54.05, 27.0), "C-09", "ph", "N", 1,
  "W-CAR 9: 1,05 × 0,40 m")
E("C9-2", "Tanque de agua 1.000 L (Ø 1,56)", R(55.5, 27.2, 57.06, 28.76), "C-09", "tanque", "S", 0, "W-CAR 9")
E("C9-3", "Puestos de prueba (2 bandejas 1,2 × 1,2)", R(52.0, 25.2, 54.6, 26.4), "C-09", "pulmon", "S", 0, "W-CAR 9")
E("C10-1", "Lugar de secado (2 carros 1,2 × 1,0)", R(52.0, 20.2, 54.6, 21.2), "C-10", "pulmon", "S", 1, "W-CAR 10")

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
# ala este: 12 a 18 en una fila (fila A'), con la granalladora hacia la pintura
_SAT = ("X-MAN 2035, aprovechamiento: sold. longitudinal 97 %, encastre, sold. circunferencial y prueba hidráulica "
        "94 %, secado, preparación de cuello y etiquetado 92 %")
Z("M-12", "12 Soldadura circunferencial (2 máquinas)", R(36.8, 41.0, 42.4, Y_M), "MAN", _M, 17.5)
Z("M-13", "13 Control de espesor", R(42.4, 41.0, 45.2, Y_M), "MAN", _M + "; W-MAN 12: PU-S y 2 PU-RT", 2.3)
Z("M-14", "14 Prueba hidráulica (2 bancos)", R(45.2, 41.0, 50.6, Y_M), "MAN", _M + "; W-MAN 13: 2 PU-6", 14.1)
Z("M-15", "15 Secado (4 secadoras)", R(50.6, 41.0, 54.8, Y_M), "MAN", _M + "; W-MAN 14: 2 PU-7", 6.0)
Z("M-16", "16 Granallado (entra por el oeste, sale hacia la detección)", R(54.8, 41.0, 61.6, Y_M), "MAN", _M, 27.4)
Z("M-17", "17 y 18 Detección y corrección de defectos; cuelgue en la pintura", R(61.6, 37.0, X_PINT, Y_M), "MAN",
  _M + "; W-MAN 16 y 17 (3 jaulas y carro de corregibles)", 9.2)
Z("RV-M", "Reserva de ampliación de manuales", R(36.8, Y_CN, 57.3, 39.0), "LIB",
  "Lugar para la máquina siguiente de los puestos saturados en 2035. " + _SAT)
Z("RV-T", "Reserva de la terminación y de la descarga de la pintura", R(58.8, Y_CN, X_PINT, 37.0), "LIB", _SAT)

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
      "M-PCU", "pulmon", "S", 0, "W-MAN 3")
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
for i in range(4):
    E(f"PU-T.{i + 1}", "Tramos 1 kg: carro de 12 cajones", Rw(18.2 + (i % 2) * 1.35, 35.3 + (i // 2) * 1.0, 1.2, 0.8),
      "M-PT", "pulmon", "S", 0, "W-MAN 2")
E("M10-1", "Prensa hidráulica Del Fabro 30 t (encastre)", R(21.6, 37.4, 22.6, 38.55), "M-10", "encastre", "S", 1,
  "ET: 1000 × 1150 × 1800 mm")
for i in range(5):
    E(f"PU-FO.{i + 1}", "Zona de fondos: carro de 12 cajones", Rw(23.2 + (i % 2) * 1.35, 35.2 + (i // 2) * 1.0, 1.2, 0.8),
      "M-10", "pulmon", "S", 0, "W-MAN 3")
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

# ala este
E("M12-1", "Soldadora circunferencial Firesafer FS-SWH", R(37.2, 43.2, 39.2, 44.6), "M-12", "sold_circ", "S", 1,
  _T + " (criterio)")
E("M12-2", "Soldadora circunferencial Firesafer FS-SWH", R(40.0, 43.2, 42.0, 44.6), "M-12", "sold_circ", "S", 1,
  _T + " (criterio)")
E("M13-1", "Medidor de espesor Melisam MR017 sobre mesa", R(42.7, 44.0, 43.9, 44.6), "M-13", "mesa_control", "S", 1,
  "Mesa 1,2 × 0,6 (W-CAR 1)")
carros_fila("PU-S", "«Espesor OK» -> prueba hidráulica", 42.6, 41.2, 1, "M-13", fuente="W-MAN 12")
carros_fila("PU-RT", "Retenidos del control de espesor", 44.4, 41.2, 2, "M-13", (0.61, 1.28), True, "W-MAN 12")
E("M14-1", "Banco de prueba hidráulica Firesafer FS-JD12A", R(45.5, 43.5, 47.55, 44.6), "M-14", "ph", "S", 1,
  "Catálogo Firesafer, pág. 11: 2050 × 1100 × 1350 mm")
E("M14-2", "Banco de prueba hidráulica Firesafer FS-JD12A", R(48.3, 43.5, 50.35, 44.6), "M-14", "ph", "S", 1,
  "Catálogo Firesafer, pág. 11: 2050 × 1100 × 1350 mm")
carros_fila("PU-6", "Probados (mojados) -> secado", 45.6, 41.2, 2, "M-14", fuente="W-MAN 13")
for i in range(4):
    E(f"M15-{i + 1}", "Secadora de cilindros Yukon", Rw(50.9 + i * 1.0, 43.8, 0.70, 0.68), "M-15", "secadora", "S",
      1 if i % 2 == 0 else 0, "ET: 700 × 680 × 1750 mm")
carros_fila("PU-7", "Secos con tapón -> granallado", 50.9, 41.2, 2, "M-15", fuente="W-MAN 14")
E("M16-1", "Granalladora de rodillos Airblast G-100 (rodillos de entrada y salida incluidos)", R(56.0, 43.3, 60.5, 44.6),
  "M-16", "granalladora", "S", 1, "Cotización Airblast: 4500 × 1300 × 2200 mm")
E("M17-1", "Mesa de inspección iluminada", R(62.0, 44.0, 63.2, 44.6), "M-17", "inspeccion", "S", 1, "W-MAN 16")
for i in range(3):
    E(f"M17-J{i + 1}", "Jaula «a corregir» / «re-granallar» / «descarte»", Rw(61.8 + i * 1.1, 37.2, 1.0, 1.0), "M-17",
      "jaula", "N", 0, "W-MAN 16")
E("M18-1", "Mesa de corrección con amoladora y extracción", R(62.0, 40.2, 63.2, 40.8), "M-17", "banco_sold", "S", 1,
  "W-MAN 17")
carros_fila("PU-CO", "Carro de corregibles", 63.6, 40.2, 1, "M-17", fuente="W-MAN 16")
E("M19-C", "Cuelgue en el riel de la pintura (operario)", R(65.0, 42.0, 65.9, 44.6), "M-17", "banco", "O", 1,
  "W-MAN 18: carga de la línea")

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
X16, X13, X11, XPT = 24.7, 39.7, 55.2, 67.6
Z("C-16", "16 Depósito de PT de carros: liberados, retenidos y rechazados", R(X16, 3.5, X13, Y_S), "PT",
  _W + " 16: ≈ 200 m² (retenidos 9 × 10, liberados 6 × 10, rechazados 5 × 3 y pasillo hasta la puerta)", 150)
Z("C-16P", "16 Pasillo de carga del depósito de carros y zona de rechazados", R(X16, 0, X13, 3.5), "PT",
  "W-CAR 16: pasillo entre las zonas y la puerta; zona de rechazados ≈ 5 × 3 m", 50)
Z("C-17", "17 Ensayos de lote (recinto de descarga, mesa y balanza)", R(X13, 0, X13 + 15.5, 4.5), "CAR",
  _W + " 17: ≈ 15,5 × 4,5 m (el patio de rodadura va afuera)", 70)
Z("C-14", "14 Sala del ensayo de pérdidas (paneles aislantes, split)", R(X13, 4.5, X13 + 5.0, 9.5), "CAR",
  _W + " 14: 5,0 × 5,0 m", 25, tipo="local")
Z("C-15", "15 Etiquetado e inspección final", R(X13, 9.5, X13 + 5.0, Y_S), "CAR",
  _W + " 15: ≈ 3,5 × 2,5 m, más el paso de los carros al depósito 16", 9)
Z("C-13", "13 Carga, armado y presurización", R(X13 + 5.0, 7.0, X11, Y_S), "CAR", _W + " 13: ≈ 10 × 6 m", 60)
Z("C-1314", "Paso de la carga a la sala de pérdidas y a los ensayos", R(X13 + 5.0, 4.5, X11, 7.0), "CAR",
  "W-CAR 13, 14 y 17: recorrido de los carros de la muestra")
X12 = X11 + 6.2
Z("C-12", "12 Recepción de pintados, cambio de juego y pulmón de pintados", R(X11, 0, X12, Y_S), "CAR",
  _W + " 12: ≈ 79 m²; al lado del puesto 13 (W-CAR); descarga por P4 con el autoelevador del pasillo principal", 79)
Z("C-11", "11 Pulmón de despacho a la pintura tercerizada (120 carros)", R(X12, 0, XPT, Y_S), "CAR",
  _W + " 11: ≈ 10 × 7 m; carga por P4 desde el pasillo principal («más el de la planta», W-CAR 11)", 70)
Z("PT-M", "Depósito de PT de manuales: 7 calles de 10 posiciones (pallets de a 2)", R(XPT, 0, LX, Y_S), "PT",
  "X-DT Almacén PT filas 127-128: 56 + 72 pallets de a 2 = 64 posiciones (115,2 m² con su pasillo)", 84)

E("C17-1", "Recinto de descarga cerrado (alto 3 m) con colector de mangas", R(X13 + 0.3, 0.3, X13 + 12.3, 3.3), "C-17",
  "cabina_muestras", "N", 0, "W-CAR 17: 12 × 3 m")
E("C17-2", "Mesa de medición y perchero de mangas", R(X13 + 12.8, 2.2, X13 + 14.8, 3.0), "C-17", "banco", "N", 1,
  "W-CAR 17: 2,0 × 0,8 m")
E("C17-3", "Balanza de plataforma con rampa", R(X13 + 12.9, 0.3, X13 + 14.1, 1.5), "C-17", "balanza", "N", 0,
  "W-CAR 17: 1,2 × 1,2 m")
E("C14-1", "Lugares numerados para 30 carros", R(X13 + 0.3, 4.8, X13 + 4.7, 9.2), "C-14", "carros", "N", 0,
  "W-CAR 14: 0,5 m² por carro")
E("C15-1", "Lugar de 2 carros y mesa de calcomanías", R(X13 + 0.4, 10.0, X13 + 3.4, 11.2), "C-15", "etiquetadora",
  "N", 1, "W-CAR 15: 2 × (1,0 × 0,8) + mesa 1,2 × 0,6")
E("C15-2", "Zona de no conforme (roja)", R(X13 + 3.6, 9.7, X13 + 4.8, 11.2), "C-15", "jaula", "N", 0,
  "W-CAR 15: 1,5 × 1,0 m")
E("C13-1", "Estación A: lugar del carro", R(X11 - 2.6, 8.4, X11 - 0.2, 10.6), "C-13", "carros", "N", 1, "W-CAR 13: 2,4 × 2,2")
E("C13-2", "Estación B: balanza con rampa y Yukon", R(X13 + 9.0, 8.0, X13 + 12.0, 10.6), "C-13", "carga_polvo",
  "N", 1, "W-CAR 13: 3,0 × 2,6 m")
E("C13-3", "Bastidor del big bag con tolva (alto 2,8 m)", R(X13 + 9.7, 11.9, X13 + 11.3, Y_S), "C-13", "tanque", "N", 0,
  "W-CAR 13: 1,6 × 1,2 m, con acceso para el autoelevador", ae=True)
E("C13-4", "Estación C: lugar del carro", R(X13 + 5.6, 8.4, X13 + 7.9, 10.6), "C-13", "carros", "N", 1,
  "W-CAR 13: 2,3 × 2,2")
E("C13-5", "Batería de nitrógeno en jaula, con manifold", R(X13 + 5.4, 12.5, X13 + 8.0, Y_S - 0.1), "C-13",
  "bateria_gas", "N", 0, "W-CAR 13: 2,6 × 0,9 m")
E("C13-6", "Estanterías de válvulas, mangas, ruedas y ejes", R(X13 + 5.4, 7.1, X13 + 11.4, 7.6), "C-13",
  "estanteria", "N", 0, "W-CAR 13: 3 × (2,0 × 0,5 m)")
E("C16-1", "Zona de liberados (100 carros)", R(X16 + 0.2, 3.7, X16 + 6.0, Y_S - 0.2), "C-16", "carros", "N", 0,
  "W-CAR 16: ≈ 6 × 10 m")
E("C16-2", "Zona de retenidos (180 carros)", R(X16 + 6.2, 3.7, X13 - 0.2, Y_S - 0.2), "C-16", "carros", "N", 0,
  "W-CAR 16: ≈ 9 × 10 m (aquí 8,6 × 9,6)")
E("C16-3", "Zona de rechazados (roja)", R(X13 - 5.2, 0.2, X13 - 0.2, 3.2), "C-16P", "carros", "N", 0,
  "W-CAR 16: ≈ 5 × 3 m")
E("C11-1", "Filas de carros a pintura por modelo y semana (120 carros)", R(X12 + 0.1, 0.2, XPT - 0.1, 10.2),
  "C-11", "carros", "N", 0, "W-CAR 11: ≈ 10 × 6 m (aquí 6,0 × 10,0)")
E("C11-2", "Pasillo de las filas a la puerta (carros a mano)", R(X12 + 0.1, 10.4, XPT - 0.1, 11.4), "C-11", "carros",
  "N", 0, "W-CAR 11: ≈ 10 × 1 m")
E("C12-1", "Pulmón de pintados (120 carros)", R(X11 + 0.1, 0.2, X12 - 0.1, 11.6), "C-12", "carros", "N", 0,
  "W-CAR 12: ≈ 10 × 7 m (aquí 6,0 × 11,4)")
E("C12-2", "Lugar de cambio de juego 1 (crique, zorra, cajones)", R(X11 + 0.1, 11.8, X11 + 2.1, Y_S - 0.1), "C-12",
  "carros", "N", 0, "W-CAR 12: 2,0 × 1,5 m")
E("C12-3", "Lugar de cambio de juego 2", R(X11 + 2.15, 11.8, X11 + 4.15, Y_S - 0.1), "C-12", "carros", "N", 0,
  "W-CAR 12: 2,0 × 1,5 m")
E("C12-4", "Rechazados del pintor (rojo)", R(X11 + 4.2, 11.8, X12 - 0.1, Y_S - 0.1), "C-12", "jaula", "N", 0,
  "W-CAR 12: ≈ 2 × 1,5 m")
# PT de manuales: 7 calles de 10 pallets de fondo, con la boca sobre el pasillo principal
for i in range(7):
    E(f"PTM-{i + 1}", "Calle de 10 posiciones de piso (2 pallets apilados por posición)",
      Rw(XPT + 0.2 + i * 1.15, 0.6, 1.05, 12.8), "PT-M", "pallets_pt", "N", 0, "X-DT Almacén PT", ae=True)

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

# ================================================================ PUERTAS DE LA NAVE
PUERTAS += [
    Puerta("P1", "O", Y_S, Y_AE - 0.2, 4.8, "porton", "Materia prima: del playón oeste al pasillo principal"),
    Puerta("P2", "S", X16 + 1.0, X16 + 5.0, 4.5, "porton", "Despacho de carros (depósito 16)"),
    Puerta("P4", "E", Y_S, Y_AE - 0.2, 4.8, "porton",
           "Playa este: despacho de PT de manuales y camión de la pintura tercerizada de carros (11 y 12)"),
    Puerta("P5", "S", X13 + 14.2, X13 + 15.3, 2.1, "peatonal", "Patio de ensayos de lote (17)"),
    Puerta("PE-1", "O", 8.6, 9.7, 2.1, "emergencia", "Salida del ángulo SO (extremo de la senda de los locales)"),
    Puerta("PE-3", "N", 3.0, 4.2, 2.1, "emergencia", "Salida del almacén (extremo norte del pasillo AL-B)"),
    Puerta("PE-4", "S", 32.0, 33.2, 2.1, "emergencia", "Salida del depósito de carros"),
    Puerta("PN-1", "N", 19.6, 21.0, 2.1, "peatonal", "Sala técnica y supervisión"),
    Puerta("PN-2", "N", 24.6, 25.8, 2.1, "peatonal", "Primeros auxilios (camilla, 1,10 m)"),
    Puerta("PN-3", "N", 46.8, 48.6, 2.1, "peatonal", "Paso de personal desde los vestuarios"),
    Puerta("PN-4", "N", 49.8, 51.0, 2.1, "emergencia", "Salida por el vestíbulo del personal"),
]

# ================================================================ ADMINISTRACIÓN Y SERVICIOS AL PERSONAL (anexo norte)
# Dotación 2035 sin recargas (X-DT): turno mañana 30 operarios + 1 encargado + 5 de oficina = 36 (32 H y 4 M);
# turno tarde 6 operarios + 1 encargado + 1 administrativo = 8. Sanitarios (Dec. 351/79 art. 49, con las fórmulas de
# la X-DT, hoja Servicios y Oficinas) para 32 H y 4 M: H 2 inodoros, 3 orinales, 4 lavabos y 3 duchas; M 1, 1 y 1.
# Armarios dobles (ropa de calle y de trabajo): uno por persona de planta de los dos turnos: 38 = 34 H + 4 M.
# Comedor: 36 personas en 2 tandas = 18 plazas (X-DT: tandas de 30 minutos).
YA0, YA1 = LY + MURO, LY + MURO + 11.2          # anexo de 11,2 m de fondo
XA0, XA1 = 17.0, 52.0
Y_PC0, Y_PC1 = YA0 + 5.2, YA0 + 6.8             # pasillo de 1,6 m
ADMIN = []                                      # locales del anexo (misma clase Zona)
MOB = []                                        # muebles: (tipo de planta/mobiliario.py, R, frente, n)


def A(cod, nombre, r, fuente="", req=0.0, cat="ADM"):
    ADMIN.append(Zona(cod, nombre, r, cat, fuente, req, "local"))


def MB(tipo, r, frente="S", n=1):
    MOB.append((tipo, r, frente, n))


_DT = "X-DT hoja Servicios y Oficinas, 2035 sin recargas"
A("AD-ST", "Sala técnica: calidad, PCP y encargado de turno", R(XA0, YA0, 23.4, Y_PC0),
  _DT + ": responsable de calidad, PCP y encargado (3 puestos, vista a la planta)")
A("AD-PA", "Primeros auxilios; consultorio de medicina laboral y de higiene y seguridad", R(23.4, YA0, 27.0, Y_PC0),
  "Dec. 1338/96: servicios de medicina del trabajo y de higiene y seguridad (externos)")
A("AD-EP", "Pañol de EPP (ventanilla a la planta)", R(27.0, YA0, 29.2, Y_PC0), "W-MAN y W-CAR: EPP de cada puesto")
A("AD-VM", "Vestuario y sanitarios de mujeres", R(29.2, YA0, 33.4, Y_PC0),
  _DT + ": 4 mujeres en el turno más numeroso; 4 armarios", cat="SAN")
A("AD-SH", "Sanitarios de varones", R(33.4, YA0, 38.4, Y_PC0),
  _DT + ": 32 varones en el turno más numeroso (Dec. 351/79 art. 49)", cat="SAN")
A("AD-VH", "Vestuario de varones (34 armarios dobles)", R(38.4, YA0, 46.4, Y_PC0),
  _DT + ": 34 varones de planta en los dos turnos", cat="SAN")
A("AD-PP", "Paso de personal a la planta", R(46.4, YA0, 49.0, Y_PC0), "Croquis del usuario (paso de personal)",
  cat="CIRC")
A("AD-VE", "Vestíbulo de ingreso del personal (reloj de fichado y cartelera)", R(49.0, YA0, XA1, YA1),
  "Ingreso lateral de operarios, separado del de visitas (croquis del usuario)", cat="CIRC")
A("AD-PC", "Pasillo de la administración (1,6 m)", R(XA0, Y_PC0, 49.0, Y_PC1), "", cat="CIRC")
A("AD-JP", "Jefatura de planta", R(XA0, Y_PC1, 21.0, YA1), _DT + ": jefe de planta / producción")
A("AD-SR", "Sala de reuniones (8 personas)", R(21.0, Y_PC1, 26.0, YA1), "Croquis del usuario")
A("AD-HA", "Hall de recepción y espera de visitas", R(26.0, Y_PC1, 31.0, YA1), "Croquis del usuario", cat="CIRC")
A("AD-BA", "Baño accesible (visitas y oficinas)", R(31.0, Y_PC1, 33.2, YA1), "Ley 24.314 y Dec. 914/97", cat="SAN")
A("AD-AD", "Administración: ventas y cobranzas, compras y administrativo de la tarde", R(33.2, Y_PC1, 38.2, YA1),
  _DT + ": 2 puestos a la mañana y 1 a la tarde (comparte escritorio)")
A("AD-AR", "Archivo: legajos, protocolos de lote y documentación de calidad", R(38.2, Y_PC1, 40.2, YA1), "")
A("AD-CO", "Comedor (18 plazas) con office", R(40.2, Y_PC1, 46.8, YA1),
  _DT + ": 36 personas en 2 tandas de 30 minutos = 18 plazas")
A("AD-LI", "Limpieza y termotanque", R(46.8, Y_PC1, 49.0, YA1), "")

# puertas del anexo: (x, y, ancho, muro 'h' o 'v', hacia dónde abre +1/-1)
PUERTAS_ADMIN = [
    (21.6, Y_PC0, 0.9, "h", -1), (25.4, Y_PC0, 0.9, "h", -1), (27.6, Y_PC0, 0.8, "h", -1), (32.3, Y_PC0, 0.9, "h", -1),
    (36.9, Y_PC0, 0.9, "h", -1), (39.0, Y_PC0, 0.9, "h", -1), (47.0, Y_PC0, 1.2, "h", -1),
    (17.6, Y_PC1, 0.9, "h", 1), (24.6, Y_PC1, 0.9, "h", 1), (27.5, Y_PC1, 1.6, "h", 1), (31.6, Y_PC1, 0.9, "h", 1),
    (36.9, Y_PC1, 0.9, "h", 1), (38.6, Y_PC1, 0.8, "h", 1), (43.2, Y_PC1, 1.2, "h", 1), (47.2, Y_PC1, 0.8, "h", 1),
    (49.0, Y_PC0 + 0.3, 1.2, "v", -1),
]
PUERTAS_EXT_ADMIN = [("H1", "N", 27.6, 29.4, "Ingreso de visitas y oficinas (rampa accesible)"),
                     ("H2", "E", YA0 + 7.2, YA0 + 8.8, "Ingreso del personal")]

# mobiliario (planta/mobiliario.py)
MB("escritorio", R(17.4, YA0 + 3.0, 19.0, YA0 + 3.9), "S")
MB("escritorio", R(19.4, YA0 + 3.0, 21.0, YA0 + 3.9), "S")
MB("escritorio", R(21.4, YA0 + 3.0, 23.0, YA0 + 3.9), "S")
MB("mesa", R(18.4, YA0 + 0.7, 21.4, YA0 + 1.7), "S", 6)
MB("pizarra", R(17.15, YA0 + 0.4, 17.45, YA0 + 2.4), "E")
MB("camilla", R(23.6, YA0 + 2.9, 24.3, YA0 + 4.8), "E")
MB("botiquin", R(26.3, YA0 + 4.4, 26.85, YA0 + 5.0), "S")
MB("escritorio", R(25.0, YA0 + 1.2, 26.6, YA0 + 2.1), "N")
MB("lavabos", R(23.6, YA0 + 0.15, 24.6, YA0 + 0.7), "N", 1)
MB("estanteria", R(27.1, YA0 + 1.0, 27.7, YA0 + 4.0), "E")
MB("estanteria", R(28.5, YA0 + 1.0, 29.1, YA0 + 4.0), "O")
MB("ventanilla", R(27.4, YA0, 28.8, YA0 + 0.3), "S")
MB("armarios", R(29.4, YA0 + 0.1, 31.8, YA0 + 0.6), "N", 4)
MB("banco_vest", R(29.6, YA0 + 1.4, 31.6, YA0 + 1.8), "N")
MB("inodoro", R(32.4, YA0 + 0.1, 33.3, YA0 + 1.5), "O")
MB("duchas", R(32.4, YA0 + 1.9, 33.3, YA0 + 2.8), "O", 1)
MB("lavabos", R(29.4, Y_PC0 - 0.65, 30.4, Y_PC0 - 0.1), "S", 1)
MB("inodoro", R(33.5, YA0 + 0.1, 34.4, YA0 + 1.5), "N")
MB("inodoro", R(34.5, YA0 + 0.1, 35.4, YA0 + 1.5), "N")
MB("mingitorios", R(35.7, YA0 + 0.1, 37.5, YA0 + 0.5), "N", 3)
MB("duchas", R(37.45, YA0 + 1.7, 38.35, YA0 + 4.2), "O", 3)
MB("lavabos", R(33.6, Y_PC0 - 0.65, 36.0, Y_PC0 - 0.1), "S", 4)
MB("armarios", R(38.8, YA0 + 0.1, 46.0, YA0 + 0.6), "N", 12)
MB("armarios", R(39.4, YA0 + 2.3, 46.0, YA0 + 2.8), "S", 11)
MB("armarios", R(39.4, YA0 + 2.8, 46.0, YA0 + 3.3), "N", 11)
MB("banco_vest", R(39.2, YA0 + 1.4, 45.6, YA0 + 1.8), "N")
MB("banco_vest", R(40.2, YA0 + 4.2, 45.6, YA0 + 4.6), "S")
MB("lavabos", R(46.5, YA0 + 1.4, 47.05, YA0 + 3.6), "E", 3)
MB("pizarra", R(48.6, YA0 + 1.6, 48.9, YA0 + 3.6), "O")
MB("reloj", R(51.4, YA0 + 6.0, 51.9, YA0 + 7.0), "O")
MB("pizarra", R(51.6, YA0 + 2.6, 51.9, YA0 + 4.6), "O")
MB("escritorio", R(17.3, YA1 - 1.2, 18.9, YA1 - 0.3), "S")
MB("archivo", R(19.6, YA1 - 0.75, 20.8, YA1 - 0.15), "S", 2)
MB("mesa", R(22.3, Y_PC1 + 1.5, 24.7, Y_PC1 + 2.6), "S", 8)
MB("sillas", R(26.1, Y_PC1 + 1.5, 26.6, Y_PC1 + 3.5), "E", 4)
MB("inodoro_acc", R(31.1, Y_PC1 + 0.9, 33.1, YA1 - 0.1), "N")
MB("escritorio", R(33.5, YA1 - 1.2, 35.1, YA1 - 0.3), "S")
MB("escritorio", R(35.6, YA1 - 1.2, 37.2, YA1 - 0.3), "S")
MB("archivo", R(33.3, Y_PC1 + 0.2, 34.1, Y_PC1 + 0.8), "N", 2)
MB("archivo", R(38.3, Y_PC1 + 1.2, 38.9, YA1 - 0.3), "E", 5)
MB("mesa", R(40.8, Y_PC1 + 2.5, 42.6, Y_PC1 + 3.3), "S", 6)
MB("mesa", R(43.0, Y_PC1 + 2.5, 44.8, Y_PC1 + 3.3), "S", 6)
MB("mesa", R(40.8, Y_PC1 + 0.9, 42.6, Y_PC1 + 1.7), "S", 6)
MB("mesada", R(45.1, Y_PC1 + 0.2, 46.7, Y_PC1 + 0.8), "N", 2)
MB("heladera", R(45.9, YA1 - 0.8, 46.7, YA1 - 0.1), "S")
MB("carro_limpieza", R(47.0, YA1 - 1.3, 47.8, YA1 - 0.2), "S")
MB("lavadero", R(47.9, YA1 - 1.3, 48.9, YA1 - 0.2), "S")

# ================================================================ EXTERIOR (calle al norte)
EXTERIOR = [
    ("CALLE", "Calle (frente norte)", R(-27.0, 71.5, 104.0, 77.0)),
    ("VE", "Vereda", R(-27.0, 69.0, 104.0, 71.5)),
    ("EST", "Estacionamiento de visitas y personal (incluye 1 cajón accesible de 3,5 × 5,0 m)", R(17.0, 60.0, 52.0, 69.0)),
    ("PO", "Playón oeste: descarga de MP (franja de 15 × 5 m de W-CAR) y maniobra", R(-22.0, 6.0, -0.2, 26.0)),
    ("PS", "Playa sur: despachos, pintura tercerizada, gases y patio de ensayos", R(-22.0, -22.0, 98.0, -0.2)),
    ("PE", "Playa este: despacho de PT de manuales", R(LX + 0.2, 6.0, 98.0, 26.0)),
    ("PEN", "Patio de ensayos de lote (rodadura, plataforma de caída y pared)", R(46.0, -12.0, 58.0, -2.0)),
    ("JG", "Jaula de gases ventilada (Arcal 21 y N₂ en packs con manifold)", R(60.0, -4.2, 67.0, -1.2)),
    ("SC", "Contenedores de scrap y chatarra", R(-12.0, 28.0, -4.0, 32.0)),
]
CAMINO_CAMIONES = [(-26.0, 69.0), (-26.0, -18.0), (102.0, -18.0), (102.0, 69.0)]
