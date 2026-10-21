"""Esquema_de_corte_en_guillotina.docx: un solo Word con el corte de los cuerpos de 1 a 100 kg (incluye el 1 kg en
chapa de 0,9 mm), las dos guillotinas en serie, la verificación de cuchillas y topes, las piezas del plano y los
discos por embutido. Los números salen del Excel Analisis_alternativas_corte_chapa.xlsx (hojas Corte, Datos,
Cálculo y Resumen); la geometría de las figuras se recalcula acá con el mismo criterio y se controla contra el Excel."""

import json
import math
import os
import subprocess
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import datos_corte as DC  # noqa: E402
import generar_comparacion_corte as GC  # noqa: E402

SALIDA = os.path.join(RAIZ, "salida")
XLSX = os.path.join(SALIDA, "Analisis_alternativas_corte_chapa.xlsx")
DOCX = os.path.join(SALIDA, "Esquema_de_corte_en_guillotina.docx")
NODE_PATH = os.environ.get("NODE_PATH", "/tmp/claude-0/-home-user-TP-optimizacion/"
                                        "15292aaf-e550-5dee-a83e-77fd9177a6ef/scratchpad/jw/node/node_modules")
NAR, VER, GRI = "#D9622B", "#2E7D5B", "#F6E3DA"
URL_QC = "https://www.alibaba.com/product-detail/QC12-Series-6mm-3-2m-Qc12Y_1600900259147.html"
URL_ERM = "https://resale.info/en/ermaksan-cnc-hgs-2600-6-cnc-shears/No-165879844"
URL_EUR = "https://www.poundsterlinglive.com/history/USD-EUR-2026"
COLS = "ABCDEFGHIJKLMNOPQRSTUVWXY"
CAMPOS = ["f", "B", "C", "ori", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
          "V", "W", "X", "ctrl"]


def n(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def nz(x, d=2):
    """Número con hasta d decimales, sin ceros de más."""
    s = n(x, d)
    return s.rstrip("0").rstrip(",") if "," in s else s


# ------------------------------------------------------------------ valores del Excel
def excel():
    wb = load_workbook(XLSX, data_only=True)
    co, da, ca, rs = wb["Corte"], wb["Datos"], wb["Cálculo"], wb["Resumen"]
    filas = []
    for r in range(GC.HS0, GC.HMIX + 1):
        filas.append({k: co[f"{COLS[j]}{r}"].value for j, k in enumerate(CAMPOS)})
    dat = {}
    for r in range(1, da.max_row + 1):
        if isinstance(da.cell(r, 1).value, str):
            dat[da.cell(r, 1).value] = da.cell(r, 2).value
    out = {"filas": filas, "dat": dat, "res": {rs.cell(r, 1).value: [rs.cell(r, c).value for c in range(2, 7)]
                                                 for r in range(4, 20) if rs.cell(r, 1).value}}
    for k in ("B_g1", "B_g2", "D_h"):
        out[k] = [ca.cell(GC.R[k], 3 + i).value for i in range(10)]
    out["u"] = [[ca.cell(GC.U0 + i, 3 + j).value for j in range(10)] for i in range(8)]
    return out


def maq(dat):
    def v(t):
        return next(x for k, x in dat.items() if k.startswith(t))
    return dict(gpm1=v("Guillotina 1 (franjas) Ermaksan"), L1=v("Guillotina 1: largo de corte"),
                tope1=v("Guillotina 1: recorrido"), gpm2=v("Guillotina 2 (piezas)"),
                L2=v("Guillotina 2: largo de corte"), tope2=v("Guillotina 2: recorrido"),
                ciclo=v("Hojas por ciclo"), mix100=v("Cuerpos de 100 kg"), mix70=v("Cuerpos de 70 kg"))


# ------------------------------------------------------------------ mismo criterio que la hoja Corte (control)
def corte(W, C, al, de, M, anchos=None, pieza=None):
    """1.er corte por el lado corto W: franjas de ancho a (a lo largo de C); 2.º corte de b (a lo ancho de W)."""
    def feas(a, b):
        return a <= M["tope1"] and a <= M["L2"] and W <= M["L1"] and (
            b <= M["tope2"] or (W // b == 1 and W - b <= M["tope2"]))
    if anchos is None:
        p1 = (C // al) * (W // de) if feas(al, de) else 0
        p2 = (C // de) * (W // al) if feas(de, al) else 0
        ori = 1 if p1 > p2 else 2 if p2 > p1 else (1 if C // al <= C // de else 2)
        a, b = (al, de) if ori == 1 else (de, al)
        anchos = [a] * int(C // a)
    else:
        ori, b = 1, pieza
    nf, h = len(anchos), int(W // b)
    cap = int(M["L2"] // min(anchos))
    tph = []
    for k in range(1, 5):
        if k > M["ciclo"]:
            tph.append(1e9)
            continue
        t = math.ceil(k * nf / cap)
        if len(set(anchos)) > 1:
            t = max(t, math.ceil(k * sum(anchos) / M["L2"]))
        tph.append(t / k)
    nc = tph.index(min(tph)) + 1
    tandas = round(tph[nc - 1] * nc)
    g1 = nf if C - sum(anchos) > 0.001 else nf - 1
    t2 = (b if b <= M["tope2"] else W - h * b)
    gt = (h if W - h * b > 0.001 else h - 1) if b <= M["tope2"] else 1
    g2 = gt * tandas / nc
    m1, m2 = g1 / M["gpm1"], g2 / M["gpm2"]
    return dict(W=W, C=C, ori=ori, anchos=anchos, E=max(anchos), F=nf, G=b, H=h, I=nf * h, L=t2, M=cap, N=nc,
                O=tandas, P=g1, Q=gt, R=g2, S=m1, T=m2, V=nf * h * 60 / max(m1, m2),
                por_tanda=math.ceil(nf * nc / tandas))


def controlar(X, M):
    """Cada fila de la hoja Corte tiene que dar lo mismo que el cálculo de las figuras."""
    geo = []
    for f in DC.FORM:
        al, de = DC.CUERPO[f][:2]
        geo.append(corte(DC.CUERPO[f][3], DC.CUERPO[f][4], al, de, M))
    a70, d70, a100 = DC.CUERPO["70 kg"][0], DC.CUERPO["70 kg"][1], DC.CUERPO["100 kg"][0]
    geo.append(corte(1500, 3000, None, None, M, anchos=[a100] * int(M["mix100"]) + [a70] * int(M["mix70"]),
                     pieza=d70))
    for x, y in zip(X["filas"], geo):
        for k in ("I", "F", "H", "N", "O", "P", "R"):
            assert abs(x[k] - y[k]) < 1e-6, (x["f"], k, x[k], y[k])
    return geo


# ------------------------------------------------------------------ figuras
def fig_proceso(ruta):
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 27)
    ax.axis("off")
    cajas = [(1, "Paquete de hojas\nen la mesa elevadora"),
             (23, "Guillotina 1\nErmaksan HGS 2600-6\n1.er corte por el\nlado corto: franjas"),
             (45, "Pulmón de franjas\n(carro porta-desarrollos)"),
             (67, "Guillotina 2\nQC12Y 6 × 2500\nfranjas de hojas enteras\nen paralelo: una pieza\nde cada una"),
             (89, "Desarrollos\na cilindrado")]
    for x, t in cajas:
        ax.add_patch(FancyBboxPatch((x, 8), 19, 15, boxstyle="round,pad=0.4", fc="#F2F2F2", ec="black", lw=1))
        ax.text(x + 9.5, 15.5, t, ha="center", va="center", fontsize=8.6)
    for x in (20.5, 42.5, 64.5, 86.5):
        ax.annotate("", xy=(x + 2.2, 15.5), xytext=(x, 15.5), arrowprops=dict(arrowstyle="-|>", lw=1.3))
    ax.text(55, 2.6, "G1 hace solo el 1.er corte y G2 solo el 2.º. En 70 y 100 kg la pieza (1.210,5 mm) supera los "
                     "topes: G2 corta la orilla de 289,5 mm.", ha="center", fontsize=8.5, color=NAR)
    fig.savefig(ruta, dpi=170, bbox_inches="tight")
    plt.close(fig)


def fig_formato(g, M, ruta, nombre):
    """Izquierda: la hoja con el 1.er corte (franjas por el lado corto) y el 2.º (piezas). Derecha: una tanda en G2."""
    W, C, anchos, b, h = g["W"], g["C"], g["anchos"], g["G"], g["H"]
    orilla = b > M["tope2"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw=dict(width_ratios=[1.3, 1]))
    a1.add_patch(Rectangle((0, 0), C, W, fc=GRI, ec="#333333", lw=1.2))
    x0 = 0
    for k, a in enumerate(anchos):
        a1.add_patch(Rectangle((x0, 0), a, h * b, fc="#E3F1EA", ec="none"))
        for j in range(1, h + 1):
            if j * b < W - 0.01:
                a1.plot([x0, x0 + a], [j * b, j * b], ls="--", color=VER, lw=1.1)
        a1.plot([x0 + a, x0 + a], [-W * 0.012, W * 1.012], color=NAR, lw=2.2)
        if len(anchos) <= 10:
            a1.text(x0 + a / 2, -W * 0.05, f"Franja {k + 1}", ha="center", va="top", fontsize=7, rotation=0
                    if a > C / 8 else 90)
        x0 += a
    a1.text(anchos[0] / 2, min(b, W) / 2, f"{nz(b, 1)}\n×\n{nz(anchos[0], 1)}", ha="center", va="center",
            fontsize=7.5, color=VER)
    a1.set_xlim(-C * 0.07, C * 1.02)
    a1.set_ylim(-W * 0.3, W * 1.12)
    a1.set_aspect("equal")
    a1.axis("off")
    a1.text(C / 2, W * 1.04, f"Hoja {n(C)} mm", ha="center", fontsize=9)
    a1.text(-C * 0.02, W / 2, f"{n(W)} mm\n(lado corto: paralelo\na la cuchilla de G1)", rotation=90, ha="right",
            va="center", fontsize=7.5)
    a1.plot([], [], color=NAR, lw=2, label="1.er corte (G1): franjas")
    a1.plot([], [], color=VER, ls="--", label="2.º corte (G2): " + ("orilla" if orilla else "piezas"))
    a1.add_patch(Rectangle((0, 0), 0, 0, fc=GRI, ec="#333333", label="Sobrante (scrap)"))
    a1.legend(loc="lower center", bbox_to_anchor=(0.5, -0.06), ncol=3, fontsize=7.5, frameon=False)
    # una tanda en G2
    L2, Lc = M["L2"], g["L"]
    tanda = anchos[:g["por_tanda"]] if len(set(anchos)) == 1 else [anchos[0], anchos[-1], anchos[-1]]
    largo = W - Lc
    a2.set_xlim(-L2 * 0.16, L2 * 1.04)
    a2.set_ylim(-largo * 1.32, Lc + W * 0.42)
    a2.axis("off")
    x0 = 0
    for a in tanda:
        a2.add_patch(Rectangle((x0 + 3, -largo), a - 6, largo, fc="#C6E3D3" if orilla else "#E3F1EA", ec=VER,
                               lw=0.9))
        a2.add_patch(Rectangle((x0 + 3, 0), a - 6, Lc, fc=GRI if orilla else "#C6E3D3", ec=VER, lw=0.9))
        x0 += a
    a2.plot([-L2 * 0.02, L2], [0, 0], color="#B00020", lw=3)
    a2.text(-L2 * 0.03, 0, "cuchilla", ha="right", va="center", fontsize=7.5, color="#B00020")
    a2.plot([0, L2], [Lc, Lc], color="black", ls=":", lw=1)
    a2.text(L2, Lc + W * 0.02, f"tope trasero a {nz(Lc, 1)} mm" + (" (orilla)" if orilla else ""), ha="right",
            va="bottom", fontsize=8)
    a2.annotate("", xy=(0, -largo * 1.1), xytext=(L2, -largo * 1.1), arrowprops=dict(arrowstyle="<->", lw=0.8,
                                                                                    color="#666666"))
    a2.text(L2 / 2, -largo * 1.16, f"{len(tanda)} franjas una al lado de la otra: {nz(sum(tanda), 1)} de "
                                   f"{n(L2)} mm", ha="center", va="top", fontsize=8)
    ciclo = ("las franjas de una hoja en cada tanda" if g["N"] == 1 and g["O"] == 1 else
             f"ciclo de {g['N']} hoja{'s' if g['N'] > 1 else ''}: {g['F'] * g['N']} franjas en {g['O']} tandas")
    que = "corta la orilla de" if orilla else "corta una pieza de cada una de"
    a2.text(L2 / 2, Lc + W * 0.3, f"2.º corte en la G2: cada golpe {que} {len(tanda)} franjas", ha="center",
            fontsize=8.5, weight="bold")
    a2.text(L2 / 2, Lc + W * 0.18, ciclo, ha="center", fontsize=8)
    fig.suptitle(nombre, fontsize=10, y=1.0)
    fig.tight_layout()
    fig.savefig(ruta, dpi=170, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ documento
def bloques(X, geo, M, tmp):
    b = []
    p, h1, h2, nota, bul = (lambda t: b.append({"t": "p", "x": t}), lambda t: b.append({"t": "h1", "x": t}),
                            lambda t: b.append({"t": "h2", "x": t}), lambda t: b.append({"t": "nota", "x": t}),
                            lambda t: b.append({"t": "b", "x": t}))

    def img(ruta, pie, ancho=16.5):
        import PIL.Image as Im
        w, hh = Im.open(ruta).size
        b.append({"t": "img", "ruta": ruta, "pie": pie, "ancho": ancho, "anchoPx": w, "alto": hh})

    F = X["filas"]
    b.append({"t": "titulo", "x": "Esquema de corte en guillotina"})
    b.append({"t": "sub", "x": "FLAMA S.A. · Cuerpos de 1 a 100 kg en hoja estándar, con dos guillotinas en serie: "
                               "G1 Ermaksan CNC HGS 2600-6 (franjas) y G2 QC12Y 6 × 2500 (piezas). Medidas de los "
                               "planos de recipiente. Números del Excel «Análisis alternativas corte chapa»."})
    h1("1. Cómo se corta")
    p("Cada cuerpo sale de dos cortes: el **1.er corte** separa la hoja en franjas y el **2.º corte** separa cada "
      "franja en piezas (desarrollos). Cada corte tiene su máquina:")
    bul(f"**Guillotina 1**, [Ermaksan CNC HGS 2600-6]({URL_ERM}): largo de corte {n(M['L1'])} mm, 6 mm de espesor, "
        f"tope trasero motorizado de {n(M['tope1'])} mm. La ficha da 24 golpes por minuto; se toman "
        f"{nz(M['gpm1'])}, como en el Dimensionamiento de Manuales. Hace **solo el 1.er corte**: la hoja entra con el "
        "lado corto paralelo a la cuchilla y el tope fija el ancho de la franja.")
    bul("**El 1.er corte va siempre por el lado corto de la hoja** (1.000, 1.220 o 1.500 mm). Una franja de 3.000 mm "
        "pesa el doble y el operario no la puede mover; así, la franja más larga mide 1.500 mm (sección 3).")
    bul("**Pulmón de franjas**: las franjas esperan en el carro porta-desarrollos entre las dos máquinas, así una no "
        "frena a la otra.")
    bul(f"**Guillotina 2**, [QC12Y 6 × 2500]({URL_QC}): cuchilla de 2.550 mm, tope de 20 a {n(M['tope2'])} mm, "
        f"{nz(M['gpm2'])} golpes por minuto. Hace **solo el 2.º corte**: se apoyan franjas una al lado de la otra, "
        f"hasta {n(M['L2'])} mm, y cada golpe corta una pieza de cada franja. En 70 y 100 kg la pieza (1.210,5 mm) "
        "supera los topes de las dos máquinas: la G2 corta la orilla de 289,5 mm y la pieza queda del lado del "
        "operario.")
    bul("**Franjas en paralelo, de hojas enteras.** En la G2 se apoyan las franjas de hojas completas, sin dejar "
        "franjas sueltas en el pulmón. Si en la G2 entran más franjas de las que da una hoja, se apoyan solo las de "
        "hojas enteras: con 3 franjas por hoja y lugar para 7, se apoyan 6, porque la 7.ª obliga a cortar otra hoja "
        "para una sola franja. Si la hoja da más franjas de las que entran, se arma un ciclo de hojas que se repite: "
        "con 3 franjas por hoja y lugar para 5, la tanda es de 5 y después de 4. Se elige el ciclo de hasta "
        f"{nz(M['ciclo'])} hojas que da menos tandas por hoja; si hay empate, el más corto.")
    p("El tiempo de cada máquina sale de sus golpes por minuto: golpes por hoja ÷ golpes por minuto. La línea rinde "
      "lo que rinde la más lenta de las dos. Los tiempos son a ritmo de máquina, sin manipulación.")
    ruta = os.path.join(tmp, "proceso.png")
    fig_proceso(ruta)
    img(ruta, "Figura 1. Recorrido de la chapa por las dos guillotinas.")

    h1("2. Resumen por formato")
    filas = []
    for x, g in zip(F, geo):
        par = (f"{g['por_tanda']} (1 hoja)" if g["N"] == 1 else f"{g['por_tanda']} (ciclo de {g['N']} hojas, "
                                                                 f"{g['O']} tandas)")
        filas.append([x["f"].replace("Hoja mixta ", "Mixta "), f"{n(x['B'])} × {n(x['C'])}",
                      nz(DC.CUERPO["100 kg" if x["f"].startswith("Hoja") else x["f"]][2], 2),
                      f"{x['F']} × {x['H']}", str(x["I"]), n(x["J"] * 100, 1) + " %", par, nz(x["P"], 2),
                      nz(x["R"], 2), f"{n(max(x['S'], x['T']), 2)} ({x['U']})", n(x["V"])])
    b.append({"t": "tabla", "cab": ["Formato", "Hoja (mm)", "e (mm)", "Franjas × piezas", "Piezas por hoja", "Aprov.",
                                    "Franjas por tanda en G2", "Golpes G1 por hoja", "Golpes G2 por hoja",
                                    "Min por hoja (manda)", "Cuerpos por hora"],
              "cols": [11, 11, 6, 8, 7, 7, 15, 7, 7, 10, 8], "filas": filas, "num": [2, 3, 4, 5, 7, 8, 9, 10]})
    nota("Cuerpos por hora: piezas por hoja × 60 ÷ minutos de la máquina que manda. El 70 kg se corta en la hoja "
         "mixta (1 de 100 kg y 3 de 70 kg), que aprovecha más la chapa que la hoja sola.")
    g1, g2 = X["B_g1"][-1], X["B_g2"][-1]
    p(f"Con la demanda de 2035 la G1 trabaja **{n(g1)} h** y la G2 **{n(g2)} h** al año a ritmo de máquina (hoja "
      "Cálculo del Excel, opción D).")

    h1("3. Verificación de cuchillas y topes")
    p("No alcanza con que la hoja entre a lo ancho de la cuchilla: el tope trasero (cuánto se mete la chapa hacia "
      "adentro) tiene que llegar a la medida de cada corte. Se verifica cada formato en las dos máquinas:")
    filas = []
    for x, g in zip(F, geo):
        apoy = (sum(sorted(g["anchos"], reverse=True)[:g["por_tanda"]]) if len(set(g["anchos"])) > 1 else
                g["por_tanda"] * x["E"])
        filas.append([x["f"].replace("Hoja mixta ", "Mixta "), n(x["B"]), nz(x["E"], 1), nz(x["K"], 1), nz(apoy, 1),
                      nz(x["L"], 1) + (" (orilla)" if x["G"] > M["tope2"] else ""), x["ctrl"]])
    b.append({"t": "tabla", "cab": ["Formato", f"G1: largo de corte (≤ {n(M['L1'])})",
                                    f"G1: tope = franja (≤ {n(M['tope1'])})", "Masa de la franja (kg)",
                                    f"G2: ancho apoyado (≤ {n(M['L2'])})",
                                    f"G2: tope = pieza u orilla (≤ {n(M['tope2'])})", "Control"],
              "cols": [10, 10, 10, 9, 10, 12, 18], "filas": filas, "num": [1, 2, 3, 4, 5]})
    nota("La franja más pesada es la del 100 kg (900 × 1.500 × 4,75 mm). Con el 1.er corte por el lado largo, las "
         "franjas medirían 3.000 mm y pesarían el doble.")

    h1("4. Esquemas por formato")
    k = 0
    for i, (x, g) in enumerate(zip(F, geo)):
        if x["f"] == "70 kg":
            continue
        k += 1
        nombre = x["f"] if x["f"].startswith("Hoja") else f"Cuerpo {x['f']}"
        h2(f"4.{k} {nombre}")
        ruta = os.path.join(tmp, f"f{i}.png")
        fig_formato(g, M, ruta, f"{nombre}: hoja {n(x['B'])} × {n(x['C'])} mm")
        img(ruta, f"Figura {k + 1}. {nombre}: 1.er corte por el lado corto en la G1 y 2.º corte en la G2.")
        orilla = x["G"] > M["tope2"]
        if x["f"].startswith("Hoja"):
            fr = (f"{n(M['mix100'])} franja de {nz(DC.CUERPO['100 kg'][0], 1)} mm y {n(M['mix70'])} de "
                  f"{nz(DC.CUERPO['70 kg'][0], 1)} mm, de {n(x['B'])} mm de largo")
        else:
            fr = f"{x['F']} franja{'s' if x['F'] > 1 else ''} de {nz(x['E'], 1)} × {n(x['B'])} mm"
        seg = (f"la G2 corta la orilla de {nz(x['L'], 1)} mm (la pieza de {nz(x['G'], 1)} mm supera el tope)"
               if orilla else f"la G2 corta piezas de {nz(x['G'], 1)} mm con el tope en {nz(x['L'], 1)} mm")
        cic = ("las franjas de una hoja en cada tanda" if g["N"] == 1 else
               f"un ciclo de {g['N']} hojas: {g['F'] * g['N']} franjas en {g['O']} tandas")
        p(f"1.er corte en la G1 con el tope en {nz(x['E'], 1)} mm: {fr}. 2.º corte: {seg}, con {cic}. Quedan "
          f"**{x['I']} cuerpos por hoja**, {nz(x['P'], 2)} golpes de G1 y {nz(x['R'], 2)} de G2 por hoja; "
          f"aprovechamiento {n(x['J'] * 100, 1)} %.")
        if x["f"] == "1 kg":
            b.extend(bloque_1kg(X, x, M))
    b.append({"t": "salto"})

    h1("5. Medidas de las piezas (planos)")
    p("Todas las medidas salen de los planos de recipiente (modelo 3D). El desarrollo es el **perímetro del cilindro** "
      "en la fibra media: desarrollo = π·(Ø exterior − espesor). Alto × desarrollo es la superficie de chapa del "
      "cuerpo. El alto es el del cuerpo del plano, con el labio del encastre.")
    filas = []
    for f in DC.FORM:
        al, de, e = DC.CUERPO[f][:3]
        filas.append([f, n(GC.DIAM[f], 1), n(e, 2), n(al, 1), n(de, 1), DC.PLANO[f]])
    b.append({"t": "tabla", "cab": ["Formato", "Ø ext. (mm)", "Espesor (mm)", "Alto (mm)", "Desarrollo (mm)", "Plano"],
              "cols": [10, 10, 10, 10, 11, 30], "filas": filas, "num": [1, 2, 3, 4]})
    h2("5.1 Disco de cúpulas y fondos: embutido")
    p("El disco no tiene el diámetro de la cúpula ni del fondo: al embutirlo, la chapa toma la profundidad de la pieza. "
      "Como el espesor casi no cambia, el disco tiene **la misma superficie que la pieza embutida** (Harsle, «How to "
      "Calculate Deep Drawing Parts»). Con las medidas del plano:")
    bul("**Cúpulas y fondo del 1 kg** (casquete): semielipsoide de semiejes a = Ø/2 − e/2 y b = altura − pollera − e/2, "
        "más una pollera recta de 6 mm. A = π·a² + π·b²/(2ε)·ln((1+ε)/(1−ε)) + 2π·a·p, con ε = √(1 − b²/a²).")
    bul("**Fondos de 2,5 a 10 kg** (cóncavos): paraboloide de radio ρ = Ø/2 − e/2 y profundidad h, más una pestaña "
        "recta de 10 mm. A = π/(6k²)·[(1 + 4k²ρ²)^1,5 − 1] + 2π·ρ·p, con k = h/ρ². Fórmulas de superficie de "
        "MathWorld.")
    bul("**Diámetro del disco**: D0 = √(4A/π), redondeado a 0,5 mm hacia arriba.")
    bul("**Relación de embutido**: m = d/D0, con d = 2a. Si m es mayor que m1 de la tabla del primer embutido (copa sin "
        "brida, con prensachapas; EasyChair, preprint Vxvp), sale en un solo golpe. Todas dan m entre 0,77 y 0,90 contra "
        "un m1 de 0,53 a 0,55.")
    bul("**Sin sobremedida de recorte**: la prensa corta y embute en el mismo golpe y no hay recorte después (W-MAN, "
        "puesto 4); además la tabla de sobremedida de recorte de Harsle arranca en h/d = 0,5 y estas piezas tienen h/d "
        "de 0,12 a 0,36.")
    filas = []
    for d in DC.DISC:
        filas.append([f"{d['pieza']} {d['formato']}", n(d["e"], 2), n(d["d_ext"], 1), n(d["h"], 1), n(d["A"]),
                      n(d["d0a"], 1), n(d["m"], 3), n(d["m1"], 2), n(d["ancho"], 1), n(d["paso"], 1)])
    b.append({"t": "tabla", "cab": ["Pieza", "e (mm)", "Ø (mm)", "h (mm)", "Área (mm²)", "Disco Ø (mm)", "m = d/D0",
                                    "m1 mín.", "Ancho de fleje (mm)", "Paso (mm)"],
              "cols": [12, 6, 7, 7, 9, 8, 8, 7, 9, 8], "filas": filas, "num": list(range(1, 10))})
    nota("Fleje: ancho = D0 + 2 × puente al borde y paso = D0 + puente de avance, con los puentes de MISUMI (1,5 veces "
         "el espesor, mínimo 0,7 mm; al borde, 1,5 veces el de avance).")

    h1("6. Resultado de la comparación de alternativas")
    res = X["res"]
    va = res["Valor actual a 10 años (USD)"]
    inv = res["Inversión en equipos (USD)"]
    p(f"Con el 1.er corte por el lado corto y la Ermaksan como G1, la **opción D** (hojas + fleje) sigue siendo la que "
      f"conviene de las que cortan en planta: valor actual de USD {n(va[3])}, contra {n(va[0])} de A, {n(va[1])} de B y "
      f"{n(va[2])} de C. La inversión de D es de USD {n(inv[3])}. La hoja tendría que subir "
      f"{n(res['Margen de D: suba del precio de la hoja que la iguala con A'][0] * 100, 1)} % para que A la iguale. El "
      "detalle está en el Excel «Análisis alternativas corte chapa» (hojas Resumen y Cálculo).")
    h1("7. Pendiente")
    bul("Precio de la G1: la Ermaksan se tomó de un anuncio de máquina usada (2018) en euros, sin flete ni "
        "nacionalización. Hay que pedir cotización.")
    bul("Precio de la G2 puesta en planta: los USD 10.700 son FOB, sin flete ni nacionalización.")
    bul("Mandril de la soldadora longitudinal TIG del 1 kg: confirmar con Firesafer que entra en el interior de "
        "74,4 mm.")
    h1("Fuentes")
    for t in [f"[Ermaksan CNC HGS 2600-6, anuncio resale.info N.° 165879844]({URL_ERM}): 2.600 × 6 mm, 24 golpes por "
              "minuto, tope trasero de 1.000 mm, EUR 26.000 (usada, 2018).",
              f"[Pound Sterling Live, USD/EUR 2026]({URL_EUR}): 0,8723 al cierre del 21/09/2026.",
              f"[Publicación Alibaba 1600900259147, QC12Y 6 × 2500]({URL_QC}): cuchilla 2.550 mm, tope 20-800 mm, "
              "USD 10.700 FOB.",
              "Molinari Maquinarias, ficha de la guillotina Panther HG (formulario de cotización): HG 6 × 2500, 20 golpes "
              "por minuto.",
              "Dimensionamiento de Manuales del grupo: golpes por minuto de G1 y G2; soldadora longitudinal TIG Firesafer "
              "para el 1 kg.",
              "IRAM 3523 (matafuegos de polvo bajo presión): 3.2.1 a), 3.2.4.1 y 3.2.4.2.",
              "[MISUMI, Press Dies Tutorial: puentes de corte](https://www.misumi-techcentral.com/tt/en/press/2009/09/"
              "012-basics-of-blanking-work-1-blanking-work.html).",
              "[Harsle, How to Calculate Deep Drawing Parts](https://harslepress.com/how-to-calculate-deep-drawing-parts/).",
              "[EasyChair, preprint Vxvp: relación de embutido m1](https://easychair.org/publications/preprint/Vxvp).",
              "[MathWorld, Oblate Spheroid](https://mathworld.wolfram.com/OblateSpheroid.html) y "
              "[Paraboloid](https://mathworld.wolfram.com/Paraboloid.html).",
              "Hierros Parrotta, presupuesto 413329; Pradecon 173170 y 173195; Pacheco Chapas PR 42021 y 42024."]:
        bul(t)
    return b


def bloque_1kg(X, x, M):
    """Detalle del 1 kg en chapa de 0,9 mm (antes, Word aparte)."""
    b = []
    al, de, e = DC.CUERPO["1 kg"][:3]
    u35 = X["u"][0][-1]
    h35 = u35 / x["I"]
    b.append({"t": "h3", "x": "Pieza, chapa y tiempos del 1 kg"})
    filas = [["Ø exterior del cuerpo", "76,2 mm", DC.PLANO["1 kg"]],
             ["Alto del cuerpo", f"{n(al, 1)} mm", "Cuerpo del modelo 3D con los dos labios del encastre"],
             ["Desarrollo", f"{n(de, 1)} mm = π·(76,2 − 0,9)", "Perímetro del cilindro en la fibra media"],
             ["Hoja", "1.220 × 2.440 × 0,9 mm", "Hierros Parrotta, presupuesto 413329 (28/09/2026)"],
             ["Precio de la hoja", "USD 1,356/kg sin IVA", "Hierros Parrotta, con 6,84 % de descuento, contado"],
             ["Ritmo de la línea", f"{n(x['V'])} cuerpos por hora (manda la {x['U']})",
              f"{nz(M['gpm1'])} golpes por minuto la G1 y {nz(M['gpm2'])} la G2"],
             ["Año 2035", f"{n(u35)} cuerpos = {n(h35)} hojas", f"G1 {n(h35 * x['S'] / 60)} h y G2 "
                                                                f"{n(h35 * x['T'] / 60)} h al año"]]
    b.append({"t": "tabla", "cab": ["Dato", "Valor", "Fuente o cálculo"], "cols": [9, 14, 16], "filas": filas})
    filas = []
    for W, C in ((1220, 2440), (1000, 2000)):
        y = corte(W, C, al, de, M)
        filas.append([f"{n(W)} × {n(C)}", f"{y['F']} × {y['H']}", str(y["I"]),
                      n(y["I"] * al * de / (W * C) * 100, 1) + " %", nz(y["P"], 2), nz(y["R"], 2),
                      n(max(y["S"], y["T"]), 2)])
    b.append({"t": "h3", "x": "Hojas evaluadas para el 1 kg (1.er corte por el lado corto)"})
    b.append({"t": "tabla", "cab": ["Hoja (mm)", "Franjas × piezas", "Cuerpos", "Aprov.", "Golpes G1", "Golpes G2",
                                    "Min por hoja"], "cols": [12, 9, 7, 7, 7, 7, 8], "filas": filas,
              "num": [2, 3, 4, 5, 6]})
    b.append({"t": "p", "x": "Se elige la hoja de 1.220 × 2.440: da 45 cuerpos contra 28 y aprovecha más. Las orillas de "
                             "37,5 mm y los recortes de 68,5 mm no sirven para discos (la cúpula del 1 kg necesita un "
                             "fleje de 93 mm)."})
    b.append({"t": "b", "x": "Espesor: la IRAM 3523, 3.2.1 a), pide chapa de acero al carbono de 0,71 mm como mínimo; "
                             "0,9 mm cumple. La 3.2.4.1 admite una costura longitudinal y dos transversales."})
    b.append({"t": "b", "x": "El cuerpo de chapa se cilindra y lleva soldadura longitudinal TIG, que el caño no tenía: "
                             "proceso automático en atmósfera inerte, admitido por la IRAM 3523, 3.2.4.2. Se adoptó la "
                             "soldadora longitudinal Firesafer con fuente TIG (Dimensionamiento de Manuales)."})
    return b


def render(bl, salida, pie):
    js = os.path.join(AQUI, "word_corte.js")
    tmpj = salida + ".json"
    with open(tmpj, "w", encoding="utf-8") as fh:
        json.dump(bl, fh, ensure_ascii=False)
    env = dict(os.environ, NODE_PATH=NODE_PATH)
    subprocess.run(["node", js, tmpj, salida, pie], check=True, env=env)
    os.remove(tmpj)


def main():
    X = excel()
    M = maq(X["dat"])
    geo = controlar(X, M)
    tmp = tempfile.mkdtemp(prefix="figs_corte_")
    render(bloques(X, geo, M, tmp), DOCX, "Esquema de corte en guillotina")
    print("ok", DOCX, tmp)


if __name__ == "__main__":
    main()
