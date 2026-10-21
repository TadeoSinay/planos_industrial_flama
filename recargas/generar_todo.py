"""Corre toda la cadena en orden y deja los 5 Excel en salida/.

1. Aprovechamientos de recargas (comercial e industrial) -> recálculo.
2. Manuales y Carros sobre los archivos del grupo (referencias/), con el pedido de sustitutos de cada planta.
3. Recargas.xlsx (logística), que lee los dimensionamientos ya recalculados.
Al final se deja __xludf.DUMMYFUNCTION como lo exporta Google, para que al subirlo a Sheets vuelva a ser IMPORTRANGE.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import actualizar_manuales_carros as mc  # noqa: E402
import generar_dim_recargas as g  # noqa: E402
import generar_logistica_recargas as lg  # noqa: E402

if __name__ == "__main__":
    dims = []
    for p in ("Comercial", "Industrial"):
        dem, cap, recurso, umbral, t_max, anio_2t, _ = g.modelo_demanda(p)
        dims.append(g.generar(p, g.plan_capacidad(dem, cap, recurso, umbral, t_max, anio_2t)))
    for ruta in dims:
        mc.recalc(ruta)
    ped = mc.pedidos()
    for f in (mc.manuales, mc.carros):
        ruta, verif = f(ped)
        print(ruta, "| fórmulas de demanda fuera de patrón:", len(verif))
    log = lg.generar()
    mc.recalc(log)
    for ruta in dims + [log]:
        mc.arreglar_dummy(ruta)
    print("Listo:", ", ".join(os.path.basename(r) for r in dims + [log]))
