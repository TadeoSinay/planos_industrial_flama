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
    Pasillo("PC", R(0.3, 19.2, 69.8, 23.0), "PM", 3.8,
            "Pasillo central: autoelevador 3,0 t doble sentido (2 × 1,25 m + 3 × 0,40 m de huelgo)"),
    Pasillo("PP", R(0.3, 23.2, 69.8, 24.4), "PP", 1.2,
            "Senda peatonal separada del carril de autoelevador por una defensa con aberturas en las sendas"),
    Pasillo("AM", R(10.2, 24.6, 13.6, 43.6), "PM", 3.4,
            "Pasillo de autoelevador del almacén de MP: alero de descarga (P1) -> racks -> máquinas"),
    Pasillo("PO-1", R(39.4, 24.6, 41.0, 35.2), "PO", 1.6, "Calle de operarios y carros de pulmón (N1 -> N4)"),
    Pasillo("PO-1N", R(39.85, 35.2, 40.75, 38.95), "PO", 0.9, "Paso de operarios entre encastre y bordoneado"),
    Pasillo("PO-2", R(30.0, 33.6, 82.6, 34.8), "PO", 1.2, "Calle de operarios y carros de la línea principal"),
    Pasillo("PO-3", R(16.9, 38.95, 41.0, 39.95), "PO", 1.0, "Calle de operarios de cúpulas y cuellos (N3)"),
    Pasillo("PO-L", R(16.8, 31.8, 29.2, 32.9), "PO", 1.1, "Calle del operario de los láseres"),
    Pasillo("PO-4", R(41.0, 39.4, 87.6, 40.6), "PO", 1.2,
            "Calle norte: pañol de línea, escuelita, muestras y granalla; salidas SE-2, SE-3 y SE-4"),
    Pasillo("PO-E", R(84.6, 31.6, 87.4, 39.4), "PO", 2.8, "Calle de transpaleta: P3 -> granalla (GR)"),
    Pasillo("PT-A", R(34.2, 0.3, 37.6, 18.8), "PM", 3.4, "Autoelevador: M3 -> casquetes y rack de PT 1"),
    Pasillo("PT-B", R(38.7, 6.8, 42.1, 18.8), "PM", 3.4, "Autoelevador del almacén de PT (centro)"),
    Pasillo("PT-C", R(44.3, 6.8, 47.7, 18.8), "PM", 3.4, "Autoelevador del almacén de PT (este) y envolvedora"),
    Pasillo("EX", R(40.6, 3.0, 49.8, 6.6), "PM", 3.6, "Calle de expedición frente a los muelles M1 y M2"),
    Pasillo("AT", R(50.2, 1.9, 62.0, 4.2), "PM", 2.3, "Calle de abastecimiento de terminación (transpaleta)"),
    Pasillo("PO-T", R(52.8, 7.2, 62.0, 8.2), "PO", 1.0, "Calle de operarios de terminación"),
    Pasillo("RC-P", R(0.5, 5.6, 17.8, 7.0), "PO", 1.4, "Corredor de recargas (sur)"),
    Pasillo("RC-Q", R(0.5, 11.8, 16.2, 13.2), "PO", 1.4, "Corredor de recargas (centro)"),
    Pasillo("RC-N", R(16.4, 7.0, 17.8, 18.8), "PO", 1.4, "Conector de recargas al pasillo central"),
]

# sendas peatonales: se calculan al final del módulo en cada cruce de un hilo con un flujo
SENDAS = []

# ============================================================ SECTORES
SECTORES = [
    # ---------------- banda norte: almacén de MP (oeste)
    Sector("AL-1H", "Chapa en paquetes (reserva)", R(0.5, 24.8, 10.0, 31.0), "MP", "común",
           "8 posiciones de 1,6 × 3,1 m a 2 alturas = 16 paquetes ≤ 2 t; FIFO, semáforo de antigüedad", 50.0),
    Sector("PÑ", "Pañol de insumos pesados", R(0.5, 31.2, 10.0, 37.8), "MP", "común",
           "Alambre MIG, granalla, cuplas, tapones y consumibles", 35.2),
    Sector("SCR", "Scrap: orillas, despuntes y esqueleto de fleje", R(0.5, 38.0, 10.0, 43.5), "AUX", "común",
           "Contenedores basculantes; salen por P2 al volquete del patio norte"),
    Sector("AL-1R", "Racks frente a máquina: chapa, caño y flejes", R(13.8, 24.8, 16.4, 43.5), "MP", "común",
           "Chapa en uso (frente a la guillotina), caño 6 m (frente a los láseres), flejes (frente a la prensa)"),
    # ---------------- banda norte: línea convergente
    Sector("N1", "Corte y cuerpo 2,5-10 kg", R(16.8, 24.8, 38.8, 29.5), "PROD", "S2",
           "1 guillotina -> 2 numerado -> 3 cilindrado -> 4 soldadura longitudinal"),
    Sector("N2", "Corte de caño 1 kg", R(16.8, 29.7, 29.4, 34.9), "PROD", "S1", "5 corte láser de caño"),
    Sector("N3", "Cúpulas, fondos y cuellos", R(16.8, 35.1, 30.0, 43.5), "PROD", "S1 / S2",
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
    Sector("EPP", "EPP, botiquín y ducha lavaojos", R(65.6, 24.8, 69.8, 29.4), "AUX", "común",
           "Entrega de EPP contra vale; caretas fotosensibles de recambio"),
    Sector("MT", "Taller de mantenimiento", R(41.2, 24.8, 49.2, 29.4), "AUX", "común",
           "Bancos, torno, agujereadora, soldadora móvil y repuestos; entra la transpaleta desde el pasillo", 30.0),
    Sector("PV", "Carros vacíos: supermercado de retorno", R(41.2, 29.6, 62.0, 33.4), "AUX", "común",
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
    Sector("S-P", "Pintura en polvo (lazo)", R(70.2, 0.3, 87.7, 24.4), "PINT", "S1 / S2",
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
    Sector("EXP", "Expedición y muelles", R(40.6, 0.3, 50.0, 6.6), "PT", "común",
           "Consolidación de pedidos frente a M1-M2"),
    Sector("S4", "Tercerizados revendidos", R(37.8, 0.3, 40.4, 6.6), "PT", "S4",
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
    E_("HJ1", "Chapa en paquetes (reserva, 2 alturas)", Rw(0.8, 25.2, 8.8, 5.4), "AL-1H", 0, fuente="E",
       tipo="paquetes"),
    E_("PN1", "Estantería del pañol", Rw(0.8, 31.6, 1.0, 5.8), "PÑ", 0, fuente="E", tipo="estanteria", frente="O"),
    E_("PN2", "Estantería del pañol", Rw(4.4, 31.6, 1.0, 5.8), "PÑ", 0, fuente="E", tipo="estanteria", frente="O"),
    E_("PN3", "Estantería del pañol", Rw(8.4, 31.6, 1.0, 5.8), "PÑ", 0, fuente="E", tipo="estanteria", frente="O"),
    E_("SC1", "Contenedores basculantes de scrap", Rw(3.0, 38.4, 6.6, 1.4), "SCR", 0, fuente="E",
       tipo="contenedores"),
    E_("RH1", "Rack de chapa en uso", Rw(14.0, 25.0, 2.2, 4.4), "AL-1R", 0, fuente="E", tipo="paquetes",
       frente="O"),
    E_("RT1", "Cantiléver de caño 6 m", Rw(14.0, 29.8, 2.2, 5.0), "AL-1R", 0, fuente="E", tipo="cantilever",
       frente="O"),
    E_("RF1", "Porta-flejes (27 rollos)", Rw(14.0, 35.2, 2.2, 8.2), "AL-1R", 0, fuente="E", tipo="portaflejes",
       frente="O"),
    # ---------------- N1: corte y cuerpo 2,5-10 kg (oeste -> este, eje y = 27,2)
    E_("M02", "Mesa elevadora de tijera 3 t", Rw(16.8, 25.8, 1.2, 3.0), "N1", 0, 2.2, fuente="MP Manipulación",
       frente="O"),
    E_("M03", "Mesa de bolas", Rw(18.1, 25.6, 1.4, 3.4), "N1", 0, fuente="MP Manipulación", frente="O"),
    E_("M04", "Guillotina hidráulica 8 × 3200", Rw(20.2, 25.4, 2.3, 4.2), "N1", 1, 15.0, fuente="C Cena E21",
       frente="O", paso="1"),
    E_("M05", "Mesa de salida", Rw(22.7, 25.8, 1.4, 3.4), "N1", 0, fuente="E", frente="O"),
    E_("B01", "Numerado de cuerpo", Rw(26.7, 26.8, 1.2, 0.8), "N1", 1, 0.5, fuente="E", paso="2"),
    E_("B01b", "Numerado de cuerpo", Rw(28.3, 26.8, 1.2, 0.8), "N1", 1, 0.5, fuente="E", paso="2"),
    E_("B02", "Cilindradora", Rw(31.8, 26.7, 1.7, 0.9), "N1", 1, 1.1, fuente="C Bästlein", paso="3"),
    E_("B03", "Soldadura longitudinal", Rw(35.8, 26.4, 2.2, 1.6), "N1", 1, 12.0, polvo=True,
       fuente="C Mitusa GS2ft Ergo", paso="4"),
    # ---------------- N2: corte de caño 1 kg
    E_("M16", "Láser de tubo 6012", Rw(16.8, 29.75, 10.2, 2.0), "N2", 1, 10.0, aire=True, polvo=True,
       fuente="C Leapion 6012", frente="N"),
    E_("M15", "Láser de tubo 6012", Rw(16.8, 32.95, 10.2, 2.0), "N2", 0, 10.0, aire=True, polvo=True,
       fuente="C Leapion 6012"),
    # ---------------- N3: cúpulas, fondos y cuellos
    E_("M06", "Desbobinador y enderezador", Rw(16.8, 36.2, 2.6, 2.0), "N3", 0, 3.0, fuente="C alimentador 900 mm",
       paso="6"),
    E_("M07", "Alimentador servo", Rw(19.6, 36.6, 1.4, 1.2), "N3", 0, 2.0, fuente="C alimentador 900 mm",
       paso="6"),
    E_("M08", "Prensa de corte y embutido 300 t", Rw(21.2, 35.8, 3.0, 2.6), "N3", 1, 30.0, aire=True,
       fuente="C PHM 300", frente="N", paso="6"),
    E_("M09", "Preparación de cuello", Rw(17.2, 40.6, 1.2, 1.0), "N3", 1, 3.0, aire=True, fuente="E", paso="7"),
    E_("M10", "Preparación de cuello", Rw(18.8, 40.6, 1.2, 1.0), "N3", 0, 3.0, aire=True, fuente="E", paso="7"),
    E_("M11", "Soldadura circ. de cuello", Rw(20.8, 40.5, 1.6, 1.2), "N3", 1, 12.0, polvo=True, fuente="C FS-HFM1",
       paso="8"),
    E_("M12", "Soldadura circ. de cuello", Rw(22.8, 40.5, 1.6, 1.2), "N3", 0, 12.0, polvo=True, fuente="C FS-HFM1",
       paso="8"),
    # ---------------- N4: unión y prueba hidráulica (línea principal, eje y = 36,2)
    E_("E09a", "Encastre de fondo", Rw(35.0, 35.6, 1.2, 1.0), "N4", 1, 1.0, aire=True, fuente="E", paso="9"),
    E_("E09b", "Encastre de fondo", Rw(36.8, 35.6, 1.2, 1.0), "N4", 1, 1.0, aire=True, fuente="E", paso="9"),
    E_("E09c", "Encastre de fondo", Rw(38.6, 35.6, 1.2, 1.0), "N4", 1, 1.0, aire=True, fuente="E", paso="9"),
    E_("B04", "Bordoneadora", Rw(40.8, 35.7, 1.2, 0.9), "N4", 1, 1.5, fuente="C SWM-400", paso="10"),
    E_("A06", "Soldadura circ. cúpula y fondo", Rw(42.6, 35.4, 2.4, 1.8), "N4", 1, 15.0, polvo=True,
       fuente="C Getweld", paso="11"),
    E_("B06", "Soldadura circ. cúpula y fondo", Rw(45.6, 35.4, 2.4, 1.8), "N4", 1, 15.0, polvo=True,
       fuente="C SCWelding PRO WP150", paso="11"),
    E_("A07", "Prueba hidráulica automática", Rw(50.8, 35.4, 3.2, 2.6), "N4", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A", paso="12"),
    E_("B07", "Prueba hidráulica automática", Rw(54.4, 35.4, 3.2, 2.6), "N4", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A", paso="12"),
    E_("B14", "Secadora de cilindros", Rw(60.0, 35.2, 4.0, 1.6), "N4", 0, 6.0, gas=True, fuente="E", paso="13"),
    E_("A11", "Secadora de cilindros", Rw(60.0, 37.2, 4.0, 1.6), "N4", 0, 6.0, gas=True, fuente="E", paso="13"),
    # ---------------- N5: granallado y defectos (columna este, arriba)
    E_("B08", "Granalladora de túnel", Rw(71.0, 35.4, 4.5, 2.2), "N5", 1, 15.0, polvo=True,
       fuente="C Airblast G-100", paso="14"),
    E_("B13", "Colector de polvo", Rw(71.4, 37.9, 1.8, 1.4), "N5", 0, 5.5, polvo=True, fuente="E"),
    E_("B09", "Detección de defectos", Rw(76.4, 35.8, 2.2, 1.2), "N5", 1, 0.5, fuente="E", paso="15"),
    E_("B10", "Corrección de defectos", Rw(80.0, 35.6, 2.2, 1.5), "N5", 1, 10.0, polvo=True, fuente="E",
       paso="16"),
    # ---------------- pintura: lazo (eje: y 21,4 / x 84,0 / y 2,6 / x 73,1)
    E_("P01", "Tren de carga", Rw(76.0, 18.2, 5.0, 6.2), "S-P", 2, fuente="C Electricolor", frente="N",
       paso="17"),
    E_("P02", "Túnel de pretratamiento (3 etapas)", Rw(82.9, 10.6, 2.2, 8.4), "S-P", 0, 11.0, agua=True,
       polvo=True, fuente="E SP Ingeniería / Electricolor", frente="O", paso="17"),
    E_("P03", "Horno de secado 6 × 2,44 m", Rw(82.78, 3.8, 2.44, 6.0), "S-P", 0, 3.0, gas=True,
       fuente="C Electricolor", frente="O", paso="17"),
    E_("P04", "Cabina de pintura y reciprocador", Rw(77.0, 1.6, 3.2, 2.0), "S-P", 1, 5.0, aire=True, polvo=True,
       fuente="C Electricolor EC40-200D", frente="N", paso="17"),
    E_("P05", "Ciclones de recuperación", Rw(76.6, 4.4, 4.0, 1.6), "S-P", 0, 11.0, polvo=True,
       fuente="C Electricolor", frente="S"),
    E_("P06", "Horno de polimerizado 6 × 2,44 m", Rw(71.88, 3.4, 2.44, 6.0), "S-P", 0, 3.0, gas=True,
       fuente="C Electricolor", frente="O", paso="17"),
    E_("P07", "Enfriamiento", Rw(71.88, 9.8, 2.44, 4.0), "S-P", 0, fuente="E", frente="O"),
    E_("P08", "Tren de descarga", Rw(70.6, 14.2, 5.0, 6.0), "S-P", 1, fuente="C Electricolor", frente="O",
       paso="17"),
    E_("P09", "Retoque y control de espesor", Rw(77.0, 13.0, 2.4, 1.6), "S-P", 0, fuente="E"),
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
    E_("T07", "Etiquetadora semiautomática", Rw(53.1, 5.0, 1.5, 0.8), "S-T", 1, 0.5, fuente="C SISA", frente="N",
       paso="22"),
    E_("T08", "Embalaje y palletizado", Rw(50.5, 4.4, 1.6, 1.6), "S-T", 1, fuente="E", frente="E", paso="23"),
    E_("T09", "Embalaje y palletizado", Rw(50.5, 6.4, 1.6, 1.6), "S-T", 1, fuente="E", frente="E", paso="23"),
    E_("T10", "Palletizado de cilindros vendidos", Rw(50.5, 8.4, 1.6, 1.6), "S-T", 1, fuente="E", frente="E",
       paso="23"),
    E_("RKI", "Rack de insumos de terminación", Rw(50.6, 0.5, 7.6, 1.1), "AL-2", 0, fuente="E", forma="rack"),
    # ---------------- PT
    E_("T11", "Envolvedora de pallets", Rw(48.2, 8.2, 1.5, 3.0), "AL-3", 0, 1.5, fuente="C EDOS PS5", paso="24"),
    E_("RK1", "Rack de PT 1 (4 módulos × 2 × 4)", Rw(37.6, 6.8, 1.1, 11.6), "AL-3", 0, fuente="E", forma="rack"),
    E_("RK2", "Rack de PT 2 (4 módulos × 2 × 4)", Rw(42.1, 6.8, 1.1, 11.6), "AL-3", 0, fuente="E", forma="rack"),
    E_("RK3", "Rack de PT 3 (4 módulos × 2 × 4)", Rw(43.2, 6.8, 1.1, 11.6), "AL-3", 0, fuente="E", forma="rack"),
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
    E_("C10", "Pluma giratoria 1 t", Rw(29.9, 14.9, 0.6, 0.6), "S3", 0, 1.5, fuente="E", forma="circ"),
    E_("AL1C", "Rack de casquetes de carros", Rw(32.8, 8.4, 1.2, 3.2), "S3", 0, fuente="E", forma="rack"),
    E_("C12", "Carros a pintura tercerizada", Rw(18.4, 0.6, 3.6, 6.8), "PU-CP", 0, fuente="E", forma="rack",
       tipo="carros"),
    E_("T02", "Carga de polvo de carros", Rw(25.4, 3.4, 2.6, 2.4), "SP-2", 1, 2.0, aire=True, polvo=True,
       fuente="E", frente="N", paso="C8"),
    E_("Q01", "Cabina de descarga de muestras", Rw(22.6, 0.6, 2.6, 3.0), "SP-2", 0, 3.0, polvo=True, fuente="E",
       frente="E"),
    E_("T12", "Armado de carros", Rw(29.0, 4.4, 2.4, 2.0), "S-TC", 1, 0.5, aire=True, fuente="E", frente="N",
       paso="C9"),
    E_("T13", "Presurización y etiquetado de carros", Rw(31.6, 4.4, 2.4, 2.0), "S-TC", 1, 0.5, n2=True,
       fuente="E", frente="N", paso="C10"),
    E_("T14", "Estructuras y ruedas de carros", Rw(29.0, 6.8, 4.8, 0.9), "S-TC", 0, fuente="E", forma="rack"),
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
    ("R07", "Prueba hidráulica con jaula", (12.3, 9.0, 3.2, 2.4), "RC-PH", 1, "ph", "S"),
    ("R08", "Secado de cilindros", (12.3, 7.4, 2.4, 1.0), "RC-PH", 0, "secadora", "N"),
    ("R23", "Prueba Puffer (IRAM 3672)", (14.9, 7.4, 1.2, 1.2), "RC-PH", 0, "banco", "N"),
    ("R03a", "Carga de polvo por vacío", (4.8, 9.6, 1.6, 1.8), "RC-PV", 1, "carga_polvo", "S"),
    ("R03b", "Carga de polvo por vacío", (6.8, 9.6, 1.6, 1.8), "RC-PV", 1, "carga_polvo", "S"),
    ("R03c", "Carga de polvo por vacío", (8.8, 9.6, 1.6, 1.8), "RC-PV", 0, "carga_polvo", "S"),
    ("R16", "Clase D (descarga / carga manual)", (10.6, 7.4, 1.0, 1.6), "RC-PV", 0, "banco", "O"),
    ("R18", "Deshumidificador sala de polvo", (4.8, 7.4, 2.0, 1.0), "RC-PV", 0, "deshumidificador", "N"),
    ("R24", "Descarga de CO₂ / agente limpio", (0.8, 9.8, 1.2, 1.4), "RC-GA", 1, "presurizacion", "E"),
    ("R12", "Carga de CO₂ (trasvasador)", (2.6, 9.8, 1.2, 1.4), "RC-GA", 0, "presurizacion", "O"),
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
    "P01": "17.1", "P02": "17.2", "P03": "17.3", "P04": "17.4", "P06": "17.5", "P07": "17.6", "P08": "17.7",
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
    Pulmon("PU-L1", R(27.4, 29.8, 29.2, 31.7), "Cuerpos 1 kg cortados (láser 5.1)", "5.1 Láser", "PU-L2", 1, "v"),
    Pulmon("PU-L2", R(27.4, 33.0, 29.2, 34.9), "Cuerpos 1 kg cortados", "5.2 Láser / PU-L1", "9 Encastre", 1, "v"),
    Pulmon("PU-K", R(24.6, 35.3, 26.4, 38.9), "Fondos embutidos", "6 Embutido", "9 Encastre", 2, "v"),
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
    Puerta("P1", "N", 10.4, 13.4, 4.5, "porton", "MP: autoelevador desde el alero de descarga"),
    Puerta("P2", "O", 39.0, 42.0, 4.0, "porton", "Scrap a volquete"),
    Puerta("RC-1", "O", 1.0, 5.0, 4.0, "porton", "Recargas: recepción de equipos"),
    Puerta("RC-2", "O", 16.2, 18.4, 4.0, "porton", "Recargas: despacho de equipos recargados"),
    Puerta("P6", "S", 18.8, 21.8, 4.0, "porton", "Carros a pintura tercerizada"),
    Puerta("P8", "S", 25.2, 28.2, 4.0, "porton", "Carros pintados, polvo, estructuras y ruedas de carros"),
    Puerta("P9", "S", 30.0, 33.0, 3.0, "porton", "Carros terminados (camión a nivel)"),
    Puerta("M3", "S", 34.4, 37.4, 3.2, "muelle", "Recepción de tercerizados y casquetes"),
    Puerta("M1", "S", 41.2, 44.2, 3.2, "muelle", "Expedición PT (rampa niveladora)"),
    Puerta("M2", "S", 45.6, 48.6, 3.2, "muelle", "Expedición PT (rampa niveladora)"),
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
LAZO = [(78.5, 21.4), (84.0, 21.4), (84.0, 2.6), (73.1, 2.6), (73.1, 14.2)]   # SE cargado del lazo de pintura

FLUJOS = [
    # ---------------- MP
    Flujo("MP", [(11.9, 52.0), (11.9, 43.8), (11.9, 27.3), (13.8, 27.3)], "Chapa: alero -> rack de la guillotina"),
    Flujo("MP", [(16.4, 27.3), (16.8, 27.3)], "Paquete a la mesa elevadora"),
    Flujo("MP", [(12.4, 52.0), (12.4, 43.8), (12.4, 32.4), (13.8, 32.4)], "Caño: alero -> cantiléver del láser"),
    Flujo("MP", [(16.4, 30.75), (16.8, 30.75)], "Atado al cargador"),
    Flujo("MP", [(16.4, 33.95), (16.8, 33.95)], "Atado al cargador"),
    Flujo("MP", [(12.9, 52.0), (12.9, 43.8), (12.9, 37.4), (13.8, 37.4)], "Flejes: alero -> porta-flejes"),
    Flujo("MP", [(16.4, 37.2), (16.8, 37.2)], "Rollo al desbobinador"),
    Flujo("MP", [(11.4, 52.0), (11.4, 43.8), (11.4, 34.5), (10.0, 34.5)], "Insumos al pañol"),
    Flujo("MP", [(35.2, -6.0), (35.2, 0.0), (35.2, 10.0), (34.0, 10.0)], "Casquetes de carros (M3)", "S3"),
    Flujo("MP", [(32.6, 10.0), (28.1, 10.0), (28.1, 12.2)], "Casquete a la soldadura circ.", "S3"),
    Flujo("MP", [(36.6, -6.0), (36.6, 0.0), (36.6, 1.5), (37.8, 1.5)], "Tercerizados revendidos (M3)", "S4"),
    Flujo("MP", [(64.5, -6.0), (64.5, 0.0), (64.5, 2.0), (68.6, 2.0)], "Polvo químico en big bags (P4)"),
    Flujo("MP", [(68.6, 5.2), (67.6, 5.2)], "Big bag a la carga de polvo"),
    Flujo("MP", [(48.2, -6.0), (48.2, 0.0), (48.2, 1.0), (50.2, 1.0)], "Válvulas, manómetros, cajas (muelle M2)"),
    Flujo("MP", [(55.5, 1.6), (55.5, 3.0), (59.3, 3.0), (59.3, 4.8)], "Válvulas a ensamblaje"),
    Flujo("MP", [(51.3, 1.6), (51.3, 4.4)], "Cajas y film a embalaje"),
    Flujo("MP", [(96.0, 27.5), (88.0, 27.5), (86.0, 27.5)], "Químicos y pintura en polvo (P3)"),
    Flujo("MP", [(86.0, 24.8), (86.0, 15.0), (85.1, 15.0)], "Desengrasante y fosfatizante al túnel"),
    Flujo("MP", [(87.0, 24.8), (87.0, 1.0), (78.6, 1.0), (78.6, 1.6)], "Pintura en polvo a la cabina"),
    Flujo("MP", [(26.7, -6.0), (26.7, 0.0), (26.7, 3.4)], "Carros pintados y polvo de carros (P8)", "S3"),
    # ---------------- SE: N1 corte y cuerpo 2,5-10 kg
    Flujo("SE", [(22.5, 27.5), (22.7, 27.5)], "Cuerpo cortado"),
    Flujo("SE", [(24.1, 27.5), (24.3, 27.5)], "Cuerpos al pulmón"),
    Flujo("SE", [(26.3, 27.2), (26.7, 27.2), (27.9, 27.2), (28.3, 27.2), (29.5, 27.2), (29.7, 27.2), (31.5, 27.2),
                 (31.8, 27.2), (33.5, 27.2), (33.7, 27.2), (35.5, 27.2), (35.8, 27.2), (38.0, 27.2), (38.2, 27.2)],
          "Cuerpo 2,5-10 kg: numerado -> cilindrado -> soldadura longitudinal", "S2"),
    Flujo("SE", [(38.9, 29.3), (38.9, 35.6)], "Cuerpos 2,5-10 kg al encastre", "S2"),
    Flujo("SE", [(25.3, 25.0), (25.3, 24.4), (25.3, 19.6), (25.3, 18.2)], "Cuerpos de carros a la cilindradora",
          "S3"),
    # ---------------- SE: N2 1 kg y N3 cúpulas y fondos
    Flujo("SE", [(27.0, 30.75), (27.4, 30.75)], "Cuerpo 1 kg"),
    Flujo("SE", [(27.0, 33.95), (27.4, 33.95)], "Cuerpo 1 kg"),
    Flujo("SE", [(28.3, 31.7), (28.3, 33.0)], "PU-L1 a PU-L2"),
    Flujo("SE", [(29.2, 34.0), (34.2, 34.0), (34.2, 36.1), (35.0, 36.1)], "Cuerpos 1 kg al encastre", "S1"),
    Flujo("SE", [(19.4, 37.2), (19.6, 37.2)], "Fleje enderezado"),
    Flujo("SE", [(21.0, 37.2), (21.2, 37.2)], "Fleje al troquel"),
    Flujo("SE", [(24.2, 37.1), (24.6, 37.1)], "Fondos al pulmón"),
    Flujo("SE", [(26.4, 37.6), (35.6, 37.6), (35.6, 36.6)], "Fondos al encastre"),
    Flujo("SE", [(23.8, 38.4), (23.8, 40.5)], "Cúpulas a la soldadura de cuello"),
    Flujo("SE", [(20.0, 41.1), (20.8, 41.1)], "Cuello preparado"),
    Flujo("SE", [(24.4, 41.1), (24.8, 41.1)], "Cúpulas con cuello al pulmón"),
    Flujo("SE", [(26.8, 41.4), (46.8, 41.4), (46.8, 37.2)], "Cúpulas a la soldadura circ."),
    Flujo("SE", [(43.8, 41.4), (43.8, 37.2)], "Cúpulas a la soldadura circ."),
    # ---------------- SE: N4-N5 línea principal (eje y = 36,1)
    Flujo("SE", [(36.2, 36.1), (36.8, 36.1), (38.0, 36.1), (38.6, 36.1), (39.8, 36.1), (40.8, 36.1), (42.0, 36.1),
                 (42.6, 36.1), (45.0, 36.1), (45.6, 36.1), (48.0, 36.1), (48.4, 36.1), (50.4, 36.1), (50.8, 36.1),
                 (54.0, 36.1), (54.4, 36.1), (57.6, 36.1), (58.0, 36.1), (59.6, 36.1), (60.0, 36.1), (64.0, 36.1),
                 (64.4, 36.1), (66.4, 36.1), (71.0, 36.1), (75.5, 36.1), (76.4, 36.1)],
          "Línea principal: encastre -> bordoneado -> soldadura circ. -> PH -> secado -> granallado"),
    Flujo("SE", [(78.6, 36.4), (80.0, 36.4)], "Defectos a corrección"),
    Flujo("SE", [(78.2, 35.8), (78.2, 33.2)], "Aprobados al pulmón de pintura"),
    Flujo("SE", [(81.9, 35.6), (81.9, 32.0), (80.4, 32.0)], "Corregidos al pulmón de pintura"),
    Flujo("SE", [(78.5, 30.4), (78.5, 24.4)], "A la carga de pintura"),
    # ---------------- SE: pintura (lazo) y terminación
    Flujo("SE", LAZO, "Lazo de pintura: pretratamiento, secado, cabina, polimerizado, enfriamiento"),
    Flujo("RET", [(73.1, 20.2), (73.1, 21.4), (76.0, 21.4)], "Retorno de ganchos vacíos (aéreo, +4,0 m)"),
    Flujo("SE", [(70.6, 15.0), (69.6, 15.0)], "Pintados al pulmón"),
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
    Flujo("PT", [(62.4, 16.0), (50.2, 16.0), (47.7, 16.0)], "Cilindros vendidos vacíos al almacén de PT"),
    Flujo("PT", [(50.5, 5.2), (49.7, 8.6)], "Pallet a envolvedora"),
    Flujo("PT", [(50.5, 7.2), (49.7, 9.6)], "Pallet a envolvedora"),
    Flujo("PT", [(50.5, 9.2), (49.7, 10.6)], "Pallet de cilindros a envolvedora"),
    Flujo("PT", [(48.2, 9.7), (46.0, 9.7), (46.0, 12.0)], "Almacén de PT"),
    Flujo("PT", [(40.4, 6.8), (40.4, 5.0), (42.7, 5.0), (42.7, 0.0), (42.7, -6.0)], "Expedición M1"),
    Flujo("PT", [(46.0, 6.8), (47.1, 5.0), (47.1, 0.0), (47.1, -6.0)], "Expedición M2"),
    Flujo("PT", [(32.8, 4.4), (32.8, 0.0), (32.8, -6.0)], "Carros terminados (P9)", "S3"),
    Flujo("PT", [(40.4, 2.0), (41.6, 2.0)], "Tercerizados a expedición", "S4"),
    # ---------------- scrap
    Flujo("SCRAP", [(2.0, 40.5), (0.0, 40.5), (-3.0, 40.5)], "Scrap a volquete (P2)"),
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
    br = [(5.0, Y_PP, 5.0, 31.4), (11.9, Y_PP, 11.9, 24.6)]
    br += _bajada(19.8, Y_PP, "M04")
    for c in ("B01", "B01b", "B02", "B03"):
        br += _bajada(_op(c)[0], Y_PP, c)
    H.append(("Almacén de MP y corte (N1)", [(0.0, Y_PP), (38.0, Y_PP)], br))
    # láseres, línea principal, cúpulas y calidad: por la calle PO-1
    br = [(40.0, 32.35, 21.9, 32.35), (21.9, 32.35, _op("M16")[0], _op("M16")[1])]
    br += [(40.0, 34.4, 35.6, 34.4)]
    for c in ("E09a", "E09b", "E09c"):
        x, y = _op(c)
        br.append((x, 34.4, x, y))
    br += [(40.0, 34.4, 58.0, 34.4)]
    for c in ("B04", "A06", "B06", "A07", "B07"):
        x, y = _op(c)
        br.append((x, 34.4, x, y))
    br += [(40.3, 34.4, 40.3, 39.45), (40.3, 39.45, 17.8, 39.45)]
    for c in ("M08", "M09", "M11"):
        x, y = _op(c)
        br.append((x, 39.45, x, y))
    H.append(("Láseres, cúpulas, unión y PH (N2-N4)", [(38.0, Y_PP), (40.0, Y_PP), (40.0, 34.4)], br))
    # granallado y defectos (N5) y pintura
    br = [(68.0, 34.2, 77.5, 34.2)]
    for c in ("B08", "B09"):
        x, y = _op(c)
        br.append((x, 34.2, x, y))
    br += [(77.5, 34.2, 79.2, 34.2), (79.2, 34.2, 79.2, 35.2), (79.2, 35.2, _op("B10")[0], _op("B10")[1])]
    br += [(69.8, Y_PP, 69.8, 24.6), (69.8, 24.6, 77.67, 24.6), (77.67, 24.6, 77.67, _op("P01")[1])]
    br += [(69.9, Y_PP, 69.9, _op("P08")[1]), (69.9, _op("P08")[1], _op("P08")[0], _op("P08")[1])]
    br += [(75.6, 21.0, 75.6, 5.0), (75.6, 5.0, _op("P04")[0], _op("P04")[1]), (69.9, 21.0, 75.6, 21.0)]
    H.append(("Granallado, defectos y pintura (N5, S-P)", [(38.0, Y_PP), (68.0, Y_PP), (68.0, 34.2)], br))
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
    Sector("SV-OF", "Oficina (6 puestos)", R(-15.0, 19.1, -8.6, 22.9), "SERV", "común",
           "Calidad, administración y ventas, compras, PCP y administrativo de la tarde (Servicios y Oficinas)"),
    Sector("SV-JP", "Jefatura de planta y reuniones", R(-8.4, 19.1, -5.4, 22.9), "SERV", "común",
           "Escritorio y mesa para 4"),
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
    *[Mb("escritorio", R(-14.9 + i * 1.8, 19.15, -13.2 + i * 1.8, 20.45), "N") for i in range(3)],
    *[Mb("escritorio", R(-14.9 + i * 1.8, 21.55, -13.2 + i * 1.8, 22.85), "S") for i in range(3)],
    Mb("archivo", R(-9.4, 19.15, -8.65, 19.6), "N", 2), Mb("pizarra", R(-14.98, 20.6, -14.9, 21.4), "E"),
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
    Mb("estanteria", R(48.6, 25.0, 49.15, 28.2), "O"), Mb("soldadora", R(41.3, 25.0, 42.3, 25.6), "N"),
    Mb("escritorio", R(46.6, 24.85, 48.4, 26.15), "N"), Mb("contenedor", R(45.0, 24.85, 46.4, 25.75), "N"),
    # ---- Q laboratorio de calidad
    Mb("marmol", R(49.5, 27.9, 51.5, 28.9), "S"), Mb("mesa_lab", R(51.8, 28.65, 55.0, 29.35), "S"),
    Mb("camara", R(55.3, 28.3, 56.75, 29.35), "S"), Mb("camara", R(55.9, 26.6, 56.75, 27.6), "O"),
    Mb("balanza_lab", R(49.5, 25.0, 50.2, 25.6), "N"), Mb("escritorio", R(50.5, 24.85, 52.3, 26.15), "N"),
    Mb("estanteria", R(52.6, 24.85, 54.6, 25.35), "N"), Mb("mesa_lab", R(54.9, 24.85, 56.75, 25.55), "N"),
    # ---- QR cuarentena
    Mb("jaula", R(57.1, 24.9, 60.9, 29.3), "S"), Mb("pallets", R(57.3, 27.8, 59.9, 29.1), "S", 1),
    Mb("cilindros_piso", R(57.3, 25.9, 58.9, 27.4), "S", 0),
    # ---- SUP supervisión y PCP
    Mb("escritorio", R(61.3, 28.0, 62.9, 29.35), "S"), Mb("escritorio", R(63.1, 28.0, 64.7, 29.35), "S"),
    Mb("pizarra", R(65.2, 25.5, 65.35, 27.5), "O"), Mb("mesa", R(61.4, 25.0, 63.4, 26.8), "S", 4),
    Mb("archivo", R(64.0, 24.85, 65.3, 25.35), "N", 3),
    # ---- EPP
    Mb("estanteria", R(65.7, 28.8, 69.7, 29.35), "S"), Mb("estanteria", R(65.65, 25.6, 66.15, 28.4), "E"),
    Mb("ventanilla", R(67.0, 24.85, 69.0, 25.5), "N"), Mb("botiquin", R(69.3, 26.0, 69.75, 26.8), "O"),
    Mb("lavaojos", R(69.1, 27.2, 69.75, 27.9), "O"),
    # ---- PV supermercado de carros vacíos (frente a la calle PO-2)
    Mb("carros_vacios", R(41.6, 29.7, 49.6, 31.3), "N", 10), Mb("carros_vacios", R(49.8, 29.7, 56.6, 31.3), "N", 8),
    Mb("carros_vacios", R(56.8, 29.7, 61.8, 31.3), "N", 5),
    # ---- ST-I tableros y compresor
    Mb("tablero_el", R(70.3, 30.6, 74.3, 31.35), "S", 4), Mb("compresor", R(70.4, 25.0, 73.4, 26.4), "N"),
    Mb("estanteria", R(75.6, 25.0, 76.15, 28.0), "O"),
    # ---- QP químicos y pintura en polvo
    Mb("tambores", R(81.0, 29.6, 84.4, 31.3), "S", 10), Mb("tambores", R(81.0, 25.0, 83.0, 26.4), "N", 6),
    Mb("pallets", R(84.8, 29.8, 87.5, 31.3), "S", 0), Mb("estanteria", R(85.0, 25.0, 87.5, 25.5), "N"),
    Mb("lavaojos", R(83.6, 25.0, 84.2, 25.6), "N"),
    # ---- franja norte: pañol de línea, escuelita, muestras y granalla
    Mb("estanteria", R(48.1, 43.0, 55.0, 43.55), "S"), Mb("estanteria", R(48.1, 41.2, 48.6, 42.7), "E"),
    Mb("ventanilla", R(52.0, 40.85, 54.0, 41.25), "N"), Mb("escritorio", R(55.2, 42.2, 57.0, 43.55), "S"),
    Mb("pallets", R(55.3, 40.9, 57.9, 42.0), "N", 0),
    Mb("cabina_sold", R(58.3, 41.0, 63.7, 43.55), "S", 3), Mb("mesa", R(63.9, 41.2, 65.5, 43.0), "E", 4),
    Mb("estanteria", R(67.7, 43.0, 75.9, 43.55), "S"), Mb("estanteria", R(68.5, 41.6, 74.5, 42.1), "S"),
    Mb("escritorio", R(74.6, 40.85, 75.95, 42.2), "N"),
    Mb("pallets", R(78.2, 42.3, 85.0, 43.5), "S", 0), Mb("estanteria", R(85.3, 42.9, 87.5, 43.55), "S"),
    Mb("contenedor", R(78.2, 40.9, 79.8, 41.9), "N"),
    # ---- expedición y tercerizados
    Mb("rampa", R(41.2, 0.35, 44.2, 2.35), "S"), Mb("rampa", R(45.6, 0.35, 48.6, 2.35), "S"),
    Mb("pallets", R(37.9, 0.4, 40.3, 6.5), "E", 0),
    # ---- AL-C: carga de baterías sobre el pasillo central y pallets de cilindros
    Mb("cargador", R(50.4, 16.9, 54.6, 18.75), "N", 3), Mb("pallets", R(50.4, 12.6, 62.2, 15.3), "S", 1),
    Mb("pallets", R(55.0, 16.7, 62.2, 18.6), "N", 1),
    # ---- RC-IR inutilizados y residuos
    Mb("jaula", R(0.6, 13.5, 2.6, 15.7), "E"), Mb("cilindros_piso", R(0.75, 13.7, 2.4, 15.5), "E", 0),
    Mb("tambores", R(2.8, 13.5, 4.1, 14.9), "O", 2), Mb("contenedor", R(2.8, 15.0, 4.1, 15.7), "O"),
]

# puertas interiores de una hoja: (x, y, ancho, muro 'h'/'v', abre +1/-1)
PUERTAS_INT = [
    (-16.2, 22.9, 0.8, "h", -1), (-9.5, 22.9, 0.8, "h", -1), (-6.5, 22.9, 0.8, "h", -1), (-4.6, 22.9, 0.9, "h", -1),
    (-1.1, 22.9, 0.8, "h", -1), (-13.0, 24.6, 0.9, "h", 1), (-12.9, 31.5, 0.9, "h", 1), (-8.2, 24.6, 0.8, "h", 1),
    (-10.2, 28.9, 0.8, "h", 1), (-6.3, 34.6, 0.8, "v", -1), (-4.9, 25.0, 0.9, "v", 1),
]

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
    ("PL-N", "Alero de descarga de MP (semi 18,6 m y chasis)", R(-1.0, 44.4, 22.0, 55.0), "playa"),
    ("VQ-O", "Volquete 6 m³ (scrap)", R(-9.0, 38.6, -3.0, 42.6), "volquete"),
    ("JG-S", "Jaula de gases de soldadura (Ar/CO₂)", R(48.0, 44.4, 56.0, 48.4), "jaula"),
    ("ERM", "Regulación de gas de hornos", R(88.6, 4.0, 91.6, 7.0), "gas"),
    ("JG-N", "Jaula de N₂ y CO₂ (manifold)", R(51.0, -6.0, 55.0, -1.0), "jaula"),
    ("RI", "Reserva de agua contra incendio y bombas", R(100.0, 34.0, 110.0, 44.0), "incendio"),
    ("AMP", "Reserva de ampliación (nave hacia el este)", R(92.0, -8.0, 114.0, 30.0), "reserva"),
    ("PTE", "Tratamiento de efluentes líquidos", R(64.0, -27.0, 76.0, -19.0), "efluentes"),
    ("EST", "Estacionamiento de personal (38 + 2 accesibles)", R(-28.0, -44.0, 30.0, -22.0), "estac"),
    ("EU", "Utilitarios de reparto y recargas (8)", R(-28.0, -4.0, -10.0, 8.0), "estac"),
    ("GAR", "Garita y control de acceso", R(20.0, -58.0, 24.0, -54.0), "garita"),
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
    (10.2, 13.6, "autoelevador al almacén de MP (AM)"),
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
