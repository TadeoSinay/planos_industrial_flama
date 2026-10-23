"""Layout rev22 (plano_carros_rev22: planta integrada carros + manuales + recargas + PT único) para la app.

El plano viene en PDF; los nombres de los sectores están dibujados como trazos, así que no se leen como texto:
  * fondo_rev22.webp: el plano rasterizado en metros (x este, y sur; origen en la esquina noroeste de la nave),
  * muros y portones: los trazos gruesos del PDF (paredes negras de 4,5 y 6,5 pt; portones naranjas de 6 pt),
  * puestos: ubicados a mano sobre una grilla de 1 m encima del plano (centro de cada puesto, ±0,5 m),
  * pasillos: los del plano (nombre y ancho rotulados en él), para que los recorridos vayan por ahí.
Escala: la nave mide 51,7 m (rótulo del plano) = 987,9 pt entre los ejes de los muros este y oeste.
Uso: python3 generar_rev22.py ../../../referencias/plano_carros_rev22.pdf"""
import io
import json
import os
import sys

import pymupdf
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
S = 987.9 / 51.7            # pt por metro
X0, Y0 = 617.8, 533.0       # esquina noroeste de la nave en el PDF (pt)
LIM = [-22, -15.5, 94, 86.5]  # x, y, ancho, alto en m (todo el predio)
PPM = 44                    # px por metro del fondo

# id, línea, nombre, x, y (m) — ubicados sobre el plano rev22
P = [
    # recargas (zona de recargas, U 15,1 × 15,3 m) y su playa
    ("EXT_RETIRO", "EXT", "Playa de recargas (clientes y flota)", 9.5, -4.0),
    ("RE", "REC", "Pulmón de entrada (E)", 15.0, 2.3),
    ("R1", "REC", "R1 · Recepción y registro", 12.6, 6.0),
    ("R2", "REC", "R2 · Inspección visual", 12.6, 7.7),
    ("R5", "REC", "R5 · Líquidos: agua, AFFF, clase K", 12.6, 9.6),
    ("R7", "REC", "R7 · Halogenados", 12.6, 12.0),
    ("R9", "REC", "R9 · Desarme e inspección general", 12.6, 13.8),
    ("R22", "REC", "R22 · Inutilización", 12.6, 15.6),
    ("R10", "REC", "R10 · Laboratorio", 12.6, 18.0),
    ("PL", "REC", "PL · Pulmón a recinto", 7.0, 17.0),
    ("R3", "REC", "R3 · Descarga ABC", 1.2, 17.2),
    ("R4", "REC", "R4 · Descarga ABC y BC", 1.2, 15.3),
    ("R8", "REC", "R8 · Desarme (recinto de polvo)", 3.6, 14.4),
    ("R11", "REC", "R11 · Prueba hidráulica", 7.6, 14.6),
    ("R12", "REC", "R12-R13 · Secado y videoscopio", 7.6, 12.9),
    ("R14", "REC", "R14 · Pintura (cabina)", 1.0, 12.2),
    ("R16", "REC", "R16 · Carga ABC y BC", 3.6, 11.0),
    ("R18", "REC", "R18-R19 · Ensamblaje general y peso", 7.6, 11.1),
    ("R6", "REC", "R6 · CO₂: recuperación y carga", 7.6, 9.7),
    ("R17", "REC", "R17 · Presurización", 3.6, 7.6),
    ("R20", "REC", "R20 · Ensayo de pérdidas", 7.6, 7.9),
    ("R21", "REC", "R21 · Precinto y despacho", 7.6, 6.2),
    ("RD", "REC", "Pulmón de salida (D)", 4.5, 2.3),
    ("EXT_ENTREGA", "EXT", "Recorrido de entrega (flota)", 4.5, -4.0),
    # materia prima
    ("MP_GALPON", "MP", "Dársena de descarga de MP (zona D)", -6.5, 37.5),
    ("MP_TRAZ", "MP", "Puesto de trazabilidad de MP (remitos)", 2.6, 20.6),
    ("MP_ALM", "MP", "Almacén de MP (carros + manuales)", 6.2, 33.0),
    # corte y marcado
    ("G1", "MAN", "2 · Guillotina 1 (franjas)", 14.0, 43.6),
    ("G2", "MAN", "2 · Guillotina 2 (piezas)", 14.8, 39.6),
    ("MARC1", "MAN", "Marcado de manuales (marcadora 1)", 13.4, 33.8),
    ("MARC2", "CAR", "2.1 · Marcado de carros (marcadora 2)", 16.3, 42.0),
    # manuales
    ("M1", "MAN", "M1 · Cilindrado 1 a 10 kg", 17.0, 34.2),
    ("M3B", "MAN", "M3b · Soldadura longitudinal TIG 1 kg", 21.0, 34.8),
    ("M3", "MAN", "M3 · Soldadura longitudinal 2,5 a 10 kg", 26.0, 34.8),
    ("M9", "MAN", "M9 · Corte y embutido (cúpulas y fondos)", 14.5, 28.4),
    ("M6A", "MAN", "M6a · Preparación de cuello", 21.7, 28.0),
    ("M6B", "MAN", "M6b · Soldadura de cuello", 29.8, 34.8),
    ("M4", "MAN", "M4 · Encastre de fondo", 26.2, 28.0),
    ("M5", "MAN", "M5 · Bordoneado", 30.6, 28.0),
    ("M7", "MAN", "M7 · Soldadura circunferencial", 33.7, 34.8),
    ("M8", "MAN", "M8 · Control de espesor", 38.3, 34.3),
    ("PHM", "MAN", "PH manuales", 41.6, 33.4),
    ("SEC", "MAN", "Secado (manuales y carros)", 44.6, 33.4),
    ("M10", "MAN", "M10 · Granallado", 37.0, 28.4),
    ("M11", "MAN", "M11 · Detección y corrección de defectos", 41.5, 28.4),
    ("M18", "MAN", "M18 · Pintura en polvo + horno", 32.0, 21.0),
    ("M12", "MAN", "M12 · Carga de polvo", 23.6, 18.0),
    ("M13", "MAN", "M13 · Ensamblaje", 19.6, 18.2),
    ("M14", "MAN", "M14 · Presurización", 19.6, 13.4),
    ("M15", "MAN", "M15 · Ensayo de pérdidas", 19.6, 10.4),
    ("M16", "MAN", "M16 · Etiquetado", 19.6, 8.0),
    ("M17", "MAN", "M17 · Embalaje y paletizado", 25.2, 8.0),
    ("PTM", "PT", "16 · Almacén de PT (rack, 90 lugares)", 35.0, 10.0),
    ("ANDEN", "PT", "Andén de PT (20 pallets)", 26.0, 2.6),
    ("EXT_DESPACHO", "EXT", "Despacho: sider o camión chico (portón M)", 30.5, -4.0),
    # carros
    ("C3", "CAR", "3 · Cilindrado", 21.5, 45.2),
    ("C4", "CAR", "4 · Punteo", 22.0, 40.2),
    ("C5", "CAR", "5 · Soldadura longitudinal", 29.6, 40.2),
    ("C6", "CAR", "6 · Soldadura de cupla", 35.4, 40.2),
    ("C7", "CAR", "7 · Armado y soldadura circunferencial", 41.2, 40.2),
    ("C80", "CAR", "8.0 · Casquetes, chapas e insumos", 29.2, 45.2),
    ("C81", "CAR", "8.1 · Fabricación de accesorios", 37.6, 45.2),
    ("C8", "CAR", "8 · Soldadura de accesorios", 47.5, 40.2),
    ("PHC", "CAR", "PH carros", 48.4, 33.8),
    ("C11", "CAR", "11 · Espera del pintor", 47.0, 28.2),
    ("EXT_PINTOR", "EXT", "Pintor tercerizado (portón E1)", 56.5, 27.7),
    ("C12", "CAR", "12 · Recepción de pintados y ruedas", 42.6, 23.2),
    ("C13", "CAR", "13 · Carga y presurización (con pérdidas)", 43.2, 19.0),
    ("C15", "CAR", "15 · Etiquetado + no conformes", 44.2, 11.5),
    ("C17", "CAR", "17 · Ensayos de lote", 48.2, 7.2),
    ("C16", "PT", "16c · Expedición de carros (PT carros)", 47.5, 2.6),
    ("EXT_CARROS", "EXT", "Entrega de carros (Master, portón S)", 46.3, -4.0),
    # PT: trazabilidad
    ("REV", "PT", "Trazabilidad de PT (recepción de revendidos)", 42.7, 6.4),
]
RUTAS = {
    "REC-ABC": ("REC", "Recarga ABC", ["EXT_RETIRO", "RE", "R1", "R2", "PL", "R3", "R8", "R16", "R17", "R20", "R21", "RD", "EXT_ENTREGA"]),
    "REC-ABC-PH": ("REC", "Recarga ABC con PH", ["EXT_RETIRO", "RE", "R1", "R2", "PL", "R3", "R8", "R11", "R12", "R16", "R17", "R20", "R21", "RD", "EXT_ENTREGA"]),
    "MAN-STD": ("MAN", "Manuales 2,5 a 10 kg", ["MP_ALM", "G1", "G2", "MARC1", "M1", "M3", "M4", "M5", "M7", "M8", "PHM", "SEC", "M10", "M11",
                                                "M18", "M12", "M13", "M14", "M15", "M16", "M17", "PTM", "ANDEN", "EXT_DESPACHO"]),
    "MAN-1KG": ("MAN", "Manuales 1 kg", ["MP_ALM", "G1", "G2", "MARC1", "M1", "M3B", "M4", "M5", "M7", "M8", "PHM", "SEC", "M10", "M11",
                                         "M18", "M12", "M13", "M14", "M15", "M16", "M17", "PTM", "ANDEN", "EXT_DESPACHO"]),
    "CAR-STD": ("CAR", "Carro rodante", ["MP_ALM", "G1", "G2", "MARC2", "C3", "C4", "C5", "C6", "C7", "C8", "PHC", "SEC", "C11", "EXT_PINTOR",
                                         "C12", "C13", "C15", "C17", "C16", "EXT_CARROS"]),
}
# Pasillos rotulados en el plano (x, y, ancho, alto en m)
PASILLOS = [
    [0.0, 3.6, 18.0, 1.4],      # calle 2,75 m de recargas
    [17.0, 0.4, 28.0, 4.3],     # calle de carga 4,75 m (andén ↔ rack ↔ portón M)
    [9.4, 5.0, 2.0, 16.6],      # pasillo central de recargas 2,3 m
    [15.6, 5.0, 1.4, 16.6],     # pasillo peatonal 1,5 m
    [0.0, 21.6, 18.0, 3.0],     # pasillo autoelevador de manuales 4,5 m
    [10.5, 24.2, 16.0, 1.0],    # senda peatonal 1,5 m
    [17.0, 15.6, 34.7, 1.0],    # pasillo norte 1,5 m
    [30.0, 4.8, 2.8, 10.8],     # pasillo PT 1
    [37.0, 4.8, 1.8, 10.8],     # pasillo PT 2
    [49.8, 4.6, 1.9, 33.0],     # pasillo este 2,0 m
    [17.0, 30.6, 34.7, 1.0],    # pasillo de carros 1,5 m
    [17.0, 42.1, 34.7, 0.9],    # pasillo 1,0 m entre las filas de carros
    [0.0, 47.1, 44.0, 3.9],     # pasillo principal del autoelevador 4,0 m
    [3.0, 25.0, 6.2, 22.1],     # calle del almacén 6,2 m
    [0.0, 51.3, 52.0, 1.2],     # pasillo peatonal sur 1,5 m
    [-11.0, -12.5, 72.0, 5.5],  # calle norte del predio
]


def main(pdf):
    d = pymupdf.open(pdf)
    p = d[0]
    m = lambda pt: [round((pt.x - X0) / S, 2), round((pt.y - Y0) / S, 2)]
    muros, portones = [], []
    for x in p.get_drawings():
        col, w = x.get("color"), x.get("width") or 0
        if not col:
            continue
        seg = [[m(it[1]), m(it[2])] for it in x["items"] if it[0] == "l"]
        if max(col) < 0.2 and w >= 4.4:
            muros += seg
        elif tuple(round(v, 2) for v in col) == (0.9, 0.49, 0.13) and abs(w - 6) < 0.1:
            portones += [dict(id=f"P{i}", de=s[0], a=s[1], texto="") for i, s in enumerate(seg)]
    x0, y0, w, h = LIM
    z = PPM / S
    clip = pymupdf.Rect(X0 + x0 * S, Y0 + y0 * S, X0 + (x0 + w) * S, Y0 + (y0 + h) * S)
    pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip)
    Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB").save(os.path.join(AQUI, "fondo_rev22.webp"), "WEBP", quality=70, method=6)
    layout = dict(fuente="plano_carros_rev22 (PDF) · Planta integrada carros + manuales", revision=22,
                  nave=dict(ancho=51.7, largo=52.6, anexos=[[0, 52.6, 26.4, 14.3]]), fondo=dict(x=x0, y=y0, w=w, h=h),
                  sectores=[dict(id="s_" + q[0], nombre=q[2], rect=[q[3] - 0.8, q[4] - 0.8, 1.6, 1.6]) for q in P],
                  muros=[s for s in muros], portones=portones, pasillos=[dict(id=f"p{i}", rect=r) for i, r in enumerate(PASILLOS)],
                  divisiones=[], puertas=[])
    cat = dict(fuente="Puestos ubicados sobre plano_carros_rev22; recorridos según sus circuitos 1 a 45",
               puestos=[dict(id=q[0], linea=q[1], nombre=q[2], sector="s_" + q[0], x=q[3], y=q[4], fuera=q[1] == "EXT") for q in P],
               zonas=[], limites=LIM, rutas={k: dict(linea=v[0], nombre=v[1], pasos=v[2]) for k, v in RUTAS.items()})
    json.dump(layout, open(os.path.join(AQUI, "layout_rev22.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(cat, open(os.path.join(AQUI, "catalogo_rev22.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(muros), "muros ·", len(portones), "portones ·", len(P), "puestos")


if __name__ == "__main__":
    main(sys.argv[1])
