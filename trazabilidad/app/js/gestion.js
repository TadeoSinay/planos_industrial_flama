// ================================================================ gestión: tablero, desvíos, insumos, reportes y configuración
function estadoInsumo(m) {
  const st = S.insumos[m.cod], dia = m.anio26 / 240, plazo = +(m.pmax || m.pmin || 10);
  if (!st) return { k: "gr", t: "sin inventario registrado", cob: null };
  if (!dia) return { k: "gr", t: "sin consumo en " + D.anio, cob: null };
  const cob = st.stock / dia;
  // criterio: pedir cuando la cobertura no llega al plazo máximo más la mitad
  return cob < plazo ? { k: "no", t: "pedir ya", cob } : cob < plazo * 1.5 ? { k: "av", t: "pedir", cob } : { k: "ok", t: "ok", cob };
}

// ---------------------------------------------------------------- desvíos
VISTAS.desvios = {
  titulo: "Desvíos",
  sub: () => "Registro de desvíos de proceso, proveedor, custodia y cliente, con causa y acción",
  acciones: () => `<button class="btn pri" data-a="nuevoRD">Nuevo desvío</button>`,
  html() {
    const f = fil("rdest", "abiertos"), xs = S.desvios.filter(d => f === "todos" || d.estado !== "Cerrado");
    const sev = { "Crítica": "no", "Mayor": "av", "Menor": "in" };
    return `<div class="kpis">${["Crítica", "Mayor", "Menor"].map(s => `<div class="kpi ${sev[s]}"><span>${s}s abiertas</span><b>${S.desvios.filter(d => d.sev === s && d.estado !== "Cerrado").length}</b></div>`).join("")}<div class="kpi ok"><span>Cerrados</span><b>${S.desvios.filter(d => d.estado === "Cerrado").length}</b></div></div>
      ${UI.f.nuevoRD ? `<div class="panel"><header><h2>Nuevo desvío</h2><button class="btn sm" data-a="cancelarRD">Cancelar</button></header><div class="cuerpo"><form class="form" data-f="crearRD">
        <label class="campo">Origen<select id="rdOri"><option>Proceso</option><option>Proveedor</option><option>Custodia</option><option>Cliente</option><option>Registro</option></select></label>
        <label class="campo">Severidad<select id="rdSev"><option>Menor</option><option>Mayor</option><option>Crítica</option></select></label>
        <label class="campo">Referencia (orden, serie, lote, remito)<input id="rdRef"></label><label class="campo">Responsable<input id="rdResp" value="Calidad"></label>
        <label class="campo ancho">Qué pasó<input id="rdQue"></label><div class="ancho"><button class="btn pri" type="submit">Registrar</button></div></form></div></div>` : ""}
      <div class="panel"><header><h2>Registro</h2>${chips("rdest", [["abiertos", "Abiertos"], ["todos", "Todos"]], "abiertos")}</header>${tabla(["Desvío", "Fecha", "Origen", "Qué pasó", "Referencia", "Severidad", "Responsable", "Estado"], xs.map(d => `<tr class="click" data-det="desvio" data-id="${d.id}"><td class="mono nw">${d.id}</td><td class="nw">${fecha(d.fecha)}</td><td>${d.origen}</td><td>${esc(d.que)}</td><td class="mono nw">${esc(d.ref)}</td><td>${pill(d.sev, sev[d.sev])}</td><td>${esc(d.resp)}</td><td>${pill(d.estado, d.estado === "Cerrado" ? "ok" : d.estado === "Abierto" ? "no" : "av")}</td></tr>`), { vacio: "Sin desvíos abiertos" })}</div>`;
  },
};
ACC.nuevoRD = () => { UI.f.nuevoRD = true; pintar(); };
ACC.cancelarRD = () => { UI.f.nuevoRD = false; pintar(); };
FORM.crearRD = () => { const d = { id: `RD-${AA}-${String(++S.nRd).padStart(3, "0")}`, fecha: ahoraISO(), origen: $("#rdOri").value, sev: $("#rdSev").value, ref: $("#rdRef").value || "—", resp: $("#rdResp").value, que: $("#rdQue").value || "(sin descripción)", estado: "Abierto", causa: "", accion: "" };
  S.desvios.unshift(d); UI.f.nuevoRD = false; registrar("Desvío abierto", d.id); toast(`${d.id} registrado`); pintar(); abrirDetalle("desvio", d.id); };
DETALLES.desvio = id => {
  const d = S.desvios.find(x => x.id === id); if (!d) return null;
  return { titulo: d.id, sub: `${d.origen} · ${d.sev} · ${fecha(d.fecha)}`,
    pie: d.estado !== "Cerrado" ? `<button class="btn ok" data-a="rdCerrar" data-id="${d.id}">Cerrar con verificación</button>` : "",
    cuerpo: `<dl class="dl"><dt>Qué pasó</dt><dd>${esc(d.que)}</dd><dt>Referencia</dt><dd class="mono">${esc(d.ref)}</dd><dt>Responsable</dt><dd>${esc(d.resp)}</dd><dt>Estado</dt><dd>${esc(d.estado)}</dd></dl>
      <form class="form" data-f="guardarRD"><input type="hidden" id="rdId" value="${d.id}"><label class="campo ancho">Causa raíz<textarea id="rdCausa" rows="2">${esc(d.causa)}</textarea></label>
      <label class="campo ancho">Acción correctiva<textarea id="rdAccion" rows="2">${esc(d.accion)}</textarea></label><div class="ancho"><button class="btn" type="submit">Guardar</button></div></form>` };
};
FORM.guardarRD = () => { const d = S.desvios.find(x => x.id === $("#rdId").value); d.causa = $("#rdCausa").value; d.accion = $("#rdAccion").value; if (d.estado === "Abierto" && d.accion) d.estado = "En curso"; registrar("Desvío actualizado", d.id); toast("Guardado"); pintar(); };
ACC.rdCerrar = el => { const d = S.desvios.find(x => x.id === el.dataset.id); d.estado = "Cerrado"; registrar("Desvío cerrado", d.id); toast(`${d.id} cerrado`); pintar(); };

// ---------------------------------------------------------------- insumos
VISTAS.insumos = {
  titulo: "Insumos",
  sub: () => `${D.insumos.length} materiales del MRP · consumo de ${D.anio} (CONSOLIDADO) y plazos de entrega de POLITICA_STOCK`,
  html() {
    const f = fil("iest", "todos"), q = (UI.f.iq || "").toUpperCase();
    const xs = D.insumos.map(m => [m, estadoInsumo(m)]).filter(([m, e]) => (f === "todos" || (f === "pedir" ? e.k === "no" || e.k === "av" : e.k === f)) && (!q || (m.cod + m.mat + m.prov).toUpperCase().includes(q)));
    return `<div class="kpis"><div class="kpi no"><span>Pedir ya</span><b>${D.insumos.filter(m => estadoInsumo(m).k === "no").length}</b><small>la cobertura no llega al plazo</small></div><div class="kpi av"><span>Pedir</span><b>${D.insumos.filter(m => estadoInsumo(m).k === "av").length}</b><small>cobertura menor a 1,5 × plazo (criterio)</small></div><div class="kpi ok"><span>Cubiertos</span><b>${D.insumos.filter(m => estadoInsumo(m).k === "ok").length}</b></div></div>
      <div class="panel"><header><div class="filtros"><input id="iq" type="search" placeholder="Código, material o proveedor" value="${esc(UI.f.iq || "")}" data-in="iq" aria-label="Buscar insumo">${chips("iest", [["todos", "Todos"], ["pedir", "A pedir"], ["ok", "Cubiertos"], ["gr", "Sin inventario o consumo"]], "todos")}</div><span class="muted">${xs.length}</span></header>
      ${tabla(["Código", "Material", "Proveedor", "Stock", "Consumo/día", "Cobertura", "Plazo (días háb.)", "Estado"], xs.map(([m, e]) => `<tr class="click" data-det="insumo" data-id="${esc(m.cod)}"><td class="mono nw">${esc(m.cod)}</td><td>${esc(m.mat)}</td><td>${esc(m.prov)}</td><td class="num nw">${S.insumos[m.cod] ? nf(S.insumos[m.cod].stock, 1) + " " + esc(m.um) : "—"}</td><td class="num">${nf(m.anio26 / 240, 2)}</td><td class="num">${e.cob == null ? "—" : n0(e.cob) + " d"}</td><td class="num">${m.pmin === m.pmax ? m.pmin : `${m.pmin}-${m.pmax}`}</td><td>${pill(e.t, e.k)}</td></tr>`), { vacio: "Ningún material con ese filtro" })}</div>`;
  },
};
DETALLES.insumo = cod => {
  const m = D.insumos.find(x => x.cod === cod); if (!m) return null;
  const st = S.insumos[cod] || null, e = estadoInsumo(m);
  return { titulo: esc(m.cod), sub: esc(m.mat), pie: `<button class="btn pri" data-a="ingresoMP" data-id="${esc(cod)}">Registrar ingreso</button>`,
    cuerpo: `<dl class="dl"><dt>Proveedor</dt><dd>${esc(m.prov)}</dd><dt>Stock</dt><dd>${st ? nf(st.stock, 1) + " " + esc(m.um) : "—"} · ${pill(e.t, e.k)}</dd><dt>Lote vigente</dt><dd class="mono">${st ? esc(st.lote) + " · ingresó " + fecha(st.ingreso) + (st.cert ? " · certificado " + esc(st.cert) : "") : "—"}</dd>
      <dt>Consumo ${D.anio}</dt><dd>${nf(m.anio26, 1)} ${esc(m.um)}/año · ${nf(m.anio26 / 240, 2)} por día hábil</dd><dt>Plazo de entrega</dt><dd>${m.pmin} a ${m.pmax} días hábiles</dd>
      <dt>Política 2035 (MRP)</dt><dd>punto de pedido ${nf(m.pdp, 1)} · stock de seguridad ${nf(m.seg, 1)} ${esc(m.um)}</dd></dl>
      <form class="form" data-f="ingresoMP"><input type="hidden" id="mpCod" value="${esc(cod)}"><label class="campo">Cantidad (${esc(m.um)})<input id="mpCant" type="number" min="0" step="any" required></label><label class="campo">Lote del proveedor<input id="mpLote" required></label><label class="campo">Certificado o remito del proveedor<input id="mpCert"></label><div class="ancho"><button class="btn pri" type="submit">Registrar ingreso</button></div></form>` };
};
ACC.ingresoMP = () => FORM.ingresoMP();
FORM.ingresoMP = () => { const cod = $("#mpCod").value, st = S.insumos[cod] || (S.insumos[cod] = { stock: 0 }), q = +$("#mpCant").value || 0;
  if (!q || !$("#mpLote").value.trim()) return toast("Cantidad y lote del proveedor son obligatorios");
  st.stock = Math.round((st.stock + q) * 10) / 10; st.lote = $("#mpLote").value.trim(); st.cert = ($("#mpCert") || { value: "" }).value.trim(); st.ingreso = ahoraISO();
  registrar("Ingreso de insumo", cod, `${q} · lote ${st.lote}${st.cert ? " · certificado " + st.cert : ""}`); toast(`${cod}: +${q}`); pintar(); };

// ---------------------------------------------------------------- reportes
const REPORTES = {
  dps: ["Libro de actas DPS · estampillas de fabricación", "PBA · Res. 349/07 art. 19 y 21-23", () => {
    const out = ["serie\tmodelo\torden\tpartida\tidentificado\tvisado"];
    S.ordenes.forEach(o => { for (let n = o.desde; n <= o.hasta; n++) if (S.ident[n]) out.push([ser(n), o.modelo, o.op, o.partida, fecha(S.ident[n]), o.visado ? o.visado.quien : ""].join("\t")); });
    return out.join("\n"); }],
  sgm: ["SGM de la AGC · archivo para el proceso batch", "CABA · Res. 32-AGC/15 anexo II art. 4", () => {
    const out = ["cuit;razon_social;rubro;ubicacion;fabricante;recargador;agente;capacidad;serie;fecha_fabricacion;vida_util;fecha_ph;fecha_mantenimiento"];
    const max = S.ordenes[S.ordenes.length - 1].hasta;
    for (let n = 1; n <= max; n++) { const e = equipo(n); if (e.estado === "Instalado" && e.cliente.jur === "CABA") out.push([e.cliente.cuit, e.cliente.nombre, e.cliente.rubro || e.cliente.tipo, e.inst.ubic + " · " + e.cliente.loc, "FLAMA S.A.", "FLAMA S.A.", "polvo ABC", e.o.modelo.replace(/.*ABC /, ""), e.s, fecha(e.fab), fecha(e.vida), fecha(e.fab), fecha(e.mant)].join(";")); }
    return out.join("\n"); }],
  venc: ["Vencimientos de mantenimiento · próximos 60 días", "IRAM 3517-2 9.2 · aviso al cliente", () => {
    const out = ["serie\tmodelo\tcliente\tvence"], max = S.ordenes[S.ordenes.length - 1].hasta;
    for (let n = 1; n <= max; n++) { const e = equipo(n); if (e.mant && dias(HOY, e.mant) >= 0 && dias(HOY, e.mant) <= 60) out.push([e.s, e.o.modelo, e.custodia, fecha(e.mant)].join("\t")); }
    return out.length > 1 ? out.join("\n") : "Sin equipos identificados con mantenimiento en los próximos 60 días."; }],
  prod: ["Producción del mes por modelo", "FLAMA_Trazabilidad › Rendimiento (Sheets)", () => {
    const out = ["modelo\tplan\tordenes\tcerrados\taptos\trechazos"];
    D.plan.filter(p => p.tipo === "Terminado").forEach(p => { const os = S.ordenes.filter(o => o.mes === D.mes && o.modelo === p.producto), c = os.filter(o => o.etapa >= E["Para etiquetar"]);
      out.push([p.producto, p.cant, os.length, c.reduce((a, o) => a + o.cant, 0), c.reduce((a, o) => a + aptos(o), 0), c.reduce((a, o) => a + o.rech.length, 0)].join("\t")); });
    return out.join("\n"); }],
  eventos: ["Registro de eventos de esta sesión", "acciones hechas en el sistema", () => ["fecha\tevento\treferencia\tdetalle\tusuario", ...S.eventos.map(e => [new Date(e.t).toLocaleString("es-AR"), e.tipo, e.ref, e.detalle, e.quien].join("\t"))].join("\n")],
};
VISTAS.reportes = {
  titulo: "Reportes",
  sub: () => "Salidas para la autoridad de aplicación, para Sheets y para avisos a clientes",
  html() {
    const k = fil("rep", "dps"), [t, base, fn] = REPORTES[k], txt = fn(), filas = txt.split("\n").length - 1;
    return `<div class="grilla"><div class="panel c4"><header><h2>Reportes</h2></header><div class="cuerpo" style="display:flex;flex-direction:column;gap:6px">${Object.entries(REPORTES).map(([id, [tt, bb]]) => `<button class="btn" style="justify-content:flex-start;white-space:normal;text-align:left;${id === k ? "border-color:var(--ink)" : ""}" data-a="filtro" data-k="rep" data-v="${id}"><span><b>${esc(tt)}</b><br><span class="muted" style="font-weight:400">${esc(bb)}</span></span></button>`).join("")}</div></div>
      <div class="panel c8"><header><h2>${esc(t)}</h2><div class="acciones"><span class="muted">${filas > 0 ? n0(filas) + " filas" : ""}</span><button class="btn pri" data-a="copiarRep">Copiar</button></div></header><div class="cuerpo"><pre class="salida" id="repTxt">${esc(txt.split("\n").slice(0, 120).join("\n"))}${filas > 120 ? "\n…" : ""}</pre></div></div></div>`;
  },
};
ACC.copiarRep = () => copiar(REPORTES[fil("rep", "dps")][2]());

// ---------------------------------------------------------------- configuración
const REGLAS = [
  ["Prueba hidráulica con ✗", "1 equipo", "Cierre de lote", "bloquea la serie en etiquetado y suma un rechazo", "DOC-02"],
  ["Contraste del manómetro de PH", "más de 15 días", "Calidad", "no deja cerrar lotes de esa línea", "Res. 349/07 art. 20"],
  ["Calibración del patrón", "más de 2 años", "Calidad", "aviso; el contraste deja de ser válido", "Res. 349/07 art. 15 l"],
  ["Masa de carga", "fuera de la banda del BOM", "Carga", "rechazo de la serie", "IRAM 3523 · BOM"],
  ["Carta de carga", "un punto fuera de 3 σ o 7 seguidos del mismo lado", "Calidad", "aviso a calidad (sin rechazo)", "criterio"],
  ["Lectura de una serie rechazada", "1 lectura", "Etiquetado", "no imprime etiqueta ni asigna estampilla", "IRAM 3517-2 anexo F"],
  ["Partida DPS", "100 u o más", "Órdenes", "agrupa órdenes del mismo modelo y mes", "Res. 349/07 art. 21"],
  ["Recepción sin confirmar", "más de 48 h", "Expedición", "aviso a ventas y desvío si sigue", "criterio"],
  ["Alturas de instalación", "parte superior 0,10-1,5 m · cartel 2,0-2,5 m", "Instalaciones", "no deja registrar fuera de rango", "IRAM 3517-2 6.2.14 y 7.3"],
  ["Polvo bajo de peso en recarga", "masa menor a la nominal", "Recargas", "cambio total por polvo nuevo", "Res. 349/07 art. 33"],
  ["Vida útil", "20 años desde la fabricación", "Recargas", "manda a inutilizar", "Res. 349/07 art. 26"],
  ["Reclamo de seguridad", "sin contacto a las 24 h", "Reclamos", "sube al jefe de calidad", "criterio"],
  ["Pedido de datos personales", "10 días corridos", "Reclamos", "vence el plazo legal", "Ley 25.326 art. 14"],
];
const NORMAS = [
  ["IRAM 3517-2", "6.2.14, 7.3, 9.2, 9.4.5, 9.4.13-9.4.16, 9.6, 9.7, 9.10-9.12, anexos E, F y G", "instalación, mantenimiento, sustituto, precinto, etiqueta, registros, marbete, inutilización"],
  ["Res. 349/07 (PBA)", "art. 7-9, 19-29, 32, 33, 43-46 · anexos I-IV", "responsable técnico, planillas, libro de actas, contraste, tarjeta y estampilla DPS, vida útil, inutilización"],
  ["Res. 32-AGC/15 (CABA)", "anexos I-III", "tarjeta de identificación y SGM con proceso batch"],
  ["DOC-02 FLAMA", "R1-R9, L1-L5", "presión de PH, tolerancias de carga y N₂"],
  ["Ley 24.240", "art. 4, 8 bis, 10 ter, 11, 14, 15, 21, 23, 34", "información, garantía, presupuesto, constancia de servicio, baja y arrepentimiento"],
  ["Ley 25.326", "art. 6, 9, 14, 16, 21", "datos personales de los titulares"],
  ["IRAM-ISO 10002", "—", "tratamiento de reclamos"],
  ["Res. 195/97 · CCyCN art. 1298 · COT ARBA", "—", "transporte de UN 1044 y carta de porte"],
];
VISTAS.config = {
  titulo: "Configuración",
  sub: () => "Modelos, parámetros, reglas, normativa, integraciones y usuarios",
  html() {
    const t = fil("ctab", "mod"), tabs = [["mod", "Modelos y parámetros"], ["reg", "Reglas automáticas"], ["nor", "Normativa"], ["int", "Integraciones"], ["usu", "Usuarios y datos"]];
    let c = "";
    if (t === "mod") c = `<div class="grilla"><div class="panel c7"><header><h2>Modelos (BOM)</h2></header>${tabla(["Código", "Equipo", "IRAM", "Carga", "Mínima", "Máxima", "Espesor"], D.modelos.map(m => `<tr><td class="mono">${esc(m.cod)}</td><td>${esc(m.nombre)}</td><td>${m.iram}</td><td class="num">${nf(m.carga, 1)} ${m.um}</td><td class="num">${nf(m.min, 2)}</td><td class="num">${nf(m.max, 2)}</td><td class="num">${nf(ESPESOR[kgDe(m.nombre)] || 0, 2)} mm</td></tr>`))}</div>
      <div class="panel c5"><header><h2>Parámetros</h2></header><div class="cuerpo"><dl class="dl"><dt>Tamaño de lote</dt><dd>1 kg 60 · 2,5 y 5 kg 48 · 10 kg 24 · carros 25-50 kg 4, 70-100 kg 2 (lo que entra en el carro interno; criterio)</dd>
        <dt>Prueba hidráulica</dt><dd>manuales ${nf(PH.man, 1)} MPa · carros ${nf(PH.car, 1)} MPa · 60 s (DOC-02)</dd><dt>Presurización</dt><dd>N₂ ${nf(N2, 1)} MPa</dd><dt>Series</dt><dd>año + correlativo de 6 dígitos para matafuegos y cilindros, sin reutilizar</dd>
        <dt>Grabado</dt><dd>FLAMA S.A. N° serie año DPS · franja 130 × 12 mm (manuales) o dos renglones (carros)</dd><dt>Etiqueta</dt><dd>QR 45 × 25 mm, poliéster + resina, se renueva en cada servicio</dd>
        <dt>Plazos</dt><dd>reclamos de seguridad 24 h · resto 2 días hábiles · datos personales 10 días · recepción 48 h</dd><dt>Vencimientos</dt><dd>mantenimiento anual · PH cada 5 años · vida útil 20 años</dd></dl></div></div></div>`;
    if (t === "reg") c = `<div class="panel">${tabla(["Qué se mira", "Umbral", "Módulo", "Qué hace el sistema", "Base"], REGLAS.map(r => `<tr>${r.map((x, i) => `<td class="${i === 4 ? "mono" : ""}">${esc(x)}</td>`).join("")}</tr>`))}</div>`;
    if (t === "nor") c = `<div class="panel">${tabla(["Norma", "Cláusulas", "Para qué se usa en el sistema"], NORMAS.map(r => `<tr><td class="nw"><b>${esc(r[0])}</b></td><td class="mono">${esc(r[1])}</td><td>${esc(r[2])}</td></tr>`))}<p class="muted" style="padding:0 14px 12px;margin:0">Las normas se citan por cláusula; no se transcriben.</p></div>`;
    if (t === "int") c = `<div class="grilla"><div class="panel c4"><header><h2>Se lee</h2></header><div class="cuerpo"><dl class="dl" style="grid-template-columns:1fr"><dd><b>Aprovechamiento_Manuales › Plan mensual</b><br><span class="mono">${D.rangos.man}</span> del año · columnas D a O</dd><dd><b>Aprovechamiento_Carros › Plan mensual</b><br><span class="mono">${D.rangos.car}</span></dd><dd><b>Aprovechamiento_Recargas_Planta_Comercial / _Industrial › Plan mensual</b></dd><dd><b>FLAMA_MRP › POLITICA_STOCK y CONSOLIDADO</b></dd><dd><b>FLAMA_BOM › MODELOS</b></dd></dl></div></div>
      <div class="panel c4"><header><h2>Se guarda</h2></header><div class="cuerpo"><dl class="dl" style="grid-template-columns:1fr">${["OP · órdenes, partidas y series", "SERIES · estado, estampilla, custodia", "EVENTOS · qué, cuándo, quién, hash anterior y propio", "LOTES_INSUMO · lotes anotados en la hoja de ruta", "AGREGACION · equipo → caja → pallet → remito", "CUSTODIA · traspasos con documento", "FICHAS · rev. 0 de fábrica y rev. n de cada servicio", "RECLAMOS · DESVIOS · RETIROS"].map(x => `<dd>${esc(x)}</dd>`).join("")}</dl></div></div>
      <div class="panel c4"><header><h2>Sale</h2></header><div class="cuerpo"><dl class="dl" style="grid-template-columns:1fr"><dd><b>FLAMA_Trazabilidad (Google Sheets)</b><br>cada noche: OP, rendimiento, custodia, vencimientos, reclamos, desvíos</dd><dd><b>SGM de la AGC</b><br>archivo txt del proceso batch (Reportes)</dd><dd><b>Libro de actas DPS</b><br>estampillas, tarjetas e inutilizaciones (Reportes)</dd><dd><b>Avisos al cliente</b><br>vencimientos de mantenimiento y PH</dd></dl></div></div>
      <div class="panel c12"><div class="cuerpo"><dl class="dl"><dt>Arquitectura</dt><dd>página web en Vercel + base Postgres; Google Sheets por API con cuenta de servicio de solo lectura; copia nocturna en Sheets</dd><dt>Puestos</dt><dd>lector de mano USB en modo teclado; impresora de etiquetas desde el navegador; archivo de series para la marcadora</dd><dt>Campo</dt><dd>chofer, distribuidor e instalador desde el celular, leyendo el QR del remito o del equipo</dd><dt>Volumen 2035</dt><dd>≈ ${n0(284463 + 3107)} equipos/año · ≈ ${n0((284463 + 3107) * 3)} eventos/año: no entra en un Sheet (10 millones de celdas), por eso la base es Postgres</dd></dl></div></div></div>`;
    if (t === "usu") c = `<div class="grilla"><div class="panel c7"><header><h2>Roles y permisos</h2></header>${tabla(["Rol", "Puede"], [["PCP", "órdenes, remitos, reportes"], ["Producción", "registrar etapas, etiquetado"], ["Calidad", "cerrar lotes, medición, desvíos, retiros"], ["Responsable técnico", "visar cierres e inutilizaciones"], ["Recargas", "órdenes de servicio, sustitutos, inutilización"], ["Atención al cliente", "reclamos, clientes, instalaciones"], ["Distribuidor, chofer, instalador", "confirmar salida, recepción e instalación desde el QR"]].map(f => `<tr>${f.map(x => `<td>${esc(x)}</td>`).join("")}</tr>`))}</div>
      <div class="panel c5"><header><h2>Datos</h2></header><div class="cuerpo" style="display:flex;flex-direction:column;gap:10px"><dl class="dl"><dt>Del proyecto</dt><dd>Plan mensual y capacidad (Aprovechamiento_Manuales, _Carros, _Recargas), FLAMA_MRP, MRP_MP, FLAMA_BOM, palletizado_PT, Balanceo_Materiales_y_Linea</dd><dt>Registrados acá</dt><dd>etapas, firmas, rechazos, pesadas, ensayos, controles de medición, identificación, clientes, remitos, instalaciones, recargas, reclamos, desvíos, retiros e inventario</dd><dt>Registros</dt><dd>${S.eventos.length} eventos en este navegador</dd></dl><button class="btn" data-a="reiniciar">Borrar los registros de este navegador</button></div></div></div>`;
    return `<div class="filtros" role="tablist">${tabs.map(([k, x]) => `<button role="tab" aria-pressed="${t === k}" data-a="filtro" data-k="ctab" data-v="${k}">${x}</button>`).join("")}</div>${c}`;
  },
};
ACC.reiniciar = () => { reiniciar(); toast("Registros de este navegador borrados"); pintar(); };

// ---------------------------------------------------------------- traza y retiros
function afectados(lote) { const out = []; S.ordenes.filter(o => Object.values(o.insumos).some(v => v === lote)).forEach(o => { if (o.etapa < E["Para etiquetar"]) return; for (let n = o.desde; n <= o.hasta; n++) if (!o.rech.some(x => x.n === n)) out.push(n); }); return out; }
function traza(q) {
  q = (q || "").trim(); const Q = q.toUpperCase(); if (!q) return "";
  const n = numSerie(Q);
  if (n && ordenDe(n)) { const e = equipo(n), o = e.o;
    return `<div class="grilla"><div class="panel c6"><header><h2>← Hacia atrás</h2><span class="muted">${e.tipo} ${e.s}</span></header><div class="cuerpo"><ul class="lista-alertas">${[`Orden <a href="#" data-det="orden" data-id="${o.op}">${o.op}</a> · partida ${o.partida} · plan ${MES_TXT[o.mes - 1]}`, ...Object.entries(o.insumos).map(([k, v]) => `${k}: <span class="mono">${esc(v)}</span>`), ...hojaRuta(o).filter(h => h.firma && h.etapa < 6).map(h => `puesto ${h.puesto} · ${esc(h.op)} · ${esc(h.firma)}`)].map(x => `<li class="in"><span>${x}</span><span></span></li>`).join("")}</ul></div></div>
      <div class="panel c6"><header><h2>Hacia adelante →</h2><span class="muted">${pill(e.estado, estadoPill[e.estado])}</span></header><div class="cuerpo"><ul class="lista-alertas">${historia(e).filter(h => /Identificado|Despachado|Salida|Recibido|Instalado|Inutilizado/.test(h[1])).map(h => `<li class="ok"><span><b>${esc(h[1])}</b> · ${fecha(h[0])}<br><span class="muted">${esc(h[2])}</span></span><span></span></li>`).join("") || `<li class="in"><span>Sigue en planta</span><span></span></li>`}</ul>
      <a href="#" class="btn sm" data-det="equipo" data-id="${n}">Abrir el historial completo</a></div></div></div>`; }
  const o = S.ordenes.find(x => x.op.replace(/\s/g, "") === Q.replace(/\s/g, "") || x.op.replace("OP ", "") === Q);
  if (o) return `<div class="aviso in">Orden <b>${o.op}</b> · ${esc(o.modelo)} · ${o.cant} u · <a href="#" data-det="orden" data-id="${o.op}">abrir el historial del lote</a></div>`;
  const rm = S.remitos.find(r => r.id.replace(/\D/g, "").endsWith(Q.replace(/\D/g, "")) && Q.replace(/\D/g, "").length >= 4);
  if (rm) return `<div class="aviso in">Remito <a href="#" data-det="remito" data-id="${rm.id}">${rm.id}</a> · ${esc(cliente(rm.cliente).nombre)} · ${uRem(rm)} equipos · ${rm.ops.join(", ")}</div>`;
  const ops = S.ordenes.filter(x => Object.values(x.insumos).some(v => v.toUpperCase() === Q));
  if (ops.length) { const af = afectados(Object.values(ops[0].insumos).find(v => v.toUpperCase() === Q)), dist = {};
    af.forEach(k => { const e = equipo(k); const key = e.estado + "|" + e.custodia; dist[key] = (dist[key] || 0) + 1; });
    return `<div class="kpis"><div class="kpi in"><span>Órdenes</span><b>${ops.length}</b></div><div class="kpi in"><span>Equipos aptos</span><b>${n0(af.length)}</b></div><div class="kpi in"><span>Usuarios</span><b>${new Set(af.map(k => equipo(k).cliente && equipo(k).cliente.id).filter(Boolean)).size}</b></div><div class="kpi in"><span>Distribuidores</span><b>${new Set(ops.filter(x => x.remito).map(x => remito(x.remito).cliente)).size}</b></div></div>
      <div class="grilla"><div class="panel c6"><header><h2>Órdenes que usaron ${esc(q)}</h2></header>${tabla(["Orden", "Modelo", "Cant", "Etapa", "Remito"], ops.map(x => `<tr class="click" data-det="orden" data-id="${x.op}"><td class="mono">${x.op}</td><td>${esc(x.modelo)}</td><td class="num">${x.cant}</td><td>${pill(ETAPAS[x.etapa], etapaPill(x.etapa))}</td><td class="mono">${x.remito || "—"}</td></tr>`))}</div>
      <div class="panel c6"><header><h2>Dónde están</h2><button class="btn sm pri" data-a="nuevoRetiro" data-q="${esc(q)}">Abrir retiro preventivo</button></header>${tabla(["Estado", "Custodia", "Equipos"], Object.entries(dist).sort((a, b) => b[1] - a[1]).map(([k, v]) => { const [e, c] = k.split("|"); return `<tr><td>${pill(e, estadoPill[e])}</td><td>${esc(c)}</td><td class="num">${v}</td></tr>`; }), { vacio: "Ningún equipo cerrado con ese lote" })}</div></div>`; }
  return `<div class="aviso av">No encontré «${esc(q)}». Se busca una serie (${ser(1)} a ${ser(maxSerie())}), una orden del plan, un lote de insumo anotado en una hoja de ruta o un remito.</div>`;
}
VISTAS.traza = {
  titulo: "Traza y retiros",
  sub: () => "Hacia atrás (de dónde viene) y hacia adelante (dónde está) desde una serie, una orden, un lote de insumo o un remito · meta: menos de 2 minutos (criterio)",
  html() {
    const q = UI.f.trq || "", t0 = performance.now(), res = traza(q), ms = performance.now() - t0;
    return `<div class="panel"><div class="cuerpo"><form class="lector" data-f="traza"><input id="trq" value="${esc(q)}" placeholder="Serie, orden, lote de insumo o remito" aria-label="Buscar traza"><button class="btn pri" type="submit">Buscar</button></form>
      <div class="filtros" style="margin-top:10px">${[...new Set(S.ordenes.flatMap(o => Object.values(o.insumos)))].slice(-4).map(x => `<button data-a="trazaLote" data-q="${esc(x)}">${esc(x)}</button>`).join("")}${q ? `<span class="muted">respondido en ${nf(ms, 0)} ms</span>` : ""}</div></div></div>
      ${res}
      <div class="panel"><header><h2>Retiros preventivos</h2><span class="muted">bloquear series, ubicar cada equipo y cambiarlo sin costo</span></header>${tabla(["Retiro", "Fecha", "Lote", "Motivo", "Equipos", "Ubicados", "Estado", ""], S.retiros.map(x => { const a = afectados(x.lote), u = Math.round(a.length * x.ubicados);
        return `<tr><td class="mono">${x.id}</td><td>${fecha(x.fecha)}</td><td class="mono"><a href="#" data-a="trazaLote" data-q="${esc(x.lote)}">${esc(x.lote)}</a></td><td>${esc(x.motivo)}</td><td class="num">${a.length}</td><td style="min-width:140px">${barra(u, a.length, "var(--green)")}<small class="muted">${u} de ${a.length}</small></td><td>${pill(x.estado, x.estado === "Cerrado" ? "ok" : "no")}</td><td class="num">${x.estado !== "Cerrado" ? `<button class="btn sm" data-a="avanceRetiro" data-id="${x.id}">+10 % ubicados</button>` : ""}</td></tr>`; }), { vacio: "Sin retiros" })}</div>`;
  },
};
FORM.traza = () => { UI.f.trq = $("#trq").value; const o = S.ordenes.find(x => x.op.replace(/\s/g, "") === UI.f.trq.toUpperCase().replace(/\s/g, "")); o ? ir("lote", o.op) : pintar(); };
ACC.nuevoRetiro = el => { const r = { id: `RP-${AA}-${String(++S.nRp).padStart(2, "0")}`, fecha: ahoraISO(), lote: el.dataset.q, motivo: "Lote de insumo bajo sospecha: verificación preventiva", estado: "Abierto", ubicados: 0 };
  S.retiros.unshift(r); registrar("Retiro preventivo abierto", r.id, `${r.lote} · ${afectados(r.lote).length} equipos`); toast(`${r.id} abierto`); pintar(); };
ACC.avanceRetiro = el => abrirDetalle("retiro", el.dataset.id);
DETALLES.retiro = id => { const r = S.retiros.find(x => x.id === id), a = afectados(r.lote).length;
  return { titulo: `${r.id} · ${esc(r.lote)}`, sub: `${a} equipos afectados`, cuerpo: `<form class="form" data-f="regRetiro"><input type="hidden" id="rtId" value="${esc(id)}">
    <label class="campo">Equipos ubicados hasta hoy<input id="rtU" type="number" min="0" max="${a}" required value="${Math.round(r.ubicados * a)}"></label><div class="ancho"><button class="btn pri" type="submit">Registrar</button></div></form>` }; };
FORM.regRetiro = () => { const r = S.retiros.find(x => x.id === $("#rtId").value), a = Math.max(1, afectados(r.lote).length), u = +$("#rtU").value;
  r.ubicados = Math.min(1, u / a); if (r.ubicados >= 0.999) r.estado = "Cerrado"; registrar("Retiro: equipos ubicados", r.id, `${u} de ${a}`); ACC.cerrarDetalle(); pintar(); };

// ---------------------------------------------------------------- registro de eventos
VISTAS.eventos = {
  titulo: "Registro de eventos",
  sub: () => "Todo lo que se hizo en el sistema: nada se borra; una corrección es un evento nuevo · cada evento guarda el hash SHA-256 del anterior",
  acciones: () => `<button class="btn" data-a="verificarCadena">Verificar la cadena</button>`,
  html() {
    return `${UI.f.cadena ? `<div class="aviso ${UI.f.cadena.ok ? "ok" : "no"}">${UI.f.cadena.ok ? `✓ Cadena íntegra: ${UI.f.cadena.n} eventos verificados` : `✗ La cadena se rompe en el evento ${UI.f.cadena.i}: alguien modificó un registro anterior`}</div>` : ""}
      <div class="panel">${tabla(["Fecha y hora", "Evento", "Referencia", "Detalle", "Usuario", "Hash anterior", "Hash"], S.eventos.map(e => `<tr><td class="nw">${new Date(e.t).toLocaleString("es-AR")}</td><td>${esc(e.tipo)}</td><td class="mono">${esc(e.ref)}</td><td class="muted">${esc(e.detalle)}</td><td>${esc(e.quien)}</td><td class="mono muted">${esc((e.prev || "").slice(0, 12))}…</td><td class="mono">${e.hash ? e.hash.slice(0, 12) + "…" : "…"}</td></tr>`), { vacio: "Todavía no hay eventos en esta sesión: cerrá un lote, emití un remito o registrá una recarga y aparece acá" })}</div>`;
  },
};
ACC.verificarCadena = async () => { const ev = S.eventos.slice().reverse(); let prev = "0".repeat(64), i = 0;
  for (; i < ev.length; i++) { const e = ev[i]; if (e.prev !== prev) break; const h = await sha256(e.prev + e.t + e.tipo + e.ref + e.detalle + e.quien); if (h !== e.hash) break; prev = h; }
  UI.f.cadena = { ok: i === ev.length, n: ev.length, i: i + 1 }; pintar(); };
