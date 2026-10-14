# Memoria de cálculo del layout - planta industrial FLAMA S.A. (año 10 = 2035)

Se genera desde `planta/calculos.py` y `planta/layout.py` (`python generar.py`). Cada número indica su fuente: **DT** = Dimensionamiento_TecnicoV2.xlsx, **MP** = MP_Abastecimiento_Almacenamiento_FLAMA_OpcionD.xlsx, **CC** = Comparacion_corte.xlsx, **X-ALM** = Dimensionamiento_Almacenes_MP_v5.xlsx (MRP del grupo), **W-MAN**, **W-CAR** y **W-REC** = Word de proceso de manuales, carros y recargas, **C** = cotización de proveedor, **E** = estimado, **SUP** = supuesto a validar.

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

Nave de 88 × 44 m = 3.872 m², puestos en el orden y la disposición de los Word de proceso (W-MAN, W-CAR, W-REC), pórticos de dos luces (19,40 y 24,60 m) cada 8 m, altura libre 8,00 m (Dec. 351/79 exige ≥ 3 m). Recargas dentro de la nave (ángulo SO, 327 m²). Anexos: servicios 288 m² y sala técnica 58 m².

| Código | Sector | m² proyectados | m² requeridos | Nota |
|---|---|---|---|---|
| AL-MM | Insumos de montaje (manuales) | 14,3 | 13,8 | Dimensionamiento_Almacenes_MP_v5: 31 posiciones, 13,8 m² netos (20,7 brutos); rack de 4 módulos × 2 × 4 niveles = 32: válvulas, manómetros, toberas, mangueras y soportes; salen una vez por turno en el carro de abastecimiento |
| AL-ID | Identificación (etiquetas, obleas, sellos) | 2,0 | 3,0 | Dimensionamiento_Almacenes_MP_v5: 9 lugares, 3,0 m² netos; estantería de 5 niveles; sellos y obleas numerados bajo llave |
| AL-MC | Insumos de montaje (carros) | 3,8 | 2,9 | Dimensionamiento_Almacenes_MP_v5: 7 posiciones, 4,8 m² netos; rack de 1 módulo × 2 × 4 niveles: ruedas, válvulas de carro y alambre Ø1,0 |
| AL-CA | Carros de abastecimiento | 3,9 | - | W-CAR tabla 5: estacionamiento de 3 × 1 m para los 2 carros de abastecimiento diario |
| AL-CU | Cuarentena de MP (compartida manuales y carros) | 25,0 | 25,0 | W-MAN y W-CAR tabla 5: 10 × 2,5 m, demarcada en amarillo: 7 pallets, mesa de inspección de 1,2 × 0,6 y 1,3 m de circulación; colada, espesor en 3 puntos y etiqueta de lote. X-MAN 2035: 3 operarios de recepción (descarga, control y ubicación) |
| AL-RE | Retenidos de MP (no conforme) | 6,0 | 6,0 | W-CAR tabla 5: 4 × 1,5 m demarcados en rojo, 3 pallets; se reclama al proveedor |
| AL-CH | Chapa LAF de manuales (3 formatos) | 18,8 | - | Dimensionamiento_Almacenes_MP_v5 'Chapa y fleje': hojas 1220 × 2440, 1000 × 2000 y 1500 × 3000 en paquetes de 2 alturas (7 lugares); el autoelevador los toma de costado desde A2 (W-MAN) |
| AL-FL | Flejes LAF de manuales | 10,9 | - | Dimensionamiento_Almacenes_MP_v5: 21 rollos parados en cunas; porta-flejes de 3 niveles (24 cunas, MP Opción D) en vez de 1 nivel a piso: misma capacidad en la tercera parte del frente de calle |
| AL-SS | Insumos de soldadura y superficie | 5,6 | 4,8 | Dimensionamiento_Almacenes_MP_v5: 12 posiciones, 4,8 m² netos; rack de 2 módulos: alambre MAG Ø0,9, granalla S330/S390, discos y sprays (la granalla va a la granalladora en el carro de abastecimiento) |
| AL-CC | Chapa LAC de carros (calle de chapa) | 15,0 | - | W-CAR tabla 5 y v5: 3 posiciones de 3,0 × 1,5 m, 2 paquetes por posición; van a la misma guillotina |
| AL-CT | Cantiléver de caños y barras | 31,2 | 30,0 | Dimensionamiento_Almacenes_MP_v5: 11 posiciones a 3 niveles, 30 m² netos (lugar de 5 m² por ítem): caño Ø76,2 del 1 kg en atados de 16 (frente al cajón del láser, cruzando A3), caños de 1" y 1¼" y barras de 3/4" y 1" de carros (al puesto 8.1) |
| AL-CQ | Casquetes y cuplas de carros | 8,1 | 6,0 | Dimensionamiento_Almacenes_MP_v5: 11 posiciones (4 niveles), 6,0 m² netos; rack de 2 módulos × 2 × 4 niveles = 16 frente a AN; carros 1 y 2 a los puestos 6 y 7 (W-CAR) |
| AL-1N | Gasoil e insumos del autoelevador de MP y carros | 4,4 | - | Armario de inflamables y estante; el Heli CPCD50 diésel (W-MAN) se estaciona al final del pasillo central |
| N1 | Corte de chapa (compartido) y marcado de carros | 56,5 | 53,0 | W-CAR: guillotina CENA 8 × 3200 (≈ 3,9 × 2,1), mesa elevadora 2,6 × 1,8 con 1 m de paso, zona trasera 3,9 × 2,5 (rampa, contenedor y carros) = 44 m²; marcado de carros 3,5 × 2,5 pegado a la rampa = 9 m² |
| N2 | Corte de tubo 1 kg | 29,9 | - | W-MAN: 1 láser (X-MAN); cajón de alimentación de 6,5 m al lado de la máquina, dos posiciones de carro «en llenado» y «vacío» de 1,2 × 0,8 m y contenedor de 1.000 L junto a la máquina |
| AL-PR | Procesado: cuerpos cortados de chapa y tramos de 1 kg | 25,6 | - | Dimensionamiento_Almacenes_MP_v5 hoja Procesado A: colchón de 7 días (manuales) y 5 días (rodantes) = 10 pallets de cuerpos de chapa junto a la guillotina y 14 de tramos de 1 kg junto al láser (24 pallets, 28,9 m² netos, con AL-PT); a piso, con zorra |
| AL-PT | Procesado: tramos de 1 kg (continuación) | 8,5 | - | Dimensionamiento_Almacenes_MP_v5 hoja Procesado A: pallets de tramos parados en capas, entre el láser y el encastre |
| AL-PK | Procesado: cúpulas y fondos 1 a 10 kg | 9,1 | - | Dimensionamiento_Almacenes_MP_v5 hoja Procesado B: 18 pallets (21,6 m² netos) = AL-PK más las zonas de cúpulas (PU-CU) y de fondos (PU-FO) de W-MAN; frente a la calle PO-3, entre el embutido y el encastre |
| N6 | Cilindrado y soldadura longitudinal 2,5-10 kg | 23,8 | - | W-MAN: roladora Firesafer FS-RM01 y soldadora longitudinal con el carro FCHP20505 entre las dos (un lado largo hacia cada máquina) |
| N3 | Corte de disco y embutido | 31,0 | - | W-MAN: desbobinador, enderezador y alimentador Cena PRE-1, prensa Sangiacomo; estantería de matrices y carro porta-matrices al lado de la prensa; contenedor de 1.000 L del esqueleto |
| N7 | Celda de cuello: numerado, muesca y soldadura | 37,4 | - | W-MAN: las prensas de muesca van pegadas a la de numerado y a la soldadora de cuello, sin transporte entre las tres; zona de cúpulas al lado |
| N4 | Encastre, bordoneado, soldadura circ., espesor y PH | 94,5 | - | W-MAN y X-MAN: encastre 1, bordoneado 1, soldadura circ. 2, control de espesor 1, PH 2; un FCHP20505 entre cada par de puestos |
| N5 | Secado, granallado, detección y corrección | 109,3 | - | W-MAN y X-MAN: secado 4, granallado 1 (de rodillos), detección 1, corrección 1; tres jaulas al lado del puesto; el detector cuelga el cilindro en el riel de pintura |
| MT | Taller de mantenimiento | 36,8 | 30,0 | Mantenimiento preventivo: bancos, torno, agujereadora, soldadora móvil; entra la transpaleta desde el pasillo central; puerta directa al pañol |
| PÑL | Pañol de mantenimiento y de línea | 17,3 | - | Pegado al taller: repuestos críticos, herramental del preventivo, consumibles de soldadura (toberas, puntas, discos) contra vale por la ventanilla a PO-1 |
| Q | Laboratorio de calidad | 34,0 | 31,0 | Metrología, ensayo de rotura (1 cilindro por lote, W-MAN), adherencia y espesor de pintura, humedad del polvo, probetas de soldadura de carros (X-DT) y descarga de muestras (IRAM 3550); legajos |
| QR | Cuarentena de producto y muestras retenidas | 18,4 | 15,0 | Jaula con llave: lotes rechazados y un cilindro testigo por lote (IRAM 3517 / 3523) |
| SUP | Supervisor de planta | 13,8 | - | Oficina propia del encargado de turno, con ventana a la línea y al pasillo central |
| PCP | Planificación y control de la producción | 18,4 | - | Separada del supervisor: 2 puestos y tablero de programación con ventana a la línea |
| PV | Supermercado de carros vacíos | 56,9 | - | Carros FCHP20505 y de estantes de 12 cajones de reserva y para el cambio de formato (W-MAN: dos por tramo, uno en uso y otro para el formato siguiente) |
| SC | Compresores y colector de humos | 56,3 | - | Reguladores de Arcal 21 y N₂ que vienen de la jaula exterior (puerta PG), colector de humos, 2 compresores de tornillo, secador y pulmón |
| S-P | Pintura en polvo (riel aéreo) | 286,0 | - | W-MAN: riel transportador aéreo -> horno de precalentamiento -> cabina con recuperación -> horno de curado 180-220 °C -> enfriamiento y descarga; esquema de 22 × 13 m |
| ST-I | Tableros y compresor de la cabina | 27,7 | - | Tablero de la línea este y compresor sin aceite dedicado a la cabina de pintura |
| DP | Depósito de polvo químico (único de la planta) | 12,6 | 12,6 | Dimensionamiento_Almacenes_MP_v5: 11 posiciones, 8,4 m² netos, 12,6 brutos; cerrado y seco: big bags de ABC 60 y ABC 90, polvo D y pintura en polvo; entra por AT (muelle P3) y sale a la carga (norte), a carros y a pintura (oeste) |
| S-T | Terminación 1 a 10 kg | 55,0 | - | W-MAN: carga (estación de big bag y transportador neumático) -> ensamblaje -> presurización -> ensayo de pérdidas -> etiquetado, con un FCHP20505 entre cada par de puestos; termina en el embalaje |
| EMB | Embalaje y paletizado (vacíos y terminados) | 71,0 | - | W-MAN: los vacíos se encajonan al lado de la descarga de pintura y los terminados al final de la terminación, en la misma zona: armadora de cajas, 2 mesas de encajonado (X-MAN) y envolvedora EDOS PS5 |
| AL-EB | Embalaje: cajas plegadas, film y pallets | 23,1 | 17,8 | Dimensionamiento_Almacenes_MP_v5: 50 posiciones, 22,2 m² netos; rack de 6 módulos × 2 × 4 niveles = 48 + pila de pallets vacíos junto a la envolvedora; las cajas van a la armadora con la transpaleta |
| PU-9 | Terminados pintados esperando la carga | 15,7 | - | W-MAN: 413 matafuegos por día en el pico en carros FCHP20505 y de cajones (1 kg) |
| DL | Ducha de emergencia y lavaojos | 6,0 | - | A menos de 10 s de la carga de polvo, de la presurización y de la descarga de pintura |
| AL-3 | Almacén de producto terminado y de cilindros | 134,4 | - | X-DT Almacén PT 2035: 56 pallets esperando despacho + 72 del stock oct-nov = 128; racks de 4 módulos a 5 niveles: RK1 40 + RK2 80 + RK3 40 = 160 (incluye 8 pallets de carros terminados) |
| EXP | Expedición y muelle P3 | 81,9 | - | Un solo muelle con rampa niveladora: sale PT y carros (terminados y al pintor); entran polvo, pintura en polvo, embalaje y revendidos. Recepción 7 a 10 h, expedición 13 a 17 h |
| S4 | Tercerizados revendidos | 11,4 | 9,6 | Dimensionamiento_Almacenes_MP_v5 'Almacén de producto terminado': 17 posiciones (14,4 m² brutos); rack de 2 módulos × 4 niveles: CO₂, agua, AFFF, clase K y agente limpio |
| REC | Recepción del muelle: mesa de control | 4,8 | - | Remito contra orden de compra y muestra del lote de polvo al laboratorio (humedad) antes de liberarlo |
| C-5 | Soldadura longitudinal de carros (5) | 23,0 | 22,0 | W-CAR tabla: ≈ 5,5 × 4,0 = 22 m²; mandril con 1,5 m libres para el cuerpo; no conforme en rojo |
| C-4 | Punteo del cuerpo ×2 (4) | 31,3 | 27,0 | W-CAR ≈ 6,0 × 4,5 por puesto; X-DT 2035: 2 viradores (comparten banco, cuna y pulmón) |
| C-3 | Cilindrado de carros (3) | 33,6 | 30,8 | W-CAR ≈ 7,0 × 5,0 = 35 m²: roladora W12 8 × 1500, zona de carga, EFE 600 y mesa móvil, salida axial y pulmón de 1,8 × 1,2 |
| C-6 | Soldadura de cupla en la cúpula (6) | 20,0 | 16,0 | W-CAR ≈ 4,5 × 3,5 = 16 m²; pegado al armado (7); lo hace el operario de punteo |
| C-7 | Armado y soldadura circunferencial (7) | 28,0 | 27,0 | W-CAR ≈ 6,0 × 4,5 = 27 m²: virador, carro canasto de cúpulas y carro 2 de fondos |
| C-8 | Soldadura de accesorios e inspección (8) | 25,0 | 20,0 | W-CAR ≈ 5,0 × 4,0 = 20 m²: virador y carro de kits; monta eje y ruedas; inspección de costuras (X-DT) |
| C-T | Terminación de carros | 21,5 | - | Carga de polvo ABC 90 (estación de big bag), armado de válvula y manguera, presurización y etiquetado; vuelven del pintor por PO-CN |
| C-81 | Fabricación de accesorios (8.1) | 39,2 | 32,0 | W-CAR ≈ 8,0 × 4,0 = 32 m²: rack de barras de 6,5 m sobre la calle PO-C, caballetes, sensitiva, dobladora, taladro, banco y prensa de 20 t; el carro de kits va al puesto 8 |
| C-9 | Prueba hidráulica de carros (9) | 27,0 | 22,0 | W-CAR ≈ 5,5 × 4,0 = 22 m²: 2 bandejas con rampa, pantalla, Yukon M-000200, tanque de 1.000 L en circuito cerrado |
| C-10 | Secado de carros | 10,3 | - | W-CAR puesto 9: sale vacío y rodando hacia el secado |
| C-PP | Carros al muelle: a pintura y terminados | 32,3 | 32,0 | Pulmón de despacho a pintura tercerizada (6 carros, W-CAR) y carros terminados esperando despacho (X-DT Almacén PT: 32 m²; 8 pallets más en RK1) |

Almacenes: los dimensiona el grupo en el MRP (X-ALM v5, con la planilla de plazos de entrega); el plano ubica cada sección con al menos su superficie neta o sus posiciones. Una sola recepción de MP con cuarentena compartida con carros (W-MAN, W-CAR). Calles de 5,0 m para el Heli CPCD50 (W-CAR tabla 5).

| Sección (X-ALM) | Posiciones | m² netos | m² brutos | Sector del plano | m² en el plano | Cómo se guarda |
|---|---|---|---|---|---|---|
| Chapa y fleje (manuales) | 28 | 38,7 | 58,0 | AL-CH + AL-FL | 29,7 | hojas a piso (2 alturas); fleje en porta-flejes de 3 niveles |
| Calle de chapa (carros) | 3 | 9,0 | 13,5 | AL-CC | 15,0 | pilas a piso de 2 alturas, acceso de costado desde A2 |
| Cantilever de caños y barras | 11 | 30,0 | 45,0 | AL-CT | 31,2 | cantiléver de 3 niveles frente a A3 |
| Rack de casquetes y cuplas (carros) | 11 | 6,0 | 9,0 | AL-CQ | 8,1 | rack de 2 módulos × 4 niveles frente a AN |
| Insumos de montaje (manuales) | 31 | 13,8 | 20,7 | AL-MM | 14,3 | rack de 4 módulos × 4 niveles frente a A1 |
| Rack de insumos de montaje (carros) | 7 | 4,8 | 7,2 | AL-MC | 3,8 | rack de 1 módulo × 4 niveles frente a A1 |
| Identificación | 9 | 3,0 | 4,5 | AL-ID | 2,0 | estantería de 5 niveles, sellos bajo llave |
| Insumos de soldadura y superficie | 12 | 4,8 | 7,2 | AL-SS | 5,6 | rack de 3 pallets × 4 niveles frente a AN |
| Depósito de polvo químico | 11 | 8,4 | 12,6 | DP | 12,6 | local cerrado y seco junto a la carga |
| Embalaje | 50 | 22,2 | 33,3 | AL-EB | 23,1 | rack de 6 módulos × 4 niveles sobre AT |
| Almacén de producto terminado | 17 | 9,6 | 14,4 | S4 | 11,4 | revendidos: rack de 2 módulos × 4 niveles |
| Insumos de recargas | 10 | 9,6 | 14,4 | RC-IN | 7,0 | rack de recargas (fuera de línea) |
| Jaula de gases | 12 | 10,5 | 15,8 | JG | 15,8 | jaula exterior con packs y manifold (W-MAN) |
| Procesado: cuerpos cortados y cúpulas y fondos embutidos | 42 | 50,5 | 75,8 | AL-PR + AL-PT + AL-PK + PU-FO + PU-CU | 61,7 | pallets a piso junto a la guillotina, al láser y al embutido |

X-ALM redondea cada ítem a lugares enteros (sin compartir columna). Donde el plano tiene menos m² netos (fleje, insumos de carros, identificación e insumos de recargas) las posiciones entran igual: el fleje va en porta-flejes de 3 niveles en lugar de pallets a piso, y los ítems chicos comparten columna de rack o estantería. El área bruta de X-ALM (× 1,5 de circulación) queda reemplazada por las calles de 5 m del plano, por eso el almacén de MP ocupa más que la suma de las áreas brutas.


## 3. Recepción de MP y análisis de peso de la carga

Se dimensiona para la carga máxima: un semirremolque de 18,6 m y 30 t o dos chasis de 10 m en el alero de descarga norte (32 × 11,6 m), playos y con el costado libre (W-CAR), con descarga por ambos lados con el autoelevador. La nave tiene tres portones: P1 (una sola recepción de MP de manuales y carros, con cuarentena, W-MAN), P2 (recargas) y el muelle único P3 (PT y carros; entran polvo, pintura en polvo, embalaje y revendidos; recepción 7 a 10 h y expedición 13 a 17 h). El ex P4 se suprimió: la pintura en polvo va al depósito de polvo DP (X-ALM) y la granalla al almacén de MP (AL-SS). Los packs de gases se cambian desde el patio norte en la jaula exterior JG. Los camiones entran por G1 (garita y báscula) y salen por G3.

| Formato | Largo (m) | Carga útil (t) | PBT (t) | Descarga |
|---|---|---|---|---|
| Semirremolque playo 3+3 ejes | 18,6 | 30,0 | 45,0 | Alero de descarga norte: autoelevador por los dos lados; entra por P1 a la cuarentena (A1) |
| Camión chasis con balancín (3 ejes) | 11,0 | 16,0 | 26,0 | Alero de descarga norte (junto al semi): autoelevador por los dos lados, bajo techo |
| Camión chasis 2 ejes | 9,5 | 9,0 | 16,5 | Alero norte (P1), muelle P3 o jaula de gases según el material |
| Utilitario / furgón | 6,0 | 1,5 | 3,5 | Recargas e insumos de recargas por P2 |

| Proveedor / material | t por entrega | Entregas/año | Vehículo | Portón | Destino |
|---|---|---|---|---|---|
| Pradecon: hojas + fleje 0,9 | 35,26 | 18,1 | Semi (máx.) o 2 chasis quincenales | Alero + P1 | AL-CU -> AL-CH y AL-FL |
| Pacheco: flejes 1,25-2,0 y chapa LAC | 5,05 | 29,3 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-FL y AL-CC |
| Metalprisa: caño Ø76,2 | 4,23 | 28,9 | Chasis 2 ejes | Alero + P1 (atado atravesado) | AL-CU -> AL-CT |
| Eli-Met: cuellos y roscas | 3,68 | 5,6 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-MM |
| Soldadura: alambre MAG | 1,89 | 8,1 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-SS |
| Air Liquide: Arcal 21 (packs) | 3,80 | 15,6 | Chasis 2 ejes | Jaula exterior JG | JG -> reguladores CG1 |
| Air Liquide: N₂ (packs) | 3,80 | 15,6 | Chasis 2 ejes | Jaula exterior JG | JG -> reguladores CG1 |
| Polvo químico (Polvex / DEMSA) | 13,13 | 31,0 | Chasis con balancín | Muelle P3 | DP (depósito único) |
| Válvulas, manómetros y pescantes | 8,16 | 8,3 | Chasis con balancín | Alero + P1 | AL-CU -> AL-MM |
| Casquetes de carros | 5,93 | 4,1 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-CQ |
| Estructuras y ruedas de carros | 5,52 | 15,1 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-MC |
| Embalaje, pallets, etiquetas y precintos | 4,61 | 15,3 | Chasis 2 ejes | Muelle P3 | AL-EB y AL-ID |
| Tercerizados revendidos | 3,00 | 24,0 | Chasis 2 ejes (SUPUESTO) | Muelle P3 | S4 |
| Agentes para recargas | 2,87 | 8,2 | Utilitario / chasis 2 ejes | P2 | RC-IN |
| CYM: granalla | 3,11 | 2,0 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-SS |
| Pintura electrostática en polvo | 0,79 | 8,3 | Utilitario | Muelle P3 | DP |

Pradecon entrega 35,3 t por mes (hojas + fleje 0,9): supera la carga útil de un semi. Se parte en 2 entregas quincenales de 17,6 t, que entran en un chasis con balancín y bajan el stock máximo de chapa medio mes.

Capacidad residual del autoelevador con un paquete de hoja de 1500 × 3000 mm y 2 t (Q = Qn · (cn + d) / (c + d), d = 0,45 m):

| Nominal (c = 500 mm) | Por el lado largo (c = 750 mm) | Por el lado corto (c = 1500 mm) |
|---|---|---|
| 2,5 t | 1,98 t | 1,22 t |
| 3,0 t | 2,38 t | 1,46 t |
| 3,5 t | 2,77 t | 1,71 t |

Se adopta el autoelevador de W-MAN: Heli CPCD50 K2 diésel de 5 t, compartido entre la MP de manuales y la de carros, con uñas largas, prolongadores para los atados, espolón para los rollos y pluma para los big bags y los atados (Mecánica Porta). Con 5 t nominales toma el paquete de 2 t por cualquier lado. El PT y el muelle tienen su propio autoelevador (racks de 5 niveles), y el embalaje una transpaleta eléctrica con una manual de respaldo (W-MAN).

## 4. Política de stock de chapa, fleje y caño (MRP del grupo)

| Artículo | Consumo (día pico) | Unidad de compra | Punto de pedido y plazo | Se pide | Stock máximo |
|---|---|---|---|---|---|
| Caño c/costura Ø76,2 × 1,25 × 6 m | 52,9 barra/día | Atado de 16 barras | Punto de pedido 53 barra; plazo 1 d | cada 5 días: 17 u. | 288 barra |
| Hoja LAF 1,25 × 1220 × 2440 mm | 2,9 hoja/día | Paquete de 50 hojas | Punto de pedido 29 hoja; plazo 10 d | cada 20 días: 2 u. | 110 hoja |
| Hoja LAF 1,6 × 1000 × 2000 mm | 30,0 hoja/día | Paquete de 80 hojas | Punto de pedido 300 hoja; plazo 10 d | cada 20 días: 8 u. | 747 hoja |
| Hoja LAF 2,0 × 1500 × 3000 mm | 1,4 hoja/día | Paquete de 20 hojas | Punto de pedido 14 hoja; plazo 10 d | cada 20 días: 2 u. | 45 hoja |
| Fleje LAF 0,9 × 114 mm | 96,0 kg/día | Rollo de 1.900 kg | Punto de pedido 960 kg; plazo 10 d | cada 5 días: 1 u. | 2293 kg |
| Fleje LAF 1,25 × 135 mm | 185,2 kg/día | Rollo de 1.900 kg | Punto de pedido 1852 kg; plazo 10 d | cada 5 días: 1 u. | 2659 kg |
| Fleje LAF 1,25 × 200 mm | 50,7 kg/día | Rollo de 492 kg | Punto de pedido 507 kg; plazo 10 d | cada 10 días: 2 u. | 1164 kg |
| Fleje LAF 1,6 × 250 mm | 252,9 kg/día | Rollo de 615 kg | Punto de pedido 2529 kg; plazo 10 d | cada 5 días: 3 u. | 2745 kg |
| Fleje LAF 1,6 × 200 mm | 162,6 kg/día | Rollo de 492 kg | Punto de pedido 1626 kg; plazo 10 d | cada 5 días: 2 u. | 1563 kg |
| Fleje LAF 1,6 × 300 mm | 20,8 kg/día | Rollo de 590 kg | Punto de pedido 208 kg; plazo 10 d | cada 20 días: 1 u. | 664 kg |
| Fleje LAF 2,0 × 249 mm | 17,2 kg/día | Rollo de 498 kg | Punto de pedido 172 kg; plazo 10 d | cada 20 días: 1 u. | 559 kg |
| Hoja LAC 3,2 × 1500 × 3000 mm | 1,7 hoja/día | Paquete de 20 hojas | Punto de pedido 17 hoja; plazo 10 d | cada 20 días: 2 u. | 44 hoja |
| Hoja LAC 4,75 × 1500 × 3000 mm | 0,7 hoja/día | Paquete de 15 hojas | Punto de pedido 7 hoja; plazo 10 d | cada 20 días: 1 u. | 17 hoja |

Fuente: X-ALM v5, hoja Política de stock (stock máximo = stock de seguridad + una compra). Hoja LAF aceitada con film VCI, siempre bajo techo y lejos de la PH; FIFO por tarjeta de color del mes de ingreso.

## 5. Pulmones y manejo de materiales (métodos y tiempos)

| Pulmón | Tasa (u/h) | Cobertura (h) | Unidades | Carros | Criterio |
|---|---|---|---|---|---|
| PU-1 / PU-D desarrollos 2,5-10 kg y carros | 33,0 | 8,00 | 264 | 6 | La guillotina corta por tandas de un formato: 1 turno de consumo |
| PU-T1 / PU-T2 tramos 1 kg (láser) | 79,0 | 0,50 | 40 | 2 | Carro «en llenado» y «vacío» (W-MAN) |
| PU-FO / PU-CU cúpulas y fondos (pares) | 110,8 | 4,00 | 443 | 3 | Cambio de troquel de la prensa (≈ 30 min) cada medio turno: 3 a 5 carros (W-MAN) |
| PU-CC / PU-CC2 cúpulas con cuello | 110,8 | 1,00 | 111 | 3 | Carro en llenado en la soldadura de cuello y en consumo en las circunferenciales |
| PU-6 / PU-7 probados y secos | 110,8 | 0,75 | 83 | 2 | Secado y granallado sin detener la PH |
| PU-TP terminados pintados a la carga | 110,8 | 0,50 | 55 | 2 | Carga de polvo por lote |

Tiempo por viaje = 2 × distancia / velocidad + tiempo fijo de toma y entrega. Distancias medidas sobre los recorridos del modelo; día pico 2035.

| Unidad de carga | Medio | Recorrido | Viajes/día | m | min/viaje | min/día |
|---|---|---|---|---|---|---|
| Paquete de hojas ≤ 2 t | Autoelevador MP y carros | Alero -> P1 -> A1 -> cuarentena | 0,6 | 24 | 2,0 | 1 |
| Paquete aprobado | Autoelevador MP y carros | Cuarentena -> A1 -> AN -> A2 -> AL-CH | 0,5 | 29 | 2,1 | 1 |
| Paquete LAF a la guillotina y vuelta | Autoelevador MP y carros | AL-CH -> A2, AN y A3 -> mesa elevadora | 1,0 | 40 | 2,4 | 2 |
| Paquete LAC a la guillotina y vuelta | Autoelevador MP y carros | AL-CC -> mesa elevadora | 0,3 | 34 | 2,3 | 1 |
| Rollo de fleje 0,5-1,9 t | Autoelevador MP y carros | Porta-flejes -> AN -> desbobinador | 1,1 | 15 | 1,8 | 2 |
| Atado de caños Ø76,2 | Autoelevador MP y carros | Cantiléver -> cajón del láser (pluma) | 3,3 | 10 | 1,7 | 6 |
| Barras y caños de carros | Carro a mano | Cantiléver -> PC -> PO-CW -> rack 8.1 (porta-barras) | 2,0 | 32 | 1,8 | 4 |
| Casquetes y cuplas (carros 1 y 2) | Carro a mano | AL-CQ -> puestos 6 y 7 | 2,0 | 32 | 1,8 | 4 |
| Contenedor de orillas (guillotina) | Autoelevador MP y carros | Guillotina -> volquete (P1) | 0,2 | 54 | 2,7 | 1 |
| Contenedor de recortes (láser) | Autoelevador MP y carros | Láser -> A3 -> volquete (P1) | 0,2 | 40 | 2,4 | 0 |
| Contenedor del esqueleto (ruedas) | Carro a mano | Prensa -> PO-3 -> AN -> volquete | 1,0 | 37 | 2,1 | 2 |
| Big bag de polvo 1 t / caja de pintura | Autoelevador PT | Muelle P3 -> AT -> depósito DP | 1,7 | 11 | 1,7 | 3 |
| Big bag de ABC 60 | Autoelevador PT | DP -> estación de la carga (19) | 1,3 | 3 | 1,6 | 2 |
| Big bag de ABC 90 | Transpaleta | DP -> AC -> PC -> PO-CN -> carros (C12) | 0,4 | 37 | 2,5 | 1 |
| Caja de pintura en polvo | Transpaleta | DP -> AC -> PC -> PO-PI -> tolvas | 0,6 | 41 | 2,7 | 2 |
| Pallet de cilindros vacíos | Transpaleta | Mesa de vacíos -> envolvedora | 6,0 | 10 | 1,4 | 9 |
| Pallet de terminados | Transpaleta | Mesa de terminados -> envolvedora | 2,0 | 6 | 1,3 | 2 |
| Pallet de PT | Transpaleta | Envolvedora -> AT -> T2 (pie del rack) | 8,0 | 18 | 1,7 | 14 |
| Pallet de PT | Autoelevador PT | Ubica en el rack; rack -> T1 -> EX -> muelle P3 | 8,0 | 14 | 1,8 | 14 |
| Pallet de revendidos | Autoelevador PT | Muelle P3 -> S4 -> muelle P3 | 0,2 | 19 | 1,9 | 0 |
| Carro rodante (al pintor y terminado) | Carro a mano | C-PP -> PO-C -> EX -> rampa del muelle P3 | 40,0 | 12 | 1,0 | 40 |
| Carro rodante pintado (rueda) | Carro a mano | Muelle P3 -> EX -> PO-CN -> C-T | 20,0 | 21 | 1,4 | 28 |
| Carro rodante terminado (rueda) | Carro a mano | C-T -> PO-C -> C-PP | 20,0 | 5 | 0,7 | 14 |
| Carro de kits (≈ 10 kits) | Carro a mano | Puesto 8.1 -> PO-C -> puesto 8 | 2,0 | 10 | 0,9 | 2 |
| FCHP de cuerpos 2,5-10 kg (63 a 120 u) | Carro a mano | PU-V3 -> 9 encastre | 6,0 | 1 | 0,6 | 3 |
| Carro de 12 cajones de tramos (420 u) | Carro a mano | PU-T1 -> PU-T2 (encastre) | 3,0 | 5 | 0,7 | 2 |
| Carro de 12 cajones de fondos | Carro a mano | PU-K -> zona de fondos | 2,0 | 3 | 0,6 | 1 |
| Carro de 12 cajones de cúpulas | Carro a mano | PU-K -> zona de cúpulas | 2,0 | 0 | 0,5 | 1 |
| Carro de cúpulas con cuello | Carro a mano | PU-CC2 -> PU-CC (sold. circ.) | 3,0 | 3 | 0,6 | 2 |
| Carro de cilindros, 9 tramos 9 -> 17 | Carro a mano | entre pasos (prom. por tramo) | 126,0 | 4 | 0,7 | 83 |
| Carro de terminados pintados | Carro a mano | Descarga -> PO-PI -> AT2 -> PU-TP | 3,5 | 30 | 1,8 | 6 |
| Carro de cilindros vacíos | Carro a mano | Descarga -> mesa de vacíos | 10,5 | 11 | 1,0 | 10 |
| Zorra de consumibles y cajas (vuelta) | Zorra milk run | AL-CA -> puestos -> AL-CA | 4,0 | 156 | 7,0 | 28 |

Ocupación sobre un turno útil de 408 min: autoelevador de MP y carros 3 %, de PT 5 %, transpaleta 7 %. Entre pasos se mueven 14 carros FCHP20505 por día y por tramo: W-MAN pone un carro entre cada par de puestos y lo empuja el operario que cierra el lote, sin tren logístico; al norte de la senda no entra el autoelevador. El riel aéreo lleva el cilindro de la detección a la descarga de pintura (53 m cargado, 10 m del horno de curado 2 y 36 m de retorno de ganchos vacíos). Los carros rodantes ruedan sobre sus ruedas por PO-C y EX hasta la rampa del muelle. El abastecedor hace el milk run con los 2 carros de abastecimiento (AL-CA, W-CAR) una vez por turno.

| Portón | Qué entra o sale | Vehículo | Frecuencia | Horario |
|---|---|---|---|---|
| P1 + alero | Entran hojas, flejes, caños y barras, casquetes, insumos de montaje, alambre y granalla (una sola recepción con cuarentena, W-MAN); sale el scrap al volquete | Semi / chasis | ≈ 2,4 camiones por semana | 7 a 10 h |
| Jaula JG (PG) | Cambio de packs de Arcal 21 y N₂ y de cilindros de CO₂ de recargas desde el patio norte | Chasis 2 ejes | ≈ 0,6 por semana | 7 a 10 h |
| P2 | Recargas: los utilitarios dejan y retiran equipos de clientes y traen insumos de recargas | Utilitarios de reparto (8) | 2 vueltas por día | Milk run mañana y tarde |
| P3 (muelle) | Sale PT y carros (terminados y al pintor); entran revendidos, polvo, pintura en polvo y embalaje | Semi / chasis | 7 PT + ≈ 3 recepciones por semana | Recepción 7 a 10 h; expedición 13 a 17 h |
| PP-1 | Personal: vestuarios <-> senda de la nave | A pie | 63 personas, 2 turnos | Entrada y salida |

Gases (W-MAN): packs de 12 cilindros de Arcal 21 y de N₂ con manifold en la jaula exterior JG, detrás de la sala SC; los reguladores CG1 están en el extremo oeste de la sala: 317 m de cañería (recorrido ortogonal) a las 9 soldadoras, contra 370 m desde el centro de la sala. Recargas: diagrama de gases de W-REC (equipo de transferencia THB/BP al centro, cilindros de origen a la entrada y de destino a la salida, N₂ o argón arriba y bomba de vacío abajo) en el local RC-HA, y trasvasadora de CO₂ con manifold en RC-GA.

| Soldadora | m desde los reguladores CG1 |
|---|---|
| B03 | 23,8 |
| M11 | 7,4 |
| A06 | 15,3 |
| B06 | 12,9 |
| C02s | 45,0 |
| C04 | 52,5 |
| C06 | 58,7 |
| C05 | 53,6 |
| C08 | 48,0 |
## 6. Cruces de flujos y de hilos

Cruces entre flujos de MP, SE y PT (verificación geométrica sobre el modelo): **54**. Cruces de hilos de personal con flujos: todos dentro de las **30** sendas peatonales señalizadas (X1 a X30).

## 7. Sanitarios, vestuarios y servicios (Dec. 351/79 arts. 49 y 50)

Turno más numeroso: 55 hombres (47 del turno mañana + 8 choferes) y 6 mujeres.

| Artefacto | H requerido | H proyectado | M requerido | M proyectado |
|---|---|---|---|---|
| inodoros | 3 | 3 | 1 | 1 |
| lavabos | 6 | 6 | 1 | 1 |
| orinales | 6 | 6 | 0 | 0 |
| duchas | 3 | 3 | 1 | 1 |

Armarios: H 56 requeridos / 60 proyectados; M 7 / 9 (vestuario de mujeres al 20 % de la dotación). Lockers individuales, 1 por empleado, en bloques de 10 columnas × 3 filas. Un sanitario accesible con ducha en el bloque de servicios (Ley 24.314, Dec. 914/97: círculo libre de Ø 1,50 m, espacio lateral de 0,80 m, barras); los sanitarios de planta (banda sur, sobre la calle AT2) son de hombres y de mujeres. Espacio de cuidado no obligatorio (Dec. 144/2022 exige 100 o más personas; la dotación es 71). Comedor de 30 plazas en 2 tandas (DT Servicios).

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
| SN-H Sanitarios hombres (planta) | 17,4 |
| SN-M Sanitario mujeres (planta) | 7,8 |
| RC-RD Recepción, registro y despacho (portón P2) | 26,2 |
| RC-IV Inspección visual (zona general) | 17,2 |
| RC-PV Recinto de polvo químico (HR ≤ 70 %) | 96,8 |
| RC-LB Laboratorio de polvo y calidad de recargas | 9,5 |
| RC-IR Inutilización y disposición final | 6,2 |
| RC-IN Insumos de recargas | 7,0 |
| RC-AC Antecámara del recinto de polvo | 4,5 |
| RC-PE Pérdidas, peso, precinto y etiquetado | 21,1 |
| RC-LQ Líquidos: agua, AFFF y clase K | 19,4 |
| RC-GA CO₂: recuperación, desarme y carga | 17,3 |
| RC-HA Halogenados: circuito cerrado | 16,2 |
| RC-PH Prueba hidráulica, secado y cámara | 19,4 |

## 8. Medios de escape (Dec. 351/79 anexo VII)

Factor de ocupación industrial 16 m²/persona: N = 242 personas teóricas; n = N/100 -> 3 unidades de ancho de salida (1,55 m mínimos). Proyectado: 10 salidas de emergencia de 1,10 m (11,00 m) con barral antipánico, más los portones con puerta de hombre y el paso a servicios.

Recorrido real máximo hasta una salida, calculado sobre una grilla de 0,5 m que rodea los equipos: **36,9 m** (punto x = 49,5, y = 26,0), por debajo de los 40 m que se toman como límite (verificar el artículo vigente).

## 9. Protección contra incendio

Extintores ABC de 10 kg en la nave: **20** (mínimo por superficie 1 cada 200 m² = 20), ubicados por cálculo para que ningún punto quede a más de 20 m de recorrido (IRAM 3517-2:2020, fuego clase A). Se suman 10 en anexos y exteriores, CO₂ junto a tableros y un carro de 50 kg ABC en pintura y en la sala de polvo. Señalización con chapa baliza y cartel en altura (IRAM 3517-2 cap. 7). La reserva de agua contra incendio y la red de hidrantes quedan previstas en el terreno y se confirman con el estudio de carga de fuego.

## 10. Iluminación (método de los lúmenes)

Luminaria LED de 150 W y 21.000 lm; factor de utilización 0,65; mantenimiento 0,80. Niveles: nave 300 lx, depósitos 150 lx, pintura 500 lx, laboratorio 750 lx; soldadura y montaje fino 500 lx y líquidos penetrantes 750 lx con iluminación localizada.

| Sector | lx | m² | Luminarias | kW |
|---|---|---|---|---|
| AL-MM Insumos de montaje (manuales) | 150 | 14 | 1 | 0,15 |
| AL-ID Identificación (etiquetas, obleas, sellos) | 150 | 2 | 1 | 0,15 |
| AL-MC Insumos de montaje (carros) | 150 | 4 | 1 | 0,15 |
| AL-CA Carros de abastecimiento | 150 | 4 | 1 | 0,15 |
| AL-CU Cuarentena de MP (compartida manuales y carros) | 750 | 25 | 2 | 0,30 |
| AL-RE Retenidos de MP (no conforme) | 750 | 6 | 1 | 0,15 |
| AL-CH Chapa LAF de manuales (3 formatos) | 150 | 19 | 1 | 0,15 |
| AL-FL Flejes LAF de manuales | 150 | 11 | 1 | 0,15 |
| AL-SS Insumos de soldadura y superficie | 150 | 6 | 1 | 0,15 |
| AL-CC Chapa LAC de carros (calle de chapa) | 150 | 15 | 1 | 0,15 |
| AL-CT Cantiléver de caños y barras | 150 | 31 | 1 | 0,15 |
| AL-CQ Casquetes y cuplas de carros | 150 | 8 | 1 | 0,15 |
| AL-1N Gasoil e insumos del autoelevador de MP y carros | 300 | 4 | 1 | 0,15 |
| N1 Corte de chapa (compartido) y marcado de carros | 300 | 56 | 2 | 0,30 |
| N2 Corte de tubo 1 kg | 300 | 30 | 1 | 0,15 |
| AL-PR Procesado: cuerpos cortados de chapa y tramos de 1 kg | 150 | 26 | 1 | 0,15 |
| AL-PT Procesado: tramos de 1 kg (continuación) | 150 | 9 | 1 | 0,15 |
| AL-PK Procesado: cúpulas y fondos 1 a 10 kg | 150 | 9 | 1 | 0,15 |
| N6 Cilindrado y soldadura longitudinal 2,5-10 kg | 300 | 24 | 1 | 0,15 |
| N3 Corte de disco y embutido | 300 | 31 | 1 | 0,15 |
| N7 Celda de cuello: numerado, muesca y soldadura | 300 | 37 | 2 | 0,30 |
| N4 Encastre, bordoneado, soldadura circ., espesor y PH | 300 | 94 | 3 | 0,45 |
| N5 Secado, granallado, detección y corrección | 300 | 109 | 4 | 0,60 |
| MT Taller de mantenimiento | 300 | 37 | 2 | 0,30 |
| PÑL Pañol de mantenimiento y de línea | 300 | 17 | 1 | 0,15 |
| Q Laboratorio de calidad | 750 | 34 | 3 | 0,45 |
| QR Cuarentena de producto y muestras retenidas | 750 | 18 | 2 | 0,30 |
| SUP Supervisor de planta | 300 | 14 | 1 | 0,15 |
| PCP Planificación y control de la producción | 300 | 18 | 1 | 0,15 |
| PV Supermercado de carros vacíos | 300 | 57 | 2 | 0,30 |
| SC Compresores y colector de humos | 300 | 56 | 2 | 0,30 |
| S-P Pintura en polvo (riel aéreo) | 500 | 286 | 14 | 2,10 |
| ST-I Tableros y compresor de la cabina | 300 | 28 | 1 | 0,15 |
| DP Depósito de polvo químico (único de la planta) | 150 | 13 | 1 | 0,15 |
| S-T Terminación 1 a 10 kg | 300 | 55 | 2 | 0,30 |
| EMB Embalaje y paletizado (vacíos y terminados) | 150 | 71 | 1 | 0,15 |
| AL-EB Embalaje: cajas plegadas, film y pallets | 150 | 23 | 1 | 0,15 |
| PU-9 Terminados pintados esperando la carga | 300 | 16 | 1 | 0,15 |
| DL Ducha de emergencia y lavaojos | 300 | 6 | 1 | 0,15 |
| AL-3 Almacén de producto terminado y de cilindros | 150 | 134 | 2 | 0,30 |
| EXP Expedición y muelle P3 | 150 | 82 | 2 | 0,30 |
| S4 Tercerizados revendidos | 150 | 11 | 1 | 0,15 |
| REC Recepción del muelle: mesa de control | 750 | 5 | 1 | 0,15 |
| C-5 Soldadura longitudinal de carros (5) | 300 | 23 | 1 | 0,15 |
| C-4 Punteo del cuerpo ×2 (4) | 300 | 31 | 1 | 0,15 |
| C-3 Cilindrado de carros (3) | 300 | 34 | 1 | 0,15 |
| C-6 Soldadura de cupla en la cúpula (6) | 300 | 20 | 1 | 0,15 |
| C-7 Armado y soldadura circunferencial (7) | 300 | 28 | 1 | 0,15 |
| C-8 Soldadura de accesorios e inspección (8) | 300 | 25 | 1 | 0,15 |
| C-T Terminación de carros | 300 | 21 | 1 | 0,15 |
| C-81 Fabricación de accesorios (8.1) | 300 | 39 | 2 | 0,30 |
| C-9 Prueba hidráulica de carros (9) | 300 | 27 | 1 | 0,15 |
| C-10 Secado de carros | 300 | 10 | 1 | 0,15 |
| C-PP Carros al muelle: a pintura y terminados | 150 | 32 | 1 | 0,15 |

Total: 85 luminarias, 12,8 kW.

## 11. Redes: longitud de tendidos (criterio 4)

| Tablero seccional | kW | Largo desde el TGBT (m) |
|---|---|---|
| N1 | 13,7 | 30,2 |
| N2 | 10,0 | 26,1 |
| N6 | 16,0 | 16,6 |
| N3 | 41,4 | 13,0 |
| N7 | 13,5 | 4,1 |
| N4 | 44,4 | 10,1 |
| N5 | 48,0 | 30,0 |
| S-P | 27,0 | 65,2 |
| S-T | 8,0 | 51,3 |
| EMB | 4,5 | 59,1 |
| C-3 | 7,5 | 32,5 |
| C-4 | 11,0 | 37,3 |
| C-5 | 12,0 | 44,7 |
| C-6 | 6,0 | 50,9 |
| C-7 | 10,0 | 45,8 |
| C-8 | 10,5 | 40,2 |
| C-T | 6,0 | 34,5 |
| C-81 | 5,0 | 61,7 |
| C-9 | 2,0 | 54,0 |
| C-10 | 6,0 | 49,4 |
| SC | 69,0 | 18,1 |
| RC-RD | 1,5 | 77,8 |
| RC-IV | 1,0 | 72,4 |
| RC-PV | 10,5 | 70,4 |
| RC-LB | 0,5 | 68,5 |
| RC-IN | 0,5 | 62,2 |
| RC-PE | 2,0 | 66,8 |
| RC-LQ | 1,5 | 64,7 |
| RC-GA | 1,5 | 61,0 |
| RC-HA | 2,0 | 57,2 |
| RC-PH | 1,0 | 54,1 |

**Agua de PH y pérdidas a PTE**: A07 77 m, B07 74 m, DEC 78 m, T06 34 m (total 263 m).

**Gas natural a hornos**: B14a 64 m, B14b 62 m, B14c 61 m, B14d 59 m, P01 22 m, P03 14 m, P06 11 m, C10 58 m (total 351 m).

**Nitrógeno**: T05 44 m, T13 45 m (total 89 m).

**Gas de soldadura**: M11 7 m, C06 59 m, C08 48 m (total 114 m).


Aire comprimido (anillo, ramales y bajadas de 6 m): 441 m. Potencia instalada de equipos: 394 kW.

## 12. Longitud de los flujos

| Tipo | Flujo | Largo (m) |
|---|---|---|
| MP | Recepción: alero -> P1 -> A1 -> cuarentena (colada, espesor y lote) | 24,4 |
| MP | Hojas aprobadas: cuarentena -> A1 -> AN -> A2 -> paquetes de manuales | 28,7 |
| MP | Paquete a la mesa elevadora (autoelevador de costado por A2, AN y A3) | 40,2 |
| MP | Paquete LAC de carros a la misma mesa elevadora | 34,2 |
| MP | Rollo de fleje al desbobinador (espolón por AN) | 14,9 |
| MP | Atado de caños del cantiléver al cajón del láser (pluma) | 10,1 |
| MP | Barras y caños de carros: A3 -> pasillo central -> PO-CW -> rack del puesto 8.1 | 32,1 |
| MP | Casquetes y cuplas: carros 1 y 2 a los puestos 6 y 7 | 32,1 |
| MP | Big bags de polvo y pintura en polvo (P3 -> AT -> depósito) | 17,1 |
| MP | Big bag de ABC 60 a la estación de la carga (autoelevador) | 2,6 |
| MP | Big bag de ABC 90 a la terminación de carros (AC -> PC -> PO-CN) | 37,0 |
| MP | Pintura en polvo a las tolvas de la cabina (AC -> PC -> PO-PI) | 41,1 |
| MP | Revendidos al rack S4 (P3) | 15,0 |
| SE | Desarrollos a la rampa | 0,2 |
| SE | Carro de plataforma con desarrollos al lado de la roladora | 4,9 |
| SE | Cuerpo de carro al marcado | 0,2 |
| SE | Virola al FCHP | 0,2 |
| SE | Virola a la soldadora | 0,4 |
| SE | Cuerpo soldado al FCHP | 0,3 |
| SE | FCHP lleno al lado del encastre | 1,4 |
| SE | Cuerpos 2,5-10 kg al encastre | 1,3 |
| SE | Tramos 1 kg al carro de cajones | 1,2 |
| SE | Carro de tramos al encastre | 5,3 |
| SE | Tramo al encastre | 0,2 |
| SE | Fleje enderezado | 0,3 |
| SE | Fleje al troquel | 0,3 |
| SE | Cúpulas y fondos a los carros de cajones | 1,4 |
| SE | Carro de cúpulas a la zona de cúpulas | 0,3 |
| SE | Carro de fondos a la zona de fondos | 2,8 |
| SE | Fondos al encastre | 0,3 |
| SE | Celda: numerado -> muesca del cuello -> soldadura de cuello (sin transporte) | 5,6 |
| SE | Cúpulas con cuello a las soldadoras circ. | 2,7 |
| SE | Línea principal: encastre -> bordoneado -> soldadura circ. -> espesor -> PH -> secado -> granallado -> detección | 34,7 |
| SE | Lote rechazado a retenidos | 0,7 |
| SE | Defectuosos a las jaulas | 0,4 |
| SE | Jaula «a corregir» a la corrección | 4,4 |
| SE | Corregidos y a re-granallar: vuelven a los rodillos de entrada | 14,7 |
| TL | Riel aéreo: cuelga en la detección -> precalentamiento -> cabina -> curado -> descarga | 52,6 |
| TL | Riel aéreo: horno de curado 2 en paralelo | 10,1 |
| RET | Retorno de ganchos vacíos a la detección (aéreo) | 36,3 |
| SE | Terminados pintados (con tapón) a la espera de la carga (PO-PI -> AT2) | 30,0 |
| SE | Carro de terminados a la carga | 5,2 |
| SE | Terminación: carga -> ensamblaje -> presurización -> pérdidas -> etiquetado | 11,2 |
| SE | Etiquetado al FCHP del encajonado | 2,3 |
| SE | Terminados a la mesa de encajonado | 0,2 |
| SE | Cilindros vacíos (con tapón de PE) a la mesa de encajonado de al lado | 10,9 |
| PT | Cajas de terminados al pallet | 0,9 |
| PT | Cajas de cilindros al pallet | 0,9 |
| PT | Pallet de cilindros a la envolvedora | 10,1 |
| PT | Pallet de terminados a la envolvedora | 6,2 |
| PT | Pallets al almacén de PT y de cilindros (transpaleta por AT y T2) | 17,9 |
| PT | Expedición (T1 -> muelle P3) | 19,5 |
| PT | Revendidos a expedición | 15,6 |
| SE | Cuerpos grabados de carros (EFE 600 / mesa móvil) a la roladora | 10,1 |
| SE | Cuerpo rolado al pulmón | 0,2 |
| SE | Punteo (2 viradores) | 6,9 |
| SE | Cuerpo punteado al pulmón | 0,4 |
| SE | Pulmón a la soldadura longitudinal | 3,6 |
| SE | Cuerpo soldado al armado (cuna) | 11,0 |
| SE | Cúpula con cupla al armado (carro canasto) | 3,7 |
| SE | Cilindro cerrado a la soldadura de accesorios | 4,0 |
| SE | Kits del puesto 8.1 al carro de kits | 10,4 |
| SE | Recipiente a la inspección de costuras | 2,5 |
| SE | Carro inspeccionado (sobre ruedas) a la PH | 10,2 |
| SE | PH -> secado | 2,4 |
| SE | Secado -> pulmón de despacho a pintura | 0,8 |
| SE | Carros a pintura tercerizada y carros terminados (muelle P3) | 18,1 |
| SE | Carros pintados (vuelven por P3) a la terminación de carros | 27,3 |
| SE | Carga de polvo -> armado de válvula y manguera | 2,7 |
| SE | Armado -> presurización y etiquetado | 0,2 |
| SE | Carro terminado al pulmón del muelle | 5,2 |
| SCRAP | Orillas de la guillotina: autoelevador por el pasillo central, A3, AN y A1 al volquete (P1) | 54,2 |
| SCRAP | Recortes del láser: autoelevador por A3 al volquete (P1) | 39,5 |
| SCRAP | Esqueleto de la prensa: contenedor por PO-3 y AN al volquete (P1) | 37,3 |
| SCRAP | Descartes inutilizados al volquete (PO-3, AN y A1) | 79,3 |

## 13. Supuestos a validar

- Tercerizados revendidos: volumen estimado (no figura en los Excel).
- Retiros, FOS y FOT del parque industrial; ubicación de la celda de media tensión y de la reducción de gas.
- Medidas de diseño (marcadas D con su criterio): confirmar con los proveedores al cotizar.
- Textos normativos marcados como B en el README (Dec. 351/79 arts. 49, 50 y anexo VII; Res. SRT 960/2015): verificar la versión vigente en InfoLEG.
- Recargas se incluye porque figura en el dimensionamiento técnico, aunque no estaba en la lista de secciones del pedido.
