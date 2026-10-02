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

Nave de 88 × 44 m = 3.872 m², recorrido en U con una línea que converge paso a paso, pórticos de dos luces (19,40 y 24,60 m) cada 8 m, altura libre 8,00 m (Dec. 351/79 exige ≥ 3 m). Recargas dentro de la nave (ángulo SO, 327 m²). Anexos: servicios 338 m² y sala técnica 58 m².

| Código | Sector | m² proyectados | m² requeridos | Nota |
|---|---|---|---|---|
| AL-1H | Chapa en paquetes (reserva) | 58,9 | 50,0 | 8 posiciones de 1,6 × 3,1 m a 2 alturas = 16 paquetes ≤ 2 t; FIFO, semáforo de antigüedad |
| PÑ | Pañol de insumos pesados | 62,7 | 35,2 | Alambre MIG, granalla, cuplas, tapones y consumibles |
| SCR | Scrap: orillas, despuntes y esqueleto de fleje | 52,2 | - | Contenedores basculantes; salen por P2 al volquete del patio norte |
| AL-1R | Racks frente a máquina: chapa, caño y flejes | 48,6 | - | Chapa en uso (frente a la guillotina), caño 6 m (frente a los láseres), flejes (frente a la prensa) |
| N1 | Corte y cuerpo 2,5-10 kg | 103,4 | - | 1 guillotina -> 2 numerado -> 3 cilindrado -> 4 soldadura longitudinal |
| N2 | Corte de caño 1 kg | 65,5 | - | 5 corte láser de caño |
| N3 | Cúpulas, fondos y cuellos | 110,9 | - | 6 desbobinado + embutido -> 7 preparación de cuello -> 8 soldadura de cuello |
| N4 | Unión y prueba hidráulica | 128,0 | - | 9 encastre -> 10 bordoneado -> 11 soldadura circ. -> 12 PH -> 13 secado |
| N5 | Granallado y defectos | 83,5 | - | 14 granallado -> 15 detección de defectos -> 16 corrección |
| Q | Laboratorio de calidad | 34,0 | 31,0 | Rotura, expansión, potencial extintor; probetas de soldadura (IRAM 3523 / 3550) |
| QR | Cuarentena y lotes retenidos | 18,4 | 15,0 | Jaula con llave: lotes rechazados y muestras |
| SUP | Supervisión de planta y PCP | 19,3 | - |  |
| EPP | EPP y botiquín | 19,3 | - |  |
| MT | Mantenimiento y pañol de herramientas | 36,8 | 30,0 | Banco, torno chico, soldadora y repuestos |
| PV | Carros vacíos y retorno de pulmones | 79,0 | - | Estacionamiento de carros de pulmón vacíos sobre la calle PO-2 |
| RES | Reserva para ampliación de la línea | 91,6 | - | Lugar para una 3ª PH / 2ª granalladora si crece la demanda |
| S-P | Pintura en polvo (lazo) | 421,7 | - | 17 carga -> pretratamiento -> secado -> cabina -> polimerizado -> enfriamiento -> descarga |
| QP | Químicos y pintura en polvo | 44,9 | 24,1 | Batea ≥ 110 % del mayor envase; pintura en polvo < 30 °C; portón P3 |
| ST-I | Tableros, compresor de pintura y colector | 39,6 | - |  |
| AL-C | Almacén de cilindros pintados | 125,4 | - | Cilindros vendidos vacíos y pulmón de pintados antes de terminación |
| SP-1 | Sala de carga de polvo | 92,8 | - | Recinto HR ≤ 70 %, 8 renovaciones por hora, sin estufas (IRAM 3517-2); big bags a 2 alturas |
| S-T | Terminación 1-10 kg | 119,5 | - | 18 carga de polvo -> 19 ensamblaje -> 20 presurización -> 21 hermeticidad -> 22 etiquetado -> 23 embalaje -> 24 envolvedora |
| AL-2 | Insumos de terminación y embalaje | 17,7 | 40,0 | Rack de 4 niveles a lo largo del muro sur; entra por P5 |
| AL-3 | Almacén de producto terminado | 189,6 | - | 4 racks de 12 m × 4 niveles = 128 posiciones (req. 88) |
| EXP | Expedición y muelles | 59,2 | - | Consolidación de pedidos frente a M1-M2 |
| S4 | Tercerizados revendidos | 16,4 | - | CO₂, agua, AFFF, clase K y agente limpio con sello IRAM: recepción por M3, control y stock |
| S3 | Línea de carros 25-100 kg | 170,6 | - | C1 cilindrado -> C2 punteo -> C3 soldadura long. -> C4 soldadura circ. -> C5 inspección -> C6 PH -> C7 marcado |
| SP-2 | Sala de carga de polvo de carros | 45,0 | - | Recinto HR ≤ 70 %: big bags propios y cabina de descarga de muestras (IRAM 3550) |
| S-TC | Terminación de carros | 40,5 | - | C9 armado de ruedas y manguera -> C10 presurización y etiquetado |
| PU-CP | Carros a pintura tercerizada | 30,0 | - | Espera de retiro del pintor (P6); vuelven pintados por P8 |

Los m² requeridos de MP (hoja MP Almacén) suponen almacenamiento a piso o en rack de 3 niveles con medio pasillo propio. En el layout la chapa, los flejes, el caño y los casquetes van en cantiléver y racks en altura, frente al pasillo de autoelevador AM que comparten, con las mismas posiciones: hojas 15 paquetes (3 módulos × 5 niveles), flejes 21 rollos + 6 en espera, caño 12 atados, casquetes 18 pallets.


## 3. Recepción de MP y análisis de peso de la carga

Se dimensiona para la carga máxima: un semirremolque de 18,6 m y 30 t o dos chasis de 10 m en el alero de descarga norte (23 × 10,6 m), con descarga por ambos lados con autoelevador. La MP entra por P1 al pasillo AM y queda en racks frente a la máquina que la consume (chapa frente a la guillotina, caño frente a los láseres, flejes frente a la prensa). Otros ingresos, junto a su consumo: P4 y P5 al sur (polvo e insumos de terminación), P3 al este (químicos y pintura), M3 (casquetes y tercerizados) y P8 (polvo, estructuras y ruedas de carros).

| Formato | Largo (m) | Carga útil (t) | PBT (t) | Descarga |
|---|---|---|---|---|
| Semirremolque playo 3+3 ejes | 18,6 | 30,0 | 45,0 | Alero de descarga norte: autoelevador por los dos lados; entra al almacén de MP por P1 |
| Camión chasis con balancín (3 ejes) | 11,0 | 16,0 | 26,0 | Alero de descarga norte (junto al semi): autoelevador por los dos lados, bajo techo |
| Camión chasis 2 ejes | 9,5 | 9,0 | 16,5 | Alero norte, P4, P5, P3, P8 o M3 según el material |
| Utilitario / furgón | 6,0 | 1,5 | 3,5 | Portones de cada sector; recargas por RC-1 |

| Proveedor / material | t por entrega | Entregas/año | Vehículo | Portón | Destino |
|---|---|---|---|---|---|
| Pradecon: hojas + fleje 0,9 | 35,26 | 18,1 | Semi (máx.) o 2 chasis quincenales | Alero + P1 | AL-1H, AL-1R |
| Pacheco: flejes 1,25-2,0 | 5,05 | 29,3 | Chasis 2 ejes | Alero + P1 | AL-1R |
| Metalprisa: caño Ø76,2 | 4,23 | 28,9 | Chasis 2 ejes | Alero + P1 | AL-1R |
| Casquetes de carros | 5,93 | 4,1 | Chasis 2 ejes | M3 | AL1C |
| Eli-Met: cuplas y asientos | 3,68 | 5,6 | Chasis 2 ejes | Alero + P1 | PÑ |
| Soldadura: alambre y consumibles | 1,89 | 8,1 | Chasis 2 ejes | Alero + P1 | PÑ |
| CYM: granalla | 3,11 | 2,0 | Chasis 2 ejes | Alero + P1 | PÑ |
| Air Liquide: gases | 7,64 | 31,3 | Chasis 2 ejes (baterías) | Jaulas JG-S y JG-N | Exterior |
| Polvo químico (Polvex / DEMSA) | 13,13 | 31,0 | Chasis con balancín | P4 (1-10 kg) y P8 (carros) | SP-1, SP-2 |
| Válvulas y componentes | 8,16 | 8,3 | Chasis con balancín | P5 | AL-2 |
| Estructuras y ruedas de carros | 5,52 | 15,1 | Chasis 2 ejes | P8 | S-TC |
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

Cruces entre flujos de MP, SE y PT (verificación geométrica sobre el modelo): **0**. Cruces de hilos de personal con flujos: todos dentro de las **16** sendas peatonales señalizadas (SP-1 a SP-16).

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
| RC-RE Recepción, clasificación y recibidos | 26,0 |
| RC-DE Desarme y lavado | 28,4 |
| RC-DC Descarga y ensayo de funcionamiento | 28,4 |
| RC-C1 Corredor de recargas (sur) | 24,2 |
| RC-GA CO₂ y agente limpio | 16,3 |
| RC-PV Recinto de polvo (HR ≤ 70 %) | 32,6 |
| RC-PH PH con jaula, secado y Puffer | 18,5 |
| RC-C2 Corredor de recargas (centro) | 22,0 |
| RC-CN Conector al pasillo central | 18,5 |
| RC-IR Inutilizados y residuos | 8,9 |
| RC-DP Despacho y equipos para entregar | 9,6 |
| RC-EN Ensamblaje, presurización, peso, hermeticidad y retoque | 38,5 |
| RC-LQ Líquidos | 10,1 |
| RC-RP Etiquetado y flota de intercambio | 10,9 |

## 8. Medios de escape (Dec. 351/79 anexo VII)

Factor de ocupación industrial 16 m²/persona: N = 242 personas teóricas; n = N/100 -> 3 unidades de ancho de salida (1,55 m mínimos). Proyectado: 9 salidas de emergencia de 1,10 m (9,90 m) con barral antipánico, más los portones con puerta de hombre y el paso a servicios.

Recorrido real máximo hasta una salida, calculado sobre una grilla de 0,5 m que rodea los equipos: **26,3 m** (punto x = 16,5, y = 29,0), por debajo de los 40 m que se toman como límite (verificar el artículo vigente).

## 9. Protección contra incendio

Extintores ABC de 10 kg en la nave: **20** (mínimo por superficie 1 cada 200 m² = 20), ubicados por cálculo para que ningún punto quede a más de 20 m de recorrido (IRAM 3517-2:2020, fuego clase A). Se suman 10 en anexos y exteriores, CO₂ junto a tableros y un carro de 50 kg ABC en pintura y en la sala de polvo. Señalización con chapa baliza y cartel en altura (IRAM 3517-2 cap. 7). La reserva de agua contra incendio y la red de hidrantes quedan previstas en el terreno y se confirman con el estudio de carga de fuego.

## 10. Iluminación (método de los lúmenes)

Luminaria LED de 150 W y 21.000 lm; factor de utilización 0,65; mantenimiento 0,80. Niveles: nave 300 lx, depósitos 150 lx, pintura 500 lx, laboratorio 750 lx; soldadura y montaje fino 500 lx y líquidos penetrantes 750 lx con iluminación localizada.

| Sector | lx | m² | Luminarias | kW |
|---|---|---|---|---|
| AL-1H Chapa en paquetes (reserva) | 150 | 59 | 1 | 0,15 |
| PÑ Pañol de insumos pesados | 150 | 63 | 1 | 0,15 |
| SCR Scrap: orillas, despuntes y esqueleto de fleje | 300 | 52 | 2 | 0,30 |
| AL-1R Racks frente a máquina: chapa, caño y flejes | 150 | 49 | 1 | 0,15 |
| N1 Corte y cuerpo 2,5-10 kg | 300 | 103 | 3 | 0,45 |
| N2 Corte de caño 1 kg | 300 | 66 | 2 | 0,30 |
| N3 Cúpulas, fondos y cuellos | 300 | 111 | 4 | 0,60 |
| N4 Unión y prueba hidráulica | 300 | 128 | 4 | 0,60 |
| N5 Granallado y defectos | 300 | 84 | 3 | 0,45 |
| Q Laboratorio de calidad | 750 | 34 | 3 | 0,45 |
| QR Cuarentena y lotes retenidos | 750 | 18 | 2 | 0,30 |
| SUP Supervisión de planta y PCP | 300 | 19 | 1 | 0,15 |
| EPP EPP y botiquín | 300 | 19 | 1 | 0,15 |
| MT Mantenimiento y pañol de herramientas | 300 | 37 | 2 | 0,30 |
| PV Carros vacíos y retorno de pulmones | 300 | 79 | 3 | 0,45 |
| RES Reserva para ampliación de la línea | 300 | 92 | 3 | 0,45 |
| S-P Pintura en polvo (lazo) | 500 | 422 | 20 | 3,00 |
| QP Químicos y pintura en polvo | 150 | 45 | 1 | 0,15 |
| ST-I Tableros, compresor de pintura y colector | 300 | 40 | 2 | 0,30 |
| AL-C Almacén de cilindros pintados | 150 | 125 | 2 | 0,30 |
| SP-1 Sala de carga de polvo | 300 | 93 | 3 | 0,45 |
| S-T Terminación 1-10 kg | 300 | 119 | 4 | 0,60 |
| AL-2 Insumos de terminación y embalaje | 150 | 18 | 1 | 0,15 |
| AL-3 Almacén de producto terminado | 150 | 190 | 3 | 0,45 |
| EXP Expedición y muelles | 150 | 59 | 1 | 0,15 |
| S4 Tercerizados revendidos | 150 | 16 | 1 | 0,15 |
| S3 Línea de carros 25-100 kg | 300 | 171 | 5 | 0,75 |
| SP-2 Sala de carga de polvo de carros | 300 | 45 | 2 | 0,30 |
| S-TC Terminación de carros | 300 | 40 | 2 | 0,30 |
| PU-CP Carros a pintura tercerizada | 300 | 30 | 1 | 0,15 |

Total: 84 luminarias, 12,6 kW.

## 11. Redes: longitud de tendidos (criterio 4)

| Tablero seccional | kW | Largo desde el TGBT (m) |
|---|---|---|
| N1 | 31,3 | 30,2 |
| N2 | 20,0 | 31,0 |
| N3 | 65,0 | 24,2 |
| N4 | 54,5 | 16,4 |
| N5 | 31,0 | 42,1 |
| S-P | 33,0 | 75,3 |
| SP-1 | 9,0 | 61,4 |
| S-T | 2,5 | 55,3 |
| AL-3 | 1,5 | 42,5 |
| S3 | 68,0 | 41,3 |
| SP-2 | 5,0 | 57,1 |
| S-TC | 1,0 | 48,3 |
| RC-RE | 1,5 | 80,6 |
| RC-DE | 2,0 | 73,0 |
| RC-DC | 2,5 | 66,7 |
| RC-PH | 1,5 | 62,2 |
| RC-PV | 2,5 | 67,7 |
| RC-GA | 1,5 | 73,5 |
| RC-LQ | 0,5 | 57,8 |
| RC-EN | 4,0 | 60,9 |
| RC-RP | 0,5 | 54,1 |
| RC-DP | 0,5 | 65,2 |

**Agua de PH y pretratamiento a PTE**: A07 73 m, B07 70 m, P02 48 m (total 191 m).

**Gas natural a hornos**: B14 57 m, A11 59 m, P03 6 m, P06 16 m (total 138 m).

**Nitrógeno**: T05 11 m, T13 27 m (total 37 m).

**Gas de soldadura**: B03 32 m, M11 34 m, M12 32 m, A06 16 m, B06 13 m, C04 52 m, C05 55 m (total 234 m).


Anillo de aire comprimido: 272 m. Potencia instalada de equipos: 339 kW.

## 12. Longitud de los flujos

| Tipo | Flujo | Largo (m) |
|---|---|---|
| MP | Chapa: alero -> rack de la guillotina | 26,6 |
| MP | Paquete a la mesa elevadora | 0,4 |
| MP | Caño: alero -> cantiléver del láser | 21,0 |
| MP | Atado al cargador | 0,4 |
| MP | Atado al cargador | 0,4 |
| MP | Flejes: alero -> porta-flejes | 15,5 |
| MP | Rollo al desbobinador | 0,4 |
| MP | Insumos al pañol | 18,9 |
| MP | Casquetes de carros (M3) | 17,2 |
| MP | Casquete a la soldadura circ. | 6,7 |
| MP | Tercerizados revendidos (M3) | 8,7 |
| MP | Polvo químico en big bags (P4) | 12,1 |
| MP | Big bag a la carga de polvo | 1,0 |
| MP | Válvulas, manómetros, cajas (P5) | 8,8 |
| MP | Válvulas a ensamblaje | 7,0 |
| MP | Cajas y film a embalaje | 2,8 |
| MP | Químicos y pintura en polvo (P3) | 10,0 |
| MP | Desengrasante y fosfatizante al túnel | 10,7 |
| MP | Pintura en polvo a la cabina | 32,8 |
| MP | Carros pintados y polvo de carros (P8) | 9,4 |
| SE | Cuerpo cortado | 0,2 |
| SE | Cuerpos al pulmón | 0,2 |
| SE | Cuerpo 2,5-10 kg: numerado -> cilindrado -> soldadura longitudinal | 11,9 |
| SE | Cuerpos 2,5-10 kg al encastre | 6,3 |
| SE | Cuerpos de carros a la cilindradora | 6,8 |
| SE | Cuerpo 1 kg | 0,4 |
| SE | Cuerpo 1 kg | 0,4 |
| SE | PU-L1 a PU-L2 | 1,3 |
| SE | Cuerpos 1 kg al encastre | 7,9 |
| SE | Fleje enderezado | 0,2 |
| SE | Fleje al troquel | 0,2 |
| SE | Fondos al pulmón | 0,4 |
| SE | Fondos al encastre | 10,2 |
| SE | Cúpulas a la soldadura de cuello | 2,1 |
| SE | Cuello preparado | 0,8 |
| SE | Cúpulas con cuello al pulmón | 0,4 |
| SE | Cúpulas a la soldadura circ. | 24,2 |
| SE | Cúpulas a la soldadura circ. | 4,2 |
| SE | Línea principal: encastre -> bordoneado -> soldadura circ. -> PH -> secado -> granallado | 40,2 |
| SE | Defectos a corrección | 1,4 |
| SE | Aprobados al pulmón de pintura | 2,6 |
| SE | Corregidos al pulmón de pintura | 5,1 |
| SE | A la carga de pintura | 6,0 |
| SE | Lazo de pintura: pretratamiento, secado, cabina, polimerizado, enfriamiento | 46,8 |
| RET | Retorno de ganchos vacíos (aéreo, +4,0 m) | 4,1 |
| SE | Pintados al pulmón | 1,0 |
| SE | A la carga de polvo | 6,0 |
| SE | Ensamblaje -> presurización -> hermeticidad -> etiquetado -> embalaje | 12,1 |
| SE | Carros: punteo, soldaduras, inspección, PH y marcado | 29,0 |
| SE | Carros a la espera del pintor | 1,2 |
| SE | Carros a pintura tercerizada (P6) | 6,6 |
| SE | Carga de polvo -> armado | 1,0 |
| SE | Armado -> presurización | 0,2 |
| PT | Cilindros vendidos vacíos al almacén de PT | 14,7 |
| PT | Pallet a envolvedora | 3,5 |
| PT | Pallet a envolvedora | 2,5 |
| PT | Pallet de cilindros a envolvedora | 1,6 |
| PT | Almacén de PT | 4,5 |
| PT | Expedición M1 | 15,1 |
| PT | Expedición M2 | 13,1 |
| PT | Carros terminados (P9) | 10,4 |
| PT | Tercerizados a expedición | 1,2 |
| SCRAP | Scrap a volquete (P2) | 5,0 |

## 13. Supuestos a validar

- Tercerizados revendidos: volumen estimado (no figura en los Excel).
- Retiros, FOS y FOT del parque industrial; ubicación de la celda de media tensión y de la reducción de gas.
- Medidas de equipos marcados E (estimados): confirmar con los proveedores.
- Textos normativos marcados como B en el README (Dec. 351/79 arts. 49, 50 y anexo VII; Res. SRT 960/2015): verificar la versión vigente en InfoLEG.
- Recargas se incluye porque figura en el dimensionamiento técnico, aunque no estaba en la lista de secciones del pedido.
