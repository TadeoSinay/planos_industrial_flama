"""Actualiza los Dimensionamientos de Manuales y Carros del grupo (referencias/) y los deja en salida/.

Cambios sobre los archivos del grupo, sin mover sus hojas:
- Hoja Links con los links de los IMPORTRANGE (Proyecciones y los dos Dimensionamientos de recargas, a completar).
- datos_base con IMPORTRANGE de Proyecciones (Indexado Dim Técnico) y un bloque de sustitutos ABC por modelo: la
  planta industrial los pide terminados (proceso completo en la línea) y la comercial como cilindro vacío.
- Plan mensual con esas filas (perfil de estacionalidad del modelo); la demanda por puesto las suma igual en sin y con
  sobrestock: los terminados pasan por todos los puestos y los cilindros solo por los de alcance "Todos".
- Aprovechamiento indexado a las tablas de máquinas y turnos (sin "/2" escritos a mano), tablas cargadas con el
  criterio de Manuales a partir de lo que ya estaba (ningún puesto pasa el umbral del 90 %) y colores por formato
  condicional.
- Formato gris en la hoja Links y en el bloque de sobrestock de parametros_manuales (venía en azul y verde).
"""

import os
import subprocess
import sys
import zipfile
from copy import copy

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter as L

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_dim_recargas as g  # noqa: E402

RAIZ = g.RAIZ
REF = os.path.join(RAIZ, "referencias")
RECALC = os.environ.get("RECALC", "/root/.claude/skills/synced/25c356cd-d646-4fc6-a248-83c7f917a94a_"
                                  "ed033efe-807e-46d6-9687-95e22d26e759/xlsx/scripts/recalc.py")
ANIO_2T = g.ANIO_2T

# Proyecciones, Indexado Dim Técnico (valores que trae el IMPORTRANGE)
TERM_MAN = [[4178.736543, 5997.303977, 6851.747758, 8467.135549, 12680.63271, 15620.25307, 20332.55326, 25132.07848,
             28573.33614, 32072.63913],
            [295.0303572, 709.7274503, 986.8680576, 1500.638174, 2312.627726, 3252.869887, 4102.315524, 5104.306587,
             6195.186243, 7424.858444],
            [2255.773025, 3846.978881, 5093.537591, 6823.115313, 10819.30694, 14605.96411, 18877.75984, 23368.18637,
             26967.72455, 30750.77872],
            [91.83318153, 177.2472967, 252.9787798, 358.0204941, 602.7181519, 872.605032, 1127.160545, 1395.444812,
             1612.350054, 1840.848079]]
CIL_MAN = [[0.0, 0.0, 7662.4, 26694.8, 49434.8, 71680.2, 101340.6, 131001.0, 146819.8, 170548.0],
           [0.0, 0.0, 299.6, 1043.8, 1933.0, 2803.0, 3963.0, 5123.0, 5741.4, 6669.0],
           [0.0, 0.0, 1478.8, 5152.0, 9540.8, 13834.2, 19558.6, 25283.0, 28335.8, 32915.0],
           [0.0, 0.0, 90.4, 315.0, 583.4, 845.8, 1195.4, 1545.0, 1731.4, 2011.0]]
TERM_CAR = [[34.05179136, 58.46214745, 75.20853998, 100.5298529, 155.8760035, 211.9344827, 272.6682332, 337.8486707,
             393.6274156, 453.2705332],
            [74.913941, 128.6167244, 165.458788, 221.1656765, 342.9272077, 466.255862, 599.8701129, 743.2670756,
             865.9803143, 997.1951731],
            [16.34485985, 28.06183078, 36.10009919, 48.25432941, 74.82048167, 101.7285517, 130.8807519, 162.1673619,
             188.9411595, 217.569856],
            [10.89657324, 18.70788719, 24.06673279, 32.16955294, 49.88032112, 67.81903447, 87.25383461, 108.1115746,
             125.960773, 145.0465706]]
CIL_CAR = [[0.0, 0.0, 14.4, 50.2, 93.0, 135.0, 191.0, 247.0, 277.0, 322.0],
           [0.0, 0.0, 31.8, 110.8, 205.2, 297.6, 420.8, 544.0, 609.6, 708.0],
           [0.0, 0.0, 7.0, 24.4, 45.2, 65.4, 92.2, 119.0, 133.4, 155.0],
           [0.0, 0.0, 4.6, 16.0, 29.6, 42.8, 60.4, 78.0, 87.6, 102.0]]

LINKS = [g.LINKS[0],
         ("Dimensionamiento Recargas Planta Comercial", g.PEGAR,
          "sobrestock_sustitutos, paso 6: sustitutos ABC que pide como cilindro vacío"),
         ("Dimensionamiento Recargas Planta Industrial", g.PEGAR,
          "sobrestock_sustitutos, paso 6: sustitutos ABC que pide como matafuego terminado")]
LK_PROY, LK_COM, LK_IND = "Links!$B$4", "Links!$B$5", "Links!$B$6"
PED_MAN = f"sobrestock_sustitutos!B{g.S_PED}:K{g.S_PED + 3}"
PED_CAR = f"sobrestock_sustitutos!B{g.S_PED + 4}:K{g.S_PED + 7}"
# Recurso de cada puesto (para el color de máquina u operario), según el equipo de parametros y el Word de procesos
REC_MAN = ["Manual"] + ["Máquina"] * 11 + ["Manual", "Máquina", "Máquina", "Máquina", "Manual", "Manual", "Máquina",
                                           "Máquina", "Manual", "Máquina", "Máquina", "Máquina", "Manual"]
REC_CAR = ["Manual", "Máquina", "Máquina", "Máquina", "Manual", "Máquina", "Máquina", "Máquina", "Manual", "Manual",
           "Máquina", "Máquina", "Manual", "Manual", "Máquina", "Manual", "Manual", "Manual"]


def pedidos():
    """Sustitutos ABC por modelo y año que pide cada planta de recargas (paso 6 de su Dimensionamiento)."""
    out = {}
    for p in ("Comercial", "Industrial"):
        alta = g.modelo_demanda(p)[-1]["alta"]
        out[p] = [[alta[i][k] for i in range(10)] for k in g.K_ABC]
    return out


def estilo(src, dst):
    dst.font, dst.fill, dst.border = copy(src.font), copy(src.fill), copy(src.border)
    dst.alignment, dst.number_format = copy(src.alignment), src.number_format


def imp(ws, r0, c0, link, rango, valores):
    """IMPORTRANGE como lo exporta Google (la celda conserva su formato)."""
    for i, fila in enumerate(valores):
        for j, x in enumerate(fila):
            if i == 0 and j == 0:
                f = f'=IFERROR(__xludf.DUMMYFUNCTION("IMPORTRANGE({link},""{rango}"")"),{x!r})'
            else:
                f = f'=IFERROR(__xludf.DUMMYFUNCTION("""COMPUTED_VALUE"""),{x!r})'
            ws.cell(r0 + i, c0 + j).value = f


def links(wb):
    g.h_links(wb, LINKS)
    wb.move_sheet("Links", offset=-(len(wb.sheetnames) - 1))


def grises(wb):
    """Encabezados azules a gris claro con letra negra y celdas verdes de resultado a gris, como el resto del archivo."""
    gris = {"FF1F4E78": "FFF2F2F2", "FFE2EFDA": "FFD9D9D9"}
    for ws in wb:
        for fila in ws.iter_rows():
            for c in fila:
                if c.fill.fill_type == "solid" and c.fill.fgColor.type == "rgb" and c.fill.fgColor.rgb in gris:
                    if c.fill.fgColor.rgb == "FF1F4E78":
                        f = copy(c.font)
                        f.color = "FF000000"
                        c.font = f
                    c.fill = PatternFill("solid", fgColor=gris[c.fill.fgColor.rgb])


def bloque_sustitutos(ws, r0, modelos, rango, ped, fila_estilo, fila_tot, nota_txt):
    """datos_base: terminados (industrial) y cilindros (comercial) para sustitutos, con IMPORTRANGE."""
    ws.cell(r0, 1).value = "Sustitutos ABC para las plantas de recargas"
    for c in range(1, 12):
        estilo(ws.cell(1, c), ws.cell(r0, c))
    for i in range(10):
        ws.cell(r0, 2 + i).value = g.ANIOS[i]
    filas = {}
    for b, (pl, txt, lk) in enumerate([("Industrial", "terminado, planta industrial", LK_IND),
                                       ("Comercial", "cilindro vacío, planta comercial", LK_COM)]):
        r1 = r0 + 1 + 5 * b
        for j, mo in enumerate(modelos):
            ws.cell(r1 + j, 1).value = f"{mo} — sustituto ({txt})"
            for c in range(1, 12):
                estilo(ws.cell(fila_estilo, c), ws.cell(r1 + j, c))
        imp(ws, r1, 2, lk, rango, ped[pl])
        rt = r1 + 4
        ws.cell(rt, 1).value = f"Total sustitutos {'terminados' if b == 0 else 'cilindros vacíos'}"
        for c in range(1, 12):
            estilo(ws.cell(fila_tot, c), ws.cell(rt, c))
        for i in range(10):
            col = L(2 + i)
            ws.cell(rt, 2 + i).value = f"=SUM({col}{r1}:{col}{r1 + 3})"
        filas[pl] = r1
    ws.cell(r0 + 11, 1).value = nota_txt
    ws.cell(r0 + 11, 1).font = Font(name="Arial", size=9, italic=True)
    return filas


def plan_sustitutos(ws, fila_ini, fila_db, hoja_perfil, modelos):
    """Plan mensual: bloque por año con los sustitutos (mismo perfil del modelo que en estacionalidad)."""
    ws.cell(fila_ini - 1, 2).value = ("SUSTITUTOS PARA LAS PLANTAS DE RECARGAS (perfil de estacionalidad del modelo; "
                                      "se suman igual en sin y con sobrestock)")
    ws.cell(fila_ini - 1, 2).font = Font(name="Arial", size=11, bold=True)
    for i in range(10):
        r0 = fila_ini + 11 * i
        y = L(2 + i)
        for c in range(1, 17):
            estilo(ws.cell(1, c), ws.cell(r0, c))
            ws.cell(r0, c).value = ws.cell(1, c).value
        ws.cell(r0, 1).value = g.ANIOS[i]
        for b, (tipo, base) in enumerate([("Terminado", fila_db["Industrial"]), ("Cilindro", fila_db["Comercial"])]):
            for j, mo in enumerate(modelos):
                r = r0 + 1 + 4 * b + j
                for c in range(1, 17):
                    estilo(ws.cell(2 + 4 * b + j, c), ws.cell(r, c))
                ws.cell(r, 1).value = g.ANIOS[i]
                ws.cell(r, 2).value = f"{mo} — sustituto ({'planta industrial' if b == 0 else 'planta comercial'})"
                ws.cell(r, 3).value = f"{tipo} sustituto"
                for m in range(12):
                    ws.cell(r, 4 + m).value = f"=datos_base!${y}${base + j}*{hoja_perfil}!{L(2 + m)}${12 + j}"
                ws.cell(r, 16).value = f"=SUM(D{r}:O{r})"
        rt = r0 + 9
        for c in range(1, 17):
            estilo(ws.cell(10, c), ws.cell(rt, c))
        ws.cell(rt, 2).value = "Total sustitutos"
        for c in range(4, 17):
            col = L(c)
            ws.cell(rt, c).value = f"=SUM({col}{r0 + 1}:{col}{r0 + 8})"


def termino(pm, p, coef, t, ts, c_, cs, ref):
    return (f"{pm}!${coef}${p}*({ref(t)}+{ref(ts)}+IF({pm}!$H${p}=\"Todos\",{ref(c_)}+{ref(cs)},0))")


def demanda_plan(ws_dem, pm, n_puestos, bloque_dem, cierre, fila_sust, verif):
    """Demanda que sale del Plan mensual (sin sobrestock / carros): suma los sustitutos del bloque nuevo."""
    for i in range(10):
        r_plan = 1 + 11 * i
        r_sust = fila_sust + 11 * i
        for k in range(n_puestos):
            r = bloque_dem * i + 2 + k
            p = 19 + k
            for m in range(12):
                c = L(4 + m)

                def ref(fila):
                    return f"'Plan mensual'!{c}{fila}"
                viejo = "=(" + "+".join(
                    f"{pm}!${co}${p}*({ref(r_plan + 1 + j)}+IF({pm}!$H${p}=\"Todos\",{ref(r_plan + 5 + j)},0))"
                    for j, co in enumerate("DEFG")) + ")" + cierre(p)
                actual = ws_dem.cell(r, 2 + m).value
                if actual != viejo:
                    verif.append((ws_dem.title, ws_dem.cell(r, 2 + m).coordinate, actual, viejo))
                ws_dem.cell(r, 2 + m).value = "=(" + "+".join(
                    termino(pm, p, co, r_plan + 1 + j, r_sust + 1 + j, r_plan + 5 + j, r_sust + 5 + j, ref)
                    for j, co in enumerate("DEFG")) + ")" + cierre(p)


def demanda_sobrestock(ws_dem, fila_db, verif):
    """Manuales con sobrestock: producción = datos_base × perfil de producción; los sustitutos van con el perfil de
    estacionalidad (filas 12 a 15), igual que en la hoja sin sobrestock."""
    pm = "parametros_manuales"
    prod = [95, 100, 105, 110]
    for i in range(10):
        y = L(2 + i)
        for k in range(25):
            r = 27 * i + 2 + k
            p = 19 + k
            for m in range(12):
                mc = L(2 + m)
                viejo = "=(" + "+".join(
                    f"{pm}!${co}${p}*(datos_base!${y}${2 + j}+IF({pm}!$H${p}=\"Todos\",datos_base!${y}${9 + j},0))"
                    f"*{pm}!${mc}${prod[j]}" for j, co in enumerate("DEFG")) + f")*{pm}!$I${p}*{pm}!$J${p}"
                actual = ws_dem.cell(r, 2 + m).value
                if actual != viejo:
                    verif.append((ws_dem.title, ws_dem.cell(r, 2 + m).coordinate, actual, viejo))
                nuevo = "+".join(
                    f"{pm}!${co}${p}*(datos_base!${y}${2 + j}+IF({pm}!$H${p}=\"Todos\",datos_base!${y}${9 + j},0))"
                    f"*{pm}!${mc}${prod[j]}+{pm}!${co}${p}*(datos_base!${y}${fila_db['Industrial'] + j}"
                    f"+IF({pm}!$H${p}=\"Todos\",datos_base!${y}${fila_db['Comercial'] + j},0))*{pm}!${mc}${12 + j}"
                    for j, co in enumerate("DEFG"))
                ws_dem.cell(r, 2 + m).value = f"=({nuevo})*{pm}!$I${p}*{pm}!$J${p}"


def resumen(ws, n, r_maq, r_tur, util, recursos, umbral_ref, celda_umbral, legend_row, piso_solo=False):
    """Fórmulas de aprovechamiento indexadas a las tablas, columna Recurso, umbral local y colores."""
    for k in range(n):
        for i in range(10):
            ws.cell(2 + k, 2 + i).value = util(k, i, f"{L(2 + i)}{r_maq + k}", f"{L(2 + i)}{r_tur + k}")
            ws.cell(2 + k, 2 + i).fill = PatternFill(fill_type=None)
    assert ws["L1"].value is None, ws.title
    estilo(ws["K1"], ws["L1"])
    ws["L1"].value = "Recurso"
    for k in range(n):
        estilo(ws.cell(2 + k, 1), ws.cell(2 + k, 12))
        ws.cell(2 + k, 12).value = recursos[k]
    rm, rn = celda_umbral
    ws[rm].value = "Umbral de aprovechamiento"
    ws[rm].font = Font(name="Arial", size=10, bold=True)
    ws[rn].value = f"={umbral_ref}"
    ws[rn].number_format = "0%"
    ws.cell(legend_row, 13).value = ("Colores automáticos (formato condicional) comparando las tablas de máquinas y "
                                     "turnos con el año anterior. Ningún puesto pasa el umbral; amarillo solo si se "
                                     "cambian las tablas a mano y lo pasa.")
    ws.cell(legend_row, 13).font = Font(name="Arial", size=9, italic=True)
    g.colores_aprovechamiento(ws, 2, r_maq, r_tur, n, "L", "$" + rn[0] + "$" + rn[1:], sin_maquina_es_terc=True)


def piso(ws, n, r_maq, r_tur, mitad, multiplica):
    """Máquinas y turnos efectivos de lo que ya estaba cargado: el "/2" escrito a mano cuenta como 2 turnos (sin
    sobrestock la fórmula no leía la tabla; con sobrestock dividía la tabla por 2)."""
    out = {}
    for k in range(n):
        for i in range(10):
            m = ws.cell(r_maq + k, 2 + i).value
            t = ws.cell(r_tur + k, 2 + i).value or 1
            h = 2 if mitad(k, i) else 1
            out[(k, i)] = (1 if m is None else int(m), int(t * h if multiplica else max(t, h)))
    return out


def mitades(ws, n):
    """Celdas de aprovechamiento con "/2" escrito a mano."""
    c = {(k, i) for k in range(n) for i in range(10) if "/2" in str(ws.cell(2 + k, 2 + i).value)}
    return lambda k, i: (k, i) in c


def escribir_tablas(ws, n, r_maq, r_tur, plan):
    for k in range(n):
        for i in range(10):
            ws.cell(r_maq + k, 2 + i).value = plan[(k, i)][0]
            ws.cell(r_tur + k, 2 + i).value = plan[(k, i)][1]


def recalc(ruta):
    out = subprocess.run([sys.executable, RECALC, ruta, "180"], capture_output=True, text=True)
    print(out.stdout.strip()[:400])


def arreglar_dummy(ruta):
    """LibreOffice guarda __xludf.DUMMYFUNCTION en minúscula: se vuelve a poner como lo exporta Google."""
    tmp = ruta + ".tmp"
    with zipfile.ZipFile(ruta) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            d = zi.read(it.filename)
            if it.filename.startswith("xl/worksheets/"):
                d = d.replace(b"__xludf.dummyfunction", b"__xludf.DUMMYFUNCTION").replace(
                    b"_xludf.dummyfunction", b"_xludf.DUMMYFUNCTION")
            zo.writestr(it, d)
    os.replace(tmp, ruta)


def manuales(ped):
    ent = os.path.join(REF, "Dimensionamiento_Manuales.xlsx")
    sal = os.path.join(g.SALIDA, "Dimensionamiento_Manuales.xlsx")
    wb = load_workbook(ent)
    verif = []
    links(wb)
    grises(wb)
    db = wb["datos_base"]
    imp(db, 2, 2, LK_PROY, "Indexado Dim Técnico!B3:K6", TERM_MAN)
    imp(db, 9, 2, LK_PROY, "Indexado Dim Técnico!B15:K18", CIL_MAN)
    modelos = ["ABC 1 kg", "ABC 2,5 kg", "ABC 5 kg", "ABC 10 kg"]
    fila_db = bloque_sustitutos(db, 17, modelos, PED_MAN, {p: v[:4] for p, v in ped.items()}, 2, 6,
                                "Sustitutos: paso 6 de sobrestock_sustitutos de cada Dimensionamiento de recargas. La "
                                "planta industrial los fabrica terminados (proceso completo); la comercial los recibe "
                                "como cilindro vacío y los carga allá.")
    db["A15"].value = "Total recipientes a fabricar (con sustitutos)"
    for i in range(10):
        c = L(2 + i)
        db[f"{c}15"].value = f"={c}6+{c}13+{c}22+{c}27"
    plan_sustitutos(wb["Plan mensual"], 112, fila_db, "parametros_manuales", modelos)
    cierre = lambda p: f"*parametros_manuales!$I${p}*parametros_manuales!$J${p}"  # noqa: E731
    demanda_plan(wb["Demanda puesto sin sobrestock"], "parametros_manuales", 25, 27, cierre, 112, verif)
    demanda_sobrestock(wb["Demanda puesto con sobrestock"], fila_db, verif)
    pm = wb["parametros_manuales"]
    pm["A9"].value = "Año de inicio del 2° turno (antes: más máquinas)"
    pm["B9"].value = ANIO_2T
    pm["C9"].value = "Criterio del aprovechamiento: antes de ese año se agrega máquina u operario; desde ese año, turno"
    for c in "ABC":
        estilo(pm[f"{c}8"], pm[f"{c}9"])
    pm["B9"].number_format = "0"
    pm["A8"].value = "Umbral de aprovechamiento"
    pm["C8"].value = ("Límite duro (análisis de riesgos): por encima se agrega máquina, operario o turno según el año "
                      "(Resumen cap.); con 2 turnos se agrega máquina. Ningún puesto queda por encima")
    hojas = [("Resumen cap. sin sobrestock", "Demanda puesto sin sobrestock", False),
             ("Resumen cap. con sobrestock", "Demanda puesto con sobrestock", True)]
    pisos = {}
    for rn, dn, multiplica in hojas:
        ws = wb[rn]
        pisos[rn] = piso(ws, 25, 30, 58, mitades(ws, 25), multiplica)

        def util(k, i, mq, tu, dn=dn):
            pr = 27 * i + 2 + k
            return (f"=IF({mq}*{tu}*parametros_manuales!$M${19 + k}*parametros_manuales!$B$6=0,0,'{dn}'!$P${pr}/"
                    f"(parametros_manuales!$M${19 + k}*{mq}*{tu}*parametros_manuales!$B$6))")
        resumen(ws, 25, 30, 58, util, REC_MAN, "parametros_manuales!$B$8", ("M13", "N13"), 14)
        escribir_tablas(ws, 25, 30, 58, pisos[rn])
    wb["Resumen cap. con sobrestock"]["O1"].value = ("Turnos: esta hoja divide por la tabla de turnos (filas 58 a 82), "
                                                     "igual que la hoja sin sobrestock.")
    wb.save(sal)
    recalc(sal)
    # segunda pasada: tablas con el criterio de Manuales sobre la demanda nueva
    wv = load_workbook(sal, data_only=True)
    wb = load_workbook(sal)
    cap = [wv["parametros_manuales"].cell(19 + k, 13).value for k in range(25)]
    b6 = wv["parametros_manuales"]["B6"].value
    umbral = wv["parametros_manuales"]["B8"].value
    for rn, dn, _ in hojas:
        dem = [[wv[dn].cell(27 * i + 2 + k, 16).value / b6 for i in range(10)] for k in range(25)]
        plan = g.plan_capacidad(dem, cap, ["Máquina"] * 25, umbral, 2, ANIO_2T, piso=pisos[rn])
        escribir_tablas(wb[rn], 25, 30, 58, plan)
    wb.save(sal)
    recalc(sal)
    arreglar_dummy(sal)
    return sal, verif


def carros(ped):
    ent = os.path.join(REF, "Dimensionamiento_Carros.xlsx")
    sal = os.path.join(g.SALIDA, "Dimensionamiento_Carros.xlsx")
    wb = load_workbook(ent)
    verif = []
    links(wb)
    grises(wb)
    db = wb["datos_base"]
    imp(db, 2, 2, LK_PROY, "Indexado Dim Técnico!B7:K10", TERM_CAR)
    imp(db, 9, 2, LK_PROY, "Indexado Dim Técnico!B19:K22", CIL_CAR)
    modelos = ["Carro ABC 25 kg", "Carro ABC 50 kg", "Carro ABC 70 kg", "Carro ABC 100 kg"]
    fila_db = bloque_sustitutos(db, 34, modelos, PED_CAR, {p: v[4:] for p, v in ped.items()}, 2, 6,
                                "Sustitutos: paso 6 de sobrestock_sustitutos de cada Dimensionamiento de recargas. La "
                                "planta industrial los fabrica terminados (proceso completo); la comercial los recibe "
                                "como cilindro vacío y los carga allá.")
    db["A15"].value = "Total recipientes a fabricar (con sustitutos)"
    for i in range(10):
        c = L(2 + i)
        db[f"{c}15"].value = f"={c}6+{c}13+{c}39+{c}44"
    db["A24"].value = (db["A24"].value or "").replace(
        "Fuente: Dimensionamiento-Tecnico-FLAMA.xlsx, hoja DATOS-BASE: terminados filas 7 a 10 ('ABC 25/50/70/100 kg "
        "s/ruedas') y cilindros filas 19 a 22.",
        "Fuente: Proyecciones, Indexado Dim Técnico (IMPORTRANGE): terminados filas 7 a 10 y cilindros filas 19 a 22.")
    plan_sustitutos(wb["Plan mensual"], 112, fila_db, "parametros_carros", modelos)
    demanda_plan(wb["Demanda por puesto"], "parametros_carros", 18, 20, lambda p: "/60", 112, verif)
    pc = wb["parametros_carros"]
    pc["A8"].value = "Umbral de aprovechamiento"
    pc["C8"].value = ("Límite duro (análisis de riesgos): por encima se agrega máquina, operario o turno según el año "
                      "(Resumen Capacidad); con 2 turnos se agrega máquina. Ningún puesto queda por encima. El Word toma "
                      "80 % del turno como límite para una persona")
    ws = wb["Resumen Capacidad"]
    estilo(ws["M5"], ws["M6"])
    ws["M6"].value = "Revisar"
    ws["M6"].fill = PatternFill("solid", fgColor=g.COLOR_ACC["Revisar"], bgColor=g.COLOR_ACC["Revisar"])
    piso_c = piso(ws, 18, 23, 44, mitades(ws, 18), False)

    def util(k, i, mq, tu):
        return f"=IF({mq}*{tu}=0,0,'Demanda por puesto'!$P${20 * i + 2 + k}/({mq}*{tu}))"
    resumen(ws, 18, 23, 44, util, REC_CAR, "parametros_carros!$B$8", ("M8", "N8"), 9)
    wb.save(sal)
    recalc(sal)
    wv = load_workbook(sal, data_only=True)
    wb = load_workbook(sal)
    umbral = wv["parametros_carros"]["B8"].value
    dem = [[wv["Demanda por puesto"].cell(20 * i + 2 + k, 16).value for i in range(10)] for k in range(18)]
    plan = g.plan_capacidad(dem, [1] * 18, ["Máquina"] * 18, umbral, 2, ANIO_2T, piso=piso_c)
    escribir_tablas(wb["Resumen Capacidad"], 18, 23, 44, plan)
    wb.save(sal)
    recalc(sal)
    arreglar_dummy(sal)
    return sal, verif


if __name__ == "__main__":
    ped = pedidos()
    for f in (manuales, carros):
        ruta, verif = f(ped)
        print(ruta, "| fórmulas de demanda que no seguían el patrón:", len(verif))
        for v in verif[:5]:
            print("   ", v)
