"""Word «Sistema de trazabilidad FLAMA» (salida/Sistema_de_trazabilidad_FLAMA.docx): marcado por modelo, trazabilidad
intraplanta, extraplanta, retorno y seguros, devolución e inutilización. Reemplaza al Excel Trazabilidad_FLAMA."""
import json
import os
import subprocess
import tempfile

from PIL import Image

import figuras_trazabilidad as FT

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DOCX = os.path.join(RAIZ, "salida", "Sistema_de_trazabilidad_FLAMA.docx")
JS = os.path.join(RAIZ, "corte", "word_corte.js")
NODE_PATH = os.environ.get("NODE_PATH", "/tmp/claude-0/-home-user-TP-optimizacion/"
                                        "15292aaf-e550-5dee-a83e-77fd9177a6ef/scratchpad/jw/node/node_modules")

U_PANNIER = "https://www.directindustry.com/prod/pannier/product-24420-679289.html"
U_FAB = ("https://www.thefabricator.com/thefabricator/product/shopmanagement/"
         "dot-peen-system-makes-marks-that-are-readable-after-coating")
U_PROTO = "https://www.protocase.com/products/graphics-markings/dot-peening/"
U_KEY = ("https://www.keyence.com/products/marker/laser-marker/resources/laser-marking-resources/"
         "shot-blast-resistant-laser-marking.jsp")
U_EPCIS = "https://www.gs1.org/epcis"
U_EPCIS2 = "https://GS1.org/docs/epcis/epcis_2-0_launch.pdf"
U_ZX = "https://github.com/zxing-cpp/zxing-cpp/"
U_DMTX = "https://desk.ximea.com/kb/articles/pdf/libdmtx"
U_YOLO1 = "https://engrxiv.org/preprint/view/6685"
U_YOLO2 = "https://hal.archives-ouvertes.fr/hal-03837669"
U_CCYCN = "https://www.conceptosjuridicos.com/ar/articulos/codigo-civil-y-comercial-articulo-1298/"
U_COT = ("https://web.arba.gov.ar/sites/default/files/2024-02/"
         "COT%20C%C3%B3digo%20de%20Operaci%C3%B3n%20Traslado%20o%20Transporteggti.pdf")
U_SEG = "https://economis.com.ar/?p=438705"
U_RFID = "https://www.rfidtagworld.com/products/On-Metal-Tag/On-Metal-Tag_1548.html"
U_UMP = ("https://news.ump.edu.my/research/"
         "ts-dr-wan-isni-sofiah-develops-mobile-application-streamline-fire-extinguisher-maintenance")


def render(bl, salida, pie):
    tmpj = salida + ".json"
    with open(tmpj, "w", encoding="utf-8") as fh:
        json.dump(bl, fh, ensure_ascii=False)
    subprocess.run(["node", JS, tmpj, salida, pie], check=True, env=dict(os.environ, NODE_PATH=NODE_PATH))
    os.remove(tmpj)


def bloques(fig):
    b = []

    def add(t, x, **k):
        b.append(dict(t=t, x=x, **k))

    def tabla(cab, filas, cols, **k):
        b.append(dict(t="tabla", cab=cab, filas=filas, cols=cols, **k))

    def img(clave, pie, ancho=16.5):
        w, h = Image.open(fig[clave]).size
        b.append(dict(t="img", ruta=fig[clave], pie=pie, ancho=ancho, anchoPx=w, alto=h))

    add("titulo", "Sistema de trazabilidad FLAMA")
    add("sub", "Marcado del recipiente, seguimiento en planta, cadena de entrega, servicio, retorno e inutilización")
    add("p", "Un número por recipiente, grabado en el cuerpo al cortar la chapa, que no se pierde nunca. Todo lo demás "
             "(etiqueta, QR, sistema) cuelga de ese número. Las normas se citan por cláusula; donde el valor es un "
             "criterio de diseño y no un requisito, se dice **criterio**.")

    # ------------------------------------------------------------------ 0
    add("h1", "0. Qué cambié para que la lógica cierre")
    add("p", "La versión en Excel listaba etapas y datos, pero no decía qué pasa cuando algo falla, quién lee fuera de "
             "la planta, ni cómo cambia el equipo en cada recarga. Estos son los seis cambios de fondo:")
    tabla(["Antes (Excel)", "Ahora", "Por qué funciona mejor"], [
        ["Registro: cada puesto anota", "**Control:** cada puesto lee el grabado, el sistema le muestra la ficha "
         "del modelo y solo deja pasar si el estado anterior está aprobado (compuertas o «gates»)",
         "Un equipo sin PH o sin ensayo de pérdidas no puede llegar a la etiqueta: el error se frena en el puesto, "
         "no en la auditoría"],
        ["Una planilla por etapa", "**Eventos:** cada lectura es un renglón inmutable (qué, cuándo, dónde, por qué, "
         "cómo), con el modelo GS1 EPCIS 2.0", "La historia del equipo es la lista de sus eventos; nada se pisa"],
        ["Leer equipo por equipo", "**Agregación:** serie → caja → pallet (SSCC). Se lee el pallet y el sistema sabe "
         "qué series lleva", "Un traspaso de 200 equipos es una lectura, no 200"],
        ["El cliente «aparece» al final", "**Custodia:** cada traspaso es doble (sale de uno / entra al otro) con su "
         "documento", "Se sabe en todo momento quién tiene el equipo y dónde se cortó la cadena"],
        ["La ficha era fija", "**Ficha versionada:** el equipo nace con la ficha rev. 0 (como se fabricó) y cada "
         "servicio genera rev. n+1 (como quedó)", "La recarga re-especifica el equipo: agente, masa, presión, "
         "componentes, PH y vencimientos"],
        ["La baja era un dato más", "**Bloqueo:** un serie inutilizado queda bloqueado; si alguien lo lee, el "
         "sistema muestra «INUTILIZADO»", "Evita que un cuerpo dado de baja vuelva al mercado"],
    ], [3, 6, 5])
    add("p", "La regla de oro: **el grabado es la verdad y la etiqueta es un puntero.** Si la etiqueta se pierde "
             "(repintado, IRAM 3517-2 9.10) el número sigue en el cuerpo y se reimprime el QR.")

    # ------------------------------------------------------------------ 1
    add("h1", "1. Forma y lugar del marcado")
    add("h2", "1.1 Qué pide la norma y qué se suma")
    tabla(["Requisito", "Fuente", "Cómo se cumple"], [
        ["Grabar fabricante, n° de recipiente y año (2 dígitos), en el recipiente o en un accesorio fijo",
         "IRAM 3523 5.1 (manuales); IRAM 3550 5.1 (carros)", "Texto legible de 5 mm: «FLAMA S.A. · N° 26-000123 · 26»"],
        ["Carros: además la presión de ensayo", "IRAM 3550 5.1", "Segunda línea en la franja de carros (por eso 14 mm)"],
        ["Tolerancia de ±3 meses en el cambio de año", "IRAM 3523 5.1", "El año grabado es el del corte"],
        ["Cuño DPS de 1,5 × 0,7 cm al lado del n° de identificación, en la pollera u ojiva",
         "Res. 349/07 (PBA) anexo IV", "Cuño en la misma franja, a la derecha del número"],
        ["No dañar la identificación", "Res. 349/07 art. 25 e)", "Franja fuera de soldaduras; la faja va por encima"],
        ["Faja verde de reserva o amarilla de sustituto (≤ 40 mm) sin tapar los datos grabados",
         "IRAM 3517-2 5.3 y 9.4.5 b)", "La faja se pega por encima de la franja grabada, nunca sobre ella"],
        ["Sistema informatizado de seguimiento y trazabilidad del recargador; marcado con lápiz vibratorio",
         "IRAM 3517-2 4.x aa) y bb)", "El sistema de este documento; el grabado de servicio sigue en el tubo de "
         "pesca (Res. 349/07 art. 28/29)"],
        ["N° de serie en la etiqueta de servicio; registro de 6 años", "IRAM 3517-2 9.4.14 y 9.4.16",
         "La etiqueta lleva el QR del mismo serie; los eventos no se borran"],
    ], [6, 4, 6])
    add("p", "Lo que se **suma** sin reemplazar nada: un DataMatrix ECC 200 grabado al lado del texto, con el mismo "
             "número. La norma no fija tecnología (IRAM 3517-2 cap. 1 no restringe tecnologías nuevas); el código "
             "solo agrega lectura automática.")
    add("h2", "1.2 Contenido de la franja")
    img("contenido", "Franja de marcado a escala: DataMatrix 18 × 18 celdas de 0,6 mm (10,8 mm), texto IRAM de 5 mm y "
                     "cuño DPS 15 × 7 mm.")
    tabla(["Elemento", "Contenido", "Medida"], [
        ["DataMatrix ECC 200", "(01) GTIN del modelo + (21) serie «26000123» (formato GS1)", "18 × 18 celdas, 10,8 mm"],
        ["Texto legible", "FLAMA S.A. · N° 26-000123 · 26 (carros: + presión de ensayo)", "letra 5 mm"],
        ["Cuño DPS", "según Res. 349/07 anexo IV", "15 × 7 mm"],
        ["Franja total", "los tres en línea", "≈ 128 × 12 mm (carros 14 mm)"],
    ], [3, 7, 4])
    add("nota", "El texto es el respaldo humano: si un lector no decodifica el DataMatrix, el operario tipea los 8 "
                "dígitos. GTIN requiere ser miembro de GS1 Argentina; sin GTIN el DataMatrix lleva solo el serie.")
    add("h2", "1.3 Ubicación por modelo")
    img("ubicacion", "Vista de frente de cada familia: franja adelante y abajo, a 180° de la costura longitudinal y "
                     "debajo de la etiqueta.")
    tabla(["Modelo", "Zona", "Franja (mm desde el borde inferior del cuerpo)", "Profundidad (criterio)",
           "Máquina y puesto", "Cuándo"], [
        ["1 kg", "cuerpo bajo (no tiene pollera: el fondo va por fuera)", "14 – 27", "0,08 – 0,10 mm",
         "Pannier ADP120160D, salida de G2", "en plano, antes de cilindrar"],
        ["2,5 kg", "pollera (16 mm, sin presión)", "2 – 14", "0,20 – 0,25 mm", "Pannier, salida de G2", "ídem"],
        ["5 kg", "pollera (21,5 mm)", "4,5 – 16,5", "0,20 – 0,25 mm", "Pannier, salida de G2", "ídem"],
        ["10 kg", "pollera (16,5 mm)", "2 – 14", "0,20 – 0,25 mm", "Pannier, salida de G2", "ídem"],
        ["25 / 50 kg", "cuerpo bajo (casquetes insertos, sin pollera)", "35 – 49", "0,30 mm",
         "DTMAQ MPE 150130, puesto 2.1", "ídem"],
        ["70 / 100 kg", "cuerpo bajo", "35 – 49", "0,40 – 0,45 mm", "DTMAQ MPE 150130, puesto 2.1", "ídem"],
        ["Cilindros y sustitutos", "igual que su modelo", "ídem", "ídem", "ídem", "ídem"],
        ["Revendidos y recargas de otras marcas", "no se graban: se respeta el marcado de su fabricante",
         "—", "—", "etiqueta con QR en la recepción", "al recibir"],
    ], [2.2, 4, 2.6, 2.4, 3.4, 2.6])
    add("p", "Por qué ahí: la costura longitudinal va atrás, la etiqueta adelante; la franja baja queda a la vista, "
             "lejos de la soldadura circunferencial y del encastre del fondo (alturas de los planos, **criterio**). "
             "Para 1 kg y carros, que no tienen pollera, falta confirmar con la DPS si el cuerpo bajo vale como "
             "«pollera u ojiva»; si no, el cuño DPS y el número se repiten en la ojiva.")
    add("h2", "1.4 Profundidad")
    img("profundidad", "Corte de la pared con la huella del punzón y la pintura de 70 µm (esquema).")
    tabla(["Caso", "Regla (criterio)", "Resultado"], [
        ["1 kg: pared a presión, e = 0,9 mm", "≤ 10 % del espesor, y la PH al 100 % (se hace después del grabado) "
         "valida la pared ya marcada", "0,08 – 0,10 mm"],
        ["2,5 – 10 kg: pollera sin presión", "≈ 3 × el espesor de pintura (70 µm) para seguir legible tras varios "
         "repintados", "0,20 – 0,25 mm"],
        ["Carros 25 / 50 kg, e = 3,2", "≤ 10 % de e (0,32) y ≥ 3 × pintura (0,21)", "0,30 mm"],
        ["Carros 70 / 100 kg, e = 4,75", "≤ 10 % de e (0,475) y ≥ 3 × pintura", "0,40 – 0,45 mm"],
    ], [5, 7, 3])
    add("p", "La Pannier ADP120160D graba texto, logos y códigos 2D en una ventana de 120 × 160 mm y su fabricante "
             "la ofrece para marcas profundas legibles después de granallado y pintura "
             f"([ficha]({U_PANNIER})); lo mismo reportan [The Fabricator]({U_FAB}) y [Protocase]({U_PROTO}) para "
             f"micropercusión bajo recubrimiento. El láser también sirve ([Keyence]({U_KEY})) pero sería una máquina "
             "nueva.")
    add("h2", "1.5 Dónde se graba: la planchuela plana")
    img("planchuela", "Planchuela del 5 kg a la salida de la guillotina 2: la mesa de la Pannier tiene topes en el "
                      "borde inferior y en un borde de costura.", 13)
    add("p", "La Pannier se muda del puesto 6 «Numerado de cúpula» a la salida de G2. La franja cae siempre a "
             "desarrollo / 2 del borde de costura, o sea adelante una vez cilindrado. Grabar en plano es más "
             "rápido y repetible que en un cuerpo curvo, y el serie nace atado a la hoja y al lote de chapa. Al "
             "cilindrar, el DataMatrix de 10,8 mm queda sobre Ø 76 a 390 mm: la curvatura es chica frente al código.")
    add("h2", "1.6 Ensayo de validación (antes de cambiar planos)")
    add("p", "Una tanda por espesor (0,9 · 1,25 · 1,6 · 2,0 · 3,2 · 4,75): **grabar → cilindrar → soldar → PH → "
             "granallar → pintar → leer**, y una segunda pintura encima para simular un repintado. Se aprueba si el "
             "texto se lee a simple vista, el DataMatrix decodifica con el lector elegido y la PH no muestra "
             "deformación en la franja. Con eso se fijan las profundidades de la tabla, que hoy son criterio.")

    # ------------------------------------------------------------------ 2
    add("h1", "2. Trazabilidad intraplanta: del grabado al embalado (y a la inutilización)")
    img("intraplanta", "Estados del recipiente. Cada flecha es una lectura del grabado; las compuertas (GATE) "
                       "bloquean el paso si la ficha no se cumple.")
    add("h2", "2.1 La estación barata de cada puesto")
    add("p", "Cada puesto tiene lo mismo, y es lo que pediste: un lugar donde se completan las especificaciones y la "
             "situación del equipo, y que va armando su historial de producción.")
    tabla(["Componente", "Qué es", "Por qué"], [
        ["Celular o tablet Android en un soporte", "La pantalla del puesto", "Barato y reemplazable"],
        ["Lector", "La cámara del celular (librería [zxing-cpp]({}) o [libdmtx]({})); lector DPM de mano solo "
                   "donde la cámara no lea (después de pintar, a definir en el ensayo 1.6)".format(U_ZX, U_DMTX),
         "El código grabado tiene poco contraste; el lector DPM está hecho para eso"],
        ["App", "AppSheet sobre Google Sheets (FLAMA ya trabaja en Sheets con IMPORTRANGE); funciona sin conexión "
                "y sincroniza", "Sin programar ni servidores; se arma por formularios"],
        ["Ficha del modelo", "Tabla FICHAS: por modelo y puesto, parámetro, mínimo, máximo, unidad y norma",
         "El operario ve lo que tiene que cumplir el equipo que tiene en la mano"],
        ["Respaldo", "Tipear el número grabado", "Nunca se frena la línea por un lector"],
    ], [3.5, 8, 5])
    add("p", "**Cómo trabaja el operario:** lee el grabado → la app muestra modelo, estado y la ficha del puesto → "
             "completa los valores (o los toma la balanza o el banco de PH) → la app compara con mínimo y máximo → "
             "si cumple, el equipo pasa al estado siguiente; si no, pide motivo y foto y lo manda a RECHAZO "
             "(retrabajo o ANULADO). Lo mismo arma la **ficha del equipo**: por cada parámetro, especificado, real y "
             "«cumple».")
    add("h2", "2.2 Manuales: qué se registra en cada puesto")
    tabla(["Puesto", "Lectura y registro", "Ficha (qué se controla)", "Estado"], [
        ["1 Recepción de chapa", "lote, colada, certificado del proveedor", "espesor y calidad del certificado",
         "lote disponible"],
        ["2 Corte G2 + Pannier", "**nace el serie**: modelo, hoja, lote de chapa, fecha; la app verifica que el "
         "DataMatrix recién grabado se lea", "medidas de la planchuela, lectura OK", "CORTADO y GRABADO"],
        ["4 a 7 Cúpula y cuello", "por lote (carro de cúpulas = lote; ya no se numera la cúpula)",
         "embutido y soldadura de cuello", "lote de cúpulas"],
        ["8 Cilindrado · 9 Soldadura longitudinal", "soldador o máquina, lote de alambre y gas",
         "modelo = matriz seteada", "CONFORMADO"],
        ["10 Encastre · 11 Bordoneado · 12 Soldadura circunferencial", "**agregación:** serie ← lote de cúpula ← "
         "lote de fondo", "parámetros de soldadura", "CONFORMADO"],
        ["13 Control de espesor", "espesores medidos", "≥ mínimo de la ficha", "**GATE**"],
        ["14 Prueba hidráulica", "presión, tiempo, resultado (lo toma el banco)", "presión de ensayo de la norma; "
         "falla → ANULADO", "**GATE** → PROBADO"],
        ["15 Secado · 16 Granallado", "tiempos", "—", "PROBADO"],
        ["17 Detección de defectos · 18 Corrección", "foto (visión, ver 2.4) y decisión del operario",
         "sin poros ni golpes", "PROBADO"],
        ["19 Pintura (cuelgue)", "lote de pintura, temperatura del horno", "espesor de película", "TERMINADO"],
        ["19 Descarga", "cilindros vacíos → embalaje directo", "—", "TERMINADO"],
        ["20 a 22 Carga, ensamblaje, presurización", "lote de polvo, masa (balanza), válvula y manómetro, presión",
         "masa y presión de la ficha", "CARGADO"],
        ["23 Pérdidas", "resultado del ensayo", "sin pérdida", "**GATE** → APROBADO"],
        ["24 Etiquetado", "se imprime la etiqueta con el QR **leyendo el grabado**; sello IRAM, oblea, precinto",
         "QR = grabado", "**GATE** → IDENTIFICADO"],
        ["25 Embalaje", "serie → caja → pallet (SSCC)", "cantidad del pallet", "EMBALADO"],
    ], [4, 6, 4.5, 3])
    add("h2", "2.3 Carros: diferencias")
    tabla(["Puesto", "Lectura y registro", "Estado"], [
        ["2 Corte + 2.1 Marcado del cuerpo", "nace el serie (DTMAQ MPE 150130, confirmar DataMatrix con el "
                                           "proveedor)", "CORTADO y GRABADO"],
        ["3 a 8 Cilindrado, punteo, soldaduras, cupla, accesorios", "soldador, lotes de casquetes, ruedas y "
                                                                   "accesorios", "CONFORMADO"],
        ["9 Prueba hidráulica · 10 Secado", "presión, tiempo, resultado", "**GATE** → PROBADO"],
        ["11 Pulmón a pintura tercerizada", "doble lectura **sale**: lista del envío al pintor", "EN PINTOR"],
        ["12 Recepción de pintados", "doble lectura **entra**: la app compara contra la lista enviada y marca "
                                     "faltantes; rechazados del pintor con foto", "TERMINADO"],
        ["13 Carga · 14 Pérdidas", "lote de agente, masa, presión; ensayo de pérdidas", "**GATE** → APROBADO"],
        ["15 Etiquetado e inspección final", "QR = grabado; foto de control final", "**GATE** → IDENTIFICADO"],
        ["16 Depósito PT · 17 Ensayos de lote", "retenido hasta que el lote aprueba; la muestra ensayada queda "
                                               "ANULADA", "EMBALADO / liberado"],
    ], [5, 9, 3.5])
    add("p", "La pintura tercerizada es el único punto donde el carro sale de la planta antes de terminarse: por eso "
             "ahí la doble lectura es obligatoria.")
    add("h2", "2.4 Visión con YOLO: dónde suma")
    tabla(["Uso", "Cómo", "Qué aporta"], [
        ["Ubicar y leer el grabado", "YOLO detecta la franja en la foto, recorta y la pasa a zxing-cpp / libdmtx; "
                                     "si falla, OCR del texto", "Lectura con cualquier cámara, también de otras marcas en "
                                                               "recargas"],
        ["Defectos después del granallado (puesto 17)", "Detector entrenado con fotos propias de poros, golpes y "
         f"soldaduras ([YOLO en soldadura]({U_YOLO1}); [YOLOv3]({U_YOLO2}))",
         "Marca el defecto; decide el operario"],
        ["Control final (24 manuales, 15 carros)", "Verifica etiqueta, precinto, manómetro en verde, faja, tobera y "
                                                   "pasador; guarda la foto", "Evidencia fechada por equipo"],
        ["Conteo de pallet", "Cuenta equipos en la foto del pallet y compara con la agregación SSCC",
         "Faltantes antes de cargar el camión"],
        ["Recepción en recargas", "Clasifica corrosión y golpes como apoyo a IRAM 3517-2 9.7.1.3",
         "Prioriza qué revisar; decide el recargador"],
    ], [4, 7.5, 5])
    add("p", "YOLO corre en una PC chica con cámara fija; el entrenamiento necesita un lote de fotos propias "
             "etiquetadas, por eso va en la fase 3.")
    add("h2", "2.5 Datos y prueba de integridad")
    tabla(["Tabla", "Qué guarda"], [
        ["SERIES", "serie, modelo (GTIN), estado actual, rev. de ficha, lote de chapa, quién lo tiene"],
        ["EVENTOS", "id, serie o SSCC, tipo, puesto, fecha y hora, operario, valores, resultado, foto, hash anterior, "
                    "hash"],
        ["FICHAS", "modelo, revisión, puesto, parámetro, mínimo, máximo, unidad, norma"],
        ["LOTES", "chapa, polvo, válvulas, manómetros, pintura: proveedor y certificado"],
        ["AGREGACIONES", "padre (caja, pallet SSCC, lote de cúpula) e hijo (serie)"],
    ], [3.5, 13])
    add("p", "Cada evento guarda el hash del anterior (cadena de hashes, una fórmula): si alguien edita un renglón "
             "viejo, la cadena se rompe y se nota. Da la misma prueba que se le pide a una «blockchain» sin "
             "necesitarla. Eventos con la estructura de [GS1 EPCIS 2.0]({}) ([lanzamiento]({})): qué, cuándo, "
             "dónde, por qué y cómo.".format(U_EPCIS, U_EPCIS2))

    # ------------------------------------------------------------------ 3
    add("h1", "3. Trazabilidad extraplanta: de la carta de porte a la llave en mano")
    img("extraplanta", "Cadena de custodia: cada traspaso es una doble lectura con su documento.")
    tabla(["Traspaso", "Documento", "Lectura", "Qué queda"], [
        ["FLAMA → transportista", "remito y factura; carta de porte suscripta por el cargador (CCyCN [art. 1298]({}))"
         ", segundo ejemplar (art. 1299) y guía del transportista (art. 1300); COT de ARBA si el traslado supera los "
         "umbrales vigentes ([ARBA]({}))".format(U_CCYCN, U_COT), "pallet (SSCC) sale ✓ en despacho; el chofer "
         "confirma entra ✓ con el celular leyendo el QR del remito", "fecha, camión, chofer, series"],
        ["Transportista → distribuidor", "remito con firma de recepción", "pallet entra ✓; faltantes y daños con foto",
         "custodia: distribuidor"],
        ["Distribuidor → instalador o cliente", "remito o factura del distribuidor", "al abrir el pallet se lee "
         "cada serie que vende (desagregación)", "a quién se vendió cada serie"],
        ["Instalador → cliente (llave en mano)", "acta de entrega firmada en el celular", "serie + ubicación "
         "(dirección, sector, foto en el soporte)", "estado EN SERVICIO, dueño = cliente"],
    ], [3.5, 6.5, 4.5, 3])
    add("p", "**El punto débil real** es que el distribuidor no tiene obligación de leer nada. Propuesta "
             "(**criterio**): la garantía del equipo se activa cuando se registra la venta o la instalación. Así "
             "el que vende tiene un motivo para leer. Instaladores propios de FLAMA leen siempre.")
    add("p", "El QR de la etiqueta (GS1 Digital Link) abre la ficha con dos solapas, **técnica** y **comercial**, "
             "las dos con la historia; lotes, operarios y parámetros de máquina quedan solo para FLAMA.")

    # ------------------------------------------------------------------ 4
    add("h1", "4. Retorno del matafuego, re-especificación por recarga y seguros")
    img("retorno", "Ciclo en servicio: retiro con sustituto, recepción, servicio con nueva revisión de ficha, "
                   "devolución o inutilización.")
    add("h2", "4.1 Retiro y sustituto")
    add("p", "Al retirar el equipo se deja un sustituto (tarjeta «sustituto habilitado», Res. 349/07 art. 32; faja "
             "amarilla ≤ 40 mm en el borde inferior con sus leyendas, IRAM 3517-2 9.4.5 b); la faja es vinilo "
             "autoadhesivo amarillo, la norma no fija material). La app **parea** sustituto ↔ equipo retirado: se "
             "sabe dónde está cada sustituto y cuánto lleva afuera.")
    add("h2", "4.2 Recepción y servicio")
    add("p", "En recargas se lee el grabado (o el QR), se saca foto y la visión ayuda a clasificar el estado. La app "
             "trae la última ficha y aplica las reglas de la norma como bloqueos:")
    tabla(["Regla", "Fuente", "Qué hace la app"], [
        ["No convertir el tipo de agente", "IRAM 3517-2 9.4.6", "No deja cargar otro agente que el de la ficha"],
        ["PH cada 5 años (polvo) y vida útil de 20 años", "IRAM 3517-2 anexo E", "Exige PH si vence; si pasó la vida "
                                                                                 "útil manda a inutilización"],
        ["Inutilizar por corrosión, daños, etc.", "IRAM 3517-2 9.7.1.3", "Rechazo en recepción → INUTILIZACIÓN"],
        ["Precinto trazable", "IRAM 3517-2 9.4.13", "Registra el n° de precinto nuevo"],
        ["Repintado", "IRAM 3517-2 9.10", "Registra el repintado y reimprime la etiqueta con el QR"],
        ["Etiqueta con n° de serie; registro 6 años", "IRAM 3517-2 9.4.14 y 9.4.16", "Etiqueta nueva; el evento "
                                                                                    "no se borra"],
        ["Fecha y PH grabadas en el tubo de pesca con lápiz vibratorio", "Res. 349/07 art. 28/29",
         "Se registra lo grabado"],
    ], [5, 4, 7])
    add("h2", "4.3 Re-especificación: ficha rev. n+1")
    add("p", "Cada servicio cierra con una revisión nueva de la ficha del equipo, que es «cómo quedó»:")
    tabla(["Campo", "Rev. 0 (fábrica)", "Rev. n+1 (servicio)"], [
        ["Agente", "lote de polvo de fábrica, masa", "lote recargado, masa nueva (o recuperado + reposición)"],
        ["Presión", "presión de fábrica", "presión de servicio"],
        ["Componentes", "válvula, manómetro, manguera de fábrica", "los que se cambiaron, con su lote"],
        ["PH", "PH de fábrica", "fecha, presión y resultado si tocó"],
        ["Terminación", "pintura de fábrica", "repintado, etiqueta nueva"],
        ["Vencimientos", "recarga y PH", "recalculados; vida útil sigue contando desde la fabricación"],
        ["Responsable", "FLAMA", "recargador, tarjeta DPS / AGC, precinto, marbete"],
    ], [3.5, 6, 7])
    add("h2", "4.4 Seguros")
    add("p", "El sistema no cambia lo que cubre una póliza (eso lo dice cada póliza; ver por ejemplo [qué cubre un "
             f"seguro de incendio]({U_SEG})), pero da la prueba: con el mismo QR se muestra, a la fecha del "
             "siniestro, el último servicio, el marbete vigente, la ubicación y las fotos, con la cadena de hashes "
             "como garantía de que no se editó. No encontré una fuente que diga que la aseguradora condiciona el pago "
             "al mantenimiento: es un uso posible, no un requisito.")
    add("p", "Para FLAMA el valor fuerte es el **recall**: si un lote de chapa, polvo o válvulas sale mal, se consulta "
             "el lote → series → quién los tiene (custodia) → aviso directo. Sin el sistema eso no se puede hacer.")

    # ------------------------------------------------------------------ 5
    add("h1", "5. Retorno al cliente e inutilización")
    tabla(["Caso", "Qué se hace", "Lectura y estado"], [
        ["Apto", "Se devuelve, se retira el sustituto", "doble lectura: equipo entra ✓ al cliente, sustituto sale ✓; "
                                                         "EN SERVICIO con ficha rev. n+1"],
        ["No apto", "Inutilización (IRAM 3517-2 9.12) con acta del anexo G; se ofrece reemplazo",
         "INUTILIZADO → BAJA: el serie queda **bloqueado** para siempre"],
        ["Fin de vida útil", "Igual que no apto, avisado antes por el sistema", "ídem"],
        ["Equipo de otra marca", "Se inutiliza igual; se registra su número grabado", "ídem"],
    ], [3, 7, 7])
    add("p", "Si alguien lee un serie bloqueado, la app y el QR público muestran «INUTILIZADO — fecha — acta». La "
             "numeración queda auditable: cada serie está fabricado, anulado en planta o dado de baja.")

    # ------------------------------------------------------------------ 6
    add("h1", "6. Herramientas y alternativas evaluadas")
    tabla(["Herramienta", "Uso", "Decisión"], [
        ["Micropercusión profunda (Pannier / DTMAQ)", "grabado + DataMatrix", "**Base**: ya están en planta"],
        ["DataMatrix ECC 200 + QR en la etiqueta (GS1 Digital Link)", "lectura automática y acceso del cliente",
         "Sí"],
        ["GS1 EPCIS 2.0 + SSCC", "eventos y agregación", "Sí (estructura, no hace falta software GS1)"],
        ["Cadena de hashes", "integridad", "Sí"],
        ["YOLO + zxing-cpp / libdmtx + OCR", "visión y lectura", "Fase 3"],
        ["AppSheet sobre Sheets", "estación de puesto", "Sí (fase 1)"],
        [f"Etiqueta RFID / NFC para metal ([ejemplo]({U_RFID}))", "lectura sin línea de vista",
         "No por ahora: se va con el repintado igual que la etiqueta"],
        ["Tinta invisible UV", "marca oculta", "No: el granallado y el repintado la tapan o la quitan; la marca "
                                              "profunda sobrevive"],
        [f"App de mantenimiento con QR ([caso UMP]({U_UMP}))", "referencia de uso en mantenimiento", "Referencia"],
    ], [6, 5, 6])

    # ------------------------------------------------------------------ 7
    add("h1", "7. Fases y pendientes")
    tabla(["Fase", "Qué entra"], [
        ["0", "Ensayo de marcado (1.6) y confirmación con la DPS de la ubicación en 1 kg y carros"],
        ["1", "Serie, estados, 3 compuertas, fichas por modelo, etiqueta con QR (AppSheet + Sheets)"],
        ["2", "Agregación SSCC, doble lectura en despacho y pintura tercerizada, portal QR con dos solapas"],
        ["3", "Visión YOLO, recargas con ficha rev. n+1, pareo de sustitutos, recall"],
    ], [2, 15])
    add("p", "**Pendientes antes de tocar planos:** profundidades (hoy criterio) con el ensayo; DataMatrix de la "
             "DTMAQ MPE 150130; cuño DPS en 1 kg y carros; GTIN (alta en GS1 Argentina) o serie solo; umbrales "
             "vigentes del COT de ARBA. Después: mover el marcado de la cúpula a la franja del cuerpo en los planos, "
             "la faja por encima, y la Pannier a la salida de G2.")

    # ------------------------------------------------------------------ fuentes
    add("h1", "Fuentes")
    for t, u in (("Pannier ADP120160D Deep Marker", U_PANNIER), ("The Fabricator: micropercusión legible tras "
                 "recubrimiento", U_FAB), ("Protocase: dot peening", U_PROTO),
                 ("Keyence: marcado láser resistente al granallado", U_KEY), ("GS1 EPCIS", U_EPCIS),
                 ("GS1 EPCIS 2.0", U_EPCIS2), ("zxing-cpp", U_ZX), ("libdmtx", U_DMTX),
                 ("Detección de defectos de soldadura con YOLO", U_YOLO1), ("Defectos de soldadura con YOLOv3",
                 U_YOLO2), ("CCyCN art. 1298 a 1300", U_CCYCN), ("ARBA: COT", U_COT),
                 ("Seguro de incendio", U_SEG), ("Etiqueta RFID para metal", U_RFID), ("UMP: app de mantenimiento "
                 "de matafuegos", U_UMP)):
        add("b", f"[{t}]({u})")
    add("b", "IRAM 3523:1983 5.1 · IRAM 3550 5.1 · IRAM 3517-2:2020 (cláusulas citadas) · Res. 349/07 PBA "
             "(art. 25, 28, 29, 32 y anexo IV). Se citan, no se transcriben.")
    return b


def main():
    fig = FT.todas(tempfile.mkdtemp(prefix="figs_traz_"))
    render(bloques(fig), DOCX, "Sistema de trazabilidad FLAMA")
    print("ok", DOCX)


if __name__ == "__main__":
    main()
