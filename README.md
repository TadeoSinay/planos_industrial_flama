# planos_industrial_flama: planta industrial de extintores FLAMA S.A.

Layout de la planta de fabricación de extintores (matafuegos) FLAMA S.A. **al año 10 (2035)**, rehecho desde cero
sobre un modelo en código (`planta/layout.py`, coordenadas en metros). De ahí salen los planos en DXF para AutoCAD y en
PDF, con rótulo IRAM 4508, formato IRAM 4504 y acotación IRAM 4513, más la memoria de cálculo. Usa la misma base de
dibujo que [planos_flama-](https://github.com/TadeoSinay/planos_flama-).

> Estado: layout completo, 5 planos (9 láminas), memoria de cálculo y diagnóstico del rev4. Verificación automática
> sin errores: **0 cruces entre flujos de MP, SE y PT**, 2 cruces de personal (ambos en sendas señalizadas),
> recorrido máximo a una salida de 26,9 m, 22 extintores por cálculo de recorrido.

## Planos (`salida/`)

| Código | Plano | Formato y escala | Contenido |
|---|---|---|---|
| `FL_PI_01` | **DIR: recorrido de hilos del personal** | A0 1:200 | Hilos desde el estacionamiento y los vestuarios hasta cada puesto; longitudes, puestos, sanitarios (art. 49) |
| `FL_PI_02` | **Flujo de operaciones** | A0 1:200 | Símbolos ASME en cada equipo, flujo de SE por sección y cursogramas sinópticos de S1, S2, S3, S4, subconjunto de cúpulas y recargas |
| `FL_PI_03` | **Flujo de materiales** (2 hojas) | A0 1:200 | H1: MP (azul), SE (naranja), tren logístico, PT (verde), scrap, efluentes; recepción de MP con análisis de peso y anti-sobrestock. H2: redes eléctricas, aire, N₂, gases y efluentes con longitudes |
| `FL_PI_04` | **Plano formal normalizado** (4 hojas) | A0 1:200 / 1:100 / 1:50 / 1:20 | H1 implantación; H2 y H3 planta de la nave acotada (ejes, vanos, pasillos, equipos, extintores, salidas); H4 servicios 1:50, sanitario accesible 1:20 y corte 1:100 |
| `FL_PI_05` | **Aprovechamiento de chapa** | A1 1:20 / 1:10 | Anidado de cuerpos 2,5-100 kg en hojas estándar, discos de cúpula y fondo en fleje, caño del 1 kg |

Documentos: [`docs/MEMORIA_DE_CALCULO.md`](docs/MEMORIA_DE_CALCULO.md) (se regenera con el modelo) y
[`docs/DIAGNOSTICO_REV4.md`](docs/DIAGNOSTICO_REV4.md) (errores del rev4 y cómo se resolvieron).

### Colores de los flujos (iguales en todos los planos)

| Flujo | Color | ACI | Capa |
|---|---|---|---|
| **MP**, materia prima | azul | 5 | F-MP |
| **SE**, semielaborado | naranja | 30 | F-SE, F-TL (tren logístico) |
| **PT**, producto terminado | verde | 3 | F-PT |
| Personal (hilos) | magenta, trazos | 6 | F-PERSONAL |
| Scrap y retal | gris, trazo y punto | 8 | F-SCRAP |
| Efluentes líquidos / gaseosos | marrón / cian, trazos | 34 / 4 | F-EFL-LIQ / F-EFL-GAS |

## Concepto del layout

- **Terreno** 170 × 125 m (rev4) en el Parque Industrial Villa de Luján, Sarandí; calle al sur.
- **Nave** de 120 × 36 m (4.320 m²), una sola luz sin columnas interiores, pórticos cada 8 m, altura libre 8 m.
  Anexos: servicios al personal y oficinas (364 m²), ala de recargas (476 m²), sala técnica norte (72 m²).
- **Flujo recto oeste -> este**: sector MP y corte -> celdas de 1 kg y de 2,5-10 kg -> pintura -> terminación ->
  PT y muelles. La línea de carros (25-100 kg) corre en la franja sur del sector MP de este a oeste. Sale por su
  propio portón (P6) a la pintura tercerizada y vuelve por P8, al este, a su propia sala de carga de polvo.
- **Tren logístico de un solo sentido** en el pasillo de materiales: recoge en el sector MP y en las celdas y entrega
  en pintura. Así las dos celdas y el sector MP usan el mismo pasillo sin que se crucen los flujos.
- **Dos circulaciones separadas**: pasillo de personal al sur, pegado a los servicios; pasillo de materiales al norte.
  En las celdas, que tienen forma de horquilla, los operarios trabajan del lado de afuera.
- **Cada MP entra junto a su proceso**:
  - Chapa, flejes, caño e insumos pesados: bahía interior y playa norte techada del sector MP.
  - Casquetes: P7, junto a la línea de carros.
  - Polvo e insumos de terminación: P4 y P5, junto a la terminación.
  - Químicos y pintura en polvo: P3, junto a pintura.
  - Polvo, estructuras y ruedas de carros: P8.
  - Tercerizados: M3.
- **Recepción dimensionada a la carga máxima**, con análisis de peso: semi de 18,6 m y 30 t en la playa norte y chasis
  de 10 m en la bahía interior, los dos con descarga por ambos lados. Autoelevador de 3,0 t.
- **Anti-sobrestock de chapa SAE 1010**: kanban de 2 paquetes por formato, paquetes chicos (≤ 2 semanas), semáforo
  de antigüedad, entregas quincenales, siempre bajo techo.
- **Instalaciones en el centro de cargas**:
  - Transformador, TGBT y compresores en la fachada norte.
  - Jaulas de gases junto a sus consumos.
  - Efluentes por gravedad a la planta de tratamiento, al sur, junto a la colectora.
- **Servicios**:
  - Vestuarios por sexo, con circuito sucio -> limpio.
  - Dos núcleos sanitarios (principal y este), cada uno con H, M y sanitario accesible.
  - Lactario, primeros auxilios y comedor para 30 personas.

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
planta/dibujo.py    dibujo de planta a escala sobre la lámina (capas, muros, ejes, flujos con flechas, cotas, tablas)
planta/planos.py    FL_PI_01 a FL_PI_03
planta/formal.py    FL_PI_04 (4 hojas)
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
