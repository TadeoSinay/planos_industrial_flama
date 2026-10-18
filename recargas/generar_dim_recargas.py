"""Genera salida/Dimensionamiento_Recargas_Planta_Comercial.xlsx y ..._Industrial.xlsx.

Mismo modelo para las dos plantas; cada archivo aplica su propio % de recargas (Proyecciones, Indexado Dim
Técnico V61 / V63). Hojas: PROY_Indexado -> datos_base -> parametros_recargas -> Plan mensual -> Demanda por
puesto -> Resumen Capacidad. Todo lo calculado es fórmula; máquinas y turnos quedan en 1 para cargarlos a mano.
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
# Sustituto equivalente por tipo (Proyecciones, Reservas y Sustitutos, filas 54 a 65; IRAM 3517-2 9.4.5);
# None = no lleva sustituto (ABC 1 kg automotor: vuelve el mismo equipo, criterio del usuario)
SUST = [None, "ABC 5 kg", "ABC 5 kg", "ABC 10 kg", "Agua 10 l", "AFFF 10 l", "AFFF 50 l s/ruedas", "BC 5 kg",
        "Sales K 6 l", "CO₂ 5 kg", "CO₂ 5 kg", "HCFC/HFC 5 kg", "Clase D 9 l", "ABC 50 kg s/ruedas",
        "ABC 50 kg s/ruedas", "ABC 100 kg s/ruedas", "ABC 100 kg s/ruedas"]
GRUPOS = ["ABC 5 kg", "ABC 10 kg", "Agua 10 l", "AFFF 10 l", "AFFF 50 l s/ruedas", "BC 5 kg", "Sales K 6 l",
          "CO₂ 5 kg", "HCFC/HFC 5 kg", "Clase D 9 l", "ABC 50 kg s/ruedas", "ABC 100 kg s/ruedas"]
SS = "sobrestock_sustitutos"
S_TIPO = 10    # tabla 1 de sobrestock_sustitutos
S_STOCK = 111  # tabla 6 (stock por equivalente)
S_MANT = 175   # tabla 10 (mantenimiento por tipo)
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

    # perfil mensual: rampa del crecimiento anual
    tit(ws, 34, "PERFIL MENSUAL POR AÑO (rampa del crecimiento anual)")
    nota(ws, 35, "Cada equipo vuelve en su mes (IRAM 3517-2 9.2.1 y 9.4.14 a). Criterio: el crecimiento al año "
                 "siguiente se reparte parejo mes a mes; 2035 usa el crecimiento 2034→2035.")
    cab(ws, 36, ["Año", "Recargas del año", "Recargas del año siguiente", "Crecimiento", "Factor mensual (q)"]
        + MESES + ["Total"])
    for i, a in enumerate(ANIOS):
        r = FILA_PERFIL + i
        col = L(2 + i)
        celda(ws, r, 1, a, "0").alignment = CEN
        celda(ws, r, 2, f"=datos_base!{col}19", "#,##0")
        sig = f"=datos_base!{L(3 + i)}19" if i < 9 else "=IF(datos_base!J19>0,datos_base!K19^2/datos_base!J19,0)"
        celda(ws, r, 3, sig, "#,##0")
        celda(ws, r, 4, f"=IF(B{r}>0,C{r}/B{r},1)", "0.000")
        celda(ws, r, 5, f"=D{r}^(1/12)", "0.0000")
        for m in range(12):
            celda(ws, r, 6 + m, f"=IF(ABS($E{r}-1)<0.000000001,1/12,$E{r}^{m}*($E{r}-1)/($E{r}^12-1))", "0.0%")
        celda(ws, r, 18, f"=SUM(F{r}:Q{r})", "0.0%", res=True)

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
                celda(ws, r, 4 + m, f"=datos_base!${y}${2 + k}*parametros_recargas!${L(6 + m)}${rp}+{ms}/12",
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

    titulos = {"util": "Aprovechamiento por puesto", "maq": "Máquinas en el puesto (cargar a mano)",
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
    """Stock de sustitutos (9.4.5) por equivalente y su mantenimiento anual, que vuelve al Plan mensual."""
    ws = hoja(wb, "sobrestock_sustitutos", [44] + [11] * 10 + [70])
    tit(ws, 1, "SOBRESTOCK DE SUSTITUTOS (IRAM 3517-2 9.4.5)")
    nota(ws, 2, "Equipos afuera = retiros por día del mes pico × días afuera (ley de Little); depende de las recargas, "
                "no de la cantidad de clientes. El mantenimiento anual del stock entra al Plan mensual del año "
                "siguiente y suma al aprovechamiento.")
    cab(ws, 4, ["Parámetro", "Valor"] + [""] * 9 + ["Fuente / criterio"])
    celda(ws, 5, 1, "Días de ruta (retiro y devolución)")
    celda(ws, 5, 2, 1, "0", dato=True)
    celda(ws, 5, 12, "Criterio (a confirmar): se retira hoy, se recarga y vuelve en la ruta del día siguiente. El "
                     "camión entrega los recargados y retira en la misma visita (Word de procesos, Recepción)")
    celda(ws, 6, 1, "Días hábiles por mes")
    celda(ws, 6, 2, "=parametros_recargas!B2", "0", res=True)

    def tabla(r, titulo, filas, nombres, f_celda, fmt, total=False):
        tit(ws, r, titulo)
        cab(ws, r + 1, ["Tipo" if len(filas) == 17 else ("Agente" if len(filas) == 8 else "Sustituto equivalente")]
            + ANIOS)
        for k in range(len(filas)):
            rr = r + 2 + k
            celda(ws, rr, 1, nombres[k])
            for i in range(10):
                celda(ws, rr, 2 + i, f_celda(k, i, rr), fmt)
        if total:
            rt = r + 2 + len(filas)
            celda(ws, rt, 1, "Total", neg=True)
            for i in range(10):
                c = L(2 + i)
                celda(ws, rt, 2 + i, f"=SUM({c}{r + 2}:{c}{rt - 1})", fmt, res=True)

    # 1. tipos y sustituto equivalente
    tit(ws, 8, "1. Tipo y sustituto equivalente (igual clasificación y por lo menos igual capacidad)")
    cab(ws, 9, ["Tipo", "Agente", "Lleva sustituto (1 = sí)", "Sustituto equivalente"] + [""] * 7 + ["Fuente"])
    for k in range(17):
        r = S_TIPO + k
        celda(ws, r, 1, f"=datos_base!A{2 + k}")
        celda(ws, r, 2, f"=parametros_recargas!B{FILA_TIPO + k}").alignment = CEN
        celda(ws, r, 3, 0 if SUST[k] is None else 1, "0", dato=True)
        celda(ws, r, 4, SUST[k] or GRUPOS[0], dato=True)
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=6)
        celda(ws, r, 12, "Automotor: sin canje, vuelve el mismo equipo (criterio del usuario)" if SUST[k] is None
              else "Proyecciones, Reservas y Sustitutos, filas 54 a 65; 9.4.5")
    dv = DataValidation(type="list", formula1=f"$A${S_STOCK}:$A${S_STOCK + 11}", allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"D{S_TIPO}:D{S_TIPO + 16}")
    tipos = [f"=datos_base!A{2 + k}" for k in range(17)]

    # 2. retiros por día en el mes pico (sólo clientes)
    tabla(28, "2. Retiros por día hábil en el mes pico (recargas de clientes × mes pico ÷ días del mes)",
          range(17), tipos,
          lambda k, i, rr: f"=datos_base!{L(2 + i)}{2 + k}*MAX(parametros_recargas!$F${FILA_PERFIL + i}:"
                           f"$Q${FILA_PERFIL + i})/$B$6", "#,##0.0")
    # 3. aprovechamiento máximo de la ruta de cada agente y días de cola
    tabla(48, "3a. Aprovechamiento máximo de los puestos de la ruta (mes pico, Resumen Capacidad)", range(8),
          AGENTES,
          lambda k, i, rr: f"=SUMPRODUCT(MAX((parametros_recargas!${L(5 + k)}${FILA_PUESTO}:${L(5 + k)}$"
                           f"{FILA_PUESTO + 27}>0)*'Resumen Capacidad'!{L(2 + i)}$2:{L(2 + i)}$29))", "0%")
    tabla(58, "3b. Días de cola = (aprovechamiento − 1) × días del mes, si pasa el 100 %", range(8), AGENTES,
          lambda k, i, rr: f"=MAX(0,{L(2 + i)}{50 + k}-1)*$B$6", "0.0")
    # 4. días afuera y 5. equipos afuera
    tabla(69, "4. Días afuera = días de ruta + días de cola del agente", range(17), tipos,
          lambda k, i, rr: f"=$B$5+INDEX({L(2 + i)}$60:{L(2 + i)}$67,MATCH($B${S_TIPO + k},$A$60:$A$67,0))", "0.0")
    tabla(89, "5. Equipos afuera en el mes pico = retiros por día × días afuera", range(17), tipos,
          lambda k, i, rr: f"={L(2 + i)}{30 + k}*{L(2 + i)}{71 + k}*$C${S_TIPO + k}", "#,##0.0")
    # 6. stock por equivalente
    tabla(S_STOCK - 2, "6. Stock de sustitutos por equivalente (redondeado hacia arriba)", GRUPOS, GRUPOS,
          lambda k, i, rr: f"=ROUNDUP(SUMIF($D${S_TIPO}:$D${S_TIPO + 16},$A{rr},{L(2 + i)}$91:{L(2 + i)}$107),0)",
          "#,##0", total=True)
    # 7. equipos afuera en un mes promedio y 8. sobrestock
    tabla(125, "7. Equipos afuera en un mes promedio (recargas del año ÷ 240 × días afuera)", GRUPOS, GRUPOS,
          lambda k, i, rr: f"=SUMPRODUCT(($D${S_TIPO}:$D${S_TIPO + 16}=$A{rr})*$C${S_TIPO}:$C${S_TIPO + 16}"
                           f"*datos_base!{L(2 + i)}$2:{L(2 + i)}$18*{L(2 + i)}$71:{L(2 + i)}$87)/(12*$B$6)",
          "#,##0.0", total=True)
    tabla(141, "8. Sobrestock = stock − equipos afuera en un mes promedio (lo que sobra fuera del pico)", GRUPOS,
          GRUPOS, lambda k, i, rr: f"={L(2 + i)}{S_STOCK + k}-{L(2 + i)}{127 + k}", "#,##0", total=True)
    # 9. alta anual
    tabla(157, "9. Alta anual de sustitutos = lo que crece el stock + reposición de inutilizados", GRUPOS, GRUPOS,
          lambda k, i, rr: (f"={L(2 + i)}{S_STOCK + k}" if i == 0 else
                            f"=MAX(0,{L(2 + i)}{S_STOCK + k}-{L(1 + i)}{S_STOCK + k})+{L(1 + i)}{S_STOCK + k}"
                            f"*IF(INDEX($B${S_TIPO}:$B${S_TIPO + 16},MATCH($A{rr},$A${S_TIPO}:$A${S_TIPO + 16},0))"
                            f'="CO₂",parametros_recargas!$B$23,parametros_recargas!$B$24)'), "#,##0", total=True)
    # 10. mantenimiento anual del stock (al Plan mensual)
    tabla(S_MANT - 2, "10. Mantenimiento anual de sustitutos = stock del año anterior (9.4.5 y 9.2.1); entra al "
                      "Plan mensual parejo en los 12 meses", range(17), tipos,
          lambda k, i, rr: (0 if i == 0 else
                            f"=SUMIF($A${S_STOCK}:$A${S_STOCK + 11},$A{rr},{L(1 + i)}${S_STOCK}:{L(1 + i)}$"
                            f"{S_STOCK + 11})"), "#,##0", total=True)
    nota(ws, S_MANT + 19, "Criterio: el mantenimiento del stock propio se programa parejo en el año (1/12 por mes).")
    ws.freeze_panes = "B5"


def generar(planta):
    wb = Workbook()
    wb.remove(wb.active)
    h_proy(wb, planta)
    h_datos(wb)
    h_param(wb, planta)
    h_plan(wb)
    h_demanda(wb)
    h_resumen(wb)
    h_sust(wb)
    wb.active = wb.sheetnames.index("Resumen Capacidad")
    os.makedirs(SALIDA, exist_ok=True)
    ruta = os.path.join(SALIDA, f"Dimensionamiento_Recargas_Planta_{planta}.xlsx")
    wb.save(ruta)
    return ruta


if __name__ == "__main__":
    for p in ("Comercial", "Industrial"):
        print(generar(p))
