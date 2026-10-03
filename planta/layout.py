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
    Pasillo("PC", R(0.3, 19.2, 74.4, 23.0), "PM", 3.8,
            "Pasillo central: autoelevador 3,0 t doble sentido (2 × 1,25 m + 3 × 0,40 m de huelgo)"),
    Pasillo("PP", R(0.3, 23.2, 74.4, 24.4), "PP", 1.2,
            "Senda peatonal separada del carril de autoelevador por una defensa con aberturas en las sendas"),
    Pasillo("A2", R(9.1, 24.6, 12.7, 41.8), "PM", 3.6,
            "Calle de autoelevador de abastecimiento: paquetes y rollos (oeste) -> mesa elevadora y desbobinador (este)"),
    Pasillo("A1", R(2.0, 24.6, 5.6, 41.8), "PM", 3.6,
            "Calle de autoelevador de depósito: pañol de insumos pesados y scrap (oeste), rollos de fleje (este)"),
    Pasillo("AN", R(0.3, 41.9, 12.7, 43.6), "PM", 1.7,
            "Cabecera norte del almacén: une A1 y A2 con P1 (MP) y P2 (scrap); giro del autoelevador"),
    Pasillo("PO-1", R(39.4, 24.6, 41.0, 34.4), "PO", 1.6, "Calle de operarios y carros de pulmón (N1 -> N4)"),
    Pasillo("PO-1N", R(39.85, 34.4, 40.75, 39.15), "PO", 0.9, "Paso de operarios entre encastre y bordoneado"),
    Pasillo("PO-2", R(30.0, 33.3, 82.6, 34.4), "PO", 1.1,
            "Calle de carros de la línea principal: empieza a 1,0 m del frente de las máquinas (espalda libre)"),
    Pasillo("PO-5", R(68.6, 24.6, 70.0, 33.3), "PO", 1.4,
            "Calle de la senda peatonal a la línea este (granallado, defectos) sin atravesar locales"),
    Pasillo("PO-3", R(12.8, 39.15, 41.0, 40.15), "PO", 1.0, "Calle de operarios de cúpulas y cuellos (N3)"),
    Pasillo("PO-L", R(12.8, 32.05, 30.4, 33.45), "PO", 1.4,
            "Calle del carro porta-tubos de 6 m: gira desde A2 porque (3,6^(2/3) + 1,4^(2/3))^(3/2) = 7,4 m > 6,5 m"),
    Pasillo("PO-LK", R(29.2, 33.45, 30.4, 33.7), "PO", 1.2, "Unión de la calle de los láseres con PO-2"),
    Pasillo("PO-4", R(41.0, 39.4, 87.6, 40.6), "PO", 1.2,
            "Calle norte: pañol de línea, escuelita, muestras y granalla; salidas SE-2, SE-3 y SE-4"),
    Pasillo("PO-E", R(84.6, 31.6, 87.4, 39.4), "PO", 2.8, "Calle de transpaleta: P3 -> granalla (GR)"),
    Pasillo("PO-P", R(70.2, 4.6, 71.8, 19.2), "PO", 1.6,
            "Calle este: carros de pintados (descarga -> PU-9) y acceso al núcleo sanitario"),
    Pasillo("PO-P2", R(71.8, 4.6, 74.6, 6.6), "PO", 2.0, "Salida de la descarga de pintura a la calle este"),
    Pasillo("T1", R(35.5, 6.8, 38.8, 18.8), "PM", 3.3,
            "Calle de rack de PT (oeste): pasillo central <-> calle de expedición; columna B-6 fuera de la boca"),
    Pasillo("T2", R(41.2, 6.8, 44.5, 18.8), "PM", 3.3, "Calle de rack de PT (centro): pasillo central <-> expedición"),
    Pasillo("T3", R(45.8, 6.8, 47.7, 18.8), "PM", 1.9,
            "Calle de apiladora: envolvedora -> rack RK3 -> expedición (apiladora de conductor acompañante)"),
    Pasillo("EX", R(34.2, 2.4, 50.0, 6.8), "PM", 4.4,
            "Calle de expedición: une las 3 calles del rack con las rampas de M3, M1 y M2"),
    Pasillo("AT", R(50.2, 1.9, 62.0, 4.2), "PM", 2.3, "Calle de abastecimiento de terminación (transpaleta)"),
    Pasillo("PO-T", R(53.2, 7.2, 62.0, 8.2), "PO", 1.0, "Calle de operarios de terminación"),
    Pasillo("PO-AC", R(60.6, 8.2, 61.8, 19.2), "PO", 1.2,
            "Calle del pasillo central a terminación a través del almacén de cilindros"),
    Pasillo("RC-P", R(0.5, 5.6, 17.8, 7.0), "PO", 1.4, "Corredor de recargas (sur)"),
    Pasillo("RC-Q", R(0.5, 11.8, 16.2, 13.2), "PO", 1.4, "Corredor de recargas (centro)"),
    Pasillo("RC-N", R(16.4, 7.0, 17.8, 18.8), "PO", 1.4, "Conector de recargas al pasillo central"),
]

# sendas peatonales: se calculan al final del módulo en cada cruce de un hilo con un flujo
SENDAS = []

# ============================================================ SECTORES
SECTORES = [
    # ---------------- banda norte: almacén de MP (oeste)
    Sector("PÑ", "Pañol de insumos pesados", R(0.4, 24.8, 1.9, 37.8), "MP", "común",
           "Rack de pallets 3 niveles (5 módulos × 2 × 3 = 30 posiciones): alambre MIG, cuplas, asientos, tapones",
           35.2),
    Sector("SCR", "Scrap: basculantes a volquete", R(0.4, 38.0, 1.9, 41.7), "AUX", "común",
           "El autoelevador vuelca los basculantes en el volquete del alero por P2; el chatarrero no entra"),
    Sector("AL-1F", "Rollos de fleje", R(5.7, 24.8, 7.2, 41.7), "MP", "común",
           "Rack porta-flejes 2 niveles, 12 cunas × 2 = 24 rollos ≤ 1 t (8 anchos); se toman con gancho C"),
    Sector("AL-1H", "Paquetes de hojas por formato", R(7.4, 24.8, 9.0, 41.7), "MP", "común",
           "5 posiciones de 1,6 × 3,1 m a 4 alturas = 20 paquetes ≤ 2 t; un formato por posición; FIFO", 50.0),
    # ---------------- banda norte: línea convergente
    Sector("N1", "Corte y cuerpo 2,5-10 kg", R(12.8, 24.8, 38.8, 29.5), "PROD", "S2",
           "1 guillotina -> 2 numerado -> 3 cilindrado -> 4 soldadura longitudinal"),
    Sector("N2", "Corte de caño 1 kg", R(12.8, 29.7, 29.4, 35.8), "PROD", "S1",
           "5 corte láser de caño; caños desde el cantiléver del alero en carro porta-tubos"),
    Sector("N3", "Cúpulas, fondos y cuellos", R(12.8, 35.85, 30.0, 43.5), "PROD", "S1 / S2",
           "6 desbobinado + embutido -> 7 preparación de cuello -> 8 soldadura de cuello"),
    Sector("N4", "Unión y prueba hidráulica", R(34.6, 35.0, 66.6, 39.0), "PROD", "S1 / S2",
           "9 encastre -> 10 bordoneado -> 11 soldadura circ. -> 12 PH -> 13 secado"),
    Sector("N5", "Granallado y defectos", R(70.2, 34.8, 87.6, 39.3), "PROD", "S1 / S2",
           "14 granallado -> 15 detección de defectos -> 16 corrección"),
    Sector("Q", "Laboratorio de calidad", R(49.4, 24.8, 56.8, 29.4), "CAL", "común",
           "Metrología, espesor por ultrasonido, adherencia y espesor de pintura, niebla salina, humedad del "
           "polvo; probetas de soldadura (IRAM 3523 / 3550)", 31.0),
    Sector("QR", "Cuarentena y lotes retenidos", R(57.0, 24.8, 61.0, 29.4), "CAL", "común",
           "Jaula con llave: lotes rechazados y muestras", 15.0),
    Sector("SUP", "Supervisión de planta y PCP", R(61.2, 24.8, 65.4, 29.4), "AUX", "común",
           "Encargado de turno y PCP con ventana a la línea; tablero de gestión a la vista"),
    Sector("EPP", "EPP, botiquín y ducha lavaojos", R(65.6, 24.8, 68.4, 29.4), "AUX", "común",
           "Entrega de EPP contra vale; caretas fotosensibles de recambio"),
    Sector("MT", "Taller de mantenimiento", R(41.2, 24.8, 49.2, 29.4), "AUX", "común",
           "Bancos, torno, agujereadora, soldadora móvil y repuestos; entra la transpaleta desde el pasillo", 30.0),
    Sector("ESC", "Escalera y plataforma elevadora al entrepiso de oficinas (+3,50)", R(41.2, 29.6, 43.8, 33.2),
           "CIRC", "común", "Escalera en U de 1,10 m y plataforma elevadora 1,10 × 1,40 (Ley 24.314)"),
    Sector("PV", "Carros vacíos: supermercado de retorno", R(44.0, 29.6, 62.0, 33.2), "AUX", "común",
           "Cada carro vuelve vacío a su puesto de carga por PO-1 / PO-2; acá esperan los de reserva y los del "
           "milk run de abastecimiento"),
    # ---------------- franja norte (sobre la calle PO-4): apoyo a la línea
    Sector("PÑL", "Pañol de línea (ventanilla)", R(48.0, 40.8, 58.0, 43.6), "AUX", "común",
           "Alambre 0,9 / 1,2 mm, toberas, puntas, discos y EPP; entrega contra vale a 10 m de las soldadoras"),
    Sector("ES", "Escuelita de soldadura", R(58.2, 40.8, 65.6, 43.6), "AUX", "común",
           "3 cabinas con mampara y extracción: práctica y homologación de soldadores (cátedra)"),
    Sector("AR", "Muestras retenidas y archivo de calidad", R(67.6, 40.8, 76.0, 43.6), "CAL", "común",
           "Un cilindro testigo por lote y legajos de trazabilidad (IRAM 3517 / 3523)"),
    Sector("GR", "Granalla y repuestos de granallado y pintura", R(78.0, 40.8, 87.6, 43.6), "MP", "común",
           "Pallets de granalla (40 × 25 kg) junto a la granalladora; entran por P3 con transpaleta"),
    # ---------------- columna este: pintura y servicios de pintura
    Sector("S-P", "Pintura en polvo (esquema Electricolor 22 × 13 m)", R(74.6, 2.3, 87.6, 24.3), "PINT", "S1 / S2",
           "17 carga -> pretratamiento -> secado -> cabina -> polimerizado -> enfriamiento -> descarga"),
    Sector("QP", "Químicos y pintura en polvo", R(80.8, 24.8, 87.6, 31.4), "MP", "S1 / S2",
           "Batea ≥ 110 % del mayor envase; pintura en polvo < 30 °C; portón P3", 24.1),
    Sector("ST-I", "Tableros, compresor de pintura y colector", R(70.2, 24.8, 76.2, 31.4), "AUX", "común"),
    # ---------------- banda sur: terminación y almacén de cilindros
    Sector("AL-C", "Almacén de cilindros pintados", R(50.2, 12.4, 69.8, 18.8), "PT", "S1 / S2",
           "Pulmón de pintados antes de la carga de polvo y cilindros vendidos vacíos; estación de carga de "
           "baterías de autoelevador y apiladoras sobre el pasillo central"),
    Sector("SP-1", "Sala de carga de polvo", R(62.0, 0.3, 69.8, 12.2), "TERM", "S1 / S2",
           "Recinto HR ≤ 70 %, 8 renovaciones por hora, sin estufas (IRAM 3517-2); big bags a 2 alturas"),
    Sector("S-T", "Terminación 1-10 kg", R(50.2, 1.9, 61.8, 12.2), "TERM", "S1 / S2",
           "18 carga de polvo -> 19 ensamblaje -> 20 presurización -> 21 hermeticidad -> 22 etiquetado "
           "-> 23 embalaje -> 24 envolvedora"),
    Sector("AL-2", "Insumos de terminación y embalaje", R(50.2, 0.3, 62.0, 1.8), "MP", "S1 / S2",
           "Rack de 4 niveles a lo largo del muro sur; llega por el muelle M2 (sin portón propio)", 40.0),
    # ---------------- banda sur: PT
    Sector("AL-3", "Almacén de producto terminado", R(34.2, 6.8, 50.0, 18.8), "PT", "S1 / S2",
           "4 racks de 12 m × 4 niveles = 128 posiciones (req. 88)"),
    Sector("EXP", "Expedición y muelles", R(34.2, 0.3, 50.0, 6.8), "PT", "común",
           "Consolidación de pedidos frente a M1-M2"),
    Sector("S4", "Tercerizados revendidos", R(37.6, 0.3, 40.4, 2.35), "PT", "S4",
           "CO₂, agua, AFFF, clase K y agente limpio con sello IRAM: recepción por M3, control y stock"),
    # ---------------- banda sur: carros (U)
    Sector("S3", "Línea de carros 25-100 kg", R(18.2, 8.0, 34.0, 18.8), "PROD", "S3",
           "C1 cilindrado -> C2 punteo -> C3 soldadura long. -> C4 soldadura circ. -> C5 inspección -> C6 PH "
           "-> C7 marcado"),
    Sector("SP-2", "Sala de carga de polvo de carros", R(22.4, 0.3, 28.4, 7.8), "TERM", "S3",
           "Recinto HR ≤ 70 %: big bags propios y cabina de descarga de muestras (IRAM 3550)"),
    Sector("S-TC", "Terminación de carros", R(28.6, 0.3, 34.0, 7.8), "TERM", "S3",
           "C9 armado de ruedas y manguera -> C10 presurización y etiquetado"),
    Sector("PU-CP", "Carros a pintura tercerizada", R(18.2, 0.3, 22.2, 7.8), "PROD", "S3",
           "Espera de retiro del pintor (P6); vuelven pintados por P8"),
]
# ============================================================ EQUIPOS (paso = número de operación en el plano)
# fuente: C = cotización recibida (referencias/INVESTIGACION PROVEEDORES), E = estimado de catálogo
E_ = Equipo
EQUIPOS = [
    # ---------------- almacén de MP: contenido
    E_("PN1", "Rack de pallets del pañol (3 niveles)", Rw(0.45, 25.0, 1.4, 12.6), "PÑ", 0, fuente="E ARLOG",
       tipo="rack", frente="E"),
    E_("SC1", "Basculantes de scrap 1 m³", Rw(0.45, 38.2, 1.4, 3.4), "SCR", 0, fuente="E", tipo="contenedores",
       frente="E"),
    E_("RF1", "Porta-flejes 2 niveles (24 rollos)", Rw(5.75, 25.0, 1.4, 16.6), "AL-1F", 0, fuente="E MP Opción D",
       tipo="portaflejes", frente="O"),
    E_("HJ1", "Paquetes de hojas (5 pos. × 4 alturas)", Rw(7.45, 25.0, 1.5, 16.6), "AL-1H", 0, fuente="E",
       tipo="paquetes", frente="E"),
    # ---------------- N1: corte y cuerpo 2,5-10 kg (oeste -> este, eje y = 27,2); se carga desde A2
    E_("M02", "Mesa elevadora de tijera 3 t", Rw(12.9, 25.6, 1.2, 3.1), "N1", 0, 2.2, fuente="MP Manipulación",
       frente="O"),
    E_("M03", "Mesa de bolas", Rw(14.2, 25.5, 1.2, 3.2), "N1", 1, fuente="MP Manipulación", frente="N"),
    E_("M04", "Guillotina Molinari HG 6 × 3200", Rw(15.6, 25.2, 1.7, 3.9), "N1", 0, 7.5,
       fuente="C Molinari HG 6x3200 (largo 3200; huella de catálogo)", frente="O", paso="1"),
    E_("M05", "Mesa de salida", Rw(17.5, 25.6, 1.2, 3.1), "N1", 0, fuente="E", frente="O"),
    E_("B01", "Numerado de cuerpo", Rw(26.7, 26.8, 1.2, 0.8), "N1", 1, 0.5, fuente="E", paso="2"),
    E_("B01b", "Numerado de cuerpo", Rw(28.3, 26.8, 1.2, 0.8), "N1", 1, 0.5, fuente="E", paso="2"),
    E_("B02", "Cilindradora Bästlein 1050 × 1,8", Rw(31.8, 26.7, 1.7, 0.7), "N1", 1, 1.1,
       fuente="C Bästlein 1700 x 700", paso="3"),
    E_("B03", "Soldadura longitudinal automática", Rw(35.8, 26.4, 2.0, 1.4), "N1", 1, 12.0, polvo=True,
       fuente="C Firesafer (medida estimada)", paso="4"),
    # ---------------- N2: corte de caño 1 kg: láser - caballete - calle - caballete - láser
    E_("M15", "Láser de tubo Leapion 6012", Rw(13.6, 29.75, 6.85, 0.8), "N2", 0, 10.0, aire=True, polvo=True,
       fuente="C Leapion 6850 x 800", frente="N"),
    E_("CB2", "Caballete porta-tubos (1 día)", Rw(13.6, 31.55, 6.5, 0.5), "N2", 0, fuente="E", tipo="cantilever",
       frente="N"),
    E_("CB1", "Caballete porta-tubos (1 día)", Rw(13.6, 33.45, 6.5, 0.5), "N2", 0, fuente="E", tipo="cantilever",
       frente="S"),
    E_("M16", "Láser de tubo Leapion 6012", Rw(13.6, 34.95, 6.85, 0.8), "N2", 1, 10.0, aire=True, polvo=True,
       fuente="C Leapion 6850 x 800", frente="S"),
    # ---------------- N3: cúpulas, fondos y cuellos (se carga el rollo desde A2 con gancho C)
    E_("M06", "Desbobinador SHIMEQ (2 mandriles)", Rw(12.9, 36.2, 1.8, 2.0), "N3", 0, 2.2,
       fuente="C SHIMEQ D-S-9000", frente="O", paso="6"),
    E_("M07", "Enderezador y alimentador SHIMEQ", Rw(15.0, 36.6, 1.6, 1.2), "N3", 0, 2.2,
       fuente="C SHIMEQ D-S-9000", paso="6"),
    E_("M08", "Prensa PHM 300 t (mesa 1800 × 1300)", Rw(16.9, 35.9, 2.6, 2.2), "N3", 1, 37.0, aire=True,
       fuente="C PHM 300 (montantes + unidad hidráulica)", frente="N", paso="6"),
    E_("M09", "Preparación de cuello", Rw(17.2, 41.2, 1.2, 1.0), "N3", 1, 3.0, aire=True, fuente="E", paso="7"),
    E_("M10", "Preparación de cuello", Rw(18.8, 41.2, 1.2, 1.0), "N3", 0, 3.0, aire=True, fuente="E", paso="7"),
    E_("M11", "Soldadura circ. de cuello", Rw(20.8, 41.2, 1.6, 1.2), "N3", 1, 12.0, polvo=True, fuente="C FS-HFM1",
       paso="8"),
    E_("M12", "Soldadura circ. de cuello", Rw(22.8, 41.2, 1.6, 1.2), "N3", 0, 12.0, polvo=True, fuente="C FS-HFM1",
       paso="8"),
    # ---------------- N4: unión y prueba hidráulica (línea principal, eje y = 36,2)
    E_("E09a", "Encastre de fondo", Rw(35.0, 35.6, 1.2, 1.0), "N4", 1, 1.0, aire=True, fuente="E", paso="9"),
    E_("E09b", "Encastre de fondo", Rw(36.8, 35.6, 1.2, 1.0), "N4", 1, 1.0, aire=True, fuente="E", paso="9"),
    E_("E09c", "Encastre de fondo", Rw(38.6, 35.6, 1.2, 1.0), "N4", 1, 1.0, aire=True, fuente="E", paso="9"),
    E_("B04", "Bordoneadora", Rw(40.8, 35.7, 1.0, 0.8), "N4", 1, 2.2, fuente="C Bendmak SWM-400 (350 kg)", paso="10"),
    E_("A06", "Soldadura circ. cúpula y fondo", Rw(42.6, 35.4, 2.0, 1.4), "N4", 1, 15.0, polvo=True,
       fuente="C Getweld (posicionador + fuente MIG)", paso="11"),
    E_("B06", "Soldadura circ. cúpula y fondo", Rw(45.6, 35.4, 2.0, 1.4), "N4", 1, 15.0, polvo=True,
       fuente="C SCWelding Promotech PRO WP150 + fuente MIG", paso="11"),
    E_("A07", "Prueba hidráulica automática", Rw(50.8, 35.4, 2.4, 1.6), "N4", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A (medida estimada)", paso="12"),
    E_("B07", "Prueba hidráulica automática", Rw(54.4, 35.4, 2.4, 1.6), "N4", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A (medida estimada)", paso="12"),
    E_("B14", "Secadora de cilindros", Rw(60.0, 35.2, 4.0, 1.6), "N4", 0, 6.0, gas=True, fuente="E", paso="13"),
    E_("A11", "Secadora de cilindros", Rw(60.0, 37.2, 4.0, 1.6), "N4", 0, 6.0, gas=True, fuente="E", paso="13"),
    # ---------------- N5: granallado y defectos (columna este, arriba)
    E_("B08", "Granalladora de túnel", Rw(71.0, 35.4, 4.5, 1.3), "N5", 1, 15.0, polvo=True,
       fuente="C Airblast G-100 4500 x 1300", paso="14"),
    E_("B13", "Colector de polvo", Rw(71.4, 37.9, 1.8, 1.4), "N5", 0, 5.5, polvo=True, fuente="E"),
    E_("B09", "Detección de defectos", Rw(76.4, 35.8, 2.2, 1.2), "N5", 1, 0.5, fuente="E", paso="15"),
    E_("B10", "Corrección de defectos", Rw(80.0, 35.6, 2.2, 1.5), "N5", 1, 10.0, polvo=True, fuente="E",
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
    E_("P09", "Retoque y control de espesor", Rw(76.8, 7.0, 2.0, 1.4), "S-P", 0, fuente="E", frente="O"),
    # ---------------- terminación 1-10 kg (este -> oeste, eje y = 8,0)
    E_("T01", "Carga de polvo 1-10 kg", Rw(64.2, 4.6, 3.4, 2.0), "SP-1", 1, 3.0, aire=True, polvo=True,
       fuente="C Yukon M-000121 + estación de big bag", frente="N", paso="18"),
    E_("T15", "Deshumidificador y extracción", Rw(67.2, 10.6, 2.4, 1.2), "SP-1", 0, 6.0, fuente="E", frente="N"),
    E_("RKV", "Rack de big bags de polvo", Rw(68.6, 0.6, 1.1, 5.6), "SP-1", 0, fuente="E", forma="rack", frente="O"),
    E_("T03", "Ensamblaje de válvula", Rw(60.3, 4.8, 1.6, 1.2), "S-T", 1, 0.5, aire=True, fuente="E", frente="N",
       paso="19"),
    E_("T04", "Ensamblaje de válvula", Rw(58.5, 4.8, 1.6, 1.2), "S-T", 1, 0.5, aire=True, fuente="E", frente="N",
       paso="19"),
    E_("T05", "Presurización con N₂", Rw(56.7, 4.9, 1.5, 1.0), "S-T", 1, 0.5, n2=True, fuente="C Yukon M-000150",
       frente="N", paso="20"),
    E_("T06", "Hermeticidad", Rw(54.9, 4.9, 1.5, 1.0), "S-T", 0, 0.5, fuente="E", frente="N", paso="21"),
    E_("T07", "Etiquetadora semiautomática", Rw(53.1, 5.0, 1.2, 0.6), "S-T", 1, 0.5, fuente="C SISA", frente="N",
       paso="22"),
    E_("T08", "Embalaje y palletizado", Rw(50.5, 4.4, 1.6, 1.6), "S-T", 1, fuente="E", frente="E", paso="23"),
    E_("T09", "Embalaje y palletizado", Rw(50.5, 6.4, 1.6, 1.6), "S-T", 1, fuente="E", frente="E", paso="23"),
    E_("T10", "Palletizado de cilindros vendidos", Rw(50.5, 8.4, 1.6, 1.6), "S-T", 1, fuente="E", frente="E",
       paso="23"),
    E_("RKI", "Rack de insumos de terminación", Rw(50.6, 0.5, 7.6, 1.1), "AL-2", 0, fuente="E", forma="rack"),
    # ---------------- PT
    E_("T11", "Envolvedora de pallets", Rw(48.2, 8.2, 1.5, 3.0), "AL-3", 0, 1.5, fuente="C EDOS PS5", paso="24"),
    E_("RK1", "Rack RK1 pasante: PT (este) / casquetes (oeste)", Rw(34.3, 7.0, 1.1, 11.6), "AL-3", 0, fuente="E",
       forma="rack", frente="E"),
    E_("RK2", "Rack RK2 doble (4 módulos × 2 × 4 por cara)", Rw(38.9, 7.0, 2.2, 11.6), "AL-3", 0, fuente="E",
       forma="rack", frente="E"),
    E_("RK3", "Rack RK3 de alta rotación (4 × 2 × 4)", Rw(44.6, 7.0, 1.1, 11.6), "AL-3", 0, fuente="E",
       forma="rack", frente="E"),
    # ---------------- S3 carros (U: norte O -> E, centro E -> O, sale por P6 y vuelve por P8)
    E_("C01", "Cilindradora de 4 rodillos", Rw(23.0, 16.8, 4.5, 1.4), "S3", 1, 5.5, fuente="C Getweld", paso="C1"),
    E_("C02", "Punteo, refuerzo y estructura", Rw(28.0, 16.6, 2.5, 1.5), "S3", 1, 10.0, polvo=True, fuente="E",
       paso="C2"),
    E_("C03", "Punteo, refuerzo y estructura", Rw(31.0, 16.6, 2.5, 1.5), "S3", 1, 10.0, polvo=True, fuente="E",
       paso="C2"),
    E_("C04", "Soldadura longitudinal de carros", Rw(30.4, 12.0, 3.0, 2.0), "S3", 1, 18.0, polvo=True,
       fuente="C Getweld ZF-1000", frente="N", paso="C3"),
    E_("C05", "Soldadura circ. de fondo y cúpula", Rw(26.6, 12.2, 3.0, 1.8), "S3", 1, 18.0, polvo=True, fuente="E",
       frente="N", paso="C4"),
    E_("C06", "Inspección de costuras", Rw(23.6, 12.5, 2.2, 1.2), "S3", 1, 0.5, fuente="E", frente="N",
       paso="C5"),
    E_("C07", "PH 4,0 MPa con jaula", Rw(19.4, 11.8, 3.6, 2.6), "S3", 1, 2.0, agua=True,
       fuente="C Yukon M-000200 + jaula", frente="N", paso="C6"),
    E_("C08", "Marcado del recipiente", Rw(18.6, 8.6, 1.5, 1.0), "S3", 0, 0.5, fuente="E", frente="E",
       paso="C7"),
    E_("C09", "Probetas de soldadura", Rw(23.6, 9.0, 2.4, 1.2), "S3", 0, 2.0, fuente="E", frente="N"),
    E_("C10", "Pluma giratoria 1 t", Rw(29.75, 12.6, 0.6, 0.6), "S3", 0, 1.5, fuente="E", forma="circ"),
    E_("C12", "Carros a pintura tercerizada", Rw(18.4, 0.6, 3.6, 6.8), "PU-CP", 0, fuente="E", forma="rack",
       tipo="carros"),
    E_("T02", "Carga de polvo de carros", Rw(25.4, 3.4, 2.6, 2.4), "SP-2", 1, 2.0, aire=True, polvo=True,
       fuente="E", frente="N", paso="C8"),
    E_("Q01", "Cabina de descarga de muestras", Rw(22.6, 0.6, 2.6, 3.0), "SP-2", 0, 3.0, polvo=True, fuente="E",
       frente="E"),
    E_("T12", "Armado de carros", Rw(29.0, 3.8, 2.4, 1.8), "S-TC", 1, 0.5, aire=True, fuente="E", frente="N",
       paso="C9"),
    E_("T13", "Presurización y etiquetado de carros", Rw(31.6, 3.8, 2.4, 1.8), "S-TC", 1, 0.5, n2=True,
       fuente="E", frente="N", paso="C10"),
    E_("T14", "Estructuras y ruedas de carros", Rw(29.0, 6.7, 4.8, 0.9), "S-TC", 0, fuente="E", forma="rack"),
]

# recargas: puestos R (numeración del dimensionamiento de recargas), dentro de sus locales
_RC = [
    # (cod, nombre, (x, y, w, h), local, op, tipo, frente)
    ("R01", "Recepción y clasificación", (1.0, 3.6, 2.4, 0.9), "RC-RE", 1, "mesa_control", "S"),
    ("R19a", "Inspección visual", (0.8, 0.8, 1.6, 0.9), "RC-RE", 1, "inspeccion", "N"),
    ("R19b", "Inspección visual", (2.8, 0.8, 1.6, 0.9), "RC-RE", 1, "inspeccion", "N"),
    ("R04a", "Desarme de matafuego (morsa)", (6.4, 3.8, 1.4, 0.9), "RC-DE", 1, "banco", "S"),
    ("R04b", "Desarme de matafuego (morsa)", (8.2, 3.8, 1.4, 0.9), "RC-DE", 1, "banco", "S"),
    ("R04c", "Desarme de matafuego (morsa)", (10.0, 3.8, 1.4, 0.9), "RC-DE", 1, "banco", "S"),
    ("R05", "Lavado interior de cilindro", (6.6, 0.8, 2.6, 1.4), "RC-DE", 1, "hermeticidad", "N"),
    ("R02a", "Descarga de polvo con recuperación", (12.4, 3.6, 1.2, 1.4), "RC-DC", 1, "cabina_muestras", "S"),
    ("R02b", "Descarga de polvo con recuperación", (13.8, 3.6, 1.2, 1.4), "RC-DC", 1, "cabina_muestras", "S"),
    ("R02c", "Descarga de polvo con recuperación", (15.2, 3.6, 1.2, 1.4), "RC-DC", 0, "cabina_muestras", "S"),
    ("R02d", "Descarga de polvo con recuperación", (16.6, 3.6, 1.0, 1.4), "RC-DC", 0, "cabina_muestras", "S"),
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
    ("R17", "Despacho (precintos + remito)", (1.0, 17.3, 2.4, 0.9), "RC-DP", 1, "mesa_control", "S"),
]
for _c, _n, (_x, _y, _w, _h), _s, _op, _t, _f in _RC:
    EQUIPOS.append(Equipo(_c, _n, Rw(_x, _y, _w, _h), _s, _op, 0.5, fuente="E", tipo=_t, frente=_f,
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
PUERTAS = [
    Puerta("P1", "N", 9.4, 12.4, 4.5, "porton", "MP: autoelevador desde el alero de descarga"),
    Puerta("P2", "N", 0.8, 3.8, 4.0, "porton", "Scrap a volquete del alero"),
    Puerta("RC-1", "O", 1.0, 5.0, 4.0, "porton", "Recargas: recepción de equipos"),
    Puerta("RC-2", "O", 16.2, 18.4, 4.0, "porton", "Recargas: despacho de equipos recargados"),
    Puerta("P6", "S", 18.8, 21.8, 4.0, "porton", "Carros a pintura tercerizada"),
    Puerta("P8", "S", 25.2, 28.2, 4.0, "porton", "Carros pintados, polvo, estructuras y ruedas de carros"),
    Puerta("P9", "S", 30.0, 33.0, 3.0, "porton", "Carros terminados (camión a nivel)"),
    Puerta("M3", "S", 34.4, 37.4, 3.2, "muelle", "Recepción de tercerizados y casquetes"),
    Puerta("M1", "S", 40.6, 43.6, 3.2, "muelle", "Expedición PT (rampa niveladora)"),
    Puerta("M2", "S", 44.6, 47.6, 3.2, "muelle", "Expedición PT (rampa niveladora)"),
    Puerta("P4", "S", 63.0, 66.0, 4.0, "porton", "Polvo químico (big bags)"),
    Puerta("P3", "E", 26.0, 29.0, 3.0, "porton", "Químicos de pretratamiento, pintura en polvo y granalla"),
    # salidas de emergencia (1,10 m, barral antipánico, abren hacia afuera)
    Puerta("SE-1", "N", 30.0, 31.1, 2.1, "emergencia"),
    Puerta("SE-2", "N", 46.9, 48.0, 2.1, "emergencia"),
    Puerta("SE-3", "N", 66.0, 67.1, 2.1, "emergencia"),
    Puerta("SE-4", "N", 76.4, 77.5, 2.1, "emergencia"),
    Puerta("SE-5", "E", 36.0, 37.1, 2.1, "emergencia"),
    Puerta("SE-6", "E", 12.0, 13.1, 2.1, "emergencia"),
    Puerta("SE-7", "S", 86.0, 87.1, 2.1, "emergencia"),
    Puerta("SE-8", "S", 14.0, 15.1, 2.1, "emergencia"),
    Puerta("SE-9", "S", 52.0, 53.1, 2.1, "emergencia"),
    Puerta("PP-1", "O", 23.2, 24.4, 2.1, "peatonal", "Ingreso de personal desde vestuarios"),
]

# ============================================================ ANEXOS
ANEXOS = [
    Sector("SV", "Bloque de servicios al personal y oficinas", R(-18.0, 19.0, 0.0, 37.8), "SERV", "común"),
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
    # ---------------- MP
    Flujo("MP", [(11.9, 52.0), (11.9, 43.8), (11.9, 31.0), (9.0, 31.0)], "Chapa: alero -> paquetes AL-1H (P1)"),
    Flujo("MP", [(9.0, 27.15), (12.9, 27.15)], "Paquete a la mesa elevadora (autoelevador por el lado largo)"),
    Flujo("MP", [(12.3, 47.0), (12.3, 43.8), (12.3, 32.75), (13.6, 32.75)],
          "Caños: cantiléver del alero -> carro porta-tubos -> caballetes del láser"),
    Flujo("MP", [(13.6, 32.75), (20.0, 32.75)], "Tubos a los caballetes"),
    Flujo("MP", [(11.4, 52.0), (11.4, 43.8), (11.4, 42.6), (4.6, 42.6), (4.6, 33.0), (5.6, 33.0)],
          "Flejes: alero -> porta-flejes AL-1F (P1)"),
    Flujo("MP", [(5.6, 36.0), (5.0, 36.0), (5.0, 42.2), (12.5, 42.2), (12.5, 37.2), (12.9, 37.2)],
          "Rollo al desbobinador (gancho C)"),
    Flujo("MP", [(10.9, 52.0), (10.9, 43.8), (10.9, 43.0), (3.0, 43.0), (3.0, 30.0), (1.9, 30.0)],
          "Insumos al pañol"),
    Flujo("MP", [(36.0, -6.0), (36.0, 0.0), (36.0, 10.0), (35.4, 10.0)], "Casquetes de carros (M3 -> rack pasante RK1)",
          "S3"),
    Flujo("MP", [(34.3, 10.0), (28.1, 10.0), (28.1, 12.2)], "Casquete a la soldadura circ.", "S3"),
    Flujo("MP", [(36.8, -6.0), (36.8, 0.0), (36.8, 1.3), (37.6, 1.3)], "Tercerizados revendidos (M3)", "S4"),
    Flujo("MP", [(64.5, -6.0), (64.5, 0.0), (64.5, 2.0), (68.6, 2.0)], "Polvo químico en big bags (P4)"),
    Flujo("MP", [(68.6, 5.2), (67.6, 5.2)], "Big bag a la carga de polvo"),
    Flujo("MP", [(47.2, -6.0), (47.2, 0.0), (47.2, 1.0), (50.2, 1.0)], "Válvulas, manómetros, cajas (muelle M2)"),
    Flujo("MP", [(55.5, 1.6), (55.5, 3.0), (59.3, 3.0), (59.3, 4.8)], "Válvulas a ensamblaje"),
    Flujo("MP", [(51.3, 1.6), (51.3, 4.4)], "Cajas y film a embalaje"),
    Flujo("MP", [(96.0, 27.5), (88.0, 27.5), (86.0, 27.5)], "Químicos y pintura en polvo (P3)"),
    Flujo("MP", [(87.2, 24.8), (87.2, 18.0), (81.1, 18.0)], "Pintura en polvo a las tolvas de aplicación"),
    Flujo("MP", [(26.7, -6.0), (26.7, 0.0), (26.7, 3.4)], "Carros pintados y polvo de carros (P8)", "S3"),
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
    # ---------------- SE: carros (U)
    Flujo("SE", [(27.5, 17.5), (28.0, 17.4), (30.5, 17.4), (31.0, 17.4), (33.5, 17.4), (33.8, 17.4), (33.8, 13.0),
                 (33.4, 13.0), (30.4, 13.0), (29.6, 13.0), (26.6, 13.0), (25.8, 13.1), (23.6, 13.1), (23.0, 13.1),
                 (19.4, 13.1), (19.0, 13.1), (19.0, 9.6)],
          "Carros: punteo, soldaduras, inspección, PH y marcado", "S3"),
    Flujo("SE", [(19.4, 8.6), (19.4, 7.4)], "Carros a la espera del pintor", "S3"),
    Flujo("SE", [(20.2, 0.6), (20.2, 0.0), (20.2, -6.0)], "Carros a pintura tercerizada (P6)", "S3"),
    Flujo("SE", [(28.0, 5.4), (29.0, 5.4)], "Carga de polvo -> armado", "S3"),
    Flujo("SE", [(31.4, 5.4), (31.6, 5.4)], "Armado -> presurización", "S3"),
    # ---------------- PT
    Flujo("PT", [(62.4, 16.0), (50.2, 16.0), (46.8, 16.0)], "Cilindros vendidos vacíos al almacén de PT"),
    Flujo("PT", [(50.5, 5.2), (49.7, 8.6)], "Pallet a envolvedora"),
    Flujo("PT", [(50.5, 7.2), (49.7, 9.6)], "Pallet a envolvedora"),
    Flujo("PT", [(50.5, 9.2), (49.7, 10.6)], "Pallet de cilindros a envolvedora"),
    Flujo("PT", [(48.2, 9.7), (46.8, 9.7), (46.8, 12.0)], "Almacén de PT (envolvedora -> RK3)"),
    Flujo("PT", [(41.1, 9.0), (42.4, 9.0), (42.4, 0.0), (42.4, -6.0)], "Expedición M1 (RK2 -> T2 -> rampa)"),
    Flujo("PT", [(45.7, 8.6), (46.2, 8.6), (46.2, 0.0), (46.2, -6.0)], "Expedición M2 (RK3 -> T3 -> rampa)"),
    Flujo("PT", [(32.8, 3.8), (32.8, 0.0), (32.8, -6.0)], "Carros terminados (P9)", "S3"),
    Flujo("PT", [(40.4, 1.3), (40.8, 1.3)], "Tercerizados a expedición", "S4"),
    # ---------------- scrap
    Flujo("SCRAP", [(1.9, 40.0), (2.6, 40.0), (2.6, 43.6), (2.6, 44.4), (1.8, 46.0)], "Scrap a volquete (P2)"),
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
    br += [(19.0, Y_PP, 19.0, 29.6), (19.0, 29.6, _op("M03")[0], 29.6), (_op("M03")[0], 29.6, *_op("M03"))]
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
    br += [(74.2, Y_PP, 74.2, _op("P01")[1]), (74.2, _op("P01")[1], *_op("P01"))]
    br += [(74.2, _op("P01")[1], 74.2, _op("P04")[1]), (74.2, _op("P04")[1], *_op("P04"))]
    br += [(74.2, _op("P04")[1], 74.2, _op("P08")[1]), (74.2, _op("P08")[1], *_op("P08"))]
    H.append(("Granallado, defectos y pintura (N5, S-P)", [(38.0, Y_PP), (69.3, Y_PP), (69.3, 33.85)], br))
    # terminación y PT: bajan cruzando el pasillo y el almacén de cilindros
    br = [(61.0, 7.6, 52.52, 7.6), (52.52, 7.6, 52.52, _op("T08")[1]), (52.52, 7.6, 52.52, _op("T10")[1]),
          (61.0, 7.6, 65.9, 7.6), (65.9, 7.6, _op("T01")[0], _op("T01")[1])]
    for c in ("T03", "T04", "T05", "T07"):
        x, y = _op(c)
        br.append((x, 7.6, x, y))
    br.append((49.0, Y_PP, 49.0, 18.8))
    for c in ("Q", "QR", "SUP", "EPP"):
        r = next(s_.rect for s_ in SECTORES if s_.cod == c)
        br.append((r.c[0], Y_PP, r.c[0], r.y0))
    H.append(("Terminación, calidad y expedición", [(38.0, Y_PP), (61.0, Y_PP), (61.0, 7.6)], br))
    # carros: entran por el oeste a la calle interior de la U
    br = []
    for c in ("C01", "C02", "C03", "C05", "C06", "C07"):
        x, y = _op(c)
        br.append((x, 15.6, x, y))
    br += [(34.3, Y_PP, 34.3, 6.8), (34.3, 6.8, _op("T13")[0], _op("T13")[1]),
           (_op("T13")[0], _op("T13")[1], _op("T12")[0], _op("T12")[1]),
           (_op("T12")[0], _op("T12")[1], _op("T02")[0], _op("T02")[1])]
    H.append(("Línea de carros (S3)", [(0.0, Y_PP), (20.6, Y_PP), (20.6, 15.6), (33.0, 15.6)], br))
    # recargas
    H.append(("Recargas (RC)", [(17.1, Y_PP), (17.1, 18.8), (17.1, 6.3)],
              [(17.1, 6.3, 1.0, 6.3), (17.1, 12.5, 1.0, 12.5)]))
    return H


# ============================================================ LOCALES
# servicios SV (x -18..0, y 19..37,8). Circuito: ingreso SV-1 -> hall y fichado -> pasillo limpio (PL) ->
# vestuario -> sanitarios y duchas (sólo desde el vestuario) -> pasillo limpio -> PP-1 -> senda de la nave.
# Al sur del pasillo, lo que usan visitas y administración sin cruzar vestuarios; al norte, el personal.
# El comedor queda a 6 m de PP-1 (refrigerio de 30 min en 2 tandas) con lavamanos en la entrada.
LOCALES = [
    Sector("SV-PA", "Primeros auxilios y lactario", R(-17.9, 19.1, -15.2, 22.9), "SERV", "común",
           "Camilla, botiquín, lavabo y heladera; salida directa al exterior para ambulancia"),
    Sector("SV-OF", "Sala de capacitación (12 personas)", R(-15.0, 19.1, -8.6, 22.9), "SERV", "común",
           "Inducción, teoría de la escuelita de soldadura y simulacros; comedor de visitas"),
    Sector("SV-JP", "Higiene y seguridad y medicina laboral", R(-8.4, 19.1, -5.4, 22.9), "SERV", "común",
           "Servicio de HyS (Dec. 1338/96): legajos, exámenes periódicos, EPP"),
    Sector("SV-AC", "Sanitario accesible y de visitas", R(-5.2, 19.1, -3.2, 22.9), "SERV", "común",
           "Círculo libre Ø 1,50 m, barras, inodoro con 0,80 m libre lateral (Ley 24.314, Dec. 914/97)"),
    Sector("SV-HA", "Hall, recepción y fichado", R(-3.0, 19.1, -0.1, 22.9), "SERV", "común",
           "Reloj biométrico y tablero de novedades al paso"),
    Sector("SV-PL", "Pasillo limpio a la planta (PP-1)", R(-17.9, 23.0, -0.1, 24.5), "CIRC", "común"),
    Sector("SV-VH", "Vestuario hombres (60 armarios dobles)", R(-17.9, 24.6, -11.2, 31.4), "SERV", "común",
           "Armario doble ropa de calle / de trabajo (Dec. 351/79 art. 50); req. 56 en 2035"),
    Sector("SV-SH", "Sanitarios y duchas hombres", R(-17.9, 31.6, -11.2, 37.7), "SERV", "común",
           "3 inodoros, 6 mingitorios, 6 lavabos, 4 duchas (art. 49: turno mañana 47 H + 8 choferes)"),
    Sector("SV-VM", "Vestuario mujeres (20 armarios dobles)", R(-11.0, 24.6, -6.4, 28.8), "SERV", "común",
           "Req. 10 en 2035"),
    Sector("SV-SM", "Sanitarios y duchas mujeres", R(-11.0, 29.0, -6.4, 33.8), "SERV", "común",
           "4 inodoros, 4 lavabos, 3 duchas"),
    Sector("SV-LI", "Limpieza, ropería y lavadero", R(-11.0, 34.0, -6.4, 37.7), "SERV", "común",
           "Lavado de ropa de trabajo; carro y artículos de limpieza"),
    Sector("SV-PS", "Pasillo de servicios", R(-6.2, 24.6, -5.0, 37.7), "CIRC", "común"),
    Sector("SV-CM", "Comedor (30 plazas) y office", R(-4.8, 24.6, -0.1, 37.7), "SERV", "común",
           "5 mesas de 6; 2 tandas de 30 min por turno (27 personas en la tanda mayor)"),
    # núcleo sanitario de planta (este): pintura, terminación y PT a menos de 25 m (los vestuarios quedan a 75 m)
    Sector("SN-AC", "Sanitario accesible (planta)", R(72.0, 16.8, 74.4, 19.0), "SERV", "común",
           "Círculo Ø 1,50 m, barras; abre a la calle este, a 4 m del pasillo central"),
    Sector("SN-H", "Sanitarios hombres (planta)", R(72.0, 13.4, 74.4, 16.6), "SERV", "común",
           "2 inodoros, 2 mingitorios, 2 lavabos sobre la misma pared húmeda"),
    Sector("SN-M", "Sanitario mujeres (planta)", R(72.0, 10.4, 74.4, 13.2), "SERV", "común", "1 inodoro y lavabo"),
    Sector("SN-LI", "Sala de limpieza (planta)", R(72.0, 6.8, 74.4, 10.2), "SERV", "común",
           "Pileta de lavado, carro y artículos de limpieza; barredora"),
    # recargas RC (x 0,3..18, y 0,3..19,2): entra por RC-1, recorre en U y sale por RC-2
    Sector("RC-RE", "Recepción, clasificación y recibidos", R(0.5, 0.5, 5.8, 5.4), "RC", "RC",
           "Clasificación en 4 colas: polvo, CO₂, agente limpio y líquidos"),
    Sector("RC-DE", "Desarme y lavado", R(6.0, 0.5, 11.8, 5.4), "RC", "RC"),
    Sector("RC-DC", "Descarga y ensayo de funcionamiento", R(12.0, 0.5, 17.8, 5.4), "RC", "RC",
           "Sala con extracción y recuperación de polvo"),
    Sector("RC-C1", "Corredor de recargas (sur)", R(0.5, 5.6, 17.8, 7.0), "CIRC", "RC"),
    Sector("RC-GA", "CO₂ y agente limpio", R(0.5, 7.2, 4.2, 11.6), "RC", "RC", "Trasvasador y balanza", 15.0),
    Sector("RC-PV", "Recinto de polvo (HR ≤ 70 %)", R(4.4, 7.2, 11.8, 11.6), "RC", "RC",
           "Carga ABC, BC y D; 8 renovaciones por hora; sin estufas", 32.0),
    Sector("RC-PH", "PH con jaula, secado y Puffer", R(12.0, 7.2, 16.2, 11.6), "RC", "RC", "", 18.0),
    Sector("RC-C2", "Corredor de recargas (centro)", R(0.5, 11.8, 16.2, 13.2), "CIRC", "RC"),
    Sector("RC-CN", "Conector al pasillo central", R(16.4, 5.6, 17.8, 18.8), "CIRC", "RC"),
    Sector("RC-IR", "Inutilizados y residuos", R(0.5, 13.4, 4.2, 15.8), "RC", "RC", "", 8.0),
    Sector("RC-DP", "Despacho y equipos para entregar", R(0.5, 16.0, 4.2, 18.6), "RC", "RC", "", 9.0),
    Sector("RC-EN", "Ensamblaje, presurización, peso, hermeticidad y retoque", R(4.4, 13.4, 11.8, 18.6), "RC",
           "RC", "", 38.0),
    Sector("RC-LQ", "Líquidos", R(12.0, 13.4, 16.2, 15.8), "RC", "RC", "Agua, AFFF y clase K", 10.0),
    Sector("RC-RP", "Etiquetado y flota de intercambio", R(12.0, 16.0, 16.2, 18.6), "RC", "RC"),
]

PUERTAS_ANEXOS = [
    ("SV-1", (-2.6, 19.0), (-1.0, 19.0), "peatonal", "Ingreso de personal y visitas (desde el estacionamiento)"),
    ("SV-2", (-18.0, 27.6), (-18.0, 28.6), "peatonal", "Salida de emergencia de vestuarios"),
    ("SV-3", (-17.6, 19.0), (-16.6, 19.0), "peatonal", "Primeros auxilios: salida a ambulancia"),
]

# ============================================================ MOBILIARIO (ningún local vacío)
Mb = Mueble
MOBILIARIO = [
    # ---- SV-PA primeros auxilios y lactario
    Mb("camilla", R(-17.85, 20.2, -17.15, 22.1), "E"), Mb("botiquin", R(-15.6, 21.4, -15.25, 22.2), "O"),
    Mb("lavabos", R(-17.0, 22.35, -16.3, 22.85), "S", 1), Mb("escritorio", R(-16.4, 19.15, -15.25, 20.45), "N"),
    Mb("heladera", R(-15.65, 20.6, -15.25, 21.1), "O"),
    # ---- SV-OF oficina: 6 puestos enfrentados, archivo
    Mb("mesa", R(-14.0, 19.6, -10.0, 21.4), "S", 10), Mb("pizarra", R(-14.98, 19.8, -14.9, 21.6), "E"),
    Mb("archivo", R(-9.4, 19.15, -8.65, 19.6), "N", 2), Mb("sillas", R(-14.6, 22.35, -10.0, 22.85), "S", 4),
    # ---- SV-JP jefatura y reuniones
    Mb("escritorio", R(-8.3, 21.55, -6.6, 22.85), "S"), Mb("mesa", R(-8.3, 19.15, -6.3, 20.95), "S", 4),
    Mb("archivo", R(-5.9, 19.2, -5.45, 20.4), "O", 2),
    # ---- SV-AC sanitario accesible
    Mb("inodoro_acc", R(-5.15, 19.15, -3.25, 22.85), "N"), Mb("lavabos", R(-5.15, 20.0, -4.65, 20.7), "E", 1),
    # ---- SV-HA hall, recepción y fichado
    Mb("mostrador", R(-2.95, 21.2, -1.3, 22.4), "S"), Mb("reloj", R(-0.45, 19.6, -0.15, 20.0), "O"),
    Mb("pizarra", R(-0.2, 20.2, -0.12, 21.4), "O"), Mb("sillas", R(-2.95, 19.9, -2.5, 20.9), "E", 2),
    # ---- SV-VH vestuario hombres: 30 módulos dobles × 2 alturas = 60 armarios, bancos
    Mb("armarios", R(-17.88, 24.7, -17.38, 27.1), "E", 4), Mb("armarios", R(-17.88, 28.9, -17.38, 31.3), "E", 4),
    Mb("armarios", R(-17.3, 30.88, -13.1, 31.38), "S", 7), Mb("armarios", R(-11.72, 25.5, -11.22, 30.9), "O", 9),
    Mb("armarios", R(-15.6, 27.4, -13.6, 27.9), "S", 3), Mb("armarios", R(-15.6, 27.9, -13.6, 28.4), "N", 3),
    Mb("banco_vest", R(-16.9, 24.9, -16.5, 27.0), "E"), Mb("banco_vest", R(-16.9, 29.0, -16.5, 30.6), "E"),
    Mb("banco_vest", R(-12.6, 25.6, -12.2, 30.2), "O"), Mb("banco_vest", R(-15.6, 26.5, -13.6, 26.9), "S"),
    Mb("banco_vest", R(-15.6, 28.9, -13.6, 29.3), "N"),
    # ---- SV-SH sanitarios y duchas hombres
    Mb("inodoro", R(-17.85, 36.15, -15.0, 37.65), "S", 3), Mb("mingitorios", R(-14.9, 37.2, -11.3, 37.65), "S", 6),
    Mb("duchas", R(-17.85, 31.7, -16.95, 35.3), "E", 4), Mb("banco_vest", R(-16.4, 32.0, -16.0, 35.0), "O"),
    Mb("lavabos", R(-11.75, 31.9, -11.25, 36.1), "O", 6),
    # ---- SV-VM y SV-SM mujeres
    Mb("armarios", R(-6.92, 25.5, -6.42, 28.5), "O", 5), Mb("armarios", R(-10.98, 25.5, -10.48, 28.5), "E", 5),
    Mb("banco_vest", R(-8.9, 25.4, -8.5, 28.2), "E"),
    Mb("inodoro", R(-7.95, 29.05, -6.45, 32.85), "O", 4), Mb("duchas", R(-10.95, 32.85, -8.25, 33.75), "S", 3),
    Mb("lavabos", R(-10.95, 29.6, -10.45, 32.4), "E", 4),
    # ---- SV-LI limpieza, ropería y lavadero
    Mb("lavadero", R(-10.9, 37.0, -8.2, 37.65), "S"), Mb("estanteria", R(-8.0, 37.1, -6.5, 37.65), "S"),
    Mb("carro_limpieza", R(-10.8, 34.2, -10.1, 34.8), "N"), Mb("estanteria", R(-10.95, 35.2, -10.45, 36.6), "E"),
    # ---- SV-CM comedor: 5 mesas de 6, office y lavamanos en la entrada
    Mb("lavabos", R(-4.75, 26.3, -4.3, 27.7), "E", 2),
    *[Mb("mesa", R(-3.9, y0, -1.9, y0 + 1.7), "S", 6) for y0 in (25.1, 27.4, 29.7, 32.0, 34.3)],
    Mb("mesada", R(-0.75, 33.0, -0.15, 37.6), "O", 2), Mb("heladera", R(-0.85, 32.0, -0.15, 32.8), "O"),
    Mb("dispenser", R(-0.55, 25.0, -0.15, 25.4), "O"),
    # ---- MT taller de mantenimiento
    Mb("torno", R(41.3, 28.4, 43.6, 29.35), "S"), Mb("agujereadora", R(43.8, 28.6, 44.6, 29.35), "S"),
    Mb("banco_trabajo", R(44.8, 28.6, 47.0, 29.35), "S"), Mb("banco_trabajo", R(47.2, 28.6, 49.15, 29.35), "S"),
    Mb("estanteria", R(48.6, 25.0, 49.15, 28.2), "O"), Mb("soldadora", R(41.3, 27.0, 42.3, 27.6), "E"),
    Mb("escritorio", R(46.6, 24.85, 48.4, 26.15), "N"), Mb("contenedor", R(45.0, 24.85, 46.4, 25.75), "N"),
    # ---- Q laboratorio de calidad
    Mb("marmol", R(49.5, 27.9, 51.5, 28.9), "S"), Mb("mesa_lab", R(51.8, 28.65, 55.0, 29.35), "S"),
    Mb("camara", R(55.3, 28.3, 56.75, 29.35), "S"), Mb("camara", R(55.9, 26.6, 56.75, 27.6), "O"),
    Mb("balanza_lab", R(49.5, 25.0, 50.2, 25.6), "N"), Mb("escritorio", R(50.5, 24.85, 52.3, 26.15), "N"),
    Mb("estanteria", R(53.7, 24.85, 54.8, 25.35), "N"), Mb("mesa_lab", R(54.9, 24.85, 56.75, 25.55), "N"),
    # ---- QR cuarentena
    Mb("jaula", R(57.1, 24.9, 60.9, 29.3), "S"), Mb("pallets", R(57.3, 27.8, 59.9, 29.1), "S", 1),
    Mb("cilindros_piso", R(57.3, 25.9, 58.9, 27.4), "S", 0),
    # ---- SUP supervisión y PCP
    Mb("escritorio", R(61.3, 28.0, 62.9, 29.35), "S"), Mb("escritorio", R(63.1, 28.0, 64.7, 29.35), "S"),
    Mb("pizarra", R(65.2, 25.5, 65.35, 27.5), "O"), Mb("mesa", R(61.3, 25.6, 62.7, 27.4), "S", 4),
    Mb("archivo", R(64.0, 24.85, 65.3, 25.35), "N", 3),
    # ---- EPP
    Mb("estanteria", R(65.7, 28.8, 68.3, 29.35), "S"), Mb("estanteria", R(65.65, 25.6, 66.15, 28.4), "E"),
    Mb("ventanilla", R(66.4, 24.85, 68.3, 25.5), "N"), Mb("botiquin", R(67.85, 26.0, 68.3, 26.8), "O"),
    Mb("lavaojos", R(67.65, 28.0, 68.3, 28.7), "O"),
    # ---- PV supermercado de carros vacíos (frente a la calle PO-2)
    Mb("carros_vacios", R(44.2, 29.7, 51.4, 31.3), "N", 9), Mb("carros_vacios", R(51.6, 29.7, 57.0, 31.3), "N", 7),
    Mb("carros_vacios", R(57.2, 29.7, 61.8, 31.3), "N", 5),
    # ---- ST-I tableros y compresor
    Mb("tablero_el", R(70.3, 30.6, 74.3, 31.35), "S", 4), Mb("compresor", R(70.4, 27.0, 73.4, 28.4), "N"),
    Mb("estanteria", R(75.6, 25.0, 76.15, 28.0), "O"),
    # ---- QP químicos y pintura en polvo
    Mb("tambores", R(81.0, 29.6, 83.6, 31.3), "S", 8), Mb("tambores", R(81.0, 25.0, 83.0, 26.4), "N", 6),
    Mb("pallets", R(84.8, 29.8, 87.5, 31.3), "S", 0), Mb("estanteria", R(85.0, 25.0, 87.5, 25.5), "N"),
    Mb("lavaojos", R(83.6, 25.0, 84.2, 25.6), "N"),
    # ---- franja norte: pañol de línea, escuelita, muestras y granalla
    Mb("estanteria", R(48.1, 43.0, 55.0, 43.55), "S"), Mb("estanteria", R(48.1, 41.2, 48.6, 42.7), "E"),
    Mb("ventanilla", R(52.0, 40.85, 54.0, 41.25), "N"), Mb("escritorio", R(55.2, 42.2, 57.0, 43.55), "S"),
    Mb("pallets", R(49.0, 40.9, 51.6, 42.0), "N", 0),
    Mb("cabina_sold", R(58.3, 41.0, 63.7, 43.55), "S", 3), Mb("mesa", R(64.0, 41.9, 65.5, 43.5), "E", 4),
    Mb("estanteria", R(67.7, 43.0, 75.9, 43.55), "S"), Mb("estanteria", R(68.5, 41.6, 74.5, 42.1), "S"),
    Mb("escritorio", R(74.6, 40.85, 75.95, 42.2), "N"),
    Mb("pallets", R(78.2, 42.3, 85.0, 43.5), "S", 0), Mb("estanteria", R(85.3, 42.9, 87.5, 43.55), "S"),
    Mb("contenedor", R(78.2, 40.9, 79.8, 41.9), "N"),
    # ---- expedición y tercerizados
    Mb("rampa", R(40.6, 0.35, 43.6, 2.35), "S"), Mb("rampa", R(44.6, 0.35, 47.6, 2.35), "S"),
    Mb("rampa", R(34.4, 0.35, 37.4, 2.35), "S"), Mb("pallets", R(37.65, 0.4, 40.35, 2.3), "N", 0),
    # ---- AL-C: carga de baterías sobre el pasillo central y pallets de cilindros
    Mb("cargador", R(50.4, 16.9, 54.6, 18.75), "N", 3), Mb("pallets", R(50.4, 12.6, 60.4, 15.3), "S", 1),
    Mb("pallets", R(55.0, 16.7, 60.4, 18.6), "N", 1),
    # ---- núcleo sanitario de planta
    Mb("inodoro_acc", R(72.05, 16.85, 74.35, 18.95), "O"), Mb("lavabos", R(73.75, 16.9, 74.35, 17.6), "O", 1),
    Mb("inodoro", R(72.6, 15.05, 74.35, 16.55), "S", 2), Mb("mingitorios", R(73.2, 13.45, 74.35, 13.85), "N", 2),
    Mb("lavabos", R(72.05, 13.45, 72.6, 14.85), "E", 2),
    Mb("inodoro", R(73.3, 11.65, 74.35, 13.15), "S", 1), Mb("lavabos", R(73.75, 10.45, 74.35, 11.15), "O", 1),
    Mb("lavadero", R(73.0, 9.5, 74.35, 10.15), "S"), Mb("carro_limpieza", R(72.2, 6.9, 72.9, 7.5), "N"),
    Mb("estanteria", R(73.8, 6.9, 74.35, 8.9), "O"),
    # ---- RC-IR inutilizados y residuos
    Mb("jaula", R(0.6, 13.5, 2.6, 15.7), "E"), Mb("cilindros_piso", R(0.75, 13.7, 2.4, 15.5), "E", 0),
    Mb("tambores", R(2.8, 13.5, 4.1, 14.9), "O", 2), Mb("contenedor", R(2.8, 15.0, 4.1, 15.7), "O"),
]

# puertas interiores de una hoja: (x, y, ancho, muro 'h'/'v', abre +1/-1)
PUERTAS_INT = [
    (-16.2, 22.9, 0.8, "h", -1), (-9.5, 22.9, 0.8, "h", -1), (-6.5, 22.9, 0.8, "h", -1), (-4.6, 22.9, 0.9, "h", -1),
    (-1.1, 22.9, 0.8, "h", -1), (-13.0, 24.6, 0.9, "h", 1), (-12.9, 31.5, 0.9, "h", 1), (-8.2, 24.6, 0.8, "h", 1),
    (-10.2, 28.9, 0.8, "h", 1), (-6.3, 34.6, 0.8, "v", -1), (-4.9, 25.0, 0.9, "v", 1),
    (72.0, 17.0, 0.9, "v", 1), (72.0, 14.95, 0.8, "v", 1), (72.0, 10.6, 0.8, "v", 1), (72.0, 7.7, 0.8, "v", 1),
]

# ============================================================ LOCALES CERRADOS DENTRO DE LA NAVE
# tabique en todo el perímetro (salvo donde coincide con el cerramiento de la nave) y sus aberturas:
# (lado, desde, hasta, tipo): puerta (hoja 0,90), porton (corredizo), cortina (lamas de PVC, pasa material),
# ventanilla (mostrador, no es paso), ventana (vidrio a la planta, no es paso)
CERRADOS = {
    "MT": [("S", 41.6, 43.6, "porton"), ("N", 45.0, 48.6, "ventana")],
    "Q": [("S", 52.6, 53.5, "puerta"), ("N", 50.0, 56.4, "ventana"), ("S", 50.0, 52.2, "ventana")],
    "QR": [("S", 58.5, 59.5, "puerta")],
    "SUP": [("S", 62.9, 63.7, "puerta"), ("N", 61.6, 65.0, "ventana"), ("S", 64.0, 65.1, "ventana")],
    "EPP": [("S", 66.4, 68.3, "ventanilla"), ("E", 27.0, 27.8, "puerta")],
    "ST-I": [("O", 25.2, 26.8, "porton")],
    "QP": [("N", 83.75, 84.65, "puerta"), ("O", 28.0, 29.0, "puerta")],
    "SP-1": [("O", 5.0, 6.4, "cortina"), ("N", 66.0, 67.2, "cortina"), ("O", 9.0, 9.9, "puerta")],
    "SP-2": [("N", 25.0, 26.2, "cortina"), ("E", 4.8, 6.0, "cortina"), ("N", 23.0, 23.9, "puerta")],
    "PÑL": [("S", 52.0, 54.0, "ventanilla"), ("S", 56.6, 57.5, "puerta")],
    "ES": [("S", 64.4, 65.3, "puerta"), ("S", 58.6, 63.6, "ventana")],
    "AR": [("S", 70.0, 70.9, "puerta")],
    "GR": [("S", 82.0, 83.4, "porton")],
}

# ============================================================ ENTREPISO DE OFICINAS (+3,50) SOBRE LA FILA CENTRAL
# Administración, PCP y jefatura con ventana corrida a la línea (norte) y al pasillo central / PT (sur);
# se baja por la escalera ESC a la calle PO-1 y a la senda: comunicación directa con producción.
ENTREPISO = R(41.2, 24.8, 68.4, 29.4)
Z_ENTREPISO = 3.50
LOCALES_PA = [
    Sector("PA-CO", "Pasillo vidriado al pasillo central", R(41.3, 24.9, 68.3, 26.0), "CIRC", "común"),
    Sector("PA-HA", "Llegada de escalera y plataforma", R(41.3, 26.1, 43.8, 29.3), "CIRC", "común"),
    Sector("PA-OF", "Administración, ventas, compras y calidad (6 puestos)", R(43.9, 26.1, 52.0, 29.3), "SERV",
           "común", "Servicios y Oficinas 2035: 6 puestos en el turno mañana"),
    Sector("PA-PCP", "Planificación y control de la producción", R(52.1, 26.1, 56.0, 29.3), "SERV", "común",
           "Tablero de programación a la vista de la línea"),
    Sector("PA-JP", "Jefatura de planta", R(56.1, 26.1, 59.6, 29.3), "SERV", "común"),
    Sector("PA-RE", "Sala de reuniones (8)", R(59.7, 26.1, 64.4, 29.3), "SERV", "común"),
    Sector("PA-AC", "Sanitario accesible", R(64.5, 26.1, 66.4, 29.3), "SERV", "común"),
    Sector("PA-AR", "Archivo y office", R(66.5, 26.1, 68.3, 29.3), "SERV", "común"),
]
MOBILIARIO_PA = [
    *[Mb("escritorio", R(44.0 + i * 1.95, 28.0, 45.8 + i * 1.95, 29.25), "S") for i in range(4)],
    *[Mb("escritorio", R(44.0 + i * 1.95, 26.15, 45.8 + i * 1.95, 27.4), "N") for i in range(2)],
    Mb("archivo", R(48.2, 26.15, 51.9, 26.6), "N", 6),
    Mb("escritorio", R(52.2, 28.0, 54.0, 29.25), "S"), Mb("escritorio", R(54.1, 28.0, 55.9, 29.25), "S"),
    Mb("pizarra", R(52.2, 26.15, 55.9, 26.25), "N"),
    Mb("escritorio", R(56.4, 28.0, 58.4, 29.25), "S"), Mb("mesa", R(56.4, 26.15, 59.3, 27.6), "S", 4),
    Mb("mesa", R(60.0, 26.6, 64.1, 28.8), "S", 8),
    Mb("inodoro_acc", R(64.55, 26.15, 66.35, 29.25), "E"), Mb("lavabos", R(64.55, 28.6, 65.2, 29.25), "S", 1),
    Mb("archivo", R(66.55, 28.7, 68.25, 29.25), "S", 3), Mb("mesada", R(66.55, 26.15, 68.25, 26.75), "N", 1),
]
PUERTAS_PA = [(44.9, 26.05, 0.9, "h", 1), (52.6, 26.05, 0.9, "h", 1), (56.6, 26.05, 0.9, "h", 1),
              (60.2, 26.05, 0.9, "h", 1), (64.8, 26.05, 0.9, "h", 1), (66.9, 26.05, 0.8, "h", 1)]

# ============================================================ PROTECCIÓN CONTRA INCENDIO Y SEÑALIZACIÓN
# bocas de incendio equipadas (manguera 25 m + chorro 5 m): cubren toda la nave desde las calles
BIE = [(8.0, 23.0), (30.0, 23.0), (52.0, 23.0), (73.0, 23.0), (30.0, 39.7), (55.0, 39.9), (80.0, 39.9),
       (22.0, 7.6), (56.0, 8.0), (80.0, 2.0), (9.0, 12.4)]
# pulsadores manuales de alarma junto a cada salida y sirena con luz estroboscópica
PULSADORES = [(10.9, 43.3), (2.0, 43.3), (30.5, 43.3), (47.4, 43.3), (66.5, 43.3), (77.0, 43.3), (87.3, 36.5),
              (87.3, 12.5), (86.5, 0.7), (52.5, 0.7), (14.5, 0.7), (0.7, 3.0), (0.7, 17.3), (0.7, 23.8)]


def _senales():
    """Señalética (IRAM 10005-1 colores y formas; Dec. 351/79): (tipo, código, x, y, texto).
    tipo: obl (azul, círculo), adv (amarilla, triángulo), pro (roja, círculo con barra), sal (verde, rectángulo),
    inc (roja, cuadrado)."""
    S = []
    # salidas: sobre cada puerta de emergencia y portón, y flechas a lo largo del pasillo central
    for p in PUERTAS:
        if p.tipo in ("emergencia", "peatonal") or p.cod in ("RC-1", "RC-2", "P1", "M1", "M2", "M3"):
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
    for x, y in ((81.2, 31.0), (51.0, 47.9), (53.0, -1.4)):
        S.append(("adv", "INFLAM", x, y, "Inflamables / gases a presión"))
    for x, y in ((19.8, 38.3), (12.5, 37.6), (26.0, 18.6)):
        S.append(("adv", "ATRAP", x, y, "Riesgo de atrapamiento / cargas suspendidas"))
    # prohibiciones
    for x, y in ((75.0, 23.0), (68.0, 11.5), (27.5, 7.5), (84.0, 30.8), (48.0, 44.6)):
        S.append(("pro", "FUMAR", x, y, "Prohibido fumar y llama abierta"))
    for x, y in ((3.8, 25.2), (10.9, 25.2), (36.0, 18.3), (43.0, 18.3)):
        S.append(("pro", "PEATON", x, y, "Prohibido el paso de peatones (calle de autoelevador)"))
    # información y salvamento
    for x, y in ((67.0, 29.9), (-15.6, 22.6), (73.2, 19.6), (82.6, 26.0)):
        S.append(("sal", "+", x, y, "Primeros auxilios / lavaojos"))
    S.append(("sal", "REUNIÓN", 28.0, -30.0, "Punto de reunión"))
    S.append(("sal", "PLANO", 0.9, 22.6, "Plano de evacuación (ingreso PP-1)"))
    return S


SENALES = _senales()

# función de cada portón, rotulada en todos los planos (qué entra o sale, nunca un código suelto)
USO_CORTO = {
    "P1": "MP: chapa, caño, flejes e insumos pesados", "P2": "Scrap a volquete",
    "RC-1": "Recargas: entran equipos", "RC-2": "Recargas: salen equipos",
    "P6": "Carros al pintor y vuelta", "P8": "Carros: estructuras, ruedas y polvo", "P9": "Carros terminados",
    "M3": "Tercerizados y casquetes", "M1": "PT a camión", "M2": "PT a camión / insumos de terminación",
    "P4": "Polvo químico (big bags)", "P3": "Químicos, pintura en polvo y granalla", "PP-1": "Personal",
}

# ============================================================ IMPLANTACIÓN
LM_Y = TERRENO[1]
RETIRO_FRENTE = 10.0

EXTERIOR = [
    ("PL-N", "Alero de descarga de MP (semi 18,6 m y chasis)", R(-1.0, 44.4, 31.0, 56.0), "playa"),
    ("VQ-O", "Volquete 6 m³ (scrap)", R(-0.6, 44.8, 4.6, 47.6), "volquete"),
    ("CT", "Cantiléver de caños 6 m bajo alero (12 atados ≤ 600 kg)", R(13.2, 44.8, 21.4, 47.2), "cantilever"),
    ("JG-S", "Jaula de gases de soldadura (Ar/CO₂)", R(48.0, 44.4, 56.0, 48.4), "jaula"),
    ("ERM", "Regulación de gas de hornos", R(88.6, 4.0, 91.6, 7.0), "gas"),
    ("JG-N", "Jaula de N₂ y CO₂ (manifold)", R(51.0, -6.0, 55.0, -1.0), "jaula"),
    ("RI", "Reserva de agua contra incendio y bombas", R(100.0, 34.0, 110.0, 44.0), "incendio"),
    ("AMP", "Reserva de ampliación (nave hacia el este)", R(92.0, -8.0, 114.0, 30.0), "reserva"),
    ("PTE", "Tratamiento de efluentes líquidos", R(64.0, -27.0, 76.0, -19.0), "efluentes"),
    ("EST", "Estacionamiento de personal (38 + 2 accesibles)", R(-28.0, -44.0, 30.0, -22.0), "estac"),
    ("EU", "Utilitarios de reparto y recargas (8)", R(-28.0, -4.0, -10.0, 8.0), "estac"),
    ("GAR", "Garita de seguridad: control de acceso, CCTV y balanza de camiones", R(19.0, -58.5, 25.0, -53.5),
     "garita"),
    ("PR", "Punto de reunión (evacuación)", R(24.0, -32.0, 32.0, -28.0), "reunion"),
    ("MT", "Celda de medición de media tensión", R(-38.0, -60.0, -32.0, -56.0), "elec"),
    ("ERP", "Estación reductora de gas", R(120.0, -60.0, 124.0, -57.0), "gas"),
]
CALLES = [R(-36.0, -62.0, -29.0, 63.0), R(-36.0, 56.5, 126.0, 63.0), R(119.0, -62.0, 126.0, 63.0)]
PORTONES_TERRENO = [
    ("G1", -36.0, -29.0, "Camiones de MP, scrap, recargas y pintor"),
    ("G2", -6.0, 0.0, "Autos del personal"),
    ("G4", 21.0, 24.0, "Peatones"),
    ("G3", 119.0, 126.0, "Camiones de PT, carros, polvo, insumos y químicos"),
]

# ============================================================ EFLUENTES
EFLUENTES = [
    Flujo("EFL-L", [(84.0, 10.6), (84.0, 9.9), (88.4, 9.9), (88.4, 0.0), (74.0, -19.0)], "Pretratamiento de pintura"),
    Flujo("EFL-L", [(52.4, 35.4), (52.4, 34.0), (61.8, 34.0), (61.8, 0.6), (70.0, -19.0)], "Agua de PH 1-10 kg"),
    Flujo("EFL-L", [(56.0, 35.4), (56.0, 34.0)], "Agua de PH 1-10 kg"),
    Flujo("EFL-L", [(21.2, 11.8), (21.2, 10.6), (34.2, 10.6), (34.2, 0.6), (61.8, 0.6)], "Agua de PH de carros"),
    Flujo("EFL-L", [(15.0, 9.4), (15.0, 0.6), (18.2, 0.6)], "Lavado y PH de recargas"),
    Flujo("EFL-L", [(70.0, -27.0), (70.0, -62.0)], "Vuelco a colectora (previa autorización)"),
]
RC_FLUJO = [(-6.0, 3.0), (0.0, 3.0), (3.1, 3.0), (8.9, 3.0), (14.9, 3.0), (14.9, 9.4), (8.1, 9.4), (8.1, 15.6),
            (14.1, 15.6), (14.1, 17.8), (2.3, 17.8), (0.0, 17.3), (-6.0, 17.3)]

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
    (9.1, 12.7, "autoelevador al almacén de MP (A2)"),
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
