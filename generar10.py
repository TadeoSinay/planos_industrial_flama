"""Genera las láminas del layout v10 (DXF para AutoCAD + PDF) en salida/v10/ después de verificar el modelo."""

import os
import sys

from planta.lamina import nuevo_doc, FORMATOS
from planta import dibujo as D
from planta.exportar import preparar_layouts, pdf_hojas
from planta10 import laminas as L10
from planta10.verificar import verificar

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida", "v10")
PLANOS = [("FL_PI10_01", "A0", L10.fl_01), ("FL_PI10_02", "A0", L10.fl_02), ("FL_PI10_03", "A0", L10.fl_03),
          ("FL_PI10_04", "A0", L10.fl_04), ("FL_PI10_05", "A0", L10.fl_05)]


def generar(sel):
    err, _ = verificar(silencioso=True)
    if err:
        for s in err:
            print("ERROR", s)
        sys.exit("El modelo no pasa la verificación: no se generan láminas.")
    os.makedirs(SALIDA, exist_ok=True)
    for cod, fmt, fn in PLANOS:
        if sel and cod not in sel:
            continue
        doc = nuevo_doc()
        D.capas_planta(doc)
        fn(doc, 0.0)
        preparar_layouts(doc, [(cod, fmt, 0.0)])
        doc.saveas(os.path.join(SALIDA, f"{cod}.dxf"))
        pdf = pdf_hojas(doc, [(cod, fmt, 0.0)], capas_color=True)
        pdf.save(os.path.join(SALIDA, f"{cod}.pdf"))
        print(os.path.join(SALIDA, f"{cod}.pdf"))


if __name__ == "__main__":
    generar(sys.argv[1:])
