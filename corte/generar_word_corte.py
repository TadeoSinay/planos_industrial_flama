"""Los dos Word de corte de chapa, con las medidas del plano y las dos guillotinas en serie:
- Esquemas_de_corte_cuerpos_guillotina.docx (todos los formatos, piezas del plano y discos por embutido)
- Esquema_de_corte_cuerpo_1_kg_chapa_09_mm.docx (cuerpo de 1 kg en chapa de 0,9 mm)
Los números de la comparación salen del Excel Comparacion_corte.xlsx recalculado."""

import json
import os
import shutil
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
RECALC = os.environ.get("RECALC", "/root/.claude/skills/synced/25c356cd-d646-4fc6-a248-83c7f917a94a_"
                                  "ed033efe-807e-46d6-9687-95e22d26e759/xlsx/scripts/recalc.py")
NODE_PATH = os.environ.get("NODE_PATH", "/tmp/claude-0/-home-user-TP-optimizacion/"
                                        "15292aaf-e550-5dee-a83e-77fd9177a6ef/scratchpad/jw/node/node_modules")
GPM1, L1, TOPE1, GPM2, L2, TOPE2 = 10, 3200, 1000, 20, 2500, 800
NAR, VER, GRI = "#D9622B", "#2E7D5B", "#F6E3DA"
URL_LINK = "https://www.alibaba.com/product-detail/QC12-Series-6mm-3-2m-Qc12Y_1600900259147.html"


def n(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ------------------------------------------------------------------ cálculo (mismo criterio que la hoja Corte)
def hoja(f, B=None, C=None):
    al, de, e, hb, hl, ac = DC.CUERPO[f]
    B, C = B or hb, C or hl
    o1, o2 = (B // al) * (C // de), (B // de) * (C // al)
    if o1 >= o2:
        fr, nfr, pzf, pz = al, int(B // al), int(C // de), de
    else:
        fr, nfr, pzf, pz = de, int(B // de), int(C // al), al
    piezas = nfr * pzf
    t1 = fr if fr <= TOPE1 else B - fr * nfr
    maq = "G2" if pz <= TOPE2 and fr <= L2 else "G1"
    par = int((L2 if maq == "G2" else L1) // fr)
    g1 = nfr + (nfr * pzf / par if maq == "G1" else 0)
    g2 = nfr * pzf / par if maq == "G2" else 0
    m1, m2 = g1 / GPM1, g2 / GPM2
    return dict(f=f, B=B, C=C, e=e, al=al, de=de, fr=fr, nfr=nfr, pzf=pzf, pz=pz, piezas=piezas,
                aprov=piezas * al * de / (B * C), orilla=B - nfr * fr, recorte=C - pzf * pz, tope1=t1, maq=maq,
                par=par, g1=g1, g2=g2, m1=m1, m2=m2, cph=piezas * 60 / max(m1, m2), ac=ac,
                masa=B * C * e * DC.DENS / 1e6)


def mixta():
    a70, d70, a100, d100 = DC.CUERPO["70 kg"][0], DC.CUERPO["70 kg"][1], DC.CUERPO["100 kg"][0], DC.CUERPO["100 kg"][1]
    B, C = 1500, 3000
    par = int(L1 // d100)
    g1 = 1 + 4 / par
    return dict(f="Mixta 70 + 100 kg", B=B, C=C, e=4.75, fr=d100, nfr=1, pzf=4, pz=a100, piezas=4,
                aprov=(a100 * d100 + 3 * a70 * d70) / (B * C), orilla=B - d100, recorte=C - a100 - 3 * a70,
                tope1=B - d100, maq="G1", par=par, g1=g1, g2=0, m1=g1 / GPM1, m2=0, cph=4 * 60 / (g1 / GPM1),
                piezas_txt="1 × 900 + 3 × 680")


HOJAS = [hoja(f) for f in DC.FORM]
MIX = mixta()


# ------------------------------------------------------------------ figuras
def fig_proceso(ruta):
    fig, ax = plt.subplots(figsize=(11, 2.6))
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 26)
    ax.axis("off")
    cajas = [(1, "Paquete de hojas\nen la mesa elevadora"), (23, "Guillotina 1\nCENA 8 × 3200\ncorta franjas"),
             (45, "Pulmón de franjas\n(carro porta-desarrollos)"),
             (67, "Guillotina 2\nQC12Y 6 × 2500\nfranjas en paralelo:\nuna pieza de cada una"),
             (89, "Desarrollos\na cilindrado")]
    for x, t in cajas:
        ax.add_patch(FancyBboxPatch((x, 9), 19, 13, boxstyle="round,pad=0.4", fc="#F2F2F2", ec="black", lw=1))
        ax.text(x + 9.5, 15.5, t, ha="center", va="center", fontsize=9)
    for x in (20.5, 42.5, 64.5, 86.5):
        ax.annotate("", xy=(x + 2.2, 15.5), xytext=(x, 15.5), arrowprops=dict(arrowstyle="-|>", lw=1.3))
    ax.annotate("", xy=(98, 8.6), xytext=(32, 8.6), arrowprops=dict(arrowstyle="-|>", lw=1, ls="--", color=NAR,
                                                                      connectionstyle="arc3,rad=0.12"))
    ax.text(65, 2.2, "Rodantes (pieza de 858 a 1.210 mm, mayor que el tope de 800 de G2): el 2.º corte también se "
                     "hace en la G1, con franjas en paralelo", ha="center", fontsize=8.5, color=NAR)
    fig.savefig(ruta, dpi=170, bbox_inches="tight")
    plt.close(fig)


def fig_formato(h, ruta, nota_piezas=None):
    """Izquierda: la hoja con los cortes 1 (franjas) y 2 (piezas). Derecha: el 2.º corte con franjas en paralelo."""
    B, C, fr, nfr, pzf, pz = h["B"], h["C"], h["fr"], h["nfr"], h["pzf"], h["pz"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw=dict(width_ratios=[1.25, 1]))
    a1.add_patch(Rectangle((0, 0), C, B, fc=GRI, ec="#555555", lw=1))
    piezas = [900, 680, 680, 680] if h.get("piezas_txt") else [pz] * pzf
    for k in range(nfr):
        y0 = B - (k + 1) * fr
        a1.add_patch(Rectangle((0, y0), sum(piezas), fr, fc="#E3F1EA", ec="none"))
        x = 0
        for j, p in enumerate(piezas):
            if j:
                a1.plot([x, x], [y0, y0 + fr], ls="--", color=VER, lw=1)
            x += p
        a1.plot([x, x], [y0, y0 + fr], ls="--", color=VER, lw=1)
        a1.plot([0, C], [y0, y0], color=NAR, lw=2)
        a1.text(C + C * 0.01, y0 + fr / 2, f"Franja {k + 1}", va="center", fontsize=8)
    a1.text(piezas[0] / 2, B - fr / 2, f"{n(pz if not h.get('piezas_txt') else 900, 1)}\n×\n{n(fr, 1)}",
            ha="center", va="center", fontsize=7, color=VER)
    a1.set_xlim(-C * 0.02, C * 1.16)
    a1.set_ylim(-B * 0.12, B * 1.12)
    a1.set_aspect("equal")
    a1.axis("off")
    a1.text(C / 2, B * 1.04, f"Hoja {n(C)} mm (lado paralelo a la cuchilla de G1)", ha="center", fontsize=8.5)
    a1.text(-C * 0.015, B / 2, f"{n(B)} mm", rotation=90, ha="right", va="center", fontsize=8.5)
    a1.plot([], [], color=NAR, lw=2, label="1.er corte (G1): franjas")
    a1.plot([], [], color=VER, ls="--", label="2.º corte: piezas")
    a1.add_patch(Rectangle((0, 0), 0, 0, fc=GRI, ec="#555555", label="Sobrante (scrap)"))
    a1.legend(loc="lower center", bbox_to_anchor=(0.5, -0.17), ncol=3, fontsize=7.5, frameon=False)
    # segundo corte
    Lm = L2 if h["maq"] == "G2" else L1
    par = h["par"]
    largo = C * 0.55
    a2.set_xlim(-Lm * 0.05, Lm * 1.05)
    a2.set_ylim(-largo * 1.1, pz * 1.6 + 60)
    a2.axis("off")
    a2.plot([0, Lm], [0, 0], color="#B00020", lw=3)
    a2.text(Lm / 2, -largo * 1.02, f"{par} franjas de {n(fr, 1)} mm apoyadas una al lado de la otra",
            ha="center", fontsize=8)
    for k in range(par):
        x0 = k * fr + 2
        a2.add_patch(Rectangle((x0, -largo), fr - 4, largo, fc="#E3F1EA", ec=VER, lw=0.8))
        a2.add_patch(Rectangle((x0, 0), fr - 4, pz, fc="#C6E3D3", ec=VER, lw=0.8))
    a2.plot([0, Lm], [pz, pz], color="black", ls=":", lw=1)
    tope = "900 y 680" if h.get("piezas_txt") else n(pz, 1)
    a2.text(Lm, pz + 25, f"tope trasero a {tope} mm", ha="right", va="bottom", fontsize=8)
    maq = "Guillotina 2 (QC12Y 6 × 2500)" if h["maq"] == "G2" else "Guillotina 1 (CENA 8 × 3200)"
    a2.text(Lm / 2, pz * 1.6 + 30, f"2.º corte en la {maq}: cada golpe corta {par} piezas", ha="center",
            fontsize=8.5, weight="bold")
    a2.text(-Lm * 0.02, 0, "cuchilla", ha="right", va="center", fontsize=7.5, color="#B00020")
    fig.tight_layout()
    fig.savefig(ruta, dpi=170, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ valores del Excel
def excel():
    src = os.path.join(SALIDA, "Comparacion_corte.xlsx")
    tmp = os.path.join(tempfile.mkdtemp(prefix="cc_"), "cc.xlsx")
    shutil.copy(src, tmp)
    subprocess.run([sys.executable, RECALC, tmp, "240"], capture_output=True, text=True, check=True)
    wb = load_workbook(tmp, data_only=True)
    rs, ca = wb["Resumen"], wb["Cálculo"]
    out = {"res": [[rs.cell(r, c).value for c in range(1, 7)] for r in range(4, 20)]}
    R = GC.R
    for k in ("B_g1", "B_g2", "D_h", "D_t", "B_hc"):
        out[k] = [ca.cell(R[k], 3 + i).value for i in range(10)]
    out["u"] = [[ca.cell(GC.U0 + i, 3 + j).value for j in range(10)] for i in range(8)]
    return out


# ------------------------------------------------------------------ Word 1: todos los formatos
def bloques_general(X, tmp):
    b = []
    p, h1, h2, nota, bul = (lambda t: b.append({"t": "p", "x": t}), lambda t: b.append({"t": "h1", "x": t}),
                            lambda t: b.append({"t": "h2", "x": t}), lambda t: b.append({"t": "nota", "x": t}),
                            lambda t: b.append({"t": "b", "x": t}))

    def img(ruta, pie, ancho=16.5):
        import PIL.Image as Im
        w, hh = Im.open(ruta).size
        b.append({"t": "img", "ruta": ruta, "pie": pie, "ancho": ancho, "anchoPx": w, "alto": hh})
    b.append({"t": "titulo", "x": "Esquemas de corte de cuerpos: dos guillotinas en serie"})
    b.append({"t": "sub", "x": "FLAMA S.A. · Opción D: hojas estándar, guillotina 1 CENA 8 × 3200 (franjas) y guillotina 2 "
                               "QC12Y 6 × 2500 (piezas). Medidas de los planos de recipiente."})
    h1("1. Cómo trabajan las dos guillotinas")
    p("Los cuerpos se cortan en dos pasos, igual que antes: **1.er corte** en franjas y **2.º corte** de cada franja en "
      "piezas (desarrollos). Lo que cambia es que cada paso tiene su máquina y que el segundo corta varias franjas a la "
      "vez:")
    bul("**Guillotina 1, CENA 8 × 3200** (control E21, tope trasero 20-1.000 mm, 10 golpes por minuto; cotización "
        "CENA): corta la hoja en franjas. Entra una hoja por golpe, con el lado largo paralelo a la cuchilla.")
    bul("**Pulmón de franjas**: las franjas esperan en el carro porta-desarrollos entre las dos máquinas, así una no "
        "frena a la otra.")
    bul(f"**Guillotina 2, QC12Y 6 × 2500** (cuchilla de 2.550 mm, tope 20-800 mm, control E21, 7,5 kW; "
        f"[publicación del link]({URL_LINK}), USD 10.700 FOB): se apoyan varias franjas una al lado de la otra, tantas "
        "como entran en 2.500 mm, y cada golpe corta una pieza de cada franja, a 20 golpes por minuto.")
    bul("**Rodantes**: la pieza mide de 858 a 1.210 mm y no entra en el tope de 800 mm de la G2; el 2.º corte se hace en "
        "la G1 (tope de 1.000 mm), también con franjas en paralelo en sus 3.200 mm.")
    p("El tiempo de cada máquina sale de sus golpes por minuto: golpes por hoja ÷ golpes por minuto. La línea rinde lo "
      "que rinde la más lenta de las dos (cuello de botella).")
    ruta = os.path.join(tmp, "proceso.png")
    fig_proceso(ruta)
    img(ruta, "Figura 1. Recorrido de la chapa por las dos guillotinas.")
    h1("2. Resumen por formato")
    filas = []
    for x in HOJAS + [MIX]:
        filas.append([x["f"], f"{n(x['B'])} × {n(x['C'])}", n(x["e"], 2),
                      f"{x['nfr']} × {x['pzf']}" if not x.get("piezas_txt") else "1 × 4", str(x["piezas"]),
                      n(x["aprov"] * 100, 1) + " %", x["maq"], str(x["par"]), n(x["g1"], 1), n(x["g2"], 1),
                      n(x["m1"] + x["m2"], 2), n(x["cph"])])
    b.append({"t": "tabla", "cab": ["Formato", "Hoja (mm)", "e (mm)", "Franjas × piezas", "Piezas por hoja",
                                    "Aprov.", "2.º corte en", "Franjas en paralelo", "Golpes G1 por hoja",
                                    "Golpes G2 por hoja", "Min por hoja", "Cuerpos por hora"],
              "cols": [12, 11, 6, 9, 7, 7, 7, 7, 7, 7, 7, 8], "filas": filas, "num": list(range(2, 12))})
    nota("Cuerpos por hora: piezas por hoja × 60 ÷ minutos de la máquina más cargada (ritmo de máquina, sin "
         "manipulación). El 70 kg se corta en la hoja mixta: su pieza de 1.210,5 mm supera el tope de la G1.")
    g1, g2 = X["B_g1"][-1], X["B_g2"][-1]
    p(f"Con la demanda de 2035 la G1 trabaja **{n(g1)} h** y la G2 **{n(g2)} h** al año a ritmo de máquina (hoja "
      "Cálculo del Excel, opción D).")
    h1("3. Esquemas por formato")
    k = 0
    for i, x in enumerate(HOJAS + [MIX]):
        if x["f"] == "70 kg":
            continue
        k += 1
        h2(f"3.{k} {'Cuerpo ' if x['f'][0].isdigit() else 'Hoja '}{x['f']}")
        ruta = os.path.join(tmp, f"f{i}.png")
        fig_formato(x, ruta)
        img(ruta, f"Figura {k + 1}. {x['f']}: hoja {n(x['B'])} × {n(x['C'])} × {n(x['e'], 2)} mm y 2.º corte en la "
                  f"{'guillotina 2' if x['maq'] == 'G2' else 'guillotina 1'}.")
        pzs = x.get("piezas_txt") or f"{n(x['pz'], 1)} mm"
        p(f"1.er corte en la G1 con el tope en **{n(x['tope1'], 1)} mm**: {x['nfr']} franja{'s' if x['nfr'] > 1 else ''} de {n(x['fr'], 1)} × "
          f"{n(x['C'])} mm{'; la franja se saca cortando la orilla del otro lado' if x['tope1'] != x['fr'] else ''}. "
          f"2.º corte en la {x['maq']} con {x['par']} franjas en paralelo y piezas de {pzs}: {x['piezas']} cuerpos por "
          f"hoja, {n(x['g1'], 1)} golpes de G1 y {n(x['g2'], 1)} de G2 por hoja. Sobra una orilla de "
          f"{n(x['orilla'], 1)} mm a lo ancho y {n(x['recorte'], 1)} mm al final de cada franja; aprovechamiento "
          f"{n(x['aprov'] * 100, 1)} %.")
    b.append({"t": "salto"})
    h1("4. Medidas de las piezas (planos)")
    p("Todas las medidas salen de los planos de recipiente (modelo 3D). El cuerpo se desarrolla por la fibra media: "
      "desarrollo = π·(Ø exterior − espesor). El alto es el del cuerpo del plano, con el labio del encastre.")
    filas = []
    for f in DC.FORM:
        al, de, e = DC.CUERPO[f][:3]
        filas.append([f, n(GC.DIAM[f], 1), n(e, 2), n(al, 1), n(de, 1), DC.PLANO[f]])
    b.append({"t": "tabla", "cab": ["Formato", "Ø ext. (mm)", "Espesor (mm)", "Alto (mm)", "Desarrollo (mm)", "Plano"],
              "cols": [10, 10, 10, 10, 11, 30], "filas": filas, "num": [1, 2, 3, 4]})
    nota("El 1 kg se corta de chapa de 0,9 mm por decisión del grupo.")
    h2("4.1 Disco de cúpulas y fondos: embutido")
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
         "el espesor, mínimo 0,7 mm; al borde, 1,5 veces el de avance). Antes se usaban discos de la planilla «Dimensiones "
         "de chapa» (108 a 258 mm); con el plano dan de 89 a 231,5 mm.")
    h1("5. Qué cambia en la comparación de alternativas")
    res = {r[0]: r[1:] for r in X["res"] if r and r[0]}
    va = res["Valor actual a 10 años (USD)"]
    p(f"Con el 1 kg en chapa, las dos guillotinas y las medidas del plano, la **opción D** (hojas + fleje) sigue siendo "
      f"la que conviene de las que cortan en planta: valor actual de USD {n(va[3])}, contra {n(va[1])} de B, "
      f"{n(va[0])} de A y {n(va[2])} de C. El margen se achicó: la hoja tendría que subir "
      f"{n(res['Margen de D: suba del precio de la hoja que la iguala con A'][0] * 100, 1)} % para que A la iguale. El "
      "detalle está en el Excel Comparacion_corte (hojas Resumen y Cálculo).")
    h1("6. Pendiente")
    bul("Precio de la guillotina 2 puesta en planta: los USD 10.700 son FOB, sin flete ni nacionalización.")
    h1("Fuentes")
    for t in ["Cotización CENA, guillotina hidráulica 8 × 3200 E21 (Drive): USD 36.800 + IVA, tope 20-1.000 mm, 10 golpes "
              "por minuto.",
              f"[Publicación Alibaba 1600900259147, QC12Y 6 × 2500]({URL_LINK}): cuchilla 2.550 mm, tope 20-800 mm, "
              "USD 10.700 FOB.",
              "Molinari Maquinarias, ficha de la guillotina Panther HG (formulario de cotización): HG 6 × 2500, 20 golpes "
              "por minuto.",
              "[MISUMI, Press Dies Tutorial: puentes de corte](https://www.misumi-techcentral.com/tt/en/press/2009/09/"
              "012-basics-of-blanking-work-1-blanking-work.html).",
              "[Harsle, How to Calculate Deep Drawing Parts](https://harslepress.com/how-to-calculate-deep-drawing-parts/).",
              "[EasyChair, preprint Vxvp: relación de embutido m1](https://easychair.org/publications/preprint/Vxvp).",
              "[MathWorld, Oblate Spheroid](https://mathworld.wolfram.com/OblateSpheroid.html) y "
              "[Paraboloid](https://mathworld.wolfram.com/Paraboloid.html).",
              "Hierros Parrotta, presupuesto 413329; Pradecon 173170 y 173195; Pacheco Chapas PR 42021 y 42024."]:
        bul(t)
    return b


# ------------------------------------------------------------------ Word 2: cuerpo de 1 kg
def bloques_1kg(X, tmp):
    b = []
    p, h1, nota, bul = (lambda t: b.append({"t": "p", "x": t}), lambda t: b.append({"t": "h1", "x": t}),
                        lambda t: b.append({"t": "nota", "x": t}), lambda t: b.append({"t": "b", "x": t}))
    x = HOJAS[0]
    al, de, e = DC.CUERPO["1 kg"][:3]
    u35 = X["u"][0][-1]
    hojas35 = u35 / x["piezas"]
    b.append({"t": "titulo", "x": "Esquema de corte del cuerpo de 1 kg en chapa de 0,9 mm"})
    b.append({"t": "sub", "x": "FLAMA S.A. · Cuerpo de 1 kg desde hoja doble decapada N.° 20 (0,9 mm), cortado en las "
                               "dos guillotinas en serie. Mismo criterio que «Esquemas de corte de cuerpos»."})
    h1("1. Pieza y chapa")
    filas = [["Ø exterior del cuerpo", "76,2 mm", "Plano recipiente 1 kg (G809)"],
             ["Alto del cuerpo", f"{n(al, 1)} mm", "Plano: cuerpo del modelo 3D con los dos labios del encastre"],
             ["Desarrollo", f"{n(de, 1)} mm = π·(76,2 − 0,9)", "Fibra media, igual que 2,5 a 100 kg"],
             ["Hoja", "1220 × 2440 × 0,9 mm", "Hierros Parrotta, presupuesto 413329 (28/09/2026)"],
             ["Precio de la hoja", "USD 1,356/kg sin IVA (USD 30,24 la hoja de 22,3 kg de balanza)",
              "Hierros Parrotta, con 6,84 % de descuento, contado"]]
    b.append({"t": "tabla", "cab": ["Dato", "Valor", "Fuente"], "cols": [10, 14, 16], "filas": filas})
    nota("El esquema anterior usaba 255 mm de alto (corte actual del caño). El plano da 263,5 mm; igual entran 45 "
         "cuerpos por hoja.")
    h1("2. Esquema y corte en las dos guillotinas")
    ruta = os.path.join(tmp, "f1kg.png")
    fig_formato(x, ruta)
    import PIL.Image as Im
    w, hh = Im.open(ruta).size
    b.append({"t": "img", "ruta": ruta, "pie": "Hoja de 1220 × 2440: 5 franjas de 236,5 mm y 9 cuerpos por franja; "
                                               "en la G2 entran 10 franjas.", "ancho": 16.5, "anchoPx": w, "alto": hh})
    filas = [["Franjas × cuerpos por franja", f"{x['nfr']} × {x['pzf']} = {x['piezas']} cuerpos"],
             ["Aprovechamiento de la hoja", n(x["aprov"] * 100, 1) + " %"],
             ["Sobrante", f"Orilla de {n(x['orilla'], 1)} × 2440 mm y {n(x['recorte'], 1)} mm al final de cada franja"],
             ["Guillotina 1 (CENA)", f"Tope en {n(x['fr'], 1)} mm: 5 golpes por hoja = {n(x['m1'], 2)} min"],
             ["Guillotina 2 (QC12Y)", f"{x['par']} franjas en paralelo (2.365 de 2.500 mm), tope en {n(x['pz'], 1)} "
                                      f"mm: 9 golpes cada 2 hojas = {n(x['g2'], 1)} golpes y {n(x['m2'], 2)} min por "
                                      "hoja"],
             ["Ritmo de la línea", f"{n(x['cph'])} cuerpos por hora (manda la G1)"],
             ["Año 2035", f"{n(u35)} cuerpos = {n(hojas35)} hojas: G1 {n(hojas35 * x['m1'] / 60)} h y G2 "
                          f"{n(hojas35 * x['m2'] / 60)} h al año"]]
    b.append({"t": "tabla", "cab": ["Dato", "Valor"], "cols": [10, 26], "filas": filas})
    nota("Tiempos a ritmo de máquina (golpes por minuto), sin manipulación: 10 golpes por minuto la G1 y 20 la G2.")
    h1("3. Alternativas evaluadas")
    filas = []
    for (B, C), lado in (((1220, 2440), "franjas a lo largo"), ((2440, 1220), "franjas a lo ancho"),
                         ((1000, 2000), "franjas a lo largo"), ((2000, 1000), "franjas a lo ancho")):
        y = hoja("1 kg", B, C)
        filas.append([f"{min(B, C)} × {max(B, C)} ({lado})", f"{y['nfr']} × {y['pzf']}", str(y["piezas"]),
                      n(y["aprov"] * 100, 1) + " %", n(y["g1"], 1), n(y["g2"], 1), n(y["m1"] + y["m2"], 2)])
    b.append({"t": "tabla", "cab": ["Hoja", "Franjas × piezas", "Cuerpos", "Aprov.", "Golpes G1", "Golpes G2",
                                    "Min por hoja"], "cols": [16, 9, 7, 7, 7, 7, 8], "filas": filas,
              "num": [2, 3, 4, 5, 6]})
    p("Se elige la hoja de 1220 × 2440 con franjas a lo largo: da 45 cuerpos, el mejor aprovechamiento y la menor "
      "cantidad de golpes de G1, que es la máquina que manda. La de 1000 × 2000 (Parrotta) aprovecha menos.")
    h1("4. Observaciones")
    bul("Espesor: la IRAM 3525, 3.2.1 a) pide chapa de 0,71 mm como mínimo y la 3.2.2.1 admite 1 costura longitudinal "
        "y 2 transversales: 0,9 mm con costura cumple (validado en el proyecto).")
    bul("El cuerpo de chapa necesita rolado y soldadura longitudinal TIG, que el caño no tenía; el mandril de la "
        "soldadora tiene que entrar en el interior de 74,4 mm.")
    bul("Las orillas de 37,5 mm y los recortes de 68,5 mm no sirven para discos: la cúpula del 1 kg necesita un fleje "
        "de 93 mm de ancho.")
    return b


def render(bloques, salida, pie):
    js = os.path.join(AQUI, "word_corte.js")
    tmpj = salida + ".json"
    with open(tmpj, "w", encoding="utf-8") as fh:
        json.dump(bloques, fh, ensure_ascii=False)
    env = dict(os.environ, NODE_PATH=NODE_PATH)
    subprocess.run(["node", js, tmpj, salida, pie], check=True, env=env)
    os.remove(tmpj)


def main():
    X = excel()
    tmp = tempfile.mkdtemp(prefix="figs_corte_")
    render(bloques_general(X, tmp), os.path.join(SALIDA, "Esquemas_de_corte_cuerpos_guillotina.docx"),
           "Esquemas de corte de cuerpos")
    render(bloques_1kg(X, tmp), os.path.join(SALIDA, "Esquema_de_corte_cuerpo_1_kg_chapa_09_mm.docx"),
           "Corte del cuerpo de 1 kg")
    print("ok")


if __name__ == "__main__":
    main()
