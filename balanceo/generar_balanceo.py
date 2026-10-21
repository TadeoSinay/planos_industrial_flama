"""Balanceo de materiales y de línea de la planta industrial (salida/Balanceo_Materiales_y_Linea.xlsx).

Hojas: Links (links e IMPORTRANGE) -> Resumen (año, producción vs demanda vs MRP) -> Materiales (MP, semielaborados,
scrap y PT por línea) -> MP_detalle (cascada del MRP: compra contra lo que pide la producción) -> Linea (balanceo de
línea) -> Esquema materiales y Esquema linea (diagramas de bloques que leen las otras hojas).
Todo lo que viene de otro archivo entra por IMPORTRANGE (hoja Links); el resto son fórmulas. El año se elige en
Resumen!C3.
"""
import math
import os
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, "recargas"))
import actualizar_manuales_carros as amc  # noqa: E402
import generar_dim_recargas as g  # noqa: E402

SAL = os.path.join(RAIZ, "salida")
SALIDA = os.path.join(SAL, "Balanceo_Materiales_y_Linea.xlsx")
ARCH = {"mrp": os.path.join(os.path.dirname(RAIZ), "planos_flama-", "salida", "mrp", "FLAMA_MRP.xlsx"),
        "man": os.path.join(SAL, "Aprovechamiento_Manuales.xlsx"),
        "car": os.path.join(SAL, "Aprovechamiento_Carros.xlsx"),
        "rec": os.path.join(SAL, "Aprovechamiento_Recargas_Planta_Industrial.xlsx"),
        "corte": os.path.join(SAL, "Analisis_alternativas_corte_chapa.xlsx")}
FUENTES = [("mrp", "MRP (FLAMA_MRP)", g.PEGAR, "DEMANDA, MANUALES, RODANTES, RECARGAS, REVENDIDOS y POLITICA_STOCK"),
           ("man", "Aprovechamiento Manuales", g.PEGAR, "datos_base, parametros, Plan mensual, Demanda puesto y "
                                                         "Resumen cap. con sobrestock"),
           ("car", "Aprovechamiento Carros", g.PEGAR, "datos_base, parametros, Plan mensual, Demanda por puesto y "
                                                       "Resumen Capacidad"),
           ("rec", "Aprovechamiento Recargas Planta Industrial", g.PEGAR, "datos_base, parametros, Plan mensual, "
                                                                          "Demanda por puesto y Resumen Capacidad"),
           ("corte", "Análisis alternativas corte chapa", g.PEGAR, "Corte (hojas y piezas por hoja) y Piezas (masas "
                                                                    "y discos)")]
ANIOS = list(range(2026, 2036))
Y = "Resumen!$C$3"
YI = f"({Y}-2025)"          # columna del año en un bloque 2026..2035 (1 a 10)
DY = f"({Y}-2026)"          # años desde 2026 (bloques por año hacia abajo)
ACERO = 7.85                # kg/dm³ (BOM, MAT_ACERO)
REND_ALAMBRE = 0.95         # BOM C1: rendimiento de deposición del alambre macizo MAG (ESAB 90-97 %)
REND_PINTURA = 0.95         # MRP MP-31: aprovechamiento del polvo con recuperación (Powder Coating Institute)
# carros: largos por unidad (MRP, constantes MANIJA, CANO_EJE y EJE del proceso de carros 8.1) en mm
MANIJA = (1440, 1520, 1590, 1590)
CANO_EJE = (354, 354, 434, 434)
EJE = (490, 510, 590, 590)

FN = Font(name="Arial", size=10)
FB = Font(name="Arial", size=10, bold=True)
FT = Font(name="Arial", size=12, bold=True)
FS = Font(name="Arial", size=9, italic=True)
FW = Font(name="Arial", size=10, bold=True, color="FFFFFF")
NEGRO = PatternFill("solid", fgColor="000000")
GRIS = PatternFill("solid", fgColor="F2F2F2")
GRIS_O = PatternFill("solid", fgColor="D9D9D9")
fino = Side(style="thin", color="808080")
BORDE = Border(left=fino, right=fino, top=fino, bottom=fino)
CEN = Alignment(horizontal="center", vertical="center", wrap_text=True)
IZQ = Alignment(horizontal="left", vertical="center", wrap_text=True)
DER = Alignment(horizontal="right", vertical="center")
OK, NO = '"✔ Sí"', '"✖ No"'


# ------------------------------------------------------------------ IMPORTRANGE
def _lit(x):
    if isinstance(x, str):
        return "&".join('"' + x[i:i + 250].replace('"', '""') + '"' for i in range(0, max(len(x), 1), 250))
    if isinstance(x, bool):
        return "TRUE" if x else "FALSE"
    return repr(x)


def importrange(ws, r0, c0, link, rango, valores, fmt):
    """Como g.importrange, con textos entre comillas y celdas vacías salteadas (al final arreglar_dummy deja vacías
    las celdas del bloque que no son la primera)."""
    for i, fila in enumerate(valores):
        for j, x in enumerate(fila):
            if i == j == 0:
                f = f'=IFERROR(__xludf.DUMMYFUNCTION("IMPORTRANGE({link},""{rango}"")"),{_lit("" if x is None else x)})'
            elif x is None:
                continue
            else:
                f = f'=IFERROR(__xludf.DUMMYFUNCTION("""COMPUTED_VALUE"""),{_lit(x)})'
            c = ws.cell(r0 + i, c0 + j, f)
            c.font, c.border = FN, BORDE
            if fmt:
                c.number_format = fmt
    # marca vacía justo afuera de la esquina inferior derecha del bloque: Google Sheets arma la hoja del tamaño de lo
    # que tiene contenido y, con el bloque vacío (arreglar_dummy), las fórmulas que leen sus últimas filas o columnas
    # darían «La referencia no existe»
    if valores:
        ws.cell(r0 + len(valores), c0 + max(len(f) for f in valores), '=""')


g.importrange = importrange
LB = g.Links(FUENTES)
SRC = {}


def src(k):
    if k not in SRC:
        SRC[k] = load_workbook(ARCH[k], data_only=True)
    return SRC[k]


class Bloque:
    """Bloque importado en Links. a(i, j) = celda (fila i, columna j del bloque, desde 0)."""

    def __init__(self, clave, hoja, rango, fmt="#,##0.00", titulo=""):
        ws = src(clave)[hoja]
        self.valores = [[c.value for c in fila] for fila in ws[rango]]
        self.r0, self.c0 = LB.imp(clave, f"{hoja}!{rango}", self.valores, fmt, titulo)
        self.nr, self.nc = len(self.valores), len(self.valores[0])

    def a(self, i, j=0):
        return f"Links!${L(self.c0 + j)}${self.r0 + i}"

    def fila(self, i, j0, j1):
        return f"Links!${L(self.c0 + j0)}${self.r0 + i}:${L(self.c0 + j1)}${self.r0 + i}"

    def col(self, j):
        return f"Links!${L(self.c0 + j)}${self.r0}:${L(self.c0 + j)}${self.r0 + self.nr - 1}"

    def anio(self, i, j0=0):
        """Valor del año elegido en una fila con los años 2026..2035 desde la columna j0."""
        return f"INDEX({self.fila(i, j0, j0 + 9)},1,{YI})"

    def abajo(self, j, paso, k):
        """Fila k (desde 1) del bloque del año elegido, en bloques de `paso` filas hacia abajo."""
        return f"INDEX({self.col(j)},{DY}*{paso}+{k})"


# ------------------------------------------------------------------ estilo
def hoja(wb, nombre, anchos):
    ws = wb.create_sheet(nombre)
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 90
    for k, a in enumerate(anchos):
        ws.column_dimensions[L(k + 1)].width = a
    return ws


def c(ws, r, col, v, fmt=None, neg=False, dato=False, gris=False, izq=None, borde=True):
    x = ws.cell(r, col, v)
    x.font = FB if neg else FN
    if borde:
        x.border = BORDE
    if fmt:
        x.number_format = fmt
    if dato:
        x.fill = PatternFill("solid", fgColor="FFF2CC")
    elif gris:
        x.fill = GRIS
    texto = isinstance(v, str) and not v.startswith("=")
    x.alignment = IZQ if (izq if izq is not None else texto) else (CEN if fmt is None else DER)
    return x


def cab(ws, r, textos, c0=1):
    for k, t in enumerate(textos):
        x = ws.cell(r, c0 + k, t)
        x.font, x.fill, x.alignment, x.border = FW, NEGRO, CEN, BORDE
    ws.row_dimensions[r].height = 30


def tit(ws, r, t, col=1):
    ws.cell(r, col, t).font = FT


def sub(ws, r, t, n, col=1):
    for k in range(n):
        x = ws.cell(r, col + k)
        x.fill = GRIS_O
        x.border = BORDE
    x = ws.cell(r, col, t)
    x.font = FB


def nota(ws, r, t, col=1):
    x = ws.cell(r, col, t)
    x.font = FS
    x.alignment = Alignment(horizontal="left", vertical="center")


def sino(cond):
    return f"=IF({cond},{OK},{NO})"


def pinta_checks(ws, rango):
    ws.conditional_formatting.add(rango, FormulaRule(formula=[f'LEFT({rango.split(":")[0].replace("$", "")},1)="✖"'],
                                                     fill=PatternFill("solid", fgColor="F8CBAD"),
                                                     font=Font(name="Arial", bold=True, color="9C0006")))
    ws.conditional_formatting.add(rango, FormulaRule(formula=[f'LEFT({rango.split(":")[0].replace("$", "")},1)="✔"'],
                                                     fill=PatternFill("solid", fgColor="C6EFCE"),
                                                     font=Font(name="Arial", color="006100")))


# ------------------------------------------------------------------ datos de las fuentes
MAN = ["ABC 1 kg", "ABC 2,5 kg", "ABC 5 kg", "ABC 10 kg"]
ROD = ["ABC 25 kg", "ABC 50 kg", "ABC 70 kg", "ABC 100 kg"]
TIPOS_REC = ["ABC 1 kg", "ABC 2,5 kg", "ABC 5 kg", "ABC 10 kg", "Agua 10 l", "AFFF 10 l", "AFFF 50 l s/ruedas",
             "BC 5 kg", "Sales K 6 l", "CO₂ 2 kg", "CO₂ 5 kg", "HCFC/HFC 5 kg", "Clase D 9 l", "ABC 25 kg s/ruedas",
             "ABC 50 kg s/ruedas", "ABC 70 kg s/ruedas", "ABC 100 kg s/ruedas"]
REV = ["Agua 10 l", "AFFF 10 l", "AFFF 50 l", "BC 5 kg", "Clase K 6 l", "CO₂ 2 kg", "CO₂ 5 kg", "HCFC 5 kg",
       "Clase D 9 l"]


def ultima(ws, col=2, desde=16):
    r = desde
    while ws.cell(r + 1, col).value:
        r += 1
    return r


def familia(cod):
    """Familia de cada ítem del MRP (para agrupar la materia prima)."""
    base = cod.split("/")[0]
    fam = {"MP-01": "Chapa en hojas", "MP-02": "Chapa en hojas", "MP-03": "Chapa en hojas", "MP-04": "Chapa en hojas",
           "MP-11": "Chapa en hojas", "MP-12": "Chapa en hojas",
           **{k: "Fleje en rollos" for k in ("MP-05", "MP-06", "MP-07", "MP-08", "MP-09", "MP-10", "MP-13", "MP-14")},
           "MP-15": "Casquetes y cuplas", "MP-16": "Casquetes y cuplas", "MP-17": "Casquetes y cuplas",
           "MP-20": "Casquetes y cuplas", "MP-21": "Casquetes y cuplas",
           "MP-18": "Asientos de válvula", "MP-19": "Asientos de válvula",
           "MP-66": "Caños y barras", "MP-67": "Caños y barras", "MP-68": "Caños y barras", "MP-69": "Caños y barras",
           "MP-23": "Soldadura: alambre", "MP-24": "Soldadura: alambre",
           "MP-25": "Soldadura: gases", "MP-26": "Soldadura: gases", "MP-29": "Soldadura: electrodo TIG",
           "MP-28": "Granalla", "MP-31": "Pintura", "MP-65": "Pintura", "MP-96": "Pintura (servicio)",
           "MP-33": "Agente: polvo", "MP-33B": "Agente: polvo", "MP-35": "Agente: polvo", "MP-36": "Agente: polvo",
           "MP-37": "Agente: CO₂ y limpio", "MP-38": "Agente: CO₂ y limpio",
           "MP-40": "Agente: líquidos", "MP-41": "Agente: líquidos", "MP-34": "Nitrógeno",
           "MP-92": "Abrasivos y corte", "MP-27": "Abrasivos y corte", "MP-93": "Abrasivos y corte",
           "MP-94": "Abrasivos y corte", "MP-95": "Abrasivos y corte"}
    if base in fam:
        return fam[base]
    if base.startswith("RV-"):
        return "Equipos comprados"
    n = int(base[3:5]) if base[3:5].isdigit() else 0
    if base in ("MP-42", "MP-43", "MP-44", "MP-45", "MP-46", "MP-47", "MP-48", "MP-49", "MP-50", "MP-52", "MP-54",
                "MP-55", "MP-62", "MP-70", "MP-71", "MP-86", "MP-87"):
        return "Componentes comprados"
    if 56 <= n <= 60 or n == 90 or n in (51, 53):
        return "Identificación y embalaje"
    return "Identificación y embalaje" if n >= 72 else "Componentes comprados"


# ------------------------------------------------------------------ libro
class Libro:
    def __init__(self):
        mrp = src("mrp")
        self.mb = {}
        # MRP: DEMANDA (D01..D47) y las cuatro líneas (código, material, UM, destino, consumos, años)
        self.m_dem = Bloque("mrp", "DEMANDA", "C4:M50", "#,##0.00", "demanda por producto (D01 a D47)")
        for hoja_, ncons in (("MANUALES", 8), ("RODANTES", 8), ("RECARGAS", 18), ("REVENDIDOS", 9)):
            ws = mrp[hoja_]
            r1 = ultima(ws)
            j1 = 5 + ncons + 10
            self.mb[hoja_] = (Bloque("mrp", hoja_, f"B16:{L(j1)}{r1}", "#,##0.0000", "consumo por unidad y compra "
                                     "por año"), ncons)
        ws = mrp["POLITICA_STOCK"]
        self.m_pol = Bloque("mrp", "POLITICA_STOCK", f"B5:B{ultima(ws, 2, 5)}", None, "código")
        self.m_pol2 = Bloque("mrp", "POLITICA_STOCK", f"O5:P{ultima(ws, 2, 5)}", None, "unidad de compra y contenido")
        # Aprovechamiento Manuales
        self.a_mdb = Bloque("man", "datos_base", "B2:K29", "#,##0.0", "producción y proyecciones")
        self.a_mplan = Bloque("man", "Plan mensual", "D1:P109", "#,##0.0", "plan mensual por año (11 filas por año)")
        self.a_mpar = Bloque("man", "parametros_manuales", "K19:K44", "#,##0.00", "tiempo tipo (s/u)")
        self.a_mh = Bloque("man", "parametros_manuales", "B7:B7", "#,##0", "horas productivas por mes (1 turno)")
        self.a_mdp = Bloque("man", "Demanda puesto con sobrestock", "N1:N279", "#,##0.0",
                            "unidades por puesto y año (28 filas por año)")
        self.a_mres = Bloque("man", "Resumen cap. con sobrestock", "B2:K85", "#,##0.00",
                             "aprovechamiento, máquinas y turnos")
        # Aprovechamiento Carros
        self.a_cdb = Bloque("car", "datos_base", "B2:K12", "#,##0.0", "proyección de carros y cilindros")
        self.a_cplan = Bloque("car", "Plan mensual", "D1:P109", "#,##0.0", "plan mensual por año (11 filas por año)")
        self.a_cpar = Bloque("car", "parametros_carros", "I19:I36", "#,##0.00", "tiempo ponderado (min/u)")
        self.a_ch = Bloque("car", "parametros_carros", "B7:B7", "#,##0", "horas productivas por mes (1 turno)")
        self.a_cdp = Bloque("car", "Demanda por puesto", "N1:N199", "#,##0.0", "horas por puesto y año (20 filas)")
        self.a_cres = Bloque("car", "Resumen Capacidad", "B2:K61", "#,##0.00", "aprovechamiento, máquinas y turnos")
        # Aprovechamiento Recargas Planta Industrial
        self.a_rdb = Bloque("rec", "datos_base", "B2:K18", "#,##0.0", "recargas por tipo")
        self.a_rplan = Bloque("rec", "Plan mensual", "D1:P318", "#,##0.0", "plan mensual por año (32 filas por año)")
        self.a_rpar = Bloque("rec", "parametros_recargas", "N76:N98", "#,##0", "tiempo tipo (s/u)")
        self.a_rh = Bloque("rec", "parametros_recargas", "B6:B6", "#,##0", "horas productivas por mes (1 turno)")
        self.a_rdp = Bloque("rec", "Demanda por puesto", "N1:N312", "#,##0.0", "unidades por puesto y año (32 filas)")
        self.a_rres = Bloque("rec", "Resumen Capacidad", "B2:K88", "#,##0.00", "aprovechamiento, máquinas y turnos")
        # corte
        self.k_corte = Bloque("corte", "Corte", "B6:J14", "#,##0.000", "hojas, franjas, piezas por hoja, aprovech.")
        self.k_pz = Bloque("corte", "Piezas", "D6:H13", "#,##0.000", "cuerpos: Ø, espesor, alto, desarrollo, masa")
        self.k_dz = Bloque("corte", "Piezas", "D18:L25", "#,##0.000", "discos: espesor ... D0 adoptado")
        self.nombres = {
            "man": [v[0] for v in src("man")["parametros_manuales"]["B19:B44"]],
            "car": [v[0] for v in src("car")["parametros_carros"]["B19:B36"]],
            "rec": [v[0] for v in src("rec")["parametros_recargas"]["B76:B98"]],
            "man_r": [v[0] for v in src("man")["Resumen cap. con sobrestock"]["L2:L27"]],
            "car_r": [v[0] for v in src("car")["Resumen Capacidad"]["L2:L19"]],
            "rec_r": [v[0] for v in src("rec")["parametros_recargas"]["D76:D98"]],
        }
        self.nombres = {k: [x.value for x in v] for k, v in self.nombres.items()}
        self.wb = Workbook()
        self.wb.remove(self.wb.active)
        self.res = {}       # (línea, i) -> fila de Resumen
        self.mat = {}       # claves -> celda de Materiales
        self.lin = {}       # línea -> datos de Linea

    # -------- Resumen
    def resumen(self):
        ws = hoja(self.wb, "Resumen", [12, 26, 14, 14, 13, 12, 13, 14, 15, 14])
        tit(ws, 1, "BALANCEO DE MATERIALES Y DE LÍNEA — planta industrial FLAMA")
        nota(ws, 2, "Elegí el año en C3. Todo sale de las hojas que llegan por IMPORTRANGE (hoja Links).")
        c(ws, 3, 1, "Año", neg=True)
        c(ws, 3, 3, 2035, "0", dato=True)
        dv = DataValidation(type="list", formula1='"' + ",".join(str(a) for a in ANIOS) + '"', allow_blank=False)
        ws.add_data_validation(dv)
        dv.add("C3")
        sub(ws, 5, "1) Producción contra demanda y contra lo que compra el MRP (año elegido)", 10)
        cab(ws, 6, ["Línea", "Producto", "Demanda (Proyecciones)", "Producción (Aprovechamiento)", "Sobrestock (u)",
                    "Sobrestock (%)", "¿Producción ≥ demanda?", "El MRP compra para (u)",
                    "¿El MRP cubre la producción?", "MRP − producción (u)"])
        r = 7
        filas = []
        # (línea, producto, demanda, producción, fila de DEMANDA del MRP)
        for i, n in enumerate(MAN + [f"Cilindro {x} vacío" for x in MAN]):
            d = self.a_mdb.anio(17 + i) if i < 4 else self.a_mdb.anio(24 + i - 4)
            p = self.a_mplan.abajo(12, 11, 2 + i)
            filas.append(("MANUALES", f"Matafuego {n}" if i < 4 else n, d, p, 4 + i))
        for i, n in enumerate(ROD + [f"Cilindro {x} vacío" for x in ROD]):
            d = self.a_cdb.anio(i) if i < 4 else self.a_cdb.anio(7 + i - 4)
            p = self.a_cplan.abajo(12, 11, 2 + i)
            filas.append(("RODANTES", f"Carro {n}" if i < 4 else n, d, p, 12 + i))
        for i, n in enumerate(TIPOS_REC):
            filas.append(("RECARGAS", f"Recarga {n}", self.a_rdb.anio(i), self.a_rplan.abajo(12, 32, 2 + i), 20 + i))
        for k, (lin, prod, d, p, rd) in enumerate(filas):
            c(ws, r, 1, lin)
            c(ws, r, 2, prod)
            c(ws, r, 3, "=" + d, "#,##0.0")
            c(ws, r, 4, "=" + p, "#,##0.0")
            c(ws, r, 5, f"=D{r}-C{r}", "#,##0.0")
            c(ws, r, 6, f"=IF(C{r}=0,0,D{r}/C{r}-1)", "0.0%")
            c(ws, r, 7, sino(f"ROUND(D{r}-C{r},1)>=0"))
            c(ws, r, 8, "=" + self.m_dem.anio(rd, 1), "#,##0.0")
            c(ws, r, 9, sino(f"ROUND(H{r}-D{r},1)>=0"))
            c(ws, r, 10, f"=H{r}-D{r}", "#,##0.0")
            self.res[(lin, k)] = r
            r += 1
        self.r_res = (7, r - 1)
        pinta_checks(ws, f"G7:G{r - 1}")
        pinta_checks(ws, f"I7:I{r - 1}")
        # totales por línea
        r += 1
        sub(ws, r, "Totales por línea (año elegido)", 10)
        r += 1
        cab(ws, r, ["Línea", "", "Demanda", "Producción", "Sobrestock (u)", "Sobrestock (%)",
                    "Productos con producción < demanda", "MRP compra para", "Productos que el MRP no cubre",
                    "MRP − producción"])
        r += 1
        self.tot = {}
        for lin in ("MANUALES", "RODANTES", "RECARGAS"):
            a, b = 7, self.r_res[1]
            c(ws, r, 1, lin, neg=True)
            for col, letra in ((3, "C"), (4, "D"), (5, "E"), (8, "H"), (10, "J")):
                c(ws, r, col, f'=SUMIF($A${a}:$A${b},$A{r},{letra}${a}:{letra}${b})', "#,##0", neg=True)
            c(ws, r, 6, f"=IF(C{r}=0,0,D{r}/C{r}-1)", "0.0%", neg=True)
            c(ws, r, 7, f'=COUNTIFS($A${a}:$A${b},$A{r},$G${a}:$G${b},{NO})', "0", neg=True)
            c(ws, r, 9, f'=COUNTIFS($A${a}:$A${b},$A{r},$I${a}:$I${b},{NO})', "0", neg=True)
            self.tot[lin] = r
            r += 1
        # todos los años
        r += 1
        sub(ws, r, "2) Todos los años: sobrestock y checks por línea", 12)
        r += 1
        cab(ws, r, ["Línea", "Indicador"] + [str(a) for a in ANIOS])
        for k in range(10):
            ws.column_dimensions[L(3 + k)].width = max(ws.column_dimensions[L(3 + k)].width or 0, 12)
        r += 1
        r_ini = r
        for lin, plan, paso, n, dem in (("MANUALES", self.a_mplan, 11, 8, None), ("RODANTES", self.a_cplan, 11, 8, None),
                                        ("RECARGAS", self.a_rplan, 32, 17, None)):
            for ind in ("Producción (u)", "Demanda (u)", "Sobrestock (%)", "Productos con producción < demanda",
                        "Productos que el MRP no cubre"):
                c(ws, r, 1, lin, neg=ind.startswith("Producción"))
                c(ws, r, 2, ind)
                for k in range(10):
                    col = L(plan.c0 + 12)
                    p0, p1 = plan.r0 + paso * k + 1, plan.r0 + paso * k + n
                    prng = f"Links!${col}${p0}:${col}${p1}"
                    if lin == "MANUALES":
                        drng = [(self.a_mdb, 17, 20, 0), (self.a_mdb, 24, 27, 4)]
                        m0 = 4
                    elif lin == "RODANTES":
                        drng = [(self.a_cdb, 0, 3, 0), (self.a_cdb, 7, 10, 4)]
                        m0 = 12
                    else:
                        drng = [(self.a_rdb, 0, 16, 0)]
                        m0 = 20
                    dcol = L(self.a_mdb.c0 + k)
                    dsum = "+".join(f"SUM(Links!${dcol}${b.r0 + i0}:${dcol}${b.r0 + i1})" for b, i0, i1, _ in drng)
                    mcol = L(self.m_dem.c0 + 1 + k)
                    mrng = f"Links!${mcol}${self.m_dem.r0 + m0}:${mcol}${self.m_dem.r0 + m0 + n - 1}"
                    if ind == "Producción (u)":
                        f = f"=SUM({prng})"
                    elif ind == "Demanda (u)":
                        f = f"={dsum}"
                    elif ind == "Sobrestock (%)":
                        f = f"=IF({L(3 + k)}{r - 1}=0,0,{L(3 + k)}{r - 2}/{L(3 + k)}{r - 1}-1)"
                    elif ind.startswith("Productos con"):
                        partes = []
                        for b, i0, i1, off in drng:
                            pr = f"Links!${col}${p0 + off}:${col}${p0 + off + i1 - i0}"
                            dr = f"Links!${dcol}${b.r0 + i0}:${dcol}${b.r0 + i1}"
                            partes.append(f"SUMPRODUCT(--(ROUND({pr}-{dr},1)<0))")
                        f = "=" + "+".join(partes)
                    else:
                        f = f"=SUMPRODUCT(--(ROUND({mrng}-{prng},1)<0))"
                    c(ws, r, 3 + k, f, "0.0%" if ind == "Sobrestock (%)" else "#,##0")
                r += 1
        for rr in range(r_ini, r):
            if ws.cell(rr, 2).value.startswith("Productos"):
                ws.conditional_formatting.add(f"C{rr}:L{rr}", FormulaRule(
                    formula=[f"C{rr}>0"], fill=PatternFill("solid", fgColor="F8CBAD")))
                ws.conditional_formatting.add(f"C{rr}:L{rr}", FormulaRule(
                    formula=[f"C{rr}=0"], fill=PatternFill("solid", fgColor="C6EFCE")))
        r += 1
        nota(ws, r, "Demanda = Proyecciones (manuales y carros: datos_base de cada Aprovechamiento; recargas: "
                    "Proyecciones × parte de la planta industrial). Producción = Plan mensual de cada Aprovechamiento "
                    "(incluye sustitutos). MRP = DEMANDA del MRP, con la que compra la materia prima.")
        nota(ws, r + 1, "Revendidos no se fabrican: la compra del MRP es el producto terminado (hoja Materiales).")
        ws.freeze_panes = "C7"

    # -------- MP_detalle (cascada del MRP)
    def mp_detalle(self):
        ws = hoja(self.wb, "MP_detalle", [12, 22, 13, 46, 6, 24, 14, 14, 13, 11, 11, 12, 10, 13])
        tit(ws, 1, "CASCADA DEL MRP: compra de cada material contra lo que pide la producción (año elegido)")
        nota(ws, 2, "Necesario = consumo por unidad del MRP × producción de cada producto (Resumen). Si el MRP compra "
                    "menos de lo necesario, el balance no cierra para esa producción.")
        r = 4
        self.det = {}
        prods = {"MANUALES": [("MANUALES", k) for k in range(8)], "RODANTES": [("RODANTES", 8 + k) for k in range(8)],
                 "RECARGAS": [("RECARGAS", 16 + k) for k in range(17)], "REVENDIDOS": None}
        share = {"MANUALES": 1, "RODANTES": 1, "RECARGAS": 2, "REVENDIDOS": 1}   # DEMANDA: D02 nuevos, D03 recargas
        for lin in ("MANUALES", "RODANTES", "RECARGAS", "REVENDIDOS"):
            b, n = self.mb[lin]
            sub(ws, r, lin, 14)
            r += 1
            # vector de producción del año (mismo orden que las columnas del MRP)
            c(ws, r, 1, "Producción", neg=True)
            c(ws, r, 2, "(mismo orden que el MRP) →", izq=True)
            for k in range(n):
                if prods[lin] is None:                       # revendidos: lo compra el MRP
                    v = "=" + self.m_dem.anio(38 + k, 1)
                elif k < len(prods[lin]):
                    v = f"=Resumen!$D${self.res[prods[lin][k]]}"
                else:                                        # kit de sustitutos: lo del MRP
                    v = "=" + self.m_dem.anio(37, 1)
                c(ws, r, 15 + k, v, "#,##0.0", gris=True)
            rp = r
            r += 1
            cab(ws, r, ["Línea", "Familia", "Código", "Material", "UM", "Formato de compra", "Compra MRP",
                        "Necesario para la producción", "Compra − necesario", "¿Cubre?", "Contenido de la unidad de "
                        "compra", "Unidades de compra necesarias", "kg por UM", "kg necesarios"])
            r += 1
            r0 = r
            for i in range(b.nr):
                cod = b.valores[i][0]
                if not cod:
                    continue
                c(ws, r, 1, lin)
                c(ws, r, 2, familia(cod))
                c(ws, r, 3, "=" + b.a(i, 0))
                c(ws, r, 4, "=" + b.a(i, 1))
                c(ws, r, 5, "=" + b.a(i, 2))
                c(ws, r, 6, f'=IFERROR(INDEX({self.m_pol2.col(0)},MATCH(C{r},{self.m_pol.col(0)},0)),"")', izq=True)
                c(ws, r, 7, "=" + b.anio(i, 4 + n), "#,##0.0")
                dest = b.a(i, 3)
                sh = self.m_dem.anio(share[lin], 1)
                fac = f'IF({dest}="CABA",{sh},IF({dest}="PBA",1-{sh},1))'
                c(ws, r, 8, f"=SUMPRODUCT({b.fila(i, 4, 3 + n)},$O${rp}:${L(14 + n)}${rp})*{fac}", "#,##0.0")
                c(ws, r, 9, f"=G{r}-H{r}", "#,##0.0")
                c(ws, r, 10, sino(f"ROUND(G{r}-H{r},1)>=0"))
                c(ws, r, 11, f'=IFERROR(INDEX({self.m_pol2.col(1)},MATCH(C{r},{self.m_pol.col(0)},0)),1)', "#,##0.0")
                c(ws, r, 12, f"=IF(K{r}>0,H{r}/K{r},0)", "#,##0.0")
                c(ws, r, 13, self.kg_um(cod, r), '#,##0.000;-#,##0.000;""')
                c(ws, r, 14, f"=H{r}*M{r}", '#,##0;-#,##0;""')
                self.det[cod, lin] = r
                r += 1
            pinta_checks(ws, f"J{r0}:J{r - 1}")
            self.det[lin] = (r0, r - 1)
            r += 1
        ws.freeze_panes = "E4"
        for k in range(18):
            ws.column_dimensions[L(15 + k)].width = 9

    def kg_um(self, cod, r):
        """kg por unidad de medida: hojas (lado × lado × espesor × 7,85) y todo lo que se mide en kg."""
        hojas = {"MP-01": 0, "MP-02": 1, "MP-03": 2, "MP-04": 3, "MP-11": 4, "MP-12": 6}
        if cod in hojas:
            i = hojas[cod]
            return (f"={self.k_corte.a(i, 0)}*{self.k_corte.a(i, 1)}*{self.k_pz.a(i, 1)}*{ACERO}/1000000")
        return f'=IF(E{r}="kg",1,0)'

    # -------- Materiales
    def materiales(self):
        ws = hoja(self.wb, "Materiales", [40, 26, 13, 13, 13, 13, 13, 15])
        tit(ws, 1, "BALANCE DE MATERIALES (año elegido en Resumen)")
        nota(ws, 2, "1) materia prima que entra · 2) semielaborados en proceso · 3) scrap, desechos y mermas · "
                    "4) producto terminado. Cantidades = lo que pide la producción del año (MP_detalle).")
        r = 4
        m = self.mat
        D = "MP_detalle"

        def nec(lin, fam, col="H"):
            r0, r1 = self.det[lin]
            return f"SUMIFS({D}!${col}${r0}:${col}${r1},{D}!$B${r0}:$B${r1},\"{fam}\")"

        def nec_cod(lin, cods, col="H"):
            return "+".join(f"{D}!${col}${self.det[k, lin]}" for k in cods if (k, lin) in self.det) or "0"

        def bloque_mp(lin, fams):
            nonlocal r
            sub(ws, r, "1) Materia prima que entra", 8)
            r += 1
            cab(ws, r, ["Familia", "Formato de compra", "Cantidad", "UM", "Unidades de compra", "kg", "", ""])
            r += 1
            for fam, um in fams:
                r0, r1 = self.det[lin]
                c(ws, r, 1, fam)
                c(ws, r, 2, f'=IFERROR(INDEX({D}!$F${r0}:$F${r1},MATCH("{fam}",{D}!$B${r0}:$B${r1},0)),"")'
                            + (' & " (varios)"' if fam in ("Componentes comprados", "Identificación y embalaje",
                                                          "Equipos comprados") else ""), izq=True)
                c(ws, r, 3, "=" + nec(lin, fam), "#,##0.0")
                c(ws, r, 4, um)
                c(ws, r, 5, "=" + nec(lin, fam, "L"), "#,##0.0")
                c(ws, r, 6, "=" + nec(lin, fam, "N"), '#,##0;-#,##0;""')
                m[lin, "mp", fam] = r
                r += 1
            r += 1

        def kg_disco(i, cupula):
            """kg del disco (cúpula o fondo) del formato i (0 = 1 kg) desde Piezas: π D0² / 4 × e × 7,85."""
            k = 2 * i + (0 if cupula else 1)
            return f"(PI()*{self.k_dz.a(k, 8)}^2/4*{self.k_dz.a(k, 0)}*{ACERO}/1000000)"

        # ================= MANUALES
        sub(ws, r, "LÍNEA DE MANUALES (1 a 10 kg)", 8)
        ws.cell(r, 1).font = FT
        r += 1
        bloque_mp("MANUALES", [("Chapa en hojas", "hojas"), ("Fleje en rollos", "kg"), ("Asientos de válvula", "u"),
                               ("Soldadura: alambre", "kg"), ("Soldadura: gases", "m³"),
                               ("Soldadura: electrodo TIG", "u"), ("Granalla", "kg"), ("Pintura", "kg"),
                               ("Agente: polvo", "kg"), ("Nitrógeno", "m³"), ("Componentes comprados", "u"),
                               ("Identificación y embalaje", "u")])
        sub(ws, r, "2) Semielaborados en proceso", 8)
        r += 1
        cab(ws, r, ["Etapa", "Formato"] + MAN + ["Total (u)", "kg de acero"])
        r += 1
        P = {i: f"Resumen!$D${self.res[('MANUALES', i)]}" for i in range(8)}
        rec = [f"({P[i]}+{P[4 + i]})" for i in range(4)]
        kgc = [self.k_pz.a(i, 4) for i in range(4)]
        kgd = [f"({kg_disco(i, True)}+{kg_disco(i, False)})" for i in range(4)]
        se = [("Planchuela de cuerpo cortada", "Rectángulo de chapa: desarrollo × alto (Piezas)", 1, "c"),
              ("Discos de cúpula y fondo", "Disco plano Ø D0 desde fleje (2 por recipiente)", 2, "d"),
              ("Casquetes embutidos (cúpula numerada con cuello, fondo)", "Casquete embutido", 2, "d"),
              ("Virola cilindrada y soldada", "Tubo con costura longitudinal", 1, "c"),
              ("Recipiente soldado (PH, secado, granallado)", "Recipiente cerrado sin pintar", 1, "cd"),
              ("Recipiente pintado", "Cilindro pintado rojo", 1, "cd")]
        for etapa, fmt, mult, kg in se:
            c(ws, r, 1, etapa)
            c(ws, r, 2, fmt)
            for i in range(4):
                c(ws, r, 3 + i, f"={mult}*{rec[i]}", "#,##0")
            c(ws, r, 7, f"=SUM(C{r}:F{r})", "#,##0", neg=True)
            partes = []
            for i in range(4):
                pz = {"c": kgc[i], "d": kgd[i], "cd": f"({kgc[i]}+{kgd[i]})"}[kg]
                partes.append(f"{rec[i]}*{pz}")
            c(ws, r, 8, "=" + "+".join(partes), "#,##0")
            m["MANUALES", "se", etapa] = r
            r += 1
        c(ws, r, 1, "Matafuego cargado y presurizado (antes de etiquetar)")
        c(ws, r, 2, "Recipiente + válvula + polvo + N₂")
        for i in range(4):
            c(ws, r, 3 + i, f"={P[i]}", "#,##0")
        c(ws, r, 7, f"=SUM(C{r}:F{r})", "#,##0", neg=True)
        c(ws, r, 8, "")
        r += 2
        r_cuerpo = m["MANUALES", "se", "Planchuela de cuerpo cortada"]
        r_disco = m["MANUALES", "se", "Discos de cúpula y fondo"]
        self.scrap(ws, r, "MANUALES", [
            ("Recortes de hoja", "Corte en guillotinas", f"={nec('MANUALES', 'Chapa en hojas', 'N')}-H{r_cuerpo}",
             "kg", "Sí: chatarra", "Contenedor de chatarra (playa de scrap)"),
            ("Esqueleto de fleje y despunte", "Corte de disco y embutido",
             f"={nec('MANUALES', 'Fleje en rollos', 'N')}-H{r_disco}", "kg", "Sí: chatarra", "Contenedor de chatarra"),
            ("Salpicadura de soldadura", "Soldaduras MAG", f"={nec('MANUALES', 'Soldadura: alambre')}*{1 - REND_ALAMBRE}",
             "kg", "No", f"Residuo ({1 - REND_ALAMBRE:.0%} del alambre: BOM, rendimiento ESAB)"),
            ("Gas de protección y argón", "Soldaduras MAG y TIG", f"={nec('MANUALES', 'Soldadura: gases')}", "m³",
             "No (se consume)", "Merma: queda en el ambiente de soldadura"),
            ("Electrodo de tungsteno gastado", "Soldadura TIG del 1 kg",
             f"={nec('MANUALES', 'Soldadura: electrodo TIG')}", "u", "No", "Residuo (criterio a medir: MRP)"),
            ("Granalla gastada y óxido", "Granallado", f"={nec('MANUALES', 'Granalla')}", "kg", "No",
             "Residuo del colector de la granalladora"),
            ("Polvo de pintura no recuperado", "Cabina de pintura",
             f"={nec('MANUALES', 'Pintura')}*{1 - REND_PINTURA}", "kg", "No",
             f"Residuo ({1 - REND_PINTURA:.0%}: el resto se recupera en la cabina)"),
            ("Polvo ABC de carga", "Carga de polvo", "=0", "kg", "—", "El proceso de manuales no agrega merma (MRP)")])
        r = self.r_scrap_fin
        self.pt(ws, r, "MANUALES", [(f"Matafuego {n}", "Embalado en caja, en pallet", f"={P[i]}") for i, n in
                                    enumerate(MAN)] +
                [(f"Cilindro {n} vacío", "Cilindro pintado, en pallet", f"={P[4 + i]}") for i, n in enumerate(MAN)])
        r = self.r_pt_fin
        self.acero(ws, r, "MANUALES", f"={nec('MANUALES', 'Chapa en hojas', 'N')}+{nec('MANUALES', 'Fleje en rollos', 'N')}",
                   f"=H{m['MANUALES', 'se', 'Recipiente pintado']}",
                   f"=C{m['MANUALES', 'scrap', 0]}+C{m['MANUALES', 'scrap', 1]}")
        r = self.r_acero_fin

        # ================= RODANTES
        sub(ws, r, "LÍNEA DE CARROS (25 a 100 kg)", 8)
        ws.cell(r, 1).font = FT
        r += 1
        bloque_mp("RODANTES", [("Chapa en hojas", "hojas"), ("Casquetes y cuplas", "u"), ("Caños y barras", "barras"),
                               ("Soldadura: alambre", "kg"), ("Soldadura: gases", "m³"), ("Abrasivos y corte", "u"),
                               ("Pintura (servicio)", "servicio"), ("Agente: polvo", "kg"), ("Nitrógeno", "m³"),
                               ("Componentes comprados", "u"), ("Identificación y embalaje", "u")])
        sub(ws, r, "2) Semielaborados en proceso", 8)
        r += 1
        cab(ws, r, ["Etapa", "Formato"] + ROD + ["Total (u)", "kg de acero"])
        r += 1
        P = {i: f"Resumen!$D${self.res[('RODANTES', 8 + i)]}" for i in range(8)}
        rec = [f"({P[i]}+{P[4 + i]})" for i in range(4)]
        kgc = [self.k_pz.a(4 + i, 4) for i in range(4)]
        se = [("Planchuela de cuerpo cortada", "Rectángulo de chapa LAC: desarrollo × alto (Piezas)", "rec"),
              ("Virola rolada, punteada y soldada", "Tubo con costura longitudinal", "rec"),
              ("Recipiente armado (cuerpo + 2 casquetes + cupla)", "Recipiente cerrado sin pintar", "rec"),
              ("Recipiente probado y secado", "Recipiente probado (PH)", "rec"),
              ("Recipiente pintado (tercerizado: sale y vuelve)", "Cilindro pintado rojo", "rec"),
              ("Carro armado y cargado", "Recipiente + carro + manga + polvo + N₂", "term")]
        for etapa, fmt, base in se:
            c(ws, r, 1, etapa)
            c(ws, r, 2, fmt)
            for i in range(4):
                c(ws, r, 3 + i, "=" + (rec[i] if base == "rec" else P[i]), "#,##0")
            c(ws, r, 7, f"=SUM(C{r}:F{r})", "#,##0", neg=True)
            c(ws, r, 8, "=" + "+".join(f"{rec[i]}*{kgc[i]}" for i in range(4)) if base == "rec" else "", "#,##0")
            m["RODANTES", "se", etapa] = r
            r += 1
        r += 1
        r_cuerpo = m["RODANTES", "se", "Planchuela de cuerpo cortada"]
        metros = "+".join(f"{P[i]}*({MANIJA[i]}+{CANO_EJE[i]}+{EJE[i]})/1000" for i in range(4))
        self.scrap(ws, r, "RODANTES", [
            ("Recortes de hoja", "Corte en guillotinas", f"={nec('RODANTES', 'Chapa en hojas', 'N')}-H{r_cuerpo}",
             "kg", "Sí: chatarra", "Contenedor de chatarra (playa de scrap)"),
            ("Recortes de caño y barra", "Fabricación de accesorios (sensitiva)",
             f"=({nec_cod('RODANTES', ['MP-66', 'MP-67', 'MP-69'])})*6+({nec_cod('RODANTES', ['MP-68'])})*4-({metros})",
             "m", "Sí: chatarra", "Contenedor de chatarra"),
            ("Salpicadura de soldadura", "Soldaduras MAG", f"={nec('RODANTES', 'Soldadura: alambre')}*{1 - REND_ALAMBRE}",
             "kg", "No", f"Residuo ({1 - REND_ALAMBRE:.0%} del alambre: BOM)"),
            ("Gas de protección", "Soldaduras MAG", f"={nec('RODANTES', 'Soldadura: gases')}", "m³", "No (se consume)",
             "Merma"),
            ("Discos de corte y flap, mechas, aerosoles gastados", "Corte y terminación de accesorios",
             f"={nec('RODANTES', 'Abrasivos y corte')}", "u", "No", "Residuo"),
            ("Pintura", "Tercerizada", "=0", "kg", "—", "La merma queda en el pintor de carros")])
        r = self.r_scrap_fin
        self.pt(ws, r, "RODANTES", [(f"Carro {n}", "Carro armado, film, en pallet", f"={P[i]}") for i, n in
                                    enumerate(ROD)] +
                [(f"Cilindro {n} vacío", "Cilindro pintado, en pallet", f"={P[4 + i]}") for i, n in enumerate(ROD)])
        r = self.r_pt_fin
        self.acero(ws, r, "RODANTES", f"={nec('RODANTES', 'Chapa en hojas', 'N')}",
                   f"=H{m['RODANTES', 'se', 'Planchuela de cuerpo cortada']}", f"=C{m['RODANTES', 'scrap', 0]}",
                   "Solo la chapa del cuerpo: los casquetes y la cupla se compran terminados")
        r = self.r_acero_fin

        # ================= RECARGAS
        sub(ws, r, "LÍNEA DE RECARGAS (planta industrial)", 8)
        ws.cell(r, 1).font = FT
        r += 1
        bloque_mp("RECARGAS", [("Agente: polvo", "kg"), ("Agente: CO₂ y limpio", "kg"), ("Agente: líquidos", "L"),
                               ("Nitrógeno", "m³"), ("Pintura", "L"), ("Componentes comprados", "u"),
                               ("Identificación y embalaje", "u")])
        sub(ws, r, "2) Semielaborados en proceso: equipos del cliente por etapa", 8)
        r += 1
        cab(ws, r, ["Etapa", "Formato", "Equipos (u. equiv.)", "", "", "", "", ""])
        r += 1
        dp = self.a_rdp
        etapas = [("Recibidos e inspeccionados", "Equipo identificado, en jaula", [0]),
                  ("Descargados (polvo, líquidos, CO₂, limpio)", "Recipiente vacío", [2, 3, 4, 5, 6]),
                  ("Desarmados y limpios", "Recipiente sin válvula", [7, 8]),
                  ("Con prueba hidráulica", "Recipiente probado", [10]),
                  ("Secados", "Recipiente seco", [11]),
                  ("Pintados", "Recipiente repintado", [13]),
                  ("Cargados y presurizados (polvo)", "Equipo armado", [16]),
                  ("Ensayados (pérdidas)", "Equipo listo", [19]),
                  ("Precintados, etiquetados y despachados", "Equipo en jaula", [20])]
        for etapa, fmt, ks in etapas:
            c(ws, r, 1, etapa)
            c(ws, r, 2, fmt)
            c(ws, r, 3, "=" + "+".join(dp.abajo(0, 32, 2 + k) for k in ks), "#,##0")
            m["RECARGAS", "se", etapa] = r
            r += 1
        r += 1
        Pr = {i: f"Resumen!$D${self.res[('RECARGAS', 16 + i)]}" for i in range(17)}
        self.scrap(ws, r, "RECARGAS", [
            ("Polvo retirado a descarte", "Descarga a descarte y reposición",
             f"={nec('RECARGAS', 'Agente: polvo')}", "kg", "No", "Residuo: igual al polvo nuevo que se carga (cota "
             "superior: incluye lo que se descargó en el uso)"),
            ("Agua, espuma AFFF y agente K retirados", "Descarga de líquidos",
             f"={Pr[4]}*10+{Pr[5]}*10+{Pr[6]}*50+{Pr[8]}*6", "L", "No", "Efluente: capacidad nominal de cada equipo"),
            ("Equipos inutilizados", "Inutilización y disposición final", "=" + dp.abajo(0, 32, 2 + 21), "u. equiv.",
             "Sí: chatarra", "Recipiente perforado, a chatarra (IRAM 3517-2 9.12)"),
            ("CO₂ y agente limpio", "Recuperación en circuito cerrado", "=0", "kg", "—",
             "Se recuperan; lo nuevo repone lo que se descargó en el uso")])
        r = self.r_scrap_fin
        grupos = [("Recargas ABC manuales (1 a 10 kg)", [0, 1, 2, 3]), ("Recargas ABC rodantes (25 a 100 kg)",
                                                                        [13, 14, 15, 16]),
                  ("Recargas de agua, AFFF y sales K", [4, 5, 6, 8]), ("Recargas de CO₂", [9, 10]),
                  ("Recargas de HCFC/HFC", [11]), ("Recargas de BC y clase D", [7, 12])]
        self.pt(ws, r, "RECARGAS", [(n, "Equipo recargado, precintado y etiquetado",
                                     "=" + "+".join(Pr[k] for k in ks)) for n, ks in grupos])
        r = self.r_pt_fin

        # ================= REVENDIDOS
        sub(ws, r, "REVENDIDOS (no se fabrican: entran y salen iguales)", 8)
        ws.cell(r, 1).font = FT
        r += 1
        cab(ws, r, ["Producto", "Formato", "Entra = sale (u)", "", "", "", "", ""])
        r += 1
        r0, r1 = self.det["REVENDIDOS"]
        r_rev = r
        for k, n in enumerate(REV):
            c(ws, r, 1, f"Matafuego {n}")
            c(ws, r, 2, f"=MP_detalle!F{r0 + k}")
            c(ws, r, 3, f"=MP_detalle!H{r0 + k}", "#,##0")
            r += 1
        c(ws, r, 1, "Total revendidos", neg=True)
        c(ws, r, 3, f"=SUM(C{r_rev}:C{r - 1})", "#,##0", neg=True)
        m["REVENDIDOS", "pt"] = r
        ws.freeze_panes = "A4"

    def scrap(self, ws, r, lin, filas):
        sub(ws, r, "3) Scrap, desechos no recuperables y mermas", 8)
        r += 1
        cab(ws, r, ["Qué", "De dónde sale", "Cantidad", "UM", "¿Se recupera?", "Destino / formato", "", ""])
        r += 1
        for k, (que, de, f, um, recup, dest) in enumerate(filas):
            c(ws, r, 1, que)
            c(ws, r, 2, de)
            c(ws, r, 3, f, "#,##0.0")
            c(ws, r, 4, um)
            c(ws, r, 5, recup)
            c(ws, r, 6, dest)
            ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8)
            self.mat[lin, "scrap", k] = r
            r += 1
        self.r_scrap_fin = r + 1

    def pt(self, ws, r, lin, filas):
        sub(ws, r, "4) Producto terminado", 8)
        r += 1
        cab(ws, r, ["Producto", "Formato", "Unidades", "", "", "", "", ""])
        r += 1
        r0 = r
        for n, fmt, f in filas:
            c(ws, r, 1, n)
            c(ws, r, 2, fmt)
            c(ws, r, 3, f, "#,##0")
            r += 1
        c(ws, r, 1, "Total producto terminado", neg=True)
        c(ws, r, 3, f"=SUM(C{r0}:C{r - 1})", "#,##0", neg=True)
        self.mat[lin, "pt"] = r
        self.mat[lin, "pt0"] = (r0, r - 1)
        self.r_pt_fin = r + 2

    def acero(self, ws, r, lin, entra, pt, chat, obs="Chapa de cuerpos y fleje de cúpulas y fondos"):
        sub(ws, r, "Balance de acero (kg)", 8)
        r += 1
        cab(ws, r, ["Entra (MP)", "Queda en el producto", "Chatarra", "Cierre (entra − producto − chatarra)",
                    "Aprovechamiento real", "¿Cierra?", "", ""])
        r += 1
        c(ws, r, 1, entra, "#,##0")
        c(ws, r, 2, pt, "#,##0")
        c(ws, r, 3, chat, "#,##0")
        c(ws, r, 4, f"=A{r}-B{r}-C{r}", "#,##0")
        c(ws, r, 5, f"=IF(A{r}=0,0,B{r}/A{r})", "0.0%")
        c(ws, r, 6, sino(f"ABS(D{r})<1"))
        pinta_checks(ws, f"F{r}:F{r}")
        nota(ws, r + 1, obs + ". Producto = planchuelas y discos de la producción del año (Piezas del Excel de corte).")
        self.mat[lin, "acero"] = r
        self.r_acero_fin = r + 3

    # -------- Línea
    def linea(self):
        ws = hoja(self.wb, "Linea", [6, 44, 10, 12, 13, 13, 8, 8, 10, 13, 12])
        tit(ws, 1, "BALANCEO DE LÍNEA (año elegido en Resumen)")
        nota(ws, 2, "Tiempos, unidades y recursos de cada Aprovechamiento. Eficiencia de balanceo = aprovechamiento "
                    "medio / aprovechamiento del cuello de botella (100 % = línea perfectamente balanceada).")
        r = 4
        defs = [("MANUALES", "LÍNEA DE MANUALES", "man", self.a_mpar, self.a_mdp, 28, self.a_mres, (0, 29, 58),
                 self.a_mplan, 11, self.a_mh, "s", 8),
                ("RODANTES", "LÍNEA DE CARROS", "car", self.a_cpar, self.a_cdp, 20, self.a_cres, (0, 21, 42),
                 self.a_cplan, 11, self.a_ch, "min", 8),
                ("RECARGAS", "LÍNEA DE RECARGAS", "rec", self.a_rpar, self.a_rdp, 32, self.a_rres, (0, 32, 64),
                 self.a_rplan, 32, self.a_rh, "s", 17)]
        for lin, titulo, k, par, dp, paso, res, (iu, im, it), plan, ppaso, horas, ut, nprod in defs:
            nombres = self.nombres[k]
            recurso = self.nombres[k + "_r"]
            n = len(nombres)
            sub(ws, r, titulo, 11)
            ws.cell(r, 1).font = FT
            r += 1
            # indicadores
            r_ind = r
            fila_tot = (1 + nprod) if lin != "RECARGAS" else 18
            u_anio = f"=SUM(Resumen!$D${self.res[(lin, {'MANUALES': 0, 'RODANTES': 8, 'RECARGAS': 16}[lin])]}" \
                     f":$D${self.res[(lin, {'MANUALES': 7, 'RODANTES': 15, 'RECARGAS': 32}[lin])]})"
            pico = f"=MAX(INDEX(Links!${L(plan.c0)}${plan.r0}:${L(plan.c0 + 11)}${plan.r0 + plan.nr - 1}," \
                   f"{DY}*{ppaso}+{fila_tot + 1},0))"
            ind = [("Unidades del año (recipientes / recargas)", u_anio, "#,##0"),
                   ("Unidades del mes pico", pico, "#,##0"),
                   ("Horas productivas por mes (1 turno)", "=" + horas.a(0, 0), "#,##0"),
                   ("Takt del mes pico, 1 turno (s/u)", f"=IF(C{r + 1}=0,0,C{r + 2}*3600/C{r + 1})", "#,##0.0"),
                   ("Contenido de trabajo por unidad (s/u)", None, "#,##0.0"),
                   ("Recursos-turno mínimos teóricos (contenido / takt)", f"=IF(C{r + 3}=0,0,C{r + 4}/C{r + 3})",
                    "#,##0.0"),
                   ("Recursos-turno instalados (máquinas × turnos)", None, "#,##0"),
                   ("Aprovechamiento medio (ponderado por recursos)", None, "0.0%"),
                   ("Cuello de botella", None, None),
                   ("Aprovechamiento del cuello de botella", None, "0.0%"),
                   ("Eficiencia de balanceo (medio / cuello)", f"=IF(C{r + 9}=0,0,C{r + 7}/C{r + 9})", "0.0%"),
                   ("Tiempo ocioso del balanceo", f"=1-C{r + 10}", "0.0%")]
            for t, f, fmt in ind:
                c(ws, r, 1, "")
                c(ws, r, 2, t)
                c(ws, r, 3, f, fmt, neg=True)
                ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
                r += 1
            r += 1
            cab(ws, r, ["N°", "Puesto", "Recurso", f"Tiempo ({ut}/u)", "Unidades del año", "Horas de trabajo",
                        "Máq.", "Turnos", "Recursos", "Aprovechamiento", "Cuello"])
            r += 1
            r0 = r
            for i in range(n):
                c(ws, r, 1, i + 1, "0")
                c(ws, r, 2, nombres[i])
                c(ws, r, 3, recurso[i])
                c(ws, r, 4, "=" + par.a(i, 0), "#,##0.00")
                if lin == "RODANTES":           # el Aprovechamiento de carros da horas por puesto
                    c(ws, r, 6, "=" + dp.abajo(0, paso, 2 + i), "#,##0.0")
                    c(ws, r, 5, f"=IF(D{r}=0,0,F{r}*60/D{r})", "#,##0")
                else:
                    c(ws, r, 5, "=" + dp.abajo(0, paso, 2 + i), "#,##0")
                    c(ws, r, 6, f"=E{r}*D{r}/3600", "#,##0.0")
                c(ws, r, 7, f"=INDEX({res.fila(im + i, 0, 9)},1,{YI})", "0")
                c(ws, r, 8, f"=INDEX({res.fila(it + i, 0, 9)},1,{YI})", "0")
                c(ws, r, 9, f"=G{r}*H{r}", "0")
                c(ws, r, 10, f"=INDEX({res.fila(iu + i, 0, 9)},1,{YI})", "0.0%")
                c(ws, r, 11, f'=IF(J{r}=MAX($J${r0}:$J${r0 + n - 1}),"◀ cuello","")')
                r += 1
            r1 = r - 1
            c(ws, r, 2, "Total", neg=True)
            for col in ("F", "I"):
                c(ws, r, {"F": 6, "I": 9}[col], f"=SUM({col}{r0}:{col}{r1})", "#,##0", neg=True)
            f_cont = f"=IF(C{r_ind}=0,0,F{r}*3600/C{r_ind})"
            ws.cell(r_ind + 4, 3).value = f_cont
            ws.cell(r_ind + 6, 3).value = f"=I{r}"
            ws.cell(r_ind + 7, 3).value = f"=IF(I{r}=0,0,SUMPRODUCT(J{r0}:J{r1},I{r0}:I{r1})/I{r})"
            ws.cell(r_ind + 8, 3).value = f"=INDEX(B{r0}:B{r1},MATCH(MAX(J{r0}:J{r1}),J{r0}:J{r1},0))"
            ws.cell(r_ind + 8, 3).alignment = IZQ
            ws.cell(r_ind + 9, 3).value = f"=MAX(J{r0}:J{r1})"
            rng = f"J{r0}:J{r1}"
            ws.conditional_formatting.add(rng, FormulaRule(formula=[f"J{r0}>=0.9"],
                                                           fill=PatternFill("solid", fgColor="F8CBAD")))
            ws.conditional_formatting.add(rng, FormulaRule(formula=[f"AND(J{r0}>=0.75,J{r0}<0.9)"],
                                                           fill=PatternFill("solid", fgColor="FFEB9C")))
            ws.conditional_formatting.add(rng, FormulaRule(formula=[f"J{r0}<0.75"],
                                                           fill=PatternFill("solid", fgColor="C6EFCE")))
            self.lin[lin] = dict(r_ind=r_ind, r0=r0, r1=r1, n=n)
            r += 3
        ws.freeze_panes = "A4"

    # -------- esquemas
    def caja(self, ws, r, col, w, h, f, color, neg=False):
        ws.merge_cells(start_row=r, start_column=col, end_row=r + h - 1, end_column=col + w - 1)
        x = ws.cell(r, col, f)
        x.alignment = CEN
        x.font = Font(name="Arial", size=9, bold=neg)
        x.fill = PatternFill("solid", fgColor=color)
        med = Side(style="medium", color="404040")
        for rr in range(r, r + h):
            for cc in range(col, col + w):
                ws.cell(rr, cc).border = Border(left=med if cc == col else None, right=med if cc == col + w - 1
                                                else None, top=med if rr == r else None,
                                                bottom=med if rr == r + h - 1 else None)
                if (rr, cc) != (r, col):
                    ws.cell(rr, cc).fill = PatternFill("solid", fgColor=color)

    def flecha(self, ws, r, col, h, t="➜"):
        ws.merge_cells(start_row=r, start_column=col, end_row=r + h - 1, end_column=col)
        x = ws.cell(r, col, t)
        x.alignment = CEN
        x.font = Font(name="Arial", size=16, bold=True, color="404040")

    def esquema_materiales(self):
        ws = hoja(self.wb, "Esquema materiales", [2] + [6] * 44)
        tit(ws, 1, "ESQUEMA DEL BALANCE DE MATERIALES (año elegido en Resumen) — los números salen de la hoja Materiales")
        nota(ws, 2, "Azul: materia prima · amarillo: semielaborados · verde: producto terminado · rojo: scrap, "
                    "desechos y mermas · gris: checks. Editable: los textos son fórmulas.")
        M = "Materiales"
        m = self.mat
        N = "CHAR(10)"

        def t(x, fmt="#,##0"):
            return f'TEXT({x},"{fmt}")'

        def mp(lin, fam):
            return f"{M}!$C${m[lin, 'mp', fam]}"

        def se(lin, etapa, col="G"):
            return f"{M}!${col}${m[lin, 'se', etapa]}"

        def sc(lin, k):
            return f"{M}!$C${m[lin, 'scrap', k]}"

        def ptc(lin):
            return f"{M}!$C${m[lin, 'pt']}"

        def suma(*xs):
            return "+".join(xs)

        def chk(lin):
            rt = self.tot[lin]
            return (f'="CHECKS {self.anio_txt()}"&{N}&"Producción ≥ demanda: "&IF(Resumen!$G${rt}=0,"✔","✖ "&Resumen!$G${rt}'
                    f'&" productos")&{N}&"Sobrestock: "&{t("Resumen!$F$" + str(rt), "0.0%")}&{N}&"MRP cubre la producción: "&'
                    f'IF(Resumen!$I${rt}=0,"✔","✖ "&Resumen!$I${rt}&" productos")')

        r = 4
        H = 7
        rep_id = suma(mp("RECARGAS", "Componentes comprados"), mp("RECARGAS", "Identificación y embalaje"))
        filas = [
            ("MANUALES", "LÍNEA DE MANUALES",
             f'="MATERIA PRIMA"&{N}&"Chapa: "&{t(mp("MANUALES", "Chapa en hojas"))}&" hojas"&{N}&"Fleje: "&'
             f'{t(mp("MANUALES", "Fleje en rollos"))}&" kg"&{N}&"Polvo ABC: "&{t(mp("MANUALES", "Agente: polvo"))}&" kg"'
             f'&{N}&"Componentes: "&{t(mp("MANUALES", "Componentes comprados"))}&" u"',
             [f'="CORTE"&{N}&{t(se("MANUALES", "Planchuela de cuerpo cortada"))}&" planchuelas"&{N}&'
              f'{t(se("MANUALES", "Discos de cúpula y fondo"))}&" discos"',
              f'="EMBUTIDO Y SOLDADURA"&{N}&{t(se("MANUALES", "Casquetes embutidos (cúpula numerada con cuello, fondo)"))}'
              f'&" casquetes"&{N}&{t(se("MANUALES", "Recipiente soldado (PH, secado, granallado)"))}&" recipientes"',
              f'="TERMINACIÓN"&{N}&"PH, secado, granallado, pintura"&{N}&'
              f'{t(se("MANUALES", "Recipiente pintado"))}&" recipientes pintados"',
              f'="CARGA Y ARMADO"&{N}&"polvo, válvula, N₂, ensayo de pérdidas"'],
             f'="PRODUCTO TERMINADO"&{N}&{t(ptc("MANUALES"))}&" u"&{N}&"matafuegos 1 a 10 kg y '
             f'cilindros vacíos"',
             f'="SCRAP Y MERMAS"&{N}&"Chatarra: "&{t(suma(sc("MANUALES", 0), sc("MANUALES", 1)))}&" kg (recortes y '
             f'esqueleto de fleje)"&{N}&"Desechos: "&{t(suma(sc("MANUALES", 2), sc("MANUALES", 5), sc("MANUALES", 6)))}'
             f'&" kg (salpicadura, granalla, pintura)"&{N}&"Gases: "&{t(sc("MANUALES", 3))}&" m³"'),
            ("RODANTES", "LÍNEA DE CARROS",
             f'="MATERIA PRIMA"&{N}&"Chapa: "&{t(mp("RODANTES", "Chapa en hojas"))}&" hojas"&{N}&"Casquetes y cuplas: "'
             f'&{t(mp("RODANTES", "Casquetes y cuplas"))}&" u"&{N}&"Polvo ABC 90: "&{t(mp("RODANTES", "Agente: polvo"))}'
             f'&" kg"&{N}&"Caños y barras: "&{t(mp("RODANTES", "Caños y barras"), "#,##0.0")}&" barras"',
             [f'="CORTE Y ROLADO"&{N}&{t(se("RODANTES", "Planchuela de cuerpo cortada"))}&" planchuelas"&{N}&'
              f'{t(se("RODANTES", "Virola rolada, punteada y soldada"))}&" virolas"',
              f'="ARMADO Y SOLDADURA"&{N}&{t(se("RODANTES", "Recipiente armado (cuerpo + 2 casquetes + cupla)"))}'
              f'&" recipientes"&{N}&"accesorios del carro"',
              f'="PH, SECADO Y PINTURA"&{N}&{t(se("RODANTES", "Recipiente pintado (tercerizado: sale y vuelve)"))}'
              f'&" recipientes"&{N}&"(pintura tercerizada)"',
              f'="CARGA Y ARMADO"&{N}&{t(se("RODANTES", "Carro armado y cargado"))}&" carros"'],
             f'="PRODUCTO TERMINADO"&{N}&{t(ptc("RODANTES"))}&" u"&{N}&"carros 25 a 100 kg y '
             f'cilindros vacíos"',
             f'="SCRAP Y MERMAS"&{N}&"Chatarra de chapa: "&{t(sc("RODANTES", 0))}&" kg"&{N}&"Recorte de caño y barra: "'
             f'&{t(sc("RODANTES", 1), "#,##0.0")}&" m"&{N}&"Desechos: "&{t(sc("RODANTES", 2), "#,##0.0")}&" kg y "'
             f'&{t(sc("RODANTES", 4))}&" abrasivos"'),
            ("RECARGAS", "LÍNEA DE RECARGAS",
             f'="MATERIA PRIMA"&{N}&"Polvos: "&{t(mp("RECARGAS", "Agente: polvo"))}&" kg"&{N}&"CO₂ y limpio: "&'
             f'{t(mp("RECARGAS", "Agente: CO₂ y limpio"))}&" kg"&{N}&"Líquidos: "&{t(mp("RECARGAS", "Agente: líquidos"))}'
             f'&" L"&{N}&"Repuestos e identificación: "&{t(rep_id)}&" u"',
             [f'="RECEPCIÓN Y DESCARGA"&{N}&{t(se("RECARGAS", "Recibidos e inspeccionados", "C"))}&" recibidos"&{N}&'
              f'{t(se("RECARGAS", "Descargados (polvo, líquidos, CO₂, limpio)", "C"))}&" descargados"',
              f'="DESARME Y PH"&{N}&{t(se("RECARGAS", "Desarmados y limpios", "C"))}&" desarmados"&{N}&'
              f'{t(se("RECARGAS", "Con prueba hidráulica", "C"))}&" con PH"',
              f'="SECADO Y PINTURA"&{N}&{t(se("RECARGAS", "Secados", "C"))}&" secados"&{N}&'
              f'{t(se("RECARGAS", "Pintados", "C"))}&" pintados"',
              f'="CARGA Y ENSAYO"&{N}&{t(se("RECARGAS", "Cargados y presurizados (polvo)", "C"))}&" cargados"&{N}&'
              f'{t(se("RECARGAS", "Ensayados (pérdidas)", "C"))}&" ensayados"'],
             f'="PRODUCTO TERMINADO"&{N}&{t(ptc("RECARGAS"))}&" recargas"&{N}&"precintadas y '
             f'etiquetadas"',
             f'="SCRAP Y MERMAS"&{N}&"Polvo a descarte: "&{t(sc("RECARGAS", 0))}&" kg"&{N}&"Líquidos: "&'
             f'{t(sc("RECARGAS", 1))}&" L"&{N}&"Equipos inutilizados: "&{t(sc("RECARGAS", 2))}&" (chatarra)"')]
        for lin, titulo, f_mp, f_se, f_pt, f_sc in filas:
            x = ws.cell(r, 2, titulo)
            x.font = FT
            r += 1
            col = 2
            self.caja(ws, r, col, 5, H, f_mp, "DDEBF7", True)
            col += 5
            for f in f_se:
                self.flecha(ws, r, col, H)
                col += 1
                self.caja(ws, r, col, 5, H, f, "FFF2CC")
                col += 5
            self.flecha(ws, r, col, H)
            col += 1
            self.caja(ws, r, col, 5, H, f_pt, "C6EFCE", True)
            col += 6
            self.caja(ws, r, col, 6, H, chk(lin), "EDEDED")
            # scrap debajo de los semielaborados
            for k in range(4):
                x = ws.cell(r + H, 8 + 6 * k + 2, "▼")
                x.alignment = CEN
                x.font = Font(name="Arial", size=12, color="C00000")
            self.caja(ws, r + H + 1, 8, 23, 4, f_sc, "F8CBAD")
            r += H + 7
        # revendidos
        x = ws.cell(r, 2, "REVENDIDOS")
        x.font = FT
        r += 1
        self.caja(ws, r, 2, 5, 3, f'="COMPRA"&{N}&{t(ptc("REVENDIDOS"))}&" equipos"', "DDEBF7", True)
        self.flecha(ws, r, 7, 3)
        self.caja(ws, r, 8, 5, 3, f'="VENTA"&{N}&{t(ptc("REVENDIDOS"))}&" equipos"', "C6EFCE", True)
        for rr in range(4, r + 4):
            ws.row_dimensions[rr].height = 16

    def anio_txt(self):
        return '"&Resumen!$C$3&"'

    def esquema_linea(self):
        ws = hoja(self.wb, "Esquema linea", [2] + [7] * 42)
        tit(ws, 1, "ESQUEMA DEL BALANCEO DE LÍNEA (año elegido en Resumen) — cada caja es un puesto, en orden de proceso")
        nota(ws, 2, "Color por aprovechamiento: verde < 75 % · amarillo 75 a 90 % · rojo ≥ 90 % (umbral). El borde "
                    "grueso marca el cuello de botella. Los números salen de la hoja Linea.")
        N = "CHAR(10)"
        r = 4
        por_fila = 6
        for lin, titulo in (("MANUALES", "LÍNEA DE MANUALES"), ("RODANTES", "LÍNEA DE CARROS"),
                            ("RECARGAS", "LÍNEA DE RECARGAS")):
            d = self.lin[lin]
            x = ws.cell(r, 2, titulo)
            x.font = FT
            ri = d["r_ind"]
            res = ws.cell(r, 14, f'="Takt "&TEXT(Linea!$C${ri + 3},"#,##0.0")&" s/u · contenido "&TEXT(Linea!$C${ri + 4},'
                                 f'"#,##0.0")&" s/u · eficiencia de balanceo "&TEXT(Linea!$C${ri + 10},"0%")&" · cuello: "&'
                                 f'Linea!$C${ri + 8}&" ("&TEXT(Linea!$C${ri + 9},"0%")&")"')
            res.font = FB
            r += 1
            for i in range(d["n"]):
                fi, co = divmod(i, por_fila)
                if fi % 2:                      # serpentina
                    co = por_fila - 1 - co
                rr = r + fi * 5
                cc = 2 + co * 7
                rl = d["r0"] + i
                self.caja(ws, rr, cc, 6, 3, f'=Linea!$A${rl}&". "&Linea!$B${rl}&{N}&Linea!$I${rl}&" recurso(s)"',
                          "FFFFFF")
                v = ws.cell(rr + 3, cc, f"=Linea!$J${rl}")
                ws.merge_cells(start_row=rr + 3, start_column=cc, end_row=rr + 3, end_column=cc + 5)
                v.number_format = "0.0%"
                v.alignment = CEN
                v.font = FB
                caja = f"{L(cc)}{rr}:{L(cc + 5)}{rr + 3}"
                ref = f"${L(cc)}${rr + 3}"
                for cond, color in ((f"{ref}>=0.9", "F8CBAD"), (f"AND({ref}>=0.75,{ref}<0.9)", "FFEB9C"),
                                    (f"{ref}<0.75", "C6EFCE")):
                    ws.conditional_formatting.add(caja, FormulaRule(formula=[cond],
                                                                    fill=PatternFill("solid", fgColor=color)))
                ws.conditional_formatting.add(caja, FormulaRule(
                    formula=[f'{ref}=MAX(Linea!$J${d["r0"]}:$J${d["r1"]})'],
                    font=Font(name="Arial", bold=True, color="9C0006")))
                # flecha al siguiente
                if i < d["n"] - 1:
                    sig_fi, sig_co = divmod(i + 1, por_fila)
                    if sig_fi == fi:
                        fx = cc + 6 if fi % 2 == 0 else cc - 1
                        x = ws.cell(rr + 1, fx, "➜" if fi % 2 == 0 else "⬅")
                    else:
                        x = ws.cell(rr + 4, cc + 2, "⬇")
                    x.alignment = CEN
                    x.font = Font(name="Arial", size=14, bold=True, color="404040")
            filas = math.ceil(d["n"] / por_fila)
            r += filas * 5 + 2
        for rr in range(4, r):
            ws.row_dimensions[rr].height = 15

    def armar(self):
        self.resumen()
        self.mp_detalle()
        self.materiales()
        self.linea()
        self.esquema_materiales()
        self.esquema_linea()
        LB.escribir(self.wb)
        orden = ["Links", "Resumen", "Esquema materiales", "Esquema linea", "Materiales", "MP_detalle", "Linea"]
        self.wb._sheets = [self.wb[n] for n in orden]
        for ws in self.wb.worksheets:
            ws.page_setup.orientation = "landscape"
            ws.page_setup.paperSize = ws.PAPERSIZE_A4
            ws.sheet_properties.pageSetUpPr.fitToPage = True
            ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        self.wb.active = 1
        self.wb.calculation.fullCalcOnLoad = True
        self.wb.save(SALIDA)
        amc.recalc(SALIDA)
        amc.arreglar_dummy(SALIDA)
        print("guardado", SALIDA)


if __name__ == "__main__":
    Libro().armar()
