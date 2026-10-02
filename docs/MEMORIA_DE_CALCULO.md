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

Nave de 96 × 50 m = 4.800 m², layout en U, pórticos de dos luces de 25 m cada 8 m, altura libre 8,00 m (Dec. 351/79 exige ≥ 3 m). Recargas dentro de la nave (ángulo SO, 435 m²). Anexos: servicios 342 m², sala técnica 70 m², cobertizo de químicos 58 m².

| Código | Sector | m² proyectados | m² requeridos | Nota |
|---|---|---|---|---|
| BR | Bahía interior de descarga | 136,0 | - | Chasis de 10 m entra por P1 y se descarga por los dos lados con autoelevador de 3,0 t |
| SCR-O | Scrap (orillas, esqueleto de fleje y recortes) | 33,6 | - | Contenedores basculantes de 1 m³; salen por P2 al volquete del patio oeste |
| PÑ | Pañol de insumos pesados | 40,9 | 35,2 | Alambre MIG, granalla, asientos de válvula y cuplas, tapones, consumibles |
| AL-1F | Flejes | 18,0 | 18,0 | Porta-flejes de 5 módulos × 3 niveles = 15 rollos + 6 en espera junto al desbobinador |
| AL-1H | Chapa en hojas | 17,8 | 17,8 | Cantiléver de 3 módulos × 5 niveles = 15 paquetes ≤ 2 t; un formato por módulo, FIFO |
| AL-1T | Caño Ø76,2 × 6 m | 12,6 | 12,6 | Cantiléver de 3 niveles × 4 atados = 12 atados |
| MQ-G | Corte de cuerpos (guillotina) | 70,1 | - |  |
| MQ-K | Cúpulas, fondos y cuellos | 59,2 | - |  |
| MQ-T | Corte de caño 1 kg (láser de tubo) | 75,6 | - |  |
| S1 | Celda 1 kg | 177,2 | - | Numerado, encastre de fondo y cúpula, soldadura circ., PH, secado y transportador a pintura |
| S2 | Línea 2,5-10 kg | 322,7 | - | Cilindrado, soldadura long., encastre, bordoneado, soldadura circ., PH, secado, granallado, detección y corrección |
| S-P | Pintura en polvo 1-10 kg (lazo) | 1.160,9 | - | Transportador aéreo por empuje en lazo: carga, pretratamiento, secado, cabina, polimerizado, enfriamiento y descarga |
| Q | Laboratorio de calidad | 42,2 | 36,2 | Rotura, expansión, potencial extintor; control de polvo y de soldadura |
| QR | Cuarentena y lotes retenidos | 31,7 | 15,0 | Jaula con llave: lotes rechazados y muestras |
| MT | Mantenimiento y pañol de herramientas | 44,8 | 30,0 | Banco, torno chico y repuestos |
| SUP | Supervisión de planta y PCP | 16,3 | - |  |
| EPP | EPP y botiquín | 16,3 | - |  |
| SP-1 | Sala de carga de polvo 1-10 kg | 64,0 | - | Recinto cerrado HR ≤ 70 %, 8 renovaciones por hora, sin estufas (IRAM 3517-2) |
| S-T | Terminación 1-10 kg | 96,8 | - | Ensamblaje, presurización con N₂, hermeticidad, etiquetado, embalaje y palletizado |
| AL-PV | Polvo químico en big bags | 102,2 | 23,1 | 21 posiciones a 2 alturas, HR ≤ 70 %, entra por P4 |
| AL-2 | Insumos de terminación y embalaje | 154,6 | 97,5 | Rack de 4 niveles: válvulas, manómetros, mangueras, etiquetas, cajas, film y pallets; entra por P5 |
| AL-3 | Almacén de producto terminado | 165,9 | - | Rack de 3 frentes × 4 niveles = 100 posiciones (req. 88) |
| EXP | Expedición y muelles | 88,1 | - | Consolidación de pedidos frente a M1-M2 (2 × 8 pallets) |
| S4 | Tercerizados revendidos | 42,6 | - | CO₂, agua, AFFF, clase K y agente limpio con sello IRAM: recepción, control y stock |
| BAT | Carga de baterías de autoelevadores | 22,1 | - | Local ventilado con lavaojos; estacionamiento de autoelevadores y tractor |
| S3 | Línea de carros 25-100 kg | 293,0 | - | Horquilla: cilindrado, punteo, soldadura long. (norte, O->E); soldadura circ., inspección, PH 4,0 MPa y marcado (centro, E->O) |
| AL-1C | Casquetes de carros | 8,3 | 8,0 | Rack de 3 niveles × 4 pallets = 12 posiciones, junto a la soldadura circunferencial |
| SP-2 | Sala de carga de polvo de carros | 68,8 | - | Recinto HR ≤ 70 %: big bags propios y cabina de descarga de muestras (IRAM 3550) |
| S-TC | Terminación de carros | 50,2 | - | Armado de ruedas y manguera, presurización y etiquetado |
| PTC | Carros terminados | 18,0 | 12,0 | 0,5 m² por carro a piso |

Los m² requeridos de MP (hoja MP Almacén) suponen almacenamiento a piso o en rack de 3 niveles con medio pasillo propio. En el layout la chapa, los flejes, el caño y los casquetes van en cantiléver y racks en altura, frente al pasillo de autoelevador AM que comparten, con las mismas posiciones: hojas 15 paquetes (3 módulos × 5 niveles), flejes 21 rollos + 6 en espera, caño 12 atados, casquetes 18 pallets.


## 3. Recepción de MP y análisis de peso de la carga

Se dimensiona para la carga máxima: un semirremolque de 18,6 m y 30 t en la playa norte bajo alero, y un chasis de 10 m en la bahía interior BR. En los dos puntos el camión se descarga por ambos lados con autoelevador (lateral de 4,5 a 6 m libres a cada lado). Hay dos puntos de ingreso de MP además de estos: P4/P5 (polvo e insumos de terminación, al norte, junto a su consumo) y P8 (polvo, estructuras y ruedas de carros, al este).

| Formato | Largo (m) | Carga útil (t) | PBT (t) | Descarga |
|---|---|---|---|---|
| Semirremolque playo 3+3 ejes | 18,6 | 30,0 | 45,0 | Playa norte techada (alero): autoelevador por los dos lados; entra al sector MP por P1b |
| Camión chasis con balancín (3 ejes) | 11,0 | 16,0 | 26,0 | Bahía interior BR (entra por P1): autoelevador por los dos lados, bajo techo |
| Camión chasis 2 ejes | 9,5 | 9,0 | 16,5 | Bahía interior BR, P4, P5, P3, P8 o M3 según el material |
| Utilitario / furgón | 6,0 | 1,5 | 3,5 | Portones de cada sector; recargas por RC-1 |

| Proveedor / material | t por entrega | Entregas/año | Vehículo | Portón | Destino |
|---|---|---|---|---|---|
| Pradecon: hojas + fleje 0,9 | 35,26 | 18,1 | Semi (máx.) o 2 chasis quincenales | P1b / P1 | AL-1H, AL-1F |
| Pacheco: flejes 1,25-2,0 | 5,05 | 29,3 | Chasis 2 ejes | P1b | AL-1F |
| Metalprisa: caño Ø76,2 | 4,23 | 28,9 | Chasis 2 ejes | P1 | AL-1T |
| Casquetes de carros | 5,93 | 4,1 | Chasis 2 ejes | P7 | AL-1C |
| Eli-Met: cuplas y asientos | 3,68 | 5,6 | Chasis 2 ejes | P1 | PÑ |
| Soldadura: alambre y consumibles | 1,89 | 8,1 | Chasis 2 ejes | P1 | PÑ |
| CYM: granalla | 3,11 | 2,0 | Chasis 2 ejes | P1 | PÑ |
| Air Liquide: gases | 7,64 | 31,3 | Chasis 2 ejes (baterías) | Jaulas JG-S y JG-N | Exterior |
| Polvo químico (Polvex / DEMSA) | 13,13 | 31,0 | Chasis con balancín | P4 (1-10 kg) y P8 (carros) | AL-PV, SP-2 |
| Válvulas y componentes | 8,16 | 8,3 | Chasis con balancín | P5 | AL-2 |
| Estructuras y ruedas de carros | 5,52 | 15,1 | Chasis 2 ejes | P8 | T14 |
| Pintura en polvo | 0,79 | 8,3 | Utilitario | P3 | QP |
| Químicos de pretratamiento | 0,46 | 1,8 | Utilitario | P3 | QP |
| Embalaje, pallets e imprenta | 4,61 | 15,3 | Chasis 2 ejes | P5 | AL-2 |
| Agentes para recargas | 2,87 | 8,2 | Chasis 2 ejes | RC-1 | RC |
| Tercerizados revendidos | 3,00 | 24,0 | Chasis 2 ejes (SUPUESTO) | M3 | S4 |

Pradecon entrega 35,3 t por mes (hojas + fleje 0,9): supera la carga útil de un semi. Se parte en 2 entregas quincenales de 17,6 t, que entran en un chasis con balancín y bajan el stock máximo de chapa medio mes.

Capacidad residual del autoelevador con un paquete de hoja de 1500 × 3000 mm y 2 t (Q = Qn · (cn + d) / (c + d), d = 0,45 m):

| Nominal (c = 500 mm) | Por el lado largo (c = 750 mm) | Por el lado corto (c = 1500 mm) |
|---|---|---|
| 2,5 t | 1,98 t | 1,22 t |
| 3,0 t | 2,38 t | 1,46 t |
| 3,5 t | 2,77 t | 1,71 t |

Se adopta autoelevador eléctrico de 3,0 t con horquillas de 1,8 m y posicionador: toma el paquete por el lado largo (2,37 t > 2 t). El de 2,5 t que proponía el Excel queda justo (1,98 t) y no sirve por el lado corto.

## 4. Anti-sobrestock de chapa SAE 1010

| Formato | Hojas/semana | Paquete de 2 t cubre (sem) | Paquete propuesto | Stock máx. (sem) |
|---|---|---|---|---|
| LAF 1,25 × 1220 × 2440 (2,5 kg) | 10,9 | 6,3 | 22 hojas (644 kg) | 4,0 |
| LAF 1,6 × 1000 × 2000 (5 kg) | 110,5 | 0,7 | 79 hojas (1.989 kg) | 1,4 |
| LAF 2,0 × 1500 × 3000 (10 kg) | 5,4 | 5,2 | 11 hojas (779 kg) | 4,1 |
| LAC 3,2 × 1500 × 3000 (25 y 50 kg) | 7,7 | 2,2 | 16 hojas (1.813 kg) | 4,1 |
| LAC 4,75 × 1500 × 3000 (70 y 100 kg) | 3,4 | 3,2 | 7 hojas (1.177 kg) | 4,1 |

Reglas: un módulo del cantiléver por formato con dos posiciones (en uso y en espera) y tope pintado; si están ocupadas no se emite pedido (kanban de 2 paquetes). Paquetes chicos en los formatos de bajo consumo para que ninguno cubra más de 2 semanas. Tarjeta de color por mes de ingreso y semáforo (verde < 4 semanas, amarillo 4 a 6, rojo > 6: se consume primero y se inspecciona óxido). Hoja LAF aceitada con film VCI, descargada y guardada siempre bajo techo, lejos de la PH y del lavado.

## 5. Pulmones y tren logístico

| Pulmón | Tasa (u/h) | Cobertura (h) | Unidades | Carros | Criterio |
|---|---|---|---|---|---|
| PU-G cuerpos 2,5-10 kg y carros | 33,0 | 8,00 | 264 | 6 | La guillotina corta por tandas de un formato: 1 turno de consumo |
| M17 cuerpos 1 kg (láser) | 79,0 | 0,50 | 40 | 2 | Un viaje del tren logístico + cambio de barra |
| SM-K cúpulas y fondos (pares) | 110,8 | 4,00 | 443 | 3 | Cambio de troquel de la prensa (≈ 30 min) cada medio turno |
| A00 kanban celda 1 kg | 79,0 | 0,50 | 40 | 2 | 2 carros: uno en uso y otro en reposición |
| B00 supermercado celda 2,5-10 kg | 31,8 | 1,00 | 32 | 2 | 2 carros por formato en curso |
| A08 y B11 a pintura | 110,8 | 0,75 | 83 | 2 | Parada de cambio de color / limpieza de cabina (≈ 45 min) sin detener las celdas |
| PU a terminación (tren de descarga) | 110,8 | 0,50 | 55 | 2 | Carga de polvo por lote |

Tren logístico (tractor eléctrico + 3 carros), recorrido de un solo sentido de 0 m: ciclo de 7,0 min con 7 paradas; admite 8,6 viajes/h y hacen falta 0,7 por capacidad: se programa cada 20 min (3 viajes/h) para que los kanban roten chicos. Es lo que permite que las dos celdas y el sector MP entreguen y retiren en el mismo pasillo sin que se crucen los flujos.

## 6. Cruces de flujos y de hilos

Cruces entre flujos de MP, SE y PT (verificación geométrica sobre el modelo): **0**. Cruces de hilos de personal con flujos: todos dentro de las **7** sendas peatonales señalizadas (SP-1 a SP-7).

## 7. Sanitarios, vestuarios y servicios (Dec. 351/79 arts. 49 y 50)

Turno más numeroso: 55 hombres (47 del turno mañana + 8 choferes) y 6 mujeres.

| Artefacto | H requerido | H proyectado | M requerido | M proyectado |
|---|---|---|---|---|
| inodoros | 3 | 5 | 1 | 3 |
| lavabos | 6 | 8 | 1 | 3 |
| orinales | 6 | 8 | 0 | 0 |
| duchas | 3 | 4 | 1 | 2 |

Armarios: H 56 requeridos / 62 proyectados; M 7 / 14 (vestuario de mujeres al 20 % de la dotación). Dos núcleos (principal y este) con sanitario accesible cada uno (Ley 24.314, Dec. 914/97: círculo libre de Ø 1,50 m, espacio lateral de 0,80 m, barras). Lactario como buena práctica (Ley 26.873). Espacio de cuidado no obligatorio (Dec. 144/2022 exige 100 o más personas; la dotación es 71). Comedor de 30 plazas en 2 tandas (DT Servicios).

| Local | m² |
|---|---|
| SV-VH Vestuario hombres (62 armarios) | 40,0 |
| SV-SH Sanitarios y duchas hombres | 25,9 |
| SV-LI Limpieza | 9,0 |
| SV-PS Paso a planta | 6,6 |
| SV-VM Vestuario y sanitarios mujeres (14 armarios) | 40,0 |
| SV-AC Sanitario accesible | 6,2 |
| SV-LA Lactario | 6,2 |
| SV-PA Primeros auxilios | 29,2 |
| SV-CO Pasillo | 33,5 |
| SV-HA Hall, recepción y fichado | 28,1 |
| SV-OF Oficinas (6 puestos) | 28,1 |
| SV-JP Jefatura de planta | 7,6 |
| SV-RE Reuniones | 6,8 |
| SV-CM Comedor 30 plazas y office | 39,4 |
| RC-MO Mostrador, recepción y clasificación | 32,5 |
| RC-DE Desarme | 33,1 |
| RC-DC Descarga y ensayo de funcionamiento | 34,2 |
| RC-PH PH con jaula, lavado y secado | 34,8 |
| RC-PV Recinto de polvo (HR ≤ 70 %) | 33,6 |
| RC-EN Ensamblaje, presurización y despacho | 33,1 |
| RC-GA CO₂ y agente limpio | 22,8 |
| RC-LQ Líquidos | 22,0 |
| RC-RP Retoque de pintura y etiquetado | 21,7 |
| RC-CO Pasillo de recargas | 39,4 |
| RC-FI Flota de intercambio | 70,2 |
| RC-IR Inutilizados y residuos | 36,0 |

## 8. Medios de escape (Dec. 351/79 anexo VII)

Factor de ocupación industrial 16 m²/persona: N = 300 personas teóricas; n = N/100 -> 3 unidades de ancho de salida (1,55 m mínimos). Proyectado: 10 salidas de emergencia de 1,10 m (11,00 m) con barral antipánico, más los portones con puerta de hombre y el paso a servicios.

Recorrido real máximo hasta una salida, calculado sobre una grilla de 0,5 m que rodea los equipos: **30,0 m** (punto x = 44,5, y = 24,5), por debajo de los 40 m que se toman como límite (verificar el artículo vigente).

## 9. Protección contra incendio

Extintores ABC de 10 kg en la nave: **24** (mínimo por superficie 1 cada 200 m² = 24), ubicados por cálculo para que ningún punto quede a más de 20 m de recorrido (IRAM 3517-2:2020, fuego clase A). Se suman 10 en anexos y exteriores, CO₂ junto a tableros y un carro de 50 kg ABC en pintura y en la sala de polvo. Señalización con chapa baliza y cartel en altura (IRAM 3517-2 cap. 7). La reserva de agua contra incendio y la red de hidrantes quedan previstas en el terreno y se confirman con el estudio de carga de fuego.

## 10. Iluminación (método de los lúmenes)

Luminaria LED de 150 W y 21.000 lm; factor de utilización 0,65; mantenimiento 0,80. Niveles: nave 300 lx, depósitos 150 lx, pintura 500 lx, laboratorio 750 lx; soldadura y montaje fino 500 lx y líquidos penetrantes 750 lx con iluminación localizada.

| Sector | lx | m² | Luminarias | kW |
|---|---|---|---|---|
| BR Bahía interior de descarga | 150 | 136 | 2 | 0,30 |
| SCR-O Scrap (orillas, esqueleto de fleje y recortes) | 300 | 34 | 1 | 0,15 |
| PÑ Pañol de insumos pesados | 150 | 41 | 1 | 0,15 |
| AL-1F Flejes | 150 | 18 | 1 | 0,15 |
| AL-1H Chapa en hojas | 150 | 18 | 1 | 0,15 |
| AL-1T Caño Ø76,2 × 6 m | 150 | 13 | 1 | 0,15 |
| MQ-G Corte de cuerpos (guillotina) | 300 | 70 | 2 | 0,30 |
| MQ-K Cúpulas, fondos y cuellos | 300 | 59 | 2 | 0,30 |
| MQ-T Corte de caño 1 kg (láser de tubo) | 300 | 76 | 3 | 0,45 |
| S1 Celda 1 kg | 300 | 177 | 5 | 0,75 |
| S2 Línea 2,5-10 kg | 300 | 323 | 9 | 1,35 |
| S-P Pintura en polvo 1-10 kg (lazo) | 500 | 1.161 | 54 | 8,10 |
| Q Laboratorio de calidad | 750 | 42 | 3 | 0,45 |
| QR Cuarentena y lotes retenidos | 750 | 32 | 3 | 0,45 |
| MT Mantenimiento y pañol de herramientas | 300 | 45 | 2 | 0,30 |
| SUP Supervisión de planta y PCP | 300 | 16 | 1 | 0,15 |
| EPP EPP y botiquín | 300 | 16 | 1 | 0,15 |
| SP-1 Sala de carga de polvo 1-10 kg | 300 | 64 | 2 | 0,30 |
| S-T Terminación 1-10 kg | 300 | 97 | 3 | 0,45 |
| AL-PV Polvo químico en big bags | 150 | 102 | 2 | 0,30 |
| AL-2 Insumos de terminación y embalaje | 150 | 155 | 3 | 0,45 |
| AL-3 Almacén de producto terminado | 150 | 166 | 3 | 0,45 |
| EXP Expedición y muelles | 150 | 88 | 2 | 0,30 |
| S4 Tercerizados revendidos | 150 | 43 | 1 | 0,15 |
| BAT Carga de baterías de autoelevadores | 300 | 22 | 1 | 0,15 |
| S3 Línea de carros 25-100 kg | 300 | 293 | 9 | 1,35 |
| AL-1C Casquetes de carros | 150 | 8 | 1 | 0,15 |
| SP-2 Sala de carga de polvo de carros | 300 | 69 | 2 | 0,30 |
| S-TC Terminación de carros | 300 | 50 | 2 | 0,30 |
| PTC Carros terminados | 150 | 18 | 1 | 0,15 |

Total: 124 luminarias, 18,6 kW.

## 11. Redes: longitud de tendidos (criterio 4)

| Tablero seccional | kW | Largo desde el TGBT (m) |
|---|---|---|
| BR | 0,1 | 45,1 |
| MQ-G | 17,2 | 36,4 |
| MQ-K | 65,0 | 25,0 |
| MQ-T | 20,0 | 22,0 |
| S2 | 72,1 | 24,0 |
| S1 | 28,0 | 3,8 |
| S-P | 33,0 | 73,5 |
| SP-1 | 9,0 | 55,8 |
| S-T | 2,5 | 47,6 |
| AL-3 | 1,5 | 39,6 |
| S3 | 69,5 | 41,1 |
| SP-2 | 5,0 | 59,5 |
| S-TC | 1,0 | 53,7 |

**Agua de PH y pretratamiento a PTE**: B07 81 m, A07 98 m, P02 66 m (total 244 m).

**Gas natural a hornos**: B14 52 m, A11 68 m, P03 8 m, P06 31 m (total 160 m).

**Nitrógeno**: T05 23 m, T13 34 m (total 57 m).

**Gas de soldadura**: M11 32 m, M12 34 m, B03 36 m, B06 27 m, A06 15 m, C04 46 m, C05 54 m (total 244 m).


Anillo de aire comprimido: 302 m. Potencia instalada de equipos: 324 kW.

## 12. Longitud de los flujos

| Tipo | Flujo | Largo (m) |
|---|---|---|
| MP | Chapa en hojas (chasis en bahía interior) | 31,9 |
| MP | Paquete a la mesa elevadora | 0,3 |
| MP | Hoja a la guillotina | 1,6 |
| MP | Caño en atados (semi en playa norte) | 11,0 |
| MP | Atado al cargador del láser | 0,2 |
| MP | Flejes (semi en playa norte) | 15,2 |
| MP | Rollo al desbobinador | 7,2 |
| MP | Insumos al pañol | 18,7 |
| MP | Casquetes (M3) | 16,5 |
| MP | Casquete a la soldadura circ. | 1,6 |
| MP | Polvo químico (big bags, P4) | 15,2 |
| MP | Big bag a la carga de polvo | 7,7 |
| MP | Válvulas, manómetros, etiquetas, cajas (P5) | 15,2 |
| MP | Insumos a ensamblaje y embalaje | 8,1 |
| MP | Químicos y pintura (QP) | 2,0 |
| MP | Desengrasante y fosfatizante al túnel | 15,1 |
| MP | Pintura en polvo a la cabina (P3b) | 11,2 |
| MP | Carros pintados y polvo de carros (P8) | 12,1 |
| MP | Tercerizados revendidos (M3) | 10,0 |
| SE | Cuerpo cortado | 0,3 |
| SE | Cuerpos al pulmón | 0,3 |
| SE | Cuerpos de carros a la cilindradora | 9,6 |
| SE | Fleje enderezado | 0,2 |
| SE | Fleje al troquel | 0,2 |
| SE | Cúpulas al cuello | 1,9 |
| SE | Cúpulas al cuello | 1,1 |
| SE | Cuello preparado | 0,6 |
| SE | Cuello preparado | 0,6 |
| SE | Cúpulas 1 kg al supermercado | 0,6 |
| SE | Cúpulas 2,5-10 kg al supermercado | 0,6 |
| SE | Fondos al supermercado | 7,2 |
| SE | Cuerpos 1 kg | 1,2 |
| SE | Cuerpos 1 kg | 1,2 |
| SE | Fondos 1 kg | 5,8 |
| SE | Cúpulas 1 kg | 7,2 |
| SE | Cúpulas y fondos 2,5-10 kg | 11,2 |
| SE | Línea 2,5-10 kg -> granallado -> pintura | 49,6 |
| SE | Reproceso: corrección -> nueva PH | 22,0 |
| SE | Celda 1 kg -> pintura (sin granallado) | 48,4 |
| SE | Lazo de pintura: pretratamiento, secado, cabina, polimerizado, enfriamiento | 81,9 |
| RET | Retorno de ganchos vacíos (aéreo, +4,0 m) | 13,0 |
| SE | Pintados a carga de polvo | 3,0 |
| SE | Ensamblaje -> presurización -> hermeticidad -> etiquetado -> embalaje | 12,4 |
| SE | Línea de carros: cilindrado, punteo, soldaduras, inspección, PH y marcado | 33,1 |
| SE | Carros a pintura tercerizada (P6) | 16,2 |
| SE | Carga de polvo -> armado -> presurización | 6,0 |
| PT | Pallet a envolvedora | 0,8 |
| PT | Pallet a envolvedora | 1,6 |
| PT | Almacén de PT | 8,0 |
| PT | Almacén de PT | 0,1 |
| PT | Expedición M1 | 23,6 |
| PT | Expedición M2 | 24,1 |
| PT | Carros terminados (P9) | 12,6 |
| PT | Tercerizados a expedición | 2,8 |
| SCRAP | Scrap (P2) | 7,0 |

## 13. Supuestos a validar

- Tercerizados revendidos: volumen estimado (no figura en los Excel).
- Retiros, FOS y FOT del parque industrial; ubicación de la celda de media tensión y de la reducción de gas.
- Medidas de equipos marcados E (estimados): confirmar con los proveedores.
- Textos normativos marcados como B en el README (Dec. 351/79 arts. 49, 50 y anexo VII; Res. SRT 960/2015): verificar la versión vigente en InfoLEG.
- Recargas se incluye porque figura en el dimensionamiento técnico, aunque no estaba en la lista de secciones del pedido.
