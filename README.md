# planos_industrial_flama: planta industrial de extintores FLAMA S.A.

Layout de la planta de fabricación de extintores (matafuegos) FLAMA S.A. **al año 10 (2035)**, rehecho desde cero
sobre un modelo en código (`planta/layout.py`, coordenadas en metros). De ahí salen los planos en DXF para AutoCAD y en
PDF, con rótulo IRAM 4508, formato IRAM 4504 y acotación IRAM 4513, más la memoria de cálculo. Usa la misma base de
dibujo que [planos_flama-](https://github.com/TadeoSinay/planos_flama-).

> Estado: **versión 3: línea convergente paso a paso** (nave 88 × 44 m) según el diagrama de bloques de FLAMA, con
> el lenguaje gráfico del rev4: cada máquina con su número de paso, operario y área de trabajo; pulmones (PU) con carros
> entre pasos; sectores en rojo. Verificación automática sin errores: **0 cruces entre flujos de MP, SE y PT**, cruces
> de personal sólo en 9 sendas señalizadas, recorrido máximo a una salida de 24,4 m, 20 extintores por cálculo.

## Planos (`salida/`): una faceta por lámina

| Código | Lámina | Formato y escala | Contenido |
|---|---|---|---|
| `FL_PI_01` | **Plano general formal** | 2A0 1:100 (+ 1:500, 1:200) | Planta acotada completa con cada máquina, puesto, pulmón, mueble, tabique, puerta y ventana; implantación; corte; cuadro de equipos con **medida cotizada** y superficie de **Guerchet** por equipo y por sector |
| `FL_PI_02` | **Flujos y operaciones** | A0 1:200 | MP, SE, PT, scrap y efluentes; símbolos ASME en cada equipo; cursogramas de S1, S2, cúpulas, S3, S4 y recargas |
| `FL_PI_03` | **Personal, evacuación y señalización** | A0 1:200 | DIR (hilos y sendas), salidas, recorrido máximo, extintores, BIE, pulsadores, señalética IRAM 10005, sanitarios y accesibilidad |
| `FL_PI_04` | **Logística de MP y PT** (2 hojas) | A0 1:50 + A1 1:20 | Almacén de MP (descarga, distribución por tipo de chapa, carga a cada máquina), almacén de PT y expedición, políticas de stock, métodos y tiempos, flota; hoja 2: aprovechamiento de chapa |
| `FL_PI_05` | **Servicios, oficinas y apoyo** | A0 1:50 | Todo en planta baja: servicios y administración (lockers 1 por empleado, duchas e inodoros en locales separados, sanitario accesible con ducha, comedor); fila central (mantenimiento + pañol, calidad, cuarentena, supervisor, PCP); sanitarios de planta H y M; sala de compresores y colectores |

Para abrir en AutoCAD y guardar como DWG: ver [`autocad/LEEME.md`](autocad/LEEME.md).

### Colores de los flujos (iguales en todos los planos)

| Flujo | Color | ACI | Capa |
|---|---|---|---|
| **MP**, materia prima | azul | 5 | F-MP |
| **SE**, semielaborado | naranja | 30 | F-SE |
| **PT**, producto terminado | verde | 3 | F-PT |
| Personal (hilos) | magenta, trazos | 6 | F-PERSONAL |
| Scrap y retal | gris, trazo y punto | 8 | F-SCRAP |
| Efluentes líquidos / gaseosos | marrón / cian, trazos | 34 / 4 | F-EFL-LIQ / F-EFL-GAS |

## Versión 7: cuatro portones, almacén de MP de seis rubros y servicios sin entrepiso

- **Camiones con ingreso a cada portón**: entran por G1 (garita y báscula de 18 m) y salen por G3. Calle norte al
  alero de P1, calle sur a la playa de maniobra del muelle P3, calle este a P4. La garita controla G1 (camiones), G2
  (autos y utilitarios) y G4 (peatones); el camino peatonal llega al hall sin cruzar calles de camiones.
- **Cuatro portones**: P1 (MP de producción, 7,20 m para que el atado de caño entre atravesado), P2 (recargas, al sur),
  muelle único P3 (PT, carros, revendidos, casquetes, válvulas, embalaje, polvos, agentes y N₂; recepción 7 a 10 h y
  expedición 13 a 17 h) y P4 (pintura y granalla). Se eliminaron P2 viejo, P6, P7, P8, P9, M2, M3, RC-1 y RC-2.
- **Almacén de MP con sólo seis rubros**: gases Arcal 21 (jaula), hojas, flejes, caños (cantiléver interior), cuellos y
  roscas, alambre MAG. Sin pañol de insumos pesados ni scrap. Válvulas, manómetros y pescantes en AL-2 (terminación)
  con buffers en cajas por línea (estantería pasante en nuevos, BVC en carros, estante en recargas). Polvos, agentes
  extintores, baterías de N₂ y deshumidificador en el almacén previo a la carga (SP-1).
- **Scrap en el puesto**: contenedor en la guillotina, carros en los dos láseres y en la prensa; salen al volquete por
  P1, el portón más cercano a los tres.
- **Embalaje diferenciado**: nuevos y revendidos en EMB (junto al muelle), carros en S-TC, recargas en RC-RD; precintos
  como insumo de PT. Nafta e insumos de autoelevadores en dos armarios (MP y PT).
- **3 autoelevadores**, uno por frente: MP, carros y recargas (calle nueva PO-C del muelle a carros y recargas), PT.
- **Servicios y administración** en planta baja (sin entrepiso): limpieza en el ex primeros auxilios; higiene y
  seguridad + medicina laboral + primeros auxilios + EPP en una oficina de una persona; administración (compras,
  ventas, RRHH) contra la nave con ventana al pasillo central. Lockers 1 por empleado en bloques de 10 × 3; duchas
  en su propio local; inodoros, mingitorios, lavabos y duchas cada grupo sobre su pared; sanitario accesible con ducha
  donde estaba limpieza, por el pasillo PS que termina en la salida SV-2; comedor con las mesas lejos de la puerta y
  el lavamanos junto a la bacha. Sanitarios de planta sólo H y M.
- **Fila central**: mantenimiento con su pañol pegado (repuestos y herramental del preventivo), calidad, cuarentena
  (con las muestras y el archivo de calidad), supervisor en oficina propia y PCP separado, con ventana a la línea.
- **Compresores y colectores de gases de soldadura** en el área libre (ampliada con el ex pañol): colector de Arcal 21
  y de humos en el extremo oeste, el más cercano a las soldadoras (largo calculado en la memoria).
- **Recargas**: recepción y despacho en la misma sala junto a P2; local de calidad IRAM 3517-2 (patrones calibrados,
  contraste mensual de instrumentos, mufla, cámara, freezer, trazabilidad).
- **Controles nuevos**: máximo 4 portones, toda puerta con paso libre a una calle o a su local, scrap a ≤ 3 m del
  puesto, lockers 1 por empleado sin sobredimensionar.

## Versión 6: red de calles continua, sin calles ciegas

- **Calles que se tocan**: A1, A2, PO-1 y PO-5 llegan a la senda; T1-T3 y RC-N al pasillo central; EX a AT; PO-2 a
  PO-E; PO-3 y PO-L a A2. Se dibuja el contorno único de la red (ya no se ven tramos partidos).
- **Ningún extremo muere contra un muro**: cada extremo remata en otra calle, en una puerta (SE-5 pasó al final de la
  calle norte; SE-10 y SE-11 nuevas al final de los corredores de recargas; la puerta de SP-1 quedó frente a PO-T) o
  en su destino; los fondos de calle de rack están declarados (`FONDOS`). Nueva calle de operarios de pintura PO-PI
  como remate este del pasillo central. El autoelevador hace un circuito de sentido único en el almacén de MP
  (entra por A2, sale por A1 con cruce marcado de la senda).
- **Cantiléver de caños** fuera de la playa de camiones: exterior oeste con techo propio, cargado desde el patio PCT;
  los caños entran con el carro porta-tubos por el portón P7.
- **Sin escuelita de soldadura**: el espacio queda libre (LB-1, 20,7 m²) para debatir.
- **Fuentes de medida**: "C" cotización; el resto indica su criterio (pieza, pallet, módulo de rack o puesto del
  Dimensionamiento de recargas). Ningún "estimado" suelto.
- **Controles nuevos en `verificar.py`**: extremos de calle sin tolerancia, recorridos y flujos que atraviesan máquinas
  y muros de locales cerrados (QP con puerta a pintura y portón a PO-E para la transpaleta; cortina de SP-2 ampliada).

## Versión 5: medidas cotizadas, logística real y seguridad

- **Medidas de las cotizaciones** (`referencias/INVESTIGACION PROVEEDORES`): guillotina Molinari HG 6 × 3200,
  láser Leapion 6850 × 800, cilindradora Bästlein 1700 × 700, prensa PHM 300 (mesa 1800 × 1300), desbobinador y
  alimentador SHIMEQ, bordoneadora SWM-400, soldadoras Promotech/Getweld, granalladora Airblast 4500 × 1300,
  envolvedora EDOS PS5. **Pintura** según el esquema de Electricolor (22 × 13 m = 286 m², 2 hornos 6 × 2,44,
  cabina 2 × 1,5): bajó de 421,7 m² y no lleva túnel de pretratamiento (no cotizado; queda a debatir con el DT).
  Lo que no tiene cotización lleva su criterio de medida (pieza, pallet 1,2 × 1,0, módulo de rack de 2,7 m o puesto
  del Dimensionamiento de recargas) en vez de "estimado".
- **Superficie liberada**: el cuadro de Guerchet muestra la holgura de cada sector (N2, N3, AL-3, S-T) para debatir.
- **MP**: un autoelevador 3 t con prolongaciones (paquetes por el lado largo), pluma con percha y gancho C (rollos);
  calles A1/A2 y cabecera AN; carga directa a la mesa elevadora y al desbobinador; caños en el cantiléver CT (exterior oeste,
  fuera de la playa de camiones) y carro porta-tubos por P7 a los caballetes de los láseres. Políticas de stock por formato (kanban de 2 paquetes, 2 rollos).
- **PT**: 3 calles pasantes del pasillo central a la calle de expedición, racks accesibles por ambas caras, muelles y
  calles sin columnas.
- **Oficinas**: administración, PCP y jefatura en un entrepiso vidriado sobre la fila central (ven la línea y bajan
  en 30 s); supervisión en planta baja con ventana.
- **Seguridad**: tabiques, puertas y ventanas en todos los locales cerrados; 1,0 m libre detrás de cada operario
  (verificado); señalética IRAM 10005; BIE y pulsadores; tres sanitarios accesibles; núcleo sanitario y sala de
  limpieza en planta; garita y punto de reunión.

## Versión 4: logística, métodos y tiempos

- **5 láminas en vez de 9**: DIR, operaciones, materiales (con manejo de materiales) y un único plano formal 2A0
  1:100 con todo; más el anidado de chapa.
- **Ningún local vacío** (verificado por `verificar.py`): oficinas con sus 6 puestos, jefatura, hall y fichado,
  vestuarios con 60 + 20 armarios dobles y bancos, sanitarios y duchas según art. 49 (H incluye choferes),
  comedor de 5 mesas de 6 con office, primeros auxilios, laboratorio, taller, pañoles, supervisión, EPP,
  cuarentena, supermercado de carros vacíos, muestras, granalla, tableros y compresor,
  químicos, estación de carga de baterías, rampas de muelle. Biblioteca en `planta/mobiliario.py`.
- **Servicios con circuito**: SV-1 -> hall y fichado -> pasillo limpio -> vestuario -> sanitarios y duchas (sólo desde
  el vestuario) -> pasillo limpio -> PP-1 -> senda. Administración y visitas al sur del pasillo, sin cruzar
  vestuarios; comedor a 6 m de la planta.
- **Circulación**: el autoelevador sólo circula por el pasillo central, el almacén de MP y PT/expedición; al norte de
  la senda es zona sin autoelevador (carros a mano y transpaleta). Cruces peatonales numerados X1-X16.
  Mamparas de soldadura en cada puesto de soldar.
- **Portones con función rotulada**; el P5 se suprimió (≈ 1 camión/semana): esos insumos entran por el muelle M2.
- **Métodos y tiempos**: 1 autoelevador (≈ 7 % de un turno) y 1 apiladora; 22 carros/día por tramo empujados por
  el operario que cierra el lote; milk run de consumibles desde el pañol de línea.

## Concepto del layout (v3)

- **Nave** de 88 × 44 m (3.872 m²): 11 módulos de 8 m, dos luces (19,40 y 24,60 m) con columnas en el eje B, al borde
  del pasillo central (autoelevador doble sentido + senda peatonal).
- **Banda norte, una línea que converge** (diagrama de bloques de FLAMA):
  - fila sur (N1): chapa -> 1 guillotina -> 2 numerado -> 3 cilindrado -> 4 soldadura longitudinal;
  - fila media (N2): caño -> 5 corte láser (1 kg);
  - fila central (N3): fleje -> 6 desbobinado y embutido -> fondos al encastre; cúpulas -> 7 preparación de cuello ->
    8 soldadura de cuello;
  - línea principal (N4-N5): 9 encastre -> 10 bordoneado -> 11 soldadura circunferencial (entra la cúpula) -> 12 PH ->
    13 secado -> 14 granallado -> 15 detección de defectos -> 16 corrección -> 17 pintura.
- **Columna este**: 17 pintura en polvo en lazo (carga, pretratamiento, secado, cabina, polimerizado, enfriamiento,
  descarga). Es la vuelta de la U.
- **Banda sur, de este a oeste**: 18-24 terminación y almacén de cilindros pintados -> PT y muelles M1-M2 -> carros
  (C1-C10, en U, pintura tercerizada por P6/P8) -> recargas (R1-R26, en locales).
- **MP frente a su máquina**: alero de descarga norte (semi y chasis) -> P1 -> racks de chapa, caño y flejes frente a la
  guillotina, los láseres y la prensa. Polvo por P4 e insumos de terminación por el muelle M2, químicos por P3 junto a pintura.
- **Pulmones** PU-1 a PU-9 entre pasos, con carros de cilindros.

## Secciones de la planta

| Sección | Productos | Dónde |
|---|---|---|
| S1 | ABC 1 kg fabricado (cuerpo de caño Ø76,2) | Láser de tubo en el sector MP + celda 1 kg |
| S2 | ABC manuales 2,5, 5 y 10 kg | Guillotina + celda 2,5-10 kg (granallado, detección y corrección) |
| S3 | ABC rodantes 25, 50, 70 y 100 kg | Línea de carros (sur) + terminación de carros (sudeste) |
| S4 | Tercerizados revendidos (CO₂, agua, AFFF, K, agente limpio) | Recepción M3 y stock S4 junto a expedición |
| RC | Recargas (servicio, figura en el dimensionamiento técnico) | Ala propia con recepción, mostrador y despacho |

Pintura y terminación son comunes a S1 y S2. Las cúpulas y fondos de 1-10 kg salen de una prensa con desbobinador
y de las estaciones de cuello del sector MP.

## Criterios de diseño (pedidos por FLAMA) y dónde se cumplen

1. **Recepción de MP**: formatos de descarga y análisis de peso -> FL_PI_03 H1, memoria § 3. Anti-sobrestock ->
   FL_PI_03 H1, memoria § 4.
2. **MP junto al proceso**: portones y almacenes por consumo -> FL_PI_03 H1.
3. **Procesos contiguos sin superponer diagramas**: 0 cruces entre flujos; los hilos no recorren los pasillos de
   materiales -> FL_PI_01, FL_PI_02, `verificar.py`.
4. **Minimizar tendidos y efluentes**: FL_PI_03 H2, memoria § 11.
5. **Seguridad e higiene**: pasillos demarcados, 10 salidas de emergencia y recorrido ≤ 26,9 m, sanitarios art. 49,
   sanitarios accesibles, lactario, extintores -> FL_PI_04, memoria §§ 7 a 10.
6. **Accesibilidad y pulmones**: calles de operarios por puesto, pulmones dimensionados por tasa y cobertura, tren
   logístico con capacidad ociosa -> memoria § 5.

## Checklist normativo

Estado: **N** = verificado en la norma · **B** = tomado de búsqueda, verificar texto oficial · **P** = pendiente.

| Tema | Requisito aplicado | Fuente | Estado |
|---|---|---|---|
| Sanitarios | ≤ 5 personas: 1 + 1 + 1; 6 a 10: por sexo 1 + 1 + 1; más: 1 inodoro c/20, 1 lavabo y 1 orinal c/10, 1 ducha c/20, por turno | Dec. 351/79 art. 49 | B |
| Vestuarios | más de 10 personas por sexo, contiguos a los sanitarios, armarios individuales | Dec. 351/79 art. 50 | B |
| Sanitario accesible | círculo Ø 1,50 m; espacio lateral 0,80 m; barras; lavatorio 0,80-0,85 m | Ley 24.314, Dec. 914/97 | B |
| Espacio de cuidado | obligatorio con 100 o más personas (dotación 71: no aplica) | Ley 20.744 art. 179, Dec. 144/2022 | B |
| Lactario | buena práctica | Ley 26.873 | B |
| Medios de escape | factor de ocupación 16 m²/persona; n = N/100 unidades (0,55 m las 2 primeras, 0,45 m las siguientes); recorrido máximo | Dec. 351/79 anexo VII | B |
| Altura de locales | ≥ 3 m (nave 8 m, servicios 3,20 m) | Dec. 351/79 cap. 5 | B |
| Iluminación | nave 300 lx, depósitos 150 lx, soldadura 500 lx, líquidos penetrantes 750 lx, laboratorio 750 lx | Dec. 351/79 anexo IV / Res. SRT 84/12 | B |
| Ruido | 85 dBA 8 h (soldadura, granallado, prensa: mamparas y protección) | Res. MTESS 295/03 | B |
| Extintores | 1 cada 200 m²; recorrido ≤ 20 m (A) / 15 m (B); señalización | Dec. 351/79 anexo VII; IRAM 3517-2:2020 6.2.4 y cap. 7 | N / B |
| Sala de polvo | HR ≤ 70 %, 8 renovaciones por hora, sin estufas | IRAM 3517-2:2020 | N |
| Colores de seguridad | demarcación amarilla de pasillos, rojo de incendio, verde de escape | IRAM 10005; Dec. 351/79 art. 79 | B |
| Autoelevadores | pasillos de 3,5 m, sendas peatonales separadas | Res. SRT 960/2015 | P |
| Efluentes y residuos | tratamiento previo al vuelco; residuos peligrosos (polvo de pintura, aceites) | Ley 11.459 PBA, Ley 24.051, Ley 25.675 | P |
| Lotes y control de calidad | laboratorio, cuarentena, descarga de muestras de carros | IRAM 3523 / 3550 | N |

## Uso

```bash
pip install -r requirements.txt
python generar.py          # regenera los 5 planos (DXF + PDF) y la memoria de cálculo
python generar.py FL_PI_03 # un solo plano
python verificar.py        # cruces de flujos, superposiciones, escape, sanitarios, extintores y salidas
```

En Windows, `autocad/1_convertir_DXF_a_DWG.bat` guarda todos los planos como DWG 2018 (ver
`autocad/LEAME_AutoCAD.txt`).

## Estructura

```
planta/layout.py    modelo del layout: nave, sectores, equipos, pasillos, puertas, flujos, hilos, exteriores (m)
planta/calculos.py  memoria de cálculo: recepción, anti-sobrestock, pulmones, sanitarios, escape, extintores, redes
planta/simbolos.py  símbolos de máquinas en planta a escala (40 tipos), operarios y vehículos
planta/dibujo.py    dibujo de planta a escala sobre la lámina (capas, muros, ejes, flujos con flechas, cotas, tablas)
planta/planos.py    FL_PI_01 a FL_PI_03
planta/formal.py    FL_PI_04 (1 hoja 2A0)
planta/chapa.py     FL_PI_05
planta/memoria.py   genera docs/MEMORIA_DE_CALCULO.md
planta/lamina.py    formato IRAM 4504, rótulo IRAM 4508, estilos de cota IRAM 4513
docs/               memoria de cálculo y diagnóstico del rev4
referencias/        archivos de entrada (rev4, Excel de dimensionamiento, cotizaciones, normas)
salida/             DXF y PDF generados
autocad/            conversión a DWG
```

## Supuestos a validar

- Volumen de tercerizados revendidos (no figura en los Excel): se estimó en 10.700 u/año.
- Retiros, FOS y FOT del parque industrial; ubicación de la celda de media tensión y de la reducción de gas.
- Medidas de los equipos marcados como estimados en las tablas de FL_PI_04 (el resto sale de cotizaciones).
- Recargas se incluye aunque no estaba en la lista de secciones del pedido, porque está en el dimensionamiento
  técnico con 16 operarios y 22 máquinas.
