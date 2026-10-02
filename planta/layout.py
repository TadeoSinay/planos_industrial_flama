"""Modelo del layout de la planta industrial FLAMA S.A. al año 10 (2035): LAYOUT EN U.

Todas las medidas en METROS, origen en el eje A-1 de la nave (esquina SO, cara interior de columnas),
X hacia el este, Y hacia el norte. La calle (acceso) está al sur.

El modelo es la fuente única de los planos (DIR, flujo de operaciones, flujo de materiales, plano formal)
y de la memoria de cálculo.

Concepto (U)
------------
* Nave de 96 × 50 m: 12 módulos de 8 m, dos luces de 25 m con una fila de columnas en el eje B (y = 25).
* Pasillo central de personal (PC) a lo largo del eje B, pegado al bloque de servicios (fachada oeste):
  divide la nave en una banda norte y una banda sur y llega hasta el interior del lazo de pintura.
* Banda norte (de oeste a este): recepción y almacén de MP -> corte -> tres líneas paralelas que avanzan
  hacia el este: T (1 kg, láser de tubo), K (cúpulas, fondos y cuellos) y G (2,5-10 kg).
* Columna este: pintura en polvo con transportador aéreo en lazo: carga (NO) -> pretratamiento (N) ->
  secado y cabina (E) -> polimerizado y enfriamiento (S) -> descarga (O). El lazo baja y gira: la U.
* Banda sur (de este a oeste): carga de polvo y terminación -> almacén de PT y muelles (sur) -> línea de
  carros 25-100 kg en horquilla -> recargas (SO).
* El material da la vuelta a la nave y nunca cruza su propio flujo; el personal entra por el centro (PC) y
  sólo cruza un flujo en sendas peatonales señalizadas.
"""

from dataclasses import dataclass, field

# ---------------------------------------------------------------- nave
NAVE_L, NAVE_A = 96.0, 50.0           # largo (E-O) y ancho (N-S) entre ejes
MODULO = 8.0                          # separación de pórticos
ALTURA_LIBRE = 8.0                    # bajo cercha (m)
ALTURA_ALERO = 7.2
EJES_X = [i * MODULO for i in range(int(NAVE_L / MODULO) + 1)]   # 0 ... 96
EJES_Y = [0.0, 25.0, NAVE_A]          # fila central de columnas en el eje B
COL = 0.40                            # columna de alma llena 400 mm
MURO = 0.20                           # cerramiento (zócalo de bloque + chapa)

# terreno 170 × 125 m, calle al sur, en coordenadas de la nave
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
    Pasillo("PC", R(0.3, 25.3, 90.6, 29.5), "PP", 4.2,
            "Pasillo central de personal y evacuación: une los servicios con todos los puestos y el lazo de pintura"),
    Pasillo("AM", R(12.6, 29.7, 16.2, 49.7), "PM", 3.6,
            "Pasillo de autoelevador del sector MP: recepción, almacén y alimentación de máquinas"),
    Pasillo("PO-1", R(38.0, 29.7, 39.2, 45.4), "PO", 1.2,
            "Calle de operarios: línea G (2,5-10 kg), cúpulas y celda 1 kg"),
    Pasillo("PT-1", R(38.4, 18.8, 49.8, 22.4), "PM", 3.6, "Pasillo de autoelevador del almacén de PT (ingreso)"),
    Pasillo("PT-2", R(38.4, 13.8, 49.8, 17.4), "PM", 3.6, "Pasillo de autoelevador del almacén de PT (salida a muelles)"),
    Pasillo("AT", R(52.2, 13.6, 72.0, 16.2), "PM", 2.6,
            "Calle de abastecimiento de terminación: insumos (AL-2) y polvo (AL-PV) con transpaleta"),
]

# sendas peatonales señalizadas: únicos puntos donde un hilo de personal corta un flujo de materiales
SENDAS = []          # se completan al final del módulo (ver _sendas)

# ============================================================ SECTORES (nave)
SECTORES = [
    # ---- banda norte: recepción y almacén de MP (oeste)
    Sector("BR", "Bahía interior de descarga", R(0.3, 36.5, 10.6, 49.7), "MP", "común",
           "Chasis de 10 m entra por P1 y se descarga por los dos lados con autoelevador de 3,0 t"),
    Sector("SCR-O", "Scrap (orillas, esqueleto de fleje y recortes)", R(0.3, 29.7, 6.0, 35.6), "AUX", "común",
           "Contenedores basculantes de 1 m³; salen por P2 al volquete del patio oeste"),
    Sector("PÑ", "Pañol de insumos pesados", R(6.2, 29.7, 12.4, 36.3), "MP", "común",
           "Alambre MIG, granalla, asientos de válvula y cuplas, tapones, consumibles", 35.2),
    Sector("AL-1F", "Flejes", R(10.8, 38.8, 12.6, 48.8), "MP", "común",
           "Porta-flejes de 5 módulos × 3 niveles = 15 rollos + 6 en espera junto al desbobinador", 18.0),
    Sector("AL-1H", "Chapa en hojas", R(16.2, 29.7, 18.2, 38.6), "MP", "común",
           "Cantiléver de 3 módulos × 5 niveles = 15 paquetes ≤ 2 t; un formato por módulo, FIFO", 17.8),
    Sector("AL-1T", "Caño Ø76,2 × 6 m", R(16.2, 43.4, 18.2, 49.7), "MP", "S1",
           "Cantiléver de 3 niveles × 4 atados = 12 atados", 12.6),
    Sector("MQ-G", "Corte de cuerpos (guillotina)", R(18.2, 29.7, 27.8, 37.0), "PROD", "S2 / S3"),
    Sector("MQ-K", "Cúpulas, fondos y cuellos", R(18.2, 39.0, 33.0, 43.0), "PROD", "S1 / S2"),
    Sector("MQ-T", "Corte de caño 1 kg (láser de tubo)", R(18.2, 43.6, 30.6, 49.7), "PROD", "S1"),
    # ---- banda norte: líneas
    Sector("S1", "Celda 1 kg", R(30.8, 45.4, 72.0, 49.7), "PROD", "S1",
           "Numerado, encastre de fondo y cúpula, soldadura circ., PH, secado y transportador a pintura"),
    Sector("S2", "Línea 2,5-10 kg", R(27.8, 29.7, 72.0, 37.0), "PROD", "S2",
           "Cilindrado, soldadura long., encastre, bordoneado, soldadura circ., PH, secado, granallado, "
           "detección y corrección"),
    # ---- columna este: pintura
    Sector("S-P", "Pintura en polvo 1-10 kg (lazo)", R(72.2, 0.3, 95.7, 49.7), "PINT", "S1 / S2",
           "Transportador aéreo por empuje en lazo: carga, pretratamiento, secado, cabina, polimerizado, "
           "enfriamiento y descarga"),
    Sector("Q", "Laboratorio de calidad", R(78.4, 30.0, 84.8, 36.6), "CAL", "común",
           "Rotura, expansión, potencial extintor; control de polvo y de soldadura", 36.2),
    Sector("QR", "Cuarentena y lotes retenidos", R(85.0, 30.0, 89.8, 36.6), "CAL", "común",
           "Jaula con llave: lotes rechazados y muestras", 15.0),
    Sector("MT", "Mantenimiento y pañol de herramientas", R(78.4, 17.6, 84.8, 24.6), "AUX", "común",
           "Banco, torno chico y repuestos", 30.0),
    Sector("SUP", "Supervisión de planta y PCP", R(85.0, 21.2, 89.8, 24.6), "AUX", "común"),
    Sector("EPP", "EPP y botiquín", R(85.0, 17.6, 89.8, 21.0), "AUX", "común"),
    # ---- banda sur: terminación (este -> oeste)
    Sector("SP-1", "Sala de carga de polvo 1-10 kg", R(64.2, 16.4, 72.0, 24.6), "TERM", "S1 / S2",
           "Recinto cerrado HR ≤ 70 %, 8 renovaciones por hora, sin estufas (IRAM 3517-2)"),
    Sector("S-T", "Terminación 1-10 kg", R(52.2, 16.4, 64.0, 24.6), "TERM", "S1 / S2",
           "Ensamblaje, presurización con N₂, hermeticidad, etiquetado, embalaje y palletizado"),
    Sector("AL-PV", "Polvo químico en big bags", R(64.2, 0.3, 72.0, 13.4), "MP", "S1 / S2",
           "21 posiciones a 2 alturas, HR ≤ 70 %, entra por P4", 23.1),
    Sector("AL-2", "Insumos de terminación y embalaje", R(52.2, 0.3, 64.0, 13.4), "MP", "S1 / S2",
           "Rack de 4 niveles: válvulas, manómetros, mangueras, etiquetas, cajas, film y pallets; entra por P5",
           97.5),
    # ---- banda sur: PT y expedición
    Sector("AL-3", "Almacén de producto terminado", R(38.4, 12.4, 52.0, 24.6), "PT", "S1 / S2",
           "Rack de 3 frentes × 4 niveles = 100 posiciones (req. 88)"),
    Sector("EXP", "Expedición y muelles", R(44.6, 0.3, 52.0, 12.2), "PT", "común",
           "Consolidación de pedidos frente a M1-M2 (2 × 8 pallets)"),
    Sector("S4", "Tercerizados revendidos", R(38.4, 0.3, 44.4, 7.4), "PT", "S4",
           "CO₂, agua, AFFF, clase K y agente limpio con sello IRAM: recepción, control y stock"),
    Sector("BAT", "Carga de baterías de autoelevadores", R(39.6, 7.6, 44.4, 12.2), "AUX", "común",
           "Local ventilado con lavaojos; estacionamiento de autoelevadores y tractor"),
    # ---- banda sur: línea de carros (horquilla)
    Sector("S3", "Línea de carros 25-100 kg", R(18.4, 9.8, 38.2, 24.6), "PROD", "S3",
           "Horquilla: cilindrado, punteo, soldadura long. (norte, O->E); soldadura circ., inspección, "
           "PH 4,0 MPa y marcado (centro, E->O)"),
    Sector("AL-1C", "Casquetes de carros", R(36.4, 8.0, 38.2, 12.6), "MP", "S3",
           "Rack de 3 niveles × 4 pallets = 12 posiciones, junto a la soldadura circunferencial", 8.0),
    Sector("SP-2", "Sala de carga de polvo de carros", R(22.6, 0.3, 30.0, 9.6), "TERM", "S3",
           "Recinto HR ≤ 70 %: big bags propios y cabina de descarga de muestras (IRAM 3550)"),
    Sector("S-TC", "Terminación de carros", R(30.2, 0.3, 35.6, 9.6), "TERM", "S3",
           "Armado de ruedas y manguera, presurización y etiquetado"),
    Sector("PTC", "Carros terminados", R(35.8, 0.3, 38.2, 7.8), "PT", "S3", "0,5 m² por carro a piso", 12.0),
]

# ============================================================ EQUIPOS
# fuente: C = cotización recibida (referencias/INVESTIGACION PROVEEDORES), E = estimado de catálogo
E_ = Equipo
EQUIPOS = [
    # ---- MP y corte
    E_("M01", "Balanza de plataforma 3 t", Rw(8.6, 36.8, 1.5, 1.5), "BR", 0, 0.1, fuente="MP Manipulación"),
    E_("M02", "Mesa elevadora de tijera 3 t", Rw(18.5, 31.8, 1.5, 3.0), "MQ-G", 0, 2.2, fuente="MP Manipulación"),
    E_("M04", "Guillotina hidráulica 8 × 3200", Rw(21.6, 31.2, 2.3, 4.2), "MQ-G", 1, 15.0, fuente="C Cena E21",
       frente="O"),
    E_("M05", "Mesa de salida", Rw(24.2, 31.6, 1.6, 3.4), "MQ-G", 0, fuente="E"),
    E_("PU1", "Pulmón de cuerpos cortados", Rw(26.1, 31.0, 1.4, 4.4), "MQ-G", 0, fuente="E", tipo="kanban"),
    E_("M06", "Desbobinador y enderezador", Rw(18.4, 39.8, 2.6, 2.0), "MQ-K", 0, 3.0, fuente="C alimentador 900 mm"),
    E_("M07", "Alimentador servo", Rw(21.2, 40.2, 1.4, 1.2), "MQ-K", 0, 2.0, fuente="C alimentador 900 mm"),
    E_("M08", "Prensa de corte y embutido 300 t", Rw(22.8, 39.6, 3.0, 2.6), "MQ-K", 1, 30.0, aire=True,
       fuente="C PHM 300"),
    E_("M09", "Preparación de cuello", Rw(26.4, 41.6, 1.2, 1.0), "MQ-K", 0, 3.0, aire=True, fuente="E"),
    E_("M10", "Preparación de cuello", Rw(26.4, 39.6, 1.2, 1.0), "MQ-K", 1, 3.0, aire=True, fuente="E"),
    E_("M11", "Soldadura circ. de cuello", Rw(28.2, 41.5, 1.6, 1.2), "MQ-K", 0, 12.0, polvo=True, fuente="C FS-HFM1"),
    E_("M12", "Soldadura circ. de cuello", Rw(28.2, 39.5, 1.6, 1.2), "MQ-K", 1, 12.0, polvo=True, fuente="C FS-HFM1"),
    E_("SMK", "Supermercado de cúpulas y fondos", Rw(30.4, 39.4, 2.4, 3.4), "MQ-K", 0, fuente="E", tipo="kanban"),
    E_("M16", "Láser de tubo 6012", Rw(18.4, 44.0, 9.6, 2.0), "MQ-T", 0, 10.0, aire=True, polvo=True,
       fuente="C Leapion 6012"),
    E_("M15", "Láser de tubo 6012", Rw(18.4, 47.6, 9.6, 2.0), "MQ-T", 1, 10.0, aire=True, polvo=True,
       fuente="C Leapion 6012"),
    E_("M17", "Pulmón de cuerpos 1 kg", Rw(29.2, 44.2, 1.2, 5.2), "MQ-T", 0, fuente="E", tipo="kanban"),
    # ---- S2 línea 2,5-10 kg (oeste -> este, eje y = 32,9)
    E_("B01", "Numerado de cuerpo", Rw(28.4, 32.6, 1.2, 0.8), "S2", 1, 0.5, fuente="E"),
    E_("B02", "Cilindradora", Rw(30.4, 32.5, 1.7, 0.9), "S2", 1, 1.1, fuente="C Bästlein"),
    E_("B03", "Soldadura longitudinal", Rw(33.0, 32.1, 2.2, 1.6), "S2", 1, 12.0, polvo=True,
       fuente="C Mitusa GS2ft Ergo"),
    E_("B05", "Encastre de fondo y cúpula", Rw(36.2, 32.4, 1.2, 1.0), "S2", 1, 1.0, aire=True, fuente="E"),
    E_("B04", "Bordoneadora", Rw(40.0, 32.5, 1.2, 0.9), "S2", 1, 1.5, fuente="C SWM-400"),
    E_("B06", "Soldadura circ. cúpula y fondo", Rw(42.0, 32.0, 2.4, 1.8), "S2", 1, 15.0, polvo=True,
       fuente="C SCWelding PRO WP150"),
    E_("B07", "Prueba hidráulica automática", Rw(45.2, 31.6, 3.2, 2.6), "S2", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A"),
    E_("B14", "Secadora de cilindros", Rw(49.4, 31.8, 4.0, 2.2), "S2", 0, 6.0, gas=True, fuente="E"),
    E_("B08", "Granalladora de túnel", Rw(54.4, 31.4, 4.5, 2.2), "S2", 1, 15.0, polvo=True, fuente="C Airblast G-100"),
    E_("B13", "Colector de polvo", Rw(55.6, 34.2, 1.8, 1.4), "S2", 0, 5.5, polvo=True, fuente="E"),
    E_("B09", "Detección de defectos", Rw(59.8, 32.0, 2.2, 1.2), "S2", 1, 0.5, fuente="E"),
    E_("B10", "Corrección de defectos", Rw(62.8, 31.8, 2.2, 1.5), "S2", 1, 10.0, polvo=True, fuente="E"),
    E_("B11", "Pulmón a pintura", Rw(66.0, 32.4, 3.6, 1.0), "S2", 0, fuente="E", tipo="pulmon"),
    # ---- S1 celda 1 kg (oeste -> este, eje y = 47,0)
    E_("A03", "Numerado de cuerpo", Rw(31.2, 46.6, 1.2, 0.8), "S1", 1, 0.5, fuente="E"),
    E_("A04", "Encastre de fondo", Rw(33.2, 46.6, 1.2, 1.0), "S1", 1, 1.0, aire=True, fuente="E"),
    E_("A05", "Encastre de cúpula", Rw(35.2, 46.6, 1.2, 1.0), "S1", 1, 1.0, aire=True, fuente="E"),
    E_("A06", "Soldadura circ. cúpula y fondo", Rw(39.6, 46.2, 2.4, 1.8), "S1", 1, 15.0, polvo=True,
       fuente="C Getweld"),
    E_("A07", "Prueba hidráulica automática", Rw(43.0, 45.8, 3.2, 2.6), "S1", 1, 4.0, agua=True,
       fuente="C Firesafer FS-JD12A"),
    E_("A11", "Secadora de cilindros", Rw(47.2, 45.9, 4.0, 2.2), "S1", 0, 6.0, gas=True, fuente="E"),
    E_("CT1", "Transportador de rodillos a pintura", Rw(51.8, 46.6, 13.6, 0.8), "S1", 0, 0.5, fuente="E",
       tipo="mesa_rodillos"),
    E_("A08", "Pulmón a pintura", Rw(66.0, 46.5, 3.6, 1.0), "S1", 0, fuente="E", tipo="pulmon"),
    # ---- pintura: lazo del transportador aéreo (eje: y 38,9 / x 92,0 / y 3,4 / x 75,1)
    E_("P01", "Tren de carga", Rw(72.6, 35.6, 5.0, 6.6), "S-P", 2, fuente="C Electricolor"),
    E_("P02", "Túnel de pretratamiento (3 etapas)", Rw(79.4, 37.8, 8.4, 2.2), "S-P", 0, 11.0, agua=True,
       polvo=True, fuente="E SP Ingeniería / Electricolor"),
    E_("P03", "Horno de secado 6 × 2,44 m", Rw(90.78, 27.0, 2.44, 6.0), "S-P", 0, 3.0, gas=True,
       fuente="C Electricolor", frente="O"),
    E_("P04", "Cabina de pintura y reciprocador", Rw(91.0, 15.0, 2.0, 3.2), "S-P", 1, 5.0, aire=True, polvo=True,
       fuente="C Electricolor EC40-200D", frente="O"),
    E_("P05", "Ciclones de recuperación", Rw(93.4, 14.6, 1.8, 4.0), "S-P", 0, 11.0, polvo=True,
       fuente="C Electricolor", frente="O"),
    E_("P06", "Horno de polimerizado 6 × 2,44 m", Rw(84.2, 2.18, 6.0, 2.44), "S-P", 0, 3.0, gas=True,
       fuente="C Electricolor", frente="N"),
    E_("P07", "Enfriamiento", Rw(76.6, 2.18, 7.0, 2.44), "S-P", 0, fuente="E", frente="N"),
    E_("P08", "Tren de descarga", Rw(72.6, 16.0, 5.0, 6.6), "S-P", 1, fuente="C Electricolor", frente="N"),
    E_("P09", "Retoque y control de espesor", Rw(78.6, 12.6, 2.4, 1.6), "S-P", 0, fuente="E"),
    # ---- terminación 1-10 kg (este -> oeste, eje y = 19,0)
    E_("T01", "Carga de polvo 1-10 kg", Rw(66.2, 18.0, 3.4, 2.0), "SP-1", 1, 3.0, aire=True, polvo=True,
       fuente="C Yukon M-000121 + estación de big bag", frente="N"),
    E_("T15", "Deshumidificador y extracción", Rw(69.4, 22.8, 2.4, 1.2), "SP-1", 0, 6.0, fuente="E", frente="N"),
    E_("T03", "Ensamblaje de válvula", Rw(61.8, 18.4, 1.6, 1.2), "S-T", 1, 0.5, aire=True, fuente="E", frente="N"),
    E_("T04", "Ensamblaje de válvula", Rw(59.8, 18.4, 1.6, 1.2), "S-T", 1, 0.5, aire=True, fuente="E", frente="N"),
    E_("T05", "Presurización con N₂", Rw(57.8, 18.5, 1.5, 1.0), "S-T", 1, 0.5, n2=True, fuente="C Yukon M-000150",
       frente="N"),
    E_("T06", "Hermeticidad", Rw(55.9, 18.5, 1.5, 1.0), "S-T", 0, 0.5, fuente="E", frente="N"),
    E_("T07", "Etiquetadora semiautomática", Rw(54.0, 18.6, 1.5, 0.8), "S-T", 1, 0.5, fuente="C SISA", frente="N"),
    E_("T08", "Embalaje y palletizado", Rw(52.3, 18.2, 1.5, 1.6), "S-T", 1, fuente="E", frente="N"),
    E_("T09", "Embalaje y palletizado", Rw(52.3, 20.6, 1.5, 1.6), "S-T", 1, fuente="E", frente="N"),
    E_("T10", "Palletizado de cilindros vendidos", Rw(52.3, 16.5, 1.5, 1.4), "S-T", 0, fuente="E", frente="N"),
    E_("T11", "Envolvedora de pallets", Rw(50.0, 17.6, 1.5, 3.0), "AL-3", 0, 1.5, fuente="C EDOS PS5"),
    E_("RK1", "Rack de PT, frente norte (4 × 2 × 4)", Rw(39.0, 22.6, 10.6, 1.1), "AL-3", 0, fuente="E", forma="rack"),
    E_("RK2", "Rack de PT, frente central (4 × 2 × 4)", Rw(39.0, 17.6, 10.6, 1.1), "AL-3", 0, fuente="E",
       forma="rack"),
    E_("RK3", "Rack de PT, frente sur (2 × 2 × 4)", Rw(39.0, 12.6, 5.4, 1.1), "AL-3", 0, fuente="E", forma="rack"),
    E_("RKI", "Rack de insumos de terminación", Rw(52.6, 9.2, 10.8, 1.1), "AL-2", 0, fuente="E", forma="rack"),
    E_("RKV", "Rack de big bags de polvo", Rw(64.6, 9.2, 7.0, 1.1), "AL-PV", 0, fuente="E", forma="rack"),
    # ---- S3 línea de carros (horquilla: norte O->E, centro E->O)
    E_("C01", "Cilindradora de 4 rodillos", Rw(23.0, 20.0, 4.5, 1.4), "S3", 1, 5.5, fuente="C Getweld"),
    E_("C02", "Punteo, refuerzo y estructura", Rw(28.4, 19.8, 2.5, 1.5), "S3", 1, 10.0, polvo=True, fuente="E"),
    E_("C03", "Punteo, refuerzo y estructura", Rw(31.4, 19.8, 2.5, 1.5), "S3", 1, 10.0, polvo=True, fuente="E"),
    E_("C04", "Soldadura longitudinal de carros", Rw(34.6, 19.6, 3.0, 2.0), "S3", 1, 18.0, polvo=True,
       fuente="C Getweld ZF-1000"),
    E_("C05", "Soldadura circ. de fondo y cúpula", Rw(33.8, 12.8, 3.0, 1.8), "S3", 1, 18.0, polvo=True,
       fuente="E", frente="N"),
    E_("C06", "Inspección de costuras", Rw(30.4, 13.1, 2.2, 1.2), "S3", 1, 0.5, fuente="E", frente="N"),
    E_("C07", "PH 4,0 MPa con jaula", Rw(25.6, 12.4, 3.6, 2.6), "S3", 1, 2.0, agua=True,
       fuente="C Yukon M-000200 + jaula", frente="N"),
    E_("C08", "Marcado del recipiente", Rw(23.0, 13.2, 1.5, 1.0), "S3", 0, 0.5, fuente="E", frente="N"),
    E_("C12", "Carros a pintura tercerizada", Rw(18.6, 10.2, 3.6, 6.0), "S3", 0, fuente="E", forma="rack",
       tipo="carros"),
    E_("C09", "Probetas de soldadura", Rw(29.0, 10.2, 2.4, 1.2), "S3", 0, 2.0, fuente="E", frente="N"),
    E_("C10", "Pluma giratoria 1 t", Rw(33.3, 18.1, 0.6, 0.6), "S3", 0, 1.5, fuente="E", forma="circ"),
    E_("C11", "Pluma giratoria 1 t", Rw(28.0, 16.6, 0.6, 0.6), "S3", 0, 1.5, fuente="E", forma="circ"),
    # ---- terminación de carros (vuelven pintados por P8; salen por P9)
    E_("T02", "Carga de polvo de carros", Rw(26.6, 4.2, 2.8, 2.6), "SP-2", 1, 2.0, aire=True, polvo=True,
       fuente="E", frente="N"),
    E_("Q01", "Cabina de descarga de muestras", Rw(22.8, 6.0, 2.8, 3.4), "SP-2", 0, 3.0, polvo=True, fuente="E",
       frente="E"),
    E_("T12", "Armado de carros", Rw(30.4, 4.4, 2.4, 2.0), "S-TC", 1, 0.5, aire=True, fuente="E", frente="N"),
    E_("T13", "Presurización y etiquetado de carros", Rw(33.0, 4.4, 2.4, 2.0), "S-TC", 1, 0.5, n2=True,
       fuente="E", frente="N"),
    E_("T14", "Estructuras y ruedas de carros", Rw(30.4, 7.6, 5.0, 1.0), "S-TC", 0, fuente="E", forma="rack"),
]

# ============================================================ PUERTAS Y PORTONES
PUERTAS = [
    Puerta("P1", "O", 41.4, 46.4, 5.0, "porton", "MP: chasis de 10 m a la bahía interior"),
    Puerta("P1b", "N", 12.9, 16.1, 4.0, "porton", "MP: autoelevador desde la playa del semi"),
    Puerta("P2", "O", 30.6, 33.6, 4.0, "porton", "Scrap a volquete"),
    Puerta("RC-1", "O", 1.0, 5.0, 4.0, "porton", "Recargas: recepción de equipos"),
    Puerta("RC-2", "O", 7.0, 10.6, 4.0, "porton", "Recargas: despacho de equipos recargados"),
    Puerta("P6", "S", 19.0, 22.0, 4.0, "porton", "Carros a pintura tercerizada"),
    Puerta("P8", "S", 24.4, 27.6, 4.0, "porton", "Carros pintados, polvo de carros, estructuras y ruedas"),
    Puerta("P9", "S", 35.9, 38.1, 3.0, "porton", "Carros terminados (camión a nivel)"),
    Puerta("M3", "S", 39.4, 42.4, 3.2, "muelle", "Recepción de tercerizados y casquetes"),
    Puerta("M1", "S", 45.0, 48.0, 3.2, "muelle", "Expedición PT (rampa niveladora)"),
    Puerta("M2", "S", 48.6, 51.6, 3.2, "muelle", "Expedición PT (rampa niveladora)"),
    Puerta("P5", "S", 56.0, 60.0, 4.0, "porton", "Insumos de terminación y embalaje"),
    Puerta("P4", "S", 66.0, 70.0, 4.0, "porton", "Polvo químico (big bags)"),
    Puerta("P3", "E", 41.0, 44.0, 3.0, "porton", "Químicos de pretratamiento"),
    Puerta("P3b", "E", 9.6, 12.6, 3.0, "porton", "Pintura en polvo"),
    # salidas de emergencia (1,10 m, barral antipánico, abren hacia afuera)
    Puerta("SE-1", "N", 30.0, 31.1, 2.1, "emergencia"),
    Puerta("SE-2", "N", 52.0, 53.1, 2.1, "emergencia"),
    Puerta("SE-3", "N", 70.0, 71.1, 2.1, "emergencia"),
    Puerta("SE-4", "N", 88.0, 89.1, 2.1, "emergencia"),
    Puerta("SE-5", "E", 22.0, 23.1, 2.1, "emergencia"),
    Puerta("SE-6", "S", 92.4, 93.5, 2.1, "emergencia"),
    Puerta("SE-7", "S", 62.0, 63.1, 2.1, "emergencia"),
    Puerta("SE-8", "S", 31.0, 32.1, 2.1, "emergencia"),
    Puerta("SE-9", "O", 36.8, 37.9, 2.1, "emergencia"),
    Puerta("SE-10", "S", 13.0, 14.1, 2.1, "emergencia"),
    Puerta("PP-1", "O", 26.0, 28.4, 2.1, "peatonal", "Ingreso de personal desde vestuarios"),
]

# ============================================================ ANEXOS
ANEXOS = [
    Sector("SV", "Bloque de servicios al personal y oficinas", R(-18.0, 11.0, 0.0, 30.0), "SERV", "común"),
    Sector("RC", "Recargas (ala SO de la nave)", R(0.3, 0.3, 18.2, 24.6), "RC", "RC",
           "Dentro de la nave, con tabiques y portones propios"),
    Sector("ST", "Sala técnica: transformador, TGBT y compresores", R(36.0, 50.2, 48.0, 56.0), "AUX", "común"),
    Sector("QP", "Químicos y pintura en polvo", R(96.2, 36.0, 102.0, 46.0), "MP", "S1 / S2",
           "Cobertizo con batea ≥ 110 % del mayor envase; pintura en polvo < 30 °C"),
]

# ============================================================ FLUJOS (m)
TL = []
TL_CARGADO = []
TL_RETORNO = []
LAZO = [(75.1, 38.9), (92.0, 38.9), (92.0, 3.4), (75.1, 3.4), (75.1, 16.0)]   # SE cargado del lazo de pintura

FLUJOS = [
    # ---------------- MP
    Flujo("MP", [(-6.0, 43.9), (0.0, 43.9), (5.0, 43.9), (5.0, 37.6), (11.6, 37.6), (14.4, 37.6), (14.4, 34.2),
                 (16.2, 34.2)], "Chapa en hojas (chasis en bahía interior)"),
    Flujo("MP", [(18.2, 33.3), (18.5, 33.3)], "Paquete a la mesa elevadora"),
    Flujo("MP", [(20.0, 33.3), (21.6, 33.3)], "Hoja a la guillotina"),
    Flujo("MP", [(15.2, 56.0), (15.2, 50.0), (15.2, 46.0), (16.2, 46.0)], "Caño en atados (semi en playa norte)"),
    Flujo("MP", [(18.2, 46.0), (18.4, 46.0)], "Atado al cargador del láser"),
    Flujo("MP", [(13.4, 56.0), (13.4, 50.0), (13.4, 41.6), (12.6, 41.6)], "Flejes (semi en playa norte)"),
    Flujo("MP", [(12.6, 39.4), (13.4, 39.4), (13.4, 40.8), (18.4, 40.8)], "Rollo al desbobinador"),
    Flujo("MP", [(-6.0, 42.0), (0.0, 42.0), (3.5, 42.0), (3.5, 36.8), (7.0, 36.8), (7.0, 36.3)], "Insumos al pañol"),
    Flujo("MP", [(39.8, -6.0), (39.8, 0.0), (39.8, 7.6), (39.2, 7.6), (37.3, 7.6), (37.3, 8.0)], "Casquetes (M3)"),
    Flujo("MP", [(36.4, 12.0), (35.6, 12.0), (35.6, 12.8)], "Casquete a la soldadura circ."),
    Flujo("MP", [(68.0, -6.0), (68.0, 0.0), (68.0, 9.2)], "Polvo químico (big bags, P4)"),
    Flujo("MP", [(68.0, 10.3), (68.0, 18.0)], "Big bag a la carga de polvo"),
    Flujo("MP", [(58.0, -6.0), (58.0, 0.0), (58.0, 9.2)], "Válvulas, manómetros, etiquetas, cajas (P5)"),
    Flujo("MP", [(60.6, 10.3), (60.6, 18.4)], "Insumos a ensamblaje y embalaje"),
    Flujo("MP", [(104.0, 42.5), (102.0, 42.5)], "Químicos y pintura (QP)"),
    Flujo("MP", [(96.2, 42.5), (90.0, 42.5), (83.6, 42.5), (83.6, 40.0)], "Desengrasante y fosfatizante al túnel"),
    Flujo("MP", [(102.0, 11.1), (96.0, 11.1), (94.3, 11.1), (94.3, 14.6)], "Pintura en polvo a la cabina (P3b)"),
    Flujo("MP", [(26.0, -6.0), (26.0, 0.0), (26.0, 5.5), (26.6, 5.5)], "Carros pintados y polvo de carros (P8)",
          "S3"),
    Flujo("MP", [(40.9, -6.0), (40.9, 0.0), (40.9, 4.0)], "Tercerizados revendidos (M3)", "S4"),
    # ---------------- SE: corte
    Flujo("SE", [(23.9, 33.3), (24.2, 33.3)], "Cuerpo cortado"),
    Flujo("SE", [(25.8, 33.3), (26.1, 33.3)], "Cuerpos al pulmón"),
    Flujo("SE", [(26.8, 31.0), (26.8, 29.5), (26.8, 25.3), (26.8, 21.4)], "Cuerpos de carros a la cilindradora",
          "S3"),
    Flujo("SE", [(21.0, 40.8), (21.2, 40.8)], "Fleje enderezado"),
    Flujo("SE", [(22.6, 40.8), (22.8, 40.8)], "Fleje al troquel"),
    Flujo("SE", [(25.8, 40.8), (26.0, 40.8), (26.0, 42.1), (26.4, 42.1)], "Cúpulas al cuello"),
    Flujo("SE", [(26.0, 40.8), (26.0, 40.1), (26.4, 40.1)], "Cúpulas al cuello"),
    Flujo("SE", [(27.6, 42.1), (28.2, 42.1)], "Cuello preparado"),
    Flujo("SE", [(27.6, 40.1), (28.2, 40.1)], "Cuello preparado"),
    Flujo("SE", [(29.8, 42.1), (30.4, 42.1)], "Cúpulas 1 kg al supermercado"),
    Flujo("SE", [(29.8, 40.1), (30.4, 40.1)], "Cúpulas 2,5-10 kg al supermercado"),
    Flujo("SE", [(25.0, 39.6), (25.0, 39.2), (31.6, 39.2), (31.6, 39.4)], "Fondos al supermercado"),
    Flujo("SE", [(28.0, 45.0), (29.2, 45.0)], "Cuerpos 1 kg"),
    Flujo("SE", [(28.0, 48.6), (29.2, 48.6)], "Cuerpos 1 kg"),
    # ---------------- SE: cúpulas y fondos a las líneas
    Flujo("SE", [(31.8, 42.8), (31.8, 44.4), (33.8, 44.4), (33.8, 46.6)], "Fondos 1 kg", "S1"),
    Flujo("SE", [(32.4, 42.8), (32.4, 43.8), (35.8, 43.8), (35.8, 46.6)], "Cúpulas 1 kg", "S1"),
    Flujo("SE", [(32.8, 40.6), (36.8, 40.6), (36.8, 33.4)], "Cúpulas y fondos 2,5-10 kg", "S2"),
    # ---------------- SE: líneas
    Flujo("SE", [(26.8, 33.3), (27.5, 33.3), (28.4, 32.9), (29.6, 32.9), (30.4, 32.9), (32.1, 32.9), (33.0, 32.9),
                 (35.2, 32.9), (36.2, 32.9), (37.4, 32.9), (40.0, 32.9), (41.2, 32.9), (42.0, 32.9), (44.4, 32.9),
                 (45.2, 32.9), (48.4, 32.9), (49.4, 32.9), (53.4, 32.9), (54.4, 32.9), (58.9, 32.9), (59.8, 32.9),
                 (62.0, 32.9), (62.8, 32.9), (65.0, 32.9), (66.0, 32.9), (69.6, 32.9), (73.6, 32.9), (73.6, 35.6)],
          "Línea 2,5-10 kg -> granallado -> pintura", "S2"),
    Flujo("SE", [(63.9, 33.3), (63.9, 36.2), (46.8, 36.2), (46.8, 34.2)], "Reproceso: corrección -> nueva PH",
          "S2"),
    Flujo("SE", [(30.4, 47.0), (31.2, 47.0), (32.4, 47.0), (33.2, 47.0), (34.4, 47.0), (35.2, 47.0), (36.4, 47.0),
                 (39.6, 47.0), (42.0, 47.0), (43.0, 47.0), (46.2, 47.0), (47.2, 47.0), (51.2, 47.0), (51.8, 47.0),
                 (65.4, 47.0), (66.0, 47.0), (69.6, 47.0), (74.0, 47.0), (74.0, 42.2)],
          "Celda 1 kg -> pintura (sin granallado)", "S1"),
    # ---------------- SE: pintura (lazo) y terminación
    Flujo("SE", LAZO, "Lazo de pintura: pretratamiento, secado, cabina, polimerizado, enfriamiento"),
    Flujo("RET", [(75.1, 22.6), (75.1, 35.6)], "Retorno de ganchos vacíos (aéreo, +4,0 m)"),
    Flujo("SE", [(72.6, 19.3), (69.6, 19.3)], "Pintados a carga de polvo"),
    Flujo("SE", [(66.2, 19.0), (64.0, 19.0), (63.4, 19.0), (61.8, 19.0), (61.4, 19.0), (59.8, 19.0), (59.3, 19.0),
                 (57.8, 19.0), (57.4, 19.0), (55.9, 19.0), (55.5, 19.0), (54.0, 19.0), (53.8, 19.0)],
          "Ensamblaje -> presurización -> hermeticidad -> etiquetado -> embalaje"),
    # ---------------- SE: línea de carros
    Flujo("SE", [(27.5, 20.7), (28.4, 20.7), (30.9, 20.7), (31.4, 20.7), (33.9, 20.7), (34.6, 20.7), (37.6, 20.7),
                 (37.9, 20.7), (37.9, 13.7), (36.8, 13.7), (33.8, 13.7), (32.6, 13.7), (30.4, 13.7), (29.2, 13.7),
                 (25.6, 13.7), (24.5, 13.7), (23.0, 13.7), (22.2, 13.7)],
          "Línea de carros: cilindrado, punteo, soldaduras, inspección, PH y marcado", "S3"),
    Flujo("SE", [(20.4, 10.2), (20.4, 0.0), (20.4, -6.0)], "Carros a pintura tercerizada (P6)", "S3"),
    Flujo("SE", [(29.4, 5.5), (30.4, 5.4), (32.8, 5.4), (33.0, 5.4), (35.4, 5.4)],
          "Carga de polvo -> armado -> presurización", "S3"),
    # ---------------- PT
    Flujo("PT", [(52.3, 19.0), (51.5, 19.0)], "Pallet a envolvedora"),
    Flujo("PT", [(52.3, 21.4), (51.5, 20.0)], "Pallet a envolvedora"),
    Flujo("PT", [(50.0, 20.6), (44.0, 20.6), (44.0, 22.6)], "Almacén de PT"),
    Flujo("PT", [(44.0, 18.8), (44.0, 18.7)], "Almacén de PT"),
    Flujo("PT", [(46.5, 17.6), (46.5, 12.2), (46.5, 0.0), (46.5, -6.0)], "Expedición M1"),
    Flujo("PT", [(48.5, 17.6), (48.5, 12.2), (50.1, 10.0), (50.1, 0.0), (50.1, -6.0)], "Expedición M2"),
    Flujo("PT", [(35.4, 5.0), (37.0, 5.0), (37.0, 0.0), (37.0, -6.0)], "Carros terminados (P9)", "S3"),
    Flujo("PT", [(42.6, 4.0), (44.4, 4.0), (45.4, 4.0)], "Tercerizados a expedición", "S4"),
    # ---------------- scrap
    Flujo("SCRAP", [(2.0, 32.1), (0.0, 32.1), (-5.0, 32.1)], "Scrap (P2)"),
]

# hilos de personal (DIR): (nombre, recorrido principal, ramales (x0, y0, x1, y1))
Y_PC = 27.4


def _op(cod):
    """Punto de trabajo del primer operario de un equipo (al frente, 0,42 m)."""
    e = next(e for e in EQUIPOS if e.cod == cod)
    from .simbolos import frente_de
    r, f = e.rect, frente_de(e)
    return {"S": (r.c[0], r.y0 - 0.42), "N": (r.c[0], r.y1 + 0.42), "O": (r.x0 - 0.42, r.c[1]),
            "E": (r.x1 + 0.42, r.c[1])}[f]


def _ramal(x_pc, cod, y_pc=Y_PC):
    x, y = _op(cod)
    return (x_pc, y_pc, x, y) if abs(x_pc - x) < 1e-6 else None


HILOS = []


def _hilos():
    H = []
    pc = lambda x: (x, Y_PC)
    # corte, MP, pañol y scrap
    H.append(("Corte, MP y pañol", [(0.0, Y_PC), pc(20.6), (20.6, 32.4)],
              [(9.0, Y_PC, 9.0, 29.7), (3.0, Y_PC, 3.0, 29.7), (14.4, Y_PC, 14.4, 29.7)]))
    # línea G (2,5-10 kg), granallado y corrección: ramales al frente sur de cada equipo
    br = []
    for c in ("B01", "B02", "B03", "B05", "B04", "B06", "B07", "B08", "B09", "B10"):
        x, y = _op(c)
        br.append((x, Y_PC, x, y))
    H.append(("Línea 2,5-10 kg", [pc(20.6), pc(66.0)], br))
    # cúpulas (K) y celda 1 kg (T): calle PO-1
    br = [(38.6, 38.8, 23.6, 38.8)]
    for c in ("M08", "M10", "M12"):
        x, y = _op(c)
        br.append((x, 38.8, x, y))
    br.append((38.6, 43.2, 23.6, 43.2))
    br.append((23.6, 43.2, 23.6, _op("M16")[1]))
    br.append((28.5, 43.2, 28.5, 47.2))
    br.append((28.5, 47.2, 23.6, 47.2))
    br.append((38.6, 45.2, 31.8, 45.2))
    for c in ("A03", "A04", "A05"):
        x, y = _op(c)
        br.append((x, 45.2, x, y))
    br.append((38.6, 45.2, 44.6, 45.2))
    for c in ("A06", "A07"):
        x, y = _op(c)
        br.append((x, 45.2, x, y))
    H.append(("Cúpulas, láseres y celda 1 kg", [pc(38.6), (38.6, 45.2)], br))
    # pintura: carga, descarga, cabina, laboratorio y mantenimiento
    br = [(74.3, Y_PC, 74.3, _op("P01")[1]), (74.0, Y_PC, 74.0, _op("P08")[1]),
          (89.6, Y_PC, 89.6, _op("P04")[1]), (89.6, _op("P04")[1], _op("P04")[0], _op("P04")[1]),
          (81.6, Y_PC, 81.6, 30.0), (87.4, Y_PC, 87.4, 30.0), (81.6, Y_PC, 81.6, 24.6), (87.4, Y_PC, 87.4, 24.6)]
    H.append(("Pintura, calidad y mantenimiento", [pc(66.0), pc(89.6)], br))
    # terminación 1-10 kg y PT: ramales al frente norte
    br = []
    for c in ("T01", "T03", "T04", "T05", "T07", "T08"):
        x, y = _op(c)
        br.append((x, Y_PC, x, y))
    br.append((51.0, Y_PC, 51.0, 22.4))
    H.append(("Terminación y expedición", [pc(48.0), pc(70.0)], br))
    # línea de carros (horquilla): entra por el oeste a la calle interior
    br = []
    for c in ("C01", "C02", "C03", "C04"):
        x, y = _op(c)
        br.append((x, 17.8, x, y))
    for c in ("C05", "C06", "C07"):
        x, y = _op(c)
        br.append((x, 17.8, x, y))
    br.append((31.6, 17.8, 31.6, _op("T12")[1]))
    br.append((31.6, _op("T12")[1], 27.9, _op("T02")[1]))
    br.append((31.6, _op("T12")[1], _op("T13")[0], _op("T13")[1]))
    H.append(("Línea de carros", [pc(20.6), (20.6, 17.8), (36.2, 17.8)], br))
    # recargas
    H.append(("Recargas", [pc(9.0), (9.0, 24.6), (9.0, 19.4)], [(9.0, 19.4, 3.0, 19.4), (9.0, 19.4, 15.0, 19.4)]))
    return H


# ============================================================ LOCALES
# servicios SV (x -18..0, y 11..30): pasillo N-S contra la nave (PP-1); vestuarios al norte, oficinas al sur
LOCALES = [
    Sector("SV-VH", "Vestuario hombres (62 armarios)", R(-17.8, 24.4, -10.4, 29.8), "SERV", "común"),
    Sector("SV-SH", "Sanitarios y duchas hombres", R(-10.2, 24.4, -5.4, 29.8), "SERV", "común",
           "3 inodoros, 6 mingitorios, 6 lavabos, 4 duchas"),
    Sector("SV-LI", "Limpieza", R(-5.2, 26.8, -2.2, 29.8), "SERV", "común"),
    Sector("SV-PS", "Paso a planta", R(-5.2, 24.4, -2.2, 26.6), "CIRC", "común"),
    Sector("SV-VM", "Vestuario y sanitarios mujeres (14 armarios)", R(-17.8, 18.8, -10.4, 24.2), "SERV", "común",
           "2 inodoros, 2 lavabos, 2 duchas"),
    Sector("SV-AC", "Sanitario accesible", R(-10.2, 21.6, -7.8, 24.2), "SERV", "común",
           "Círculo libre Ø 1,50 m, barras, inodoro con 0,80 m libre lateral (Ley 24.314, Dec. 914/97)"),
    Sector("SV-LA", "Lactario", R(-10.2, 18.8, -7.8, 21.4), "SERV", "común", "Buena práctica (Ley 26.873)"),
    Sector("SV-PA", "Primeros auxilios", R(-7.6, 18.8, -2.2, 24.2), "SERV", "común"),
    Sector("SV-CO", "Pasillo", R(-2.0, 11.2, -0.2, 29.8), "CIRC", "común"),
    Sector("SV-HA", "Hall, recepción y fichado", R(-6.0, 11.2, -2.2, 18.6), "SERV", "común"),
    Sector("SV-OF", "Oficinas (6 puestos)", R(-17.8, 14.8, -10.4, 18.6), "SERV", "común"),
    Sector("SV-JP", "Jefatura de planta", R(-10.2, 14.8, -8.2, 18.6), "SERV", "común"),
    Sector("SV-RE", "Reuniones", R(-8.0, 14.8, -6.2, 18.6), "SERV", "común"),
    Sector("SV-CM", "Comedor 30 plazas y office", R(-17.8, 11.2, -6.2, 14.6), "SERV", "común"),
    # recargas RC (x 0,3..18,2, y 0,3..24,6): entra por RC-1, recorre en U y sale por RC-2
    Sector("RC-MO", "Mostrador, recepción y clasificación", R(0.3, 0.3, 6.0, 6.0), "RC", "RC",
           "Clasificación en 4 colas: polvo, CO₂, agente limpio y líquidos"),
    Sector("RC-DE", "Desarme", R(6.2, 0.3, 12.0, 6.0), "RC", "RC"),
    Sector("RC-DC", "Descarga y ensayo de funcionamiento", R(12.2, 0.3, 18.2, 6.0), "RC", "RC",
           "Sala con extracción y recuperación de polvo"),
    Sector("RC-PH", "PH con jaula, lavado y secado", R(12.2, 6.2, 18.2, 12.0), "RC", "RC", "", 20.0),
    Sector("RC-PV", "Recinto de polvo (HR ≤ 70 %)", R(6.2, 6.2, 12.0, 12.0), "RC", "RC",
           "Carga ABC, BC y D; 8 renovaciones por hora; sin estufas", 33.5),
    Sector("RC-EN", "Ensamblaje, presurización y despacho", R(0.3, 6.2, 6.0, 12.0), "RC", "RC",
           "Peso, hermeticidad por inmersión y salida por RC-2", 6.0),
    Sector("RC-GA", "CO₂ y agente limpio", R(12.2, 12.2, 18.2, 16.0), "RC", "RC", "Trasvasador y balanza", 15.0),
    Sector("RC-LQ", "Líquidos", R(6.2, 12.2, 12.0, 16.0), "RC", "RC", "Agua, AFFF y clase K", 15.0),
    Sector("RC-RP", "Retoque de pintura y etiquetado", R(0.3, 12.2, 6.0, 16.0), "RC", "RC", "", 15.0),
    Sector("RC-CO", "Pasillo de recargas", R(0.3, 16.2, 18.2, 18.4), "CIRC", "RC"),
    Sector("RC-FI", "Flota de intercambio", R(0.3, 18.6, 12.0, 24.6), "RC", "RC", "958 equipos de reemplazo"),
    Sector("RC-IR", "Inutilizados y residuos", R(12.2, 18.6, 18.2, 24.6), "RC", "RC", "", 8.0),
]

PUERTAS_ANEXOS = [
    # (cod, (x0, y0), (x1, y1), tipo, uso)
    ("SV-1", (-5.2, 11.0), (-3.2, 11.0), "peatonal", "Ingreso de personal y visitas"),
    ("SV-2", (-18.0, 26.0), (-18.0, 27.2), "peatonal", "Salida de emergencia de vestuarios"),
]

# ============================================================ IMPLANTACIÓN
LM_Y = TERRENO[1]                  # línea municipal (calle al sur)
RETIRO_FRENTE = 10.0               # supuesto: retiro de frente parquizado (verificar con el PIVLA)

EXTERIOR = [
    ("PL-N", "Playa de descarga del semi bajo alero", R(6.0, 50.4, 30.0, 56.0), "playa"),
    ("PL-O", "Playa del chasis y volquete", R(-14.0, 36.0, -1.0, 50.0), "playa"),
    ("VQ-O", "Volquete 6 m³ (scrap)", R(-9.0, 30.6, -3.0, 34.6), "volquete"),
    ("JG-S", "Jaula de gases de soldadura (Ar/CO₂)", R(49.0, 50.4, 57.0, 54.4), "jaula"),
    ("ERM", "Regulación de gas de hornos", R(97.0, 24.0, 100.0, 27.0), "gas"),
    ("JG-N", "Jaula de N₂ y CO₂ (manifold)", R(60.6, -6.0, 64.6, -1.0), "jaula"),
    ("RI", "Reserva de agua contra incendio y bombas", R(108.0, 38.0, 118.0, 48.0), "incendio"),
    ("AMP", "Reserva de ampliación (nave hacia el este)", R(102.0, -8.0, 116.0, 34.0), "reserva"),
    ("PTE", "Tratamiento de efluentes líquidos", R(70.0, -27.0, 82.0, -19.0), "efluentes"),
    ("EST", "Estacionamiento de personal (38 + 2 accesibles)", R(-28.0, -44.0, 30.0, -22.0), "estac"),
    ("EU", "Utilitarios de reparto y recargas (8)", R(-28.0, -6.0, -8.0, 6.0), "estac"),
    ("GAR", "Garita y control de acceso", R(20.0, -58.0, 24.0, -54.0), "garita"),
    ("MT", "Celda de medición de media tensión", R(-38.0, -60.0, -32.0, -56.0), "elec"),
    ("ERP", "Estación reductora de gas", R(120.0, -60.0, 124.0, -57.0), "gas"),
]
# calles internas de camiones (ancho 7 m): anillo oeste - norte - este, entra por G1 y sale por G3
CALLES = [R(-36.0, -62.0, -29.0, 63.0), R(-36.0, 56.5, 126.0, 63.0), R(119.0, -62.0, 126.0, 63.0)]
PORTONES_TERRENO = [
    ("G1", -36.0, -29.0, "Camiones de MP, scrap, recargas y pintor"),
    ("G2", -6.0, 0.0, "Autos del personal"),
    ("G4", 21.0, 24.0, "Peatones"),
    ("G3", 119.0, 126.0, "Camiones de PT, carros, polvo, insumos y químicos"),
]

# ============================================================ EFLUENTES
EFLUENTES = [
    Flujo("EFL-L", [(83.6, 37.8), (83.6, 36.8), (77.0, 36.8), (77.0, 0.8), (76.0, -19.0)],
          "Pretratamiento de pintura"),
    Flujo("EFL-L", [(44.6, 45.8), (44.6, 44.6), (71.4, 44.6), (71.4, 0.8), (73.0, -19.0)], "Agua de PH 1 kg"),
    Flujo("EFL-L", [(46.8, 31.6), (46.8, 30.0), (71.0, 30.0)], "Agua de PH 2,5-10 kg"),
    Flujo("EFL-L", [(27.4, 12.4), (27.4, 11.0), (37.6, 11.0), (37.6, 0.8), (71.0, 0.8)], "Agua de PH de carros"),
    Flujo("EFL-L", [(15.2, 6.2), (15.2, 0.8), (18.2, 0.8)], "Lavado de recargas"),
    Flujo("EFL-L", [(76.0, -27.0), (76.0, -62.0)], "Vuelco a colectora (previa autorización)"),
]
# recargas: entra por RC-1, recorre la fila sur hacia el este, sube a PH y vuelve al oeste por la recarga
RC_FLUJO = [(-6.0, 3.0), (0.0, 3.0), (3.2, 3.0), (9.1, 3.0), (15.2, 3.0), (15.2, 9.1), (9.1, 9.1), (9.1, 14.1),
            (3.2, 14.1), (3.2, 9.1), (0.0, 8.8), (-6.0, 8.8)]

EMISIONES = [
    (28.2, 40.6, "Humos de soldadura de cuellos"), (36.1, 20.6, "Humos de soldadura de carros"),
    (35.3, 13.7, "Humos de soldadura de carros"), (40.8, 47.1, "Humos de soldadura 1 kg"),
    (34.1, 32.9, "Humos de soldadura 2,5-10 kg"), (43.2, 32.9, "Humos de soldadura 2,5-10 kg"),
    (56.5, 34.9, "Colector de la granalladora"), (92.0, 30.0, "Chimenea horno de secado"),
    (87.2, 3.4, "Chimenea horno de polimerizado"), (94.3, 16.6, "Ciclones de la cabina"),
    (70.6, 23.4, "Extracción sala de polvo 1-10 kg"), (24.2, 7.7, "Extracción sala de polvo carros"),
    (23.2, 46.6, "Humos de corte láser"), (9.1, 9.1, "Extracción recinto de polvo de recargas"),
    (51.4, 32.9, "Chimenea secadora 2,5-10 kg"), (49.2, 47.0, "Chimenea secadora 1 kg"),
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
    # agrupa cruces cercanos en una sola senda (franja de 1,2 m)
    grupos = []
    for p in sorted(set(pts)):
        for g in grupos:
            if any(abs(p[0] - q[0]) < 2.6 and abs(p[1] - q[1]) < 2.6 for q in g):
                g.append(p)
                break
        else:
            grupos.append([p])
    S = []
    for i, g in enumerate(grupos, 1):
        xs, ys = [p[0] for p in g], [p[1] for p in g]
        S.append((f"SP-{i}", R(min(xs) - 0.6, min(ys) - 0.6, max(xs) + 0.6, max(ys) + 0.6),
                  "Senda peatonal señalizada (cebra amarilla, IRAM 10005) en el cruce del personal con un flujo"))
    return S


HILOS = _hilos()
SENDAS = _sendas()
