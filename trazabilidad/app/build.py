"""Arma app/index.html (POC de la app de trazabilidad) desde plantilla.html + js/*.js + img/*.webp: lee el Plan mensual real de los Excel de
Aprovechamiento (como hará la app con Google Sheets), arma los lotes del mes, reserva las series y genera los QR reales
(segno) del lote de ejemplo. Uso: python3 build.py [año] [mes 1-12]."""
import base64
import json
import os
import sys

import segno
from openpyxl import load_workbook

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "salida")
URL = "https://trazabilidad-flama.vercel.app/m/"
JS = ["base.js", "recorrido.js", "clientes.js", "manual.js", "desvios.js", "inicio.js", "app.js"]   # orden de carga
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
# tamaño de lote = lo que entra en el carro de transporte interno del modelo (criterio de la POC, lo fija PCP)
LOTE = {"ABC 1 kg": 60, "ABC 2,5 kg": 48, "ABC 5 kg": 48, "ABC 10 kg": 24, "Carro ABC 25 kg": 4, "Carro ABC 50 kg": 4,
        "Carro ABC 70 kg": 2, "Carro ABC 100 kg": 2}


def plan(archivo, anio):
    """Filas del año en la hoja «Plan mensual»: [(producto, tipo, [12 valores])] y el rango leído."""
    ws = load_workbook(os.path.join(SALIDA, archivo), read_only=True, data_only=True)["Plan mensual"]
    filas, desde, hasta = [], None, None
    for i, r in enumerate(ws.iter_rows(values_only=True), 1):
        if r[0] == anio and r[1] not in (None, "Producto"):
            filas.append((r[1], r[2], [float(x or 0) for x in r[3:15]]))
            desde = desde or i
            hasta = i
    return filas, f"A{desde}:P{hasta}"


def qr_path(texto):
    m = segno.make(texto, error="m").matrix
    d = []
    for y, fila in enumerate(m):
        x = 0
        while x < len(fila):
            if fila[x]:
                x0 = x
                while x < len(fila) and fila[x]:
                    x += 1
                d.append(f"M{x0} {y}h{x - x0}v1h{x0 - x}z")
            else:
                x += 1
    return {"n": len(m), "d": "".join(d)}


def imagenes():
    """app/img/*.webp (las arma imagenes.py) como data URI: la página es un solo archivo."""
    carpeta = os.path.join(AQUI, "img")
    return {os.path.splitext(f)[0]: "data:image/webp;base64," + base64.b64encode(open(os.path.join(carpeta, f), "rb").read()).decode()
            for f in sorted(os.listdir(carpeta)) if f.endswith(".webp")} | \
        {"familia_x": json.load(open(os.path.join(carpeta, "familia.json")))}


def logo():
    """Logo oficial si está en app/logo.svg o app/logo.png; si no, la app usa la marca provisoria."""
    for nombre, tipo in (("logo.svg", "image/svg+xml"), ("logo.png", "image/png")):
        ruta = os.path.join(AQUI, nombre)
        if os.path.exists(ruta):
            return f"data:{tipo};base64," + base64.b64encode(open(ruta, "rb").read()).decode()
    return None


def main(anio=2026, mes=3):
    man, rango_m = plan("Aprovechamiento_Manuales.xlsx", anio)
    car, rango_c = plan("Aprovechamiento_Carros.xlsx", anio)
    k = mes - 1
    # las series del año son correlativas para todos los modelos: el mes arranca donde terminó el anterior
    previas = sum(round(v[j]) for _, t, v in man + car for j in range(k) if t == "Terminado")
    serie = previas + 1
    lotes, filas = [], []
    for prod, tipo, v in man + car:
        cant = round(v[k])
        filas.append({"producto": prod, "tipo": tipo, "valor": round(v[k], 2), "cant": cant,
                      "origen": "Aprovechamiento_Carros" if prod.startswith(("Carro", "Cilindros ABC 25",
                                                                              "Cilindros ABC 50", "Cilindros ABC 70",
                                                                              "Cilindros ABC 100"))
                      else "Aprovechamiento_Manuales"})
        if tipo != "Terminado" or cant == 0:
            continue
        tam = LOTE.get(prod, 48)
        n = 0
        while n < cant:
            c = min(tam, cant - n)
            lotes.append({"op": f"OP {anio % 100:02d}-{mes:02d}-{len(lotes) + 1:02d}", "modelo": prod, "cant": c,
                          "desde": serie, "hasta": serie + c - 1, "lote": tam})
            serie += c
            n += c
    demo = next(x for x in lotes if x["modelo"] == "ABC 5 kg")
    aa = anio % 100
    series = [f"{aa:02d}-{s:06d}" for s in range(demo["desde"], demo["hasta"] + 1)]
    qr = {s: qr_path(URL + s) for s in series}
    qr["OP"] = qr_path("OP:" + demo["op"])
    qr["REMITO"] = qr_path("https://trazabilidad-flama.vercel.app/r/0001-00004521")
    qr["SSCC"] = qr_path("https://trazabilidad-flama.vercel.app/p/00077900000004574")
    datos = {"anio": anio, "mes": mes, "mesNombre": MESES[k], "rangos": {"man": rango_m, "car": rango_c},
             "filas": filas, "lotes": lotes, "demo": dict(demo, series=series), "qr": qr, "url": URL,
             "previas": previas}
    with open(os.path.join(AQUI, "plantilla.html"), encoding="utf-8") as fh:
        html = fh.read()
    html = html.replace("/*__DATOS__*/null", json.dumps(datos, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("/*__IMG__*/null", json.dumps(imagenes()))
    html = html.replace("/*__LOGO__*/null", json.dumps(logo()))
    html = html.replace("/*__JS__*/", "\n".join(open(os.path.join(AQUI, "js", f), encoding="utf-8").read() for f in JS))
    with open(os.path.join(AQUI, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print("ok", demo["op"], series[0], "…", series[-1], len(lotes), "lotes")


if __name__ == "__main__":
    main(*(int(x) for x in sys.argv[1:3]))
