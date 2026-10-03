# Memoria de cálculo del layout - planta industrial FLAMA S.A. (año 10 = 2035)

Se genera desde `planta/calculos.py` y `planta/layout.py` (`python generar.py`). Cada número indica su fuente: **DT** = Dimensionamiento_TecnicoV2.xlsx, **MP** = MP_Abastecimiento_Almacenamiento_FLAMA_OpcionD.xlsx, **CC** = Comparacion_corte.xlsx, **C** = cotización de proveedor, **E** = estimado, **SUP** = supuesto a validar.

## 1. Demanda y tasas de diseño

| Formato | Matafuegos (u/año) | Cilindros vendidos (u/año) |
|---|---|---|
| 1 kg | 32.073 | 170.548 |
| 2,5 kg | 7.425 | 6.669 |
| 5 kg | 30.751 | 32.915 |
| 10 kg | 1.841 | 2.011 |
| 25 kg | 453 | 322 |
| 50 kg | 997 | 708 |
| 70 kg | 218 | 155 |
| 100 kg | 145 | 102 |

Recargas en planta: 128.800 u/año (DT). Tercerizados revendidos: 10.700 u/año (**SUP**: 12,7 % no ABC sobre las ventas de equipos; no hay dato en los Excel).

Mes pico = 1,40 × promedio (dic-ene). Horas productivas del mes pico: 22 días × 2 turnos × 8 h × 0,85 = 299 h.

| Familia | Tasa de diseño (u/h) |
|---|---|
| 1 kg | 79,0 |
| 2,5-10 kg | 31,8 |
| carros | 1,2 |

## 2. Nave y sectores

Nave de 88 × 44 m = 3.872 m², recorrido en U con una línea que converge paso a paso, pórticos de dos luces (19,40 y 24,60 m) cada 8 m, altura libre 8,00 m (Dec. 351/79 exige ≥ 3 m). Recargas dentro de la nave (ángulo SO, 327 m²). Anexos: servicios 288 m² y sala técnica 58 m².

| Código | Sector | m² proyectados | m² requeridos | Nota |
|---|---|---|---|---|
| AL-GS | Gases de soldadura Arcal 21: baterías llenas y vacías | 11,3 | - | Jaula ventilada contra el muro exterior; 2 baterías de 12 cilindros (llena + en espera); la que está en uso va al colector de la sala SC |
| AL-1T | Caños de 6 m: cantiléver interior | 13,8 | - | 12 atados ≤ 600 kg a 3 niveles; se cargan desde AN con el atado atravesado (P1 de 7,20 m) |
| AL-1H | Paquetes de hojas: 4 formatos de alto consumo | 19,5 | 50,0 | 4 posiciones de 1,5 × 3,0 m a 4 alturas = 16 paquetes ≤ 2 t; un formato por posición; FIFO; la más usada (1,6 × 1000 × 2000) frente a la mesa elevadora |
| AL-1F | Rollos de fleje | 18,0 | - | Porta-flejes de 3 niveles: 8 cunas × 3 = 24 rollos ≤ 1 t (8 anchos); se toman con gancho C |
| AL-1L | Hojas de bajo consumo (carros) | 5,1 | - | LAC 4,75 × 1500 × 3000: 1 paquete de ≈ 10 hojas cada 2 meses |
| AL-1C | Cuellos y roscas (cajas) | 3,8 | - | Estantería de cajas por medida; salen con la zorra del milk run a la preparación de cuello |
| AL-1A | Alambre MAG | 5,8 | - | Rack 1 módulo × 3 niveles = 6 pallets (bobinas de 15 kg y tambores de 250 kg) |
| AL-1N | Nafta e insumos del autoelevador de MP | 5,5 | - | Armario de inflamables (bidones de nafta) y estante de insumos; el autoelevador se estaciona al final del pasillo central |
| N1 | Corte y cuerpo 2,5-10 kg | 122,2 | - | 1 guillotina -> 2 numerado -> 3 cilindrado -> 4 soldadura longitudinal |
| N2 | Corte de caño 1 kg | 101,3 | - | 5 corte láser de caño; caños del cantiléver interior en carro porta-tubos por AN, A2 y PO-L |
| N3 | Cúpulas, fondos y cuellos | 131,6 | - | 6 desbobinado + embutido -> 7 preparación de cuello -> 8 soldadura de cuello |
| N4 | Unión y prueba hidráulica | 128,0 | - | 9 encastre -> 10 bordoneado -> 11 soldadura circ. -> 12 PH -> 13 secado |
| N5 | Granallado y defectos | 78,3 | - | 14 granallado -> 15 detección de defectos -> 16 corrección |
| MT | Taller de mantenimiento | 36,8 | 30,0 | Mantenimiento preventivo: bancos, torno, agujereadora, soldadora móvil; entra la transpaleta desde el pasillo central; puerta directa al pañol |
| PÑL | Pañol de mantenimiento y de línea | 17,3 | - | Pegado al taller: repuestos críticos, herramental del preventivo, consumibles de soldadura (toberas, puntas, discos) contra vale por la ventanilla a PO-1 |
| Q | Laboratorio de calidad | 34,0 | 31,0 | Metrología, espesor por ultrasonido, adherencia y espesor de pintura, niebla salina, humedad del polvo; probetas de soldadura (IRAM 3523 / 3550); archivo de legajos de calidad |
| QR | Cuarentena y muestras retenidas | 18,4 | 15,0 | Jaula con llave: lotes rechazados y un cilindro testigo por lote (IRAM 3517 / 3523) |
| SUP | Supervisor de planta | 13,8 | - | Oficina propia del encargado de turno, con ventana a la línea y al pasillo central |
| PCP | Planificación y control de la producción | 18,4 | - | Separada del supervisor: 2 puestos y tablero de programación con ventana a la línea |
| PV | Carros vacíos: supermercado de retorno | 56,9 | - | Cada carro vuelve vacío a su puesto de carga por PO-1 / PO-2; acá esperan los de reserva y los del milk run de abastecimiento |
| SC | Compresores y colectores de gases de soldadura | 49,3 | - | Área libre de la v6 más el ex pañol: colector de Arcal 21 y colector de humos en el extremo oeste (el más cercano a las soldadoras), 2 compresores de tornillo, secador y pulmón al este |
| GR | Granalla de acero y repuestos de la granalladora | 23,5 | - | Bolsas de 25 kg en pallets frente a la tolva de la granalladora (a 4 m); entra por P4 con transpaleta |
| S-P | Pintura en polvo (esquema Electricolor 22 × 13 m) | 286,0 | - | 17 carga -> cabina -> polimerizado -> enfriamiento -> descarga |
| QP | Pintura electrostática en polvo | 44,9 | 24,1 | Cajas de 25 kg por color en pallets, < 30 °C; entra por el portón P4; puerta directa a las tolvas |
| ST-I | Tableros y compresor de la cabina | 39,6 | - | Tablero de la línea este y compresor sin aceite dedicado a la cabina de pintura |
| AL-C | Almacén de cilindros pintados | 125,4 | - | Pulmón de pintados antes de la carga de polvo y cilindros vendidos vacíos |
| SP-1 | Almacén previo a la carga y carga de polvo | 92,8 | - | Polvos (big bags), agentes extintores y baterías de N₂ de presurización; deshumidificador: HR ≤ 70 %, 8 renovaciones por hora, sin estufas (IRAM 3517-2) |
| S-T | Terminación 1-10 kg | 119,5 | - | 18 carga de polvo -> 19 ensamblaje -> 20 presurización -> 21 hermeticidad -> 22 etiquetado -> 23 embalaje -> 24 envolvedora |
| AL-2 | Válvulas, manómetros y pescantes (MP de terminación) | 17,7 | 40,0 | Rack de 4 niveles contra el muro sur; llegan por el muelle P3; se reparten en cajas a los buffers de cada línea (nuevos, carros, recargas) |
| DL | Ducha de emergencia y lavaojos | 6,2 | - | Junto a la carga de polvo y la pintura (a menos de 10 s de marcha) |
| AL-3 | Almacén de producto terminado | 189,6 | - | 4 racks de 12 m × 4 niveles = 128 posiciones (req. 88) |
| EXP | Expedición y muelle P3 | 102,7 | - | Un solo muelle con rampa niveladora: sale PT y entran revendidos, insumos, polvos, agentes y N₂ |
| S4 | Tercerizados revendidos | 5,7 | - | CO₂, agua, AFFF, clase K y agente limpio con sello IRAM: recepción por P3, control y stock |
| EMB | Embalaje de matafuegos nuevos y revendidos | 12,7 | - | Film, pallets, etiquetas, cajas de cartón, grapas y precintos; sólo para la logística interna de PT |
| AL-PN | Nafta e insumos de los autoelevadores de PT y de carros | 6,2 | - | Armario de inflamables y estante de repuestos (logística interna) |
| S3 | Línea de carros 25-100 kg | 170,6 | - | C1 cilindrado -> C2 punteo -> C3 soldadura long. -> C4 soldadura circ. -> C5 inspección -> C6 PH -> C7 marcado |
| PU-CP | Carros a pintura tercerizada | 19,6 | - | Esperan el camión del pintor; salen y vuelven por PO-C y el muelle P3 |
| SP-2 | Sala de carga de polvo de carros | 29,4 | - | Recinto HR ≤ 70 %: big bag de carros y cabina de descarga de muestras (IRAM 3550) |
| S-TC | Terminación de carros | 26,5 | - | C9 armado de ruedas y manguera -> C10 presurización y etiquetado; embalaje de carros |

Los m² requeridos de MP (hoja MP Almacén) suponen almacenamiento a piso o en rack de 3 niveles con medio pasillo propio. En el layout el almacén de MP guarda sólo seis rubros, en altura frente a las calles A1/A2 del autoelevador de MP: hojas en paquetes sobre tacos (AL-1H, 4 posiciones × 4 alturas, más el LAC 4,75 en AL-1L), flejes en porta-flejes de 3 niveles (AL-1F, 24 rollos), caño en el cantiléver interior (AL-1T, 12 atados), cuellos y roscas (AL-1C), alambre MAG (AL-1A) y baterías de Arcal 21 (AL-GS). Válvulas, manómetros y pescantes van a AL-2 junto a terminación; polvos, agentes y N₂ al almacén previo a la carga (SP-1); pintura y granalla a QP y GR. El scrap no se guarda: queda en el contenedor de cada puesto.


## 3. Recepción de MP y análisis de peso de la carga

Se dimensiona para la carga máxima: un semirremolque de 18,6 m y 30 t o dos chasis de 10 m en el alero de descarga norte (32 × 11,6 m), con descarga por ambos lados con autoelevador. La nave tiene sólo cuatro portones, uno por frente logístico: P1 (MP de producción, 7,20 m de ancho para que el atado de caño de 6 m entre atravesado), P2 (recargas), el muelle único P3 (PT, carros, revendidos, casquetes, válvulas, embalaje, polvos, agentes y N₂; recepción 7 a 10 h y expedición 13 a 17 h) y P4 (pintura y granalla). Los camiones entran por G1 (garita y báscula) y salen por G3: calle norte al alero de P1, calle sur a la playa del muelle P3 y calle este a P4.

| Formato | Largo (m) | Carga útil (t) | PBT (t) | Descarga |
|---|---|---|---|---|
| Semirremolque playo 3+3 ejes | 18,6 | 30,0 | 45,0 | Alero de descarga norte: autoelevador por los dos lados; entra al almacén de MP por P1 |
| Camión chasis con balancín (3 ejes) | 11,0 | 16,0 | 26,0 | Alero de descarga norte (junto al semi): autoelevador por los dos lados, bajo techo |
| Camión chasis 2 ejes | 9,5 | 9,0 | 16,5 | Alero norte (P1), muelle P3 o portón P4 según el material |
| Utilitario / furgón | 6,0 | 1,5 | 3,5 | Recargas por P2; pintura por P4 |

| Proveedor / material | t por entrega | Entregas/año | Vehículo | Portón | Destino |
|---|---|---|---|---|---|
| Pradecon: hojas + fleje 0,9 | 35,26 | 18,1 | Semi (máx.) o 2 chasis quincenales | Alero + P1 | AL-1H, AL-1F |
| Pacheco: flejes 1,25-2,0 | 5,05 | 29,3 | Chasis 2 ejes | Alero + P1 | AL-1F |
| Metalprisa: caño Ø76,2 | 4,23 | 28,9 | Chasis 2 ejes | Alero + P1 (atado atravesado) | AL-1T cantiléver |
| Eli-Met: cuellos y roscas | 3,68 | 5,6 | Chasis 2 ejes | Alero + P1 | AL-1C |
| Soldadura: alambre MAG | 1,89 | 8,1 | Chasis 2 ejes | Alero + P1 | AL-1A |
| Air Liquide: Arcal 21 (baterías) | 3,80 | 15,6 | Chasis 2 ejes | Alero + P1 | AL-GS -> colector SC |
| Air Liquide: N₂ (baterías) | 3,80 | 15,6 | Chasis 2 ejes | Muelle P3 | SP-1 |
| Polvo químico (Polvex / DEMSA) | 13,13 | 31,0 | Chasis con balancín | Muelle P3 | SP-1 (y SP-2, recargas) |
| Válvulas, manómetros y pescantes | 8,16 | 8,3 | Chasis con balancín | Muelle P3 | AL-2 -> buffers |
| Casquetes de carros | 5,93 | 4,1 | Chasis 2 ejes | Muelle P3 | RK1 (cara este) |
| Estructuras y ruedas de carros | 5,52 | 15,1 | Chasis 2 ejes | Muelle P3 | S-TC |
| Embalaje, pallets, etiquetas y precintos | 4,61 | 15,3 | Chasis 2 ejes | Muelle P3 | EMB / S-TC / RC-RD |
| Tercerizados revendidos | 3,00 | 24,0 | Chasis 2 ejes (SUPUESTO) | Muelle P3 | S4 |
| Agentes para recargas | 2,87 | 8,2 | Chasis 2 ejes | Muelle P3 | SP-1 -> recargas |
| CYM: granalla | 3,11 | 2,0 | Chasis 2 ejes | P4 | GR |
| Pintura electrostática en polvo | 0,79 | 8,3 | Utilitario | P4 | QP |

Pradecon entrega 35,3 t por mes (hojas + fleje 0,9): supera la carga útil de un semi. Se parte en 2 entregas quincenales de 17,6 t, que entran en un chasis con balancín y bajan el stock máximo de chapa medio mes.

Capacidad residual del autoelevador con un paquete de hoja de 1500 × 3000 mm y 2 t (Q = Qn · (cn + d) / (c + d), d = 0,45 m):

| Nominal (c = 500 mm) | Por el lado largo (c = 750 mm) | Por el lado corto (c = 1500 mm) |
|---|---|---|
| 2,5 t | 1,98 t | 1,22 t |
| 3,0 t | 2,38 t | 1,46 t |
| 3,5 t | 2,77 t | 1,71 t |

Se adopta para MP un autoelevador a nafta de 3,0 t con horquillas de 1,8 m y posicionador: toma el paquete por el lado largo (2,37 t > 2 t). El de 2,5 t que proponía el Excel queda justo (1,98 t) y no sirve por el lado corto; sí alcanza para los frentes de carros y recargas y de PT.

## 4. Anti-sobrestock de chapa SAE 1010

| Formato | Hojas/semana | Paquete de 2 t cubre (sem) | Paquete propuesto | Stock máx. (sem) |
|---|---|---|---|---|
| LAF 1,25 × 1220 × 2440 (2,5 kg) | 10,9 | 6,3 | 22 hojas (644 kg) | 4,0 |
| LAF 1,6 × 1000 × 2000 (5 kg) | 110,5 | 0,7 | 79 hojas (1.989 kg) | 1,4 |
| LAF 2,0 × 1500 × 3000 (10 kg) | 5,4 | 5,2 | 11 hojas (779 kg) | 4,1 |
| LAC 3,2 × 1500 × 3000 (25 y 50 kg) | 7,7 | 2,2 | 16 hojas (1.813 kg) | 4,1 |
| LAC 4,75 × 1500 × 3000 (70 y 100 kg) | 3,4 | 3,2 | 7 hojas (1.177 kg) | 4,1 |

Reglas: una posición de AL-1H por formato con dos paquetes (en uso y en espera) y tope pintado; si están ocupadas no se emite pedido (kanban de 2 paquetes). Paquetes chicos en los formatos de bajo consumo para que ninguno cubra más de 2 semanas. Tarjeta de color por mes de ingreso y semáforo (verde < 4 semanas, amarillo 4 a 6, rojo > 6: se consume primero y se inspecciona óxido). Hoja LAF aceitada con film VCI, descargada y guardada siempre bajo techo, lejos de la PH y del lavado.

## 5. Pulmones y manejo de materiales (métodos y tiempos)

| Pulmón | Tasa (u/h) | Cobertura (h) | Unidades | Carros | Criterio |
|---|---|---|---|---|---|
| PU-G cuerpos 2,5-10 kg y carros | 33,0 | 8,00 | 264 | 6 | La guillotina corta por tandas de un formato: 1 turno de consumo |
| M17 cuerpos 1 kg (láser) | 79,0 | 0,50 | 40 | 2 | Un viaje del tren logístico + cambio de barra |
| SM-K cúpulas y fondos (pares) | 110,8 | 4,00 | 443 | 3 | Cambio de troquel de la prensa (≈ 30 min) cada medio turno |
| A00 kanban celda 1 kg | 79,0 | 0,50 | 40 | 2 | 2 carros: uno en uso y otro en reposición |
| B00 supermercado celda 2,5-10 kg | 31,8 | 1,00 | 32 | 2 | 2 carros por formato en curso |
| A08 y B11 a pintura | 110,8 | 0,75 | 83 | 2 | Parada de cambio de color / limpieza de cabina (≈ 45 min) sin detener las celdas |
| PU a terminación (tren de descarga) | 110,8 | 0,50 | 55 | 2 | Carga de polvo por lote |

Tiempo por viaje = 2 × distancia / velocidad + tiempo fijo de toma y entrega. Distancias medidas sobre los recorridos del modelo; día pico 2035.

| Unidad de carga | Medio | Recorrido | Viajes/día | m | min/viaje | min/día |
|---|---|---|---|---|---|---|
| Paquete de hojas ≤ 2 t | Autoelevador MP | Alero -> P1 -> AL-1H | 1,5 | 26 | 2,1 | 3 |
| Paquete a la guillotina | Autoelevador MP | AL-1H -> mesa elevadora | 1,5 | 4 | 1,6 | 2 |
| Rollo de fleje 0,5-1 t | Autoelevador MP | Alero -> P1 -> porta-flejes | 0,8 | 52 | 2,7 | 2 |
| Rollo al desbobinador | Autoelevador MP | Porta-flejes -> desbobinador | 0,8 | 35 | 2,3 | 2 |
| Atado de caño 6 m (atravesado) | Autoelevador MP | Alero -> P1 -> cantiléver | 0,6 | 13 | 1,8 | 1 |
| Carro porta-tubos (6,5 m) | Carro a mano | Cantiléver -> AN -> A2 -> PO-L | 1,5 | 17 | 1,2 | 2 |
| Batería de Arcal 21 | Autoelevador MP | Jaula AL-GS -> patio norte -> SC | 0,2 | 64 | 2,9 | 1 |
| Contenedor de scrap (guillotina) | Autoelevador MP | Guillotina -> volquete (P1) | 0,5 | 43 | 2,5 | 1 |
| Carro de scrap (láseres y prensa) | Carro a mano | Puesto -> A2 -> volquete (P1) | 1,5 | 29 | 1,7 | 3 |
| Big bag de polvo 1 t | Autoelevador PT | Muelle P3 -> AT -> SP-1 | 1,7 | 30 | 2,2 | 4 |
| Pallet de válvulas / manómetros | Autoelevador PT | Muelle P3 -> AL-2 | 1,3 | 16 | 1,8 | 2 |
| Pallet de embalaje | Autoelevador PT | Muelle P3 -> EMB | 0,7 | 4 | 1,6 | 1 |
| Pallet de PT | Autoelevador PT | Envolvedora -> rack AL-3 | 7,2 | 4 | 1,6 | 11 |
| Pallet de PT | Autoelevador PT | Rack AL-3 -> muelle P3 | 7,2 | 10 | 1,7 | 12 |
| Pallet de cilindros vacíos | Autoelevador PT | AL-C -> rack AL-3 | 2,8 | 16 | 1,8 | 5 |
| Pallet de casquetes | Autoelevador carros | Muelle P3 -> rack pasante RK1 | 0,2 | 16 | 1,9 | 0 |
| Carros pintados / polvo / estructuras | Autoelevador carros | Muelle P3 -> PO-C -> SP-2 y S-TC | 0,6 | 22 | 2,0 | 1 |
| Carro terminado 25-100 kg | Autoelevador carros | S-TC -> muelle P3 | 1,0 | 12 | 1,8 | 2 |
| Pallet de bolsas de polvo y agentes | Autoelevador carros | SP-1 -> AT -> EX -> PO-C -> recargas | 1,0 | 75 | 3,2 | 3 |
| Caja de pintura / bolsa de granalla | Transpaleta | P4 -> QP y GR | 0,6 | 37 | 2,5 | 2 |
| Carro de cuerpos 2,5-10 kg (24 u) | Carro a mano | PU-4 -> 9 encastre | 14,0 | 6 | 0,8 | 11 |
| Carro de cuerpos 1 kg (80 u) | Carro a mano | PU-L2 -> 9 encastre | 12,0 | 13 | 1,1 | 13 |
| Carro de fondos (150 u) | Carro a mano | PU-K -> 9 encastre | 8,0 | 15 | 1,1 | 9 |
| Carro de cúpulas con cuello (60 u) | Carro a mano | PU-C -> 11 sold. circ. | 20,0 | 24 | 1,5 | 30 |
| Carro de cilindros, 9 tramos 9 -> 16 | Carro a mano | entre pasos (prom. por tramo) | 198,0 | 4 | 0,7 | 136 |
| Carro de cilindros controlados | Carro a mano | PU-8 -> 17 carga de pintura | 22,0 | 6 | 0,8 | 17 |
| Carro de cilindros pintados | Carro a mano | PU-9 -> 18 carga de polvo | 22,0 | 6 | 0,8 | 16 |
| Zorra de consumibles y cajas (vuelta) | Zorra milk run | Pañol y AL-1 -> puestos -> pañol | 4,0 | 79 | 3,8 | 15 |

Ocupación sobre un turno útil de 408 min: autoelevador de MP 3 %, de carros y recargas 2 %, de PT 9 %. Se asigna uno por frente (MP, carros y recargas, PT) para que ninguno cruce el frente de otro ni la línea; los tres a nafta, con su armario de inflamables e insumos en MP (AL-1N) y en PT (AL-PN). Entre pasos se mueven 22 carros por día y por tramo: los empuja el operario que cierra el lote (< 1 min por viaje), sin tren logístico ni chofer; al norte de la senda no entra el autoelevador. Un abastecedor por turno hace el milk run de consumibles desde el pañol de línea y repone carros vacíos desde el supermercado PV.

| Portón | Qué entra o sale | Vehículo | Frecuencia | Horario |
|---|---|---|---|---|
| P1 + alero | Entran hojas, flejes, caños, cuellos, alambre MAG y Arcal 21; sale el scrap al volquete | Semi / chasis | ≈ 2,4 camiones + 0,6 gases por semana | 7 a 10 h |
| P2 | Recargas: los utilitarios dejan y retiran equipos de clientes | Utilitarios de reparto (8) | 2 vueltas por día | Milk run mañana y tarde |
| P3 (muelle) | Sale PT y carros (terminados y al pintor); entran revendidos, casquetes, válvulas, embalaje, polvos, agentes y N₂ | Semi / chasis | 7 PT + ≈ 3 recepciones por semana | Recepción 7 a 10 h; expedición 13 a 17 h |
| P4 | Entran pintura electrostática y granalla | Utilitario / chasis | ≈ 0,2 por semana | 7 a 10 h |
| PP-1 | Personal: vestuarios <-> senda de la nave | A pie | 63 personas, 2 turnos | Entrada y salida |

Colector de Arcal 21 y de humos de soldadura en el extremo oeste de la sala SC: 285 m de cañería (recorrido ortogonal) a las 9 soldadoras, contra 354 m si estuviera en el centro de la sala.

| Soldadora | m desde el colector |
|---|---|
| B03 | 27,5 |
| A06 | 11,7 |
| B06 | 8,7 |
| M11 | 28,0 |
| M12 | 26,0 |
| C02 | 44,8 |
| C03 | 41,8 |
| C04 | 46,5 |
| C05 | 50,2 |
## 6. Cruces de flujos y de hilos

Cruces entre flujos de MP, SE y PT (verificación geométrica sobre el modelo): **63**. Cruces de hilos de personal con flujos: todos dentro de las **22** sendas peatonales señalizadas (X1 a X22).

## 7. Sanitarios, vestuarios y servicios (Dec. 351/79 arts. 49 y 50)

Turno más numeroso: 55 hombres (47 del turno mañana + 8 choferes) y 6 mujeres.

| Artefacto | H requerido | H proyectado | M requerido | M proyectado |
|---|---|---|---|---|
| inodoros | 3 | 3 | 1 | 1 |
| lavabos | 6 | 6 | 1 | 1 |
| orinales | 6 | 6 | 0 | 0 |
| duchas | 3 | 3 | 1 | 1 |

Armarios: H 56 requeridos / 60 proyectados; M 7 / 9 (vestuario de mujeres al 20 % de la dotación). Lockers individuales, 1 por empleado, en bloques de 10 columnas × 3 filas. Un sanitario accesible con ducha en el bloque de servicios (Ley 24.314, Dec. 914/97: círculo libre de Ø 1,50 m, espacio lateral de 0,80 m, barras); los sanitarios de planta son sólo de hombres y de mujeres. Espacio de cuidado no obligatorio (Dec. 144/2022 exige 100 o más personas; la dotación es 71). Comedor de 30 plazas en 2 tandas (DT Servicios).

| Local | m² |
|---|---|
| SV-LU Utilitarios de limpieza | 10,3 |
| SV-HY Higiene y seguridad, medicina laboral, primeros auxilios y EPP | 16,7 |
| SV-HA Hall, recepción y fichado | 10,6 |
| SV-AD Administración: compras, ventas y RRHH | 27,7 |
| SV-PL Pasillo limpio a la planta (PP-1) | 26,7 |
| SV-VH Vestuario hombres (60 lockers) | 25,2 |
| SV-DH Duchas hombres | 18,2 |
| SV-SH Inodoros, mingitorios y lavabos hombres | 26,0 |
| SV-VM Vestuario mujeres (9 lockers) | 10,8 |
| SV-SM Inodoro y lavabo mujeres | 5,4 |
| SV-DM Ducha mujeres | 5,4 |
| SV-AC Sanitario accesible con ducha | 13,3 |
| SV-PS Pasillo al sanitario accesible, al comedor y a la salida SV-2 | 12,4 |
| SV-CM Comedor (30 plazas) y office | 55,6 |
| SN-H Sanitarios hombres (planta) | 14,4 |
| SN-M Sanitario mujeres (planta) | 7,2 |
| RC-RD Recepción y despacho (portón P2) | 26,0 |
| RC-DE Desarme y lavado | 28,4 |
| RC-DC Descarga y ensayo de funcionamiento | 28,4 |
| RC-C1 Corredor de recargas (sur) | 24,2 |
| RC-GA CO₂ y agente limpio | 16,3 |
| RC-PV Recinto de polvo (HR ≤ 70 %) | 32,6 |
| RC-PH PH con jaula, secado y Puffer | 18,5 |
| RC-C2 Corredor de recargas (centro) | 22,3 |
| RC-CN Conector al pasillo central | 18,5 |
| RC-IR Inutilizados y residuos | 8,9 |
| RC-CQ Calidad de recargas (IRAM 3517-2) | 9,6 |
| RC-EN Ensamblaje, presurización, peso, hermeticidad y retoque | 38,5 |
| RC-LQ Líquidos | 10,1 |
| RC-RP Etiquetado y flota de intercambio | 10,9 |

## 8. Medios de escape (Dec. 351/79 anexo VII)

Factor de ocupación industrial 16 m²/persona: N = 242 personas teóricas; n = N/100 -> 3 unidades de ancho de salida (1,55 m mínimos). Proyectado: 10 salidas de emergencia de 1,10 m (11,00 m) con barral antipánico, más los portones con puerta de hombre y el paso a servicios.

Recorrido real máximo hasta una salida, calculado sobre una grilla de 0,5 m que rodea los equipos: **35,7 m** (punto x = 49,5, y = 26,0), por debajo de los 40 m que se toman como límite (verificar el artículo vigente).

## 9. Protección contra incendio

Extintores ABC de 10 kg en la nave: **20** (mínimo por superficie 1 cada 200 m² = 20), ubicados por cálculo para que ningún punto quede a más de 20 m de recorrido (IRAM 3517-2:2020, fuego clase A). Se suman 10 en anexos y exteriores, CO₂ junto a tableros y un carro de 50 kg ABC en pintura y en la sala de polvo. Señalización con chapa baliza y cartel en altura (IRAM 3517-2 cap. 7). La reserva de agua contra incendio y la red de hidrantes quedan previstas en el terreno y se confirman con el estudio de carga de fuego.

## 10. Iluminación (método de los lúmenes)

Luminaria LED de 150 W y 21.000 lm; factor de utilización 0,65; mantenimiento 0,80. Niveles: nave 300 lx, depósitos 150 lx, pintura 500 lx, laboratorio 750 lx; soldadura y montaje fino 500 lx y líquidos penetrantes 750 lx con iluminación localizada.

| Sector | lx | m² | Luminarias | kW |
|---|---|---|---|---|
| AL-GS Gases de soldadura Arcal 21: baterías llenas y vacías | 150 | 11 | 1 | 0,15 |
| AL-1T Caños de 6 m: cantiléver interior | 150 | 14 | 1 | 0,15 |
| AL-1H Paquetes de hojas: 4 formatos de alto consumo | 150 | 20 | 1 | 0,15 |
| AL-1F Rollos de fleje | 150 | 18 | 1 | 0,15 |
| AL-1L Hojas de bajo consumo (carros) | 150 | 5 | 1 | 0,15 |
| AL-1C Cuellos y roscas (cajas) | 150 | 4 | 1 | 0,15 |
| AL-1A Alambre MAG | 150 | 6 | 1 | 0,15 |
| AL-1N Nafta e insumos del autoelevador de MP | 300 | 6 | 1 | 0,15 |
| N1 Corte y cuerpo 2,5-10 kg | 300 | 122 | 4 | 0,60 |
| N2 Corte de caño 1 kg | 300 | 101 | 3 | 0,45 |
| N3 Cúpulas, fondos y cuellos | 300 | 132 | 4 | 0,60 |
| N4 Unión y prueba hidráulica | 300 | 128 | 4 | 0,60 |
| N5 Granallado y defectos | 300 | 78 | 3 | 0,45 |
| MT Taller de mantenimiento | 300 | 37 | 2 | 0,30 |
| PÑL Pañol de mantenimiento y de línea | 300 | 17 | 1 | 0,15 |
| Q Laboratorio de calidad | 750 | 34 | 3 | 0,45 |
| QR Cuarentena y muestras retenidas | 750 | 18 | 2 | 0,30 |
| SUP Supervisor de planta | 300 | 14 | 1 | 0,15 |
| PCP Planificación y control de la producción | 300 | 18 | 1 | 0,15 |
| PV Carros vacíos: supermercado de retorno | 300 | 57 | 2 | 0,30 |
| SC Compresores y colectores de gases de soldadura | 300 | 49 | 2 | 0,30 |
| GR Granalla de acero y repuestos de la granalladora | 150 | 24 | 1 | 0,15 |
| S-P Pintura en polvo (esquema Electricolor 22 × 13 m) | 500 | 286 | 14 | 2,10 |
| QP Pintura electrostática en polvo | 150 | 45 | 1 | 0,15 |
| ST-I Tableros y compresor de la cabina | 300 | 40 | 2 | 0,30 |
| AL-C Almacén de cilindros pintados | 150 | 125 | 2 | 0,30 |
| SP-1 Almacén previo a la carga y carga de polvo | 300 | 93 | 3 | 0,45 |
| S-T Terminación 1-10 kg | 300 | 119 | 4 | 0,60 |
| AL-2 Válvulas, manómetros y pescantes (MP de terminación) | 150 | 18 | 1 | 0,15 |
| DL Ducha de emergencia y lavaojos | 300 | 6 | 1 | 0,15 |
| AL-3 Almacén de producto terminado | 150 | 190 | 3 | 0,45 |
| EXP Expedición y muelle P3 | 150 | 103 | 2 | 0,30 |
| S4 Tercerizados revendidos | 150 | 6 | 1 | 0,15 |
| EMB Embalaje de matafuegos nuevos y revendidos | 150 | 13 | 1 | 0,15 |
| AL-PN Nafta e insumos de los autoelevadores de PT y de carros | 300 | 6 | 1 | 0,15 |
| S3 Línea de carros 25-100 kg | 300 | 171 | 5 | 0,75 |
| PU-CP Carros a pintura tercerizada | 300 | 20 | 1 | 0,15 |
| SP-2 Sala de carga de polvo de carros | 300 | 29 | 1 | 0,15 |
| S-TC Terminación de carros | 300 | 26 | 1 | 0,15 |

Total: 85 luminarias, 12,8 kW.

## 11. Redes: longitud de tendidos (criterio 4)

| Tablero seccional | kW | Largo desde el TGBT (m) |
|---|---|---|
| N1 | 23,8 | 30,4 |
| N2 | 20,0 | 35,4 |
| N3 | 71,4 | 26,7 |
| N4 | 55,2 | 16,4 |
| N5 | 31,0 | 42,3 |
| S-P | 24,0 | 65,3 |
| SP-1 | 9,0 | 61,4 |
| S-T | 2,5 | 55,3 |
| AL-3 | 1,5 | 42,5 |
| S3 | 68,0 | 41,3 |
| SP-2 | 5,0 | 58,1 |
| S-TC | 1,0 | 50,8 |
| SC | 69,0 | 17,8 |
| RC-RD | 2,0 | 78,2 |
| RC-DE | 2,0 | 73,0 |
| RC-DC | 2,5 | 67,1 |
| RC-PH | 1,5 | 62,2 |
| RC-PV | 2,5 | 67,7 |
| RC-GA | 1,5 | 73,4 |
| RC-LQ | 0,5 | 57,8 |
| RC-EN | 4,0 | 60,9 |
| RC-RP | 0,5 | 54,1 |

**Agua de PH y pretratamiento a PTE**: A07 73 m, B07 70 m (total 143 m).

**Gas natural a hornos**: B14 57 m, A11 59 m, P03 14 m, P06 11 m (total 142 m).

**Nitrógeno**: T05 11 m, T13 38 m (total 48 m).

**Gas de soldadura**: B03 28 m, M11 28 m, M12 26 m, A06 12 m, B06 9 m, C04 46 m, C05 50 m (total 199 m).


Anillo de aire comprimido: 272 m. Potencia instalada de equipos: 398 kW.

## 12. Longitud de los flujos

| Tipo | Flujo | Largo (m) |
|---|---|---|
| MP | Hojas: alero -> P1 -> A2 -> paquetes AL-1H | 25,8 |
| MP | Paquete a la mesa elevadora (autoelevador por el lado largo) | 3,9 |
| MP | Caños: el autoelevador entra por P1 con el atado atravesado y lo apoya en el cantiléver | 13,4 |
| MP | Caños: carro porta-tubos por AN, A2 y PO-L a los caballetes | 16,7 |
| MP | Tubos a los caballetes | 6,4 |
| MP | Flejes: alero -> P1 -> A2 -> pasillo central -> A1 -> porta-flejes | 52,2 |
| MP | Rollo al desbobinador (gancho C) | 35,1 |
| MP | Gases Arcal 21: baterías a la jaula AL-GS | 12,0 |
| MP | Batería de Arcal 21 al colector de la sala SC (patio norte, puerta PG) | 64,4 |
| MP | Casquetes de carros (P3 -> rack pasante RK1) | 21,8 |
| MP | Casquete a la soldadura circ. | 8,4 |
| MP | Tercerizados revendidos (P3) | 8,5 |
| MP | Válvulas, manómetros y pescantes (P3 -> AL-2) | 21,5 |
| MP | Válvulas a la estantería pasante de ensamblaje | 4,7 |
| MP | Embalaje, pallets y precintos (P3 -> EMB) | 10,4 |
| MP | Polvos, agentes y N₂ (P3 -> AT -> almacén previo a la carga) | 36,2 |
| MP | Big bag a la carga de polvo | 1,0 |
| MP | Cajas y film de EMB al embalaje | 4,3 |
| MP | Pintura electrostática (P4) | 10,0 |
| MP | Pintura en polvo a las tolvas de aplicación | 12,9 |
| MP | Granalla (P4 -> PO-E -> PO-4 -> GR) | 36,9 |
| MP | Carros pintados, polvo y estructuras de carros (P3 -> PO-C) | 28,1 |
| SE | Cuerpo cortado | 0,2 |
| SE | Cuerpos al pulmón | 5,6 |
| SE | Cuerpo 2,5-10 kg: numerado -> cilindrado -> soldadura longitudinal | 11,9 |
| SE | Cuerpos 2,5-10 kg al encastre | 6,3 |
| SE | Cuerpos de carros a la cilindradora | 6,8 |
| SE | Cuerpo 1 kg | 1,2 |
| SE | Cuerpo 1 kg | 1,2 |
| SE | PU-L1 a PU-L2 | 2,4 |
| SE | Cuerpos 1 kg al encastre | 13,3 |
| SE | Fleje enderezado | 0,3 |
| SE | Fleje al troquel | 0,3 |
| SE | Fondos al pulmón | 0,5 |
| SE | Fondos al encastre | 14,8 |
| SE | Cúpulas a la preparación de cuello | 3,1 |
| SE | Cuello preparado | 0,8 |
| SE | Cúpulas con cuello al pulmón | 0,4 |
| SE | Cúpulas a la soldadura circ. | 24,4 |
| SE | Cúpulas a la soldadura circ. | 4,6 |
| SE | Línea principal: encastre -> bordoneado -> soldadura circ. -> PH -> secado -> granallado | 40,2 |
| SE | Defectos a corrección | 1,4 |
| SE | Aprobados al pulmón de pintura | 2,6 |
| SE | Corregidos al pulmón de pintura | 5,1 |
| SE | A la carga de pintura | 6,2 |
| SE | Pintura: carga, cabina, horno 1 y descarga (transportador aéreo por empuje) | 22,1 |
| SE | Pintura: horno 2 en paralelo | 10,7 |
| RET | Retorno de ganchos (sistema de avance) | 23,0 |
| SE | Pintados al pulmón | 21,0 |
| SE | A la carga de polvo | 6,0 |
| SE | Ensamblaje -> presurización -> hermeticidad -> etiquetado -> embalaje | 12,1 |
| SE | Carros: punteo, soldaduras, inspección, PH y marcado | 29,0 |
| SE | Carros a la espera del pintor (cruzan PO-C) | 3,4 |
| SE | Carros al pintor por PO-C y el muelle P3 | 33,9 |
| SE | Carga de polvo -> armado | 0,8 |
| SE | Armado -> presurización | 0,2 |
| PT | Cilindros vendidos vacíos al almacén de PT | 15,6 |
| PT | Pallet a envolvedora | 3,5 |
| PT | Pallet a envolvedora | 2,5 |
| PT | Pallet de cilindros a envolvedora | 1,6 |
| PT | Almacén de PT (envolvedora -> RK3) | 3,7 |
| PT | Expedición (RK2 -> T2 -> muelle P3) | 16,3 |
| PT | Expedición (RK3 -> T3 -> muelle P3) | 18,5 |
| PT | Carros terminados (S-TC -> EX -> muelle P3) | 18,0 |
| PT | Tercerizados a expedición | 8,4 |
| SCRAP | Scrap de la guillotina: autoelevador de MP por el pasillo central y A2 al volquete (P1) | 42,9 |
| SCRAP | Scrap del láser 5.2: carro por PO-L y A2 al volquete (P1) | 32,8 |
| SCRAP | Scrap del láser 5.1 a PO-L | 9,5 |
| SCRAP | Esqueleto de la prensa: carro por PO-3 y AN al volquete (P1) | 29,0 |

## 13. Supuestos a validar

- Tercerizados revendidos: volumen estimado (no figura en los Excel).
- Retiros, FOS y FOT del parque industrial; ubicación de la celda de media tensión y de la reducción de gas.
- Medidas de diseño (marcadas D con su criterio): confirmar con los proveedores al cotizar.
- Textos normativos marcados como B en el README (Dec. 351/79 arts. 49, 50 y anexo VII; Res. SRT 960/2015): verificar la versión vigente en InfoLEG.
- Recargas se incluye porque figura en el dimensionamiento técnico, aunque no estaba en la lista de secciones del pedido.
