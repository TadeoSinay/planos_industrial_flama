"""Genera salida/Dimensionamiento_Recargas_Planta_Comercial.xlsx y ..._Industrial.xlsx.

Mismo modelo para las dos plantas; cada archivo aplica su propio % de recargas (Proyecciones, Indexado Dim
Técnico V61 / V63). Hojas: PROY_Indexado -> datos_base -> parametros_recargas -> sobrestock_sustitutos -> Plan
mensual -> Demanda por puesto -> Resumen Capacidad (aprovechamiento consolidado). Todo lo calculado es fórmula; máquinas y turnos quedan en 1 para cargarlos a mano.
Negro y grises.
"""

import os

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "salida")

# ------------------------------------------------------------------ datos de las fuentes
ANIOS = list(range(2026, 2036))
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
# Proyecciones, Indexado Dim Técnico, filas 27 a 43 (recargas por tipo, 2026 a 2035)
REC = [
    ("ABC 1 kg", [3477.482124, 16970.58564, 30546.08951, 56048.31106, 84270.22613, 117407.8231, 147610.6356, 171404.3607, 183690.566, 196282.6907]),
    ("ABC 2,5 kg", [329.996668, 1287.414024, 2947.169216, 5426.043269, 7850.875806, 10423.94365, 12809.89571, 14263.06831, 15432.86983, 16620.76117]),
    ("ABC 5 kg", [1950.394097, 7852.61852, 17775.85701, 33605.56835, 48407.57189, 64323.04276, 78721.10039, 87237.2124, 94103.66761, 101095.1762]),
    ("ABC 10 kg", [118.343632, 437.716578, 1024.974821, 1960.409862, 2844.976846, 3810.390622, 4663.67807, 5164.514584, 5571.544328, 5985.950855]),
    ("Agua 10 l", [159.308736, 643.423542, 1474.362741, 2766.451205, 3991.465221, 5335.75578, 6538.958887, 7269.819681, 7855.44139, 8450.814081]),
    ("AFFF 10 l", [22.758391, 161.315751, 316.607276, 527.39462, 743.788946, 962.874335, 1194.942207, 1351.617183, 1477.54886, 1604.441422]),
    ("AFFF 50 l s/ruedas", [11.379195, 83.22352, 164.463834, 281.341145, 398.902509, 514.527284, 629.065505, 711.178024, 773.41098, 836.350805]),
    ("BC 5 kg", [6.827517, 47.073112, 88.889676, 159.502491, 219.796202, 291.869853, 368.844169, 408.408953, 445.781944, 483.479203]),
    ("Sales K 6 l", [81.930207, 335.398855, 746.598352, 1358.899837, 1961.125522, 2598.541412, 3197.263477, 3578.539452, 3870.747997, 4167.559622]),
    ("CO₂ 2 kg", [450.616139, 1697.18149, 3955.196858, 7561.26033, 10920.14481, 14514.88522, 17746.49927, 19617.20546, 21161.80625, 22734.50171]),
    ("CO₂ 5 kg", [125.17115, 643.630371, 1375.626719, 2460.284265, 3545.257683, 4723.461784, 5853.905178, 6608.459909, 7185.708397, 7769.577127]),
    ("HCFC/HFC 5 kg", [18.206713, 112.075122, 230.854041, 400.715334, 574.507789, 754.345623, 944.84884, 1072.234671, 1171.695753, 1271.941099]),
    ("Clase D 9 l", [6.827517, 47.073112, 88.889676, 148.279182, 205.226053, 255.765145, 328.417902, 366.908071, 401.681707, 436.686782]),
    ("ABC 25 kg s/ruedas", [17.637753, 85.987819, 186.869567, 336.583621, 484.132598, 643.220385, 792.431742, 889.677707, 965.31111, 1041.939702]),
    ("ABC 50 kg s/ruedas", [38.803056, 189.173203, 411.113048, 740.483966, 1065.091715, 1415.084848, 1743.349833, 1957.290955, 2123.684441, 2292.267343]),
    ("ABC 70 kg s/ruedas", [8.466121, 41.274153, 89.697392, 161.560138, 232.383647, 308.745785, 380.367236, 427.045299, 463.349333, 500.131057]),
    ("ABC 100 kg s/ruedas", [5.644081, 27.516102, 59.798262, 107.706759, 154.922431, 205.830523, 253.578158, 284.696866, 308.899555, 333.420704]),
]
# Proyecciones, Indexado Dim Técnico, filas 61 a 74, columna U (% zonal 2035) y planta según V61 / V63
ZONAS = [
    ("CABA Norte", 0.0521797399, "Comercial"),
    ("CABA Este", 0.0798836162, "Comercial"),
    ("CABA Sur", 0.0598172860, "Industrial"),
    ("CABA Oeste", 0.0637650712, "Comercial"),
    ("PBA Sur 1er (Avellaneda)", 0.0676801452, "Industrial"),
    ("PBA Sur 2do cordón", 0.0932172985, "Industrial"),
    ("PBA Sur 3er cordón", 0.0675217758, "Industrial"),
    ("PBA Norte 1er cordón", 0.0533558834, "Comercial"),
    ("PBA Norte 2do cordón", 0.0885682049, "Comercial"),
    ("PBA Norte 3er cordón", 0.0471361107, "Comercial"),
    ("PBA Oeste 1er cordón", 0.0848900664, "Comercial"),
    ("PBA Oeste 2do cordón", 0.0672643024, "Comercial"),
    ("PBA Oeste 3er cordón", 0.0174767438, "Comercial"),
    ("PBA Interior", 0.1572437555, "Comercial"),
]
# Proyecciones, hojas PROYECCION <rubro>: cociente sobre RECARGAS An (es el mismo en todos los tipos y rubros)
TASAS = [
    ("Mat Usados ÷ RECARGAS An", 0.05, "Se usa: equipos que llegan descargados por uso"),
    ("Mat PH ÷ RECARGAS An", 0.02, "Se usa: equipos que no pasan la PH y se inutilizan"),
    ("Mat Rot ÷ RECARGAS An", 0.01, "Se usa: equipos rotos que se inutilizan"),
    ("Mat Fin VU ÷ RECARGAS An", 0.03302041313770093,
     "No se usa: Proyecciones aplica la misma vida útil a todos los tipos; acá va la del Anexo E (20 años, CO₂ 30)"),
]
AGENTES = ["ABC", "BC", "Clase D", "Agua", "AFFF", "Sales K", "CO₂", "Halogenado"]
# agente de ruta, rodante (u. equivalentes), manguera con PH anual (IRAM 3517-2 9.7.1.4)
SIN_M = "No: la manguera no tiene cierre en el extremo"
TIPOS = [
    ("ABC", 0, 0, "No: tobera sin manguera"), ("ABC", 0, 0, SIN_M), ("ABC", 0, 0, SIN_M), ("ABC", 0, 0, SIN_M),
    ("Agua", 0, 0, SIN_M), ("AFFF", 0, 0, SIN_M),
    ("AFFF", 1, 1, "Sí, 9.7.1.4 a): lanza con cierre (rodante, IRAM 3541)"),
    ("BC", 0, 0, SIN_M), ("Sales K", 0, 0, SIN_M),
    ("CO₂", 0, 0, "No: difusor de brazo, sin manguera (catálogo FLAMA)"),
    ("CO₂", 0, 1, "Sí, 9.7.1.4 b): manguera de CO₂ (difusor con manga)"),
    ("Halogenado", 0, 0, SIN_M), ("Clase D", 0, 0, SIN_M),
] + [("ABC", 1, 1, "Sí, 9.7.1.4 a): válvula de cierre en la manguera (rodante, IRAM 3550)")] * 4

# Parámetros: (fila, texto, valor o fórmula, formato, dato a mano, fuente)
P_GEN = [
    (2, "Días hábiles por mes", 20, "0", True, "240 días hábiles por año ÷ 12 (dato del usuario)"),
    (3, "Horas por día (1 turno)", 8, "0", True, "Criterio: jornada de 8 h"),
    (4, "Refrigerio (min/turno)", 30, "0", True, "Criterio"),
    (5, "Horas productivas por turno", "=B3-B4/60", "0.00", False, ""),
    (6, "Horas productivas por mes (1 turno)", "=B2*B5", "0", False, ""),
    (7, "Umbral de aprovechamiento", 0.9, "0%", True,
     "Criterio (Dimensionamiento Técnico V2): 10 % de holgura para variabilidad, averías y mantenimiento"),
    (8, "Turnos máximos por día", 2, "0", True, "Criterio: hasta 2 turnos de 8 h; después se agrega máquina"),
    (9, "Equivalencia de un rodante (u. equivalentes)", 3, "0", True,
     "Criterio (Dimensionamiento Técnico V2): traslado en carro, morsa y manipuleo del porte"),
]
P_RUTA = [
    (13, "Intervalo máximo de PH — polvos, CO₂ y halogenados (años)", 5, "0", True,
     "IRAM 3517-2:2020, Anexo E (IRAM 3523, 3550, 3509, 3565 y 3504)"),
    (14, "Intervalo máximo de PH — agua, AFFF y sales K (años)", 2, "0", True,
     "IRAM 3517-2:2020, Anexo E (IRAM 3525, 3527, 3537, 3541, 3693 y 3694)"),
    (15, "% con PH — polvos, CO₂ y halogenados", "=1/B13", "0.0%", False,
     "En régimen vence la PH de 1 de cada 5 equipos por año"),
    (16, "% con PH — agua, AFFF y sales K", "=1/B14", "0.0%", False,
     "En régimen vence la PH de 1 de cada 2 equipos por año"),
    (17, "Vida útil — CO₂ (años)", 30, "0", True, "IRAM 3517-2:2020, Anexo E (IRAM 3509; IRAM 3565 hasta 10 kg)"),
    (18, "Vida útil — resto de los tipos (años)", 20, "0", True, "IRAM 3517-2:2020, Anexo E"),
    (19, "% fin de vida útil — CO₂", "=1/B17", "0.0%", False, "En régimen llega al fin de su vida 1 de cada 30"),
    (20, "% fin de vida útil — resto", "=1/B18", "0.0%", False, "En régimen llega al fin de su vida 1 de cada 20"),
    (21, "% que no pasan la PH", "=PROY_Indexado!B48", "0.0%", False,
     "Proyecciones (Mat PH). La norma manda inutilizarlos (9.12) pero no fija el %"),
    (22, "% rotos", "=PROY_Indexado!B49", "0.0%", False, "Proyecciones (Mat Rot)"),
    (23, "% inutilizados — CO₂", "=B19+B21+B22", "0.0%", False, "Fin de vida útil + no pasan la PH + rotos"),
    (24, "% inutilizados — resto", "=B20+B21+B22", "0.0%", False, "Fin de vida útil + no pasan la PH + rotos"),
    (25, "% que llegan descargados por uso", "=PROY_Indexado!B47", "0.0%", False,
     "Proyecciones (Mat Usados). 9.2.2: se recarga después de usarlo; la norma no fija el %"),
    (26, "Dígitos posibles del año de fabricación", 10, "0", True,
     "9.9.4 a): se cambia el polvo ABC cuando el último dígito del año de fabricación coincide con el del año "
     "del mantenimiento"),
    (27, "% ABC con cambio de polvo (a descarte)", "=1/B26", "0.0%", False, "1 de cada 10 equipos por año"),
    (28, "% agua, AFFF y sales K que se vacían y recargan", 1, "0%", True,
     "Anexo E: el agente se cambia cada año; 9.9.1.9 (sales K) y 9.9.1.10 (AFFF)"),
    (29, "% CO₂ que se abren por daño o cambio de piezas", 0.05, "0.0%", True,
     "Criterio sin fuente, a validar con una recargadora. 9.7.1.2: el dañado se examina y va a PH"),
    (30, "% que se pintan", 0.10, "0.0%", True, "Criterio sin fuente. 9.10 pide pintar los deteriorados; no fija %"),
    (31, "% polvos con humedad en el desarme (secado extra)", 0.01, "0.0%", True, "Criterio sin fuente"),
    (32, "Ensayos de laboratorio por recipiente de polvo", 0.001, "0.000", True,
     "Criterio. 9.9.3.1: el ensayo se hace cuando hay dudas sobre el polvo"),
]
# Sustituto del mismo tipo que el equipo retirado; el ABC 1 kg automotor no lleva (sin canje, criterio del usuario)
LLEVA = [0] + [1] * 16
SS = "sobrestock_sustitutos"
S_RUB = 14     # paso 1: tiempo por rubro (rubros en columnas B a H)
S_TIPO = 21    # paso 2: tipos
S_STOCK = 42   # paso 3: stock
S_ALTA = 64    # paso 4: alta anual (fabricar / comprar)
S_MANT = 88    # paso 5: mantenimiento anual en planta
# Proyecciones, hojas PROYECCION <rubro>, 2035: recargas de mercado por rubro y tipo en las zonas de cada planta
# (industrial = CABA Sur y PBA Sur; comercial = el resto). Los carros se reparten 25/55/12/8 % entre 25, 50, 70 y
# 100 kg como en PxQ (Corregido), filas 66 a 69.
RUBROS = ["Automotor", "Edificios", "Educación", "Hoteles", "Industrias / almacenes", "Salud", "Supermercados"]
MIX_RUBRO = {
    "Comercial": [
        [2787299, 0, 85878, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0],
        [0, 126747.3, 924509.9, 56663.5, 71575.0, 0, 0, 0, 25349.5, 231127.5, 32805.2, 0, 0, 5591.8, 12301.9, 2684.1,
         1789.4],
        [0, 25545.6, 95138.1, 10225.0, 8788.7, 0, 0, 0, 8036.5, 34334.4, 1607.3, 0, 0, 359.1, 790.0, 172.4, 114.9],
        [3578.5, 76743.6, 29300.8, 7032.2, 4688.1, 0, 0, 0, 11720.3, 11720.3, 5860.1, 0, 0, 586.0, 1289.2, 281.3, 187.5],
        [0, 0, 137671.9, 0, 15126.6, 19056.2, 11022.6, 5628.9, 9968.1, 7798.5, 39872.3, 11257.7, 4339.2, 4925.3,
         10835.6, 2364.1, 1576.1],
        [0, 12077.2, 77208.2, 10321.9, 14747.1, 0, 0, 0, 4616.3, 17366.2, 19474.2, 3992.6, 0, 2245.9, 4940.9, 1078.0,
         718.7],
        [612, 7088, 6153, 0, 647, 0, 0, 0, 0, 0, 2914, 0, 0, 0.0, 0.0, 0.0, 0.0],
    ],
    "Industrial": [
        [1188664, 0, 36760, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0],
        [0, 51231.6, 373689.5, 22903.5, 28930.8, 0, 0, 0, 10246.3, 93422.4, 13260.0, 0, 0, 2260.2, 4972.5, 1084.9,
         723.3],
        [0, 8719.2, 32472.3, 3490.0, 2999.8, 0, 0, 0, 2743.0, 11718.9, 548.6, 0, 0, 122.6, 269.6, 58.8, 39.2],
        [1533.8, 23764.4, 6552.8, 1572.7, 1048.4, 0, 0, 0, 2621.1, 2621.1, 1310.5, 0, 0, 131.1, 288.3, 62.9, 41.9],
        [0, 0, 44086.3, 0, 4377.3, 6232.7, 3220.9, 1816.2, 3384.2, 2600.2, 13536.8, 3632.5, 1568.0, 1589.2, 3496.3,
         762.8, 508.5],
        [0, 4173.4, 26680.3, 3566.9, 5096.0, 0, 0, 0, 1595.2, 6001.1, 6729.6, 1379.7, 0, 776.1, 1707.4, 372.5,
         248.3],
        [331, 3794, 3289, 0, 346, 0, 0, 0, 0, 0, 1558, 0, 0, 0.0, 0.0, 0.0, 0.0],
    ],
}
P_MIX = 98     # PROY_Indexado: primera fila de la matriz de esta planta (tipos en filas, rubros en columnas)
FILA_PERFIL = 37   # primera fila del perfil mensual (2026)
FILA_TIPO = 51     # primera fila de la tabla de tipos
FILA_PUESTO = 72   # primera fila de la tabla de puestos
N_PUESTOS = 29

PH_P, PH_A = "$B$15", "$B$16"
USO, DANO, DESC, HUM, LAB, LIQ, PINT = "$B$25", "$B$29", "$B$27", "$B$31", "$B$32", "$B$28", "$B$30"
INU_C, INU_R = "$B$23", "$B$24"


def todos(v):
    return [v] * 8


def agentes(**kw):
    claves = ["abc", "bc", "d", "agua", "afff", "k", "co2", "hal"]
    return [kw.get(k, 0) for k in claves]


LIQS = dict(agua="=" + LIQ, afff="=" + LIQ, k="=" + LIQ)
# (puesto, máquina / equipo, recurso, ruta por agente, tiempo tipo (fórmula de pasos), desglose, nota)
PUESTOS = [
    ("Recepción y registro", "Autoelevador + tablet e impresora de etiquetas; jaulas A y B", "Manual", todos(1),
     "=12.5+12.5+40+10", "Cargar jaulas 12,5 + descargar y controlar contra remito 12,5 + datos en el sistema 40 + "
     "separar por agente 10. Lo que se hace en el cliente no cuenta.", ""),
    ("Inspección visual", "Mesa con goma, lámpara con lupa, PC", "Manual", todos(1),
     "=5+30+25+10+15+5", "Escanear 5 + exterior 30 + válvula, manómetro y manguera 25 + fecha PH 10 + registro 15 + "
     "bandeja 5", "Antes 70 s; los pasos suman 90 s"),
    ("Descarga ABC — ruta recuperable", "Máquina neumática Yukon (tolva 240 kg)", "Máquina",
     agentes(abc="=1-" + USO + "-" + DESC), "=15+60+10",
     "Escanear y agitado 15 + descargar mirando el visor 60 + tapar 10 (el retiro de válvula se cuenta en Desarme)", ""),
    ("Descarga ABC — ruta descarte", "Tambor Yukon M-000030", "Máquina", agentes(abc="=" + DESC), "=15+60+10",
     "Igual que la ruta recuperable, al tambor", ""),
    ("Descarga BC", "Tambor Yukon M-000030 dedicado BC", "Máquina", agentes(bc=1), "=15+60+10",
     "Igual que ABC; todo a descarte", ""),
    ("Descarga de agua / AFFF / sales K", "IBC 1.000 l (AFFF) y tanque 600 l (agua)", "Máquina", agentes(**LIQS),
     "=10+10+15+60+10", "Escanear 10 + quitar lanza 10 + acoplar 15 + vaciar 60 + llevar a desarme 10",
     "Antes 180 s; los pasos suman 105 s. Sales K: misma ruta que agua y AFFF"),
    ("Recuperación de CO₂", "Trasvasadora CO₂ 103/D1 (misma máquina que la carga)", "Máquina",
     agentes(co2="=" + PH_P + "+" + DANO), "=20+20+120+20+15+10",
     "Pesar 20 + conectar 20 + bombear 120 + verificar y pesar 20 + desconectar 15 + registrar 10", ""),
    ("Recuperación de halogenado", "Unidad THB/BP (misma máquina que la carga)", "Máquina",
     agentes(hal="=" + PH_P + "+" + USO), "=60+20+30+300+40+15",
     "Preparar y verificar cilindro de paso 60 + pesar 20 + conectar 30 + recuperar 300 + pesar ambos 40 + anotar 15",
     ""),
    ("Desarme y limpieza — recinto", "Lanza de soplado + aspiradora industrial + llaves", "Manual",
     agentes(abc=1, bc=1, d=1), "=5+30+5+10+20+120*" + PH_P + "+5",
     "Verificar 5 + retirar válvula 30 + marbete 5 + bandeja 10 + soplar 20 + limpieza profunda 120 × % con PH + "
     "tapar 5", "Antes 90 s con 25 % de PH; los pasos suman 99 s con 20 %"),
    ("Desarme e inspección interior — zona general", "Boroscopio Klein ET19 + llaves", "Manual",
     agentes(co2="=" + PH_P + "+" + DANO, hal="=" + PH_P + "+" + USO, **LIQS), "=10+40+60+90*0.4+15+15",
     "Confirmar vacío 10 + retirar válvula 40 + boroscopio 60 + enjuague 90 × 40 % + foto 15 + tapar 15", ""),
    ("Laboratorio — Puffer y mufla", "Puffer Yukon M-100150 + mufla ORL-0", "Máquina",
     agentes(abc="=" + LAB, bc="=" + LAB), "=300+600+1800+60+120+300",
     "Tiempo por ENSAYO: registro 300 + mufla 600 + Puffer 1.800 + dictamen 60 + carga 120 + liberar tolva 300", ""),
    ("Prueba hidráulica", "Máquina PH Yukon 300 kg/cm²", "Máquina",
     agentes(abc="=" + PH_P, bc="=" + PH_P, d="=" + PH_P, agua="=" + PH_A, afff="=" + PH_A, k="=" + PH_A,
             co2="=" + PH_P, hal="=" + PH_P), "=12+20+90+90+75+15",
     "Verificar con patrón 12 + escanear 20 + llenar y conectar 90 + ensayo 90 + vaciar y retirar 75 + registrar 15. "
     "CO₂ lleva además ultrasonido y acuñado", ""),
    ("Secado", "Secadora Yukon de 6 recipientes", "Máquina",
     agentes(abc="=" + PH_P + "+" + HUM, bc="=" + PH_P + "+" + HUM, d="=" + PH_P + "+" + HUM,
             co2="=" + PH_P, hal="=" + PH_P), "=15+15*60/6+15",
     "Colocar 15 + 15 min ÷ 6 recipientes = 150 + retirar 15", "Agua, AFFF y sales K no se secan: se vuelven a llenar"),
    ("Inspección interior con videoscopio", "Videoscopio + mesa con soporte en V", "Manual",
     agentes(abc="=" + PH_P + "+" + HUM, bc="=" + PH_P + "+" + HUM, d="=" + PH_P + "+" + HUM,
             co2="=" + PH_P, hal="=" + PH_P), "=60+15+10", "Recorrer con la sonda 60 + guardar foto 15 + tapar 10", ""),
    ("Pintura", "Cabina con extracción, HVLP, lámparas IR, amoladora", "Máquina", todos("=" + PINT), 750,
     "", "Sin desglose de pasos en el original"),
    ("Carga de polvo ABC", "Máquina neumática Yukon con corte por peso", "Máquina", agentes(abc=1),
     "=6+15+45+15+15+10", "Contraste por turno 6 + tara 15 + carga 45 + pesar 15 + rosca 15 + registrar 10",
     "Antes 90 s; los pasos suman 106 s"),
    ("Carga de polvo BC", "Cargadora portátil Yukon dedicada BC", "Máquina", agentes(bc=1), "=10+15+75+15+15+10",
     "Contraste 10 + tara 15 + carga portátil 75 + pesar 15 + rosca 15 + registrar 10", ""),
    ("Descarga y carga Clase D", "Recipiente exclusivo + embudo + balanza", "Manual", agentes(d=1),
     "=180+15+240+30+15+10", "Descarga manual 180 + tara 15 + carga con embudo 240 + ajuste 30 + rosca 15 + registro 10",
     "Supuesto del original (no está en el documento de procesos)"),
    ("Carga de agua / AFFF / sales K", "Red + tanque de premezcla con bomba 40 l/min + balanza", "Máquina",
     agentes(**LIQS), "=20+10+30+15+15+10",
     "Contraste y premezcla 20 + tara 10 + cargar 30 + corregir 15 + rosca 15 + registrar 10", ""),
    ("Carga de CO₂", "Trasvasadora CO₂ 103/D1 + manifold", "Máquina",
     agentes(co2="=" + PH_P + "+" + DANO + "+" + USO), "=30+10+15+150+25+10",
     "Tarar y programar 30 + elegir origen 10 + abrir manifold 15 + llenar 150 + pesar 25 + registrar 10", ""),
    ("Ensamblaje y marbete — recinto", "Morsa + llave dinamométrica", "Manual", agentes(abc=1, bc=1, d=1),
     "=10+30+20+10+30+20", "Escanear 10 + revisar piezas 30 + o-ring 20 + marbete 10 + enroscar 30 + manguera y "
     "repuestos 20", ""),
    ("Presurización — recinto", "Pinza Yukon M-000150 + regulador", "Máquina", agentes(abc=1, bc=1, d=1),
     "=3+15+10+20+15+10", "Contraste por turno 3 + fijar presión 15 + colocar 10 + presurizar 20 + pasador 15 + "
     "registrar 10", ""),
    ("Ensamblaje y presurización — zona general", "Morsa + dinamométrica + pinza Yukon", "Manual",
     agentes(co2="=" + PH_P + "+" + DANO, hal="=" + PH_P + "+" + USO, **LIQS), "=120+50",
     "Ensamblaje 120 + presurización 50. CO₂ no se presuriza y halogenados se presurizan en la carga", ""),
    ("Carga y presurización de halogenado", "Unidad THB/BP + pinza", "Máquina", agentes(hal="=" + PH_P + "+" + USO),
     "=300+40+60+30", "Cargar 300 + presurizar 40 + agitar y repetir 60 + pesar y registrar 30", ""),
    ("Control de peso (CO₂ y halogenados sin recarga)", "Balanza", "Manual",
     agentes(co2="=1-(" + PH_P + "+" + DANO + "+" + USO + ")", hal="=1-(" + PH_P + "+" + USO + ")"), "=30+10",
     "Pesar y comparar 30 + registrar 10", "Anexo E: control anual de la masa"),
    ("Ensayo de pérdidas", "Tanque de inmersión inox (6 posiciones); spray en rodantes", "Máquina", todos(1),
     "=5+45+10+10+10", "Preparar por turno 5 + bajar y observar en tandas de 6: 45 + sacar 10 + secar 10 + registrar 10",
     ""),
    ("Precinto, etiqueta y despacho", "Dispensador + impresora + jaulas", "Manual", todos(1),
     "=15+25+15+10+15+6", "Precinto 15 + etiqueta 25 + revisión final 15 + cerrar OT 10 + jaula 15 + remito 6",
     "Antes 80 s; los pasos suman 86 s"),
    ("Inutilización y disposición final", "Taladro de columna con prensa en V", "Máquina",
     agentes(abc="=" + INU_R, bc="=" + INU_R, d="=" + INU_R, agua="=" + INU_R, afff="=" + INU_R, k="=" + INU_R,
             co2="=" + INU_C, hal="=" + INU_R), "=30+120+90+60+90",
     "Confirmar 30 + perforar 120 + desarmar y cortar manguera 90 + residuos 60 + foto y acta 90",
     "9.12 y Anexo G: acta de inutilización"),
    ("PH de mangueras (CO₂ y rodantes)", "Máquina PH Yukon 300 kg/cm² (misma que la PH de recipientes)", "Máquina",
     None, "=12+20+90+90+75+15",
     "Mismos pasos que la PH del recipiente: patrón 12 + escanear 20 + llenar y conectar 90 + ensayo 90 + vaciar y "
     "retirar 75 + registrar 15",
     "9.7.1.4: PH anual de mangueras de CO₂ y con cierre en el extremo (tabla 5). Demanda = fila Mangueras del Plan "
     "mensual. Criterio: tiempo igual al de la PH del recipiente; falta el rótulo plástico"),
]

# ------------------------------------------------------------------ estilo (sólo negro y grises)
F_N = Font(name="Arial", size=10)
F_B = Font(name="Arial", size=10, bold=True)
F_T = Font(name="Arial", size=12, bold=True)
F_W = Font(name="Arial", size=10, bold=True, color="FFFFFF")
NEGRO = PatternFill("solid", fgColor="000000")
GRIS = PatternFill("solid", fgColor="D9D9D9")
GRIS_C = PatternFill("solid", fgColor="F2F2F2")
GRIS_O = PatternFill("solid", fgColor="A6A6A6")
fino = Side(style="thin", color="808080")
BORDE = Border(left=fino, right=fino, top=fino, bottom=fino)
CEN = Alignment(horizontal="center", vertical="center", wrap_text=True)
IZQ = Alignment(horizontal="left", vertical="center", wrap_text=True)
DER = Alignment(horizontal="right", vertical="center")


def hoja(wb, nombre, anchos):
    ws = wb.create_sheet(nombre)
    ws.sheet_view.showGridLines = False
    for k, a in enumerate(anchos):
        ws.column_dimensions[L(k + 1)].width = a
    return ws


def tit(ws, r, t, c=1):
    ws.cell(r, c, t).font = F_T


def nota(ws, r, t, c=1):
    x = ws.cell(r, c, t)
    x.font = Font(name="Arial", size=9, italic=True)
    x.alignment = Alignment(horizontal="left", vertical="center")


def cab(ws, r, textos, c0=1):
    for k, t in enumerate(textos):
        c = ws.cell(r, c0 + k, t)
        c.font, c.fill, c.alignment, c.border = F_W, NEGRO, CEN, BORDE


def celda(ws, r, c, v, fmt=None, dato=False, neg=False, res=False):
    x = ws.cell(r, c, v)
    x.font = F_B if (neg or res) else F_N
    x.border = BORDE
    if dato:
        x.fill = GRIS
    elif res:
        x.fill = GRIS_C
    if fmt:
        x.number_format = fmt
    x.alignment = IZQ if isinstance(v, str) and not v.startswith("=") else (CEN if fmt is None else DER)
    return x


# ------------------------------------------------------------------ hojas
def h_proy(wb, planta):
    ws = hoja(wb, "PROY_Indexado", [30, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 50])
    tit(ws, 1, "Proyecciones — Indexado Dim Técnico (valores copiados)")
    nota(ws, 2, "Para actualizar: pegar valores de Proyecciones, Indexado Dim Técnico A27:K43 y U61:U74, o "
                "reemplazar por IMPORTRANGE. Celdas gris oscuro = datos.")
    cab(ws, 4, ["Recargas por tipo"] + ANIOS)
    for i, (n, v) in enumerate(REC):
        celda(ws, 5 + i, 1, n)
        for k, x in enumerate(v):
            celda(ws, 5 + i, 2 + k, x, "#,##0", dato=True)
    celda(ws, 22, 1, "Recargas total", neg=True)
    for k in range(10):
        celda(ws, 22, 2 + k, f"=SUM({L(2 + k)}5:{L(2 + k)}21)", "#,##0", res=True)

    tit(ws, 24, "Recargas por zona y planta (% zonal 2035, columna U; planta según V61 y V63)")
    cab(ws, 25, ["Zona", "% zonal 2035", "Planta"])
    for i, (z, p, pl) in enumerate(ZONAS):
        celda(ws, 26 + i, 1, z)
        celda(ws, 26 + i, 2, p, "0.0%", dato=True)
        celda(ws, 26 + i, 3, pl, dato=True).alignment = CEN
    dv = DataValidation(type="list", formula1='"Comercial,Industrial"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add("C26:C39")
    celda(ws, 41, 1, "% planta comercial", neg=True)
    celda(ws, 41, 2, '=SUMIF($C$26:$C$39,"Comercial",$B$26:$B$39)', "0.0%", res=True)
    celda(ws, 42, 1, "% planta industrial", neg=True)
    celda(ws, 42, 2, '=SUMIF($C$26:$C$39,"Industrial",$B$26:$B$39)', "0.0%", res=True)
    celda(ws, 43, 1, "Control (tiene que dar 100 %)")
    celda(ws, 43, 2, "=B41+B42", "0.0%")

    tit(ws, 45, "Tasas de Proyecciones (hojas PROYECCION por rubro; iguales para todos los tipos)")
    cab(ws, 46, ["Concepto", "Valor", "Uso en este archivo"])
    ws.merge_cells("C46:L46")
    for i, (t, v, u) in enumerate(TASAS):
        celda(ws, 47 + i, 1, t)
        celda(ws, 47 + i, 2, v, "0.0%", dato=True)
        celda(ws, 47 + i, 3, u)
        ws.merge_cells(start_row=47 + i, start_column=3, end_row=47 + i, end_column=12)

    celda(ws, 52, 1, "Planta de este archivo", neg=True)
    celda(ws, 52, 2, planta, dato=True).alignment = CEN
    dv2 = DataValidation(type="list", formula1='"Comercial,Industrial"', allow_blank=False)
    ws.add_data_validation(dv2)
    dv2.add("B52")
    celda(ws, 53, 1, "% de recargas de esta planta", neg=True)
    celda(ws, 53, 2, '=IF(B52="Comercial",B41,B42)', "0.0%", res=True)

    tit(ws, 55, "Recargas de mercado 2035 por tipo y rubro, zonas de cada planta (hojas PROYECCION <rubro>)")
    for j, (pl, r0) in enumerate([("Comercial", P_MIX - 40), ("Industrial", P_MIX - 20), (None, P_MIX)]):
        cab(ws, r0 - 1, [f"Planta {pl.lower()}" if pl else "Esta planta"] + RUBROS + ["Total"])
        for k in range(17):
            r = r0 + k
            celda(ws, r, 1, f"=A{5 + k}")
            for c in range(7):
                if pl:
                    celda(ws, r, 2 + c, MIX_RUBRO[pl][c][k], "#,##0", dato=True)
                else:
                    celda(ws, r, 2 + c, f'=IF($B$52="Comercial",{L(2 + c)}{P_MIX - 40 + k},{L(2 + c)}{P_MIX - 20 + k})',
                          "#,##0")
            celda(ws, r, 9, f"=SUM(B{r}:H{r})", "#,##0", res=True)
    nota(ws, P_MIX + 18, "Carros repartidos 25/55/12/8 % entre 25, 50, 70 y 100 kg, como PxQ (Corregido) filas 66 a 69.")
    ws.freeze_panes = "B5"


def h_datos(wb):
    ws = hoja(wb, "datos_base", [24, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11])
    cab(ws, 1, ["Tipo de matafuego"] + [f"=PROY_Indexado!{L(2 + k)}4" for k in range(10)])
    for i in range(17):
        celda(ws, 2 + i, 1, f"=PROY_Indexado!A{5 + i}")
        for k in range(10):
            celda(ws, 2 + i, 2 + k, f"=PROY_Indexado!{L(2 + k)}{5 + i}*PROY_Indexado!$B$53", "#,##0")
    celda(ws, 19, 1, "Recargas Total", neg=True)
    for k in range(10):
        celda(ws, 19, 2 + k, f"=SUM({L(2 + k)}2:{L(2 + k)}18)", "#,##0", res=True)
    nota(ws, 21, "Recargas de la planta = recargas del Indexado × % de esta planta (PROY_Indexado B53).")
    ws.freeze_panes = "B2"


def h_param(wb, planta):
    ws = hoja(wb, "parametros_recargas", [52, 30, 34, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 10, 11, 70, 60, 8])
    cab(ws, 1, ["Parámetro", "Valor", "Fuente / criterio"])
    ws.merge_cells("C1:P1")
    for r, t, v, f, d, fu in P_GEN:
        celda(ws, r, 1, t)
        celda(ws, r, 2, v, f, dato=d, res=not d)
        celda(ws, r, 3, fu)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=16)
    tit(ws, 11, f"CRITERIOS DE RUTA — PLANTA {planta.upper()} (IRAM 3517-2:2020 y Proyecciones)")
    cab(ws, 12, ["Parámetro", "Valor", "Fuente / criterio"])
    ws.merge_cells("C12:P12")
    for r, t, v, f, d, fu in P_RUTA:
        celda(ws, r, 1, t)
        celda(ws, r, 2, v, f, dato=d, res=not d)
        celda(ws, r, 3, fu)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=16)

    # perfil mensual plano
    tit(ws, 34, "PERFIL MENSUAL POR AÑO (plano, 1/12 por mes)")
    nota(ws, 35, "IRAM 3517-2:2020 9.2.1 (mantenimiento como mínimo anual) y 9.4.14 a) (la etiqueta fija el mes y año "
                 "del próximo): cada equipo vuelve en su mes y la norma no fija ningún mes del calendario. El "
                 "crecimiento se toma entre años (Proyecciones es anual).")
    cab(ws, 36, ["Año"] + MESES + ["Total"])
    for i, a in enumerate(ANIOS):
        r = FILA_PERFIL + i
        celda(ws, r, 1, a, "0").alignment = CEN
        for m in range(12):
            celda(ws, r, 2 + m, "=1/12", "0.0%", dato=True)
        celda(ws, r, 14, f"=SUM(B{r}:M{r})", "0.0%", res=True)

    # tipos
    tit(ws, 49, "TIPOS DE MATAFUEGO")
    cab(ws, 50, ["Tipo", "Agente (ruta)", "u. equivalentes por recipiente", "Manguera con PH anual (1 = sí)",
                 "Fuente de la manguera"])
    ws.merge_cells("E50:P50")
    for i, (ag, rod, mang, fu) in enumerate(TIPOS):
        r = FILA_TIPO + i
        celda(ws, r, 1, f"=datos_base!A{2 + i}")
        celda(ws, r, 2, ag).alignment = CEN
        celda(ws, r, 3, "=$B$9" if rod else 1, "0", res=bool(rod), dato=not rod)
        celda(ws, r, 4, mang, "0", dato=True)
        celda(ws, r, 5, fu)
        ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=16)
    dv = DataValidation(type="list", formula1=f"$E${FILA_PUESTO - 1}:$L${FILA_PUESTO - 1}", allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"B{FILA_TIPO}:B{FILA_TIPO + 16}")

    # puestos
    tit(ws, 70, "CAPACIDAD POR PUESTO (fracción de cada agente que pasa por el puesto)")
    cab(ws, FILA_PUESTO - 1, ["N°", "Puesto / operación", "Máquina / equipo", "Recurso"] + AGENTES
        + ["Tiempo tipo (s/u)", "Cap. real (u/h)", "Cap. real (u/mes, 1 turno)", "Desglose del tiempo (s)", "Nota"])
    for k, (pu, maq, rec, ruta, t, des, no) in enumerate(PUESTOS):
        r = FILA_PUESTO + k
        celda(ws, r, 1, k + 1, "0").alignment = CEN
        celda(ws, r, 2, pu)
        celda(ws, r, 3, maq)
        celda(ws, r, 4, rec, dato=True).alignment = CEN
        for j in range(8):
            if ruta is None:
                celda(ws, r, 5 + j, "—").alignment = CEN
            else:
                celda(ws, r, 5 + j, ruta[j], "0.0%")
        celda(ws, r, 13, t, "0", dato=True)
        celda(ws, r, 14, f"=IF(M{r}>0,3600/M{r},0)", "0.0", res=True)
        celda(ws, r, 15, f"=N{r}*$B$6", "#,##0", res=True)
        celda(ws, r, 16, des)
        celda(ws, r, 17, no)
    dv = DataValidation(type="list", formula1='"Máquina,Manual,Tercerizado"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"D{FILA_PUESTO}:D{FILA_PUESTO + N_PUESTOS - 1}")
    r = FILA_PUESTO + N_PUESTOS + 1
    celda(ws, r, 1, "—").alignment = CEN
    celda(ws, r, 2, "PH Firesafer (alternativa, no entra en el cálculo)")
    celda(ws, r, 3, "Banco Firesafer FS-JD12A")
    celda(ws, r, 13, 60, "0", dato=True)
    celda(ws, r, 14, f"=IF(M{r}>0,3600/M{r},0)", "0.0", res=True)
    celda(ws, r, 17, "El original copia el desglose de la Yukon (302 s) con 60 s: revisar antes de usarla")
    ws.freeze_panes = "B2"


def bloque_plan(r0):
    """Filas del bloque de un año en Plan mensual: tipos, total, agentes y mangueras."""
    return {"t1": r0 + 1, "t17": r0 + 17, "tot": r0 + 18, "ag1": r0 + 20, "mang": r0 + 28}


def h_plan(wb):
    ws = hoja(wb, "Plan mensual", [26, 12, 9] + [9] * 12 + [10, 14])
    for i, a in enumerate(ANIOS):
        r0 = 1 + 32 * i
        b = bloque_plan(r0)
        cab(ws, r0, [a, "Agente", "u. equiv."] + MESES + ["Total", "Incluye mant. de sustitutos (u./año)"])
        ws.cell(r0, 1).number_format = "0"
        rp = FILA_PERFIL + i
        y = L(2 + i)
        for k in range(17):
            r = b["t1"] + k
            ms = f"{SS}!${y}${S_MANT + k}"
            celda(ws, r, 1, f"=parametros_recargas!A{FILA_TIPO + k}")
            celda(ws, r, 2, f"=parametros_recargas!B{FILA_TIPO + k}").alignment = CEN
            celda(ws, r, 3, f"=parametros_recargas!C{FILA_TIPO + k}", "0")
            for m in range(12):
                celda(ws, r, 4 + m, f"=datos_base!${y}${2 + k}*parametros_recargas!${L(2 + m)}${rp}+{ms}/12",
                      "#,##0.0")
            celda(ws, r, 16, f"=SUM(D{r}:O{r})", "#,##0", res=True)
            celda(ws, r, 17, f"={ms}", "#,##0")
        celda(ws, b["tot"], 1, "Total recipientes", neg=True)
        for m in range(13):
            c = L(4 + m)
            celda(ws, b["tot"], 4 + m, f"=SUM({c}{b['t1']}:{c}{b['t17']})", "#,##0", res=True)
        celda(ws, b["tot"] + 1, 1, "Por agente (u. equivalentes)", neg=True)
        for j, ag in enumerate(AGENTES):
            r = b["ag1"] + j
            celda(ws, r, 1, ag)
            for m in range(13):
                c = L(4 + m)
                celda(ws, r, 4 + m, f"=SUMPRODUCT(($B${b['t1']}:$B${b['t17']}=$A{r})*{c}${b['t1']}:{c}${b['t17']}"
                                    f"*$C${b['t1']}:$C${b['t17']})", "#,##0.0")
        r = b["mang"]
        celda(ws, r, 1, "Mangueras con PH anual (u.)", neg=True)
        for m in range(13):
            c = L(4 + m)
            celda(ws, r, 4 + m, f"=SUMPRODUCT({c}${b['t1']}:{c}${b['t17']}*parametros_recargas!$D${FILA_TIPO}:"
                                f"$D${FILA_TIPO + 16})", "#,##0.0", res=True)
    ws.freeze_panes = "D2"


def fila_dem(i, k):
    return 2 + 32 * i + k


def h_demanda(wb):
    ws = hoja(wb, "Demanda por puesto", [44] + [9] * 12 + [11, 13, 12])
    for i, a in enumerate(ANIOS):
        r0 = 1 + 32 * i
        b = bloque_plan(r0)
        cab(ws, r0, [f"Año {a}"] + MESES + ["Total anual", "Demanda mes pico (u/mes)", "Demanda (u/h, 1 turno)"])
        for k in range(N_PUESTOS):
            r = fila_dem(i, k)
            rp = FILA_PUESTO + k
            celda(ws, r, 1, f"=parametros_recargas!$B${rp}")
            for m in range(12):
                c = L(4 + m)
                if PUESTOS[k][3] is None:
                    f = f"='Plan mensual'!{c}{b['mang']}"
                else:
                    f = "=" + "+".join(f"parametros_recargas!${L(5 + j)}${rp}*'Plan mensual'!{c}{b['ag1'] + j}"
                                       for j in range(8))
                celda(ws, r, 2 + m, f, "#,##0.0")
            celda(ws, r, 14, f"=SUM(B{r}:M{r})", "#,##0", res=True)
            celda(ws, r, 15, f"=MAX(B{r}:M{r})", "#,##0.0", res=True)
            celda(ws, r, 16, f"=O{r}/parametros_recargas!$B$6", "0.00", res=True)
    ws.freeze_panes = "B2"


ACCIONES = ["OK", "Agrega turno", "Agrega máquina", "Agrega operario (puesto manual)", "Tercerizado", "Revisar"]
ACC_TXT = ["Aprovechamiento dentro del umbral", "Hay turnos disponibles (menos que el máximo por día)",
           "Ya está en el máximo de turnos y el puesto es de máquina",
           "Ya está en el máximo de turnos y el puesto es manual",
           "Recurso cargado como Tercerizado en parametros_recargas", "Hay demanda y el puesto no tiene tiempo tipo"]


def h_resumen(wb):
    ws = hoja(wb, "Resumen Capacidad", [48] + [10] * 10 + [3, 3, 30, 56])
    bloques = {"util": 1, "maq": 33, "tur": 65, "nec": 97, "acc": 129}
    # lista de acciones (la acción sugerida se indexa a esta tabla)
    cab(ws, 1, ["Acciones (lista)", "Cuándo"], 14)
    for k, (a, t) in enumerate(zip(ACCIONES, ACC_TXT)):
        celda(ws, 2 + k, 14, a, dato=True)
        celda(ws, 2 + k, 15, t)
    celda(ws, 9, 14, "Umbral de aprovechamiento", neg=True)
    celda(ws, 9, 15, "=parametros_recargas!B7", "0%", res=True)
    celda(ws, 10, 14, "Turnos máximos por día", neg=True)
    celda(ws, 10, 15, "=parametros_recargas!B8", "0", res=True)
    nota(ws, 12, "Máquinas y turnos: celdas gris oscuro, cargar a mano.", 14)

    titulos = {"util": "Aprovechamiento consolidado (recargas de clientes + mantenimiento de sustitutos)", "maq": "Máquinas en el puesto (cargar a mano)",
               "tur": "Turnos del puesto (cargar a mano)", "nec": "Máquina × turno necesarios al umbral",
               "acc": "Acción sugerida"}
    for clave, r0 in bloques.items():
        cab(ws, r0, [titulos[clave]] + ANIOS)
        for k in range(N_PUESTOS):
            r = r0 + 1 + k
            rp = FILA_PUESTO + k
            celda(ws, r, 1, f"=parametros_recargas!$B${rp}")
            for i in range(10):
                c = L(2 + i)
                rd = fila_dem(i, k)
                dem = f"'Demanda por puesto'!$P${rd}"
                cap = f"parametros_recargas!$N${rp}"
                u = f"{c}{bloques['util'] + 1 + k}"
                mq = f"{c}{bloques['maq'] + 1 + k}"
                tu = f"{c}{bloques['tur'] + 1 + k}"
                if clave == "util":
                    celda(ws, r, 2 + i, f"=IF({cap}*{mq}*{tu}=0,0,{dem}/({cap}*{mq}*{tu}))", "0%")
                elif clave in ("maq", "tur"):
                    celda(ws, r, 2 + i, 1, "0", dato=True)
                elif clave == "nec":
                    celda(ws, r, 2 + i, f"=IF({cap}=0,0,ROUNDUP({dem}/({cap}*$O$9),0))", "0")
                else:
                    rec = f"parametros_recargas!$D${rp}"
                    celda(ws, r, 2 + i,
                          f'=IF({dem}=0,"—",IF({cap}=0,$N$7,IF({u}<=$O$9,$N$2,IF({rec}="Tercerizado",$N$6,'
                          f'IF({tu}<$O$10,$N$3,IF({rec}="Manual",$N$5,$N$4))))))').alignment = CEN
        rt = r0 + 1 + N_PUESTOS
        if clave == "util":
            celda(ws, rt, 1, "Aprovechamiento máximo", neg=True)
            for i in range(10):
                c = L(2 + i)
                celda(ws, rt, 2 + i, f"=MAX({c}{r0 + 1}:{c}{rt - 1})", "0%", res=True)
            ws.conditional_formatting.add(f"B{r0 + 1}:K{rt}",
                                          CellIsRule(operator="greaterThan", formula=["$O$9"], fill=GRIS_O,
                                                     font=Font(name="Arial", size=10, bold=True)))
        elif clave == "maq":
            celda(ws, rt, 1, "TOTAL máquinas / puestos", neg=True)
            for i in range(10):
                c = L(2 + i)
                celda(ws, rt, 2 + i, f"=SUM({c}{r0 + 1}:{c}{rt - 1})", "0", res=True)
        elif clave == "tur":
            celda(ws, rt, 1, "Turnos de la planta (máximo)", neg=True)
            for i in range(10):
                c = L(2 + i)
                celda(ws, rt, 2 + i, f"=MAX({c}{r0 + 1}:{c}{rt - 1})", "0", res=True)
        elif clave == "nec":
            celda(ws, rt, 1, "TOTAL máquina × turno necesarios", neg=True)
            for i in range(10):
                c = L(2 + i)
                celda(ws, rt, 2 + i, f"=SUM({c}{r0 + 1}:{c}{rt - 1})", "0", res=True)
    ws.freeze_panes = "B2"


def h_sust(wb):
    """Sustitutos (9.4.5): ciclo por rubro, stock, alta anual (fabricar / comprar) y mantenimiento, por tipo."""
    ws = hoja(wb, SS, [36, 12, 12, 12, 12, 12, 12, 12, 11, 11, 11, 26])
    tit(ws, 1, "SUSTITUTOS (IRAM 3517-2:2020, 9.4.5)")
    nota(ws, 2, "Mismo tipo que el equipo retirado. Va con el camión al retirar y vuelve cuando se devuelve el recargado.")
    cab(ws, 4, ["Parámetro", "Valor", "Fuente / criterio"])
    ws.merge_cells("C4:L4")
    filas = [("Días hábiles por mes", "=parametros_recargas!B2", "0", False, "parametros_recargas B2"),
             ("Día de retiro", 1, "0", True, "El sustituto sale con el camión que retira"),
             ("Día de devolución", 1, "0", True, "El sustituto vuelve con el camión que devuelve; no se deja en otro "
                                                  "cliente en ese viaje"),
             ("Minutos productivos por turno", "=parametros_recargas!B5*60", "0", False, "parametros_recargas B5"),
             ("Planta", "=PROY_Indexado!B52", None, False, "Comercial: compra todos. Industrial: fabrica los ABC")]
    for j, (t, v, f, d, fu) in enumerate(filas):
        r = 5 + j
        celda(ws, r, 1, t)
        celda(ws, r, 2, v, f, dato=d, res=not d).alignment = CEN
        celda(ws, r, 3, fu)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=12)

    # paso 1: tiempo por rubro
    tipos_rng = f"$C${S_TIPO}:$C${S_TIPO + 16}"
    tit(ws, S_RUB - 3, "PASO 1 — Tiempo por rubro (mix del rubro × tiempos de operación)")
    nota(ws, S_RUB - 2, "Días de proceso = minutos por equipo ÷ minutos del turno, redondeado hacia arriba (mínimo 1). "
                        "Ciclo del sustituto = retiro + proceso + devolución")
    cab(ws, S_RUB - 1, ["Concepto"] + RUBROS)
    conceptos = ["% de las recargas (mercado, zonas de la planta)", "Minutos de operación por equipo",
                 "Días de proceso", "Ciclo del sustituto (días)"]
    for j, t in enumerate(conceptos):
        r = S_RUB + j
        celda(ws, r, 1, t, neg=(j == 3))
        for c in range(7):
            col = L(2 + c)
            mix = f"PROY_Indexado!{col}${P_MIX}:{col}${P_MIX + 16}"
            f = [f"=SUM({mix})/SUM(PROY_Indexado!$B${P_MIX}:$H${P_MIX + 16})",
                 f"=IF(SUM({mix})=0,0,SUMPRODUCT({mix},{tipos_rng})/SUM({mix}))",
                 f"=MAX(1,ROUNDUP({col}{S_RUB + 1}/$B$8,0))",
                 f"=$B$6+{col}{S_RUB + 2}+$B$7"][j]
            celda(ws, r, 2 + c, f, ["0.0%", "0.0", "0", "0"][j], res=(j == 3))

    # paso 2: tipos
    tit(ws, S_TIPO - 2, "PASO 2 — Tipos (el ciclo de cada tipo pesa los rubros según sus recargas)")
    cab(ws, S_TIPO - 1, ["Tipo", "Lleva sustituto (1 = sí)", "Minutos de operación por equipo",
                         "Ciclo del sustituto (días)", "Origen", "", "Nota"])
    ws.merge_cells(f"E{S_TIPO - 1}:F{S_TIPO - 1}")
    ws.merge_cells(f"G{S_TIPO - 1}:L{S_TIPO - 1}")
    pr = "parametros_recargas"
    for k in range(17):
        r = S_TIPO + k
        rt = FILA_TIPO + k
        fila_mix = f"PROY_Indexado!$B${P_MIX + k}:$H${P_MIX + k}"
        celda(ws, r, 1, f"=datos_base!A{2 + k}")
        celda(ws, r, 2, LLEVA[k], "0", dato=True)
        celda(ws, r, 3, f"=(SUMPRODUCT(INDEX({pr}!$E${FILA_PUESTO}:$L${FILA_PUESTO + 27},0,MATCH({pr}!$B${rt},"
                        f"{pr}!$E${FILA_PUESTO - 1}:$L${FILA_PUESTO - 1},0)),{pr}!$M${FILA_PUESTO}:$M$"
                        f"{FILA_PUESTO + 27})*{pr}!$C${rt}+{pr}!$D${rt}*{pr}!$M${FILA_PUESTO + 28})/60", "0.0")
        celda(ws, r, 4, f"=IF(SUM({fila_mix})=0,$B$6+1+$B$7,SUMPRODUCT({fila_mix},$B${S_RUB + 3}:$H${S_RUB + 3})"
                        f"/SUM({fila_mix}))", "0.0", res=True)
        celda(ws, r, 5, f'=IF(AND($B$9="Industrial",LEFT(A{r},3)="ABC"),"Fabrica","Compra")').alignment = CEN
        ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=6)
        celda(ws, r, 7, "" if LLEVA[k] else "Automotor: sin canje")
        ws.merge_cells(start_row=r, start_column=7, end_row=r, end_column=12)

    origen = f"$E${S_TIPO}:$E${S_TIPO + 16}"

    def bloque(r0, titulo, explica, f_celda, pie, fmt):
        tit(ws, r0 - 3, titulo)
        nota(ws, r0 - 2, explica)
        cab(ws, r0 - 1, ["Tipo"] + ANIOS)
        for k in range(17):
            r = r0 + k
            celda(ws, r, 1, f"=datos_base!A{2 + k}")
            for i in range(10):
                celda(ws, r, 2 + i, f_celda(k, i), fmt)
        for j, (txt, f) in enumerate(pie):
            r = r0 + 17 + j
            celda(ws, r, 1, txt, neg=True)
            for i in range(10):
                c = L(2 + i)
                celda(ws, r, 2 + i, f(c, r0, r0 + 16), fmt, res=True)

    total = [("Total", lambda c, a, b: f"=SUM({c}{a}:{c}{b})")]
    bloque(S_STOCK, "PASO 3 — Stock (u.)",
           "Stock = recargas del año × % del mes pico ÷ días del mes × ciclo del sustituto, redondeado hacia arriba",
           lambda k, i: (f"=ROUNDUP(datos_base!{L(2 + i)}{2 + k}*$B${S_TIPO + k}*$D${S_TIPO + k}"
                         f"*MAX({pr}!$B${FILA_PERFIL + i}:$M${FILA_PERFIL + i})/$B$5,0)"),
           total, "#,##0")
    bloque(S_ALTA, "PASO 4 — Alta anual (u.)",
           "Alta = lo que crece el stock + stock del año anterior × % inutilizados (parametros_recargas B23 CO₂, "
           "B24 resto). Cada alta lleva faja amarilla y tarjeta",
           lambda k, i: (f"={L(2 + i)}{S_STOCK + k}" if i == 0 else
                         f"=MAX(0,{L(2 + i)}{S_STOCK + k}-{L(1 + i)}{S_STOCK + k})+{L(1 + i)}{S_STOCK + k}"
                         f'*IF({pr}!$B${FILA_TIPO + k}="CO₂",{pr}!$B$23,{pr}!$B$24)'),
           [("A fabricar (planta industrial)", lambda c, a, b: f'=SUMIF({origen},"Fabrica",{c}{a}:{c}{b})'),
            ("A comprar", lambda c, a, b: f'=SUMIF({origen},"Compra",{c}{a}:{c}{b})'),
            ("Kits de sustituto", lambda c, a, b: f"=SUM({c}{a}:{c}{b})")], "#,##0.0")
    bloque(S_MANT, "PASO 5 — Mantenimiento anual en planta (u.)",
           "Mantenimiento = stock del año anterior (9.4.5 y 9.2.1); entra al Plan mensual, 1/12 por mes",
           lambda k, i: 0 if i == 0 else f"={L(1 + i)}{S_STOCK + k}", total, "#,##0")
    ws.freeze_panes = "B5"


def generar(planta):
    wb = Workbook()
    wb.remove(wb.active)
    h_proy(wb, planta)
    h_datos(wb)
    h_param(wb, planta)
    h_sust(wb)
    h_plan(wb)
    h_demanda(wb)
    h_resumen(wb)
    wb.active = wb.sheetnames.index("Resumen Capacidad")
    os.makedirs(SALIDA, exist_ok=True)
    ruta = os.path.join(SALIDA, f"Dimensionamiento_Recargas_Planta_{planta}.xlsx")
    wb.save(ruta)
    return ruta


if __name__ == "__main__":
    for p in ("Comercial", "Industrial"):
        print(generar(p))
