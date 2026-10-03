# Llevar las láminas a AutoCAD

Las láminas se generan como **DXF nativos** (`salida/FL_PI_0x.dxf`, versión R2018) con capas, tipos de línea,
textos ISO 3098 y una **presentación (layout) por lámina** ya configurada con `DWG To PDF.pc3` y papel
"ISO full bleed" (A0, A1 y 2A0), así que se abren y se trazan directo desde AutoCAD.

1. Abrir el DXF en AutoCAD (ABRIR, tipo de archivo DXF).
2. Guardarlo como DWG: comando `SCRIPT` -> `guardar_como_dwg.scr` (lo guarda como `FL_PI_0x.dwg` formato 2018,
   compatible con AutoCAD 2018 a 2027). Para varios archivos juntos: ScriptPro o `CONVERTDWG` una vez que son DWG.
3. Trazar: cada presentación ya tiene su configuración de página; `TRAZAR` o `PUBLICAR` las 6 hojas.

Referencia: ayuda oficial de Autodesk, "Acerca de los cambios en los archivos de dibujo (DWG)" y
"How to print pdf in full layout in AutoCAD?" (papel full bleed con márgenes 0).

No hay conexión en vivo entre esta sesión y una instalación de AutoCAD: el modelo `planta/layout.py` es la
fuente única y `python generar.py` vuelve a escribir los DXF cuando algo cambia.
