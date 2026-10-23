// ================================================================ atención al cliente: portal del QR, bandeja con plazos y matriz normativa
const TIPOS = {
  seguridad: { t: "El equipo podría no funcionar", plazo: "contacto ≤ 24 h · sustituto ≤ 48 h" },
  garantia: { t: "Garantía del equipo", plazo: "respuesta ≤ 2 días hábiles" },
  servicio: { t: "Problema con una recarga", plazo: "se corrige sin costo (30 días)" },
  atencion: { t: "Atención o entrega", plazo: "respuesta ≤ 2 días hábiles" },
  datos: { t: "Mis datos personales", plazo: "≤ 10 días corridos" },
};
const ETAPAS = ["Recibido", "Acuse con número", "Evaluado", "Investigado con la traza", "Respondido", "Cerrado"];
let nRec = 118;
function reclamoEjemplo() { return { id: `RC-${AA}-000117`, tipo: "seguridad", tipoTxt: TIPOS.seguridad.t, texto: "El manómetro marca en la zona roja y el precinto está roto.", fecha: hoy(), etapa: 1, estado: "Abierto" }; }
const BANDEJA = [
  { id: `RC-${AA}-000109`, tipo: "atencion", serie: `${AA}-001502`, texto: "El instalador no dejó el acta firmada.", etapa: 5, estado: "Cerrado", hace: "6 días", ok: true },
  { id: `RC-${AA}-000112`, tipo: "garantia", serie: `${AA}-001611`, texto: "La manguera llegó fisurada.", etapa: 4, estado: "Respondido", hace: "3 días", ok: true },
  { id: `RC-${AA}-000115`, tipo: "servicio", serie: `${AA}-000874`, texto: "Después de la recarga pierde presión.", etapa: 3, estado: "En análisis", hace: "1 día", ok: true },
  { id: `RC-${AA}-000116`, tipo: "seguridad", serie: `${AA}-001198`, texto: "Se cayó y tiene un golpe en la cúpula.", etapa: 2, estado: "Vencido", hace: "27 h", ok: false },
];

function portal() {
  const c = S.cli, t = c.tab;
  const tabs = [["equipo", "Mi equipo"], ["servicio", "Servicio"], ["reclamo", "Reclamo"], ["datos", "Mis datos"], ["baja", "Baja de avisos"], ["arrep", "Arrepentimiento"]];
  let cuerpo = "";
  if (t === "equipo") cuerpo = paginaQR();
  if (t === "servicio") cuerpo = c.servicio
    ? `<div class="aviso ok">✓ Pedido SV-${AA}-004417 · te llamamos para coordinar el retiro</div><ul class="tl"><li><span><b>Antes de trabajar</b> te mandamos el presupuesto (Ley 24.240 art. 21)</span></li><li><span><b>Mientras tanto</b> te dejamos un equipo sustituto habilitado</span></li><li><span><b>Al terminar</b> recibís la constancia del servicio con lo que se cambió y 30 días de garantía</span></li></ul>`
    : `<div class="h2">Pedir mantenimiento</div><p class="sub" style="margin:0">${esc(CLI)} · vence en ${MES} ${D.anio + 1}</p>
       <label class="campo" for="svmodo">Cómo<select id="svmodo"><option>Retiro en mi domicilio con sustituto</option><option>Lo llevo a la planta de recargas</option></select></label>
       <label class="campo" for="svfecha">Desde qué fecha<input id="svfecha" type="date"></label>
       <p class="nota" style="margin:0">El sustituto queda en el mismo lugar mientras tu equipo está en el taller (IRAM 3517-2 9.4.5; Res. 349/07 art. 32).</p>
       <button class="btn pri" data-a="pedirServicio">Pedir el servicio</button>`;
  if (t === "reclamo") {
    const r = c.reclamos[0];
    cuerpo = r && !c.form ? `<div class="aviso ok">✓ Recibimos tu reclamo <b class="mono">${esc(r.id)}</b></div>
       <dl class="dl"><dt>Tipo</dt><dd>${esc(r.tipoTxt)}</dd><dt>Plazo</dt><dd>${esc(TIPOS[r.tipo].plazo)}</dd><dt>Estado</dt><dd>${esc(ETAPAS[r.etapa])}</dd></dl>
       <ul class="tl">${ETAPAS.map((e, i) => `<li class="${i <= r.etapa ? "" : "p"}"><span>${esc(e)}</span></li>`).join("")}</ul>
       <p class="nota" style="margin:0">Si la respuesta no te conforma podés ir a la Ventanilla Federal de Defensa del Consumidor o al COPREC (Ley 26.993). Te lo informamos en cada respuesta.</p><button class="btn sm" data-a="otroReclamo">Hacer otro reclamo</button>`
      : `<div class="h2">Hacer un reclamo</div><p class="sub" style="margin:0">No hace falta que busques el número: ya sabemos qué equipo es (${esc(CLI)}).</p>
       <label class="campo" for="rtipo">Qué pasa<select id="rtipo" data-i="rtipo">${Object.entries(TIPOS).map(([k, v]) => `<option value="${k}" ${c.tipo === k ? "selected" : ""}>${esc(v.t)}</option>`).join("")}</select></label>
       <label class="campo" for="rtexto">Contanos<textarea id="rtexto" rows="3" data-i="rtexto">${esc(c.texto)}</textarea></label>
       <label class="campo" for="rfoto">Foto (opcional)<input id="rfoto" type="file" accept="image/*"></label>
       <div class="aviso in" style="font-size:12.5px">Plazo: ${esc(TIPOS[c.tipo].plazo)}.${c.tipo === "seguridad" ? " Mientras tanto no lo tomes como tu único equipo." : ""}</div>
       <button class="btn pri" data-a="enviarReclamo">Enviar reclamo</button>`;
  }
  if (t === "datos") cuerpo = `<div class="h2">Tus datos</div>
       <dl class="dl"><dt>Qué</dt><dd>nombre o razón social, CUIT, dirección del equipo, mail y teléfono</dd><dt>Para qué</dt><dd>avisarte vencimientos, coordinar servicios y responder reclamos</dd><dt>Cuánto</dt><dd>los registros de servicio se guardan 6 años (IRAM 3517-2 9.4.16)</dd><dt>Quién ve</dt><dd>FLAMA y el recargador que elijas; la página del QR no muestra nada tuyo</dd></dl>
       ${c.datos ? `<div class="aviso ok">✓ Pedido ${esc(c.datos.id)} · respuesta hasta el ${esc(c.datos.vence)}</div>` : `<div class="fila"><button class="btn sm" data-a="datosAcceso">Pedir mis datos</button><button class="btn sm" data-a="datosCorregir">Corregir o borrar</button></div>`}
       <p class="nota" style="margin:0">Acceso: 10 días corridos (Ley 25.326 art. 14). Corrección o supresión: 5 días hábiles (art. 16). Podés reclamar ante la Agencia de Acceso a la Información Pública.</p>`;
  if (t === "baja") cuerpo = c.baja
    ? `<div class="aviso ok">✓ Listo. No te mandamos más avisos. Código de baja BJ-${AA}-00921</div><p class="nota" style="margin:0">Tu equipo sigue registrado: los recargadores e inspectores lo pueden consultar por el QR.</p>`
    : `<div class="h2">Dejar de recibir avisos</div><p class="sub" style="margin:0">Se da de baja por el mismo medio en que te anotaste, sin trámites ni llamados (Ley 24.240 art. 10 ter).</p><button class="btn pri" data-a="baja">Dar de baja los avisos</button>`;
  if (t === "arrep") cuerpo = `<div class="h2">Botón de arrepentimiento</div><p class="sub" style="margin:0">Si compraste por la web, tenés 10 días corridos desde que lo recibiste para revocar la compra (Ley 24.240 art. 34; CCyCN art. 1110).</p>
       <label class="campo" for="pedido">N° de pedido<input id="pedido" value="WEB-${AA}-03318"></label>
       ${c.arrep ? `<div class="aviso ok">✓ Código de revocación ARR-${AA}-00057 · te lo mandamos también por mail</div>` : `<button class="btn pri" data-a="arrepentirse">Me arrepiento de la compra</button>`}
       <p class="nota" style="margin:0">El código sale en el momento; la norma da 24 h (Res. SCI 424/2020).</p>`;
  return tel(`<div class="filtros" role="tablist" aria-label="Portal del cliente">${tabs.map(([k, v]) => `<button role="tab" aria-pressed="${t === k}" data-a="ct" data-k="${k}">${esc(v)}</button>`).join("")}</div>${cuerpo}`, "flama · cliente");
}

function bandeja() {
  const filas = [...S.cli.reclamos.map(r => Object.assign({ serie: CLI, hace: "ahora", ok: true, mio: true }, r)), ...BANDEJA];
  return `<div class="tscroll"><table class="tabla"><thead><tr><th>Reclamo</th><th>Qué pasa</th><th>Estado</th></tr></thead><tbody>
    ${filas.map((r, i) => `<tr><td class="nw"><span class="mono">${esc(r.id)}</span><div class="nota mono">${esc(r.serie)}</div></td><td><b>${esc(TIPOS[r.tipo].t)}</b><div class="nota">«${esc(r.texto)}»</div></td>
    <td><div class="nw">${esc(ETAPAS[r.etapa])}</div><span class="pill ${r.estado === "Cerrado" ? "ok" : r.ok ? "in" : "no"}">${esc(r.estado === "Vencido" ? "vencido · " + r.hace : r.estado + " · " + r.hace)}</span>${r.etapa < 5 && r.mio && i === 0 ? `<div style="margin-top:6px"><button class="btn sm" data-a="avanzarReclamo">Pasar a la etapa siguiente</button></div>` : ""}</td></tr>`).join("")}</tbody></table></div>`;
}

const PLAZOS = [
  ["Seguridad: el equipo podría no funcionar", "inmediato", "contacto ≤ 24 h", "sustituto ≤ 48 h", "criterio FLAMA · IRAM 3517-2 9.4.5"],
  ["Garantía del equipo", "inmediato", "≤ 2 días hábiles", "≤ 10 días hábiles", "Ley 24.240 art. 11-17 · plazos: criterio"],
  ["Deficiencia de una recarga", "inmediato", "≤ 2 días hábiles", "sin costo, si aparece dentro de 30 días", "Ley 24.240 art. 23"],
  ["Acceso a datos personales", "inmediato", "—", "≤ 10 días corridos", "Ley 25.326 art. 14"],
  ["Corrección o supresión de datos", "inmediato", "—", "≤ 5 días hábiles", "Ley 25.326 art. 16"],
  ["Arrepentimiento de compra web", "código ≤ 24 h", "—", "10 días corridos para ejercerlo", "Res. SCI 424/2020 · Ley 24.240 art. 34"],
  ["Baja de avisos o del contrato de mantenimiento", "inmediata", "—", "—", "Ley 24.240 art. 10 ter"],
];
const MATRIZ = [
  ["Ley 24.240 art. 4", "Información cierta, clara y detallada del producto.", "La página del QR muestra modelo, clases de fuego, vencimientos de mantenimiento y PH, vida útil y la historia del equipo.", "QR · Comercial"],
  ["Ley 24.240 art. 8 bis", "Trato digno; nada intimidatorio ni vejatorio.", "Avisos de vencimiento informativos (sin «multas» ni amenazas); plantillas de respuesta revisadas por calidad.", "Avisos · Reclamos"],
  ["Ley 24.240 art. 10 ter", "La baja se hace por el mismo medio que el alta.", "Botón «Dejar de recibir avisos» en el pie de cada página del QR, sin registro previo.", "Portal · Baja"],
  ["Ley 24.240 art. 11 y 14", "Garantía legal de 6 meses para cosas nuevas; certificado con su contenido.", "La garantía se emite al firmar el acta de instalación y queda en la ficha del equipo con su fecha de inicio.", "Recorrido · paso 11"],
  ["Ley 24.240 art. 15", "Constancia de reparación: qué se hizo, piezas, fechas de entrega y devolución.", "Al cerrar la ficha rev. n la app manda la constancia con agente, precinto, piezas y fechas.", "Recorrido · paso 14"],
  ["Ley 24.240 art. 21", "Presupuesto previo al servicio.", "Recepción de recargas emite el presupuesto PR antes de abrir la ficha; sin aceptación no se trabaja.", "Recorrido · paso 14"],
  ["Ley 24.240 art. 23", "Defectos del servicio dentro de 30 días: se corrigen sin costo.", "Cada ficha de servicio muestra «garantía del servicio hasta…»; un reclamo dentro de ese plazo abre una orden sin cargo.", "Reclamos"],
  ["Ley 24.240 art. 34 · Res. SCI 424/2020", "Botón de arrepentimiento en ventas a distancia; código en 24 h.", "Enlace en el pie del QR y de la tienda; el código sale en el momento.", "Portal · Arrepentimiento"],
  ["Ley 26.993", "Vías de conciliación en relaciones de consumo.", "Cada respuesta informa la Ventanilla Federal y el COPREC si el cliente no queda conforme.", "Reclamos"],
  ["Ley 25.326 art. 6 y 9", "Informar finalidad y proteger los datos.", "Aviso al titular en la instalación; la página pública del QR no muestra datos del dueño.", "Recorrido · pasos 11 y 12"],
  ["Ley 25.326 art. 14 y 16", "Acceso en 10 días corridos; corrección o supresión en 5 días hábiles.", "Pedidos desde «Mis datos» con vencimiento calculado y alerta en Desvíos si se pasa.", "Portal · Mis datos"],
  ["Ley 25.326 art. 21", "Inscripción de la base de datos.", "La base de trazabilidad se inscribe en el registro de la AAIP antes de salir a producción.", "Manual · 6"],
  ["Res. 349/07 (PBA) art. 21-23, 32, 46", "Tarjeta DPS, estampillas propias numeradas en el libro, sustituto habilitado.", "La app asigna estampilla por serie y arma el libro de actas; el sustituto lleva tarjeta con sello «sustituto habilitado».", "Recorrido · pasos 6, 11 y 14"],
  ["Res. 349/07 (PBA) art. 25", "Condiciones que el usuario debe controlar en su equipo.", "Solapa «Revisalo vos» del QR con los controles a-f en lenguaje simple.", "QR · Revisalo vos"],
  ["Res. 349/07 (PBA) art. 27-29", "Inutilización con corte de rosca; fechas en el tubo de pesca; oblea de PH.", "Reglas de recarga e inutilización por jurisdicción con acta y aviso al propietario.", "Recorrido · pasos 14 y 15"],
  ["Res. 32-AGC/15 (CABA) anexo II", "Cada fabricación o recarga se registra en el SGM; la tarjeta lleva QR de validación.", "La app arma el archivo del proceso batch con los datos del art. 4; el QR FLAMA no reemplaza la tarjeta oficial.", "Recorrido · paso 11"],
  ["IRAM 3517-2 9.4.14 y 9.4.16", "Etiqueta con n° de serie renovada en cada servicio; registros 6 años.", "Etiqueta nueva con el mismo QR en cada ficha; la base guarda todo el historial con hash.", "Recorrido · paso 14"],
  ["IRAM-ISO 10002", "Tratamiento de quejas: visible, accesible, con respuesta, objetivo, confidencial y con mejora continua.", "Reclamo desde el QR con número, etapas y plazos; cada causa se analiza en Desvíos.", "Bandeja · Desvíos"],
];

function vistaClientes() {
  return `<div class="cabeza wrap"><div class="cabeza-in"><div><div class="ceja">Atención al cliente</div><h1>Del QR a la respuesta</h1>
    <p>El cliente escanea su equipo y desde ahí pide servicio, reclama, ve sus datos o se da de baja. FLAMA recibe el reclamo con el equipo ya identificado y lo responde dentro de un plazo que se mide.</p></div>
    <div class="doc-id">Política AC-01 · rev. 0<br>Base: Ley 24.240 · Ley 25.326 · Res. 349/07 · Res. 32-AGC/15 · IRAM-ISO 10002</div></div></div>
  <div class="cuerpo wrap"><div class="dos-col">
    <div class="pila"><div class="bloque" style="display:grid;place-items:center;background:radial-gradient(120% 90% at 50% 0%, var(--surface-2), var(--bg))">${portal()}</div></div>
    <div class="pila">
      <div class="bloque"><h3>Bandeja de reclamos</h3><p class="sub">Lo que ve atención al cliente. Los que mandes desde el celular aparecen arriba.</p>${bandeja()}</div>
      <div class="bloque"><h3>Plazos de respuesta</h3><p class="sub">Los que fija la ley se cumplen tal cual; los marcados «criterio» los fija FLAMA y se miden en Desvíos.</p>
        <div class="tscroll"><table class="tabla"><thead><tr><th>Pedido</th><th>Acuse</th><th>Primera respuesta</th><th>Resolución</th><th>Base</th></tr></thead><tbody>
        ${PLAZOS.map(f => `<tr>${f.map((c, i) => `<td class="${i === 4 ? "nota" : ""}">${esc(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div></div>
      <div class="bloque"><h3>Cómo se trata un reclamo</h3><p class="sub">Etapas de IRAM-ISO 10002, cada una con su evento en la base.</p>
        <ul class="tl">${ETAPAS.map((e, i) => `<li><span><b>${esc(e)}</b> · ${["entra por el QR, el mail o el teléfono y se carga igual", "número y plazo en el momento", "seguridad primero: si el equipo puede no funcionar, sustituto", "la traza muestra lote, insumos, ensayos y otros reclamos del mismo lote", "respuesta escrita con la vía de conciliación", "encuesta de una pregunta; la causa pasa a Desvíos"][i]}</span></li>`).join("")}</ul></div>
    </div></div>
    <div class="bloque" style="margin-top:22px"><h3>Matriz normativa</h3><p class="sub">Qué exige cada norma y dónde lo cumple la app.</p>
      <div class="tscroll"><table class="tabla matriz"><thead><tr><th>Norma</th><th>Qué exige</th><th>Cómo lo cumple la app</th><th>Dónde se ve</th></tr></thead><tbody>
      ${MATRIZ.map(f => `<tr><td>${esc(f[0])}</td><td>${esc(f[1])}</td><td>${esc(f[2])}</td><td><span class="pill vi">${esc(f[3])}</span></td></tr>`).join("")}</tbody></table></div></div>
  </div>`;
}

Object.assign(ACC, {
  ct(el) { S.cli.tab = el.dataset.k; pintar(); },
  async pedirServicio() { S.cli.servicio = true; await evento("SERVICIO SOLICITADO", CLI, "cliente · QR", { id: "SV-" + AA + "-004417" }); pintar(); },
  async enviarReclamo() {
    const r = { id: `RC-${AA}-${String(nRec++).padStart(6, "0")}`, tipo: S.cli.tipo, tipoTxt: TIPOS[S.cli.tipo].t, texto: S.cli.texto, fecha: hoy(), etapa: 1, estado: "Abierto" };
    S.cli.reclamos.unshift(r); S.cli.form = false; await evento("RECLAMO RECIBIDO · ACUSE", r.id, "cliente · QR", { serie: CLI, tipo: r.tipo }); pintar();
  },
  otroReclamo() { S.cli.form = true; pintar(); },
  async avanzarReclamo() { const r = S.cli.reclamos[0]; if (!r) return; r.etapa = Math.min(5, r.etapa + 1); r.estado = r.etapa === 5 ? "Cerrado" : r.etapa === 4 ? "Respondido" : "En análisis"; await evento("RECLAMO · " + ETAPAS[r.etapa].toUpperCase(), r.id, "atención"); pintar(); },
  async resolverReclamo() {
    if (!S.cli.reclamos.length) S.cli.reclamos.unshift(reclamoEjemplo());
    const r = S.cli.reclamos[0]; r.etapa = 5; r.estado = "Cerrado"; await evento("RECLAMO CERRADO · SUSTITUTO", r.id, "atención + calidad"); pintar();
  },
  async datosAcceso() { S.cli.datos = { id: `DP-${AA}-0031`, vence: sumarDias(10) }; await evento("PEDIDO DE ACCESO A DATOS", S.cli.datos.id, "cliente"); pintar(); },
  async datosCorregir() { S.cli.datos = { id: `DP-${AA}-0032`, vence: sumarDias(5, true) }; await evento("PEDIDO DE CORRECCIÓN DE DATOS", S.cli.datos.id, "cliente"); pintar(); },
  async baja() { S.cli.baja = true; await evento("BAJA DE AVISOS", CLI, "cliente · QR"); pintar(); },
  async arrepentirse() { S.cli.arrep = true; await evento("ARREPENTIMIENTO · CÓDIGO", `ARR-${AA}-00057`, "cliente · web"); pintar(); },
});
INPUT.rtipo = v => { S.cli.tipo = v; return true; };
INPUT.rtexto = v => { S.cli.texto = v; };
