"""Word «Resumen FLAMA 2035»: síntesis de Balanceo, Pulmones, PT, MP y el guion de exposición (Word de cada tema)."""
import json
import os
import subprocess

RAIZ = "/home/user/planos_industrial_flama"
DOCX = os.path.join(RAIZ, "salida", "Resumen_FLAMA2035.docx")
JS = os.path.join(RAIZ, "corte", "word_corte.js")
NODE_PATH = os.environ.get("NODE_PATH", "/tmp/claude-0/-home-user-TP-optimizacion/15292aaf-e550-5dee-a83e-77fd9177a6ef/scratchpad/jw/node/node_modules")

bl = []
add = lambda t, x=None, **k: bl.append(dict(t=t, x=x, **k))
p = lambda x: add("p", x)
b = lambda x: add("b", x)


def tabla(cab, filas, cols, num=(), negrita=()):
    bl.append(dict(t="tabla", cab=cab, filas=filas, cols=cols, num=list(num), negrita=list(negrita)))


add("titulo", "FLAMA S.A. · Resumen 2035")
add("sub", "Materia prima, balanceo, pulmones, producto terminado y despacho, en pocas páginas")
add("sub", "Fuentes: Balanceo-FLAMA2035, PULMONES-FLAMA2035, PTPINTADO-FLAMA2035, MP-FLAMA2035 y Guion de exposición")

add("h1", "La idea en un minuto")
p("Se sigue el material de punta a punta: entra, se fabrica, espera entre puestos y sale. Cinco decisiones ordenan todo:")
b("**Se compra en la unidad en que se usa.** El paquete de chapa es una tanda de corte y el rollo de fleje una tanda de la prensa.")
b("**Ningún puesto pasa el 90 %.** El cuello de manuales es la soldadura longitudinal de 2,5 a 10 kg, al 81 %.")
b("**Tandas y ola.** Las máquinas con cambio caro trabajan por tandas; el resto pasa en ola, al ritmo de la soldadura circunferencial.")
b("**Pulmones solo donde se junta material.** Se simuló el plan y va estante solo donde el puesto que consume es más lento.")
b("**El producto terminado sale con días fijos.** Los carros van al pintor cada 2 días y no se retienen al final.")
add("nota", "En total se reservan 793 m², contra 1.004 m² del planteo anterior.")
tabla(["Tema", "Número", "Dónde sale"], [
    ["Manuales 2035", "284.463 recipientes/año · 1.280 por día en enero", "Balanceo, Carga"],
    ["Carros / recargas (su mes pico)", "14 carros/día en marzo · 589 equipos/día en diciembre", "Balanceo, Carga"],
    ["Cuello de manuales", "Sold. longitudinal 2,5–10 kg: 81,2 % (tope 90 %)", "Balanceo, Rueda"],
    ["Calendario", "Se repite cada 16 días hábiles", "Balanceo, Rueda"],
    ["Pulmones de manuales", "20.801 piezas · 44 módulos · 32 carros · 108,3 m²", "Pulmones"],
    ["Pulmones de carros", "178 recipientes · 47,3 m²", "Pulmones"],
    ["Almacén de MP", "119 lugares · 221,8 m² · 596 pedidos/año", "MP"],
    ["Almacén de PT", "85 pallets · 43 carros en el piso · 272,6 m²", "PT y Balanceo"],
    ["Total a reservar", "793,3 m² (antes 1.004,0)", "Balanceo, Pulmones"],
], [28, 50, 22])

add("h1", "1. Cuánto se fabrica (Balanceo)")
b("**Se balancea la producción, no la venta.** La planta fabrica parejo: de agosto a noviembre arma el sobrestock y en "
  "diciembre y enero lo consume. Ningún mes pasa el 9 % del año.")
b("**Mes de cálculo: enero de 2035**, con 1.280 manuales por día. Se usa la mezcla real (71 % de 1 kg, 22 % de 5 kg, "
  "5 % de 2,5 kg y 1 % de 10 kg): con un recipiente promedio el cuello parece holgado, porque el 10 kg es el 1 % de las "
  "unidades pero tarda 115 s en la soldadura longitudinal.")
tabla(["Línea", "Por día", "Mes pico", "Cuello de botella", "Carga"], [
    ["Manuales", "1.280", "Enero", "Sold. longitudinal 2,5–10 kg", "81,2 %"],
    ["Carros", "14", "Marzo", "Soldadura de accesorios", "52,3 %"],
    ["Recargas", "589", "Diciembre", "Ensayo de pérdidas", "87,3 %"],
], [16, 12, 14, 38, 20], num=[1, 4])
add("nota", "Carga = piezas del día × tiempo de cada modelo. Capacidad = máquinas × turnos × 450 min. Tope del 90 % para fallas y variaciones.")
add("h2", "1.1 Tandas: las máquinas con cambio caro")
b("**Regla.** Cada tanda dura al menos 3 veces lo que lleva el cambio (el cambio pesa como mucho el 25 %), y las "
  "frecuencias son 1, 2, 4, 8 o 16 días, así el calendario se repite cada 16 días hábiles.")
b("**Guillotinas.** 1 kg y 5 kg todos los días, 2,5 kg cada 8, 10 kg cada 16 y carros cada 4. Cada una sola va holgada "
  "(65 % y 38 %), pero juntas suman 464 min/día: hacen falta 2 operarios de corte.")
b("**Embutidora.** 8 matrices con 90 min de cambio: cambiar todas cada día serían 720 min, el 80 % de la prensa. Por eso "
  "cada matriz trabaja cada 4 a 16 días y la prensa queda al 47,9 %. Cúpula y fondo de un modelo van en días seguidos.")
tabla(["Formato", "Ola (cada días)", "Guillotina (cada días)", "Hojas por tanda", "Embutidora (cada días)", "Piezas por tanda"], [
    ["1 kg", "1", "1", "21", "4", "3.647"], ["2,5 kg", "1", "8", "19", "16", "1.017"],
    ["5 kg", "1", "1", "24", "8", "2.299"], ["10 kg", "2", "16", "19", "16", "278"],
], [14, 15, 18, 15, 19, 19], num=[1, 2, 3, 4, 5])
add("h2", "1.2 La ola y el marcapasos")
b("**Ola.** Del cilindrado al embalaje, cada formato pasa el mismo día por todos los puestos: pulmones chicos, el "
  "primero que entra sale primero (un defecto se ve rápido) y un solo plan para toda la línea.")
b("**Marcapasos: la soldadura circunferencial (73 %)**, porque ahí se juntan las dos ramas, cuerpo y cúpula.")
b("**Marcado del número de serie** en el desarrollo plano, entre la guillotina 2 y el cilindrado. Hasta 2033 un solo "
  "puesto (en 2033 llega al 85 % y pasa a ser el cuello); desde 2034, dos.")
add("h2", "1.3 Carros y recargas")
b("**Carros.** 52 % en marzo, en la soldadura de accesorios: un soldador atiende armado, circunferencial y accesorios.")
b("**Recargas.** 87 % en diciembre en el ensayo de pérdidas: si crece la demanda, segundo turno ahí. En planta hay "
  "779 equipos en 45 jaulas (108 m²), por la ley de Little: equipos por hora × (tiempo de operación + 0,5 h de espera).")

add("h1", "2. Materia prima (MP)")
add("h2", "2.1 Se compra en la unidad en que se usa")
b("**Chapa.** El paquete es la tanda de corte: 21 hojas del 1 kg (todos los días), 19 del 2,5 kg (cada 8 días), 24 del "
  "5 kg (todos los días), 19 del 10 kg (cada 16 días); para carros, 7 hojas de 3,2 mm y 3 de 4,75 mm (cada 4 días). Entra "
  "entero a la mesa elevadora de la guillotina 1 y nunca vuelve empezado al almacén.")
b("**Fleje.** El rollo es la tanda de la matriz (la embutidora tiene un solo desbobinador para 8 matrices): rollos de 179 "
  "a 1.181 kg; el mayor, la cúpula del 5 kg, entra en los 1.350 kg del desbobinador.")
add("h2", "2.2 Cuánto se guarda")
tabla(["Concepto", "Fórmula"], [
    ["Consumo del día pico", "Consumo promedio × factor de pico de la línea (1,08 manuales y carros; 1,22 recargas)"],
    ["Stock de seguridad", "Consumo pico × plazo máximo − consumo promedio × plazo medio (chapa y fleje: en paquetes o rollos enteros, mínimo 1)"],
    ["Stock máximo", "Seguridad + lo que trae un pedido (consumo pico × días entre pedidos): fija el lugar en el almacén"],
], [24, 76])
b("**Ejemplo, chapa del 1 kg:** 20,3 hojas/día en el pico × 10 días − 18,8 × 10 días = 15 hojas → 1 paquete de "
  "seguridad; más un pedido mensual de 20 paquetes: 21 paquetes (9,3 t) como máximo.")
b("**Un pedido por proveedor, en revisión periódica:** flejes cada 10 días, chapa cada 20, lo voluminoso semanal "
  "(polvo, gases, cajas, pallets) y lo de muy poco consumo cada 60. Son 596 pedidos por año (2,5 por día hábil).")
add("h2", "2.3 Cómo se guarda")
tabla(["Qué", "Cómo", "Por qué"], [
    ["Chapa", "7 pilas de hasta 2,5 m, una por formato sobre sus 3 tacos (el 5 kg en dos)", "El paquete mide 2 a 3 m y va entero a la mesa; manda el tope más bajo: autoelevador 3 m, estabilidad, piso 5 t/m²"],
    ["Flejes", "Acostados (ojo al cielo), un código por pallet, rack de 2 módulos y 4 alturas; apilador con pinza giratoria («volteador»)", "Parados se ovalan y no se apilan; los de más de 1 t en el piso del rack"],
    ["Casquetes de carros", "Contenedor 1.200 × 1.000 de NOVA Ruedas, un pedido por mes", "Compra nacional como Fadesa (≈ 40 días): el máximo baja a la mitad frente al importado"],
    ["El resto", "Rack selectivo: abajo lo que se usa, arriba la reposición", "Muchos códigos con pocos pallets: acceso directo y FIFO"],
], [16, 44, 40])
add("nota", "Resultado: 119 lugares, 221,8 m² (antes 207,5, que contaba mal la chapa) y $ 21,6 M en equipos de almacén con IVA.")

add("h1", "3. Pulmones entre puestos")
b("**El máximo es el que se junta de verdad.** Antes se sumaba el máximo de cada modelo como si esperaran todos a la "
  "vez. Simulando el plan minuto a minuto, las virolas bajan de 1.171 a 607 y toda la línea de manuales de 29.555 a 20.801 piezas.")
b("**Estante solo donde el que consume es más lento** (por pieza, por cambios o porque trabaja menos turnos): 14 de 19 "
  "tramos llevan estante; en los otros 5 el carro es el pulmón.")
b("**Protección solo donde importa:** 1 h antes del cuello y 3,75 h antes del marcapasos. El control de espesor es una "
  "muestra del 2 % al costado: no retiene el lote.")
b("**Cómo espera y cómo se mueve.** Bandeja 1.200 × 600 (hasta 150 kg) o cajón 600 × 400 × 300 (hasta 20 kg); estante "
  "pasante de 1,2 × 0,6 × 2,0 m que se carga desde el pasillo y se usa desde el puesto; la bandeja llena rueda sobre "
  "rodillos y nunca se levanta. Un carro por tramo; dos solo a la salida del cuello y del horno, que no pueden parar.")
b("**Fondos y cúpulas:** la tanda espera en un rack de 17 pallets al lado de la prensa; al puesto va solo la ola del día siguiente.")
b("**Carros:** esperan parados en piso demarcado. Cuerpos planos 52; al pintor cada 2 días (esperan 29, hay 41 en el "
  "pintor y 29 pintados sin ruedas sobre un taco); sin retención de 7 días al final: se verifica el manómetro al cargar.")
tabla(["Pulmones", "Antes", "Ahora"], [
    ["Piezas esperando en manuales (máximo)", "29.555", "20.801"],
    ["Contenedores / carros en manuales", "205", "32 carros + 44 módulos de estante"],
    ["m² de pulmones de manuales", "298,1", "108,3"],
    ["Recipientes de carro y m²", "280 · 104,3 m²", "178 · 47,3 m²"],
], [44, 22, 34], num=[1])

add("h1", "4. Producto terminado y despacho")
b("**Todo va parado**, para que el peso baje por el cuerpo y no por la válvula. Pallet ARLOG 1.200 × 1.000, hasta 1,6 m "
  "y 1.100 kg (límites de la envolvedora).")
tabla(["Producto", "Por pallet (1 · 2,5 · 5 · 10 kg)"], [
    ["Nuevos en caja (cajas paradas)", "360 · 168 · 84 · 60"],
    ["Cilindros vacíos de manuales (cartón entre capas)", "780 · 288 · 126 · 60"],
    ["Cilindros de carro (25 · 50 · 70 · 100 kg)", "24 · 9 · 6 · 6"],
    ["Carros terminados, sueltos en la Master", "14 · 10 · 7 · 7"],
], [55, 45])
b("**Stock máximo** = lo que deja el sobrestock + 5 días de venta de seguridad + 1 pallet en armado. Pico en noviembre: "
  "85 pallets en un rack de 3 niveles y 15 módulos, más 43 carros en el piso y un andén de 20 pallets: 272,6 m².")
b("**Mástil de 4,5 m:** el pallet más alto (10 kg en caja, 1.515 mm) obliga a levantar 3,73 m; el estándar llega a 3 m.")
tabla(["Vehículo", "Qué lleva", "Cuándo"], [
    ["Camión chico (6 pallets)", "Nuevos en caja", "Lunes, miércoles y viernes"],
    ["Sider (14 pallets)", "Cilindros de manuales y de carro", "Martes y jueves"],
    ["Renault Master con rampa", "Carros a clientes · ida y vuelta al pintor", "Todos los días · pintor cada 2 días"],
], [26, 40, 34])
b("**Pintura cada 2 días:** la menor cantidad de viajes (7,5 por semana), la Master al 95 % y solo 2 días de espera. Una "
  "sola Master alcanza (≈ 35 h por semana, 88 %). 18 carros de manipulación reemplazan 177 juegos provisorios de ruedas.")
add("nota", "Equipos de PT con precio: $ 10,1 M con IVA (rack); a cotizar el mástil, los carros de manipulación, cintas y tacos.")

add("h1", "5. Lo que hay que reservar en el layout")
tabla(["Concepto", "m²", "Antes"], [
    ["Pulmones de manuales (estantes, carros y rack de fondos y cúpulas)", "108,3", "298,1"],
    ["Pulmones de carros (espera del pintor y pintados)", "47,3", "104,3"],
    ["Recargas en planta", "108,0", "—"],
    ["Almacén de producto terminado", "272,6", "250,6"],
    ["Almacén de materia prima", "221,8", "207,5"],
    ["MP al pie de los puestos", "35,5", "—"],
    ["Total", "793,3", "1.004,0"],
], [62, 19, 19], num=[1, 2], negrita=[6])
add("nota", "Más de 200 m² menos sin perder capacidad: los pulmones se dimensionaron con lo que de verdad se junta y el "
            "estante usa la altura en lugar de carros parados.")

add("h1", "6. Preguntas que pueden hacer")
tabla(["Pregunta", "Respuesta corta"], [
    ["¿Por qué el paquete de chapa no es más grande?", "Va entero a la mesa: si sobra, vuelve empezado y la guillotina para a devolverlo; además ocupa más lugar."],
    ["¿Por qué un solo paquete de seguridad?", "Plazo corto (7 a 10 días) y consumo parejo: la fórmula da menos de uno y se redondea; el 5 kg lleva 3."],
    ["¿Por qué frecuencias en potencias de 2?", "1, 2, 4, 8 y 16 dividen a 16: cada formato cae siempre el mismo día del ciclo."],
    ["¿Por qué la embutidora no sigue la ola?", "Cambiar las 8 matrices cada día sería el 80 % de la prensa."],
    ["¿Por qué estante y no el carro parado?", "Usa la altura hasta 1,6 m, tiene lugar fijo, respeta el FIFO y libera el carro."],
    ["¿Por qué 2 carros en algunos tramos?", "Solo donde el que entrega no puede parar: el cuello y el horno de pintura."],
    ["¿Por qué no se retienen los carros?", "Control al 100 % con el manómetro al cargar y ensayos sobre la muestra; retener ocupaba 33,8 m²."],
    ["¿Qué limita la planta hoy?", "Manuales: soldadura longitudinal 2,5–10 kg (81 %). Recargas: ensayo de pérdidas en diciembre (87 %)."],
], [36, 64])

add("h1", "7. Lo que falta confirmar")
for t in ["Carga del piso del almacén (se supuso 5 t/m²).",
          "Cotizar el mástil de 4,5 m, el apilador con pinza, estantes, bandejas, carros porta-bandejas, rack y cajones.",
          "Cambio de matriz de la embutidora: 90 min (planilla) contra 120 min (Word de manuales).",
          "Medir pollera y domo de una cúpula y un fondo de cada modelo: definen cuántos entran por cajón.",
          "Alinear el Word de carros: lote semanal, retención y juegos de ruedas del puesto 8."]:
    b(t)

tmp = DOCX + ".json"
json.dump(bl, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
subprocess.run(["node", JS, tmp, DOCX, "Resumen FLAMA 2035"], check=True, env=dict(os.environ, NODE_PATH=NODE_PATH))
os.remove(tmp)
print("ok", DOCX)
