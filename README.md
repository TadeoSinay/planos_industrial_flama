# planos_industrial_flama: planta industrial de extintores FLAMA S.A.

Layout de la planta de fabricación de extintores (matafuegos) FLAMA S.A. **al año 10**,
dibujado desde cero por código (DXF para AutoCAD + PDF), con rótulo ISO/IRAM 4508,
acotación IRAM 4513 y la misma base de dibujo que
[planos_flama-](https://github.com/TadeoSinay/planos_flama-) (planos de producto).

> **Estado:** estructura, convenciones y checklist normativo listos. Para el layout faltan los archivos de
> la carpeta `Claude Plano Industrial` (ver [Datos de entrada](#datos-de-entrada)).

## Secciones de la planta

| Sección | Productos | Proceso base (a confirmar con el esquemático de procesos) |
|---|---|---|
| S1 | ABC 1 kg (fabricado) | recipiente de tubo Ø 76,2 (3") o chapa · cúpula · soldadura · PH · pintura · armado · carga · presurizado |
| S2 | ABC manuales 2,5 · 5 · 10 kg | corte de chapa · rolado · soldadura longitudinal · embutido de cúpula y fondo · soldadura circunferencial y cuello · PH 100 % · secado · granallado · pintura en polvo · horno · armado · carga · presurizado · estanqueidad · etiquetado |
| S3 | ABC rodantes 25 · 50 · 70 · 100 kg | ídem con dos cabezales, carro (caño, ruedas), manguera y válvula esférica |
| S4 | Tercerizados revendidos | recepción · control · depósito · picking · despacho (sin transformación) |

Servicios comunes: recepción de MP (descarga exterior e interior), depósito de chapa con **FIFO / control de
antigüedad** (la SAE 1010 se corroe con el sobrestock), depósito de PT y expedición, laboratorio de ensayos
(PH, potencial, descarga), mantenimiento, compresores y N₂, sala de polvo (HR ≤ 70 %), efluentes, oficinas,
sanitarios, vestuarios, comedor, enfermería, lactario / espacio de cuidado si corresponde.

## Los cuatro planos

| Código | Plano | Contenido |
|---|---|---|
| `FL_PI_01` | **DIR, recorridos de hilos de personal** | Hilos de cada puesto: ingreso → vestuario → puesto → sanitarios/comedor → salida. Sin cruces con flujo de MP ni entre procesos |
| `FL_PI_02` | **Flujo de operaciones** | Alto nivel: secuencia de operaciones y procesos por sección (símbolos ASME: operación, inspección, transporte, demora, almacenamiento) |
| `FL_PI_03` | **Flujo de materiales** | Alto nivel: MP entrantes, SE entre secciones, PT a expedición, scrap y retales, efluentes |
| `FL_PI_04` | **Plano formal normalizado** | Planta arquitectónica acotada: muros, columnas, portones, máquinas, pasillos, sanitarios, medios de escape, matafuegos, tableros, redes |

### Colores de los flujos (iguales en los cuatro planos)

| Flujo | Color | ACI AutoCAD | Línea |
|---|---|---|---|
| **MP**, materia prima | azul | 5 | continua gruesa |
| **SE**, semielaborado | naranja | 30 | continua gruesa |
| **PT**, producto terminado | verde | 3 | continua gruesa |
| Personal (hilos) | magenta | 6 | trazos |
| Scrap y retal de chapa | gris | 8 | trazo y punto |
| Efluentes líquidos / gaseosos | marrón / cian | 34 / 4 | trazos finos |

## Criterios de diseño (pedidos por FLAMA)

1. **Recepción de MP**: varios formatos de descarga (semi, chasis, utilitario) con análisis de peso de carga;
   dimensionada a la capacidad máxima; descarga por varios lados; playa exterior y bahía interior.
   Chapa SAE 1010 con **sistema anti-sobrestock** (kanban / FIFO con fecha, stock máximo en días).
2. **MP junto al proceso** que la transforma.
3. **Procesos asociados contiguos**, sin superponer diagramas de hilos.
4. **Minimizar** tendidos eléctricos, cañerías (aire, N₂, agua) y recorridos de efluentes líquidos y gaseosos.
5. **Seguridad e higiene**: pasillos, medios de escape, sanitarios accesibles, lactario si es obligatorio,
   sanitarios y vestuarios divididos en forma equitativa por sexo.
6. **Accesibilidad** a recursos y puestos; **buffers** dimensionados para no generar cuellos de botella.

## Checklist normativo

Estado: **N** = verificado en la norma · **B** = tomado de búsqueda, verificar texto oficial · **P** = pendiente.

| Tema | Requisito | Fuente | Estado |
|---|---|---|---|
| Sanitarios | hasta 5 personas: 1 inodoro, 1 lavabo, 1 ducha; 6 a 10: por sexo 1 + 1 + 1; más: 1 inodoro c/20, 1 lavabo y 1 orinal c/10, 1 ducha c/20 (por turno) | Dec. 351/79 art. 49 | B |
| Vestuarios | más de 10 personas de cada sexo; junto a los sanitarios | Dec. 351/79 art. 50 | B |
| Sanitario accesible | círculo de giro Ø 1,50 m; inodoro con 0,80 m libre a un lado y 0,30 m al otro; lavatorio a 0,80-0,85 m; barras | Ley 24.314, Dec. 914/97 | B |
| Espacio de cuidado | establecimientos con **100 o más** personas: espacio de cuidado (45 días a 3 años) o reintegro por CCT | Ley 20.744 art. 179, Dec. 144/2022 | B |
| Lactario | promoción; se incluye como buena práctica (definir con la dotación del año 10) | Ley 26.873, Ley 27.611 | P |
| Medios de escape | n = N/100 unidades de ancho de salida: 0,55 m las dos primeras y 0,45 m las siguientes; mínimo 2 unidades (1,10 m) | Dec. 351/79 anexo VII 3.1 | B |
| Altura de locales | 3 m libres mínimo | Dec. 351/79 cap. 5 | B |
| Iluminación | por tarea y por local (tablas 1 y 2) | Dec. 351/79 anexo IV | P |
| Ruido | 85 dBA 8 h | Res. MTESS 295/03 | B |
| Ventilación | por cubaje y contaminantes (soldadura, pintura) | Dec. 351/79 cap. 11 | P |
| Protección contra incendio | carga de fuego, resistencia, extintores 1 c/200 m² y recorrido ≤ 20 m (A) / 15 m (B) | Dec. 351/79 anexo VII; IRAM 3517-2:2020 6.2.4 | N / B |
| Señalización de extintores | chapas baliza, cartel en altura | IRAM 3517-2:2020 cap. 7 | N |
| Colores de seguridad | demarcación de pasillos y zonas | IRAM 10005; Dec. 351/79 art. 79 | P |
| Autoelevadores | pasillos y circulación | Res. SRT 960/2015 | P |
| Aparatos a presión | compresores, pulmones, N₂ | normativa provincial (p. ej. Res. 231/96 Bs. As.) | P |
| Pintura en polvo | cabina con extracción y riesgo de explosión de polvo | NFPA 33 / EN 12981 (referencia) | P |
| Residuos peligrosos y efluentes | polvo de pintura, aceites, efluentes de lavado y PH | Ley 24.051, Ley 25.675 y norma provincial | P |

## Datos de entrada

La carpeta `C:\Users\Usuario\OneDrive\Escritorio\Claude Plano Industrial` está en la PC del usuario y no es
accesible desde la sesión en la nube. Hace falta subirla a `referencias/` o adjuntarla en el chat:

- plano **rev4** (DWG y PDF) y el plano esquemático;
- esquemático de procesos por sección;
- aprovechamiento seccional en el tiempo (hasta el año 10) y volúmenes de producción;
- aprovechamiento de chapa por formato (medidas de chapa y bobina, anidado de discos y cuerpos);
- especificaciones técnicas de máquinas (medidas, potencia, consumos);
- dotación de personal por turno y por sexo, turnos por día;
- terreno y nave disponibles (medidas, columnas, portones, orientación, accesos).

## Estructura

```
planta/       motor de dibujo (lámina IRAM, rótulo, exportación DXF/PDF)
docs/         memoria de cálculo y normativa
referencias/  archivos de entrada (rev4, esquemáticos, especificaciones)
salida/       DXF y PDF generados
autocad/      scripts para convertir a DWG en AutoCAD 2027
```
