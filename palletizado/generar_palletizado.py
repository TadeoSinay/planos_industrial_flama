"""Genera salida/palletizado_PT.xlsx: palletizado del producto terminado, camión y frecuencia de envíos.

Lógica pedida por el usuario:
1. Vehículo: carrocería de Guajardo y Linares (GyL) que se carga por los laterales (sider) para los pallets y la
   Renault Master L3H2 para los rodantes.
2. Cuántos pallets entran en el vehículo elegido.
3. Disposición por pallet: cajas por tipo de matafuego (manuales) y cilindros vendidos vacíos (a granel, parados).
4. Cinco escenarios por grupo (manuales: 1 / 2,5 / 5 / 10 kg y mix de 2,5, 5 y 10; rodantes: 25 / 50 / 70 / 100 kg y
   mix de los cuatro) con la producción estacionalizada por semana -> frecuencia de envío.

Los datos salen de las planillas del usuario (MP - Abastecimiento y Almacenamiento, hoja Pallets PT; Proyecciones 5,
hoja Indexado Dim Técnico) y de fuentes web citadas en la hoja Fuentes. Todo lo calculado es fórmula.
Formato: sólo negro y grises (pedido del usuario).
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                       # noqa: E402
from matplotlib.patches import Rectangle, Circle     # noqa: E402
from openpyxl import Workbook                         # noqa: E402
from openpyxl.drawing.image import Image as XLImage  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter as L     # noqa: E402
from openpyxl.worksheet.datavalidation import DataValidation  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "salida")
IMG = os.path.join(SALIDA, "palletizado_img")

# ------------------------------------------------------------------ datos de las fuentes
MP = "MP - Abastecimiento y Almacenamiento, hoja Pallets PT"
PROY = "Proyecciones 5, hoja Indexado Dim Técnico"
TIPOS = ["1 kg", "2,5 kg", "5 kg", "10 kg", "25 kg", "50 kg", "70 kg", "100 kg"]
ANIOS = list(range(2026, 2036))
# Proyecciones 5, Indexado Dim Técnico, filas 3 a 10 (matafuegos terminados) y 15 a 22 (cilindros vendidos vacíos)
TERMINADOS = [
    [4178.736543, 5997.303977, 6851.747758, 8467.135549, 12680.63271, 15620.25307, 20332.55326, 25132.07848, 28573.33614, 32072.63913],
    [295.0303572, 709.7274503, 986.8680576, 1500.638174, 2312.627726, 3252.869887, 4102.315524, 5104.306587, 6195.186243, 7424.858444],
    [2255.773025, 3846.978881, 5093.537591, 6823.115313, 10819.30694, 14605.96411, 18877.75984, 23368.18637, 26967.72455, 30750.77872],
    [91.83318153, 177.2472967, 252.9787798, 358.0204941, 602.7181519, 872.605032, 1127.160545, 1395.444812, 1612.350054, 1840.848079],
    [34.05179136, 58.46214745, 75.20853998, 100.5298529, 155.8760035, 211.9344827, 272.6682332, 337.8486707, 393.6274156, 453.2705332],
    [74.913941, 128.6167244, 165.458788, 221.1656765, 342.9272077, 466.255862, 599.8701129, 743.2670756, 865.9803143, 997.1951731],
    [16.34485985, 28.06183078, 36.10009919, 48.25432941, 74.82048167, 101.7285517, 130.8807519, 162.1673619, 188.9411595, 217.569856],
    [10.89657324, 18.70788719, 24.06673279, 32.16955294, 49.88032112, 67.81903447, 87.25383461, 108.1115746, 125.960773, 145.0465706],
]
CILINDROS = [
    [0, 0, 7662.4, 26694.8, 49434.8, 71680.2, 101340.6, 131001, 146819.8, 170548],
    [0, 0, 299.6, 1043.8, 1933, 2803, 3963, 5123, 5741.4, 6669],
    [0, 0, 1478.8, 5152, 9540.8, 13834.2, 19558.6, 25283, 28335.8, 32915],
    [0, 0, 90.4, 315, 583.4, 845.8, 1195.4, 1545, 1731.4, 2011],
    [0, 0, 14.4, 50.2, 93, 135, 191, 247, 277, 322],
    [0, 0, 31.8, 110.8, 205.2, 297.6, 420.8, 544, 609.6, 708],
    [0, 0, 7, 24.4, 45.2, 65.4, 92.2, 119, 133.4, 155],
    [0, 0, 4.6, 16, 29.6, 42.8, 60.4, 78, 87.6, 102],
]
# Perfiles de estacionalidad del Dimensionamiento Técnico FLAMA (DATOS-BASE, filas 102 a 104), los mismos del MRP
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
PERFILES = [("Automovilístico (1 kg)", [.12, .09, .08, .075, .07, .07, .075, .075, .075, .075, .075, .12]),
            ("Manual comercial (2,5 / 5 / 10 kg)", [.10, .08, .085, .085, .08, .075, .08, .08, .08, .075, .07, .11]),
            ("Industrial sobre ruedas (25 a 100 kg)", [.085, .075, .09, .09, .09, .08, .09, .09, .085, .075, .07, .08])]
PERFIL_DE = [1, 2, 2, 2, 3, 3, 3, 3]           # perfil de cada tipo (1-based)
# MP, Pallets PT: sección B (cajas), sección A (cilindros), sección C (carros)
CAJA = {"u": [6, 1, 1, 1], "L": [265, 135, 165, 195], "A": [190, 135, 165, 195], "H": [410, 435, 515, 685],
        "tara": [0.35, 0.25, 0.35, 0.5], "masa": [2.08, 4.63, 8.48, 16.23]}
CIL = {"D": [76.2, 124, 153, 181.5, 276.5, 320, 390, 390], "H": [297.5, 333, 414, 582, 672, 858, 908, 1128],
       "m": [0.76, 1.48, 2.78, 5.48, 15.92, 23.3, 46.86176284, 56.84631739]}
CARRO = {"L": [600, 700, 800, 800], "A": [550, 600, 700, 750], "H": [962, 1145, 1200, 1597],
         "m": [55, 100, 140, 185]}

# ------------------------------------------------------------------ estilo (sólo negro y grises)
AR = "Arial"
F_N = Font(name=AR, size=10)
F_B = Font(name=AR, size=10, bold=True)
F_T = Font(name=AR, size=14, bold=True)
F_S = Font(name=AR, size=11, bold=True)
F_W = Font(name=AR, size=10, bold=True, color="FFFFFF")
F_I = Font(name=AR, size=9, italic=True, color="404040")
NEGRO = PatternFill("solid", fgColor="000000")
GRIS_O = PatternFill("solid", fgColor="BFBFBF")
GRIS = PatternFill("solid", fgColor="D9D9D9")
GRIS_C = PatternFill("solid", fgColor="F2F2F2")
fino = Side(style="thin", color="808080")
BORDE = Border(left=fino, right=fino, top=fino, bottom=fino)
WRAP = Alignment(wrap_text=True, vertical="center")
CEN = Alignment(horizontal="center", vertical="center", wrap_text=True)


def titulo(ws, t, sub=None, ancho=12):
    ws["A1"] = t
    ws["A1"].font = F_T
    if sub:
        ws["A2"] = sub
        ws["A2"].font = F_I
    ws.sheet_view.showGridLines = False


def cab(ws, r, textos, c0=1):
    for k, t in enumerate(textos):
        c = ws.cell(r, c0 + k, t)
        c.font = F_W
        c.fill = NEGRO
        c.alignment = CEN
        c.border = BORDE


def seccion(ws, r, t, ncol=10):
    c = ws.cell(r, 1, t)
    c.font = F_S
    for k in range(1, ncol + 1):
        ws.cell(r, k).fill = GRIS_O


def celda(ws, r, c, v, fmt=None, dato=False, neg=False, al=None):
    x = ws.cell(r, c, v)
    x.font = F_B if neg else F_N
    x.border = BORDE
    if dato:
        x.fill = GRIS
    if fmt:
        x.number_format = fmt
    x.alignment = al or (Alignment(horizontal="left", vertical="center", wrap_text=True) if isinstance(v, str) and
                         not str(v).startswith("=") else Alignment(horizontal="right", vertical="center"))
    return x


def anchos(ws, w):
    for k, a in enumerate(w):
        ws.column_dimensions[L(k + 1)].width = a


# ================================================================== libro
wb = Workbook()
D = {}          # direcciones de los datos: clave -> "Datos!$C$5"


def ref(hoja, col, fila):
    return f"{hoja}!${col}${fila}"


# ------------------------------------------------------------------ LEEME
ws = wb.active
ws.title = "LEEME"
titulo(ws, "PALLETIZADO DEL PRODUCTO TERMINADO Y FRECUENCIA DE ENVÍOS - FLAMA S.A.",
       "Producción estacionalizada por semana, disposición por pallet, vehículo y 5 escenarios por grupo.")
lineas = [
    ("Qué responde", "Cuántos pallets entran en el camión, cómo se arma cada pallet (cajas por tipo de matafuego y "
                     "cilindros a granel) y cada cuánto tiene que salir un camión según la producción de cada semana."),
    ("Lógica", "1) Vehículo (hoja Camion): carrocería sider de Guajardo y Linares para los pallets, cargada por los "
               "laterales con el autoelevador, y Renault Master L3H2 para los rodantes. 2) Pallets por camión. "
               "3) Disposición por pallet (Pallet_cajas, Pallet_cilindros). 4) Escenarios (Escenarios_manuales, "
               "Escenarios_rodantes, Escenarios_cilindros) con la producción semanal (Produccion). "
               "5) Frecuencia mes por mes (Frecuencia_mensual)."),
    ("Escenarios", "Manuales: 1) pallet lleno de 1 kg, 2) todo 2,5 kg, 3) todo 5 kg, 4) todo 10 kg, 5) mix de 2,5, "
                   "5 y 10 kg. Rodantes: lo mismo con 25, 50, 70 y 100 kg y el mix de los cuatro. Cilindros vendidos "
                   "vacíos: los mismos escenarios con su propia disposición."),
    ("Mix", "El mix se arma con pallets de un solo tipo cada uno (las cajas de 2,5, 5 y 10 kg tienen distinta altura y "
            "una capa sobre otra no cierra en 1,60 m), en la proporción de la producción del año elegido. En la "
            "Master el mix es la mezcla de carros en la proporción de la producción."),
    ("Cómo usar", "Las celdas con fondo gris de la hoja Datos son los datos: año de análisis, vehículo elegido, "
                  "medidas y pesos. Todo lo demás es fórmula y se recalcula."),
    ("Formato", "Negro y grises. Gris: dato editable. Blanco: fórmula. Negro: encabezado."),
    ("Criterio", "Lo que no sale de una fuente está rotulado «criterio» en la columna Fuente de la hoja Datos."),
    ("Esquemas", "La hoja Disposicion tiene los esquemas de cada pallet y de la carga de cada vehículo, dibujados con "
                 "los valores de este libro (año y vehículo de la hoja Datos al generarlo)."),
]
cab(ws, 4, ["Tema", "Detalle"])
for k, (a, b) in enumerate(lineas):
    celda(ws, 5 + k, 1, a, neg=True)
    celda(ws, 5 + k, 2, b)
    ws.row_dimensions[5 + k].height = 48
anchos(ws, [16, 120])

# ------------------------------------------------------------------ Datos
ws = wb.create_sheet("Datos")
titulo(ws, "DATOS", "Fondo gris = dato editable. Fuente de cada dato a la derecha.")
cab(ws, 4, ["Parámetro", "Unidad", "Valor", "Fuente / criterio"])
r = 5
seccion(ws, r, "Análisis", 4)
r += 1
for clave, nom, un, v, fu in [
    ("anio", "Año de análisis", "año", 2035, "Año de diseño de la planta (layout 2035)"),
    ("sem_mes", "Semanas por mes", "sem", 4, "20 días hábiles por mes ÷ 5 días por semana (MP, hoja Volumenes)"),
    ("sem_anio", "Semanas operativas por año", "sem", 48, "MP, hoja Volumenes: 48 semanas operativas"),
    ("dias_sem", "Días hábiles por semana", "días", 5, "Lunes a viernes"),
]:
    celda(ws, r, 1, nom)
    celda(ws, r, 2, un)
    celda(ws, r, 3, v, "0", dato=True)
    celda(ws, r, 4, fu)
    D[clave] = ref("Datos", "C", r)
    r += 1
dv = DataValidation(type="list", formula1='"' + ",".join(str(a) for a in ANIOS) + '"', allow_blank=False)
ws.add_data_validation(dv)
dv.add(D["anio"].split("!")[1].replace("$", ""))
r += 1
seccion(ws, r, "Pallet", 4)
r += 1
for clave, nom, un, v, fu in [
    ("PL", "Pallet: largo", "mm", 1200, "ARLOG IRAM 10016 (" + MP + ")"),
    ("PA", "Pallet: ancho", "mm", 1000, "ARLOG IRAM 10016 (" + MP + ")"),
    ("PH", "Pallet: alto", "mm", 145, "ARLOG IRAM 10016 (" + MP + ")"),
    ("PT", "Pallet: tara", "kg", 35, "ARLOG IRAM 10016 (" + MP + ")"),
    ("HMAX", "Altura máxima de la carga con el pallet", "mm", 1600, "Envolvedora EDOS: cargas de 1.000 a 1.700 mm (" + MP + ")"),
    ("WMAX", "Peso máximo de la carga por pallet", "kg", 1100, "EDOS 600 a 1.200 kg; ARLOG 1.500 kg en rack: se toma 1.100 (" + MP + ")"),
    ("SE", "Separador de cartón entre capas de cilindros: espesor", "mm", 3, MP + " (estimación)"),
    ("SM", "Separador de cartón: masa", "kg", 0.6, MP + " (estimación)"),
    ("NIV", "Pallets apilados en el camión", "niveles", 1, "Criterio: las cajas de cartón no soportan otro pallet encima"),
]:
    celda(ws, r, 1, nom)
    celda(ws, r, 2, un)
    celda(ws, r, 3, v, "0.0" if isinstance(v, float) else "#,##0", dato=True)
    celda(ws, r, 4, fu)
    D[clave] = ref("Datos", "C", r)
    r += 1
r += 1
seccion(ws, r, "Matafuegos manuales terminados, en caja (" + MP + ", sección B)", 7)
r += 1
cab(ws, r, ["Parámetro", "Unidad", "1 kg", "2,5 kg", "5 kg", "10 kg", "Fuente / criterio"])
r += 1
D["caja"] = {}
for clave, nom, un, fu in [("u", "Matafuegos por caja", "u", "ET's Matafuegos: el 1 kg va de a 6; el resto, de a uno"),
                           ("L", "Caja: largo exterior", "mm", "Ø + holgura (las de ET's no entran: ver Dudas en MP)"),
                           ("A", "Caja: ancho exterior", "mm", "Ídem"),
                           ("H", "Caja: alto exterior", "mm", "Recipiente + válvula (≈ 80 mm) + 20 mm"),
                           ("tara", "Tara de la caja", "kg", "Estimación de MP"),
                           ("masa", "Masa del matafuego lleno con accesorios", "kg", "Recipiente + polvo + válvula + accesorios (MP)")]:
    celda(ws, r, 1, nom)
    celda(ws, r, 2, un)
    for k in range(4):
        celda(ws, r, 3 + k, CAJA[clave][k], "0.00" if clave in ("tara", "masa") else "#,##0", dato=True)
    celda(ws, r, 7, fu)
    D["caja"][clave] = r
    r += 1
r += 1
seccion(ws, r, "Cilindros vendidos vacíos, a granel y parados (" + MP + ", sección A)", 11)
r += 1
cab(ws, r, ["Parámetro", "Unidad"] + TIPOS + ["Fuente"])
r += 1
D["cil"] = {}
for clave, nom, un, fu in [("D", "Ø del cilindro", "mm", "MP, hoja Geometria Acero"),
                           ("H", "Alto sin válvula (con tapón)", "mm", "MP, hoja Geometria Acero"),
                           ("m", "Masa del cilindro vacío", "kg", "MP, hoja Geometria Acero")]:
    celda(ws, r, 1, nom)
    celda(ws, r, 2, un)
    for k in range(8):
        celda(ws, r, 3 + k, CIL[clave][k], "0.00" if clave == "m" else "#,##0.0", dato=True)
    celda(ws, r, 11, fu)
    D["cil"][clave] = r
    r += 1
r += 1
seccion(ws, r, "Rodantes terminados, sobre sus ruedas", 7)
r += 1
cab(ws, r, ["Parámetro", "Unidad", "25 kg", "50 kg", "70 kg", "100 kg", "Fuente"])
r += 1
D["car"] = {}
for clave, nom, un, fu in [("L", "Huella del carro: largo", "mm", MP + ", sección C"),
                           ("A", "Huella del carro: ancho", "mm", MP + ", sección C"),
                           ("H", "Alto del carro", "mm", MP + ", sección C (ET's)"),
                           ("m", "Peso del matafuego cargado", "kg", "Ficha técnica Georgia ABC 90 (FLAMA_BOM, hoja Mercado)")]:
    celda(ws, r, 1, nom)
    celda(ws, r, 2, un)
    for k in range(4):
        celda(ws, r, 3 + k, CARRO[clave][k], "#,##0", dato=True)
    celda(ws, r, 7, fu)
    D["car"][clave] = r
    r += 1
r += 1
seccion(ws, r, "Vehículos", 7)
r += 1
cab(ws, r, ["Parámetro", "Unidad", "Sider GyL Full p/ balancín", "Sider baranda volcable GyL", "", "", "Fuente / criterio"])
r += 1
D["veh"] = {}
VEH = [("Lx", "Largo de la carrocería", "m", [7.5, 6.5], "Avisos de Guajardo y Linares en Agroads: hasta 7,50 m (balancín) y hasta 6,50 m"),
       ("Ax", "Ancho de la carrocería", "m", [2.6, 2.6], "Agroads: hasta 2,60 m / ancho reglamentario (Ley 24.449: 2,60 m)"),
       ("Hx", "Alto interior de la carrocería", "m", [2.4, 2.6], "Agroads: hasta 2,40 m y hasta 2,60 m"),
       ("dL", "Descuento al largo útil (frente y puertas)", "m", [0.1, 0.1], "Criterio"),
       ("dA", "Descuento al ancho útil (parantes y lonas)", "m", [0.14, 0.14], "Criterio"),
       ("dH", "Descuento al alto útil", "m", [0.1, 0.1], "Criterio"),
       ("CU", "Carga útil", "kg", [12000, 10000], "Balancín sider de 7,50 m: 12 a 14 t y 12 pallets (flota de Logística HC); "
                                                  "la de 6,50 m: criterio")]
for clave, nom, un, vals, fu in VEH:
    celda(ws, r, 1, nom)
    celda(ws, r, 2, un)
    for k, v in enumerate(vals):
        celda(ws, r, 3 + k, v, "#,##0" if clave == "CU" else "0.00", dato=True)
    celda(ws, r, 7, fu)
    D["veh"][clave] = r
    r += 1
celda(ws, r, 1, "Vehículo elegido para los pallets (1 o 2)", neg=True)
celda(ws, r, 2, "n.º")
celda(ws, r, 3, 1, "0", dato=True)
celda(ws, r, 7, "1 = Sider GyL Full para balancín: el más largo de GyL que se carga de costado (lonas corredizas)")
D["veh_sel"] = ref("Datos", "C", r)
dv2 = DataValidation(type="list", formula1='"1,2"', allow_blank=False)
ws.add_data_validation(dv2)
dv2.add(f"C{r}")
r += 2
cab(ws, r, ["Renault Master L3H2 (rodantes)", "Unidad", "Valor", "Fuente / criterio"])
r += 1
D["mas"] = {}
for clave, nom, un, v, fu in [
    ("L", "Largo de carga (al piso)", "m", 3.857, "Vansdirect, guía de medidas Renault Master L3H2"),
    ("A", "Ancho de carga", "m", 1.765, "Vansdirect / Vanaways (ancho de carga 1.760 a 1.765 mm)"),
    ("Ap", "Ancho entre pasos de rueda", "m", 1.38, "Vansdirect: 1.380 mm. Renault Malta da 1.730/1.760 para la Master nueva: se toma el menor (lado seguro)"),
    ("Lp", "Largo de la zona de los pasos de rueda", "m", 1.0, "Criterio"),
    ("Lt", "Largo libre entre los pasos de rueda y la puerta trasera", "m", 0.6,
     "Criterio (no hay dato publicado de la posición de los pasos de rueda)"),
    ("H", "Alto de carga", "m", 1.894, "Vanaways (alto de carga 1.894 mm)"),
    ("CU", "Carga útil", "kg", 1593, "Autocosmos, Renault Master L3H2 Furgón 2.3 (Argentina): 1.593 kg"),
]:
    celda(ws, r, 1, nom)
    celda(ws, r, 2, un)
    celda(ws, r, 3, v, "#,##0" if clave == "CU" else "0.000", dato=True)
    celda(ws, r, 4, fu)
    D["mas"][clave] = ref("Datos", "C", r)
    r += 1
anchos(ws, [46, 9, 13, 13, 13, 13, 13, 13, 13, 13, 60])
ws.column_dimensions["D"].width = 22
ws.freeze_panes = "A5"


def dcaja(clave, k):
    return f"Datos!${L(3 + k)}${D['caja'][clave]}"


def dcil(clave, k):
    return f"Datos!${L(3 + k)}${D['cil'][clave]}"


def dcar(clave, k):
    return f"Datos!${L(3 + k)}${D['car'][clave]}"


def dveh(clave, k):
    return f"Datos!${L(3 + k)}${D['veh'][clave]}"


# ------------------------------------------------------------------ Produccion
ws = wb.create_sheet("Produccion")
titulo(ws, "PRODUCCIÓN ANUAL, MENSUAL Y SEMANAL (estacionalizada)",
       "Anual: " + PROY + ". Estacionalidad: perfiles del Dimensionamiento Técnico FLAMA (DATOS-BASE, filas 102 a 104).")
r = 4
seccion(ws, r, "A. Producción anual (unidades)", 18)
r += 1
cab(ws, r, ["Año"] + ["Terminado " + t for t in TIPOS] + ["Cilindro " + t for t in TIPOS])
r_an0 = r + 1
for j, a in enumerate(ANIOS):
    rr = r_an0 + j
    celda(ws, rr, 1, a, "0", neg=True, al=CEN)
    for k in range(8):
        celda(ws, rr, 2 + k, TERMINADOS[k][j], "#,##0", dato=True)
        celda(ws, rr, 10 + k, CILINDROS[k][j], "#,##0", dato=True)
r_an1 = r_an0 + len(ANIOS) - 1
r = r_an1 + 1
celda(ws, r, 1, "Año elegido", neg=True)
r_sel = r
for c in range(2, 18):
    celda(ws, r, c, f"=INDEX({L(c)}{r_an0}:{L(c)}{r_an1},MATCH({D['anio']},$A${r_an0}:$A${r_an1},0))", "#,##0",
          neg=True)
    ws.cell(r, c).fill = GRIS_C
r += 2
seccion(ws, r, "B. Perfiles de estacionalidad (% de la producción anual de cada mes)", 15)
r += 1
cab(ws, r, ["Perfil"] + MESES + ["Total"])
r_pf = r + 1
for k, (nom, v) in enumerate(PERFILES):
    rr = r_pf + k
    celda(ws, rr, 1, f"{k + 1}. {nom}")
    for j, x in enumerate(v):
        celda(ws, rr, 2 + j, x, "0.0%", dato=True)
    celda(ws, rr, 14, f"=SUM(B{rr}:M{rr})", "0%")
r = r_pf + 3
celda(ws, r, 1, "Perfil de cada tipo (terminados y cilindros):", neg=True)
for k in range(8):
    celda(ws, r, 2 + k, f"{TIPOS[k]}: {PERFIL_DE[k]}")
r += 2
seccion(ws, r, "C. Producción mensual del año elegido (unidades)", 22)
r += 1
GRUPOS = [("Manuales mix (2,5+5+10)", [1, 2, 3], 0), ("Rodantes mix (25 a 100)", [4, 5, 6, 7], 0),
          ("Cil. manuales mix (2,5+5+10)", [1, 2, 3], 8), ("Cil. rodantes mix (25 a 100)", [4, 5, 6, 7], 8)]
cab(ws, r, ["Mes"] + ["Terminado " + t for t in TIPOS] + ["Cilindro " + t for t in TIPOS] + [g[0] for g in GRUPOS])
r_m0 = r + 1


def col_tipo(k, cil=False):
    return 2 + k + (8 if cil else 0)


for j in range(12):
    rr = r_m0 + j
    celda(ws, rr, 1, MESES[j], neg=True, al=CEN)
    for c in range(2, 18):
        k = (c - 2) % 8
        pr = r_pf + PERFIL_DE[k] - 1
        celda(ws, rr, c, f"={L(c)}${r_sel}*${L(2 + j)}${pr}", "#,##0")
    for g, (nom, ks, off) in enumerate(GRUPOS):
        celda(ws, rr, 18 + g, "=" + "+".join(f"{L(2 + off + k)}{rr}" for k in ks), "#,##0")
r_m1 = r_m0 + 11
rr = r_m1 + 1
celda(ws, rr, 1, "Total", neg=True)
for c in range(2, 22):
    celda(ws, rr, c, f"=SUM({L(c)}{r_m0}:{L(c)}{r_m1})", "#,##0", neg=True)
    ws.cell(rr, c).fill = GRIS_C
r = rr + 2
seccion(ws, r, "D. Producción por semana del año elegido (unidades por semana = mes ÷ semanas por mes)", 22)
r += 1
cab(ws, r, ["Mes"] + ["Terminado " + t for t in TIPOS] + ["Cilindro " + t for t in TIPOS] + [g[0] for g in GRUPOS])
r_s0 = r + 1
for j in range(12):
    rr = r_s0 + j
    celda(ws, rr, 1, MESES[j], neg=True, al=CEN)
    for c in range(2, 22):
        celda(ws, rr, c, f"={L(c)}{r_m0 + j}/{D['sem_mes']}", "#,##0")
r_s1 = r_s0 + 11
R_SEM = {}
for k2, (nom, f) in enumerate([("Semana promedio del año", "prom"), ("Semana del mes pico", "max"),
                                ("Semana del mes más bajo", "min")]):
    rr = r_s1 + 1 + k2
    celda(ws, rr, 1, nom, neg=True)
    for c in range(2, 22):
        if f == "prom":
            v = f"={L(c)}{r_m1 + 1}/{D['sem_anio']}"
        elif f == "max":
            v = f"=MAX({L(c)}{r_s0}:{L(c)}{r_s1})"
        else:
            v = f"=MIN({L(c)}{r_s0}:{L(c)}{r_s1})"
        celda(ws, rr, c, v, "#,##0", neg=True)
        ws.cell(rr, c).fill = GRIS_C
    R_SEM[f] = rr
rr = r_s1 + 4
celda(ws, rr, 1, "Mes pico", neg=True)
for c in range(2, 22):
    celda(ws, rr, c, f"=IF(MAX({L(c)}{r_s0}:{L(c)}{r_s1})=0,\"-\",INDEX($A${r_s0}:$A${r_s1},"
                     f"MATCH(MAX({L(c)}{r_s0}:{L(c)}{r_s1}),{L(c)}{r_s0}:{L(c)}{r_s1},0)))", al=CEN)
R_SEM["mes"] = rr
anchos(ws, [30] + [11] * 21)
ws.freeze_panes = "B4"
PROD = {"sel": r_sel, "m0": r_m0, "s0": r_s0, "s1": r_s1, "tot": r_m1 + 1}


def pcol(k, cil=False):
    return L(col_tipo(k, cil))


def gcol(g):
    return L(18 + g)


# ------------------------------------------------------------------ Pallet_cajas
ws = wb.create_sheet("Pallet_cajas")
titulo(ws, "DISPOSICIÓN POR PALLET: MATAFUEGOS MANUALES EN CAJA",
       "Pallet ARLOG 1.200 × 1.000 mm. Cajas paradas, en capas iguales; se elige la orientación que más cajas da.")
cab(ws, 4, ["Concepto", "Unidad", "1 kg", "2,5 kg", "5 kg", "10 kg", "Cómo se calcula"])
filas = [
    ("u", "Matafuegos por caja", "u", lambda k: f"={dcaja('u', k)}", "#,##0", "Datos"),
    ("L", "Caja: largo", "mm", lambda k: f"={dcaja('L', k)}", "#,##0", "Datos"),
    ("A", "Caja: ancho", "mm", lambda k: f"={dcaja('A', k)}", "#,##0", "Datos"),
    ("H", "Caja: alto", "mm", lambda k: f"={dcaja('H', k)}", "#,##0", "Datos"),
    ("pc", "Peso por caja", "kg", lambda k: f"={dcaja('u', k)}*{dcaja('masa', k)}+{dcaja('tara', k)}", "0.00",
     "matafuegos × masa + tara"),
    ("o1", "Cajas por capa: largo de la caja sobre el largo del pallet", "u",
     lambda k: f"=INT({D['PL']}/{{L}})*INT({D['PA']}/{{A}})", "#,##0", "INT(1200/largo) × INT(1000/ancho)"),
    ("o2", "Cajas por capa: girada 90°", "u",
     lambda k: f"=INT({D['PL']}/{{A}})*INT({D['PA']}/{{L}})", "#,##0", "INT(1200/ancho) × INT(1000/largo)"),
    ("cc", "CAJAS POR CAPA", "u", lambda k: "=MAX({o1},{o2})", "#,##0", "la mejor orientación"),
    ("dis", "Disposición de la capa", "", lambda k: '=IF({o1}>={o2},INT(' + D['PL'] + '/{L})&" × "&INT(' + D['PA'] +
     '/{A})&" (largo de la caja a lo largo)",INT(' + D['PL'] + '/{A})&" × "&INT(' + D['PA'] + '/{L})&" (girada 90°)")',
     None, "cajas a lo largo × a lo ancho del pallet"),
    ("ch", "Capas por altura", "u", lambda k: f"=INT(({D['HMAX']}-{D['PH']})/{{H}})", "#,##0",
     "(1.600 − 145) ÷ alto de la caja"),
    ("cp", "Capas por peso", "u", lambda k: f"=INT({D['WMAX']}/({{cc}}*{{pc}}))", "#,##0",
     "1.100 kg ÷ peso de una capa"),
    ("ca", "Capas adoptadas", "u", lambda k: "=MIN({ch},{cp})", "#,##0", "la menor"),
    ("cpal", "Cajas por pallet", "u", lambda k: "={cc}*{ca}", "#,##0", ""),
    ("U", "MATAFUEGOS POR PALLET", "u", lambda k: "={cpal}*{u}", "#,##0", "resultado"),
    ("W", "Peso bruto del pallet", "kg", lambda k: f"={{cpal}}*{{pc}}+{D['PT']}", "#,##0", "cajas × peso + tara"),
    ("Hp", "Altura del pallet armado", "mm", lambda k: f"={D['PH']}+{{ca}}*{{H}}", "#,##0", "pallet + capas × alto"),
    ("ap", "Superficie del pallet ocupada", "%", lambda k: f"={{cc}}*{{L}}*{{A}}/({D['PL']}*{D['PA']})", "0%",
     "cajas × huella ÷ 1,2 m²"),
    ("lim", "Limita", "", lambda k: '=IF({cp}<{ch},"el peso","la altura")', None, ""),
]
PC = {}
for i, f in enumerate(filas):
    PC[f[0]] = 5 + i


def armar(ws, filas, R, ncol, c0=3):
    for i, (clave, nom, un, fn, fmt, como) in enumerate(filas):
        rr = 5 + i
        celda(ws, rr, 1, nom, neg=clave in ("cc", "U", "UP", "ca"))
        celda(ws, rr, 2, un, al=CEN)
        for k in range(ncol):
            col = L(c0 + k)
            v = fn(k)
            for cl, fila in R.items():
                v = v.replace("{" + cl + "}", f"{col}{fila}")
            x = celda(ws, rr, c0 + k, v, fmt, neg=clave in ("U", "UP"))
            if clave in ("U", "UP"):
                x.fill = GRIS_C
            if fmt is None:
                x.alignment = CEN
        celda(ws, rr, c0 + ncol, como)


armar(ws, filas, PC, 4)
anchos(ws, [46, 7, 14, 14, 14, 14, 40])
ws.column_dimensions["C"].width = 16
PCAJ = PC

# ------------------------------------------------------------------ Pallet_cilindros
ws = wb.create_sheet("Pallet_cilindros")
titulo(ws, "DISPOSICIÓN POR PALLET: CILINDROS VENDIDOS VACÍOS",
       "A granel, parados, en cuadrícula, con separador de cartón entre capas y film (" + MP + ", sección A).")
cab(ws, 4, ["Concepto", "Unidad"] + TIPOS + ["Cómo se calcula"])
filas = [
    ("D", "Ø del cilindro", "mm", lambda k: f"={dcil('D', k)}", "#,##0.0", "Datos"),
    ("H", "Alto (con tapón)", "mm", lambda k: f"={dcil('H', k)}", "#,##0", "Datos"),
    ("m", "Masa del cilindro", "kg", lambda k: f"={dcil('m', k)}", "0.00", "Datos"),
    ("a", "Cilindros a lo largo del pallet", "u", lambda k: f"=INT({D['PL']}/{{D}})", "#,##0", "INT(1200/Ø)"),
    ("b", "Cilindros a lo ancho del pallet", "u", lambda k: f"=INT({D['PA']}/{{D}})", "#,##0", "INT(1000/Ø)"),
    ("cc", "CILINDROS POR CAPA", "u", lambda k: "={a}*{b}", "#,##0", "cuadrícula (al tresbolillo entran más, pero se "
                                                                      "desarma: no se adopta)"),
    ("ch", "Capas por altura", "u", lambda k: f"=INT(({D['HMAX']}-{D['PH']})/({{H}}+{D['SE']}))", "#,##0",
     "(1.600 − 145) ÷ (alto + separador)"),
    ("cp", "Capas por peso", "u", lambda k: f"=INT({D['WMAX']}/({{cc}}*{{m}}+{D['SM']}))", "#,##0",
     "1.100 kg ÷ peso de una capa"),
    ("ca", "Capas adoptadas", "u", lambda k: "=MAX(1,MIN({ch},{cp}))", "#,##0", "la menor (al menos 1)"),
    ("U", "CILINDROS POR PALLET", "u", lambda k: "={cc}*{ca}", "#,##0", "resultado"),
    ("sep", "Separadores por pallet", "u", lambda k: "={ca}+1", "#,##0", "capas + 1"),
    ("W", "Peso bruto del pallet", "kg", lambda k: f"={{U}}*{{m}}+{{sep}}*{D['SM']}+{D['PT']}", "#,##0", ""),
    ("Hp", "Altura del pallet armado", "mm", lambda k: f"={D['PH']}+{{ca}}*{{H}}+{{sep}}*{D['SE']}", "#,##0", ""),
    ("lim", "Limita", "", lambda k: '=IF({cp}<{ch},"el peso","la altura")', None, ""),
]
PCI = {f[0]: 5 + i for i, f in enumerate(filas)}
armar(ws, filas, PCI, 8)
anchos(ws, [40, 7] + [11] * 8 + [44])

# ------------------------------------------------------------------ Camion
ws = wb.create_sheet("Camion")
titulo(ws, "VEHÍCULOS: PALLETS POR CAMIÓN Y CARROS POR FURGÓN",
       "Los pallets se cargan por los laterales con el autoelevador (carrocería sider de lonas corredizas).")
cab(ws, 4, ["Concepto", "Unidad", "Sider GyL Full p/ balancín", "Sider baranda volcable GyL", "Cómo se calcula"])
filas = [
    ("Li", "Largo útil", "m", lambda k: f"={dveh('Lx', k)}-{dveh('dL', k)}", "0.00", "largo − descuento"),
    ("Ai", "Ancho útil", "m", lambda k: f"={dveh('Ax', k)}-{dveh('dA', k)}", "0.00", "ancho − descuento"),
    ("Hi", "Alto útil", "m", lambda k: f"={dveh('Hx', k)}-{dveh('dH', k)}", "0.00", "alto − descuento"),
    ("o1", "Pallets en el piso: lado de 1,2 m a lo ancho", "u",
     lambda k: f"=INT({{Li}}*1000/{D['PA']})*INT({{Ai}}*1000/{D['PL']})", "#,##0",
     "INT(largo/1,0) × INT(ancho/1,2)"),
    ("o2", "Pallets en el piso: lado de 1,2 m a lo largo", "u",
     lambda k: f"=INT({{Li}}*1000/{D['PL']})*INT({{Ai}}*1000/{D['PA']})", "#,##0",
     "INT(largo/1,2) × INT(ancho/1,0)"),
    ("piso", "PALLETS EN EL PISO", "u", lambda k: "=MAX({o1},{o2})", "#,##0", "la mejor orientación"),
    ("dis", "Disposición", "", lambda k: '=IF({o1}>={o2},INT({Li}*1000/' + D['PA'] + ')&" filas × "&INT({Ai}*1000/' +
     D['PL'] + ')&" (1,2 m a lo ancho)",INT({Li}*1000/' + D['PL'] + ')&" filas × "&INT({Ai}*1000/' + D['PA'] +
     ')&" (1,2 m a lo largo)")', None, ""),
    ("niv", "Niveles", "u", lambda k: f"={D['NIV']}", "#,##0", "Datos (sin apilar)"),
    ("UP", "PALLETS POR CAMIÓN (lugar)", "u", lambda k: "={piso}*{niv}", "#,##0", "piso × niveles"),
    ("CU", "Carga útil", "kg", lambda k: f"={dveh('CU', k)}", "#,##0", "Datos"),
    ("hmax", "Pallet más alto de este libro", "mm",
     lambda k: f"=MAX(Pallet_cajas!C{PCAJ['Hp']}:F{PCAJ['Hp']},Pallet_cilindros!C{PCI['Hp']}:J{PCI['Hp']})", "#,##0",
     "control de altura"),
    ("ok", "¿Entra de alto?", "", lambda k: '=IF({hmax}*{niv}<={Hi}*1000,"sí","no")', None, ""),
]
CAM = {f[0]: 5 + i for i, f in enumerate(filas)}
armar(ws, filas, CAM, 2)
r = 5 + len(filas) + 1
celda(ws, r, 1, "VEHÍCULO ELEGIDO (Datos)", neg=True)
celda(ws, r, 3, f'=INDEX(C4:D4,{D["veh_sel"]})', neg=True, al=CEN)
CAM["sel_nom"] = r
r += 1
celda(ws, r, 1, "Pallets por camión del vehículo elegido", neg=True)
celda(ws, r, 3, f"=INDEX(C{CAM['UP']}:D{CAM['UP']},{D['veh_sel']})", "#,##0", neg=True)
ws.cell(r, 3).fill = GRIS_C
CAM["sel_UP"] = r
r += 1
celda(ws, r, 1, "Carga útil del vehículo elegido", neg=True)
celda(ws, r, 3, f"=INDEX(C{CAM['CU']}:D{CAM['CU']},{D['veh_sel']})", "#,##0", neg=True)
CAM["sel_CU"] = r
r += 2
seccion(ws, r, "Renault Master L3H2: carros por furgón (cargados por atrás con la rampa, sobre sus ruedas)", 7)
r += 1
cab(ws, r, ["Concepto", "Unidad", "25 kg", "50 kg", "70 kg", "100 kg", "Cómo se calcula"])
r0 = r + 1
M_ = D["mas"]


def zona(largo, ancho):
    # carros de una zona: la mejor de las dos orientaciones (ROUND evita que 0,6/0,6 dé 0,999…)
    return (f"=MAX(INT(ROUND({largo}/{{l}},6))*INT(ROUND({ancho}/{{a}},6)),"
            f"INT(ROUND({largo}/{{a}},6))*INT(ROUND({ancho}/{{l}},6)))")


filas_m = [
    ("l", "Carro: largo", "m", lambda k: f"={dcar('L', k)}/1000", "0.00", "Datos"),
    ("a", "Carro: ancho", "m", lambda k: f"={dcar('A', k)}/1000", "0.00", "Datos"),
    ("zf", "Zona delantera (hasta los pasos de rueda)", "u",
     lambda k: zona(f"({M_['L']}-{M_['Lp']}-{M_['Lt']})", M_['A']),
     "#,##0", "largo − pasos de rueda − zona trasera; ancho de carga; mejor orientación"),
    ("zp", "Zona de los pasos de rueda", "u", lambda k: zona(M_['Lp'], M_['Ap']),
     "#,##0", "entre pasos de rueda; mejor orientación"),
    ("zt", "Zona trasera (hasta la puerta)", "u", lambda k: zona(M_['Lt'], M_['A']),
     "#,##0", "ancho de carga; mejor orientación"),
    ("piso", "CARROS POR LUGAR", "u", lambda k: "={zf}+{zp}+{zt}", "#,##0", "suma de las tres zonas"),
    ("m", "Peso del carro cargado", "kg", lambda k: f"={dcar('m', k)}", "#,##0", "Datos"),
    ("peso", "Carros por peso", "u", lambda k: f"=INT({M_['CU']}/{{m}})", "#,##0", "carga útil ÷ peso"),
    ("alto", "¿Entra de alto?", "", lambda k: f'=IF({dcar("H", k)}/1000<={M_["H"]},"sí","no")', None, ""),
    ("UP", "CARROS POR FURGÓN", "u", lambda k: "=MIN({piso},{peso})", "#,##0", "el menor"),
    ("lim", "Limita", "", lambda k: '=IF({peso}<{piso},"el peso","el lugar")', None, ""),
]
CM = {f[0]: r0 + i for i, f in enumerate(filas_m)}
for i, (clave, nom, un, fn, fmt, como) in enumerate(filas_m):
    rr = r0 + i
    celda(ws, rr, 1, nom, neg=clave in ("piso", "UP"))
    celda(ws, rr, 2, un, al=CEN)
    for k in range(4):
        col = L(3 + k)
        v = fn(k)
        for cl, fila in CM.items():
            v = v.replace("{" + cl + "}", f"{col}{fila}")
        x = celda(ws, rr, 3 + k, v, fmt, neg=clave == "UP")
        if clave == "UP":
            x.fill = GRIS_C
        if fmt is None:
            x.alignment = CEN
    celda(ws, rr, 7, como)
anchos(ws, [44, 7, 22, 22, 22, 22, 46])

# ------------------------------------------------------------------ escenarios
SEL_UP = f"Camion!$C${CAM['sel_UP']}"
SEL_CU = f"Camion!$C${CAM['sel_CU']}"


def esc_hoja(nombre, tit, sub, grupos):
    """grupos: [(titulo, [(nombre, tipo_k o 'mix', lista_k, cil, fuente_pallet)], vehiculo)]"""
    ws = wb.create_sheet(nombre)
    titulo(ws, tit, sub)
    r = 4
    salida = {}
    for gt, escs, veh in grupos:
        seccion(ws, r, gt, 7)
        r += 1
        cab(ws, r, ["Concepto", "Unidad"] + [e[0] for e in escs])
        r += 1
        r_ini = r
        R = {}
        rows = ["cont", "U", "W", "H", "lugar", "porpeso", "N", "lim", "UC", "an", "sp", "spi", "sva", "mes", "pal",
                "cp", "cpi", "cva", "dias", "env", "cmes", "can"]
        for i, cl in enumerate(rows):
            R[cl] = r_ini + i
        nombres = {
            "cont": ("Contenido", ""), "U": ("Unidades por pallet" if veh == "pal" else "Matafuegos por carro", "u"),
            "W": ("Peso bruto del pallet" if veh == "pal" else "Peso del carro cargado", "kg"),
            "H": ("Altura del pallet" if veh == "pal" else "Alto del carro", "mm"),
            "lugar": ("Pallets por camión por lugar" if veh == "pal" else "Carros por furgón por lugar", "u"),
            "porpeso": ("Pallets por camión por peso" if veh == "pal" else "Carros por furgón por peso", "u"),
            "N": ("PALLETS POR CAMIÓN" if veh == "pal" else "CARROS POR FURGÓN", "u"),
            "lim": ("Limita", ""), "UC": ("UNIDADES POR VIAJE", "u"),
            "an": ("Producción del año elegido", "u/año"), "sp": ("Producción: semana promedio", "u/sem"),
            "spi": ("Producción: semana del mes pico", "u/sem"), "sva": ("Producción: semana del mes más bajo", "u/sem"),
            "mes": ("Mes pico", ""), "pal": ("Pallets por semana en el mes pico" if veh == "pal" else
                                            "Carros por semana en el mes pico", "u/sem"),
            "cp": ("Viajes por semana: promedio", "viajes"), "cpi": ("VIAJES POR SEMANA: MES PICO", "viajes"),
            "cva": ("Viajes por semana: mes más bajo", "viajes"),
            "dias": ("Días hábiles entre envíos (mes pico, camión lleno)", "días"),
            "env": ("FRECUENCIA DE ENVÍO (mes pico)", ""), "cmes": ("Viajes en el mes pico", "viajes"),
            "can": ("Viajes por año", "viajes")}
        for cl in rows:
            nom, un = nombres[cl]
            celda(ws, R[cl], 1, nom, neg=cl in ("N", "UC", "cpi", "env"))
            celda(ws, R[cl], 2, un, al=CEN)
        for e_i, (enom, tipo, ks, cil, cont) in enumerate(escs):
            c = L(3 + e_i)
            if tipo != "mix":
                k = tipo
                if veh == "pal":
                    hoja = "Pallet_cilindros" if cil else "Pallet_cajas"
                    RR = PCI if cil else PCAJ
                    colp = L(3 + k)
                    U = f"={hoja}!{colp}{RR['U']}"
                    W = f"={hoja}!{colp}{RR['W']}"
                    H = f"={hoja}!{colp}{RR['Hp']}"
                    lugar = f"={SEL_UP}"
                    porpeso = f"=INT({SEL_CU}/{c}{R['W']})"
                else:
                    colc = L(3 + k - 4)
                    U = "=1"
                    W = f"=Camion!{colc}{CM['m']}"
                    H = f"={dcar('H', k - 4)}"
                    lugar = f"=Camion!{colc}{CM['piso']}"
                    porpeso = f"=Camion!{colc}{CM['peso']}"
                pc = pcol(k, cil)
                an = f"=Produccion!{pc}{PROD['sel']}"
                sp = f"=Produccion!{pc}{R_SEM['prom']}"
                spi = f"=Produccion!{pc}{R_SEM['max']}"
                sva = f"=Produccion!{pc}{R_SEM['min']}"
                mes = f"=Produccion!{pc}{R_SEM['mes']}"
                cmes = f"=IF({c}{R['UC']}=0,0,MAX(Produccion!{pc}{PROD['m0']}:{pc}{PROD['m0'] + 11})/{c}{R['UC']})"
            else:
                g = [i for i, gg in enumerate(GRUPOS) if gg[1] == ks and (gg[2] == 8) == cil][0]
                gc = gcol(g)
                prods = [f"Produccion!{pcol(k, cil)}{PROD['sel']}" for k in ks]
                sum_p = "+".join(prods)
                if veh == "pal":
                    hoja = "Pallet_cilindros" if cil else "Pallet_cajas"
                    RR = PCI if cil else PCAJ
                    den = "+".join(f"IF({hoja}!{L(3 + k)}{RR['U']}=0,0,{p}/{hoja}!{L(3 + k)}{RR['U']})"
                                   for k, p in zip(ks, prods))
                    U = f"=IF(({den})=0,0,({sum_p})/({den}))"
                    W = f"=IF(({den})=0,0,(" + "+".join(f"{p}/{hoja}!{L(3 + k)}{RR['U']}*{hoja}!{L(3 + k)}{RR['W']}"
                                                           for k, p in zip(ks, prods)) + f")/({den}))"
                    H = "=MAX(" + ",".join(f"{hoja}!{L(3 + k)}{RR['Hp']}" for k in ks) + ")"
                    lugar = f"={SEL_UP}"
                    porpeso = f"=IF({c}{R['W']}=0,0,INT({SEL_CU}/{c}{R['W']}))"
                else:
                    U = "=1"
                    W = f"=IF(({sum_p})=0,0,(" + "+".join(f"{p}*Camion!{L(3 + k - 4)}{CM['m']}"
                                                         for k, p in zip(ks, prods)) + f")/({sum_p}))"
                    H = "=MAX(" + ",".join(dcar("H", k - 4) for k in ks) + ")"
                    den = "+".join(f"{p}/Camion!{L(3 + k - 4)}{CM['piso']}" for k, p in zip(ks, prods))
                    lugar = f"=IF(({sum_p})=0,0,INT(({sum_p})/({den})))"
                    porpeso = f"=IF({c}{R['W']}=0,0,INT({M_['CU']}/{c}{R['W']}))"
                an = f"=Produccion!{gc}{PROD['tot']}"
                sp = f"=Produccion!{gc}{R_SEM['prom']}"
                spi = f"=Produccion!{gc}{R_SEM['max']}"
                sva = f"=Produccion!{gc}{R_SEM['min']}"
                mes = f"=Produccion!{gc}{R_SEM['mes']}"
                cmes = f"=IF({c}{R['UC']}=0,0,MAX(Produccion!{gc}{PROD['m0']}:{gc}{PROD['m0'] + 11})/{c}{R['UC']})"
            vals = {
                "cont": cont, "U": U, "W": W, "H": H, "lugar": lugar, "porpeso": porpeso,
                "N": f"=MIN({c}{R['lugar']},{c}{R['porpeso']})",
                "lim": f'=IF({c}{R["porpeso"]}<{c}{R["lugar"]},"el peso","el lugar")',
                "UC": f"={c}{R['N']}*{c}{R['U']}",
                "an": an, "sp": sp, "spi": spi, "sva": sva, "mes": mes,
                "pal": f"=IF({c}{R['U']}=0,0,{c}{R['spi']}/{c}{R['U']})",
                "cp": f"=IF({c}{R['UC']}=0,0,{c}{R['sp']}/{c}{R['UC']})",
                "cpi": f"=IF({c}{R['UC']}=0,0,{c}{R['spi']}/{c}{R['UC']})",
                "cva": f"=IF({c}{R['UC']}=0,0,{c}{R['sva']}/{c}{R['UC']})",
                "dias": f"=IF({c}{R['cpi']}=0,\"-\",{D['dias_sem']}/{c}{R['cpi']})",
                # menos de 1 viaje por semana: cada INT(1/v) semanas, así lo acumulado nunca supera el vehículo
                "env": f'=IF({c}{R["cpi"]}=0,"sin producción",IF({c}{R["cpi"]}>=1,ROUNDUP({c}{R["cpi"]},0)&" viajes por '
                       f'semana (carga media "&TEXT({c}{R["cpi"]}/ROUNDUP({c}{R["cpi"]},0),"0%")&")",'
                       f'IF(INT(1/{c}{R["cpi"]})=1,"1 viaje por semana","1 viaje cada "&INT(1/{c}{R["cpi"]})&" semanas")'
                       f'&" (carga "&TEXT({c}{R["cpi"]}*INT(1/{c}{R["cpi"]}),"0%")&")"))',
                "cmes": cmes,
                "can": f"=IF({c}{R['UC']}=0,0,{c}{R['an']}/{c}{R['UC']})",
            }
            fmts = {"cont": None, "U": "#,##0", "W": "#,##0", "H": "#,##0", "lugar": "#,##0", "porpeso": "#,##0",
                    "N": "#,##0", "lim": None, "UC": "#,##0", "an": "#,##0", "sp": "#,##0", "spi": "#,##0",
                    "sva": "#,##0", "mes": None, "pal": "0.0", "cp": "0.00", "cpi": "0.00", "cva": "0.00",
                    "dias": "0.0", "env": None, "cmes": "0.0", "can": "0.0"}
            for cl in rows:
                x = celda(ws, R[cl], 3 + e_i, vals[cl], fmts[cl], neg=cl in ("N", "UC", "cpi", "env"))
                if fmts[cl] is None:
                    x.alignment = CEN
                if cl in ("N", "UC", "cpi", "env"):
                    x.fill = GRIS_C
            if veh == "car" and tipo != "mix":
                ws.cell(R["U"], 3 + e_i).value = "=1"
        ws.row_dimensions[R["cont"]].height = 42
        ws.row_dimensions[R["env"]].height = 30
        salida[gt] = (R, len(escs))
        r = R[rows[-1]] + 3
    anchos(ws, [46, 8, 22, 22, 22, 22, 26])
    return ws, salida


CONT_M = ["Pallet lleno de matafuegos de 1 kg (cajas de 6)", "Pallet lleno de 2,5 kg (cajas individuales)",
          "Pallet lleno de 5 kg", "Pallet lleno de 10 kg",
          "Camión con pallets de 2,5, 5 y 10 kg en la proporción de la producción"]
ws_em, EM = esc_hoja("Escenarios_manuales", "ESCENARIOS: MATAFUEGOS MANUALES TERMINADOS",
                     "Pallets en el vehículo elegido (hoja Camion). Producción semanal del año elegido (hoja Produccion).",
                     [("Matafuegos manuales en caja", [("1. Todo 1 kg", 0, None, False, CONT_M[0]),
                                                       ("2. Todo 2,5 kg", 1, None, False, CONT_M[1]),
                                                       ("3. Todo 5 kg", 2, None, False, CONT_M[2]),
                                                       ("4. Todo 10 kg", 3, None, False, CONT_M[3]),
                                                       ("5. Mix 2,5 + 5 + 10 kg", "mix", [1, 2, 3], False, CONT_M[4])],
                       "pal")])
CONT_R = ["Furgón lleno de carros de 25 kg", "Furgón lleno de carros de 50 kg", "Furgón lleno de carros de 70 kg",
          "Furgón lleno de carros de 100 kg", "Mix de 25, 50, 70 y 100 kg en la proporción de la producción"]
ws_er, ER = esc_hoja("Escenarios_rodantes", "ESCENARIOS: RODANTES TERMINADOS EN LA RENAULT MASTER L3H2",
                     "Carros sobre sus ruedas, cargados por atrás con la rampa. Mix: capacidad ponderada por la producción.",
                     [("Rodantes en la Master L3H2", [("1. Todo 25 kg", 4, None, False, CONT_R[0]),
                                                      ("2. Todo 50 kg", 5, None, False, CONT_R[1]),
                                                      ("3. Todo 70 kg", 6, None, False, CONT_R[2]),
                                                      ("4. Todo 100 kg", 7, None, False, CONT_R[3]),
                                                      ("5. Mix 25 a 100 kg", "mix", [4, 5, 6, 7], False, CONT_R[4])],
                       "car")])
CONT_C = ["Pallet lleno de cilindros de {}", "Camión con pallets de {} en la proporción de la producción"]
ws_ec, EC = esc_hoja("Escenarios_cilindros", "ESCENARIOS: CILINDROS VENDIDOS VACÍOS",
                     "A granel, parados, con separador por capa. Pallets en el vehículo elegido.",
                     [("Cilindros de manuales", [("1. Todo 1 kg", 0, None, True, CONT_C[0].format("1 kg")),
                                                 ("2. Todo 2,5 kg", 1, None, True, CONT_C[0].format("2,5 kg")),
                                                 ("3. Todo 5 kg", 2, None, True, CONT_C[0].format("5 kg")),
                                                 ("4. Todo 10 kg", 3, None, True, CONT_C[0].format("10 kg")),
                                                 ("5. Mix 2,5 + 5 + 10 kg", "mix", [1, 2, 3], True,
                                                  CONT_C[1].format("2,5, 5 y 10 kg"))], "pal"),
                      ("Cilindros de rodantes", [("1. Todo 25 kg", 4, None, True, CONT_C[0].format("25 kg")),
                                                 ("2. Todo 50 kg", 5, None, True, CONT_C[0].format("50 kg")),
                                                 ("3. Todo 70 kg", 6, None, True, CONT_C[0].format("70 kg")),
                                                 ("4. Todo 100 kg", 7, None, True, CONT_C[0].format("100 kg")),
                                                 ("5. Mix 25 a 100 kg", "mix", [4, 5, 6, 7], True,
                                                  CONT_C[1].format("25 a 100 kg"))], "pal")])

# ------------------------------------------------------------------ Frecuencia mensual
ws = wb.create_sheet("Frecuencia_mensual")
titulo(ws, "FRECUENCIA DE ENVÍOS MES POR MES (viajes por semana, vehículo lleno)",
       "Con la producción de cada semana del mes (hoja Produccion) y la capacidad de cada escenario. "
       "Columna final: todo lo palletizado junto (terminados en caja + cilindros) en el vehículo elegido.")
cols = [("Manuales 1 kg (esc. 1)", "Escenarios_manuales", EM, "Matafuegos manuales en caja", 0, pcol(0)),
        ("Manuales mix 2,5/5/10 (esc. 5)", "Escenarios_manuales", EM, "Matafuegos manuales en caja", 4, gcol(0)),
        ("Rodantes mix en la Master (esc. 5)", "Escenarios_rodantes", ER, "Rodantes en la Master L3H2", 4, gcol(1)),
        ("Cilindros 1 kg (esc. 1)", "Escenarios_cilindros", EC, "Cilindros de manuales", 0, pcol(0, True)),
        ("Cilindros mix 2,5/5/10 (esc. 5)", "Escenarios_cilindros", EC, "Cilindros de manuales", 4, gcol(2)),
        ("Cilindros rodantes mix (esc. 5)", "Escenarios_cilindros", EC, "Cilindros de rodantes", 4, gcol(3))]
cab(ws, 4, ["Mes"] + [c[0] for c in cols] + ["Pallets por semana (todo lo palletizado)", "Kg por semana",
                                             "Viajes del vehículo elegido por semana (todo junto)"])
for j in range(12):
    rr = 5 + j
    celda(ws, rr, 1, MESES[j], neg=True, al=CEN)
    for i, (nom, hoja, E, g, e_i, pc) in enumerate(cols):
        R, n = E[g]
        uc = f"{hoja}!{L(3 + e_i)}{R['UC']}"
        celda(ws, rr, 2 + i, f"=IF({uc}=0,0,Produccion!{pc}{PROD['s0'] + j}/{uc})", "0.00")
    # pallets y kg de todo lo palletizado: terminados 1 a 10 kg en caja + cilindros de 1 a 100 kg
    pal, kg = [], []
    for k in range(4):
        p = f"Produccion!{pcol(k)}{PROD['s0'] + j}"
        pal.append(f"{p}/Pallet_cajas!{L(3 + k)}{PCAJ['U']}")
        kg.append(f"{p}/Pallet_cajas!{L(3 + k)}{PCAJ['U']}*Pallet_cajas!{L(3 + k)}{PCAJ['W']}")
    for k in range(8):
        p = f"Produccion!{pcol(k, True)}{PROD['s0'] + j}"
        pal.append(f"{p}/Pallet_cilindros!{L(3 + k)}{PCI['U']}")
        kg.append(f"{p}/Pallet_cilindros!{L(3 + k)}{PCI['U']}*Pallet_cilindros!{L(3 + k)}{PCI['W']}")
    cP, cK = L(2 + len(cols)), L(3 + len(cols))
    celda(ws, rr, 2 + len(cols), "=" + "+".join(pal), "0.0")
    celda(ws, rr, 3 + len(cols), "=" + "+".join(kg), "#,##0")
    celda(ws, rr, 4 + len(cols), f"=MAX({cP}{rr}/{SEL_UP},{cK}{rr}/{SEL_CU})", "0.00", neg=True)
    ws.cell(rr, 4 + len(cols)).fill = GRIS_C
rr = 17
celda(ws, rr, 1, "Máximo", neg=True)
for c in range(2, 5 + len(cols)):
    celda(ws, rr, c, f"=MAX({L(c)}5:{L(c)}16)", "0.00", neg=True)
    ws.cell(rr, c).fill = GRIS_C
rr = 18
celda(ws, rr, 1, "Promedio", neg=True)
for c in range(2, 5 + len(cols)):
    celda(ws, rr, c, f"=AVERAGE({L(c)}5:{L(c)}16)", "0.00", neg=True)
rr = 20
celda(ws, rr, 1, "Lectura", neg=True)
celda(ws, rr, 2, "Menos de 1 viaje por semana = el vehículo sale lleno cada 1 ÷ valor semanas. Los pallets de PT "
                 "esperan en el rack de PT hasta completar el viaje (stock de ciclo de despacho).")
ws.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=4 + len(cols))
ws.row_dimensions[rr].height = 30
anchos(ws, [10] + [18] * (len(cols) + 3))
ws.row_dimensions[4].height = 45


# ------------------------------------------------------------------ cálculo en Python (para los esquemas)
def py_caja(k):
    PL, PA, HMAX, PH, WMAX = 1200, 1000, 1600, 145, 1100
    L_, A_, H_ = CAJA["L"][k], CAJA["A"][k], CAJA["H"][k]
    pc = CAJA["u"][k] * CAJA["masa"][k] + CAJA["tara"][k]
    o1 = (PL // L_) * (PA // A_)
    o2 = (PL // A_) * (PA // L_)
    if o1 >= o2:
        nx, ny, bw, bh = PL // L_, PA // A_, L_, A_
    else:
        nx, ny, bw, bh = PL // A_, PA // L_, A_, L_
    cc = max(o1, o2)
    ca = min((HMAX - PH) // H_, int(WMAX // (cc * pc)))
    return dict(nx=nx, ny=ny, bw=bw, bh=bh, cc=cc, ca=ca, H=H_, U=cc * ca * CAJA["u"][k], W=cc * ca * pc + 35,
                Hp=PH + ca * H_)


def py_cil(k):
    PL, PA, HMAX, PH, WMAX = 1200, 1000, 1600, 145, 1100
    D_, H_, m = CIL["D"][k], CIL["H"][k], CIL["m"][k]
    a, b = int(PL // D_), int(PA // D_)
    cc = a * b
    ca = max(1, min(int((HMAX - PH) // (H_ + 3)), int(WMAX // (cc * m + 0.6))))
    return dict(a=a, b=b, D=D_, cc=cc, ca=ca, H=H_, U=cc * ca, W=cc * ca * m + (ca + 1) * 0.6 + 35,
                Hp=PH + ca * H_ + (ca + 1) * 3)


MAS = dict(L=3.857, A=1.765, Ap=1.38, Lp=1.0, Lt=0.6)


def py_master(k):
    """Zonas (x0, x1, ancho, y0, largo del carro en x, ancho en y, carros) y totales."""
    l, a = CARRO["L"][k] / 1000, CARRO["A"][k] / 1000
    Lm, Am, Ap, Lp, Lt = MAS["L"], MAS["A"], MAS["Ap"], MAS["Lp"], MAS["Lt"]
    xa = Lm - Lp - Lt
    zonas = []
    for x0, x1, w, y0 in [(0, xa, Am, 0), (xa, xa + Lp, Ap, (Am - Ap) / 2), (xa + Lp, Lm, Am, 0)]:
        op = [(int(round((x1 - x0) / l_, 6)) * int(round(w / a_, 6)), l_, a_) for l_, a_ in ((l, a), (a, l))]
        n, l_, a_ = max(op, key=lambda t: t[0])
        zonas.append((x0, x1, w, y0, l_, a_, n))
    return zonas, sum(z[6] for z in zonas), int(1593 // CARRO["m"][k])


# ------------------------------------------------------------------ esquemas
os.makedirs(IMG, exist_ok=True)
GR = ["#d9d9d9", "#bfbfbf", "#a6a6a6", "#8c8c8c"]


def esquema_caja(k):
    p = py_caja(k)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw={"width_ratios": [1.25, 1]})
    a1.add_patch(Rectangle((0, 0), 1200, 1000, fc="white", ec="black", lw=1.5))
    for i in range(p["nx"]):
        for j in range(p["ny"]):
            a1.add_patch(Rectangle((i * p["bw"] + 2, j * p["bh"] + 2), p["bw"] - 4, p["bh"] - 4, fc=GR[(i + j) % 2],
                                   ec="black", lw=0.6))
    a1.set_xlim(-30, 1230)
    a1.set_ylim(-30, 1030)
    a1.set_aspect("equal")
    a1.set_title(f"Capa: {p['nx']} × {p['ny']} = {p['cc']} cajas", fontsize=9)
    a1.set_xlabel("1.200 mm", fontsize=8)
    a1.set_ylabel("1.000 mm", fontsize=8)
    a1.tick_params(labelsize=6)
    a2.add_patch(Rectangle((0, 0), 1200, 145, fc="#595959", ec="black"))
    for c in range(p["ca"]):
        for i in range(p["nx"]):
            a2.add_patch(Rectangle((i * p["bw"] + 2, 145 + c * p["H"] + 2), p["bw"] - 4, p["H"] - 4, fc=GR[c % 2 + 1],
                                   ec="black", lw=0.6))
    a2.axhline(1600, color="black", ls="--", lw=0.8)
    a2.text(600, 1620, "altura máx. 1.600 mm", ha="center", fontsize=7)
    a2.set_xlim(-30, 1230)
    a2.set_ylim(0, 1750)
    a2.set_aspect("equal")
    a2.set_title(f"Costado: {p['ca']} capas, {p['Hp']} mm", fontsize=9)
    a2.tick_params(labelsize=6)
    fig.suptitle(f"Matafuego {TIPOS[k]}: {p['U']} u por pallet, {p['W']:,.0f} kg".replace(",", "."), fontsize=10,
                 fontweight="bold")
    fig.tight_layout()
    f = os.path.join(IMG, f"caja_{k}.png")
    fig.savefig(f, dpi=110)
    plt.close(fig)
    return f


def esquema_cil(k):
    p = py_cil(k)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw={"width_ratios": [1.25, 1]})
    a1.add_patch(Rectangle((0, 0), 1200, 1000, fc="white", ec="black", lw=1.5))
    r_ = p["D"] / 2
    for i in range(p["a"]):
        for j in range(p["b"]):
            a1.add_patch(Circle((r_ + i * p["D"], r_ + j * p["D"]), r_ * 0.96, fc=GR[1], ec="black", lw=0.4))
    a1.set_xlim(-30, 1230)
    a1.set_ylim(-30, 1030)
    a1.set_aspect("equal")
    a1.set_title(f"Capa: {p['a']} × {p['b']} = {p['cc']} cilindros", fontsize=9)
    a1.tick_params(labelsize=6)
    a2.add_patch(Rectangle((0, 0), 1200, 145, fc="#595959", ec="black"))
    y = 145
    for c in range(p["ca"]):
        a2.add_patch(Rectangle((0, y), 1200, 3, fc="black"))
        y += 3
        for i in range(p["a"]):
            a2.add_patch(Rectangle((i * p["D"] + 2, y), p["D"] - 4, p["H"], fc=GR[c % 2 + 1], ec="black", lw=0.4))
        y += p["H"]
    a2.add_patch(Rectangle((0, y), 1200, 3, fc="black"))
    a2.axhline(1600, color="black", ls="--", lw=0.8)
    a2.set_xlim(-30, 1230)
    a2.set_ylim(0, 1750)
    a2.set_aspect("equal")
    a2.set_title(f"Costado: {p['ca']} capas con separador, {p['Hp']:.0f} mm", fontsize=9)
    a2.tick_params(labelsize=6)
    fig.suptitle(f"Cilindro {TIPOS[k]}: {p['U']} u por pallet, {p['W']:,.0f} kg".replace(",", "."), fontsize=10,
                 fontweight="bold")
    fig.tight_layout()
    f = os.path.join(IMG, f"cil_{k}.png")
    fig.savefig(f, dpi=110)
    plt.close(fig)
    return f


def esquema_camion():
    Li, Ai = 7.4, 2.46
    fig, ax = plt.subplots(figsize=(8.5, 3.0))
    ax.add_patch(Rectangle((0, 0), 7.5, 2.6, fc="white", ec="black", lw=1.5))
    ax.add_patch(Rectangle((0.05, 0.07), Li, Ai, fc="#f2f2f2", ec="black", lw=0.6, ls="--"))
    n = int(Li // 1.0)
    for i in range(n):
        for j in range(2):
            ax.add_patch(Rectangle((0.1 + i * 1.0, 0.08 + j * 1.2), 0.96, 1.16, fc=GR[(i + j) % 2 + 1], ec="black",
                                   lw=0.6))
            ax.text(0.58 + i * 1.0, 0.66 + j * 1.2, f"{2 * i + j + 1}", ha="center", va="center", fontsize=7)
    ax.add_patch(Rectangle((-1.6, 0.25), 1.5, 2.1, fc=GR[3], ec="black"))
    ax.text(-0.85, 1.3, "cabina", ha="center", va="center", fontsize=7, rotation=90)
    for x in (1.5, 4.0, 6.5):
        ax.annotate("", xy=(x, -0.05), xytext=(x, -0.6), arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.text(4.0, -0.85, "carga lateral con autoelevador (lonas corredizas)", ha="center", fontsize=7)
    ax.set_xlim(-1.8, 7.8)
    ax.set_ylim(-1.1, 2.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Sider GyL Full para balancín (7,50 × 2,60 m): {2 * n} pallets de 1.200 × 1.000, "
                 "el lado de 1,2 m a lo ancho", fontsize=9)
    fig.tight_layout()
    f = os.path.join(IMG, "camion.png")
    fig.savefig(f, dpi=110)
    plt.close(fig)
    return f


def esquema_master(k):
    zonas, npiso, npeso = py_master(k)
    Lm, Am, Ap, Lp, Lt = MAS["L"], MAS["A"], MAS["Ap"], MAS["Lp"], MAS["Lt"]
    fig, ax = plt.subplots(figsize=(5.2, 2.7))
    ax.add_patch(Rectangle((0, 0), Lm, Am, fc="white", ec="black", lw=1.5))
    xa = Lm - Lp - Lt
    for y0 in (0, Am - (Am - Ap) / 2):
        ax.add_patch(Rectangle((xa, y0), Lp, (Am - Ap) / 2, fc=GR[3], ec="black", lw=0.6))
    cnt = 0
    nmax = min(npiso, npeso)
    for x0, x1, w, y0, l, a, _n in zonas:
        nx, ny = int(round((x1 - x0) / l, 6)), int(round(w / a, 6))
        for i in range(nx):
            for j in range(ny):
                if cnt >= nmax:
                    break
                ax.add_patch(Rectangle((x0 + i * l + 0.02, y0 + j * a + 0.02), l - 0.04, a - 0.04, fc=GR[1],
                                       ec="black", lw=0.6))
                cnt += 1
    ax.text(Lm + 0.08, Am / 2, "puertas traseras\n(rampa)", va="center", fontsize=7)
    ax.set_xlim(-0.1, Lm + 0.9)
    ax.set_ylim(-0.1, Am + 0.1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Master L3H2, carros de {TIPOS[4 + k]}: {nmax} por viaje (lugar {npiso}, peso {npeso})", fontsize=9)
    fig.tight_layout()
    f = os.path.join(IMG, f"master_{k}.png")
    fig.savefig(f, dpi=110)
    plt.close(fig)
    return f


ws = wb.create_sheet("Disposicion")
titulo(ws, "ESQUEMAS DE LA DISPOSICIÓN POR PALLET Y DE LA CARGA DE LOS VEHÍCULOS",
       "Dibujados con los datos base de este libro (año 2035, vehículo 1). Si se cambian los datos, los números de "
       "las hojas se recalculan; los esquemas no.")
ws.column_dimensions["A"].width = 2
fila = 4
ws.cell(fila, 2, "Matafuegos manuales en caja").font = F_S
fila += 1
for k in range(4):
    img = XLImage(esquema_caja(k))
    img.width, img.height = 600, 275
    ws.add_image(img, f"{'B' if k % 2 == 0 else 'L'}{fila + (k // 2) * 15}")
fila += 31
ws.cell(fila, 2, "Cilindros vendidos vacíos (a granel, parados, separador por capa)").font = F_S
fila += 1
for k in range(8):
    img = XLImage(esquema_cil(k))
    img.width, img.height = 600, 275
    ws.add_image(img, f"{'B' if k % 2 == 0 else 'L'}{fila + (k // 2) * 15}")
fila += 61
ws.cell(fila, 2, "Vehículo de los pallets").font = F_S
fila += 1
img = XLImage(esquema_camion())
img.width, img.height = 760, 270
ws.add_image(img, f"B{fila}")
fila += 16
ws.cell(fila, 2, "Renault Master L3H2: carros sobre sus ruedas").font = F_S
fila += 1
for k in range(4):
    img = XLImage(esquema_master(k))
    img.width, img.height = 470, 245
    ws.add_image(img, f"{'B' if k % 2 == 0 else 'L'}{fila + (k // 2) * 14}")

# ------------------------------------------------------------------ Fuentes
ws = wb.create_sheet("Fuentes")
titulo(ws, "FUENTES")
cab(ws, 3, ["Dato", "Fuente"])
F = [
    ("Producción anual 2026 a 2035", PROY + " (filas 3 a 10 terminados; 15 a 22 cilindros)"),
    ("Perfiles de estacionalidad", "Dimensionamiento Técnico FLAMA, DATOS-BASE filas 102 a 104 (los mismos del MRP de "
                                   "insumos, hoja ESTACIONALIDAD)"),
    ("Pallet, cajas, cilindros, carros", MP + " (secciones A, B y C) y hojas Volumenes y Geometria Acero"),
    ("Peso cargado de los rodantes", "Ficha técnica Georgia ABC 90 (25, 50, 70 y 100 kg), hoja Mercado de FLAMA_BOM"),
    ("Carrocerías Guajardo y Linares", "https://www.agroads.com.ar/e/carrocerias-y-acoplados-guajardo-y-linares/ ; "
                                       "Sider GyL Full para balancín: https://www.agroads.com.ar/detalle.asp?clasi=957986 ; "
                                       "Sider baranda volcable GyL: https://www.agroads.com.ar/detalle.asp?clasi=782473"),
    ("Capacidad de un balancín sider", "Logística HC, flota: balancín sider de 7,50 × 2,50 m, 12 pallets, 12/14 t "
                                       "(https://logisticashc.com.ar/nosotros/nuestra-flota)"),
    ("Renault Master L3H2: medidas de carga", "Vansdirect, Renault Master dimensions "
                                             "(https://www.vansdirect.co.uk/load-sizing-guide/renault-master-dimensions/); "
                                             "Vanaways, fichas Master H2 (alto 1.894 mm); Renault Malta, Master furgón "
                                             "(https://renault.com.mt/cars/master-xdd-ph1-en/xdd-fourgon.html)"),
    ("Renault Master L3H2: carga útil", "Autocosmos Argentina, Renault Master L3H2 Furgón 2.3: 1.593 kg "
                                        "(https://www.autocosmos.com.ar/)"),
    ("Despacho de rodantes con la Master", "Plano de carros del usuario (rev 6): furgón Renault Master L3H2 y rampa "
                                           "TRAN-IN-240"),
]
for k, (a, b) in enumerate(F):
    celda(ws, 4 + k, 1, a, neg=True)
    celda(ws, 4 + k, 2, b)
    ws.row_dimensions[4 + k].height = 32
anchos(ws, [36, 130])

for w in wb.worksheets:
    w.sheet_properties.pageSetUpPr = None
salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SALIDA, "palletizado_PT.xlsx")
wb.save(salida)
print(salida)
