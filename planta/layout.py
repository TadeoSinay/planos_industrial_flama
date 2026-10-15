"""Modelo del layout de la planta FLAMA S.A. al año 10 (2035) - versión 9: sin recargas y con los puestos 1 a 17 de carros.

Medidas en METROS, origen en el eje A-1 (esquina SO, cara interior de columnas), X al este, Y al norte.
Calle al sur. Fuente única de los planos (DIR, operaciones, materiales, formal) y de la memoria de cálculo.

Fuentes de la versión 9 (todas en referencias/ o entregadas por el grupo)
------------------------------------------------------------------------
* W-MAN  PROCESO_DE_MANUALES_EXPLICATIVO (orden, disposición, carros y transportadores de cada puesto).
* W-CAR  PROCESO_CARRO_EN_LIMPIO, versión de 17 puestos (tablas de espacios en m de cada puesto).
* X-MAN  Dimensionamiento_Manuales.xlsx, hoja Resumen Capacidad 2035 (34 puestos, 2 turnos).
* X-CAR  Dimensionamiento_Carros.xlsx, hoja Resumen Capacidad 2035 (18 puestos, 1 de cada uno, 1 turno).
* X-DT   Dimensionamiento_TecnicoV2.xlsx (Almacén PT 2035: 128 pallets).
* X-ALM  Dimensionamiento_Almacenes_MP_v5.xlsx (secciones del almacén de MP, posiciones, m² netos y brutos).

Concepto (correcciones de la versión 9)
---------------------------------------
* Recargas sale de la planta (va por afuera). En su lugar, ángulo SO, quedan las oficinas que estaban en la franja
  central (mantenimiento y pañol, calidad, cuarentena de producto, supervisor y planificación), con entrada propia por
  el oeste, y los ensayos de lote de carros (puestos 14 y 17) contra el muro sur, con el patio de ensayos afuera.
* Administración (compras, ventas y RRHH) pasa al lado este, en el ex espacio libre LB-1, con entrada de visitas por la
  fachada este: queda en la otra punta de la nave respecto de P1.
* Portón de MP P1 de 7,0 m: el atado de caños de 6 m entra atravesado, recorre la calle de recepción A1 (7,5 m) y se
  apoya derecho en el cantiléver del fondo, sin girar. Toda la MP entra por P1 y pasa por la única cuarentena (W-MAN).
* Carros: puestos 3 a 11 en dos filas en la franja central (al lado de la guillotina compartida, el cuerpo ya no
  cruza el pasillo central); puestos 12 a 17 y el depósito de PT de carros en la banda sur, junto al muelle P3.
* Un solo autoelevador (Heli CPCD50, W-MAN y W-CAR): el PT de manuales pasa a racks con una calle de 5 m.
* Horno único (X-MAN: 1 equipo «pintura en polvo + horno»): el riel pasa dos veces por el mismo cuerpo, primero para el
  precalentamiento y después, a la vuelta de la cabina, para el curado.
* Pulmones y almacenes intermedios: sólo los que nombran W-MAN y W-CAR (se sacan el procesado del Excel de almacenes y
  el supermercado de carros vacíos).
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
    cat: str                 # MP, PROD, PINT, TERM, PT, CAL, SERV, AUX, CIRC, EXT
    seccion: str = ""        # S1 1 kg, S2 manuales, S3 rodantes, S4 tercerizados, común
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
            "Pasillo central: el único autoelevador lleva la MP de P1 a la banda sur (polvo y pintura al depósito, "
            "embalaje, revendidos) por la calle del muelle T, y el big bag de ABC 90 a la carga de carros"),
    Pasillo("PP", R(0.3, 23.2, 74.6, 24.4), "PP", 1.2,
            "Senda peatonal separada del carril de autoelevador por una defensa con aberturas en los cruces; los "
            "puestos 8 a 11 de carros se atienden desde acá"),
    # ---- almacén de MP: recepción de 7,5 m frente a P1 y dos calles de 5 m unidas por la cabecera AN
    Pasillo("A1", R(1.6, 26.2, 9.1, 43.6), "PM", 7.5,
            "Calle de recepción de 7,5 m frente a P1 (7,0 m): el atado de caños de 6 m entra atravesado y llega derecho "
            "al cantiléver del fondo; cuarentena y retenidos al este, insumos de montaje al oeste"),
    Pasillo("A2", R(13.1, 19.2, 18.1, 37.2), "PM", 5.0,
            "Calle de chapa: paquetes de hojas de manuales (oeste) y chapa LAC de carros (este). " + _AE),
    Pasillo("A3", R(19.6, 19.2, 24.6, 37.2), "PM", 5.0,
            "Calle de carga a máquina: mesa elevadora de la guillotina, contenedor y cajón del láser (este). " + _AE),
    Pasillo("AN", R(9.1, 37.2, 24.6, 42.2), "PM", 5.0,
            "Cabecera del almacén: une A1, A2 y A3; porta-flejes y racks de soldadura y de casquetes al norte; el rollo "
            "va con el espolón al desbobinador del embutido (extremo este)"),
    # ---- banda norte: calles de operarios y carros a mano
    Pasillo("PO-1", R(36.8, 24.4, 38.2, 34.6), "PO", 1.4,
            "Calle de operarios de la senda a la línea principal; por acá entran los cuerpos de carros grabados (EFE 600 "
            "y mesa móvil) del marcado al cilindrado (3)"),
    Pasillo("PO-2", R(28.9, 33.6, 87.6, 34.6), "PO", 1.0,
            "Calle sur de la línea principal y norte de la fila de carros 3 a 7: carros FCHP20505 entre puestos; "
            "termina en la salida SE-6"),
    Pasillo("PO-3", R(24.6, 39.3, 87.6, 40.3), "PO", 1.0,
            "Calle norte: celda de cuello, embutido, compresores y corrección; termina en la salida SE-5"),
    Pasillo("PO-6", R(74.6, 24.4, 76.0, 33.6), "PO", 1.4,
            "Continuación de PO-PI hasta la línea principal (operarios de pintura, granallado y detección); puerta de "
            "personal de administración; el retorno del riel pasa por arriba"),
    Pasillo("PO-7", R(61.1, 34.6, 62.1, 39.3), "PO", 1.0, "Paso de operarios entre secado y granallado (PO-2 <-> PO-3)"),
    Pasillo("PO-8", R(28.9, 34.6, 33.6, 35.8), "PO", 1.2, "Calle de los carros de tramos (láser -> encastre)"),
    # ---- pintura
    Pasillo("PO-PI", R(74.6, 0.6, 76.0, 24.4), "PO", 1.4,
            "Calle de operarios de pintura: remate este del pasillo central; los vacíos la cruzan al embalaje y los "
            "terminados suben por ella a la calle AT2"),
    Pasillo("PO-PS", R(74.6, 0.6, 87.1, 2.2), "PO", 1.6, "Paso al sur de la descarga de pintura hasta la salida SE-7"),
    # ---- banda sur: muelle, PT y carros
    Pasillo("T", R(50.0, 0.3, 53.6, 19.2), "PM", 3.6,
            "Calle del muelle P3: une el pasillo central con el muelle; autoelevador (pallets de PT, MP de P1 al "
            "depósito de polvo y big bag de carros) y carros a mano (despacho y vuelta de pintura)"),
    Pasillo("T-PT", R(30.6, 1.5, 50.0, 6.5), "PM", 5.0,
            "Calle del almacén de PT: racks a los dos lados; remata en el bastidor del big bag de la carga de carros "
            "(13). " + _AE),
    Pasillo("PO-K", R(12.8, 17.5, 50.0, 18.7), "PO", 1.2,
            "Calle de carros y personal de la banda sur: une la oficina, el depósito de retenidos, el pulmón de "
            "pintados, los liberados y la calle del muelle"),
    Pasillo("PO-OF", R(12.8, 5.0, 14.0, 17.5), "PO", 1.2,
            "Paso de la oficina a la banda sur: técnico de calidad a los ensayos (17), a la sala de pérdidas (14) y al "
            "depósito (16)"),
    Pasillo("PO-K2", R(30.6, 7.9, 42.2, 10.4), "PO", 2.5,
            "Calle de los carros pintados: del cambio de juego al pulmón de pintados y de ahí a la carga (13)"),
    Pasillo("PO-K3", R(34.6, 10.4, 35.8, 17.5), "PO", 1.2, "Une PO-K con PO-K2 (personal y carros)"),
    # ---- terminación y embalaje de manuales
    Pasillo("AT", R(53.6, 1.8, 74.6, 4.4), "PM", 2.6,
            "Calle de embalaje: pallets de la envolvedora al PT; MP de P1 al depósito de polvo; rack de embalaje"),
    Pasillo("AC", R(53.6, 4.4, 55.0, 19.2), "PO", 1.4,
            "Calle oeste de terminación: pasillo central <-> AT; pintura en polvo del depósito a la cabina"),
    Pasillo("AT2", R(55.0, 13.0, 74.6, 15.6), "PO", 2.6,
            "Calle de terminación: terminados pintados de la descarga a la carga; sanitarios y ducha de emergencia"),
]

# sendas peatonales: se calculan al final del módulo en cada cruce de un hilo con un flujo
SENDAS = []

# zona sin autoelevador (banda norte al este del almacén de MP): sólo carros a mano y transpaleta
ZONA_SIN_AE = R(24.7, 24.5, 87.7, 43.7)

# ============================================================ SECTORES
_V5 = "Dimensionamiento_Almacenes_MP_v5"
SECTORES = [
    # ---------------- almacén de MP (una sola recepción y una sola cuarentena para manuales y carros, W-MAN y W-CAR)
    Sector("AL-CA", "Carros de abastecimiento", R(0.3, 19.3, 1.6, 23.0), "MP", "común",
           "W-CAR tabla 5: 3 × 1 m para los 2 carros de abastecimiento; salen directo a la senda PP"),
    Sector("AL-1N", "Gasoil del autoelevador", R(0.3, 24.6, 1.6, 26.2), "AUX", "común",
           "Armario de inflamables; el Heli CPCD50 diésel (W-MAN) se estaciona al final del pasillo central"),
    Sector("AL-MM", "Insumos de montaje (manuales)", R(0.3, 26.4, 1.6, 37.2), "MP", "S1 / S2",
           f"{_V5}: 31 posiciones, 13,8 m² netos (20,7 brutos); rack de 4 módulos × 2 × 4 niveles = 32: válvulas, "
           "manómetros, toberas, mangueras y soportes; salen una vez por turno en el carro de abastecimiento", 13.8),
    Sector("AL-ID", "Identificación (etiquetas, obleas, sellos)", R(0.3, 37.4, 1.6, 38.9), "MP", "común",
           f"{_V5}: 9 lugares, 3,0 m² netos; estantería de 5 niveles; sellos y obleas numerados bajo llave", 3.0),
    Sector("AL-MC", "Insumos de montaje (carros)", R(0.3, 39.1, 1.6, 42.0), "MP", "S3",
           f"{_V5}: 7 posiciones, 4,8 m² netos; rack de 1 módulo × 2 × 4 niveles: ruedas, válvulas de carro, "
           "manómetros, mangas y precintos (W-CAR 13)", 2.9),
    Sector("AL-CT", "Cantiléver de caños y barras (frente a P1)", R(1.6, 24.6, 9.0, 26.2), "MP", "común",
           f"{_V5}: 11 posiciones a 3 niveles; el atado de 16 caños de 6 m (W-MAN) entra atravesado por P1 y se apoya "
           "sin girar; de acá la pluma lo lleva al cajón del láser y las barras de carros salen de a una, a mano, al "
           "rack del puesto 8.1 (W-CAR)", 11.0),
    Sector("AL-CU", "Cuarentena de MP (compartida manuales y carros)", R(9.1, 24.6, 11.6, 34.6), "CAL", "común",
           "W-MAN y W-CAR tabla 5: 10 × 2,5 m, demarcada en amarillo: pallets, mesa de inspección de 1,2 × 0,6 y "
           "balanza de plataforma de 1,2 × 1,2 m (W-MAN: la misma de carros). X-MAN 2035: 3 operarios de recepción",
           25.0),
    Sector("AL-RE", "Retenidos de MP (no conforme)", R(9.1, 34.8, 11.6, 37.2), "CAL", "común",
           "W-CAR tabla 5: 4 × 1,5 m demarcados en rojo, 3 pallets; se reclama al proveedor", 6.0),
    Sector("AL-CH", "Chapa LAF de manuales (3 formatos)", R(11.6, 24.6, 13.1, 36.8), "MP", "S2",
           f"{_V5} 'Chapa y fleje': hojas 1220 × 2440, 1000 × 2000 y 1500 × 3000 en paquetes de 2 alturas "
           "(7 lugares); el autoelevador los toma de costado desde A2 (W-MAN)"),
    Sector("AL-CC", "Chapa LAC de carros", R(18.1, 24.6, 19.6, 34.6), "MP", "S3",
           "W-CAR tabla 5 y v5: 3 posiciones de 3,0 × 1,5 m, 2 paquetes por posición; van a la misma guillotina"),
    Sector("AL-FL", "Flejes LAF de manuales", R(9.1, 42.2, 15.2, 43.6), "MP", "S1 / S2",
           f"{_V5}: 21 rollos parados en cunas; porta-flejes de 3 niveles × 7 cunas (MP Opción D)"),
    Sector("AL-SS", "Insumos de soldadura y superficie", R(15.3, 42.2, 19.1, 43.6), "MP", "común",
           f"{_V5}: 12 posiciones, 4,8 m² netos; rack de 1 módulo de 3 pallets × 4 niveles: alambre MAG Ø0,9, "
           "granalla, discos y sprays", 4.8),
    Sector("AL-CQ", "Casquetes y cuplas de carros", R(19.15, 42.2, 24.6, 43.6), "MP", "S3",
           f"{_V5}: 11 posiciones (4 niveles), 6,0 m² netos; rack de 2 módulos frente a AN; carros 1 y 2 a los "
           "puestos 6 y 7 (W-CAR)", 6.0),
    # ---------------- banda norte: corte, tubo, cuerpo de manuales, embutido y celda de cuello
    Sector("N1", "Corte de chapa (compartido) y marcado de carros", R(24.7, 24.6, 36.0, 29.6), "PROD", "S2 / S3",
           "W-CAR: guillotina CENA 8 × 3200 (≈ 3,9 × 2,1), mesa elevadora 2,6 × 1,8 con 1 m de paso, zona trasera "
           "3,9 × 2,5 (rampa, contenedor y carros) = 44 m²; marcado de carros 3,5 × 2,5 pegado a la rampa = 9 m²",
           53.0),
    Sector("N2", "Corte de tubo 1 kg", R(24.7, 29.8, 28.8, 37.1), "PROD", "S1",
           "W-MAN: 1 láser (X-MAN); cajón de alimentación de 6,5 m al lado de la máquina, dos posiciones de carro "
           "«en llenado» y «vacío» de 1,2 × 0,8 m y contenedor de 1.000 L junto a la máquina"),
    Sector("N6", "Cilindrado y soldadura longitudinal 2,5-10 kg", R(28.9, 29.8, 36.6, 33.6), "PROD", "S2",
           "W-MAN: carro de desarrollos frenado al lado de la roladora, roladora Firesafer FS-RM01 y soldadora "
           "longitudinal con el carro FCHP20505 entre las dos (un lado largo hacia cada máquina); pegado a la "
           "guillotina (ocupa el ex procesado, que no figura en el Word)"),
    Sector("N3", "Corte de disco y embutido", R(24.7, 40.4, 34.4, 43.6), "PROD", "S1 / S2",
           "W-MAN: desbobinador, enderezador y alimentador Cena PRE-1, prensa Sangiacomo; estantería de matrices y "
           "carro porta-matrices al lado de la prensa; contenedor de 1.000 L del esqueleto"),
    Sector("N7", "Celda de cuello: numerado, muesca y soldadura", R(34.5, 40.4, 46.2, 43.6), "PROD", "S1 / S2",
           "W-MAN: las prensas de muesca van pegadas a la de numerado y a la soldadora de cuello, sin transporte "
           "entre las tres; zona de cúpulas al lado"),
    Sector("N4", "Encastre, bordoneado, soldadura circ., espesor y PH", R(33.6, 34.7, 54.6, 39.2), "PROD",
           "S1 / S2", "W-MAN y X-MAN: encastre 1, bordoneado 1, soldadura circ. 2, control de espesor 1, PH 2; "
           "un FCHP20505 entre cada par de puestos"),
    Sector("N5", "Secado, granallado y detección", R(54.7, 34.7, 75.4, 39.2), "PROD", "S1 / S2",
           "W-MAN y X-MAN: secado 4, granallado 1 (de rodillos), detección 1; tres jaulas al lado del puesto; el "
           "detector cuelga el cilindro en el riel de pintura"),
    Sector("N8", "Corrección de defectos", R(71.6, 40.4, 79.0, 43.6), "PROD", "S1 / S2",
           "W-MAN: los corregibles llegan en un carro desde la jaula «a corregir» y vuelven a los rodillos de "
           "entrada de la granalladora; X-MAN: 1 puesto"),
    # ---------------- franja norte: servicios de la línea
    Sector("SC", "Compresores y colector de humos", R(48.0, 40.4, 71.4, 43.6), "AUX", "común",
           "Reguladores de Arcal 21 y N₂ que vienen de la jaula exterior (puerta PG), colector de humos, 2 compresores "
           "de tornillo, secador y pulmón, con 1 m libre alrededor de cada equipo para mantenimiento"),
    Sector("ST-I", "Tableros de la línea este y compresor de la cabina", R(79.2, 40.4, 87.6, 43.6), "AUX", "común",
           "Tablero de N5 y de pintura y compresor sin aceite dedicado a la cabina (pasa del ex LB-2)"),
    # ---------------- franja central: carros, puestos 3 a 11 (W-CAR), en dos filas
    Sector("C-3", "Cilindrado de carros (3)", R(38.4, 29.4, 47.4, 33.6), "PROD", "S3",
           "W-CAR ≈ 7,0 × 5,0 = 35 m²: roladora W12 8 × 1500, zona de carga, EFE 600 y mesa móvil, salida axial "
           "y pulmón de cuerpos rolados de 1,8 × 1,2; recibe los cuerpos grabados del marcado por PO-1", 35.0),
    Sector("C-4", "Punteo del cuerpo (4)", R(47.6, 29.4, 55.0, 33.6), "PROD", "S3",
           "W-CAR ≈ 6,0 × 4,5 = 27 m²; X-CAR 2035: 1 virador (el segundo de la v8 se saca)", 27.0),
    Sector("C-5", "Soldadura longitudinal de carros (5)", R(55.2, 29.4, 61.4, 33.6), "PROD", "S3",
           "W-CAR ≈ 5,5 × 4,0 = 22 m²; zona de carga axial y no conforme en rojo", 22.0),
    Sector("C-6", "Soldadura de cupla en la cúpula (6)", R(61.6, 29.4, 66.0, 33.6), "PROD", "S3",
           "W-CAR ≈ 4,5 × 3,5 = 16 m²; pegado al armado (7); lo hace el operario de punteo", 16.0),
    Sector("C-7", "Armado y soldadura circunferencial (7)", R(66.2, 29.4, 74.4, 33.6), "PROD", "S3",
           "W-CAR ≈ 6,0 × 4,5 = 27 m²: virador, carro canasto de cúpulas, carro 2 de fondos, pulmón de cilindros "
           "cerrados y no conforme", 27.0),
    Sector("C-8", "Soldadura de accesorios (8)", R(67.6, 24.6, 74.4, 29.2), "PROD", "S3",
           "W-CAR ≈ 6,5 × 4,5 = 29 m²: virador, carro de kits del lado del 8.1, cuna del lado del 7 (arriba), "
           "juegos provisorios contra el fondo y salida al norte; la inspección de costuras la hace el mismo soldador "
           "(X-CAR no tiene mesa aparte)", 29.0),
    Sector("C-81", "Fabricación de accesorios (8.1)", R(60.4, 24.6, 67.4, 29.2), "PROD", "S3",
           "W-CAR ≈ 8,0 × 4,0 = 32 m²: rack de barras de 6,5 m sobre la senda PP (las barras de 6 m llegan a mano por "
           "la senda y entran al rack sin girarlas), banco con sensitiva, dobladora, taladro y prensa de 20 t; por el "
           "fondo pasan los carros del 8 a la PH", 32.0),
    Sector("C-9", "Prueba hidráulica de carros (9)", R(55.2, 24.6, 60.2, 29.2), "PROD", "S3",
           "W-CAR ≈ 5,5 × 4,0 = 22 m²: 2 bandejas con rampa, pantalla, Yukon M-000200, tanque de 1.000 L en "
           "circuito cerrado en el rincón del fondo", 22.0),
    Sector("C-10", "Secado de carros (10)", R(52.4, 24.6, 55.0, 29.2), "PROD", "S3",
           "W-CAR ≈ 3,0 × 2,5 = 7,5 m²: secadora eléctrica Melisam MR011, lugar del carro y espera de 2 carros "
           "mojados; lo atiende el operario de prueba hidráulica", 7.5),
    Sector("C-11", "Pulmón de despacho a pintura (11)", R(38.4, 24.6, 52.2, 29.2), "PT", "S3",
           "W-CAR ≈ 10 × 7 = 70 m²: 120 carros secos en filas por modelo y semana (0,5 m² por carro con el paso); "
           "salen por el muelle P3 cuando el lote está aprobado en la prueba hidráulica", 60.0),
    # ---------------- columna este: pintura en polvo (riel aéreo, W-MAN) y administración
    Sector("S-P", "Pintura en polvo (riel aéreo, horno único)", R(74.6, 2.3, 87.6, 24.3), "PINT", "S1 / S2",
           "W-MAN: riel transportador aéreo -> horno (precalentamiento) -> cabina con recuperación -> horno (curado "
           "180-220 °C) -> enfriamiento y descarga; X-MAN: un solo equipo de horno; esquema de 22 × 13 m"),
    # ---------------- banda sur: oficinas que estaban en la franja central (ex recargas, ángulo SO)
    Sector("MT", "Taller de mantenimiento", R(0.3, 12.9, 6.6, 18.8), "AUX", "común",
           "Mantenimiento preventivo: bancos, torno, agujereadora, soldadora móvil; entra la transpaleta por el "
           "portón del pasillo central; puerta directa al pañol", 30.0),
    Sector("PÑL", "Pañol de mantenimiento y de línea", R(6.8, 12.9, 9.8, 18.8), "AUX", "común",
           "Pegado al taller: repuestos críticos, herramental del preventivo, consumibles de soldadura (toberas, "
           "puntas, discos) contra vale por la ventanilla al pasillo de oficinas"),
    Sector("QR", "Cuarentena de producto y muestras retenidas", R(10.0, 12.9, 12.6, 18.8), "CAL", "común",
           "Jaula con llave: lotes rechazados y un cilindro testigo por lote (IRAM 3517 / 3523)", 15.0),
    Sector("OF-C", "Pasillo de oficinas", R(0.3, 11.6, 12.6, 12.8), "CIRC", "común",
           "Entrada de las oficinas desde el exterior (OF-1, camino peatonal desde SV-1) y paso a la banda sur"),
    Sector("Q", "Laboratorio de calidad", R(0.3, 5.0, 5.6, 11.4), "CAL", "común",
           "Metrología, ensayo de rotura (1 cilindro por lote, W-MAN), adherencia y espesor de pintura, humedad del "
           "polvo, probetas de soldadura de carros; legajos", 31.0),
    Sector("PCP", "Planificación y control de la producción", R(5.8, 5.0, 8.6, 11.4), "AUX", "común",
           "2 puestos y tablero de programación"),
    Sector("SUP", "Supervisor de planta", R(8.8, 5.0, 12.6, 11.4), "AUX", "común",
           "Oficina propia del encargado de turno, con ventana a la banda de carros"),
    # ---------------- banda sur: ensayos de lote y terminación de carros (W-CAR 12 a 17)
    Sector("C-17", "Ensayos de lote de carros (17)", R(0.3, 0.3, 15.8, 4.8), "CAL", "S3",
           "W-CAR ≈ 15,5 × 4,5 = 70 m²: recinto de descarga de 12 × 3 m (alto 3 m) con colector de mangas en el "
           "fondo, balanza de plataforma al lado de la puerta del recinto, mesa de medición y perchero de mangas; "
           "la rodadura sale al patio por PE-1", 70.0),
    Sector("C-14", "Sala del ensayo de pérdidas (14)", R(16.0, 0.3, 21.0, 5.3), "CAL", "S3",
           "W-CAR 5 × 5 m de paneles aislantes con puerta, 21 °C (split BGH 3000F y registrador): 30 lugares "
           "numerados; al lado de la carga (13) y del recinto de descarga (17)", 25.0),
    Sector("C-15", "Etiquetado e inspección final (15)", R(21.2, 0.3, 24.4, 3.5), "TERM", "S3",
           "W-CAR ≈ 3,5 × 2,5 = 9 m²: 2 lugares de carro, mesa de calcomanías y no conforme; a la salida del 13",
           9.0),
    Sector("C-13", "Carga, armado y presurización de carros (13)", R(24.6, 0.3, 30.4, 10.3), "TERM", "S3",
           "W-CAR ≈ 10 × 6 = 60 m²: estación A (cinta e interior), B (balanza con rampa y Yukon M-000121) con el "
           "bastidor del big bag detrás (el autoelevador llega por la calle del PT), batería de N₂ en jaula contra "
           "la pared, estación C (manga, traba y precinto) y estanterías", 58.0),
    Sector("C-12", "Pulmón de pintados (12)", R(24.6, 10.5, 34.6, 17.4), "TERM", "S3",
           "W-CAR ≈ 10 × 7 = 70 m²: 120 carros pintados sobre sus ruedas nuevas, al lado de la estación A del 13",
           70.0),
    Sector("C-12C", "Recepción de pintados: cambio de juego y rechazados (12)", R(42.4, 7.9, 49.9, 11.0), "TERM",
           "S3", "W-CAR: 2 lugares de cambio de juego de 2,0 × 1,5 m (crique, zorra de retorno y cajones de ejes y "
           "ruedas) y rechazados del pintor 2 × 1,5 m en rojo, al lado de la puerta, entre el camión y el pulmón", 9.0),
    Sector("C-16R", "Depósito de carros: retenidos y rechazados (16)", R(14.2, 5.5, 24.4, 17.4), "PT", "S3",
           "W-CAR: retenidos 180 carros ≈ 9 × 10 (amarillo) a la salida del etiquetado y rechazados ≈ 5 × 3 (rojo), "
           "separados", 105.0),
    Sector("C-16L", "Depósito de carros: liberados (16)", R(36.0, 10.6, 48.4, 17.4), "PT", "S3",
           "W-CAR: liberados 100 carros ≈ 6 × 10 (verde), hacia la puerta de despacho (calle T y muelle P3)", 60.0),
    # ---------------- banda sur: PT de manuales y muelle
    Sector("AL-3", "Almacén de producto terminado y de cilindros", R(30.6, 0.3, 50.0, 7.8), "PT", "S1 / S2",
           "X-DT Almacén PT 2035: 56 pallets esperando despacho + 72 del stock oct-nov = 128; con un solo "
           "autoelevador (W-MAN) dos racks de 7 módulos a 5 niveles sobre una calle de 5 m: 140 posiciones"),
    Sector("S4", "Tercerizados revendidos", R(48.6, 11.2, 49.9, 16.8), "PT", "S4",
           f"{_V5} 'Almacén de producto terminado': 17 posiciones; rack de 2 módulos × 4 niveles frente a la calle "
           "del muelle (CO₂, agua, AFFF, clase K y agente limpio)", 7.3),
    Sector("EXP", "Calle del muelle y expedición (P3)", R(50.0, 0.3, 53.6, 19.2), "PT", "común",
           "Un solo muelle con rampa niveladora (P3 queda para despachar, la MP entra por P1): sale PT, cilindros y "
           "carros (a pintura y terminados); vuelven los carros pintados. Expedición 13 a 17 h"),
    # ---------------- banda sur: terminación de manuales, depósito de polvo y embalaje
    Sector("DP", "Depósito de polvo químico (único de la planta)", R(55.2, 4.6, 59.4, 7.6), "MP", "común",
           f"{_V5}: 11 posiciones, 8,4 m² netos, 12,6 brutos; cerrado y seco: big bags de ABC 60 y ABC 90, polvo D y "
           "pintura en polvo; llegan de P1 por la calle del muelle y AT; salen a la carga (norte), a carros (AT y "
           "calle del PT) y a pintura (oeste)", 12.6),
    Sector("S-T", "Terminación 1 a 10 kg", R(55.2, 9.6, 72.4, 12.8), "TERM", "S1 / S2",
           "W-MAN: carga (estación de big bag y transportador neumático) -> ensamblaje -> presurización -> ensayo de "
           "pérdidas -> etiquetado, con un FCHP20505 entre cada par de puestos; termina en el embalaje"),
    Sector("EMB", "Embalaje y paletizado (vacíos y terminados)", R(59.6, 4.6, 74.4, 9.4), "PT", "S1 / S2",
           "W-MAN: los vacíos se encajonan al lado de la descarga de pintura y los terminados al final de la "
           "terminación, en la misma zona: armadora de cajas, 2 mesas de encajonado (X-MAN) y envolvedora EDOS PS5"),
    Sector("AL-EB", "Embalaje: cajas plegadas, film y pallets", R(53.7, 0.3, 70.2, 1.7), "MP", "S1 / S2",
           f"{_V5}: 50 posiciones, 22,2 m² netos; rack de 6 módulos × 2 × 4 niveles = 48 + pila de pallets vacíos "
           "junto a la envolvedora; las cajas van a la armadora con la transpaleta", 17.8),
    Sector("PU-9", "Terminados pintados esperando la carga", R(55.2, 15.8, 57.8, 18.6), "TERM", "S1 / S2",
           "W-MAN: van de la descarga a la carga en sus carros; el Word no dimensiona el pulmón: 1 carro"),
    Sector("DL", "Ducha de emergencia y lavaojos", R(70.4, 15.8, 72.4, 18.8), "AUX", "común",
           "A menos de 10 s de la carga de polvo, de la presurización y de la descarga de pintura"),
]

# ============================================================ EQUIPOS (paso = número de operación en el plano)
# fuente: C = cotización recibida (referencias/INVESTIGACION PROVEEDORES); W = Word del proceso (W-MAN, W-CAR);
# X = Excel de dimensionamiento; D = medida de diseño con su criterio
E_ = Equipo
EQUIPOS = [
    # ---------------- almacén de MP
    E_("RMM", "Rack de insumos de montaje (4 mód. × 4 niveles)", Rw(0.35, 26.4, 1.15, 10.8), "AL-MM", 0,
       fuente="X-ALM: 32 posiciones de pallet 1,2 × 1,0", forma="rack", tipo="rack", frente="E"),
    E_("EID", "Estantería de identificación (5 niveles)", Rw(0.35, 37.5, 0.7, 1.3), "AL-ID", 0,
       fuente="X-ALM: estantería de cajas", tipo="estanteria", frente="E"),
    E_("RMC", "Rack de insumos de carros (1 mód. × 4 niveles)", Rw(0.35, 39.2, 1.15, 2.7), "AL-MC", 0,
       fuente="X-ALM: 8 posiciones", forma="rack", tipo="rack", frente="E"),
    E_("CAB", "Carros de abastecimiento (2)", Rw(0.4, 19.6, 1.1, 2.6), "AL-CA", 0,
       fuente="W-CAR tabla 5: 3 × 1 m", forma="rack", tipo="carros", frente="N"),
    E_("CT1", "Cantiléver de caños y barras (3 niveles)", Rw(1.8, 24.65, 7.0, 1.45), "AL-CT", 0,
       fuente="X-ALM: caño de 6 m + 0,4 m por extremo; brazos hacia P1", tipo="cantilever", frente="N"),
    E_("MI1", "Mesa de inspección de recepción (micrómetro)", Rw(9.3, 24.75, 1.2, 0.6), "AL-CU", 1,
       fuente="W-MAN y W-CAR: mesa 1,2 × 0,6", tipo="mesa_control", frente="N"),
    E_("BP1", "Balanza de plataforma 1,20 × 1,20 m, 1.500 kg (recepción)", Rw(9.2, 32.6, 1.2, 1.2), "AL-CU", 0,
       fuente="W-MAN y W-CAR puesto 1: balanza de plataforma compartida", tipo="balanza", frente="O"),
    E_("HJ1", "Paquetes de hojas LAF (5 posiciones × 2 alturas)", Rw(11.65, 24.7, 1.4, 12.0), "AL-CH", 0,
       fuente="X-ALM: 7 lugares de 1,22 × 2,44 a 1,5 × 3,0", tipo="paquetes", frente="E"),
    E_("HJ2", "Chapa LAC de carros (3 posiciones)", Rw(18.15, 24.7, 1.4, 9.7), "AL-CC", 0,
       fuente="W-CAR: 3 posiciones de 3,0 × 1,5 m", tipo="paquetes", frente="O"),
    E_("RF1", "Porta-flejes de 3 niveles (21 cunas)", Rw(9.15, 42.25, 6.0, 1.3), "AL-FL", 0,
       fuente="X-ALM 21 rollos; porta-flejes de MP Opción D", tipo="portaflejes", frente="S"),
    E_("RSS", "Rack de soldadura y superficie (1 mód. de 3 pallets × 4 niveles)", Rw(15.35, 42.3, 3.7, 1.15), "AL-SS",
       0, fuente="X-ALM: 12 posiciones", forma="rack", tipo="rack", frente="S"),
    E_("RCQ", "Rack de casquetes y cuplas (2 mód. × 4 niveles)", Rw(19.2, 42.3, 5.35, 1.15), "AL-CQ", 0,
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
    E_("B02", "Roladora Firesafer FS-RM01", Rw(30.8, 30.4, 1.7, 0.8), "N6", 1, 4.0,
       fuente="W-MAN: trifásica 380 V, 4 kW (huella de catálogo)", tipo="cilindradora", frente="N"),
    E_("B03", "Soldadora longitudinal Firesafer (MAG)", Rw(33.5, 30.0, 2.0, 1.4), "N6", 1, 12.0, polvo=True,
       fuente="C Firesafer; W-MAN", tipo="sold_long", frente="N"),
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
    E_("B10", "Corrección: mesa y cabina de amolado con extracción", Rw(73.4, 41.8, 2.2, 1.5), "N8", 1, 3.0,
       polvo=True, fuente="W-MAN: amoladora 115 mm, machos y calibres", tipo="banco_sold", frente="S"),
    # ---------------- pintura: riel aéreo con horno único (precalentamiento y curado en el mismo cuerpo)
    E_("P03", "Horno a gas: precalentamiento y curado 180-220 °C (dos pasadas del riel)", Rw(82.6, 13.0, 2.44, 6.0),
       "S-P", 0, 3.0, gas=True, fuente="C Electricolor 6 × 2,44 m; W-MAN 15 a 20 min; X-MAN: 1 horno",
       tipo="horno", frente="O"),
    E_("P04", "Cabina de pintura 2 × 1,5 m y reciprocador 1300", Rw(78.35, 10.4, 1.7, 2.0), "S-P", 1, 5.0,
       aire=True, polvo=True, fuente="C Electricolor", tipo="cabina", frente="O"),
    E_("P05", "Ciclones de recuperación de polvo (2)", Rw(80.4, 10.5, 1.4, 1.7), "S-P", 0, 11.0, polvo=True,
       fuente="C Electricolor", tipo="ciclones", frente="O"),
    E_("P02", "Equipos de aplicación y tolvas EC40-200D", Rw(76.1, 12.6, 1.0, 1.8), "S-P", 0, 2.0, aire=True,
       fuente="C Electricolor", frente="E"),
    E_("P08", "Enfriamiento y descarga: separa vacíos y terminados", Rw(81.2, 3.1, 5.5, 6.8), "S-P", 1,
       fuente="C Electricolor; W-MAN: el flujo se divide al descolgar", tipo="estacion_pintura", frente="O"),
    E_("P09", "Control de espesor de película y adherencia", Rw(78.15, 5.6, 2.0, 1.4), "S-P", 0,
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
    # ---------------- PT de manuales (un solo autoelevador: calle de 5 m)
    E_("RK1", "Rack RK1 (7 mód. × 5 niveles)", Rw(30.8, 0.4, 18.9, 1.1), "AL-3", 0,
       fuente="X-DT 128 pallets: 7 módulos de 2,7 m × 2 pallets × 5 niveles = 70", forma="rack", tipo="rack",
       frente="N"),
    E_("RK2", "Rack RK2 (7 mód. × 5 niveles)", Rw(30.8, 6.6, 18.9, 1.1), "AL-3", 0,
       fuente="X-DT 128 pallets: 7 módulos × 2 × 5 = 70 (total 140)", forma="rack", tipo="rack", frente="S"),
    E_("RKR", "Rack de revendidos (2 mód. × 4 niveles)", Rw(48.7, 11.3, 1.1, 5.4), "S4", 0,
       fuente="X-ALM: 17 posiciones", forma="rack", tipo="rack", frente="E"),
    # ---------------- carros: franja central (W-CAR 3 a 11)
    E_("C01", "Roladora hidráulica CNC W12 8 × 1500", Rw(41.6, 30.0, 3.2, 1.4), "C-3", 1, 7.5,
       fuente="W-CAR: ≈ 3,2 × 1,4 m (a confirmar)", tipo="cilindradora", frente="N"),
    E_("C02a", "Punteo: virador sobre base fija", Rw(50.4, 30.4, 1.2, 0.6), "C-4", 1, 0.5,
       fuente="W-CAR: 1,2 × 0,6 con 1 m libre en cada boca; X-CAR: 1", tipo="posicionador", frente="N"),
    E_("C02s", "Soldadora Pampa 300 y banco con morsa", Rw(47.8, 32.4, 2.0, 0.9), "C-4", 0, 10.0,
       polvo=True, fuente="W-CAR: soldadora 0,9 × 0,5 y banco 1,5 × 0,7", tipo="banco", frente="S"),
    E_("C04", "Soldadora longitudinal ZH-1300 con mesa", Rw(57.4, 30.2, 2.3, 1.14), "C-5", 1, 12.0, polvo=True,
       fuente="W-CAR: 2,30 × 1,14 m; fuente MIG-350IX y chiller detrás", tipo="sold_long", frente="N"),
    E_("C06", "Soldadura de cupla: mesa Müller con posicionador", Rw(63.2, 31.2, 0.9, 0.6), "C-6", 1, 6.0,
       polvo=True, fuente="W-CAR: ≈ 0,9 × 0,6 m", tipo="posicionador", frente="N"),
    E_("C05", "Armado y soldadura circ.: virador con tope axial", Rw(69.6, 31.0, 1.6, 0.8), "C-7", 1, 10.0,
       polvo=True, fuente="W-CAR: ≈ 1,6 × 0,8 m, 1 m libre en cada punta", tipo="posicionador", frente="N"),
    E_("C08", "Soldadura de accesorios e inspección de cordones: virador", Rw(70.0, 26.6, 1.6, 0.8), "C-8", 1, 10.0,
       polvo=True, fuente="W-CAR: ≈ 1,6 × 0,8 m, 1 m libre en cada punta", tipo="posicionador", frente="S"),
    E_("C81r", "Rack de barras (6,5 m) y caballetes", Rw(60.5, 24.65, 6.6, 1.2), "C-81", 0,
       fuente="W-CAR 8.1: 6,5 × 0,6 + caballetes 6,8 × 0,6", tipo="cantilever", frente="N"),
    E_("C81", "Sensitiva, dobladora, taladro, prensa 20 t y banco de kits", Rw(60.8, 26.85, 6.0, 1.3), "C-81", 1,
       5.0, fuente="W-CAR 8.1: ≈ 8,0 × 4,0 m", tipo="banco", frente="S"),
    E_("C07", "PH: 2 bandejas, pantalla y Yukon M-000200", Rw(55.5, 26.7, 3.0, 1.4), "C-9", 1, 2.0, agua=True,
       fuente="C Yukon M-000200; W-CAR tabla del puesto 9", tipo="ph", frente="S"),
    E_("C07t", "Tanque de 1.000 L con bomba y filtros (circuito cerrado)", Rw(58.6, 24.7, 1.56, 1.56), "C-9", 0,
       fuente="W-CAR: Rotoplas Ø1,56 m en el rincón del fondo", tipo="tanque", forma="circ"),
    E_("C10", "Secadora eléctrica Melisam MR011 (lanza a la boca)", Rw(53.4, 27.6, 0.6, 0.5), "C-10", 0, 2.0,
       fuente="W-CAR 10: ≈ 0,6 × 0,5 m, resistencia de ≈ 2 kW", tipo="secadora", frente="S"),
    # ---------------- carros: banda sur (W-CAR 12 a 17)
    E_("C12J", "Cambio de juego (2 lugares): crique carrito, zorra de retorno y cajones", Rw(42.6, 9.4, 4.0, 1.5),
       "C-12C", 1, fuente="W-CAR 12: 2 × (2,0 × 1,5 m)", tipo="banco", frente="S"),
    E_("T12", "Estación A: cinta y control del interior (lugar del carro)", Rw(25.0, 7.6, 2.4, 2.2), "C-13", 1,
       fuente="W-CAR 13: 2,4 × 2,2 m del lado del pulmón de pintados", tipo="ensamble", frente="E"),
    E_("T02", "Estación B: balanza de plataforma con rampa y cargadora Yukon M-000121", Rw(25.8, 3.6, 2.6, 2.6),
       "C-13", 1, 3.0, aire=True, polvo=True, n2=True, fuente="W-CAR 13: 3,0 × 2,6 m; C Yukon M-000121",
       tipo="carga_polvo", frente="O"),
    E_("BB2", "Bastidor de big bag (ABC 90) con tolva de 100 L", Rw(28.6, 4.1, 1.6, 1.2), "C-13", 0,
       fuente="W-CAR 13: 1,6 × 1,2 m detrás de la balanza, con acceso para el autoelevador", tipo="carga_polvo",
       frente="E"),
    E_("CL13", "Colector de polvo 3 HP (aspiración en la boca)", Rw(28.7, 5.6, 0.8, 0.8), "C-13", 0, 2.2,
       polvo=True, fuente="W-CAR 13", tipo="colector"),
    E_("BN2", "Batería de N₂ (11 tubos de 50 L) en jaula, con manifold", Rw(29.4, 6.6, 0.9, 2.6), "C-13", 0,
       fuente="W-CAR 13: 2,6 × 0,9 m contra la pared, encadenada", tipo="bateria_gas", frente="O"),
    E_("T13", "Estación C: manga, traba, precinto y tarjeta (lugar del carro)", Rw(25.0, 0.5, 2.3, 2.2), "C-13", 1,
       fuente="W-CAR 13: 2,3 × 2,2 m del lado del etiquetado", tipo="ensamble", frente="E"),
    E_("T15", "Etiquetado e inspección final: mesa de calcomanías", Rw(23.1, 2.6, 1.2, 0.6), "C-15", 0,
       fuente="W-CAR 15: mesa 1,2 × 0,6 m", tipo="etiquetadora", frente="S"),
    E_("C14", "Split frío/calor BGH 3000F y registrador (21 °C)", Rw(16.1, 4.4, 0.6, 0.8), "C-14", 0, 3.5,
       fuente="W-CAR 14", tipo="deshumidificador", frente="E"),
    E_("C17R", "Recinto de descarga 12 × 3 m, alto 3 m, con piso marcado y ventana", Rw(1.6, 0.5, 11.0, 3.0),
       "C-17", 1, fuente="W-CAR 17: viento < 15 km/h, alcance marcado cada 0,5 m", tipo="cabina_muestras",
       frente="N", polvo=True),
    E_("C17C", "Colector de polvo con filtro de mangas (3 HP)", Rw(0.45, 0.5, 1.0, 1.0), "C-17", 0, 2.2,
       polvo=True, fuente="W-CAR 17: ≈ 1,0 × 1,0 m en el fondo del recinto", tipo="colector"),
    E_("BP2", "Balanza de plataforma 1,2 × 1,2 m con rampa (300 kg)", Rw(12.9, 2.6, 1.2, 1.2), "C-17", 0,
       fuente="W-CAR 17: al lado de la puerta del recinto, del lado de la sala de pérdidas", tipo="balanza",
       frente="E"),
    # ---------------- SC compresores
    E_("CG1", "Reguladores de Arcal 21 y N₂ (de la jaula exterior)", Rw(49.6, 41.8, 2.0, 1.2), "SC", 0,
       fuente="W-MAN: pack con manifold y cañería a los puestos", tipo="bateria_gas", frente="S"),
    E_("CH1", "Colector de humos de soldadura (filtro de cartuchos)", Rw(53.0, 41.4, 2.4, 1.5), "SC", 0, 7.5,
       polvo=True, fuente="D colector de cartuchos 6000 m³/h", tipo="colector", frente="S"),
    E_("CP1", "Compresor de tornillo 30 kW", Rw(57.0, 41.6, 1.9, 1.1), "SC", 0, 30.0,
       fuente="D compresor de tornillo 30 kW (1,9 × 1,1)", tipo="compresor", frente="S"),
    E_("CP2", "Compresor de tornillo 30 kW (reserva)", Rw(60.4, 41.6, 1.9, 1.1), "SC", 0, 30.0,
       fuente="D compresor de tornillo 30 kW (1,9 × 1,1)", tipo="compresor", frente="S"),
    E_("SEC", "Secador frigorífico y filtros", Rw(63.8, 41.7, 1.0, 0.9), "SC", 0, 1.5,
       fuente="D secador para 5 m³/min", tipo="compresor", frente="S"),
    E_("TQ1", "Pulmón de aire 2000 L", Rw(66.4, 41.6, 1.2, 1.2), "SC", 0, fuente="D tanque vertical Ø 1,2 m",
       tipo="tanque", forma="circ", frente="S"),
]

# ============================================================ NUMERACIÓN DE PASOS (orden de los Word)
# manuales (W-MAN): 1 corte de chapa, 2 corte de tubo, 3 disco y embutido, 4 cuello, 5 numerado, 6 cilindrado,
# 7 soldadura longitudinal, 8 soldadura de cuello, 9 encastre, 10 bordoneado, 11 soldadura circ., 12 espesor,
# 13 PH, 14 secado, 15 granallado, 16 detección, 17 corrección, 18 pintura (18.1 y 18.3 en el mismo horno),
# 19 carga, 20 ensamblaje, 21 presurización, 22 pérdidas, 23 etiquetado, 24 embalaje. Carros (W-CAR): C2.1 marcado,
# C3 cilindrado ... C17 ensayos de lote.
PASOS = {
    "M04": "1", "M16": "2", "M06": "3.1", "M07": "3.2", "M08": "3.3", "M09a": "4.1", "M09b": "4.2", "M10": "5",
    "B02": "6", "B03": "7", "M11": "8", "E09": "9", "B04": "10", "A06": "11.1", "B06": "11.2", "Q01": "12",
    "A07": "13.1", "B07": "13.2", "B14a": "14.1", "B14b": "14.2", "B14c": "14.3", "B14d": "14.4", "RIN": "15",
    "B08": "15", "ROUT": "15", "B09": "16", "B10": "17", "P03": "18.1-3", "P04": "18.2", "P08": "18.4",
    "BB1": "19", "T01": "19", "T03": "20", "T05": "21", "T06": "22", "T07": "23",
    "T09": "24.1", "T08": "24.2", "AC1": "24", "T11": "24.3",
    "MK1": "C2.1", "C01": "C3", "C02a": "C4", "C04": "C5", "C06": "C6", "C05": "C7", "C08": "C8", "C81": "C8.1",
    "C07": "C9", "C10": "C10", "C12J": "C12", "T12": "C13A", "T02": "C13B", "T13": "C13C", "C14": "C14",
    "T15": "C15", "C17R": "C17",
}
for _e in EQUIPOS:
    _e.paso = PASOS.get(_e.cod, "")


# ============================================================ PULMONES (sólo los que nombran W-MAN y W-CAR)
_FC = "Carro FCHP20505 (3 planos de 1280 × 610 mm)"
_CE = "Carros de estantes de 12 cajones"
PULMONES = [
    # corte de chapa y cuerpo de manuales (W-MAN corte de chapa, cilindrado y soldadura longitudinal)
    Pulmon("PU-1", R(29.9, 26.5, 32.1, 28.7), "Rampa trasera: carro de plataforma de desarrollos (W-MAN, en llenado) "
           "y carro de salida de cuerpos de carros (W-CAR)", "1 Guillotina", "6 Cilindrado / C2.1 marcado", 2, "h"),
    Pulmon("PU-M", R(33.9, 24.9, 35.6, 27.2), "EFE 600 (25 y 50 kg) y mesa móvil (70 y 100 kg) con cuerpos grabados",
           "C2.1 Marcado", "C3 Cilindrado de carros", 2, "v"),
    Pulmon("PU-D", R(29.0, 30.3, 30.6, 31.2), "Carro de plataforma con desarrollos frenado al lado de la roladora",
           "1 Guillotina", "6 Cilindrado", 1, "h"),
    Pulmon("PU-V1", R(32.7, 30.1, 33.31, 31.38), _FC + ": virolas (el segundo carro es el de cambio de formato)",
           "6 Cilindrado", "7 Sold. longitudinal", 1, "v"),
    Pulmon("PU-V2", R(35.7, 30.1, 36.31, 31.38), _FC + ": cuerpos soldados (se llena)", "7 Sold. longitudinal",
           "9 Encastre", 1, "v"),
    Pulmon("PU-V3", R(34.6, 34.9, 35.88, 35.51), _FC + ": cuerpos soldados (al lado del encastre)",
           "7 Sold. longitudinal", "9 Encastre", 1, "h"),
    Pulmon("PU-FX", R(29.2, 36.0, 33.3, 36.8), _FC + ": carros de cambio de formato (W-MAN: cilindrado, encastre y "
           "bordoneado, uno por tramo)", "Cambio de formato", "6, 9 y 10", 3, "h"),
    # tubo, embutido y cuello
    Pulmon("PU-T1", R(27.3, 35.0, 28.6, 36.8), _CE + ": tramos «en llenado» y «vacío»", "2 Corte de tubo",
           "9 Encastre", 2, "v"),
    Pulmon("PU-T2", R(33.9, 35.6, 35.8, 36.9), _CE + ": tramos «en consumo» y «lleno»", "2 Corte de tubo",
           "9 Encastre", 2, "h"),
    Pulmon("PU-K", R(31.5, 40.5, 34.3, 41.6), _CE + ": cúpulas y fondos en llenado", "3 Embutido",
           "Zonas de cúpulas y de fondos", 2, "h"),
    Pulmon("PU-FO", R(33.9, 37.1, 37.3, 39.1), "Zona de fondos: 3 a 5 carros (W-MAN, colchón de la tanda)", "3 Embutido",
           "9 Encastre", 4, "h"),
    Pulmon("PU-CU", R(34.6, 40.6, 38.8, 43.4), "Zona de cúpulas: carros numerados por orden de llegada (3 a 5, igual "
           "que la de fondos)", "3 Embutido", "5 Numerado", 4, "h"),
    Pulmon("PU-CC2", R(44.6, 40.6, 45.9, 41.9), _CE + ": cúpulas con cuello (en llenado)", "8 Sold. de cuello",
           "11 Sold. circunferencial", 1, "v"),
    Pulmon("PU-CC", R(41.8, 37.3, 43.1, 38.6), _CE + ": cúpulas con cuello (en consumo; W-MAN: dos carros "
           "alternándose)", "8 Sold. de cuello", "11 Sold. circunferencial", 1, "h"),
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
    Pulmon("PU-CO", R(76.2, 40.8, 77.5, 41.6), "Carro de corregibles (W-MAN)", "16 Detección", "17 Corrección", 1,
           "h"),
    # terminación de manuales (un FCHP20505 entre cada par de puestos)
    Pulmon("PU-F1", R(59.2, 10.5, 59.85, 11.8), _FC, "19 Carga de polvo", "20 Ensamblaje", 1, "v"),
    Pulmon("PU-F2", R(61.9, 10.5, 62.55, 11.8), _FC, "20 Ensamblaje", "21 Presurización", 1, "v"),
    Pulmon("PU-F3", R(64.5, 10.5, 65.15, 11.8), _FC, "21 Presurización", "22 Ensayo de pérdidas", 1, "v"),
    Pulmon("PU-F4", R(67.6, 10.5, 68.25, 11.8), _FC, "22 Ensayo de pérdidas", "23 Etiquetado", 1, "v"),
    Pulmon("PU-F5", R(66.6, 8.95, 67.9, 9.6), _FC + ": etiqueta hacia afuera", "23 Etiquetado", "24 Encajonado",
           1, "h"),
    Pulmon("PU-TP", R(55.4, 16.0, 56.7, 16.65), "Carro de terminados pintados (con tapón de silicona)",
           "18 Descarga de pintura", "19 Carga de polvo", 1, "h"),
    # carros (W-CAR, tablas de espacios de cada puesto)
    Pulmon("PU-CI", R(41.6, 32.5, 44.0, 33.5), "EFE 600 y mesa móvil frente a la zona de carga", "C2.1 Marcado",
           "C3 Cilindrado", 2, "h"),
    Pulmon("PU-CR", R(45.8, 29.6, 47.0, 31.4), "Pulmón de cuerpos rolados y tiras (1,8 × 1,2, amarillo)",
           "C3 Cilindrado", "C4 Punteo", 1, "v"),
    Pulmon("PU-CP", R(53.2, 30.0, 54.6, 31.6), "Pulmón de cuerpos punteados (1,6 × 1,2)", "C4 Punteo",
           "C5 Sold. longitudinal", 1, "v"),
    Pulmon("PU-NC5", R(59.9, 30.1, 60.9, 30.9), "No conforme (1,0 × 0,8, rojo)", "C5 Sold. longitudinal",
           "Reparación o scrap", 1, "h"),
    Pulmon("PU-K1", R(61.8, 32.3, 62.9, 33.0), "Carro 1: cúpulas y cuplas (1,07 × 0,7)", "AL-CQ",
           "C6 Cupla", 1, "h"),
    Pulmon("PU-C6", R(64.6, 30.0, 65.7, 30.7), "Carro canasto de salida (1,1 × 0,7)", "C6 Cupla", "C7 Armado", 1,
           "h"),
    Pulmon("PU-F7", R(66.4, 30.9, 67.5, 31.6), "Carro 2 de fondos (1,1 × 0,7)", "AL-CQ", "C7 Armado", 1, "h"),
    Pulmon("PU-C7", R(71.8, 29.6, 73.3, 30.8), "Pulmón de cilindros cerrados (1,5 × 1,2)", "C7 Armado",
           "C8 Accesorios", 1, "h"),
    Pulmon("PU-NC7", R(73.5, 32.6, 74.2, 33.2), "No conforme de los puestos 6 y 7 (0,7 × 0,6, rojo)", "C6 y C7",
           "Reparación o scrap", 1, "h"),
    Pulmon("PU-CK", R(68.3, 26.6, 68.82, 27.65), "Carro de kits (≈ 10 kits)", "C8.1 Accesorios", "C8 Accesorios",
           1, "v"),
    Pulmon("PU-JP", R(67.7, 24.7, 74.3, 25.2), "Juegos provisorios de eje y ruedas: 3 estanterías de ruedas y 3 "
           "cajones de ejes (vuelven de la recepción de pintados)", "C12 Cambio de juego", "C8 Accesorios", 3, "h"),
    Pulmon("PU-S8", R(67.7, 28.3, 68.8, 29.0), "Salida: carro sobre su juego provisorio (amarillo)", "C8 Accesorios",
           "C9 Prueba hidráulica", 1, "h"),
    Pulmon("PU-10", R(52.5, 25.0, 54.9, 26.1), "Espera de carros mojados (2) y lugar del carro que se seca",
           "C9 Prueba hidráulica", "C10 Secado", 2, "h"),
    Pulmon("PU-11", R(38.6, 24.8, 52.0, 29.0), "Carros secos con la boca tapada, en filas por modelo y semana",
           "C10 Secado", "Muelle P3 -> pintura tercerizada", 120, "h"),
    Pulmon("PU-RP", R(46.9, 8.0, 49.8, 9.3), "Rechazados del pintor (≈ 2 × 1,5, rojo)", "Muelle P3",
           "Vuelven al pintor", 2, "h"),
    Pulmon("PU-12", R(24.8, 10.7, 34.4, 17.2), "Carros pintados sobre sus ruedas nuevas, en filas por modelo y lote",
           "C12 Cambio de juego", "C13 Carga", 120, "h"),
    Pulmon("PU-14", R(16.8, 0.5, 20.8, 4.9), "Lugares numerados de la sala (30 carros de la muestra)", "C13 Carga",
           "C15 / C17", 30, "h"),
    Pulmon("PU-15", R(21.3, 1.4, 23.5, 2.3), "Lugar del carro que se etiqueta (2 × 1,0 × 0,8)", "C13 Carga",
           "C16 Retenidos", 2, "h"),
    Pulmon("PU-NC15", R(21.3, 2.5, 22.6, 3.4), "No conforme de la inspección final (rojo)", "C15 Etiquetado",
           "C13", 1, "h"),
    Pulmon("PU-16R", R(14.4, 8.6, 24.2, 17.2), "Retenidos: tarjeta amarilla (180 carros, filas por modelo y lote)",
           "C15 Etiquetado", "Liberados o rechazados", 180, "h"),
    Pulmon("PU-16X", R(14.4, 5.7, 19.4, 8.4), "Rechazados del lote: tarjeta roja (≈ 5 × 3)", "Retenidos",
           "Revisión al 100 % en el 13", 15, "h"),
    Pulmon("PU-16L", R(36.2, 10.8, 48.2, 17.2), "Liberados: tarjeta verde (100 carros)", "Retenidos",
           "Muelle P3 -> clientes", 100, "h"),
]

# ============================================================ PUERTAS Y PORTONES
# Dos portones en toda la nave (MP y muelle); el resto son puertas de personas y de emergencia.
PUERTAS = [
    Puerta("P1", "N", 0.5, 7.5, 4.5, "porton",
           "MP de manuales y de carros (toda la MP, una sola cuarentena): hojas, flejes, caños de 6 m (atado "
           "atravesado), barras, casquetes, insumos, polvo y pintura, embalaje y revendidos; sale el scrap"),
    Puerta("P3", "S", 50.15, 53.15, 3.2, "muelle",
           "Muelle de despacho: PT y cilindros, carros a pintura y terminados; vuelven los carros pintados"),
    # salidas de emergencia (1,10 m, barral antipánico, abren hacia afuera)
    Puerta("SE-1", "N", 46.5, 47.6, 2.1, "emergencia"),
    Puerta("SE-4", "N", 77.6, 78.7, 2.1, "emergencia"),
    Puerta("SE-5", "E", 39.25, 40.35, 2.1, "emergencia"),
    Puerta("SE-6", "E", 33.55, 34.65, 2.1, "emergencia"),
    Puerta("SE-7", "S", 86.0, 87.1, 2.1, "emergencia"),
    Puerta("SE-9", "S", 70.6, 71.7, 2.1, "emergencia"),
    Puerta("SE-10", "O", 7.0, 8.1, 2.1, "emergencia"),
    Puerta("SE-11", "O", 17.6, 18.7, 2.1, "emergencia"),
    Puerta("PE-1", "S", 14.4, 15.6, 2.1, "peatonal",
           "Patio de ensayos de carros (rodadura, caída y choque, W-CAR 17) y salida de emergencia"),
    Puerta("PP-1", "O", 23.2, 24.4, 2.1, "peatonal", "Ingreso de personal desde vestuarios"),
    Puerta("OF-1", "O", 11.65, 12.75, 2.1, "peatonal", "Ingreso a las oficinas (camino peatonal desde SV-1)"),
    Puerta("AD-1", "E", 26.0, 27.2, 2.1, "peatonal", "Administración: ingreso de visitas por la fachada este"),
    Puerta("PG", "N", 48.3, 49.3, 2.1, "peatonal", "A la jaula exterior de gases (control de presión y cambio de pack)"),
]

# ventanas en el cerramiento de la nave: (lado, desde, hasta, uso)
VENTANAS_NAVE = [("O", 8.6, 10.8, "Laboratorio de calidad: luz natural"),
                 ("E", 29.6, 32.6, "Administración: ventana al este")]

# ============================================================ ANEXOS
ANEXOS = [
    Sector("SV", "Bloque de servicios al personal", R(-18.0, 19.0, 0.0, 35.0), "SERV", "común"),
    Sector("ST", "Sala técnica: transformador y TGBT", R(36.0, 44.2, 46.0, 50.0), "AUX", "común"),
]

# ============================================================ RIEL AÉREO DE PINTURA (W-MAN)
# cargado: detección -> bajada por el este -> horno (pasada 1, precalentamiento) -> lazo por la cabina -> horno
# (pasada 2, curado) -> enfriamiento por el oeste -> descarga; retorno de ganchos vacíos por encima de PO-PI y PO-6
RIEL = [(74.6, 36.4), (86.6, 36.4), (86.6, 20.2), (84.44, 20.2), (84.44, 10.0), (79.2, 10.0), (79.2, 12.4),
        (83.2, 12.4), (83.2, 21.4), (77.6, 21.4), (77.6, 8.0), (82.0, 8.0)]
RIEL_2 = []
RIEL_RET = [(81.2, 5.0), (75.3, 5.0), (75.3, 35.0), (74.9, 35.0)]
LAZO = RIEL                          # compatibilidad con el dibujo del transportador
TL = []                              # sin tren logístico: carros a mano entre puestos pegados (W-MAN)
TL_CARGADO = []
TL_RETORNO = []

# ============================================================ FLUJOS (m)
FLUJOS = [
    # ---------------- MP: una sola recepción por P1 (W-MAN y W-CAR: playón -> cuarentena compartida)
    Flujo("MP", [(4.0, 52.0), (4.0, 43.8), (4.0, 30.0), (9.1, 30.0)],
          "Recepción: alero -> P1 -> A1 -> cuarentena (colada, espesor, peso y lote)"),
    Flujo("MP", [(2.6, 52.0), (2.6, 43.8), (2.6, 26.1)],
          "Atado de caños de 6 m: entra atravesado por P1 y se apoya en el cantiléver sin girar"),
    Flujo("MP", [(9.1, 31.0), (8.0, 31.0), (8.0, 40.0), (14.4, 40.0), (14.4, 30.5), (13.1, 30.5)],
          "Hojas aprobadas: cuarentena -> A1 -> AN -> A2 -> paquetes de manuales"),
    Flujo("MP", [(13.1, 27.0), (14.0, 27.0), (14.0, 39.2), (21.2, 39.2), (21.2, 26.2), (24.8, 26.2)],
          "Paquete a la mesa elevadora (autoelevador de costado por A2, AN y A3)"),
    Flujo("MP", [(18.1, 29.4), (17.0, 29.4), (17.0, 38.6), (22.4, 38.6), (22.4, 25.6), (24.8, 25.6)],
          "Paquete LAC de carros a la misma mesa elevadora"),
    Flujo("MP", [(12.1, 42.25), (12.1, 41.6), (24.8, 41.6)], "Rollo de fleje al desbobinador (espolón por AN)"),
    Flujo("MP", [(5.4, 26.1), (5.4, 39.6), (23.4, 39.6), (23.4, 33.2), (24.75, 33.2)],
          "Atado del cantiléver al cajón del láser (pluma, por A1, AN y A3)"),
    Flujo("MP", [(6.6, 26.1), (6.6, 38.0), (19.9, 38.0), (19.9, 24.0), (64.0, 24.0), (64.0, 24.65)],
          "Barras y caños de carros de 6 m: de a una, a mano, del cantiléver al rack del puesto 8.1 (W-CAR)", "S3"),
    Flujo("MP", [(21.9, 42.3), (21.9, 41.0), (24.0, 41.0), (24.0, 24.2), (37.6, 24.2), (37.6, 34.35),
                 (62.3, 34.35), (62.3, 33.0)],
          "Casquetes y cuplas: carros 1 y 2 a los puestos 6 y 7", "S3"),
    Flujo("MP", [(7.2, 52.0), (7.2, 43.8), (7.2, 40.6), (22.9, 40.6), (22.9, 20.0), (50.4, 20.0), (50.4, 3.0),
                 (57.0, 3.0), (57.0, 4.6)],
          "Polvo y pintura en big bags, embalaje y revendidos: P1 -> cuarentena -> pasillo central -> calle del "
          "muelle -> depósito de polvo, AL-EB y S4"),
    Flujo("MP", [(56.6, 7.6), (56.6, 10.2)], "Big bag de ABC 60 a la estación de la carga (autoelevador)"),
    Flujo("MP", [(57.6, 4.6), (57.6, 3.6), (52.0, 3.6), (52.0, 4.7), (30.2, 4.7)],
          "Big bag de ABC 90 al bastidor de la carga de carros (AT, calle del muelle y calle del PT)", "S3"),
    Flujo("MP", [(55.2, 6.4), (54.6, 6.4), (54.6, 20.4), (76.6, 20.4), (76.6, 14.4)],
          "Pintura en polvo a las tolvas de la cabina (AC -> PC -> PO-PI)"),
    # ---------------- SE: corte de chapa, tubo y cuerpo (W-MAN)
    Flujo("SE", [(29.7, 27.0), (29.9, 27.0)], "Desarrollos a la rampa"),
    Flujo("SE", [(30.3, 28.7), (30.3, 30.3)], "Carro de plataforma con desarrollos al lado de la roladora", "S2"),
    Flujo("SE", [(32.1, 26.6), (32.3, 26.6)], "Cuerpo de carro al marcado", "S3"),
    Flujo("SE", [(30.6, 30.75), (30.8, 30.75)], "Desarrollo a la roladora", "S2"),
    Flujo("SE", [(32.5, 30.8), (32.7, 30.8)], "Virola al FCHP", "S2"),
    Flujo("SE", [(33.31, 30.7), (33.5, 30.7)], "Virola a la soldadora", "S2"),
    Flujo("SE", [(35.5, 30.7), (35.7, 30.7)], "Cuerpo soldado al FCHP", "S2"),
    Flujo("SE", [(36.0, 31.38), (36.0, 34.2), (35.2, 34.2), (35.2, 34.9)], "FCHP lleno al lado del encastre", "S2"),
    Flujo("SE", [(35.88, 35.2), (36.4, 35.2), (36.4, 35.8)], "Cuerpos 2,5-10 kg al encastre", "S2"),
    Flujo("SE", [(26.15, 36.6), (27.3, 36.6)], "Tramos 1 kg al carro de cajones", "S1"),
    Flujo("SE", [(28.6, 35.3), (33.75, 35.3), (33.75, 36.2), (33.9, 36.2)], "Carro de tramos al encastre", "S1"),
    Flujo("SE", [(35.8, 36.3), (36.0, 36.3)], "Tramo al encastre", "S1"),
    # ---------------- SE: embutido, celda de cuello y fondos
    Flujo("SE", [(26.6, 42.4), (26.9, 42.4)], "Fleje enderezado"),
    Flujo("SE", [(28.5, 42.4), (28.8, 42.4)], "Fleje al troquel"),
    Flujo("SE", [(30.4, 41.35), (30.4, 41.05), (31.5, 41.05)], "Cúpulas y fondos a los carros de cajones"),
    Flujo("SE", [(34.3, 41.0), (34.6, 41.0)], "Carro de cúpulas a la zona de cúpulas"),
    Flujo("SE", [(33.0, 40.5), (33.0, 39.6), (34.4, 39.6), (34.4, 39.1)], "Carro de fondos a la zona de fondos"),
    Flujo("SE", [(36.6, 37.1), (36.6, 36.8)], "Fondos al encastre"),
    Flujo("SE", [(38.8, 42.2), (39.0, 42.2), (40.0, 42.2), (40.2, 42.2), (41.2, 42.2), (41.4, 42.2), (42.4, 42.2),
                 (42.6, 42.2), (44.2, 42.2), (44.6, 42.2)],
          "Celda: numerado -> muesca del cuello -> soldadura de cuello (sin transporte)"),
    Flujo("SE", [(45.2, 40.6), (45.2, 39.0), (42.5, 39.0), (42.5, 38.6)],
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
    Flujo("SE", [(72.4, 38.4), (72.4, 39.0), (74.0, 39.0), (74.0, 41.8)],
          "Jaula «a corregir» a la corrección (carro de corregibles)"),
    Flujo("SE", [(73.4, 42.5), (72.0, 42.5), (72.0, 40.0), (64.6, 40.0), (64.6, 36.8)],
          "Corregidos y a re-granallar: vuelven a los rodillos de entrada"),
    # ---------------- riel aéreo (TL cargado; RET vacío)
    Flujo("TL", RIEL, "Riel aéreo: detección -> horno (precalentamiento) -> cabina -> horno (curado) -> descarga"),
    Flujo("RET", RIEL_RET, "Retorno de ganchos vacíos a la detección (aéreo)"),
    # ---------------- SE: descarga de pintura, terminación y embalaje (W-MAN)
    Flujo("SE", [(81.2, 9.0), (75.7, 9.0), (75.7, 14.4), (56.2, 14.4), (56.2, 16.0)],
          "Terminados pintados (con tapón) a la espera de la carga (PO-PI -> AT2)"),
    Flujo("SE", [(55.8, 16.0), (55.8, 13.2), (58.2, 13.2), (58.2, 11.8)], "Carro de terminados a la carga"),
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
    Flujo("PT", [(60.9, 5.0), (60.9, 2.4), (45.0, 2.4), (45.0, 1.5)],
          "Pallets al almacén de PT y de cilindros (transpaleta por AT, calle del muelle y calle del PT)"),
    Flujo("PT", [(40.0, 6.6), (40.0, 5.5), (50.7, 5.5), (50.7, 0.0), (50.7, -6.0)],
          "Expedición: rack -> calle del PT -> muelle P3"),
    Flujo("PT", [(49.8, 12.5), (51.0, 12.5), (51.0, 0.0), (51.0, -6.0)], "Revendidos a expedición (muelle P3)", "S4"),
    # ---------------- SE: carros, franja central (W-CAR 3 a 11)
    Flujo("SE", [(35.6, 26.0), (37.2, 26.0), (37.2, 33.0), (41.6, 33.0)],
          "Cuerpos grabados (EFE 600 / mesa móvil) del marcado al cilindrado por PO-1", "S3"),
    Flujo("SE", [(42.8, 32.5), (42.8, 31.4)], "Cuerpo a la roladora", "S3"),
    Flujo("SE", [(44.8, 30.7), (45.8, 30.7)], "Cuerpo rolado al pulmón", "S3"),
    Flujo("SE", [(47.0, 30.7), (50.4, 30.7)], "Pulmón al punteo", "S3"),
    Flujo("SE", [(51.6, 30.7), (53.2, 30.7)], "Cuerpo punteado al pulmón", "S3"),
    Flujo("SE", [(54.6, 30.8), (57.4, 30.8)], "Pulmón a la soldadura longitudinal", "S3"),
    Flujo("SE", [(58.5, 30.2), (58.5, 29.75), (70.4, 29.75), (70.4, 31.0)], "Cuerpo soldado al armado", "S3"),
    Flujo("SE", [(62.35, 32.3), (62.35, 31.5), (63.2, 31.5)], "Cúpula y cupla a la mesa", "S3"),
    Flujo("SE", [(64.1, 31.5), (64.4, 31.5), (64.4, 30.35), (64.6, 30.35)], "Cúpula con cupla al carro canasto", "S3"),
    Flujo("SE", [(65.7, 30.35), (69.0, 30.35), (69.0, 31.4), (69.6, 31.4)],
          "Carro canasto de cúpulas al armado", "S3"),
    Flujo("SE", [(67.5, 31.25), (68.6, 31.25), (68.6, 31.6), (69.6, 31.6)], "Fondos al armado", "S3"),
    Flujo("SE", [(71.2, 31.4), (72.5, 31.4), (72.5, 30.8)], "Cilindro cerrado al pulmón", "S3"),
    Flujo("SE", [(72.5, 29.6), (72.5, 27.0), (71.6, 27.0)], "Cilindro cerrado a la soldadura de accesorios", "S3"),
    Flujo("SE", [(66.8, 27.4), (68.3, 27.4)], "Kits del 8.1 al carro de kits", "S3"),
    Flujo("SE", [(68.82, 27.1), (70.0, 27.1)], "Kit al virador", "S3"),
    Flujo("SE", [(70.8, 27.4), (70.8, 28.65), (68.8, 28.65)], "Carro con su juego provisorio a la salida", "S3"),
    Flujo("SE", [(67.7, 28.65), (57.0, 28.65), (57.0, 28.1)], "Carro rodando a la prueba hidráulica", "S3"),
    Flujo("SE", [(55.5, 27.0), (55.1, 27.0), (55.1, 25.55), (54.9, 25.55)], "PH -> espera del secado", "S3"),
    Flujo("SE", [(53.5, 26.1), (53.5, 27.6)], "Carro al secado", "S3"),
    Flujo("SE", [(53.4, 27.85), (52.0, 27.85)], "Secado -> pulmón de despacho a pintura", "S3"),
    Flujo("SE", [(51.6, 24.8), (51.6, 24.6), (52.6, 24.6), (52.6, 0.0), (52.6, -6.0)],
          "Lote aprobado a pintura tercerizada (muelle P3)", "S3"),
    # ---------------- SE: carros, banda sur (W-CAR 12 a 17)
    Flujo("SE", [(52.2, -6.0), (52.2, 0.0), (52.2, 10.15), (46.6, 10.15)],
          "Carros pintados (vuelven por P3) al cambio de juego", "S3"),
    Flujo("SE", [(42.6, 9.9), (33.0, 9.9), (33.0, 10.7)], "Carros con ruedas nuevas al pulmón de pintados", "S3"),
    Flujo("SE", [(26.2, 10.7), (26.2, 9.8)], "Pulmón de pintados a la estación A", "S3"),
    Flujo("SE", [(26.6, 7.6), (26.6, 6.2)], "A -> B: carga de polvo y presurización", "S3"),
    Flujo("SE", [(26.6, 3.6), (26.6, 2.7)], "B -> C: manga, traba y precinto", "S3"),
    Flujo("SE", [(25.0, 1.85), (23.5, 1.85)], "Carro terminado al etiquetado", "S3"),
    Flujo("SE", [(22.85, 2.3), (22.85, 8.8)], "Etiquetado a retenidos (tarjeta amarilla)", "S3"),
    Flujo("SE", [(25.0, 0.8), (20.8, 0.8)], "Muestra del lote a la sala de pérdidas (7 días a 21 °C)", "S3"),
    Flujo("SE", [(16.8, 3.3), (14.1, 3.3)], "Muestra a la balanza (ensayo de funcionamiento)", "S3"),
    Flujo("SE", [(12.9, 3.2), (12.6, 3.2)], "Muestra al recinto de descarga", "S3"),
    Flujo("SE", [(16.8, 1.5), (15.0, 1.5), (15.0, 0.0), (15.0, -4.0)],
          "Muestra a la rodadura en el patio (remolque, caída y choque)", "S3"),
    Flujo("PT", [(23.0, 17.2), (23.0, 17.75), (36.6, 17.75), (36.6, 17.2)],
          "Lote aceptado: retenidos -> liberados (tarjeta verde)", "S3"),
    Flujo("PT", [(47.5, 17.2), (47.5, 17.85), (51.4, 17.85), (51.4, 0.0), (51.4, -6.0)],
          "Despacho de carros liberados (muelle P3)", "S3"),
    # ---------------- scrap: contenedor en el puesto; el autoelevador lo lleva al volquete (P1)
    Flujo("SCRAP", [(30.6, 24.9), (30.6, 22.4), (22.6, 22.4), (22.6, 41.2), (2.2, 41.2), (2.2, 43.8), (-1.2, 46.2)],
          "Orillas de la guillotina: autoelevador por el pasillo central, A3, AN y A1 al volquete (P1)"),
    Flujo("SCRAP", [(24.75, 28.6), (23.8, 28.6), (23.8, 40.8), (3.2, 40.8), (3.2, 43.8), (-1.2, 45.8)],
          "Recortes del láser: autoelevador por A3 al volquete (P1)"),
    Flujo("SCRAP", [(32.2, 41.9), (32.2, 40.9), (31.4, 40.0), (25.2, 40.0), (25.2, 39.8), (3.6, 39.8), (3.6, 43.8),
                    (-1.2, 45.4)], "Esqueleto de la prensa: contenedor por PO-3 y AN al volquete (P1)"),
    Flujo("SCRAP", [(74.6, 38.4), (74.6, 39.55), (2.4, 39.55), (2.4, 43.8), (-1.2, 45.0)],
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
          (_op("MK1")[0], Y_PP, *_op("MK1")), (_op("MI1")[0], Y_PP, *_op("MI1"))]
    H.append(("Recepción, corte de chapa y marcado (N1)", [(0.0, Y_PP), (36.0, Y_PP)], br))
    # cuerpo de manuales y línea principal: por PO-1 y PO-2
    br = [(37.8, 34.1, _op("B03")[0], 34.1), (_op("B03")[0], 34.1, *_op("B03")),
          (_op("B02")[0], 34.1, *_op("B02")), (_op("B03")[0], 34.1, _op("B02")[0], 34.1)]
    for c in ("E09", "B04", "A06", "B06", "Q01", "A07", "B07"):
        x, y = _op(c)
        br.append((x, 34.1, x, y))
    H.append(("Cuerpo, unión y PH (N4, N6)", [(36.0, Y_PP), (37.8, Y_PP), (37.8, 34.1), (54.0, 34.1)], br))
    # secado, granallado, detección y corrección: por PO-2, PO-7 y PO-3
    br = []
    for c in ("B14a", "B14c", "B08", "B09"):
        x, y = _op(c)
        br.append((x, 34.1, x, y))
    br += [(61.6, 34.1, 61.6, 39.8), (61.6, 39.8, _op("B10")[0], 39.8), (_op("B10")[0], 39.8, *_op("B10"))]
    H.append(("Secado, granallado, detección y corrección (N5, N8)", [(54.0, 34.1), (74.9, 34.1), (74.9, Y_PP)], br))
    # láser y embutido: por PO-3 desde PO-7
    br = [(31.0, 39.8, *_op("M08")), (_op("M16")[0], 39.8, *_op("M16")), (_op("M10")[0], 39.8, *_op("M10")),
          (_op("M09a")[0], 39.8, *_op("M09a")), (_op("M09b")[0], 39.8, *_op("M09b")),
          (_op("M11")[0], 39.8, *_op("M11"))]
    H.append(("Láser, embutido y celda de cuello (N2, N3, N7)", [(61.6, 39.8), (26.65, 39.8)], br))
    # pintura, terminación y embalaje: por PO-PI
    br = [(74.9, 11.4, *_op("P04")), (74.9, 6.5, 80.6, 6.5), (80.6, 6.5, *_op("P08"))]
    br += [(74.9, 10.2, _op("T01")[0], 10.2)]
    br += [(66.3, 10.2, 66.3, _op("T09")[1]), (66.3, _op("T09")[1], *_op("T09")),
           (72.6, 10.2, 72.6, _op("T08")[1]), (72.6, _op("T08")[1], *_op("T08"))]
    H.append(("Pintura, terminación y embalaje", [(74.9, Y_PP), (74.9, 0.6)], br))
    # PT y expedición: por AC y AT a la calle del muelle
    H.append(("PT y expedición", [(54.3, Y_PP), (54.3, 4.0)], [(54.3, 4.0, 53.0, 4.0)]))
    # carros 3 a 11 (franja central): fila sur desde la senda PP, fila norte desde PO-2
    br = []
    x, y = _op("C07")
    br.append((x, Y_PP, x, y))
    # 8.1 y 8: por el paso entre el rack de barras y los juegos provisorios
    x81, x08 = _op("C81")[0], _op("C08")[0]
    br += [(67.35, Y_PP, 67.35, 26.2), (67.35, 26.2, x81, 26.2), (x81, 26.2, *_op("C81")),
           (67.35, 26.2, x08, 26.2), (x08, 26.2, *_op("C08"))]
    for c in ("C01", "C02a", "C04", "C06", "C05"):
        x, y = _op(c)
        br.append((x, 34.1, x, y))
    H.append(("Carros: puestos 3 a 11 (franja central)", [(37.8, Y_PP), (74.0, Y_PP)], br))
    # carros 12 a 17, depósito y calidad (banda sur): cruzan el pasillo central por la senda de PO-K
    xa, ya = _op("T12")
    xb, yb = _op("T02")
    xc, yc = _op("T13")
    br = [(25.6, 18.4, 35.2, 18.4), (35.2, 18.4, 35.2, 8.2), (35.2, 8.2, *_op("C12J")),
          (35.2, 9.6, 28.0, 9.6), (28.0, 9.6, xa, ya), (28.0, 9.6, 28.0, 7.0), (28.0, 7.0, xb, 7.0),
          (xb, 7.0, xb, yb), (28.0, 7.0, 28.5, 7.0), (28.5, 7.0, 28.5, 2.8), (28.5, 2.8, xc, yc),
          (13.4, 5.3, 13.4, 4.2), (13.4, 4.2, _op("C17R")[0], 4.2), (_op("C17R")[0], 4.2, *_op("C17R"))]
    H.append(("Carros: puestos 12 a 17, depósito y calidad (banda sur)",
              [(25.6, Y_PP), (25.6, 18.4), (13.4, 18.4), (13.4, 5.3)], br))
    # oficinas: del pasillo de oficinas a la banda sur
    H.append(("Oficinas (MT, PÑL, QR, Q, PCP, SUP)", [(0.3, 12.2), (13.4, 12.2)], []))
    return H


# ============================================================ LOCALES
# Servicios SV (x -18..0, y 19..35): sin administración (pasa al este) y sin el pasillo del comedor.
LOCALES = [
    Sector("SV-LU", "Utilitarios de limpieza", R(-17.9, 19.1, -15.2, 22.9), "SERV", "común",
           "Pileta de lavado, carros, máquina de piso y artículos de limpieza"),
    Sector("SV-HY", "Higiene y seguridad, medicina laboral, primeros auxilios y EPP", R(-15.0, 19.1, -10.6, 22.9),
           "SERV", "común", "Una sola persona: escritorio, camilla, botiquín y lavabo; entrega de EPP por ventanilla "
           "al pasillo limpio; salida directa al exterior para ambulancia (SV-3)"),
    Sector("SV-AC", "Sanitario accesible con ducha", R(-10.4, 19.1, -6.8, 22.9), "SERV", "común",
           "Inodoro con 0,80 m libre lateral, lavabo, ducha a nivel con asiento rebatible y barras; círculo Ø 1,50 m "
           "(Ley 24.314, Dec. 914/97); abre directo al pasillo limpio"),
    Sector("SV-HA", "Hall, recepción y fichado", R(-6.6, 19.1, -0.1, 22.9), "SERV", "común",
           "Reloj biométrico y tablero de novedades al paso (las visitas de administración entran por el este)"),
    Sector("SV-PL", "Pasillo limpio a la planta (PP-1)", R(-17.9, 23.0, -0.1, 24.5), "CIRC", "común"),
    Sector("SV-VH", "Vestuario hombres (42 lockers)", R(-17.9, 24.6, -10.9, 28.2), "SERV", "común",
           "1 locker por empleado: 2 bloques de 7 columnas × 3 filas = 42 (39 en 2035 sin recargas) y bancos"),
    Sector("SV-DH", "Duchas hombres", R(-17.9, 28.4, -15.1, 34.9), "SERV", "común",
           "3 duchas sobre la misma pared (art. 49: 40 H en el turno mañana con choferes piden 2), banco y percheros; "
           "separadas de inodoros y mingitorios"),
    Sector("SV-SH", "Inodoros, mingitorios y lavabos hombres", R(-14.9, 28.4, -10.9, 34.9), "SERV", "común",
           "3 inodoros en la pared norte, 6 mingitorios en la pared este y 6 lavabos en la pared oeste"),
    Sector("SV-VM", "Vestuario mujeres (9 lockers)", R(-10.7, 24.6, -7.1, 29.0), "SERV", "común",
           "1 bloque de 3 columnas × 3 filas = 9 lockers (7 en 2035) y banco"),
    Sector("SV-SM", "Inodoro y lavabo mujeres", R(-10.7, 29.2, -9.0, 34.9), "SERV", "común",
           "Art. 49: 6 M por turno -> 1 inodoro y 1 lavabo"),
    Sector("SV-DM", "Ducha mujeres", R(-8.8, 29.2, -7.1, 34.9), "SERV", "común", "1 ducha, separada del inodoro"),
    Sector("SV-CM", "Comedor (30 plazas) y office", R(-6.9, 24.6, -0.1, 34.9), "SERV", "común",
           "5 mesas de 6 lejos de la puerta; office con bacha y lavamanos sobre la misma pared; 2 tandas de 30 min; "
           "abre directo al pasillo limpio y tiene su salida de emergencia SV-2"),
    # sanitarios de planta: junto a terminación, embalaje, pintura y PT (entran desde la calle AT2)
    Sector("SN-H", "Sanitarios hombres (planta)", R(64.0, 16.0, 70.2, 18.8), "SERV", "común",
           "2 inodoros y 2 mingitorios (pared norte) y 2 lavabos (pared este)"),
    Sector("SN-M", "Sanitario mujeres (planta)", R(61.0, 16.0, 63.8, 18.8), "SERV", "común", "1 inodoro y lavabo"),
    # administración (lado este, ex LB-1): visitas por la fachada este (AD-1), personal por PO-6
    Sector("AD-OF", "Administración: compras, ventas y RRHH", R(76.3, 28.6, 87.5, 33.3), "SERV", "común",
           "4 puestos (compras 1, ventas 2, RRHH 1) y archivo; puerta a PO-6 para ir a la planta"),
    Sector("AD-HA", "Hall y recepción de visitas", R(79.1, 24.7, 87.5, 28.4), "SERV", "común",
           "Entrada por la fachada este (AD-1), lejos de P1 y del alero de MP"),
    Sector("AD-SA", "Sanitario accesible de administración", R(76.3, 24.7, 78.9, 28.4), "SERV", "común",
           "Inodoro accesible y lavabo (Ley 24.314); lo usan las visitas y el personal de administración"),
]

PUERTAS_ANEXOS = [
    ("SV-1", (-4.2, 19.0), (-2.6, 19.0), "peatonal", "Ingreso de personal (camino peatonal desde G4)"),
    ("SV-2", (-6.8, 35.0), (-5.8, 35.0), "peatonal", "Salida de emergencia del comedor"),
    ("SV-3", (-14.6, 19.0), (-13.6, 19.0), "peatonal", "Higiene y seguridad: salida a ambulancia"),
    # sala técnica, jaula de gases y construcciones del terreno: ninguna sin puerta
    ("ST-1", (36.0, 45.2), (36.0, 46.2), "peatonal", "Sala técnica: electricista desde el patio norte"),
    ("ST-2", (38.0, 50.0), (41.0, 50.0), "porton", "Sala técnica: portón del transformador"),
    ("JG-1", (49.0, 47.3), (52.0, 47.3), "porton", "Jaula de gases: cambio de packs desde el patio norte"),
    ("MT-1", (-38.6, -24.0), (-37.6, -24.0), "peatonal", "Celda de media tensión"),
    ("GAR-1", (-26.5, -57.0), (-25.6, -57.0), "peatonal", "Garita"),
    ("RI-1", (100.0, 35.0), (100.0, 36.2), "peatonal", "Sala de bombas contra incendio"),
    ("ERM-1", (91.6, 5.0), (91.6, 6.0), "peatonal", "Gabinete de regulación de gas"),
    ("ERP-1", (126.5, -58.5), (126.5, -57.5), "peatonal", "Gabinete de la estación reductora"),
    ("PTE-1", (69.0, -19.0), (72.0, -19.0), "porton", "Planta de efluentes: acceso del camión atmosférico"),
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
    # ---- SV-AC sanitario accesible con ducha (a nivel, asiento rebatible)
    Mb("inodoro_acc", R(-10.35, 19.2, -8.7, 21.0), "N"), Mb("ducha_acc", R(-8.3, 19.15, -6.85, 20.55), "N"),
    Mb("lavabos", R(-7.4, 22.3, -6.85, 22.85), "S", 1),
    # ---- SV-HA hall, recepción y fichado
    Mb("mostrador", R(-2.0, 20.6, -0.85, 22.0), "O"), Mb("reloj", R(-6.4, 22.55, -6.0, 22.85), "S"),
    Mb("sillas", R(-6.45, 19.4, -5.95, 20.9), "E", 3),
    # ---- SV-VH vestuario hombres: 2 bloques de lockers de 10 columnas × 3 filas = 60
    Mb("lockers", R(-17.88, 24.9, -17.38, 27.0), "E", 7), Mb("lockers", R(-11.42, 24.9, -10.92, 27.0), "O", 7),
    Mb("banco_vest", R(-16.6, 25.2, -16.2, 27.4), "E"), Mb("banco_vest", R(-12.6, 25.2, -12.2, 27.4), "O"),
    # ---- SV-DH duchas hombres (pared oeste)
    Mb("duchas", R(-17.85, 31.0, -16.95, 34.85), "E", 3), Mb("banco_vest", R(-15.9, 29.2, -15.5, 33.6), "O"),
    # ---- SV-SH inodoros (norte), mingitorios (este) y lavabos (oeste)
    Mb("inodoro", R(-14.85, 33.4, -11.95, 34.85), "S", 3), Mb("mingitorios", R(-11.35, 28.9, -10.95, 32.5), "O", 6),
    Mb("lavabos", R(-14.85, 28.7, -14.35, 31.7), "E", 6),
    # ---- SV-VM y sanitarios de mujeres
    Mb("lockers", R(-10.68, 25.0, -10.18, 25.9), "E", 3), Mb("banco_vest", R(-9.0, 25.4, -8.6, 27.6), "O"),
    Mb("inodoro", R(-10.65, 33.4, -9.05, 34.85), "S", 1), Mb("lavabos", R(-10.65, 30.0, -10.15, 30.8), "E", 1),
    Mb("duchas", R(-8.75, 33.95, -7.85, 34.85), "S", 1), Mb("banco_vest", R(-7.55, 30.6, -7.15, 31.5), "O"),
    # ---- SV-CM comedor: office junto a la pared este (bacha y lavamanos en la misma pared) y mesas al fondo
    Mb("mesada", R(-3.6, 24.65, -0.15, 25.25), "N", 2), Mb("lavabos", R(-0.65, 25.4, -0.15, 26.6), "O", 2),
    Mb("heladera", R(-0.85, 26.8, -0.15, 27.5), "O"), Mb("dispenser", R(-0.55, 27.7, -0.15, 28.1), "O"),
    *[Mb("mesa", R(x0, y0, x0 + 1.7, y0 + 2.0), "S", 6) for x0, y0 in
      ((-4.9, 28.2), (-2.3, 28.2), (-4.9, 30.6), (-2.3, 30.6), (-4.9, 32.8))],
    # ---- MT taller de mantenimiento (preventivo)
    Mb("banco_trabajo", R(0.5, 13.05, 2.7, 13.8), "N"), Mb("agujereadora", R(2.9, 13.05, 3.7, 13.8), "N"),
    Mb("torno", R(0.4, 14.4, 1.35, 16.7), "E"), Mb("estanteria", R(6.0, 13.2, 6.5, 14.7), "O"),
    Mb("soldadora", R(5.4, 16.0, 6.4, 16.6), "O"), Mb("escritorio", R(4.7, 17.4, 6.45, 18.7), "S"),
    Mb("contenedor", R(1.2, 17.6, 2.5, 18.5), "N"),
    # ---- PÑL pañol de mantenimiento y de línea (pegado al taller, ventanilla al pasillo de oficinas)
    Mb("estanteria", R(6.95, 16.2, 7.45, 18.6), "E"), Mb("estanteria", R(9.25, 13.9, 9.75, 18.6), "O"),
    Mb("estanteria", R(7.6, 18.2, 9.1, 18.7), "S"), Mb("ventanilla", R(8.55, 12.95, 9.55, 13.3), "S"),
    Mb("escritorio", R(7.7, 16.2, 9.1, 17.5), "N"),
    # ---- QR cuarentena de producto y muestras retenidas
    Mb("jaula", R(10.15, 13.95, 12.45, 18.65), "S"), Mb("pallets", R(10.3, 17.0, 12.3, 18.5), "S", 1),
    Mb("estanteria", R(11.95, 14.1, 12.4, 16.6), "O"), Mb("cilindros_piso", R(10.3, 14.2, 11.8, 16.6), "S", 0),
    # ---- Q laboratorio de calidad (+ archivo de legajos)
    Mb("marmol", R(1.4, 5.2, 3.4, 6.2), "N"), Mb("mesa_lab", R(3.6, 5.15, 5.45, 5.85), "N"),
    Mb("camara", R(4.3, 6.2, 5.45, 7.2), "O"), Mb("camara", R(4.6, 7.4, 5.45, 8.4), "O"),
    Mb("balanza_lab", R(1.2, 8.8, 1.9, 9.4), "E"), Mb("mesa_lab", R(4.8, 8.8, 5.45, 10.4), "O"),
    Mb("escritorio", R(3.0, 9.9, 4.6, 11.25), "S"), Mb("archivo", R(1.2, 10.75, 1.95, 11.25), "S", 2),
    # ---- PCP planificación y SUP supervisor
    Mb("escritorio", R(5.95, 5.15, 7.75, 6.45), "N"), Mb("escritorio", R(5.95, 7.0, 7.75, 8.3), "N"),
    Mb("pizarra", R(8.45, 6.0, 8.55, 8.2), "O"), Mb("archivo", R(7.9, 8.6, 8.5, 9.9), "O", 2),
    Mb("escritorio", R(10.5, 5.15, 12.3, 6.45), "N"), Mb("archivo", R(8.95, 5.15, 9.55, 6.4), "E", 2),
    Mb("sillas", R(11.9, 7.2, 12.4, 8.5), "O", 2),
    # ---- administración (lado este)
    *[Mb("escritorio", R(77.0 + i * 2.2, 31.9, 78.8 + i * 2.2, 33.2), "S") for i in range(4)],
    Mb("archivo", R(85.8, 32.75, 87.4, 33.25), "S", 3), Mb("pizarra", R(76.35, 30.6, 76.45, 32.0), "E"),
    Mb("mostrador", R(82.0, 26.8, 83.3, 28.2), "O"), Mb("sillas", R(80.2, 24.8, 82.6, 25.3), "N", 4),
    Mb("inodoro_acc", R(76.4, 25.6, 78.1, 28.3), "E"), Mb("lavabos", R(76.4, 24.8, 77.2, 25.3), "N", 1),
    # ---- SC compresores y colectores: tablero
    Mb("tablero_el", R(69.6, 42.95, 71.2, 43.55), "S", 2),
    # ---- ST-I tableros de la línea este y compresor de la cabina
    Mb("tablero_el", R(83.0, 42.95, 87.4, 43.55), "S", 4), Mb("compresor", R(79.6, 41.4, 82.6, 42.8), "S"),
    # ---- almacén de MP: cuarentena y retenidos a piso; gasoil del autoelevador
    Mb("pallets", R(9.2, 26.5, 11.5, 32.4), "O", 0), Mb("pallets", R(9.2, 34.9, 11.5, 37.1), "O", 0),
    Mb("inflamables", R(0.45, 24.7, 1.55, 25.8), "E"),
    # ---- embalaje: pila de pallets vacíos, stock de cajas y pallets en armado
    Mb("pallets", R(60.0, 7.2, 61.2, 8.2), "E", 0), Mb("pallets", R(61.9, 7.6, 63.1, 8.6), "E", 0),
    Mb("pallets", R(66.8, 5.0, 68.0, 6.0), "N", 0), Mb("pallets", R(70.8, 5.0, 72.0, 6.0), "N", 1),
    # ---- depósito de polvo: big bags a piso de la tanda
    Mb("bigbags", R(56.6, 5.6, 58.0, 7.0), "S", 1),
    # ---- muelle: rampa niveladora y combustible del autoelevador junto a la calle del muelle
    Mb("rampa", R(50.15, 0.35, 53.15, 2.35), "S"),
    # ---- carros: estanterías del puesto 13 y mesa de medición del 17
    Mb("estanteria", R(28.6, 0.45, 30.3, 0.95), "N"), Mb("estanteria", R(28.6, 1.1, 30.3, 1.6), "N"),
    Mb("estanteria", R(28.6, 1.75, 30.3, 2.25), "N"),
    Mb("mesa_lab", R(14.2, 3.9, 15.7, 4.6), "N"),
    # ---- sanitarios de planta
    Mb("inodoro", R(64.1, 17.35, 66.4, 18.7), "S", 2), Mb("mingitorios", R(66.8, 18.3, 68.0, 18.7), "S", 2),
    Mb("lavabos", R(69.6, 16.4, 70.1, 17.6), "O", 2),
    Mb("inodoro", R(61.1, 17.35, 62.3, 18.7), "S", 1), Mb("lavabos", R(62.8, 18.2, 63.4, 18.7), "S", 1),
    # ---- DL ducha de emergencia y lavaojos
    Mb("ducha_emergencia", R(70.8, 17.4, 72.0, 18.6), "S"), Mb("lavaojos", R(71.7, 15.9, 72.3, 16.5), "O"),
]

# puertas interiores de una hoja: (x, y, ancho, muro 'h'/'v', abre +1/-1)
PUERTAS_INT = [
    # bloque de servicios
    (-16.1, 22.9, 0.8, "h", -1), (-11.5, 22.9, 0.8, "h", -1), (-9.6, 22.9, 0.9, "h", -1), (-5.4, 22.9, 0.9, "h", -1),
    (-14.6, 24.6, 0.9, "h", 1), (-8.4, 24.6, 0.8, "h", 1), (-16.6, 28.3, 0.8, "h", 1), (-12.4, 28.3, 0.8, "h", 1),
    (-10.2, 29.1, 0.7, "h", 1), (-8.4, 29.1, 0.7, "h", 1), (-6.6, 24.6, 0.9, "h", 1),
    # sanitarios de planta (a la calle AT2)
    (66.6, 16.0, 0.8, "h", 1), (63.0, 16.0, 0.8, "h", 1),
    # administración
    (76.3, 29.0, 0.9, "v", 1), (84.0, 28.5, 0.9, "h", 1), (79.0, 25.0, 0.9, "v", 1),
]

# ============================================================ LOCALES CERRADOS DENTRO DE LA NAVE
# tabique en todo el perímetro (salvo donde coincide con el cerramiento de la nave) y sus aberturas:
# (lado, desde, hasta, tipo): puerta (hoja 0,90), porton (corredizo), cortina (lamas de PVC, pasa material),
# ventanilla (mostrador, no es paso), ventana (vidrio a la planta, no es paso)
CERRADOS = {
    "MT": [("N", 2.6, 4.6, "porton"), ("S", 4.8, 5.7, "puerta"), ("E", 15.0, 15.9, "puerta")],
    "PÑL": [("S", 7.3, 8.2, "puerta"), ("S", 8.5, 9.6, "ventanilla"), ("O", 15.0, 15.9, "puerta")],
    "QR": [("S", 10.9, 11.8, "puerta")],
    "OF-C": [("E", 11.7, 12.7, "puerta")],
    "Q": [("N", 2.0, 2.9, "puerta")],
    "PCP": [("N", 6.6, 7.5, "puerta")],
    "SUP": [("N", 9.4, 10.3, "puerta"), ("E", 6.0, 10.6, "ventana")],
    "C-17": [("N", 12.9, 13.9, "puerta"), ("E", 1.2, 3.6, "puerta")],
    "C-14": [("O", 1.2, 3.6, "puerta"), ("E", 0.5, 1.7, "puerta")],
    "ST-I": [("S", 80.0, 81.8, "porton")],
    "SC": [("S", 56.0, 56.9, "puerta"), ("S", 52.2, 54.0, "porton")],
    "DP": [("S", 56.4, 58.4, "porton"), ("N", 55.8, 57.4, "porton"), ("O", 5.0, 7.0, "porton")],
}

# ============================================================ PROTECCIÓN CONTRA INCENDIO Y SEÑALIZACIÓN
# bocas de incendio equipadas (manguera 25 m + chorro 5 m): cubren toda la nave desde las calles
BIE = [(8.0, 23.0), (30.0, 23.0), (52.0, 23.0), (73.0, 23.0), (30.0, 39.8), (55.0, 39.8), (80.0, 39.8),
       (13.4, 9.0), (36.0, 18.1), (54.3, 12.0), (80.0, 2.0)]
# pulsadores manuales de alarma junto a cada salida y sirena con luz estroboscópica
PULSADORES = [(5.35, 43.3), (47.0, 43.3), (78.1, 43.3), (87.3, 39.8), (87.3, 34.1), (86.5, 0.7), (71.1, 0.7),
              (15.0, 0.7), (0.7, 7.5), (0.7, 18.1), (0.7, 23.8), (0.7, 12.2), (87.3, 26.6), (51.6, 2.6)]


def _senales():
    """Señalética (IRAM 10005-1 colores y formas; Dec. 351/79): (tipo, código, x, y, texto).
    tipo: obl (azul, círculo), adv (amarilla, triángulo), pro (roja, círculo con barra), sal (verde, rectángulo),
    inc (roja, cuadrado)."""
    S = []
    for p in PUERTAS:
        if p.tipo in ("emergencia", "peatonal") or p.cod in ("P1", "P3"):
            m = (p.a + p.b) / 2
            xy = {"N": (m, NAVE_A - 0.9), "S": (m, 0.9), "O": (0.9, m), "E": (NAVE_L - 0.9, m)}[p.muro]
            S.append(("sal", "SALIDA", *xy, "Salida"))
    for x in range(6, 72, 12):
        S.append(("sal", "->", float(x), 21.1, "Recorrido de evacuación"))
    auditiva = ("M04", "M08", "B08", "M16", "C01", "C81", "B10")
    careta = ("B03", "A06", "B06", "M11", "C02s", "C04", "C05", "C06", "C08", "B10")
    respirador = ("P04", "T01", "BB1", "T02", "BB2", "B08", "C17R")
    for e in EQUIPOS:
        x, y = e.rect.x1 + 0.35, e.rect.y1 + 0.35
        if e.cod in auditiva:
            S.append(("obl", "OÍDOS", x, y, "Protección auditiva"))
        if e.cod in careta:
            S.append(("obl", "CARETA", x, y - 0.75 if e.cod in auditiva else y, "Careta fotosensible y guantes"))
        if e.cod in respirador:
            S.append(("obl", "RESP", e.rect.x0 - 0.35, y, "Respirador P2"))
    S.append(("obl", "CALZADO", 2.6, 24.0, "Calzado de seguridad y ropa de trabajo (ingreso a planta)"))
    for x, y in ((5.3, 27.4), (15.6, 24.9), (22.1, 24.9), (51.8, 17.0), (34.0, 21.1), (60.0, 21.1), (40.0, 4.0)):
        S.append(("adv", "AUTOELEV", x, y, "Circulación de autoelevadores"))
    for x, y in ((83.4, 42.0), (39.0, 44.6), (36.3, 47.8)):
        S.append(("adv", "ELECT", x, y, "Riesgo eléctrico"))
    for x, y in ((84.0, 19.6), (85.5, 16.0)):
        S.append(("adv", "CALOR", x, y, "Superficie caliente (horno)"))
    for x, y in ((50.6, 43.3), (59.6, 7.4), (29.0, 9.6)):
        S.append(("adv", "INFLAM", x, y, "Gases a presión"))
    for x, y in ((31.6, 40.9), (45.0, 31.6), (65.4, 37.2)):
        S.append(("adv", "ATRAP", x, y, "Riesgo de atrapamiento / cargas suspendidas"))
    for x, y in ((75.0, 23.0), (59.0, 8.0), (13.0, 4.2), (27.5, 6.6)):
        S.append(("pro", "FUMAR", x, y, "Prohibido fumar y llama abierta"))
    for x, y in ((5.3, 27.8), (15.6, 25.2), (22.1, 25.2), (51.8, 17.5), (40.0, 5.5)):
        S.append(("pro", "PEATON", x, y, "Prohibido el paso de peatones (calle de autoelevador)"))
    for x, y in ((-12.4, 22.4), (71.4, 15.9), (3.0, 12.2), (39.0, 25.2)):
        S.append(("sal", "+", x, y, "Primeros auxilios / lavaojos"))
    S.append(("sal", "REUNIÓN", 28.0, -30.0, "Punto de reunión"))
    S.append(("sal", "PLANO", 0.9, 24.0, "Plano de evacuación (ingreso PP-1)"))
    return S


SENALES = _senales()

# función de cada portón, rotulada en todos los planos (qué entra o sale, nunca un código suelto)
USO_CORTO = {
    "P1": "MP (toda): chapa, fleje, caños de 6 m, barras, casquetes, insumos, polvo, pintura, embalaje y revendidos; "
          "sale scrap",
    "P3": "Muelle de despacho: PT, cilindros y carros; vuelven los carros pintados",
    "PP-1": "Personal", "PG": "Jaula exterior de gases", "OF-1": "Oficinas", "AD-1": "Administración",
    "PE-1": "Patio de ensayos",
}

# fondos de calle admitidos, con su motivo (el resto remata en otra calle, en una puerta o en su destino)
FONDOS = {
    ("PC", "O"): "Cabecera oeste del pasillo central: portón de mantenimiento MT, carros de abastecimiento AL-CA y "
                 "estacionamiento y combustible del autoelevador (AL-1N); el autoelevador entra y sale marcha atrás",
}

# cruces de flujos que no se pueden evitar, declarados con su motivo: los dos flujos son a mano, de baja frecuencia,
# y se cruzan dentro de una senda peatonal señalizada (el verificador comprueba que el cruce caiga en esa senda)
CRUCES_DECLARADOS = [
    ("Barras y caños de carros", "Lote aprobado a pintura", "X19",
     "Barras de 6 m a mano (8,6 por día, W-CAR 8.1) contra carros rodando al muelle (20 por día): el cantiléver de "
     "MP y el puesto 8.1 quedan a los dos lados del camino de los carros al muelle; una barra de 6 m no puede girar "
     "por PO-1 (1,4 m) para rodearlo"),
    ("Casquetes y cuplas", "Cuerpos grabados", "X11",
     "Carro de casquetes (2 viajes por día, W-CAR) contra el EFE 600 o la mesa móvil (20 cuerpos por día): los dos "
     "usan PO-1, uno a lo largo y otro de lado a lado; la otra vía (PO-3) cruzaría 3 flujos de la línea de manuales"),
]

# ============================================================ ESPACIOS LIBRES: ninguno en la versión 9
LIBRES = []

# ============================================================ IMPLANTACIÓN
LM_Y = TERRENO[1]
RETIRO_FRENTE = 10.0

EXTERIOR = [
    ("PL-N", "Alero de descarga de MP (semi 18,6 m y chasis); franja de descarga de 15 × 5 m (W-CAR)",
     R(-1.0, 44.4, 31.0, 56.0), "playa"),
    ("VQ-N", "Volquete de scrap 6 m³ junto a P1", R(-3.8, 44.8, -1.2, 47.6), "volquete"),
    ("JG", "Jaula exterior de gases (15,75 m², v5): pack de 12 cilindros de Arcal 21 y pack de 12 de N₂ con manifold; "
     "cañería a los puestos de soldadura y de presurización", R(48.0, 44.3, 53.25, 47.3), "gas"),
    ("PM", "Playa de maniobra del muelle P3 (semi 18,6 m)", R(40.0, -26.0, 62.0, 0.0), "playa"),
    ("PE", "Patio de ensayos de carros (W-CAR 17): circuito de remolque de 1 km en vueltas, plataforma de caída y pared "
     "de choque; el autoelevador llega desde la playa del muelle", R(4.0, -8.6, 40.0, -0.4), "playa"),
    ("PE-C", "Plataforma de caída de 20 cm (1,5 × 1,5 m)", R(30.0, -3.0, 31.5, -1.5), "obra"),
    ("PE-P", "Pared de choque de 60 cm (2,0 × 0,3 m)", R(33.0, -2.2, 35.0, -1.9), "obra"),
    ("ERM", "Estación de regulación y medición de gas natural (horno y secadoras)", R(88.6, 4.0, 91.6, 7.0),
     "gas"),
    ("RI", "Reserva de agua contra incendio y bombas", R(100.0, 34.0, 110.0, 44.0), "incendio"),
    ("AMP", "Reserva de ampliación (nave hacia el este)", R(92.0, -8.0, 114.0, 21.0), "reserva"),
    ("PTE", "Tratamiento de efluentes líquidos", R(64.0, -27.0, 76.0, -19.0), "efluentes"),
    ("EST", "Estacionamiento de personal y visitas (38 + 2 accesibles)", R(-12.0, -50.0, 30.0, -28.0), "estac"),
    ("GAR", "Garita: control de camiones (G1), autos (G2) y peatones (G4); CCTV", R(-28.5, -61.5, -23.5, -57.0),
     "garita"),
    ("BAL", "Báscula de camiones de 18 m (entrada)", R(-35.5, -50.0, -29.5, -32.0), "balanza"),
    ("PR", "Punto de reunión (evacuación)", R(-27.5, -30.0, -21.5, -24.0), "reunion"),
    ("MT", "Celda de medición de media tensión", R(-39.6, -30.0, -36.4, -24.0), "elec"),
    ("ERP", "Estación reductora de gas", R(126.5, -60.0, 129.5, -56.0), "gas"),
]
# circuito de remolque del patio de ensayos (W-CAR 17: 1 km en vueltas, unos 6 minutos a 10 km/h)
CIRCUITO = [(7.0, -7.8), (37.0, -7.8), (37.0, -3.8), (7.0, -3.8), (7.0, -7.8)]
# jaula exterior de gases (W-MAN): pack de 12 cilindros en uso y otro de reserva por gas, con manifold de conmutación
JAULA_GASES = [("Arcal 21: pack en uso y de reserva", R(48.3, 46.0, 50.5, 46.9)),
               ("N₂: pack en uso y de reserva", R(50.8, 46.0, 53.0, 46.9))]
MANIFOLD_GASES = [(48.3, 45.6), (53.0, 45.6)]
CALLES = [R(-36.0, -62.0, -29.0, 63.0), R(-36.0, 56.5, 126.0, 63.0), R(119.0, -62.0, 126.0, 63.0),
          R(30.0, -16.0, 119.0, -9.0)]
PORTONES_TERRENO = [
    ("G1", -36.0, -29.0, "Camiones: entran (báscula y garita)"),
    ("G4", -21.0, -18.0, "Peatones"),
    ("G2", -12.0, -6.0, "Autos del personal y de las visitas"),
    ("G3", 119.0, 126.0, "Camiones: salen"),
]
CAMINO_PEATONAL = [(-19.5, -62.0), (-19.5, 16.5), (-3.4, 16.5), (-3.4, 19.0)]
# ramales del camino peatonal: a la entrada de oficinas (OF-1) y a la entrada de visitas de administración (AD-1)
CAMINO_OFICINAS = [(-3.4, 16.5), (-3.4, 12.2), (0.0, 12.2)]
CAMINO_ADMIN = [(-19.5, -27.4), (92.6, -27.4), (92.6, 26.6), (88.0, 26.6)]

# ============================================================ EFLUENTES
EFLUENTES = [
    Flujo("EFL-L", [(48.7, 35.6), (48.7, 34.9), (47.0, 34.9), (47.0, 37.6), (47.6, 37.6)],
          "Agua de PH a la cámara de decantación"),
    Flujo("EFL-L", [(66.4, 11.6), (66.4, 12.9), (73.6, 12.9), (73.6, 34.9), (50.2, 34.9), (50.2, 37.6)],
          "Ensayo de pérdidas a la misma cámara (cañería enterrada)"),
    Flujo("EFL-L", [(50.2, 38.8), (50.2, 39.0), (52.8, 39.0), (52.8, 34.8), (61.0, 34.8), (61.0, 0.6),
                    (70.0, -19.0)], "Cámara de decantación a la planta de efluentes"),
    Flujo("EFL-L", [(59.3, 29.06), (59.3, 34.6), (51.0, 34.6), (51.0, 37.6)],
          "Purga del tanque de la PH de carros a la cámara de decantación"),
    Flujo("EFL-L", [(70.0, -27.0), (70.0, -62.0)], "Vuelco a colectora (previa autorización)"),
]

EMISIONES = [
    (43.6, 41.9, "Humos de soldadura de cuellos"), (37.7, 31.5, "Humos de soldadura longitudinal"),
    (41.4, 36.3, "Humos de soldadura circunferencial"), (43.8, 36.3, "Humos de soldadura circunferencial"),
    (48.8, 33.0, "Humos de soldadura de carros"), (58.5, 31.6, "Humos de soldadura de carros"),
    (70.4, 32.2, "Humos de soldadura de carros"), (71.2, 26.2, "Humos de soldadura de carros"),
    (67.1, 38.1, "Colector de la granalladora"), (83.8, 19.4, "Chimenea del horno"), (81.1, 12.4, "Ciclones de la cabina"),
    (56.3, 11.1, "Extracción de la carga de polvo"), (29.1, 6.0, "Extracción de la carga de carros"),
    (25.75, 31.0, "Humos de corte láser"), (57.0, 36.1, "Chimenea secadoras"), (74.5, 43.0, "Humos de corrección"),
    (0.95, 1.5, "Colector del recinto de descarga de carros"),
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
    (13.1, 18.1, "autoelevador de MP: calle de chapa A2"),
    (19.6, 24.6, "autoelevador de MP: calle de carga A3"),
    (29.9, 31.4, "autoelevador retira el contenedor de la guillotina"),
    (25.0, 26.2, "personal a la banda sur: oficina, carros y calidad (PO-K)"),
    (36.8, 38.2, "personal a la línea principal (PO-1)"),
    (51.0, 53.0, "personal y carros: despacho a pintura y del muelle (calle T)"),
    (53.6, 55.0, "personal a terminación y PT (AC)"),
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
