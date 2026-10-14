"""Modelo del layout de la planta FLAMA S.A. al año 10 (2035) - versión 8: procesos de los Word y almacenes v5.

Medidas en METROS, origen en el eje A-1 (esquina SO, cara interior de columnas), X al este, Y al norte.
Calle al sur. Fuente única de los planos (DIR, operaciones, materiales, formal) y de la memoria de cálculo.

Fuentes de la versión 8 (todas en referencias/ o entregadas por el grupo)
------------------------------------------------------------------------
* W-MAN  PROCESO_DE_MANUALES_EXPLICATIVO (orden, disposición, carros y transportadores de cada puesto).
* W-CAR  PROCESO_CARRO_EN_LIMPIO (puestos 1 a 9 con su tabla de espacios en m).
* W-REC  PROCESO_DE_RECARGAS_EXPLICATIVO (zona general, recinto de polvo y fuera de línea; gases).
* X-MAN  Dimensionamiento_Manuales.xlsx, hoja Resumen Capacidad 2035 (34 puestos, 2 turnos).
* X-DT   Dimensionamiento_TecnicoV2.xlsx (carros: 9 máquinas; recargas: 22 máquinas; Almacén PT).
* X-ALM  Dimensionamiento_Almacenes_MP_v5.xlsx (secciones de almacén, posiciones, m² netos y brutos).

Concepto
--------
* Nave 88 × 44 m (11 módulos de 8 m; columnas centrales en el eje B). Pasillo central E-O con senda peatonal.
* Una sola recepción de MP (W-MAN: cuarentena compartida con carros): alero norte -> P1 -> almacén de MP de tres
  calles de 5 m (W-CAR: radio de giro del Heli CPCD50 + pallet + margen). El polvo, el embalaje y los revendidos
  entran por el muelle P3; los gases van a la jaula exterior con packs y manifold (W-MAN).
* Banda norte, en el orden de W-MAN: corte de chapa (guillotina compartida con carros y marcado de carros en su
  rampa trasera), corte de tubo, embutido, celda de cuello (numerado, muesca y soldadura pegados), cilindrado y
  soldadura longitudinal con el carro FCHP20505 entre las dos, encastre, bordoneado, 2 soldaduras circ., control de
  espesor con zona de retenidos, 2 PH con decantación, 4 secadoras, granallado de rodillos y detección, que cuelga
  el cilindro en el riel aéreo de pintura (precalentamiento, cabina, curado, descarga).
* Banda sur: recargas (zona general, recinto de polvo con antecámara y 3 pasaplatos, fuera de línea), carros
  (puestos 3 a 9 en U, terminación y pulmón al muelle), PT y el muelle P3, y la terminación de manuales, que termina
  en el embalaje junto a la descarga de pintura, donde también se encajonan los cilindros vacíos (W-MAN).
"""

from dataclasses import dataclass

# ---------------------------------------------------------------- nave
NAVE_L, NAVE_A = 88.0, 44.0
MODULO = 8.0
ALTURA_LIBRE = 8.0
ALTURA_ALERO = 7.2
EJES_X = [i * MODULO for i in range(int(NAVE_L / MODULO) + 1)]   # 0 ... 88
EJES_Y = [0.0, 19.0, NAVE_A]          # fila central de columnas en el eje B (borde sur del pasillo)
COL = 0.40
MURO = 0.20

# terreno 170 × 125 m, calle al sur
TERRENO = (-40.0, -62.0, 130.0, 63.0)


@dataclass
class R:
    """Rectángulo x0, y0, x1, y1 (m)."""
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
class Sector:
    cod: str
    nombre: str
    rect: R
    cat: str                 # MP, PROD, PINT, TERM, PT, CAL, SERV, AUX, CIRC, RC, EXT
    seccion: str = ""        # S1 1 kg, S2 manuales, S3 rodantes, S4 tercerizados, RC, común
    nota: str = ""
    area_req: float = 0.0    # m² requeridos por la fuente (0 = no aplica)


@dataclass
class Equipo:
    cod: str
    nombre: str
    rect: R
    sector: str
    op: int = 1              # operarios por turno (turno mañana)
    kw: float = 0.0          # potencia instalada estimada
    aire: bool = False
    n2: bool = False
    gas: bool = False
    agua: bool = False       # consumo / vertido de agua
    polvo: bool = False      # extracción de polvo o humos
    fuente: str = ""         # de dónde sale la medida
    forma: str = "rect"      # rect | circ | jaula | rack | carro
    tipo: str = ""           # símbolo de detalle (planta/simbolos.py); vacío = según el nombre
    frente: str = ""         # lado del operario: S, E, N, O
    paso: str = ""           # número de operación en el plano (globo)


@dataclass
class Mueble:
    tipo: str                # función de planta/mobiliario.py
    rect: R
    frente: str = "S"        # lado de uso / acceso (S, E, N, O)
    n: int = 1               # cantidad de módulos (armarios, inodoros, sillas...) o variante


@dataclass
class Puerta:
    cod: str
    muro: str                # N, S, E, O (de la nave) o texto de anexo
    a: float                 # coordenada inicial sobre el muro (x para N/S, y para E/O)
    b: float
    alto: float
    tipo: str                # porton, muelle, peatonal, emergencia
    uso: str = ""
    x_muro: float = None     # para puertas de anexos: coordenada fija del muro


@dataclass
class Flujo:
    cat: str                 # MP, SE, PT, SCRAP, TL (riel aéreo cargado), RET (riel vacío), EFL-L, EFL-G
    pts: list
    rot: str = ""            # rótulo
    seccion: str = ""


@dataclass
class Pasillo:
    cod: str
    rect: R
    tipo: str                # PM (materiales/autoelevador), PP (personal), PO (operarios y carros a mano)
    ancho: float = 0.0
    nota: str = ""


@dataclass
class Pulmon:
    cod: str
    rect: R
    guarda: str
    viene: str
    va: str
    carros: int = 2
    orient: str = "h"        # carros en fila horizontal (h) o vertical (v)


# ============================================================ PASILLOS
_AE = "5,0 m: radio de giro del Heli CPCD50 (2,93 m) + pallet (1,2 m) + 0,8 m de margen (W-CAR, tabla 5)"
PASILLOS = [
    Pasillo("PC", R(2.0, 19.2, 74.6, 23.0), "PM", 3.8,
            "Pasillo central: autoelevador doble sentido; por acá pasan los big bags y la pintura en polvo desde el "
            "depósito (calle AC), los casquetes y las barras de carros y el carro de abastecimiento de cada turno"),
    Pasillo("PP", R(0.3, 23.2, 74.6, 24.4), "PP", 1.2,
            "Senda peatonal separada del carril de autoelevador por una defensa con aberturas en los cruces"),
    # ---- almacén de MP: tres calles de 5 m que se cierran en la cabecera AN y en el pasillo central
    Pasillo("A1", R(1.6, 19.2, 6.6, 43.6), "PM", 5.0,
            "Calle de recepción: alero -> P1 -> cuarentena y retenidos (este) e insumos de montaje (oeste). " + _AE),
    Pasillo("A2", R(10.6, 19.2, 15.6, 37.2), "PM", 5.0,
            "Calle de chapa: paquetes de hojas de manuales (oeste) y calle de chapa de carros (este). " + _AE),
    Pasillo("A3", R(19.6, 19.2, 24.6, 37.2), "PM", 5.0,
            "Calle de carga a máquina: cantiléver y casquetes (oeste); mesa elevadora de la guillotina, contenedor del "
            "láser y cajón de alimentación de 6,5 m (este). " + _AE),
    Pasillo("AN", R(6.6, 37.2, 24.6, 42.2), "PM", 5.0,
            "Cabecera del almacén: une A1, A2 y A3; porta-flejes y racks de soldadura al norte; el rollo va con el "
            "espolón al desbobinador del embutido (extremo este)"),
    # ---- banda norte: calles de operarios y carros a mano
    Pasillo("PO-1", R(40.0, 24.4, 41.0, 34.6), "PO", 1.0,
            "Calle de operarios de la senda a la línea principal; ventanilla del pañol"),
    Pasillo("PO-2", R(40.0, 33.6, 87.6, 34.6), "PO", 1.0,
            "Calle sur de la línea principal: carros FCHP20505 entre puestos; termina en la salida SE-6"),
    Pasillo("PO-3", R(24.6, 39.3, 87.6, 40.3), "PO", 1.0,
            "Calle norte: celda de cuello, embutido, compresores; vuelta de los corregidos; termina en la salida SE-5"),
    Pasillo("PO-5", R(68.6, 24.4, 70.0, 33.6), "PO", 1.4, "Calle de la senda a la línea este y al tablero ST-I"),
    Pasillo("PO-6", R(74.6, 24.4, 76.0, 33.6), "PO", 1.4,
            "Continuación de PO-PI hasta la línea principal (operarios de pintura, granallado y detección)"),
    Pasillo("PO-7", R(61.1, 34.6, 62.1, 39.3), "PO", 1.0, "Paso de operarios entre secado y granallado (PO-2 <-> PO-3)"),
    Pasillo("PO-8", R(28.9, 35.4, 33.6, 36.6), "PO", 1.2,
            "Calle de los carros de tramos (láser -> encastre) y de la zorra del procesado AL-PR / AL-PT"),
    Pasillo("PO-9", R(28.9, 36.6, 29.9, 39.3), "PO", 1.0, "Une PO-8 con la calle norte PO-3 (zorra del procesado)"),
    # ---- pintura
    Pasillo("PO-PI", R(74.6, 0.6, 76.0, 24.4), "PO", 1.4,
            "Calle de operarios de pintura: remate este del pasillo central; los vacíos la cruzan al embalaje y los "
            "terminados suben por ella a la calle AT2"),
    Pasillo("PO-PS", R(74.6, 0.6, 87.1, 2.2), "PO", 1.6, "Paso al sur de la descarga de pintura hasta la salida SE-7"),
    # ---- banda sur: carros
    Pasillo("PO-CW", R(18.0, 5.4, 21.3, 19.2), "PM", 3.3,
            "Calle oeste de carros: pasillo central <-> PO-C; autoelevador de carros y recargas (barras al puesto "
            "8.1) y carro de casquetes"),
    Pasillo("PO-C", R(18.0, 5.4, 41.0, 8.0), "PM", 2.6,
            "Calle de carros entre las filas y el bloque sur: kits, inspección -> PH, carros al muelle"),
    Pasillo("PO-CR", R(21.3, 13.2, 41.0, 14.2), "PO", 1.0, "Calle interior de la U de carros (operarios)"),
    Pasillo("PO-CN", R(41.0, 6.8, 42.4, 19.2), "PO", 1.4,
            "Calle este de carros: vuelven los carros pintados y llega el big bag de ABC 90 a la terminación de carros"),
    # ---- PT y expedición
    Pasillo("T1", R(43.6, 6.8, 46.9, 19.2), "PM", 3.3, "Calle de rack de PT (oeste): pasillo central <-> expedición"),
    Pasillo("T2", R(49.1, 6.8, 52.4, 19.2), "PM", 3.3,
            "Calle de rack de PT (este): envolvedora -> racks; pasillo central <-> muelle P3"),
    Pasillo("EX", R(41.0, 2.4, 53.6, 6.8), "PM", 4.4,
            "Calle de expedición: une T1, T2, PO-C, PO-CN, AT y AC con el muelle P3"),
    # ---- terminación y embalaje
    Pasillo("AT", R(53.6, 1.8, 74.6, 4.4), "PM", 2.6,
            "Calle de embalaje: pallets de la envolvedora al PT; big bags del muelle al depósito; rack de embalaje"),
    Pasillo("AC", R(53.6, 4.4, 55.0, 19.2), "PO", 1.4,
            "Calle oeste de terminación: pasillo central <-> AT; big bags al carro y pintura en polvo desde el depósito"),
    Pasillo("AT2", R(55.0, 13.0, 74.6, 15.6), "PO", 2.6,
            "Calle de terminación: terminados pintados de la descarga a la carga; sanitarios y ducha de emergencia"),
    # ---- recargas
    Pasillo("RC-N", R(11.0, 0.5, 12.2, 19.2), "PO", 1.2,
            "Corredor de recargas: pasillo central <-> salida SE-8; une la zona general este y oeste y el recinto"),
    Pasillo("RC-Q", R(0.5, 17.6, 11.0, 18.7), "PO", 1.1, "Corredor norte de recargas (fuera de línea); salida SE-11"),
]

# sendas peatonales: se calculan al final del módulo en cada cruce de un hilo con un flujo
SENDAS = []

# zona sin autoelevador (banda norte al este del almacén de MP): sólo carros a mano y transpaleta
ZONA_SIN_AE = R(24.7, 24.5, 87.7, 43.7)

# ============================================================ SECTORES
_V5 = "Dimensionamiento_Almacenes_MP_v5"
SECTORES = [
    # ---------------- almacén de MP (una sola recepción: cuarentena compartida con carros, W-MAN)
    Sector("AL-MM", "Insumos de montaje (manuales)", R(0.3, 24.6, 1.6, 35.6), "MP", "S1 / S2",
           f"{_V5}: 31 posiciones, 13,8 m² netos (20,7 brutos); rack de 4 módulos × 2 × 4 niveles = 32: válvulas, "
           "manómetros, toberas, mangueras y soportes; salen una vez por turno en el carro de abastecimiento", 13.8),
    Sector("AL-ID", "Identificación (etiquetas, obleas, sellos)", R(0.3, 35.8, 1.6, 37.3), "MP", "común",
           f"{_V5}: 9 lugares, 3,0 m² netos; estantería de 5 niveles; sellos y obleas numerados bajo llave", 3.0),
    Sector("AL-MC", "Insumos de montaje (carros)", R(0.3, 37.5, 1.6, 40.4), "MP", "S3",
           f"{_V5}: 7 posiciones, 4,8 m² netos; rack de 1 módulo × 2 × 4 niveles: ruedas, válvulas de carro y "
           "alambre Ø1,0", 2.9),
    Sector("AL-CA", "Carros de abastecimiento", R(0.3, 40.6, 1.6, 43.6), "MP", "común",
           "W-CAR tabla 5: estacionamiento de 3 × 1 m para los 2 carros de abastecimiento diario"),
    Sector("AL-CU", "Cuarentena de MP (compartida manuales y carros)", R(6.6, 24.6, 9.1, 34.6), "CAL", "común",
           "W-MAN y W-CAR tabla 5: 10 × 2,5 m, demarcada en amarillo: 7 pallets, mesa de inspección de 1,2 × 0,6 y "
           "1,3 m de circulación; colada, espesor en 3 puntos y etiqueta de lote", 25.0),
    Sector("AL-RE", "Retenidos de MP (no conforme)", R(6.6, 34.7, 9.1, 37.1), "CAL", "común",
           "W-CAR tabla 5: 4 × 1,5 m demarcados en rojo, 3 pallets; se reclama al proveedor", 6.0),
    Sector("AL-CH", "Chapa LAF de manuales (3 formatos)", R(9.1, 24.6, 10.6, 37.1), "MP", "S2",
           f"{_V5} 'Chapa y fleje': hojas 1220 × 2440, 1000 × 2000 y 1500 × 3000 en paquetes de 2 alturas "
           "(7 lugares); el autoelevador los toma de costado desde A2 (W-MAN)"),
    Sector("AL-FL", "Flejes LAF de manuales", R(6.6, 42.2, 14.4, 43.6), "MP", "S1 / S2",
           f"{_V5}: 21 rollos parados en cunas; porta-flejes de 3 niveles (24 cunas, MP Opción D) en vez de 1 nivel "
           "a piso: misma capacidad en la tercera parte del frente de calle"),
    Sector("AL-SS", "Insumos de soldadura y superficie", R(14.6, 42.2, 18.6, 43.6), "MP", "común",
           f"{_V5}: 12 posiciones, 4,8 m² netos; rack de 2 módulos: alambre MAG Ø0,9, granalla S330/S390, discos y "
           "sprays (la granalla va a la granalladora en el carro de abastecimiento)", 4.8),
    Sector("AL-CC", "Chapa LAC de carros (calle de chapa)", R(15.6, 24.6, 17.1, 34.6), "MP", "S3",
           "W-CAR tabla 5 y v5: 3 posiciones de 3,0 × 1,5 m, 2 paquetes por posición; van a la misma guillotina"),
    Sector("AL-CT", "Cantiléver de caños y barras", R(17.1, 24.6, 19.6, 37.1), "MP", "común",
           f"{_V5}: 11 posiciones a 3 niveles, 30 m² netos (lugar de 5 m² por ítem): caño Ø76,2 del 1 kg en atados de "
           "16 (frente al cajón del láser, cruzando A3), caños de 1\" y 1¼\" y barras de 3/4\" y 1\" de carros "
           "(al puesto 8.1)", 30.0),
    Sector("AL-CQ", "Casquetes y cuplas de carros", R(18.8, 42.2, 24.6, 43.6), "MP", "S3",
           f"{_V5}: 11 posiciones (4 niveles), 6,0 m² netos; rack de 2 módulos × 2 × 4 niveles = 16 frente a AN; "
           "carros 1 y 2 a los puestos 6 y 7 (W-CAR)", 6.0),
    Sector("AL-1N", "Gasoil e insumos del autoelevador de MP y carros", R(0.4, 19.3, 1.6, 23.0), "AUX", "común",
           "Armario de inflamables y estante; el Heli CPCD50 diésel (W-MAN) se estaciona al final del pasillo central"),
    # ---------------- banda norte: corte, tubo, embutido, celda de cuello y cuerpo
    Sector("N1", "Corte de chapa (compartido) y marcado de carros", R(24.7, 24.6, 36.0, 29.6), "PROD", "S2 / S3",
           "W-CAR: guillotina CENA 8 × 3200 (≈ 3,9 × 2,1), mesa elevadora 2,6 × 1,8 con 1 m de paso, zona trasera "
           "3,9 × 2,5 (rampa, contenedor y carros) = 44 m²; marcado de carros 3,5 × 2,5 pegado a la rampa = 9 m²",
           53.0),
    Sector("N2", "Corte de tubo 1 kg", R(24.7, 29.8, 28.8, 37.1), "PROD", "S1",
           "W-MAN: 1 láser (X-MAN); cajón de alimentación de 6,5 m al lado de la máquina, dos posiciones de carro "
           "«en llenado» y «vacío» de 1,2 × 0,8 m y contenedor de 1.000 L junto a la máquina"),
    Sector("AL-PR", "Procesado: cuerpos cortados de chapa y tramos de 1 kg", R(28.9, 29.8, 36.0, 33.4), "MP",
           "S1 / S2 / S3", f"{_V5} hoja Procesado A: colchón de 7 días (manuales) y 5 días (rodantes) = 10 pallets de "
           "cuerpos de chapa junto a la guillotina y 14 de tramos de 1 kg junto al láser (24 pallets, 28,9 m² netos, "
           "con AL-PT); a piso, con zorra"),
    Sector("AL-PT", "Procesado: tramos de 1 kg (continuación)", R(28.9, 33.5, 36.0, 34.7), "MP", "S1",
           f"{_V5} hoja Procesado A: pallets de tramos parados en capas, entre el láser y el encastre"),
    Sector("AL-PK", "Procesado: cúpulas y fondos 1 a 10 kg", R(29.9, 36.6, 33.4, 39.2), "MP", "S1 / S2",
           f"{_V5} hoja Procesado B: 18 pallets (21,6 m² netos) = AL-PK más las zonas de cúpulas (PU-CU) y de fondos "
           "(PU-FO) de W-MAN; frente a la calle PO-3, entre el embutido y el encastre"),
    Sector("N6", "Cilindrado y soldadura longitudinal 2,5-10 kg", R(36.2, 26.8, 39.8, 33.4), "PROD", "S2",
           "W-MAN: roladora Firesafer FS-RM01 y soldadora longitudinal con el carro FCHP20505 entre las dos "
           "(un lado largo hacia cada máquina)"),
    Sector("N3", "Corte de disco y embutido", R(24.7, 40.4, 34.4, 43.6), "PROD", "S1 / S2",
           "W-MAN: desbobinador, enderezador y alimentador Cena PRE-1, prensa Sangiacomo; estantería de matrices y "
           "carro porta-matrices al lado de la prensa; contenedor de 1.000 L del esqueleto"),
    Sector("N7", "Celda de cuello: numerado, muesca y soldadura", R(34.5, 40.4, 46.2, 43.6), "PROD", "S1 / S2",
           "W-MAN: las prensas de muesca van pegadas a la de numerado y a la soldadora de cuello, sin transporte "
           "entre las tres; zona de cúpulas al lado"),
    Sector("N4", "Encastre, bordoneado, soldadura circ., espesor y PH", R(33.6, 34.7, 54.6, 39.2), "PROD",
           "S1 / S2", "W-MAN y X-MAN: encastre 1, bordoneado 1, soldadura circ. 2, control de espesor 1, PH 2; "
           "un FCHP20505 entre cada par de puestos"),
    Sector("N5", "Secado, granallado, detección y corrección", R(54.7, 34.7, 79.0, 39.2), "PROD", "S1 / S2",
           "W-MAN y X-MAN: secado 4, granallado 1 (de rodillos), detección 1, corrección 1; tres jaulas al lado "
           "del puesto; el detector cuelga el cilindro en el riel de pintura"),
    # ---------------- fila central: mantenimiento, calidad y conducción (planta baja, sin entrepiso)
    Sector("MT", "Taller de mantenimiento", R(41.2, 24.8, 49.2, 29.4), "AUX", "común",
           "Mantenimiento preventivo: bancos, torno, agujereadora, soldadora móvil; entra la transpaleta desde el "
           "pasillo central; puerta directa al pañol", 30.0),
    Sector("PÑL", "Pañol de mantenimiento y de línea", R(41.2, 29.6, 46.0, 33.2), "AUX", "común",
           "Pegado al taller: repuestos críticos, herramental del preventivo, consumibles de soldadura (toberas, "
           "puntas, discos) contra vale por la ventanilla a PO-1"),
    Sector("Q", "Laboratorio de calidad", R(49.4, 24.8, 56.8, 29.4), "CAL", "común",
           "Metrología, ensayo de rotura (1 cilindro por lote, W-MAN), adherencia y espesor de pintura, humedad del "
           "polvo, probetas de soldadura de carros (X-DT) y descarga de muestras (IRAM 3550); legajos", 31.0),
    Sector("QR", "Cuarentena de producto y muestras retenidas", R(57.0, 24.8, 61.0, 29.4), "CAL", "común",
           "Jaula con llave: lotes rechazados y un cilindro testigo por lote (IRAM 3517 / 3523)", 15.0),
    Sector("SUP", "Supervisor de planta", R(61.2, 24.8, 64.2, 29.4), "AUX", "común",
           "Oficina propia del encargado de turno, con ventana a la línea y al pasillo central"),
    Sector("PCP", "Planificación y control de la producción", R(64.4, 24.8, 68.4, 29.4), "AUX", "común",
           "Separada del supervisor: 2 puestos y tablero de programación con ventana a la línea"),
    Sector("PV", "Supermercado de carros vacíos", R(46.2, 29.6, 62.0, 33.2), "AUX", "común",
           "Carros FCHP20505 y de estantes de 12 cajones de reserva y para el cambio de formato (W-MAN: dos por "
           "tramo, uno en uso y otro para el formato siguiente)"),
    # ---------------- franja norte
    Sector("SC", "Compresores y colector de humos", R(48.0, 40.4, 65.6, 43.6), "AUX", "común",
           "Reguladores de Arcal 21 y N₂ que vienen de la jaula exterior (puerta PG), colector de humos, 2 compresores "
           "de tornillo, secador y pulmón"),
    # ---------------- columna este: pintura en polvo (riel aéreo, W-MAN)
    Sector("S-P", "Pintura en polvo (riel aéreo)", R(74.6, 2.3, 87.6, 24.3), "PINT", "S1 / S2",
           "W-MAN: riel transportador aéreo -> horno de precalentamiento -> cabina con recuperación -> horno de curado "
           "180-220 °C -> enfriamiento y descarga; esquema de 22 × 13 m"),
    Sector("ST-I", "Tableros y compresor de la cabina", R(70.2, 24.8, 74.4, 31.4), "AUX", "común",
           "Tablero de la línea este y compresor sin aceite dedicado a la cabina de pintura"),
    # ---------------- banda sur: terminación de manuales, depósito de polvo y embalaje
    Sector("DP", "Depósito de polvo químico (único de la planta)", R(55.2, 4.6, 59.4, 7.6), "MP", "común",
           f"{_V5}: 11 posiciones, 8,4 m² netos, 12,6 brutos; cerrado y seco: big bags de ABC 60 y ABC 90, polvo D y "
           "pintura en polvo; entra por AT (muelle P3) y sale a la carga (norte), a carros y a pintura (oeste)", 12.6),
    Sector("S-T", "Terminación 1 a 10 kg", R(55.2, 9.6, 72.4, 12.8), "TERM", "S1 / S2",
           "W-MAN: carga (estación de big bag y transportador neumático) -> ensamblaje -> presurización -> ensayo de "
           "pérdidas -> etiquetado, con un FCHP20505 entre cada par de puestos; termina en el embalaje"),
    Sector("EMB", "Embalaje y paletizado (vacíos y terminados)", R(59.6, 4.6, 74.4, 9.4), "PT", "S1 / S2",
           "W-MAN: los vacíos se encajonan al lado de la descarga de pintura y los terminados al final de la "
           "terminación, en la misma zona: armadora de cajas, 2 mesas de encajonado (X-MAN) y envolvedora EDOS PS5"),
    Sector("AL-EB", "Embalaje: cajas plegadas, film y pallets", R(53.7, 0.3, 70.2, 1.7), "MP", "S1 / S2",
           f"{_V5}: 50 posiciones, 22,2 m² netos; rack de 6 módulos × 2 × 4 niveles = 48 + pila de pallets vacíos "
           "junto a la envolvedora; las cajas van a la armadora con la transpaleta", 17.8),
    Sector("PU-9", "Terminados pintados esperando la carga", R(55.2, 15.8, 60.8, 18.6), "TERM", "S1 / S2",
           "W-MAN: 413 matafuegos por día en el pico en carros FCHP20505 y de cajones (1 kg)"),
    Sector("DL", "Ducha de emergencia y lavaojos", R(70.4, 15.8, 72.4, 18.8), "AUX", "común",
           "A menos de 10 s de la carga de polvo, de la presurización y de la descarga de pintura"),
    # ---------------- banda sur: PT y expedición
    Sector("AL-3", "Almacén de producto terminado y de cilindros", R(42.4, 6.8, 53.6, 18.8), "PT", "S1 / S2",
           "X-DT Almacén PT 2035: 56 pallets esperando despacho + 72 del stock oct-nov = 128; racks de 4 módulos a 5 "
           "niveles: RK1 40 + RK2 80 + RK3 40 = 160 (incluye 8 pallets de carros terminados)"),
    Sector("EXP", "Expedición y muelle P3", R(41.0, 0.3, 53.6, 6.8), "PT", "común",
           "Un solo muelle con rampa niveladora: sale PT y carros (terminados y al pintor); entran polvo, pintura en "
           "polvo, embalaje y revendidos. Recepción 7 a 10 h, expedición 13 a 17 h"),
    Sector("S4", "Tercerizados revendidos", R(41.0, 0.3, 46.7, 2.3), "PT", "S4",
           f"{_V5} 'Almacén de producto terminado': 17 posiciones (14,4 m² brutos); rack de 2 módulos × 4 niveles: "
           "CO₂, agua, AFFF, clase K y agente limpio", 9.6),
    Sector("REC", "Recepción del muelle: mesa de control", R(46.8, 0.3, 49.2, 2.3), "CAL", "común",
           "Remito contra orden de compra y muestra del lote de polvo al laboratorio (humedad) antes de liberarlo"),
    # ---------------- banda sur: carros (W-CAR, puestos 3 a 9 en U)
    Sector("C-5", "Soldadura longitudinal de carros (5)", R(21.4, 14.2, 26.4, 18.8), "PROD", "S3",
           "W-CAR tabla: ≈ 5,5 × 4,0 = 22 m²; mandril con 1,5 m libres para el cuerpo; no conforme en rojo", 22.0),
    Sector("C-4", "Punteo del cuerpo ×2 (4)", R(26.6, 14.2, 34.0, 18.8), "PROD", "S3",
           "W-CAR ≈ 6,0 × 4,5 por puesto; X-DT 2035: 2 viradores (comparten banco, cuna y pulmón)", 27.0),
    Sector("C-3", "Cilindrado de carros (3)", R(34.2, 14.2, 40.9, 18.8), "PROD", "S3",
           "W-CAR ≈ 7,0 × 5,0 = 35 m²: roladora W12 8 × 1500, zona de carga, EFE 600 y mesa móvil, salida axial "
           "y pulmón de 1,8 × 1,2", 30.8),
    Sector("C-6", "Soldadura de cupla en la cúpula (6)", R(21.4, 8.2, 25.4, 13.2), "PROD", "S3",
           "W-CAR ≈ 4,5 × 3,5 = 16 m²; pegado al armado (7); lo hace el operario de punteo", 16.0),
    Sector("C-7", "Armado y soldadura circunferencial (7)", R(25.6, 8.2, 31.2, 13.2), "PROD", "S3",
           "W-CAR ≈ 6,0 × 4,5 = 27 m²: virador, carro canasto de cúpulas y carro 2 de fondos", 27.0),
    Sector("C-8", "Soldadura de accesorios e inspección (8)", R(31.4, 8.2, 36.4, 13.2), "PROD", "S3",
           "W-CAR ≈ 5,0 × 4,0 = 20 m²: virador y carro de kits; monta eje y ruedas; inspección de costuras (X-DT)",
           20.0),
    Sector("C-T", "Terminación de carros", R(36.6, 8.2, 40.9, 13.2), "TERM", "S3",
           "Carga de polvo ABC 90 (estación de big bag), armado de válvula y manguera, presurización y etiquetado; "
           "vuelven del pintor por PO-CN"),
    Sector("C-81", "Fabricación de accesorios (8.1)", R(18.2, 0.3, 26.2, 5.2), "PROD", "S3",
           "W-CAR ≈ 8,0 × 4,0 = 32 m²: rack de barras de 6,5 m sobre la calle PO-C, caballetes, sensitiva, "
           "dobladora, taladro, banco y prensa de 20 t; el carro de kits va al puesto 8", 32.0),
    Sector("C-9", "Prueba hidráulica de carros (9)", R(26.4, 0.3, 31.9, 5.2), "PROD", "S3",
           "W-CAR ≈ 5,5 × 4,0 = 22 m²: 2 bandejas con rampa, pantalla, Yukon M-000200, tanque de 1.000 L en "
           "circuito cerrado", 22.0),
    Sector("C-10", "Secado de carros", R(32.1, 0.3, 34.2, 5.2), "PROD", "S3",
           "W-CAR puesto 9: sale vacío y rodando hacia el secado"),
    Sector("C-PP", "Carros al muelle: a pintura y terminados", R(34.4, 0.3, 41.0, 5.2), "PT", "S3",
           "Pulmón de despacho a pintura tercerizada (6 carros, W-CAR) y carros terminados esperando despacho "
           "(X-DT Almacén PT: 32 m²; 8 pallets más en RK1)", 32.0),
]

# ============================================================ EQUIPOS (paso = número de operación en el plano)
# fuente: C = cotización recibida (referencias/INVESTIGACION PROVEEDORES); W = Word del proceso (W-MAN, W-CAR,
# W-REC); X = Excel de dimensionamiento; D = medida de diseño con su criterio
E_ = Equipo
EQUIPOS = [
    # ---------------- almacén de MP
    E_("RMM", "Rack de insumos de montaje (4 mód. × 4 niveles)", Rw(0.35, 24.7, 1.15, 10.8), "AL-MM", 0,
       fuente="X-ALM: 32 posiciones de pallet 1,2 × 1,0", forma="rack", tipo="rack", frente="E"),
    E_("EID", "Estantería de identificación (5 niveles)", Rw(0.35, 35.9, 0.7, 1.3), "AL-ID", 0,
       fuente="X-ALM: estantería de cajas", tipo="estanteria", frente="E"),
    E_("RMC", "Rack de insumos de carros (1 mód. × 4 niveles)", Rw(0.35, 37.6, 1.15, 2.7), "AL-MC", 0,
       fuente="X-ALM: 8 posiciones", forma="rack", tipo="rack", frente="E"),
    E_("CAB", "Carros de abastecimiento (2)", Rw(0.4, 40.8, 1.1, 2.6), "AL-CA", 0,
       fuente="W-CAR tabla 5: 3 × 1 m", forma="rack", tipo="carros", frente="E"),
    E_("MI1", "Mesa de inspección de recepción (micrómetro)", Rw(7.6, 33.4, 1.2, 0.6), "AL-CU", 1,
       fuente="W-MAN y W-CAR: mesa 1,2 × 0,6", tipo="mesa_control", frente="O"),
    E_("HJ1", "Paquetes de hojas LAF (5 posiciones × 2 alturas)", Rw(9.15, 24.7, 1.4, 12.2), "AL-CH", 0,
       fuente="X-ALM: 7 lugares de 1,22 × 2,44 a 1,5 × 3,0", tipo="paquetes", frente="E"),
    E_("RF1", "Porta-flejes de 3 niveles (24 cunas)", Rw(6.7, 42.25, 7.6, 1.3), "AL-FL", 0,
       fuente="X-ALM 21 rollos; porta-flejes de MP Opción D", tipo="portaflejes", frente="S"),
    E_("RSS", "Rack de soldadura y superficie (1 mód. de 3 pallets × 4 niveles)", Rw(14.7, 42.3, 3.7, 1.15), "AL-SS",
       0, fuente="X-ALM: 12 posiciones", forma="rack", tipo="rack", frente="S"),
    E_("HJ2", "Calle de chapa LAC de carros (3 posiciones)", Rw(15.65, 24.7, 1.4, 9.7), "AL-CC", 0,
       fuente="W-CAR: 3 posiciones de 3,0 × 1,5 m", tipo="paquetes", frente="O"),
    E_("CT1", "Cantiléver de caños y barras (3 niveles)", Rw(17.2, 24.7, 2.3, 12.3), "AL-CT", 0,
       fuente="X-ALM: caño de 6 m + 0,4 m por extremo", tipo="cantilever", frente="E"),
    E_("RCQ", "Rack de casquetes y cuplas (2 mód. × 4 niveles)", Rw(18.95, 42.3, 5.4, 1.15), "AL-CQ", 0,
       fuente="X-ALM: 11 posiciones", forma="rack", tipo="rack", frente="S"),
    # ---------------- N1 corte de chapa (compartido) y marcado de carros
    E_("M02", "Mesa elevadora de tijera 3 t (compartida)", Rw(24.8, 24.9, 1.8, 2.6), "N1", 0, 2.2,
       fuente="W-MAN y W-CAR: 2,6 × 1,8 m", tipo="mesa_tijera", frente="O"),
    E_("M04", "Guillotina CENA 8 × 3200 (compartida)", Rw(27.6, 24.8, 2.1, 3.9), "N1", 1, 11.0,
       fuente="W-CAR: ≈ 3,9 × 2,1 m (a confirmar con Cena)", tipo="guillotina", frente="O"),
    E_("SCG", "Contenedor de scrap 1.000 L con volcador", Rw(29.9, 24.9, 1.47, 1.42), "N1", 0,
       fuente="W-CAR: 1470 × 1420 mm detrás de la guillotina, a un costado", tipo="contenedores", frente="S"),
    E_("MK1", "Marcado de carros: mesa 1,4 × 1,0 y marcadora de columna", Rw(32.3, 25.9, 1.4, 1.0), "N1", 0, 0.5,
       fuente="W-CAR 2.1: lo atiende el operario de corte", tipo="marcadora", frente="S"),
    # ---------------- N2 corte de tubo (1 láser)
    E_("CJ1", "Cajón de alimentación 0,5 × 0,5 × 6,5 m (atado de 16 caños)", Rw(24.75, 29.9, 0.5, 6.5), "N2", 0,
       fuente="W-MAN: el autoelevador deja el atado y se desfleja", tipo="cantilever", frente="O"),
    E_("M16", "Láser de tubo Leapion 1,5 kW con chiller", Rw(25.35, 29.9, 0.8, 6.85), "N2", 1, 10.0, aire=True,
       polvo=True, fuente="C Leapion; W-MAN: recorrido útil 6150 mm", tipo="laser", frente="E"),
    E_("SCL", "Contenedor 1.000 L de recortes del láser", Rw(24.75, 27.9, 1.47, 1.42), "N2", 0,
       fuente="W-MAN: junto a la máquina, lo vacía el autoelevador (A3)", tipo="contenedores", frente="O"),
    # ---------------- N6 cilindrado y soldadura longitudinal (manuales)
    E_("B02", "Roladora Firesafer FS-RM01", Rw(36.8, 28.8, 1.7, 0.8), "N6", 1, 4.0,
       fuente="W-MAN: trifásica 380 V, 4 kW (huella de catálogo)", tipo="cilindradora", frente="S"),
    E_("B03", "Soldadora longitudinal Firesafer (MAG)", Rw(36.7, 30.8, 2.0, 1.4), "N6", 1, 12.0, polvo=True,
       fuente="C Firesafer; W-MAN", tipo="sold_long", frente="S"),
    # ---------------- N3 embutido
    E_("M06", "Desbobinador de eje horizontal con carro portabobinas", Rw(24.8, 41.4, 1.8, 2.0), "N3", 0, 2.2,
       fuente="W-MAN: rollo parado, cargado con el espolón desde AN", tipo="desbobinador", frente="O"),
    E_("M07", "Enderezador, lubricante y alimentador servo Cena PRE-1", Rw(26.9, 41.9, 1.6, 1.2), "N3", 0, 2.2,
       fuente="C Cena PRE-1 (Drive)", tipo="alimentador", frente="S"),
    E_("M08", "Prensa embutidora Sangiacomo", Rw(28.8, 41.35, 2.6, 2.2), "N3", 1, 37.0, aire=True,
       fuente="W-MAN: corta el disco y embute en el mismo golpe", tipo="prensa", frente="S"),
    E_("SCP", "Contenedor 1.000 L del esqueleto (sobre ruedas)", Rw(31.5, 41.9, 1.47, 1.42), "N3", 0,
       fuente="W-MAN: el cortador trocea el esqueleto al contenedor", tipo="contenedores", frente="S"),
    E_("EM", "Estantería de matrices (8 juegos) y carro porta-matrices", Rw(33.1, 41.8, 1.2, 1.7), "N3", 0,
       fuente="W-MAN: 8 juegos, al lado de la prensa", tipo="estanteria", frente="S"),
    # ---------------- N7 celda de cuello
    E_("M10", "Numerado de cúpula: micropercusión Pannier ADP120160D", Rw(39.0, 41.8, 1.0, 0.8), "N7", 1, 0.5,
       fuente="W-MAN: marcadora de columna sobre banco", tipo="marcadora", frente="S"),
    E_("M09a", "Preparación de cuello: prensa de muesca Pannier MB-21", Rw(40.2, 41.8, 1.0, 0.8), "N7", 1, 0.5,
       aire=True, fuente="W-MAN: prensa de banco neumática 3.500 kg", tipo="torno", frente="S"),
    E_("M09b", "Preparación de cuello: prensa de muesca Pannier MB-21", Rw(41.4, 41.8, 1.0, 0.8), "N7", 1, 0.5,
       aire=True, fuente="W-MAN: prensa de banco neumática 3.500 kg", tipo="torno", frente="S"),
    E_("M11", "Soldadura de cuello Firesafer FS-HFM1", Rw(42.6, 41.6, 1.6, 1.2), "N7", 1, 12.0, polvo=True,
       fuente="C Firesafer FS-HFM1 (plato divisor)", tipo="sold_circ", frente="S"),
    # ---------------- N4 encastre -> PH
    E_("E09", "Prensa de encastre Del Fabro 30 t", Rw(36.0, 35.8, 1.2, 1.0), "N4", 1, 4.0, aire=True,
       fuente="W-MAN: prensa hidráulica motorizada, matriz por formato", tipo="encastre", frente="S"),
    E_("B04", "Bordoneadora motorizada Pilman SWM-400", Rw(38.3, 35.8, 1.0, 0.8), "N4", 1, 2.2,
       fuente="C Pilman / Bendmak SWM-400", tipo="bordoneadora", frente="S"),
    E_("A06", "Soldadora circunferencial Firesafer", Rw(40.4, 35.6, 2.0, 1.4), "N4", 1, 15.0, polvo=True,
       fuente="W-MAN: cúpula y fondo a la vez, MAG 350 A", tipo="sold_circ", frente="S"),
    E_("B06", "Soldadora circunferencial Firesafer", Rw(42.8, 35.6, 2.0, 1.4), "N4", 1, 15.0, polvo=True,
       fuente="W-MAN: cúpula y fondo a la vez, MAG 350 A", tipo="sold_circ", frente="S"),
    E_("Q01", "Control de espesor: mesa y ultrasonido Melisam MR017", Rw(45.9, 35.8, 1.2, 0.8), "N4", 1, 0.2,
       fuente="W-MAN: mesa al costado de la salida", tipo="mesa_control", frente="S"),
    E_("A07", "Prueba hidráulica Firesafer FS-JD12A", Rw(47.5, 35.6, 2.4, 1.6), "N4", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A (huella de catálogo)", tipo="ph", frente="S"),
    E_("B07", "Prueba hidráulica Firesafer FS-JD12A", Rw(50.2, 35.6, 2.4, 1.6), "N4", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A (huella de catálogo)", tipo="ph", frente="S"),
    E_("DEC", "Cámara de decantación y separador de aceites (PH y pérdidas)", Rw(47.6, 37.6, 2.6, 1.2), "N4", 0,
       agua=True, fuente="W-MAN: compartidos con el ensayo de pérdidas; tapa al piso", tipo="hermeticidad",
       frente="S"),
    # ---------------- N5 secado, granallado y detección
    E_("B14a", "Secadora de cilindros (boquilla en el cuello)", Rw(54.7, 35.7, 1.4, 0.9), "N5", 1, 6.0, gas=True,
       fuente="W-MAN: secadora Yukon; D gabinete de 4 boquillas", tipo="secadora", frente="S"),
    E_("B14b", "Secadora de cilindros (boquilla en el cuello)", Rw(56.3, 35.7, 1.4, 0.9), "N5", 0, 6.0, gas=True,
       fuente="W-MAN: secadora Yukon; D gabinete de 4 boquillas", tipo="secadora", frente="S"),
    E_("B14c", "Secadora de cilindros (boquilla en el cuello)", Rw(57.9, 35.7, 1.4, 0.9), "N5", 1, 6.0, gas=True,
       fuente="W-MAN: secadora Yukon; D gabinete de 4 boquillas", tipo="secadora", frente="S"),
    E_("B14d", "Secadora de cilindros (boquilla en el cuello)", Rw(59.5, 35.7, 1.4, 0.9), "N5", 0, 6.0, gas=True,
       fuente="W-MAN: secadora Yukon; D gabinete de 4 boquillas", tipo="secadora", frente="S"),
    E_("RIN", "Rodillos de entrada de la granalladora", Rw(64.0, 35.9, 1.5, 0.9), "N5", 0,
       fuente="W-MAN: los cilindros entran acostados", tipo="mesa_rodillos", frente="S"),
    E_("B08", "Granalladora de rodillos AirBlast G-100", Rw(65.6, 35.7, 4.5, 1.3), "N5", 1, 15.0, polvo=True,
       fuente="C Airblast G-100 4500 × 1300", tipo="granalladora", frente="S"),
    E_("B13", "Colector de polvo de la granalladora", Rw(66.2, 37.4, 1.8, 1.4), "N5", 0, 5.5, polvo=True,
       fuente="D colector de cartuchos del G-100", tipo="colector"),
    E_("ROUT", "Rodillos de salida y boquilla de soplado", Rw(70.2, 35.9, 1.5, 0.9), "N5", 0,
       fuente="W-MAN: soplado del polvo a la salida", tipo="mesa_rodillos", frente="S"),
    E_("B09", "Detección de defectos: mesa iluminada", Rw(71.9, 35.8, 2.2, 1.2), "N5", 1, 0.5,
       fuente="W-MAN: a continuación de los rodillos de salida, junto al riel", tipo="inspeccion", frente="S"),
    E_("J1", "Jaula «a corregir»", Rw(71.9, 37.4, 1.0, 1.0), "N5", 0, fuente="W-MAN: tres jaulas al lado del puesto",
       tipo="jaula", frente="S"),
    E_("J2", "Jaula «a re-granallar»", Rw(73.0, 37.4, 1.0, 1.0), "N5", 0, fuente="W-MAN", tipo="jaula", frente="S"),
    E_("J3", "Jaula «descarte»", Rw(74.1, 37.4, 1.0, 1.0), "N5", 0, fuente="W-MAN", tipo="jaula", frente="S"),
    E_("B10", "Corrección: mesa y cabina de amolado con extracción", Rw(75.6, 37.4, 2.2, 1.5), "N5", 1, 3.0,
       polvo=True, fuente="W-MAN: amoladora 115 mm, machos y calibres", tipo="banco_sold", frente="S"),
    # ---------------- pintura: riel aéreo (precalentamiento -> cabina -> curado -> descarga)
    E_("P01", "Horno de precalentamiento (túnel a gas)", Rw(80.4, 20.9, 6.0, 2.44), "S-P", 0, 3.0, gas=True,
       fuente="W-MAN: saca la humedad antes de la cabina; huella de horno Electricolor", tipo="horno", frente="S"),
    E_("P04", "Cabina de pintura 2 × 1,5 m y reciprocador 1300", Rw(78.3, 16.6, 1.7, 2.0), "S-P", 1, 5.0, aire=True,
       polvo=True, fuente="C Electricolor", tipo="cabina", frente="O"),
    E_("P05", "Ciclones de recuperación de polvo (2)", Rw(76.7, 18.7, 1.4, 2.0), "S-P", 0, 11.0, polvo=True,
       fuente="C Electricolor", tipo="ciclones", frente="O"),
    E_("P02", "Equipos de aplicación y tolvas EC40-200D", Rw(80.1, 16.7, 1.0, 1.8), "S-P", 0, 2.0, aire=True,
       fuente="C Electricolor", frente="O"),
    E_("P03", "Horno de curado 180-220 °C", Rw(81.2, 10.6, 2.44, 6.0), "S-P", 0, 3.0, gas=True,
       fuente="C Electricolor 6 × 2,44 m; W-MAN 15 a 20 min", tipo="horno", frente="O"),
    E_("P06", "Horno de curado 2 (en paralelo para el pico)", Rw(84.2, 10.6, 2.44, 6.0), "S-P", 0, 3.0, gas=True,
       fuente="C Electricolor 6 × 2,44 m", tipo="horno", frente="O"),
    E_("P08", "Enfriamiento y descarga: separa vacíos y terminados", Rw(81.2, 3.1, 5.5, 6.8), "S-P", 1,
       fuente="C Electricolor; W-MAN: el flujo se divide al descolgar", tipo="estacion_pintura", frente="O"),
    E_("P09", "Control de espesor de película y adherencia", Rw(76.8, 7.0, 2.0, 1.4), "S-P", 0,
       fuente="W-MAN: por muestreo, con registro de temperatura", tipo="retoque", frente="O"),
    # ---------------- terminación 1 a 10 kg (W-MAN)
    E_("RKP", "Rack pesado de big bags y pallets de pintura", Rw(55.3, 4.7, 1.1, 2.8), "DP", 0,
       fuente="X-ALM: big bags de 1 t y pallets, 11 posiciones", forma="rack", tipo="rack", frente="E"),
    E_("BB1", "Estación de big bag (ABC 60) con transportador neumático", Rw(55.4, 10.2, 1.8, 1.8), "S-T", 0, 3.0,
       aire=True, polvo=True, fuente="W-MAN: bastidor con polipasto y transferencia por vacío", tipo="carga_polvo",
       frente="S"),
    E_("T01", "Cargadora de polvo por vacío Yukon M-000121", Rw(57.4, 10.6, 1.6, 1.2), "S-T", 1, 3.0, aire=True,
       polvo=True, fuente="C Yukon M-000121; W-MAN", tipo="carga_polvo", frente="S"),
    E_("T03", "Ensamblaje: llave dinamométrica y estante de cajones", Rw(60.1, 10.6, 1.6, 1.2), "S-T", 1, 0.5,
       fuente="W-MAN: puesto manual", tipo="ensamble", frente="S"),
    E_("T05", "Presurización con N₂: pinza Yukon M-000150", Rw(62.8, 10.6, 1.5, 1.0), "S-T", 1, 0.5, n2=True,
       fuente="C Yukon M-000150; N₂ por cañería del pack exterior", tipo="presurizacion", frente="S"),
    E_("T06", "Ensayo de pérdidas: tanque de inmersión y rejilla", Rw(65.4, 10.6, 2.0, 1.0), "S-T", 1, 0.5,
       agua=True, fuente="W-MAN: 6 matafuegos por tanda, 100 mm de agua", tipo="hermeticidad", frente="S"),
    E_("T07", "Etiquetado: dispensador, posicionador e impresora", Rw(68.4, 10.6, 1.6, 0.8), "S-T", 1, 0.5,
       fuente="W-MAN: etiqueta preimpresa + n° de serie y fecha", tipo="etiquetadora", frente="S"),
    E_("T11", "Envolvedora de pallets EDOS PS5", Rw(60.0, 5.0, 1.8, 1.8), "EMB", 0, 1.5,
       fuente="C EDOS PS5 (plato Ø1,65 m + columna)", tipo="envolvedora", frente="E"),
    E_("AC1", "Armadora automática de cajas (caja del 1 kg)", Rw(63.4, 7.6, 2.4, 1.2), "EMB", 0, 3.0, aire=True,
       fuente="W-MAN: al inicio de las mesas de encajonado (a cotizar)", tipo="palletizado", frente="E"),
    E_("T09", "Mesa de encajonado: terminados", Rw(66.6, 7.9, 1.6, 0.8), "EMB", 1,
       fuente="W-MAN y X-MAN (embalaje 2): al final de la terminación", tipo="palletizado", frente="S"),
    E_("T08", "Mesa de encajonado: cilindros vacíos", Rw(70.6, 7.9, 1.6, 0.8), "EMB", 1,
       fuente="W-MAN: al lado de la descarga de pintura", tipo="palletizado", frente="S"),
    E_("RKE", "Rack de embalaje (6 mód. × 4 niveles)", Rw(53.8, 0.4, 16.2, 1.1), "AL-EB", 0,
       fuente="X-ALM: 48 posiciones de cajas plegadas, film y etiquetas", forma="rack", tipo="rack", frente="N"),
    # ---------------- PT
    E_("RK1", "Rack RK1 (4 mód. × 5 niveles)", Rw(42.5, 7.0, 1.1, 11.6), "AL-3", 0,
       fuente="D 4 módulos de 2,7 m × 5 niveles (pallet 1,2 × 1,0)", forma="rack", tipo="rack", frente="E"),
    E_("RK2", "Rack RK2 doble (4 mód. × 2 × 5 por cara)", Rw(46.9, 7.0, 2.2, 11.6), "AL-3", 0,
       fuente="D 4 módulos de 2,7 m, doble fondo × 5 niveles", forma="rack", tipo="rack", frente="E"),
    E_("RK3", "Rack RK3 (4 mód. × 5 niveles)", Rw(52.4, 7.0, 1.1, 11.6), "AL-3", 0,
       fuente="D 4 módulos de 2,7 m × 5 niveles", forma="rack", tipo="rack", frente="O"),
    E_("RKR", "Rack de revendidos (2 mód. × 4 niveles)", Rw(41.1, 0.4, 5.4, 1.1), "S4", 0,
       fuente="X-ALM: 17 posiciones", forma="rack", tipo="rack", frente="N"),
    # ---------------- carros (W-CAR)
    E_("C01", "Roladora hidráulica CNC W12 8 × 1500", Rw(35.4, 15.0, 1.4, 3.2), "C-3", 1, 7.5,
       fuente="W-CAR: ≈ 3,2 × 1,4 m (a confirmar)", tipo="cilindradora", frente="E"),
    E_("C02a", "Punteo: virador sobre base fija", Rw(27.4, 16.4, 1.2, 0.6), "C-4", 1, 0.5,
       fuente="W-CAR: 1,2 × 0,6 con 1 m libre en cada boca", tipo="posicionador", frente="S"),
    E_("C02b", "Punteo: virador sobre base fija", Rw(31.4, 16.4, 1.2, 0.6), "C-4", 1, 0.5,
       fuente="W-CAR; X-DT 2035: 2 puestos", tipo="posicionador", frente="S"),
    E_("C02s", "Soldadoras Pampa 300 y banco con morsa (compartidos)", Rw(29.0, 17.6, 2.0, 0.9), "C-4", 0, 10.0,
       polvo=True, fuente="W-CAR: soldadora 0,9 × 0,5 y banco 1,5 × 0,7", tipo="banco", frente="S"),
    E_("C04", "Soldadora longitudinal ZH-1300 con mesa", Rw(22.4, 16.4, 2.3, 1.14), "C-5", 1, 12.0, polvo=True,
       fuente="W-CAR: 2,30 × 1,14 m; fuente MIG-350IX y chiller detrás", tipo="sold_long", frente="S"),
    E_("C06", "Soldadura de cupla: mesa Müller con posicionador", Rw(23.0, 10.6, 0.9, 0.6), "C-6", 1, 6.0,
       polvo=True, fuente="W-CAR: ≈ 0,9 × 0,6 m", tipo="posicionador", frente="N"),
    E_("C05", "Armado y soldadura circ.: virador con tope axial", Rw(27.6, 10.6, 1.6, 0.8), "C-7", 1, 10.0,
       polvo=True, fuente="W-CAR: ≈ 1,6 × 0,8 m, 1 m libre en cada punta", tipo="posicionador", frente="N"),
    E_("C08", "Soldadura de accesorios: virador", Rw(33.2, 10.6, 1.6, 0.8), "C-8", 1, 10.0, polvo=True,
       fuente="W-CAR: ≈ 1,6 × 0,8 m", tipo="posicionador", frente="N"),
    E_("C09", "Inspección de costuras (mesa)", Rw(35.0, 8.4, 1.3, 0.9), "C-8", 1, 0.5,
       fuente="X-DT: inspección de costuras int. y ext.", tipo="inspeccion", frente="N"),
    E_("BB2", "Estación de big bag (ABC 90) con transportador neumático", Rw(39.3, 11.3, 1.5, 1.5), "C-T", 0,
       3.0, aire=True, polvo=True, fuente="D igual a la de manuales (W-MAN)", tipo="carga_polvo", frente="O"),
    E_("T02", "Carga de polvo de carros 25 a 100 kg", Rw(37.8, 11.5, 1.2, 1.2), "C-T", 1, 2.0, aire=True,
       polvo=True, fuente="D carga por vacío con balanza", tipo="carga_polvo", frente="S"),
    E_("T12", "Armado de válvula, manguera y tobera", Rw(36.7, 8.4, 1.4, 1.2), "C-T", 1, 0.5, aire=True,
       fuente="D banco de armado", tipo="ensamble", frente="N"),
    E_("T13", "Presurización y etiquetado de carros", Rw(38.3, 8.4, 1.4, 1.2), "C-T", 1, 0.5, n2=True,
       fuente="D banco de presurización + etiquetado", tipo="presurizacion", frente="N"),
    E_("C81r", "Rack de barras (6,5 m) y caballetes", Rw(18.6, 4.0, 6.8, 1.0), "C-81", 0,
       fuente="W-CAR 8.1: 6,5 × 0,6 + caballetes 6,8 × 0,6", tipo="cantilever", frente="S"),
    E_("C81", "Sensitiva, dobladora, taladro, prensa 20 t y banco de kits", Rw(19.0, 0.6, 6.4, 1.4), "C-81", 1,
       5.0, fuente="W-CAR 8.1: ≈ 8,0 × 4,0 m", tipo="banco", frente="N"),
    E_("C07", "PH: 2 bandejas, pantalla y Yukon M-000200", Rw(27.0, 2.0, 3.0, 1.4), "C-9", 1, 2.0, agua=True,
       fuente="C Yukon M-000200; W-CAR tabla del puesto 9", tipo="ph", frente="N"),
    E_("C07t", "Tanque de 1.000 L con bomba y filtros (circuito cerrado)", Rw(30.2, 0.5, 1.56, 1.56), "C-9", 0,
       fuente="W-CAR: Rotoplas Ø1,56 m", tipo="tanque", forma="circ"),
    E_("C10", "Secadora de carros (aire caliente por la cupla)", Rw(32.4, 2.2, 1.4, 1.0), "C-10", 0, 6.0,
       gas=True, fuente="D secado con boquilla en la cupla", tipo="secadora", frente="N"),
    E_("C12", "Carros a pintura (6) y carros terminados", Rw(34.6, 0.5, 6.2, 4.5), "C-PP", 0,
       fuente="W-CAR: 6 carros 1,1 × 2,2; X-DT 32 m² de carros terminados", forma="rack", tipo="carros"),
    # ---------------- SC compresores
    E_("CG1", "Reguladores de Arcal 21 y N₂ (de la jaula exterior)", Rw(49.6, 41.8, 2.0, 1.2), "SC", 0,
       fuente="W-MAN: pack con manifold y cañería a los puestos", tipo="bateria_gas", frente="S"),
    E_("CH1", "Colector de humos de soldadura (filtro de cartuchos)", Rw(52.2, 41.4, 2.4, 1.5), "SC", 0, 7.5,
       polvo=True, fuente="D colector de cartuchos 6000 m³/h", tipo="colector", frente="S"),
    E_("CP1", "Compresor de tornillo 30 kW", Rw(55.2, 41.6, 1.9, 1.1), "SC", 0, 30.0,
       fuente="D compresor de tornillo 30 kW (1,9 × 1,1)", tipo="compresor", frente="S"),
    E_("CP2", "Compresor de tornillo 30 kW (reserva)", Rw(57.8, 41.6, 1.9, 1.1), "SC", 0, 30.0,
       fuente="D compresor de tornillo 30 kW (1,9 × 1,1)", tipo="compresor", frente="S"),
    E_("SEC", "Secador frigorífico y filtros", Rw(60.4, 41.7, 1.0, 0.9), "SC", 0, 1.5,
       fuente="D secador para 5 m³/min", tipo="compresor", frente="S"),
    E_("TQ1", "Pulmón de aire 2000 L", Rw(62.0, 41.6, 1.2, 1.2), "SC", 0, fuente="D tanque vertical Ø 1,2 m",
       tipo="tanque", forma="circ", frente="S"),
]

# recargas: puestos (X-DT 2035) dentro de sus locales; zona general, recinto de polvo y fuera de línea (W-REC)
_RC = [
    # (cod, nombre, (x, y, w, h), local, op, tipo, frente)
    # zona general sur: recepción, inspección, despacho
    ("R01", "Recepción y registro (escáner y balanza)", (0.7, 3.6, 1.6, 0.9), "RC-RD", 1, "mesa_control", "S"),
    ("R17a", "Despacho: precinto, remito y carga", (2.6, 3.6, 1.6, 0.9), "RC-RD", 1, "mesa_control", "S"),
    ("R17b", "Despacho: precinto, remito y carga", (4.5, 3.6, 1.6, 0.9), "RC-RD", 1, "mesa_control", "S"),
    ("R19a", "Inspección visual (pesa el CO₂ y el halogenado)", (7.0, 3.6, 1.6, 0.9), "RC-IV", 1, "inspeccion", "S"),
    ("R19b", "Inspección visual", (8.9, 3.6, 1.6, 0.9), "RC-IV", 1, "inspeccion", "S"),
    # recinto de polvo (HR ≤ 70 %)
    ("R02a", "Descarga de polvo ABC FS-SDP-1 (recuperación)", (0.7, 5.2, 1.2, 1.4), "RC-PV", 1, "cabina_muestras",
     "N"),
    ("R02b", "Descarga de polvo ABC FS-SDP-1 (recuperación)", (2.1, 5.2, 1.2, 1.4), "RC-PV", 1, "cabina_muestras",
     "N"),
    ("R02c", "Descarga de polvo ABC FS-SDP-1 (recuperación)", (3.5, 5.2, 1.2, 1.4), "RC-PV", 0, "cabina_muestras",
     "N"),
    ("R02d", "Descarga BC: tambor Yukon M-000030 exclusivo", (4.9, 5.2, 1.0, 1.0), "RC-PV", 0, "banco", "N"),
    ("R02e", "Descarga clase D: recipiente exclusivo", (6.1, 5.2, 1.0, 1.0), "RC-PV", 0, "banco", "N"),
    ("R04a", "Desarme y limpieza: morsa neumática FS-PC", (0.7, 8.4, 1.4, 0.9), "RC-PV", 1, "banco", "S"),
    ("R04b", "Desarme y limpieza: morsa neumática FS-PC", (2.3, 8.4, 1.4, 0.9), "RC-PV", 1, "banco", "S"),
    ("R04c", "Desarme y limpieza: morsa neumática FS-PC", (3.9, 8.4, 1.4, 0.9), "RC-PV", 0, "banco", "S"),
    ("R05", "Lavado interior (si va a PH)", (5.5, 8.4, 1.6, 0.9), "RC-PV", 0, "hermeticidad", "S"),
    ("R20a", "Cabina de pintura de retoque con extracción", (7.3, 8.2, 1.6, 1.1), "RC-PV", 1, "retoque", "S"),
    ("R20b", "Cabina de pintura de retoque con extracción", (9.0, 8.2, 1.6, 1.1), "RC-PV", 0, "retoque", "S"),
    ("R09a", "Carga de polvo ABC por vacío FS-ZR01", (0.7, 10.4, 1.6, 1.8), "RC-PV", 1, "carga_polvo", "S"),
    ("R09b", "Carga de polvo ABC por vacío FS-ZR01", (2.5, 10.4, 1.6, 1.8), "RC-PV", 1, "carga_polvo", "S"),
    ("R09c", "Carga de polvo BC (cargadora portátil exclusiva)", (4.3, 10.6, 1.0, 1.0), "RC-PV", 0, "carga_polvo",
     "S"),
    ("R16", "Carga manual clase D (embudo)", (5.5, 10.6, 1.0, 1.0), "RC-PV", 0, "banco", "S"),
    ("R18", "Deshumidificador y filtro de la extracción (8 renov./h)", (8.6, 10.4, 2.0, 1.0), "RC-PV", 0,
     "deshumidificador", "S"),
    ("R10a", "Ensamblaje y marbete: morsa FS-MC", (0.7, 13.3, 1.6, 1.0), "RC-PV", 1, "ensamble", "S"),
    ("R10b", "Ensamblaje y marbete: morsa FS-MC", (2.5, 13.3, 1.6, 1.0), "RC-PV", 1, "ensamble", "S"),
    ("R10c", "Ensamblaje y marbete: morsa FS-MC", (4.3, 13.3, 1.6, 1.0), "RC-PV", 0, "ensamble", "S"),
    ("R11a", "Presurización con N₂ FS-N2C (pinza)", (6.1, 13.3, 1.5, 1.0), "RC-PV", 1, "presurizacion", "S"),
    ("R11b", "Presurización con N₂ FS-N2C (pinza)", (7.8, 13.3, 1.5, 1.0), "RC-PV", 0, "presurizacion", "S"),
    # fuera de línea
    ("R23", "Laboratorio: Puffer (IRAM 3672) y mufla", (0.7, 14.8, 1.6, 0.8), "RC-LB", 1, "banco", "N"),
    ("RRI", "Rack de insumos de recargas", (6.6, 14.7, 2.3, 1.1), "RC-IN", 0, "rack", "N"),
    # zona general este
    ("R12", "Ensayo de pérdidas: tanque de inmersión", (12.6, 2.4, 1.8, 1.0), "RC-PE", 1, "hermeticidad", "S"),
    ("R22", "Ensayo de peso (balanza de precisión)", (14.6, 2.6, 0.9, 0.8), "RC-PE", 0, "balanza", "S"),
    ("R21a", "Precinto y etiquetado (oblea IRAM, marbete)", (15.6, 2.6, 1.0, 0.8), "RC-PE", 1, "etiquetadora", "S"),
    ("R21b", "Precinto y etiquetado (oblea IRAM, marbete)", (16.7, 2.6, 1.0, 0.8), "RC-PE", 1, "etiquetadora", "S"),
    ("R26", "Descarga de líquidos: IBC 1.000 L (AFFF) y tanque 600 L (agua)", (12.6, 4.6, 2.4, 1.2), "RC-LQ", 0,
     "hermeticidad", "N"),
    ("R25", "Desarme y enjuague con boroscopio", (15.4, 4.6, 1.4, 0.9), "RC-LQ", 1, "banco", "N"),
    ("R14", "Carga de líquidos: premezcla 600 L, bomba 40 L/min, balanza", (12.6, 6.8, 2.6, 1.1), "RC-LQ", 0,
     "hermeticidad", "S"),
    ("R24", "CO₂: trasvasadora 103/D1 (recupera y carga)", (12.6, 8.4, 1.4, 1.0), "RC-GA", 1, "presurizacion", "N"),
    ("R24m", "Manifold de CO₂: cilindro de suministro y de recuperación", (12.6, 10.7, 2.6, 0.8), "RC-GA", 0,
     "bateria_gas", "S"),
    ("R13", "CO₂: desarme, boroscopio, espesores, balanza y morsa", (15.6, 8.4, 2.0, 1.0), "RC-GA", 0, "banco", "N"),
    ("R27o", "Halogenados: cilindros de origen (suministro, almacenamiento)", (12.6, 12.0, 1.4, 1.4), "RC-HA", 0,
     "bateria_gas", "E"),
    ("R27", "Halogenados: unidad THB/BP (recupera y carga, circuito cerrado)", (14.3, 12.1, 1.2, 0.9), "RC-HA", 1,
     "presurizacion", "N"),
    ("R27n", "N₂ o argón con regulador (presurizar)", (14.3, 14.0, 1.2, 0.6), "RC-HA", 0, "bateria_gas", "S"),
    ("R27d", "Halogenados: cilindros de destino (recuperación, contaminados)", (15.9, 12.0, 1.7, 1.4), "RC-HA", 0,
     "bateria_gas", "O"),
    ("R07", "PH FS-HPT1 (3 estaciones, apto CO₂) con jaula", (12.6, 15.2, 2.6, 1.8), "RC-PH", 1, "ph", "N"),
    ("R08", "Secado FS-D4 (4 cabezales) y cámara de inspección", (15.6, 15.2, 2.0, 1.0), "RC-PH", 0, "secadora",
     "N"),
]
for _c, _n, (_x, _y, _w, _h), _s, _op, _t, _f in _RC:
    EQUIPOS.append(Equipo(_c, _n, Rw(_x, _y, _w, _h), _s, _op, 0.5,
                          fuente="X-DT Análisis Recargas 2035; W-REC", tipo=_t, frente=_f,
                          forma="rack" if _t == "rack" else "rect"))

# ============================================================ NUMERACIÓN DE PASOS (orden de los Word)
# manuales (W-MAN): 1 corte de chapa, 2 corte de tubo, 3 disco y embutido, 4 cuello, 5 numerado, 6 cilindrado,
# 7 soldadura longitudinal, 8 soldadura de cuello, 9 encastre, 10 bordoneado, 11 soldadura circ., 12 espesor,
# 13 PH, 14 secado, 15 granallado, 16 detección, 17 corrección, 18 pintura, 19 carga, 20 ensamblaje,
# 21 presurización, 22 pérdidas, 23 etiquetado, 24 embalaje. Carros (W-CAR): C2 corte ... C9 PH; recargas (W-REC):
# R1 ... R14 del mapa del proceso.
PASOS = {
    "M04": "1", "M16": "2", "M06": "3.1", "M07": "3.2", "M08": "3.3", "M09a": "4.1", "M09b": "4.2", "M10": "5",
    "B02": "6", "B03": "7", "M11": "8", "E09": "9", "B04": "10", "A06": "11.1", "B06": "11.2", "Q01": "12",
    "A07": "13.1", "B07": "13.2", "B14a": "14.1", "B14b": "14.2", "B14c": "14.3", "B14d": "14.4", "RIN": "15",
    "B08": "15", "ROUT": "15", "B09": "16", "B10": "17", "P01": "18.1", "P04": "18.2", "P03": "18.3",
    "P06": "18.4", "P08": "18.5", "BB1": "19", "T01": "19", "T03": "20", "T05": "21", "T06": "22", "T07": "23",
    "T09": "24.1", "T08": "24.2", "AC1": "24", "T11": "24.3",
    "MK1": "C2.1", "C01": "C3", "C02a": "C4.1", "C02b": "C4.2", "C04": "C5", "C06": "C6", "C05": "C7",
    "C08": "C8", "C09": "C8", "C81": "C8.1", "C07": "C9", "C10": "C10", "BB2": "C12", "T02": "C12", "T12": "C13",
    "T13": "C14",
    "R01": "R1", "R19a": "R2.1", "R19b": "R2.2", "R02a": "R3.1", "R02b": "R3.2", "R02c": "R3.3", "R02d": "R3.4",
    "R02e": "R3.5", "R04a": "R4.1", "R04b": "R4.2", "R04c": "R4.3", "R05": "R4.4", "R23": "R5", "R07": "R6",
    "R08": "R7", "R20a": "R8.1", "R20b": "R8.2", "R09a": "R9.1", "R09b": "R9.2", "R09c": "R9.3", "R16": "R9.4",
    "R10a": "R10.1", "R10b": "R10.2", "R10c": "R10.3", "R11a": "R11.1", "R11b": "R11.2", "R12": "R12",
    "R22": "R13.1", "R21a": "R13.2", "R21b": "R13.3", "R17a": "R13.4", "R17b": "R13.5",
    "R26": "R3-L", "R25": "R4-L", "R14": "R9-L", "R24": "R3/9-C", "R13": "R4-C", "R27": "R3/9-H",
}
for _e in EQUIPOS:
    _e.paso = PASOS.get(_e.cod, "")


# ============================================================ PULMONES (carros entre puestos, W-MAN / W-CAR)
_FC = "Carro FCHP20505 (3 planos de 1280 × 610 mm)"
_CE = "Carros de estantes de 12 cajones"
PULMONES = [
    # corte de chapa y cuerpo de manuales
    Pulmon("PU-1", R(29.9, 26.5, 32.1, 28.7), "Rampa trasera: carro de salida y carro de plataforma de desarrollos",
           "1 Guillotina", "6 Cilindrado / C2.1 marcado", 2, "h"),
    Pulmon("PU-M", R(33.9, 24.9, 35.6, 27.2), "EFE 600 (25 y 50 kg) y mesa móvil (70 y 100 kg) con cuerpos grabados",
           "C2.1 Marcado", "C3 Cilindrado de carros", 2, "v"),
    Pulmon("PU-D", R(36.9, 26.9, 38.5, 27.8), "Carro de plataforma con desarrollos (al lado de la roladora)",
           "1 Guillotina", "6 Cilindrado", 1, "h"),
    Pulmon("PU-V1", R(37.0, 29.8, 38.3, 30.45), _FC + ": virolas", "6 Cilindrado", "7 Sold. longitudinal", 1, "h"),
    Pulmon("PU-V2", R(37.0, 32.5, 38.3, 33.15), _FC + ": cuerpos soldados (se llena)", "7 Sold. longitudinal",
           "9 Encastre", 1, "h"),
    Pulmon("PU-V3", R(36.0, 33.8, 37.3, 34.45), _FC + ": cuerpos soldados (al lado del encastre)",
           "7 Sold. longitudinal", "9 Encastre", 1, "h"),
    # tubo, embutido y cuello
    Pulmon("PU-T1", R(27.3, 35.0, 28.6, 36.8), _CE + ": tramos «en llenado» y «vacío»", "2 Corte de tubo",
           "9 Encastre", 2, "v"),
    Pulmon("PU-T2", R(33.9, 35.6, 35.8, 36.9), _CE + ": tramos «en consumo» y «lleno»", "2 Corte de tubo",
           "9 Encastre", 2, "h"),
    Pulmon("PU-K", R(31.5, 40.5, 34.3, 41.6), _CE + ": cúpulas y fondos en llenado", "3 Embutido",
           "Zonas de cúpulas y de fondos", 2, "h"),
    Pulmon("PU-FO", R(33.9, 37.1, 37.3, 39.1), "Zona de fondos: 3 a 5 carros (colchón de la tanda)", "3 Embutido",
           "9 Encastre", 3, "h"),
    Pulmon("PU-CU", R(34.6, 40.6, 38.8, 43.4), "Zona de cúpulas: carros numerados por orden de llegada",
           "3 Embutido", "5 Numerado", 3, "h"),
    Pulmon("PU-CC2", R(44.4, 40.6, 46.0, 43.4), _CE + ": cúpulas con cuello (en llenado)", "8 Sold. de cuello",
           "11 Sold. circunferencial", 2, "v"),
    Pulmon("PU-CC", R(40.4, 37.3, 44.8, 38.6), _CE + ": cúpulas con cuello al lado de las soldadoras",
           "8 Sold. de cuello", "11 Sold. circunferencial", 3, "h"),
    # línea principal
    Pulmon("PU-E", R(37.45, 35.6, 38.1, 36.9), _FC, "9 Encastre", "10 Bordoneado", 1, "v"),
    Pulmon("PU-B", R(39.5, 35.6, 40.15, 36.9), _FC, "10 Bordoneado", "11 Sold. circunferencial", 1, "v"),
    Pulmon("PU-S", R(45.0, 35.6, 45.65, 36.9), _FC + ": tarjeta «espesor OK»", "11 Sold. circunferencial",
           "13 PH", 1, "v"),
    Pulmon("PU-RT", R(45.0, 37.3, 47.3, 38.6), "Retenidos (zona demarcada en rojo)", "12 Control de espesor",
           "13 PH o scrap", 2, "h"),
    Pulmon("PU-6", R(52.9, 35.6, 54.4, 38.6), "Cilindros probados (mojados) en sus carros", "13 PH", "14 Secado",
           2, "v"),
    Pulmon("PU-7", R(62.3, 35.6, 63.8, 38.6), "Cilindros secos con tapón: al lado de la boca de entrada",
           "14 Secado", "15 Granallado", 2, "v"),
    # terminación (un FCHP20505 entre cada par de puestos)
    Pulmon("PU-F1", R(59.2, 10.5, 59.85, 11.8), _FC, "19 Carga de polvo", "20 Ensamblaje", 1, "v"),
    Pulmon("PU-F2", R(61.9, 10.5, 62.55, 11.8), _FC, "20 Ensamblaje", "21 Presurización", 1, "v"),
    Pulmon("PU-F3", R(64.5, 10.5, 65.15, 11.8), _FC, "21 Presurización", "22 Ensayo de pérdidas", 1, "v"),
    Pulmon("PU-F4", R(67.6, 10.5, 68.25, 11.8), _FC, "22 Ensayo de pérdidas", "23 Etiquetado", 1, "v"),
    Pulmon("PU-F5", R(66.6, 8.95, 67.9, 9.6), _FC + ": etiqueta hacia afuera", "23 Etiquetado", "24 Encajonado",
           1, "h"),
    Pulmon("PU-TP", R(55.6, 16.0, 60.6, 18.4), "Terminados pintados en carros (con tapón de silicona)",
           "18 Descarga de pintura", "19 Carga de polvo", 4, "h"),
    # carros
    Pulmon("PU-CI", R(37.9, 16.0, 39.4, 18.6), "EFE 600 y mesa móvil frente a la zona de carga", "C2.1 Marcado",
           "C3 Cilindrado", 2, "v"),
    Pulmon("PU-CR", R(34.2, 14.4, 35.2, 16.2), "Pulmón de cuerpos rolados (1,8 × 1,2, amarillo)", "C3 Cilindrado",
           "C4 Punteo", 1, "v"),
    Pulmon("PU-CP", R(26.6, 14.7, 27.2, 16.3), "Pulmón de cuerpos punteados (1,6 × 1,2)", "C4 Punteo",
           "C5 Sold. longitudinal", 1, "v"),
    Pulmon("PU-CK", R(31.5, 9.5, 32.7, 10.4), "Carro de kits (≈ 10 kits)", "C8.1 Accesorios", "C8 Accesorios",
           1, "h"),
]

# ============================================================ PUERTAS Y PORTONES
# Tres portones en toda la nave (MP, recargas y muelle); el resto son puertas de personas y de emergencia.
PUERTAS = [
    Puerta("P1", "N", 2.0, 6.4, 4.5, "porton",
           "MP de producción y carros: hojas, flejes, caños y barras, casquetes, insumos de montaje, alambre y "
           "granalla; sale el scrap al volquete"),
    Puerta("P2", "S", 0.8, 3.6, 3.0, "porton", "Recargas: los utilitarios dejan y retiran equipos y traen insumos"),
    Puerta("P3", "S", 49.3, 52.3, 3.2, "muelle",
           "Muelle único: sale PT y carros; entran polvo, pintura en polvo, embalaje y revendidos"),
    # salidas de emergencia (1,10 m, barral antipánico, abren hacia afuera)
    Puerta("SE-1", "N", 46.5, 47.6, 2.1, "emergencia"),
    Puerta("SE-3", "N", 66.0, 67.1, 2.1, "emergencia"),
    Puerta("SE-4", "N", 80.0, 81.1, 2.1, "emergencia"),
    Puerta("SE-5", "E", 39.25, 40.35, 2.1, "emergencia"),
    Puerta("SE-6", "E", 33.55, 34.65, 2.1, "emergencia"),
    Puerta("SE-7", "S", 86.0, 87.1, 2.1, "emergencia"),
    Puerta("SE-8", "S", 11.05, 12.15, 2.1, "emergencia"),
    Puerta("SE-9", "S", 70.6, 71.7, 2.1, "emergencia"),
    Puerta("SE-10", "O", 7.0, 8.1, 2.1, "emergencia"),
    Puerta("SE-11", "O", 17.6, 18.7, 2.1, "emergencia"),
    Puerta("PP-1", "O", 23.2, 24.4, 2.1, "peatonal", "Ingreso de personal desde vestuarios"),
    Puerta("PG", "N", 48.3, 49.3, 2.1, "peatonal", "A la jaula exterior de gases (control de presión y cambio de pack)"),
]

# ventanas en el cerramiento de la nave: (lado, desde, hasta, uso)
VENTANAS_NAVE = [("O", 19.4, 20.9, "Administración: vista a lo largo del pasillo central")]

# ============================================================ ANEXOS
ANEXOS = [
    Sector("SV", "Bloque de servicios al personal y administración", R(-18.0, 19.0, 0.0, 35.0), "SERV", "común"),
    Sector("RC", "Recargas (ángulo SO de la nave)", R(0.3, 0.3, 18.0, 18.8), "RC", "RC",
           "Dentro de la nave, con tabiques propios: zona general, recinto de polvo y fuera de línea (W-REC)"),
    Sector("ST", "Sala técnica: transformador, TGBT y compresores", R(36.0, 44.2, 46.0, 50.0), "AUX", "común"),
]

# ============================================================ RIEL AÉREO DE PINTURA (W-MAN)
# cargado: detección -> norte del esquema -> precalentamiento -> cabina -> curado (2 en paralelo) -> descarga
RIEL = [(74.6, 36.4), (86.6, 36.4), (86.6, 22.1), (79.15, 22.1), (79.15, 17.0), (82.42, 17.0), (82.42, 6.5)]
RIEL_2 = [(82.42, 17.0), (85.42, 17.0), (85.42, 9.9)]
RIEL_RET = [(81.2, 5.0), (78.9, 5.0), (78.9, 35.0), (74.9, 35.0)]
LAZO = RIEL                          # compatibilidad con el dibujo del transportador
TL = []                              # sin tren logístico: carros a mano entre puestos pegados (W-MAN)
TL_CARGADO = []
TL_RETORNO = []

# ============================================================ FLUJOS (m)
FLUJOS = [
    # ---------------- MP: una sola recepción por P1 (W-MAN: playón -> cuarentena compartida con carros)
    Flujo("MP", [(4.2, 52.0), (4.2, 43.8), (4.2, 30.0), (6.6, 30.0)],
          "Recepción: alero -> P1 -> A1 -> cuarentena (colada, espesor y lote)"),
    Flujo("MP", [(6.6, 31.6), (5.4, 31.6), (5.4, 40.4), (12.4, 40.4), (12.4, 30.5), (10.6, 30.5)],
          "Hojas aprobadas: cuarentena -> A1 -> AN -> A2 -> paquetes de manuales"),
    Flujo("MP", [(10.6, 27.0), (13.2, 27.0), (13.2, 39.6), (21.2, 39.6), (21.2, 26.2), (24.8, 26.2)],
          "Paquete a la mesa elevadora (autoelevador de costado por A2, AN y A3)"),
    Flujo("MP", [(15.6, 29.4), (14.4, 29.4), (14.4, 38.8), (22.4, 38.8), (22.4, 25.6), (24.8, 25.6)],
          "Paquete LAC de carros a la misma mesa elevadora"),
    Flujo("MP", [(10.5, 42.2), (10.5, 41.6), (24.8, 41.6)], "Rollo de fleje al desbobinador (espolón por AN)"),
    Flujo("MP", [(19.5, 28.4), (23.4, 28.4), (23.4, 33.2), (24.75, 33.2)],
          "Atado de caños del cantiléver al cajón del láser (pluma)"),
    Flujo("MP", [(19.5, 30.2), (20.0, 30.2), (20.0, 21.2), (18.6, 21.2), (18.6, 6.6), (23.6, 6.6), (23.6, 5.0)],
          "Barras y caños de carros: A3 -> pasillo central -> PO-CW -> rack del puesto 8.1", "S3"),
    Flujo("MP", [(20.3, 42.2), (20.3, 21.8), (20.9, 21.8), (20.9, 13.45), (23.4, 13.45),
                 (23.4, 13.2)], "Casquetes y cuplas: carros 1 y 2 a los puestos 6 y 7", "S3"),
    # ---------------- MP por el muelle P3: polvo, pintura y embalaje (recepción 7 a 10 h)
    Flujo("MP", [(50.8, -6.0), (50.8, 0.0), (50.8, 3.2), (57.3, 3.2), (57.3, 4.6)],
          "Big bags de polvo y pintura en polvo (P3 -> AT -> depósito)"),
    Flujo("MP", [(56.6, 7.6), (56.6, 10.2)], "Big bag de ABC 60 a la estación de la carga (autoelevador)"),
    Flujo("MP", [(55.2, 5.4), (54.0, 5.4), (54.0, 20.0), (41.7, 20.0), (41.7, 12.0), (40.8, 12.0)],
          "Big bag de ABC 90 a la terminación de carros (AC -> PC -> PO-CN)", "S3"),
    Flujo("MP", [(55.2, 6.4), (54.6, 6.4), (54.6, 20.4), (75.4, 20.4), (75.4, 17.6), (78.3, 17.6)],
          "Pintura en polvo a las tolvas de la cabina (AC -> PC -> PO-PI)"),
    Flujo("MP", [(46.0, -6.0), (46.0, 0.0), (46.0, 1.6)], "Revendidos al rack S4 (P3)", "S4"),
    # ---------------- SE: corte de chapa, tubo y cuerpo (W-MAN)
    Flujo("SE", [(29.7, 27.0), (29.9, 27.0)], "Desarrollos a la rampa"),
    Flujo("SE", [(32.1, 27.6), (36.6, 27.6), (36.9, 27.4)], "Carro de plataforma con desarrollos al lado de la roladora",
          "S2"),
    Flujo("SE", [(32.1, 26.6), (32.3, 26.6)], "Cuerpo de carro al marcado", "S3"),
    Flujo("SE", [(37.6, 29.6), (37.6, 29.8)], "Virola al FCHP"),
    Flujo("SE", [(37.65, 30.45), (37.65, 30.8)], "Virola a la soldadora"),
    Flujo("SE", [(37.65, 32.2), (37.65, 32.5)], "Cuerpo soldado al FCHP"),
    Flujo("SE", [(37.0, 32.8), (36.65, 32.8), (36.65, 33.8)], "FCHP lleno al lado del encastre", "S2"),
    Flujo("SE", [(36.65, 34.45), (36.65, 35.8)], "Cuerpos 2,5-10 kg al encastre", "S2"),
    Flujo("SE", [(26.15, 36.6), (27.3, 36.6)], "Tramos 1 kg al carro de cajones", "S1"),
    Flujo("SE", [(28.6, 36.2), (33.9, 36.2)], "Carro de tramos al encastre", "S1"),
    Flujo("SE", [(35.8, 36.3), (36.0, 36.3)], "Tramo al encastre", "S1"),
    # ---------------- SE: embutido, celda de cuello y fondos
    Flujo("SE", [(26.6, 42.4), (26.9, 42.4)], "Fleje enderezado"),
    Flujo("SE", [(28.5, 42.4), (28.8, 42.4)], "Fleje al troquel"),
    Flujo("SE", [(30.4, 41.35), (30.4, 41.05), (31.5, 41.05)], "Cúpulas y fondos a los carros de cajones"),
    Flujo("SE", [(34.3, 41.0), (34.6, 41.0)], "Carro de cúpulas a la zona de cúpulas"),
    Flujo("SE", [(33.0, 40.5), (33.0, 39.6), (34.4, 39.6), (34.4, 39.1)], "Carro de fondos a la zona de fondos"),
    Flujo("SE", [(36.6, 37.1), (36.6, 36.8)], "Fondos al encastre"),
    Flujo("SE", [(38.8, 42.2), (39.0, 42.2), (40.0, 42.2), (40.2, 42.2), (41.2, 42.2), (41.4, 42.2), (42.4, 42.2),
                 (42.6, 42.2), (44.2, 42.2), (44.4, 42.2)],
          "Celda: numerado -> muesca del cuello -> soldadura de cuello (sin transporte)"),
    Flujo("SE", [(45.2, 40.6), (45.2, 39.0), (44.5, 39.0), (44.5, 38.6)],
          "Cúpulas con cuello a las soldadoras circ."),
    # ---------------- SE: línea principal (eje y = 36,2)
    Flujo("SE", [(37.2, 36.2), (37.45, 36.2), (38.1, 36.2), (38.3, 36.2), (39.3, 36.2), (39.5, 36.2), (40.15, 36.2),
                 (40.4, 36.2), (42.4, 36.2), (42.8, 36.2), (44.8, 36.2), (45.0, 36.2), (45.65, 36.2), (45.9, 36.2),
                 (47.1, 36.2), (47.5, 36.2), (49.9, 36.2), (50.2, 36.2), (52.6, 36.2), (52.9, 36.2), (54.4, 36.2),
                 (54.7, 36.2), (60.9, 36.2), (62.3, 36.2), (63.8, 36.2), (64.0, 36.2), (65.5, 36.2), (65.6, 36.2),
                 (70.1, 36.2), (70.2, 36.2), (71.7, 36.2), (71.9, 36.2)],
          "Línea principal: encastre -> bordoneado -> soldadura circ. -> espesor -> PH -> secado -> granallado -> "
          "detección"),
    Flujo("SE", [(46.5, 36.6), (46.5, 37.3)], "Lote rechazado a retenidos"),
    Flujo("SE", [(72.4, 37.0), (72.4, 37.4)], "Defectuosos a las jaulas"),
    Flujo("SE", [(72.4, 38.4), (72.4, 39.05), (76.0, 39.05), (76.0, 38.9)], "Jaula «a corregir» a la corrección"),
    Flujo("SE", [(76.7, 38.9), (76.7, 39.15), (64.6, 39.15), (64.6, 36.8)],
          "Corregidos y a re-granallar: vuelven a los rodillos de entrada"),
    # ---------------- riel aéreo (TL cargado; RET vacío)
    Flujo("TL", RIEL, "Riel aéreo: cuelga en la detección -> precalentamiento -> cabina -> curado -> descarga"),
    Flujo("TL", RIEL_2, "Riel aéreo: horno de curado 2 en paralelo"),
    Flujo("RET", RIEL_RET, "Retorno de ganchos vacíos a la detección (aéreo)"),
    # ---------------- SE: descarga de pintura, terminación y embalaje (W-MAN)
    Flujo("SE", [(81.2, 9.0), (75.7, 9.0), (75.7, 14.4), (58.2, 14.4), (58.2, 16.0)],
          "Terminados pintados (con tapón) a la espera de la carga (PO-PI -> AT2)"),
    Flujo("SE", [(57.2, 16.0), (57.2, 13.0), (58.2, 13.0), (58.2, 11.8)], "Carro de terminados a la carga"),
    Flujo("SE", [(57.2, 11.2), (57.4, 11.2), (59.0, 11.2), (59.2, 11.2), (59.85, 11.2), (60.1, 11.2), (61.7, 11.2),
                 (61.9, 11.2), (62.55, 11.2), (62.8, 11.2), (64.3, 11.2), (64.5, 11.2), (65.15, 11.2),
                 (65.4, 11.2), (67.4, 11.2), (67.6, 11.2), (68.25, 11.2), (68.4, 11.2)],
          "Terminación: carga -> ensamblaje -> presurización -> pérdidas -> etiquetado"),
    Flujo("SE", [(68.9, 10.6), (68.9, 9.9), (67.6, 9.9), (67.6, 9.6)], "Etiquetado al FCHP del encajonado"),
    Flujo("SE", [(67.25, 8.95), (67.25, 8.7)], "Terminados a la mesa de encajonado"),
    Flujo("SE", [(81.2, 6.4), (73.4, 6.4), (73.4, 8.3), (72.2, 8.3)],
          "Cilindros vacíos (con tapón de PE) a la mesa de encajonado de al lado"),
    Flujo("PT", [(67.4, 6.9), (67.4, 6.0)], "Cajas de terminados al pallet"),
    Flujo("PT", [(71.4, 6.9), (71.4, 6.0)], "Cajas de cilindros al pallet"),
    Flujo("PT", [(71.4, 5.0), (71.4, 4.75), (61.8, 4.75), (61.8, 5.0)], "Pallet de cilindros a la envolvedora"),
    Flujo("PT", [(67.4, 5.0), (67.4, 5.6), (61.8, 5.6)], "Pallet de terminados a la envolvedora"),
    Flujo("PT", [(60.9, 5.0), (60.9, 2.6), (50.75, 2.6), (50.75, 8.0)],
          "Pallets al almacén de PT y de cilindros (transpaleta por AT y T2)"),
    Flujo("PT", [(45.2, 9.0), (45.2, 3.6), (49.6, 3.6), (49.6, 0.0), (49.6, -6.0)], "Expedición (T1 -> muelle P3)"),
    Flujo("PT", [(43.6, 1.6), (43.6, 2.2), (48.2, 2.2), (48.2, 0.0), (48.2, -6.0)], "Revendidos a expedición", "S4"),
    # ---------------- SE: carros (W-CAR) en U
    Flujo("SE", [(34.75, 24.9), (34.75, 18.9), (38.6, 18.9), (38.6, 18.6)],
          "Cuerpos grabados de carros (EFE 600 / mesa móvil) a la roladora", "S3"),
    Flujo("SE", [(35.4, 15.3), (35.2, 15.3)], "Cuerpo rolado al pulmón", "S3"),
    Flujo("SE", [(34.2, 15.3), (32.6, 15.3), (32.6, 16.6), (31.4, 16.6), (28.6, 16.6)], "Punteo (2 viradores)", "S3"),
    Flujo("SE", [(27.4, 16.4), (27.2, 16.0)], "Cuerpo punteado al pulmón", "S3"),
    Flujo("SE", [(26.6, 15.2), (25.4, 15.2), (25.4, 16.9), (24.7, 16.9)], "Pulmón a la soldadura longitudinal", "S3"),
    Flujo("SE", [(22.4, 16.9), (22.0, 16.9), (22.0, 14.5), (25.9, 14.5), (25.9, 12.0), (27.6, 11.4)],
          "Cuerpo soldado al armado (cuna)", "S3"),
    Flujo("SE", [(23.9, 10.9), (27.6, 10.9)], "Cúpula con cupla al armado (carro canasto)", "S3"),
    Flujo("SE", [(29.2, 11.0), (33.2, 11.0)], "Cilindro cerrado a la soldadura de accesorios", "S3"),
    Flujo("SE", [(25.8, 5.2), (25.8, 7.6), (31.3, 7.6), (31.3, 9.9), (31.5, 9.9)], "Kits del puesto 8.1 al carro de kits",
          "S3"),
    Flujo("SE", [(34.8, 11.0), (35.6, 11.0), (35.6, 9.3)], "Recipiente a la inspección de costuras", "S3"),
    Flujo("SE", [(35.2, 8.4), (35.2, 6.2), (30.0, 6.2), (30.0, 3.4)],
          "Carro inspeccionado (sobre ruedas) a la PH", "S3"),
    Flujo("SE", [(30.0, 2.7), (32.4, 2.7)], "PH -> secado", "S3"),
    Flujo("SE", [(33.8, 2.7), (34.6, 2.7)], "Secado -> pulmón de despacho a pintura", "S3"),
    Flujo("SE", [(40.8, 2.8), (49.0, 2.8), (49.0, 0.0), (49.0, -6.0)],
          "Carros a pintura tercerizada y carros terminados (muelle P3)", "S3"),
    Flujo("SE", [(49.3, -6.0), (49.3, 0.0), (49.3, 6.6), (40.4, 6.6), (40.4, 10.8), (39.0, 10.8)],
          "Carros pintados (vuelven por P3) a la terminación de carros", "S3"),
    Flujo("SE", [(37.8, 11.9), (37.4, 11.9), (37.4, 9.6)], "Carga de polvo -> armado de válvula y manguera", "S3"),
    Flujo("SE", [(38.1, 9.0), (38.3, 9.0)], "Armado -> presurización y etiquetado", "S3"),
    Flujo("SE", [(39.0, 8.4), (39.0, 7.4), (37.2, 7.4), (37.2, 5.0)], "Carro terminado al pulmón del muelle", "S3"),
    # ---------------- scrap: contenedor en el puesto; el autoelevador lo lleva al volquete (P1)
    Flujo("SCRAP", [(30.6, 24.9), (30.6, 22.4), (22.6, 22.4), (22.6, 41.0), (4.0, 41.0), (4.0, 43.8), (1.2, 46.2)],
          "Orillas de la guillotina: autoelevador por el pasillo central, A3, AN y A1 al volquete (P1)"),
    Flujo("SCRAP", [(24.75, 28.6), (23.8, 28.6), (23.8, 40.2), (3.4, 40.2), (3.4, 43.8), (1.2, 45.8)],
          "Recortes del láser: autoelevador por A3 al volquete (P1)"),
    Flujo("SCRAP", [(32.2, 41.9), (32.2, 40.9), (31.4, 40.0), (25.2, 40.0), (25.2, 39.8), (2.8, 39.8), (2.8, 43.8),
                    (1.2, 45.4)], "Esqueleto de la prensa: contenedor por PO-3 y AN al volquete (P1)"),
    Flujo("SCRAP", [(74.6, 38.4), (74.6, 39.55), (2.4, 39.55), (2.4, 43.8), (1.2, 45.0)],
          "Descartes inutilizados al volquete (PO-3, AN y A1)"),
]

# ============================================================ HILOS DE PERSONAL (DIR)
Y_PP = 23.8          # eje de la senda peatonal del pasillo central


def _op(cod):
    """Punto de trabajo del primer operario de un equipo (al frente, 0,42 m)."""
    from .simbolos import frente_de
    e = next(e for e in EQUIPOS if e.cod == cod)
    r, f = e.rect, frente_de(e)
    return {"S": (r.c[0], r.y0 - 0.42), "N": (r.c[0], r.y1 + 0.42), "O": (r.x0 - 0.42, r.c[1]),
            "E": (r.x1 + 0.42, r.c[1])}[f]


def _hilos():
    H = []
    # recepción, corte de chapa y marcado: desde la senda del pasillo central
    br = [(26.9, Y_PP, 26.9, _op("M04")[1]), (26.9, _op("M04")[1], *_op("M04")),
          (_op("MK1")[0], Y_PP, *_op("MK1")), (5.0, Y_PP, 5.0, 33.7), (5.0, 33.7, *_op("MI1"))]
    H.append(("Recepción, corte de chapa y marcado (N1)", [(0.0, Y_PP), (36.0, Y_PP)], br))
    # cuerpo de manuales, láser, procesado y línea principal: por PO-1 y PO-2
    br = [(40.5, 28.4, 38.6, 28.4), (38.6, 28.4, *_op("B02")), (40.5, 30.4, 38.9, 30.4), (38.9, 30.4, *_op("B03"))]
    for c in ("E09", "B04", "A06", "B06", "Q01", "A07", "B07"):
        x, y = _op(c)
        br.append((x, 34.1, x, y))
    br += [(40.5, 34.1, 35.9, 34.1), (35.9, 34.1, 35.9, 35.0), (35.9, 35.0, *_op("E09"))]
    H.append(("Cuerpo, unión y PH (N4, N6)", [(36.0, Y_PP), (40.5, Y_PP), (40.5, 34.1), (54.0, 34.1)], br))
    # secado, granallado, detección y corrección: por PO-2 y PO-7
    br = []
    for c in ("B14a", "B14c", "B08", "B09"):
        x, y = _op(c)
        br.append((x, 34.1, x, y))
    br += [(61.6, 34.1, 61.6, 39.8), (74.9, 34.1, 78.2, 34.1), (78.2, 34.1, 78.2, _op("B10")[1]),
           (78.2, _op("B10")[1], *_op("B10"))]
    H.append(("Secado, granallado y detección (N5)", [(54.0, 34.1), (74.9, 34.1), (74.9, Y_PP)], br))
    # láser y embutido: por AN no (autoelevador): por PO-3 desde PO-7
    br = [(31.0, 39.8, *_op("M08")), (_op("M16")[0], 39.8, *_op("M16")), (_op("M10")[0], 39.8, *_op("M10")),
          (_op("M09a")[0], 39.8, *_op("M09a")), (_op("M09b")[0], 39.8, *_op("M09b")),
          (_op("M11")[0], 39.8, *_op("M11"))]
    H.append(("Láser, embutido y celda de cuello (N2, N3, N7)", [(61.6, 39.8), (26.65, 39.8)], br))
    # pintura, terminación y embalaje: por PO-PI
    br = [(74.9, 18.2, 77.6, 18.2), (77.6, 18.2, *_op("P04")), (74.9, 6.7, 79.8, 6.7), (79.8, 6.7, *_op("P08"))]
    br += [(74.9, 10.2, _op("T01")[0], 10.2)]
    br += [(66.3, 10.2, 66.3, _op("T09")[1]), (66.3, _op("T09")[1], *_op("T09")),
           (72.6, 10.2, 72.6, _op("T08")[1]), (72.6, _op("T08")[1], *_op("T08"))]
    H.append(("Pintura, terminación y embalaje", [(74.9, Y_PP), (74.9, 0.6)], br))
    # PT y expedición
    H.append(("PT y expedición", [(54.3, Y_PP), (54.3, 4.0)], [(54.3, 4.0, 47.0, 4.0)]))
    # carros: entran por PO-CW a la calle interior de la U
    br = []
    for c in ("C04", "C02a", "C02b"):
        x, y = _op(c)
        br.append((x, 13.7, x, y))
    for c in ("C06", "C05", "C08"):
        x, y = _op(c)
        br.append((x, 13.7, x, y))
    br += [(_op("C01")[0], 13.7, *_op("C01")), (19.6, 13.7, 19.6, 6.7), (19.6, 6.7, 18.4, 6.7),
           (18.4, 6.7, 18.4, _op("C81")[1]), (18.4, _op("C81")[1], *_op("C81")),
           (19.6, 6.7, _op("C07")[0], 6.7), (_op("C07")[0], 6.7, *_op("C07")),
           (_op("C09")[0], 13.7, *_op("C09")), (36.6, 13.7, 36.6, _op("T02")[1]), (36.6, _op("T02")[1], *_op("T02")),
           (36.6, _op("T02")[1], 36.6, _op("T13")[1]), (36.6, _op("T13")[1], *_op("T13"))]
    H.append(("Línea de carros (S3)", [(19.6, Y_PP), (19.6, 13.7), (40.5, 13.7)], br))
    # recargas
    H.append(("Recargas (RC)", [(11.6, Y_PP), (11.6, 0.6)], [(11.6, 18.1, 1.0, 18.1)]))
    return H


# ============================================================ LOCALES
# Servicios SV (x -18..0, y 19..35): sin cambios de la versión 7.
LOCALES = [
    Sector("SV-LU", "Utilitarios de limpieza", R(-17.9, 19.1, -15.2, 22.9), "SERV", "común",
           "Pileta de lavado, carros, máquina de piso y artículos de limpieza"),
    Sector("SV-HY", "Higiene y seguridad, medicina laboral, primeros auxilios y EPP", R(-15.0, 19.1, -10.6, 22.9),
           "SERV", "común", "Una sola persona: escritorio, camilla, botiquín y lavabo; entrega de EPP por ventanilla "
           "al pasillo limpio; salida directa al exterior para ambulancia (SV-3)"),
    Sector("SV-HA", "Hall, recepción y fichado", R(-10.4, 19.1, -7.6, 22.9), "SERV", "común",
           "Reloj biométrico y tablero de novedades al paso; atiende a visitas y proveedores"),
    Sector("SV-AD", "Administración: compras, ventas y RRHH", R(-7.4, 19.1, -0.1, 22.9), "SERV", "común",
           "4 puestos (compras 1, ventas 2, RRHH 1) y archivo; ventana a la nave a lo largo del pasillo central y "
           "puerta a PP-1 a 6 m: comunicación directa con producción"),
    Sector("SV-PL", "Pasillo limpio a la planta (PP-1)", R(-17.9, 23.0, -0.1, 24.5), "CIRC", "común"),
    Sector("SV-VH", "Vestuario hombres (60 lockers)", R(-17.9, 24.6, -10.9, 28.2), "SERV", "común",
           "1 locker por empleado: 2 bloques de 10 columnas × 3 filas = 60 (56 en 2035) y bancos"),
    Sector("SV-DH", "Duchas hombres", R(-17.9, 28.4, -15.1, 34.9), "SERV", "común",
           "3 duchas sobre la misma pared (art. 49: 55 H en el turno mañana con choferes), banco y percheros; "
           "separadas de inodoros y mingitorios"),
    Sector("SV-SH", "Inodoros, mingitorios y lavabos hombres", R(-14.9, 28.4, -10.9, 34.9), "SERV", "común",
           "3 inodoros en la pared norte, 6 mingitorios en la pared este y 6 lavabos en la pared oeste"),
    Sector("SV-VM", "Vestuario mujeres (9 lockers)", R(-10.7, 24.6, -7.1, 27.6), "SERV", "común",
           "1 bloque de 3 columnas × 3 filas = 9 lockers (7 en 2035) y banco"),
    Sector("SV-SM", "Inodoro y lavabo mujeres", R(-10.7, 27.8, -9.0, 31.0), "SERV", "común",
           "Art. 49: 6 M por turno -> 1 inodoro y 1 lavabo"),
    Sector("SV-DM", "Ducha mujeres", R(-8.8, 27.8, -7.1, 31.0), "SERV", "común", "1 ducha, separada del inodoro"),
    Sector("SV-AC", "Sanitario accesible con ducha", R(-10.7, 31.2, -7.1, 34.9), "SERV", "común",
           "Inodoro con 0,80 m libre lateral, lavabo, ducha a nivel con asiento rebatible y barras; círculo Ø 1,50 m "
           "(Ley 24.314, Dec. 914/97); entra desde el pasillo PS"),
    Sector("SV-PS", "Pasillo al sanitario accesible, al comedor y a la salida SV-2", R(-6.9, 24.6, -5.7, 34.9),
           "CIRC", "común"),
    Sector("SV-CM", "Comedor (30 plazas) y office", R(-5.5, 24.6, -0.1, 34.9), "SERV", "común",
           "5 mesas de 6 lejos de la puerta; office con bacha y lavamanos sobre la misma pared; 2 tandas de 30 min"),
    # sanitarios de planta: junto a terminación, embalaje, pintura y PT (entran desde la calle AT2)
    Sector("SN-H", "Sanitarios hombres (planta)", R(64.0, 16.0, 70.2, 18.8), "SERV", "común",
           "2 inodoros y 2 mingitorios (pared norte) y 2 lavabos (pared este)"),
    Sector("SN-M", "Sanitario mujeres (planta)", R(61.0, 16.0, 63.8, 18.8), "SERV", "común", "1 inodoro y lavabo"),
    # recargas (W-REC): zona general, recinto de polvo (HR ≤ 70 %) y fuera de línea
    Sector("RC-RD", "Recepción, registro y despacho (portón P2)", R(0.5, 0.5, 6.6, 4.8), "RC", "RC",
           "Zona general: recepción y registro, despacho (X-DT 2), flota de intercambio y jaulas de 1 kg "
           "(X-DT Almacén PT)"),
    Sector("RC-IV", "Inspección visual (zona general)", R(6.8, 0.5, 10.8, 4.8), "RC", "RC",
           "2 puestos (X-DT); pasaplatos 1 al recinto de polvo"),
    Sector("RC-PV", "Recinto de polvo químico (HR ≤ 70 %)", R(0.5, 5.0, 10.8, 14.4), "RC", "RC",
           "W-REC: descarga, desarme y limpieza, pintura (cabina), carga, ensamblaje y marbete, presurización; "
           "deshumidificador sin estufas, 8 renovaciones por hora con filtro; entra por la antecámara; 3 pasaplatos",
           32.0),
    Sector("RC-LB", "Laboratorio de polvo y calidad de recargas", R(0.5, 14.6, 3.9, 17.4), "RC", "RC",
           "Fuera de línea: Puffer y mufla (W-REC 5); patrones con calibración vigente (IRAM 3517-2)"),
    Sector("RC-IR", "Inutilización y disposición final", R(4.1, 14.6, 6.3, 17.4), "RC", "RC",
           "Fuera de línea (W-REC 14): jaula NO APTO, tambores de residuo; comprobante de cada retiro"),
    Sector("RC-IN", "Insumos de recargas", R(6.5, 14.6, 9.0, 17.4), "RC", "RC",
           f"{_V5}: 10 posiciones, 9,6 m² netos: agente limpio, AFFF, acetato de potasio, obleas y marbetes"),
    Sector("RC-AC", "Antecámara del recinto de polvo", R(9.2, 14.6, 10.8, 17.4), "RC", "RC",
           "W-REC: dos puertas con cierre automático; EPP del recinto"),
    Sector("RC-PE", "Pérdidas, peso, precinto y etiquetado", R(12.4, 0.5, 17.8, 4.4), "RC", "RC",
           "Zona general (W-REC 12 y 13): tanque de inmersión, balanza y 2 puestos de etiquetado (X-DT)"),
    Sector("RC-LQ", "Líquidos: agua, AFFF y clase K", R(12.4, 4.6, 17.8, 8.2), "RC", "RC",
           "W-REC: fuera del recinto; IBC 1.000 L (AFFF) y tanque 600 L (agua) con tubo buzo y venteo; premezcla "
           "al 3 % con refractómetro; el AFFF va a bidones de operador habilitado"),
    Sector("RC-GA", "CO₂: recuperación, desarme y carga", R(12.4, 8.4, 17.8, 11.6), "RC", "RC",
           "W-REC: trasvasadora 103/D1 con manifold (cilindro de suministro y de recuperación, nunca dos válvulas "
           "abiertas); el stock de cilindros llenos está en la jaula exterior"),
    Sector("RC-HA", "Halogenados: circuito cerrado", R(12.4, 11.8, 17.8, 14.8), "RC", "RC",
           "W-REC (diagrama de gases): THB/BP al centro; origen a la entrada (extintor, recuperación, almacenamiento, "
           "suministro), destino a la salida (recuperación, almacenamiento, contaminados), N₂ o argón arriba y bomba "
           "de vacío abajo"),
    Sector("RC-PH", "Prueba hidráulica, secado y cámara", R(12.4, 15.0, 17.8, 18.6), "RC", "RC",
           "Zona general (W-REC 6 y 7): pasa al recinto por el pasaplatos 3"),
]

PUERTAS_ANEXOS = [
    ("SV-1", (-9.8, 19.0), (-8.2, 19.0), "peatonal", "Ingreso de personal y visitas (camino peatonal desde G4)"),
    ("SV-2", (-6.8, 35.0), (-5.8, 35.0), "peatonal", "Salida de emergencia al final del pasillo PS"),
    ("SV-3", (-14.6, 19.0), (-13.6, 19.0), "peatonal", "Higiene y seguridad: salida a ambulancia"),
]

# ============================================================ MOBILIARIO (ningún local vacío)
Mb = Mueble
MOBILIARIO = [
    # ---- SV-LU utilitarios de limpieza
    Mb("lavadero", R(-17.85, 22.2, -16.2, 22.85), "S"), Mb("carro_limpieza", R(-17.8, 19.2, -17.1, 19.8), "N"),
    Mb("carro_limpieza", R(-16.9, 19.2, -16.2, 19.8), "N"), Mb("estanteria", R(-15.75, 19.2, -15.25, 21.4), "O"),
    # ---- SV-HY higiene y seguridad + medicina laboral + primeros auxilios + EPP (una persona)
    Mb("escritorio", R(-12.6, 19.15, -10.65, 20.45), "N"), Mb("camilla", R(-14.95, 19.6, -14.25, 21.5), "E"),
    Mb("botiquin", R(-14.95, 21.8, -14.6, 22.6), "E"), Mb("lavabos", R(-13.9, 22.35, -13.2, 22.85), "S", 1),
    Mb("estanteria", R(-11.15, 20.6, -10.65, 21.9), "O"), Mb("ventanilla", R(-13.0, 22.45, -11.7, 22.85), "S"),
    Mb("lavaojos", R(-14.95, 22.65, -14.4, 22.85), "E"),
    # ---- SV-HA hall, recepción y fichado
    Mb("mostrador", R(-10.35, 21.0, -9.2, 22.4), "E"), Mb("reloj", R(-9.0, 22.55, -8.6, 22.85), "S"),
    Mb("sillas", R(-10.35, 19.4, -9.9, 20.6), "E", 2),
    # ---- SV-AD administración: compras, ventas y RRHH
    *[Mb("escritorio", R(-6.9 + i * 1.9, 21.55, -5.1 + i * 1.9, 22.85), "S") for i in range(3)],
    Mb("escritorio", R(-2.0, 19.15, -0.2, 20.45), "N"), Mb("archivo", R(-6.9, 19.15, -4.4, 19.6), "N", 4),
    Mb("pizarra", R(-0.2, 20.8, -0.12, 22.0), "O"),
    # ---- SV-VH vestuario hombres: 2 bloques de lockers de 10 columnas × 3 filas = 60
    Mb("lockers", R(-17.88, 24.9, -17.38, 27.9), "E", 10), Mb("lockers", R(-11.42, 24.9, -10.92, 27.9), "O", 10),
    Mb("banco_vest", R(-16.6, 25.2, -16.2, 27.4), "E"), Mb("banco_vest", R(-12.6, 25.2, -12.2, 27.4), "O"),
    # ---- SV-DH duchas hombres (pared oeste)
    Mb("duchas", R(-17.85, 31.0, -16.95, 34.85), "E", 3), Mb("banco_vest", R(-15.9, 29.2, -15.5, 33.6), "O"),
    # ---- SV-SH inodoros (norte), mingitorios (este) y lavabos (oeste)
    Mb("inodoro", R(-14.85, 33.4, -11.95, 34.85), "S", 3), Mb("mingitorios", R(-11.35, 28.9, -10.95, 32.5), "O", 6),
    Mb("lavabos", R(-14.85, 28.7, -14.35, 31.7), "E", 6),
    # ---- SV-VM y sanitarios de mujeres
    Mb("lockers", R(-10.68, 25.0, -10.18, 25.9), "E", 3), Mb("banco_vest", R(-9.0, 25.0, -8.6, 27.2), "O"),
    Mb("inodoro", R(-10.65, 29.5, -9.05, 30.95), "S", 1), Mb("lavabos", R(-10.65, 27.85, -10.15, 28.65), "E", 1),
    Mb("duchas", R(-8.75, 30.05, -7.85, 30.95), "S", 1), Mb("banco_vest", R(-7.55, 29.0, -7.15, 29.9), "O"),
    # ---- SV-AC sanitario accesible con ducha (a nivel, asiento rebatible)
    Mb("inodoro_acc", R(-10.65, 31.25, -8.9, 34.85), "E"), Mb("lavabos", R(-8.85, 34.35, -8.15, 34.85), "S", 1),
    Mb("ducha_acc", R(-8.6, 31.25, -7.15, 32.65), "N"),
    # ---- SV-CM comedor: office junto a la puerta (bacha y lavamanos en la misma pared) y mesas al fondo
    Mb("mesada", R(-3.6, 24.65, -0.15, 25.25), "N", 2), Mb("lavabos", R(-0.65, 25.4, -0.15, 26.6), "O", 2),
    Mb("heladera", R(-0.85, 26.8, -0.15, 27.5), "O"), Mb("dispenser", R(-0.55, 27.7, -0.15, 28.1), "O"),
    *[Mb("mesa", R(x0, y0, x0 + 1.7, y0 + 2.0), "S", 6) for x0, y0 in
      ((-4.9, 28.2), (-2.3, 28.2), (-4.9, 30.6), (-2.3, 30.6), (-4.9, 32.8))],
    # ---- MT taller de mantenimiento (preventivo)
    Mb("banco_trabajo", R(42.6, 28.6, 44.8, 29.35), "S"), Mb("agujereadora", R(45.0, 28.6, 45.8, 29.35), "S"),
    Mb("torno", R(46.6, 28.4, 48.9, 29.35), "S"),
    Mb("estanteria", R(48.6, 25.0, 49.15, 28.2), "O"), Mb("soldadora", R(41.3, 26.6, 42.3, 27.2), "E"),
    Mb("escritorio", R(46.6, 24.85, 48.4, 26.15), "N"), Mb("contenedor", R(45.0, 24.85, 46.4, 25.75), "N"),
    # ---- PÑL pañol de mantenimiento y de línea (pegado al taller, ventanilla a PO-1)
    Mb("estanteria", R(42.0, 32.65, 45.95, 33.15), "S"), Mb("estanteria", R(45.45, 30.6, 45.95, 32.4), "O"),
    Mb("estanteria", R(42.6, 29.65, 44.6, 30.15), "N"), Mb("ventanilla", R(41.25, 30.6, 41.65, 32.2), "E"),
    Mb("escritorio", R(42.6, 30.9, 43.9, 32.2), "E"),
    # ---- Q laboratorio de calidad (+ archivo de legajos)
    Mb("marmol", R(49.5, 27.9, 51.5, 28.9), "S"), Mb("mesa_lab", R(51.8, 28.65, 55.0, 29.35), "S"),
    Mb("camara", R(55.3, 28.3, 56.75, 29.35), "S"), Mb("camara", R(55.9, 26.6, 56.75, 27.6), "O"),
    Mb("balanza_lab", R(49.5, 25.0, 50.2, 25.6), "N"), Mb("escritorio", R(50.5, 24.85, 52.3, 26.15), "N"),
    Mb("archivo", R(53.7, 24.85, 54.8, 25.35), "N", 2), Mb("mesa_lab", R(54.9, 24.85, 56.75, 25.55), "N"),
    # ---- QR cuarentena de producto y muestras retenidas
    Mb("jaula", R(57.1, 24.9, 60.9, 29.3), "S"), Mb("pallets", R(57.3, 27.8, 59.9, 29.1), "S", 1),
    Mb("estanteria", R(60.35, 25.0, 60.85, 27.5), "O"), Mb("cilindros_piso", R(57.3, 25.9, 58.9, 27.4), "S", 0),
    # ---- SUP supervisor y PCP (separados, con ventana a la línea)
    Mb("escritorio", R(61.3, 28.0, 63.1, 29.35), "S"), Mb("archivo", R(63.55, 24.85, 64.15, 26.1), "O", 2),
    Mb("sillas", R(61.25, 26.3, 61.7, 27.6), "E", 2),
    Mb("escritorio", R(64.5, 28.0, 66.3, 29.35), "S"), Mb("escritorio", R(66.5, 28.0, 68.3, 29.35), "S"),
    Mb("pizarra", R(68.25, 25.2, 68.35, 27.4), "O"), Mb("archivo", R(64.5, 24.85, 65.8, 25.35), "N", 3),
    # ---- PV supermercado de carros vacíos (frente a la calle PO-2)
    Mb("carros_vacios", R(46.4, 29.7, 51.4, 31.3), "N", 6), Mb("carros_vacios", R(51.6, 29.7, 57.0, 31.3), "N", 7),
    Mb("carros_vacios", R(57.2, 29.7, 61.8, 31.3), "N", 5),
    # ---- SC compresores y colectores: tablero
    Mb("tablero_el", R(63.9, 42.95, 65.5, 43.55), "S", 2),
    # ---- ST-I tableros y compresor de la cabina
    Mb("tablero_el", R(70.3, 30.6, 74.3, 31.35), "S", 4), Mb("compresor", R(70.4, 27.0, 73.4, 28.4), "N"),
    # ---- almacén de MP: cuarentena y retenidos a piso
    Mb("pallets", R(6.7, 24.8, 8.95, 32.9), "O", 0), Mb("pallets", R(6.7, 34.8, 8.95, 36.95), "O", 0),
    Mb("inflamables", R(0.45, 21.8, 1.55, 22.9), "E"), Mb("estanteria", R(0.45, 21.15, 1.55, 21.6), "E"),
    # ---- procesado: cuerpos cortados en pallets a piso
    Mb("pallets", R(29.0, 29.9, 35.9, 33.3), "N", 0), Mb("pallets", R(29.0, 33.55, 35.9, 34.65), "N", 1),
    Mb("pallets", R(30.0, 36.7, 33.3, 39.1), "N", 0),
    # ---- tramos 1 kg junto al láser
    Mb("pallets", R(27.3, 29.9, 28.65, 34.8), "O", 1),
    # ---- embalaje: pila de pallets vacíos, stock de cajas y pallets en armado
    Mb("pallets", R(60.0, 7.2, 61.2, 8.2), "E", 0), Mb("pallets", R(61.9, 7.6, 63.1, 8.6), "E", 0),
    Mb("pallets", R(66.8, 5.0, 68.0, 6.0), "N", 0), Mb("pallets", R(70.8, 5.0, 72.0, 6.0), "N", 1),
    # ---- depósito de polvo: big bags a piso de la tanda
    Mb("bigbags", R(56.6, 5.6, 58.0, 7.0), "S", 1),
    # ---- expedición: rampa del muelle, recepción y combustible del autoelevador de PT
    Mb("rampa", R(49.3, 0.35, 52.3, 2.35), "S"), Mb("mesa_lab", R(47.0, 0.45, 49.0, 1.2), "N"),
    Mb("inflamables", R(52.5, 0.4, 53.5, 1.4), "N"),
    # ---- sanitarios de planta
    Mb("inodoro", R(64.1, 17.35, 66.4, 18.7), "S", 2), Mb("mingitorios", R(66.8, 18.3, 68.0, 18.7), "S", 2),
    Mb("lavabos", R(69.6, 16.4, 70.1, 17.6), "O", 2),
    Mb("inodoro", R(61.1, 17.35, 62.3, 18.7), "S", 1), Mb("lavabos", R(62.8, 18.2, 63.4, 18.7), "S", 1),
    # ---- DL ducha de emergencia y lavaojos
    Mb("ducha_emergencia", R(70.8, 17.4, 72.0, 18.6), "S"), Mb("lavaojos", R(71.7, 15.9, 72.3, 16.5), "O"),
    # ---- recargas
    Mb("estanteria", R(6.0, 2.3, 6.5, 3.4), "O"), Mb("jaula", R(4.4, 0.6, 5.8, 1.8), "N"),
    Mb("ventanilla", R(9.0, 4.55, 9.8, 4.72), "N"), Mb("ventanilla", R(10.4, 9.6, 10.7, 10.4), "E"),
    Mb("ventanilla", R(10.4, 12.4, 10.7, 13.2), "E"),
    Mb("mesa_lab", R(2.4, 14.7, 3.8, 15.4), "N"), Mb("heladera", R(0.55, 16.6, 1.25, 17.3), "N"),
    Mb("balanza_lab", R(2.4, 16.6, 3.0, 17.2), "S"),
    Mb("jaula", R(4.2, 14.7, 6.2, 16.2), "E"), Mb("tambores", R(4.2, 16.3, 4.9, 17.3), "N", 2),
    Mb("estanteria", R(9.3, 16.6, 9.7, 17.3), "O"),
    Mb("estanteria", R(12.5, 0.6, 15.0, 1.1), "N"),
    Mb("estanteria", R(16.9, 4.7, 17.7, 6.5), "O"), Mb("tambores", R(16.2, 6.8, 17.7, 8.1), "O", 2),
]

# puertas interiores de una hoja: (x, y, ancho, muro 'h'/'v', abre +1/-1)
PUERTAS_INT = [
    # bloque de servicios
    (-16.1, 22.9, 0.8, "h", -1), (-11.5, 22.9, 0.8, "h", -1), (-8.4, 22.9, 0.8, "h", -1), (-7.5, 19.9, 0.9, "v", 1),
    (-1.0, 22.9, 0.8, "h", -1), (-14.6, 24.6, 0.9, "h", 1), (-8.4, 24.6, 0.8, "h", 1), (-16.6, 28.3, 0.8, "h", 1),
    (-12.4, 28.3, 0.8, "h", 1), (-10.0, 27.7, 0.7, "h", 1), (-8.1, 27.7, 0.7, "h", 1), (-7.0, 33.4, 0.9, "v", 1),
    (-5.6, 25.3, 0.9, "v", 1),
    # sanitarios de planta (a la calle AT2)
    (66.6, 16.0, 0.9, "h", 1), (63.0, 16.0, 0.8, "h", 1),
    # recargas: cada local abre a un corredor o al local vecino de la zona general
    (6.6, 1.2, 0.9, "v", 1), (10.8, 1.2, 0.9, "v", 1), (12.4, 1.3, 0.9, "v", -1), (12.4, 5.9, 0.8, "v", -1),
    (12.4, 9.6, 0.9, "v", -1), (12.4, 13.6, 0.9, "v", -1), (12.4, 17.2, 0.9, "v", -1),
    (10.8, 15.4, 0.9, "v", 1), (9.6, 14.5, 0.9, "h", 1), (1.4, 17.5, 0.8, "h", 1), (5.2, 17.5, 0.8, "h", 1),
    (7.2, 17.5, 0.8, "h", 1),
]

# ============================================================ LOCALES CERRADOS DENTRO DE LA NAVE
# tabique en todo el perímetro (salvo donde coincide con el cerramiento de la nave) y sus aberturas:
# (lado, desde, hasta, tipo): puerta (hoja 0,90), porton (corredizo), cortina (lamas de PVC, pasa material),
# ventanilla (mostrador, no es paso), ventana (vidrio a la planta, no es paso)
CERRADOS = {
    "MT": [("S", 43.4, 45.4, "porton"), ("N", 41.5, 42.4, "puerta"), ("N", 46.0, 48.6, "ventana")],
    "PÑL": [("S", 41.5, 42.4, "puerta"), ("O", 30.6, 32.2, "ventanilla")],
    "Q": [("S", 52.6, 53.5, "puerta"), ("N", 50.0, 56.4, "ventana"), ("S", 50.0, 52.2, "ventana")],
    "QR": [("S", 58.5, 59.5, "puerta")],
    "SUP": [("S", 62.0, 62.9, "puerta"), ("N", 61.5, 63.9, "ventana"), ("S", 63.2, 64.0, "ventana")],
    "PCP": [("S", 66.2, 67.1, "puerta"), ("N", 64.8, 68.0, "ventana"), ("S", 64.6, 65.9, "ventana")],
    "ST-I": [("O", 25.2, 26.8, "porton")],
    "SC": [("S", 56.0, 56.9, "puerta"), ("S", 52.2, 54.0, "porton")],
    "DP": [("S", 56.4, 58.4, "porton"), ("N", 55.8, 57.4, "porton"), ("O", 5.0, 7.0, "porton")],
}

# ============================================================ PROTECCIÓN CONTRA INCENDIO Y SEÑALIZACIÓN
# bocas de incendio equipadas (manguera 25 m + chorro 5 m): cubren toda la nave desde las calles
BIE = [(8.0, 23.0), (30.0, 23.0), (52.0, 23.0), (73.0, 23.0), (30.0, 39.8), (55.0, 39.8), (80.0, 39.8),
       (24.0, 6.8), (54.3, 12.0), (80.0, 2.0), (11.6, 9.0)]
# pulsadores manuales de alarma junto a cada salida y sirena con luz estroboscópica
PULSADORES = [(4.2, 43.3), (47.0, 43.3), (66.5, 43.3), (80.5, 43.3), (87.3, 39.8), (87.3, 34.1), (86.5, 0.7),
              (71.1, 0.7), (11.6, 0.7), (2.2, 0.7), (0.7, 7.5), (0.7, 18.1), (0.7, 23.8), (50.8, 2.6)]


def _senales():
    """Señalética (IRAM 10005-1 colores y formas; Dec. 351/79): (tipo, código, x, y, texto).
    tipo: obl (azul, círculo), adv (amarilla, triángulo), pro (roja, círculo con barra), sal (verde, rectángulo),
    inc (roja, cuadrado)."""
    S = []
    for p in PUERTAS:
        if p.tipo in ("emergencia", "peatonal") or p.cod in ("P1", "P2", "P3"):
            m = (p.a + p.b) / 2
            xy = {"N": (m, NAVE_A - 0.9), "S": (m, 0.9), "O": (0.9, m), "E": (NAVE_L - 0.9, m)}[p.muro]
            S.append(("sal", "SALIDA", *xy, "Salida"))
    for x in range(6, 72, 12):
        S.append(("sal", "->", float(x), 21.1, "Recorrido de evacuación"))
    auditiva = ("M04", "M08", "B08", "M16", "C01", "C81", "B10")
    careta = ("B03", "A06", "B06", "M11", "C02s", "C04", "C05", "C06", "C08", "B10")
    respirador = ("P04", "T01", "BB1", "T02", "BB2", "B08", "R09a", "R02a")
    for e in EQUIPOS:
        x, y = e.rect.x1 + 0.35, e.rect.y1 + 0.35
        if e.cod in auditiva:
            S.append(("obl", "OÍDOS", x, y, "Protección auditiva"))
        if e.cod in careta:
            S.append(("obl", "CARETA", x, y - 0.75 if e.cod in auditiva else y, "Careta fotosensible y guantes"))
        if e.cod in respirador:
            S.append(("obl", "RESP", e.rect.x0 - 0.35, y, "Respirador P2"))
    S.append(("obl", "CALZADO", 1.2, 25.0, "Calzado de seguridad y ropa de trabajo (ingreso a planta)"))
    for x, y in ((4.0, 24.9), (13.1, 24.9), (22.1, 24.9), (40.0, 6.3), (34.0, 21.1), (60.0, 21.1), (19.6, 7.0)):
        S.append(("adv", "AUTOELEV", x, y, "Circulación de autoelevadores"))
    for x, y in ((70.4, 31.0), (39.0, 44.6), (36.3, 47.8)):
        S.append(("adv", "ELECT", x, y, "Riesgo eléctrico"))
    for x, y in ((83.0, 10.2), (86.0, 10.2), (83.4, 23.6)):
        S.append(("adv", "CALOR", x, y, "Superficie caliente (hornos)"))
    for x, y in ((50.6, 43.3), (59.6, 7.4), (15.0, 11.4), (15.0, 14.6)):
        S.append(("adv", "INFLAM", x, y, "Gases a presión"))
    for x, y in ((31.6, 40.9), (37.9, 18.6), (65.4, 37.2)):
        S.append(("adv", "ATRAP", x, y, "Riesgo de atrapamiento / cargas suspendidas"))
    for x, y in ((75.0, 23.0), (59.0, 8.0), (10.0, 6.0), (39.8, 13.0)):
        S.append(("pro", "FUMAR", x, y, "Prohibido fumar y llama abierta"))
    for x, y in ((4.0, 25.2), (13.1, 25.2), (22.1, 25.2), (45.2, 18.3), (50.75, 18.3)):
        S.append(("pro", "PEATON", x, y, "Prohibido el paso de peatones (calle de autoelevador)"))
    for x, y in ((-12.4, 22.4), (71.4, 15.9), (2.0, 15.0), (40.5, 31.5)):
        S.append(("sal", "+", x, y, "Primeros auxilios / lavaojos"))
    S.append(("sal", "REUNIÓN", 28.0, -30.0, "Punto de reunión"))
    S.append(("sal", "PLANO", 0.9, 24.0, "Plano de evacuación (ingreso PP-1)"))
    return S


SENALES = _senales()

# función de cada portón, rotulada en todos los planos (qué entra o sale, nunca un código suelto)
USO_CORTO = {
    "P1": "MP: chapa, fleje, caños y barras, casquetes, insumos de montaje y soldadura; sale scrap",
    "P2": "Recargas: utilitarios",
    "P3": "Muelle único: sale PT y carros; entran polvo, pintura, embalaje y revendidos",
    "PP-1": "Personal", "PG": "Jaula exterior de gases",
}

# fondos de calle admitidos: ninguno (versión 8: toda calle remata en otra calle o en una puerta)
FONDOS = {}

# ============================================================ ESPACIOS LIBRES (a debatir)
LIBRES = [
    ("LB-1", R(76.2, 24.8, 87.6, 33.4), "Libre 98 m² al norte de pintura: queda del almacén de pintura y del pulmón "
     "a pintura de la v7 (la pintura en polvo pasó al depósito de polvo, v5, y el detector cuelga en el riel)"),
    ("LB-2", R(65.8, 40.4, 87.6, 43.6), "Libre 70 m² sobre la calle norte: la granalla pasó al almacén de MP (v5)"),
]

# ============================================================ IMPLANTACIÓN
LM_Y = TERRENO[1]
RETIRO_FRENTE = 10.0

EXTERIOR = [
    ("PL-N", "Alero de descarga de MP (semi 18,6 m y chasis); franja de descarga de 15 × 5 m (W-CAR)",
     R(-1.0, 44.4, 31.0, 56.0), "playa"),
    ("VQ-N", "Volquete de scrap 6 m³ junto a P1", R(-0.8, 44.8, 1.8, 47.6), "volquete"),
    ("JG", "Jaula exterior de gases (15,75 m², v5): pack de 12 cilindros de Arcal 21 y pack de 12 de N₂ con manifold, "
     "y CO₂ de recargas; cañería a los puestos de soldadura y de presurización", R(48.0, 44.3, 53.25, 47.3), "gas"),
    ("PM", "Playa de maniobra del muelle P3 (semi 18,6 m)", R(40.0, -26.0, 62.0, 0.0), "playa"),
    ("PU", "Playa cubierta de utilitarios frente a P2: preparación de las rutas de reparto (80 m², X-DT Almacén PT)",
     R(-1.0, -10.0, 9.0, 0.0), "playa"),
    ("ERM", "Estación de regulación y medición de gas natural (hornos y secadoras)", R(88.6, 4.0, 91.6, 7.0),
     "gas"),
    ("RI", "Reserva de agua contra incendio y bombas", R(100.0, 34.0, 110.0, 44.0), "incendio"),
    ("AMP", "Reserva de ampliación (nave hacia el este)", R(92.0, -8.0, 114.0, 21.0), "reserva"),
    ("PTE", "Tratamiento de efluentes líquidos", R(64.0, -27.0, 76.0, -19.0), "efluentes"),
    ("EST", "Estacionamiento de personal (38 + 2 accesibles)", R(-12.0, -50.0, 30.0, -28.0), "estac"),
    ("EU", "Utilitarios de reparto y recargas (8)", R(-15.0, -20.0, -1.0, -10.0), "estac"),
    ("GAR", "Garita: control de camiones (G1), autos (G2) y peatones (G4); CCTV", R(-28.5, -61.5, -23.5, -57.0),
     "garita"),
    ("BAL", "Báscula de camiones de 18 m (entrada)", R(-35.5, -50.0, -29.5, -32.0), "balanza"),
    ("PR", "Punto de reunión (evacuación)", R(-27.5, -30.0, -21.5, -24.0), "reunion"),
    ("MT", "Celda de medición de media tensión", R(-39.6, -30.0, -36.4, -24.0), "elec"),
    ("ERP", "Estación reductora de gas", R(126.5, -60.0, 129.5, -56.0), "gas"),
]
# jaula exterior de gases (W-MAN): pack de 12 cilindros en uso y otro de reserva por gas, con manifold de conmutación
JAULA_GASES = [("Arcal 21: pack en uso y de reserva", R(48.3, 46.0, 50.5, 46.9)),
               ("N₂: pack en uso y de reserva", R(50.8, 46.0, 53.0, 46.9)),
               ("CO₂ de recargas: cilindros llenos", R(51.0, 44.5, 53.0, 45.3))]
MANIFOLD_GASES = [(48.3, 45.6), (53.0, 45.6)]
CALLES = [R(-36.0, -62.0, -29.0, 63.0), R(-36.0, 56.5, 126.0, 63.0), R(119.0, -62.0, 126.0, 63.0),
          R(30.0, -16.0, 119.0, -9.0)]
PORTONES_TERRENO = [
    ("G1", -36.0, -29.0, "Camiones: entran (báscula y garita)"),
    ("G4", -21.0, -18.0, "Peatones"),
    ("G2", -12.0, -6.0, "Autos del personal y utilitarios de recargas"),
    ("G3", 119.0, 126.0, "Camiones: salen"),
]
CAMINO_PEATONAL = [(-19.5, -62.0), (-19.5, 16.5), (-9.0, 16.5), (-9.0, 19.0)]

# ============================================================ EFLUENTES
EFLUENTES = [
    Flujo("EFL-L", [(48.7, 35.6), (48.7, 34.9), (47.0, 34.9), (47.0, 37.6), (47.6, 37.6)],
          "Agua de PH a la cámara de decantación"),
    Flujo("EFL-L", [(66.4, 11.6), (66.4, 12.9), (73.6, 12.9), (73.6, 34.9), (50.2, 34.9), (50.2, 37.6)],
          "Ensayo de pérdidas a la misma cámara (cañería enterrada)"),
    Flujo("EFL-L", [(50.2, 38.8), (50.2, 39.0), (52.8, 39.0), (52.8, 34.8), (61.0, 34.8), (61.0, 0.6),
                    (70.0, -19.0)], "Cámara de decantación a la planta de efluentes"),
    Flujo("EFL-L", [(30.9, 1.3), (30.9, 0.6), (40.0, 0.6), (40.0, -19.0), (64.0, -19.0)],
          "Purga del tanque de la PH de carros"),
    Flujo("EFL-L", [(14.0, 4.6), (14.0, 0.6), (18.2, 0.6)], "Agua usada de líquidos y PH de recargas"),
    Flujo("EFL-L", [(70.0, -27.0), (70.0, -62.0)], "Vuelco a colectora (previa autorización)"),
]
RC_FLUJO = [(2.2, -6.0), (2.2, 0.0), (2.2, 2.4), (7.8, 2.4), (9.4, 4.0), (9.4, 6.2), (5.8, 6.9), (2.6, 7.9),
            (4.6, 9.6), (2.6, 12.6), (6.9, 12.6), (9.8, 12.8), (10.6, 9.8), (11.6, 9.8), (11.6, 2.8), (12.4, 2.8),
            (17.2, 2.8), (17.2, 2.0), (11.6, 2.0), (11.6, 1.2), (6.6, 1.6), (2.2, 1.6), (2.2, 0.0), (2.2, -6.0)]

EMISIONES = [
    (43.6, 41.9, "Humos de soldadura de cuellos"), (23.5, 17.9, "Humos de soldadura de carros"),
    (28.4, 11.4, "Humos de soldadura de carros"), (37.7, 31.5, "Humos de soldadura longitudinal"),
    (41.4, 36.3, "Humos de soldadura circunferencial"), (43.8, 36.3, "Humos de soldadura circunferencial"),
    (67.1, 38.1, "Colector de la granalladora"), (84.0, 6.8, "Chimenea horno de curado"),
    (83.4, 22.1, "Chimenea horno de precalentamiento"), (77.4, 19.7, "Ciclones de la cabina"),
    (56.3, 11.1, "Extracción de la carga de polvo"), (39.9, 12.1, "Extracción de la carga de carros"),
    (25.75, 31.0, "Humos de corte láser"), (8.6, 10.9, "Extracción del recinto de polvo de recargas"),
    (57.0, 36.1, "Chimenea secadoras"), (76.7, 38.1, "Humos de corrección"),
]


# ============================================================ sendas (cruces hilo-flujo señalizados)
def _sendas():
    from shapely.geometry import LineString
    fl = [LineString(f.pts) for f in FLUJOS if f.cat in ("MP", "SE", "PT")]
    pts = []
    for nom, main, br in HILOS:
        tramos = [LineString(main)] + [LineString([(a, b), (c, d)]) for a, b, c, d in br]
        for t in tramos:
            for f in fl:
                if t.intersects(f):
                    g = t.intersection(f)
                    for q in ([g] if g.geom_type == "Point" else list(getattr(g, "geoms", [g]))):
                        if q.geom_type == "Point":
                            pts.append((round(q.x, 2), round(q.y, 2)))
    grupos = []
    for p in sorted(set(pts)):
        for g in grupos:
            if any(abs(p[0] - q[0]) < 1.6 and abs(p[1] - q[1]) < 1.6 for q in g):
                g.append(p)
                break
        else:
            grupos.append([p])
    S = []
    for i, g in enumerate(grupos, 1):
        xs, ys = [p[0] for p in g], [p[1] for p in g]
        S.append((f"X{i}", R(min(xs) - 0.6, min(ys) - 0.6, max(xs) + 0.6, max(ys) + 0.6),
                  "Senda peatonal señalizada (cebra amarilla, IRAM 10005) en el cruce del personal con un flujo"))
    return S


HILOS = _hilos()
SENDAS = _sendas()

# ============================================================ DEFENSA ENTRE CARRILES DEL PASILLO CENTRAL
# baranda de 0,20 m entre el carril de autoelevador y la senda peatonal; aberturas donde se cruza
Y_DEF = 23.1
ABERTURAS = [
    (1.6, 6.6, "autoelevador de MP: calle de recepción A1"),
    (10.6, 15.6, "autoelevador de MP: calle de chapa A2"),
    (19.6, 24.6, "autoelevador de MP: calle de carga A3 (barras y casquetes a carros)"),
    (29.9, 31.4, "autoelevador retira el contenedor de la guillotina"),
    (34.2, 35.4, "EFE 600 y mesa móvil: cuerpos de carros al cilindrado"),
    (40.0, 41.0, "personal a la línea principal (PO-1)"),
    (11.0, 12.2, "personal a recargas (RC-N)"),
    (18.0, 19.2, "personal a carros (PO-CW)"),
    (53.6, 55.0, "personal a terminación y PT (AC)"),
    (68.6, 70.0, "personal a la línea este (PO-5)"),
    (74.6, 76.0, "personal a pintura (PO-PI)"),
]


def _defensas():
    tramos, x = [], 0.3
    for a, b, _ in sorted(ABERTURAS):
        if a > x:
            tramos.append((x, a))
        x = max(x, b)
    if x < 74.6:
        tramos.append((x, 74.6))
    return tramos


DEFENSAS = _defensas()
for _a, _b, _t in ABERTURAS:
    if _t.startswith("personal"):
        SENDAS.append((f"X{len(SENDAS) + 1}", R(_a, 19.2, _b, 23.0), "Senda peatonal: " + _t +
                       " (cruza el carril de autoelevador)"))
