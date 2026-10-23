// Trazabilidad interna FLAMA (sin QR). Datos fijos en D (build.py, libros 2035 de MP, PT y balanceo); lo que pasa en
// planta (conteos, pedidos, formularios, pallets, revendidos) arranca vacío y se guarda en este navegador. El stock de MP
// se carga con la planilla de conteo del almacén (Excel); no hay cámaras.
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const nf = (x, d = 0) => (x === null || x === undefined || x === "" || isNaN(x)) ? "—" :
  Number(x).toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
const hoy = () => new Date().toISOString().slice(0, 10);
const ahora = () => new Date().toISOString().slice(0, 16).replace("T", " ");
const fecha = (iso) => iso ? iso.slice(8, 10) + "/" + iso.slice(5, 7) + "/" + iso.slice(2, 4) : "—";
const dias = (iso) => iso ? Math.floor((Date.now() - new Date(iso + "T00:00").getTime()) / 864e5) : null;

// ---------------------------------------------------------------- estado (localStorage)
const CLAVE = "flama-traza-simple-v2";
const VACIO = () => ({ stock: {}, pedidos: {}, pallets: {}, regs: [], rev: [], n: {}, verOk: false });
let S;
let GUARDADO = null;
try { GUARDADO = JSON.parse(localStorage.getItem(CLAVE) || "null"); } catch (e) { GUARDADO = null; }
S = Object.assign(VACIO(), GUARDADO || {});
const guardar = () => { try { localStorage.setItem(CLAVE, JSON.stringify(S)); } catch (e) { /* sin almacenamiento */ } };
const sig = (k) => (S.n[k] = (S.n[k] || 0) + 1);

// ---------------------------------------------------------------- catálogos
// Modelos propios: espesor de la chapa del cuerpo (Stock_MP MP-01 a MP-04, MP-11 y MP-12) y presión de ensayo
// (DOC-02 R3: 3,5 MPa manuales, 4,0 MPa rodantes).
const MODELOS = [
  { m: "ABC 1 kg", t: 0.9, pe: 3.5, car: false }, { m: "ABC 2,5 kg", t: 1.25, pe: 3.5, car: false },
  { m: "ABC 5 kg", t: 1.6, pe: 3.5, car: false }, { m: "ABC 10 kg", t: 2.0, pe: 3.5, car: false },
  { m: "Carro ABC 25 kg", t: 3.2, pe: 4.0, car: true }, { m: "Carro ABC 50 kg", t: 3.2, pe: 4.0, car: true },
  { m: "Carro ABC 70 kg", t: 4.75, pe: 4.0, car: true }, { m: "Carro ABC 100 kg", t: 4.75, pe: 4.0, car: true },
];
const MOD = (m) => MODELOS.find((x) => x.m === m);
const RV = D.mp.filter((x) => x.cod.startsWith("RV-"));
const MP = Object.fromEntries(D.mp.map((x) => [x.cod, x]));
const PUESTO = (l, n) => (D.puestos[l].find((p) => p.n === n) || {}).nom || "";
// Instrumentos (registro de instrumentos del sistema anterior); los modelos sin confirmar quedan como «a definir».
const INSTR = {
  ph: ["PH-M1 · banco de PH Firesafer FS-JD12A", "PH-M2 · banco de PH Yukon M-000200"],
  esp: ["ESP-1 · medidor de espesor Melisam MR017"],
  pel: ["EP-1 · medidor de película ISO 2808 (modelo a definir)"],
};
// Almacenes (MP-FLAMA2035 › Almacenes, filas 19 a 31) con sus lugares y el lugar fijo de cada código (build.py)
const ALMS = D.alm;
const ALM = Object.fromEntries(ALMS.map((a) => [a.alm, a]));

// ---------------------------------------------------------------- kanban de MP
// Punto de pedido = seguridad + consumo mientras llega (Stock_MP L + K). La revisión periódica del Word de MP
// (cada «cada» días se pide hasta el máximo) sigue; el kanban avisa si entre dos revisiones se cruza el punto.
const COLS = [
  { k: "crit", t: "Bajo seguridad", c: "crit" }, { k: "pedir", t: "Pedir", c: "warn" },
  { k: "ped", t: "Pedido en camino", c: "info" }, { k: "ok", t: "Bien", c: "ok" },
  { k: "sin", t: "Sin conteo", c: "idle" }];
// Se compara la posición (stock + lo pedido que viene en camino) con el punto de pedido; la seguridad, con el stock físico.
function estado(m) {
  const s = S.stock[m.cod];
  if (!s) return "sin";
  if (s.u <= m.ss) return "crit";
  if (S.pedidos[m.cod]) return "ped";
  if (s.u <= m.pp) return "pedir";
  return "ok";
}
const bultos = (m, u) => Math.ceil(u / (m.cont || 1));
// Días de stock = unidades ÷ consumo por día (Stock_MP, col. G: consumo del año ÷ 240 días hábiles).
const diasDe = (m, u) => (m.dia > 0 && u != null ? u / m.dia : null);
const diasStock = (m) => (S.stock[m.cod] ? diasDe(m, S.stock[m.cod].u) : null);
const txtD = (d) => (d == null ? "—" : d >= 999 ? "+999 d" : nf(d, d < 10 ? 1 : 0) + " d");
function barra(m) {
  const s = S.stock[m.cod], mx = Math.max(m.max, s ? s.u : 0, m.pp) || 1, e = estado(m);
  const w = s ? Math.min(100, s.u / mx * 100) : 0;
  const cls = { crit: "crit", pedir: "warn", ped: "info", ok: "", sin: "" }[e];
  return `<div class="barra" title="seguridad ${nf(m.ss, 1)} · punto de pedido ${nf(m.pp, 1)} · máximo ${nf(m.max, 1)} ${esc(m.um)}">
    <i class="${cls}" style="width:${w}%"></i><u class="ss" style="left:${m.ss / mx * 100}%"></u><u style="left:${Math.min(99.5, m.pp / mx * 100)}%"></u></div>`;
}
const colorLinea = (l) => /Reventa/.test(l || "") ? "var(--ext)" : /^Carros/.test(l || "") ? "var(--car)" : /^Recargas/.test(l || "") ? "var(--rec)" : "var(--man)";
function tarjeta(m) {
  const s = S.stock[m.cod];
  return `<button class="tarjeta" data-mp="${esc(m.cod)}" style="--c:${colorLinea(m.linea)}">
    <span class="t1"><b>${esc(m.cod)}</b><span class="mut" style="font-size:11px;display:flex;align-items:center;gap:4px">${esc(m.ref)}${figFormato((ALM[m.alm] || {}).pref, fraccion(m), COLOR_EST[estado(m)], 22, 18)}</span></span>
    <span class="mat">${esc(m.mat.replace(/\s*\(.*\)$/, ""))}</span>${barra(m)}
    <span class="t3"><span class="num">${s ? nf(s.u, 0) : "—"} ${esc(m.um)} · <b>${txtD(diasStock(m))}</b></span><span>pedir en ${txtD(diasDe(m, m.pp))}</span></span></button>`;
}
const F = { alm: "", lin: "", q: "" };
function filtrar() {
  const q = F.q.toLowerCase();
  return D.mp.filter((m) => (!F.alm || m.alm === F.alm) && (!F.lin || (m.linea || "").includes(F.lin)) &&
    (!q || (m.cod + " " + m.mat + " " + m.prov).toLowerCase().includes(q)));
}
function vMP() {
  const lista = filtrar(), por = Object.fromEntries(COLS.map((c) => [c.k, []]));
  lista.forEach((m) => por[estado(m)].push(m));
  const almOpts = ALMS.map((a) => `<option ${F.alm === a.alm ? "selected" : ""}>${esc(a.alm)}</option>`).join("");
  const linOpts = ["Manuales", "Carros", "Recargas", "Reventa"].map((l) => `<option ${F.lin === l ? "selected" : ""}>${l}</option>`).join("");
  const sinNada = !Object.keys(S.stock).length;
  return `${bandaEjemplo()}<div class="cab"><div><h1>Kanban de MP</h1>
    <p>Cada tarjeta es una MP. Se mueve con cada planilla de conteo, retiro a la línea o recepción.</p></div>
    <div class="filtros"><select id="fAlm" aria-label="Almacén"><option value="">Todos los almacenes</option>${almOpts}</select>
    <select id="fLin" aria-label="Línea"><option value="">Todas las líneas</option>${linOpts}</select>
    <input id="fQ" type="search" placeholder="Código, material o proveedor" value="${esc(F.q)}" aria-label="Buscar">
    <button class="btn pri" data-a="planilla">Cargar planilla</button><button class="btn" data-a="bajarPlanilla">Descargar planilla</button></div></div>
    ${sinNada ? `<div class="aviso" style="margin-bottom:12px">Sin conteos todavía: cargá la planilla del almacén. <button class="btn chico" data-a="arranque" style="margin-left:6px">Arrancar con el almacén lleno</button></div>` : ""}
    <div class="tablero">${COLS.map((c) => {
      const plegada = c.k === "ok" && !S.verOk && por.ok.length > 6;
      const lista = plegada ? por[c.k].slice(0, 4) : por[c.k];
      return `<section class="col ${c.c}"><h3>${c.t}<span class="num">${por[c.k].length}</span></h3>
      <div class="lista">${lista.map(tarjeta).join("") || `<div class="vacio">Nada acá</div>`}
      ${plegada ? `<button class="btn chico" data-a="verOk">Ver las ${por.ok.length - 4} restantes</button>` : ""}</div></section>`; }).join("")}</div>
    <details class="fuente"><summary>De dónde salen los números</summary>${esc(D.fuente.mp)}. Seguridad = columna L; punto de pedido = L + K (consumo mientras llega el pedido); máximo = S. Se compara el punto de pedido con la posición: stock + lo pedido que viene en camino.</details>`;
}
function detalleMP(cod) {
  const m = MP[cod], s = S.stock[cod], p = S.pedidos[cod], e = estado(m);
  const sug = Math.max(0, m.max - (s ? s.u : 0)), sugB = bultos(m, sug);
  const pill = { crit: "crit", pedir: "warn", ped: "info", ok: "ok", sin: "idle" }[e];
  abrir(`${esc(m.cod)} · ${esc(m.mat)}`, `
    <div><span class="pill ${pill}">${COLS.find((c) => c.k === e).t}</span> ${barra(m)}</div>
    <dl class="dl">
      <dt>Stock</dt><dd class="num">${s ? `${nf(s.u, 1)} ${esc(m.um)} · ${nf(bultos(m, s.u))} × ${esc(m.bulto)} <span class="mut">(${esc(s.src)}, ${esc(s.t)})</span>` : "sin lectura"}</dd>
      <dt>Días de stock</dt><dd class="num"><b>${txtD(diasStock(m))}</b> <span class="mut">con ${nf(m.dia, m.dia < 10 ? 2 : 1)} ${esc(m.um)} por día (Stock_MP!G${m.fila}) · días hábiles</span></dd>
      <dt>Seguridad</dt><dd class="num">${nf(m.ss, 1)} ${esc(m.um)} · ${txtD(diasDe(m, m.ss))} <span class="mut">Stock_MP!L${m.fila}</span></dd>
      <dt>Punto de pedido</dt><dd class="num">${nf(m.pp, 1)} ${esc(m.um)} · ${txtD(diasDe(m, m.pp))} = seguridad + ${nf(m.k, 1)} que se consumen mientras llega <span class="mut">L${m.fila} + K${m.fila}</span></dd>
      <dt>Stock máximo</dt><dd class="num">${nf(m.max, 1)} ${esc(m.um)} · ${txtD(diasDe(m, m.max))} <span class="mut">Stock_MP!S${m.fila}</span></dd>
      <dt>Se compra</dt><dd>${esc(m.bulto)} · se pide cada ${esc(m.cada)} días hábiles · plazo ${esc(m.pmin)} a ${esc(m.pmax)} días</dd>
      <dt>Proveedor</dt><dd>${esc(m.prov)}</dd>
      <dt>Almacén</dt><dd>${esc(m.alm)} · lugar ${esc(m.lugares.join(", ") || "—")} <a href="#almacen" data-cerrar style="font-size:12.5px">ver en el almacén</a></dd>
      <dt>Cómo se guarda</dt><dd style="font-size:12.5px">${esc(m.guarda)}</dd>
      ${p ? `<dt>Pedido</dt><dd>${nf(p.cant, 1)} ${esc(m.um)} el ${esc(p.t)} a ${esc(m.prov)}</dd>` : ""}</dl>
    <form class="campos" id="fMov">
      <div class="campo"><label for="mvT">Movimiento</label><select id="mvT"><option value="conteo">Conteo (deja el stock en)</option>
        <option value="retiro">Retiro a la línea (resta)</option></select></div>
      <div class="campo"><label for="mvU">Cantidad (${esc(m.um)})</label><input id="mvU" type="number" step="any" min="0" required></div>
      <div class="campo"><label for="mvS">Fuente</label><select id="mvS"><option>Conteo a mano</option><option>Planilla de conteo</option><option>Vale de retiro</option></select></div>
      <div class="campo" style="align-self:end"><button class="btn pri" type="submit">Registrar</button></div></form>
    <div class="filtros">${p ? `<button class="btn" data-a="recibir" data-id="${esc(cod)}">Registrar la recepción (formulario FAB-01)</button>
      <button class="btn" data-a="anularPed" data-id="${esc(cod)}">Anular pedido</button>` :
      `<button class="btn" data-a="pedir" data-id="${esc(cod)}" data-cant="${sugB * m.cont}">Emitir pedido: ${nf(sugB)} × ${esc(m.bulto)} (hasta el máximo)</button>`}</div>`);
  $("#fMov").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const t = $("#mvT").value, u = parseFloat($("#mvU").value);
    if (isNaN(u)) return;
    const prev = S.stock[cod] ? S.stock[cod].u : 0;
    if (t === "retiro" && !S.stock[cod]) { toast("Primero registrá un conteo: no hay stock para descontar"); return; }
    S.stock[cod] = { u: t === "retiro" ? Math.max(0, prev - u) : u, src: $("#mvS").value, t: ahora() };
    guardar(); cerrar(); pintar(); toast(`${cod}: ${nf(S.stock[cod].u, 1)} ${m.um}`);
  });
}

// ---------------------------------------------------------------- almacén de MP: lugares
// Cada almacén con sus lugares (Almacenes, col. E) y el código fijo de cada lugar (build.py › lugares). Los racks se
// dibujan por módulo: 2 pallets por nivel, abajo lo que se usa y arriba la reposición (Word de MP, sección 8).
const COLOR_EST = { crit: "var(--critical)", pedir: "var(--warn)", ped: "var(--info)", ok: "var(--good)", sin: "var(--border-strong)" };
const PEOR = ["crit", "pedir", "ped", "ok", "sin"];
const ultimoConteo = (alm) => D.mp.filter((m) => m.alm === alm).map((m) => S.stock[m.cod])
  .filter((s) => s && /^(Planilla|Conteo)/.test(s.src)).map((s) => s.t).sort().pop();
function lugarHtml(h, pref) {
  if (!h.cods.length) return `<div class="lugar libre"><span class="lug-cab"><em>${h.id}</em>${figFormato(pref, 0, "#fff", 38, 31)}</span><span>libre</span></div>`;
  const est = h.cods.map(([c]) => estado(MP[c])).sort((a, b) => PEOR.indexOf(a) - PEOR.indexOf(b))[0];
  const prin = MP[h.cods.slice().sort((a, b) => b[1] - a[1])[0][0]];
  return `<div class="lugar e-${est}"><span class="lug-cab"><em>${h.id}</em>${figFormato(pref, fraccion(prin), COLOR_EST[estado(prin)], 38, 31)}</span>${h.cods.map(([c, f]) => {
    const m = MP[c], s = S.stock[c], e = estado(m), w = s ? Math.min(100, s.u / (Math.max(m.max, m.pp) || 1) * 100) : 0;
    return `<button class="cod" data-mp="${esc(c)}" title="${esc(c)} · ${esc(m.mat)}${f < 1 ? ` · ${Math.round(f * 100)} % del lugar` : ""} · ${s ? nf(s.u, 1) + " " + esc(m.um) + " · " + txtD(diasDe(m, s.u)) : "sin conteo"}">
      <b>${esc(c)}</b><i style="--w:${w.toFixed(0)}%;--c:${COLOR_EST[e]}"></i></button>`; }).join("")}</div>`;
}
function almacenHtml(a) {
  const hs = D.lugares[a.alm] || [], ms = D.mp.filter((m) => m.alm === a.alm);
  const al = ms.filter((m) => ["crit", "pedir"].includes(estado(m))).length, uc = ultimoConteo(a.alm);
  let cuerpo;
  if (hs.length && hs[0].mod) {
    const mods = [...new Set(hs.map((h) => h.mod))], niv = Math.max(...hs.map((h) => h.niv));
    cuerpo = `<div class="rack-mp">${mods.map((md) => `<div class="modulo">${Array.from({ length: niv }, (_, i) => niv - i).map((n) =>
      `<div class="nivel">${["A", "B"].map((l) => { const h = hs.find((x) => x.mod === md && x.niv === n && x.lado === l); return h ? lugarHtml(h, a.pref) : `<div class="lugar nada"></div>`; }).join("")}</div>`).join("")}
      <span class="pie">módulo ${md}</span></div>`).join("")}</div>`;
  } else cuerpo = `<div class="fila-mp">${hs.map((h) => lugarHtml(h, a.pref)).join("")}</div>`;
  return `<section class="alm-card ${al ? "con-alarma" : ""}" id="alm-${a.pref}"><header><div class="fmt-nom">${figFormato(a.pref, 1, "var(--surface-3)", 46, 38)}<div><h3>${esc(a.alm)}</h3>
      <span class="fmt-txt">${esc(FORMATO[a.pref] || "")}</span><br><span class="mut">${esc(a.est)} · ${hs.length} lugares${a.m2 ? ` · ${nf(a.m2, 1)} m²` : ""} · ${ms.length} códigos</span></div></div>
      ${al ? `<span class="pill crit">${al} para pedir</span>` : `<span class="pill ok">sin faltantes</span>`}</header>
    ${cuerpo}
    <footer><span class="mut">Último conteo: ${uc ? esc(uc) : "—"}</span><span class="acciones">
      <button class="btn chico" data-a="conteo" data-id="${esc(a.alm)}">Contar a mano</button>
      <button class="btn chico" data-a="bajarPlanilla" data-id="${esc(a.alm)}">Planilla de este almacén</button></span></footer></section>`;
}
function vAlmacen() {
  const ley = [["crit", "Bajo seguridad"], ["pedir", "Pedir"], ["ped", "Pedido en camino"], ["ok", "Bien"], ["sin", "Sin conteo"]];
  return `${bandaEjemplo()}<div class="cab"><div><h1>Almacén de MP</h1>
    <p>Cada lugar con su código fijo. El color es el estado del código; la barra, el stock contra el máximo.</p></div>
    <div class="filtros"><button class="btn pri" data-a="planilla">Cargar planilla</button><button class="btn" data-a="bajarPlanilla">Descargar planilla</button><a class="btn" href="#semaforo">Semáforo</a></div></div>
    <div class="saltos">${ALMS.map((a) => { const n = D.mp.filter((m) => m.alm === a.alm && ["crit", "pedir"].includes(estado(m))).length;
      return `<button data-salto="alm-${a.pref}">${figFormato(a.pref, 1, "var(--surface-3)", 20, 16)}${esc(a.corto)}${n ? ` <b>${n}</b>` : ""}</button>`; }).join("")}</div>
    <div class="leyenda" style="margin:0 0 12px">${ley.map(([k, t]) => `<span><i style="background:${COLOR_EST[k]}"></i>${t}</span>`).join("")}<span><i style="background:transparent;border:1px dashed var(--border-strong)"></i>Libre</span>
      <span class="mut">· El dibujo de cada lugar es el formato en que se guarda, lleno según el stock contra el máximo.</span></div>
    <div class="almacenes">${ALMS.map(almacenHtml).join("")}</div>
    <details class="fuente"><summary>De dónde salen los lugares</summary>Lugares de cada almacén: ${esc(D.fuente.mp.split(" y ")[1] || "Almacenes")}, columna E.
      Cada código ocupa los lugares enteros de su columna U de Stock_MP (cuánto ocupa el stock máximo) y los restos de varios códigos comparten un lugar
      (criterio: de mayor a menor, en el primero donde entran). En los racks, los lugares de un código quedan apilados en la misma columna: abajo el que se usa,
      arriba la reposición (Word de MP, sección 8). El rack de flejes tiene 4 alturas (sección 6.2); los demás, piso y 2 largueros.</details>`;
}
function dlgConteo(alm) {
  const ms = D.mp.filter((m) => m.alm === alm);
  abrir(`Conteo a mano · ${esc(alm)}`, `<p class="mut" style="margin:0">Lo que hay en cada código, en su unidad. Lo que quede vacío no cambia.</p>
    <form id="fLect" class="tabla"><table><thead><tr><th>Lugar</th><th>Código</th><th>Material</th><th class="n">PP</th><th class="n">Máx.</th><th>Stock</th></tr></thead><tbody>
    ${ms.map((m) => `<tr><td class="mono" style="font-size:11.5px">${esc(m.lugares.join(", "))}</td><td class="mono">${esc(m.cod)}</td><td style="font-size:12.5px">${esc(m.mat)}</td><td class="n">${nf(m.pp, 1)}</td><td class="n">${nf(m.max, 1)}</td>
      <td><input type="number" step="any" min="0" data-cod="${esc(m.cod)}" style="width:100px" aria-label="Stock de ${esc(m.cod)}" value="${S.stock[m.cod] ? S.stock[m.cod].u : ""}"> ${esc(m.um)}</td></tr>`).join("")}
    </tbody></table><div style="margin-top:10px"><button class="btn pri" type="submit">Guardar conteo</button></div></form>`);
  $("#fLect").addEventListener("submit", (ev) => {
    ev.preventDefault();
    $$("input[data-cod]", ev.target).forEach((i) => {
      if (i.value !== "" && (!S.stock[i.dataset.cod] || +i.value !== S.stock[i.dataset.cod].u)) S.stock[i.dataset.cod] = { u: parseFloat(i.value), src: "Conteo a mano", t: ahora() };
    });
    guardar(); cerrar(); pintar(); toast("Conteo guardado");
  });
}

// ---------------------------------------------------------------- formato de almacenamiento (dibujo)
// Cómo se guarda cada almacén (MP-FLAMA2035 › Almacenes, columnas C e I): pilas sobre tacos, rollos acostados en rack,
// brazos de cantilever, big bags, pallets en rack, estantería liviana, jaula de cilindros. El dibujo se llena con el
// stock contra el máximo y toma el color del estado.
const FORMATO = {
  CH: "Paquetes de hojas apilados sobre tacos", FL: "Rollos acostados, un código por pallet, en rack", CA: "Atados en los brazos del cantilever",
  PQ: "Big bags en el piso, de a 2", EM: "Pallets en rack selectivo", ID: "Cajas y rollos en estantería liviana", IM: "Pallets y cajas en rack selectivo",
  IR: "Tambores y bidones en rack", SO: "Pallets en rack selectivo", GA: "Cilindros y baterías en jaula", CC: "Contenedores de casquetes en rack",
  IC: "Pallets y cajas en rack", RV: "Matafuegos por modelo en la zona de reventa del PT",
};
function figFormato(pref, frac = 1, col = "var(--good)", w = 34, h = 28) {
  const L = "#59626d", V = "#fff", f = Math.max(0, Math.min(1, frac || 0));
  const k = (n) => f > 0 ? Math.max(1, Math.round(f * n)) : 0;
  const r = (x, y, ww, hh, on, rx = 0.6) => `<rect x="${x}" y="${y}" width="${ww}" height="${hh}" rx="${rx}" fill="${on ? col : V}" stroke="${L}" stroke-width=".8"/>`;
  const pallet = `<rect x="3" y="24.5" width="28" height="2" fill="${L}"/><rect x="4" y="26.5" width="3" height="1.3" fill="${L}"/><rect x="15.5" y="26.5" width="3" height="1.3" fill="${L}"/><rect x="27" y="26.5" width="3" height="1.3" fill="${L}"/>`;
  let g;
  switch (pref) {
    case "CH": { const n = k(6); g = [5, 15.5, 26].map((x) => `<rect x="${x}" y="24.5" width="3" height="3" fill="${L}"/>`).join("") + Array.from({ length: 6 }, (_, i) => r(3, 21.4 - i * 3.6, 28, 3, i < n, 0.3)).join(""); break; }
    case "FL": { const n = k(3); g = pallet + Array.from({ length: 3 }, (_, i) => r(4, 18 - i * 7, 26, 6, i < n, 3)).join(""); break; }
    case "CA": { const n = k(3); g = `<rect x="3" y="2" width="3" height="25" fill="${L}"/><rect x="1" y="26" width="9" height="1.6" fill="${L}"/>` +
      [6, 13.5, 21].map((y, i) => `<line x1="6" y1="${y + 3}" x2="32" y2="${y + 1.5}" stroke="${L}" stroke-width="1.2"/>` +
        [0, 1, 2].map((j) => `<circle cx="${12 + j * 6.5}" cy="${y + 0.2}" r="2.3" fill="${2 - i < n ? col : V}" stroke="${L}" stroke-width=".7"/>`).join("")).join(""); break; }
    case "PQ": { const hh = 19.5 * f; g = `<path d="M10 6.5 q2 -4.5 4 0 M20 6.5 q2 -4.5 4 0" fill="none" stroke="${L}" stroke-width=".9"/><rect x="6" y="6" width="22" height="20.5" rx="3" fill="${V}" stroke="${L}" stroke-width=".8"/>` +
      (hh > 0 ? `<rect x="6.5" y="${(26 - hh).toFixed(1)}" width="21" height="${hh.toFixed(1)}" rx="2.5" fill="${col}"/>` : ""); break; }
    case "GA": { const n = k(4); g = `<rect x="1.5" y="1.5" width="31" height="25.5" fill="none" stroke="#b9bec5" stroke-dasharray="1.5 1"/>` +
      Array.from({ length: 4 }, (_, i) => r(4.5 + i * 6.8, 7, 5.2, 19, i < n, 2.4) + `<rect x="${6 + i * 6.8}" y="4" width="2.2" height="3" fill="${L}"/>`).join(""); break; }
    case "ID": { const n = k(6); g = `<path d="M2 2 V27 M32 2 V27 M2 13.5 H32 M2 26.5 H32" stroke="${L}" stroke-width="1.1" fill="none"/>` +
      Array.from({ length: 6 }, (_, i) => r(4 + (i % 3) * 9.3, i < 3 ? 18.3 : 5.3, 8, 8, i < n, 0.5)).join(""); break; }
    case "RV": { const n = k(3); g = pallet + Array.from({ length: 3 }, (_, i) => `<rect x="${6 + i * 8.5}" y="9" width="6" height="15.5" rx="2.5" fill="${i < n ? col : V}" stroke="${L}" stroke-width=".8"/><rect x="${7.8 + i * 8.5}" y="6" width="2.4" height="3" fill="${L}"/>`).join(""); break; }
    case "CC": { const n = k(4); g = `<path d="M3 8 V26 H31 V8" fill="none" stroke="${L}" stroke-width="1.2"/>` +
      Array.from({ length: 4 }, (_, i) => `<path d="M7 ${24 - i * 4} Q17 ${16 - i * 4} 27 ${24 - i * 4} Z" fill="${i < n ? col : V}" stroke="${L}" stroke-width=".8"/>`).join(""); break; }
    case "IR": { const hh = 15.5 * f; g = pallet + [5, 18].map((x) => `<rect x="${x}" y="8.5" width="11" height="16" rx="1.2" fill="${V}" stroke="${L}" stroke-width=".8"/>` +
      (hh > 0 ? `<rect x="${x + 0.5}" y="${(24.5 - hh).toFixed(1)}" width="10" height="${hh.toFixed(1)}" fill="${col}"/>` : "") + `<line x1="${x}" y1="13.5" x2="${x + 11}" y2="13.5" stroke="${L}" stroke-width=".5"/><line x1="${x}" y1="19.5" x2="${x + 11}" y2="19.5" stroke="${L}" stroke-width=".5"/>`).join(""); break; }
    default: { const n = k(6); g = pallet + Array.from({ length: 6 }, (_, i) => r(4 + (i % 2) * 13.5, 18.4 - Math.floor(i / 2) * 7.2, 12.5, 6.4, i < n, 0.4)).join(""); }
  }
  return `<svg class="fmt" viewBox="0 0 34 28" width="${w}" height="${h}" aria-hidden="true">${g}</svg>`;
}
const fraccion = (m) => { const s = S.stock[m.cod]; return s ? s.u / (Math.max(m.max, m.pp) || 1) : 0; };

// ---------------------------------------------------------------- semáforo de cada almacén
// Rojo: bajo la seguridad · amarillo: en el punto de pedido o con el pedido en camino · verde: sobre el punto de pedido.
// Se cuenta en bultos, que es lo que se ve en el almacén (Stock_MP M y N: unidad de compra y su contenido). La regla de
// la tarjeta kanban de cada formato es criterio: sale de cómo se dispone cada almacén (Almacenes, columna I).
const REGLA = {
  CH: "Una pila por formato, con una marca en el poste a la altura del punto de pedido. Se toma el paquete de arriba: cuando la pila baja a la marca, la tarjeta de la pila va al tablero de pedidos.",
  FL: "Un código por pallet. El pallet que deja el stock en el punto de pedido lleva la tarjeta: cuando la pinza lo baja al piso del rack, la tarjeta va al tablero.",
  CA: "Un atado por brazo y una medida por nivel. El brazo del punto de pedido está pintado de amarillo: cuando queda a la vista, se pide.",
  PQ: "Big bags de a 2 por fecha de llegada; bolsas y cajas sobre pallet. El bulto del punto de pedido lleva la tarjeta colgada: cuando se empieza, va al tablero.",
  RACK: "Abajo el pallet o la caja en uso, arriba la reposición (Word de MP, sección 8). El bulto del punto de pedido lleva la tarjeta: cuando se baja o se abre, la tarjeta va al tablero.",
  ID: "Doble cajón: el segundo cajón (o rollo) es el punto de pedido y tiene su tarjeta. Cuando se empieza el segundo, se pide. Obleas y estampillas en el estante con candado.",
  GA: "Cilindros llenos con capuchón y baterías conectadas al manifold. Cuando quedan los llenos del punto de pedido, se pide; el vacío vuelve al proveedor con la tarjeta.",
  RV: "Lugares por modelo en la zona de reventa del PT. El lugar del punto de pedido lleva la tarjeta: cuando se despacha la última unidad de ese lugar, se pide.",
};
const reglaDe = (a) => REGLA[a.pref] || REGLA.RACK;
const LUZ = { crit: "rojo", pedir: "amarillo", ped: "amarillo", ok: "verde", sin: "apagado" };
const enBultos = (m, u) => u / (m.cont || 1);
function filaSemaforo(m) {
  const s = S.stock[m.cod], e = estado(m), ss = enBultos(m, m.ss), pp = Math.max(ss, enBultos(m, m.pp)), mx = Math.max(pp, enBultos(m, m.max)) || 1;
  const hay = s ? enBultos(m, s.u) : null, tope = Math.max(mx, hay || 0) * 1.04, pc = (x) => (x / tope * 100).toFixed(1);
  const ppN = Math.ceil(pp - 1e-9), cuando = ppN <= 1 ? "al abrir el último bulto" : `cuando quedan ${nf(ppN)} bultos`;
  const d = hay == null ? 0 : hay < 10 ? 1 : 0;
  return `<button class="sem-fila" data-mp="${esc(m.cod)}" title="${esc(m.bulto)}"><span class="luz ${LUZ[e]}"></span>
    <span class="sem-cod"><b class="mono">${esc(m.cod)}</b> ${esc(m.mat.replace(/\s*\(.*\)$/, ""))}</span>
    <span class="sem-txt">${hay != null ? `hay <b class="num">${nf(hay, d)}</b> bultos` : "sin conteo"} · pedir ${cuando}${e === "ped" ? ' · <span class="pill info">pedido en camino</span>' : ""}</span>
    <span class="sem-dias ${LUZ[e]}"><b class="num">${txtD(diasStock(m))}</b><small>de stock</small></span>
    <span class="sem-barra"><i class="r" style="width:${pc(ss)}%"></i><i class="a" style="left:${pc(ss)}%;width:${pc(pp - ss)}%"></i><i class="v" style="left:${pc(pp)}%;width:${pc(mx - pp)}%"></i>${hay != null ? `<u style="left:${pc(Math.min(hay, tope))}%"></u>` : ""}</span>
    <span class="sem-bulto mut">seguridad ${txtD(diasDe(m, m.ss))} · pedido ${txtD(diasDe(m, m.pp))} · máximo ${txtD(diasDe(m, m.max))} · ${esc(m.bulto)}</span></button>`;
}
const lampara = (cls, n, t) => `<span class="lamp ${cls} ${n ? "on" : ""}" title="${t}"><b class="num">${n}</b></span>`;
function tarjetaSemaforo(a) {
  const dd = (m) => { const d = diasStock(m); return d == null ? 1e9 : d; };
  const ms = D.mp.filter((m) => m.alm === a.alm).sort((x, y) => PEOR.indexOf(estado(x)) - PEOR.indexOf(estado(y)) || dd(x) - dd(y));
  const conD = ms.filter((m) => diasStock(m) != null), menor = conD.length ? conD.reduce((a, b) => (dd(a) <= dd(b) ? a : b)) : null;
  const c = (ks) => ms.filter((m) => ks.includes(estado(m))).length, verdes = ms.filter((m) => ["ok", "sin"].includes(estado(m)));
  const resto = ms.filter((m) => !verdes.includes(m));
  return `<section class="sem-card" id="sem-${a.pref}"><header>
      <div class="semaforo" aria-label="Semáforo">${lampara("rojo", c(["crit"]), "Bajo la seguridad")}${lampara("amarillo", c(["pedir", "ped"]), "En el punto de pedido o pedido")}${lampara("verde", c(["ok"]), "Sobre el punto de pedido")}</div>
      <div class="sem-tit"><h3>${esc(a.alm)}</h3><span class="fmt-nom">${figFormato(a.pref, 1, "var(--surface-3)", 40, 33)}<span><b>${esc(FORMATO[a.pref] || a.est)}</b><br><span class="mut">${esc(a.est)} · ${a.lug} lugares · ${ms.length} códigos</span></span></span>
        ${menor ? `<span class="sem-min">Menos días: <b class="mono">${esc(menor.cod)}</b> · <b class="dias">${txtD(dd(menor))}</b></span>` : ""}</div></header>
    <p class="regla"><b>Cómo funciona el kanban acá</b> <span class="pill idle">criterio</span><br>${esc(reglaDe(a))}</p>
    <div class="sem-lista">${resto.map(filaSemaforo).join("") || `<p class="mut" style="margin:4px 0">Todo en verde.</p>`}
      ${verdes.length ? `<details><summary>${verdes.length} en verde o sin conteo</summary>${verdes.map(filaSemaforo).join("")}</details>` : ""}</div></section>`;
}
function vSemaforo() {
  const c = (k) => D.mp.filter((m) => k.includes(estado(m))).length;
  return `${bandaEjemplo()}<div class="cab"><div><h1>Semáforo de los almacenes</h1>
    <p>Cada almacén con su semáforo, la regla de su tarjeta kanban y los días de stock de cada código. Se cuenta en bultos, como se ve en la estantería.</p></div>
    <div class="filtros"><button class="btn pri" data-a="planilla">Cargar planilla</button><a class="btn" href="#almacen">Ver los lugares</a></div></div>
    <div class="sem-ley">
      <div><span class="luz rojo"></span><b>Rojo · bajo la seguridad</b><span>Quedó menos que la seguridad (Stock_MP, col. L): menos días que los de seguridad. Pedido urgente y avisar a la línea. <b class="num">${c(["crit"])}</b> códigos.</span></div>
      <div><span class="luz amarillo"></span><b>Amarillo · pedir</b><span>Llegó al punto de pedido (seguridad + lo que se consume mientras llega, L + K): quedan los días de seguridad más los del plazo. La tarjeta va al tablero y sale el pedido. <b class="num">${c(["pedir", "ped"])}</b> códigos.</span></div>
      <div><span class="luz verde"></span><b>Verde · hay stock</b><span>Sobre el punto de pedido. No se hace nada hasta la próxima revisión. <b class="num">${c(["ok"])}</b> códigos.</span></div>
      <div class="sem-barra-ley"><span class="sem-barra"><i class="r" style="width:18%"></i><i class="a" style="left:18%;width:27%"></i><i class="v" style="left:45%;width:51%"></i><u style="left:60%"></u></span>
        <span class="mut">La barra va de 0 al máximo (col. S) en bultos: rojo hasta la seguridad, amarillo hasta el punto de pedido, verde hasta el máximo. La raya negra es lo que hay.
          <b>Días de stock</b> = stock ÷ consumo por día (Stock_MP, col. G; días hábiles): cuántos días de producción alcanza lo que hay.</span></div></div>
    <div class="saltos">${ALMS.map((a) => { const n = D.mp.filter((m) => m.alm === a.alm && ["crit", "pedir"].includes(estado(m))).length;
      return `<button data-salto="sem-${a.pref}">${esc(a.corto)}${n ? ` <b>${n}</b>` : ""}</button>`; }).join("")}</div>
    <div class="sem-grid">${ALMS.map(tarjetaSemaforo).join("")}</div>
    <details class="fuente"><summary>De dónde salen los números</summary>${esc(D.fuente.mp)}. Bultos = unidades ÷ contenido del bulto (Stock_MP, col. N).
      «Pedir cuando quedan N bultos» redondea el punto de pedido hacia arriba al bulto entero: se pide un poco antes, nunca después (criterio).
      Días de stock = unidades ÷ consumo por día (Stock_MP, col. G = consumo del año ÷ 240 días hábiles); la seguridad, el punto de pedido y el máximo también se muestran en días.
      La revisión periódica de cada proveedor (Word de MP, sección 9) sigue igual; el semáforo avisa si entre dos revisiones algo cruza el punto de pedido.</details>`;
}

// ---------------------------------------------------------------- planilla de conteo (Excel)
// La misma planilla que salida/Planilla_conteo_MP.xlsx: una hoja por almacén, se completa «Stock contado» y se carga
// acá. El Excel se lee y se arma en el navegador con SheetJS; también se acepta CSV o pegar desde Excel.
const XLSX_URL = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";
let xlsxProm = null;
const cargarXLSX = () => xlsxProm || (xlsxProm = new Promise((ok, mal) => {
  if (window.XLSX) { ok(window.XLSX); return; }
  const s = document.createElement("script");
  s.src = XLSX_URL; s.onload = () => ok(window.XLSX); s.onerror = () => { xlsxProm = null; mal(new Error("no se pudo cargar el lector de Excel")); };
  document.head.appendChild(s);
}));
const CAB_PLANILLA = ["Lugar", "Código", "Material", "UM", "Se compra en", "Seguridad", "Punto de pedido", "Máximo", "Consumo por día", "Stock contado", "Días de stock", "Estado", "Observaciones"];
async function bajarPlanilla(alm) {
  try {
    const X = await cargarXLSX(), wb = X.utils.book_new();
    (alm ? [ALM[alm]] : ALMS).forEach((a) => {
      const orden = Object.fromEntries((D.lugares[a.alm] || []).map((h, i) => [h.id, i]));
      const ms = D.mp.filter((m) => m.alm === a.alm).sort((x, y) => (orden[x.lugares[0]] ?? 999) - (orden[y.lugares[0]] ?? 999));
      const ws = X.utils.aoa_to_sheet([[`Conteo · ${a.alm}`], [`${a.est} · ${a.lug} lugares`], ["Fecha del conteo", "", "Contó", ""], [], CAB_PLANILLA,
        ...ms.map((m) => [m.lugares.join(", "), m.cod, m.mat, m.um, m.bulto, m.ss, m.pp, m.max, m.dia, "", "", "", ""])]);
      ws["!cols"] = [16, 14, 46, 7, 26, 11, 11, 11, 11, 13, 11, 16, 28].map((w) => ({ wch: w }));
      X.utils.book_append_sheet(wb, ws, a.corto);
    });
    X.writeFile(wb, `Planilla_conteo_MP${alm ? "_" + ALM[alm].pref : ""}_${hoy()}.xlsx`);
    toast("Planilla descargada");
  } catch (e) { toast("No se pudo armar la planilla: " + e.message); }
}
const norm = (s) => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").trim().toLowerCase();
function numero(v) {
  if (typeof v === "number") return v;
  let t = String(v ?? "").trim().replace(/\s/g, "");
  if (!t) return null;
  if (t.includes(",")) t = t.replace(/\./g, "").replace(",", ".");
  const x = parseFloat(t);
  return isNaN(x) ? null : x;
}
function isoDe(v) {
  if (v instanceof Date && !isNaN(v)) return v.toISOString().slice(0, 10);
  const m = /^(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})$/.exec(String(v ?? "").trim());
  if (m) return `${m[3].length === 2 ? "20" + m[3] : m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}`;
  return /^\d{4}-\d{2}-\d{2}/.test(String(v ?? "")) ? String(v).slice(0, 10) : null;
}
// Filas de una hoja: busca el encabezado con «Código» y «Stock contado» (o «Stock»); sin encabezado, toma el código de
// la primera columna y el último número de la fila. «Fecha del conteo» puede estar en cualquier fila de arriba.
function leerFilas(filas) {
  const out = [];
  let fechaC = null, cC = -1, cS = -1;
  for (const f of filas) {
    const n = f.map(norm), kF = n.findIndex((x) => x.startsWith("fecha del conteo"));
    if (kF >= 0 && fechaC == null) fechaC = f.slice(kF + 1).find((x) => x !== "" && x != null) ?? null;
    if (cC < 0) {
      const c = n.findIndex((x) => x === "codigo"), s = n.findIndex((x) => x.startsWith("stock contado") || x === "stock");
      if (c >= 0 && s >= 0) { cC = c; cS = s; }
      continue;
    }
    const cod = String(f[cC] ?? "").trim(), u = numero(f[cS]);
    if (cod && u != null) out.push({ cod, u });
  }
  if (cC < 0) filas.forEach((f) => {
    const cod = String(f[0] ?? "").trim(), nums = f.slice(1).map(numero).filter((x) => x != null);
    if (/^(MP|RV)-/i.test(cod) && nums.length) out.push({ cod, u: nums[nums.length - 1] });
  });
  return { filas: out, fecha: fechaC };
}
const partirLinea = (l) => l.split(/\t|;/).length > 1 ? l.split(/\t|;/) : l.split(",");
let LEIDO = null;
function dlgPlanilla() {
  LEIDO = null;
  abrir("Cargar planilla de conteo", `<p class="mut" style="margin:0 0 10px">La planilla del almacén (Excel o CSV) con las columnas «Código» y «Stock contado»; la app lee todas las hojas.
    También se puede pegar desde Excel: una fila por código, el código primero y el stock al final.</p>
    <div class="campos"><div class="campo ancho"><label for="plArch">Archivo</label><input id="plArch" type="file" accept=".xlsx,.xls,.csv,.txt"></div>
    <div class="campo ancho"><label for="plPeg">O pegar acá</label><textarea id="plPeg" rows="4" placeholder="MP-01&#9;14&#10;MP-62/M22&#9;35000"></textarea></div></div>
    <div class="filtros" style="margin-top:10px"><button class="btn" data-a="leerPegado">Leer lo pegado</button><button class="btn chico" data-a="bajarPlanilla">Descargar la planilla vacía</button></div>
    <div id="plVista"></div>`);
}
async function leerArchivo(file) {
  $("#plVista").innerHTML = `<p class="mut">Leyendo ${esc(file.name)}…</p>`;
  try {
    if (/\.(csv|txt)$/i.test(file.name)) { vistaPlanilla(leerFilas((await file.text()).split(/\r?\n/).map(partirLinea)), file.name); return; }
    const X = await cargarXLSX(), wb = X.read(await file.arrayBuffer(), { cellDates: true });
    const res = wb.SheetNames.map((n) => leerFilas(X.utils.sheet_to_json(wb.Sheets[n], { header: 1, raw: true, defval: "" })));
    vistaPlanilla({ filas: res.flatMap((r) => r.filas), fecha: res.map((r) => r.fecha).find((x) => x != null) }, file.name);
  } catch (e) { $("#plVista").innerHTML = `<div class="aviso">No se pudo leer: ${esc(e.message)}</div>`; }
}
function vistaPlanilla(res, origen) {
  const MPi = Object.fromEntries(D.mp.map((m) => [m.cod.toLowerCase(), m])), ok = [], mal = [];
  res.filas.forEach((r) => { const m = MPi[r.cod.toLowerCase()]; (m ? ok : mal).push({ ...r, m }); });
  const f = isoDe(res.fecha) || hoy();
  LEIDO = { ok, f, origen };
  const est = (m, u) => u <= m.ss ? ["crit", "bajo seguridad"] : u <= m.pp ? ["warn", "pedir"] : ["ok", "bien"];
  $("#plVista").innerHTML = ok.length ? `<p style="margin:12px 0 6px"><b>${ok.length} códigos</b> · conteo del ${fecha(f)}${mal.length ? ` · <span style="color:var(--critical)">${mal.length === 1 ? "1 código que no existe" : mal.length + " códigos que no existen"}: ${esc(mal.map((x) => x.cod).slice(0, 6).join(", "))}${mal.length > 6 ? "…" : ""}</span>` : ""}</p>
    <div class="tabla" style="max-height:300px;overflow:auto"><table><thead><tr><th>Código</th><th>Material</th><th class="n">Antes</th><th class="n">Contado</th><th class="n">Días</th><th>Queda</th></tr></thead><tbody>
    ${ok.map(({ m, u }) => { const [c, t] = est(m, u); return `<tr><td class="mono">${esc(m.cod)}</td><td style="font-size:12.5px">${esc(m.mat)}</td><td class="n">${S.stock[m.cod] ? nf(S.stock[m.cod].u, 1) : "—"}</td><td class="n">${nf(u, 1)} ${esc(m.um)}</td><td class="n">${txtD(diasDe(m, u))}</td><td><span class="pill ${c}">${t}</span></td></tr>`; }).join("")}
    </tbody></table></div><div style="margin-top:10px"><button class="btn pri" data-a="aplicarPlanilla">Aplicar el conteo</button></div>`
    : `<div class="aviso" style="margin-top:10px">No encontré filas con código y stock. ¿Tiene las columnas «Código» y «Stock contado»?</div>`;
}
function aplicarPlanilla() {
  if (!LEIDO) return;
  const { ok, f, origen } = LEIDO, t = f + " " + ahora().slice(11);
  ok.forEach(({ m, u }) => { S.stock[m.cod] = { u, src: `Planilla de conteo (${origen})`, t }; });
  LEIDO = null; guardar(); cerrar(); pintar(); toast(`Conteo aplicado: ${ok.length} códigos`);
}

// ---------------------------------------------------------------- PT zonificado
// Rack: 15 módulos × 3 niveles × 2 pallets (Almacen_PT B15:B16); andén 20 (B30); carros en el piso por modelo (B22:B25).
// Reventa 13 pallets y sustitutos 8 + 14 (Balanceo › Pulmones, sección 6); espera del pintor y pintados 29 + 29
// recipientes (PTPINTADO › Pintura B33:B34 = Balanceo › Pulmones filas 48 y 50).
const ZONAS = (() => {
  const z = [];
  const rack = [];
  for (let i = 1; i <= D.apt.modulos; i++) for (let n = 1; n <= 3; n++) for (const p of "AB") rack.push(`R${String(i).padStart(2, "0")}-${n}${p}`);
  z.push({ k: "rack", t: "Rack de PT", sub: `${D.apt.modulos} módulos × 3 niveles × 2 · nuevos en caja y cilindros`, slots: rack });
  z.push({ k: "carros", t: "Carros terminados en el piso", sub: "5 días de venta del mes pico", slots: Object.entries(D.carros).flatMap(([mod, n]) => Array.from({ length: n }, (_, j) => `C${mod.replace(" kg", "")}-${String(j + 1).padStart(2, "0")}`)) });
  z.push({ k: "anden", t: "Andén", sub: "lo que sale en el día · un sider y un camión chico", slots: Array.from({ length: D.apt.anden }, (_, j) => `AN-${String(j + 1).padStart(2, "0")}`) });
  z.push({ k: "rv", t: "Reventa", sub: "matafuegos revendidos, por modelo", slots: Array.from({ length: 13 }, (_, j) => `RV-${String(j + 1).padStart(2, "0")}`) });
  z.push({ k: "sus", t: "Sustitutos", sub: "8 propios + 14 comprados", slots: [...Array.from({ length: 8 }, (_, j) => `SP-${String(j + 1).padStart(2, "0")}`), ...Array.from({ length: 14 }, (_, j) => `SC-${String(j + 1).padStart(2, "0")}`)] });
  z.push({ k: "pint", t: "Rama de pintura (carros)", sub: "espera del pintor 29 · pintados 29", slots: [...Array.from({ length: 29 }, (_, j) => `EP-${String(j + 1).padStart(2, "0")}`), ...Array.from({ length: 29 }, (_, j) => `PI-${String(j + 1).padStart(2, "0")}`)] });
  return z;
})();
const TODOS_SLOTS = ZONAS.flatMap((z) => z.slots);
const COLOR_MES = (iso) => iso ? "a" + ((parseInt(iso.slice(5, 7), 10) - 1) % 4) : "";
const PRODS = [...D.pt.map((p) => p.prod), ...RV.map((r) => r.mat), "Sustituto propio", "Sustituto comprado", "Recipiente de carro (a pintar)", "Recipiente de carro (pintado)"];
const VEH = (prod) => /caja/.test(prod) ? "Camión chico · nuevos en caja" : /^Cilindro/.test(prod) ? "Sider · cilindros de manuales y de carro"
  : /^Carro/.test(prod) ? "Master · carros terminados a clientes" : null;
function proxima(veh) {
  const d = (D.desp.find((x) => x.veh === veh) || {}).dias || "";
  const map = { lunes: 1, martes: 2, "miércoles": 3, jueves: 4, viernes: 5 };
  let dd = /Lunes a viernes/.test(d) ? [1, 2, 3, 4, 5] : Object.entries(map).filter(([k]) => d.toLowerCase().includes(k)).map(([, v]) => v);
  if (!dd.length) return null;
  const x = new Date();
  for (let i = 0; i < 8; i++) { const y = new Date(x.getTime() + i * 864e5); if (dd.includes(y.getDay())) return { f: y.toISOString().slice(0, 10), d }; }
  return null;
}
function fifo() {
  const viejo = {};
  Object.entries(S.pallets).forEach(([slot, p]) => { if (!viejo[p.prod] || p.ffab < S.pallets[viejo[p.prod]].ffab) viejo[p.prod] = slot; });
  return new Set(Object.values(viejo));
}
function slotHtml(id, ff) {
  const p = S.pallets[id];
  if (!p) return `<button class="slot" data-slot="${id}" title="${id} libre" aria-label="${id} libre">${id.startsWith("R") && id.length === 6 && id[1] !== "V" ? id.split("-")[1] : id.replace("-", "·")}</button>`;
  const corto = ({ "Sustituto propio": "Sust. propio", "Sustituto comprado": "Sust. compr.", "Recipiente de carro (a pintar)": "A pintar", "Recipiente de carro (pintado)": "Pintado" })[p.prod] || p.prod.replace("Nuevo ", "N ").replace("Cilindro ", "Cil ").replace(" (en caja)", "").replace(" (manuales)", "").replace("Cilindro de carro", "CilC").replace("Carro ", "C ").replace(" terminado", "").replace("Matafuego ", "").replace(" (reventa)", "");
  return `<button class="slot lleno ${COLOR_MES(p.ffab)} ${ff.has(id) ? "fifo" : ""}" data-slot="${id}" title="${id} · ${esc(p.prod)} · ${nf(p.cant)} u · fabricado ${fecha(p.ffab)}">${esc(corto)}<br>${fecha(p.ffab).slice(0, 5)}</button>`;
}
function vPT() {
  const ff = fifo(), ocup = Object.keys(S.pallets).length;
  const enStock = (prod) => Object.values(S.pallets).filter((p) => p.prod === prod).reduce((a, p) => a + (+p.cant || 0), 0);
  const rack = ZONAS[0];
  const mods = Array.from({ length: D.apt.modulos }, (_, i) => {
    const r = `R${String(i + 1).padStart(2, "0")}`;
    return `<div class="modulo">${[3, 2, 1].map((n) => `<div class="nivel">${["A", "B"].map((p) => slotHtml(`${r}-${n}${p}`, ff)).join("")}</div>`).join("")}<em>${r}</em></div>`;
  }).join("");
  const zona = (z, c) => `<section class="zona ${c}"><h3><span>${z.t}</span><span class="mut num">${z.slots.filter((s) => S.pallets[s]).length}/${z.slots.length}</span></h3>
    <p class="mut" style="margin:-4px 0 8px;font-size:12px">${z.sub}</p><div class="piso">${z.slots.map((s) => slotHtml(s, ff)).join("")}</div></section>`;
  const desp = D.desp.slice(0, 3).map((v) => { const p = proxima(v.veh); return `<tr><td>${esc(v.veh)}</td><td>${esc(v.dias)}</td><td>${p ? fecha(p.f) : "—"}</td></tr>`; }).join("");
  return `${bandaEjemplo()}<div class="cab"><div><h1>Kanban de PT</h1>
    <p>Cada pallet en su lugar, con el color de su mes de fabricación. El recuadro negro sale primero.</p></div>
    <div class="leyenda"><span><i style="background:var(--a0)"></i>Ene · May · Sep</span><span><i style="background:var(--a1)"></i>Feb · Jun · Oct</span>
    <span><i style="background:var(--a2)"></i>Mar · Jul · Nov</span><span><i style="background:var(--a3)"></i>Abr · Ago · Dic</span><span><i style="outline:2px solid var(--fg);background:transparent"></i>sale primero</span></div></div>
    <div class="zonas">
      <section class="zona" style="grid-column:span 12"><h3><span>${rack.t}</span><span class="mut num">${rack.slots.filter((s) => S.pallets[s]).length}/${rack.slots.length}</span></h3>
        <p class="mut" style="margin:-4px 0 8px;font-size:12px">${rack.sub}. Los 10 kg en caja, en el nivel 1.</p>
        <div class="rack">${mods}</div></section>
      <div style="grid-column:span 7;display:grid;gap:12px">${zona(ZONAS[1])}${zona(ZONAS[2])}${zona(ZONAS[3])}${zona(ZONAS[4])}${zona(ZONAS[5])}</div>
      <div style="grid-column:span 5;display:grid;gap:12px;align-content:start">
        <section class="panel"><header><h2>Despacho: días fijos</h2></header><div class="cuerpo tabla"><table><thead><tr><th>Vehículo · qué lleva</th><th>Días</th><th>Próxima</th></tr></thead><tbody>${desp}</tbody></table>
</div></section>
        <section class="panel"><header><h2>Stock contra máximo</h2><span class="mut num">${ocup} lugares ocupados</span></header><div class="cuerpo tabla"><table>
          <thead><tr><th>Producto</th><th class="n">En PT</th><th class="n">Días</th><th class="n">Máximo</th></tr></thead><tbody>
          ${D.pt.map((p) => { const u = enStock(p.prod); return `<tr><td>${esc(p.prod)}</td><td class="n">${u ? nf(u) : "—"}</td><td class="n">${txtD(diasPT(u, p))}</td><td class="n">${nf(p.max)}</td></tr>`; }).join("")}
          </tbody></table></div></section>
      </div></div>`;
}
const libres = () => TODOS_SLOTS.filter((s) => !S.pallets[s]);
function dlgSlot(id) {
  const p = S.pallets[id];
  if (!p) {
    abrir(`Entrada al lugar ${id}`, `<p class="mut" style="margin:0">La entrada de producto propio se registra con el formulario de PT (FAB-11), que deja la liberación y las series. Desde acá también se puede ubicar un pallet ya liberado.</p>
      <div class="filtros"><a class="btn pri" href="#f-FAB-11" data-cerrar>Abrir FAB-11 · Producto terminado</a><a class="btn" href="#f-REV-01" data-cerrar>Recepción de revendidos (REV-01)</a></div>`);
    return;
  }
  const v = VEH(p.prod), pr = v ? proxima(v) : null;
  abrir(`${id} · ${esc(p.prod)}`, `<dl class="dl"><dt>Pallet</dt><dd class="mono">${esc(p.id)}</dd><dt>Cantidad</dt><dd class="num">${nf(p.cant)}</dd>
    <dt>Fabricado</dt><dd>${fecha(p.ffab)} · ${dias(p.ffab)} días en stock</dd><dt>Lote</dt><dd>${esc(p.lote || "—")}</dd>
    <dt>Series</dt><dd class="mono">${esc(p.series || "—")}</dd><dt>Liberó</dt><dd>${esc(p.quien || "—")} · ${esc(p.t || "")}</dd>
    <dt>Despacho</dt><dd>${v ? `${esc(v)} · próxima salida ${pr ? fecha(pr.f) : "—"}` : "según pedido"}</dd></dl>
    <form class="campos" id="fMover"><div class="campo"><label for="mvSlot">Mover a</label><select id="mvSlot">${libres().map((s) => `<option>${s}</option>`).join("")}</select></div>
      <div class="campo" style="align-self:end"><button class="btn" type="submit">Mover</button></div></form>
    <form class="campos" id="fDesp"><div class="campo"><label for="dRem">Remito</label><input id="dRem" required></div>
      <div class="campo"><label for="dN">Unidades</label><input id="dN" type="number" min="1" value="${p.cant}"></div>
      <div class="campo"><label for="dVeh">Vehículo</label><select id="dVeh">${D.desp.slice(0, 3).map((x) => `<option ${x.veh === v ? "selected" : ""}>${esc(x.veh)}</option>`).join("")}</select></div>
      <div class="campo" style="align-self:end"><button class="btn pri" type="submit">Despachar</button></div></form>`);
  $("#fMover").addEventListener("submit", (ev) => { ev.preventDefault(); const to = $("#mvSlot").value; S.pallets[to] = p; delete S.pallets[id]; guardar(); cerrar(); pintar(); toast(`${p.id} a ${to}`); });
  $("#fDesp").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const r = despachar(id, $("#dN").value, $("#dRem").value, $("#dVeh").value);
    cerrar(); pintar(); if (r) toast(`${r.id}: ${r.v.cant} u, series ${r.v.series}`);
  });
}

// ---------------------------------------------------------------- despacho: la salida con el n° de serie
// El n° de serie nace en el marcado del cuerpo (FAB-02), se repite en la etiqueta de serie (planos FL_MAT hoja 4: etiqueta
// GS1 de n° de serie en el costado), pasa a la etiqueta del pallet al liberar el lote (FAB-11) y sale escrito en el remito
// (registro DES). El QR de la etiqueta de serie es para el cliente; adentro de la planta se usa el número impreso.
const rangoSerie = (s) => { const m = /^\s*(\d+)\s*[–-]\s*(\d+)\s*$/.exec(String(s || "")); return m ? [+m[1], +m[2]] : null; };
const n6 = (x) => String(x).padStart(6, "0");
// Despacha n unidades de un pallet: si las series son un rango, salen las primeras y el resto queda en el pallet.
function despachar(slot, n, remito, veh) {
  const p = S.pallets[slot]; if (!p) return null;
  const r = rangoSerie(p.series);
  n = r ? Math.max(1, Math.min(+n || p.cant, p.cant)) : p.cant;
  const salen = r ? (n === 1 ? String(r[0]) : `${r[0]}-${r[0] + n - 1}`) : p.series;
  const reg = { id: "DES-" + String(sig("DES")).padStart(4, "0"), f: "DES", t: ahora(), res: "Despachado",
    v: { remito, veh, pallet: p.id, prod: p.prod, cant: n, series: salen, lote: p.lote, slot } };
  S.regs.push(reg);
  if (r && n < p.cant) { p.cant -= n; p.series = r[0] + n === r[1] ? String(r[1]) : `${r[0] + n}-${r[1]}`; }
  else { S.rev.forEach((x) => { if (x.slot === slot && x.estado === "En PT") { x.estado = "Despachado"; x.remito = remito; } }); delete S.pallets[slot]; }
  guardar();
  return reg;
}
function figCuerpo(serie) {
  return `<svg viewBox="0 0 150 96" class="fig-paso" role="img" aria-label="Marcado en el cuerpo"><defs><linearGradient id="gcu" x1="0" x2="1"><stop offset="0" stop-color="#8e1a14"/><stop offset=".5" stop-color="#c8312a"/><stop offset="1" stop-color="#7a1611"/></linearGradient></defs>
    <path d="M8 30 Q8 12 40 12 Q72 12 72 30 Z" fill="url(#gcu)"/><rect x="8" y="30" width="64" height="66" fill="url(#gcu)"/>
    <line x1="40" y1="31" x2="40" y2="96" stroke="#5a0d09" stroke-width="1.4" stroke-dasharray="4 2"/>
    <rect x="12" y="35" width="27" height="6" fill="none" stroke="#fff" stroke-width=".8"/>
    <path d="M39 38 L80 30 M39 41 L80 58" stroke="#1c2229" stroke-width=".6"/>
    <rect x="80" y="26" width="66" height="36" rx="3" fill="#a52520" stroke="#1c2229"/>
    <text x="84" y="40" font-size="7.6" fill="#ffe5e2" font-family="Consolas, monospace" textLength="50" lengthAdjust="spacingAndGlyphs">FLAMA S.A.</text>
    <text x="84" y="52" font-size="7.6" fill="#ffe5e2" font-family="Consolas, monospace" textLength="50" lengthAdjust="spacingAndGlyphs">N°${n6(serie)} 26</text>
    <rect x="136" y="44" width="7" height="9" fill="none" stroke="#ffe5e2" stroke-width=".7"/>
    <text x="113" y="74" font-size="6.5" fill="#4f5863" text-anchor="middle" font-family="Barlow, Arial">a 15 mm de la costura</text><text x="113" y="83" font-size="6.5" fill="#4f5863" text-anchor="middle" font-family="Barlow, Arial">y 20 mm del borde</text></svg>`;
}
function figEtqSerie(serie, modelo = "ABC 5 kg") {
  return `<svg viewBox="0 0 150 96" class="fig-paso" role="img" aria-label="Etiqueta de n° de serie"><rect x="0" y="8" width="150" height="88" rx="6" fill="#c8312a"/>
    <rect x="22" y="22" width="106" height="60" rx="3" fill="#fff" stroke="#59626d"/>
    <text x="30" y="38" font-size="8" font-family="Barlow, Arial" font-weight="700" fill="#1c2229">FLAMA S.A. · ${esc(modelo)}</text>
    <text x="30" y="57" font-size="13" font-family="Consolas, monospace" font-weight="700" fill="#1c2229" textLength="62" lengthAdjust="spacingAndGlyphs">N° ${n6(serie)}</text>
    <text x="30" y="72" font-size="7" font-family="Barlow, Arial" fill="#4f5863">Fab. 10/26 · lote OP</text>
    <g fill="#1c2229">${[0, 1, 2, 3, 4].map((i) => [0, 1, 2, 3, 4].map((j) => ((i * 3 + j * 5) % 3 ? `<rect x="${103 + j * 4}" y="${46 + i * 4}" width="3.6" height="3.6"/>` : "")).join("")).join("")}</g>
    <text x="113" y="74" font-size="5" text-anchor="middle" fill="#858d97" font-family="Barlow, Arial">QR cliente</text></svg>`;
}
function figEtqPallet(p, slot) {
  const r = rangoSerie(p.series);
  return `<svg viewBox="0 0 150 96" class="fig-paso" role="img" aria-label="Etiqueta de pallet"><rect x="4" y="4" width="142" height="88" rx="3" fill="#fff" stroke="#1c2229" stroke-width="1.4"/>
    <rect x="4" y="4" width="142" height="16" fill="#1c2229"/><text x="10" y="15.5" font-size="8.5" fill="#fff" font-family="Barlow, Arial" font-weight="700">PALLET ${esc(p.id)}</text>
    <text x="140" y="15.5" font-size="8" fill="#fff" text-anchor="end" font-family="Barlow, Arial">lugar ${esc(slot)}</text>
    <g font-family="Barlow, Arial" font-size="7.5" fill="#1c2229"><text x="10" y="33">${esc(p.prod)}</text><text x="10" y="45">${nf(p.cant)} u · lote ${esc(p.lote || "—")}</text>
    <text x="10" y="59" font-family="Consolas, monospace" font-size="9" font-weight="700">Series ${r ? `${n6(r[0])}–${n6(r[1])}` : esc(String(p.series).slice(0, 18))}</text>
    <text x="10" y="72">Fabricado ${fecha(p.ffab)} · liberó ${esc(p.quien || "Calidad")}</text><text x="10" y="84" fill="#858d97">FAB-11 ${esc(p.reg || "")}</text></g></svg>`;
}
function figRemito(r) {
  return `<svg viewBox="0 0 150 96" class="fig-paso" role="img" aria-label="Remito"><rect x="14" y="4" width="122" height="88" fill="#fff" stroke="#59626d"/>
    <g font-family="Barlow, Arial" fill="#1c2229"><text x="22" y="18" font-size="9" font-weight="700">REMITO ${esc(r.remito)}</text><text x="22" y="30" font-size="7" fill="#4f5863">${esc(r.veh)}</text>
    <line x1="22" y1="36" x2="128" y2="36" stroke="#dde1e6"/><text x="22" y="48" font-size="7.5">${nf(r.cant)} × ${esc(r.prod)}</text>
    <text x="22" y="62" font-size="8.5" font-family="Consolas, monospace" font-weight="700">Series ${esc(r.series)}</text><text x="22" y="76" font-size="7" fill="#4f5863">Lote ${esc(r.lote || "—")}</text></g></svg>`;
}
const diasPT = (u, p) => (p.dia > 0 ? u / p.dia : null);
const DESP_LUZ = (u, p) => u <= p.ss ? ["rojo", "bajo la seguridad: producir"] : u <= p.ss + p.porp ? ["amarillo", "programar el próximo lote"] : ["verde", u >= p.max ? "en el máximo" : "hay stock"];
function vDespacho() {
  const ff = fifo(), conRango = (p) => (rangoSerie(p.series) ? 0 : 1);
  const pals = Object.entries(S.pallets).sort((a, b) => conRango(a[1]) - conRango(b[1]) || (a[1].ffab || "").localeCompare(b[1].ffab || ""));
  const ej = pals.find(([, p]) => rangoSerie(p.series) && /^Nuevo/.test(p.prod)) || pals[0];
  const des = S.regs.filter((r) => r.f === "DES").slice().reverse();
  const ultimo = des[0] ? des[0].v : { remito: "R-0001-00000", veh: "Camión chico", cant: 48, prod: "Nuevo 5 kg (en caja)", series: "5480-5527", lote: "OP 26-10-08" };
  const serie = ej ? (rangoSerie(ej[1].series) || [5480])[0] : 5480;
  const paso = (n, t, fig, txt, donde) => `<article class="paso-d"><span class="n">${n}</span>${fig}<h3>${t}</h3><p>${txt}</p><span class="donde">${donde}</span></article>`;
  const enStock = (prod) => Object.values(S.pallets).filter((x) => x.prod === prod).reduce((a, x) => a + (+x.cant || 0), 0);
  const anden = ZONAS.find((z) => z.k === "anden").slots.filter((s) => S.pallets[s]);
  return `${bandaEjemplo()}<div class="cab"><div><h1>Salida y despacho</h1>
    <p>Cómo sale cada matafuego con su número: del cuerpo a la etiqueta de serie, al pallet y al remito. Con ese número se vuelve atrás hasta la colada de la chapa.</p></div>
    <div class="filtros"><a class="btn" href="#pt">Kanban de PT</a><a class="btn" href="#marcado">Identificación sin QR</a></div></div>
    <section class="panel" style="margin-bottom:18px"><header><h2>El número de punta a punta</h2><span class="mut" style="font-size:12.5px">Ejemplo con los datos cargados</span></header>
      <div class="cuerpo pasos-d">
        ${paso(1, "Marcado en el cuerpo", figCuerpo(serie), `La Pannier graba «FLAMA S.A. N° serie año» arriba, a la izquierda de la costura, en el puesto 6. Es el número que no se borra.`, "FAB-02 · rango de series del lote")}
        ${paso(2, "Etiqueta de serie", figEtqSerie(serie, ej ? ej[1].prod.replace(/^(Nuevo|Cilindro) /, "ABC ").replace(/ \(.*\)$/, "").replace(/^Carro (\d+) kg terminado$/, "Carro ABC $1 kg") : "ABC 5 kg"), `En el etiquetado se pega en el costado la etiqueta con el mismo número impreso. El QR es para el cliente; acá se lee el número.`, "FAB-11 · «etiqueta igual al marcado»")}
        ${ej ? paso(3, "Etiqueta del pallet", figEtqPallet(ej[1], ej[0]), `Calidad libera el lote y arma el pallet: producto, cantidad, lote, series desde–hasta, fecha y lugar en el PT.`, "FAB-11 · lugar en el kanban de PT") : ""}
        ${paso(4, "Remito", figRemito(ultimo), `El día del vehículo el pallet pasa al andén y sale con remito. Las series que salen quedan en el registro; si sale parte del pallet, el resto sigue con sus series.`, "Despacho · registro DES")}
      </div>
      <p class="cuerpo mut" style="font-size:13px;margin:0">Ante un reclamo, el cliente da el número del cuerpo o de la etiqueta; en <a href="#traza">Trazabilidad</a> aparece el remito, el lote, cada ficha (soldaduras, PH, pintado, pérdidas) y la colada de la chapa.</p></section>
    <div class="grid">
      <section class="panel c7"><header><h2>Despachar</h2><span class="mut" style="font-size:12.5px">Primero sale el más viejo (marcado con borde en el PT)</span></header>
        <form class="cuerpo campos" id="fDespacho">
          <div class="campo ancho"><label for="dpPal">Pallet</label><select id="dpPal">${pals.map(([s, p]) => `<option value="${s}">${ff.has(s) ? "★ " : ""}${s} · ${esc(p.prod)} · ${nf(p.cant)} u · series ${esc(String(p.series).slice(0, 24))} · ${fecha(p.ffab)}</option>`).join("")}</select></div>
          <div class="campo"><label for="dpN">Unidades que salen</label><input id="dpN" type="number" min="1" step="1"></div>
          <div class="campo"><label for="dpRem">Remito</label><input id="dpRem" required placeholder="R-0001-00000"></div>
          <div class="campo"><label for="dpVeh">Vehículo</label><select id="dpVeh">${D.desp.slice(0, 3).map((x) => `<option>${esc(x.veh)}</option>`).join("")}</select></div>
          <div class="campo ancho"><div class="aviso" id="dpVista">Elegí un pallet.</div></div>
          <div class="campo"><button class="btn pri" type="submit">Registrar el despacho</button></div></form></section>
      <section class="panel c5"><header><h2>Semáforo del PT</h2><span class="pill idle">criterio</span></header><div class="cuerpo">
        <p class="mut" style="font-size:12.5px;margin:0 0 6px">Días = unidades ÷ venta por día (Stock_PT, col. F). Rojo: bajo la seguridad (Stock_PT, col. H = 5 días de venta), hay que producir · amarillo: a menos de un pallet de la seguridad, programar el lote · verde: hay stock.</p>
        ${D.pt.map((p) => { const u = enStock(p.prod), [l, t] = DESP_LUZ(u, p); return `<div class="sem-pt"><span class="luz ${l}"></span><span>${esc(p.prod)}<br><span class="mut">${t}</span></span><span class="num der">${nf(u)} u · <b class="dias">${txtD(diasPT(u, p))}</b><br><span class="mut">seg. ${nf(p.ss)} (${txtD(diasPT(p.ss, p))}) · máx. ${nf(p.max)} (${txtD(diasPT(p.max, p))})</span></span></div>`; }).join("")}</div></section>
      <section class="panel c5"><header><h2>Andén y próximas salidas</h2></header><div class="cuerpo tabla"><table><tbody>
        ${D.desp.slice(0, 3).map((v) => { const p = proxima(v.veh); return `<tr><td><b>${esc(v.veh)}</b><br><span class="mut">${esc(v.dias)}</span></td><td class="n">${p ? fecha(p.f) : "—"}</td></tr>`; }).join("")}</tbody></table>
        <p style="margin:10px 0 4px"><b>En el andén:</b> ${anden.length ? anden.map((s) => `${s} · ${esc(S.pallets[s].prod)} (${nf(S.pallets[s].cant)} u)`).join(" — ") : "vacío"}</p></div></section>
      <section class="panel c7"><header><h2>Últimos despachos</h2><span class="mut num">${des.length}</span></header><div class="cuerpo tabla">
        ${des.length ? `<table><thead><tr><th>Cuándo</th><th>Remito</th><th>Vehículo</th><th>Producto</th><th class="n">u</th><th>Series</th></tr></thead><tbody>
        ${des.slice(0, 12).map((r) => `<tr><td class="num">${esc(r.t.slice(5))}</td><td class="mono">${esc(r.v.remito)}</td><td>${esc(String(r.v.veh).split(" · ")[0])}</td><td>${esc(r.v.prod)}</td><td class="n">${nf(r.v.cant)}</td>
          <td><a href="#" data-q="${esc((rangoSerie(r.v.series) || [r.v.series])[0])}" class="mono">${esc(String(r.v.series).slice(0, 22))}</a></td></tr>`).join("")}</tbody></table>` : `<div class="vacio">Sin despachos todavía.</div>`}</div></section>
      <section class="panel c12"><header><h2>Qué número sale en cada caso</h2></header><div class="cuerpo tabla"><table>
        <thead><tr><th>Qué sale</th><th>Número que se sigue</th><th>Dónde está</th><th>Etiquetas que lleva</th><th>Registro</th></tr></thead><tbody>
        <tr><td>Matafuego o cilindro propio</td><td>N° de serie + año</td><td>Marcado en el cuerpo y etiqueta de serie</td><td>Etiqueta del producto, etiqueta de serie, estampilla IRAM, oblea, faja y precinto</td><td>FAB-11 → despacho</td></tr>
        <tr><td>Carro terminado</td><td>N° de serie + año + presión de ensayo</td><td>Marcado en el cuerpo y etiqueta de serie</td><td>Ídem, en el carro</td><td>FAB-11 → despacho (Master)</td></tr>
        <tr><td>Equipo de recarga</td><td>Orden de servicio + n° grabado por su fabricante</td><td>Recipiente del cliente</td><td>Marbete del año, oblea, etiqueta de servicio y precinto (IRAM 3517-2 9.4.13, 9.6, 9.4.14)</td><td>REC-04</td></tr>
        <tr><td>Revendido</td><td>N° de serie del fabricante</td><td>Su etiqueta o grabado</td><td>Las de su fabricante; FLAMA no reetiqueta</td><td>REV-01 → despacho</td></tr></tbody></table></div></section>
    </div>`;
}
function armarDespacho() {
  const f = $("#fDespacho"); if (!f) return;
  const ver = () => {
    const s = $("#dpPal").value, p = S.pallets[s]; if (!p) { $("#dpVista").textContent = "No hay pallets en el PT."; return; }
    const r = rangoSerie(p.series), n = Math.max(1, Math.min(+$("#dpN").value || p.cant, p.cant));
    if (!r && n < p.cant) $("#dpN").value = p.cant;
    $("#dpVista").innerHTML = r ? `Salen <b class="mono">${n === 1 ? r[0] : `${r[0]}–${r[0] + n - 1}`}</b> (${n} u)${n < p.cant ? ` · quedan <b class="mono">${r[0] + n}–${r[1]}</b> en ${s}` : ` · el lugar ${s} queda libre`}.`
      : `Las series de este pallet son una lista: sale el pallet entero (${nf(p.cant)} u).`;
  };
  $("#dpPal").onchange = () => { const p = S.pallets[$("#dpPal").value]; $("#dpN").value = p ? p.cant : "";
    const v = p && VEH(p.prod); if (v) $("#dpVeh").value = v; ver(); };
  $("#dpN").oninput = ver;
  $("#dpPal").onchange();
  f.onsubmit = (ev) => { ev.preventDefault(); const r = despachar($("#dpPal").value, $("#dpN").value, $("#dpRem").value, $("#dpVeh").value);
    if (r) { pintar(); toast(`${r.id}: ${r.v.cant} u, series ${r.v.series}`); } };
}

// ---------------------------------------------------------------- formularios
// Campos: k, l (rótulo), tipo (txt num sel fecha si area lect), ok(v, vals) → true/false/null, ayuda.
const f = {
  fecha: () => ({ k: "fecha", l: "Fecha", tipo: "fecha", req: true }),
  oper: (l = "Operador") => ({ k: "oper", l, tipo: "txt", req: true }),
  modelo: (car = null) => ({ k: "modelo", l: "Modelo", tipo: "sel", req: true, opts: MODELOS.filter((m) => car === null || m.car === car).map((m) => m.m) }),
  lote: () => ({ k: "lote", l: "Lote (orden de producción)", tipo: "txt", req: true }),
  series: () => [{ k: "sd", l: "N° de serie desde", tipo: "num", req: true, ayuda: "El del marcado Pannier" }, { k: "sh", l: "N° de serie hasta", tipo: "num", req: true, ok: (v, x) => v === null ? null : v >= x.sd }],
  si: (k, l, ayuda) => ({ k, l, tipo: "si", ayuda, ok: (v) => !!v }),
  txt: (k, l, ayuda, req = false) => ({ k, l, tipo: "txt", ayuda, req }),
  num: (k, l, o = {}) => Object.assign({ k, l, tipo: "num" }, o),
  sel: (k, l, opts, o = {}) => Object.assign({ k, l, tipo: "sel", opts }, o),
  rech: () => ({ k: "rech", l: "Series rechazadas (separadas por coma)", tipo: "txt", ayuda: "Vacío si no hubo" }),
  obs: () => ({ k: "obs", l: "Observaciones", tipo: "area" }),
};
const nominal = (x) => (MOD(x.modelo) || {}).t;
const pe = (x) => (MOD(x.modelo) || {}).pe;
const espMP = (m) => { const r = /(LAF|LAC)\s([\d,]+)\s×/.exec(m ? m.mat : ""); return r ? parseFloat(r[2].replace(",", ".")) : null; };
const soldadura = (id, nombre, puestos, extra = []) => ({
  id, nombre, linea: "fab", puestos, normas: ["ISO 9606-1 (soldador)", "ISO 15614-1 (WPS)", "ISO 5817 nivel C", "DOC-02 R2"],
  campos: [f.fecha(), f.oper("Soldador"), f.txt("calif", "Calificación del soldador (ISO 9606-1)", "N° y vencimiento", true),
    f.txt("wps", "WPS", "Procedimiento calificado ISO 15614-1", true), f.modelo(), f.lote(), ...f.series(), ...extra,
    f.txt("alambre", "Lote de alambre (MP-23 / MP-24)", "", true), f.txt("gas", "Lote de gas (MP-25 / MP-26)", "", true),
    f.num("amp", "Corriente (A)"), f.num("volt", "Tensión (V)"),
    f.si("visual", "Inspección visual conforme", "ISO 5817 nivel C: sin fisuras, poros abiertos ni falta de penetración visible"), f.rech(), f.obs()],
});
const FORMS = [
  { id: "FAB-01", nombre: "Recepción de materia prima", linea: "fab", puestos: [["man", "1"], ["car", "1"]],
    normas: ["DOC-02 R1 (chapa)", "DOC-02 L4 (polvo)", "DOC-02 L5 (manómetros y válvulas)", "Word MP 4.1 (FIFO por colada)"],
    campos: [f.fecha(), f.oper("Recibió"), { k: "mp", l: "Materia prima", tipo: "mp", req: true, filtro: (m) => !m.cod.startsWith("RV-") },
      f.num("cant", "Cantidad recibida", { req: true, ayuda: "En la unidad del código" }), f.txt("remito", "Remito", "", true),
      f.txt("colada", "Lote o colada", "Chapa y fleje: colada del certificado", true), f.si("cert", "Certificado de calidad del lote recibido"),
      f.num("esp", "Espesor medido (mm)", { ayuda: "Chapa y fleje: ≥ espesor nominal (DOC-02 R1)", ok: (v, x) => v === null ? null : v >= (espMP(MP[x.mp]) || 0) }),
      f.si("bulto", "Bulto sano e identificado con su código"), f.obs()],
    efecto: (r) => { if (r.res === "Conforme") { const c = r.v.mp; S.stock[c] = { u: (S.stock[c] ? S.stock[c].u : 0) + (+r.v.cant || 0), src: "Recepción " + r.id, t: r.t }; delete S.pedidos[c]; } } },
  { id: "FAB-02", nombre: "Marcado del cuerpo (Pannier)", linea: "fab", puestos: [["man", "6"]],
    normas: ["IRAM 3523 5.1", "IRAM 3550 5.1", "Res. 349/07 anexo IV (cuño DPS)", "Planos FL_MAT hoja 4 R7 · FL_REC hoja 3 R3"],
    campos: [f.fecha(), f.oper(), f.modelo(), f.lote(), ...f.series(), f.num("anio", "Año (2 dígitos)", { req: true, ok: (v) => v === null ? null : v >= 0 && v <= 99 }),
      f.txt("colada", "Colada de la chapa", "La del paquete que se está usando: une la serie con el certificado", true),
      f.si("ubic", "Final del marcado a 15 mm de la costura y a 20 mm del borde superior de la chapa", "Texto horizontal que crece hacia la izquierda"),
      f.si("dps", "Cuño DPS 15 × 7 al final del texto"), f.si("pe", "Carros: presión de ensayo en el texto", "En manuales marcar igual"),
      f.si("legible", "Texto legible y sin deformar la chapa"), f.obs()] },
  soldadura("FAB-03", "Soldadura longitudinal", [["man", "9"], ["man", "10"], ["car", "5"]],
    [f.sel("proc", "Proceso", ["MAG 135 (2,5 a 10 kg y carros)", "TIG 141 (1 kg)"], { req: true, ok: (v, x) => !v || !x.modelo ? null : (x.modelo === "ABC 1 kg") === v.startsWith("TIG") })]),
  soldadura("FAB-04", "Soldadura de cúpula", [["man", "7"], ["car", "6"]], [f.sel("pieza", "Unión", ["Cuello a la cúpula (manuales)", "Cupla en la cúpula (carros)"], { req: true })]),
  soldadura("FAB-05", "Soldadura circunferencial", [["man", "13"], ["car", "7"]]),
  { id: "FAB-06", nombre: "Control de espesor", linea: "fab", puestos: [["man", "14"]],
    normas: ["DOC-02 R1 (espesor ≥ nominal)", "Muestra del 2 % (Balanceo › Carga, puesto 14)"],
    campos: [f.fecha(), f.oper(), f.sel("instr", "Instrumento", INSTR.esp, { req: true }), f.si("calib", "Calibración del instrumento vigente"), f.modelo(), f.lote(),
      f.num("serie", "N° de serie medido", { req: true }),
      { k: "lect", l: "Lecturas (mm): cuerpo arriba, medio, abajo y cúpula", tipo: "lect", n: 4, req: true, ok: (v, x) => !v || !v.length || !nominal(x) ? null : Math.min(...v) >= nominal(x), ayuda: "Ninguna por debajo del espesor nominal del modelo" }, f.obs()] },
  { id: "FAB-07", nombre: "Prueba hidráulica", linea: "fab", puestos: [["man", "15"], ["car", "9"]],
    normas: ["DOC-02 R3", "IRAM 3517-2:2020 9.7.5.2 (1 min)", "Res. 349/07 art. 20 (contraste cada 15 días)", "DOC-02 L1 y L2 (lote)"],
    campos: [f.fecha(), f.oper(), f.sel("banco", "Banco", INSTR.ph, { req: true }),
      f.num("contraste", "Días desde el último contraste del manómetro", { req: true, ok: (v) => v === null ? null : v <= 15 }), f.modelo(), f.lote(), ...f.series(),
      f.num("p", "Presión aplicada (MPa)", { req: true, ayuda: "3,5 manuales · 4,0 carros", ok: (v, x) => v === null || !pe(x) ? null : v >= pe(x) }),
      f.num("seg", "Tiempo a presión (s)", { req: true, ok: (v) => v === null ? null : v >= 60 }),
      f.si("sin", "Sin caída de presión, pérdidas ni deformación permanente visible"), f.rech(),
      f.num("et", "Lote · expansión total (cm³)", { ayuda: "L2: 10 % del lote" }), f.num("ep", "Lote · expansión permanente (cm³)", { ok: (v, x) => v === null || !x.et ? null : v <= 0.1 * x.et, ayuda: "≤ 10 % de la total" }),
      f.num("rot", "Lote · presión de rotura (MPa)", { ayuda: "L1: 1 por lote; sin fisuras hasta 2 × la de PH", ok: (v, x) => v === null || !pe(x) ? null : v >= 2 * pe(x) }), f.obs()] },
  { id: "FAB-08", nombre: "Detección y corrección de defectos", linea: "fab", puestos: [["man", "18"], ["man", "19"]],
    normas: ["ISO 5817 nivel C", "DOC-02 R2", "Criterio FLAMA: la corrección con soldadura repite la PH"],
    campos: [f.fecha(), f.oper(), f.modelo(), f.lote(), ...f.series(),
      f.sel("def", "Defecto principal", ["Sin defectos", "Poro", "Socavación", "Salpicadura", "Falta de fusión visible", "Abolladura", "Golpe o rayado", "Otro"], { req: true }),
      f.txt("defser", "Series con defecto y tipo", "Ej.: 001234 poro; 001240 golpe"),
      f.sel("acc", "Acción", ["Ninguna", "Corrección mecánica", "Corrección con soldadura", "Descarte"], { req: true }),
      f.sel("reph", "Vuelve a PH", ["No corresponde", "Sí, registrada en FAB-07"], { req: true, ok: (v, x) => x.acc === "Corrección con soldadura" ? v.startsWith("Sí") : null }), f.obs()] },
  { id: "FAB-09", nombre: "Pintado", linea: "fab", puestos: [["man", "20"], ["car", "12"]],
    normas: ["DOC-01 sección 2 (Sa 2½, 4 h, HR ≤ 85 %)", "DOC-01 sección 4", "ISO 2808 (60 a 100 µm)", "ISO 2409 (clase 0 ó 1)", "ASTM D5402 (MEK)"],
    campos: [f.fecha(), f.oper(), f.modelo(), f.lote(), f.txt("polvo", "Lote de pintura en polvo (MP-31)", "", true),
      f.si("sa", "Granallado Sa 2½ verificado con el comparador"), f.num("hs", "Horas desde el granallado", { ok: (v) => v === null ? null : v <= 4 }),
      f.num("hr", "Humedad relativa (%)", { ok: (v) => v === null ? null : v <= 85 }), f.sel("instr", "Medidor de película", INSTR.pel),
      { k: "pel", l: "Espesor de película: 5 lecturas (µm)", tipo: "lect", n: 5, req: true, ayuda: "Promedio 60 a 100 µm; ninguna < 80 % de 60",
        ok: (v) => !v || !v.length ? null : (v.reduce((a, b) => a + b, 0) / v.length >= 60 && v.reduce((a, b) => a + b, 0) / v.length <= 100 && Math.min(...v) >= 48) },
      f.sel("adh", "Adherencia (clase ISO 2409)", ["0", "1", "2", "3", "4", "5"], { req: true, ok: (v) => v === "" ? null : +v <= 1 }),
      f.si("mek", "Frote con MEK sin ablandamiento"), f.si("color", "Rojo 03-1-050, brillante, sin defectos"),
      f.sel("pintor", "Dónde se pintó", ["En planta (manuales)", "Pintor externo (carros, recepción de pintados)"], { req: true }), f.obs()] },
  { id: "FAB-10", nombre: "Ensayo de pérdidas", linea: "fab", puestos: [["man", "24"], ["car", "14-17"]],
    normas: ["IRAM 3517-2:2020 9.4.10", "DOC-02 R7 y R8"],
    campos: [f.fecha(), f.oper(), f.modelo(), f.lote(), ...f.series(), f.sel("met", "Método", ["Inmersión", "Detector"], { req: true }),
      f.si("verde", "Manómetro en zona verde al presurizar (1,4 MPa a 20 °C)"), f.si("burb", "Sin pérdidas de propelente ni de agente"),
      f.si("h24", "Manómetro en zona verde a las 24 h", "Criterio FLAMA"), f.rech(), f.obs()] },
  { id: "FAB-11", nombre: "Producto terminado", linea: "fab", puestos: [["man", "26"], ["car", "16"]],
    normas: ["DOC-02 R9 (pesada final y marcado)", "PTPINTADO › Pallets (unidades por pallet)"],
    campos: [f.fecha(), f.oper("Liberó"), f.sel("prod", "Producto", D.pt.map((p) => p.prod).concat(["Sustituto propio", "Recipiente de carro (a pintar)", "Recipiente de carro (pintado)"]), { req: true }),
      f.num("cant", "Unidades", { req: true }), f.lote(), f.txt("series", "Series (desde–hasta o lista)", "Las del marcado Pannier", true),
      { k: "ffab", l: "Fecha de fabricación", tipo: "fecha", req: true }, { k: "slot", l: "Lugar en el PT", tipo: "slot", req: true },
      f.si("pesada", "Pesada final dentro de la tolerancia"), f.si("ident", "Etiqueta, precinto y seguro colocados"),
      f.si("etqser", "Etiqueta de n° de serie con el mismo número que el marcado", "Se controla la primera y la última del lote"),
      f.txt("estamp", "Estampillas IRAM (desde–hasta)", "Una por unidad (IRAM, Anexo R)"), f.obs()],
    efecto: (r) => { if (r.res === "Conforme") S.pallets[r.v.slot] = { id: "PAL-" + String(sig("PAL")).padStart(4, "0"), prod: r.v.prod, cant: r.v.cant, lote: r.v.lote, series: r.v.series, ffab: r.v.ffab, quien: r.v.oper, t: r.t, reg: r.id }; } },
  { id: "REC-01", nombre: "Recepción de MP de recargas", linea: "rec", puestos: [],
    normas: ["IRAM 3517-2:2020 9.9 y tabla 6 (agentes certificados)", "9.9.1.6 (no mezclar ABC con BC)", "9.4.9 (gas impulsor)"],
    campos: [f.fecha(), f.oper("Recibió"), { k: "mp", l: "Materia prima", tipo: "mp", req: true, filtro: (m) => /ecargas/.test(m.linea || "") },
      f.num("cant", "Cantidad recibida", { req: true }), f.txt("remito", "Remito", "", true), f.txt("colada", "Lote del agente", "", true),
      f.si("cert", "Certificado del agente con su norma IRAM"), f.si("rotulo", "Rótulo del tipo de agente correcto (sin mezclar ABC y BC)"), f.obs()],
    efecto: (r) => { if (r.res === "Conforme") { const c = r.v.mp; S.stock[c] = { u: (S.stock[c] ? S.stock[c].u : 0) + (+r.v.cant || 0), src: "Recepción " + r.id, t: r.t }; delete S.pedidos[c]; } } },
  { id: "REC-02", nombre: "Inspección interior", linea: "rec", puestos: [["rec", "9"], ["rec", "13"]],
    normas: ["IRAM 3517-2:2020 9.8.2 (secado y cámara)", "9.7.1.2 (daño menor: PH)", "9.7.1.3 (inutilizar)", "9.12 y anexo G (acta)"],
    campos: [f.fecha(), f.oper(), f.txt("os", "Orden de servicio", "", true), f.txt("serie", "N° de serie del recipiente", "El grabado por su fabricante", true),
      f.txt("fab", "Fabricante"), f.sel("agente", "Agente", ["ABC", "BC", "Clase D", "CO₂", "Agua / AFFF", "Sales K", "HCFC"], { req: true }),
      f.txt("video", "Videoscopio usado"), f.si("seco", "Interior sin agua ni humedad condensada"),
      f.sel("corr", "Corrosión interior", ["No", "Daño menor: va a PH", "Compromete el recipiente: inutilizar"], { req: true, ok: (v) => v === "" ? null : !v.startsWith("Compromete") }),
      f.sel("dano", "Daño mecánico", ["No", "Menor: va a PH", "Abolladura: inutilizar"], { req: true, ok: (v) => v === "" ? null : !v.startsWith("Abolladura") }),
      f.txt("foto", "Foto o video (referencia del archivo)"), f.obs()] },
  { id: "REC-03", nombre: "Ensayo de pérdidas (recarga)", linea: "rec", puestos: [["rec", "20"]],
    normas: ["IRAM 3517-2:2020 9.4.10", "9.4.8 (fuera del recinto si evapora agua)"],
    campos: [f.fecha(), f.oper(), f.txt("os", "Orden de servicio", "", true), f.txt("serie", "N° de serie del recipiente", "", true),
      f.sel("met", "Método", ["Inmersión (fuera del recinto de polvo)", "Detector"], { req: true }), f.si("verde", "Manómetro en zona verde"),
      f.si("sin", "Sin pérdidas de propelente ni de agente"), f.obs()] },
  { id: "REC-04", nombre: "PT de recargas: precinto, etiqueta y despacho", linea: "rec", puestos: [["rec", "21"]],
    normas: ["IRAM 3517-2:2020 9.4.13 (traba y precinto)", "9.6 y tabla 4 (marbete)", "9.4.14 (oblea)"],
    campos: [f.fecha(), f.oper(), f.txt("os", "Orden de servicio", "", true), f.txt("serie", "N° de serie del recipiente", "", true),
      f.txt("prec", "N° de precinto", "", true), f.si("marb", "Marbete del color del año colocado"), f.si("oblea", "Oblea con próximo mantenimiento y vencimiento de la PH"),
      f.si("etq", "Etiqueta de servicio colocada"), f.txt("jaula", "Jaula de despacho"), f.txt("remito", "Remito o recorrido"), f.obs()] },
  { id: "REV-01", nombre: "Recepción de revendidos", linea: "rev", puestos: [],
    normas: ["Etiqueta y n° del fabricante (FLAMA no regraba)", "IRAM 3517-2:2020 9.4.13 (precinto)", "Stock_MP RV-*"],
    campos: [f.fecha(), f.oper("Recibió"), { k: "mp", l: "Modelo", tipo: "mp", req: true, filtro: (m) => m.cod.startsWith("RV-") },
      f.txt("fab", "Fabricante (marca de la etiqueta)", "", true), { k: "seriesRv", l: "N° de serie del fabricante (uno por línea)", tipo: "area", req: true, ayuda: "Tal como figura en su etiqueta o grabado" },
      f.num("anio", "Año de fabricación", { req: true }), f.txt("sello", "Sello o estampilla IRAM (n° del lote)"), f.txt("remito", "Remito", "", true),
      f.si("etq", "Etiqueta del fabricante completa y legible"), f.si("verde", "Manómetro en zona verde"), f.si("prec", "Traba y precinto intactos"),
      { k: "slot", l: "Lugar en el PT (zona Reventa)", tipo: "slot", req: true, zona: "rv" }, f.obs()],
    efecto: (r) => {
      if (r.res !== "Conforme") return;
      const ser = String(r.v.seriesRv || "").split(/\n|,/).map((x) => x.trim()).filter(Boolean);
      ser.forEach((s) => S.rev.push({ serie: s, cod: r.v.mp, fab: r.v.fab, anio: r.v.anio, reg: r.id, slot: r.v.slot, estado: "En PT", t: r.t }));
      const c = r.v.mp; S.stock[c] = { u: (S.stock[c] ? S.stock[c].u : 0) + ser.length, src: "Recepción " + r.id, t: r.t };
      const pal = S.pallets[r.v.slot];
      if (pal && pal.prod === MP[c].mat) { pal.cant += ser.length; pal.series += ", " + ser.join(", "); }
      else S.pallets[r.v.slot] = { id: "PAL-" + String(sig("PAL")).padStart(4, "0"), prod: MP[c].mat, cant: ser.length, lote: r.v.sello, series: ser.join(", "), ffab: r.v.anio ? `${r.v.anio}-01-01` : r.v.fecha, quien: r.v.oper, t: r.t, reg: r.id };
    } },
];
const FORM = Object.fromEntries(FORMS.map((x) => [x.id, x]));
const puestosTxt = (fm) => fm.puestos.map(([l, n]) => `${{ man: "Manuales", car: "Carros", rec: "Recargas" }[l]} ${n} · ${PUESTO(l, n)}`).join(" — ") || "Almacén";
function campoHtml(c) {
  const id = "c_" + c.k, req = c.req ? "required" : "";
  let inp;
  if (c.tipo === "fecha") inp = `<input id="${id}" type="date" value="${hoy()}" ${req}>`;
  else if (c.tipo === "num") inp = `<input id="${id}" type="number" step="any" ${req}>`;
  else if (c.tipo === "sel") inp = `<select id="${id}" ${req}><option value="">Elegir…</option>${c.opts.map((o) => `<option>${esc(o)}</option>`).join("")}</select>`;
  else if (c.tipo === "mp") inp = `<select id="${id}" ${req}><option value="">Elegir…</option>${D.mp.filter(c.filtro).map((m) => `<option value="${esc(m.cod)}">${esc(m.cod)} · ${esc(m.mat)}</option>`).join("")}</select>`;
  else if (c.tipo === "slot") inp = `<select id="${id}" ${req}><option value="">Elegir…</option>${ZONAS.filter((z) => !c.zona || z.k === c.zona).map((z) => `<optgroup label="${esc(z.t)}">${z.slots.filter((s) => !S.pallets[s] || c.zona).map((s) => `<option>${s}</option>`).join("")}</optgroup>`).join("")}</select>`;
  else if (c.tipo === "area") inp = `<textarea id="${id}" rows="3" ${req}></textarea>`;
  else if (c.tipo === "lect") inp = `<div class="lect">${Array.from({ length: c.n }, (_, i) => `<input id="${id}_${i}" type="number" step="any" aria-label="Lectura ${i + 1}" ${req}>`).join("")}</div>`;
  else if (c.tipo === "si") return `<div class="campo ancho" data-k="${c.k}"><label class="chk"><input id="${id}" type="checkbox"> <span>${esc(c.l)}${c.ayuda ? ` <span class="mut">· ${esc(c.ayuda)}</span>` : ""}</span></label></div>`;
  else inp = `<input id="${id}" ${req}>`;
  const ancho = ["area", "lect"].includes(c.tipo) || c.k === "obs" ? "ancho" : "";
  return `<div class="campo ${ancho}" data-k="${c.k}"><label for="${c.tipo === "lect" ? id + "_0" : id}">${esc(c.l)}</label>${inp}${c.ayuda && c.tipo !== "si" ? `<span class="ayuda">${esc(c.ayuda)}</span>` : ""}</div>`;
}
function leer(fm) {
  const v = {};
  fm.campos.forEach((c) => {
    const id = "c_" + c.k;
    if (c.tipo === "si") v[c.k] = $("#" + id).checked;
    else if (c.tipo === "num") { const x = $("#" + id).value; v[c.k] = x === "" ? null : parseFloat(x); }
    else if (c.tipo === "lect") v[c.k] = Array.from({ length: c.n }, (_, i) => $(`#${id}_${i}`).value).filter((x) => x !== "").map(parseFloat);
    else v[c.k] = $("#" + id).value;
  });
  return v;
}
function evaluar(fm, v) {
  const mal = [];
  fm.campos.forEach((c) => { if (c.ok) { const r = c.ok(v[c.k], v); if (r === false) mal.push(c); } });
  return mal;
}
function vForm(id) {
  const fm = FORM[id];
  if (!fm) return vFormularios();
  const regs = S.regs.filter((r) => r.f === id).slice().reverse();
  const cols = fm.campos.filter((c) => !["fecha", "obs"].includes(c.k) && c.tipo !== "si").slice(0, 5);
  return `<div class="cab"><div><a href="#formularios" class="mut" style="font-size:12.5px">← Fichas</a>
    <h1>${esc(fm.id)} · ${esc(fm.nombre)}</h1><p>${esc(puestosTxt(fm))}</p><div class="normas" style="margin-top:6px">${fm.normas.map((n) => `<span>${esc(n)}</span>`).join("")}</div></div></div>
    <div class="grid"><section class="panel c7"><header><h2>Nuevo registro</h2><span class="mut" style="font-size:12px">Los campos con criterio se marcan en verde o rojo</span></header>
      <form class="cuerpo" id="fForm"><div class="campos">${fm.campos.map(campoHtml).join("")}</div>
      <div id="fRes" style="margin-top:12px"></div><div style="margin-top:12px" class="filtros"><button class="btn pri" type="submit">Guardar registro</button></div></form></section>
    <section class="panel c5"><header><h2>Registros</h2><span class="mut num">${regs.length}</span></header><div class="cuerpo tabla">
      ${regs.length ? `<table><thead><tr><th>Registro</th>${cols.map((c) => `<th>${esc(c.l.split(" (")[0])}</th>`).join("")}<th>Resultado</th></tr></thead><tbody>
      ${regs.map((r) => `<tr><td class="mono">${esc(r.id)}<br><span class="mut">${esc(r.t)}</span></td>${cols.map((c) => `<td>${esc(Array.isArray(r.v[c.k]) ? r.v[c.k].join(" · ") : r.v[c.k] ?? "")}</td>`).join("")}
        <td><span class="pill ${r.res === "Conforme" ? "ok" : "crit"}">${esc(r.res)}</span></td></tr>`).join("")}</tbody></table>` : `<div class="vacio">Todavía no hay registros de ${esc(fm.id)}.</div>`}</div></section></div>`;
}
function armarForm(id) {
  const fm = FORM[id], form = $("#fForm");
  if (!fm || !form) return;
  const marcar = () => {
    const v = leer(fm);
    fm.campos.forEach((c) => {
      const el = $(`.campo[data-k="${c.k}"]`, form);
      if (!el || !c.ok) return;
      const r = c.ok(v[c.k], v);
      el.classList.toggle("mal", r === false); el.classList.toggle("bien", r === true);
    });
  };
  form.addEventListener("input", marcar);
  form.addEventListener("change", marcar);
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const v = leer(fm), mal = evaluar(fm, v);
    const r = { id: `${id}-${String(sig(id)).padStart(4, "0")}`, f: id, t: ahora(), v, res: mal.length ? "No conforme" : "Conforme", mal: mal.map((c) => c.l) };
    S.regs.push(r);
    if (fm.efecto) fm.efecto(r);
    guardar();
    location.hash = "f-" + id; pintar();
    toast(`${r.id} guardado · ${r.res}${mal.length ? ": " + mal.map((c) => c.l).join(", ") : ""}`);
  });
}
function vFormularios() {
  const grupo = (l, t, sub) => `<section class="panel c12"><header><h2>${t}</h2><span class="mut" style="font-size:12.5px">${sub}</span></header><div class="cuerpo forms">
    ${FORMS.filter((x) => x.linea === l).map((x) => `<a class="fcard" href="#f-${x.id}" style="text-decoration:none;color:inherit"><b>${x.id}</b><h3>${esc(x.nombre)}</h3>
      <span class="mut" style="font-size:12px">${esc(puestosTxt(x))}</span><span style="font-size:12px">${S.regs.filter((r) => r.f === x.id).length} registros</span></a>`).join("")}</div></section>`;
  return `${bandaEjemplo()}<div class="cab"><div><h1>Fichas de control</h1><p>Una por control crítico. Lo que no cumple la norma se marca en rojo.</p></div>
    <div class="filtros"><button class="btn" data-a="csv">Copiar registros (CSV)</button></div></div>
    <div class="grid">${grupo("fab", "Fabricación: manuales y carros", "Identificación: n° de serie del marcado Pannier")}
    ${grupo("rec", "Recargas", "Identificación: orden de servicio y n° de serie grabado por el fabricante del equipo")}
    ${grupo("rev", "Revendidos", "Identificación: n° de serie de la etiqueta del fabricante")}</div>`;
}

// ---------------------------------------------------------------- trazabilidad (búsqueda)
let Q = "";
function coincide(r, q) {
  const n = parseInt(q, 10);
  if (!isNaN(n) && /^\d+$/.test(q) && r.v.sd != null && r.v.sh != null && n >= r.v.sd && n <= r.v.sh) return "serie dentro del rango";
  if (!isNaN(n) && /^\d+$/.test(q) && r.v.serie != null && String(r.v.serie) === q) return "serie";
  const txt = Object.values(r.v).map((x) => Array.isArray(x) ? x.join(" ") : String(x ?? "")).join(" ").toLowerCase();
  return q && txt.includes(q.toLowerCase()) ? "texto" : null;
}
function vTraza() {
  const q = Q.trim();
  const hits = q ? S.regs.map((r) => [r, coincide(r, q)]).filter(([, c]) => c) : [];
  const pal = q ? Object.entries(S.pallets).filter(([, p]) => (p.series + " " + p.lote + " " + p.id).toLowerCase().includes(q.toLowerCase()) || (/^\d+$/.test(q) && enRango(p.series, +q))) : [];
  const rv = q ? S.rev.filter((x) => x.serie.toLowerCase() === q.toLowerCase()) : [];
  const nombre = (id) => (FORM[id] || { nombre: id === "DES" ? "Despacho" : id }).nombre;
  return `<div class="cab"><div><h1>Trazabilidad</h1><p>Buscá un n° de serie, un lote, una colada o una orden de servicio.</p></div>
    <div class="filtros"><a class="btn" href="#marcado">Identificación sin QR</a><a class="btn" href="#revendidos">Revendidos</a></div></div>
    <form id="fBus" class="filtros" style="margin-bottom:12px"><input id="bq" type="search" value="${esc(q)}" placeholder="Ej.: 1234, OP-26-10-08, colada 45871, OS-1520" style="min-width:min(380px,100%)" aria-label="Buscar"><button class="btn pri" type="submit">Buscar</button></form>
    ${!q ? `<div class="vacio">Probá con <a href="#" data-q="5500">5500</a>, <a href="#" data-q="C-45871">C-45871</a> o <a href="#" data-q="OS-1520">OS-1520</a>.</div>` : `
    <div class="grid">${rv.length ? `<section class="panel c12"><header><h2>Revendido</h2></header><div class="cuerpo"><dl class="dl">${rv.map((x) => `<dt>${esc(x.serie)}</dt><dd>${esc(MP[x.cod] ? MP[x.cod].mat : x.cod)} · ${esc(x.fab)} · ${esc(x.anio)} · ${esc(x.estado)} ${x.slot ? "· lugar " + esc(x.slot) : ""} ${x.remito ? "· remito " + esc(x.remito) : ""}</dd>`).join("")}</dl></div></section>` : ""}
    ${pal.length ? `<section class="panel c12"><header><h2>En el PT ahora</h2></header><div class="cuerpo">${pal.map(([s, p]) => `<p style="margin:0"><b>${esc(s)}</b> · ${esc(p.id)} · ${esc(p.prod)} · ${nf(p.cant)} u · fabricado ${fecha(p.ffab)}</p>`).join("")}</div></section>` : ""}
    ${(() => { const gs = grupos().filter((x) => hits.some(([r]) => (x.tipo === "lote" ? r.v.lote : r.v.os) === x.id));
      return gs.length ? `<section class="panel c12"><header><h2>${gs.length === 1 ? "Lote" : "Lotes"}</h2></header><div class="cuerpo"><ul class="lista">${gs.map(itemGrupo).join("")}</ul>
        <p class="mut" style="font-size:12.5px;margin:8px 0 0">Tocá el lote para ver su recorrido en el layout: verde lo que tiene ficha, punteado lo que falta.</p></div></section>` : ""; })()}
    <section class="panel c12"><header><h2>Registros</h2><span class="mut num">${hits.length}</span></header><div class="cuerpo tabla">
      ${hits.length ? `<table><thead><tr><th>Cuándo</th><th>Registro</th><th>Proceso</th><th>Coincide por</th><th>Datos</th><th>Resultado</th></tr></thead><tbody>
      ${hits.sort((a, b) => a[0].t.localeCompare(b[0].t)).map(([r, c]) => `<tr><td class="num">${esc(r.t)}</td><td class="mono">${esc(r.id)}</td><td>${esc(nombre(r.f))}</td><td>${esc(c)}</td>
        <td style="font-size:12.5px">${esc(["modelo", "lote", "sd", "sh", "colada", "os", "serie", "oper", "remito", "prod"].filter((k) => r.v[k] != null && r.v[k] !== "").map((k) => `${k}: ${r.v[k]}`).join(" · "))}</td>
        <td><span class="pill ${["Conforme", "Despachado"].includes(r.res) ? "ok" : "crit"}">${esc(r.res)}</span></td></tr>`).join("")}</tbody></table>` : `<div class="vacio">No hay registros con «${esc(q)}».</div>`}</div></section></div>`}`;
}
function enRango(series, n) {
  return String(series || "").split(",").some((s) => { const m = /(\d+)\s*[–-]\s*(\d+)/.exec(s); return m ? n >= +m[1] && n <= +m[2] : +s.trim() === n; });
}

// ---------------------------------------------------------------- revendidos
function vRevendidos() {
  return `${bandaEjemplo()}<div class="cab"><div><h1>Revendidos</h1><p>Cada unidad se sigue con el n° de la etiqueta de su fabricante.</p></div>
    <div class="filtros"><a class="btn pri" href="#f-REV-01">Recibir revendidos</a></div></div>
    <div class="grid"><section class="panel c7"><header><h2>Modelos de reventa</h2></header><div class="cuerpo tabla"><table>
      <thead><tr><th>Código</th><th>Modelo</th><th>Proveedor</th><th class="n">En PT</th><th class="n">PP</th><th class="n">Máx.</th></tr></thead><tbody>
      ${RV.map((m) => `<tr><td class="mono">${esc(m.cod)}</td><td>${esc(m.mat)}</td><td>${esc(m.prov)}</td><td class="n">${nf(S.rev.filter((x) => x.cod === m.cod && x.estado === "En PT").length)}</td><td class="n">${nf(m.pp, 1)}</td><td class="n">${nf(m.max, 1)}</td></tr>`).join("")}
      </tbody></table></div></section>
    <section class="panel c5"><header><h2>Unidades recibidas</h2><span class="mut num">${S.rev.length}</span></header><div class="cuerpo tabla">
      ${S.rev.length ? `<table><thead><tr><th>Serie del fabricante</th><th>Modelo</th><th>Estado</th></tr></thead><tbody>${S.rev.slice().reverse().map((x) => `<tr><td class="mono">${esc(x.serie)}</td><td>${esc(MP[x.cod].mat)}</td><td><span class="pill ${x.estado === "En PT" ? "info" : "ok"}">${esc(x.estado)}</span></td></tr>`).join("")}</tbody></table>` : `<div class="vacio">Sin unidades recibidas.</div>`}</div></section></div>`;
}

// ---------------------------------------------------------------- marcado
function figuraMarcado() {
  // matafuego manual de frente, con la costura longitudinal al frente: el marcado arriba y entero a la izquierda de la
  // costura (final a 15 mm de la costura, borde de arriba a 20 mm del borde de la chapa), la etiqueta abajo y, solo en
  // los sustitutos, la faja amarilla entera en la pollera. Escala del dibujo: 1 mm ≈ 0,7 px (esquemático).
  return `<svg viewBox="0 0 440 340" width="100%" style="max-width:540px" role="img" aria-label="Ubicación del marcado en el cuerpo">
    <defs><linearGradient id="gc" x1="0" x2="1"><stop offset="0" stop-color="#8e1a14"/><stop offset=".45" stop-color="#c8312a"/><stop offset="1" stop-color="#7a1611"/></linearGradient></defs>
    <rect x="203" y="8" width="34" height="22" rx="3" fill="#9aa3b2"/>
    <path d="M140 70 Q140 30 220 30 Q300 30 300 70 Z" fill="url(#gc)"/>
    <rect x="140" y="70" width="160" height="236" fill="url(#gc)"/>
    <line x1="140" y1="70" x2="300" y2="70" stroke="#5a0d09" stroke-width="1.5"/>
    <rect x="140" y="272" width="160" height="34" fill="#f2c400"/>
    <text x="220" y="287" font-size="9.5" text-anchor="middle" fill="#1c2229" font-family="Barlow, Arial" font-weight="600">FAJA DE SUSTITUTO ≤ 40 mm</text>
    <text x="220" y="299" font-size="9" text-anchor="middle" fill="#1c2229" font-family="Barlow, Arial">entera, sin cortes</text>
    <line x1="220" y1="72" x2="220" y2="306" stroke="#5a0d09" stroke-width="2" stroke-dasharray="6 3"/>
    <rect x="143" y="84" width="67" height="11" fill="none" stroke="#ffffff" stroke-width="1"/>
    <text x="145.5" y="92.4" font-size="6.6" fill="#ffe5e2" font-family="Consolas, monospace" textLength="52" lengthAdjust="spacingAndGlyphs">FLAMA S.A. N°000001 26</text>
    <rect x="200" y="84.5" width="10" height="10" fill="none" stroke="#ffffff"/>
    <rect x="152" y="124" width="136" height="110" rx="3" fill="#f4f4f4"/>
    <rect x="152" y="124" width="136" height="18" fill="#c8312a"/><text x="220" y="137" font-size="10" fill="#fff" text-anchor="middle" font-family="Barlow, Arial" font-weight="600">ETIQUETA</text>
    <g font-family="Barlow, Arial" font-size="11" fill="#1c2229" stroke-width="0.9">
      <line x1="210" y1="104" x2="220" y2="104" stroke="#1c2229"/><line x1="210" y1="96" x2="210" y2="108" stroke="#1c2229"/>
      <text x="224" y="107" font-size="9.5">15 mm</text>
      <line x1="130" y1="70" x2="130" y2="84" stroke="#1c2229"/><line x1="126" y1="70" x2="140" y2="70" stroke="#1c2229"/><line x1="126" y1="84" x2="143" y2="84" stroke="#1c2229"/>
      <text x="124" y="81" font-size="9.5" text-anchor="end">20 mm</text>
      <line x1="176" y1="84" x2="318" y2="50" stroke="#1c2229"/><text x="320" y="46">Marcado Pannier</text><text x="320" y="59" font-size="10" fill="#4f5863">horizontal, sin código;</text><text x="320" y="71" font-size="10" fill="#4f5863">crece hacia la izquierda</text>
      <line x1="220" y1="200" x2="318" y2="178" stroke="#1c2229"/><text x="320" y="176">Costura longitudinal</text>
      <line x1="300" y1="289" x2="318" y2="289" stroke="#1c2229"/><text x="320" y="286">Pollera</text>
      <line x1="300" y1="70" x2="318" y2="104" stroke="#1c2229"/><text x="320" y="108">Borde superior</text><text x="320" y="120" font-size="10" fill="#4f5863">de la chapa del cuerpo</text></g></svg>`;
}
function vMarcado() {
  return `<div class="cab"><div><h1>Identificación sin QR</h1><p>Qué número identifica a cada cosa y dónde está.</p></div></div>
    <div class="grid"><section class="panel c6"><header><h2>Marcado Pannier del producto propio</h2></header><div class="cuerpo">${figuraMarcado()}
      <ul style="margin:8px 0 0;padding-left:18px;display:grid;gap:4px;font-size:13px">
      <li>Lo hace la Pannier en el puesto 6 del balanceo (marcado del cuerpo), sobre el desarrollo todavía plano, entre la guillotina 2 y el cilindrado. Desde ese momento el cuerpo tiene su número.</li>
      <li>Texto: «FLAMA S.A. N° serie año» (en los carros, también la presión de ensayo) y el cuño DPS 15 × 7 al final (IRAM 3523 5.1, IRAM 3550 5.1, Res. 349/07 anexo IV).</li>
      <li>Lugar fijo en la chapa en todos los modelos: el final del marcado a 15 mm del borde de la costura y el borde de arriba a 20 mm del borde superior; el texto crece hacia la izquierda. Una línea horizontal, sin código 2D.</li>
      <li>Queda arriba de todo, por encima de la etiqueta: la faja amarilla de los sustitutos va entera en la pollera, sin cortes (IRAM 3517-2:2020 9.4.5 b).</li></ul></div></section>
    <section class="panel c6"><header><h2>Qué identifica a cada cosa</h2></header><div class="cuerpo tabla"><table><thead><tr><th>Qué</th><th>Número</th><th>Dónde está</th><th>Lo carga</th></tr></thead><tbody>
      <tr><td>Matafuego o cilindro propio</td><td>N° de serie + año</td><td>Marcado Pannier en el cuerpo</td><td>FAB-02 y siguientes</td></tr>
      <tr><td>Lote de fabricación</td><td>Orden de producción + rango de series</td><td>Hoja de ruta del lote</td><td>Todos los FAB</td></tr>
      <tr><td>Chapa y fleje</td><td>Colada del certificado</td><td>Etiqueta del paquete o rollo</td><td>FAB-01 → FAB-02</td></tr>
      <tr><td>Insumos y agentes</td><td>Lote del proveedor</td><td>Bulto</td><td>FAB-01, REC-01</td></tr>
      <tr><td>Revendido</td><td>N° de serie del fabricante</td><td>Su etiqueta o grabado</td><td>REV-01</td></tr>
      <tr><td>Equipo en recarga</td><td>Orden de servicio + n° de serie grabado</td><td>Recipiente del cliente</td><td>REC-02 a REC-04</td></tr>
      <tr><td>Pallet de PT</td><td>PAL-nnnn + lugar</td><td>Etiqueta de pallet</td><td>FAB-11, REV-01</td></tr></tbody></table></div></section></div>`;
}

// ---------------------------------------------------------------- puestos, lotes y recorridos
// Mismo plano (rev10), mismos puestos y mismos recorridos que la app de gestión interna (catalogo_gestion.json y
// caminos.js copiados de APP_SISTEMA_DE_GESTION_INTERNA_FLAMA). Cada ficha se carga en un puesto del plano; dónde está
// cada lote sale de la última ficha que tiene cargada. REV es el puesto de recepción de revendidos (sector del plano
// «Trazabilidad PT»), que la app de gestión no tiene.
const CAT = D.cat;
const PUESTOS = Object.fromEntries([...CAT.puestos, { id: "REV", linea: "PT", nombre: "Recepción de revendidos", sector: "exp_trazabilidad", registro: true }]
  .map((p, i) => [p.id, { ...p, orden: i }]));
const LIN = { REC: ["Recargas", "var(--rec)"], MAN: ["Manuales", "var(--man)"], CAR: ["Carros", "var(--car)"], MP: ["Materia prima", "var(--mp)"],
  PT: ["Producto terminado", "var(--pt)"], EXT: ["Fuera de planta", "var(--ext)"] };
// Puesto del plano donde se carga cada ficha: [manuales, carros] (Balanceo › Carga, puestos de cada ficha)
const PUESTO_FICHA = { "FAB-01": ["MP_TRAZ"], "FAB-02": ["MARC"], "FAB-03": ["M3", "C5"], "FAB-04": ["M6", "C6"], "FAB-05": ["M7", "C7"],
  "FAB-06": ["M8"], "FAB-07": ["MPH", "CPH"], "FAB-08": ["M11"], "FAB-09": ["M18", "C12"], "FAB-10": ["M15", "C15"], "FAB-11": ["PTM", "C16"],
  "REC-01": ["MP_TRAZ"], "REC-02": ["R9"], "REC-03": ["R26"], "REC-04": ["R27"], "REV-01": ["REV"] };
const FICHAS_DE = {};
Object.entries(PUESTO_FICHA).forEach(([f, ps]) => ps.forEach((p) => (FICHAS_DE[p] = (FICHAS_DE[p] || []).concat(f))));
const esCarro = (r) => !!(MOD(r.v.modelo) || {}).car || /^Carro|de carro/.test(r.v.prod || "");
const puestoDe = (r) => { const p = PUESTO_FICHA[r.f]; return !p ? null : p.length > 1 && esCarro(r) ? p[1] : p[0]; };
// Lotes (fichas FAB con lote) y órdenes de servicio (fichas REC con OS), con su recorrido y el paso donde están.
function grupos() {
  const g = {};
  S.regs.forEach((r) => {
    const k = r.v.lote && /^FAB-(0[2-9]|1[01])$/.test(r.f) ? "L:" + r.v.lote : r.v.os && /^REC-0[2-4]$/.test(r.f) ? "O:" + r.v.os : null;
    if (!k) return;
    const x = g[k] || (g[k] = { k, id: k.slice(2), tipo: k[0] === "L" ? "lote" : "os", regs: [], modelo: null, u: 0, sd: null, sh: null });
    x.regs.push(r);
    if (r.v.modelo) x.modelo = r.v.modelo;
    if (r.v.sd != null && r.v.sh != null) { x.sd = x.sd == null ? r.v.sd : Math.min(x.sd, r.v.sd); x.sh = Math.max(x.sh || 0, r.v.sh); }
    if (r.v.serie && x.tipo === "os") x.serie = r.v.serie;
  });
  return Object.values(g).map((x) => {
    x.regs.sort((a, b) => a.t.localeCompare(b.t));
    const ref = x.regs.find((r) => r.v.modelo) || x.regs[0];
    x.linea = x.tipo === "os" ? "REC" : esCarro(ref) ? "CAR" : "MAN";
    x.ruta = x.tipo === "os" ? "REC-ABC" : x.linea === "CAR" ? "CAR-STD" : x.modelo === "ABC 1 kg" ? "MAN-1KG" : "MAN-STD";
    x.u = x.tipo === "os" ? 1 : x.sd != null ? x.sh - x.sd + 1 : +((x.regs.find((r) => r.f === "FAB-11") || { v: {} }).v.cant || 0);
    const pasos = CAT.rutas[x.ruta].pasos, idx = x.regs.map((r) => pasos.indexOf(puestoDe(r))).filter((i) => i >= 0);
    x.paso = idx.length ? Math.max(...idx) : 0;
    x.puesto = pasos[x.paso];
    x.fin = x.regs.some((r) => ["FAB-11", "REC-04"].includes(r.f) && r.res === "Conforme");
    x.nc = x.regs.some((r) => r.res === "No conforme");
    x.ultima = x.regs[x.regs.length - 1];
    return x;
  });
}
const enCurso = () => grupos().filter((x) => !x.fin);

// ---------------------------------------------------------------- layout de planta
const GEO = {};
D.layout.sectores.forEach((s) => (GEO[s.id] = s));
CAT.zonas.forEach((z) => (GEO[z.id] = { ...z, externa: true }));
const caja = (s) => s.rect || (() => { const xs = s.poly.map((p) => p[0]), ys = s.poly.map((p) => p[1]); return [Math.min(...xs), Math.min(...ys), Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)]; })();
// Un punto por puesto en el centro de su sector; si varios comparten sector, se reparten sobre el lado largo (como la app de gestión).
const PUNTOS = {}, LINEA_SECTOR = {};
(() => {
  const por = {};
  Object.values(PUESTOS).forEach((p) => (por[p.sector] = por[p.sector] || []).push(p.id));
  Object.entries(por).forEach(([sid, ids]) => {
    const g = GEO[sid]; if (!g) return;
    const [x, y, w, h] = caja(g), hor = w >= h;
    ids.forEach((id, k) => {
      const f = (k + 1) / (ids.length + 1), chico = h < 3.2 && !g.externa;
      PUNTOS[id] = hor ? { x: x + w * f, y: y + h * (chico ? 0.66 : 0.62) } : { x: x + w / 2, y: y + h * f };
      const l = PUESTOS[id].linea; if (!LINEA_SECTOR[sid] && l !== "EXT") LINEA_SECTOR[sid] = l;
    });
  });
})();
let CAMINO = null;
const camino = (a, b) => (CAMINO || (CAMINO = crearCaminos({ layout: D.layout, zonas: CAT.zonas, limites: CAT.limites, puestos: PUESTOS })))(a, b, PUNTOS[a], PUNTOS[b]);
const LAY = { filtro: "todas", vb: null };
function textoSector(nombre, x, y, w, h, clase = "l-nombre") {
  const palabras = nombre.split(" ");
  let mejor = { lineas: [nombre], fs: Math.min(0.95, (w - 0.3) / (nombre.length * 0.58), h * 0.3) };
  for (let i = 1; i < palabras.length; i++) {
    const l = [palabras.slice(0, i).join(" "), palabras.slice(i).join(" ")];
    const fs = Math.min(0.95, ...l.map((t) => (w - 0.3) / (t.length * 0.58)), h * 0.22);
    if (fs > mejor.fs) mejor = { lineas: l, fs };
  }
  const fs = Math.max(0.3, mejor.fs);
  return `<text class="${clase}" font-size="${fs.toFixed(2)}" x="${(x + 0.18).toFixed(2)}" y="${(y + fs * 1.05 + 0.08).toFixed(2)}">${mejor.lineas.map((t, i) => `<tspan x="${(x + 0.18).toFixed(2)}" dy="${i ? (fs * 1.1).toFixed(2) : 0}">${esc(t)}</tspan>`).join("")}</text>`;
}
function svgPlanta() {
  const L = D.layout;
  const p = [`<defs><pattern id="rayado" width="0.9" height="0.9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="0.9" height="0.9" fill="#f7f8f9"/><line x1="0" y1="0" x2="0" y2="0.9" stroke="#dfe3e8" stroke-width="0.22"/></pattern></defs>`,
    `<text class="l-orient" font-size="1.25" x="-10" y="-40.8">▲ ARRIBA · SALIDA DE PT Y RECARGAS</text>`, `<text class="l-orient" font-size="1.25" x="24.5" y="34.6">▼ ABAJO · INGRESO DE MATERIA PRIMA</text>`];
  CAT.zonas.forEach((z) => { const [x, y, w, h] = z.rect;
    p.push(`<rect class="l-externa ${z.interna ? "interna" : ""}" data-sector="${z.id}" x="${x}" y="${y}" width="${w}" height="${h}" rx="0.4"/>`, textoSector(z.nombre, x + 0.2, y + 0.1, w - 0.4, h, "l-nombre-ext")); });
  p.push(`<rect class="l-nave" x="0" y="0" width="${L.nave.ancho}" height="${L.nave.largo}"/>`);
  L.nave.anexos.forEach(([x, y, w, h]) => p.push(`<rect class="l-nave" x="${x}" y="${y}" width="${w}" height="${h}"/>`));
  L.pasillos.forEach((q) => { const [x, y, w, h] = q.rect; p.push(`<rect class="l-pasillo" x="${x}" y="${y}" width="${w}" height="${h}"/>`); });
  L.sectores.forEach((s) => {
    const lin = LINEA_SECTOR[s.id], est = lin ? `style="--c:${LIN[lin][1]}"` : "", cls = `l-sector ${lin ? "lin" : ""}`;
    if (s.rect) { const [x, y, w, h] = s.rect; p.push(`<rect class="${cls}" ${est} data-sector="${s.id}" x="${x}" y="${y}" width="${w}" height="${h}"/>`, textoSector(s.nombre, x, y, w, h)); }
    else { const [x, y, w] = caja(s); p.push(`<polygon class="${cls}" ${est} data-sector="${s.id}" points="${s.poly.map((q) => q.join(",")).join(" ")}"/>`, textoSector(s.nombre, x, y, Math.min(w, 9), 4)); }
  });
  L.muros.forEach((m) => p.push(`<polyline class="l-muro" points="${m.map((q) => q.join(",")).join(" ")}"/>`));
  L.portones.forEach((q) => {
    p.push(`<line class="l-porton" x1="${q.de[0]}" y1="${q.de[1]}" x2="${q.a[0]}" y2="${q.a[1]}"/>`);
    const v = q.de[0] === q.a[0], tx = v ? q.de[0] + (q.de[0] < 0 ? -0.5 : 0.5) : (q.de[0] + q.a[0]) / 2, ty = v ? (q.de[1] + q.a[1]) / 2 : q.de[1] - 0.5;
    p.push(`<text class="l-porton-txt" x="${tx}" y="${ty}" text-anchor="${v ? (q.de[0] < 0 ? "end" : "start") : "middle"}">${esc(q.texto.split(" — ")[0])}</text>`);
  });
  return p.join("");
}
// Qué se cuenta en cada punto: lotes y órdenes de servicio en curso en el puesto de su última ficha; en el almacén de MP,
// los códigos para pedir; en los puestos de PT, los lugares ocupados.
const PT_PUESTO = { PTM: ["rack"], C16: ["carros"], C16B: ["anden"], REV: ["rv"] };
function cargaPuestos() {
  const f = LAY.filtro, c = {};
  if (f !== "ALM") enCurso().filter((x) => f === "todas" || x.linea === f).forEach((x) => {
    const q = c[x.puesto] || (c[x.puesto] = { n: 0, u: 0, lin: x.linea, nc: false, txt: "lotes" });
    q.n++; q.u += x.u; q.nc = q.nc || x.nc;
  });
  if (f === "todas" || f === "ALM") {
    const n = D.mp.filter((m) => ["crit", "pedir"].includes(estado(m))).length;
    if (n) c.MP_ALM = { n, lin: "MP", nc: D.mp.some((m) => estado(m) === "crit"), txt: "MP para pedir" };
    Object.entries(PT_PUESTO).forEach(([id, zs]) => { const n2 = ZONAS.filter((z) => zs.includes(z.k)).flatMap((z) => z.slots).filter((s) => S.pallets[s]).length;
      if (n2) c[id] = { n: n2, lin: "PT", txt: "lugares ocupados" }; });
  }
  return c;
}
function svgPuntos() {
  const c = cargaPuestos(), p = [];
  Object.entries(PUNTOS).forEach(([id, pt]) => {
    const P = PUESTOS[id], w = c[id], r = w ? 0.92 : 0.42, x = pt.x.toFixed(2), y = pt.y.toFixed(2), reg = !!FICHAS_DE[id] || P.registro;
    const col = LIN[w ? w.lin : P.linea] ? LIN[w ? w.lin : P.linea][1] : "var(--ext)";
    const forma = reg ? `<rect class="forma" x="${(pt.x - r).toFixed(2)}" y="${(pt.y - r).toFixed(2)}" width="${(r * 2).toFixed(2)}" height="${(r * 2).toFixed(2)}" rx="${(r * 0.3).toFixed(2)}"/>`
      : `<circle class="forma" cx="${x}" cy="${y}" r="${r}"/>`;
    const txt = w ? (w.n > 99 ? "99+" : String(w.n)) : "";
    p.push(`<g class="l-punto ${w ? "con-carga" : ""} ${w && w.nc ? "nc" : ""} ${LAY.sel === id ? "sel" : ""}" style="--c:${col}" data-puesto="${id}"><title>${esc(P.nombre)} · ${id}${w ? ` · ${w.n} ${w.txt}${w.u ? ` · ${nf(w.u)} u` : ""}` : ""}${FICHAS_DE[id] ? ` · ficha ${FICHAS_DE[id].join(", ")}` : ""}</title>${forma}${txt ? `<text class="cant" x="${x}" y="${(pt.y + 0.04).toFixed(2)}" font-size="${txt.length > 2 ? 0.62 : 0.85}">${txt}</text>` : ""}</g>`,
      `<text class="l-cod" x="${x}" y="${(pt.y + r + 0.7).toFixed(2)}" text-anchor="middle">${esc(id.replace("EXT_", ""))}</text>`);
  });
  return p.join("");
}
// Recorrido del lote: verde lo que ya tiene ficha, punteado lo que falta, punto rojo intermitente en su última ficha.
function svgRuta(x) {
  const pasos = CAT.rutas[x.ruta].pasos, act = x.fin ? pasos.length : x.paso, casco = [], hecho = [], falta = [], marcas = [], pts = [];
  for (let i = 0; i < pasos.length - 1; i++) {
    const a = pasos[i], b = pasos[i + 1];
    if (!PUNTOS[a] || !PUNTOS[b] || a === b) continue;
    const tramo = camino(a, b), linea = `points="${tramo.map(([u, v]) => `${u.toFixed(2)},${v.toFixed(2)}`).join(" ")}"`;
    if (i + 1 <= act) {
      casco.push(`<polyline class="r-casco" ${linea}/>`); hecho.push(`<polyline class="r-hecho" ${linea}/>`);
      let m = null;
      for (let k = 0; k < tramo.length - 1; k++) { const [p, q] = [tramo[k], tramo[k + 1]], l = Math.hypot(q[0] - p[0], q[1] - p[1]); if (!m || l > m.l) m = { p, q, l }; }
      if (m && m.l > 2.5) marcas.push(`<path d="M-0.4,-0.36 L0.36,0 L-0.4,0.36 Z" fill="#fff" transform="translate(${(m.p[0] + m.q[0]) / 2},${(m.p[1] + m.q[1]) / 2}) rotate(${Math.atan2(m.q[1] - m.p[1], m.q[0] - m.p[0]) * 180 / Math.PI})"/>`);
    } else falta.push(`<polyline class="r-falta" ${linea}/>`);
  }
  pasos.forEach((id, i) => {
    const p = PUNTOS[id]; if (!p || i === act) return;
    const h = i < act;
    pts.push(`<circle class="${h ? "r-punto-hecho" : "r-punto-falta"}" cx="${p.x}" cy="${p.y}" r="0.55"/><text class="r-num ${h ? "hecho" : "falta"}" x="${p.x}" y="${p.y}">${i + 1}</text>`);
  });
  if (act < pasos.length && PUNTOS[pasos[act]]) {
    const p = PUNTOS[pasos[act]];
    pts.push(`<circle class="r-pulso" cx="${p.x}" cy="${p.y}" r="0.8"/><circle class="r-pulso" cx="${p.x}" cy="${p.y}" r="0.8" style="animation-delay:.7s"/>
      <circle class="r-actual ${x.nc ? "" : "ok"}" cx="${p.x}" cy="${p.y}" r="0.85"/><text class="r-num hecho" x="${p.x}" y="${p.y}">${act + 1}</text>`);
  }
  return [...falta, ...casco, ...hecho, ...marcas, ...pts].join("");
}
const LEY_LAYOUT = `<span><svg viewBox="0 0 16 12"><line x1="1" y1="6" x2="15" y2="6" stroke="#1f9d48" stroke-width="3" stroke-linecap="round"/></svg>Recorrido con ficha</span>
  <span><svg viewBox="0 0 16 12"><circle cx="8" cy="6" r="5" fill="#c8102e"/></svg>Última ficha (dónde está)</span>
  <span><svg viewBox="0 0 16 12"><line x1="1" y1="6" x2="15" y2="6" stroke="#56606b" stroke-width="1.6" stroke-dasharray="3 2"/></svg>Lo que le falta</span>
  <span><svg viewBox="0 0 16 12"><circle cx="8" cy="6" r="3.5" fill="#fff" stroke="#8f99a4" stroke-width="1.2"/></svg>Puesto</span>
  <span><svg viewBox="0 0 16 12"><rect x="4" y="2" width="8" height="8" rx="2" fill="#fff" stroke="#8f99a4" stroke-width="1.2"/></svg>Puesto con ficha</span>
  <span><svg viewBox="0 0 16 12"><rect x="4" y="2" width="8" height="8" rx="2" fill="#fff" stroke="#c8102e" stroke-width="2"/></svg>Con ficha no conforme</span>
  <span><svg viewBox="0 0 16 12"><rect x="1" y="1" width="14" height="10" fill="url(#rayado-ley)" stroke="#9aa3ad" stroke-dasharray="2 1.5"/><defs><pattern id="rayado-ley" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="3" stroke="#dfe3e8" stroke-width="1.2"/></pattern></defs></svg>Fuera de planta</span>`;
const FILTROS = [["todas", "Todas"], ["MAN", "Manuales"], ["CAR", "Carros"], ["REC", "Recargas"], ["ALM", "Almacenes"]];
function vLayout() {
  return `<div class="layout"><section class="panel lienzo"><div class="lienzo-cab">
      <h2 class="titulo-seccion">Layout de planta<small>plano rev ${esc(D.layout.revision)} · ruedita para acercar, arrastrar para mover</small></h2>
      <div class="segmentado" id="filtro-linea">${FILTROS.map(([v, t]) => `<button data-l="${v}">${t}</button>`).join("")}</div></div>
    <div class="lienzo-area"><svg id="plano" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Layout de la planta con los puestos, las fichas y el recorrido del lote">
      <g id="capa-planta">${svgPlanta()}</g><g id="capa-puntos"></g><g id="capa-ruta"></g></svg>
      <div class="zoom"><button id="z-mas" aria-label="Acercar">+</button><button id="z-menos" aria-label="Alejar">−</button><button id="z-reset" aria-label="Ver toda la planta" title="Ver toda la planta">⤢</button></div></div>
    <div class="ley-layout">${LEY_LAYOUT}</div></section>
    <aside class="panel lado" id="lado"></aside></div>`;
}
function aplicarVB() { const s = $("#plano"); if (s) s.setAttribute("viewBox", LAY.vb.map((v) => v.toFixed(2)).join(" ")); }
function prepararZoom() {
  const svg = $("#plano");
  LAY.vbBase = [...CAT.limites];
  if (!LAY.vb) LAY.vb = [...LAY.vbBase];
  aplicarVB();
  const zoom = (f, cx, cy) => { const [x, y, w, h] = LAY.vb, nw = Math.min(LAY.vbBase[2] * 1.6, Math.max(8, w * f)), nh = nw * (h / w);
    LAY.vb = [cx - (cx - x) * (nw / w), cy - (cy - y) * (nh / h), nw, nh]; aplicarVB(); };
  const aPlano = (e) => { const r = svg.getBoundingClientRect(), [x, y, w, h] = LAY.vb, k = Math.max(w / r.width, h / r.height);
    return [x + (w - r.width * k) / 2 + (e.clientX - r.left) * k, y + (h - r.height * k) / 2 + (e.clientY - r.top) * k, k]; };
  svg.addEventListener("wheel", (e) => { e.preventDefault(); const [cx, cy] = aPlano(e); zoom(e.deltaY > 0 ? 1.15 : 1 / 1.15, cx, cy); }, { passive: false });
  let arr = null;
  svg.addEventListener("pointerdown", (e) => { if (e.target.closest(".l-punto")) return; arr = { x: e.clientX, y: e.clientY, vb: [...LAY.vb], k: aPlano(e)[2], mov: false }; });
  svg.addEventListener("pointermove", (e) => { if (!arr) return; if (!arr.mov && Math.hypot(e.clientX - arr.x, e.clientY - arr.y) < 4) return;
    if (!arr.mov) { arr.mov = true; svg.setPointerCapture(e.pointerId); svg.classList.add("arrastrando"); }
    LAY.vb = [arr.vb[0] - (e.clientX - arr.x) * arr.k, arr.vb[1] - (e.clientY - arr.y) * arr.k, arr.vb[2], arr.vb[3]]; aplicarVB(); });
  svg.addEventListener("pointerup", () => { if (arr && arr.mov) LAY.arrastro = Date.now(); arr = null; svg.classList.remove("arrastrando"); });
  const centro = () => [LAY.vb[0] + LAY.vb[2] / 2, LAY.vb[1] + LAY.vb[3] / 2];
  $("#z-mas").onclick = () => zoom(1 / 1.3, ...centro());
  $("#z-menos").onclick = () => zoom(1.3, ...centro());
  $("#z-reset").onclick = () => { LAY.vb = [...LAY.vbBase]; aplicarVB(); };
  $$("#filtro-linea button").forEach((b) => (b.onclick = () => { LAY.filtro = b.dataset.l; actualizarLayout(); }));
}
function encuadrar(ids) {
  const ps = ids.map((i) => PUNTOS[i]).filter(Boolean); if (!ps.length) return;
  const xs = ps.map((p) => p.x), ys = ps.map((p) => p.y), pad = 5;
  let [x, y, w, h] = [Math.min(...xs) - pad, Math.min(...ys) - pad, Math.max(...xs) - Math.min(...xs) + pad * 2, Math.max(...ys) - Math.min(...ys) + pad * 2];
  if (w < 30) { x -= (30 - w) / 2; w = 30; }
  if (h < 30) { y -= (30 - h) / 2; h = 30; }
  LAY.vb = [x, y, w, h]; aplicarVB();
}
// Lee los parámetros del hash (#layout?lote=…, ?os=…, ?puesto=…, ?linea=…) y redibuja puntos, recorrido y panel.
function actualizarLayout() {
  const P = PARAMS, gs = grupos();
  if (P.get("linea")) LAY.filtro = P.get("linea");
  LAY.sel = P.get("puesto") || null;
  const gid = P.get("lote") ? "L:" + P.get("lote") : P.get("os") ? "O:" + P.get("os") : null;
  LAY.g = gid ? gs.find((x) => x.k === gid) || null : null;
  $$("#filtro-linea button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.l === LAY.filtro)));
  $("#capa-puntos").innerHTML = svgPuntos();
  $$(".l-sector.activo").forEach((s) => s.classList.remove("activo"));
  if (LAY.g) {
    $("#capa-ruta").innerHTML = svgRuta(LAY.g);
    const sec = (PUESTOS[LAY.g.puesto] || {}).sector; if (sec) { const el = $(`[data-sector="${sec}"]`); if (el) el.classList.add("activo"); }
    if (LAY.encuadrado !== LAY.g.k) { encuadrar(CAT.rutas[LAY.g.ruta].pasos); LAY.encuadrado = LAY.g.k; }
  } else {
    LAY.encuadrado = null;
    const p = LAY.sel && PUNTOS[LAY.sel];
    $("#capa-ruta").innerHTML = p ? `<circle class="r-pulso" cx="${p.x}" cy="${p.y}" r="1" style="stroke:var(--text)"/>` : "";
    if (p) { const el = $(`[data-sector="${PUESTOS[LAY.sel].sector}"]`); if (el) el.classList.add("activo"); }
  }
  $("#lado").innerHTML = ladoLayout(gs);
}
const h4 = (t) => `<h4 class="h4">${t}</h4>`;
const itemGrupo = (x) => `<li data-ir="${x.tipo === "os" ? "os" : "lote"}=${encodeURIComponent(x.id)}" style="--c:${LIN[x.linea][1]}"><span><b class="mono">${esc(x.id)}</b>${x.nc ? ' <span class="pill crit">no conforme</span>' : ""}<br>
  <span class="mut">${esc(x.tipo === "os" ? "Recarga · serie " + (x.serie || "—") : (x.modelo || "") + (x.sd != null ? ` · series ${x.sd}–${x.sh}` : ""))}</span></span>
  <span class="der">${esc((PUESTOS[x.puesto] || {}).nombre || "")}<br><span class="mut">${x.u} u · ${esc(x.ultima.t.slice(5))}</span></span></li>`;
function ladoLayout(gs) {
  const vivos = gs.filter((x) => !x.fin);
  if (LAY.g) return panelGrupo(LAY.g);
  if (LAY.sel && PUESTOS[LAY.sel]) {
    const P = PUESTOS[LAY.sel], fs = FICHAS_DE[LAY.sel] || [], aca = vivos.filter((x) => x.puesto === LAY.sel);
    const regs = S.regs.filter((r) => puestoDe(r) === LAY.sel).slice(-6).reverse();
    let extra = "";
    if (LAY.sel === "MP_ALM" || LAY.sel === "MP_TRAZ") extra = h4("Almacenes con faltantes") + (ALMS.map((a) => [a, D.mp.filter((m) => m.alm === a.alm && ["crit", "pedir"].includes(estado(m))).length]).filter(([, n]) => n)
      .map(([a, n]) => `<p class="renglon"><span>${esc(a.alm)}</span><span class="pill crit">${n} para pedir</span></p>`).join("") || `<p class="mut">Ninguno.</p>`) + `<div class="filtros"><a class="btn chico" href="#almacen">Almacén de MP</a><a class="btn chico" href="#mp">Kanban de MP</a></div>`;
    if (PT_PUESTO[LAY.sel]) extra = h4("Zonas de PT") + ZONAS.filter((z) => PT_PUESTO[LAY.sel].includes(z.k)).map((z) => `<p class="renglon"><span>${esc(z.t)}</span><span class="num">${z.slots.filter((q) => S.pallets[q]).length} de ${z.slots.length}</span></p>`).join("") + `<a class="btn chico" href="#pt">Kanban de PT</a>`;
    return `<div class="panel-cab"><a class="volver" href="#layout">← Toda la planta</a><h3>${esc(P.nombre)}</h3><span class="chip linea" style="--c:${(LIN[P.linea] || LIN.EXT)[1]}">${esc((LIN[P.linea] || LIN.EXT)[0])}</span> <span class="mono mut">${esc(P.id)}</span></div>
      <div class="panel-cuerpo">${fs.length ? h4("Ficha de este puesto") + `<div style="display:grid;gap:8px">${fs.map((f) => `<a class="fcard" href="#f-${f}"><b>${f}</b><h3>${esc(FORM[f].nombre)}</h3><span class="mut" style="font-size:12px">${esc(FORM[f].normas.slice(0, 2).join(" · "))}</span></a>`).join("")}</div>` : `<p class="mut">En este puesto no se carga ficha.</p>`}
      ${aca.length ? h4(`Acá ahora · ${aca.length}`) + `<ul class="lista">${aca.map(itemGrupo).join("")}</ul>` : ""}
      ${regs.length ? h4("Últimas fichas") + `<table><tbody>${regs.map((r) => `<tr><td class="mono">${esc(r.id)}</td><td class="num">${esc(r.t.slice(5))}</td><td><span class="pill ${r.res === "Conforme" ? "ok" : "crit"}">${esc(r.res)}</span></td></tr>`).join("")}</tbody></table>` : ""}${extra}</div>`;
  }
  const f = LAY.filtro, lista = vivos.filter((x) => f === "todas" || x.linea === f).sort((a, b) => PUESTOS[a.puesto].orden - PUESTOS[b.puesto].orden);
  const u = (l) => vivos.filter((x) => x.linea === l).reduce((a, x) => a + x.u, 0);
  return `<div class="panel-cab"><span class="mut" style="font-size:12px;letter-spacing:.08em">PLANTA AHORA</span><h3>${lista.length} ${lista.length === 1 ? "lote u orden" : "lotes y órdenes"} en curso</h3>
    <span class="subtitulo">${nf(u("MAN"))} manuales · ${nf(u("CAR"))} carros · ${nf(u("REC"))} recargas</span></div>
    <div class="panel-cuerpo">${f === "ALM" ? `<p class="mut">El almacén de MP muestra los códigos para pedir; los puestos del PT, los lugares ocupados. Tocá uno para ver el detalle.</p>`
      : lista.length ? `<ul class="lista">${lista.map(itemGrupo).join("")}</ul>` : `<div class="vacio">Nada en curso. Cargá una ficha para que aparezca el lote.</div>`}
      <p class="mut" style="font-size:12px;margin-top:12px">Cada lote está en el puesto de su última ficha. Tocá un lote para ver su recorrido.</p></div>`;
}
function panelGrupo(x) {
  const pasos = CAT.rutas[x.ruta].pasos, porP = {};
  x.regs.forEach((r) => { const p = puestoDe(r); (porP[p] = porP[p] || []).push(r); });
  const fuera = x.regs.filter((r) => !pasos.includes(puestoDe(r)));
  const act = x.fin ? pasos.length : x.paso;
  return `<div class="panel-cab"><a class="volver" href="#layout">← Toda la planta</a><h3 class="mono" style="font-family:var(--cond)">${esc(x.id)}</h3>
    <span class="chip linea" style="--c:${LIN[x.linea][1]}">${esc(LIN[x.linea][0])}</span> <span class="subtitulo">${esc(x.tipo === "os" ? "Recarga · serie " + (x.serie || "—") : (x.modelo || "") + (x.sd != null ? ` · series ${x.sd} a ${x.sh}` : ""))} · ${x.u} u</span>
    <p style="margin:8px 0 0">${x.fin ? `<span class="pill ok">Terminado</span>` : `Está en <b>${esc(PUESTOS[x.puesto].nombre)}</b>`}${x.nc ? ` <span class="pill crit">tiene una ficha no conforme</span>` : ""}</p>
    <div class="filtros" style="margin-top:8px"><a class="btn chico" href="#" data-q="${esc(x.id)}">Ver en Trazabilidad</a></div></div>
    <div class="panel-cuerpo"><ol class="pasos">${pasos.map((id, i) => {
      const rs = porP[id] || [], P = PUESTOS[id], deb = (FICHAS_DE[id] || []).length && i < act && !rs.length;
      return `<li class="${i < act ? "hecho" : i === act ? "actual" : ""}"><span class="n">${i + 1}</span><span><b>${esc(P.nombre)}</b>${rs.map((r) => `<br><a href="#" data-q="${esc(r.id)}" class="mono">${esc(r.id)}</a> <span class="pill ${r.res === "Conforme" ? "ok" : "crit"}">${esc(r.res)}</span> <span class="mut">${esc(r.t.slice(5))}</span>`).join("")}
        ${deb ? `<br><span class="pill warn">sin ficha ${esc(FICHAS_DE[id].join("/"))}</span>` : ""}</span></li>`; }).join("")}</ol>
      ${fuera.length ? h4("Fichas en ramas del recorrido") + fuera.map((r) => `<p class="renglon"><span><span class="mono">${esc(r.id)}</span> · ${esc((PUESTOS[puestoDe(r)] || {}).nombre || "")}</span><span class="pill ${r.res === "Conforme" ? "ok" : "crit"}">${esc(r.res)}</span></p>`).join("") : ""}</div>`;
}

// ---------------------------------------------------------------- dashboard
// Como el de la app de gestión: indicadores, mapa de flujo (qué hay en cada etapa según la última ficha de cada lote),
// entradas y salidas de los últimos 14 días, lotes en curso, stock de MP, PT y la actividad de las fichas.
const ETAPAS = {
  MAN: ["FAB-02", "FAB-03", "FAB-05", "FAB-06", "FAB-07", "FAB-08", "FAB-09", "FAB-10"],
  CAR: ["FAB-02", "FAB-03", "FAB-04", "FAB-05", "FAB-07", "FAB-09", "FAB-10"],
  REC: ["REC-02", "REC-03"],
};
const CORTOS = { "FAB-02": "Marcado", "FAB-03": "Sold. longitudinal", "FAB-04": "Sold. de cúpula", "FAB-05": "Sold. circunferencial", "FAB-06": "Espesor",
  "FAB-07": "Prueba hidráulica", "FAB-08": "Defectos", "FAB-09": "Pintado", "FAB-10": "Pérdidas", "REC-02": "Inspección interior", "REC-03": "Pérdidas" };
const DASH = { lin: "MAN" };
const ultimaFicha = (x) => x.regs.filter((r) => puestoDe(r) === x.puesto).pop() || x.ultima;
function carrilFlujo(l, vivos) {
  const val = Object.fromEntries(ETAPAS[l].map((f) => [f, 0])), deL = vivos.filter((x) => x.linea === l);
  deL.forEach((x) => { const f = ultimaFicha(x).f; if (f in val) val[f] += x.u; });
  const mx = Math.max(1, ...Object.values(val)), tot = deL.reduce((a, x) => a + x.u, 0);
  const con = `<span class="conector" aria-hidden="true"><svg viewBox="0 0 10 14"><path d="M1 0l8 7-8 7z"/></svg></span>`;
  return `<div class="carril"><div class="carril-nombre" style="--c:${LIN[l][1]}"><b>${LIN[l][0]}</b><span>${nf(tot)} ${l === "REC" ? "equipos" : "unidades"}</span></div>
    <div class="etapas">${ETAPAS[l].map((f) => { const p = PUESTO_FICHA[f][l === "CAR" && PUESTO_FICHA[f].length > 1 ? 1 : 0];
      return `<a class="etapa ${val[f] ? "" : "vacia"}" style="--c:${LIN[l][1]}" href="#layout?puesto=${p}" title="${f} · ${esc(FORM[f].nombre)}"><span class="nom">${CORTOS[f]}</span><span class="n">${nf(val[f])}</span><span class="etb"><i style="width:${val[f] / mx * 100}%"></i></span></a>`; }).join(con)}</div></div>`;
}
// Entradas: unidades que empiezan (marcado, inspección de la recarga, recepción de revendidos); salidas: liberadas a PT,
// recargas despachadas y despachos de PT.
function serieDias(l) {
  const dias = Array.from({ length: 14 }, (_, i) => new Date(Date.now() - (13 - i) * 864e5).toISOString().slice(0, 10));
  const e = Object.fromEntries(dias.map((d) => [d, 0])), s = Object.fromEntries(dias.map((d) => [d, 0]));
  const u = (r) => r.v.sd != null && r.v.sh != null ? r.v.sh - r.v.sd + 1 : +r.v.cant || 1;
  S.regs.forEach((r) => {
    const d = r.t.slice(0, 10); if (!(d in e)) return;
    const lin = r.f.startsWith("REC") ? "REC" : r.f === "DES" ? (/^Carro/.test(r.v.prod || "") ? "CAR" : "MAN") : esCarro(r) ? "CAR" : "MAN";
    if (lin !== l) return;
    if (["FAB-02", "REC-02"].includes(r.f)) e[d] += u(r);
    if ((r.f === "FAB-11" && r.res === "Conforme") || r.f === "REC-04" || r.f === "DES") s[d] += u(r);
  });
  return { dias, e, s };
}
function grafico(l) {
  const { dias, e, s } = serieDias(l), W = 640, H = 220, pl = 34, pb = 26, mx = Math.max(4, ...dias.map((d) => Math.max(e[d], s[d])));
  const paso = Math.pow(10, Math.floor(Math.log10(mx))), tope = Math.ceil(mx / paso) * paso, cw = (W - pl) / dias.length, bw = Math.min(16, cw / 2 - 3);
  const y = (v) => H - pb - v / tope * (H - pb - 10);
  const grilla = [0, 0.25, 0.5, 0.75, 1].map((k) => `<line class="g" x1="${pl}" x2="${W}" y1="${y(tope * k)}" y2="${y(tope * k)}"/><text class="t" x="${pl - 6}" y="${y(tope * k) + 4}" text-anchor="end">${nf(tope * k)}</text>`).join("");
  const DS = ["D", "L", "M", "M", "J", "V", "S"];
  const barras = dias.map((d, i) => { const x = pl + i * cw + cw / 2, f = new Date(d + "T12:00"), fin = [0, 6].includes(f.getDay());
    return `${e[d] ? `<rect class="be" x="${x - bw - 1}" y="${y(e[d])}" width="${bw}" height="${H - pb - y(e[d])}"><title>${fecha(d)} · entraron ${e[d]}</title></rect>` : ""}
      ${s[d] ? `<rect class="bs" x="${x + 1}" y="${y(s[d])}" width="${bw}" height="${H - pb - y(s[d])}"><title>${fecha(d)} · salieron ${s[d]}</title></rect>` : ""}
      <text class="t ${fin ? "fin" : ""}" x="${x}" y="${H - 8}" text-anchor="middle">${DS[f.getDay()]} ${f.getDate()}</text>`; }).join("");
  const te = dias.reduce((a, d) => a + e[d], 0), ts = dias.reduce((a, d) => a + s[d], 0);
  return `<div class="totales" style="--c-e:${LIN[l][1]}"><span><b class="num">${nf(te)}</b>entraron</span><span><b class="num">${nf(ts)}</b>salieron</span>
    <span class="leyenda" style="margin-left:auto"><span><i style="background:var(--c-e)"></i>Entradas</span><span><i style="background:var(--c-s)"></i>Salidas</span></span></div>
    <svg class="grafico" viewBox="0 0 ${W} ${H}" role="img" aria-label="Entradas y salidas diarias de ${LIN[l][0]}" style="--c-e:${LIN[l][1]}">${grilla}<line class="eje" x1="${pl}" x2="${W}" y1="${H - pb}" y2="${H - pb}"/>${barras}</svg>`;
}
function vDashboard() {
  const gs = grupos(), vivos = gs.filter((x) => !x.fin), est = D.mp.map(estado), cuenta = (k) => est.filter((e) => e === k).length;
  const uL = (l) => vivos.filter((x) => x.linea === l).reduce((a, x) => a + x.u, 0), nL = (l) => vivos.filter((x) => x.linea === l).length;
  const nc = S.regs.filter((r) => r.res === "No conforme" && r.t >= new Date(Date.now() - 7 * 864e5).toISOString().slice(0, 10)).length;
  const sobre = D.mp.filter((m) => S.stock[m.cod] && S.stock[m.cod].u > m.ss).length;
  const ptU = Object.values(S.pallets).reduce((a, p) => a + (+p.cant || 0), 0), despHoy = S.regs.filter((r) => r.f === "DES" && r.t.startsWith(hoy())).reduce((a, r) => a + (+r.v.cant || 0), 0);
  const ind = (t, v, sub, c, h) => `<a class="indicador" style="--c:${c}" href="${h}"><span class="et">${t}</span><span class="valor num">${v}</span><span class="sub">${sub}</span></a>`;
  const pedir = D.mp.filter((m) => ["crit", "pedir"].includes(estado(m))).sort((a, b) => (S.stock[a.cod].u / (a.pp || 1)) - (S.stock[b.cod].u / (b.pp || 1))).slice(0, 8);
  const ptProd = D.pt.map((p) => [p.prod, Object.values(S.pallets).filter((x) => x.prod === p.prod).reduce((a, x) => a + (+x.cant || 0), 0), p.max]).filter(([, u]) => u);
  const act = S.regs.slice().sort((a, b) => b.t.localeCompare(a.t)).slice(0, 9);
  const linR = (r) => r.f.startsWith("REC") ? "REC" : r.f === "REV-01" || r.f === "DES" ? "PT" : r.f === "FAB-01" ? "MP" : esCarro(r) ? "CAR" : "MAN";
  return `${bandaEjemplo()}<div class="cab"><div><h1>Trazabilidad de planta</h1><p>Kanban de almacenes, fichas de control y búsqueda por el número grabado. Sin QR.</p></div>
    <div class="filtros"><a class="btn" href="#marcado">Identificación sin QR</a><a class="btn" href="#revendidos">Revendidos</a></div></div>
    <div class="indicadores">
      ${ind("Manuales en proceso", `${nf(uL("MAN"))}<small>u</small>`, `en ${nL("MAN")} lotes`, "var(--man)", "#layout?linea=MAN")}
      ${ind("Carros en proceso", nf(uL("CAR")), `en ${nL("CAR")} lotes`, "var(--car)", "#layout?linea=CAR")}
      ${ind("Recargas en planta", nf(uL("REC")), "órdenes de servicio abiertas", "var(--rec)", "#layout?linea=REC")}
      ${ind("MP para pedir", nf(cuenta("crit") + cuenta("pedir")), `${cuenta("crit")} bajo seguridad · ${cuenta("ped")} pedidas`, "var(--mp)", "#mp")}
      ${ind("Fichas no conformes", nf(nc), "últimos 7 días", "var(--critical)", "#formularios")}</div>
    <section class="panel mapa"><header><div><h2>Mapa de flujo</h2><span class="mut" style="font-size:13px">Qué hay ahora en cada etapa, según la última ficha de cada lote. Tocá una etapa para verla en el layout.</span></div></header>
      <div class="cuerpo mapa-cuerpo">
        <a class="extremo" href="#almacen"><span class="ez">Abajo · ingreso</span><h4>Materia prima</h4><span class="grande num">${sobre}<small> / ${D.mp.length}</small></span><span class="mut">MP sobre la seguridad</span>
          <span class="grande num" style="font-size:24px">${cuenta("crit") + cuenta("pedir")}</span><span class="mut">para pedir · ${cuenta("ped")} pedidos en camino</span></a>
        <div class="carriles">${carrilFlujo("MAN", vivos)}${carrilFlujo("CAR", vivos)}${carrilFlujo("REC", vivos)}</div>
        <a class="extremo" href="#pt"><span class="ez">Arriba · salida</span><h4>Producto terminado</h4><span class="grande num">${nf(ptU)}</span><span class="mut">unidades en el PT</span>
          <span class="grande num" style="font-size:24px">${nf(despHoy)}</span><span class="mut">despachadas hoy</span></a></div></section>
    <div class="grid">
      <section class="panel c8"><header><div><h2>Entradas y salidas</h2><span class="mut" style="font-size:13px">Unidades por día, últimos 14 días, según las fichas.</span></div>
        <div class="segmentado" id="seg-dash">${["REC", "MAN", "CAR"].map((l) => `<button data-dl="${l}" aria-pressed="${DASH.lin === l}">${LIN[l][0]}</button>`).join("")}</div></header>
        <div class="cuerpo" id="graf">${grafico(DASH.lin)}</div></section>
      <section class="panel c4"><header><div><h2>Lotes en curso</h2><span class="mut" style="font-size:13px">Dónde está cada uno: su última ficha.</span></div></header>
        <div class="cuerpo"><ul class="lista">${vivos.sort((a, b) => b.ultima.t.localeCompare(a.ultima.t)).slice(0, 7).map(itemGrupo).join("") || `<div class="vacio">Nada en curso.</div>`}</ul></div></section>
      <section class="panel c4"><header><div><h2>Stock de materia prima</h2><span class="mut" style="font-size:13px"><b class="num" style="font-size:22px;color:var(--text)">${sobre}</b> de ${D.mp.length} sobre la seguridad</span></div></header>
        <div class="cuerpo">${pedir.length ? `<p class="mut" style="font-size:12.5px;margin:0 0 4px">Para pedir (la marca es el punto de pedido):</p>${pedir.map((m) => { const s = S.stock[m.cod].u, mx = Math.max(m.max, s) || 1;
          return `<button class="fbar" data-mp="${esc(m.cod)}"><span><span class="mono">${esc(m.cod)}</span> ${esc(m.mat.replace(/\s*\(.*\)$/, ""))}</span><span class="val">${nf(s)} / ${nf(m.pp)} ${esc(m.um)} · <b>${txtD(diasDe(m, s))}</b></span>
            <span class="pista"><i style="width:${Math.min(100, s / mx * 100)}%;background:${estado(m) === "crit" ? "var(--critical)" : "var(--warn)"}"></i><u style="left:${Math.min(99, m.pp / mx * 100)}%"></u></span></button>`; }).join("")}`
          : `<div class="vacio">${Object.keys(S.stock).length ? "Ningún código en el punto de pedido." : "Todavía no hay conteos: cargá la planilla del almacén."}</div>`}</div></section>
      <section class="panel c4"><header><div><h2>Producto terminado</h2><span class="mut" style="font-size:13px">Unidades en el PT contra el máximo (Stock_PT, col. J).</span></div></header>
        <div class="cuerpo">${ptProd.map(([p, u, mx]) => `<a class="fbar" href="#pt" style="--c:${/^Carro|de carro/.test(p) ? "var(--car)" : "var(--man)"}"><span>${esc(p)}</span><span class="val">${nf(u)} u · ${txtD(diasPT(u, D.pt.find((x) => x.prod === p)))}</span><span class="pista"><i style="width:${Math.min(100, u / (mx || 1) * 100)}%"></i></span></a>`).join("") || `<div class="vacio">El PT está vacío.</div>`}</div></section>
      <section class="panel c4"><header><div><h2>Actividad en los puestos</h2><span class="mut" style="font-size:13px">Últimas fichas cargadas.</span></div></header>
        <div class="cuerpo"><ul class="actividad">${act.map((r) => `<li style="--c:${LIN[linR(r)][1]}"><span class="hora num">${esc(r.t.slice(11) || r.t.slice(5, 10))}</span><span><b class="mono">${esc(r.id)}</b>${r.res === "No conforme" ? ' <span class="pill crit">NC</span>' : ""}<br>
          <span class="mut">${esc(r.f === "DES" ? "Despacho" : FORM[r.f].nombre)}${r.v.oper ? " · " + esc(r.v.oper) : ""}</span></span></li>`).join("") || `<div class="vacio">Sin fichas todavía.</div>`}</ul></div></section>
      <details class="fuente c12"><summary>De dónde salen los números</summary>${esc(D.fuente.mp)} · ${esc(D.fuente.pt)} · ${esc(D.fuente.bal)} · plano rev ${esc(D.layout.revision)} y puestos de la app de gestión interna.
        Lo que se carga queda guardado en este navegador. ${S.demo ? "" : `<button class="btn chico" data-a="ejemplo">Ver con datos de ejemplo</button>`} <button class="btn chico" data-a="borrar">Borrar todo lo cargado</button></details></div>`;
}

// ---------------------------------------------------------------- datos de ejemplo
// Para ver la app funcionando: stock entre la seguridad y el máximo reales de cada MP, pallets del PT con las unidades
// por pallet reales y un lote recorrido por sus fichas. Todo queda marcado como ejemplo y se borra con «Empezar en limpio».
function azar(sem) { return () => { sem |= 0; sem = (sem + 0x6D2B79F5) | 0; let t = Math.imul(sem ^ (sem >>> 15), 1 | sem); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function ejemplo() {
  const E = VACIO(), r = azar(2035), ent = (um) => ["hoja", "u", "barra"].includes(um);
  E.demo = true;
  const dMenos = (d) => new Date(Date.now() - d * 864e5).toISOString().slice(0, 10);
  const hMenos = (h) => new Date(Date.now() - h * 36e5).toISOString().slice(0, 16).replace("T", " ");
  const nx = (k) => (E.n[k] = (E.n[k] || 0) + 1);
  D.mp.forEach((m) => {
    const tope = Math.min(m.pp, m.max), x = r();
    let u = x < 0.03 ? m.ss * (0.4 + 0.5 * r()) : x < 0.16 ? m.ss + (tope - m.ss) * r() : m.pp >= m.max ? m.ss + (m.max - m.ss) * r() : tope + (m.max - tope) * r();
    u = ent(m.um) ? Math.round(u) : Math.round(u * 10) / 10;
    E.stock[m.cod] = { u, src: "Planilla de conteo (ejemplo)", t: hMenos(20 + r() * 30) };
    if (u <= m.pp && u > m.ss && r() < 0.45) E.pedidos[m.cod] = { cant: bultos(m, m.max - u) * m.cont, t: hMenos(24 + r() * 96) };
  });
  // PT: la mitad de los pallets del máximo de cada producto, en el rack (los 10 kg en caja en el nivel 1)
  const rack = ZONAS[0].slots.filter((q) => !q.includes("-1")), piso1 = ZONAS[0].slots.filter((q) => q.includes("-1"));
  let serie = 4000;
  const op = (f) => "OP " + f.slice(2, 4) + "-" + f.slice(5, 7) + "-" + f.slice(8, 10);
  const pallet = (slot, prod, cant, ffab, series) => { E.pallets[slot] = { id: "PAL-" + String(nx("PAL")).padStart(4, "0"), prod, cant, lote: op(ffab), series, ffab, quien: "Calidad", t: hMenos(r() * 300), demo: true }; };
  D.pt.filter((p) => !/^Carro/.test(p.prod)).forEach((p) => {
    const n = Math.max(1, Math.round((+p.pallets || 1) * 0.5));
    for (let k = 0; k < n; k++) {
      const lista = /10 kg \(en caja\)/.test(p.prod) || !rack.length ? piso1 : rack, slot = lista.shift(); if (!slot) break;
      const ffab = dMenos(3 + Math.floor(r() * 80)), cant = p.porp;
      pallet(slot, p.prod, cant, ffab, `${serie}-${serie + cant - 1}`); serie += cant;
      const i1 = piso1.indexOf(slot); if (i1 >= 0) piso1.splice(i1, 1);
    }
  });
  Object.entries(D.carros).forEach(([mod, n]) => {
    for (let k = 1; k <= Math.round(n * 0.6); k++) pallet(`C${mod.replace(" kg", "")}-${String(k).padStart(2, "0")}`, `Carro ${mod} terminado`, 1, dMenos(1 + Math.floor(r() * 7)), String(serie++));
  });
  ["Nuevo 1 kg (en caja)", "Cilindro 1 kg (manuales)", "Nuevo 5 kg (en caja)"].forEach((prod, k) => {
    const p = D.pt.find((x) => x.prod === prod); pallet(`AN-${String(k + 1).padStart(2, "0")}`, prod, p.porp, dMenos(20 + k * 6), `${serie}-${serie + p.porp - 1}`); serie += p.porp;
  });
  RV.slice(0, 6).forEach((m, k) => {
    const cant = 6 + Math.floor(r() * 18), ser = Array.from({ length: 3 }, (_, j) => `EJ-${m.cod.slice(3, 6)}-${7700 + k * 10 + j}`);
    pallet(`RV-${String(k + 1).padStart(2, "0")}`, m.mat, cant, dMenos(30 + Math.floor(r() * 120)), ser.join(", ") + "…");
    ser.forEach((q) => E.rev.push({ serie: q, cod: m.cod, fab: "Fabricante (ejemplo)", anio: 2026, slot: `RV-${String(k + 1).padStart(2, "0")}`, estado: "En PT", t: hMenos(200) }));
  });
  for (let k = 1; k <= 5; k++) pallet(`SP-${String(k).padStart(2, "0")}`, "Sustituto propio", 1, dMenos(200), String(serie++));
  for (let k = 1; k <= 9; k++) pallet(`SC-${String(k).padStart(2, "0")}`, "Sustituto comprado", 1, dMenos(260), "—");
  for (let k = 1; k <= 18; k++) pallet(`EP-${String(k).padStart(2, "0")}`, "Recipiente de carro (a pintar)", 1, dMenos(1), String(serie++));
  for (let k = 1; k <= 11; k++) pallet(`PI-${String(k).padStart(2, "0")}`, "Recipiente de carro (pintado)", 1, dMenos(4), String(serie++));
  // un lote recorrido por sus fichas, un lote con PH no conforme, una recarga y una recepción de revendidos
  const reg = (fid, v, h) => {
    const fm = FORM[fid], val = {};
    fm.campos.forEach((c) => { val[c.k] = c.tipo === "si" ? true : c.tipo === "lect" ? [] : null; });
    Object.assign(val, { fecha: dMenos(h / 24), oper: "Operario (ejemplo)" }, v);
    const mal = evaluar(fm, val);
    E.regs.push({ id: `${fid}-${String(nx(fid)).padStart(4, "0")}`, f: fid, t: hMenos(h), v: val, res: mal.length ? "No conforme" : "Conforme", mal: mal.map((c) => c.l), demo: true });
  };
  const A = { modelo: "ABC 5 kg", lote: "OP 26-10-08", sd: 5480, sh: 5527 };
  reg("FAB-01", { mp: "MP-03", cant: 24, remito: "R-0001-00452", colada: "C-45871", esp: 1.61 }, 120);
  reg("FAB-02", { ...A, anio: 26, colada: "C-45871" }, 96);
  reg("FAB-03", { ...A, calif: "ISO 9606-1 n° 118", wps: "WPS-MAG-05", proc: "MAG 135 (2,5 a 10 kg y carros)", alambre: "B-2210", gas: "AL-7781", amp: 165, volt: 19 }, 90);
  reg("FAB-04", { ...A, calif: "ISO 9606-1 n° 121", wps: "WPS-MAG-07", pieza: "Cuello a la cúpula (manuales)", alambre: "B-2210", gas: "AL-7781", amp: 140, volt: 18 }, 88);
  reg("FAB-05", { ...A, calif: "ISO 9606-1 n° 118", wps: "WPS-MAG-06", alambre: "B-2210", gas: "AL-7781", amp: 170, volt: 20 }, 80);
  reg("FAB-06", { modelo: "ABC 5 kg", lote: "OP 26-10-08", instr: INSTR.esp[0], serie: 5500, lect: [1.62, 1.61, 1.63, 1.60] }, 78);
  reg("FAB-07", { ...A, banco: INSTR.ph[0], contraste: 9, p: 3.5, seg: 60, et: 120, ep: 6, rot: 9.2 }, 74);
  reg("FAB-08", { ...A, def: "Salpicadura", defser: "5491 salpicadura", acc: "Corrección mecánica", reph: "No corresponde" }, 60);
  reg("FAB-09", { ...A, polvo: "SP-03105", hs: 2, hr: 58, instr: INSTR.pel[0], pel: [72, 78, 81, 69, 75], adh: "0", pintor: "En planta (manuales)" }, 50);
  reg("FAB-10", { ...A, met: "Inmersión" }, 30);
  reg("FAB-11", { prod: "Nuevo 5 kg (en caja)", cant: 48, lote: "OP 26-10-08", series: "5480-5527", ffab: dMenos(1), slot: "R15-2A" }, 24);
  pallet("R15-2A", "Nuevo 5 kg (en caja)", 48, dMenos(1), "5480-5527"); E.pallets["R15-2A"].lote = "OP 26-10-08";
  const B2 = { modelo: "ABC 1 kg", lote: "OP 26-10-09", sd: 6100, sh: 6459 };
  reg("FAB-02", { ...B2, anio: 26, colada: "C-45902" }, 30);
  reg("FAB-03", { ...B2, calif: "ISO 9606-1 n° 130", wps: "WPS-TIG-01", proc: "TIG 141 (1 kg)", alambre: "—", gas: "AR-1102", amp: 95, volt: 11 }, 26);
  reg("FAB-07", { ...B2, banco: INSTR.ph[1], contraste: 9, p: 3.5, seg: 45, rech: "6123" }, 6);
  reg("REC-02", { os: "OS-1520", serie: "A-114502", fab: "Fabricante del cliente", agente: "ABC", video: "VS-1", corr: "No", dano: "No" }, 10);
  reg("REC-03", { os: "OS-1520", serie: "A-114502", met: "Detector" }, 8);
  reg("REC-04", { os: "OS-1520", serie: "A-114502", prec: "PR-88213", jaula: "J-03", remito: "R-0002-01177" }, 7);
  reg("REV-01", { mp: "RV-CO2_5kg", fab: "Fabricante (ejemplo)", seriesRv: E.rev.filter((x) => x.cod === "RV-CO2_5kg").map((x) => x.serie).join("\n"), anio: 2026, sello: "IRAM-EJ", remito: "R-0001-00398", slot: "RV-06" }, 300);
  // Dos semanas de planta para el mapa de flujo y el gráfico: un lote de manuales por día hábil y uno de carros cada tres,
  // que recorren sus fichas y se despachan, y cinco recargas por día. Los últimos días quedan a mitad de camino.
  const habiles = [];
  for (let d = 13; d >= 0; d--) if (![0, 6].includes(new Date(Date.now() - d * 864e5).getDay())) habiles.push(d);
  const MAN_F = ["FAB-02", "FAB-03", "FAB-04", "FAB-05", "FAB-06", "FAB-07", "FAB-08", "FAB-09", "FAB-10", "FAB-11"];
  const CAR_F = ["FAB-02", "FAB-03", "FAB-04", "FAB-05", "FAB-07", "FAB-09", "FAB-10", "FAB-11"];
  const sold = { calif: "ISO 9606-1 n° 118", alambre: "B-2210", gas: "AL-7781" };
  const valores = (f, mo, x) => {
    const M = MOD(mo), car = M.car;
    return ({
      "FAB-02": { anio: 26, colada: "C-4" + (5900 + x.i) },
      "FAB-03": { ...sold, wps: mo === "ABC 1 kg" ? "WPS-TIG-01" : "WPS-MAG-05", proc: mo === "ABC 1 kg" ? "TIG 141 (1 kg)" : "MAG 135 (2,5 a 10 kg y carros)", amp: 165, volt: 19 },
      "FAB-04": { ...sold, wps: "WPS-MAG-07", pieza: car ? "Cupla en la cúpula (carros)" : "Cuello a la cúpula (manuales)", amp: 140, volt: 18 },
      "FAB-05": { ...sold, wps: "WPS-MAG-06", amp: 170, volt: 20 },
      "FAB-06": { instr: INSTR.esp[0], serie: x.sd + 3, lect: [M.t + 0.02, M.t + 0.01, M.t + 0.03, M.t + 0.01] },
      "FAB-07": { banco: INSTR.ph[x.i % 2], contraste: 1 + x.i % 12, p: M.pe, seg: 60, et: 120, ep: 6, rot: 2 * M.pe + 0.8 },
      "FAB-08": { def: "Sin defectos", acc: "Ninguna", reph: "No corresponde" },
      "FAB-09": { polvo: "SP-03105", hs: 2, hr: 58, instr: INSTR.pel[0], pel: [72, 78, 81, 69, 75], adh: "0", pintor: car ? "Pintor externo (carros, recepción de pintados)" : "En planta (manuales)" },
      "FAB-10": { met: "Inmersión" },
    })[f] || {};
  };
  const prodDe = (mo) => MOD(mo).car ? `Carro ${mo.replace("Carro ABC ", "")} terminado` : (D.pt.find((p) => p.prod.startsWith("Nuevo " + mo.replace("ABC ", "") + " ")) || D.pt[0]).prod;
  const cadena = (mo, lote, sd, n, h0, hasta, i) => {
    const fs = MOD(mo).car ? CAR_F : MAN_F, x = { sd, i };
    fs.slice(0, hasta).forEach((f, k) => {
      const h = h0 - k * (MOD(mo).car ? 4 : 2.5) - (MOD(mo).car && f === "FAB-09" ? 48 : 0);
      if (f === "FAB-11") reg(f, { prod: prodDe(mo), cant: n, lote, series: `${sd}-${sd + n - 1}`, ffab: dMenos(h / 24), slot: "—" }, h);
      else reg(f, { modelo: mo, lote, sd, sh: sd + n - 1, ...valores(f, mo, x) }, h);
    });
    if (hasta >= fs.length) {
      const h = h0 - fs.length * 3 - 20, prod = prodDe(mo);
      E.regs.push({ id: "DES-" + String(nx("DES")).padStart(4, "0"), f: "DES", t: hMenos(h), res: "Despachado", demo: true,
        v: { remito: "R-0001-0" + (700 + i), veh: (VEH(prod) || "Master").split(" · ")[0], pallet: "—", prod, cant: n, series: `${sd}-${sd + n - 1}`, lote, slot: "—" } });
    }
  };
  const MODS_M = ["ABC 5 kg", "ABC 1 kg", "ABC 2,5 kg", "ABC 10 kg"], MODS_C = ["Carro ABC 25 kg", "Carro ABC 50 kg", "Carro ABC 70 kg", "Carro ABC 100 kg"];
  let sM = 20000, sC = 30000, os = 1400;
  const ahoraH = new Date().getUTCHours() + new Date().getUTCMinutes() / 60;
  habiles.forEach((d, i) => {
    const h0 = d * 24 + ahoraH - 7.5, viejo = d >= 4;   // arranca 7:30 de ese día
    const hastaM = viejo ? 99 : { 3: 8, 2: 6, 1: 4, 0: 2 }[d] || 2;
    if (h0 > 0) { cadena(MODS_M[i % 4], op(dMenos(d)), sM, 48, h0, hastaM, i); sM += 48; }
    if (i % 3 === 0 && h0 > 0) { cadena(MODS_C[(i / 3) % 4], op(dMenos(d)) + " C", sC, 6, h0 - 1, viejo ? 99 : d >= 2 ? 5 : 2, i); sC += 6; }
    for (let k = 0; k < 5; k++) {
      const hr = h0 - 0.5 - k * 1.2, o = "OS-" + os++, serie = "A-" + (114000 + i * 10 + k);
      if (hr <= 0) continue;
      const v = { os: o, serie, fab: "Fabricante del cliente", agente: "ABC", video: "VS-1", corr: "No", dano: "No" };
      reg("REC-02", v, hr);
      if (d > 0 || k < 3) reg("REC-03", { os: o, serie, met: "Detector" }, hr - 2.5);
      if (d > 0 || k < 1) reg("REC-04", { os: o, serie, prec: "PR-" + (88300 + i * 10 + k), jaula: "J-0" + (1 + k % 4), remito: "R-0002-0" + (1200 + i * 10 + k) }, hr - 4);
    }
  });
  E.regs.sort((a, b) => a.t.localeCompare(b.t));
  return E;
}
function bandaEjemplo() {
  return S.demo ? `<div class="banda-ejemplo"><b>Datos de ejemplo</b><span>para ver cómo funciona. Los parámetros (seguridad, punto de pedido, máximos, lugares) son los reales.</span><button class="btn chico" data-a="limpio">Empezar en limpio</button></div>` : "";
}

// ---------------------------------------------------------------- shell
const MENU = [["dashboard", "Dashboard"], ["mp", "Kanban MP"], ["semaforo", "Semáforo"], ["almacen", "Almacén"], ["pt", "Kanban PT"], ["despacho", "Despacho"], ["formularios", "Fichas"], ["layout", "Layout"], ["traza", "Trazabilidad"]];
function menu(actual) {
  const al = D.mp.filter((m) => ["crit", "pedir"].includes(estado(m))).length;
  const cuenta = { mp: al ? `<b class="alerta">${al}</b>` : "", pt: Object.keys(S.pallets).length ? `<b>${Object.keys(S.pallets).length}</b>` : "" };
  const activo = (k) => actual === k || (k === "formularios" && actual.startsWith("f-")) || (k === "traza" && ["marcado", "revendidos"].includes(actual));
  $("#pestanas").innerHTML = MENU.map(([k, t]) => `<a href="#${k}" ${activo(k) ? 'aria-current="page"' : ""}>${t}${cuenta[k] || ""}</a>`).join("");
  $("#menu-nuevo").innerHTML = [["fab", "Fabricación"], ["rec", "Recargas"], ["rev", "Revendidos"]].map(([l, t]) => `<h4>${t}</h4>` +
    FORMS.filter((x) => x.linea === l).map((x) => `<a href="#f-${x.id}"><b>${x.id}</b>${esc(x.nombre)}</a>`).join("")).join("");
}
let PARAMS = new URLSearchParams();
function pintar() {
  let [h, qs] = ((location.hash || "#dashboard").slice(1) || "dashboard").split("?");
  if (h === "inicio") h = "dashboard";
  PARAMS = new URLSearchParams(qs || "");
  menu(h);
  // el layout no se redibuja entero si ya está en pantalla: así no se pierde el zoom
  if (h === "layout" && $("#plano")) { actualizarLayout(); return; }
  const V = { dashboard: vDashboard, mp: vMP, semaforo: vSemaforo, almacen: vAlmacen, pt: vPT, despacho: vDespacho, formularios: vFormularios, traza: vTraza, revendidos: vRevendidos, marcado: vMarcado, layout: vLayout };
  $("#vista").innerHTML = h.startsWith("f-") ? vForm(h.slice(2)) : (V[h] || vDashboard)();
  if (h.startsWith("f-")) armarForm(h.slice(2));
  if (h === "layout") { prepararZoom(); actualizarLayout(); }
  if (h === "despacho") armarDespacho();
  const fA = $("#fAlm"), fL = $("#fLin"), fQ = $("#fQ");
  if (fA) { fA.onchange = () => { F.alm = fA.value; pintar(); }; fL.onchange = () => { F.lin = fL.value; pintar(); }; fQ.oninput = () => { F.q = fQ.value; const p = fQ.selectionStart; pintar(); const n = $("#fQ"); n.focus(); n.setSelectionRange(p, p); }; }
  const fb = $("#fBus");
  if (fb) fb.onsubmit = (ev) => { ev.preventDefault(); Q = $("#bq").value; pintar(); };
}
$("#busqueda-global").addEventListener("submit", (ev) => { ev.preventDefault(); Q = $("#q-global").value; if (location.hash === "#traza") pintar(); else location.hash = "traza"; });
$("#btn-nuevo").addEventListener("click", (ev) => { ev.stopPropagation(); const m = $("#menu-nuevo"); m.hidden = !m.hidden; $("#btn-nuevo").setAttribute("aria-expanded", String(!m.hidden)); });
function reloj() { const d = new Date(); $("#reloj").textContent = d.toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long" }) + " · " + d.toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" }); }
reloj(); setInterval(reloj, 30000);
function abrir(titulo, html) {
  $("#capa").innerHTML = `<div class="velo" data-cerrar-velo><div class="dialogo" role="dialog" aria-modal="true" aria-label="${esc(titulo.replace(/<[^>]+>/g, ""))}">
    <header><h2>${titulo}</h2><button class="cerrar" data-a="cerrar" aria-label="Cerrar">×</button></header><div class="cuerpo">${html}</div></div></div>`;
}
const cerrar = () => { $("#capa").innerHTML = ""; };
let tt;
function toast(t) { clearTimeout(tt); $("#toasts").innerHTML = `<div class="toast">${esc(t)}</div>`; tt = setTimeout(() => { $("#toasts").innerHTML = ""; }, 3800); }
document.addEventListener("click", (ev) => {
  const t = ev.target;
  if (!t.closest(".menu-nuevo")) { $("#menu-nuevo").hidden = true; $("#btn-nuevo").setAttribute("aria-expanded", "false"); }
  if (t.closest("#plano") && LAY.arrastro && Date.now() - LAY.arrastro < 250) return;
  const pu = t.closest("[data-puesto]"); if (pu) { location.hash = "layout?puesto=" + pu.dataset.puesto; return; }
  const sec = t.closest("[data-sector]");
  if (sec && $("#plano")) { const p = Object.values(PUESTOS).find((x) => x.sector === sec.dataset.sector); if (p) location.hash = "layout?puesto=" + p.id; return; }
  const ir = t.closest("[data-ir]"); if (ir) { location.hash = "layout?" + ir.dataset.ir; return; }
  const dq = t.closest("[data-q]"); if (dq) { ev.preventDefault(); Q = dq.dataset.q; if (location.hash === "#traza") pintar(); else location.hash = "traza"; return; }
  const sa = t.closest("[data-salto]"); if (sa) { const el = document.getElementById(sa.dataset.salto); if (el) el.scrollIntoView({ behavior: "smooth", block: "start" }); return; }
  const dl = t.closest("[data-dl]"); if (dl) { DASH.lin = dl.dataset.dl; $("#graf").innerHTML = grafico(DASH.lin); $$("#seg-dash button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.dl === DASH.lin))); return; }
  if (t.matches("[data-cerrar-velo]")) { cerrar(); return; }
  if (t.closest("[data-cerrar]")) cerrar();
  const mp = t.closest("[data-mp]"); if (mp) { detalleMP(mp.dataset.mp); return; }
  const sl = t.closest("[data-slot]"); if (sl && !t.closest(".dialogo")) { dlgSlot(sl.dataset.slot); return; }
  const a = t.closest("[data-a]"); if (!a) return;
  const k = a.dataset.a, id = a.dataset.id;
  if (k === "cerrar") cerrar();
  else if (k === "conteo") dlgConteo(id);
  else if (k === "planilla") dlgPlanilla();
  else if (k === "bajarPlanilla") bajarPlanilla(id || null);
  else if (k === "aplicarPlanilla") aplicarPlanilla();
  else if (k === "leerPegado") { const tx = $("#plPeg").value; if (tx.trim()) vistaPlanilla(leerFilas(tx.split(/\r?\n/).map(partirLinea)), "pegado desde Excel"); }
  else if (k === "pedir") { S.pedidos[id] = { cant: +a.dataset.cant, t: ahora() }; guardar(); cerrar(); pintar(); toast(`Pedido emitido a ${MP[id].prov}`); }
  else if (k === "anularPed") { delete S.pedidos[id]; guardar(); cerrar(); pintar(); }
  else if (k === "recibir") { cerrar(); location.hash = "f-" + (/ecargas/.test(MP[id].linea) && !/Manuales|Carros/.test(MP[id].linea) ? "REC-01" : "FAB-01"); setTimeout(() => { const s = $("#c_mp"); if (s) { s.value = id; s.dispatchEvent(new Event("change", { bubbles: true })); } }, 0); }
  else if (k === "limpio") { S = VACIO(); guardar(); pintar(); toast("Listo: sin datos de ejemplo"); }
  else if (k === "ejemplo") { S = ejemplo(); guardar(); pintar(); toast("Datos de ejemplo cargados"); }
  else if (k === "verOk") { S.verOk = true; pintar(); }
  else if (k === "arranque") { D.mp.forEach((m) => { S.stock[m.cod] = { u: m.max, src: "Conteo a mano (arranque al stock máximo)", t: ahora() }; }); guardar(); pintar(); toast("Arranque cargado: todo al stock máximo"); }
  else if (k === "borrar") { if (a.dataset.ok) { S = VACIO(); guardar(); pintar(); toast("Se borró todo lo cargado"); } else { a.dataset.ok = "1"; a.textContent = "Tocá de nuevo para confirmar"; } }
  else if (k === "csv") {
    const filas = [["registro", "formulario", "fecha_hora", "resultado", "datos"]].concat(S.regs.map((r) => [r.id, r.f, r.t, r.res, JSON.stringify(r.v)]));
    const csv = filas.map((f) => f.map((x) => `"${String(x).replace(/"/g, '""')}"`).join(";")).join("\n");
    navigator.clipboard.writeText(csv).then(() => toast(`${S.regs.length} registros copiados`)).catch(() => toast("No se pudo copiar: el navegador no lo permite"));
  }
});
document.addEventListener("change", (ev) => {
  if (ev.target.id === "plArch" && ev.target.files && ev.target.files[0]) leerArchivo(ev.target.files[0]);
});
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") cerrar(); });
window.addEventListener("hashchange", () => { cerrar(); const enLayout = location.hash.startsWith("#layout") && $("#plano"); pintar(); if (!enLayout) window.scrollTo(0, 0); });
if (!GUARDADO) S = ejemplo();
pintar();
