"""Arma simple/index.html (trazabilidad interna FLAMA, sin QR) desde plantilla.html + app.js con los datos de los libros
de referencias/extra_fran:
  MP-FLAMA2035.xlsx        Stock_MP (las 125 MP: seguridad, consumo mientras llega, stock máximo, bulto, almacén) y
                           Almacenes (lugares y cómo se dispone cada almacén)
  PTPINTADO-FLAMA2035.xlsx Stock_PT (stock máximo y pallets de cada producto), Almacen_PT (rack, piso, andén) y
                           Despacho (días fijos de cada vehículo)
  Balanceo-FLAMA2035.xlsx  Carga (puestos de manuales, carros y recargas, con su número)
y de la app de gestión interna FLAMA (APP_SISTEMA_DE_GESTION_INTERNA_FLAMA): el plano rev10 (layout_rev10.json, copia de
public/data/layout.json) y los logos (img/), para que las dos apps se vean y se ubiquen igual.
Los registros (conteos, pedidos, formularios, pallets) no se inventan: arrancan vacíos y los carga la app.
Uso: python3 build.py"""
import base64
import json
import math
import os

from openpyxl import load_workbook

AQUI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "referencias", "extra_fran")


def libro(nombre):
    return load_workbook(os.path.join(REF, nombre), data_only=True)


def r1(x, d=1):
    return round(float(x), d) if isinstance(x, (int, float)) else None


def stock_mp(wb):
    """Una fila por MP (Stock_MP filas 6 a 130). Punto de pedido = seguridad + consumo mientras llega (L + K): el
    stock que tiene que quedar cuando sale el pedido para que la entrega llegue antes de tocar la seguridad."""
    out = []
    for i, r in enumerate(wb["Stock_MP"].iter_rows(min_row=6, max_row=130, values_only=True), 6):
        if not r[1]:
            continue
        ss, k, mx, cont = float(r[11] or 0), float(r[10] or 0), float(r[18] or 0), float(r[13] or 1)
        out.append(dict(ref=r[0], cod=r[1], mat=r[2], um=r[3], prov=r[4], pico=r1(r[7], 2), pmin=r[8], pmax=r[9],
                        ss=r1(ss), k=r1(k), pp=r1(ss + k), max=r1(mx), bulto=r[12], cont=cont, cada=r[14],
                        alm=r[17], u=(r1(r[20], 3) if isinstance(r[20], (int, float)) else 0),
                        guarda=r[21], linea=r[22], fila=i))
    return out


def almacenes(wb):
    out = []
    for r in wb["Almacenes"].iter_rows(min_row=19, max_row=31, values_only=True):
        if r[0]:
            out.append(dict(alm=r[0], que=r[1], est=r[2], lug=r[4], m2=r1(r[6]), como=r[8]))
    return out


def stock_pt(wb):
    ws = wb["Stock_PT"]
    out = []
    for r in ws.iter_rows(min_row=63, max_row=78, values_only=True):
        out.append(dict(prod=r[0], ventas=r1(r[1], 0), dia=r1(r[5]), ss=r[7], max=r1(r[9], 0), porp=r[10],
                        pallets=r[11]))
    a = {r[0]: r[1] for r in wb["Almacen_PT"].iter_rows(min_row=7, max_row=31, values_only=True) if r[0]}
    carros = {r[0]: r[1] for r in wb["Almacen_PT"].iter_rows(min_row=22, max_row=25, values_only=True) if r[0]}
    desp = [dict(veh=r[0], dias=r[3], salidas=r[2]) for r in wb["Despacho"].iter_rows(min_row=25, max_row=28,
                                                                                         values_only=True) if r[0]]
    return out, dict(modulos=a["Módulos de rack"], lugares=a["Lugares que da el rack"], anden=a["Lugares de pallet en el andén"],
                     pesados=a["Pallets que van solo en el piso (más de la mitad de la carga del nivel)"]), carros, desp


def puestos(wb):
    """Puestos del balanceo (hoja Carga): manuales filas 34 a 59, carros 74 a 91, recargas 104 a 126."""
    ws = wb["Carga"]
    pz = lambda a, b: [dict(n=str(r[0]), nom=r[1]) for r in ws.iter_rows(min_row=a, max_row=b, values_only=True)
                       if r[0] is not None and r[1]]
    return dict(man=pz(34, 59), car=pz(74, 91), rec=pz(104, 126))


# Lugares de cada almacén (Almacenes, col. E) en el orden en que se recorren. Rack selectivo: módulo de 2 pallets por nivel,
# piso + 2 largueros (Word de MP, sección 8); el de flejes lleva 4 alturas (sección 6.2: largueros cada 75 cm). Lo demás va en
# el piso o en estantes: pilas, brazos, estantes o lugares de la jaula, uno al lado del otro.
PREF = {"Chapa (pilas en el piso)": "CH", "Flejes (rack + volteador)": "FL", "Cantilever de caños y barras": "CA",
        "Depósito de polvo químico": "PQ", "Embalaje": "EM", "Identificación": "ID", "Insumos de montaje (manuales)": "IM",
        "Insumos de recargas": "IR", "Insumos de soldadura y superficie": "SO", "Jaula de gases": "GA",
        "Rack de casquetes y cuplas (carros)": "CC", "Rack de insumos de montaje (carros)": "IC",
        "Almacén de producto terminado": "RV"}
CORTO = {"Chapa (pilas en el piso)": "Chapa", "Flejes (rack + volteador)": "Flejes", "Cantilever de caños y barras": "Cantilever",
         "Depósito de polvo químico": "Polvo", "Embalaje": "Embalaje", "Identificación": "Identificación",
         "Insumos de montaje (manuales)": "Ins. manuales", "Insumos de recargas": "Ins. recargas",
         "Insumos de soldadura y superficie": "Soldadura", "Jaula de gases": "Gases", "Rack de casquetes y cuplas (carros)": "Casquetes",
         "Rack de insumos de montaje (carros)": "Ins. carros", "Almacén de producto terminado": "Reventa (PT)"}


def huecos(a, n):
    """Lugares de un almacén en orden: en los racks, columna por columna de abajo hacia arriba (abajo lo que se usa,
    arriba la reposición, Word de MP sección 8), así los lugares de un mismo código quedan apilados."""
    p = PREF[a["alm"]]
    if a["alm"] == "Almacén de producto terminado":
        return [dict(id=f"RV-{i + 1:02d}") for i in range(n)]
    if "Rack" in (a["est"] or ""):
        niv = 4 if p == "FL" else 3
        out = []
        for m in range(math.ceil(n / (2 * niv))):
            for lado in "AB":
                for k in range(1, niv + 1):
                    out.append(dict(id=f"{p}{m + 1:02d}-{k}{lado}", mod=m + 1, niv=k, lado=lado))
        return out[:n] if len(out) == n else sorted(out, key=lambda x: (x["mod"], x["lado"], x["niv"]))[:n]
    return [dict(id=f"{p}-{i + 1:02d}") for i in range(n)]


def repartir(ms, n):
    """Lugar fijo de cada código («cada código tiene su lugar fijo», Word de MP sección 8). Criterio: cada código ocupa
    los lugares enteros de su columna U de Stock_MP; los restos se juntan en lugares compartidos (de mayor a menor, en el
    primero donde entran). Si así no alcanzan los lugares de la hoja Almacenes, se llenan de corrido en el orden de
    Stock_MP. Devuelve, por lugar, la lista de (código, fracción del lugar)."""
    llenos, restos = [], []
    for m in ms:
        k = int(m["u"] + 1e-9)
        r = m["u"] - k
        llenos += [[(m["cod"], 1.0)] for _ in range(k)]
        if r > 0.02 or (k == 0 and m["u"] > 0):
            restos.append((m["cod"], max(r, 0.01)))
    comp = []
    for c, r in sorted(restos, key=lambda x: -x[1]):
        for b in comp:
            if sum(f for _, f in b) + r <= 1 + 1e-9:
                b.append((c, r))
                break
        else:
            comp.append([(c, r)])
    if len(llenos) + len(comp) <= n:
        return llenos + comp
    # no entra con lugares enteros: se llenan los lugares de corrido, en el orden de la hoja (un código toca 2 lugares)
    out, acc = [[] for _ in range(n)], 0.0
    for m in ms:
        u = m["u"]
        while u > 1e-6:
            i = min(n - 1, int(acc + 1e-9))
            t = min(u, i + 1 - acc) if i < n - 1 else u
            out[i].append((m["cod"], t))
            acc, u = acc + t, u - t
    return [b for b in out if b]


def lugares(mp, alms):
    out = {}
    for a in alms:
        ms = [m for m in mp if m["alm"] == a["alm"]]
        n = a["lug"] if isinstance(a["lug"], int) else math.ceil(sum(m["u"] for m in ms))
        pos, rep = huecos(a, n), repartir(ms, n)
        assert len(rep) <= n, (a["alm"], len(rep), n)
        for i, h in enumerate(pos):
            h["cods"] = [[c, round(f, 2)] for c, f in (rep[i] if i < len(rep) else [])]
        out[a["alm"]] = pos
        for m in ms:
            m["lugares"] = [h["id"] for h in pos if any(c == m["cod"] for c, _ in h["cods"])]
    return out


def planilla(mp, alms, lug, ruta):
    """Planilla de conteo del almacén de MP: una hoja por almacén, en el orden de los lugares. Se completa la columna
    «Stock contado» y la app la levanta (Kanban de MP › Cargar planilla)."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.datavalidation import DataValidation
    wb = Workbook()
    ins = wb.active
    ins.title = "Instrucciones"
    f = "Arial"
    gris, amarillo = PatternFill("solid", fgColor="E7E9EC"), PatternFill("solid", fgColor="FFF4C2")
    fino = Side(style="thin", color="B9BEC5")
    borde = Border(left=fino, right=fino, top=fino, bottom=fino)
    txt = ["Planilla de conteo del almacén de MP · FLAMA 2035",
           "",
           "1. Imprimir la hoja del almacén que toca contar (o abrirla en la tablet).",
           "2. Recorrer los lugares en el orden de la hoja y anotar en «Stock contado» lo que hay, en la unidad de la columna UM.",
           "3. Completar la fecha y quién contó, arriba de la tabla.",
           "4. En la app: Kanban de MP › Cargar planilla › elegir este archivo. La app lee todas las hojas y mueve las tarjetas.",
           "",
           "Solo se completan las celdas amarillas. «Estado» se calcula solo contra la seguridad y el punto de pedido.",
           "Cuándo se cuenta: en cada revisión periódica del proveedor (cada 10, 20 o 60 días hábiles según el código, Word de MP",
           "sección 9) y siempre que un retiro deje una tarjeta cerca del punto de pedido.",
           "",
           "Fuentes: MP-FLAMA2035.xlsx › Stock_MP (L seguridad, K consumo mientras llega, S máximo, U lugares) y Almacenes (lugares).",
           "Punto de pedido = L + K. Lugar de cada código: criterio de reparto explicado en el Word de trazabilidad (sección 3)."]
    for i, t in enumerate(txt, 1):
        ins.cell(i, 1, t).font = Font(name=f, bold=(i == 1), size=13 if i == 1 else 10)
    ins.column_dimensions["A"].width = 120
    cab = ["Lugar", "Código", "Material", "UM", "Se compra en", "Seguridad", "Punto de pedido", "Máximo", "Stock contado", "Estado", "Observaciones"]
    anchos = [16, 14, 46, 7, 26, 11, 11, 11, 13, 16, 28]
    for a in alms:
        ws = wb.create_sheet(CORTO[a["alm"]])
        ws["A1"] = f"Conteo · {a['alm']}"
        ws["A1"].font = Font(name=f, bold=True, size=13)
        ws["A2"] = f"{a['est']} · {len(lug[a['alm']])} lugares · {a['como'] or ''}"[:250]
        ws["A2"].font = Font(name=f, size=9, color="59626D")
        ws["A3"], ws["C3"] = "Fecha del conteo", "Contó"
        for c in ("A3", "C3"):
            ws[c].font = Font(name=f, bold=True, size=10)
        for c in ("B3", "D3"):
            ws[c].fill, ws[c].border = amarillo, borde
        ws.merge_cells("D3:E3")
        ws["B3"].number_format = "dd/mm/yyyy"
        for j, (t, w) in enumerate(zip(cab, anchos), 1):
            c = ws.cell(5, j, t)
            c.font, c.fill, c.border = Font(name=f, bold=True, size=10), gris, borde
            c.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[c.column_letter].width = w
        fila = 6
        orden = {h["id"]: i for i, h in enumerate(lug[a["alm"]])}
        ms = sorted([m for m in mp if m["alm"] == a["alm"]], key=lambda m: orden.get((m["lugares"] or ["~"])[0], 999))
        for m in ms:
            vals = [", ".join(m["lugares"]), m["cod"], m["mat"], m["um"], m["bulto"], m["ss"], m["pp"], m["max"]]
            for j, v in enumerate(vals, 1):
                c = ws.cell(fila, j, v)
                c.font, c.border = Font(name=f, size=10), borde
                if j in (6, 7, 8):
                    c.number_format = "#,##0.0"
            ws.cell(fila, 9).fill = amarillo
            ws.cell(fila, 9).number_format = "#,##0.0"
            ws.cell(fila, 10, f'=IF(I{fila}="","",IF(I{fila}<=F{fila},"BAJO SEGURIDAD",IF(I{fila}<=G{fila},"PEDIR","OK")))')
            for j in (9, 10, 11):
                ws.cell(fila, j).border = borde
                ws.cell(fila, j).font = Font(name=f, size=10, bold=(j == 10))
            fila += 1
        dv = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True,
                            error="El stock contado es un número mayor o igual a cero")
        ws.add_data_validation(dv)
        dv.add(f"I6:I{fila - 1}")
        ws.freeze_panes = "C6"
        ws.print_title_rows = "5:5"
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(ruta)


def main():
    mp = libro("MP-FLAMA2035.xlsx")
    pt = libro("PTPINTADO-FLAMA2035.xlsx")
    bal = libro("Balanceo-FLAMA2035.xlsx")
    spt, apt, carros, desp = stock_pt(pt)
    layout = json.load(open(os.path.join(AQUI, "layout_rev10.json"), encoding="utf-8"))
    cat = json.load(open(os.path.join(AQUI, "catalogo_gestion.json"), encoding="utf-8"))
    smp, alms = stock_mp(mp), almacenes(mp)
    lug = lugares(smp, alms)
    for a in alms:
        a["lug"], a["corto"], a["pref"] = len(lug[a["alm"]]), CORTO[a["alm"]], PREF[a["alm"]]
    D = dict(mp=smp, layout=layout, cat=cat, alm=alms, lugares=lug, pt=spt, apt=apt, carros=carros, desp=desp, puestos=puestos(bal),
             fuente=dict(mp="MP-FLAMA2035.xlsx › Stock_MP (filas 6 a 130) y Almacenes (filas 19 a 31)",
                         pt="PTPINTADO-FLAMA2035.xlsx › Stock_PT (filas 63 a 78), Almacen_PT y Despacho (filas 25 a 28)",
                         bal="Balanceo-FLAMA2035.xlsx › Carga (manuales 34-59, carros 74-91, recargas 104-126)"))
    html = open(os.path.join(AQUI, "plantilla.html"), encoding="utf-8").read()
    # caminos.js es el de la app de gestión (A* por los pasillos); va sin el «export» porque todo queda en un solo archivo
    js = (open(os.path.join(AQUI, "caminos.js"), encoding="utf-8").read().replace("export function", "function") + "\n"
          + open(os.path.join(AQUI, "app.js"), encoding="utf-8").read())
    for marca, archivo in (("/*LOGO_LLAMA*/", "logo-llama.png"), ("/*LOGO_PALABRA*/", "logo-palabra.png")):
        b64 = base64.b64encode(open(os.path.join(AQUI, "img", archivo), "rb").read()).decode()
        html = html.replace(marca, "data:image/png;base64," + b64)
    html = html.replace("/*DATOS*/", "const D = " + json.dumps(D, ensure_ascii=False) + ";").replace("/*APP*/", js)
    # index.html completo (para Vercel o abrir local) y artifact.html sin envoltorio (lo arma el visor de artifacts)
    with open(os.path.join(AQUI, "artifact.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    with open(os.path.join(AQUI, "index.html"), "w", encoding="utf-8") as fh:
        fh.write('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
                 '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                 + html.replace("<style>", "<style>\nbody { margin: 0 }", 1)
                 .replace('<div class="contexto">', '</head>\n<body>\n<div class="contexto">', 1) + "\n</body>\n</html>\n")
    salida = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "salida")
    os.makedirs(salida, exist_ok=True)
    planilla(smp, alms, lug, os.path.join(salida, "Planilla_conteo_MP.xlsx"))
    print("ok", len(D["mp"]), "MP ·", len(D["pt"]), "productos de PT ·",
          {k: len(v) for k, v in D["puestos"].items()}, "puestos")


if __name__ == "__main__":
    main()
