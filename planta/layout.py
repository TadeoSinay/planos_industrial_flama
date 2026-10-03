"""Modelo del layout de la planta FLAMA S.A. al año 10 (2035) - versión 3: línea convergente paso a paso.

Medidas en METROS, origen en el eje A-1 (esquina SO, cara interior de columnas), X al este, Y al norte.
Calle al sur. Fuente única de los planos (DIR, operaciones, materiales, formal) y de la memoria de cálculo.

Concepto (diagrama de bloques de FLAMA)
---------------------------------------
* Nave 88 × 44 m (11 módulos de 8 m; dos luces de 19,4 y 24,6 m, columnas centrales en el eje B).
* Pasillo central E-O (autoelevador doble sentido + senda peatonal) entre la banda norte y la banda sur;
  termina en la columna este (pintura), que une las dos bandas: el recorrido es una U.
* Banda norte: almacén de MP al oeste (tubos y flejes / camión / chapa) y una LÍNEA QUE CONVERGE:
  - fila sur:   chapa -> 1 guillotina -> 2 numerado -> 3 cilindrado -> 4 soldadura longitudinal (sube)
  - fila media: tubo -> 5 corte láser (1 kg) (sube)
  - fila central: fleje -> 6 desbobinado + embutido -> fondos al encastre; cúpulas -> 7 prep. de cuello
                  -> 8 soldadura de cuello -> a la soldadura circunferencial
  - línea principal: 9 encastre -> 10 bordoneado -> 11 soldadura circ. -> 12 PH -> 13 secado
                  -> 14 granallado -> 15 detección -> (16 corrección) -> 17 pintura
* Columna este: pintura en lazo (carga, pretratamiento, secado, cabina, polimerizado, enfriamiento, descarga).
* Banda sur (de este a oeste): 18-24 terminación y almacén de cilindros -> PT y muelles -> carros
  (C1-C9, en U) -> recargas (R).
* Entre cada paso hay un pulmón (PU) con carros de cilindros; cada máquina lleva su número de paso.
"""

from dataclasses import dataclass, field

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
    area_req: float = 0.0    # m² requeridos por la memoria (0 = no aplica)


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
    frente: str = ""         # lado del operario: S, N, E, O
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
    cat: str                 # MP, SE, PT, SCRAP, EFL-L, EFL-G, PER
    pts: list
    rot: str = ""            # rótulo
    seccion: str = ""


@dataclass
class Pasillo:
    cod: str
    rect: R
    tipo: str                # PM (materiales/autoelevador), PP (personal), PO (operarios), SE (carros SE)
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
PASILLOS = [
    Pasillo("PC", R(2.0, 19.2, 74.6, 23.0), "PM", 3.8,
            "Pasillo central: autoelevador doble sentido (2 × 1,25 m + 3 × 0,40 m de huelgo); en el extremo oeste "
            "está el armario de nafta del autoelevador de MP y dobla a A1 por el cruce marcado de la senda"),
    Pasillo("PP", R(0.3, 23.2, 74.6, 24.4), "PP", 1.2,
            "Senda peatonal separada del carril de autoelevador por una defensa con aberturas en las sendas"),
    Pasillo("AN", R(3.0, 38.6, 12.7, 43.6), "PM", 5.0,
            "Cabecera del almacén de MP frente a P1 (7,20 m): el autoelevador entra con el atado de caños de 6 m "
            "atravesado y lo apoya en el cantiléver; carga la jaula de gases y gira a A2"),
    Pasillo("A2", R(9.1, 24.4, 12.7, 38.6), "PM", 3.6,
            "Calle del autoelevador de MP: hojas (oeste) -> mesa elevadora de la guillotina y desbobinador (este); "
            "por acá baja el carro porta-tubos a la calle de los láseres"),
    Pasillo("A1", R(2.0, 24.4, 5.6, 37.0), "PM", 3.6,
            "Calle de rack desde el pasillo central: flejes (este), hojas de bajo consumo, alambre MAG y cuellos "
            "(oeste); termina en el respaldo del cantiléver"),
    Pasillo("PO-1", R(39.4, 24.4, 41.0, 34.4), "PO", 1.6, "Calle de operarios y carros de pulmón (N1 -> N4); "
            "ventanilla del pañol"),
    Pasillo("PO-1N", R(39.85, 34.4, 40.75, 39.15), "PO", 0.9, "Paso de operarios entre encastre y bordoneado"),
    Pasillo("PO-2", R(30.0, 33.3, 84.6, 34.4), "PO", 1.1,
            "Calle de carros de la línea principal: empieza a 1,0 m del frente de las máquinas (espalda libre)"),
    Pasillo("PO-5", R(68.6, 24.4, 70.0, 33.3), "PO", 1.4,
            "Calle de la senda peatonal a la línea este (granallado, defectos) sin atravesar locales"),
    Pasillo("PO-3", R(12.7, 39.15, 41.0, 40.15), "PO", 1.0,
            "Calle de operarios de cúpulas y cuellos (N3); por acá sale el carro de scrap de la prensa a A2"),
    Pasillo("PO-L", R(12.7, 32.05, 30.4, 33.45), "PO", 1.4,
            "Calle del carro porta-tubos de 6,5 m entre los caballetes: gira desde A2 porque "
            "(3,6^(2/3) + 1,4^(2/3))^(3/2) = 6,8 m > 6,5 m; sale el scrap de los láseres"),
    Pasillo("PO-4", R(41.0, 39.4, 87.6, 40.6), "PO", 1.2,
            "Calle norte: compresores y colectores, granalla; salidas SE-2 a SE-4 y SE-5 en su extremo este"),
    Pasillo("PO-E", R(84.6, 31.4, 87.4, 39.4), "PO", 2.8, "Calle de transpaleta: P4 -> pintura -> granalla (GR); "
            "remate de PO-2"),
    Pasillo("PO-P", R(70.2, 4.6, 71.8, 19.2), "PO", 1.6,
            "Calle este: carros de pintados (descarga -> PU-9) y acceso a los sanitarios de planta"),
    Pasillo("PO-P2", R(71.8, 4.6, 74.6, 6.6), "PO", 2.0, "Salida de la descarga de pintura a la calle este"),
    Pasillo("PO-PI", R(74.6, 0.6, 76.0, 24.4), "PO", 1.4,
            "Calle de operarios de pintura (borde oeste del esquema Electricolor): remate este del pasillo central "
            "y de la senda; une carga, cabina, retoque y descarga con PO-P2 y la salida SE-7"),
    Pasillo("PO-PS", R(76.0, 0.6, 87.1, 2.2), "PO", 1.6, "Paso al sur de la descarga de pintura hasta la salida SE-7"),
    Pasillo("T1", R(35.5, 6.8, 38.8, 19.2), "PM", 3.3,
            "Calle de rack de PT (oeste): pasillo central <-> calle de expedición; columna B-6 fuera de la boca"),
    Pasillo("T2", R(41.2, 6.8, 44.5, 19.2), "PM", 3.3, "Calle de rack de PT (centro): pasillo central <-> expedición"),
    Pasillo("T3", R(45.8, 6.8, 47.7, 19.2), "PM", 1.9,
            "Calle de rack de alta rotación: envolvedora -> RK3 -> expedición (autoelevador de PT)"),
    Pasillo("EX", R(34.2, 2.4, 50.2, 6.8), "PM", 4.4,
            "Calle de expedición: une las 3 calles del rack con el muelle P3, la calle de carros PO-C y la de "
            "terminación AT"),
    Pasillo("PO-C", R(17.8, 5.4, 34.2, 8.0), "PM", 2.6,
            "Calle del autoelevador de carros y recargas: muelle P3 <-> carros al pintor, carga de polvo de carros, "
            "armado y recargas"),
    Pasillo("AT", R(50.2, 1.9, 62.0, 4.2), "PM", 2.3,
            "Calle de abastecimiento de terminación: muelle P3 -> válvulas y manómetros (AL-2) y polvos, agentes y "
            "N₂ al almacén previo a la carga (SP-1)"),
    Pasillo("PO-T", R(53.2, 7.2, 62.0, 8.2), "PO", 1.0, "Calle de operarios de terminación y buffer de válvulas"),
    Pasillo("PO-AC", R(60.6, 8.2, 61.8, 19.2), "PO", 1.2,
            "Calle del pasillo central a terminación a través del almacén de cilindros"),
    Pasillo("RC-P", R(0.5, 5.6, 17.8, 7.0), "PO", 1.4, "Corredor de recargas (sur): remata en la salida SE-10"),
    Pasillo("RC-Q", R(0.5, 11.8, 16.4, 13.2), "PO", 1.4, "Corredor de recargas (centro): remata en la salida SE-11"),
    Pasillo("RC-N", R(16.4, 7.0, 17.8, 19.2), "PO", 1.4, "Conector de recargas al pasillo central"),
]

# sendas peatonales: se calculan al final del módulo en cada cruce de un hilo con un flujo
SENDAS = []

# ============================================================ SECTORES
SECTORES = [
    # ---------------- banda norte: almacén de MP (oeste). Sólo seis rubros: gases de soldadura, hojas,
    # flejes, caños, cuellos y roscas, alambre MAG (más el armario de nafta del autoelevador de MP)
    Sector("AL-GS", "Gases de soldadura Arcal 21: baterías llenas y vacías", R(0.4, 38.8, 2.8, 43.5), "MP", "común",
           "Jaula ventilada contra el muro exterior; 2 baterías de 12 cilindros (llena + en espera); la que está en "
           "uso va al colector de la sala SC"),
    Sector("AL-1T", "Caños de 6 m: cantiléver interior", R(0.4, 37.0, 9.0, 38.6), "MP", "común",
           "12 atados ≤ 600 kg a 3 niveles; se cargan desde AN con el atado atravesado (P1 de 7,20 m)"),
    Sector("AL-1H", "Paquetes de hojas: 4 formatos de alto consumo", R(7.4, 24.8, 9.0, 37.0), "MP", "común",
           "4 posiciones de 1,5 × 3,0 m a 4 alturas = 16 paquetes ≤ 2 t; un formato por posición; FIFO; la más "
           "usada (1,6 × 1000 × 2000) frente a la mesa elevadora", 50.0),
    Sector("AL-1F", "Rollos de fleje", R(5.7, 24.8, 7.2, 36.8), "MP", "común",
           "Porta-flejes de 3 niveles: 8 cunas × 3 = 24 rollos ≤ 1 t (8 anchos); se toman con gancho C"),
    Sector("AL-1L", "Hojas de bajo consumo (carros)", R(0.4, 24.8, 2.0, 28.0), "MP", "común",
           "LAC 4,75 × 1500 × 3000: 1 paquete de ≈ 10 hojas cada 2 meses"),
    Sector("AL-1C", "Cuellos y roscas (cajas)", R(0.4, 28.2, 2.0, 30.6), "MP", "común",
           "Estantería de cajas por medida; salen con la zorra del milk run a la preparación de cuello"),
    Sector("AL-1A", "Alambre MAG", R(0.4, 30.8, 2.0, 34.4), "MP", "común",
           "Rack 1 módulo × 3 niveles = 6 pallets (bobinas de 15 kg y tambores de 250 kg)"),
    Sector("AL-1N", "Nafta e insumos del autoelevador de MP", R(0.4, 19.3, 1.9, 23.0), "AUX", "común",
           "Armario de inflamables (bidones de nafta) y estante de insumos; el autoelevador se estaciona al final "
           "del pasillo central"),
    # ---------------- banda norte: línea convergente
    Sector("N1", "Corte y cuerpo 2,5-10 kg", R(12.8, 24.8, 38.8, 29.5), "PROD", "S2",
           "1 guillotina -> 2 numerado -> 3 cilindrado -> 4 soldadura longitudinal"),
    Sector("N2", "Corte de caño 1 kg", R(12.8, 29.7, 29.4, 35.8), "PROD", "S1",
           "5 corte láser de caño; caños del cantiléver interior en carro porta-tubos por AN, A2 y PO-L"),
    Sector("N3", "Cúpulas, fondos y cuellos", R(12.8, 35.85, 30.0, 43.5), "PROD", "S1 / S2",
           "6 desbobinado + embutido -> 7 preparación de cuello -> 8 soldadura de cuello"),
    Sector("N4", "Unión y prueba hidráulica", R(34.6, 35.0, 66.6, 39.0), "PROD", "S1 / S2",
           "9 encastre -> 10 bordoneado -> 11 soldadura circ. -> 12 PH -> 13 secado"),
    Sector("N5", "Granallado y defectos", R(70.2, 34.8, 87.6, 39.3), "PROD", "S1 / S2",
           "14 granallado -> 15 detección de defectos -> 16 corrección"),
    # ---------------- fila central: mantenimiento, calidad y conducción de la planta (planta baja, sin entrepiso)
    Sector("MT", "Taller de mantenimiento", R(41.2, 24.8, 49.2, 29.4), "AUX", "común",
           "Mantenimiento preventivo: bancos, torno, agujereadora, soldadora móvil; entra la transpaleta desde el "
           "pasillo central; puerta directa al pañol", 30.0),
    Sector("PÑL", "Pañol de mantenimiento y de línea", R(41.2, 29.6, 46.0, 33.2), "AUX", "común",
           "Pegado al taller: repuestos críticos, herramental del preventivo, consumibles de soldadura (toberas, "
           "puntas, discos) contra vale por la ventanilla a PO-1"),
    Sector("Q", "Laboratorio de calidad", R(49.4, 24.8, 56.8, 29.4), "CAL", "común",
           "Metrología, espesor por ultrasonido, adherencia y espesor de pintura, niebla salina, humedad del "
           "polvo; probetas de soldadura (IRAM 3523 / 3550); archivo de legajos de calidad", 31.0),
    Sector("QR", "Cuarentena y muestras retenidas", R(57.0, 24.8, 61.0, 29.4), "CAL", "común",
           "Jaula con llave: lotes rechazados y un cilindro testigo por lote (IRAM 3517 / 3523)", 15.0),
    Sector("SUP", "Supervisor de planta", R(61.2, 24.8, 64.2, 29.4), "AUX", "común",
           "Oficina propia del encargado de turno, con ventana a la línea y al pasillo central"),
    Sector("PCP", "Planificación y control de la producción", R(64.4, 24.8, 68.4, 29.4), "AUX", "común",
           "Separada del supervisor: 2 puestos y tablero de programación con ventana a la línea"),
    Sector("PV", "Carros vacíos: supermercado de retorno", R(46.2, 29.6, 62.0, 33.2), "AUX", "común",
           "Cada carro vuelve vacío a su puesto de carga por PO-1 / PO-2; acá esperan los de reserva y los del "
           "milk run de abastecimiento"),
    # ---------------- franja norte (sobre la calle PO-4)
    Sector("SC", "Compresores y colectores de gases de soldadura", R(48.0, 40.8, 65.6, 43.6), "AUX", "común",
           "Área libre de la v6 más el ex pañol: colector de Arcal 21 y colector de humos en el extremo oeste "
           "(el más cercano a las soldadoras), 2 compresores de tornillo, secador y pulmón al este"),
    Sector("GR", "Granalla de acero y repuestos de la granalladora", R(67.6, 40.8, 76.0, 43.6), "MP", "común",
           "Bolsas de 25 kg en pallets frente a la tolva de la granalladora (a 4 m); entra por P4 con transpaleta"),
    # ---------------- columna este: pintura y servicios de pintura
    Sector("S-P", "Pintura en polvo (esquema Electricolor 22 × 13 m)", R(74.6, 2.3, 87.6, 24.3), "PINT", "S1 / S2",
           "17 carga -> cabina -> polimerizado -> enfriamiento -> descarga"),
    Sector("QP", "Pintura electrostática en polvo", R(80.8, 24.8, 87.6, 31.4), "MP", "S1 / S2",
           "Cajas de 25 kg por color en pallets, < 30 °C; entra por el portón P4; puerta directa a las tolvas", 24.1),
    Sector("ST-I", "Tableros y compresor de la cabina", R(70.2, 24.8, 76.2, 31.4), "AUX", "común",
           "Tablero de la línea este y compresor sin aceite dedicado a la cabina de pintura"),
    # ---------------- banda sur: terminación, almacén previo a la carga y cilindros
    Sector("AL-C", "Almacén de cilindros pintados", R(50.2, 12.4, 69.8, 18.8), "PT", "S1 / S2",
           "Pulmón de pintados antes de la carga de polvo y cilindros vendidos vacíos"),
    Sector("SP-1", "Almacén previo a la carga y carga de polvo", R(62.0, 0.3, 69.8, 12.2), "TERM", "S1 / S2",
           "Polvos (big bags), agentes extintores y baterías de N₂ de presurización; deshumidificador: HR ≤ 70 %, "
           "8 renovaciones por hora, sin estufas (IRAM 3517-2)"),
    Sector("S-T", "Terminación 1-10 kg", R(50.2, 1.9, 61.8, 12.2), "TERM", "S1 / S2",
           "18 carga de polvo -> 19 ensamblaje -> 20 presurización -> 21 hermeticidad -> 22 etiquetado "
           "-> 23 embalaje -> 24 envolvedora"),
    Sector("AL-2", "Válvulas, manómetros y pescantes (MP de terminación)", R(50.2, 0.3, 62.0, 1.8), "MP", "S1 / S2",
           "Rack de 4 niveles contra el muro sur; llegan por el muelle P3; se reparten en cajas a los buffers "
           "de cada línea (nuevos, carros, recargas)", 40.0),
    Sector("DL", "Ducha de emergencia y lavaojos", R(72.0, 7.0, 74.4, 9.6), "AUX", "común",
           "Junto a la carga de polvo y la pintura (a menos de 10 s de marcha)"),
    # ---------------- banda sur: PT y expedición
    Sector("AL-3", "Almacén de producto terminado", R(34.2, 6.8, 50.0, 18.8), "PT", "S1 / S2",
           "4 racks de 12 m × 4 niveles = 128 posiciones (req. 88)"),
    Sector("EXP", "Expedición y muelle P3", R(34.2, 0.3, 50.0, 6.8), "PT", "común",
           "Un solo muelle con rampa niveladora: sale PT y entran revendidos, insumos, polvos, agentes y N₂"),
    Sector("S4", "Tercerizados revendidos", R(37.6, 0.3, 40.4, 2.35), "PT", "S4",
           "CO₂, agua, AFFF, clase K y agente limpio con sello IRAM: recepción por P3, control y stock"),
    Sector("EMB", "Embalaje de matafuegos nuevos y revendidos", R(43.8, 0.3, 50.0, 2.35), "PT", "S1 / S2",
           "Film, pallets, etiquetas, cajas de cartón, grapas y precintos; sólo para la logística interna de PT"),
    Sector("AL-PN", "Nafta e insumos de los autoelevadores de PT y de carros", R(34.4, 0.3, 37.4, 2.35), "AUX",
           "común", "Armario de inflamables y estante de repuestos (logística interna)"),
    # ---------------- banda sur: carros (U)
    Sector("S3", "Línea de carros 25-100 kg", R(18.2, 8.0, 34.0, 18.8), "PROD", "S3",
           "C1 cilindrado -> C2 punteo -> C3 soldadura long. -> C4 soldadura circ. -> C5 inspección -> C6 PH "
           "-> C7 marcado"),
    Sector("PU-CP", "Carros a pintura tercerizada", R(18.2, 0.3, 22.2, 5.2), "PROD", "S3",
           "Esperan el camión del pintor; salen y vuelven por PO-C y el muelle P3"),
    Sector("SP-2", "Sala de carga de polvo de carros", R(22.4, 0.3, 28.4, 5.2), "TERM", "S3",
           "Recinto HR ≤ 70 %: big bag de carros y cabina de descarga de muestras (IRAM 3550)"),
    Sector("S-TC", "Terminación de carros", R(28.6, 0.3, 34.0, 5.2), "TERM", "S3",
           "C9 armado de ruedas y manguera -> C10 presurización y etiquetado; embalaje de carros"),
]

# ============================================================ EQUIPOS (paso = número de operación en el plano)
# fuente: C = cotización recibida (referencias/INVESTIGACION PROVEEDORES); D = medida de diseño con su criterio
# (pieza a procesar, pallet 1,2 × 1,0, módulo de rack normalizado o puesto del dimensionamiento de recargas)
E_ = Equipo
EQUIPOS = [
    # ---------------- almacén de MP: contenido
    E_("GS1", "Baterías de Arcal 21 (2 × 12 cilindros)", Rw(0.55, 39.4, 1.6, 3.6), "AL-GS", 0,
       fuente="D batería de 12 cilindros de 50 L en marco 1,0 × 1,2", tipo="bateria_gas", frente="E"),
    E_("CT1", "Cantiléver de caños de 6 m (12 atados, 3 niveles)", Rw(0.6, 37.2, 8.2, 1.2), "AL-1T", 0,
       fuente="D caño de 6 m + 1,1 m de brazos extremos", tipo="cantilever", frente="N"),
    E_("RF1", "Porta-flejes 3 niveles (24 rollos)", Rw(5.75, 24.85, 1.4, 11.9), "AL-1F", 0,
       fuente="D 8 cunas de rollo Ø 1,2 m × 3 niveles (MP Opción D)", tipo="portaflejes", frente="O"),
    E_("HJ1", "Paquetes de hojas (4 pos. × 4 alturas)", Rw(7.45, 24.85, 1.5, 12.1), "AL-1H", 0,
       fuente="D paquete del formato mayor 1,5 × 3,0 m", tipo="paquetes", frente="E"),
    E_("HJ2", "Paquete de hojas LAC 4,75 (carros)", Rw(0.45, 24.85, 1.5, 3.1), "AL-1L", 0,
       fuente="D paquete 1,5 × 3,0 m", tipo="paquetes", frente="E"),
    E_("CU1", "Estantería de cuellos y roscas (cajas)", Rw(0.45, 28.3, 0.7, 2.2), "AL-1C", 0,
       fuente="D estantería de 0,6 m de fondo, 4 niveles", tipo="estanteria", frente="E"),
    E_("AM1", "Rack de alambre MAG (1 módulo × 3 niveles)", Rw(0.45, 30.85, 1.1, 2.9), "AL-1A", 0,
       fuente="D módulo 2,7 m: 2 pallets 1,2 × 1,0 por nivel", tipo="rack", frente="E"),
    # ---------------- N1: corte y cuerpo 2,5-10 kg (oeste -> este, eje y = 27,2); se carga desde A2
    E_("M02", "Mesa elevadora de tijera 3 t", Rw(12.9, 25.6, 1.2, 3.1), "N1", 0, 2.2, fuente="MP Manipulación",
       frente="O"),
    E_("M03", "Mesa de bolas", Rw(14.2, 25.5, 1.2, 3.2), "N1", 1, fuente="MP Manipulación", frente="N"),
    E_("M04", "Guillotina Molinari HG 6 × 3200", Rw(15.6, 25.2, 1.7, 3.9), "N1", 0, 7.5,
       fuente="C Molinari HG 6x3200 (largo 3200; huella de catálogo)", frente="O", paso="1"),
    E_("M05", "Mesa de salida", Rw(17.5, 25.6, 1.2, 3.1), "N1", 0, fuente="D igual a la mesa de bolas (corte 3200)", frente="O"),
    E_("SCG", "Contenedor de scrap de la guillotina 1 m³", Rw(19.0, 25.0, 1.2, 1.2), "N1", 0,
       fuente="D basculante de 1 m³ sobre patines (autoelevador)", tipo="contenedores", frente="S"),
    E_("B01", "Numerado de cuerpo", Rw(26.7, 26.8, 1.2, 0.8), "N1", 1, 0.5, fuente="D banco de marcado 1,2 × 0,8", paso="2"),
    E_("B01b", "Numerado de cuerpo", Rw(28.3, 26.8, 1.2, 0.8), "N1", 1, 0.5, fuente="D banco de marcado 1,2 × 0,8", paso="2"),
    E_("B02", "Cilindradora Bästlein 1050 × 1,8", Rw(31.8, 26.7, 1.7, 0.7), "N1", 1, 1.1,
       fuente="C Bästlein 1700 x 700", paso="3"),
    E_("B03", "Soldadura longitudinal automática", Rw(35.8, 26.4, 2.0, 1.4), "N1", 1, 12.0, polvo=True,
       fuente="C Firesafer (huella de catálogo)", paso="4"),
    # ---------------- N2: corte de caño 1 kg: láser - caballete - calle - caballete - láser
    E_("M15", "Láser de tubo Leapion 6012", Rw(13.6, 29.75, 6.85, 0.8), "N2", 0, 10.0, aire=True, polvo=True,
       fuente="C Leapion 6850 x 800", frente="N"),
    E_("CB2", "Caballete porta-tubos (1 día)", Rw(13.6, 31.55, 6.5, 0.5), "N2", 0, fuente="D tubo de 6 m + 0,5 m de topes", tipo="cantilever",
       frente="N"),
    E_("CB1", "Caballete porta-tubos (1 día)", Rw(13.6, 33.45, 6.5, 0.5), "N2", 0, fuente="D tubo de 6 m + 0,5 m de topes", tipo="cantilever",
       frente="S"),
    E_("M16", "Láser de tubo Leapion 6012", Rw(13.6, 34.95, 6.85, 0.8), "N2", 1, 10.0, aire=True, polvo=True,
       fuente="C Leapion 6850 x 800", frente="S"),
    E_("SCL1", "Carro de scrap del láser 5.2", Rw(20.6, 30.6, 0.8, 0.9), "N2", 0,
       fuente="D carro basculante 0,8 × 0,9 (retazos de caño)", tipo="contenedores", frente="N"),
    E_("SCL2", "Carro de scrap del láser 5.1", Rw(20.6, 34.0, 0.8, 0.9), "N2", 0,
       fuente="D carro basculante 0,8 × 0,9 (retazos de caño)", tipo="contenedores", frente="S"),
    # ---------------- N3: cúpulas, fondos y cuellos (se carga el rollo desde A2 con gancho C)
    E_("M06", "Desbobinador SHIMEQ (2 mandriles)", Rw(12.9, 36.2, 1.8, 2.0), "N3", 0, 2.2,
       fuente="C SHIMEQ D-S-9000", frente="O", paso="6"),
    E_("M07", "Enderezador y alimentador SHIMEQ", Rw(15.0, 36.6, 1.6, 1.2), "N3", 0, 2.2,
       fuente="C SHIMEQ D-S-9000", paso="6"),
    E_("M08", "Prensa PHM 300 t (mesa 1800 × 1300)", Rw(16.9, 35.9, 2.6, 2.2), "N3", 1, 37.0, aire=True,
       fuente="C PHM 300 (montantes + unidad hidráulica)", frente="N", paso="6"),
    E_("SCP", "Carro de scrap de la prensa (esqueleto picado)", Rw(22.0, 35.95, 1.2, 0.8), "N3", 0,
       fuente="D carro basculante 0,5 m³ de 0,8 m de ancho (pasa por PO-3)", tipo="contenedores", frente="N"),
    E_("M09", "Preparación de cuello", Rw(17.2, 41.2, 1.2, 1.0), "N3", 1, 3.0, aire=True, fuente="D banco de cuello 1,2 × 1,0", paso="7"),
    E_("M10", "Preparación de cuello", Rw(18.8, 41.2, 1.2, 1.0), "N3", 0, 3.0, aire=True, fuente="D banco de cuello 1,2 × 1,0", paso="7"),
    E_("M11", "Soldadura circ. de cuello", Rw(20.8, 41.2, 1.6, 1.2), "N3", 1, 12.0, polvo=True, fuente="C FS-HFM1",
       paso="8"),
    E_("M12", "Soldadura circ. de cuello", Rw(22.8, 41.2, 1.6, 1.2), "N3", 0, 12.0, polvo=True, fuente="C FS-HFM1",
       paso="8"),
    # ---------------- N4: unión y prueba hidráulica (línea principal, eje y = 36,2)
    E_("E09a", "Encastre de fondo", Rw(35.0, 35.6, 1.2, 1.0), "N4", 1, 1.0, aire=True, fuente="D banco de encastre 1,2 × 1,0", paso="9"),
    E_("E09b", "Encastre de fondo", Rw(36.8, 35.6, 1.2, 1.0), "N4", 1, 1.0, aire=True, fuente="D banco de encastre 1,2 × 1,0", paso="9"),
    E_("E09c", "Encastre de fondo", Rw(38.6, 35.6, 1.2, 1.0), "N4", 1, 1.0, aire=True, fuente="D banco de encastre 1,2 × 1,0", paso="9"),
    E_("B04", "Bordoneadora", Rw(40.8, 35.7, 1.0, 0.8), "N4", 1, 2.2, fuente="C Bendmak SWM-400 (350 kg)", paso="10"),
    E_("A06", "Soldadura circ. cúpula y fondo", Rw(42.6, 35.4, 2.0, 1.4), "N4", 1, 15.0, polvo=True,
       fuente="C Getweld (posicionador + fuente MIG)", paso="11"),
    E_("B06", "Soldadura circ. cúpula y fondo", Rw(45.6, 35.4, 2.0, 1.4), "N4", 1, 15.0, polvo=True,
       fuente="C SCWelding Promotech PRO WP150 + fuente MIG", paso="11"),
    E_("A07", "Prueba hidráulica automática", Rw(50.8, 35.4, 2.4, 1.6), "N4", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A (huella de catálogo)", paso="12"),
    E_("B07", "Prueba hidráulica automática", Rw(54.4, 35.4, 2.4, 1.6), "N4", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A (huella de catálogo)", paso="12"),
    E_("B14", "Secadora de cilindros", Rw(60.0, 35.2, 4.0, 1.6), "N4", 0, 6.0, gas=True, fuente="D túnel para 2 carros de 1,6 m en serie", paso="13"),
    E_("A11", "Secadora de cilindros", Rw(60.0, 37.2, 4.0, 1.6), "N4", 0, 6.0, gas=True, fuente="D túnel para 2 carros de 1,6 m en serie", paso="13"),
    # ---------------- N5: granallado y defectos (columna este, arriba)
    E_("B08", "Granalladora de túnel", Rw(71.0, 35.4, 4.5, 1.3), "N5", 1, 15.0, polvo=True,
       fuente="C Airblast G-100 4500 x 1300", paso="14"),
    E_("B13", "Colector de polvo", Rw(71.4, 37.9, 1.8, 1.4), "N5", 0, 5.5, polvo=True, fuente="D colector de cartuchos del túnel G-100"),
    E_("B09", "Detección de defectos", Rw(76.4, 35.8, 2.2, 1.2), "N5", 1, 0.5, fuente="D mesa de inspección con luz rasante", paso="15"),
    E_("B10", "Corrección de defectos", Rw(80.0, 35.6, 2.2, 1.5), "N5", 1, 10.0, polvo=True, fuente="D mesa + cabina de amolado",
       paso="16"),
    # ---------------- pintura: lazo (eje: y 21,4 / x 84,0 / y 2,6 / x 73,1)
    E_("P01", "Tren de carga (transportador aéreo por empuje)", Rw(79.2, 18.8, 7.5, 5.4), "S-P", 2,
       fuente="C Electricolor (esquema 22 x 13 m)", frente="O", paso="17"),
    E_("P04", "Cabina de pintura 2 × 1,5 m y reciprocador 1300", Rw(78.3, 16.6, 1.7, 2.0), "S-P", 1, 5.0, aire=True,
       polvo=True, fuente="C Electricolor", frente="O", paso="17"),
    E_("P05", "Ciclones de aspiración (2)", Rw(76.7, 18.7, 1.4, 2.0), "S-P", 0, 11.0, polvo=True,
       fuente="C Electricolor", frente="O"),
    E_("P02", "Equipos de aplicación EC40-200D (7 + 1)", Rw(80.1, 16.7, 1.0, 1.8), "S-P", 0, 2.0, aire=True,
       fuente="C Electricolor", frente="O"),
    E_("P03", "Horno 1 de polimerizado 6 × 2,44 m", Rw(81.2, 10.6, 2.44, 6.0), "S-P", 0, 3.0, gas=True,
       fuente="C Electricolor", frente="O", paso="17"),
    E_("P06", "Horno 2 de polimerizado 6 × 2,44 m", Rw(84.2, 10.6, 2.44, 6.0), "S-P", 0, 3.0, gas=True,
       fuente="C Electricolor", frente="O", paso="17"),
    E_("P08", "Tren de descarga", Rw(81.2, 3.1, 5.5, 6.8), "S-P", 1, fuente="C Electricolor", frente="O",
       paso="17"),
    E_("P09", "Retoque y control de espesor", Rw(76.8, 7.0, 2.0, 1.4), "S-P", 0, fuente="D mesa de retoque junto a la descarga", frente="O"),
    # ---------------- terminación 1-10 kg (este -> oeste, eje y = 8,0)
    E_("T01", "Carga de polvo 1-10 kg", Rw(64.2, 4.6, 3.4, 2.0), "SP-1", 1, 3.0, aire=True, polvo=True,
       fuente="C Yukon M-000121 + estación de big bag", frente="N", paso="18"),
    E_("T15", "Deshumidificador y extracción", Rw(67.2, 10.6, 2.4, 1.2), "SP-1", 0, 6.0, fuente="D deshumidificador desecante (HR ≤ 70 %)", frente="N"),
    E_("RKV", "Rack de big bags de polvo", Rw(68.6, 0.6, 1.1, 5.6), "SP-1", 0, fuente="D big bag 1,0 × 1,0 a 2 alturas", forma="rack", frente="O"),
    E_("N2B", "Baterías de N₂ de presurización (2 × 12 cilindros)", Rw(62.3, 9.4, 2.2, 1.2), "SP-1", 0,
       fuente="D batería de 12 cilindros de 50 L en marco 1,0 × 1,2", tipo="bateria_gas", frente="E"),
    E_("AGX", "Agentes extintores: CO₂, agente limpio y AFFF", Rw(62.3, 10.8, 2.2, 1.2), "SP-1", 0,
       fuente="D cilindros de 45 kg y bidones en estante", tipo="bateria_gas", frente="E"),
    E_("T03", "Ensamblaje de válvula", Rw(60.3, 4.8, 1.6, 1.2), "S-T", 1, 0.5, aire=True, fuente="D banco de ensamblaje 1,6 × 1,2", frente="N",
       paso="19"),
    E_("T04", "Ensamblaje de válvula", Rw(58.5, 4.8, 1.6, 1.2), "S-T", 1, 0.5, aire=True, fuente="D banco de ensamblaje 1,6 × 1,2", frente="N",
       paso="19"),
    E_("T05", "Presurización con N₂", Rw(56.7, 4.9, 1.5, 1.0), "S-T", 1, 0.5, n2=True, fuente="C Yukon M-000150",
       frente="N", paso="20"),
    E_("T06", "Hermeticidad", Rw(54.9, 4.9, 1.5, 1.0), "S-T", 0, 0.5, fuente="D batea de inmersión para 10 kg", frente="N", paso="21"),
    E_("T07", "Etiquetadora semiautomática", Rw(53.1, 5.0, 1.2, 0.6), "S-T", 1, 0.5, fuente="C SISA", frente="N",
       paso="22"),
    E_("T08", "Embalaje y palletizado", Rw(50.5, 4.4, 1.6, 1.6), "S-T", 1, fuente="D pallet 1,2 × 1,0 + mesa giratoria", frente="E", paso="23"),
    E_("T09", "Embalaje y palletizado", Rw(50.5, 6.4, 1.6, 1.6), "S-T", 1, fuente="D pallet 1,2 × 1,0 + mesa giratoria", frente="E", paso="23"),
    E_("T10", "Palletizado de cilindros vendidos", Rw(50.5, 8.4, 1.6, 1.6), "S-T", 1, fuente="D pallet 1,2 × 1,0 + mesa giratoria", frente="E",
       paso="23"),
    E_("RKI", "Rack de válvulas, manómetros y pescantes", Rw(50.6, 0.5, 7.6, 1.1), "AL-2", 0, fuente="D 3 módulos de 2,5 m × 4 niveles", forma="rack"),
    E_("BVN", "Estantería pasante de válvulas y manómetros (nuevos)", Rw(58.5, 4.25, 3.4, 0.5), "S-T", 0,
       fuente="D estantería dinámica bajo los bancos 19.1 y 19.2", tipo="estanteria", frente="S"),
    # ---------------- PT
    E_("T11", "Envolvedora de pallets", Rw(48.2, 8.2, 1.5, 3.0), "AL-3", 0, 1.5, fuente="C EDOS PS5", paso="24"),
    E_("RK1", "Rack RK1 pasante: PT (este) / casquetes (oeste)", Rw(34.3, 7.0, 1.1, 11.6), "AL-3", 0, fuente="D 4 módulos de 2,7 m × 4 niveles (pallet 1,2 × 1,0)",
       forma="rack", frente="E"),
    E_("RK2", "Rack RK2 doble (4 módulos × 2 × 4 por cara)", Rw(38.9, 7.0, 2.2, 11.6), "AL-3", 0, fuente="D 4 módulos de 2,7 m, doble fondo × 4 niveles",
       forma="rack", frente="E"),
    E_("RK3", "Rack RK3 de alta rotación (4 × 2 × 4)", Rw(44.6, 7.0, 1.1, 11.6), "AL-3", 0, fuente="D 4 módulos de 2,7 m × 4 niveles (pallet 1,2 × 1,0)",
       forma="rack", frente="E"),
    # ---------------- S3 carros (U: norte O -> E, centro E -> O, sale por P6 y vuelve por P8)
    E_("C01", "Cilindradora de 4 rodillos", Rw(23.0, 16.8, 4.5, 1.4), "S3", 1, 5.5, fuente="C Getweld", paso="C1"),
    E_("C02", "Punteo, refuerzo y estructura", Rw(28.0, 16.6, 2.5, 1.5), "S3", 1, 10.0, polvo=True, fuente="D mesa de punteo para cilindro de 100 kg",
       paso="C2"),
    E_("C03", "Punteo, refuerzo y estructura", Rw(31.0, 16.6, 2.5, 1.5), "S3", 1, 10.0, polvo=True, fuente="D mesa de punteo para cilindro de 100 kg",
       paso="C2"),
    E_("C04", "Soldadura longitudinal de carros", Rw(30.4, 12.0, 3.0, 2.0), "S3", 1, 18.0, polvo=True,
       fuente="C Getweld ZF-1000", frente="N", paso="C3"),
    E_("C05", "Soldadura circ. de fondo y cúpula", Rw(26.6, 12.2, 3.0, 1.8), "S3", 1, 18.0, polvo=True, fuente="D virador de rodillos + fuente MIG",
       frente="N", paso="C4"),
    E_("C06", "Inspección de costuras", Rw(23.6, 12.5, 2.2, 1.2), "S3", 1, 0.5, fuente="D mesa de inspección de costuras", frente="N",
       paso="C5"),
    E_("C07", "PH 4,0 MPa con jaula", Rw(19.4, 11.8, 3.6, 2.6), "S3", 1, 2.0, agua=True,
       fuente="C Yukon M-000200 + jaula", frente="N", paso="C6"),
    E_("C08", "Marcado del recipiente", Rw(18.6, 8.6, 1.5, 1.0), "S3", 0, 0.5, fuente="D banco de marcado", frente="E",
       paso="C7"),
    E_("C09", "Probetas de soldadura", Rw(23.6, 9.0, 2.4, 1.2), "S3", 0, 2.0, fuente="D mesa de probetas (IRAM 3523)", frente="N"),
    E_("C10", "Pluma giratoria 1 t", Rw(29.75, 12.6, 0.6, 0.6), "S3", 0, 1.5, fuente="D pluma de columna, brazo 3 m", forma="circ"),
    E_("C12", "Carros a pintura tercerizada", Rw(18.4, 0.6, 3.6, 4.4), "PU-CP", 0, fuente="D 6 carros 1,1 × 2,2 en 2 filas", forma="rack",
       tipo="carros"),
    E_("T02", "Carga de polvo de carros", Rw(25.8, 1.4, 2.4, 2.4), "SP-2", 1, 2.0, aire=True, polvo=True,
       fuente="D carga de polvo de 25-100 kg + big bag", frente="N", paso="C8"),
    E_("Q01", "Cabina de descarga de muestras", Rw(22.6, 0.5, 2.2, 2.6), "SP-2", 0, 3.0, polvo=True, fuente="D cabina de descarga con filtro",
       frente="E"),
    E_("T12", "Armado de carros", Rw(29.0, 2.2, 2.2, 1.8), "S-TC", 1, 0.5, aire=True, fuente="D banco de armado de ruedas 2,4 × 1,8", frente="N",
       paso="C9"),
    E_("T13", "Presurización y etiquetado de carros", Rw(31.4, 2.2, 2.2, 1.8), "S-TC", 1, 0.5, n2=True,
       fuente="D banco de presurización + etiquetado", frente="N", paso="C10"),
    E_("T14", "Estructuras y ruedas de carros", Rw(29.0, 0.4, 2.8, 0.9), "S-TC", 0, fuente="D estantería cantiléver de estructuras", forma="rack"),
    E_("BVC", "Buffer de válvulas y manómetros de carros + embalaje", Rw(32.0, 0.4, 1.9, 0.6), "S-TC", 0,
       fuente="D estantería de cajas de 0,6 m de fondo", tipo="estanteria", frente="N"),
    # ---------------- SC compresores y colectores de gases de soldadura (extremo oeste = más cerca de las soldadoras)
    E_("CG1", "Colector de Arcal 21 (manifold de 2 baterías)", Rw(48.3, 41.2, 2.4, 1.4), "SC", 0,
       fuente="D 2 baterías 1,0 × 1,2 + regulador de 2 etapas", tipo="bateria_gas", frente="S"),
    E_("CH1", "Colector de humos de soldadura (filtro de cartuchos)", Rw(51.2, 41.1, 2.4, 1.5), "SC", 0, 7.5,
       polvo=True, fuente="D colector de cartuchos 6000 m³/h", tipo="colector", frente="S"),
    E_("CP1", "Compresor de tornillo 30 kW", Rw(54.6, 41.3, 1.9, 1.1), "SC", 0, 30.0,
       fuente="D compresor de tornillo 30 kW (1,9 × 1,1)", tipo="compresor", frente="S"),
    E_("CP2", "Compresor de tornillo 30 kW (reserva)", Rw(57.3, 41.3, 1.9, 1.1), "SC", 0, 30.0,
       fuente="D compresor de tornillo 30 kW (1,9 × 1,1)", tipo="compresor", frente="S"),
    E_("SEC", "Secador frigorífico y filtros", Rw(60.0, 41.4, 1.0, 0.9), "SC", 0, 1.5,
       fuente="D secador para 5 m³/min", tipo="compresor", frente="S"),
    E_("TQ1", "Pulmón de aire 2000 L", Rw(61.6, 41.3, 1.2, 1.2), "SC", 0, fuente="D tanque vertical Ø 1,2 m",
       tipo="tanque", forma="circ", frente="S"),
]

# recargas: puestos R (numeración del dimensionamiento de recargas), dentro de sus locales
_RC = [
    # (cod, nombre, (x, y, w, h), local, op, tipo, frente)
    ("R01", "Recepción y clasificación", (2.95, 4.35, 1.5, 0.9), "RC-RD", 1, "mesa_control", "S"),
    ("R19a", "Inspección visual", (4.1, 0.6, 1.6, 0.9), "RC-RD", 1, "inspeccion", "O"),
    ("R19b", "Inspección visual", (4.1, 1.65, 1.6, 0.9), "RC-RD", 1, "inspeccion", "O"),
    ("R04a", "Desarme de matafuego (morsa)", (6.4, 3.8, 1.4, 0.9), "RC-DE", 1, "banco", "S"),
    ("R04b", "Desarme de matafuego (morsa)", (8.2, 3.8, 1.4, 0.9), "RC-DE", 1, "banco", "S"),
    ("R04c", "Desarme de matafuego (morsa)", (10.0, 3.8, 1.4, 0.9), "RC-DE", 1, "banco", "S"),
    ("R05", "Lavado interior de cilindro", (6.6, 0.8, 2.6, 1.4), "RC-DE", 1, "hermeticidad", "N"),
    ("R02a", "Descarga de polvo con recuperación", (12.4, 3.2, 1.2, 1.4), "RC-DC", 1, "cabina_muestras", "S"),
    ("R02b", "Descarga de polvo con recuperación", (13.8, 3.2, 1.2, 1.4), "RC-DC", 1, "cabina_muestras", "S"),
    ("R02c", "Descarga de polvo con recuperación", (15.2, 3.2, 1.2, 1.4), "RC-DC", 0, "cabina_muestras", "S"),
    ("R02d", "Descarga de polvo con recuperación", (16.6, 3.2, 1.0, 1.4), "RC-DC", 0, "cabina_muestras", "S"),
    ("R26", "Descarga de líquidos", (12.4, 0.8, 1.8, 1.4), "RC-DC", 0, "hermeticidad", "N"),
    ("R07", "Prueba hidráulica con jaula (Yukon M-000200)", (12.3, 9.6, 2.6, 1.8), "RC-PH", 1, "ph", "S"),
    ("R08", "Secado de cilindros", (12.3, 7.4, 2.4, 1.0), "RC-PH", 0, "secadora", "N"),
    ("R23", "Prueba Puffer (IRAM 3672)", (14.9, 7.4, 1.2, 1.2), "RC-PH", 0, "banco", "N"),
    ("R03a", "Carga de polvo por vacío", (4.8, 9.6, 1.6, 1.8), "RC-PV", 1, "carga_polvo", "S"),
    ("R03b", "Carga de polvo por vacío", (6.8, 9.6, 1.6, 1.8), "RC-PV", 1, "carga_polvo", "S"),
    ("R03c", "Carga de polvo por vacío", (8.8, 9.6, 1.6, 1.8), "RC-PV", 0, "carga_polvo", "S"),
    ("R16", "Clase D (descarga / carga manual)", (10.6, 7.4, 1.0, 1.6), "RC-PV", 0, "banco", "O"),
    ("R18", "Deshumidificador sala de polvo", (4.8, 7.4, 2.0, 1.0), "RC-PV", 0, "deshumidificador", "N"),
    ("R24", "Descarga de CO₂ / agente limpio", (0.8, 9.8, 1.2, 1.4), "RC-GA", 1, "presurizacion", "E"),
    ("R12", "Carga de CO₂ (trasvasador)", (3.0, 9.8, 1.15, 1.4), "RC-GA", 0, "presurizacion", "N"),
    ("R13", "Carga de agente limpio + N₂", (0.8, 7.4, 1.2, 1.4), "RC-GA", 0, "presurizacion", "E"),
    ("R14", "Llenado de agente líquido", (12.4, 13.6, 1.6, 1.2), "RC-LQ", 1, "hermeticidad", "N"),
    ("R09a", "Ensamblaje (anillo, pescante, rosca)", (4.8, 17.3, 1.6, 1.0), "RC-EN", 1, "ensamble", "S"),
    ("R09b", "Ensamblaje (anillo, pescante, rosca)", (6.6, 17.3, 1.6, 1.0), "RC-EN", 1, "ensamble", "S"),
    ("R09c", "Ensamblaje (anillo, pescante, rosca)", (8.4, 17.3, 1.6, 1.0), "RC-EN", 0, "ensamble", "S"),
    ("R10a", "Presurización N₂", (10.2, 17.3, 1.5, 1.0), "RC-EN", 1, "presurizacion", "S"),
    ("R10b", "Presurización N₂", (10.2, 14.9, 1.5, 1.0), "RC-EN", 0, "presurizacion", "N"),
    ("R22", "Ensayo de peso", (4.8, 13.6, 1.2, 1.0), "RC-EN", 0, "balanza", "N"),
    ("R11", "Hermeticidad (inmersión)", (6.4, 13.6, 1.6, 1.0), "RC-EN", 1, "hermeticidad", "N"),
    ("R20", "Retoque de pintura", (8.4, 13.6, 1.6, 1.0), "RC-EN", 1, "retoque", "N"),
    ("R21", "Etiquetado (oblea IRAM + marbete)", (12.6, 17.3, 1.6, 0.9), "RC-RP", 1, "etiquetadora", "S"),
    ("R17", "Despacho (precintos + remito)", (0.6, 4.35, 2.2, 0.9), "RC-RD", 1, "mesa_control", "S"),
]
for _c, _n, (_x, _y, _w, _h), _s, _op, _t, _f in _RC:
    EQUIPOS.append(Equipo(_c, _n, Rw(_x, _y, _w, _h), _s, _op, 0.5,
                          fuente="D puesto del Dimensionamiento de recargas", tipo=_t, frente=_f,
                          paso=_c[:3].replace("R0", "R")))

# ============================================================ NUMERACIÓN DE PASOS (única, en orden de proceso)
# entero = operación; .1 .2 .3 = máquinas iguales en paralelo; C = carros; R = recargas
PASOS = {
    "M04": "1", "B01": "2.1", "B01b": "2.2", "B02": "3", "B03": "4", "M16": "5.1", "M15": "5.2",
    "M06": "6.1", "M07": "6.2", "M08": "6.3", "M09": "7.1", "M10": "7.2", "M11": "8.1", "M12": "8.2",
    "E09a": "9.1", "E09b": "9.2", "E09c": "9.3", "B04": "10", "A06": "11.1", "B06": "11.2",
    "A07": "12.1", "B07": "12.2", "B14": "13.1", "A11": "13.2", "B08": "14", "B09": "15", "B10": "16",
    "P01": "17.1", "P04": "17.2", "P03": "17.3", "P06": "17.4", "P08": "17.5",
    "T01": "18", "T03": "19.1", "T04": "19.2", "T05": "20", "T06": "21", "T07": "22",
    "T08": "23.1", "T09": "23.2", "T10": "23.3", "T11": "24",
    "C01": "C1", "C02": "C2.1", "C03": "C2.2", "C04": "C3", "C05": "C4", "C06": "C5", "C07": "C6", "C08": "C7",
    "T02": "C8", "T12": "C9", "T13": "C10",
    "R01": "R1", "R19a": "R2.1", "R19b": "R2.2", "R04a": "R3.1", "R04b": "R3.2", "R04c": "R3.3", "R05": "R4",
    "R02a": "R5.1", "R02b": "R5.2", "R02c": "R5.3", "R02d": "R5.4", "R26": "R6", "R07": "R7", "R08": "R8",
    "R23": "R9", "R03a": "R10.1", "R03b": "R10.2", "R03c": "R10.3", "R16": "R11", "R24": "R12", "R12": "R13",
    "R13": "R14", "R14": "R15", "R09a": "R16.1", "R09b": "R16.2", "R09c": "R16.3", "R10a": "R17.1",
    "R10b": "R17.2", "R22": "R18", "R11": "R19", "R20": "R20", "R21": "R21", "R17": "R22",
}
for _e in EQUIPOS:
    _e.paso = PASOS.get(_e.cod, "")


# ============================================================ PULMONES (espera entre pasos)
PULMONES = [
    Pulmon("PU-1", R(24.3, 25.0, 26.3, 29.3), "Cuerpos cortados 2,5-100 kg", "1 Guillotina",
           "2 Numerado / C1 carros", 2, "v"),
    Pulmon("PU-2", R(29.7, 25.0, 31.5, 29.3), "Cuerpos numerados", "2 Numerado", "3 Cilindrado", 2, "v"),
    Pulmon("PU-3", R(33.7, 25.0, 35.5, 29.3), "Cuerpos cilindrados, abiertos", "3 Cilindrado",
           "4 Sold. longitudinal", 2, "v"),
    Pulmon("PU-4", R(38.2, 25.0, 39.2, 29.3), "Cuerpos 2,5-10 kg soldados", "4 Sold. longitudinal",
           "9 Encastre", 1, "v"),
    Pulmon("PU-L1", R(21.6, 29.8, 23.4, 31.6), "Cuerpos 1 kg cortados (láser 5.1)", "5.1 Láser", "PU-L2", 1, "v"),
    Pulmon("PU-L2", R(21.6, 34.0, 23.4, 35.75), "Cuerpos 1 kg cortados", "5.2 Láser / PU-L1", "9 Encastre", 1, "v"),
    Pulmon("PU-K", R(20.0, 35.95, 21.8, 38.8), "Fondos embutidos", "6 Embutido", "9 Encastre", 2, "v"),
    Pulmon("PU-C", R(24.8, 40.1, 26.8, 43.5), "Cúpulas con cuello", "8 Sold. de cuello",
           "11 Sold. circunferencial", 2, "v"),
    Pulmon("PU-5", R(48.4, 35.2, 50.4, 38.9), "Cilindros soldados", "11 Sold. circunferencial", "12 PH", 2, "v"),
    Pulmon("PU-6", R(58.0, 35.2, 59.6, 38.9), "Cilindros probados (mojados)", "12 PH", "13 Secado", 2, "v"),
    Pulmon("PU-7", R(64.4, 35.2, 66.4, 38.9), "Cilindros secos", "13 Secado", "14 Granallado", 2, "v"),
    Pulmon("PU-8", R(76.6, 30.4, 80.4, 33.2), "Cilindros controlados", "15 Detección / 16 Corrección",
           "17 Pintura", 3, "h"),
    Pulmon("PU-9", R(62.4, 12.6, 69.6, 18.6), "Cilindros pintados", "17 Pintura (descarga)",
           "18 Carga de polvo / almacén de cilindros", 6, "h"),
    Pulmon("PU-10", R(33.4, 8.2, 34.0, 8.3), "-", "-", "-", 0, "h"),
]
PULMONES = [p for p in PULMONES if p.carros]

# ============================================================ PUERTAS Y PORTONES
# Cuatro portones en toda la nave (uno por frente logístico); el resto son puertas de personas y de emergencia.
PUERTAS = [
    Puerta("P1", "N", 3.4, 10.6, 4.5, "porton",
           "MP: hojas, flejes, caños (entran atravesados: 7,20 m), cuellos, alambre y gases; sale el scrap"),
    Puerta("P2", "S", 0.8, 3.6, 3.0, "porton", "Recargas: los utilitarios dejan y retiran equipos"),
    Puerta("P3", "S", 40.6, 43.6, 3.2, "muelle",
           "Muelle único: sale PT y carros; entran revendidos, válvulas, embalaje, polvos, agentes y N₂"),
    Puerta("P4", "E", 26.0, 29.0, 3.0, "porton", "Pintura electrostática y granalla"),
    # salidas de emergencia (1,10 m, barral antipánico, abren hacia afuera)
    Puerta("SE-1", "N", 30.0, 31.1, 2.1, "emergencia"),
    Puerta("SE-2", "N", 46.9, 48.0, 2.1, "emergencia"),
    Puerta("SE-3", "N", 66.0, 67.1, 2.1, "emergencia"),
    Puerta("SE-4", "N", 76.4, 77.5, 2.1, "emergencia"),
    Puerta("SE-5", "E", 39.45, 40.55, 2.1, "emergencia"),
    Puerta("SE-7", "S", 86.0, 87.1, 2.1, "emergencia"),
    Puerta("SE-8", "S", 14.6, 15.7, 2.1, "emergencia"),
    Puerta("SE-9", "S", 58.6, 59.7, 2.1, "emergencia"),
    Puerta("SE-10", "O", 5.75, 6.85, 2.1, "emergencia"),
    Puerta("SE-11", "O", 11.95, 13.05, 2.1, "emergencia"),
    Puerta("PP-1", "O", 23.2, 24.4, 2.1, "peatonal", "Ingreso de personal desde vestuarios"),
    Puerta("PG", "N", 48.6, 50.2, 2.1, "peatonal", "Cambio de baterías de Arcal 21 del colector (desde el patio norte)"),
]

# ventanas en el cerramiento de la nave: (lado, desde, hasta, uso)
VENTANAS_NAVE = [("O", 19.4, 20.9, "Administración: vista a lo largo del pasillo central")]

# ============================================================ ANEXOS
ANEXOS = [
    Sector("SV", "Bloque de servicios al personal y administración", R(-18.0, 19.0, 0.0, 35.0), "SERV", "común"),
    Sector("RC", "Recargas (ángulo SO de la nave)", R(0.3, 0.3, 18.0, 18.8), "RC", "RC",
           "Dentro de la nave, con tabiques y portones propios"),
    Sector("ST", "Sala técnica: transformador, TGBT y compresores", R(36.0, 44.2, 46.0, 50.0), "AUX", "común"),
]

# ============================================================ FLUJOS (m)
TL = []
TL_CARGADO = []
TL_RETORNO = []
LAZO = [(83.0, 21.5), (79.15, 21.5), (79.15, 17.6), (82.42, 17.6), (82.42, 6.5)]   # carga -> cabina -> horno 1 -> descarga

FLUJOS = [
    # ---------------- MP: todo lo de producción entra por P1 al almacén de MP (AN es la cabecera de maniobra)
    Flujo("MP", [(10.0, 52.0), (10.0, 43.8), (10.0, 40.0), (11.9, 40.0), (11.9, 31.0), (9.0, 31.0)],
          "Hojas: alero -> P1 -> A2 -> paquetes AL-1H"),
    Flujo("MP", [(9.0, 27.15), (12.9, 27.15)], "Paquete a la mesa elevadora (autoelevador por el lado largo)"),
    Flujo("MP", [(6.0, 52.0), (6.0, 43.8), (6.0, 38.6)],
          "Caños: el autoelevador entra por P1 con el atado atravesado y lo apoya en el cantiléver"),
    Flujo("MP", [(4.0, 38.6), (4.0, 39.2), (12.0, 39.2), (12.0, 32.75), (13.6, 32.75)],
          "Caños: carro porta-tubos por AN, A2 y PO-L a los caballetes"),
    Flujo("MP", [(13.6, 32.75), (20.0, 32.75)], "Tubos a los caballetes"),
    Flujo("MP", [(9.0, 52.0), (9.0, 43.8), (9.0, 41.0), (11.4, 41.0), (11.4, 21.6), (3.0, 21.6), (3.0, 30.0),
                 (5.6, 30.0)], "Flejes: alero -> P1 -> A2 -> pasillo central -> A1 -> porta-flejes"),
    Flujo("MP", [(5.6, 33.0), (4.6, 33.0), (4.6, 22.2), (10.6, 22.2), (10.6, 37.2), (12.9, 37.2)],
          "Rollo al desbobinador (gancho C)"),
    Flujo("MP", [(4.0, 52.0), (4.0, 43.8), (4.0, 41.2), (2.8, 41.2)], "Gases Arcal 21: baterías a la jaula AL-GS"),
    Flujo("MP", [(2.8, 40.2), (10.4, 40.2), (10.4, 43.8), (10.4, 45.0), (33.0, 45.0), (33.0, 51.0), (49.4, 51.0),
                 (49.4, 44.0)], "Batería de Arcal 21 al colector de la sala SC (patio norte, puerta PG)"),
    # ---------------- MP de carros, PT de terceros y terminación: muelle único P3 (recepción 7 a 10 h)
    Flujo("MP", [(41.2, -6.0), (41.2, 0.0), (41.2, 4.6), (37.0, 4.6), (37.0, 10.0), (35.4, 10.0)],
          "Casquetes de carros (P3 -> rack pasante RK1)", "S3"),
    Flujo("MP", [(34.3, 10.0), (28.1, 10.0), (28.1, 12.2)], "Casquete a la soldadura circ.", "S3"),
    Flujo("MP", [(40.9, -6.0), (40.9, 0.0), (40.9, 2.0), (40.4, 2.0)], "Tercerizados revendidos (P3)", "S4"),
    Flujo("MP", [(43.4, -6.0), (43.4, 0.0), (43.4, 2.6), (55.5, 2.6), (55.5, 1.8)],
          "Válvulas, manómetros y pescantes (P3 -> AL-2)"),
    Flujo("MP", [(57.0, 1.8), (57.0, 2.2), (59.3, 2.2), (59.3, 4.25)],
          "Válvulas a la estantería pasante de ensamblaje"),
    Flujo("MP", [(43.5, -6.0), (43.5, 0.0), (43.5, 2.45), (45.4, 2.45), (45.4, 2.35)],
          "Embalaje, pallets y precintos (P3 -> EMB)"),
    Flujo("MP", [(43.2, -6.0), (43.2, 0.0), (43.2, 3.4), (66.0, 3.4), (66.0, 2.0), (68.6, 2.0)],
          "Polvos, agentes y N₂ (P3 -> AT -> almacén previo a la carga)"),
    Flujo("MP", [(68.6, 5.2), (67.6, 5.2)], "Big bag a la carga de polvo"),
    Flujo("MP", [(49.0, 2.35), (49.0, 3.0), (51.3, 3.0), (51.3, 4.4)], "Cajas y film de EMB al embalaje"),
    Flujo("MP", [(96.0, 27.5), (88.0, 27.5), (86.0, 27.5)], "Pintura electrostática (P4)"),
    Flujo("MP", [(87.2, 24.8), (87.2, 18.0), (81.1, 18.0)], "Pintura en polvo a las tolvas de aplicación"),
    Flujo("MP", [(96.0, 28.6), (88.0, 28.6), (85.6, 28.6), (85.6, 40.0), (71.3, 40.0), (71.3, 40.8)],
          "Granalla (P4 -> PO-E -> PO-4 -> GR)"),
    Flujo("MP", [(41.6, -6.0), (41.6, 0.0), (41.6, 5.0), (34.6, 5.0), (34.6, 6.2), (26.7, 6.2), (26.7, 5.2)],
          "Carros pintados, polvo y estructuras de carros (P3 -> PO-C)", "S3"),
    # ---------------- SE: N1 corte y cuerpo 2,5-10 kg
    Flujo("SE", [(17.3, 27.5), (17.5, 27.5)], "Cuerpo cortado"),
    Flujo("SE", [(18.7, 27.5), (24.3, 27.5)], "Cuerpos al pulmón"),
    Flujo("SE", [(26.3, 27.2), (26.7, 27.2), (27.9, 27.2), (28.3, 27.2), (29.5, 27.2), (29.7, 27.2), (31.5, 27.2),
                 (31.8, 27.2), (33.5, 27.2), (33.7, 27.2), (35.5, 27.2), (35.8, 27.2), (38.0, 27.2), (38.2, 27.2)],
          "Cuerpo 2,5-10 kg: numerado -> cilindrado -> soldadura longitudinal", "S2"),
    Flujo("SE", [(38.9, 29.3), (38.9, 35.6)], "Cuerpos 2,5-10 kg al encastre", "S2"),
    Flujo("SE", [(25.3, 25.0), (25.3, 24.4), (25.3, 19.6), (25.3, 18.2)], "Cuerpos de carros a la cilindradora",
          "S3"),
    # ---------------- SE: N2 1 kg y N3 cúpulas y fondos
    Flujo("SE", [(20.45, 30.15), (21.6, 30.15)], "Cuerpo 1 kg"),
    Flujo("SE", [(20.45, 35.35), (21.6, 35.35)], "Cuerpo 1 kg"),
    Flujo("SE", [(22.5, 31.6), (22.5, 34.0)], "PU-L1 a PU-L2"),
    Flujo("SE", [(23.4, 34.4), (34.2, 34.4), (34.2, 36.1), (35.0, 36.1)], "Cuerpos 1 kg al encastre", "S1"),
    Flujo("SE", [(14.7, 37.2), (15.0, 37.2)], "Fleje enderezado"),
    Flujo("SE", [(16.6, 37.2), (16.9, 37.2)], "Fleje al troquel"),
    Flujo("SE", [(19.5, 37.1), (20.0, 37.1)], "Fondos al pulmón"),
    Flujo("SE", [(21.8, 37.6), (35.6, 37.6), (35.6, 36.6)], "Fondos al encastre"),
    Flujo("SE", [(17.8, 38.1), (17.8, 41.2)], "Cúpulas a la preparación de cuello"),
    Flujo("SE", [(20.0, 41.7), (20.8, 41.7)], "Cuello preparado"),
    Flujo("SE", [(24.4, 41.7), (24.8, 41.7)], "Cúpulas con cuello al pulmón"),
    Flujo("SE", [(26.8, 41.4), (46.6, 41.4), (46.6, 36.8)], "Cúpulas a la soldadura circ."),
    Flujo("SE", [(43.6, 41.4), (43.6, 36.8)], "Cúpulas a la soldadura circ."),
    # ---------------- SE: N4-N5 línea principal (eje y = 36,1)
    Flujo("SE", [(36.2, 36.1), (36.8, 36.1), (38.0, 36.1), (38.6, 36.1), (39.8, 36.1), (40.8, 36.1), (42.0, 36.1),
                 (42.6, 36.1), (45.0, 36.1), (45.6, 36.1), (48.0, 36.1), (48.4, 36.1), (50.4, 36.1), (50.8, 36.1),
                 (54.0, 36.1), (54.4, 36.1), (57.6, 36.1), (58.0, 36.1), (59.6, 36.1), (60.0, 36.1), (64.0, 36.1),
                 (64.4, 36.1), (66.4, 36.1), (71.0, 36.1), (75.5, 36.1), (76.4, 36.1)],
          "Línea principal: encastre -> bordoneado -> soldadura circ. -> PH -> secado -> granallado"),
    Flujo("SE", [(78.6, 36.4), (80.0, 36.4)], "Defectos a corrección"),
    Flujo("SE", [(78.2, 35.8), (78.2, 33.2)], "Aprobados al pulmón de pintura"),
    Flujo("SE", [(81.9, 35.6), (81.9, 32.0), (80.4, 32.0)], "Corregidos al pulmón de pintura"),
    Flujo("SE", [(79.8, 30.4), (79.8, 24.2)], "A la carga de pintura"),
    # ---------------- SE: pintura (lazo) y terminación
    Flujo("SE", LAZO, "Pintura: carga, cabina, horno 1 y descarga (transportador aéreo por empuje)"),
    Flujo("SE", [(82.42, 17.6), (85.42, 17.6), (85.42, 9.9)], "Pintura: horno 2 en paralelo"),
    Flujo("RET", [(81.2, 5.0), (79.6, 5.0), (79.6, 23.0), (83.0, 23.0)], "Retorno de ganchos (sistema de avance)"),
    Flujo("SE", [(81.2, 5.6), (71.0, 5.6), (71.0, 15.0), (69.6, 15.0)], "Pintados al pulmón"),
    Flujo("SE", [(66.6, 12.6), (66.6, 6.6)], "A la carga de polvo"),
    Flujo("SE", [(64.2, 5.6), (61.9, 5.6), (60.3, 5.6), (60.1, 5.6), (58.5, 5.6), (58.2, 5.6), (56.7, 5.6),
                 (56.4, 5.6), (54.9, 5.6), (54.6, 5.6), (53.1, 5.6), (52.1, 5.6)],
          "Ensamblaje -> presurización -> hermeticidad -> etiquetado -> embalaje"),
    # ---------------- SE: carros (U) y su vuelta por la calle PO-C
    Flujo("SE", [(27.5, 17.5), (28.0, 17.4), (30.5, 17.4), (31.0, 17.4), (33.5, 17.4), (33.8, 17.4), (33.8, 13.0),
                 (33.4, 13.0), (30.4, 13.0), (29.6, 13.0), (26.6, 13.0), (25.8, 13.1), (23.6, 13.1), (23.0, 13.1),
                 (19.4, 13.1), (19.0, 13.1), (19.0, 9.6)],
          "Carros: punteo, soldaduras, inspección, PH y marcado", "S3"),
    Flujo("SE", [(19.4, 8.6), (19.4, 5.2)], "Carros a la espera del pintor (cruzan PO-C)", "S3"),
    Flujo("SE", [(21.0, 5.2), (21.0, 6.7), (40.7, 6.7), (40.7, 0.0), (40.7, -6.0)],
          "Carros al pintor por PO-C y el muelle P3", "S3"),
    Flujo("SE", [(28.2, 3.0), (29.0, 3.0)], "Carga de polvo -> armado", "S3"),
    Flujo("SE", [(31.2, 3.0), (31.4, 3.0)], "Armado -> presurización", "S3"),
    # ---------------- PT (expedición 13 a 17 h)
    Flujo("PT", [(62.4, 16.0), (50.2, 16.0), (46.8, 16.0)], "Cilindros vendidos vacíos al almacén de PT"),
    Flujo("PT", [(50.5, 5.2), (49.7, 8.6)], "Pallet a envolvedora"),
    Flujo("PT", [(50.5, 7.2), (49.7, 9.6)], "Pallet a envolvedora"),
    Flujo("PT", [(50.5, 9.2), (49.7, 10.6)], "Pallet de cilindros a envolvedora"),
    Flujo("PT", [(48.2, 9.7), (46.8, 9.7), (46.8, 12.0)], "Almacén de PT (envolvedora -> RK3)"),
    Flujo("PT", [(41.1, 9.0), (42.4, 9.0), (42.4, 0.0), (42.4, -6.0)], "Expedición (RK2 -> T2 -> muelle P3)"),
    Flujo("PT", [(45.7, 8.6), (46.2, 8.6), (46.2, 4.0), (42.8, 4.0), (42.8, 0.0), (42.8, -6.0)],
          "Expedición (RK3 -> T3 -> muelle P3)"),
    Flujo("PT", [(33.6, 3.6), (34.2, 3.6), (42.0, 3.6), (42.0, 0.0), (42.0, -6.0)],
          "Carros terminados (S-TC -> EX -> muelle P3)", "S3"),
    Flujo("PT", [(40.4, 1.0), (41.8, 1.0), (41.8, 0.0), (41.8, -6.0)], "Tercerizados a expedición", "S4"),
    # ---------------- scrap: contenedor en cada puesto que lo genera; sale por el portón más cercano (P1)
    Flujo("SCRAP", [(19.6, 25.0), (19.6, 22.6), (11.0, 22.6), (11.0, 43.8), (11.0, 44.6), (1.2, 46.2)],
          "Scrap de la guillotina: autoelevador de MP por el pasillo central y A2 al volquete (P1)"),
    Flujo("SCRAP", [(21.0, 31.5), (21.0, 32.6), (12.4, 32.6), (12.4, 43.8), (12.4, 44.4), (1.2, 46.0)],
          "Scrap del láser 5.2: carro por PO-L y A2 al volquete (P1)"),
    Flujo("SCRAP", [(21.0, 34.0), (21.0, 32.9), (12.6, 32.9)], "Scrap del láser 5.1 a PO-L"),
    Flujo("SCRAP", [(22.6, 36.75), (22.6, 39.65), (12.8, 39.65), (12.8, 43.8), (12.8, 44.2), (1.2, 45.8)],
          "Esqueleto de la prensa: carro por PO-3 y AN al volquete (P1)"),
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


def _bajada(x0, y0, cod):
    """Ramal ortogonal desde (x0, y0) hasta el puesto del equipo `cod`: vertical y luego horizontal."""
    x, y = _op(cod)
    return [(x0, y0, x0, y), (x0, y, x, y)] if abs(x - x0) > 1e-6 else [(x0, y0, x, y)]


def _hilos():
    H = []
    # almacén de MP, corte y fila sur (N1): directo desde la senda del pasillo central
    br = [(3.8, Y_PP, 3.8, 26.0), (10.9, Y_PP, 10.9, 24.6)]
    br += [(18.85, Y_PP, 18.85, 29.6), (18.85, 29.6, _op("M03")[0], 29.6), (_op("M03")[0], 29.6, *_op("M03"))]
    for c in ("B01", "B01b", "B02", "B03"):
        br += _bajada(_op(c)[0], Y_PP, c)
    H.append(("Almacén de MP y corte (N1)", [(0.0, Y_PP), (38.0, Y_PP)], br))
    # láseres, línea principal, cúpulas y calidad: por la calle PO-1
    br = [(40.0, 32.75, 21.0, 32.75), (21.0, 32.75, 21.0, 34.45), (21.0, 34.45, _op("M16")[0], 34.45)]
    br += [(40.0, 33.85, 35.6, 33.85)]
    for c in ("E09a", "E09b", "E09c"):
        x, y = _op(c)
        br.append((x, 33.85, x, y))
    br += [(40.0, 33.85, 58.0, 33.85)]
    for c in ("B04", "A06", "B06", "A07", "B07"):
        x, y = _op(c)
        br.append((x, 33.85, x, y))
    br += [(40.3, 33.85, 40.3, 39.65), (40.3, 39.65, 17.8, 39.65)]
    for c in ("M08", "M09", "M11"):
        x, y = _op(c)
        br.append((x, 39.65, x, y))
    H.append(("Láseres, cúpulas, unión y PH (N2-N4)", [(38.0, Y_PP), (40.0, Y_PP), (40.0, 33.85)], br))
    # granallado y defectos (N5) y pintura: por la calle PO-5
    br = [(69.3, 33.85, 77.5, 33.85)]
    for c in ("B08", "B09"):
        x, y = _op(c)
        br.append((x, 33.85, x, y))
    br += [(77.5, 33.85, 79.2, 33.85), (79.2, 33.85, 79.2, 35.2), (79.2, 35.2, _op("B10")[0], _op("B10")[1])]
    br += [(69.3, Y_PP, 75.3, Y_PP), (75.3, Y_PP, 75.3, _op("P01")[1]), (75.3, _op("P01")[1], *_op("P01"))]
    br += [(75.3, _op("P01")[1], 75.3, _op("P04")[1]), (75.3, _op("P04")[1], *_op("P04"))]
    br += [(75.3, _op("P04")[1], 75.3, _op("P08")[1]), (75.3, _op("P08")[1], *_op("P08"))]
    H.append(("Granallado, defectos y pintura (N5, S-P)", [(38.0, Y_PP), (69.3, Y_PP), (69.3, 33.85)], br))
    # terminación y PT: bajan cruzando el pasillo y el almacén de cilindros
    br = [(61.0, 7.6, 52.52, 7.6), (52.52, 7.6, 52.52, _op("T08")[1]), (52.52, 7.6, 52.52, _op("T10")[1]),
          (61.0, 7.6, 65.9, 7.6), (65.9, 7.6, _op("T01")[0], _op("T01")[1])]
    for c in ("T03", "T04", "T05", "T07"):
        x, y = _op(c)
        br.append((x, 7.6, x, y))
    br.append((49.0, Y_PP, 49.0, 18.8))
    for c in ("Q", "QR", "SUP", "PCP"):                  # entran por su puerta
        r = next(s_.rect for s_ in SECTORES if s_.cod == c)
        _a, _b = next((a_, b_) for ld, a_, b_, t in CERRADOS[c] if ld == "S" and t == "puerta")
        br.append(((_a + _b) / 2, Y_PP, (_a + _b) / 2, r.y0 + 0.6))
    H.append(("Terminación, calidad y expedición", [(38.0, Y_PP), (61.0, Y_PP), (61.0, 7.6)], br))
    # carros: entran por el oeste a la calle interior de la U
    br = []
    for c in ("C01", "C02", "C03", "C05", "C06", "C07"):
        x, y = _op(c)
        br.append((x, 15.6, x, y))
    _x13 = 32.45                                         # puerta norte de S-TC
    br += [(34.3, Y_PP, 34.3, 7.6), (34.3, 7.6, _x13, 7.6), (_x13, 7.6, _x13, _op("T13")[1]),
           (_x13, _op("T13")[1], _op("T12")[0], _op("T12")[1]),
           (_op("T12")[0], _op("T12")[1], _op("T02")[0], _op("T12")[1]),
           (_op("T02")[0], _op("T12")[1], _op("T02")[0], _op("T02")[1])]       # entra a SP-2 por la cortina
    H.append(("Línea de carros (S3)", [(0.0, Y_PP), (20.6, Y_PP), (20.6, 15.6), (33.0, 15.6)], br))
    # recargas
    H.append(("Recargas (RC)", [(17.1, Y_PP), (17.1, 18.8), (17.1, 6.3)],
              [(17.1, 6.3, 1.0, 6.3), (17.1, 12.5, 1.0, 12.5)]))
    return H


# ============================================================ LOCALES
# Servicios SV (x -18..0, y 19..35). Circuito: ingreso SV-1 -> hall y fichado -> pasillo limpio (PL) ->
# vestuario -> duchas o sanitarios (sólo desde el vestuario) -> pasillo limpio -> PP-1 -> senda de la nave.
# Al sur del pasillo: limpieza, higiene y seguridad (con EPP y primeros auxilios), hall y administración, que
# remata contra la nave con una ventana a lo largo del pasillo central. El pasillo vertical PS lleva al
# sanitario accesible y al comedor y termina en la salida de emergencia SV-2.
LOCALES = [
    Sector("SV-LU", "Utilitarios de limpieza", R(-17.9, 19.1, -15.2, 22.9), "SERV", "común",
           "Pileta de lavado, carros, máquina de piso y artículos de limpieza (ex primeros auxilios)"),
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
    # sanitarios de planta (este): sólo hombres y mujeres, a menos de 25 m de pintura, terminación y PT
    Sector("SN-H", "Sanitarios hombres (planta)", R(72.0, 13.0, 74.4, 19.0), "SERV", "común",
           "2 inodoros (pared norte), 2 mingitorios (pared este) y 2 lavabos (pared sur)"),
    Sector("SN-M", "Sanitario mujeres (planta)", R(72.0, 9.8, 74.4, 12.8), "SERV", "común", "1 inodoro y lavabo"),
    # recargas RC (x 0,3..18, y 0,3..19,2): entran y salen los equipos por P2; recorrido en U
    Sector("RC-RD", "Recepción y despacho (portón P2)", R(0.5, 0.5, 5.8, 5.4), "RC", "RC",
           "Mostrador de recepción y de despacho junto al portón: clasificación en 4 colas e inspección visual; "
           "los equipos recargados vuelven por el corredor sur"),
    Sector("RC-DE", "Desarme y lavado", R(6.0, 0.5, 11.8, 5.4), "RC", "RC"),
    Sector("RC-DC", "Descarga y ensayo de funcionamiento", R(12.0, 0.5, 17.8, 5.4), "RC", "RC",
           "Sala con extracción y recuperación de polvo"),
    Sector("RC-C1", "Corredor de recargas (sur)", R(0.5, 5.6, 17.8, 7.0), "CIRC", "RC"),
    Sector("RC-GA", "CO₂ y agente limpio", R(0.5, 7.2, 4.2, 11.6), "RC", "RC", "Trasvasador y balanza", 15.0),
    Sector("RC-PV", "Recinto de polvo (HR ≤ 70 %)", R(4.4, 7.2, 11.8, 11.6), "RC", "RC",
           "Carga ABC, BC y D; 8 renovaciones por hora; sin estufas", 32.0),
    Sector("RC-PH", "PH con jaula, secado y Puffer", R(12.0, 7.2, 16.2, 11.6), "RC", "RC", "", 18.0),
    Sector("RC-C2", "Corredor de recargas (centro)", R(0.5, 11.8, 16.4, 13.2), "CIRC", "RC"),
    Sector("RC-CN", "Conector al pasillo central", R(16.4, 5.6, 17.8, 18.8), "CIRC", "RC"),
    Sector("RC-IR", "Inutilizados y residuos", R(0.5, 13.4, 4.2, 15.8), "RC", "RC", "", 8.0),
    Sector("RC-CQ", "Calidad de recargas (IRAM 3517-2)", R(0.5, 16.0, 4.2, 18.6), "RC", "RC",
           "Patrones con calibración vigente (manómetros, pesas, calibres de rosca), contraste mensual de "
           "instrumentos, mufla, cámara de inspección, freezer y sistema de trazabilidad", 9.0),
    Sector("RC-EN", "Ensamblaje, presurización, peso, hermeticidad y retoque", R(4.4, 13.4, 11.8, 18.6), "RC",
           "RC", "Buffer de válvulas, manómetros y pescantes de recargas en cajas", 38.0),
    Sector("RC-LQ", "Líquidos", R(12.0, 13.4, 16.2, 15.8), "RC", "RC", "Agua, AFFF y clase K", 10.0),
    Sector("RC-RP", "Etiquetado y flota de intercambio", R(12.0, 16.0, 16.2, 18.6), "RC", "RC"),
]

PUERTAS_ANEXOS = [
    ("SV-1", (-9.8, 19.0), (-8.2, 19.0), "peatonal", "Ingreso de personal y visitas (camino peatonal desde G4)"),
    ("SV-2", (-6.8, 35.0), (-5.8, 35.0), "peatonal", "Salida de emergencia al final del pasillo PS"),
    ("SV-3", (-14.6, 19.0), (-13.6, 19.0), "peatonal", "Higiene y seguridad: salida a ambulancia"),
]

# ============================================================ MOBILIARIO (ningún local vacío)
Mb = Mueble
MOBILIARIO = [
    # ---- SV-LU utilitarios de limpieza (ex primeros auxilios)
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
    # ---- QR cuarentena y muestras retenidas
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
    # ---- SC compresores y colectores: tablero y estante de repuestos
    Mb("tablero_el", R(63.9, 42.95, 65.5, 43.55), "S", 2),
    # ---- ST-I tableros y compresor de la cabina
    Mb("tablero_el", R(70.3, 30.6, 74.3, 31.35), "S", 4), Mb("compresor", R(70.4, 27.0, 73.4, 28.4), "N"),
    Mb("estanteria", R(75.6, 25.0, 76.15, 28.0), "O"),
    # ---- QP pintura electrostática
    Mb("pallets", R(81.0, 29.6, 83.6, 31.3), "S", 2), Mb("pallets", R(81.0, 25.0, 83.6, 26.4), "N", 2),
    Mb("estanteria", R(85.0, 25.0, 87.5, 25.5), "N"), Mb("lavaojos", R(83.9, 25.0, 84.5, 25.6), "N"),
    # ---- GR granalla
    Mb("pallets", R(67.8, 42.3, 74.0, 43.5), "S", 0), Mb("estanteria", R(74.2, 42.9, 75.9, 43.55), "S"),
    # ---- DL ducha de emergencia y lavaojos
    Mb("ducha_emergencia", R(72.4, 7.4, 73.6, 8.6), "S"), Mb("lavaojos", R(73.75, 8.9, 74.35, 9.5), "O"),
    # ---- expedición: rampa del muelle, embalaje y nafta de los autoelevadores
    Mb("rampa", R(40.6, 0.35, 43.6, 2.35), "S"), Mb("pallets", R(37.65, 0.4, 40.35, 2.3), "N", 0),
    Mb("estanteria", R(43.9, 1.75, 46.9, 2.3), "N"), Mb("estanteria", R(47.0, 1.75, 49.95, 2.3), "N"),
    Mb("pallets", R(44.0, 0.4, 49.9, 1.6), "N", 1),
    Mb("inflamables", R(34.5, 1.55, 35.7, 2.3), "N"), Mb("estanteria", R(35.9, 1.75, 37.35, 2.3), "N"),
    Mb("inflamables", R(0.5, 21.8, 1.85, 22.9), "E"), Mb("estanteria", R(0.5, 21.15, 1.85, 21.6), "E"),
    # ---- AL-C pallets de cilindros vendidos
    Mb("pallets", R(50.4, 12.6, 60.4, 15.3), "S", 1), Mb("pallets", R(50.4, 16.7, 60.4, 18.6), "N", 1),
    # ---- sanitarios de planta: inodoros, mingitorios y lavabos cada uno sobre su pared
    Mb("inodoro", R(72.05, 17.5, 74.35, 18.95), "S", 2), Mb("mingitorios", R(73.95, 14.2, 74.35, 15.4), "O", 2),
    Mb("lavabos", R(72.6, 13.05, 73.8, 13.55), "N", 2),
    Mb("inodoro", R(73.2, 11.3, 74.35, 12.75), "S", 1), Mb("lavabos", R(73.75, 9.85, 74.35, 10.45), "O", 1),
    # ---- recargas: inutilizados, calidad 3517-2, buffer de ensamblaje y embalaje de despacho
    Mb("jaula", R(0.6, 13.5, 2.6, 15.7), "E"), Mb("cilindros_piso", R(0.75, 13.7, 2.4, 15.5), "E", 0),
    Mb("tambores", R(2.8, 14.3, 4.1, 15.7), "O", 2),
    Mb("mesa_lab", R(0.55, 17.9, 2.6, 18.55), "S"), Mb("balanza_lab", R(2.8, 17.95, 3.4, 18.55), "S"),
    Mb("estanteria", R(3.65, 17.4, 4.15, 18.5), "O"), Mb("heladera", R(0.55, 16.05, 1.25, 16.75), "N"),
    Mb("escritorio", R(1.6, 16.05, 3.2, 17.2), "N"),
    Mb("estanteria", R(11.35, 16.0, 11.75, 17.1), "O"),
    Mb("estanteria", R(5.35, 2.9, 5.75, 4.1), "O"),
]

# puertas interiores de una hoja: (x, y, ancho, muro 'h'/'v', abre +1/-1)
PUERTAS_INT = [
    # bloque de servicios
    (-16.1, 22.9, 0.8, "h", -1), (-11.5, 22.9, 0.8, "h", -1), (-8.4, 22.9, 0.8, "h", -1), (-7.5, 19.9, 0.9, "v", 1),
    (-1.0, 22.9, 0.8, "h", -1), (-14.6, 24.6, 0.9, "h", 1), (-8.4, 24.6, 0.8, "h", 1), (-16.6, 28.3, 0.8, "h", 1),
    (-12.4, 28.3, 0.8, "h", 1), (-10.0, 27.7, 0.7, "h", 1), (-8.1, 27.7, 0.7, "h", 1), (-7.0, 33.4, 0.9, "v", 1),
    (-5.6, 25.3, 0.9, "v", 1),
    # sanitarios de planta
    (72.0, 15.6, 0.9, "v", 1), (72.0, 10.6, 0.8, "v", 1),
    # recargas: cada sala abre a un corredor
    (4.6, 5.5, 0.9, "h", 1), (8.5, 5.5, 0.9, "h", 1), (14.4, 5.5, 0.9, "h", 1), (2.2, 7.1, 0.9, "h", -1),
    (7.5, 7.1, 0.9, "h", -1), (16.3, 9.0, 0.9, "v", -1), (3.0, 13.3, 0.9, "h", 1), (10.2, 13.3, 0.9, "h", 1),
    (14.4, 13.3, 0.9, "h", 1), (16.3, 16.6, 0.9, "v", -1), (4.3, 16.1, 0.8, "v", -1),
]

# ============================================================ LOCALES CERRADOS DENTRO DE LA NAVE
# tabique en todo el perímetro (salvo donde coincide con el cerramiento de la nave) y sus aberturas:
# (lado, desde, hasta, tipo): puerta (hoja 0,90), porton (corredizo), cortina (lamas de PVC, pasa material),
# ventanilla (mostrador, no es paso), ventana (vidrio a la planta, no es paso)
CERRADOS = {
    "AL-GS": [("E", 39.2, 42.8, "porton")],
    "MT": [("S", 43.4, 45.4, "porton"), ("N", 41.5, 42.4, "puerta"), ("N", 46.0, 48.6, "ventana")],
    "PÑL": [("S", 41.5, 42.4, "puerta"), ("O", 30.6, 32.2, "ventanilla")],
    "Q": [("S", 52.6, 53.5, "puerta"), ("N", 50.0, 56.4, "ventana"), ("S", 50.0, 52.2, "ventana")],
    "QR": [("S", 58.5, 59.5, "puerta")],
    "SUP": [("S", 62.0, 62.9, "puerta"), ("N", 61.5, 63.9, "ventana"), ("S", 63.2, 64.0, "ventana")],
    "PCP": [("S", 66.2, 67.1, "puerta"), ("N", 64.8, 68.0, "ventana"), ("S", 64.6, 65.9, "ventana")],
    "ST-I": [("O", 25.2, 26.8, "porton")],
    "QP": [("N", 84.9, 86.3, "porton"), ("S", 86.6, 87.5, "puerta"), ("O", 28.0, 29.0, "puerta")],
    "SP-1": [("O", 5.0, 6.4, "cortina"), ("N", 66.0, 67.2, "cortina"), ("O", 7.25, 8.15, "puerta"),
             ("O", 1.9, 4.2, "porton")],
    "SP-2": [("N", 26.0, 27.4, "cortina"), ("E", 2.2, 4.6, "cortina"), ("N", 23.0, 23.9, "puerta")],
    "S-TC": [("O", 2.2, 4.6, "cortina"), ("N", 32.0, 32.9, "puerta"), ("E", 2.4, 4.4, "cortina")],
    "SC": [("S", 56.0, 56.9, "puerta"), ("S", 49.0, 50.6, "porton")],
    "GR": [("S", 70.6, 72.0, "porton")],
}

# ============================================================ PROTECCIÓN CONTRA INCENDIO Y SEÑALIZACIÓN
# bocas de incendio equipadas (manguera 25 m + chorro 5 m): cubren toda la nave desde las calles
BIE = [(8.0, 23.0), (30.0, 23.0), (52.0, 23.0), (73.0, 23.0), (30.0, 39.7), (55.0, 39.9), (80.0, 39.9),
       (22.0, 7.6), (56.0, 8.0), (80.0, 2.0), (9.0, 12.4)]
# pulsadores manuales de alarma junto a cada salida y sirena con luz estroboscópica
PULSADORES = [(7.0, 43.3), (3.2, 43.3), (30.5, 43.3), (47.4, 43.3), (66.5, 43.3), (77.0, 43.3), (87.3, 40.0),
              (87.3, 27.5), (86.5, 0.7), (59.1, 0.7), (15.2, 0.7), (2.2, 0.7), (0.7, 6.3), (0.7, 23.8), (42.1, 2.6)]


def _senales():
    """Señalética (IRAM 10005-1 colores y formas; Dec. 351/79): (tipo, código, x, y, texto).
    tipo: obl (azul, círculo), adv (amarilla, triángulo), pro (roja, círculo con barra), sal (verde, rectángulo),
    inc (roja, cuadrado)."""
    S = []
    # salidas: sobre cada puerta de emergencia y portón, y flechas a lo largo del pasillo central
    for p in PUERTAS:
        if p.tipo in ("emergencia", "peatonal") or p.cod in ("P1", "P2", "P3"):
            m = (p.a + p.b) / 2
            xy = {"N": (m, NAVE_A - 0.9), "S": (m, 0.9), "O": (0.9, m), "E": (NAVE_L - 0.9, m)}[p.muro]
            S.append(("sal", "SALIDA", *xy, "Salida"))
    for x in range(6, 72, 12):
        S.append(("sal", "->", float(x), 21.1, "Recorrido de evacuación"))
    # obligación de EPP por puesto
    auditiva = ("M04", "M08", "B08", "M15", "M16", "C01")
    careta = ("B03", "A06", "B06", "M11", "M12", "C02", "C03", "C04", "C05", "B10")
    respirador = ("P04", "T01", "T02", "B08")
    for e in EQUIPOS:
        x, y = e.rect.x1 + 0.35, e.rect.y1 + 0.35
        if e.cod in auditiva:
            S.append(("obl", "OÍDOS", x, y, "Protección auditiva"))
        if e.cod in careta:
            S.append(("obl", "CARETA", x, y - 0.75 if e.cod in auditiva else y, "Careta fotosensible y guantes"))
        if e.cod in respirador:
            S.append(("obl", "RESP", e.rect.x0 - 0.35, y, "Respirador P2"))
    S.append(("obl", "CALZADO", 1.2, 25.0, "Calzado de seguridad y ropa de trabajo (ingreso a planta)"))
    # advertencias
    for x, y in ((7.3, 24.9), (10.9, 41.0), (40.0, 6.3), (34.0, 21.1), (60.0, 21.1)):
        S.append(("adv", "AUTOELEV", x, y, "Circulación de autoelevadores"))
    for x, y in ((70.4, 31.0), (39.0, 44.6), (36.3, 47.8)):
        S.append(("adv", "ELECT", x, y, "Riesgo eléctrico"))
    for x, y in ((83.0, 10.2), (86.0, 10.2)):
        S.append(("adv", "CALOR", x, y, "Superficie caliente (hornos)"))
    for x, y in ((81.2, 31.0), (3.2, 42.0), (64.8, 9.0), (49.0, 42.9)):
        S.append(("adv", "INFLAM", x, y, "Inflamables / gases a presión"))
    for x, y in ((19.8, 38.3), (12.5, 37.6), (26.0, 18.6)):
        S.append(("adv", "ATRAP", x, y, "Riesgo de atrapamiento / cargas suspendidas"))
    # prohibiciones
    for x, y in ((75.0, 23.0), (68.0, 11.5), (27.5, 7.5), (84.0, 30.8), (48.0, 44.6)):
        S.append(("pro", "FUMAR", x, y, "Prohibido fumar y llama abierta"))
    for x, y in ((3.8, 25.2), (10.9, 25.2), (36.0, 18.3), (43.0, 18.3)):
        S.append(("pro", "PEATON", x, y, "Prohibido el paso de peatones (calle de autoelevador)"))
    # información y salvamento
    for x, y in ((-12.4, 22.4), (73.0, 9.9), (82.6, 26.0), (40.5, 31.5)):
        S.append(("sal", "+", x, y, "Primeros auxilios / lavaojos"))
    S.append(("sal", "REUNIÓN", 28.0, -30.0, "Punto de reunión"))
    S.append(("sal", "PLANO", 0.9, 24.0, "Plano de evacuación (ingreso PP-1)"))
    return S


SENALES = _senales()

# función de cada portón, rotulada en todos los planos (qué entra o sale, nunca un código suelto)
USO_CORTO = {
    "P1": "MP: hojas, flejes, caños, cuellos, alambre y gases; sale scrap", "P2": "Recargas: utilitarios",
    "P3": "Muelle único: sale PT y carros; entran revendidos, válvulas, embalaje, polvos y N₂",
    "P4": "Pintura electrostática y granalla", "PP-1": "Personal", "PG": "Cambio de baterías de gas",
}

# fondos de calle admitidos: la calle muere contra lo que sirve (rack, armario, último puesto), no contra un muro
FONDOS = {
    ("PC", "O"): "armario de nafta e insumos del autoelevador de MP (AL-1N); el autoelevador dobla a A1",
    ("A1", "N"): "respaldo del cantiléver de caños (calle de rack)",
    ("PO-T", "O"): "último puesto de terminación (22 etiquetado); se entra por PO-AC o por la puerta de SP-1",
}

# ============================================================ ESPACIOS LIBRES (a debatir)
LIBRES = [
    ("LB-1", R(78.0, 40.8, 87.6, 43.6), "Libre 26,9 m² sobre la calle norte: la granalla pasó junto a la "
     "granalladora y el archivo de calidad se repartió entre calidad y cuarentena"),
]

# ============================================================ IMPLANTACIÓN
LM_Y = TERRENO[1]
RETIRO_FRENTE = 10.0

EXTERIOR = [
    ("PL-N", "Alero de descarga de MP (semi 18,6 m y chasis)", R(-1.0, 44.4, 31.0, 56.0), "playa"),
    ("VQ-N", "Volquete de scrap 6 m³ junto a P1", R(-0.8, 44.8, 3.2, 47.6), "volquete"),
    ("PM", "Playa de maniobra del muelle P3 (semi 18,6 m)", R(32.0, -26.0, 54.0, 0.0), "playa"),
    ("PE", "Playa de descarga de P4 (pintura y granalla)", R(88.0, 22.0, 119.0, 33.0), "playa"),
    ("PU", "Playa de utilitarios frente a P2 (recargas)", R(-1.0, -6.0, 8.0, 0.0), "playa"),
    ("ERM", "Estación de regulación y medición de gas natural (hornos y secadoras)", R(88.6, 4.0, 91.6, 7.0),
     "gas"),
    ("RI", "Reserva de agua contra incendio y bombas", R(100.0, 34.0, 110.0, 44.0), "incendio"),
    ("AMP", "Reserva de ampliación (nave hacia el este)", R(92.0, -8.0, 114.0, 21.0), "reserva"),
    ("PTE", "Tratamiento de efluentes líquidos", R(64.0, -27.0, 76.0, -19.0), "efluentes"),
    ("EST", "Estacionamiento de personal (38 + 2 accesibles)", R(-12.0, -50.0, 40.0, -28.0), "estac"),
    ("EU", "Utilitarios de reparto y recargas (8)", R(-15.0, -16.0, -1.0, -6.0), "estac"),
    ("GAR", "Garita: control de camiones (G1), autos (G2) y peatones (G4); CCTV", R(-28.5, -61.5, -23.5, -57.0),
     "garita"),
    ("BAL", "Báscula de camiones de 18 m (entrada)", R(-35.5, -50.0, -29.5, -32.0), "balanza"),
    ("PR", "Punto de reunión (evacuación)", R(-27.5, -30.0, -21.5, -24.0), "reunion"),
    ("MT", "Celda de medición de media tensión", R(-39.6, -30.0, -36.4, -24.0), "elec"),
    ("ERP", "Estación reductora de gas", R(126.5, -60.0, 129.5, -56.0), "gas"),
]
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
    Flujo("EFL-L", [(84.0, 10.6), (84.0, 9.9), (88.4, 9.9), (88.4, 0.0), (74.0, -19.0)], "Pretratamiento de pintura"),
    Flujo("EFL-L", [(52.4, 35.4), (52.4, 34.0), (61.8, 34.0), (61.8, 0.6), (70.0, -19.0)], "Agua de PH 1-10 kg"),
    Flujo("EFL-L", [(56.0, 35.4), (56.0, 34.0)], "Agua de PH 1-10 kg"),
    Flujo("EFL-L", [(21.2, 11.8), (21.2, 10.6), (34.2, 10.6), (34.2, 0.6), (61.8, 0.6)], "Agua de PH de carros"),
    Flujo("EFL-L", [(15.0, 9.4), (15.0, 0.6), (18.2, 0.6)], "Lavado y PH de recargas"),
    Flujo("EFL-L", [(70.0, -27.0), (70.0, -62.0)], "Vuelco a colectora (previa autorización)"),
]
RC_FLUJO = [(3.3, -6.0), (3.3, 0.0), (3.3, 3.0), (8.9, 3.0), (14.9, 3.0), (14.9, 9.4), (8.1, 9.4), (8.1, 15.6),
            (14.1, 15.6), (14.1, 17.8), (17.1, 17.8), (17.1, 6.3), (5.05, 6.3), (5.05, 4.0), (1.2, 4.0), (1.2, 0.0),
            (1.2, -6.0)]

EMISIONES = [
    (21.6, 41.1, "Humos de soldadura de cuellos"), (32.2, 17.4, "Humos de soldadura de carros"),
    (28.1, 13.1, "Humos de soldadura de carros"), (36.9, 27.2, "Humos de soldadura longitudinal"),
    (43.8, 36.1, "Humos de soldadura circunferencial"), (46.8, 36.1, "Humos de soldadura circunferencial"),
    (72.3, 38.6, "Colector de la granalladora"), (84.0, 6.8, "Chimenea horno de secado"),
    (73.1, 6.4, "Chimenea horno de polimerizado"), (78.6, 5.2, "Ciclones de la cabina"),
    (68.4, 11.2, "Extracción sala de polvo 1-10 kg"), (24.0, 2.1, "Extracción sala de polvo carros"),
    (21.9, 31.1, "Humos de corte láser"), (8.1, 9.2, "Extracción recinto de polvo de recargas"),
    (62.0, 36.0, "Chimenea secadoras"), (81.1, 36.4, "Humos de corrección"),
]


# ============================================================ sendas (cruces hilo-flujo señalizados)
def _sendas():
    from shapely.geometry import LineString
    fl = [LineString(f.pts) for f in FLUJOS]
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
    (2.0, 5.6, "autoelevador sale del almacén de MP por A1 (circuito de sentido único A2 -> A1)"),
    (9.1, 12.7, "autoelevador entra al almacén de MP por A2"),
    (18.8, 20.4, "autoelevador retira el scrap de la guillotina"),
    (16.6, 17.8, "personal a recargas"),
    (20.0, 21.2, "personal a carros"),
    (24.6, 26.0, "carros de cuerpos a la zona de carros"),
    (33.7, 34.9, "personal a terminación de carros"),
    (41.4, 44.4, "transpaleta a mantenimiento"),
    (48.4, 49.6, "personal a PT y expedición"),
    (60.4, 61.6, "personal a terminación"),
]


def _defensas():
    tramos, x = [], 0.3
    for a, b, _ in sorted(ABERTURAS):
        if a > x:
            tramos.append((x, a))
        x = b
    if x < 69.8:
        tramos.append((x, 69.8))
    return tramos


DEFENSAS = _defensas()
for _a, _b, _t in ABERTURAS:
    if _t.startswith("personal"):
        SENDAS.append((f"X{len(SENDAS) + 1}", R(_a, 19.2, _b, 23.0), "Senda peatonal: " + _t +
                       " (cruza el carril de autoelevador)"))
