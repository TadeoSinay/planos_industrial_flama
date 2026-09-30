"""Modelo del layout de la planta industrial FLAMA S.A. al año 10 (2035).

Todas las medidas en METROS, en un sistema de coordenadas con origen en el
eje A-1 de la nave (esquina SO, cara interior de columnas), X hacia el este y
Y hacia el norte. La calle (acceso) está al sur.

El modelo es la fuente única de los cuatro planos (DIR, flujo de operaciones,
flujo de materiales y plano formal) y de la memoria de cálculo: si se mueve
un equipo acá, se mueve en todos los planos y se recalculan áreas y recorridos.

Concepto
--------
* Nave de una sola luz (36 m) sin columnas interiores, 15 módulos de 8 m (120 m).
* Flujo recto oeste -> este, sin cruces entre MP, SE y PT:
  MP y corte (O) -> celdas 1 kg y 2,5-10 kg -> pintura -> terminación -> PT y muelles (E).
  La línea de carros (25-100 kg) corre en la franja sur del sector MP, de este a
  oeste, y sale por su propio portón a la pintura tercerizada; los carros
  pintados vuelven por el portón este y se terminan junto al PT.
* Dos circulaciones separadas: pasillo de MATERIALES al norte (autoelevador y
  carros de SE) y pasillo de PERSONAL al sur, contra el bloque de servicios.
  Los operarios llegan a sus puestos por calles peatonales norte-sur que salen
  del pasillo de personal, sin recorrer el pasillo de materiales.
* Instalaciones pesadas (compresores, tablero general, colectores de polvo,
  tratamiento de efluentes, gas) sobre la fachada norte, cerca de sus consumos.
"""

from dataclasses import dataclass, field

# ---------------------------------------------------------------- nave
NAVE_L, NAVE_A = 120.0, 36.0          # largo (E-O) y ancho (N-S) entre ejes
MODULO = 8.0                          # separación de pórticos
ALTURA_LIBRE = 8.0                    # bajo cercha (m)
ALTURA_ALERO = 7.2
EJES_X = [i * MODULO for i in range(int(NAVE_L / MODULO) + 1)]   # 0 ... 120
EJES_Y = [0.0, NAVE_A]
COL = 0.40                            # columna de alma llena 400 mm
MURO = 0.20                           # cerramiento (zócalo de bloque + chapa)

# terreno (del rev4: 170 × 125 m, calle al sur) en coordenadas de la nave
TERRENO = (-24.0, -60.0, 146.0, 65.0)     # x0, y0, x1, y1 (170 × 125 m)


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


# ============================================================ PASILLOS
PASILLOS = [
    Pasillo("PP", R(0.3, 0.3, 119.7, 2.7), "PP", 2.4,
            "Pasillo de personal y evacuación (peatonal; carros manuales de herramientas)"),
    Pasillo("PM", R(36.0, 31.3, 72.2, 35.7), "PM", 4.4,
            "Pasillo de materiales: tren logístico de un sentido + retorno vacío; autoelevador"),
    Pasillo("AM", R(12.6, 13.9, 16.4, 35.7), "PM", 3.8,
            "Pasillo de autoelevador del sector MP (recepción, almacén y alimentación de máquinas)"),
    Pasillo("SE", R(36.0, 13.6, 40.0, 31.3), "SE", 4.0,
            "Colector de SE del sector MP: tramo inicial del tren logístico"),
    Pasillo("PN", R(16.4, 32.4, 27.6, 35.7), "PM", 3.3, "Calle norte del sector MP: flejes desde P1b"),
    Pasillo("PC", R(0.3, 9.9, 36.0, 13.6), "PM", 3.7,
            "Calle de la línea de carros: casquetes (P7), pluma, pulmones y scrap al oeste"),
    Pasillo("PO-A", R(40.2, 2.7, 41.4, 29.4), "PO", 1.2, "Calle de operarios celda 1 kg (bajada)"),
    Pasillo("PO-B", R(52.8, 2.7, 54.0, 26.4), "PO", 1.2, "Calle de operarios: 1 kg (subida) y 2,5-10 kg (bajada)"),
    Pasillo("PO-P", R(65.8, 2.7, 67.0, 24.2), "PO", 1.2, "Calle de operarios: 2,5-10 kg (subida) y carga de pintura"),
    Pasillo("PO-T", R(84.1, 2.7, 85.3, 22.0), "PO", 1.2, "Calle de operarios: descarga de pintura y terminación"),
    Pasillo("PO-T3", R(85.3, 20.8, 106.0, 22.0), "PO", 1.2, "Calle de operarios de terminación y acceso al almacén de PT"),
    Pasillo("PT-1", R(106.0, 12.0, 109.5, 35.7), "PM", 3.5, "Pasillo de autoelevador del almacén de PT"),
    Pasillo("PT-2", R(111.7, 17.0, 115.2, 35.7), "PM", 3.5, "Pasillo de autoelevador de PT y muelles"),
    Pasillo("PT-3", R(92.2, 8.6, 119.7, 11.8), "PM", 3.2, "Calle de carros pintados desde P8"),
]

# cruces peatonales señalizados (sendas): únicos puntos donde un hilo de personal corta un flujo
SENDAS = [
    ("SP-1", R(36.0, 22.4, 40.0, 23.6), "Personal de corte y control de recepción cruza el colector del tren logístico"),
    ("SP-2", R(36.0, 26.3, 40.0, 27.3), "Personal de prensa y cuellos cruza el colector del tren logístico"),
]

# ============================================================ SECTORES (nave)
SECTORES = [
    # ---- recepción y almacén de MP (oeste)
    Sector("BR", "Bahía interior de descarga", R(0.3, 24.0, 12.6, 35.7), "MP", "común",
           "Chasis de hasta 10 m entra por P1 y se descarga por los dos lados con autoelevador"),
    Sector("AL-1H", "Chapa en hojas", R(10.8, 13.9, 12.6, 23.8), "MP", "común",
           "Cantiléver de 3 módulos × 5 niveles = 15 paquetes ≤ 2 t; un formato por módulo, FIFO", 50.0),
    Sector("AL-1F", "Flejes", R(16.6, 30.8, 26.4, 32.2), "MP", "común",
           "Porta-flejes de 7 módulos × 3 niveles = 21 rollos + 6 en espera junto al desbobinador", 43.2),
    Sector("AL-1T", "Caño Ø76,2 × 6 m", R(16.4, 17.6, 18.0, 24.6), "MP", "S1",
           "Cantiléver de 7 m, 3 niveles × 4 atados = 12 atados", 30.8),
    Sector("AL-1C", "Casquetes de carros", R(12.0, 8.3, 18.0, 9.7), "MP", "S3",
           "Rack de 3 niveles × 6 pallets = 18 posiciones, junto a la soldadura circunferencial", 20.0),
    Sector("PÑ", "Pañol de insumos pesados", R(0.3, 18.8, 10.6, 23.8), "MP", "común",
           "Alambre MIG, granalla, asientos de válvula y cuplas, tapones, consumibles", 35.2),
    Sector("SCR-O", "Scrap oeste (orillas de hoja)", R(0.3, 13.9, 10.6, 18.6), "AUX", "común",
           "Contenedores basculantes de 1 m³; salen por P2 al volquete del patio oeste"),
    Sector("SCR-N", "Scrap norte (esqueleto de fleje)", R(27.8, 31.4, 30.7, 35.7), "AUX", "común",
           "Contenedores basculantes; salen por P2b al volquete del patio norte"),
    Sector("MQ-G", "Corte de cuerpos (guillotina)", R(16.4, 13.9, 30.6, 17.4), "PROD", "S2 / S3"),
    Sector("MQ-T", "Corte de caño 1 kg", R(18.4, 17.6, 22.2, 26.4), "PROD", "S1"),
    Sector("MQ-K", "Cúpulas, fondos y cuellos", R(16.4, 27.4, 30.6, 30.6), "PROD", "S1 / S2"),
    Sector("SM-K", "Supermercado de cúpulas y fondos", R(30.9, 27.4, 35.8, 31.2), "PROD", "S1 / S2"),
    Sector("PU-G", "Pulmón de cuerpos cortados", R(30.8, 13.9, 35.8, 19.0), "PROD", "S2 / S3"),
    Sector("OP-MP", "Control de recepción y puestos del sector MP", R(22.4, 17.6, 35.8, 26.4), "PROD", "común",
           "Mesa de control (certificado, espesor, colada), franjas en proceso y retal aprovechable"),
    # ---- línea de carros (S3)
    Sector("S3", "Línea de carros 25-100 kg", R(0.3, 2.7, 36.0, 9.9), "PROD", "S3",
           "Flujo este-oeste: cilindrado, armado, soldaduras, inspección, PH 4,0 MPa y marcado"),
    # ---- celdas
    Sector("S1", "Celda 1 kg", R(41.4, 12.0, 52.8, 31.3), "PROD", "S1"),
    Sector("S2", "Celda 2,5-10 kg", R(54.0, 11.6, 65.8, 31.3), "PROD", "S2"),
    Sector("Q", "Laboratorio de calidad", R(41.6, 2.9, 48.6, 8.2), "CAL", "común",
           "Rotura, expansión, potencial extintor; control de polvo y de soldadura", 36.2),
    Sector("QR", "Cuarentena y lotes retenidos", R(41.6, 8.4, 46.2, 11.8), "CAL", "común",
           "Jaula con llave: lotes rechazados y muestras", 15.0),
    Sector("EPP", "EPP y botiquín", R(46.4, 8.4, 48.6, 11.8), "AUX", "común"),
    Sector("MT", "Mantenimiento y pañol de herramientas", R(55.0, 2.9, 62.0, 8.2), "AUX", "común",
           "Banco, torno chico y repuestos", 30.0),
    Sector("SUP", "Supervisión de planta", R(62.2, 2.9, 65.6, 8.2), "AUX", "común", "Encargado de turno y PCP"),
    # ---- pintura
    Sector("S-P", "Pintura en polvo 1-10 kg", R(67.8, 2.7, 84.1, 31.3), "PINT", "S1 / S2",
           "Transporte aéreo por empuje: pretratamiento, secado, cabina y polimerizado"),
    Sector("QP", "Químicos y pintura en polvo", R(73.6, 31.5, 79.4, 35.7), "MP", "S1 / S2",
           "Batea ≥ 110 % del mayor envase; pintura en polvo < 30 °C", 24.1),
    # ---- terminación 1-10 kg (línea recta hacia el muelle M1)
    Sector("AL-PV", "Polvo químico en big bags", R(85.5, 30.4, 92.5, 35.7), "MP", "S1 / S2",
           "21 posiciones a 2 alturas, HR ≤ 70 %, entra por P4", 23.1),
    Sector("AL-2", "Insumos de terminación y embalaje", R(92.7, 30.4, 104.0, 35.7), "MP", "S1 / S2",
           "Rack de 4 niveles: válvulas, manómetros, mangueras, etiquetas, cajas, film y pallets; entra por P5", 97.5),
    Sector("SP-1", "Sala de carga de polvo 1-10 kg", R(85.5, 22.2, 92.5, 30.2), "TERM", "S1 / S2",
           "Recinto cerrado HR ≤ 70 %, 8 renovaciones por hora, sin estufas (IRAM 3517-2)"),
    Sector("S-T", "Terminación 1-10 kg", R(92.7, 22.2, 104.0, 30.2), "TERM", "S1 / S2",
           "Ensamblaje, presurización con N₂, hermeticidad, etiquetado, embalaje y palletizado"),
    Sector("BAT", "Carga de baterías de autoelevadores", R(85.5, 13.4, 92.0, 20.6), "AUX", "común",
           "Local ventilado con lavaojos; estacionamiento de autoelevadores y tractor del tren logístico"),
    Sector("EST", "Estacionamiento de transpaletas y carros", R(92.2, 12.0, 98.0, 20.6), "AUX", "común"),
    Sector("OF-E", "Oficina de expedición", R(98.2, 12.0, 104.0, 20.6), "AUX", "común"),
    # ---- carros: vuelven pintados por P8, se terminan y salen por P9 (recorrido en U)
    Sector("SP-2", "Sala de carga de polvo de carros", R(85.5, 2.9, 92.0, 11.8), "TERM", "S3",
           "Recinto HR ≤ 70 %: big bags propios y cabina de descarga de muestras (IRAM 3550)"),
    Sector("S-TC", "Terminación de carros", R(92.2, 2.9, 104.0, 8.4), "TERM", "S3",
           "Armado de ruedas y manguera, presurización y etiquetado"),
    Sector("PTC", "Carros terminados", R(104.2, 2.9, 119.7, 8.4), "PT", "S3", "0,5 m² por carro a piso", 25.0),
    # ---- PT
    Sector("AL-3", "Almacén de producto terminado", R(104.2, 17.0, 115.2, 35.7), "PT", "S1 / S2",
           "Rack de 2 frentes × 6 módulos × 2 pallets × 4 niveles = 96 posiciones (req. 88)"),
    Sector("EXP", "Expedición y muelles", R(115.2, 17.0, 119.7, 35.7), "PT", "común",
           "Consolidación de pedidos frente a M1-M2 (2 × 8 pallets)"),
    Sector("S4", "Tercerizados revendidos", R(111.7, 12.0, 119.7, 16.8), "PT", "S4",
           "CO₂, agua, AFFF, clase K y agente limpio con sello IRAM: recepción, control y stock"),
]

# ============================================================ EQUIPOS
# fuente: C = cotización recibida (referencias/INVESTIGACION PROVEEDORES), E = estimado de catálogo
EQUIPOS = [
    # ---- MP y corte
    Equipo("M01", "Balanza de plataforma 3 t", Rw(10.6, 24.4, 1.5, 1.5), "BR", 0, 0.1, fuente="MP Manipulación"),
    Equipo("M02", "Mesa elevadora de tijera 3 t", Rw(16.6, 14.1, 1.5, 3.0), "MQ-G", 0, 2.2, fuente="MP Manipulación"),
    Equipo("M03", "Mesa de bolas", Rw(18.2, 14.0, 2.0, 3.2), "MQ-G", 0, fuente="MP Manipulación"),
    Equipo("M04", "Guillotina hidráulica 8 × 3200", Rw(20.3, 13.95, 2.3, 4.2), "MQ-G", 1, 15.0, fuente="C Cena E21"),
    Equipo("M05", "Mesa de salida", Rw(22.8, 14.2, 3.0, 2.6), "MQ-G", 0, fuente="E"),
    Equipo("M15", "Láser de tubo 6012", Rw(18.8, 18.6, 0.8, 6.85), "MQ-T", 1, 10.0, aire=True, polvo=True,
           fuente="C Leapion 6012"),
    Equipo("M16", "Láser de tubo 6012", Rw(20.8, 18.6, 0.8, 6.85), "MQ-T", 0, 10.0, aire=True, polvo=True,
           fuente="C Leapion 6012"),
    Equipo("M17", "Pulmón de cuerpos 1 kg", Rw(18.6, 25.55, 3.6, 0.8), "MQ-T", 0, fuente="E", forma="rack"),
    Equipo("M13", "Mesa de control de recepción", Rw(24.0, 20.8, 2.4, 1.2), "OP-MP", 1, fuente="E"),
    Equipo("M06", "Desbobinador y enderezador", Rw(16.6, 27.6, 2.4, 2.0), "MQ-K", 0, 3.0, fuente="C alimentador 900 mm"),
    Equipo("M07", "Alimentador servo", Rw(19.1, 28.0, 1.4, 1.2), "MQ-K", 0, 2.0, fuente="C alimentador 900 mm"),
    Equipo("M08", "Prensa de corte y embutido 300 t", Rw(20.7, 27.6, 3.0, 2.6), "MQ-K", 1, 30.0, aire=True,
           fuente="C PHM 300"),
    Equipo("M09", "Preparación de cuello", Rw(24.4, 29.4, 1.2, 1.0), "MQ-K", 1, 3.0, aire=True, fuente="E"),
    Equipo("M10", "Preparación de cuello", Rw(24.4, 27.7, 1.2, 1.0), "MQ-K", 0, 3.0, aire=True, fuente="E"),
    Equipo("M11", "Soldadura circ. de cuello", Rw(26.2, 29.3, 1.6, 1.2), "MQ-K", 1, 12.0, polvo=True,
           fuente="C FS-HFM1"),
    Equipo("M12", "Soldadura circ. de cuello", Rw(26.2, 27.6, 1.6, 1.2), "MQ-K", 0, 12.0, polvo=True,
           fuente="C FS-HFM1"),
    # ---- S3 línea de carros (flujo E -> O)
    Equipo("C01", "Cilindradora de 4 rodillos", Rw(30.6, 4.6, 4.5, 1.4), "S3", 1, 5.5, fuente="C Getweld"),
    Equipo("C02", "Punteo, refuerzo y estructura", Rw(26.8, 4.5, 2.5, 1.5), "S3", 1, 10.0, polvo=True, fuente="E"),
    Equipo("C03", "Punteo, refuerzo y estructura", Rw(23.6, 4.5, 2.5, 1.5), "S3", 1, 10.0, polvo=True, fuente="E"),
    Equipo("C04", "Soldadura longitudinal de carros", Rw(19.4, 4.3, 3.0, 2.0), "S3", 1, 18.0, polvo=True,
           fuente="C Getweld ZF-1000"),
    Equipo("C05", "Soldadura circ. de fondo y cúpula", Rw(15.2, 4.4, 3.0, 1.8), "S3", 1, 18.0, polvo=True,
           fuente="E"),
    Equipo("C06", "Inspección de costuras", Rw(11.8, 4.5, 2.5, 1.5), "S3", 1, 0.5, fuente="E"),
    Equipo("C07", "PH 4,0 MPa con jaula", Rw(7.4, 4.0, 3.6, 2.6), "S3", 1, 2.0, agua=True,
           fuente="C Yukon M-000200 + jaula"),
    Equipo("C08", "Marcado del recipiente", Rw(5.0, 4.5, 1.5, 1.0), "S3", 0, 0.5, fuente="E"),
    Equipo("C09", "Probetas de soldadura", Rw(23.6, 7.0, 2.5, 1.2), "S3", 0, 2.0, fuente="E"),
    Equipo("C10", "Pluma giratoria 1 t", Rw(19.0, 7.2, 0.6, 0.6), "S3", 0, 1.5, fuente="E", forma="circ"),
    Equipo("C11", "Pluma giratoria 1 t", Rw(9.0, 7.2, 0.6, 0.6), "S3", 0, 1.5, fuente="E", forma="circ"),
    Equipo("C12", "Carros a pintura tercerizada", Rw(0.6, 3.2, 3.6, 6.2), "S3", 0, fuente="E", forma="rack"),
    # ---- S1 celda 1 kg (horquilla: baja por el oeste, sube por el este)
    Equipo("A00", "Kanban de cuerpos, fondos y cúpulas", Rw(41.6, 27.4, 2.4, 3.6), "S1", 0, fuente="E", forma="rack"),
    Equipo("A03", "Numerado de cuerpo", Rw(41.8, 25.6, 1.2, 0.8), "S1", 1, 0.5, fuente="E"),
    Equipo("A04", "Encastre de fondo", Rw(41.8, 23.2, 1.2, 1.0), "S1", 1, 1.0, aire=True, fuente="E"),
    Equipo("A05", "Encastre de fondo y cúpula", Rw(41.8, 21.2, 1.2, 1.0), "S1", 1, 1.0, aire=True, fuente="E"),
    Equipo("A09", "Pulmón de cuerpos armados", Rw(41.8, 13.2, 1.4, 7.0), "S1", 0, fuente="E", forma="rack"),
    Equipo("A06", "Soldadura circ. cúpula y fondo", Rw(50.9, 13.4, 1.6, 2.0), "S1", 1, 15.0, polvo=True,
           fuente="C Getweld"),
    Equipo("A07", "Prueba hidráulica automática", Rw(50.9, 16.2, 1.5, 3.0), "S1", 1, 4.0, agua=True,
           fuente="C Firesafer FS-JD12A"),
    Equipo("A10", "Pulmón de cilindros probados", Rw(50.8, 19.8, 1.8, 5.8), "S1", 0, fuente="E", forma="rack"),
    Equipo("A08", "Pulmón a pintura", Rw(50.8, 26.6, 1.8, 4.5), "S1", 0, fuente="E", forma="rack"),
    # ---- S2 celda 2,5-10 kg (horquilla)
    Equipo("B00", "Supermercado de cuerpos y cúpulas", Rw(54.4, 27.8, 2.4, 3.3), "S2", 0, fuente="E", forma="rack"),
    Equipo("B01", "Numerado de cuerpo", Rw(54.6, 26.2, 1.2, 0.8), "S2", 1, 0.5, fuente="E"),
    Equipo("B02", "Cilindradora", Rw(54.8, 23.4, 0.8, 1.7), "S2", 1, 1.1, fuente="C Bästlein"),
    Equipo("B03", "Soldadura longitudinal", Rw(54.4, 20.2, 1.6, 2.2), "S2", 1, 12.0, polvo=True,
           fuente="C Mitusa GS2ft Ergo"),
    Equipo("B04", "Bordoneadora", Rw(54.6, 18.0, 1.2, 0.9), "S2", 1, 1.5, fuente="C SWM-400"),
    Equipo("B05", "Encastre de fondo y cúpula", Rw(54.6, 16.0, 1.2, 1.0), "S2", 1, 1.0, aire=True, fuente="E"),
    Equipo("B06", "Soldadura circ. cúpula y fondo", Rw(54.4, 12.8, 1.6, 2.2), "S2", 1, 15.0, polvo=True,
           fuente="C SCWelding PRO WP150"),
    Equipo("B07", "Prueba hidráulica automática", Rw(57.4, 12.0, 3.0, 1.5), "S2", 1, 4.0, agua=True,
           fuente="C Firesafer FS-JD12A"),
    Equipo("B12", "Fondos y cúpulas (kanban)", Rw(56.8, 15.4, 1.2, 3.2), "S2", 0, fuente="E", forma="rack"),
    Equipo("B08", "Granalladora", Rw(64.0, 13.0, 1.3, 4.5), "S2", 1, 15.0, polvo=True, fuente="C Airblast G-100"),
    Equipo("B13", "Colector de polvo", Rw(62.4, 13.2, 1.3, 1.4), "S2", 0, 5.5, polvo=True, fuente="E"),
    Equipo("B09", "Detección de defectos", Rw(63.4, 19.0, 2.2, 1.2), "S2", 1, 0.5, fuente="E"),
    Equipo("B10", "Corrección de defectos", Rw(63.4, 21.4, 2.2, 1.5), "S2", 1, 10.0, polvo=True, fuente="E"),
    Equipo("B11", "Pulmón a pintura", Rw(62.4, 26.6, 3.2, 4.5), "S2", 0, fuente="E", forma="rack"),
    # ---- pintura (circuito cerrado, transporte aéreo por empuje)
    Equipo("P01", "Tren de carga", Rw(68.4, 24.4, 5.0, 6.6), "S-P", 2, fuente="C Electricolor"),
    Equipo("P02", "Túnel de pretratamiento (3 etapas)", Rw(68.6, 14.8, 2.2, 8.4), "S-P", 0, 11.0, agua=True,
           polvo=True, fuente="E SP Ingeniería / Electricolor"),
    Equipo("P03", "Horno de secado 6 × 2,44 m", Rw(68.5, 7.6, 2.44, 6.0), "S-P", 0, 3.0, gas=True,
           fuente="C Electricolor"),
    Equipo("P04", "Cabina de pintura y reciprocador", Rw(73.6, 3.4, 2.0, 1.5), "S-P", 1, 5.0, aire=True, polvo=True,
           fuente="C Electricolor EC40-200D"),
    Equipo("P05", "Ciclones de recuperación", Rw(76.2, 3.2, 2.6, 1.2), "S-P", 0, 11.0, polvo=True,
           fuente="C Electricolor"),
    Equipo("P06", "Horno de polimerizado 6 × 2,44 m", Rw(81.2, 7.6, 2.44, 6.0), "S-P", 0, 3.0, gas=True,
           fuente="C Electricolor"),
    Equipo("P07", "Enfriamiento", Rw(81.2, 14.8, 2.44, 8.4), "S-P", 0, fuente="E"),
    Equipo("P08", "Tren de descarga", Rw(78.4, 24.4, 5.4, 6.6), "S-P", 1, fuente="C Electricolor"),
    Equipo("P09", "Retoque y control de espesor", Rw(74.8, 18.0, 2.4, 1.6), "S-P", 0, fuente="E"),
    # ---- terminación 1-10 kg
    Equipo("T01", "Carga de polvo 1-10 kg", Rw(88.4, 25.2, 3.4, 3.0), "SP-1", 1, 3.0, aire=True, polvo=True,
           fuente="C Yukon M-000121 + estación de big bag"),
    Equipo("T15", "Deshumidificador y extracción", Rw(85.8, 22.5, 2.4, 1.2), "SP-1", 0, 6.0, fuente="E"),
    Equipo("T03", "Ensamblaje de válvula", Rw(93.2, 26.6, 2.0, 1.0), "S-T", 1, 0.5, aire=True, fuente="E"),
    Equipo("T04", "Ensamblaje de válvula", Rw(93.2, 24.6, 2.0, 1.0), "S-T", 1, 0.5, aire=True, fuente="E"),
    Equipo("T05", "Presurización con N₂", Rw(96.0, 25.6, 1.5, 1.0), "S-T", 1, 0.5, n2=True,
           fuente="C Yukon M-000150"),
    Equipo("T06", "Hermeticidad", Rw(98.0, 25.6, 1.5, 1.0), "S-T", 0, 0.5, fuente="E"),
    Equipo("T07", "Etiquetadora semiautomática", Rw(100.0, 25.7, 1.5, 0.8), "S-T", 1, 0.5, fuente="C SISA"),
    Equipo("T08", "Embalaje y palletizado", Rw(101.9, 26.8, 2.0, 1.5), "S-T", 1, fuente="E"),
    Equipo("T09", "Embalaje y palletizado", Rw(101.9, 24.2, 2.0, 1.5), "S-T", 1, fuente="E"),
    Equipo("T10", "Palletizado de cilindros vendidos", Rw(101.9, 28.6, 2.0, 1.5), "S-T", 1, fuente="E"),
    Equipo("T11", "Envolvedora de pallets", Rw(104.4, 26.4, 1.5, 3.0), "AL-3", 0, 1.5, fuente="C EDOS PS5"),
    Equipo("RK1", "Rack de PT, frente oeste (6 × 2 × 4)", Rw(109.5, 18.6, 1.1, 16.2), "AL-3", 0, fuente="E", forma="rack"),
    Equipo("RK2", "Rack de PT, frente este (6 × 2 × 4)", Rw(110.6, 18.6, 1.1, 16.2), "AL-3", 0, fuente="E", forma="rack"),
    # ---- terminación de carros
    Equipo("T02", "Carga de polvo de carros", Rw(86.0, 7.8, 3.0, 2.6), "SP-2", 1, 2.0, aire=True, polvo=True,
           fuente="E"),
    Equipo("Q01", "Cabina de descarga de muestras", Rw(86.0, 3.2, 3.6, 3.0), "SP-2", 0, 3.0, polvo=True,
           fuente="E"),
    Equipo("T12", "Armado de carros", Rw(93.0, 4.6, 3.0, 2.2), "S-TC", 1, 0.5, aire=True, fuente="E"),
    Equipo("T13", "Presurización y etiquetado de carros", Rw(97.6, 4.6, 2.6, 2.2), "S-TC", 1, 0.5, n2=True,
           fuente="E"),
    Equipo("T14", "Estructuras y ruedas de carros", Rw(101.0, 6.0, 3.0, 2.2), "S-TC", 0, fuente="E", forma="rack"),
]

# ============================================================ PUERTAS Y PORTONES
PUERTAS = [
    Puerta("P1", "N", 4.0, 9.0, 5.0, "porton", "MP: chasis a la bahía interior"),
    Puerta("P1b", "N", 12.9, 16.1, 4.0, "porton", "MP: autoelevador desde la playa exterior (semi)"),
    Puerta("P2", "O", 14.4, 18.0, 4.0, "porton", "Scrap oeste a volquete"),
    Puerta("P2b", "N", 27.9, 30.6, 3.5, "porton", "Scrap norte a volquete"),
    Puerta("P6", "O", 4.0, 8.0, 4.0, "porton", "Carros a pintura tercerizada"),
    Puerta("P7", "O", 10.2, 13.4, 4.0, "porton", "Casquetes de carros"),
    Puerta("P3", "N", 74.8, 77.8, 3.0, "porton", "Químicos y pintura en polvo"),
    Puerta("P4", "N", 87.0, 91.0, 4.0, "porton", "Polvo químico (big bags)"),
    Puerta("P5", "N", 96.0, 100.0, 4.0, "porton", "Insumos de terminación y embalaje"),
    Puerta("P8", "E", 8.6, 11.8, 4.0, "porton", "Carros pintados, polvo de carros, estructuras y ruedas"),
    Puerta("P9", "E", 3.4, 7.4, 4.0, "porton", "Carros terminados (camión a nivel)"),
    Puerta("M1", "E", 27.0, 30.0, 3.2, "muelle", "Expedición PT (rampa niveladora)"),
    Puerta("M2", "E", 20.0, 23.0, 3.2, "muelle", "Expedición PT (rampa niveladora)"),
    Puerta("M3", "E", 13.0, 16.0, 3.2, "muelle", "Recepción de tercerizados y devoluciones"),
    # salidas de emergencia (1,10 m, barral antipánico, abren hacia afuera)
    Puerta("SE-1", "O", 20.5, 21.6, 2.1, "emergencia"),
    Puerta("SE-2", "N", 22.0, 23.1, 2.1, "emergencia"),
    Puerta("SE-3", "N", 46.0, 47.1, 2.1, "emergencia"),
    Puerta("SE-4", "N", 62.0, 63.1, 2.1, "emergencia"),
    Puerta("SE-5", "N", 81.0, 82.1, 2.1, "emergencia"),
    Puerta("SE-6", "N", 110.0, 111.1, 2.1, "emergencia"),
    Puerta("SE-7", "S", 20.0, 21.1, 2.1, "emergencia"),
    Puerta("SE-8", "S", 67.4, 68.5, 2.1, "emergencia", "Al pasaje exterior entre servicios y recargas"),
    Puerta("SE-9", "S", 101.0, 102.1, 2.1, "emergencia"),
    Puerta("SE-10", "E", 33.0, 34.1, 2.1, "emergencia"),
    Puerta("PP-1", "S", 50.4, 52.4, 2.1, "peatonal", "Ingreso de personal desde vestuarios"),
    Puerta("PP-3", "S", 71.0, 72.2, 2.1, "peatonal", "Núcleo sanitario este (en el ala de recargas)"),
]

# ============================================================ ANEXOS (fuera de la nave)
ANEXOS = [
    Sector("SV", "Bloque de servicios al personal y oficinas", R(38.0, -13.0, 66.0, 0.0), "SERV", "común"),
    Sector("RC", "Recargas (ala propia)", R(70.0, -17.0, 98.0, 0.0), "RC", "RC"),
    Sector("ST", "Sala técnica: transformador, TGBT y compresores", R(52.0, 36.0, 64.0, 42.0), "AUX", "común"),
]

# ============================================================ FLUJOS (m)
# MP azul, SE naranja, PT verde, SCRAP gris, EFL-L marrón, EFL-G cian, TL tren logístico (SE) y RET retorno vacío
TL = [(39.2, 14.6), (39.2, 32.2), (71.8, 32.2), (71.8, 34.6), (37.0, 34.6), (37.0, 14.6), (39.2, 14.6)]
# tramo cargado: baja por el colector recogiendo (SM-K, láser, PU-G), sube y entrega/retira en celdas y pintura
TL_CARGADO = [(37.0, 34.6), (37.0, 14.6), (39.2, 14.6), (39.2, 32.2), (71.8, 32.2), (71.8, 34.6)]
TL_RETORNO = [(71.8, 34.6), (37.0, 34.6)]

FLUJOS = [
    # ---------------- MP
    Flujo("MP", [(6.5, 44.0), (6.5, 36.0), (6.5, 27.0), (12.6, 25.2), (13.2, 25.2), (13.2, 18.9), (12.6, 18.9)],
          "Chapa en hojas (chasis en bahía interior)"),
    Flujo("MP", [(12.6, 15.6), (16.6, 15.6)], "Paquete a la mesa elevadora"),
    Flujo("MP", [(8.0, 44.0), (8.0, 36.0), (8.0, 29.5), (12.6, 29.5), (15.0, 26.3), (15.0, 21.1), (16.4, 21.1)], "Caño en atados (chasis)"),
    Flujo("MP", [(18.0, 21.1), (18.8, 21.1)], "Barra al láser"),
    Flujo("MP", [(14.2, 44.0), (14.2, 36.0), (14.2, 33.8), (21.5, 33.8), (21.5, 32.2)], "Flejes (semi en playa norte)"),
    Flujo("MP", [(16.6, 31.5), (15.6, 31.5), (15.6, 29.8), (16.6, 29.8)], "Rollo al desbobinador"),
    Flujo("MP", [(4.6, 44.0), (4.6, 36.0), (4.6, 30.0), (3.0, 28.0), (3.0, 23.8)], "Insumos al pañol"),
    Flujo("MP", [(-6.0, 11.8), (0.0, 11.8), (15.0, 11.8), (15.0, 9.7)], "Casquetes (P7)"),
    Flujo("MP", [(15.0, 8.3), (15.9, 6.2)], "Casquete a la soldadura circ."),
    Flujo("MP", [(89.0, 44.0), (89.0, 36.0), (89.0, 30.4), (90.1, 28.2)], "Polvo químico (big bags)"),
    Flujo("MP", [(98.0, 44.0), (98.0, 36.0), (98.0, 30.4), (94.2, 27.6)], "Válvulas, manómetros, etiquetas, cajas"),
    Flujo("MP", [(76.3, 44.0), (76.3, 36.0), (76.3, 31.5)], "Químicos y pintura en polvo"),
    Flujo("MP", [(76.3, 31.5), (76.3, 24.0), (71.4, 19.0)], "Desengrasante y fosfatizante al túnel"),
    Flujo("MP", [(76.3, 24.0), (76.3, 20.0), (74.6, 4.9)], "Pintura en polvo a la cabina"),
    Flujo("MP", [(128.0, 9.0), (119.7, 9.0), (102.5, 9.0), (102.5, 8.2)], "Estructuras y ruedas de carros (P8)"),
    Flujo("MP", [(128.0, 10.8), (119.7, 10.8), (92.0, 10.8), (91.2, 10.8)], "Polvo de carros (P8)"),
    Flujo("MP", [(128.0, 14.5), (119.7, 14.5), (116.0, 14.5)], "Tercerizados revendidos (M3)"),
    # ---------------- SE: sector MP y línea de carros
    Flujo("SE", [(22.6, 16.0), (25.8, 16.0), (30.8, 16.0)], "Cuerpos cortados al pulmón"),
    Flujo("SE", [(32.8, 13.9), (32.8, 6.0)], "Cuerpos de carros a la cilindradora"),
    Flujo("SE", [(32.8, 5.3), (29.3, 5.3), (26.1, 5.3), (22.4, 5.3), (18.2, 5.3), (14.3, 5.3), (11.0, 5.3),
                 (6.5, 5.0), (4.2, 5.6), (0.0, 5.6), (-6.0, 5.6)], "Línea de carros -> pintura tercerizada (P6)",
          "S3"),
    Flujo("SE", [(35.8, 17.2), (37.0, 17.2)], "Cuerpos 2,5-10 kg al tren logístico"),
    Flujo("SE", [(19.2, 25.45), (19.2, 25.55)], "Cuerpo 1 kg"),
    Flujo("SE", [(21.2, 25.45), (21.2, 25.55)], "Cuerpo 1 kg"),
    Flujo("SE", [(22.2, 25.95), (36.0, 25.95), (37.0, 25.95)], "Cuerpos 1 kg al tren logístico"),
    Flujo("SE", [(19.0, 28.6), (20.7, 28.6), (23.7, 28.6), (24.4, 28.6), (27.8, 28.6), (30.9, 28.6)],
          "Discos -> cúpulas y fondos -> cuellos"),
    Flujo("SE", [(35.8, 28.6), (37.0, 28.6)], "Cúpulas y fondos al tren logístico"),
    # ---------------- SE: tren logístico (recorrido de un sentido) y celdas
    Flujo("TL", TL_CARGADO, "Tren logístico (tractor eléctrico + 3 carros), un solo sentido"),
    Flujo("RET", TL_RETORNO, "Retorno vacío"),
    Flujo("SE", [(42.8, 32.2), (42.8, 31.0)], "Entrega a la celda 1 kg"),
    Flujo("SE", [(42.4, 27.4), (42.4, 26.4), (42.4, 24.2), (42.4, 22.2), (42.4, 20.2), (42.4, 12.6), (51.7, 12.6),
                 (51.7, 13.4), (51.7, 15.4), (51.7, 19.2), (51.7, 25.6), (51.7, 26.6)], "Celda 1 kg", "S1"),
    Flujo("SE", [(51.7, 31.1), (51.7, 32.2)], "1 kg al tren logístico"),
    Flujo("SE", [(55.6, 32.2), (55.6, 31.1)], "Entrega a la celda 2,5-10 kg"),
    Flujo("SE", [(55.2, 27.8), (55.2, 27.0), (55.2, 25.1), (55.2, 22.4), (55.2, 18.9), (55.2, 17.0), (55.2, 12.75),
                 (57.4, 12.75), (60.4, 12.75), (64.65, 13.0), (64.65, 17.5), (64.5, 19.0), (64.5, 22.9), (64.0, 26.6)],
          "Celda 2,5-10 kg", "S2"),
    Flujo("SE", [(64.0, 31.1), (64.0, 32.2)], "2,5-10 kg al tren logístico"),
    Flujo("SE", [(70.9, 32.2), (70.9, 31.0)], "Entrega al tren de carga de pintura"),
    Flujo("SE", [(69.7, 24.4), (69.7, 23.2), (69.7, 14.8), (69.7, 13.6), (69.7, 7.6), (69.7, 5.4), (73.6, 4.2),
                 (75.6, 4.2), (82.4, 5.4), (82.4, 7.6), (82.4, 13.6), (82.4, 14.8), (82.4, 23.2), (81.1, 24.4)],
          "Pintura: pretratamiento, secado, cabina, polimerizado, enfriamiento"),
    # ---------------- SE: terminación 1-10 kg
    Flujo("SE", [(83.8, 27.2), (85.5, 27.2), (88.4, 26.7)], "Pintados a carga de polvo"),
    Flujo("SE", [(91.8, 26.7), (92.7, 26.2), (93.2, 27.1)], "Carga -> ensamblaje"),
    Flujo("SE", [(92.7, 26.2), (93.2, 25.1)], "Carga -> ensamblaje"),
    Flujo("SE", [(95.2, 26.1), (96.0, 26.1), (97.5, 26.1), (98.0, 26.1), (99.5, 26.1), (100.0, 26.1),
                 (101.5, 26.1), (101.9, 27.5)], "Ensamblaje -> presurización -> hermeticidad -> etiquetado"),
    Flujo("SE", [(101.5, 26.1), (101.9, 25.0)], "A embalaje"),
    Flujo("SE", [(101.5, 26.1), (101.9, 29.3)], "Cilindros vendidos a palletizado"),
        # ---------------- carros de vuelta de la pintura tercerizada (U: entran por P8, salen por P9)
    Flujo("SE", [(128.0, 9.8), (119.7, 9.8), (92.0, 9.8), (89.0, 9.8)], "Carros pintados (P8)", "S3"),
    Flujo("SE", [(87.5, 7.8), (87.5, 7.3), (91.0, 7.3), (91.0, 5.7), (92.0, 5.7), (93.0, 5.7), (96.0, 5.7),
                 (97.6, 5.7)], "Carga de polvo -> armado -> presurización", "S3"),
    # ---------------- PT
    Flujo("PT", [(103.9, 27.55), (104.4, 27.9)], "Pallet a envolvedora"),
    Flujo("PT", [(103.9, 24.95), (104.4, 26.8)], "Pallet a envolvedora"),
    Flujo("PT", [(103.9, 29.35), (104.4, 29.0)], "Pallet de cilindros a envolvedora"),
    Flujo("PT", [(105.9, 27.9), (107.75, 27.9), (107.75, 26.0), (109.5, 26.0)], "Almacén de PT"),
    Flujo("PT", [(111.7, 28.5), (113.45, 28.5), (119.7, 28.5), (126.0, 28.5)], "Expedición M1"),
    Flujo("PT", [(111.7, 21.5), (113.45, 21.5), (119.7, 21.5), (126.0, 21.5)], "Expedición M2"),
    Flujo("PT", [(100.2, 5.7), (104.2, 5.7), (119.7, 5.4), (128.0, 5.4)], "Carros terminados (P9)", "S3"),
    Flujo("PT", [(116.0, 16.8), (116.0, 19.5), (119.7, 20.6)], "Tercerizados a expedición", "S4"),
    # ---------------- scrap
    Flujo("SCRAP", [(21.4, 13.95), (21.4, 13.0), (5.5, 13.0), (5.5, 13.9)], "Orillas de hoja"),
    Flujo("SCRAP", [(5.5, 16.2), (0.0, 16.2), (-7.0, 16.2)], "Scrap oeste (P2)"),
    Flujo("SCRAP", [(23.7, 30.2), (23.7, 30.7), (29.2, 30.7), (29.2, 31.4)], "Esqueleto de fleje"),
    Flujo("SCRAP", [(29.2, 35.7), (29.2, 36.0), (29.2, 41.0)], "Scrap norte (P2b)"),
]

# hilos de personal (DIR): desde el ingreso de vestuarios PP-1 a cada grupo de puestos
HILOS = [
    ("Línea de carros", [(51.4, 0.0), (51.4, 1.5), (4.0, 1.5)], [(33.0, 1.5, 33.0, 4.3), (28.0, 1.5, 28.0, 4.3),
      (24.8, 1.5, 24.8, 4.3), (20.9, 1.5, 20.9, 4.1), (16.7, 1.5, 16.7, 4.2), (13.0, 1.5, 13.0, 4.3),
      (9.2, 1.5, 9.2, 3.8)]),
    ("Corte y control de recepción", [(51.4, 0.0), (51.4, 1.5), (40.8, 1.5), (40.8, 23.0), (36.0, 23.0),
                                      (22.4, 23.0)],
     [(25.2, 23.0, 25.2, 22.0), (22.4, 23.0, 22.4, 18.0), (22.4, 18.0, 18.6, 18.0)]),
    ("Prensa y cuellos", [(40.8, 23.0), (40.8, 26.8), (36.0, 26.8), (17.8, 26.8)],
     [(22.2, 26.8, 22.2, 27.6), (25.0, 26.8, 25.0, 27.7), (27.0, 26.8, 27.0, 27.6), (17.8, 26.8, 17.8, 27.6)]),
    ("Celda 1 kg", [(51.4, 1.5), (40.8, 1.5), (40.8, 26.0)], [(40.8, 26.0, 41.8, 26.0), (40.8, 23.7, 41.8, 23.7),
      (40.8, 21.7, 41.8, 21.7)]),
    ("Celda 1 kg y 2,5-10 kg", [(51.4, 1.5), (53.4, 1.5), (53.4, 26.0)], [(53.4, 14.4, 52.5, 14.4),
      (53.4, 17.7, 52.4, 17.7), (53.4, 26.0, 54.6, 26.6), (53.4, 24.2, 54.8, 24.2), (53.4, 21.3, 54.4, 21.3),
      (53.4, 18.4, 54.6, 18.4), (53.4, 16.5, 54.6, 16.5), (53.4, 13.9, 54.4, 13.9)]),
    ("PH 2,5-10 kg", [(53.4, 1.5), (58.9, 1.5), (58.9, 11.4)], []),
    ("Celda 2,5-10 kg y pintura", [(53.4, 1.5), (66.4, 1.5), (66.4, 23.8)], [(66.4, 15.2, 65.3, 15.2),
      (66.4, 19.6, 65.6, 19.6), (66.4, 22.1, 65.6, 22.1), (66.4, 23.8, 68.4, 24.8)]),
    ("Cabina de pintura", [(66.4, 1.5), (74.6, 1.5), (74.6, 3.4)], []),
    ("Descarga de pintura y terminación", [(66.4, 1.5), (84.7, 1.5), (84.7, 21.4), (103.0, 21.4)],
     [(84.7, 21.4, 83.0, 24.4), (86.2, 21.4, 86.2, 22.2), (90.0, 21.4, 90.0, 22.2), (94.2, 21.4, 94.2, 24.6),
      (96.8, 21.4, 96.8, 25.6), (100.8, 21.4, 100.8, 25.7), (103.0, 21.4, 103.0, 24.2)]),
    ("Terminación de carros", [(84.7, 1.5), (99.0, 1.5)], [(88.0, 1.5, 88.0, 3.2), (94.5, 1.5, 94.5, 4.6),
      (98.9, 1.5, 98.9, 4.6)]),
    ("Calidad, mantenimiento y supervisión", [(51.4, 1.5), (45.0, 2.9)], [(45.0, 1.5, 58.5, 1.5),
      (58.5, 1.5, 58.5, 2.9), (63.9, 1.5, 63.9, 2.9)]),
    ("Almacén de PT y expedición", [(84.7, 1.5), (84.7, 21.4), (106.0, 21.4)], [(88.7, 21.4, 88.7, 20.6)]),
]

# ============================================================ LOCALES DE LOS ANEXOS
# bloque de servicios SV (x 38-66, y -13-0): pasillo E-O de 1,60 m; fila norte (contra la nave) vestuarios y
# sanitarios; fila sur (a la calle, con ventanas) hall, oficinas y comedor
LOCALES = [
    Sector("SV-VH", "Vestuario hombres (62 armarios)", R(38.2, -5.6, 44.2, -0.2), "SERV", "común"),
    Sector("SV-SH", "Sanitarios y duchas hombres", R(44.4, -5.6, 50.2, -0.2), "SERV", "común",
           "3 inodoros, 6 mingitorios, 6 lavabos, 4 duchas"),
    Sector("SV-PS", "Paso a planta", R(50.4, -5.6, 52.4, -0.2), "CIRC", "común"),
    Sector("SV-VM", "Vestuario y sanitarios mujeres (14 armarios)", R(52.6, -5.6, 57.8, -0.2), "SERV", "común",
           "2 inodoros, 2 lavabos, 2 duchas"),
    Sector("SV-AC", "Sanitario accesible", R(58.0, -2.8, 60.4, -0.2), "SERV", "común",
           "Círculo libre Ø 1,50 m, barras, inodoro con 0,80 m libre lateral (Ley 24.314, Dec. 914/97)"),
    Sector("SV-LA", "Lactario", R(58.0, -5.6, 60.4, -3.0), "SERV", "común", "Buena práctica (Ley 26.873)"),
    Sector("SV-PA", "Primeros auxilios", R(60.6, -5.6, 64.0, -0.2), "SERV", "común"),
    Sector("SV-LI", "Limpieza", R(64.2, -5.6, 65.8, -0.2), "SERV", "común"),
    Sector("SV-CO", "Pasillo", R(38.2, -7.4, 65.8, -5.8), "CIRC", "común"),
    Sector("SV-HA", "Hall, recepción y fichado", R(38.2, -12.8, 43.2, -7.6), "SERV", "común"),
    Sector("SV-OF", "Oficinas (6 puestos)", R(43.4, -12.8, 51.4, -7.6), "SERV", "común"),
    Sector("SV-JP", "Jefatura de planta", R(51.6, -12.8, 53.5, -7.6), "SERV", "común"),
    Sector("SV-RE", "Reuniones", R(53.7, -12.8, 55.6, -7.6), "SERV", "común"),
    Sector("SV-CM", "Comedor 30 plazas y office", R(55.8, -12.8, 65.8, -7.6), "SERV", "común"),
    # ala de recargas RC (x 70-98, y -17-0): recorrido en U, entra por el portón sur-este y sale por el este
    Sector("RC-NS", "Núcleo sanitario este", R(70.2, -5.8, 76.0, -0.2), "SERV", "común",
           "H: 2 inodoros, 2 mingitorios, 2 lavabos; M: 1 inodoro, 1 lavabo; accesible"),
    Sector("RC-MO", "Mostrador, recepción y clasificación", R(90.2, -16.8, 97.8, -11.6), "RC", "RC",
           "Clasificación en 4 colas: polvo, CO₂, agente limpio y líquidos"),
    Sector("RC-DE", "Desarme", R(83.2, -16.8, 90.0, -11.6), "RC", "RC"),
    Sector("RC-DC", "Descarga y ensayo de funcionamiento", R(76.2, -16.8, 83.0, -11.6), "RC", "RC",
           "Sala con extracción y recuperación de polvo"),
    Sector("RC-IR", "Inutilizados y residuos", R(70.2, -16.8, 76.0, -11.6), "RC", "RC", "", 8.0),
    Sector("RC-PH", "PH con jaula, lavado y secado", R(70.2, -11.4, 76.0, -6.0), "RC", "RC", "", 20.0),
    Sector("RC-PV", "Recinto de polvo (HR ≤ 70 %)", R(76.2, -11.4, 82.4, -6.0), "RC", "RC",
           "Carga ABC, BC y D; 8 renovaciones por hora; sin estufas", 33.5),
    Sector("RC-GA", "CO₂ y agente limpio", R(82.6, -11.4, 86.4, -6.0), "RC", "RC", "Trasvasador y balanza", 15.0),
    Sector("RC-LQ", "Líquidos", R(86.6, -11.4, 90.0, -6.0), "RC", "RC", "Agua, AFFF y clase K", 15.0),
    Sector("RC-EN", "Ensamblaje, presurización, peso y hermeticidad", R(90.2, -11.4, 97.8, -6.0), "RC", "RC",
           "Control de pérdidas por inmersión", 6.0),
    Sector("RC-FI", "Flota de intercambio", R(76.2, -5.8, 84.0, -0.2), "RC", "RC", "958 equipos de reemplazo"),
    Sector("RC-RP", "Retoque de pintura y etiquetado", R(84.2, -5.8, 91.0, -0.2), "RC", "RC", "", 15.0),
    Sector("RC-DP", "Despacho y equipos para entregar", R(91.2, -5.8, 97.8, -0.2), "RC", "RC", "", 34.0),
]

PUERTAS_ANEXOS = [
    # (cod, (x0, y0), (x1, y1), tipo, uso)
    ("SV-1", (39.2, -13.0), (41.2, -13.0), "peatonal", "Ingreso de personal y visitas"),
    ("SV-2", (65.8, -6.6), (66.0, -6.6), "peatonal", "Salida al pasaje este"),
    ("RC-1", (98.0, -16.0), (98.0, -12.0), "porton", "Recepción de equipos (utilitarios)"),
    ("RC-2", (98.0, -5.0), (98.0, -1.0), "porton", "Despacho de equipos recargados"),
    ("RC-3", (92.0, -17.0), (94.0, -17.0), "peatonal", "Mostrador (particulares)"),
    ("RC-4", (70.0, -9.4), (70.0, -8.2), "peatonal", "Personal de recargas desde el pasaje"),
]

# ============================================================ IMPLANTACIÓN
LM_Y = TERRENO[1]                  # línea municipal (calle al sur)
RETIRO_FRENTE = 10.0               # supuesto: retiro de frente parquizado (verificar con el PIVLA)

EXTERIOR = [
    # (cod, nombre, rect, tipo)
    ("PL-N", "Playa de descarga del semi bajo alero", R(10.0, 36.4, 29.4, 48.6), "playa"),
    ("VQ-O", "Volquete 6 m³ (scrap oeste)", R(-9.0, 13.2, -3.0, 19.2), "volquete"),
    ("VQ-N", "Volquete 6 m³ (scrap norte)", R(29.8, 37.4, 35.8, 43.4), "volquete"),
    ("JG-S", "Jaula de gases de soldadura (Ar/CO₂)", R(38.0, 36.6, 48.0, 41.6), "jaula"),
    ("ERM", "Regulación de gas de hornos", R(80.0, 36.4, 83.0, 38.4), "gas"),
    ("JG-N", "Jaula de N₂ y CO₂ (manifold)", R(104.0, 36.6, 112.0, 41.6), "jaula"),
    ("RI", "Reserva de agua contra incendio y bombas", R(118.0, 40.0, 130.0, 50.0), "incendio"),
    ("AMP", "Reserva de ampliación (ensanche de la nave hacia el norte)", R(36.0, 48.6, 116.0, 56.0), "reserva"),
    ("PTE", "Tratamiento de efluentes líquidos", R(63.0, -29.0, 75.0, -21.0), "efluentes"),
    ("EST", "Estacionamiento de personal (38 + 2 accesibles)", R(-10.0, -42.0, 56.0, -20.0), "estac"),
    ("EU", "Utilitarios de reparto y recargas (8)", R(100.0, -19.5, 126.0, -13.0), "estac"),
    ("GAR", "Garita y control de acceso", R(16.0, -55.0, 20.0, -51.0), "garita"),
    ("MT", "Celda de medición de media tensión", R(-24.0, -58.0, -18.0, -54.0), "elec"),
    ("ERP", "Estación reductora de gas", R(142.0, -58.0, 146.0, -55.0), "gas"),
]
# calles internas de camiones (ancho 7 m): anillo oeste - norte - este, entra por G1 y sale por G3
CALLES = [R(-20.0, -60.0, -13.0, 64.0), R(-20.0, 57.0, 140.0, 64.0), R(133.0, -60.0, 140.0, 64.0)]
PORTONES_TERRENO = [
    ("G1", -20.0, -13.0, "Camiones de MP, scrap y pintor"),
    ("G2", -6.0, 0.0, "Autos del personal"),
    ("G4", 21.0, 24.0, "Peatones"),
    ("G3", 133.0, 140.0, "Camiones de PT, carros, polvo, insumos y utilitarios"),
]

# ============================================================ EFLUENTES
# líquidos: cañería enterrada por gravedad hacia la planta de tratamiento PTE (al sur, junto a la colectora)
EFLUENTES = [
    Flujo("EFL-L", [(69.7, 19.0), (67.4, 19.0), (67.4, 0.0), (67.4, -21.0)], "Pretratamiento de pintura"),
    Flujo("EFL-L", [(51.7, 16.2), (50.5, 16.2), (50.5, 1.2), (67.4, 1.2)], "Agua de PH 1 kg"),
    Flujo("EFL-L", [(58.9, 12.0), (58.9, 9.0), (66.2, 9.0), (67.4, 9.0)], "Agua de PH 2,5-10 kg"),
    Flujo("EFL-L", [(73.0, -8.7), (68.6, -8.7), (68.6, -21.0)], "Lavado de recargas"),
    Flujo("EFL-L", [(69.0, -29.0), (69.0, -60.0)], "Vuelco a colectora (previa autorización)"),
]
# gaseosos: captación localizada y salida por techo (x, y, fuente)
# recargas: entra por RC-1, recorre la fila sur hacia el oeste, sube a PH y vuelve al este por la recarga
RC_FLUJO = [(104.0, -14.0), (98.0, -14.0), (94.0, -14.2), (86.6, -14.2), (79.6, -14.2), (74.2, -13.4),
            (73.1, -11.0), (73.1, -8.7), (79.3, -8.7), (84.5, -8.7), (88.3, -8.7), (94.0, -8.7), (94.0, -6.0),
            (88.0, -3.2), (93.0, -3.0), (98.0, -3.0), (104.0, -3.0)]

EMISIONES = [
    (21.0, 29.0, "Humos de soldadura de cuellos"), (20.9, 5.3, "Humos de soldadura de carros"),
    (16.7, 5.3, "Humos de soldadura de carros"), (51.7, 14.4, "Humos de soldadura 1 kg"),
    (55.2, 21.3, "Humos de soldadura 2,5-10 kg"), (55.2, 13.9, "Humos de soldadura 2,5-10 kg"),
    (63.0, 13.9, "Colector de la granalladora"), (69.7, 10.6, "Chimenea horno de secado"),
    (82.4, 10.6, "Chimenea horno de polimerizado"), (77.5, 3.8, "Ciclones de la cabina"),
    (87.0, 23.1, "Extracción sala de polvo 1-10 kg"), (88.0, 5.0, "Extracción sala de polvo carros"),
    (20.2, 22.0, "Humos de corte láser"), (80.4, -8.7, "Extracción recinto de polvo de recargas"),
]
