"""Genera las láminas de la planta industrial (DXF para AutoCAD + PDF) en salida/."""

import os
import sys

from planta.lamina import nuevo_doc, FORMATOS
from planta import dibujo as D
from planta import planos as PL
from planta import formal as FO
from planta import chapa as CH
from planta.exportar import preparar_layouts, pdf_hojas

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida")

PLANOS = {
    "FL_PI_01": [("FL_PI_01", "A0", PL.fl_pi_01)],
    "FL_PI_02": [("FL_PI_02", "A0", PL.fl_pi_02)],
    "FL_PI_03": [("FL_PI_03", "A0", PL.fl_pi_03)],
    "FL_PI_04": [("FL_PI_04", "2A0", FO.fl_pi_04)],
    "FL_PI_05": [("FL_PI_05", "A1", CH.lamina)],
}


def generar(cod, hojas):
    doc = nuevo_doc()
    D.capas_planta(doc)
    lay, ox = [], 0.0
    for nombre, fmt, fn in hojas:
        fn(doc, ox)
        lay.append((nombre, fmt, ox))
        ox += FORMATOS[fmt][0] + 400
    preparar_layouts(doc, lay)
    os.makedirs(SALIDA, exist_ok=True)
    doc.saveas(os.path.join(SALIDA, f"{cod}.dxf"))
    pdf = pdf_hojas(doc, lay, capas_color=True)
    pdf.save(os.path.join(SALIDA, f"{cod}.pdf"))
    return os.path.join(SALIDA, f"{cod}.pdf")


if __name__ == "__main__":
    sel = sys.argv[1:] or list(PLANOS)
    for cod in sel:
        print(generar(cod, PLANOS[cod]))
    if not sys.argv[1:]:
        from planta import memoria
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "MEMORIA_DE_CALCULO.md")
        memoria.generar(ruta)
        print(ruta)
