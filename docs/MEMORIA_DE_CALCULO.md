# Memoria de cálculo del layout - planta industrial FLAMA S.A. (año 10 = 2035)

Se genera desde `planta/calculos.py` y `planta/layout.py` (`python generar.py`). Cada número indica su fuente: **DT** = Dimensionamiento_TecnicoV2.xlsx, **MP** = MP_Abastecimiento_Almacenamiento_FLAMA_OpcionD.xlsx, **CC** = Comparacion_corte.xlsx, **X-ALM** = Dimensionamiento_Almacenes_MP_v5.xlsx (MRP del grupo), **W-MAN**, **W-CAR** = Word de proceso de manuales y de carros, **C** = cotización de proveedor, **E** = estimado, **SUP** = supuesto a validar.

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

Recargas: 128.800 u/año (DT), fuera de esta planta desde la v9. Tercerizados revendidos: 10.700 u/año (**SUP**: 12,7 % no ABC sobre las ventas de equipos; no hay dato en los Excel).

Mes pico = 1,40 × promedio (dic-ene). Horas productivas del mes pico: 22 días × 2 turnos × 8 h × 0,85 = 299 h.

| Familia | Tasa de diseño (u/h) |
|---|---|
| 1 kg | 79,0 |
| 2,5-10 kg | 31,8 |
| carros | 1,2 |

## 2. Nave y sectores

Nave de 88 × 44 m = 3.872 m², puestos en el orden y la disposición de los Word de proceso (W-MAN, W-CAR), pórticos de dos luces (19,40 y 24,60 m) cada 8 m, altura libre 8,00 m (Dec. 351/79 exige ≥ 3 m). Recargas se hace fuera de esta planta: en su lugar (ángulo SO) van las oficinas de planta, y administración pasa al lado este, lejos de P1. Anexos: servicios 288 m² y sala técnica 58 m². La nave sigue en 88 × 44: lo que libera recargas (≈ 330 m²) lo ocupan los puestos 10 a 17 de carros (W-CAR: ≈ 520 m² entre secado, pulmón de despacho, cambio de juego, carga, pérdidas, etiquetado, depósito y ensayos) y la calle de PT de 5 m; no alcanza para sacar un módulo de 8 m (352 m²).

| Código | Sector | m² proyectados | m² requeridos | Nota |
|---|---|---|---|---|
| AL-CA | Carros de abastecimiento | 4,8 | - | W-CAR tabla 5: 3 × 1 m para los 2 carros de abastecimiento; salen directo a la senda PP |
| AL-1N | Gasoil del autoelevador | 2,1 | - | Armario de inflamables; el Heli CPCD50 diésel (W-MAN) se estaciona al final del pasillo central |
| AL-MM | Insumos de montaje (manuales) | 14,0 | 13,8 | Dimensionamiento_Almacenes_MP_v5: 31 posiciones, 13,8 m² netos (20,7 brutos); rack de 4 módulos × 2 × 4 niveles = 32: válvulas, manómetros, toberas, mangueras y soportes; salen una vez por turno en el carro de abastecimiento |
| AL-ID | Identificación (etiquetas, obleas, sellos) | 2,0 | 3,0 | Dimensionamiento_Almacenes_MP_v5: 9 lugares, 3,0 m² netos; estantería de 5 niveles; sellos y obleas numerados bajo llave |
| AL-MC | Insumos de montaje (carros) | 3,8 | 2,9 | Dimensionamiento_Almacenes_MP_v5: 7 posiciones, 4,8 m² netos; rack de 1 módulo × 2 × 4 niveles: ruedas, válvulas de carro, manómetros, mangas y precintos (W-CAR 13) |
| AL-CT | Cantiléver de caños y barras (frente a P1) | 11,8 | 11,0 | Dimensionamiento_Almacenes_MP_v5: 11 posiciones a 3 niveles; el atado de 16 caños de 6 m (W-MAN) entra atravesado por P1 y se apoya sin girar; de acá la pluma lo lleva al cajón del láser y las barras de carros salen de a una, a mano, al rack del puesto 8.1 (W-CAR) |
| AL-CU | Cuarentena de MP (compartida manuales y carros) | 25,0 | 25,0 | W-MAN y W-CAR tabla 5: 10 × 2,5 m, demarcada en amarillo: pallets, mesa de inspección de 1,2 × 0,6 y balanza de plataforma de 1,2 × 1,2 m (W-MAN: la misma de carros). X-MAN 2035: 3 operarios de recepción |
| AL-RE | Retenidos de MP (no conforme) | 6,0 | 6,0 | W-CAR tabla 5: 4 × 1,5 m demarcados en rojo, 3 pallets; se reclama al proveedor |
| AL-CH | Chapa LAF de manuales (3 formatos) | 18,3 | - | Dimensionamiento_Almacenes_MP_v5 'Chapa y fleje': hojas 1220 × 2440, 1000 × 2000 y 1500 × 3000 en paquetes de 2 alturas (7 lugares); el autoelevador los toma de costado desde A2 (W-MAN) |
| AL-CC | Chapa LAC de carros | 15,0 | - | W-CAR tabla 5 y v5: 3 posiciones de 3,0 × 1,5 m, 2 paquetes por posición; van a la misma guillotina |
| AL-FL | Flejes LAF de manuales | 8,5 | - | Dimensionamiento_Almacenes_MP_v5: 21 rollos parados en cunas; porta-flejes de 3 niveles × 7 cunas (MP Opción D) |
| AL-SS | Insumos de soldadura y superficie | 5,3 | 4,8 | Dimensionamiento_Almacenes_MP_v5: 12 posiciones, 4,8 m² netos; rack de 1 módulo de 3 pallets × 4 niveles: alambre MAG Ø0,9, granalla, discos y sprays |
| AL-CQ | Casquetes y cuplas de carros | 7,6 | 6,0 | Dimensionamiento_Almacenes_MP_v5: 11 posiciones (4 niveles), 6,0 m² netos; rack de 2 módulos frente a AN; carros 1 y 2 a los puestos 6 y 7 (W-CAR) |
| N1 | Corte de chapa (compartido) y marcado de carros | 56,5 | 53,0 | W-CAR: guillotina CENA 8 × 3200 (≈ 3,9 × 2,1), mesa elevadora 2,6 × 1,8 con 1 m de paso, zona trasera 3,9 × 2,5 (rampa, contenedor y carros) = 44 m²; marcado de carros 3,5 × 2,5 pegado a la rampa = 9 m² |
| N2 | Corte de tubo 1 kg | 29,9 | - | W-MAN: 1 láser (X-MAN); cajón de alimentación de 6,5 m al lado de la máquina, dos posiciones de carro «en llenado» y «vacío» de 1,2 × 0,8 m y contenedor de 1.000 L junto a la máquina |
| N6 | Cilindrado y soldadura longitudinal 2,5-10 kg | 29,3 | - | W-MAN: carro de desarrollos frenado al lado de la roladora, roladora Firesafer FS-RM01 y soldadora longitudinal con el carro FCHP20505 entre las dos (un lado largo hacia cada máquina); pegado a la guillotina (ocupa el ex procesado, que no figura en el Word) |
| N3 | Corte de disco y embutido | 31,0 | - | W-MAN: desbobinador, enderezador y alimentador Cena PRE-1, prensa Sangiacomo; estantería de matrices y carro porta-matrices al lado de la prensa; contenedor de 1.000 L del esqueleto |
| N7 | Celda de cuello: numerado, muesca y soldadura | 37,4 | - | W-MAN: las prensas de muesca van pegadas a la de numerado y a la soldadora de cuello, sin transporte entre las tres; zona de cúpulas al lado |
| N4 | Encastre, bordoneado, soldadura circ., espesor y PH | 94,5 | - | W-MAN y X-MAN: encastre 1, bordoneado 1, soldadura circ. 2, control de espesor 1, PH 2; un FCHP20505 entre cada par de puestos |
| N5 | Secado, granallado y detección | 93,2 | - | W-MAN y X-MAN: secado 4, granallado 1 (de rodillos), detección 1; tres jaulas al lado del puesto; el detector cuelga el cilindro en el riel de pintura |
| N8 | Corrección de defectos | 23,7 | - | W-MAN: los corregibles llegan en un carro desde la jaula «a corregir» y vuelven a los rodillos de entrada de la granalladora; X-MAN: 1 puesto |
| SC | Compresores y colector de humos | 74,9 | - | Reguladores de Arcal 21 y N₂ que vienen de la jaula exterior (puerta PG), colector de humos, 2 compresores de tornillo, secador y pulmón, con 1 m libre alrededor de cada equipo para mantenimiento |
| ST-I | Tableros de la línea este y compresor de la cabina | 26,9 | - | Tablero de N5 y de pintura y compresor sin aceite dedicado a la cabina (pasa del ex LB-2) |
| C-3 | Cilindrado de carros (3) | 37,8 | 35,0 | W-CAR ≈ 7,0 × 5,0 = 35 m²: roladora W12 8 × 1500, zona de carga, EFE 600 y mesa móvil, salida axial y pulmón de cuerpos rolados de 1,8 × 1,2; recibe los cuerpos grabados del marcado por PO-1 |
| C-4 | Punteo del cuerpo (4) | 31,1 | 27,0 | W-CAR ≈ 6,0 × 4,5 = 27 m²; X-CAR 2035: 1 virador (el segundo de la v8 se saca) |
| C-5 | Soldadura longitudinal de carros (5) | 26,0 | 22,0 | W-CAR ≈ 5,5 × 4,0 = 22 m²; zona de carga axial y no conforme en rojo |
| C-6 | Soldadura de cupla en la cúpula (6) | 18,5 | 16,0 | W-CAR ≈ 4,5 × 3,5 = 16 m²; pegado al armado (7); lo hace el operario de punteo |
| C-7 | Armado y soldadura circunferencial (7) | 34,4 | 27,0 | W-CAR ≈ 6,0 × 4,5 = 27 m²: virador, carro canasto de cúpulas, carro 2 de fondos, pulmón de cilindros cerrados y no conforme |
| C-8 | Soldadura de accesorios (8) | 31,3 | 29,0 | W-CAR ≈ 6,5 × 4,5 = 29 m²: virador, carro de kits del lado del 8.1, cuna del lado del 7 (arriba), juegos provisorios contra el fondo y salida al norte; la inspección de costuras la hace el mismo soldador (X-CAR no tiene mesa aparte) |
| C-81 | Fabricación de accesorios (8.1) | 32,2 | 32,0 | W-CAR ≈ 8,0 × 4,0 = 32 m²: rack de barras de 6,5 m sobre la senda PP (las barras de 6 m llegan a mano por la senda y entran al rack sin girarlas), banco con sensitiva, dobladora, taladro y prensa de 20 t; por el fondo pasan los carros del 8 a la PH |
| C-9 | Prueba hidráulica de carros (9) | 23,0 | 22,0 | W-CAR ≈ 5,5 × 4,0 = 22 m²: 2 bandejas con rampa, pantalla, Yukon M-000200, tanque de 1.000 L en circuito cerrado en el rincón del fondo |
| C-10 | Secado de carros (10) | 12,0 | 7,5 | W-CAR ≈ 3,0 × 2,5 = 7,5 m²: secadora eléctrica Melisam MR011, lugar del carro y espera de 2 carros mojados; lo atiende el operario de prueba hidráulica |
| C-11 | Pulmón de despacho a pintura (11) | 63,5 | 60,0 | W-CAR ≈ 10 × 7 = 70 m²: 120 carros secos en filas por modelo y semana (0,5 m² por carro con el paso); salen por el muelle P3 cuando el lote está aprobado en la prueba hidráulica |
| S-P | Pintura en polvo (riel aéreo, horno único) | 286,0 | - | W-MAN: riel transportador aéreo -> horno (precalentamiento) -> cabina con recuperación -> horno (curado 180-220 °C) -> enfriamiento y descarga; X-MAN: un solo equipo de horno; esquema de 22 × 13 m |
| MT | Taller de mantenimiento | 37,2 | 30,0 | Mantenimiento preventivo: bancos, torno, agujereadora, soldadora móvil; entra la transpaleta por el portón del pasillo central; puerta directa al pañol |
| PÑL | Pañol de mantenimiento y de línea | 17,7 | - | Pegado al taller: repuestos críticos, herramental del preventivo, consumibles de soldadura (toberas, puntas, discos) contra vale por la ventanilla al pasillo de oficinas |
| QR | Cuarentena de producto y muestras retenidas | 15,3 | 15,0 | Jaula con llave: lotes rechazados y un cilindro testigo por lote (IRAM 3517 / 3523) |
| OF-C | Pasillo de oficinas | 14,8 | - | Entrada de las oficinas desde el exterior (OF-1, camino peatonal desde SV-1) y paso a la banda sur |
| Q | Laboratorio de calidad | 33,9 | 31,0 | Metrología, ensayo de rotura (1 cilindro por lote, W-MAN), adherencia y espesor de pintura, humedad del polvo, probetas de soldadura de carros; legajos |
| PCP | Planificación y control de la producción | 17,9 | - | 2 puestos y tablero de programación |
| SUP | Supervisor de planta | 24,3 | - | Oficina propia del encargado de turno, con ventana a la banda de carros |
| C-17 | Ensayos de lote de carros (17) | 69,8 | 70,0 | W-CAR ≈ 15,5 × 4,5 = 70 m²: recinto de descarga de 12 × 3 m (alto 3 m) con colector de mangas en el fondo, balanza de plataforma al lado de la puerta del recinto, mesa de medición y perchero de mangas; la rodadura sale al patio por PE-1 |
| C-14 | Sala del ensayo de pérdidas (14) | 25,0 | 25,0 | W-CAR 5 × 5 m de paneles aislantes con puerta, 21 °C (split BGH 3000F y registrador): 30 lugares numerados; al lado de la carga (13) y del recinto de descarga (17) |
| C-15 | Etiquetado e inspección final (15) | 10,2 | 9,0 | W-CAR ≈ 3,5 × 2,5 = 9 m²: 2 lugares de carro, mesa de calcomanías y no conforme; a la salida del 13 |
| C-13 | Carga, armado y presurización de carros (13) | 58,0 | 58,0 | W-CAR ≈ 10 × 6 = 60 m²: estación A (cinta e interior), B (balanza con rampa y Yukon M-000121) con el bastidor del big bag detrás (el autoelevador llega por la calle del PT), batería de N₂ en jaula contra la pared, estación C (manga, traba y precinto) y estanterías |
| C-12 | Pulmón de pintados (12) | 69,0 | 70,0 | W-CAR ≈ 10 × 7 = 70 m²: 120 carros pintados sobre sus ruedas nuevas, al lado de la estación A del 13 |
| C-12C | Recepción de pintados: cambio de juego y rechazados (12) | 23,2 | 9,0 | W-CAR: 2 lugares de cambio de juego de 2,0 × 1,5 m (crique, zorra de retorno y cajones de ejes y ruedas) y rechazados del pintor 2 × 1,5 m en rojo, al lado de la puerta, entre el camión y el pulmón |
| C-16R | Depósito de carros: retenidos y rechazados (16) | 121,4 | 105,0 | W-CAR: retenidos 180 carros ≈ 9 × 10 (amarillo) a la salida del etiquetado y rechazados ≈ 5 × 3 (rojo), separados |
| C-16L | Depósito de carros: liberados (16) | 84,3 | 60,0 | W-CAR: liberados 100 carros ≈ 6 × 10 (verde), hacia la puerta de despacho (calle T y muelle P3) |
| AL-3 | Almacén de producto terminado y de cilindros | 145,5 | - | X-DT Almacén PT 2035: 56 pallets esperando despacho + 72 del stock oct-nov = 128; con un solo autoelevador (W-MAN) dos racks de 7 módulos a 5 niveles sobre una calle de 5 m: 140 posiciones |
| S4 | Tercerizados revendidos | 7,3 | 7,3 | Dimensionamiento_Almacenes_MP_v5 'Almacén de producto terminado': 17 posiciones; rack de 2 módulos × 4 niveles frente a la calle del muelle (CO₂, agua, AFFF, clase K y agente limpio) |
| EXP | Calle del muelle y expedición (P3) | 68,0 | - | Un solo muelle con rampa niveladora (P3 queda para despachar, la MP entra por P1): sale PT, cilindros y carros (a pintura y terminados); vuelven los carros pintados. Expedición 13 a 17 h |
| DP | Depósito de polvo químico (único de la planta) | 12,6 | 12,6 | Dimensionamiento_Almacenes_MP_v5: 11 posiciones, 8,4 m² netos, 12,6 brutos; cerrado y seco: big bags de ABC 60 y ABC 90, polvo D y pintura en polvo; llegan de P1 por la calle del muelle y AT; salen a la carga (norte), a carros (AT y calle del PT) y a pintura (oeste) |
| S-T | Terminación 1 a 10 kg | 55,0 | - | W-MAN: carga (estación de big bag y transportador neumático) -> ensamblaje -> presurización -> ensayo de pérdidas -> etiquetado, con un FCHP20505 entre cada par de puestos; termina en el embalaje |
| EMB | Embalaje y paletizado (vacíos y terminados) | 71,0 | - | W-MAN: los vacíos se encajonan al lado de la descarga de pintura y los terminados al final de la terminación, en la misma zona: armadora de cajas, 2 mesas de encajonado (X-MAN) y envolvedora EDOS PS5 |
| AL-EB | Embalaje: cajas plegadas, film y pallets | 23,1 | 17,8 | Dimensionamiento_Almacenes_MP_v5: 50 posiciones, 22,2 m² netos; rack de 6 módulos × 2 × 4 niveles = 48 + pila de pallets vacíos junto a la envolvedora; las cajas van a la armadora con la transpaleta |
| PU-9 | Terminados pintados esperando la carga | 7,3 | - | W-MAN: van de la descarga a la carga en sus carros; el Word no dimensiona el pulmón: 1 carro |
| DL | Ducha de emergencia y lavaojos | 6,0 | - | A menos de 10 s de la carga de polvo, de la presurización y de la descarga de pintura |

Almacenes: los dimensiona el grupo en el MRP (X-ALM v5, con la planilla de plazos de entrega); el plano ubica cada sección con al menos su superficie neta o sus posiciones. Una sola recepción de MP con cuarentena compartida con carros (W-MAN, W-CAR). Calles de 5,0 m para el Heli CPCD50 (W-CAR tabla 5).

| Sección (X-ALM) | Posiciones | m² netos | m² brutos | Sector del plano | m² en el plano | Cómo se guarda |
|---|---|---|---|---|---|---|
| Chapa y fleje (manuales) | 28 | 38,7 | 58,0 | AL-CH + AL-FL | 26,8 | hojas a piso (2 alturas); fleje en porta-flejes de 3 niveles |
| Calle de chapa (carros) | 3 | 9,0 | 13,5 | AL-CC | 15,0 | pilas a piso de 2 alturas, acceso de costado desde A2 |
| Cantilever de caños y barras | 11 | 30,0 | 45,0 | AL-CT | 11,8 | cantiléver de 3 niveles al fondo de A1, frente a P1 |
| Rack de casquetes y cuplas (carros) | 11 | 6,0 | 9,0 | AL-CQ | 7,6 | rack de 2 módulos × 4 niveles frente a AN |
| Insumos de montaje (manuales) | 31 | 13,8 | 20,7 | AL-MM | 14,0 | rack de 4 módulos × 4 niveles frente a A1 |
| Rack de insumos de montaje (carros) | 7 | 4,8 | 7,2 | AL-MC | 3,8 | rack de 1 módulo × 4 niveles frente a A1 |
| Identificación | 9 | 3,0 | 4,5 | AL-ID | 2,0 | estantería de 5 niveles, sellos bajo llave |
| Insumos de soldadura y superficie | 12 | 4,8 | 7,2 | AL-SS | 5,3 | rack de 3 pallets × 4 niveles frente a AN |
| Depósito de polvo químico | 11 | 8,4 | 12,6 | DP | 12,6 | local cerrado y seco junto a la carga |
| Embalaje | 50 | 22,2 | 33,3 | AL-EB | 23,1 | rack de 6 módulos × 4 niveles sobre AT |
| Almacén de producto terminado | 17 | 9,6 | 14,4 | S4 | 7,3 | revendidos: rack de 2 módulos × 4 niveles |
| Jaula de gases | 12 | 10,5 | 15,8 | JG | 15,8 | jaula exterior con packs y manifold (W-MAN) |
| Procesado: cuerpos cortados y cúpulas y fondos embutidos | 42 | 50,5 | 75,8 | PU-FO + PU-CU | 18,6 | sólo los pulmones de W-MAN (zonas de fondos y de cúpulas); el resto del procesado no se agrega (v9) |

X-ALM redondea cada ítem a lugares enteros (sin compartir columna). Donde el plano tiene menos m² netos (fleje, insumos de carros, identificación) las posiciones entran igual: el fleje va en porta-flejes de 3 niveles en lugar de pallets a piso, y los ítems chicos comparten columna de rack o estantería. El área bruta de X-ALM (× 1,5 de circulación) queda reemplazada por las calles de 5 m del plano, por eso el almacén de MP ocupa más que la suma de las áreas brutas.


## 3. Recepción de MP y análisis de peso de la carga

Se dimensiona para la carga máxima: un semirremolque de 18,6 m y 30 t o dos chasis de 10 m en el alero de descarga norte (32 × 11,6 m), playos y con el costado libre (W-CAR), con descarga por ambos lados con el autoelevador. La nave tiene dos portones: P1 de 7,0 m (toda la MP de manuales y carros, también polvo, pintura, embalaje y revendidos, con una sola cuarentena, W-MAN; el atado de 6 m entra atravesado y se apoya en el cantiléver sin girar) y el muelle único P3 (sólo despacho: PT, carros al pintor y liberados, 13 a 17 h). P2 (recargas) se suprimió con recargas. Los packs de gases se cambian desde el patio norte en la jaula exterior JG. Los camiones entran por G1 (garita y báscula) y salen por G3.

| Formato | Largo (m) | Carga útil (t) | PBT (t) | Descarga |
|---|---|---|---|---|
| Semirremolque playo 3+3 ejes | 18,6 | 30,0 | 45,0 | Alero de descarga norte: autoelevador por los dos lados; entra por P1 a la cuarentena (A1) |
| Camión chasis con balancín (3 ejes) | 11,0 | 16,0 | 26,0 | Alero de descarga norte (junto al semi): autoelevador por los dos lados, bajo techo |
| Camión chasis 2 ejes | 9,5 | 9,0 | 16,5 | Alero norte (P1) o jaula de gases según el material |
| Utilitario de reparto | 6,0 | 1,5 | 3,5 | Expedición de PT por el muelle P3 (rampa; DT Almacén PT: 8 vehículos) |

| Proveedor / material | t por entrega | Entregas/año | Vehículo | Portón | Destino |
|---|---|---|---|---|---|
| Pradecon: hojas + fleje 0,9 | 35,26 | 18,1 | Semi (máx.) o 2 chasis quincenales | Alero + P1 | AL-CU -> AL-CH y AL-FL |
| Pacheco: flejes 1,25-2,0 y chapa LAC | 5,05 | 29,3 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-FL y AL-CC |
| Metalprisa: caño Ø76,2 | 4,23 | 28,9 | Chasis 2 ejes | Alero + P1 (atado atravesado) | AL-CU -> AL-CT |
| Eli-Met: cuellos y roscas | 3,68 | 5,6 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-MM |
| Soldadura: alambre MAG | 1,89 | 8,1 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-SS |
| Air Liquide: Arcal 21 (packs) | 3,80 | 15,6 | Chasis 2 ejes | Jaula exterior JG | JG -> reguladores CG1 |
| Air Liquide: N₂ (packs) | 3,80 | 15,6 | Chasis 2 ejes | Jaula exterior JG | JG -> reguladores CG1 |
| Polvo químico (Polvex / DEMSA) | 13,13 | 31,0 | Chasis con balancín | Alero + P1 | AL-CU -> DP |
| Válvulas, manómetros y pescantes | 8,16 | 8,3 | Chasis con balancín | Alero + P1 | AL-CU -> AL-MM |
| Casquetes de carros | 5,93 | 4,1 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-CQ |
| Estructuras y ruedas de carros | 5,52 | 15,1 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-MC |
| Embalaje, pallets, etiquetas y precintos | 4,61 | 15,3 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-EB y AL-ID |
| Tercerizados revendidos | 3,00 | 24,0 | Chasis 2 ejes (SUPUESTO) | Alero + P1 | AL-CU -> S4 |
| CYM: granalla | 3,11 | 2,0 | Chasis 2 ejes | Alero + P1 | AL-CU -> AL-SS |
| Pintura electrostática en polvo | 0,79 | 8,3 | Chasis 2 ejes | Alero + P1 | AL-CU -> DP |

Pradecon entrega 35,3 t por mes (hojas + fleje 0,9): supera la carga útil de un semi. Se parte en 2 entregas quincenales de 17,6 t, que entran en un chasis con balancín y bajan el stock máximo de chapa medio mes.

Capacidad residual del autoelevador con un paquete de hoja de 1500 × 3000 mm y 2 t (Q = Qn · (cn + d) / (c + d), d = 0,45 m):

| Nominal (c = 500 mm) | Por el lado largo (c = 750 mm) | Por el lado corto (c = 1500 mm) |
|---|---|---|
| 2,5 t | 1,98 t | 1,22 t |
| 3,0 t | 2,38 t | 1,46 t |
| 3,5 t | 2,77 t | 1,71 t |

Se adopta el autoelevador de W-MAN: Heli CPCD50 K2 diésel de 5 t, compartido entre la MP de manuales y la de carros, con uñas largas, prolongadores para los atados, espolón para los rollos y pluma para los big bags y los atados (Mecánica Porta). Con 5 t nominales toma el paquete de 2 t por cualquier lado. Es el único autoelevador de la planta (W-CAR: compartido): también ubica el PT en los racks de 5 niveles y carga en el muelle. El embalaje tiene una transpaleta eléctrica con una manual de respaldo (W-MAN).

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

Sólo los pulmones y almacenes intermedios que figuran en W-MAN y W-CAR, con la capacidad que dan los Word; no se agregó ninguno (se quitaron el almacén de procesado y el de vacíos de la v8).

| Pulmón | Qué guarda | De | A | Carros / u. de manejo | m² | Fuente |
|---|---|---|---|---|---|---|
| PU-1 | Rampa trasera: carro de plataforma de desarrollos (W-MAN, en llenado) y carro de salida de cuerpos de carros (W-CAR) | 1 Guillotina | 6 Cilindrado / C2.1 marcado | 2 | 4,8 | W-MAN 1 y W-CAR 2 |
| PU-M | EFE 600 (25 y 50 kg) y mesa móvil (70 y 100 kg) con cuerpos grabados | C2.1 Marcado | C3 Cilindrado de carros | 2 | 3,9 | W-CAR 2.1 |
| PU-D | Carro de plataforma con desarrollos frenado al lado de la roladora | 1 Guillotina | 6 Cilindrado | 1 | 1,4 | W-MAN 1 |
| PU-V1 | Carro FCHP20505 (3 planos de 1280 × 610 mm): virolas (el segundo carro es el de cambio de formato) | 6 Cilindrado | 7 Sold. longitudinal | 1 | 0,8 | W-MAN 6 |
| PU-V2 | Carro FCHP20505 (3 planos de 1280 × 610 mm): cuerpos soldados (se llena) | 7 Sold. longitudinal | 9 Encastre | 1 | 0,8 | W-MAN 7 |
| PU-V3 | Carro FCHP20505 (3 planos de 1280 × 610 mm): cuerpos soldados (al lado del encastre) | 7 Sold. longitudinal | 9 Encastre | 1 | 0,8 | W-MAN 7 |
| PU-FX | Carro FCHP20505 (3 planos de 1280 × 610 mm): carros de cambio de formato (W-MAN: cilindrado, encastre y bordoneado, uno por tramo) | Cambio de formato | 6, 9 y 10 | 3 | 3,3 | W-MAN 7 (cambio de formato) |
| PU-T1 | Carros de estantes de 12 cajones: tramos «en llenado» y «vacío» | 2 Corte de tubo | 9 Encastre | 2 | 2,3 | W-MAN 2 |
| PU-T2 | Carros de estantes de 12 cajones: tramos «en consumo» y «lleno» | 2 Corte de tubo | 9 Encastre | 2 | 2,5 | W-MAN 2 |
| PU-K | Carros de estantes de 12 cajones: cúpulas y fondos en llenado | 3 Embutido | Zonas de cúpulas y de fondos | 2 | 3,1 | W-MAN 3 |
| PU-FO | Zona de fondos: 3 a 5 carros (W-MAN, colchón de la tanda) | 3 Embutido | 9 Encastre | 4 | 6,8 | W-MAN 3 (3 a 5 carros) |
| PU-CU | Zona de cúpulas: carros numerados por orden de llegada (3 a 5, igual que la de fondos) | 3 Embutido | 5 Numerado | 4 | 11,8 | W-MAN 3 (3 a 5 carros) |
| PU-CC2 | Carros de estantes de 12 cajones: cúpulas con cuello (en llenado) | 8 Sold. de cuello | 11 Sold. circunferencial | 1 | 1,7 | W-MAN 8 |
| PU-CC | Carros de estantes de 12 cajones: cúpulas con cuello (en consumo; W-MAN: dos carros alternándose) | 8 Sold. de cuello | 11 Sold. circunferencial | 1 | 1,7 | W-MAN 8 |
| PU-E | Carro FCHP20505 (3 planos de 1280 × 610 mm) | 9 Encastre | 10 Bordoneado | 1 | 0,8 | W-MAN 9 |
| PU-B | Carro FCHP20505 (3 planos de 1280 × 610 mm) | 10 Bordoneado | 11 Sold. circunferencial | 1 | 0,8 | W-MAN 10 |
| PU-S | Carro FCHP20505 (3 planos de 1280 × 610 mm): tarjeta «espesor OK» | 11 Sold. circunferencial | 13 PH | 1 | 0,8 | W-MAN 12 |
| PU-RT | Retenidos (zona demarcada en rojo) | 12 Control de espesor | 13 PH o scrap | 2 | 3,0 | W-MAN 12 |
| PU-6 | Cilindros probados (mojados) en sus carros | 13 PH | 14 Secado | 2 | 4,5 | W-MAN 13 |
| PU-7 | Cilindros secos con tapón: al lado de la boca de entrada | 14 Secado | 15 Granallado | 2 | 4,5 | W-MAN 14 |
| PU-CO | Carro de corregibles (W-MAN) | 16 Detección | 17 Corrección | 1 | 1,0 | W-MAN 16 y 17 |
| PU-F1 | Carro FCHP20505 (3 planos de 1280 × 610 mm) | 19 Carga de polvo | 20 Ensamblaje | 1 | 0,8 | W-MAN 13 a 17 (un carro entre cada par) |
| PU-F2 | Carro FCHP20505 (3 planos de 1280 × 610 mm) | 20 Ensamblaje | 21 Presurización | 1 | 0,8 | W-MAN 13 a 17 (un carro entre cada par) |
| PU-F3 | Carro FCHP20505 (3 planos de 1280 × 610 mm) | 21 Presurización | 22 Ensayo de pérdidas | 1 | 0,8 | W-MAN 13 a 17 (un carro entre cada par) |
| PU-F4 | Carro FCHP20505 (3 planos de 1280 × 610 mm) | 22 Ensayo de pérdidas | 23 Etiquetado | 1 | 0,8 | W-MAN 13 a 17 (un carro entre cada par) |
| PU-F5 | Carro FCHP20505 (3 planos de 1280 × 610 mm): etiqueta hacia afuera | 23 Etiquetado | 24 Encajonado | 1 | 0,8 | W-MAN 13 a 17 (un carro entre cada par) |
| PU-TP | Carro de terminados pintados (con tapón de silicona) | 18 Descarga de pintura | 19 Carga de polvo | 1 | 0,8 | W-MAN 18 |
| PU-CI | EFE 600 y mesa móvil frente a la zona de carga | C2.1 Marcado | C3 Cilindrado | 2 | 2,4 | W-CAR 2.1 |
| PU-CR | Pulmón de cuerpos rolados y tiras (1,8 × 1,2, amarillo) | C3 Cilindrado | C4 Punteo | 1 | 2,2 | W-CAR 3 |
| PU-CP | Pulmón de cuerpos punteados (1,6 × 1,2) | C4 Punteo | C5 Sold. longitudinal | 1 | 2,2 | W-CAR 4 |
| PU-NC5 | No conforme (1,0 × 0,8, rojo) | C5 Sold. longitudinal | Reparación o scrap | 1 | 0,8 | W-CAR 5 |
| PU-K1 | Carro 1: cúpulas y cuplas (1,07 × 0,7) | AL-CQ | C6 Cupla | 1 | 0,8 | W-CAR 6 |
| PU-C6 | Carro canasto de salida (1,1 × 0,7) | C6 Cupla | C7 Armado | 1 | 0,8 | W-CAR 6 |
| PU-F7 | Carro 2 de fondos (1,1 × 0,7) | AL-CQ | C7 Armado | 1 | 0,8 | W-CAR 7 |
| PU-C7 | Pulmón de cilindros cerrados (1,5 × 1,2) | C7 Armado | C8 Accesorios | 1 | 1,8 | W-CAR 7 |
| PU-NC7 | No conforme de los puestos 6 y 7 (0,7 × 0,6, rojo) | C6 y C7 | Reparación o scrap | 1 | 0,4 | W-CAR 7 |
| PU-CK | Carro de kits (≈ 10 kits) | C8.1 Accesorios | C8 Accesorios | 1 | 0,5 | W-CAR 8.1 |
| PU-JP | Juegos provisorios de eje y ruedas: 3 estanterías de ruedas y 3 cajones de ejes (vuelven de la recepción de pintados) | C12 Cambio de juego | C8 Accesorios | 3 | 3,3 | W-CAR 8 |
| PU-S8 | Salida: carro sobre su juego provisorio (amarillo) | C8 Accesorios | C9 Prueba hidráulica | 1 | 0,8 | W-CAR 8 |
| PU-10 | Espera de carros mojados (2) y lugar del carro que se seca | C9 Prueba hidráulica | C10 Secado | 2 | 2,6 | W-CAR 9 y 10 |
| PU-11 | Carros secos con la boca tapada, en filas por modelo y semana | C10 Secado | Muelle P3 -> pintura tercerizada | 120 | 56,3 | W-CAR 11 |
| PU-RP | Rechazados del pintor (≈ 2 × 1,5, rojo) | Muelle P3 | Vuelven al pintor | 2 | 3,8 | W-CAR 12 |
| PU-12 | Carros pintados sobre sus ruedas nuevas, en filas por modelo y lote | C12 Cambio de juego | C13 Carga | 120 | 62,4 | W-CAR 12 |
| PU-14 | Lugares numerados de la sala (30 carros de la muestra) | C13 Carga | C15 / C17 | 30 | 17,6 | W-CAR 14 |
| PU-15 | Lugar del carro que se etiqueta (2 × 1,0 × 0,8) | C13 Carga | C16 Retenidos | 2 | 2,0 | W-CAR 15 |
| PU-NC15 | No conforme de la inspección final (rojo) | C15 Etiquetado | C13 | 1 | 1,2 | W-CAR 15 |
| PU-16R | Retenidos: tarjeta amarilla (180 carros, filas por modelo y lote) | C15 Etiquetado | Liberados o rechazados | 180 | 84,3 | W-CAR 16 |
| PU-16X | Rechazados del lote: tarjeta roja (≈ 5 × 3) | Retenidos | Revisión al 100 % en el 13 | 15 | 13,5 | W-CAR 16 |
| PU-16L | Liberados: tarjeta verde (100 carros) | Retenidos | Muelle P3 -> clientes | 100 | 76,8 | W-CAR 16 |

Tiempo por viaje = 2 × distancia / velocidad + tiempo fijo de toma y entrega. Distancias medidas sobre los recorridos del modelo; día pico 2035.

| Unidad de carga | Medio | Recorrido | Viajes/día | m | min/viaje | min/día |
|---|---|---|---|---|---|---|
| Paquete de hojas ≤ 2 t | Autoelevador | Alero -> P1 -> A1 -> cuarentena | 0,6 | 27 | 2,1 | 1 |
| Paquete aprobado | Autoelevador | Cuarentena -> A1 -> AN -> A2 -> AL-CH | 0,5 | 27 | 2,1 | 1 |
| Paquete LAF a la guillotina y vuelta | Autoelevador | AL-CH -> A2, AN y A3 -> mesa elevadora | 1,0 | 37 | 2,3 | 2 |
| Paquete LAC a la guillotina y vuelta | Autoelevador | AL-CC -> mesa elevadora | 0,3 | 31 | 2,2 | 1 |
| Rollo de fleje 0,5-1,9 t | Autoelevador | Porta-flejes -> AN -> desbobinador | 1,1 | 13 | 1,8 | 2 |
| Atado de caños Ø76,2 | Autoelevador | Cantiléver -> cajón del láser (pluma) | 3,3 | 26 | 2,1 | 7 |
| Barra de 6 m de carros (≤ 23,9 kg) | A mano | Cantiléver -> PP -> rack del puesto 8.1 (de a una, W-CAR) | 8,6 | 84 | 4,0 | 34 |
| Casquetes y cuplas (carros 1 y 2) | Carro a mano | AL-CQ -> puestos 6 y 7 | 2,0 | 70 | 3,4 | 7 |
| Contenedor de orillas (guillotina) | Autoelevador | Guillotina -> volquete (P1) | 0,2 | 56 | 2,8 | 1 |
| Contenedor de recortes (láser) | Autoelevador | Láser -> A3 -> volquete (P1) | 0,2 | 42 | 2,4 | 0 |
| Contenedor del esqueleto (ruedas) | Carro a mano | Prensa -> PO-3 -> AN -> volquete | 1,0 | 39 | 2,1 | 2 |
| Big bag de polvo 1 t / pintura / embalaje | Autoelevador | P1 -> cuarentena -> PC -> calle T -> DP y AL-EB | 1,7 | 100 | 3,7 | 6 |
| Big bag de ABC 60 | Autoelevador | DP -> estación de la carga (19) | 1,3 | 3 | 1,6 | 2 |
| Big bag de ABC 90 | Autoelevador | DP -> AT -> calle T -> T-PT -> bastidor de carros (13) | 0,4 | 30 | 2,2 | 1 |
| Caja de pintura en polvo | Transpaleta | DP -> AC -> PC -> PO-PI -> tolvas | 0,6 | 43 | 2,8 | 2 |
| Pallet de cilindros vacíos | Transpaleta | Mesa de vacíos -> envolvedora | 6,0 | 10 | 1,4 | 9 |
| Pallet de terminados | Transpaleta | Mesa de terminados -> envolvedora | 2,0 | 6 | 1,3 | 2 |
| Pallet de PT | Transpaleta | Envolvedora -> AT -> calle T -> T-PT (pie del rack) | 8,0 | 19 | 1,8 | 14 |
| Pallet de PT | Autoelevador | Ubica en el rack; rack -> T-PT -> calle T -> muelle P3 | 8,0 | 17 | 1,9 | 15 |
| Pallet de revendidos | Autoelevador | S4 -> calle T -> muelle P3 | 0,2 | 14 | 1,8 | 0 |
| Carro rodante seco (rueda) | Carro a mano | Secado -> pulmón de despacho PU-11 | 20,0 | 1 | 0,6 | 11 |
| Carro rodante al pintor (rueda) | Carro a mano | PU-11 -> senda del PC -> calle T -> muelle P3 | 20,0 | 26 | 1,6 | 32 |
| Carro rodante pintado (rueda) | Carro a mano | Muelle P3 -> calle T -> cambio de juego (12) | 20,0 | 16 | 1,2 | 23 |
| Carro rodante terminado (rueda) | Carro a mano | 13 -> etiquetado (15) -> retenidos (16) | 20,0 | 8 | 0,8 | 17 |
| Carro rodante liberado (rueda) | Carro a mano | Retenidos -> liberados -> calle T -> muelle P3 | 20,0 | 37 | 2,0 | 41 |
| Carro de kits (≈ 10 kits) | Carro a mano | Puesto 8.1 -> puesto 8 | 2,0 | 2 | 0,6 | 1 |
| FCHP de cuerpos 2,5-10 kg (63 a 120 u) | Carro a mano | PU-V3 -> 9 encastre | 6,0 | 1 | 0,5 | 3 |
| Carro de 12 cajones de tramos (420 u) | Carro a mano | PU-T1 -> PU-T2 (encastre) | 3,0 | 6 | 0,8 | 2 |
| Carro de 12 cajones de fondos | Carro a mano | PU-K -> zona de fondos | 2,0 | 3 | 0,6 | 1 |
| Carro de 12 cajones de cúpulas | Carro a mano | PU-K -> zona de cúpulas | 2,0 | 0 | 0,5 | 1 |
| Carro de cúpulas con cuello | Carro a mano | PU-CC2 -> PU-CC (sold. circ.) | 3,0 | 5 | 0,7 | 2 |
| Carro de cilindros, 9 tramos 9 -> 17 | Carro a mano | entre pasos (prom. por tramo) | 126,0 | 4 | 0,7 | 83 |
| Carro de terminados pintados | Carro a mano | Descarga -> PO-PI -> AT2 -> PU-TP | 3,5 | 32 | 1,8 | 6 |
| Carro de cilindros vacíos | Carro a mano | Descarga -> mesa de vacíos | 10,5 | 11 | 1,0 | 10 |
| Zorra de consumibles y cajas (vuelta) | Zorra milk run | AL-CA -> puestos -> AL-CA | 4,0 | 160 | 7,2 | 29 |

Ocupación sobre un turno útil de 408 min: autoelevador (único) 10 %, transpaleta 7 %. Entre pasos se mueven 14 carros FCHP20505 por día y por tramo: W-MAN pone un carro entre cada par de puestos y lo empuja el operario que cierra el lote, sin tren logístico; al norte de la senda no entra el autoelevador. El riel aéreo lleva el cilindro de la detección a la descarga de pintura (85 m cargado, que pasa dos veces por el único horno, y 36 m de retorno de ganchos vacíos). Los carros rodantes ruedan sobre sus ruedas: del pulmón PU-11 cruzan el PC por la senda y bajan por la calle T al muelle P3. W-CAR supone una planta sin muelle (tarima con topes y autoelevador); con el muelle P3 suben rodando, y la tarima queda para camiones que no lleguen al muelle. El abastecedor hace el milk run con los 2 carros de abastecimiento (AL-CA, W-CAR) una vez por turno.

| Portón | Qué entra o sale | Vehículo | Frecuencia | Horario |
|---|---|---|---|---|
| P1 (7,0 m) + alero | Entra toda la MP: hojas, flejes, caños y barras de 6 m (atravesados), casquetes, insumos, alambre, granalla, polvo, pintura, embalaje y revendidos (una sola recepción con cuarentena); sale el scrap | Semi / chasis | ≈ 4,1 camiones por semana | 7 a 10 h |
| Jaula JG (PG) | Cambio de packs de Arcal 21 y N₂ desde el patio norte | Chasis 2 ejes | ≈ 0,6 por semana | 7 a 10 h |
| P3 (muelle) | Sale el PT (pallets y carros liberados) y los carros al pintor; vuelven los carros pintados. No entra MP | Semi / chasis / utilitarios de reparto | 7 PT + 2 viajes de carros por semana (W-CAR 11) | 13 a 17 h |
| PP-1 | Personal: vestuarios <-> senda de la nave | A pie | 44 personas, 2 turnos | Entrada y salida |

Gases (W-MAN): packs de 12 cilindros de Arcal 21 y de N₂ con manifold en la jaula exterior JG, detrás de la sala SC; los reguladores CG1 están en el extremo oeste de la sala: 185 m de cañería (recorrido ortogonal) a las 9 soldadoras, contra 193 m desde el centro de la sala. La carga de carros (W-CAR 13) tiene su propia batería de N₂ en jaula.

| Soldadora | m desde los reguladores CG1 |
|---|---|
| B03 | 27,8 |
| M11 | 7,4 |
| A06 | 15,3 |
| B06 | 12,9 |
| C02s | 11,4 |
| C04 | 19,6 |
| C06 | 24,0 |
| C05 | 30,8 |
| C08 | 35,6 |
## 6. Cruces de flujos y de hilos

Cruces entre flujos de MP, SE y PT (verificación geométrica sobre el modelo): **98**. Cruces de hilos de personal con flujos: todos dentro de las **37** sendas peatonales señalizadas (X1 a X37).

## 7. Sanitarios, vestuarios y servicios (Dec. 351/79 arts. 49 y 50)

Turno más numeroso: 40 hombres (32 del turno mañana + 8 choferes) y 4 mujeres. Fuente: DT Servicios y oficinas y Dotación planta 2035, menos los 16 operarios de recargas del turno mañana, los 2 del turno tarde y la atención de recargas (el proceso va fuera de esta planta).

| Artefacto | H requerido | H proyectado | M requerido | M proyectado |
|---|---|---|---|---|
| inodoros | 2 | 3 | 1 | 1 |
| lavabos | 4 | 6 | 1 | 1 |
| orinales | 4 | 6 | 0 | 0 |
| duchas | 2 | 3 | 1 | 1 |

Armarios: H 39 requeridos / 42 proyectados; M 5 / 9 (vestuario de mujeres al 20 % de la dotación). Lockers individuales, 1 por empleado, en bloques de 7 columnas × 3 filas. El bloque de servicios quedó con holgura al salir recargas (podría achicarse un bloque de lockers y una ducha). Un sanitario accesible con ducha en el bloque de servicios y otro en administración (Ley 24.314, Dec. 914/97: círculo libre de Ø 1,50 m, espacio lateral de 0,80 m, barras); los sanitarios de planta (banda sur, sobre la calle AT2) son de hombres y de mujeres. Espacio de cuidado no obligatorio (Dec. 144/2022 exige 100 o más personas; la dotación es 52). Comedor de 30 plazas (DT Servicios); sin recargas alcanzaría con 18 por tanda.

| Local | m² |
|---|---|
| SV-LU Utilitarios de limpieza | 10,3 |
| SV-HY Higiene y seguridad, medicina laboral, primeros auxilios y EPP | 16,7 |
| SV-AC Sanitario accesible con ducha | 13,7 |
| SV-HA Hall, recepción y fichado | 24,7 |
| SV-PL Pasillo limpio a la planta (PP-1) | 26,7 |
| SV-VH Vestuario hombres (42 lockers) | 25,2 |
| SV-DH Duchas hombres | 18,2 |
| SV-SH Inodoros, mingitorios y lavabos hombres | 26,0 |
| SV-VM Vestuario mujeres (9 lockers) | 15,8 |
| SV-SM Inodoro y lavabo mujeres | 9,7 |
| SV-DM Ducha mujeres | 9,7 |
| SV-CM Comedor (30 plazas) y office | 70,0 |
| SN-H Sanitarios hombres (planta) | 17,4 |
| SN-M Sanitario mujeres (planta) | 7,8 |
| AD-OF Administración: compras, ventas y RRHH | 52,6 |
| AD-HA Hall y recepción de visitas | 31,1 |
| AD-SA Sanitario accesible de administración | 9,6 |

## 8. Medios de escape (Dec. 351/79 anexo VII)

Factor de ocupación industrial 16 m²/persona: N = 242 personas teóricas; n = N/100 -> 3 unidades de ancho de salida (1,55 m mínimos). Proyectado: 8 salidas de emergencia de 1,10 m (8,80 m) con barral antipánico, más los portones con puerta de hombre y el paso a servicios.

Recorrido real máximo hasta una salida, calculado sobre una grilla de 0,5 m que rodea los equipos: **33,2 m** (punto x = 42,5, y = 12,0), por debajo de los 40 m que se toman como límite (verificar el artículo vigente).

## 9. Protección contra incendio

Extintores ABC de 10 kg en la nave: **20** (mínimo por superficie 1 cada 200 m² = 20), ubicados por cálculo para que ningún punto quede a más de 20 m de recorrido (IRAM 3517-2:2020, fuego clase A). Se suman 10 en anexos y exteriores, CO₂ junto a tableros y un carro de 50 kg ABC en pintura y en la sala de polvo. Señalización con chapa baliza y cartel en altura (IRAM 3517-2 cap. 7). La reserva de agua contra incendio y la red de hidrantes quedan previstas en el terreno y se confirman con el estudio de carga de fuego.

## 10. Iluminación (método de los lúmenes)

Luminaria LED de 150 W y 21.000 lm; factor de utilización 0,65; mantenimiento 0,80. Niveles: nave 300 lx, depósitos 150 lx, pintura 500 lx, laboratorio 750 lx; soldadura y montaje fino 500 lx y líquidos penetrantes 750 lx con iluminación localizada.

| Sector | lx | m² | Luminarias | kW |
|---|---|---|---|---|
| AL-CA Carros de abastecimiento | 150 | 5 | 1 | 0,15 |
| AL-1N Gasoil del autoelevador | 300 | 2 | 1 | 0,15 |
| AL-MM Insumos de montaje (manuales) | 150 | 14 | 1 | 0,15 |
| AL-ID Identificación (etiquetas, obleas, sellos) | 150 | 2 | 1 | 0,15 |
| AL-MC Insumos de montaje (carros) | 150 | 4 | 1 | 0,15 |
| AL-CT Cantiléver de caños y barras (frente a P1) | 150 | 12 | 1 | 0,15 |
| AL-CU Cuarentena de MP (compartida manuales y carros) | 750 | 25 | 2 | 0,30 |
| AL-RE Retenidos de MP (no conforme) | 750 | 6 | 1 | 0,15 |
| AL-CH Chapa LAF de manuales (3 formatos) | 150 | 18 | 1 | 0,15 |
| AL-CC Chapa LAC de carros | 150 | 15 | 1 | 0,15 |
| AL-FL Flejes LAF de manuales | 150 | 9 | 1 | 0,15 |
| AL-SS Insumos de soldadura y superficie | 150 | 5 | 1 | 0,15 |
| AL-CQ Casquetes y cuplas de carros | 150 | 8 | 1 | 0,15 |
| N1 Corte de chapa (compartido) y marcado de carros | 300 | 56 | 2 | 0,30 |
| N2 Corte de tubo 1 kg | 300 | 30 | 1 | 0,15 |
| N6 Cilindrado y soldadura longitudinal 2,5-10 kg | 300 | 29 | 1 | 0,15 |
| N3 Corte de disco y embutido | 300 | 31 | 1 | 0,15 |
| N7 Celda de cuello: numerado, muesca y soldadura | 300 | 37 | 2 | 0,30 |
| N4 Encastre, bordoneado, soldadura circ., espesor y PH | 300 | 94 | 3 | 0,45 |
| N5 Secado, granallado y detección | 300 | 93 | 3 | 0,45 |
| N8 Corrección de defectos | 300 | 24 | 1 | 0,15 |
| SC Compresores y colector de humos | 300 | 75 | 3 | 0,45 |
| ST-I Tableros de la línea este y compresor de la cabina | 300 | 27 | 1 | 0,15 |
| C-3 Cilindrado de carros (3) | 300 | 38 | 2 | 0,30 |
| C-4 Punteo del cuerpo (4) | 300 | 31 | 1 | 0,15 |
| C-5 Soldadura longitudinal de carros (5) | 300 | 26 | 1 | 0,15 |
| C-6 Soldadura de cupla en la cúpula (6) | 300 | 18 | 1 | 0,15 |
| C-7 Armado y soldadura circunferencial (7) | 300 | 34 | 1 | 0,15 |
| C-8 Soldadura de accesorios (8) | 300 | 31 | 1 | 0,15 |
| C-81 Fabricación de accesorios (8.1) | 300 | 32 | 1 | 0,15 |
| C-9 Prueba hidráulica de carros (9) | 300 | 23 | 1 | 0,15 |
| C-10 Secado de carros (10) | 300 | 12 | 1 | 0,15 |
| C-11 Pulmón de despacho a pintura (11) | 150 | 63 | 1 | 0,15 |
| S-P Pintura en polvo (riel aéreo, horno único) | 500 | 286 | 14 | 2,10 |
| MT Taller de mantenimiento | 300 | 37 | 2 | 0,30 |
| PÑL Pañol de mantenimiento y de línea | 300 | 18 | 1 | 0,15 |
| QR Cuarentena de producto y muestras retenidas | 750 | 15 | 2 | 0,30 |
| OF-C Pasillo de oficinas | 300 | 15 | 1 | 0,15 |
| Q Laboratorio de calidad | 750 | 34 | 3 | 0,45 |
| PCP Planificación y control de la producción | 300 | 18 | 1 | 0,15 |
| SUP Supervisor de planta | 300 | 24 | 1 | 0,15 |
| C-17 Ensayos de lote de carros (17) | 750 | 70 | 5 | 0,75 |
| C-14 Sala del ensayo de pérdidas (14) | 750 | 25 | 2 | 0,30 |
| C-15 Etiquetado e inspección final (15) | 300 | 10 | 1 | 0,15 |
| C-13 Carga, armado y presurización de carros (13) | 300 | 58 | 2 | 0,30 |
| C-12 Pulmón de pintados (12) | 300 | 69 | 2 | 0,30 |
| C-12C Recepción de pintados: cambio de juego y rechazados (12) | 300 | 23 | 1 | 0,15 |
| C-16R Depósito de carros: retenidos y rechazados (16) | 150 | 121 | 2 | 0,30 |
| C-16L Depósito de carros: liberados (16) | 150 | 84 | 2 | 0,30 |
| AL-3 Almacén de producto terminado y de cilindros | 150 | 146 | 2 | 0,30 |
| S4 Tercerizados revendidos | 150 | 7 | 1 | 0,15 |
| EXP Calle del muelle y expedición (P3) | 150 | 68 | 1 | 0,15 |
| DP Depósito de polvo químico (único de la planta) | 150 | 13 | 1 | 0,15 |
| S-T Terminación 1 a 10 kg | 300 | 55 | 2 | 0,30 |
| EMB Embalaje y paletizado (vacíos y terminados) | 150 | 71 | 1 | 0,15 |
| AL-EB Embalaje: cajas plegadas, film y pallets | 150 | 23 | 1 | 0,15 |
| PU-9 Terminados pintados esperando la carga | 300 | 7 | 1 | 0,15 |
| DL Ducha de emergencia y lavaojos | 300 | 6 | 1 | 0,15 |

Total: 96 luminarias, 14,4 kW.

## 11. Redes: longitud de tendidos (criterio 4)

| Tablero seccional | kW | Largo desde el TGBT (m) |
|---|---|---|
| N1 | 13,7 | 30,2 |
| N2 | 10,0 | 26,1 |
| N6 | 16,0 | 20,7 |
| N3 | 41,4 | 13,0 |
| N7 | 13,5 | 4,1 |
| N4 | 44,4 | 10,1 |
| N5 | 45,0 | 29,2 |
| N8 | 3,0 | 35,2 |
| S-P | 21,0 | 71,6 |
| S-T | 8,0 | 51,3 |
| EMB | 4,5 | 59,1 |
| C-3 | 7,5 | 15,7 |
| C-4 | 10,5 | 19,4 |
| C-5 | 12,0 | 31,0 |
| C-6 | 6,0 | 35,4 |
| C-7 | 10,0 | 42,2 |
| C-8 | 10,0 | 47,0 |
| C-81 | 5,0 | 39,5 |
| C-9 | 2,0 | 32,8 |
| C-10 | 2,0 | 29,1 |
| C-13 | 5,2 | 51,9 |
| C-14 | 3,5 | 64,0 |
| C-17 | 2,2 | 83,2 |
| SC | 69,0 | 20,2 |

**Agua de PH y pérdidas a PTE**: A07 77 m, B07 74 m, DEC 78 m, T06 34 m (total 263 m).

**Gas natural al horno y secadoras**: B14a 64 m, B14b 62 m, B14c 61 m, B14d 59 m, P03 15 m (total 261 m).

**Nitrógeno**: T05 44 m, T02 61 m (total 105 m).

**Gas de soldadura**: M11 7 m, C06 24 m, C08 36 m (total 67 m).


Aire comprimido (anillo, ramales y bajadas de 6 m): 403 m. Potencia instalada de equipos: 365 kW.

## 12. Longitud de los flujos

| Tipo | Flujo | Largo (m) |
|---|---|---|
| MP | Recepción: alero -> P1 -> A1 -> cuarentena (colada, espesor, peso y lote) | 27,1 |
| MP | Atado de caños de 6 m: entra atravesado por P1 y se apoya en el cantiléver sin girar | 25,9 |
| MP | Hojas aprobadas: cuarentena -> A1 -> AN -> A2 -> paquetes de manuales | 27,3 |
| MP | Paquete a la mesa elevadora (autoelevador de costado por A2, AN y A3) | 36,9 |
| MP | Paquete LAC de carros a la misma mesa elevadora | 31,1 |
| MP | Rollo de fleje al desbobinador (espolón por AN) | 13,3 |
| MP | Atado del cantiléver al cajón del láser (pluma, por A1, AN y A3) | 39,2 |
| MP | Barras y caños de carros de 6 m: de a una, a mano, del cantiléver al rack del puesto 8.1 (W-CAR) | 83,9 |
| MP | Casquetes y cuplas: carros 1 y 2 a los puestos 6 y 7 | 70,0 |
| MP | Polvo y pintura en big bags, embalaje y revendidos: P1 -> cuarentena -> pasillo central -> calle del muelle -> depósito de polvo, AL-EB y S4 | 100,4 |
| MP | Big bag de ABC 60 a la estación de la carga (autoelevador) | 2,6 |
| MP | Big bag de ABC 90 al bastidor de la carga de carros (AT, calle del muelle y calle del PT) | 29,5 |
| MP | Pintura en polvo a las tolvas de la cabina (AC -> PC -> PO-PI) | 42,6 |
| SE | Desarrollos a la rampa | 0,2 |
| SE | Carro de plataforma con desarrollos al lado de la roladora | 1,6 |
| SE | Cuerpo de carro al marcado | 0,2 |
| SE | Desarrollo a la roladora | 0,2 |
| SE | Virola al FCHP | 0,2 |
| SE | Virola a la soldadora | 0,2 |
| SE | Cuerpo soldado al FCHP | 0,2 |
| SE | FCHP lleno al lado del encastre | 4,3 |
| SE | Cuerpos 2,5-10 kg al encastre | 1,1 |
| SE | Tramos 1 kg al carro de cajones | 1,2 |
| SE | Carro de tramos al encastre | 6,2 |
| SE | Tramo al encastre | 0,2 |
| SE | Fleje enderezado | 0,3 |
| SE | Fleje al troquel | 0,3 |
| SE | Cúpulas y fondos a los carros de cajones | 1,4 |
| SE | Carro de cúpulas a la zona de cúpulas | 0,3 |
| SE | Carro de fondos a la zona de fondos | 2,8 |
| SE | Fondos al encastre | 0,3 |
| SE | Celda: numerado -> muesca del cuello -> soldadura de cuello (sin transporte) | 5,8 |
| SE | Cúpulas con cuello a las soldadoras circ. | 4,7 |
| SE | Línea principal: encastre -> bordoneado -> soldadura circ. -> espesor -> PH -> secado -> granallado -> detección | 34,7 |
| SE | Lote rechazado a retenidos | 0,7 |
| SE | Defectuosos a las jaulas | 0,4 |
| SE | Jaula «a corregir» a la corrección (carro de corregibles) | 5,0 |
| SE | Corregidos y a re-granallar: vuelven a los rodillos de entrada | 14,5 |
| TL | Riel aéreo: detección -> horno (precalentamiento) -> cabina -> horno (curado) -> descarga | 84,6 |
| RET | Retorno de ganchos vacíos a la detección (aéreo) | 36,3 |
| SE | Terminados pintados (con tapón) a la espera de la carga (PO-PI -> AT2) | 32,0 |
| SE | Carro de terminados a la carga | 6,6 |
| SE | Terminación: carga -> ensamblaje -> presurización -> pérdidas -> etiquetado | 11,2 |
| SE | Etiquetado al FCHP del encajonado | 2,3 |
| SE | Terminados a la mesa de encajonado | 0,2 |
| SE | Cilindros vacíos (con tapón de PE) a la mesa de encajonado de al lado | 10,9 |
| PT | Cajas de terminados al pallet | 0,9 |
| PT | Cajas de cilindros al pallet | 0,9 |
| PT | Pallet de cilindros a la envolvedora | 10,1 |
| PT | Pallet de terminados a la envolvedora | 6,2 |
| PT | Pallets al almacén de PT y de cilindros (transpaleta por AT, calle del muelle y calle del PT) | 19,4 |
| PT | Expedición: rack -> calle del PT -> muelle P3 | 23,3 |
| PT | Revendidos a expedición (muelle P3) | 19,7 |
| SE | Cuerpos grabados (EFE 600 / mesa móvil) del marcado al cilindrado por PO-1 | 13,0 |
| SE | Cuerpo a la roladora | 1,1 |
| SE | Cuerpo rolado al pulmón | 1,0 |
| SE | Pulmón al punteo | 3,4 |
| SE | Cuerpo punteado al pulmón | 1,6 |
| SE | Pulmón a la soldadura longitudinal | 2,8 |
| SE | Cuerpo soldado al armado | 13,6 |
| SE | Cúpula y cupla a la mesa | 1,6 |
| SE | Cúpula con cupla al carro canasto | 1,6 |
| SE | Carro canasto de cúpulas al armado | 4,9 |
| SE | Fondos al armado | 2,4 |
| SE | Cilindro cerrado al pulmón | 1,9 |
| SE | Cilindro cerrado a la soldadura de accesorios | 3,5 |
| SE | Kits del 8.1 al carro de kits | 1,5 |
| SE | Kit al virador | 1,2 |
| SE | Carro con su juego provisorio a la salida | 3,2 |
| SE | Carro rodando a la prueba hidráulica | 11,2 |
| SE | PH -> espera del secado | 2,1 |
| SE | Carro al secado | 1,5 |
| SE | Secado -> pulmón de despacho a pintura | 1,4 |
| SE | Lote aprobado a pintura tercerizada (muelle P3) | 31,8 |
| SE | Carros pintados (vuelven por P3) al cambio de juego | 21,8 |
| SE | Carros con ruedas nuevas al pulmón de pintados | 10,4 |
| SE | Pulmón de pintados a la estación A | 0,9 |
| SE | A -> B: carga de polvo y presurización | 1,4 |
| SE | B -> C: manga, traba y precinto | 0,9 |
| SE | Carro terminado al etiquetado | 1,5 |
| SE | Etiquetado a retenidos (tarjeta amarilla) | 6,5 |
| SE | Muestra del lote a la sala de pérdidas (7 días a 21 °C) | 4,2 |
| SE | Muestra a la balanza (ensayo de funcionamiento) | 2,7 |
| SE | Muestra al recinto de descarga | 0,3 |
| SE | Muestra a la rodadura en el patio (remolque, caída y choque) | 7,3 |
| PT | Lote aceptado: retenidos -> liberados (tarjeta verde) | 14,7 |
| PT | Despacho de carros liberados (muelle P3) | 28,4 |
| SCRAP | Orillas de la guillotina: autoelevador por el pasillo central, A3, AN y A1 al volquete (P1) | 56,5 |
| SCRAP | Recortes del láser: autoelevador por A3 al volquete (P1) | 41,6 |
| SCRAP | Esqueleto de la prensa: contenedor por PO-3 y AN al volquete (P1) | 39,3 |
| SCRAP | Descartes inutilizados al volquete (PO-3, AN y A1) | 81,4 |

## 13. Supuestos a validar

- Tercerizados revendidos: volumen estimado (no figura en los Excel).
- Retiros, FOS y FOT del parque industrial; ubicación de la celda de media tensión y de la reducción de gas.
- Medidas de diseño (marcadas D con su criterio): confirmar con los proveedores al cotizar.
- Textos normativos marcados como B en el README (Dec. 351/79 arts. 49, 50 y anexo VII; Res. SRT 960/2015): verificar la versión vigente en InfoLEG.
- Recargas va fuera de esta planta (pedido v9): su dotación, sus insumos y su portón P2 se quitaron.
- Muelle P3 contra W-CAR 11 (que supone planta sin muelle): a confirmar con el grupo.
