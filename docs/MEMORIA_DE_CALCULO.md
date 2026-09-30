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

Nave de 120 × 36 m = 4.320 m², pórticos de 36 m de luz cada 8 m, altura libre 8,00 m (Dec. 351/79 exige ≥ 3 m). Anexos: servicios 364 m², recargas 476 m², sala técnica 72 m².

| Código | Sector | m² proyectados | m² requeridos | Nota |
|---|---|---|---|---|
| BR | Bahía interior de descarga | 143,9 | - | Chasis de hasta 10 m entra por P1 y se descarga por los dos lados con autoelevador |
| AL-1H | Chapa en hojas | 17,8 | 50,0 | Cantiléver de 3 módulos × 5 niveles = 15 paquetes ≤ 2 t; un formato por módulo, FIFO |
| AL-1F | Flejes | 13,7 | 43,2 | Porta-flejes de 7 módulos × 3 niveles = 21 rollos + 6 en espera junto al desbobinador |
| AL-1T | Caño Ø76,2 × 6 m | 11,2 | 30,8 | Cantiléver de 7 m, 3 niveles × 4 atados = 12 atados |
| AL-1C | Casquetes de carros | 8,4 | 20,0 | Rack de 3 niveles × 6 pallets = 18 posiciones, junto a la soldadura circunferencial |
| PÑ | Pañol de insumos pesados | 51,5 | 35,2 | Alambre MIG, granalla, asientos de válvula y cuplas, tapones, consumibles |
| SCR-O | Scrap oeste (orillas de hoja) | 48,4 | - | Contenedores basculantes de 1 m³; salen por P2 al volquete del patio oeste |
| SCR-N | Scrap norte (esqueleto de fleje) | 12,5 | - | Contenedores basculantes; salen por P2b al volquete del patio norte |
| MQ-G | Corte de cuerpos (guillotina) | 49,7 | - |  |
| MQ-T | Corte de caño 1 kg | 33,4 | - |  |
| MQ-K | Cúpulas, fondos y cuellos | 45,4 | - |  |
| SM-K | Supermercado de cúpulas y fondos | 18,6 | - |  |
| PU-G | Pulmón de cuerpos cortados | 25,5 | - |  |
| OP-MP | Control de recepción y puestos del sector MP | 117,9 | - | Mesa de control (certificado, espesor, colada), franjas en proceso y retal aprovechable |
| S3 | Línea de carros 25-100 kg | 257,0 | - | Flujo este-oeste: cilindrado, armado, soldaduras, inspección, PH 4,0 MPa y marcado |
| S1 | Celda 1 kg | 220,0 | - |  |
| S2 | Celda 2,5-10 kg | 232,5 | - |  |
| Q | Laboratorio de calidad | 37,1 | 36,2 | Rotura, expansión, potencial extintor; control de polvo y de soldadura |
| QR | Cuarentena y lotes retenidos | 15,6 | 15,0 | Jaula con llave: lotes rechazados y muestras |
| EPP | EPP y botiquín | 7,5 | - |  |
| MT | Mantenimiento y pañol de herramientas | 37,1 | 30,0 | Banco, torno chico y repuestos |
| SUP | Supervisión de planta | 18,0 | - | Encargado de turno y PCP |
| S-P | Pintura en polvo 1-10 kg | 466,2 | - | Transporte aéreo por empuje: pretratamiento, secado, cabina y polimerizado |
| QP | Químicos y pintura en polvo | 24,4 | 24,1 | Batea ≥ 110 % del mayor envase; pintura en polvo < 30 °C |
| AL-PV | Polvo químico en big bags | 37,1 | 23,1 | 21 posiciones a 2 alturas, HR ≤ 70 %, entra por P4 |
| AL-2 | Insumos de terminación y embalaje | 59,9 | 97,5 | Rack de 4 niveles: válvulas, manómetros, mangueras, etiquetas, cajas, film y pallets; entra por P5 |
| SP-1 | Sala de carga de polvo 1-10 kg | 56,0 | - | Recinto cerrado HR ≤ 70 %, 8 renovaciones por hora, sin estufas (IRAM 3517-2) |
| S-T | Terminación 1-10 kg | 90,4 | - | Ensamblaje, presurización con N₂, hermeticidad, etiquetado, embalaje y palletizado |
| BAT | Carga de baterías de autoelevadores | 46,8 | - | Local ventilado con lavaojos; estacionamiento de autoelevadores y tractor del tren logístico |
| EST | Estacionamiento de transpaletas y carros | 49,9 | - |  |
| OF-E | Oficina de expedición | 49,9 | - |  |
| SP-2 | Sala de carga de polvo de carros | 57,9 | - | Recinto HR ≤ 70 %: big bags propios y cabina de descarga de muestras (IRAM 3550) |
| S-TC | Terminación de carros | 64,9 | - | Armado de ruedas y manguera, presurización y etiquetado |
| PTC | Carros terminados | 85,2 | 25,0 | 0,5 m² por carro a piso |
| AL-3 | Almacén de producto terminado | 205,7 | - | Rack de 2 frentes × 6 módulos × 2 pallets × 4 niveles = 96 posiciones (req. 88) |
| EXP | Expedición y muelles | 84,2 | - | Consolidación de pedidos frente a M1-M2 (2 × 8 pallets) |
| S4 | Tercerizados revendidos | 38,4 | - | CO₂, agua, AFFF, clase K y agente limpio con sello IRAM: recepción, control y stock |

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

Tren logístico (tractor eléctrico + 3 carros), recorrido de un solo sentido de 110 m: ciclo de 8,8 min con 7 paradas; admite 6,8 viajes/h y hacen falta 0,7 por capacidad: se programa cada 20 min (3 viajes/h) para que los kanban roten chicos. Es lo que permite que las dos celdas y el sector MP entreguen y retiren en el mismo pasillo sin que se crucen los flujos.

## 6. Cruces de flujos y de hilos

Cruces entre flujos de MP, SE y PT (verificación geométrica sobre el modelo): **0**. Cruces de hilos de personal con flujos: **2**, los dos en sendas señalizadas (SP-1 y SP-2) sobre el colector del tren logístico, que usa el personal del sector MP.

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
| SV-VH Vestuario hombres (62 armarios) | 32,4 |
| SV-SH Sanitarios y duchas hombres | 31,3 |
| SV-PS Paso a planta | 10,8 |
| SV-VM Vestuario y sanitarios mujeres (14 armarios) | 28,1 |
| SV-AC Sanitario accesible | 6,2 |
| SV-LA Lactario | 6,2 |
| SV-PA Primeros auxilios | 18,4 |
| SV-LI Limpieza | 8,6 |
| SV-CO Pasillo | 44,2 |
| SV-HA Hall, recepción y fichado | 26,0 |
| SV-OF Oficinas (6 puestos) | 41,6 |
| SV-JP Jefatura de planta | 9,9 |
| SV-RE Reuniones | 9,9 |
| SV-CM Comedor 30 plazas y office | 52,0 |
| RC-NS Núcleo sanitario este | 32,5 |
| RC-MO Mostrador, recepción y clasificación | 39,5 |
| RC-DE Desarme | 35,4 |
| RC-DC Descarga y ensayo de funcionamiento | 35,4 |
| RC-IR Inutilizados y residuos | 30,2 |
| RC-PH PH con jaula, lavado y secado | 31,3 |
| RC-PV Recinto de polvo (HR ≤ 70 %) | 33,5 |
| RC-GA CO₂ y agente limpio | 20,5 |
| RC-LQ Líquidos | 18,4 |
| RC-EN Ensamblaje, presurización, peso y hermeticidad | 41,0 |
| RC-FI Flota de intercambio | 43,7 |
| RC-RP Retoque de pintura y etiquetado | 38,1 |
| RC-DP Despacho y equipos para entregar | 37,0 |

## 8. Medios de escape (Dec. 351/79 anexo VII)

Factor de ocupación industrial 16 m²/persona: N = 270 personas teóricas; n = N/100 -> 3 unidades de ancho de salida (1,55 m mínimos). Proyectado: 10 salidas de emergencia de 1,10 m (11,00 m) con barral antipánico, más los portones con puerta de hombre y el paso a servicios.

Recorrido real máximo hasta una salida, calculado sobre una grilla de 0,5 m que rodea los equipos: **26,9 m** (punto x = 20,0, y = 25,0), por debajo de los 40 m que se toman como límite (verificar el artículo vigente).

## 9. Protección contra incendio

Extintores ABC de 10 kg en la nave: **22** (mínimo por superficie 1 cada 200 m² = 22), ubicados por cálculo para que ningún punto quede a más de 20 m de recorrido (IRAM 3517-2:2020, fuego clase A). Se suman 10 en anexos y exteriores, CO₂ junto a tableros y un carro de 50 kg ABC en pintura y en la sala de polvo. Señalización con chapa baliza y cartel en altura (IRAM 3517-2 cap. 7). La reserva de agua contra incendio y la red de hidrantes quedan previstas en el terreno y se confirman con el estudio de carga de fuego.

## 10. Iluminación (método de los lúmenes)

Luminaria LED de 150 W y 21.000 lm; factor de utilización 0,65; mantenimiento 0,80. Niveles: nave 300 lx, depósitos 150 lx, pintura 500 lx, laboratorio 750 lx; soldadura y montaje fino 500 lx y líquidos penetrantes 750 lx con iluminación localizada.

| Sector | lx | m² | Luminarias | kW |
|---|---|---|---|---|
| BR Bahía interior de descarga | 150 | 144 | 2 | 0,30 |
| AL-1H Chapa en hojas | 150 | 18 | 1 | 0,15 |
| AL-1F Flejes | 150 | 14 | 1 | 0,15 |
| AL-1T Caño Ø76,2 × 6 m | 150 | 11 | 1 | 0,15 |
| AL-1C Casquetes de carros | 150 | 8 | 1 | 0,15 |
| PÑ Pañol de insumos pesados | 150 | 51 | 1 | 0,15 |
| SCR-O Scrap oeste (orillas de hoja) | 300 | 48 | 2 | 0,30 |
| SCR-N Scrap norte (esqueleto de fleje) | 300 | 12 | 1 | 0,15 |
| MQ-G Corte de cuerpos (guillotina) | 300 | 50 | 2 | 0,30 |
| MQ-T Corte de caño 1 kg | 300 | 33 | 1 | 0,15 |
| MQ-K Cúpulas, fondos y cuellos | 300 | 45 | 2 | 0,30 |
| SM-K Supermercado de cúpulas y fondos | 300 | 19 | 1 | 0,15 |
| PU-G Pulmón de cuerpos cortados | 300 | 25 | 1 | 0,15 |
| OP-MP Control de recepción y puestos del sector MP | 300 | 118 | 4 | 0,60 |
| S3 Línea de carros 25-100 kg | 300 | 257 | 8 | 1,20 |
| S1 Celda 1 kg | 300 | 220 | 7 | 1,05 |
| S2 Celda 2,5-10 kg | 300 | 232 | 7 | 1,05 |
| Q Laboratorio de calidad | 750 | 37 | 3 | 0,45 |
| QR Cuarentena y lotes retenidos | 750 | 16 | 2 | 0,30 |
| EPP EPP y botiquín | 300 | 7 | 1 | 0,15 |
| MT Mantenimiento y pañol de herramientas | 300 | 37 | 2 | 0,30 |
| SUP Supervisión de planta | 300 | 18 | 1 | 0,15 |
| S-P Pintura en polvo 1-10 kg | 500 | 466 | 22 | 3,30 |
| QP Químicos y pintura en polvo | 150 | 24 | 1 | 0,15 |
| AL-PV Polvo químico en big bags | 150 | 37 | 1 | 0,15 |
| AL-2 Insumos de terminación y embalaje | 150 | 60 | 1 | 0,15 |
| SP-1 Sala de carga de polvo 1-10 kg | 300 | 56 | 2 | 0,30 |
| S-T Terminación 1-10 kg | 300 | 90 | 3 | 0,45 |
| BAT Carga de baterías de autoelevadores | 300 | 47 | 2 | 0,30 |
| EST Estacionamiento de transpaletas y carros | 300 | 50 | 2 | 0,30 |
| OF-E Oficina de expedición | 300 | 50 | 2 | 0,30 |
| SP-2 Sala de carga de polvo de carros | 300 | 58 | 2 | 0,30 |
| S-TC Terminación de carros | 300 | 65 | 2 | 0,30 |
| PTC Carros terminados | 150 | 85 | 2 | 0,30 |
| AL-3 Almacén de producto terminado | 150 | 206 | 3 | 0,45 |
| EXP Expedición y muelles | 150 | 84 | 2 | 0,30 |
| S4 Tercerizados revendidos | 150 | 38 | 1 | 0,15 |

Total: 100 luminarias, 15,0 kW.

## 11. Redes: longitud de tendidos (criterio 4)

| Tablero seccional | kW | Largo desde el TGBT (m) |
|---|---|---|
| BR | 0,1 | 57,5 |
| MQ-G | 17,2 | 57,1 |
| MQ-T | 20,0 | 51,8 |
| MQ-K | 65,0 | 41,1 |
| S3 | 69,5 | 66,9 |
| S1 | 21,5 | 27,3 |
| S2 | 66,1 | 20,5 |
| S-P | 33,0 | 42,0 |
| SP-1 | 9,0 | 41,7 |
| S-T | 2,5 | 48,8 |
| AL-3 | 1,5 | 55,3 |
| SP-2 | 5,0 | 59,2 |
| S-TC | 1,0 | 69,0 |

**Agua de PH y pretratamiento a PTE**: A07 56 m, B07 44 m, P02 41 m (total 141 m).

**Gas natural a hornos**: P03 37 m, P06 26 m (total 64 m).

**Nitrógeno**: T05 21 m, T13 39 m (total 61 m).

**Gas de soldadura**: M11 22 m, M12 24 m, C04 53 m, C05 57 m, A06 30 m, B03 27 m, B06 34 m (total 247 m).


Anillo de aire comprimido: 292 m. Potencia instalada de equipos: 311 kW.

## 12. Longitud de los flujos

| Tipo | Flujo | Largo (m) |
|---|---|---|
| MP | Chapa en hojas (chasis en bahía interior) | 30,9 |
| MP | Paquete a la mesa elevadora | 4,0 |
| MP | Caño en atados (chasis) | 29,7 |
| MP | Barra al láser | 0,8 |
| MP | Flejes (semi en playa norte) | 19,1 |
| MP | Rollo al desbobinador | 3,7 |
| MP | Insumos al pañol | 20,8 |
| MP | Casquetes (P7) | 23,1 |
| MP | Casquete a la soldadura circ. | 2,3 |
| MP | Polvo químico (big bags) | 16,1 |
| MP | Válvulas, manómetros, etiquetas, cajas | 18,3 |
| MP | Químicos y pintura en polvo | 12,5 |
| MP | Desengrasante y fosfatizante al túnel | 14,5 |
| MP | Pintura en polvo a la cabina | 19,2 |
| MP | Estructuras y ruedas de carros (P8) | 26,3 |
| MP | Polvo de carros (P8) | 36,8 |
| MP | Tercerizados revendidos (M3) | 12,0 |
| SE | Cuerpos cortados al pulmón | 8,2 |
| SE | Cuerpos de carros a la cilindradora | 7,9 |
| SE | Línea de carros -> pintura tercerizada (P6) | 38,9 |
| SE | Cuerpos 2,5-10 kg al tren logístico | 1,2 |
| SE | Cuerpo 1 kg | 0,1 |
| SE | Cuerpo 1 kg | 0,1 |
| SE | Cuerpos 1 kg al tren logístico | 14,8 |
| SE | Discos -> cúpulas y fondos -> cuellos | 11,9 |
| SE | Cúpulas y fondos al tren logístico | 1,2 |
| TL | Tren logístico (tractor eléctrico + 3 carros), un solo sentido | 74,8 |
| RET | Retorno vacío | 34,8 |
| SE | Entrega a la celda 1 kg | 1,2 |
| SE | Celda 1 kg | 38,1 |
| SE | 1 kg al tren logístico | 1,1 |
| SE | Entrega a la celda 2,5-10 kg | 1,1 |
| SE | Celda 2,5-10 kg | 38,1 |
| SE | 2,5-10 kg al tren logístico | 1,1 |
| SE | Entrega al tren de carga de pintura | 1,2 |
| SE | Pintura: pretratamiento, secado, cabina, polimerizado, enfriamiento | 51,6 |
| SE | Pintados a carga de polvo | 4,6 |
| SE | Carga -> ensamblaje | 2,1 |
| SE | Carga -> ensamblaje | 1,2 |
| SE | Ensamblaje -> presurización -> hermeticidad -> etiquetado | 7,8 |
| SE | A embalaje | 1,2 |
| SE | Cilindros vendidos a palletizado | 3,2 |
| SE | Carros pintados (P8) | 39,0 |
| SE | Carga de polvo -> armado -> presurización | 12,2 |
| PT | Pallet a envolvedora | 0,6 |
| PT | Pallet a envolvedora | 1,9 |
| PT | Pallet de cilindros a envolvedora | 0,6 |
| PT | Almacén de PT | 5,5 |
| PT | Expedición M1 | 14,3 |
| PT | Expedición M2 | 14,3 |
| PT | Carros terminados (P9) | 27,8 |
| PT | Tercerizados a expedición | 6,6 |
| SCRAP | Orillas de hoja | 17,8 |
| SCRAP | Scrap oeste (P2) | 12,5 |
| SCRAP | Esqueleto de fleje | 6,7 |
| SCRAP | Scrap norte (P2b) | 5,3 |

## 13. Supuestos a validar

- Tercerizados revendidos: volumen estimado (no figura en los Excel).
- Retiros, FOS y FOT del parque industrial; ubicación de la celda de media tensión y de la reducción de gas.
- Medidas de equipos marcados E (estimados): confirmar con los proveedores.
- Textos normativos marcados como B en el README (Dec. 351/79 arts. 49, 50 y anexo VII; Res. SRT 960/2015): verificar la versión vigente en InfoLEG.
- Recargas se incluye porque figura en el dimensionamiento técnico, aunque no estaba en la lista de secciones del pedido.
