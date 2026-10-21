"""Esquema_de_corte_en_guillotina.docx: un solo Word con el corte de los cuerpos de 1 a 100 kg (incluye el 1 kg en
chapa de 0,9 mm), las dos guillotinas en serie, la verificación de cuchillas y topes, el nesting (¿es el mejor corte?),
las piezas del plano, el esquema de embutido de cúpulas y fondos y las guillotinas compartidas por manuales y carros.
Los números salen del Excel Analisis_alternativas_corte_chapa.xlsx (hojas Corte, Datos, Nesting, Cálculo y Resumen) y
del Aprovechamiento de Manuales (tiempos con manipulación); la geometría de las figuras se recalcula acá con el mismo
criterio y se controla contra el Excel."""

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
MAN = os.path.join(SALIDA, "Aprovechamiento_Manuales.xlsx")
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
    for k in ("B_g1", "B_g2", "D_h", "B_p1", "B_p3", "B_p4"):
        out[k] = [ca.cell(GC.R[k], 3 + i).value for i in range(10)]
    out["u"] = [[ca.cell(GC.U0 + i, 3 + j).value for j in range(10)] for i in range(8)]
    ne = wb["Nesting"]

    def bloque(ws, r0, n_, c1=1, c2=15):
        return [[ws.cell(r0 + k, c).value for c in range(c1, c2 + 1)] for k in range(n_)]
    out["cand"] = bloque(ne, GC.NA0, len(GC.CAND))
    out["pat"] = bloque(ne, GC.NP0, len(GC.PAT32))
    r = fila(ne, "Controles de P1")
    out["ctl"] = bloque(ne, r + 2, 5)
    r = fila(ne, "Plan del año de referencia")
    out["plan"] = {x[0]: x[1:4] for x in bloque(ne, r + 2, 6)}
    out["prom"] = [x[1] for x in bloque(ne, GC.NPROM, 4)]
    out["p475"] = bloque(ne, GC.NC0, len(GC.PAT475))
    out["dsc"] = bloque(ne, GC.ND0, len(DC.DISC) + 1)
    out["cor_d"] = [{k: v for k, v in zip(COLS, x)} for x in bloque(co, GC.DC0, len(DC.DISC), 1, 25)]
    out["anio"] = int(dat["Año de referencia"])
    # tiempos con manipulación y guillotinas compartidas (Aprovechamiento de Manuales)
    wm = load_workbook(MAN, data_only=True)
    pm = wm["parametros_manuales"]
    out["t_man"] = bloque(pm, 124, 5, 1, 10)
    out["t_car"] = bloque(pm, 134, 4, 1, 9)
    out["gpm_m"] = (pm["B118"].value, pm["B119"].value, pm["B120"].value)
    out["util"] = {}
    for hoja in ("Resumen cap. sin sobrestock", "Resumen cap. con sobrestock"):
        ws = wm[hoja]     # aprovechamiento, máquinas y turnos de G1 y G2
        filas = [r for r in range(1, ws.max_row + 1)
                 if str(ws.cell(r, 1).value or "").startswith("Corte de chapa — 1.er corte")]
        out["util"][hoja] = [[[ws.cell(r + k, c).value for c in range(2, 12)] for k in (0, 1)] for r in filas]
    return out


def fila(ws, texto, desde=1):
    return next(r for r in range(desde, ws.max_row + 1) if str(ws.cell(r, 1).value or "").startswith(texto))


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
    for d, x in zip(DC.DISC, X["cor_d"]):
        for k, v in (("B", d["d0a"]), ("D", d["puente"]), ("E", d["borde"]), ("T", d["ancho"]), ("G", d["paso"])):
            assert abs(x[k] - v) < 1e-6, (d["pieza"], d["formato"], k)
        assert abs(x["V"] - (d["d0a"] + d["paso"] * math.sqrt(3) / 2 + 2 * d["borde"])) < 1e-6
    return geo


def mejor_patron(W, C, al, de, M):
    """Máximo de piezas al × de en la hoja W × C con guillotina de hasta tres etapas y el 1.er corte por el lado
    corto W: franjas de ancho w (múltiplo de una medida de la pieza, hasta el tope de G1), tramos de largo b a lo
    largo de W (dentro del tope de G2 o como orilla) y, si w es mayor que la pieza, corte a lo largo del tramo."""
    def tramo_ok(b):
        return b <= M["tope2"] or (W // b == 1 and W - b <= M["tope2"])
    anchos = sorted({k * x for x in (al, de) for k in range(1, 30) if k * x <= M["tope1"]})
    franja = {}
    for w in anchos:
        tramos = [(b, int(w // c)) for b, c in ((al, de), (de, al))
                  if tramo_ok(b) and c <= w and (c == w or c <= M["tope2"])]
        dp = [0] * (int(W * 2) + 1)          # mochila sobre el largo de la franja, en pasos de 0,5 mm
        for x in range(len(dp)):
            for b, v in tramos:
                if round(b * 2) <= x:
                    dp[x] = max(dp[x], dp[x - round(b * 2)] + v)
        franja[w] = dp[-1]
    dp = [0] * (int(C * 2) + 1)              # mochila de franjas sobre el lado largo
    for x in range(len(dp)):
        for w, v in franja.items():
            if round(w * 2) <= x:
                dp[x] = max(dp[x], dp[x - round(w * 2)] + v)
    return dp[-1]


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


AZU = "#2B5C8A"


def fig_combinada(ruta):
    """P1 y P3 de la hoja de 3,2 mm: franjas de 995,5 (G1), pieza de 50 kg y tramo (G2) y tramo a lo largo (G2)."""
    W, C = DC.CUERPO["25 kg"][3], DC.CUERPO["25 kg"][4]
    a25, d25 = DC.CUERPO["25 kg"][:2]
    a50, d50 = DC.CUERPO["50 kg"][:2]
    fig, axs = plt.subplots(2, 1, figsize=(10, 9.4))
    for ax, (tit, fr50) in zip(axs, (("P1: 6 de 25 kg + 3 de 50 kg (98,9 %)", [1, 1, 1]),
                                     ("P3: 6 de 50 kg, como el 50 kg solo (85,0 %)", [2, 2, 2]))):
        ax.add_patch(Rectangle((0, 0), C, W, fc=GRI, ec="#333333", lw=1.2))
        for k, n50 in enumerate(fr50):
            x0, y = k * d50, 0
            for _ in range(n50):
                ax.add_patch(Rectangle((x0, y), d50, a50, fc="#C6E3D3", ec=VER, lw=0.8))
                ax.text(x0 + d50 / 2, y + a50 / 2, f"50 kg\n{nz(a50, 1)} × {nz(d50, 1)}", ha="center", va="center",
                        fontsize=9)
                y += a50
                ax.plot([x0, x0 + d50], [y, y], color=VER, ls="--", lw=1.1)
            if n50 == 1:
                for j in range(2):
                    ax.add_patch(Rectangle((x0 + j * a25, y), a25, d25, fc="#DCE8F5", ec=AZU, lw=0.8))
                    ax.text(x0 + j * a25 + a25 / 2, y + d25 / 2, f"25 kg\n{nz(a25, 1)} × {nz(d25, 1)}", ha="center",
                            va="center", fontsize=8.5, rotation=90)
                for xx in (x0 + a25, x0 + 2 * a25):
                    ax.plot([xx, xx], [y, y + d25], color=AZU, ls=":", lw=1.6)
                y += d25
                ax.plot([x0, x0 + d50], [y, y], color=VER, ls="--", lw=1.1)
            ax.plot([x0 + d50, x0 + d50], [-W * 0.012, W * 1.012], color=NAR, lw=2.2)
        ax.set_xlim(-C * 0.04, C * 1.02)
        ax.set_ylim(-W * 0.06, W * 1.1)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{tit} · hoja {n(C)} × {n(W)} × 3,2 mm", fontsize=10)
    axs[1].plot([], [], color=NAR, lw=2, label="1.er corte (G1): franjas de 995,5")
    axs[1].plot([], [], color=VER, ls="--", label="2.º corte (G2): pieza de 50 kg y tramo")
    axs[1].plot([], [], color=AZU, ls=":", lw=1.6, label="3.er corte (G2): tramo a lo largo, 493 + 493")
    axs[1].legend(loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=8.5, frameon=False)
    fig.tight_layout()
    fig.savefig(ruta, dpi=170, bbox_inches="tight")
    plt.close(fig)


def _cota(ax, p1, p2, txt, dx=0.0, dy=0.0, fs=7.5, color="#333333", rot=0):
    ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="<->", lw=0.8, color=color, shrinkA=0, shrinkB=0))
    ax.text((p1[0] + p2[0]) / 2 + dx, (p1[1] + p2[1]) / 2 + dy, txt, ha="center", va="center", fontsize=fs,
            color=color, rotation=rot)


def fig_fleje_esquema(ruta):
    """Esquema sin escala del fleje: una fila y dos filas al tresbolillo, con los puentes."""
    from matplotlib.patches import Circle
    D, pa, pb = 40.0, 6.0, 9.0
    p = D + pa
    s3 = p * math.sqrt(3) / 2
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.2))
    # una fila
    W1, L = D + 2 * pb, 3.45 * p
    a1.add_patch(Rectangle((0, 0), L, W1, fc=GRI, ec="#333333", lw=1.1))
    cx = [pb + D / 2 + k * p for k in range(3)]
    for x in cx:
        a1.add_patch(Circle((x, W1 / 2), D / 2, fc="#C6E3D3", ec=VER, lw=1.2))
    _cota(a1, (-6, 0), (-6, W1), "ancho = D0 + 2·pb", dx=-3, rot=90)
    _cota(a1, (cx[0], W1 + 7), (cx[1], W1 + 7), "paso = D0 + pa", dy=3.2)
    _cota(a1, (cx[0] + D / 2, W1 / 2), (cx[1] - D / 2, W1 / 2), "")
    a1.annotate("pa: puente de avance", xy=((cx[0] + cx[1]) / 2, W1 / 2), xytext=((cx[0] + cx[1]) / 2 + 4, -12),
                fontsize=7.5, ha="left", arrowprops=dict(arrowstyle="-", lw=0.6))
    _cota(a1, (cx[2], W1 / 2 + D / 2), (cx[2], W1), "")
    a1.annotate("pb: puente al borde", xy=(cx[2], W1 - pb / 2), xytext=(cx[2] + 10, W1 + 9), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    _cota(a1, (cx[1] - D / 2, W1 / 2), (cx[1] + D / 2, W1 / 2), "D0", dy=3.5)
    a1.annotate("", xy=(L + 10, W1 / 2), xytext=(L + 1, W1 / 2), arrowprops=dict(arrowstyle="-|>", lw=1.1))
    a1.text(L + 11, W1 / 2, "avance\ndel fleje", fontsize=7.5, va="center")
    a1.set_xlim(-18, L + 26)
    a1.set_ylim(-18, W1 + 20)
    a1.set_aspect("equal")
    a1.axis("off")
    a1.set_title("Una fila: un disco por golpe", fontsize=9)
    # dos filas al tresbolillo
    W2 = D + s3 + 2 * pb
    a2.add_patch(Rectangle((0, 0), L + p / 2, W2, fc=GRI, ec="#333333", lw=1.1))
    y1, y2 = pb + D / 2, pb + D / 2 + s3
    c1 = [pb + D / 2 + k * p for k in range(3)]
    c2 = [x + p / 2 for x in c1]
    for x in c1:
        a2.add_patch(Circle((x, y1), D / 2, fc="#C6E3D3", ec=VER, lw=1.2))
    for x in c2:
        a2.add_patch(Circle((x, y2), D / 2, fc="#DCE8F5", ec=AZU, lw=1.2))
    _cota(a2, (-6, 0), (-6, W2), "ancho = D0 + paso·√3/2 + 2·pb", dx=-3, rot=90)
    _cota(a2, (c1[2] + p * 0.75, y1), (c1[2] + p * 0.75, y2), "paso·√3/2", dx=9, rot=90)
    a2.plot([c1[2], c1[2] + p * 0.8], [y1, y1], color="#999999", lw=0.5, ls=":")
    a2.plot([c2[2], c1[2] + p * 0.8], [y2, y2], color="#999999", lw=0.5, ls=":")
    _cota(a2, (c1[0], W2 + 7), (c1[1], W2 + 7), "paso (cada fila)", dy=3.2)
    ux, uy = (c2[0] - c1[0]) / p, (y2 - y1) / p
    _cota(a2, (c1[0] + ux * D / 2, y1 + uy * D / 2), (c2[0] - ux * D / 2, y2 - uy * D / 2), "")
    a2.annotate("pa entre filas: centros a un paso", xy=((c1[0] + c2[0]) / 2, (y1 + y2) / 2),
                xytext=(c2[0] + 6, -13), fontsize=7.5, arrowprops=dict(arrowstyle="-", lw=0.6))
    a2.set_xlim(-18, L + p / 2 + 12)
    a2.set_ylim(-18, W2 + 20)
    a2.set_aspect("equal")
    a2.axis("off")
    a2.set_title("Dos filas al tresbolillo: dos discos por golpe (matriz doble) o alimentador en zigzag", fontsize=9)
    fig.suptitle("Esquema sin escala (los puentes están agrandados para que se vean)", fontsize=8.5, y=0.04,
                 color="#666666")
    fig.tight_layout()
    fig.savefig(ruta, dpi=170, bbox_inches="tight")
    plt.close(fig)


def _perfil(ax, d, x0, y0):
    """Perfil de la pieza embutida (fibra media): pollera o pestaña recta y casquete o paraboloide."""
    a, p = d["a"], d["p"]
    t = [k / 60 * math.pi for k in range(61)]
    if d["perfil"] == "casquete":
        b = d["b"]
        xs = [-a * math.cos(u) for u in t]
        ys = [p + b * math.sin(u) for u in t]
    else:
        xs = [-a + 2 * a * k / 60 for k in range(61)]
        ys = [p + d["h"] * (1 - (x / a) ** 2) for x in xs]
    X = [-a, -a] + xs + [a, a]
    Y = [0, p] + ys + [p, 0]
    ax.fill([x0 + x for x in X], [y0 + y for y in Y], color="#E3F1EA")
    ax.plot([x0 + x for x in X], [y0 + y for y in Y], color=VER, lw=2)
    return max(ys)


def fig_embutido(fm, ds, cor, ruta):
    """Por formato: fleje de una fila y de dos filas a escala, y el embutido del disco a la pieza."""
    from matplotlib.patches import Circle
    fig, axs = plt.subplots(len(ds), 3, figsize=(12, 2.55 * len(ds)),
                            gridspec_kw=dict(width_ratios=[1.25, 1.25, 0.9]))
    for (a1, a2, a3), d, x in zip(axs, ds, cor):
        D, paso, pb = x["B"], x["G"], x["E"]
        W1, W2 = x["T"], x["V"]
        s3 = paso * math.sqrt(3) / 2
        L = 3.5 * paso
        for ax, Wf, filas in ((a1, W1, 1), (a2, W2, 2)):
            ax.add_patch(Rectangle((0, 0), L + (paso / 2 if filas == 2 else 0), Wf, fc=GRI, ec="#333333", lw=1))
            for k in range(3):
                cx = pb + D / 2 + k * paso
                ax.add_patch(Circle((cx, pb + D / 2), D / 2, fc="#C6E3D3", ec=VER, lw=1))
                if filas == 2:
                    ax.add_patch(Circle((cx + paso / 2, pb + D / 2 + s3), D / 2, fc="#DCE8F5", ec=AZU, lw=1))
            _cota(ax, (-0.05 * L, 0), (-0.05 * L, Wf), n(Wf, 1), dx=-0.05 * L, rot=90, fs=7)
            _cota(ax, (pb + D / 2, Wf + 0.06 * L), (pb + D / 2 + paso, Wf + 0.06 * L), f"paso {n(paso, 2)}",
                  dy=0.045 * L, fs=7)
            ax.set_xlim(-0.16 * L, L * 1.12 + paso / 2)
            ax.set_ylim(-0.08 * L, max(W2, W1) + 0.2 * L)
            ax.set_aspect("equal")
            ax.axis("off")
        a1.set_title(f"{d['pieza']} {fm}, una fila: ancho {n(W1, 1)} mm, aprov. {n(x['U'] * 100, 1)} %", fontsize=8.5)
        a2.set_title(f"Dos filas al tresbolillo: ancho {n(W2, 1)} mm, aprov. {n(x['W'] * 100, 1)} %", fontsize=8.5)
        # embutido: disco arriba, pieza abajo
        h = _perfil(a3, d, 0, 0)
        yd = h + 0.22 * D
        a3.add_patch(Rectangle((-D / 2, yd), D, max(d["e"] * 2.5, D * 0.012), fc="#C6E3D3", ec=VER, lw=1))
        _cota(a3, (-D / 2, yd + 0.09 * D), (D / 2, yd + 0.09 * D), f"D0 = {n(D, 1)}", dy=0.06 * D, fs=7.5)
        a3.annotate("", xy=(0, h + 0.04 * D), xytext=(0, yd - 0.02 * D), arrowprops=dict(arrowstyle="-|>", lw=1.2))
        a3.text(0.03 * D, (h + yd) / 2, "1 golpe", fontsize=7, va="center")
        _cota(a3, (-d["a"], -0.07 * D), (d["a"], -0.07 * D), f"d = {n(d['d'], 1)}", dy=-0.05 * D, fs=7.5)
        alto = f"h {n(d['h'], 1)}" if d["perfil"] == "casquete" else f"h + p {n(d['h'] + d['p'], 1)}"
        _cota(a3, (d["a"] + 0.08 * D, 0), (d["a"] + 0.08 * D, h), alto, dx=0.09 * D, rot=90, fs=7)
        a3.set_xlim(-0.62 * D, 0.72 * D)
        a3.set_ylim(-0.2 * D, yd + 0.24 * D)
        a3.set_aspect("equal")
        a3.axis("off")
        a3.set_title(f"m = d/D0 = {n(d['m'], 3)} ≥ m1 = {n(d['m1'], 2)}", fontsize=8.5)
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
    comb = X["dat"]["¿Combinar 25 y 50 kg en la hoja de 3,2 mm (corte en tres etapas)?"] == "SI"
    tresb = X["dat"]["¿Discos en fleje de dos filas al tresbolillo?"] == "SI"
    b.append({"t": "titulo", "x": "Esquema de corte en guillotina"})
    b.append({"t": "sub", "x": "FLAMA S.A. · Cuerpos de 1 a 100 kg en hoja estándar, con dos guillotinas en serie: "
                               "G1 Ermaksan CNC HGS 2600-6 (franjas) y G2 QC12Y 6 × 2500 (piezas), y discos de cúpulas "
                               "y fondos en fleje. Medidas de los planos de recipiente. Números del Excel «Análisis "
                               "alternativas corte chapa» y del Aprovechamiento de Manuales."})
    h1("1. Cómo se corta")
    p("Cada cuerpo sale de dos cortes: el **1.er corte** separa la hoja en franjas y el **2.º corte** separa cada "
      "franja en piezas (desarrollos). Cada corte tiene su máquina:")
    bul(f"**Guillotina 1**, [Ermaksan CNC HGS 2600-6]({URL_ERM}): largo de corte {n(M['L1'])} mm, 6 mm de espesor, "
        f"tope trasero motorizado de {n(M['tope1'])} mm. La ficha da 24 golpes por minuto; se toman "
        f"{nz(M['gpm1'])}, como en el Aprovechamiento de Manuales. Hace **solo el 1.er corte**: la hoja entra con el "
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
      "lo que rinde la más lenta de las dos. En las secciones 2 a 5 y en la comparación de alternativas los tiempos "
      "son a ritmo de máquina, el mismo criterio para todas las alternativas. Para dimensionar las guillotinas, que "
      "comparten manuales y carros, se suma la manipulación de cada hoja (W-MAN y W-CAR): sección 8.")
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
    if comb:
        pr = X["prom"]
        nota(f"25 y 50 kg: la tabla da cada uno en su hoja. Con el corte combinado (sección 5.2), la hoja de 3,2 mm "
             f"da en promedio {n(pr[0], 2)} cuerpos, {n(pr[1], 2)} golpes de G1 y {n(pr[2], 2)} de G2 por hoja "
             f"(plan {X['anio']}); esos son los valores que van a los Aprovechamientos.")
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
        if comb and x["f"] in ("25 kg", "50 kg"):
            p(f"Este es el patrón {'P4' if x['f'] == '25 kg' else 'P3'} de la sección 5.2. Con el corte combinado, "
              "los 25 kg salen en hojas P1 junto con 50 kg, y el resto de los 50 kg en este patrón.")
    b.append({"t": "salto"})

    b.extend(nesting(X, M, tmp, comb))
    b.extend(piezas_embutido(X, tmp, tresb))
    b.extend(guillotinas_compartidas(X, M))
    b.extend(final(X, tresb))
    return b


class Bl(list):
    """Bloques del Word (mismo formato que word_corte.js)."""
    def p(self, t):
        self.append({"t": "p", "x": t})

    def h1(self, t):
        self.append({"t": "h1", "x": t})

    def h2(self, t):
        self.append({"t": "h2", "x": t})

    def nota(self, t):
        self.append({"t": "nota", "x": t})

    def bul(self, t):
        self.append({"t": "b", "x": t})

    def tabla(self, cab, cols, filas, num=()):
        self.append({"t": "tabla", "cab": cab, "cols": cols, "filas": filas, "num": list(num)})

    def img(self, ruta, pie, ancho=16.5):
        import PIL.Image as Im
        w, hh = Im.open(ruta).size
        self.append({"t": "img", "ruta": ruta, "pie": pie, "ancho": ancho, "anchoPx": w, "alto": hh})


def nesting(X, M, tmp, comb):
    """Sección 5: todas las hojas y patrones; 25 + 50 kg combinados; 70 + 100 kg; conclusión."""
    b = Bl()
    b.h1("5. Nesting: ¿es el mejor corte?")
    b.p("Para saber si el corte elegido es el mejor se probaron **todas las hojas cotizadas** y **todos los patrones de "
        "guillotina** con el 1.er corte por el lado corto, de dos y de tres etapas (la tercera corta un tramo a lo "
        "largo, en la G2). Donde dos formatos comparten espesor (3,2 mm: 25 y 50 kg; 4,75 mm: 70 y 100 kg) se buscó "
        "además la mezcla de patrones que compra menos hojas para la demanda de cada año. Los números están en la hoja "
        "Nesting del Excel.")
    b.h2("5.1 La hoja y el patrón de cada formato")
    filas, mas = [], []
    for (fm, W, C, q), x in zip(GC.CAND, X["cand"]):
        al, de = DC.CUERPO[fm][:2]
        mx = mejor_patron(W, C, al, de, M)
        cota = int(W * C // (al * de))
        filas.append([fm, f"{n(W)} × {n(C)}", q, n(x[5], 4), x[6], str(x[7]), str(mx), str(cota), n(x[8] * 100, 1) + " %",
                      n(x[11], 2), "Sí" if x[12] == "Sí" else ""])
        assert mx >= x[7], (fm, W, C)
        if mx > x[7]:
            mas.append((fm, W, C, mx, x[9] / mx * x[5], min(y[11] for (f2, *_), y in zip(GC.CAND, X["cand"]) if f2 == fm)))
        if x[12] == "Sí":
            assert x[13] == "Sí", (fm, "la hoja más barata no es la de la hoja Corte")
    b.tabla(["Formato", "Hoja (mm)", "Cotiz.", "USD/kg", "Franjas × piezas", "Piezas (2 etapas)",
             "Máximo con 3 etapas", "Cota por superficie", "Aprov.", "USD por cuerpo", "La más barata"],
            [8, 11, 6, 7, 8, 7, 8, 8, 7, 8, 7], filas, num=[3, 5, 6, 7, 8, 9])
    b.nota("Máximo con 3 etapas: enumeración de todos los patrones (franjas de ancho igual a una medida de la pieza o a "
           "un múltiplo, hasta el tope de la G1; tramos dentro del tope de la G2 o como orilla). Cota por superficie: "
           "superficie de la hoja ÷ superficie de la pieza, que ningún corte puede pasar.")
    sig = [f"{fm} en {n(W)} × {n(C)} ({mx} cuerpos, USD {n(u, 2)} por cuerpo contra {n(m_, 2)} de la elegida)"
           for fm, W, C, mx, u, m_ in mas]
    b.p("En **todas las hojas elegidas el patrón de dos etapas ya es el máximo**: una tercera etapa no saca ni una pieza "
        "más, y en 5 kg se llega a la cota por superficie. Las orillas que quedan son más angostas que la pieza más chica. "
        + ("Tres etapas solo suman una pieza en hojas que igual salen más caras: " + "; ".join(sig) + ". "
           if sig else "")
        + "Para cada formato, la hoja elegida es la que da el cuerpo más barato.")

    # 3,2 mm
    b.h2("5.2 3,2 mm: 25 y 50 kg en la misma hoja")
    pat = {x[0]: x for x in X["pat"]}
    a25, d25 = DC.CUERPO["25 kg"][:2]
    a50, d50 = DC.CUERPO["50 kg"][:2]
    b.p(f"Por separado, la hoja de 1.500 × 3.000 × 3,2 da 9 cuerpos de 25 kg ({n(pat['P4'][10] * 100, 1)} %) o 6 de "
        f"50 kg ({n(pat['P3'][10] * 100, 1)} %). Las medidas de las dos piezas encajan: en una franja de "
        f"{nz(d50, 1)} mm (el desarrollo del 50 kg) entran, a lo largo de los 1.500 mm, una pieza de 50 kg de "
        f"{nz(a50, 1)} mm y un tramo de {nz(d25, 1)} mm (el desarrollo del 25 kg), que se corta a lo largo en dos "
        f"piezas de 25 kg de {nz(a25, 1)} mm. Es un corte en tres etapas, con las mismas dos máquinas:")
    b.bul(f"**G1**: tres franjas de {nz(d50, 1)} mm, igual que para el 50 kg solo.")
    b.bul(f"**G2, 2.º corte**: de cada franja, la pieza de 50 kg ({nz(a50, 1)} mm) y el tramo ({nz(d25, 1)} mm); "
          "quedan 1,5 mm de recorte.")
    b.bul(f"**G2, 3.er corte**: el tramo se gira y se corta a lo largo con el tope en {nz(a25, 1)} mm: dos piezas de "
          "25 kg y 9,5 mm de recorte.")
    ruta = os.path.join(tmp, "comb.png")
    fig_combinada(ruta)
    b.img(ruta, "Figura 10. Hoja de 3,2 mm: P1 (25 y 50 kg combinados, tres etapas) y P3 (50 kg solo).", 14)
    filas = [[x[0], x[1], str(x[4]), str(x[5]), nz(x[6], 2), nz(x[7], 2), nz(x[8], 2), str(x[9]),
              n(x[10] * 100, 1) + " %"] for x in X["pat"]]
    b.tabla(["Patrón", "Franjas", "25 kg", "50 kg", "Golpes G1", "Golpes G2", "Tandas G2", "Etapas", "Aprov."],
            [6, 29, 5, 5, 6, 6, 6, 6, 6], filas, num=[2, 3, 4, 5, 6, 7, 8])
    b.nota("Por hoja. Golpes de G2 en P1: cada tanda de 2 franjas lleva 2 golpes (pieza de 50 kg y tramo) y cada tanda "
           "de 2 tramos girados, 2 más (493 y el recorte).")
    b.p("Controles de P1 con las medidas del plano:")
    filas = [[x[0], nz(x[1], 1), nz(x[2], 1), x[4].replace("OK (sobran ", "Entra: sobran ").replace(".", ",")
              .replace(" mm)", " mm")] for x in X["ctl"]]
    b.tabla(["Control", "Medida (mm)", "Límite (mm)", "Resultado"], [22, 8, 8, 12], filas, num=[1, 2])
    b.nota("Los 1,5 mm que sobran a lo largo de la franja alcanzan: la chapa laminada en caliente viene con tolerancia "
           "de ancho +0 (nunca más angosta), así que el recorte siempre existe.")
    pl = X["plan"]
    i_a = X["anio"] - 2026
    n25, n50 = pl["Cuerpos de 25 kg"][0], pl["Cuerpos de 50 kg"][0]
    hp1, hp3, hp4 = (X[k][i_a] for k in ("B_p1", "B_p3", "B_p4"))
    b.p("**El plan.** Todos los cuerpos de 25 kg salen en hojas P1, que llevan además 3 de 50 kg; el resto de los "
        "50 kg sale en P3. Hojas P1 = N25 ÷ 6 y hojas P3 = (N50 − N25 ÷ 2) ÷ 6, mientras N50 sea al menos la mitad de "
        "N25 (si no, P1 = N50 ÷ 3 y el resto de los 25 kg en P4). En " + str(X["anio"]) + f": N25 = {n(n25)} y "
        f"N50 = {n(n50)}, así que {n(hp1, 1)} hojas P1 y {n(hp3, 1)} P3" + (f" y {n(hp4, 1)} P4" if hp4 > 0.05 else "")
        + ".")
    b.p("**Es el mínimo de hojas.** Si a cada cuerpo de 25 kg se le asigna 1/12 de hoja y a cada uno de 50 kg 1/6, "
        "ningún patrón suma más de una hoja (P1: 6/12 + 3/6 = 1; P2: 2/12 + 5/6 = 1; P3: 6/6 = 1; P4: 9/12 = 0,75). "
        "Entonces ninguna mezcla de patrones baja de N25/12 + N50/6 hojas, y el plan llega justo a ese número (es la "
        "solución dual de la programación lineal). P2 (2 franjas de 50 kg + 1 franja como P1) da lo mismo, porque "
        "equivale a ⅓ de P1 + ⅔ de P3; no hace falta.")
    filas = [[k, n(v[0], 1 if "Hojas" in k or "Acero" in k else 0) if "Aprov" not in k else n(v[0] * 100, 1) + " %",
              n(v[1], 1 if "Hojas" in k or "Acero" in k else 0) if "Aprov" not in k else n(v[1] * 100, 1) + " %",
              n(v[2], 1 if "Hojas" in k or "Acero" in k else 0) if "Aprov" not in k else n(v[2] * 100, 1) + " pp"]
             for k, v in pl.items()]
    b.tabla([f"Año {X['anio']}", "Separados (2 etapas)", "Combinados", "Diferencia"], [16, 10, 10, 10], filas,
            num=[1, 2, 3])
    ah = pl["Hojas de 3,2 mm"]
    au = pl["Costo del acero (USD)"]
    g = {x[0]: x for x in X["pat"]}
    g1s = (n25 / 9 + n50 / 6) * g["P3"][6]
    g2s = n25 / g["P4"][4] * g["P4"][7] + n50 / g["P3"][5] * g["P3"][7]
    g1c = (hp1 + hp3 + hp4) * g["P1"][6]
    g2c = hp1 * g["P1"][7] + hp3 * g["P3"][7] + hp4 * g["P4"][7]
    assert abs(n25 / g["P4"][4] - n25 / 9) < 1e-9
    b.p(f"Combinar ahorra **{n(-ah[2])} hojas** y **USD {n(-au[2])}** de acero en {X['anio']}. La G1 da "
        f"{n(g1s - g1c)} golpes menos (menos hojas) y la G2 {n(g2c - g2s)} más (el 3.er corte): "
        f"{n((g2c - g2s) / M['gpm2'])} minutos más al año a ritmo de máquina, nada frente al ahorro de chapa. " + ("Está activado en el Excel (Datos: combinar 25 y 50 kg = SI)."
                                            if comb else "En el Excel está desactivado (Datos: combinar = NO)."))
    # 4,75 mm
    b.h2("5.3 4,75 mm: 70 y 100 kg")
    filas = [[x[0], str(x[1]), str(x[2]), n(x[4] * 100, 1) + " %"] for x in X["p475"]]
    b.tabla(["Patrón en la hoja de 1.500 × 3.000", "70 kg", "100 kg", "Aprov."], [24, 7, 7, 8], filas, num=[1, 2, 3])
    b.p("Las piezas de 70 y 100 kg tienen el mismo desarrollo (1.210,5 mm) y van en la misma franja; con 1.500 mm de "
        "franja solo entra una pieza a lo largo, así que no hay tercera etapa que sume. La hoja mixta (3 de 70 kg + 1 de "
        "100 kg) es el patrón que más aprovecha, y el plan del Excel ya es el óptimo: hojas mixtas hasta agotar los "
        "70 kg y el resto de 100 kg solos.")
    b.h2("5.4 Conclusión")
    b.bul("1 a 10 kg: la hoja y el patrón elegidos son los mejores; no hay corte de guillotina que saque más piezas.")
    b.bul(f"3,2 mm: conviene combinar 25 y 50 kg (P1 + P3): el aprovechamiento sube de "
          f"{n(pl['Aprovechamiento'][0] * 100, 1)} % a {n(pl['Aprovechamiento'][1] * 100, 1)} %.")
    b.bul("4,75 mm: la hoja mixta ya es el óptimo.")
    b.bul("Discos: el fleje de dos filas al tresbolillo ahorra fleje, pero necesita matriz doble o alimentador en "
          "zigzag (sección 7.3).")
    return b


def piezas_embutido(X, tmp, tresb):
    """Secciones 6 y 7: medidas de las piezas y esquema de embutido de cúpulas y fondos."""
    b = Bl()
    b.h1("6. Medidas de las piezas (planos)")
    b.p("Todas las medidas salen de los planos de recipiente (modelo 3D). El desarrollo es el **perímetro del "
        "cilindro** en la fibra media: desarrollo = π·(Ø exterior − espesor). Alto × desarrollo es la superficie de "
        "chapa del cuerpo. El alto es el del cuerpo del plano, con el labio del encastre.")
    filas = []
    for f in DC.FORM:
        al, de, e = DC.CUERPO[f][:3]
        filas.append([f, n(GC.DIAM[f], 1), n(e, 2), n(al, 1), n(de, 1), DC.PLANO[f]])
    b.tabla(["Formato", "Ø ext. (mm)", "Espesor (mm)", "Alto (mm)", "Desarrollo (mm)", "Plano"],
            [10, 10, 10, 10, 11, 30], filas, num=[1, 2, 3, 4])

    b.h1("7. Esquema de embutido: cúpulas y fondos")
    b.p("Las cúpulas y los fondos de 1 a 10 kg salen de **fleje a medida** (opción D): la prensa corta el disco y lo "
        "embute en el mismo golpe. Cada pieza tiene su fleje, con el ancho y el paso de su disco.")
    b.h2("7.1 Del disco a la pieza: diámetro del disco y relaciones de embutido")
    b.p("El disco no tiene el diámetro de la cúpula ni del fondo: al embutirlo, la chapa toma la profundidad de la "
        "pieza. Como el espesor casi no cambia, el disco tiene **la misma superficie que la pieza embutida** (Harsle, "
        "«How to Calculate Deep Drawing Parts»). Con las medidas del plano:")
    b.bul("**Cúpulas y fondo del 1 kg** (casquete): semielipsoide de semiejes a = Ø/2 − e/2 y b = altura − pollera − "
          "e/2, más una pollera recta p de 6 mm. A = π·a² + π·b²/(2ε)·ln((1+ε)/(1−ε)) + 2π·a·p, con ε = √(1 − b²/a²).")
    b.bul("**Fondos de 2,5 a 10 kg** (cóncavos): paraboloide de radio ρ = Ø/2 − e/2 y profundidad h, más una pestaña "
          "recta p de 10 mm. A = π/(6k²)·[(1 + 4k²ρ²)^1,5 − 1] + 2π·ρ·p, con k = h/ρ². Fórmulas de superficie de "
          "MathWorld.")
    b.bul("**Diámetro del disco**: D0 = √(4A/π), redondeado a 0,5 mm hacia arriba.")
    b.bul("**Relación de embutido**: m = d/D0, con d = 2a, el diámetro de la pieza en la fibra media (su inversa es "
          "β = D0/d). El límite del primer embutido, m1, depende del espesor relativo t/D0 (copa sin brida, con "
          "prensachapas; EasyChair, preprint Vxvp). Si m ≥ m1, la pieza sale **en un solo golpe**, sin reembutido.")
    b.bul("**Sin sobremedida de recorte**: no hay recorte después del embutido (W-MAN, puesto 4) y la tabla de "
          "sobremedida de Harsle arranca en h/d = 0,5, más que cualquiera de estas piezas.")
    filas = []
    for d in DC.DISC:
        filas.append([f"{d['pieza']} {d['formato']}", n(d["e"], 2), n(d["d"], 1), n(d["h"], 1), n(d["p"], 0),
                      n(d["A"]), n(d["d0a"], 1), n(d["td"], 2), n(d["m"], 3), n(d["m1"], 2), n(1 / d["m"], 2),
                      n(d["hd"], 2), "1" if d["ok"] else "2"])
        assert d["ok"], d
    b.tabla(["Pieza", "e (mm)", "d (mm)", "h (mm)", "p (mm)", "Área (mm²)", "D0 (mm)", "t/D0 (%)", "m = d/D0",
             "m1 mín.", "β = D0/d", "h/Ø", "Golpes"], [11, 5, 6, 5, 5, 8, 6, 6, 6, 6, 6, 5, 5], filas,
            num=list(range(1, 13)))
    ms = [d["m"] for d in DC.DISC]
    m1s = [d["m1"] for d in DC.DISC]
    b.p(f"Todas las piezas tienen m entre {n(min(ms), 2)} y {n(max(ms), 2)}, muy por encima del límite m1 "
        f"({n(min(m1s), 2)} a {n(max(m1s), 2)}): son embutidos poco profundos y salen en un golpe. Por eso no hacen "
        "falta las relaciones de reembutido (m2, m3).")

    b.h2("7.2 El fleje: distancias de corte")
    b.p("Los discos se cortan uno detrás del otro a lo largo del fleje. Entre disco y disco, y entre el disco y el borde, "
        "queda un **puente** de chapa que sostiene el esqueleto mientras avanza el fleje (MISUMI, Press Dies Tutorial):")
    b.bul("**Puente de avance pa** (entre discos): 1,5 veces el espesor, mínimo 0,7 mm.")
    b.bul("**Puente al borde pb**: 1,5 veces el de avance, porque la guía del fleje deja juego.")
    b.bul("**Paso** = D0 + pa: lo que avanza el fleje en cada golpe. **Ancho del fleje** = D0 + 2·pb.")
    ruta = os.path.join(tmp, "fleje.png")
    fig_fleje_esquema(ruta)
    b.img(ruta, "Figura 11. Fleje de una fila y de dos filas al tresbolillo: puentes, paso y ancho.")
    filas = []
    for x in X["cor_d"]:
        filas.append([x["A"], n(x["B"], 1), n(x["C"], 2), n(x["D"], 2), n(x["E"], 2), n(x["T"], 2), n(x["G"], 2),
                      n(x["U"] * 100, 1) + " %", n(x["X"], 3)])
    b.tabla(["Pieza", "D0 (mm)", "e (mm)", "pa (mm)", "pb (mm)", "Ancho (mm)", "Paso (mm)", "Aprov.",
             "kg de fleje por disco"], [11, 7, 6, 6, 6, 8, 7, 7, 8], filas, num=list(range(1, 9)))
    b.nota("Aprovechamiento = superficie del disco ÷ (ancho × paso), con el despunte de cabeza y cola de cada rollo "
           "(Datos). El esqueleto que queda es scrap.")
    figs = 12
    for fm in ("1 kg", "2,5 kg", "5 kg", "10 kg"):
        idx = [i for i, d in enumerate(DC.DISC) if d["formato"] == fm]
        ruta = os.path.join(tmp, f"emb_{fm.replace(',', '_').replace(' ', '')}.png")
        fig_embutido(fm, [DC.DISC[i] for i in idx], [X["cor_d"][i] for i in idx], ruta)
        b.img(ruta, f"Figura {figs}. {fm}: fleje de una fila y de dos filas a escala, y embutido del disco "
                    "(perfil en la fibra media)." + (" El fondo cóncavo se dibuja como sale de la prensa; se monta "
                                                     "con la cara convexa hacia adentro del recipiente."
                                                     if fm != "1 kg" else ""))
        figs += 1

    b.h2("7.3 ¿Una fila o dos al tresbolillo?")
    b.p("Con dos filas corridas medio paso, los discos de una fila se meten entre los de la otra. Los centros de filas "
        "vecinas quedan a un paso, así que se mantiene el puente de avance, y el fleje mide D0 + paso·√3/2 + 2·pb. Se "
        "desperdicia menos esqueleto:")
    filas, usd = [], 0
    for x, c_ in zip(X["dsc"][:-1], X["cor_d"]):
        filas.append([x[0], n(x[1], 1), n(x[2] * 100, 1) + " %", n(x[3], 1), n(x[4] * 100, 1) + " %", n(x[5]),
                      n(x[6]), n(x[7])])
        usd += x[7] * c_["J"] / c_["I"]
    t = X["dsc"][-1]
    filas.append(["Total", "", "", "", "", n(t[5]), n(t[6]), n(t[7])])
    b.tabla(["Pieza", "Ancho 1 fila", "Aprov. 1 fila", "Ancho 2 filas", "Aprov. 2 filas",
             f"kg de fleje {X['anio']}, 1 fila", "kg, 2 filas", "Ahorro (kg)"], [11, 7, 7, 7, 7, 9, 8, 8], filas,
            num=list(range(1, 8)))
    b.p(f"Dos filas ahorran **{n(t[7] / 1000, 1)} t de fleje** en {X['anio']} (USD {n(usd)} al precio del fleje). "
        "Pero cada golpe tiene que cortar dos discos (matriz doble) o el fleje tiene que correrse de costado entre "
        "golpes (alimentador en zigzag), y no hay cotización de ninguno de los dos. "
        + ("En el Excel está activado (Datos: dos filas = SI)." if tresb else
           "Por eso en el Excel queda en una fila (Datos: dos filas = NO); con la cotización se prende el SI y el "
           "Excel recalcula todo."))
    return b


def guillotinas_compartidas(X, M):
    """Sección 8: tiempo con manipulación (W-MAN y W-CAR) y carga consolidada de manuales y carros."""
    b = Bl()
    gpm1, gpm2, parte = X["gpm_m"]
    b.h1("8. Guillotinas compartidas por manuales y carros")
    b.p("Los cuerpos de manuales (1 a 10 kg) y de carros (25 a 100 kg) se cortan en **las mismas dos guillotinas**, así "
        "que la demanda de las dos líneas se suma en cada máquina. El tiempo de cada cuerpo suma los golpes y la "
        "manipulación de la hoja (traerla, acomodarla, sacar franjas y piezas):")
    b.bul(f"**G1** = [golpes de G1 × máx(tiempo por corte; 1 ÷ {nz(gpm1)} golpes por minuto) + manipulación × "
          f"{n(parte * 100)} %] ÷ piezas por hoja.")
    b.bul(f"**G2** = [golpes de G2 × máx(tiempo por corte; 1 ÷ {nz(gpm2)}) + manipulación × {n((1 - parte) * 100)} %] ÷ "
          "piezas por hoja.")
    b.bul("**Tiempo por corte y manipulación**: W-MAN, «Corte de chapa»: 0,3 min por corte y 2 min por hoja (0,4 y 3 en "
          "la chapa de 2,0 mm); el 1 kg se toma como el 2,5 kg. W-CAR: 0,4 min por corte en 3,2 mm y 0,6 en 4,75 mm; la "
          "manipulación por hoja es el tiempo por hoja de W-CAR menos sus cortes (25 kg: 10,6 − 12 × 0,4 = 5,8 min; "
          "50 kg: 8,8 − 9 × 0,4 = 5,2; hoja mixta: 14,5 − 8 × 0,6 = 9,7).")
    b.bul(f"**Reparto {n(parte * 100)}/{n((1 - parte) * 100)}** de la manipulación entre G1 y G2: criterio (traer la "
          "hoja a la G1 y recargar las franjas en la G2 llevan lo mismo).")
    filas = []
    for x in X["t_man"][:4]:
        filas.append([x[0], x[1], nz(x[2], 2), nz(x[3], 2), nz(x[4], 2), nz(x[5], 1), nz(x[6], 1), n(x[7], 1),
                      n(x[8], 1)])
    for x in X["t_car"]:
        filas.append([x[0], x[1], nz(x[2], 2), nz(x[3], 2), nz(x[4], 2), nz(x[5], 1), nz(x[6], 1), n(x[7] * 60, 1),
                      n(x[8] * 60, 1)])
    b.tabla(["Cuerpo", "Hoja (mm)", "Piezas por hoja", "Golpes G1", "Golpes G2", "Min por corte",
             "Manipulación por hoja (min)", "G1 (s/cuerpo)", "G2 (s/cuerpo)"], [7, 11, 7, 7, 7, 7, 10, 8, 8], filas,
            num=list(range(2, 9)))
    tm = X["t_man"][4]
    b.nota(f"25 y 50 kg con el promedio del corte combinado; 70 y 100 kg con la hoja mixta. Tiempo tipo de manuales "
           f"(ponderado por los recipientes de 2035): G1 {n(tm[7], 2)} s y G2 {n(tm[8], 2)} s por cuerpo.")
    b.p("En el Aprovechamiento de Manuales, la carga de carros se pasa a unidades equivalentes de manuales (tiempo de "
        "carros ÷ tiempo tipo) y se suma mes a mes en los puestos de G1 y G2 (hojas «Demanda puesto»). La G1 suma "
        "además las tiras de los accesorios de carros (8,6 min por día en el pico, W-CAR). Resultado:")
    u = X["util"]["Resumen cap. sin sobrestock"]
    uc = X["util"]["Resumen cap. con sobrestock"]
    filas = [["G1, aprovechamiento"] + [n(v * 100) + " %" for v in u[0][0]],
             ["G2, aprovechamiento"] + [n(v * 100) + " %" for v in u[0][1]],
             ["G1 / G2, máquinas"] + [f"{v1:g} / {v2:g}" for v1, v2 in zip(u[1][0], u[1][1])],
             ["G1 / G2, turnos"] + [f"{v1:g} / {v2:g}" for v1, v2 in zip(u[2][0], u[2][1])]]
    b.tabla(["Sin sobrestock"] + [str(a) for a in range(2026, 2036)], [12] + [5] * 10, filas, num=list(range(1, 11)))
    b.p(f"Con manuales y carros juntos, en 2035 la G1 trabaja al **{n(u[0][0][-1] * 100)} %** y la G2 al "
        f"**{n(u[0][1][-1] * 100)} %** de un turno (con sobrestock, {n(uc[0][0][-1] * 100)} % y "
        f"{n(uc[0][1][-1] * 100)} %): **alcanza una máquina de cada una, en un turno, para las dos líneas**.")
    return b


def final(X, tresb):
    """Secciones 9 y 10 y fuentes."""
    b = Bl()
    b.h1("9. Resultado de la comparación de alternativas")
    res = X["res"]
    va = res["Valor actual a 10 años (USD)"]
    inv = res["Inversión en equipos (USD)"]
    b.p(f"Con el 1.er corte por el lado corto, la Ermaksan como G1 y el corte combinado de 3,2 mm, la **opción D** "
        f"(hojas + fleje) es la que conviene de las que cortan en planta: valor actual de USD {n(va[3])}, contra "
        f"{n(va[0])} de A, {n(va[1])} de B y {n(va[2])} de C. La inversión de D es de USD {n(inv[3])}. La hoja tendría "
        f"que subir {n(res['Margen de D: suba del precio de la hoja que la iguala con A'][0] * 100, 1)} % para que A "
        "la iguale. El detalle está en el Excel «Análisis alternativas corte chapa» (hojas Resumen y Cálculo).")
    b.h1("10. Pendiente")
    b.bul("Precio de la G1: la Ermaksan se tomó de un anuncio de máquina usada (2018) en euros, sin flete ni "
          "nacionalización. Hay que pedir cotización.")
    b.bul("Precio de la G2 puesta en planta: los USD 10.700 son FOB, sin flete ni nacionalización.")
    b.bul("Mandril de la soldadora longitudinal TIG del 1 kg: confirmar con Firesafer que entra en el interior de "
          "74,4 mm.")
    if not tresb:
        b.bul("Fleje de dos filas: pedir cotización de la matriz doble o del alimentador en zigzag (sección 7.3).")
    b.h1("Fuentes")
    for t in [f"[Ermaksan CNC HGS 2600-6, anuncio resale.info N.° 165879844]({URL_ERM}): 2.600 × 6 mm, 24 golpes por "
              "minuto, tope trasero de 1.000 mm, EUR 26.000 (usada, 2018).",
              f"[Pound Sterling Live, USD/EUR 2026]({URL_EUR}): 0,8723 al cierre del 21/09/2026.",
              f"[Publicación Alibaba 1600900259147, QC12Y 6 × 2500]({URL_QC}): cuchilla 2.550 mm, tope 20-800 mm, "
              "USD 10.700 FOB.",
              "Molinari Maquinarias, ficha de la guillotina Panther HG (formulario de cotización): HG 6 × 2500, 20 golpes "
              "por minuto.",
              "Aprovechamiento de Manuales del grupo: golpes por minuto de G1 y G2; soldadora longitudinal TIG Firesafer "
              "para el 1 kg.",
              "W-MAN, «Corte de chapa»: tiempo por corte y manipulación por hoja de manuales. W-CAR, «Corte de chapa»: "
              "tiempo por corte, minutos por hoja y tiras de accesorios de carros.",
              "IRAM 3523 (matafuegos de polvo bajo presión): 3.2.1 a), 3.2.4.1 y 3.2.4.2.",
              "[MISUMI, Press Dies Tutorial: puentes de corte](https://www.misumi-techcentral.com/tt/en/press/2009/09/"
              "012-basics-of-blanking-work-1-blanking-work.html).",
              "[Harsle, How to Calculate Deep Drawing Parts](https://harslepress.com/how-to-calculate-deep-drawing-parts/).",
              "[EasyChair, preprint Vxvp: relación de embutido m1](https://easychair.org/publications/preprint/Vxvp).",
              "[MathWorld, Oblate Spheroid](https://mathworld.wolfram.com/OblateSpheroid.html) y "
              "[Paraboloid](https://mathworld.wolfram.com/Paraboloid.html).",
              "Hierros Parrotta, presupuesto 413329; Pradecon 173170 y 173195; Pacheco Chapas PR 42021 y 42024."]:
        b.bul(t)
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
                             "soldadora longitudinal Firesafer con fuente TIG (Aprovechamiento de Manuales)."})
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
