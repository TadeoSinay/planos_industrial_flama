"""Word explicativo de la trazabilidad interna (salida/Trazabilidad_interna_FLAMA.docx): esquema, identificación sin QR
(marcado Pannier y etiqueta del fabricante), kanban de MP que se carga con la planilla de conteo del almacén, lugar fijo
de cada código, puntos de pedido de las 125 MP, kanban de PT por zonas con fechas, fichas de control de los procesos críticos con su norma, trazabilidad y layout. Datos: los mismos
libros que build.py; capturas: capturas/*.png (app armada con build.py y recorrida con Playwright)."""
import json
import math
import os
import subprocess

from PIL import Image

import build as B

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
DOCX = os.path.join(RAIZ, "salida", "Trazabilidad_interna_FLAMA.docx")
JS = os.path.join(RAIZ, "corte", "word_corte.js")
NODE_PATH = os.environ.get("NODE_PATH", "/tmp/claude-0/-home-user-TP-optimizacion/"
                                        "15292aaf-e550-5dee-a83e-77fd9177a6ef/scratchpad/jw/node/node_modules")
CAP = os.path.join(AQUI, "capturas")


def n(x, d=0):
    if x is None:
        return "—"
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def bloques():
    mp_wb, pt_wb, bal_wb = B.libro("MP-FLAMA2035.xlsx"), B.libro("PTPINTADO-FLAMA2035.xlsx"), B.libro("Balanceo-FLAMA2035.xlsx")
    MP = B.stock_mp(mp_wb)
    ALM = B.almacenes(mp_wb)
    LUG = B.lugares(MP, ALM)
    PT, APT, CARROS, DESP = B.stock_pt(pt_wb)
    PZ = B.puestos(bal_wb)
    pz = lambda l, k: next((p["nom"] for p in PZ[l] if p["n"] == k), "")
    bl = []
    add = lambda t, x=None, **k: bl.append(dict(t=t, x=x, **k))
    p = lambda x: add("p", x)
    b = lambda x: add("b", x)

    def tabla(cab, filas, cols, num=(), negrita=()):
        bl.append(dict(t="tabla", cab=cab, filas=[[("—" if c is None else str(c)) for c in f] for f in filas], cols=cols,
                       num=list(num), negrita=list(negrita)))

    def img(nombre, pie, ancho=16):
        ruta = os.path.join(CAP, nombre)
        w, h = Image.open(ruta).size
        bl.append(dict(t="img", ruta=ruta, ancho=ancho, alto=h, anchoPx=w, pie=pie))

    add("titulo", "Trazabilidad interna FLAMA")
    add("sub", "Kanban de almacenes con planilla de conteo, fichas de control de los procesos críticos e identificación sin QR")
    add("sub", "App: trazabilidad/simple (misma estructura y estilo que la app de gestión interna) · Datos: libros 2035 de MP, PT y balanceo")

    add("h1", "En una página")
    b("**Tres piezas.** Un kanban de los almacenes (MP y PT) que se llena con la planilla de conteo del almacén, una ficha "
      "por cada control crítico y una búsqueda que une todo por el número grabado. Sin cámaras.")
    b("**Sin QR.** El QR queda para la atención al cliente. Adentro de la planta, el producto propio se sigue por el n° de "
      "serie del marcado Pannier; el revendido, por el n° de la etiqueta de su fabricante; el equipo en recarga, por la "
      "orden de servicio y el n° grabado del recipiente.")
    b("**Marcado arriba de todo.** Una línea horizontal en el cuerpo, a la izquierda de la costura longitudinal, con el "
      "final siempre a 15 mm de la costura y a 20 mm del borde de la chapa. La faja amarilla de los sustitutos va entera "
      "en la pollera: ya no hay que cortarla.")
    b(f"**Puntos de pedido reales.** Las {len(MP)} MP salen de MP-FLAMA2035 › Stock_MP: seguridad, consumo mientras llega "
      "el pedido y stock máximo. Punto de pedido = seguridad + consumo mientras llega.")
    b(f"**PT por zonas y con fechas.** Rack de {APT['modulos']} módulos × 3 niveles × 2 ({APT['lugares']} lugares), carros "
      f"en el piso, andén de {APT['anden']}, reventa, sustitutos y la rama de pintura, con el mes de fabricación a la vista y "
      "el pallet más viejo marcado (FIFO).")
    b("**16 fichas.** 11 de fabricación (recepción de MP, marcado, tres soldaduras, espesor, PH, defectos, pintado, "
      "pérdidas, PT), 4 de recargas (MP, inspección interior, pérdidas, PT) y 1 de revendidos. Cada campo con criterio se "
      "marca en verde o rojo y la ficha queda conforme o no conforme.")
    b("**Misma estructura que la app de gestión interna.** Barra de contexto, encabezado con pestañas, búsqueda y «Nueva "
      "ficha», dashboard con mapa de flujo, y el mismo layout de planta (plano rev10, mismos puestos y recorridos) con "
      "zoom, filtros por línea y el recorrido de cada lote.")
    img("01_dashboard.png", "Figura 1. Dashboard (datos de ejemplo): indicadores, mapa de flujo por línea según la última "
        "ficha de cada lote, entradas y salidas de 14 días, lotes en curso, MP para pedir, PT y actividad de las fichas.", 15)

    # ------------------------------------------------------------------ 1
    add("h1", "1. Qué identifica a cada cosa (sin QR)")
    tabla(["Qué", "Número", "Dónde está", "Se carga en"], [
        ["Matafuego o cilindro propio", "N° de serie + año", "Marcado Pannier en el cuerpo", "FAB-02 y siguientes"],
        ["Lote de fabricación", "Orden de producción + rango de series", "Hoja de ruta del lote", "Todas las FAB"],
        ["Chapa y fleje", "Colada del certificado", "Etiqueta del paquete o rollo", "FAB-01 → FAB-02"],
        ["Insumos y agentes", "Lote del proveedor", "Bulto", "FAB-01, REC-01"],
        ["Revendido", "N° de serie del fabricante", "Su etiqueta o grabado", "REV-01"],
        ["Equipo en recarga", "Orden de servicio + n° de serie grabado", "Recipiente del cliente", "REC-02 a REC-04"],
        ["Pallet de PT", "PAL-nnnn + lugar", "Etiqueta de pallet", "FAB-11, REV-01"],
    ], [22, 26, 28, 18])
    add("h2", "1.1 Marcado Pannier del producto propio")
    img("fig_marcado.png", "Figura 2. Marcado en el cuerpo: arriba, a la izquierda de la costura, en una línea; faja de "
        "sustituto entera en la pollera (esquemático).", 12)
    b(f"**Cuándo.** En el puesto 6 del balanceo («{pz('man', '6')}»): la Pannier marca el desarrollo todavía plano, entre "
      "la guillotina 2 y el cilindrado (Balanceo-FLAMA2035 › Carga, fila 39). Desde ahí el cuerpo ya tiene su número, y "
      "cada ficha siguiente lo usa. Al marcar en plano, el texto no tiene que seguir la curva del cuerpo.")
    b("**Qué dice.** Fabricante, n° de serie y año (IRAM 3523 5.1); en los carros también la presión de ensayo (IRAM 3550 "
      "5.1); el cuño DPS 15 × 7 al final (Res. 349/07 anexo IV). Una sola línea horizontal y sin código 2D.")
    b("**Dónde.** El mismo lugar de la chapa en todos los modelos: el final del marcado (el cuño) a 15 mm del borde que "
      "forma la costura y el borde de arriba a 20 mm del borde superior de la chapa. El texto crece hacia la izquierda: "
      "109 mm en los manuales y 153 mm en los carros. Los 15 y 20 mm son criterio (libran el cordón y el bordón).")
    b("**Por qué arriba.** Queda por encima de la etiqueta y lejos de la pollera, así que la faja amarilla del sustituto "
      "(≤ 40 mm en la pollera, IRAM 3517-2:2020 9.4.5 b) se pega entera, sin cortes. Los planos FL_MAT (hoja 4, R7) y "
      "FL_REC (hoja 3, R3) ya lo muestran acotado.")
    add("h2", "1.2 Revendidos y recargas")
    p("FLAMA no vuelve a marcar lo que no fabrica. El revendido se recibe con la ficha REV-01, donde se copia el n° de "
      "serie de la etiqueta o el grabado de su fabricante (uno por línea), la marca, el año y el sello IRAM; queda en la "
      "zona de reventa del PT y sale con su remito. En recargas, el equipo del cliente se sigue con la orden de servicio "
      "y el n° de serie que grabó su fabricante.")

    # ------------------------------------------------------------------ 2
    add("h1", "2. Kanban de los almacenes de MP")
    p("Cada MP es una tarjeta. La tarjeta cambia de columna con cada planilla de conteo, retiro a la línea o recepción: "
      "bajo seguridad, para pedir (en el punto de pedido), pedido en camino, bien o sin conteo. La barra muestra el stock "
      "contra el máximo, con una marca roja en la seguridad y una negra en el punto de pedido.")
    add("nota", "Punto de pedido = stock de seguridad (Stock_MP, columna L) + consumo mientras llega el pedido (columna K). "
                "Es lo que tiene que quedar cuando sale el pedido para que la entrega llegue antes de tocar la seguridad. "
                "Se compara con la posición (stock + lo pedido que viene en camino); la seguridad, con el stock físico. "
                "La revisión periódica del Word de MP (sección 9: cada 10, 20 o 60 días hábiles se pide hasta el máximo) "
                "sigue: el kanban avisa si entre dos revisiones se cruza el punto.")
    img("02_kanban_mp.png", "Figura 3. Kanban de MP con los conteos de ejemplo.", 15)
    img("02b_mp_detalle.png", "Figura 4. Tarjeta de una MP: de dónde sale cada número, su lugar en el almacén, el "
        "movimiento (conteo o retiro) y el pedido sugerido hasta el máximo.", 15)
    add("h2", "2.1 La planilla de conteo del almacén")
    p("El stock se carga con una planilla de Excel, una hoja por almacén, con los códigos en el orden de sus lugares "
      "(salida/Planilla_conteo_MP.xlsx; la app también la descarga, entera o de un almacén). El almacenero recorre los "
      "lugares, anota lo que hay en «Stock contado» con la fecha y quién contó, y la sube en «Cargar planilla». La app "
      "lee todas las hojas, muestra antes de aplicar qué códigos cambian y en qué estado quedan, y avisa los códigos que no "
      "existen. También acepta CSV o pegar dos columnas copiadas de Excel (código y stock).")
    tabla(["Columna", "Qué es", "De dónde sale"], [
        ["Lugar", "Lugar o lugares fijos del código", "Reparto de la sección 2.2"],
        ["Código · Material · UM · Se compra en", "Identificación y unidad en que se cuenta", "Stock_MP, columnas B, C, D y M"],
        ["Seguridad · Punto de pedido · Máximo", "Las tres marcas de la tarjeta", "Stock_MP L, L + K y S"],
        ["Stock contado", "Lo que anota el almacenero (celda amarilla)", "Conteo"],
        ["Estado", "BAJO SEGURIDAD, PEDIR u OK (fórmula)", "Contra seguridad y punto de pedido"],
    ], [28, 40, 32])
    b("**Cuándo se cuenta.** En cada revisión periódica del proveedor (Word de MP, sección 9) y siempre que un retiro deje "
      "una tarjeta cerca del punto de pedido. Entre conteos, los retiros a la línea y las recepciones (FAB-01, REC-01) "
      "mueven la tarjeta solos. La frecuencia por almacén queda como criterio a ajustar con el uso.")
    img("03b_planilla.png", "Figura 5. Carga de la planilla: vista previa con el stock anterior, lo contado y el estado en "
        "que queda cada código.", 15)
    add("h2", "2.2 Lugares del almacén")
    p("La pestaña «Almacén MP» dibuja cada almacén con sus lugares reales (MP-FLAMA2035 › Almacenes, columna E) y el código "
      "que vive en cada uno, porque «cada código tiene su lugar fijo y su etiqueta en el larguero» (Word de MP, sección 8). "
      "Los racks se dibujan por módulo, con 2 pallets por nivel, piso y 2 largueros (sección 8); el de flejes con 4 alturas "
      "(sección 6.2). Las pilas de chapa, el polvo, el cantilever, la estantería de identificación y la jaula de gases, "
      "como lugares en fila.")
    b("**Reparto (criterio).** Cada código ocupa los lugares enteros de su columna U de Stock_MP (cuánto ocupa su stock "
      "máximo); los restos de varios códigos comparten un lugar, de mayor a menor, en el primero donde entran. En los racks, "
      "los lugares de un mismo código quedan apilados en la misma columna: abajo el que se usa, arriba la reposición. En "
      "insumos de recargas no alcanza con lugares enteros (6,98 lugares de stock en 7) y los códigos se ubican de corrido.")
    fil = []
    for a_ in ALM:
        hs = LUG[a_["alm"]]
        fil.append([a_["alm"], a_["est"], len(hs), n(sum(m["u"] for m in MP if m["alm"] == a_["alm"]), 2),
                    sum(1 for m in MP if m["alm"] == a_["alm"]), sum(1 for h in hs if not h["cods"])])
    tabla(["Almacén", "Estantería", "Lugares", "Suma de U", "Códigos", "Libres"], fil, [28, 30, 10, 11, 10, 11], num=[2, 3, 4, 5])
    add("nota", "Lugares: Almacenes, filas 19 a 31 (13 de reventa en el PT, Balanceo › Pulmones sección 6). Suma de U: Stock_MP, columna U.")
    p("Cada lugar se dibuja en el formato en que se guarda (Almacenes, columnas C e I): paquetes de hojas sobre tacos, "
      "rollos acostados en el pallet, atados en los brazos del cantilever, big bags, pallets en rack, cajas en estantería "
      "liviana, cilindros en la jaula y matafuegos en pallet. El dibujo se llena con el stock contra el máximo y toma el "
      "color del estado del código; el mismo dibujo aparece en cada tarjeta del kanban.")
    img("03_almacen.png", "Figura 6. Almacén de MP: cada lugar con su código y el dibujo de su formato, lleno según el stock "
        "y coloreado por el estado. Arriba, accesos a cada almacén con la cantidad para pedir.", 15)
    add("h2", "2.3 Semáforo de cada almacén")
    p("La pestaña «Semáforo» muestra, para cada almacén, cuántos códigos hay en rojo, amarillo y verde, y cómo funciona la "
      "tarjeta kanban en su formato. Cada código se mira en bultos, que es lo que se ve en la estantería: bultos = unidades "
      "÷ contenido del bulto (Stock_MP, columna N).")
    tabla(["Luz", "Cuándo", "Qué se hace"], [
        ["Rojo", "Stock ≤ seguridad (L)", "Pedido urgente; se avisa a la línea y a compras."],
        ["Amarillo", "Stock ≤ punto de pedido (L + K), o pedido en camino", "La tarjeta del bulto pasa al tablero de pedidos y sale el pedido hasta el máximo."],
        ["Verde", "Stock sobre el punto de pedido", "Nada hasta la próxima revisión del proveedor."],
    ], [14, 38, 48])
    b("**En bultos enteros.** «Pedir cuando quedan N bultos» redondea el punto de pedido hacia arriba al bulto entero "
      "(criterio: se pide un poco antes, nunca después). Si el punto de pedido es menos de un bulto, la regla es «pedir al "
      "abrir el último bulto».")
    fil = []
    for a_ in ALM:
        regla = {"CH": "Marca en el poste de cada pila a la altura del punto de pedido; cuando la pila baja a la marca, la tarjeta va al tablero.",
                 "FL": "El pallet de rollos que deja el stock en el punto de pedido lleva la tarjeta; cuando la pinza lo baja, va al tablero.",
                 "CA": "Brazo del punto de pedido pintado de amarillo: cuando queda a la vista, se pide.",
                 "PQ": "El big bag (o la bolsa) del punto de pedido lleva la tarjeta colgada; cuando se empieza, va al tablero.",
                 "ID": "Doble cajón: el segundo cajón tiene la tarjeta; cuando se empieza, se pide.",
                 "GA": "Cilindros llenos con capuchón; cuando quedan los del punto de pedido, se pide; el vacío vuelve con la tarjeta.",
                 "RV": "El lugar del punto de pedido en la zona de reventa lleva la tarjeta."}.get(B.PREF[a_["alm"]],
                 "Abajo el bulto en uso, arriba la reposición; el bulto del punto de pedido lleva la tarjeta y va al tablero al bajarlo o abrirlo.")
        fil.append([a_["alm"], a_["est"], regla])
    tabla(["Almacén", "Formato", "Tarjeta kanban (criterio)"], fil, [26, 22, 52])
    add("nota", "Disposición de cada almacén: MP-FLAMA2035 › Almacenes, columna I, y Word de MP, sección 8 (abajo lo que se usa, "
                "arriba la reposición). La tarjeta física es criterio de este sistema; la app muestra el mismo semáforo con los conteos.")
    img("03c_semaforo.png", "Figura 7. Semáforo de los almacenes: luces por almacén, la regla de la tarjeta de su formato y cada "
        "código con su barra en bultos (rojo hasta la seguridad, amarillo hasta el punto de pedido, verde hasta el máximo).", 15)

    # ------------------------------------------------------------------ 3
    add("h1", "3. Kanban de producto terminado")
    p("El almacén de PT por zonas, con cada pallet en su lugar. El color del pallet es el mes de fabricación (4 colores "
      "que rotan, criterio) y el borde marca el más viejo de cada producto, que sale primero. Cada pallet entra con la "
      "ficha FAB-11 (o REV-01 los revendidos) y sale con su remito y el vehículo del día.")
    tabla(["Zona", "Lugares", "Qué guarda", "Fuente"], [
        ["Rack de PT", APT["lugares"], f"Nuevos en caja y cilindros; {APT['modulos']} módulos × 3 niveles × 2; los 10 kg en caja en el nivel 1",
         "PTPINTADO › Almacen_PT B15:B16"],
        ["Carros terminados en el piso", sum(CARROS.values()), " · ".join(f"{k}: {v}" for k, v in CARROS.items()), "Almacen_PT B22:B25"],
        ["Andén", APT["anden"], "Lo que sale en el día: un sider y un camión chico", "Almacen_PT B30"],
        ["Reventa", 13, "Matafuegos revendidos, por modelo", "Balanceo › Pulmones, sección 6"],
        ["Sustitutos", 22, "8 propios + 14 comprados", "Balanceo › Pulmones, sección 6"],
        ["Rama de pintura (carros)", 58, "Espera del pintor 29 + pintados 29", "PTPINTADO › Pintura B33:B34"],
    ], [20, 9, 46, 25], num=[1])
    img("05_kanban_pt.png", "Figura 8. Kanban de PT con pallets de la prueba: rack, piso, andén, reventa, sustitutos, "
        "pintura, días fijos de despacho y stock contra máximo.", 15)
    add("h2", "3.1 Despacho por días fijos y stock máximo")
    tabla(["Vehículo · qué lleva", "Días", "Salidas por semana"], [[d["veh"], d["dias"], n(d["salidas"], 1)] for d in DESP],
          [45, 35, 20], num=[2])
    tabla(["Producto", "Ventas del año", "Seguridad", "Stock máximo", "Por pallet", "Pallets"],
          [[x["prod"], n(x["ventas"]), x["ss"], n(x["max"]), x["porp"], x["pallets"]] for x in PT],
          [34, 15, 12, 15, 12, 12], num=[1, 2, 3, 4, 5])
    add("nota", "Stock máximo = stock por sobrestock + seguridad (5 días de venta) + pallet en armado (PTPINTADO › Stock_PT, filas 63 a 78).")
    add("h2", "3.2 Salida y despacho con el n° de serie")
    p("La pestaña «Despacho» muestra el número de punta a punta y registra la salida. El número nace en el cuerpo y se "
      "repite en cada etiqueta hasta el remito:")
    tabla(["Paso", "Dónde está el número", "Qué se controla", "Registro"], [
        ["1. Marcado", "Grabado en el cuerpo con la Pannier: «FLAMA S.A. N° serie año», arriba a la izquierda de la costura", "Rango de series del lote, colada de la chapa", "FAB-02"],
        ["2. Etiqueta de serie", "Etiqueta de n° de serie en el costado (planos FL_MAT, hoja 4), con el mismo número impreso; el QR es para el cliente", "Que la etiqueta tenga el mismo número que el marcado (primera y última del lote)", "FAB-11"],
        ["3. Etiqueta del pallet", "PAL-nnnn: producto, cantidad, lote, series desde–hasta, fecha de fabricación, lugar", "Liberación del lote, pesada, estampillas IRAM (una por unidad, Anexo R)", "FAB-11"],
        ["4. Remito", "Remito con el vehículo y las series que salen", "Sale primero el pallet más viejo; si sale parte, el resto queda con sus series", "Despacho (DES)"],
    ], [15, 35, 34, 16])
    b("**Despacho parcial.** Si las series del pallet son un rango, salen las primeras N y el pallet queda con el resto "
      "del rango (por ejemplo, salen 15184–15193 y quedan 15194–15471). El vehículo se propone según el producto "
      "(Despacho, filas 25 a 28: camión chico los nuevos en caja, sider los cilindros, Master los carros).")
    b("**Reclamo.** Con el número del cuerpo o de la etiqueta, la búsqueda trae el remito, el lote, cada ficha y la colada.")
    b("**Semáforo del PT (criterio).** Rojo: stock bajo la seguridad (Stock_PT, col. H), hay que producir; amarillo: a menos "
      "de un pallet de la seguridad, programar el próximo lote; verde: hay stock.")
    tabla(["Qué sale", "Número que se sigue", "Etiquetas que lleva"], [
        ["Matafuego o cilindro propio", "N° de serie + año (marcado y etiqueta de serie)", "Etiqueta del producto, etiqueta de serie, estampilla IRAM, oblea, faja y precinto"],
        ["Carro terminado", "N° de serie + año + presión de ensayo", "Ídem, en el carro"],
        ["Equipo de recarga", "Orden de servicio + n° grabado por su fabricante", "Marbete del año, oblea, etiqueta de servicio y precinto (IRAM 3517-2 9.4.13, 9.6, 9.4.14)"],
        ["Revendido", "N° de serie del fabricante", "Las de su fabricante; FLAMA no reetiqueta"],
    ], [24, 34, 42])
    img("05b_despacho.png", "Figura 9. Despacho: el número del cuerpo a la etiqueta de serie, al pallet y al remito; el "
        "formulario de despacho (con despacho parcial) y el semáforo del PT.", 15)

    # ------------------------------------------------------------------ 4
    add("h1", "4. Fichas de control de los procesos críticos")
    p("Una ficha por control crítico. Cada una dice en qué puestos del balanceo se usa y en qué sector del plano está, "
      "qué hay que registrar y con qué norma se acepta. Los campos con criterio se marcan solos; si alguno no cumple, la "
      "ficha queda «No conforme» y dice qué campo falló.")
    F = [
        ["FAB-01", "Recepción de MP", "man 1 · car 1", "Remito, lote o colada, certificado, espesor medido (chapa y fleje)", "Espesor ≥ nominal", "DOC-02 R1, L4, L5"],
        ["FAB-02", "Marcado del cuerpo (Pannier)", "man 6", "Series desde–hasta, año, colada de la chapa, ubicación 15/20 mm, cuño DPS, legibilidad", "Marcado completo y legible", "IRAM 3523 5.1 · 3550 5.1 · Res. 349/07 anexo IV"],
        ["FAB-03", "Soldadura longitudinal", "man 9 y 10 · car 5", "Soldador calificado, WPS, proceso, lotes de alambre y gas, A y V, visual", "TIG en 1 kg, MAG en el resto; ISO 5817 C", "ISO 9606-1 · ISO 15614-1 · DOC-02 R2"],
        ["FAB-04", "Soldadura de cúpula", "man 7 · car 6", "Igual que FAB-03; unión cuello-cúpula o cupla-cúpula", "ISO 5817 C", "ídem"],
        ["FAB-05", "Soldadura circunferencial", "man 13 · car 7", "Igual que FAB-03", "ISO 5817 C", "ídem"],
        ["FAB-06", "Control de espesor", "man 14 (2 %)", "Instrumento y calibración, serie medida, 4 lecturas", "Mínima ≥ espesor nominal del modelo", "DOC-02 R1"],
        ["FAB-07", "Prueba hidráulica", "man 15 · car 9", "Banco, días desde el contraste, presión, tiempo, series rechazadas; por lote expansión y rotura", "Contraste ≤ 15 días · P ≥ 3,5 / 4,0 MPa · ≥ 60 s · permanente ≤ 10 % · rotura ≥ 2 × PH", "IRAM 3517-2 9.7.5.2 · Res. 349/07 art. 20 · DOC-02 R3, L1, L2"],
        ["FAB-08", "Detección y corrección de defectos", "man 18 y 19", "Defecto, series, acción, si vuelve a PH", "Corrección con soldadura → repite la PH (criterio)", "ISO 5817 C · DOC-02 R2"],
        ["FAB-09", "Pintado", "man 20 · car 12 (pintor externo)", "Lote de polvo, Sa 2½, horas desde el granallado, HR, 5 lecturas de película, adherencia, MEK, color", "≤ 4 h · HR ≤ 85 % · 60 a 100 µm, ninguna < 48 · clase 0 ó 1", "DOC-01 · ISO 2808 · ISO 2409 · ASTM D5402"],
        ["FAB-10", "Ensayo de pérdidas", "man 24 · car 14-17", "Método, zona verde al presurizar y a las 24 h, sin pérdidas", "Sin pérdidas; 24 h en verde (criterio)", "IRAM 3517-2 9.4.10 · DOC-02 R7, R8"],
        ["FAB-11", "Producto terminado", "man 26 · car 16", "Producto, unidades, series, fecha de fabricación, lugar en el PT, pesada, etiqueta de serie igual al marcado, estampillas IRAM", "Pesada en tolerancia; identificación completa", "DOC-02 R9 · IRAM Anexo R"],
        ["REC-01", "MP de recargas", "almacén", "Agente, lote, certificado, rótulo", "Agente normalizado con certificado; sin mezclar ABC y BC", "IRAM 3517-2 9.9, tabla 6, 9.9.1.6"],
        ["REC-02", "Inspección interior", "rec 9 y 13", "OS, n° grabado, agente, videoscopio, humedad, corrosión, daño", "Seco; corrosión o abolladura → inutilizar", "IRAM 3517-2 9.8.2 · 9.7.1.2 · 9.7.1.3 · 9.12"],
        ["REC-03", "Ensayo de pérdidas (recarga)", "rec 20", "OS, n° grabado, método, zona verde, sin pérdidas", "Sin pérdidas; inmersión fuera del recinto", "IRAM 3517-2 9.4.10 · 9.4.8"],
        ["REC-04", "PT de recargas", "rec 21", "Precinto, marbete del año, oblea, etiqueta, jaula, remito", "Precinto, marbete y oblea colocados", "IRAM 3517-2 9.4.13 · 9.6 · 9.4.14"],
        ["REV-01", "Recepción de revendidos", "almacén de PT", "Modelo, fabricante, series del fabricante, año, sello IRAM, remito, lugar", "Etiqueta legible, manómetro en verde, precinto intacto", "IRAM 3517-2 9.4.13"],
    ]
    tabla(["Ficha", "Proceso", "Puestos", "Qué registra", "Criterio que marca", "Norma"], F, [7, 14, 11, 30, 21, 17])
    add("nota", "Puestos: man = manuales, car = carros, rec = recargas, con el número de Balanceo-FLAMA2035 › Carga. "
                "Las cláusulas se citan; no se transcriben.")
    img("04_ficha_ph.png", "Figura 10. Ficha FAB-07 (prueba hidráulica): el tiempo de 45 s queda en rojo porque la norma pide "
        "1 minuto, y la ficha se guarda como no conforme.", 15)
    img("08_fichas.png", "Figura 11. Las 16 fichas agrupadas por línea, con sus puestos y la cantidad de registros.", 15)

    # ------------------------------------------------------------------ 5
    add("h1", "5. Cómo se une todo: la búsqueda de trazabilidad")
    b("**Hacia atrás.** La colada del paquete de chapa se carga al recibirlo (FAB-01) y otra vez al marcar (FAB-02): así "
      "cada rango de series queda unido a su certificado.")
    b("**A lo largo de la línea.** Cada ficha lleva el lote y el rango de series del marcado. Buscando un número aparece "
      "cada ficha cuyo rango lo contiene, en orden: marcado, soldaduras, espesor, PH, defectos, pintado, pérdidas, PT.")
    b("**Hacia adelante.** El pallet guarda sus series y su lugar; al despacharlo queda el remito y el vehículo.")
    b("**Revendidos y recargas.** Se buscan por el n° del fabricante o por la orden de servicio.")
    img("07_traza.png", "Figura 12. Búsqueda del n° 20400: el lote que lo contiene (con acceso a su recorrido) y las "
        "fichas cuyo rango lo incluye, en orden.", 15)

    # ------------------------------------------------------------------ 6
    add("h1", "6. Layout de planta")
    p("Es el layout de la app de gestión interna: el mismo plano rev10, los mismos puestos y los mismos recorridos "
      "(catalogo_gestion.json y caminos.js copiados de esa app), con zoom con la ruedita, arrastre y filtros por línea. "
      "Cada ficha se carga en un puesto del plano; un lote está en el puesto de su última ficha. El punto de cada puesto "
      "muestra cuántos lotes u órdenes hay ahí (en rojo si alguno tiene una ficha no conforme); el almacén de MP, cuántos "
      "códigos hay para pedir; los puestos de PT, los lugares ocupados.")
    tabla(["Ficha", "Puesto en manuales", "Puesto en carros"], [
        ["FAB-01 · REC-01", "MP_TRAZ (trazabilidad de MP)", "ídem"], ["FAB-02", "MARC (marcado del cuerpo)", "ídem"],
        ["FAB-03", "M3", "C5"], ["FAB-04", "M6 (rama del cuello)", "C6"], ["FAB-05", "M7", "C7"], ["FAB-06", "M8", "—"],
        ["FAB-07", "MPH", "CPH"], ["FAB-08", "M11", "—"], ["FAB-09", "M18", "C12 (recepción de pintados)"],
        ["FAB-10", "M15", "C15"], ["FAB-11", "PTM", "C16"], ["REC-02 · REC-03 · REC-04", "R9 · R26 · R27 (recargas)", ""],
        ["REV-01", "REV (sector «Trazabilidad PT»)", ""]], [26, 40, 34])
    p("Al tocar un lote (desde el layout, el dashboard o la búsqueda) se dibuja su recorrido por los pasillos: verde lo que "
      "ya tiene ficha, punteado lo que falta y un punto rojo intermitente en su última ficha. El panel lista los pasos y "
      "marca «sin ficha» los puestos con ficha que el lote pasó sin cargarla.")
    img("06_layout.png", "Figura 13. Recorrido de un lote de ABC 10 kg: con ficha hasta la prueba hidráulica; falta del "
        "secado al despacho.", 15)
    img("06b_layout_almacen.png", "Figura 14. Almacén de MP en el layout: códigos para pedir por almacén.", 15)

    # ------------------------------------------------------------------ 7
    add("h1", "7. Quién hace qué")
    tabla(["Rol", "Qué hace en la app", "Cuándo"], [
        ["Almacén", "Cuenta con la planilla y la sube; registra retiros; emite el pedido de la tarjeta; carga FAB-01 / REC-01 al recibir", "En cada revisión del proveedor y en cada recepción"],
        ["Operario del puesto", "Carga la ficha de su puesto con el lote y el rango de series", "Al cerrar cada tanda o lote"],
        ["Calidad", "Revisa las no conformes; libera el lote con FAB-11", "Al terminar el lote"],
        ["Depósito de PT", "Ubica el pallet, mueve al andén y despacha con remito y series (pestaña Despacho)", "Los días fijos de cada vehículo"],
        ["Recargas", "REC-02 a REC-04 por orden de servicio", "En cada equipo"],
    ], [18, 57, 25])

    # ------------------------------------------------------------------ 8
    add("h1", "8. Lo que queda como criterio o por confirmar")
    b("15 mm y 20 mm del marcado (ubicación fija en la chapa): criterio para librar el cordón y el bordón.")
    b("Reparto de códigos en los lugares (sección 2.2) y frecuencia de conteo por almacén: criterio, a ajustar en planta.")
    b("Tarjeta kanban física de cada formato y redondeo al bulto entero (sección 2.3): criterio. Semáforo del PT (sección 3.2): criterio.")
    b("Colores del PT por mes (4 que rotan): criterio; se pueden alinear con la regla de colores del Word de carros.")
    b("Reventa y sustitutos no tienen sector propio en el plano rev10: la app los muestra como zonas del PT. La recepción "
      "de revendidos se ubica en el sector «Trazabilidad PT».")
    b("Los datos de ejemplo (dos semanas de lotes, recargas y conteos) son para ver la app funcionando; se borran con "
      "«Empezar en limpio». Los parámetros (seguridad, punto de pedido, máximos, lugares, puestos) son los reales.")
    b("FAB-10: la lectura a las 24 h es criterio FLAMA (DOC-02 R8). FAB-06: sin tolerancia de espesor publicada, se toma ≥ nominal.")
    b("La app de esta entrega guarda lo cargado en el navegador. Para usarla entre varios puestos hay que pasar los "
      "registros a la base de la app de gestión interna (la misma API y la misma base SQLite).")

    # ------------------------------------------------------------------ anexo
    add("salto")
    add("h1", "Anexo. Puntos de pedido de las 125 MP")
    p("MP-FLAMA2035 › Stock_MP, filas 6 a 130. Unidades en la unidad de cada código; bulto = unidad de compra; lugar = "
      "reparto de la sección 2.2.")
    fil = [[m["cod"], m["mat"], m["um"], n(m["ss"], 1), n(m["pp"], 1), n(m["max"], 1), m["bulto"], m["cada"], ", ".join(m["lugares"])] for m in MP]
    tabla(["Código", "Material", "UM", "Seguridad", "Punto de pedido", "Máximo", "Se compra", "Cada (d)", "Lugar"], fil,
          [9, 22, 5, 8, 9, 8, 15, 6, 18], num=[3, 4, 5, 7])

    add("h1", "Fuentes")
    for t in ["MP-FLAMA2035.xlsx y .docx (Stock_MP, Almacenes)", "PTPINTADO-FLAMA2035.xlsx y .docx (Stock_PT, Almacen_PT, Despacho, Pintura)",
              "Balanceo-FLAMA2035.xlsx y .docx (Carga, Pulmones)", "PULMONES-FLAMA2035.docx",
              "App de gestión interna FLAMA (estructura, estilo, plano rev10, puestos, recorridos y caminos por los pasillos)",
              "IRAM 3517-2:2020 (9.4.5, 9.4.8, 9.4.10, 9.4.13, 9.4.14, 9.6, 9.7, 9.8.2, 9.9, 9.12) · IRAM 3523 y 3550 (5.1) · Res. 349/07 PBA (art. 20, anexo IV)",
              "DOC-01 (pintura) y DOC-02 (ensayos de fabricación) del repositorio de planos",
              "ISO 9606-1, ISO 15614-1, ISO 5817, ISO 2808, ISO 2409, ASTM D5402 (se citan, no se transcriben)",
              "Planos FL_MAT (hoja 4, R7) y FL_REC (hoja 3, R3) con el marcado en el cuerpo"]:
        b(t)
    return bl


def main():
    bl = bloques()
    tmp = DOCX + ".json"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(bl, fh, ensure_ascii=False)
    subprocess.run(["node", JS, tmp, DOCX, "Trazabilidad interna FLAMA"], check=True, env=dict(os.environ, NODE_PATH=NODE_PATH))
    os.remove(tmp)
    print("ok", DOCX)


if __name__ == "__main__":
    main()
