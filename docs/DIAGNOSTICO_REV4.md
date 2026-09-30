# Diagnóstico del layout rev4 y cómo se resuelve en el layout nuevo

Fuente: `referencias/Layout_Planta_2035_rev4.pdf`, `..._nave.pdf`, `..._flujos.pdf` y las hojas de dimensionamiento
(DT, MP, CC). El rev4 tiene casi todo el contenido (máquinas, pulmones, recargas, servicios), pero está mal resuelto en
logística, dimensiones y circulaciones. Se rehízo desde cero con el modelo `planta/layout.py`.

## 1. Logística y flujos

| # | Problema en el rev4 | Efecto | Solución en el layout nuevo |
|---|---|---|---|
| 1 | Recorrido en U: la MP entra por P1 (SO), se corta en el sur, los cuerpos suben al norte (N1-N4) cruzando el pasillo central, bajan a pintura (S2, sur) y vuelven a subir a terminación y a PT (este) | Los flujos 2, 3, 4, 5 y 12 cruzan el pasillo central; la cúpula (verde) y el cuerpo 1 kg (rojo) cruzan a los de 2,5-10 kg | Flujo recto oeste -> este. Sector MP al oeste, celdas en horquilla que toman y entregan sobre un pasillo de materiales al norte recorrido por un tren logístico de **un solo sentido**, pintura, terminación y PT al este. **0 cruces** entre MP, SE y PT (verificado por cálculo) |
| 2 | Polvo e insumos (flujo 13) entran por el muelle M2 de PT y cruzan toda la planta hasta la carga de polvo (S3) y la sala de polvo de recargas (NO), unos 80 m | MP y PT comparten el muelle; el polvo recorre la planta | Polvo e insumos entran por portones propios del norte (P4, P5) pegados a la sala de carga de polvo y a la terminación. El polvo de carros entra por P8 junto a su propia sala. Recargas recibe sus agentes por su portón |
| 3 | Scrap (flujo 12) desde las máquinas del sudoeste cruza la nave hasta P2 (norte) | Cruza MP y SE | Dos puntos de scrap junto a quien lo genera: orillas de hoja por P2 al oeste; esqueleto de fleje por P2b al norte. El chatarrero retira los volquetes desde afuera |
| 4 | Pintura (S2, sur) queda lejos de la salida de las celdas (N4, norte) | El cilindro granallado baja cruzando el pasillo | La pintura queda en la franja central, al final del recorrido del tren logístico y pegada a la terminación |
| 5 | Carros pintados (flujo 10) vuelven por M2 y atraviesan la zona de PT hasta S3 | Cruzan PT | Los carros salen por P6 (oeste) a la pintura tercerizada y vuelven por P8 (este) directo a su sala de carga de polvo; salen terminados por P9. Recorrido en U sin cruces |
| 6 | Recargas comparte la nave con fabricación y recorre la esquina NO en zigzag (flujo 11) | Mezcla de equipos usados y residuos con producción; cruces internos | Recargas pasa a un ala propia al sur, con recepción y despacho por el este y mostrador a la calle |
| 7 | Una sola puerta de MP (P1 7,00 × 4,50) sin bahía interior ni playa dimensionada; el camión no se descarga por los dos lados | Descarga lenta y a la intemperie (la chapa se moja) | Bahía interior para chasis de 10 m (P1) y playa norte bajo alero para semi de 18,6 m y 30 t (P1b), las dos con descarga por ambos lados. Análisis de peso por formato de camión |
| 8 | Autoelevador de 2,5 t para paquetes de 2 t de 1500 × 3000 | Por el lado largo queda justo (1,98 t); por el corto no sirve (1,22 t) | Autoelevador de 3,0 t con horquillas de 1,8 m y posicionador (2,37 t por el lado largo) |
| 9 | Sin control de sobrestock de chapa | Paquetes de 2 t de formatos de bajo consumo cubren 5 a 6 semanas: la SAE 1010 se oxida | Kanban de 2 paquetes por formato, paquetes chicos (≤ 2 semanas), semáforo de antigüedad y entregas quincenales |

## 2. Dimensiones de los espacios

| Espacio | rev4 | Requerido (MP / DT) | Layout nuevo |
|---|---|---|---|
| Almacén de acero AL-1 | 116 m² netos | 148,3 m² | Cantiléver de hojas + porta-flejes + cantiléver de caño + casquetes, en altura, junto a cada máquina |
| Pañol de insumos pesados | lejos de P1 (versión 3) | 35,2 m² junto a P1 | 51,5 m² junto a la bahía de descarga |
| Insumos de terminación y embalaje | no dibujado completo | 97,5 m² | 59,9 m² de rack de 4 niveles junto a la terminación (capacidad equivalente) |
| Polvo en big bags | dentro de AL-2, lejos de la carga | 23,1 m² seco | 37,1 m² pegado a la sala de carga, HR ≤ 70 % |
| Jaula de gases | 16 m² | 48,8 m² | 90 m² en 2 jaulas exteriores (soldadura junto a las celdas; N₂ y CO₂ junto a la terminación) |
| Químicos con batea y pintura en polvo | no dibujado | 24,1 m² | QP 22,7 m² junto a pintura con portón P3 |
| PT | 66 posiciones a 2 alturas | 88 posiciones | Rack de 2 frentes × 6 módulos × 2 pallets × 4 niveles (96 posiciones) + carros a piso + tercerizados |
| Armarios de vestuario H | 55 | 56 (DT: "faltan 1") | 62 H y 14 M |
| Sanitario accesible | 1 de 4,6 m² | Ley 24.314 | 2 (uno por núcleo) con círculo de Ø 1,50 m |
| Lactario, primeros auxilios | no | buena práctica / Ley 19.587 | sí |

## 3. Espacios desconocidos o innecesarios

- "Gabinete técnico" de 10,8 m² sin función; en el layout nuevo la sala técnica (transformador, TGBT, compresores)
  está afuera, en el centro de cargas.
- Superficies grises sin uso asignado en la franja sur y entre N4 y Q.
- "Equipos de intercambio" y "Jaulas 1 kg por concesionaria" dentro de fabricación: pasan a la flota de intercambio
  del ala de recargas (RC-FI).
- Faltaban: sala de carga de baterías y estacionamiento de autoelevadores (cátedra), oficina de expedición, planta de
  efluentes, reserva de agua contra incendio, calle interna de camiones, espacio para tercerizados revendidos.

## 4. Personal y seguridad

| Problema en el rev4 | Solución |
|---|---|
| Un solo bloque de servicios al oeste: el extremo este queda a más de 70 m del sanitario | Dos núcleos sanitarios (principal junto a PP-1 y este en el ala de recargas por PP-3); máximo 50 m |
| La senda peatonal corre junto al pasillo de autoelevadores en ambos sentidos | Pasillo de personal propio al sur y pasillo de materiales al norte; los operarios llegan a los puestos por calles PO sin recorrer los flujos. Solo 2 cruces, en sendas señalizadas |
| Recorrido máximo a salida no verificado | 26,9 m calculado sobre grilla que rodea los equipos; 10 salidas de emergencia de 1,10 m |
| Extintores sin ubicar | 22 en la nave por cálculo de recorrido ≤ 20 m (IRAM 3517-2) + 10 en anexos y exteriores |
| Efluentes, gases y tendidos no representados | Plano de redes (FL_PI_03 hoja 2) con longitudes calculadas |
