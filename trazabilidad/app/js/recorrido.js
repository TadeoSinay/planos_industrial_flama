// ================================================================ recorrido: un lote real del Plan mensual, del papel al cliente
// partida DPS: las OP del mismo modelo se agrupan hasta llegar a 100 u (Res. 349/07 art. 21, partida mínima del certificado)
const PARTIDA = (() => {
  const mismos = lotesMes().filter(l => l.modelo === DEMO.modelo), out = [];
  let g = [];
  for (const l of mismos) { g.push(l); if (g.reduce((a, x) => a + x.cant, 0) >= 100) { out.push(g); g = []; } }
  if (g.length) out.push(g);
  const i = out.findIndex(p => p.some(l => l.op === DEMO.op));
  return { id: `P-${AA}-${String(D.mes).padStart(2, "0")}-${String.fromCharCode(65 + i)}`, ops: out[i], u: out[i].reduce((a, x) => a + x.cant, 0) };
})();
const ESTAMPILLA = s => "F-" + String(41200 + SERIES.indexOf(s)).padStart(6, "0");   // n° de estampilla de fabricación DPS (ejemplo)
const ULT_CONTRASTE = 6;    // días desde el último contraste del manómetro de PH contra el patrón (ejemplo)

const PASOS = [
 { id: "orden", g: "En planta", t: "Orden del lote", r: "PCP", disp: "pc",
   bajada: `La app lee el Plan mensual del Excel de Aprovechamiento (${D.mesNombre} ${D.anio}), arma los lotes, reserva las series y agrupa las órdenes en partidas para el certificado de fabricación. Nadie tipea cantidades.`,
   quien: "Planificación (PCP)", donde: "Oficina PCP", equipo: "PC e impresora A4 (ya están)", tiempo: "≈ 5 min por semana",
   hace: "Abre «Nueva orden», revisa los lotes propuestos (puede cambiar el tamaño) y confirma.",
   falla: "Si el Plan mensual cambia después, las órdenes ya confirmadas no se tocan: las nuevas toman la diferencia.",
   normas: ["Res. 349/07 art. 21 · partida mínima 100 u", "IRAM 3517-2 9.4.16 · registros 6 años"],
   pantalla() {
     const filas = D.filas.filter(f => f.origen === "Aprovechamiento_Manuales").map(f =>
       `<tr><td>${esc(f.producto)}</td><td>${esc(f.tipo)}</td><td class="num mono">${nf(f.valor, 1)}</td><td class="num mono"><b>${n0(f.cant)}</b></td></tr>`).join("");
     const lt = lotesMes();
     const ops = lt.map(l => `<tr${l.op === DEMO.op ? ' style="background:var(--yellow-soft)"' : ""}><td class="mono nw">${l.op}</td><td class="nw">${esc(l.modelo)}</td><td class="num mono">${l.cant}</td><td class="mono nw">${String(l.desde).padStart(6, "0")} → ${String(l.hasta).padStart(6, "0")}</td></tr>`).join("");
     return pc("pcp/nueva-orden", `<div class="h2">Nueva orden · ${D.mesNombre} ${D.anio}</div><p class="sub">Leído de Aprovechamiento_Manuales › Plan mensual › ${D.rangos.man} (columna ${D.mesNombre})</p>
      <div class="dos"><div class="tscroll"><table class="tabla"><thead><tr><th>Producto</th><th>Tipo</th><th class="num">Plan</th><th class="num">A fabricar</th></tr></thead><tbody>${filas}</tbody></table></div>
      <div class="tscroll"><table class="tabla"><thead><tr><th>Orden</th><th>Modelo</th><th class="num">u</th><th>Series ${AA}-…</th></tr></thead><tbody>${ops}</tbody></table></div></div>
      <div class="aviso in" style="margin-top:12px">Partida DPS <b class="mono">${PARTIDA.id}</b> = ${PARTIDA.ops.map(l => l.op).join(" + ")} (${PARTIDA.u} u): el certificado de fabricación se pide por partida de 100 u o más.</div>
      <p class="sub" style="margin-top:12px">Las series de ${MES} arrancan en ${AA}-${String(D.previas + 1).padStart(6, "0")}: siguen a las ${n0(D.previas)} de los meses anteriores. Lote = lo que entra en el carro del modelo.</p>
      <div class="fila">${S.opOk ? `<span class="aviso ok">✓ ${lt.length} órdenes confirmadas · hojas de ruta y archivos de marcado listos</span>` : `<button class="btn pri" data-a="confirmar">Confirmar ${lt.length} órdenes e imprimir</button>`}</div>`, "PCP");
   },
   escribe() {
     const lt = lotesMes();
     return [sheet("s", "Aprovechamiento_Manuales", "Plan mensual", ["A", "B", "C", "F (" + D.mesNombre + ")"],
       D.filas.filter(f => f.origen === "Aprovechamiento_Manuales").slice(0, 4).map(f => [D.anio, f.producto, f.tipo, nf(f.valor, 1)]),
       ["Links", "datos_base", "Plan mensual", "Demanda puesto"]),
       sheet("db", "Base de trazabilidad", "OP", ["op", "modelo", "cant", "serie_desde", "serie_hasta", "partida", "estado"],
         lt.slice(0, 6).map(l => [l.op, l.modelo, l.cant, `${AA}-${String(l.desde).padStart(6, "0")}`, `${AA}-${String(l.hasta).padStart(6, "0")}`, PARTIDA.ops.includes(l) ? PARTIDA.id : "…", S.opOk ? "EMITIDA" : "PROPUESTA"]),
         TABS_DB, S.opOk ? lt.slice(0, 6).map((_, i) => i) : [])];
   } },
 { id: "hoja", g: "En planta", t: "Hoja de ruta y archivo de marcado", r: "PCP", disp: "hoja",
   bajada: `Sale por la impresora A4 con las ${SERIES.length} series ya cargadas. Viaja dentro del carro y es la planilla de cada puesto: al final la visa el responsable técnico.`,
   quien: "PCP", donde: "Oficina → carro del lote", equipo: "Impresora A4 (ya está)", tiempo: "1 hoja por lote",
   hace: "Imprime la hoja y deja el archivo de series para la marcadora (por USB o red).",
   falla: "Si la hoja se pierde, se reimprime: los datos de cabecera están en la base; lo escrito a mano se recupera de la foto del cierre.",
   normas: ["Res. 349/07 art. 9 y anexo I C · planillas por partida", "Res. 349/07 art. 43 · enmiendas salvadas por el RT"],
   pantalla() { return hojaRuta(false); },
   escribe() {
     return [sheet("db", "Base de trazabilidad", "SERIES", ["serie", "op", "modelo", "estado"],
       SERIES.slice(0, 5).map(s => [s, DEMO.op, DEMO.modelo, "RESERVADA"]).concat([["…", "", "", ""]]), TABS_DB),
       `<div class="card"><h4>Archivo para la marcadora</h4><pre class="mono" style="margin:0;font-size:12px;white-space:pre-wrap">${esc(DEMO.op.replace(" ", "_"))}.csv\n${SERIES.slice(0, 4).map(s => `FLAMA S.A.;N° ${s};${AA};DPS`).join("\n")}\n…  (${SERIES.length} renglones)</pre></div>`];
   } },
 { id: "grabado", g: "En planta", t: "Grabado en la planchuela", r: "Guillotina 2 + Pannier", disp: "maquina", fondo: "chapas",
   bajada: "La marcadora graba cada planchuela con la serie que sigue en el archivo y el cuño DPS al lado del número. El operario no tipea nada.",
   quien: "Operario de G2", donde: "Salida de la guillotina 2", equipo: "Pannier (ya está)", tiempo: "0 s extra",
   hace: "Apoya la planchuela contra los topes y aprieta marcar. La máquina avanza sola a la serie siguiente.",
   falla: "Si una planchuela sale mal grabada, se anula esa serie en la hoja y se sigue con la próxima: el número no se reutiliza.",
   normas: ["Res. 349/07 anexo IV · cuño DPS 15 × 7 mm junto al n°", "IRAM 3517-2 anexo F · n° de serie faltante → inutilizar"],
   pantalla() {
     const g = S.grabados, s = SERIES[Math.min(g, SERIES.length - 1)];
     return `<div class="maquina"><div class="placa"><span>Pannier · marcado profundo</span><span>Trabajo ${esc(DEMO.op)}</span></div>
      <div class="lcd"><div style="display:flex;gap:18px;align-items:center;flex-wrap:wrap"><div style="color:var(--lcd-ink)">${dm(s, 92)}</div>
      <div><div style="font-size:13px;opacity:.75">PRÓXIMA</div><div style="font-size:clamp(18px,3vw,28px);font-weight:600">FLAMA S.A.  N° ${esc(g < SERIES.length ? s : "—")}  ${AA}  DPS</div>
      <div style="font-size:13px;opacity:.75;margin-top:6px">grabadas ${g} / ${SERIES.length} · perfora ≈ 0,22 de 1,6 mm · franja 130 × 12 mm en la pollera</div></div></div>
      <div style="height:8px;background:#163b2a;border-radius:3px;margin-top:16px;overflow:hidden"><div style="height:100%;width:${g / SERIES.length * 100}%;background:var(--lcd-ink)"></div></div></div>
      <div class="fila" style="margin-top:14px"><button class="btn ok" data-a="grabar1" ${g >= SERIES.length ? "disabled" : ""}>Marcar planchuela</button><button class="btn" style="background:#2A333A;color:#EEF2F4;border-color:#4A555C" data-a="grabarTodo" ${g >= SERIES.length ? "disabled" : ""}>Marcar las ${SERIES.length - g} que faltan</button></div></div>`;
   },
   escribe() {
     return [sheet("db", "Base de trazabilidad", "EVENTOS", ["serie", "evento", "puesto", "fuente"],
       SERIES.slice(Math.max(0, S.grabados - 4), S.grabados).map(s => [s, "GRABADO", "G2", "archivo Pannier"]).concat(S.grabados ? [] : [["—", "", "", ""]]), TABS_DB,
       S.grabados ? [0, 1, 2, 3] : [])];
   } },
 { id: "puestos", g: "En planta", t: "Puestos: firma y tilde en la hoja", r: "Puestos 4 a 23", disp: "hoja", fondo: "carro_cupulas",
   bajada: "Cada puesto firma una vez por lote y anota sus insumos. En espesor, prueba hidráulica, carga y pérdidas, una tilde por equipo.",
   quien: "Operarios de cada puesto", donde: "En el puesto, sobre el carro", equipo: "Lapicera", tiempo: "≈ 2 s por equipo en los controles; 15 s por lote en el resto",
   hace: "Tocá un casillero de la hoja para cambiar ✓ por ✗: el equipo 17 ya viene marcado como falla en la prueba hidráulica.",
   falla: "El equipo con ✗ sale del carro con su número; el resto del lote sigue.",
   normas: ["DOC-02 · PH 3,5 MPa 1 min", "Res. 349/07 art. 20 · contraste del manómetro cada 15 días", "IRAM 2587 · deformación permanente"],
   pantalla() { return hojaRuta(true); },
   escribe() {
     return [`<div class="aviso in">En este paso no se escribe nada en el sistema: todo queda en el papel firmado. Entra en el cierre (paso 5).</div>`,
       sheet("db", "Base de trazabilidad", "EVENTOS", ["equipo", "evento", "hace"], [["Manómetro PH-M1", "CONTRASTE vs patrón", ULT_CONTRASTE + " días"], ["Patrón MP-01", "CALIBRACIÓN", "cert. vigente (2 años)"]], TABS_DB)];
   } },
 { id: "cierre", g: "En planta", t: "Cierre de la hoja", r: "Calidad + responsable técnico", disp: "tel",
   bajada: "Al terminar el lote, calidad saca una foto de la hoja firmada y confirma los rechazos; el responsable técnico visa la planilla. Recién ahí se puede etiquetar.",
   quien: "Supervisor de calidad y responsable técnico", donde: "Fin de línea", equipo: "Su celular", tiempo: "≈ 1 min por lote",
   hace: "Adjunta la foto (archivo o cámara), revisa los rechazos que la app propone desde las tildes y cierra.",
   falla: "Si la foto no se lee bien se repite; sin cierre el lote queda bloqueado en etiquetado. Si el contraste del manómetro tiene más de 15 días, la app no deja cerrar.",
   normas: ["Res. 349/07 art. 7 inc. 4 · visado de planillas", "Res. 349/07 art. 19 · anomalías al libro de actas"],
   pantalla() {
     const rech = SERIES.filter(s => !Object.values(S.tildes[s]).every(Boolean));
     return tel(`<div class="h2">Cerrar ${esc(DEMO.op)}</div><p class="sub" style="margin:0">${esc(DEMO.modelo)} · ${SERIES.length} grabados · partida ${PARTIDA.id}</p>
      <label class="campo" for="foto">Foto de la hoja firmada<input id="foto" type="file" accept="image/*" data-a="foto"></label>
      ${S.foto ? `<div class="aviso ok">✓ ${esc(S.foto)}</div>` : `<div class="aviso av">Falta la foto de la hoja</div>`}
      <div class="fila"><span class="pill ok">✓ contraste manómetro hace ${ULT_CONTRASTE} d (≤ 15)</span><span class="pill ok">✓ patrón calibrado</span></div>
      <div class="campo">Insumos anotados<div class="mono" style="font-size:12.5px;color:var(--ink)">CU-0303 · AL-2602 · G-77 · PP-2603-2 · PO-2603 · VA-118</div></div>
      <div class="campo">Rechazos (de las tildes)<div class="fila">${rech.map(s => `<span class="pill no mono">${s} · PH</span>`).join("") || "<span class='pill ok'>ninguno</span>"}</div></div>
      <div class="campo">Visado del responsable técnico<div class="mano" style="color:var(--blue)">Ing. A. Ferreyra</div></div>
      <div style="margin-top:auto">${S.cerrado ? `<div class="aviso ok">✓ Lote cerrado: ${SERIES.length - rech.length} aptos, ${rech.length} rechazo · planilla visada</div>` : `<button class="btn ok" style="width:100%" data-a="cerrar">Cerrar lote y visar</button>`}</div>`);
   },
   escribe() {
     return [sheet("db", "Base de trazabilidad", "LOTES_INSUMO", ["op", "puesto", "insumo", "lote", "firma"],
       [[DEMO.op, "4-7", "cúpulas", "CU-0303", "✓"], [DEMO.op, "9-12", "alambre / gas", "AL-2602 / G-77", "✓"], [DEMO.op, "19", "pintura", "PP-2603-2", "✓"], [DEMO.op, "20", "polvo", "PO-2603", "✓"], [DEMO.op, "21", "válvulas", "VA-118", "✓"]],
       TABS_DB, S.cerrado ? [0, 1, 2, 3, 4] : []),
       sheet("db", "Base de trazabilidad", "DESVIOS", ["serie", "tipo", "motivo", "RD"], [[REJ, "RECHAZO", "fuga en PH", "RD-" + AA + "-031"]], TABS_DB, S.cerrado ? [0] : [])];
   } },
 { id: "etiquetado", g: "En planta", t: "Etiquetado: una lectura por equipo", r: "Puesto 24 / C-15", disp: "pc",
   bajada: "El operario lee el grabado con el lector de mano y la impresora saca la etiqueta de ese equipo; la app le asigna la estampilla de fabricación DPS que va pegada. Si es un rechazo, la pantalla lo frena.",
   quien: "Operario de etiquetado", donde: "Puesto 24 (manuales) · C-15 (carros)", equipo: "PC e impresora (ya están) + lector de mano para grabados (nuevo)", tiempo: "≈ 2 s por equipo",
   hace: "Probá: escribí una serie y apretá Enter (el lector hace exactamente eso), o usá los botones.",
   falla: "Si el lector no lee, se tipea el número grabado; queda marcado como lectura manual.",
   normas: ["Res. 349/07 art. 21-23 · estampilla de fabricación DPS", "Res. 349/07 art. 46 · solo estampillas propias", "IRAM 3550 5.2.5 · etiqueta del fabricante"],
   pantalla() {
     const aptos = SERIES.filter(s => s !== REJ), falta = aptos.filter(s => !S.impresos.includes(s));
     let msg = "";
     if (!S.cerrado) msg = `<div class="aviso no">El lote no está cerrado (paso 5): no se puede etiquetar.</div>`;
     else if (S.ultimo && S.ultimo.ok) msg = `<div class="aviso ok">✓ ${esc(S.ultimo.s)} → etiqueta impresa · estampilla DPS ${ESTAMPILLA(S.ultimo.s)}</div>`;
     else if (S.ultimo) msg = `<div class="aviso no">✗ ${esc(S.ultimo.s)} → ${esc(S.ultimo.motivo)}</div>`;
     return pc("etiquetado/puesto-24", `<div class="fila" style="justify-content:space-between"><div><div class="h2">Leé el grabado</div><p class="sub" style="margin:0">Lote abierto: ${esc(DEMO.op)} · ${esc(DEMO.modelo)} · ${aptos.length} aptos</p></div><span class="pill in">impresos ${S.impresos.length} / ${aptos.length}</span></div>
      <form class="lector" data-f="leer" style="margin:14px 0"><input id="lectura" autocomplete="off" placeholder="${esc(falta[0] || SERIES[0])}" aria-label="Lectura del grabado"><button class="btn pri" type="submit">Leer</button></form>
      <div class="fila" style="margin-bottom:14px"><button class="btn sm" data-a="leerSig" ${!falta.length ? "disabled" : ""}>Simular lectura del siguiente</button><button class="btn sm" data-a="leerRech">Simular lectura del rechazo ${esc(REJ)}</button><button class="btn sm" data-a="leerTodo" ${!falta.length ? "disabled" : ""}>Leer los ${falta.length} restantes</button></div>
      ${msg}<div class="etiquetas" style="margin-top:14px">${S.impresos.slice(-3).reverse().map(s => etiqueta(s)).join("")}</div>`, "Puesto 24");
   },
   escribe() {
     return [sheet("db", "Base de trazabilidad", "SERIES", ["serie", "estado", "estampilla DPS", "lectura"],
       S.impresos.slice(-4).reverse().map(s => [s, "IDENTIFICADO", ESTAMPILLA(s), "lector"]).concat(S.impresos.length ? [] : [["—", "", "", ""]]), TABS_DB, S.impresos.length ? [0] : []),
       `<div class="card"><h4>Etiqueta de serie</h4><p style="margin:0;font-size:13.5px">45 × 25 mm, poliéster con cinta de resina, del lado de la pared. El QR es la dirección <span class="mono">${esc(D.url)}&lt;serie&gt;</span>: la misma página para el cliente, el inspector y FLAMA.</p></div>`];
   } },
 { id: "embalaje", g: "En planta", t: "Embalaje y pallet", r: "Puesto 25", disp: "pc", fondo: "pallets",
   bajada: "Cada caja lleva la misma serie que el equipo. Al cerrar el pallet se leen las cajas y sale la etiqueta del pallet.",
   quien: "Operario de embalaje", donde: "Puesto 25", equipo: "La misma PC, lector e impresora", tiempo: "1 lectura por caja",
   hace: "Cerrá el pallet: una sola etiqueta queda unida a los equipos del lote.",
   falla: "Una caja sin leer no deja cerrar el pallet; la pantalla dice cuál falta.",
   normas: ["GS1 · SSCC de 18 dígitos (criterio)"],
   pantalla() {
     const aptos = SERIES.filter(s => s !== REJ), listo = S.impresos.length >= aptos.length;
     return pc("despacho/pallet", `<div class="h2">Armar pallet</div><p class="sub">${esc(DEMO.op)} · cajas leídas ${listo ? aptos.length : S.impresos.length} de ${aptos.length}</p>
      ${!listo ? `<div class="aviso av">Faltan equipos por etiquetar (paso 6).</div>` : ""}
      <div class="dos" style="margin-top:12px"><div><div class="kpis"><div class="kpi"><b>${aptos.length}</b><span>equipos</span></div><div class="kpi"><b>${aptos.length}</b><span>cajas</span></div><div class="kpi"><b>1</b><span>pallet</span></div></div>
      <div style="margin-top:14px">${S.pallet ? `<div class="aviso ok">✓ Pallet cerrado · SSCC 0 0779xxx 000000457 4</div>` : `<button class="btn pri" data-a="pallet" ${listo ? "" : "disabled"}>Cerrar pallet e imprimir etiqueta</button>`}</div></div>
      <div>${S.pallet ? `<div class="etq" style="width:100%"><div class="qr">${qr("SSCC")}</div><div><b>PALLET · SSCC</b><div class="num" style="font-size:16px">(00) 0779xxx<br>000000457 4</div><small>${aptos.length} u · ${esc(DEMO.modelo)} · ${esc(DEMO.op)}</small></div></div>` : ""}</div></div>`, "Puesto 25");
   },
   escribe() {
     return [sheet("db", "Base de trazabilidad", "AGREGACION", ["padre", "hijo", "tipo"],
       [["SSCC …0457", "C-" + SERIES[0].slice(3), "pallet→caja"], ["C-" + SERIES[0].slice(3), SERIES[0], "caja→equipo"], ["…", "…", ""]], TABS_DB, S.pallet ? [0, 1] : [])];
   } },
 { id: "despacho", g: "Del camión al cliente", t: "Despacho y carga", r: "Depósito PT", disp: "pc", fondo: "despacho",
   bajada: "El remito sale con el anexo de series y un QR. La app suma los equipos con gas para el control de transporte.",
   quien: "Depósito y chofer", donde: "Playa de despacho", equipo: "PC del depósito + lector", tiempo: "1 lectura por pallet",
   hace: "Cargá el COT si el traslado lo necesita y despachá.",
   falla: "Si un pallet no se lee al subir, el remito no se cierra.",
   normas: ["CCyCN art. 1298 · carta de porte", "Res. 195/97 · cantidad exenta", "ARBA · COT"],
   pantalla() {
     const u = SERIES.length - 1;
     return pc("despacho/remito", `<div class="fila" style="justify-content:space-between;align-items:flex-start"><div><div class="h2">Remito R 0001-00004521</div><p class="sub">Cliente: Matafuegos Sur (comercializador inscripto) · ${u} equipos · 1 pallet</p></div><div class="qrbox">${qr("REMITO", 84)}</div></div>
      <div class="dos"><div class="campo">Carta de porte<span style="color:var(--ink)">suscripta por FLAMA como cargador</span></div>
      <label class="campo" for="cot">COT de ARBA (si supera los umbrales)<input id="cot" value="${esc(S.cot)}" placeholder="código COT" data-i="cot"></label></div>
      <div class="aviso av" style="margin-top:12px">Carga con gas: ${u} extintores UN 1044 clase 2.2. Verificá la cantidad exenta de la Res. 195/97 vigente antes de despachar.</div>
      <div class="fila" style="margin-top:12px"><span class="pill in">equipos de pie</span><span class="pill in">seguro y precinto puestos</span><span class="pill in">pallet con film y fajas</span></div>
      <div style="margin-top:14px">${S.despachado ? `<div class="aviso ok">✓ Despachado · ${u} equipos salen de FLAMA</div>` : `<button class="btn pri" data-a="despachar" ${S.pallet ? "" : "disabled"}>Despachar</button>${S.pallet ? "" : ` <span class="sub">Cerrá el pallet primero (paso 7).</span>`}`}</div>`, "Depósito PT");
   },
   escribe() {
     return [sheet("db", "Base de trazabilidad", "CUSTODIA", ["serie / SSCC", "de", "a", "documento"],
       [["SSCC …0457", "FLAMA", "Transportes Ruta 3", "R 0001-00004521"]], TABS_DB, S.despachado ? [0] : [])];
   } },
 { id: "chofer", g: "Del camión al cliente", t: "El chofer confirma la salida", r: "Transportista", disp: "tel", fondo: "despacho",
   bajada: "Lee el QR del remito con su celular: se abre una página, no hay app que bajar.",
   quien: "Chofer", donde: "Al salir de planta", equipo: "Su celular", tiempo: "≈ 30 s",
   hace: "Confirma la carga: queda EN TRÁNSITO a su nombre.",
   falla: "Sin señal, la página guarda la confirmación y la manda cuando vuelve la conexión.",
   normas: [],
   pantalla() {
     return tel(`<div class="h2">Remito 0001-00004521</div><p class="sub" style="margin:0">FLAMA → Matafuegos Sur</p>
      <div class="kpis"><div class="kpi"><b>1</b><span>pallet</span></div><div class="kpi"><b>${SERIES.length - 1}</b><span>equipos</span></div></div>
      <label class="campo" for="patente">Patente<input id="patente" value="AB123CD"></label>
      <div style="margin-top:auto">${S.salida ? `<div class="aviso ok">✓ En tránsito · ${hoy()}</div>` : `<button class="btn ok" style="width:100%" data-a="salida" ${S.despachado ? "" : "disabled"}>Confirmar carga y salir</button>`}</div>`);
   },
   escribe() { return [sheet("db", "Base de trazabilidad", "CUSTODIA", ["SSCC", "estado", "chofer"], [["…0457", "EN TRÁNSITO", "AB123CD"]], TABS_DB, S.salida ? [0] : [])]; } },
 { id: "distribuidor", g: "Del camión al cliente", t: "Recibe el distribuidor", r: "Comercializador", disp: "tel",
   bajada: "Cuenta, revisa y confirma desde el mismo QR del remito. Si algo llegó golpeado, lo marca con foto y se abre un desvío.",
   quien: "Distribuidor (comercializador inscripto)", donde: "Su depósito", equipo: "Su celular", tiempo: "≈ 1 min por entrega",
   hace: "Marcá un daño si querés ver cómo queda registrado, y confirmá.",
   falla: "Si no confirma en 48 h, la app avisa a ventas; la custodia queda en el último que confirmó.",
   normas: ["Res. 349/07 art. 3 · registro de comercializadores", "Res. 349/07 art. 6 · completa la tarjeta solo en su lugar"],
   pantalla() {
     return tel(`<div class="h2">¿Llegó todo?</div><p class="sub" style="margin:0">Remito 0001-00004521 · ${SERIES.length - 1} equipos</p>
      <label class="fila" for="danio" style="gap:8px"><input id="danio" type="checkbox" ${S.danio ? "checked" : ""} data-a="danio"> Hay un equipo dañado</label>
      ${S.danio ? `<div class="aviso av">${esc(SERIES[5])} con golpe en la cúpula · foto adjunta · se abre RD-${AA}-033</div>` : ""}
      <label class="campo" for="recibe">Recibe<input id="recibe" value="L. Gómez · DNI 30.111.222"></label>
      <div style="margin-top:auto">${S.recibido ? `<div class="aviso ok">✓ Recibido por Matafuegos Sur</div>` : `<button class="btn ok" style="width:100%" data-a="recibir" ${S.salida ? "" : "disabled"}>Confirmar recepción</button>`}</div>`);
   },
   escribe() { return [sheet("db", "Base de trazabilidad", "CUSTODIA", ["serie / SSCC", "de", "a", "obs."], [["…0457", "transportista", "Matafuegos Sur", S.danio ? "1 dañado → RD" : "ok"]], TABS_DB, S.recibido ? [0] : [])]; } },
 { id: "instalacion", g: "Del camión al cliente", t: "Instalación y entrega al cliente", r: "Instalador", disp: "tel",
   bajada: "El instalador cuelga el equipo, lee su QR y carga dónde quedó. La app pide los datos que exige la jurisdicción, controla las alturas, emite la garantía y pide el consentimiento para los datos personales.",
   quien: "Instalador", donde: "En la propiedad del cliente", equipo: "Su celular", tiempo: "≈ 1 min por equipo",
   hace: "Cambiá la jurisdicción y mirá qué tarjeta oficial corresponde. Si movés las alturas fuera de norma, no deja firmar.",
   falla: "Si el cliente instala solo, el equipo queda registrado cuando escanea el QR por primera vez y acepta los términos.",
   normas: ["IRAM 3517-2 6.2.14 y 7.3 · alturas", "Res. 32-AGC/15 art. 4 · datos de la tarjeta (CABA)", "Res. 349/07 art. 21 · tarjeta DPS (PBA)", "Ley 24.240 art. 11 y 14 · garantía", "Ley 25.326 art. 6 · información al titular"],
   pantalla() {
     const I = S.instalado || { alt: 1.35, sen: 2.2, jur: "PBA", ok: true };
     const okA = I.alt <= 1.5 && I.alt >= 0.1, okS = I.sen >= 2 && I.sen <= 2.5, okC = I.ok !== false;
     const caba = I.jur === "CABA";
     return tel(`<div class="h2">${esc(CLI)}</div><p class="sub" style="margin:0">${esc(DEMO.modelo)} · Matafuegos Sur → Panadería La Espiga</p>
      <div class="fila"><label class="campo" for="jur" style="flex:1">Jurisdicción<select id="jur" data-i="jur"><option ${!caba ? "selected" : ""}>PBA</option><option ${caba ? "selected" : ""}>CABA</option></select></label>
      <label class="campo" for="cuit" style="flex:1.4">CUIT<input id="cuit" value="30-71234567-9"></label></div>
      <label class="campo" for="dir">${caba ? "Dirección, rubro y n° de habilitación" : "Dirección y sector"}<input id="dir" value="${caba ? "Av. Corrientes 2210 · panadería · hab. 4410/2019" : "Av. Mitre 1450, Avellaneda · salón"}"></label>
      <div class="fila"><label class="campo" for="alt" style="flex:1">Parte superior (m)<input id="alt" type="number" step="0.05" value="${I.alt}" data-i="alt"></label><label class="campo" for="sen" style="flex:1">Cartel (m)<input id="sen" type="number" step="0.05" value="${I.sen}" data-i="sen"></label></div>
      <div class="fila"><span class="pill ${okA ? "ok" : "no"}">${okA ? "✓" : "✗"} 0,10–1,5 m</span><span class="pill ${okS ? "ok" : "no"}">${okS ? "✓" : "✗"} cartel 2,0–2,5 m</span><span class="pill vi">${caba ? "tarjeta SGM + QR AGC" : "tarjeta DPS + estampilla"}</span></div>
      <label class="fila" for="consent" style="gap:8px;font-size:12.5px;align-items:flex-start"><input id="consent" type="checkbox" ${okC ? "checked" : ""} data-a="consent"> El titular leyó para qué se usan sus datos (avisos de vencimiento y servicio) y cómo pedir acceso, corrección o baja.</label>
      <div style="margin-top:auto">${I.firmado ? `<div class="aviso ok">✓ Acta firmada · EN SERVICIO · garantía hasta ${new Date(Date.now() + 182 * 864e5).toLocaleDateString("es-AR")}</div>` : `<button class="btn ok" style="width:100%" data-a="firmar" ${okA && okS && okC && S.recibido ? "" : "disabled"}>Firmar acta y emitir garantía</button>${S.recibido ? "" : `<p class="sub" style="margin:6px 0 0">Primero confirmá la recepción (paso 10).</p>`}`}</div>`);
   },
   escribe() {
     const I = S.instalado || { jur: "PBA" }, f = I.firmado;
     const gob = I.jur === "CABA"
       ? sheet("gov", "SGM · archivo batch (txt)", "tarjetas", ["CUIT", "rubro", "ubicación", "serie", "fabr.", "vida útil", "PH", "mant."], [["30-71234567-9", "panadería", "Corrientes 2210", CLI, MES + " " + D.anio, D.anio + 20, MES + " " + D.anio, MES + " " + (D.anio + 1)]], null, f ? [0] : [])
       : sheet("gov", "Libro de actas DPS", "tarjetas y estampillas", ["serie", "estampilla fabr.", "tarjeta DPS", "usuario"], [[CLI, ESTAMPILLA(CLI), "T-" + AA + "-118204", "Panadería La Espiga"]], null, f ? [0] : []);
     return [sheet("db", "Base de trazabilidad", "CUSTODIA", ["serie", "a", "ubicación", "garantía"], [[CLI, "Panadería La Espiga", I.jur === "CABA" ? "Corrientes 2210" : "Mitre 1450 · salón", "6 meses"]], TABS_DB, f ? [0] : []), gob];
   } },
 { id: "cliente", g: "Del camión al cliente", t: "Lo que ve quien escanea el QR", r: "Cliente / inspector", disp: "tel",
   bajada: "Una página pública con los datos del equipo y ninguno de su dueño. Tres solapas: comercial, técnica (para inspectores y recargadores) y una guía para que el usuario lo revise.",
   quien: "Cliente, inspector DPS / AGC", donde: "Donde esté el equipo", equipo: "Su celular", tiempo: "—",
   hace: "Cambiá de solapa: las tres leen la misma historia. Los enlaces del pie llevan a Atención al cliente.",
   falla: "Si la etiqueta se perdió, el recargador lee el grabado y la reimprime.",
   normas: ["Res. 32-AGC/15 art. 6 · QR de validación", "Res. 349/07 art. 25 · controles a-h del usuario", "Ley 24.240 art. 4 · información clara", "Ley 25.326 art. 9 · datos del titular protegidos"],
   pantalla() { return tel(paginaQR()); },
   escribe() { return [`<div class="aviso in">Leer el QR no escribe nada: la página consulta la base y muestra solo datos del equipo. Si el usuario pide servicio o reclama, se agrega un evento.</div>`]; } },
 { id: "reclamo", g: "Del camión al cliente", t: "Reclamo y respuesta", r: "Atención al cliente", disp: "pc",
   bajada: "El reclamo entra desde el QR con el equipo ya identificado: la persona de atención ve su lote, sus insumos y su historia sin pedirle nada al cliente.",
   quien: "Atención al cliente + calidad", donde: "Oficina comercial", equipo: "PC", tiempo: "acuse inmediato · seguridad ≤ 24 h",
   hace: "Abrí el reclamo de ejemplo, mirá la traza y despachá el sustituto. El caso completo está en Atención al cliente.",
   falla: "Si vence el plazo, el reclamo sube al jefe de calidad y queda marcado en Desvíos.",
   normas: ["IRAM-ISO 10002 · tratamiento de quejas", "Ley 24.240 art. 8 bis · trato digno", "Ley 24.240 art. 23 · 30 días para corregir el servicio"],
   pantalla() {
     const r = S.cli.reclamos[0] || reclamoEjemplo();
     return pc("atencion/reclamos/" + r.id, `<div class="fila" style="justify-content:space-between"><div><div class="h2">${esc(r.id)} · ${esc(r.tipoTxt)}</div><p class="sub" style="margin:0">Ingresó por el QR de ${esc(CLI)} · ${esc(r.fecha)}</p></div><span class="pill ${r.estado === "Cerrado" ? "ok" : "no"}">${esc(r.estado)}</span></div>
      <div class="dos" style="margin-top:14px"><div class="campo">Lo que escribió el cliente<div style="color:var(--ink);font-size:14px">«${esc(r.texto)}»</div>
        <div class="campo" style="margin-top:10px">Traza automática<ul class="arbol"><li><b>${esc(DEMO.op)}</b> · partida ${PARTIDA.id}</li><li>polvo <b>PO-2603</b> · válvula <b>VA-118</b></li><li>PH fábrica 3,5 MPa ✓ · carga 5,14 kg ✓</li><li>instalado ${S.instalado && S.instalado.firmado ? "✓" : "—"} · ${S.eventos.length} eventos</li></ul></div></div>
      <div><table class="tabla"><tbody><tr><td>Plazo</td><td><b>${r.tipo === "seguridad" ? "contacto ≤ 24 h · sustituto ≤ 48 h" : "respuesta ≤ 2 días hábiles"}</b></td></tr><tr><td>Responsable</td><td>Atención · calidad</td></tr><tr><td>Otros del lote</td><td>0 reclamos de ${SERIES.length - 1} equipos</td></tr></tbody></table>
      <div style="margin-top:12px">${r.estado === "Cerrado" ? `<div class="aviso ok">✓ Sustituto entregado · equipo a recarga · cliente avisado</div>` : `<button class="btn pri" data-a="resolverReclamo">Enviar sustituto y responder</button>`}</div></div></div>`, "Atención al cliente");
   },
   escribe() { const r = S.cli.reclamos[0] || reclamoEjemplo(); return [sheet("db", "Base de trazabilidad", "RECLAMOS", ["n°", "serie", "tipo", "plazo", "estado"], [[r.id, CLI, r.tipo, r.tipo === "seguridad" ? "24 h" : "2 d háb.", r.estado]], TABS_DB, S.cli.reclamos.length ? [0] : [])]; } },
 { id: "recarga", g: "Servicio", t: "Recarga anual: presupuesto, servicio y ficha nueva", r: "Recargas", disp: "pc",
   bajada: `Un año después el equipo vuelve. Recepción lee el grabado, entrega el presupuesto y el sustituto habilitado, y la app aplica las reglas de IRAM 3517-2 y de la Res. 349/07.`,
   quien: "Recepción de recargas y taller", donde: "Planta de recargas", equipo: "Tablet e impresora (ya previstas) + lector", tiempo: "≈ 1 min de recepción por equipo",
   hace: "Elegí el estado del equipo y mirá qué decide la app. Si es apto, el taller cierra la ficha rev. 1 y el cliente recibe la constancia.",
   falla: "Si la regla dice inutilizar, la app no deja recargarlo.",
   normas: ["Ley 24.240 art. 21 · presupuesto", "Res. 349/07 art. 32 · sustituto habilitado", "Res. 349/07 art. 28 · fecha en el tubo de pesca", "Res. 349/07 art. 33 · polvo bajo de peso → cambio total", "IRAM 3517-2 9.4.14 · etiqueta nueva", "Ley 24.240 art. 15 y 23 · constancia y garantía de servicio"],
   pantalla() {
     const r = S.recarga || { corr: false, golpe: false, bajo: false, hecho: false };
     const inutil = r.corr || r.golpe;
     return pc("recargas/recepcion", `<div class="fila" style="justify-content:space-between"><div><div class="h2">${esc(CLI)} · ${esc(DEMO.modelo)}</div><p class="sub" style="margin:0">Fabricado ${MES} ${D.anio} · ficha rev. 0 · presupuesto PR-${AA}-2207 aceptado · sustituto SUS-ABC5-014 entregado</p></div><span class="pill in">recepción ${MES} ${D.anio + 1}</span></div>
      <div class="dos" style="margin-top:14px"><div class="campo">Revisión
       <label class="fila" for="rc1"><input id="rc1" type="checkbox" data-a="rCorr" ${r.corr ? "checked" : ""}> Corrosión (9.7.1.3 b)</label>
       <label class="fila" for="rc2"><input id="rc2" type="checkbox" data-a="rGolpe" ${r.golpe ? "checked" : ""}> Daño mecánico o abolladura (anexo F)</label>
       <label class="fila" for="rc3"><input id="rc3" type="checkbox" data-a="rBajo" ${r.bajo ? "checked" : ""}> Polvo por debajo de la carga nominal</label>
       <span class="pill ok">fecha y n° de serie legibles ✓</span><span class="pill ok">vida útil hasta ${D.anio + 20} (Res. 349/07 art. 26) ✓</span></div>
      <div>${inutil ? `<div class="aviso no">La regla manda INUTILIZAR (IRAM 3517-2 9.12). No se puede recargar.</div>` :
        `<table class="tabla"><tbody><tr><td>Polvo</td><td>${r.bajo ? `<b>cambio total</b> por polvo nuevo PO-2702 (art. 33.2)` : `puffer clase B ✓ · se repone PO-2702`} · 5,12 kg</td></tr><tr><td>Tubo de pesca</td><td>fecha ${MES} ${D.anio + 1} grabada (art. 28)</td></tr><tr><td>Marbete</td><td>color del año ${D.anio + 1}</td></tr><tr><td>Precinto</td><td class="mono">P-${+AA + 1}-00881</td></tr><tr><td>Etiqueta</td><td>nueva, mismo QR (9.4.14)</td></tr><tr><td>Garantía del servicio</td><td>30 días (art. 23)</td></tr></tbody></table>
        <div style="margin-top:10px">${r.hecho ? `<div class="aviso ok">✓ Ficha rev. 1 cerrada · constancia enviada al cliente · vuelve en ${MES} ${D.anio + 2}</div>` : `<button class="btn ok" data-a="servicio">Cerrar servicio y enviar constancia</button>`}</div>`}</div></div>`, "Recargas");
   },
   escribe() { return [sheet("db", "Base de trazabilidad", "FICHAS", ["serie", "rev", "agente", "masa", "precinto", "próx."],
     [[CLI, "0", "PO-2603", "5,14", "fábrica", (D.anio + 1) + ""], [CLI, "1", "PO-2702", "5,12", "P-" + (+AA + 1) + "-00881", (D.anio + 2) + ""]], TABS_DB, S.recarga && S.recarga.hecho ? [1] : [])]; } },
 { id: "inutilizacion", g: "Servicio", t: "Inutilización y bloqueo", r: "Recargas", disp: "pc",
   bajada: "Cuando la regla lo manda, se inutiliza según la norma y la jurisdicción, se labra el acta y el número queda bloqueado para siempre.",
   quien: "Recargas", donde: "Planta de recargas", equipo: "PC + impresora", tiempo: "≈ 5 min por equipo",
   hace: "Inutilizá el equipo de ejemplo y después mirá qué muestra su QR.",
   falla: "El equipo queda 30 días en depósito a disposición del propietario antes de la disposición final (anexo G).",
   normas: ["IRAM 3517-2 9.12 y anexo G · acta", "Res. 349/07 art. 27 · corte de la rosca y devolución", "Res. 32-AGC/15 art. 7 · asentar en el SGM"],
   pantalla() {
     return pc("recargas/inutilizacion", `<div class="h2">Acta de inutilización · ${esc(OTRO)}</div><p class="sub">Motivo: corrosión en la pollera (IRAM 3517-2 9.7.1.3 b) · propietario: Hotel Rivera (PBA)</p>
      <table class="tabla"><tbody><tr><td>Agente</td><td>retirado · 5,1 kg a disposición final (9.12.1 a)</td></tr><tr><td>Recipiente</td><td>2 orificios Ø 10 mm en lugar visible, lejos de la franja grabada (9.12.1 c)</td></tr>
      <tr><td>Rosca del cuello</td><td>corte longitudinal (PBA, Res. 349/07 art. 27)</td></tr><tr><td>Manguera</td><td>cortada en 2 (9.12.1 d)</td></tr><tr><td>Propietario</td><td>avisado por mail y teléfono · 30 días para retirarlo (anexo G)</td></tr></tbody></table>
      <div style="margin-top:14px">${S.inutil ? `<div class="aviso no">Serie ${esc(OTRO)} BLOQUEADA · leer su QR muestra «INUTILIZADO»</div>` : `<button class="btn pri" data-a="inutilizar">Firmar acta e inutilizar</button>`}</div>`, "Recargas");
   },
   escribe() { return [sheet("db", "Base de trazabilidad", "SERIES", ["serie", "estado", "acta"], [[OTRO, S.inutil ? "BAJA" : "EN SERVICIO", S.inutil ? "AG-" + (+AA + 1) + "-0019" : ""]], TABS_DB, S.inutil ? [0] : []),
     sheet("gov", "Libro de actas DPS", "inutilizaciones", ["serie", "motivo", "acta", "fecha"], [[OTRO, "corrosión", "AG-" + (+AA + 1) + "-0019", S.inutil ? hoy() : "—"]], null, S.inutil ? [0] : [])]; } },
 { id: "datos", g: "Sistema", t: "Cómo se conecta con los Sheets y los registros oficiales", r: "Todo el sistema", disp: "pc",
   bajada: "Los Sheets de producción entran por la izquierda; la base guarda cada evento; los reportes vuelven a Sheets todas las noches y los registros oficiales salen armados.",
   quien: "—", donde: "—", equipo: "Vercel + base Postgres + Google Sheets", tiempo: "—",
   hace: "Mirá qué se lee, qué se guarda y qué se devuelve, con los rangos exactos.",
   falla: "Si la app se cae, la copia diaria en Sheets y las hojas de ruta en papel permiten seguir.",
   normas: ["Ley 25.326 art. 21 · inscripción de la base", "IRAM 3517-2 9.4.16 · 6 años de registro"],
   pantalla() {
     const vol = 284463 + 3107;
     return pc("sistema", `<div class="arq">
      <div class="col"><h5>Se lee (Google Sheets)</h5>
       <div class="blk s"><b>Aprovechamiento_Manuales › Plan mensual</b>${esc(D.rangos.man)} del año · col. D a O = Ene a Dic · al abrir «Nueva orden»</div>
       <div class="blk s"><b>Aprovechamiento_Carros › Plan mensual</b>${esc(D.rangos.car)} · igual</div>
       <div class="blk s"><b>FLAMA_BOM › MODELOS</b>modelo, GTIN, presión de ensayo, masa: para las fichas</div>
       <div class="blk s"><b>FLAMA_MRP › lotes de insumo</b>lotes vigentes de polvo, válvulas, pintura</div></div>
      <div class="col"><h5>Se guarda (base de la app)</h5>
       ${TABS_DB.map(t => `<div class="blk d"><b>${t}</b>${{ OP: "orden, modelo, cantidad, series, partida DPS", SERIES: "una fila por equipo, su estado y su estampilla", EVENTOS: "qué, cuándo, dónde, quién, hash anterior y propio", LOTES_INSUMO: "insumos de cada lote (del cierre)", AGREGACION: "equipo → caja → pallet", CUSTODIA: "quién lo tiene y desde cuándo", FICHAS: "rev. 0 de fábrica y rev. n de cada servicio", RECLAMOS: "n°, serie, tipo, plazo, respuesta", DESVIOS: "registro de desvíos y acciones" }[t]}</div>`).join("")}</div>
      <div class="col"><h5>Sale armado</h5>
       <div class="blk p"><b>FLAMA_Trazabilidad (Sheets, cada noche)</b>OP · Rendimiento · Custodia · Vencimientos · Reclamos · Desvíos</div>
       <div class="blk g"><b>SGM de la AGC (CABA)</b>archivo txt del proceso batch con los datos del art. 4 de la Res. 32-AGC/15</div>
       <div class="blk g"><b>Libro de actas y planillas DPS (PBA)</b>planilla por partida (anexo I C), n° de estampillas y tarjetas, inutilizaciones</div>
       <div class="blk g"><b>Avisos al cliente</b>vencimiento de mantenimiento y PH, con baja en un clic</div></div></div>
      <div class="aviso av" style="margin-top:14px">Por qué la base no es un Sheet: en 2035 el Plan mensual llega a ≈ ${n0(vol)} equipos por año. Con unos 3 eventos por equipo son ≈ ${n0(vol * 3)} filas por año; un Google Sheet admite 10 millones de celdas, que con 8 columnas se llenan en poco más de un año.</div>`, "Sistemas");
   },
   escribe() { return [`<div class="card"><h4>Conexiones</h4><dl class="dl"><dt>Sheets → app</dt><dd>API de Google Sheets con una cuenta de servicio de solo lectura</dd><dt>App → Sheets</dt><dd>tarea nocturna que reescribe las pestañas de FLAMA_Trazabilidad</dd><dt>Lector</dt><dd>USB en modo teclado: escribe en la pantalla</dd><dt>Impresora</dt><dd>desde el navegador (Zebra Browser Print o PDF)</dd><dt>Marcadora</dt><dd>archivo de series por USB o red</dd><dt>Celulares</dt><dd>el QR abre una página web</dd><dt>AGC / DPS</dt><dd>archivos para subir; la app no reemplaza la tarjeta oficial</dd></dl></div>`]; } },
];

// ---------------------------------------------------------------- hoja de ruta (papel)
function hojaRuta(interactiva) {
  const fila = (p, ins, f) => `<tr><td>${p}</td><td>${ins}</td><td class="mano">${f ? "12/03" : ""}</td><td class="mano">${f ? "J. Pérez" : ""}</td></tr>`;
  const col = arr => `<table><thead><tr><th>Serie</th><th>Esp.</th><th>PH</th><th>Carga</th><th>Pérd.</th></tr></thead><tbody>${arr.map(s => {
    const t = S.tildes[s];
    const c = (k, v) => `<td class="caja-tilde mano ${v ? "" : "rojo"}" ${interactiva ? `data-t="${s}|${k}" tabindex="0" role="button" aria-label="${s} ${k}"` : ""}>${interactiva ? (v ? "✓" : "✗") : ""}</td>`;
    return `<tr><td class="mono" style="font-size:10.5px;white-space:nowrap">${s}</td>${c("esp", t.esp)}${c("ph", t.ph)}${c("carga", t.carga)}${c("perd", t.perd)}</tr>`; }).join("")}</tbody></table>`;
  const tercio = Math.ceil(SERIES.length / 3);
  return `<div class="hoja"><div style="display:flex;justify-content:space-between;gap:14px;align-items:flex-start"><div><div style="display:flex;align-items:center;gap:8px">${logo(22)}<h2>Hoja de ruta del lote</h2></div>
    <div class="meta"><b>${esc(DEMO.op)}</b> · ${esc(DEMO.modelo)} · ${SERIES.length} u · series ${SERIES[0]} a ${SERIES[SERIES.length - 1]} · partida ${PARTIDA.id}<br>Chapa H-0412 (colada 4521) · emitida por PCP · viaja en el carro · manómetro PH-M1 contrastado hace ${ULT_CONTRASTE} días</div></div><div class="qrbox">${qr("OP", 74)}</div></div>
    <div class="tscroll"><table style="margin-bottom:12px"><thead><tr><th>Puesto</th><th>Insumo (anotar o pegar etiqueta)</th><th>Fecha</th><th>Firma</th></tr></thead><tbody>
    ${fila("2 · G2 + Pannier", `grabados ${SERIES[0].slice(-3)}–${SERIES[SERIES.length - 1].slice(-3)}`, interactiva)}${fila("4–7 · Cúpulas", `<span class="mano">CU-0303</span>`, interactiva)}${fila("8–12 · Soldaduras", `<span class="mano">AL-2602 / G-77</span>`, interactiva)}${fila("16–19 · Pintura", `<span class="mano">PP-2603-2</span>`, interactiva)}${fila("20–22 · Carga", `<span class="mano">PO-2603 / VA-118</span>`, interactiva)}</tbody></table></div>
    <div class="series-grid">${col(SERIES.slice(0, tercio))}${col(SERIES.slice(tercio, 2 * tercio))}${col(SERIES.slice(2 * tercio))}</div>
    <p style="font-size:12px;margin:10px 0 0">Cierre (calidad): rechazos <span class="mano rojo">${interactiva ? SERIES.filter(s => !Object.values(S.tildes[s]).every(Boolean)).join(", ") || "—" : ""}</span> · firma <span class="mano">${interactiva ? "M. Ruiz" : ""}</span> · visado responsable técnico <span class="mano">${interactiva ? "A. Ferreyra" : ""}</span></p></div>`;
}

// ---------------------------------------------------------------- página pública del QR (la usan el recorrido y Atención al cliente)
function paginaQR(tab = S.tab) {
  const s = CLI, inst = S.instalado && S.instalado.firmado;
  const hist = [["Fabricado y controlado", D.mesNombre + " " + D.anio, 1], ["Despachado", S.despachado ? "sí" : "pendiente", S.despachado], ["Instalado", inst ? "sí" : "pendiente", inst], ["Mantenimiento anual", D.mesNombre + " " + (D.anio + 1), S.recarga && S.recarga.hecho]];
  const com = `<div class="estado-grande" style="background:var(--green-soft);color:var(--green)"><div class="grande">VIGENTE</div><div>Próximo mantenimiento ${MES} ${D.anio + 1}</div></div>
    <dl class="dl"><dt>Equipo</dt><dd>${esc(DEMO.modelo)} · fuegos A, B y C</dd><dt>Prueba hidráulica</dt><dd>vence ${MES} ${D.anio + 5}</dd><dt>Vida útil</dt><dd>hasta ${MES} ${D.anio + 20}</dd><dt>Garantía</dt><dd>${inst ? "6 meses desde la entrega" : "empieza al instalarlo"}</dd></dl>
    <ul class="tl">${hist.map(h => `<li class="${h[2] ? "" : "p"}"><span><b>${esc(h[0])}</b> · ${esc(h[1])}</span></li>`).join("")}</ul>
    <div class="fila"><button class="btn pri sm" data-v="clientes" data-ct="servicio">Pedir mantenimiento</button><button class="btn sm" data-v="clientes" data-ct="reclamo">Hacer un reclamo</button></div>`;
  const tec = `<dl class="dl"><dt>Orden</dt><dd class="mono">${esc(DEMO.op)} · ${PARTIDA.id}</dd><dt>Estampilla</dt><dd class="mono">${ESTAMPILLA(s)}</dd><dt>Chapa</dt><dd class="mono">H-0412 · colada 4521</dd><dt>PH fábrica</dt><dd>3,5 MPa · 1 min ✓</dd><dt>Carga</dt><dd>5,14 kg (5,00–5,30) ✓</dd><dt>Polvo</dt><dd class="mono">PO-2603</dd><dt>Válvula</dt><dd class="mono">VA-118</dd><dt>Custodia</dt><dd>${inst ? "usuario final" : S.recibido ? "Matafuegos Sur" : "FLAMA"}</dd><dt>Eventos</dt><dd>${S.eventos.length} · cadena de hashes ✓</dd></dl>
    <div class="aviso in" style="font-size:12.5px">Inspectores: los datos del titular se ven con la tarjeta oficial (DPS o SGM), no en esta página.</div>`;
  const rev = `<p class="sub" style="margin:0">Revisalo una vez por mes. Si algo no está bien, no lo uses de referencia y pedí servicio.</p>
    <ul class="tl">${["Las instrucciones se leen bien", "No tiene golpes, óxido, pérdidas ni la tobera tapada", "El precinto y el seguro están puestos y sanos", "La aguja del manómetro está en la zona verde", "La identificación del equipo está sana", "La tarjeta y la estampilla oficiales están sanas"].map(t => `<li><span>${esc(t)}</span></li>`).join("")}</ul>
    <p class="nota" style="margin:0">Res. 349/07 (PBA) art. 25 incs. a–f.</p>`;
  return `<div class="fila" style="justify-content:space-between"><div><div class="h2">${esc(s)}</div><p class="sub" style="margin:0">FLAMA S.A. · ${esc(DEMO.modelo)}</p></div><div style="color:var(--ink)">${dm(s, 44)}</div></div>
    <div class="tabs-tel" role="tablist"><button role="tab" aria-selected="${tab === "com"}" data-a="tabCom">Comercial</button><button role="tab" aria-selected="${tab === "tec"}" data-a="tabTec">Técnica</button><button role="tab" aria-selected="${tab === "rev"}" data-a="tabRev">Revisalo vos</button></div>
    ${tab === "com" ? com : tab === "tec" ? tec : rev}
    <div class="legal"><button data-v="clientes" data-ct="datos">Datos personales</button><button data-v="clientes" data-ct="baja">Dejar de recibir avisos</button><button data-v="clientes" data-ct="arrep">Botón de arrepentimiento</button><a href="https://www.argentina.gob.ar/produccion/defensadelconsumidor" target="_blank" rel="noopener">Defensa del consumidor</a></div>`;
}

// ---------------------------------------------------------------- vista y pintado
function estados() {
  const c = { reservado: 0, grabado: 0, rechazo: 0, identificado: 0, despachado: 0 };
  SERIES.forEach((s, i) => {
    if (S.cerrado && s === REJ) c.rechazo++;
    else if (S.despachado && S.impresos.includes(s)) c.despachado++;
    else if (S.impresos.includes(s)) c.identificado++;
    else if (i < S.grabados) c.grabado++;
    else c.reservado++;
  });
  return c;
}
const COL = { reservado: "#7A8792", grabado: "#6DB2E6", identificado: "#4CC27D", despachado: "#E2A800", rechazo: "#E4473A" };
function pintarBarra() {
  const c = estados(), t = SERIES.length;
  $("#barra").innerHTML = Object.entries(c).map(([k, v]) => v ? `<i style="width:${v / t * 100}%;background:${COL[k]}" title="${k}: ${v}"></i>` : "").join("");
  $("#leyenda").innerHTML = Object.entries(c).map(([k, v]) => `<span><i style="background:${COL[k]}"></i>${k} ${v}</span>`).join("");
}
function vistaRecorrido() {
  return `<div class="lotebar wrap"><div class="lotebar-in"><b style="font:700 15px/1 var(--f-display);letter-spacing:.06em;text-transform:uppercase">Lote en recorrido</b>
    <span class="chip">${esc(DEMO.op)} · ${esc(DEMO.modelo)} · ${SERIES[0]} a ${SERIES[SERIES.length - 1]}</span><span class="chip">partida ${PARTIDA.id}</span>
    <div><div class="barra" id="barra" aria-label="Estado de los equipos del lote"></div><div class="leyenda" id="leyenda"></div></div></div></div>
  <div class="app wrap"><nav class="pasos" id="pasos" aria-label="Pasos del recorrido"></nav>
    <div class="escena"><div class="cab"><div class="ceja" id="ceja"></div><h1 id="titulo"></h1><p id="bajada"></p></div>
      <div class="escenario" id="escenario"></div>
      <div class="nav"><button class="btn" id="ant" data-a="ant">← Paso anterior</button><button class="btn pri" id="sig" data-a="sig">Paso siguiente →</button></div></div>
    <aside class="ficha" id="ficha"></aside></div>`;
}
function pintarNav() {
  const grupos = [...new Set(PASOS.map(p => p.g))];
  $("#pasos").innerHTML = grupos.map(g => `<div class="grupo"><h3>${esc(g)}</h3><ol>${PASOS.map((p, i) => p.g !== g ? "" :
    `<li><button class="paso-btn ${hecho(i) ? "hecho" : ""}" data-p="${i}" ${i === S.paso ? 'aria-current="step"' : ""}><span class="n">${hecho(i) && i !== S.paso ? "✓" : i + 1}</span><span class="t">${esc(p.t)}<small>${esc(p.r)}</small></span></button></li>`).join("")}</ol></div>`).join("");
}
function hecho(i) {
  const inst = !!(S.instalado && S.instalado.firmado);
  return { orden: S.opOk, hoja: S.opOk, grabado: S.grabados >= SERIES.length, puestos: S.cerrado, cierre: S.cerrado, etiquetado: S.impresos.length >= SERIES.length - 1,
    embalaje: S.pallet, despacho: S.despachado, chofer: S.salida, distribuidor: S.recibido, instalacion: inst, cliente: inst,
    reclamo: !!(S.cli.reclamos[0] && S.cli.reclamos[0].estado === "Cerrado"), recarga: !!(S.recarga && S.recarga.hecho), inutilizacion: S.inutil, datos: false }[PASOS[i].id];
}
function pintarRecorrido() {
  const p = PASOS[S.paso];
  $("#ceja").textContent = `${p.g} · paso ${S.paso + 1} de ${PASOS.length}`;
  $("#titulo").textContent = p.t;
  $("#bajada").textContent = p.bajada;
  const esc_ = $("#escenario");
  esc_.className = "escenario" + (p.fondo && foto(p.fondo) ? " foto" : "");
  esc_.style.backgroundImage = p.fondo && foto(p.fondo) ? `url(${foto(p.fondo)})` : "";
  esc_.innerHTML = p.pantalla();
  $("#ficha").innerHTML = `<div class="card"><h4>Quién, dónde y con qué</h4><dl class="dl"><dt>Quién</dt><dd>${esc(p.quien)}</dd><dt>Dónde</dt><dd>${esc(p.donde)}</dd><dt>Equipo</dt><dd>${esc(p.equipo)}</dd><dt>Tiempo</dt><dd>${esc(p.tiempo)}</dd></dl></div>
    <div class="card"><h4>Qué hace</h4><p style="margin:0;font-size:14px">${esc(p.hace)}</p></div>
    ${p.normas.length ? `<div class="card"><h4>Normativa que aplica</h4>${norm(p.normas)}</div>` : ""}
    <div class="card"><h4>Se escribe en</h4><div style="display:flex;flex-direction:column;gap:10px">${p.escribe().join("")}</div></div>
    <div class="card"><h4>Si falla</h4><p style="margin:0;font-size:14px">${esc(p.falla)}</p></div>`;
  $("#ant").disabled = S.paso === 0; $("#sig").disabled = S.paso === PASOS.length - 1;
  pintarNav(); pintarBarra();
}
function ir(i) { S.paso = Math.max(0, Math.min(PASOS.length - 1, i)); S.ultimo = null; marcarHash(PASOS[S.paso].id); pintarRecorrido(); window.scrollTo({ top: 0, behavior: "smooth" }); }

// ---------------------------------------------------------------- acciones del recorrido
async function leer(s) {
  s = s.trim().toUpperCase().replace(/^N°\s*/, "");
  if (/^\d{8}$/.test(s)) s = s.slice(0, 2) + "-" + s.slice(2);
  if (!S.cerrado) { S.ultimo = { s, ok: false, motivo: "lote sin cerrar" }; }
  else if (!SERIES.includes(s)) { S.ultimo = { s, ok: false, motivo: "no pertenece al lote abierto" }; }
  else if (s === REJ) { S.ultimo = { s, ok: false, motivo: "BLOQUEADO: rechazo en la prueba hidráulica" }; await evento("BLOQUEO EN ETIQUETADO", s, "puesto 24"); }
  else if (S.impresos.includes(s)) { S.ultimo = { s, ok: false, motivo: "ya tiene etiqueta (reimpresión solo con supervisor)" }; }
  else { S.impresos.push(s); S.ultimo = { s, ok: true }; await evento("IDENTIFICADO", s, "puesto 24 · lector", { estampilla: ESTAMPILLA(s) }); }
  pintarRecorrido(); const i = $("#lectura"); if (i) i.focus();
}
const instalado = () => S.instalado || (S.instalado = { alt: 1.35, sen: 2.2, jur: "PBA", ok: true });
Object.assign(ACC, {
  ant() { ir(S.paso - 1); }, sig() { ir(S.paso + 1); },
  async confirmar() { S.opOk = true; for (const l of lotesMes().slice(0, 3)) await evento("OP EMITIDA", l.op, "PCP", { modelo: l.modelo }); await evento("SERIES RESERVADAS", `${SERIES[0]}…${SERIES[SERIES.length - 1]}`, "PCP"); pintar(); },
  async grabar1() { if (!S.opOk) { await ACC.confirmar(); } if (S.grabados < SERIES.length) { S.grabados++; await evento("GRABADO", SERIES[S.grabados - 1], "G2 · Pannier"); } pintar(); },
  async grabarTodo() { if (!S.opOk) await ACC.confirmar(); const d = S.grabados; S.grabados = SERIES.length; await evento("GRABADO (lote)", `${SERIES[d]}…${SERIES[SERIES.length - 1]}`, "G2 · Pannier"); pintar(); },
  async cerrar() { if (S.grabados < SERIES.length) { S.grabados = SERIES.length; await evento("GRABADO (lote)", DEMO.op, "G2 · Pannier"); }
    S.cerrado = true; await evento("HOJA CERRADA Y VISADA", DEMO.op, "calidad + RT · celular", { foto: S.foto || "sin foto" });
    for (const s of SERIES.filter(s => !Object.values(S.tildes[s]).every(Boolean))) await evento("RECHAZO → RD", s, "calidad"); pintar(); },
  async leerSig() { const f = SERIES.filter(s => s !== REJ && !S.impresos.includes(s)); if (f.length) await leer(f[0]); },
  async leerRech() { await leer(REJ); },
  async leerTodo() { if (!S.cerrado) return leer(SERIES[0]); const f = SERIES.filter(s => s !== REJ && !S.impresos.includes(s)); S.impresos.push(...f); S.ultimo = { s: f[f.length - 1], ok: true }; await evento("IDENTIFICADO (lote)", `${f.length} equipos`, "puesto 24 · lector"); pintar(); },
  async pallet() { S.pallet = true; S.cajas = SERIES.length - 1; await evento("PALLET CERRADO", "SSCC …0457", "puesto 25"); pintar(); },
  async despachar() { S.despachado = true; await evento("DESPACHADO", "R 0001-00004521", "depósito PT", { cot: S.cot }); pintar(); },
  async salida() { S.salida = true; await evento("EN TRÁNSITO", "SSCC …0457", "chofer · celular"); pintar(); },
  async danio() { S.danio = !S.danio; pintar(); },
  async recibir() { S.recibido = true; await evento("RECIBIDO", "SSCC …0457", "Matafuegos Sur · celular", { danio: S.danio }); if (S.danio) await evento("DESVÍO ABIERTO", "RD-" + AA + "-033", "app"); pintar(); },
  consent() { const I = instalado(); I.ok = !I.ok; pintar(); },
  async firmar() { const I = instalado(); I.firmado = true; await evento("INSTALADO · GARANTÍA EMITIDA", CLI, "instalador · celular", { jur: I.jur }); pintar(); },
  tabCom() { S.tab = "com"; pintar(); }, tabTec() { S.tab = "tec"; pintar(); }, tabRev() { S.tab = "rev"; pintar(); },
  rCorr() { S.recarga = Object.assign({ corr: false, golpe: false, bajo: false, hecho: false }, S.recarga); S.recarga.corr = !S.recarga.corr; pintar(); },
  rGolpe() { S.recarga = Object.assign({ corr: false, golpe: false, bajo: false, hecho: false }, S.recarga); S.recarga.golpe = !S.recarga.golpe; pintar(); },
  rBajo() { S.recarga = Object.assign({ corr: false, golpe: false, bajo: false, hecho: false }, S.recarga); S.recarga.bajo = !S.recarga.bajo; pintar(); },
  async servicio() { S.recarga = Object.assign({}, S.recarga, { hecho: true }); await evento("SERVICIO · FICHA REV. 1 · CONSTANCIA", CLI, "recargas"); pintar(); },
  async inutilizar() { S.inutil = true; await evento("INUTILIZADO · BAJA", OTRO, "recargas", { acta: "AG-" + (+AA + 1) + "-0019" }); pintar(); },
});
INPUT.cot = v => { S.cot = v; };
INPUT.alt = v => { instalado().alt = parseFloat(v) || 0; return true; };
INPUT.sen = v => { instalado().sen = parseFloat(v) || 0; return true; };
INPUT.jur = v => { instalado().jur = v; return true; };
