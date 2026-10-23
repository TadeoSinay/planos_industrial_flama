// Trazabilidad interna FLAMA (sin QR). Datos fijos en D (build.py, libros 2035 de MP, PT y balanceo); lo que pasa en
// planta (conteos, pedidos, formularios, pallets, revendidos) arranca vacío y se guarda en este navegador.
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
const CLAVE = "flama-traza-simple-v1";
const VACIO = () => ({ stock: {}, pedidos: {}, pallets: {}, regs: [], rev: [], n: {}, fotos: {}, verOk: false });
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
// Señal kanban que ve la cámara según cómo se guarda (criterio, sección 3 del Word)
const SENAL = [
  [/Apilado/, "Franja roja pintada en el poste a la altura del punto de pedido. La cámara mide el alto de la pila: si queda por debajo de la franja, pide."],
  [/Rack/, "Lugar del punto de pedido demarcado en rojo en el larguero. Abajo se usa, arriba se repone: cuando el lugar rojo queda vacío, la cámara lo ve y pide."],
  [/liviana/, "Doble cajón: el segundo cajón es el punto de pedido. Al abrirlo queda a la vista su tarjeta roja y la cámara la detecta."],
  [/Cantilever/, "Brazo del punto de pedido pintado de rojo: cuando no tiene atado, la cámara lo ve."],
  [/Jaula/, "Cilindros llenos con capuchón; la cámara cuenta capuchones contra el punto de pedido."],
  [/PT|producto/, "Lugares de reventa demarcados por modelo; el último lugar antes del punto de pedido va en rojo."],
];
const senal = (est) => (SENAL.find(([re]) => re.test(est || "")) || [0, "Señal a definir."])[1];
const ALMS = [...D.alm.filter((a) => !/producto terminado/.test(a.alm)),
  { alm: "Almacén de producto terminado", que: "Matafuegos de reventa", est: "En el almacén de PT", lug: RV.length, como: "Por modelo, en la zona de reventa del PT." }];
const camId = (alm) => "CAM-" + String(ALMS.findIndex((a) => a.alm === alm) + 1).padStart(2, "0");

// ---------------------------------------------------------------- kanban de MP
// Punto de pedido = seguridad + consumo mientras llega (Stock_MP L + K). La revisión periódica del Word de MP
// (cada «cada» días se pide hasta el máximo) sigue; el kanban avisa si entre dos revisiones se cruza el punto.
const COLS = [
  { k: "crit", t: "Bajo seguridad", c: "crit" }, { k: "pedir", t: "Pedir", c: "warn" },
  { k: "ped", t: "Pedido en camino", c: "info" }, { k: "ok", t: "Bien", c: "ok" },
  { k: "sin", t: "Sin lectura", c: "idle" }];
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
    <span class="t1"><b>${esc(m.cod)}</b><span class="mut" style="font-size:11px">${esc(m.ref)}</span></span>
    <span class="mat">${esc(m.mat.replace(/\s*\(.*\)$/, ""))}</span>${barra(m)}
    <span class="t3"><span class="num">${s ? nf(s.u, 0) : "—"} ${esc(m.um)}</span><span>pedir en ${nf(m.pp, 0)}</span></span></button>`;
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
    <p>Cada tarjeta es una MP. Se mueve sola con cada lectura de cámara, retiro o recepción.</p></div>
    <div class="filtros"><select id="fAlm" aria-label="Almacén"><option value="">Todos los almacenes</option>${almOpts}</select>
    <select id="fLin" aria-label="Línea"><option value="">Todas las líneas</option>${linOpts}</select>
    <input id="fQ" type="search" placeholder="Código, material o proveedor" value="${esc(F.q)}" aria-label="Buscar"></div></div>
    ${sinNada ? `<div class="aviso" style="margin-bottom:12px">Sin lecturas todavía. <button class="btn chico" data-a="arranque" style="margin-left:6px">Arrancar con el almacén lleno</button></div>` : ""}
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
      <dt>Seguridad</dt><dd class="num">${nf(m.ss, 1)} ${esc(m.um)} <span class="mut">Stock_MP!L${m.fila}</span></dd>
      <dt>Punto de pedido</dt><dd class="num">${nf(m.pp, 1)} ${esc(m.um)} = seguridad + ${nf(m.k, 1)} que se consumen mientras llega <span class="mut">L${m.fila} + K${m.fila}</span></dd>
      <dt>Stock máximo</dt><dd class="num">${nf(m.max, 1)} ${esc(m.um)} <span class="mut">Stock_MP!S${m.fila}</span></dd>
      <dt>Se compra</dt><dd>${esc(m.bulto)} · se pide cada ${esc(m.cada)} días hábiles · plazo ${esc(m.pmin)} a ${esc(m.pmax)} días</dd>
      <dt>Proveedor</dt><dd>${esc(m.prov)}</dd>
      <dt>Almacén</dt><dd>${esc(m.alm)} · ${esc(m.lug)} lugar(es) · ${camId(m.alm)}</dd>
      <dt>Cómo se guarda</dt><dd style="font-size:12.5px">${esc(m.guarda)}</dd>
      ${p ? `<dt>Pedido</dt><dd>${nf(p.cant, 1)} ${esc(m.um)} el ${esc(p.t)} a ${esc(m.prov)}</dd>` : ""}</dl>
    <form class="campos" id="fMov">
      <div class="campo"><label for="mvT">Movimiento</label><select id="mvT"><option value="conteo">Lectura / conteo (deja el stock en)</option>
        <option value="retiro">Retiro a la línea (resta)</option></select></div>
      <div class="campo"><label for="mvU">Cantidad (${esc(m.um)})</label><input id="mvU" type="number" step="any" min="0" required></div>
      <div class="campo"><label for="mvS">Fuente</label><select id="mvS"><option>${camId(m.alm)} (cámara)</option><option>Conteo manual</option></select></div>
      <div class="campo" style="align-self:end"><button class="btn pri" type="submit">Registrar</button></div></form>
    <div class="filtros">${p ? `<button class="btn" data-a="recibir" data-id="${esc(cod)}">Registrar la recepción (formulario FAB-01)</button>
      <button class="btn" data-a="anularPed" data-id="${esc(cod)}">Anular pedido</button>` :
      `<button class="btn" data-a="pedir" data-id="${esc(cod)}" data-cant="${sugB * m.cont}">Emitir pedido: ${nf(sugB)} × ${esc(m.bulto)} (hasta el máximo)</button>`}</div>`);
  $("#fMov").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const t = $("#mvT").value, u = parseFloat($("#mvU").value);
    if (isNaN(u)) return;
    const prev = S.stock[cod] ? S.stock[cod].u : 0;
    if (t === "retiro" && !S.stock[cod]) { toast("Primero registrá una lectura: no hay stock para descontar"); return; }
    S.stock[cod] = { u: t === "retiro" ? Math.max(0, prev - u) : u, src: $("#mvS").value, t: ahora() };
    guardar(); cerrar(); pintar(); toast(`${cod}: ${nf(S.stock[cod].u, 1)} ${m.um}`);
  });
}

// ---------------------------------------------------------------- cámaras
const fotoDe = (alm) => S.fotos[alm] || (D.fotos || {})[alm] || null;
function vCamaras() {
  return `${bandaEjemplo()}<div class="cab"><div><h1>Cámaras de almacén</h1>
    <p>Una cámara por almacén. Ve la señal roja del punto de pedido y avisa sola.</p></div></div>
    <div class="camaras">${ALMS.map((a) => {
      const ms = D.mp.filter((m) => m.alm === a.alm), alarma = ms.filter((m) => ["crit", "pedir"].includes(estado(m))).length;
      const lect = ms.map((m) => S.stock[m.cod]).filter(Boolean).map((x) => x.t).sort().pop(), foto = fotoDe(a.alm);
      return `<article class="cam ${alarma ? "con-alarma" : ""}"><header><span><span class="rec">●</span> ${camId(a.alm)} · ${esc(a.alm)}</span><span>${lect ? esc(lect.slice(11)) : "—"}</span></header>
        <div class="feed">${foto ? `<img src="${foto}" alt="${esc(a.alm)}">` : `<div class="sin-foto">${camSvg(ms, 120)}</div>`}
          ${alarma ? `<span class="badge alarma">${alarma} para pedir</span>` : `<span class="badge ok">sin alarmas</span>`}</div>
        ${foto ? `<div class="vista">${camSvg(ms, 46)}</div>` : ""}
        <footer><span title="${esc(senal(a.est))}">${esc(a.est)} · ${esc(a.lug)} lugares</span>
          <span class="acciones"><button class="btn chico" data-a="lectura" data-id="${esc(a.alm)}">Lectura</button>
          <label class="btn chico">Foto<input type="file" accept="image/*" data-foto="${esc(a.alm)}" hidden></label></span></footer></article>`;
    }).join("")}</div>
    <details class="fuente"><summary>Cómo ve la cámara el punto de pedido</summary>${ALMS.map((a) => `<b>${esc(a.alm)}:</b> ${esc(senal(a.est))}`).join("<br>")}</details>`;
}
function camSvg(ms, h = 96) {
  const w = 40, W = Math.max(300, ms.length * w + 8);
  const cols = ms.map((m, i) => {
    const s = S.stock[m.cod], mx = Math.max(m.max, s ? s.u : 0, m.pp) || 1, x = 6 + i * w, e = estado(m);
    const fill = s ? Math.min(1, s.u / mx) * h : 0, col = { crit: "#ff5c50", pedir: "#f0b04a", ped: "#7fb0ec", ok: "#6cc070", sin: "#3b4452" }[e];
    const yPP = 6 + h - Math.min(1, m.pp / mx) * h, ySS = 6 + h - Math.min(1, m.ss / mx) * h;
    return `<g ${["crit", "pedir"].includes(e) ? 'class="alarma"' : ""}><title>${esc(m.cod)} · ${esc(m.mat)}</title>
      <rect x="${x}" y="6" width="${w - 10}" height="${h}" fill="#1a2029" stroke="#2b3340"/>
      ${s ? `<rect x="${x}" y="${6 + h - fill}" width="${w - 10}" height="${fill}" fill="${col}" opacity=".85"/>` :
        `<line x1="${x}" y1="${6 + h}" x2="${x + w - 10}" y2="6" stroke="#3b4452"/>`}
      <line x1="${x - 2}" x2="${x + w - 8}" y1="${yPP}" y2="${yPP}" stroke="#ffffff" stroke-width="1.5"/>
      <line x1="${x - 2}" x2="${x + w - 8}" y1="${ySS}" y2="${ySS}" stroke="#ff5c50" stroke-dasharray="3 2"/>
      <text x="${x + (w - 10) / 2}" y="${h + 20}" fill="#9aa3b2" font-size="9.5" text-anchor="middle" font-family="Barlow Condensed, Arial Narrow, sans-serif">${esc(m.ref)}</text></g>`;
  }).join("");
  return `<svg width="${W}" height="${h + 28}" viewBox="0 0 ${W} ${h + 28}" role="img" aria-label="Stock por código">${cols}</svg>`;
}
function dlgLectura(alm) {
  const ms = D.mp.filter((m) => m.alm === alm);
  abrir(`Lectura de ${camId(alm)} · ${esc(alm)}`, `<p class="mut" style="margin:0">Cargá lo que muestra la cámara (o el conteo) en la unidad de cada código. Lo que dejes vacío no cambia.</p>
    <form id="fLect" class="tabla"><table><thead><tr><th>Código</th><th>Material</th><th class="n">PP</th><th class="n">Máx.</th><th>Stock</th></tr></thead><tbody>
    ${ms.map((m) => `<tr><td class="mono">${esc(m.cod)}</td><td style="font-size:12.5px">${esc(m.mat)}</td><td class="n">${nf(m.pp, 1)}</td><td class="n">${nf(m.max, 1)}</td>
      <td><input type="number" step="any" min="0" data-cod="${esc(m.cod)}" style="width:110px" aria-label="Stock de ${esc(m.cod)}" value="${S.stock[m.cod] ? S.stock[m.cod].u : ""}"> ${esc(m.um)}</td></tr>`).join("")}
    </tbody></table><div style="margin-top:10px"><button class="btn pri" type="submit">Guardar lectura</button></div></form>`);
  $("#fLect").addEventListener("submit", (ev) => {
    ev.preventDefault();
    $$("input[data-cod]", ev.target).forEach((i) => {
      if (i.value !== "") S.stock[i.dataset.cod] = { u: parseFloat(i.value), src: camId(alm) + " (cámara)", t: ahora() };
    });
    guardar(); cerrar(); pintar(); toast("Lectura guardada");
  });
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
          <thead><tr><th>Producto</th><th class="n">En PT</th><th class="n">Máximo</th></tr></thead><tbody>
          ${D.pt.map((p) => { const u = enStock(p.prod); return `<tr><td>${esc(p.prod)}</td><td class="n">${u ? nf(u) : "—"}</td><td class="n">${nf(p.max)}</td></tr>`; }).join("")}
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
      <div class="campo"><label for="dVeh">Vehículo</label><select id="dVeh">${D.desp.slice(0, 3).map((x) => `<option ${x.veh === v ? "selected" : ""}>${esc(x.veh)}</option>`).join("")}</select></div>
      <div class="campo" style="align-self:end"><button class="btn pri" type="submit">Despachar</button></div></form>`);
  $("#fMover").addEventListener("submit", (ev) => { ev.preventDefault(); const to = $("#mvSlot").value; S.pallets[to] = p; delete S.pallets[id]; guardar(); cerrar(); pintar(); toast(`${p.id} a ${to}`); });
  $("#fDesp").addEventListener("submit", (ev) => {
    ev.preventDefault();
    S.regs.push({ id: "DES-" + String(sig("DES")).padStart(4, "0"), f: "DES", t: ahora(), res: "Despachado", v: { remito: $("#dRem").value, veh: $("#dVeh").value, pallet: p.id, prod: p.prod, cant: p.cant, series: p.series, lote: p.lote, slot: id } });
    S.rev.forEach((r) => { if (r.slot === id) { r.estado = "Despachado"; r.remito = $("#dRem").value; } });
    delete S.pallets[id]; guardar(); cerrar(); pintar(); toast(`${p.id} despachado`);
  });
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
      f.si("pesada", "Pesada final dentro de la tolerancia"), f.si("ident", "Etiqueta, precinto y seguro colocados"), f.obs()],
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

// ---------------------------------------------------------------- dashboard
function vDashboard() {
  const est = D.mp.map(estado), cuenta = (k) => est.filter((e) => e === k).length;
  const hoyR = S.regs.filter((r) => r.t.startsWith(hoy())).length, nc = S.regs.filter((r) => r.res === "No conforme").length;
  const paso = (t, h, c = "") => `<a class="paso ${c}" href="#${h}">${t}</a>`, fl = `<span class="flecha" aria-hidden="true">▶</span>`;
  const carril = (c, t, sub, pasos) => `<div class="carril"><div class="carril-nombre" style="--c:${c}"><b>${t}</b><span>${sub}</span></div><div class="flujo">${pasos.join(fl)}</div></div>`;
  const alertas = D.mp.filter((m) => ["crit", "pedir"].includes(estado(m))).slice(0, 8);
  return `${bandaEjemplo()}<div class="cab"><div><h1>Trazabilidad de planta</h1><p>Almacenes con cámaras, fichas de control y búsqueda por el número grabado. Sin QR.</p></div>
    <div class="filtros"><a class="btn" href="#marcado">Identificación sin QR</a><a class="btn" href="#revendidos">Revendidos</a></div></div>
    <div class="kpis" style="margin-bottom:18px">
      <div class="kpi crit"><span>MP bajo seguridad</span><b class="num">${cuenta("crit")}</b><small>de ${D.mp.length} códigos</small></div>
      <div class="kpi warn"><span>MP para pedir</span><b class="num">${cuenta("pedir")}</b><small>en el punto de pedido</small></div>
      <div class="kpi info"><span>Pedidos en curso</span><b class="num">${cuenta("ped")}</b><small>esperando la recepción</small></div>
      <div class="kpi"><span>MP sin lectura</span><b class="num">${cuenta("sin")}</b><small>códigos sin conteo</small></div>
      <div class="kpi ok"><span>Lugares de PT ocupados</span><b class="num">${Object.keys(S.pallets).length}</b><small>de ${TODOS_SLOTS.length}</small></div>
      <div class="kpi ${nc ? "crit" : "ok"}"><span>Fichas cargadas</span><b class="num">${S.regs.filter((r) => r.f !== "DES").length}</b><small>${hoyR} hoy · ${nc} no conformes</small></div></div>
    <div class="grid">
      <section class="panel c8"><header><h2>Mapa de controles</h2><span class="leyenda"><span><i style="background:var(--info-bg);border:1px solid var(--info)"></i>kanban</span><span><i style="background:var(--accent-soft);border:1px solid var(--accent)"></i>ficha</span></span></header><div class="cuerpo">
        ${carril("var(--mp)", "Materia prima", "kanban + cámaras", [paso("Almacén de MP", "mp", "kan"), paso("Cámaras", "camaras", "kan"), paso("FAB-01 Recepción", "f-FAB-01", "form"), paso("REC-01 Recepción recargas", "f-REC-01", "form")])}
        ${carril("var(--man)", "Manuales y carros", "n° del marcado Pannier", [paso("FAB-02 Marcado", "f-FAB-02", "form"), paso("FAB-03 Sold. longitudinal", "f-FAB-03", "form"), paso("FAB-04 Sold. de cúpula", "f-FAB-04", "form"),
          paso("FAB-05 Sold. circunferencial", "f-FAB-05", "form"), paso("FAB-06 Espesor 2 %", "f-FAB-06", "form"), paso("FAB-07 PH", "f-FAB-07", "form"), paso("FAB-08 Defectos", "f-FAB-08", "form"),
          paso("FAB-09 Pintado", "f-FAB-09", "form"), paso("FAB-10 Pérdidas", "f-FAB-10", "form"), paso("FAB-11 PT", "f-FAB-11", "form")])}
        ${carril("var(--rec)", "Recargas", "orden de servicio + n° grabado", [paso("REC-02 Inspección interior", "f-REC-02", "form"), paso("REC-03 Pérdidas", "f-REC-03", "form"), paso("REC-04 PT y despacho", "f-REC-04", "form")])}
        ${carril("var(--ext)", "Revendidos", "n° de la etiqueta del fabricante", [paso("REV-01 Recepción", "f-REV-01", "form"), paso("Zona de reventa", "pt", "kan")])}
        ${carril("var(--pt)", "Producto terminado", "zonificado con fechas", [paso("Kanban de PT", "pt", "kan"), paso("Despacho por días fijos", "pt")])}</div></section>
      <section class="panel c4"><header><h2>Para pedir</h2><a href="#mp" style="font-size:13px">Kanban de MP</a></header><div class="cuerpo">
        ${alertas.length ? `<table><tbody>${alertas.map((m) => `<tr><td class="mono">${esc(m.cod)}</td><td>${esc(m.mat)}</td><td><span class="pill ${estado(m) === "crit" ? "crit" : "warn"}">${estado(m) === "crit" ? "bajo seguridad" : "pedir"}</span></td></tr>`).join("")}</tbody></table>`
          : `<div class="vacio">${Object.keys(S.stock).length ? "Ningún código en el punto de pedido." : "Todavía no hay lecturas de stock: cargalas desde Cámaras o desde una tarjeta del kanban."}</div>`}</div></section>
      <details class="fuente c12"><summary>De dónde salen los números</summary>${esc(D.fuente.mp)} · ${esc(D.fuente.pt)} · ${esc(D.fuente.bal)} · plano rev ${esc(D.layout.revision)} de la app de gestión interna.
        Lo que se carga queda guardado en este navegador. ${S.demo ? "" : `<button class="btn chico" data-a="ejemplo">Ver con datos de ejemplo</button>`} <button class="btn chico" data-a="borrar">Borrar todo lo cargado</button></details></div>`;
}

// ---------------------------------------------------------------- layout de planta (plano rev10 de la app de gestión)
// Sectores donde se carga cada ficha y zonas de almacén; los nombres y la geometría son los del plano.
const SECTOR_FICHA = {
  "FAB-01": ["mp_trazabilidad", "p01_almacen_mp"], "FAB-02": ["p021_marcado"], "FAB-03": ["m03_sold_long", "p05_sold_long"],
  "FAB-04": ["m06_cuello", "p06_sold_cupla"], "FAB-05": ["m07_circunferencial", "p07_armado_circ"], "FAB-06": ["m08_espesor"],
  "FAB-07": ["m09_ph_secado"], "FAB-08": ["m11_granallado"], "FAB-09": ["m18_pintura", "p12_recepcion_pintados"],
  "FAB-10": ["m15_perdidas", "p17_ensayos_lote"], "FAB-11": ["m17_embalaje", "p16_deposito_pt"], "REC-01": ["rec_polvo"],
  "REC-02": ["rec_R10", "rec_R13R14"], "REC-03": ["rec_R26"], "REC-04": ["rec_R27"], "REV-01": ["exp_trazabilidad"],
};
const SECTOR_PT = { pt_manuales: ["rack"], p16_deposito_pt: ["carros"], p16b_lugar_carga: ["anden"], p11_pulmon_despacho: ["pint"], p12_recepcion_pintados: ["pint"] };
const SECTOR_MP = ["p01_almacen_mp"];
const geo = Object.fromEntries(D.layout.sectores.map((s) => [s.id, s]));
const caja = (s) => s.rect || (() => { const xs = s.poly.map((p) => p[0]), ys = s.poly.map((p) => p[1]); return [Math.min(...xs), Math.min(...ys), Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)]; })();
let SEL = null;
function textoSector(nombre, x, y, w, h) {
  const fs = Math.max(0.3, Math.min(0.9, (w - 0.3) / (nombre.length * 0.58), h * 0.28));
  const lineas = nombre.length * fs * 0.58 > w - 0.3 && nombre.includes(" ") ? [nombre.slice(0, nombre.lastIndexOf(" ", Math.ceil(nombre.length / 2) + 4)), nombre.slice(nombre.lastIndexOf(" ", Math.ceil(nombre.length / 2) + 4) + 1)] : [nombre];
  const f2 = Math.max(0.3, Math.min(fs * (lineas.length > 1 ? 1.6 : 1), 0.9, ...lineas.map((t) => (w - 0.3) / (t.length * 0.58))));
  return `<text class="l-nombre" font-size="${f2.toFixed(2)}" x="${(x + 0.18).toFixed(2)}" y="${(y + f2 * 1.05 + 0.08).toFixed(2)}">${lineas.map((t, i) => `<tspan x="${(x + 0.18).toFixed(2)}" dy="${i ? (f2 * 1.1).toFixed(2) : 0}">${esc(t)}</tspan>`).join("")}</text>`;
}
function svgPlano() {
  const L = D.layout, fichaDe = {};
  Object.entries(SECTOR_FICHA).forEach(([fid, ss]) => ss.forEach((sid) => (fichaDe[sid] = (fichaDe[sid] || []).concat(fid))));
  const alarmaMP = D.mp.some((m) => ["crit", "pedir"].includes(estado(m)));
  const p = [`<text class="l-orient" font-size="1.25" x="-2" y="-41.2">▲ SALIDA DE PT Y RECARGAS</text>`, `<text class="l-orient" font-size="1.25" x="-2" y="16.6">▼ INGRESO DE MATERIA PRIMA</text>`];
  p.push(`<rect class="l-nave" x="0" y="0" width="${L.nave.ancho}" height="${L.nave.largo}"/>`);
  L.nave.anexos.forEach(([x, y, w, h]) => p.push(`<rect class="l-nave" x="${x}" y="${y}" width="${w}" height="${h}"/>`));
  L.pasillos.forEach((q) => { const [x, y, w, h] = q.rect; p.push(`<rect class="l-pasillo" x="${x}" y="${y}" width="${w}" height="${h}"/>`); });
  L.sectores.forEach((s) => {
    const cls = ["l-sector", fichaDe[s.id] ? "ficha" : "", SECTOR_MP.includes(s.id) ? "alm" : "", SECTOR_PT[s.id] ? "ptz" : "",
      SECTOR_MP.includes(s.id) && alarmaMP ? "alerta" : "", SEL === s.id ? "sel" : ""].join(" ");
    const forma = s.rect ? `<rect class="${cls}" data-sector="${s.id}" x="${s.rect[0]}" y="${s.rect[1]}" width="${s.rect[2]}" height="${s.rect[3]}"/>`
      : `<polygon class="${cls}" data-sector="${s.id}" points="${s.poly.map((q) => q.join(",")).join(" ")}"/>`;
    const [x, y, w, h] = caja(s);
    p.push(forma, textoSector(s.nombre, x, y, s.rect ? w : Math.min(w, 9), s.rect ? h : 4));
  });
  L.muros.forEach((m) => p.push(`<polyline class="l-muro" points="${m.map((q) => q.join(",")).join(" ")}"/>`));
  L.portones.forEach((q) => p.push(`<line class="l-porton" x1="${q.de[0]}" y1="${q.de[1]}" x2="${q.a[0]}" y2="${q.a[1]}"/>`));
  // fichas: un cuadradito por sector (como los puestos con ficha de la app de gestión), con el número de la ficha
  Object.entries(fichaDe).forEach(([sid, fs]) => {
    const g = geo[sid]; if (!g) return;
    const [x, y, w, h] = caja(g);
    fs.forEach((fid, k) => { const cx = x + w - 0.75 - k * 1.5, cy = y + h - 0.7;
      p.push(`<rect class="l-ficha" data-sector="${sid}" x="${cx - 0.65}" y="${cy - 0.45}" width="1.3" height="0.9" rx="0.15"/><text class="l-ficha-txt" x="${cx}" y="${cy}">${fid.split("-")[1]}</text>`); });
  });
  // cámaras del almacén de MP repartidas dentro del sector 1, con la cantidad para pedir
  const [ax, ay, , ah] = caja(geo.p01_almacen_mp);
  ALMS.filter((a) => !/producto terminado/.test(a.alm)).forEach((a, i) => {
    const cx = ax + 4.2 + (i % 2) * 2.9, cy = ay + 6 + Math.floor(i / 2) * ((ah - 7) / 6);
    const n = D.mp.filter((m) => m.alm === a.alm && ["crit", "pedir"].includes(estado(m))).length;
    p.push(`<g class="l-cam ${n ? "alarma" : ""}" data-cam="${esc(a.alm)}"><title>${camId(a.alm)} · ${esc(a.alm)}</title><rect x="${cx - 1.4}" y="${cy - 0.45}" width="2.8" height="0.9" rx="0.2" ${n ? 'style="fill:var(--critical)"' : ""}/><text x="${cx}" y="${cy}">${camId(a.alm)}${n ? " · " + n : ""}</text></g>`);
  });
  // ocupación de las zonas de PT
  Object.entries(SECTOR_PT).forEach(([sid, zs]) => {
    const g = geo[sid]; if (!g) return;
    const [x, y, w, h] = caja(g), sl = ZONAS.filter((z) => zs.includes(z.k)).flatMap((z) => z.slots), oc = sl.filter((q) => S.pallets[q]).length;
    p.push(`<text class="l-cuenta" x="${x + w / 2}" y="${y + h / 2 + 0.6}" text-anchor="middle" style="fill:var(--pt)">${oc}/${sl.length}</text>`);
  });
  return p.join("");
}
function vLayout() {
  return `<div class="layout"><section class="panel lienzo"><div class="lienzo-cab"><h2>Layout de planta <span class="mut" style="font:500 12.5px var(--font);text-transform:none;letter-spacing:0">plano rev ${esc(D.layout.revision)} · tocá un sector</span></h2></div>
    <div class="lienzo-area"><svg id="plano" viewBox="-4 -43 59 61" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Layout de la planta con fichas, cámaras y zonas de almacén">${svgPlano()}</svg></div>
    <div class="ley-layout"><span><svg viewBox="0 0 16 12"><rect x="1" y="2" width="14" height="8" rx="2" fill="#fff" stroke="#c8102e" stroke-width="1.4"/></svg>Puesto con ficha (número)</span>
      <span><svg viewBox="0 0 16 12"><rect x="1" y="3" width="14" height="6" rx="1" fill="#11161c"/></svg>Cámara de almacén</span>
      <span><svg viewBox="0 0 16 12"><rect x="1" y="1" width="14" height="10" fill="#efedfb" stroke="#6250d6"/></svg>Almacén de MP</span>
      <span><svg viewBox="0 0 16 12"><rect x="1" y="1" width="14" height="10" fill="#eaf3eb" stroke="#2f7d32"/></svg>Zona de PT (ocupados/lugares)</span>
      <span><svg viewBox="0 0 16 12"><rect x="1" y="1" width="14" height="10" fill="#fbe2e6" stroke="#c8102e"/></svg>Hay MP para pedir</span></div></section>
    <aside class="panel lado" id="lado">${ladoLayout()}</aside></div>`;
}
function ladoLayout() {
  if (!SEL || !geo[SEL]) return `<div class="cuerpo"><span class="mut" style="font-size:12.5px">PLANTA INDUSTRIAL</span><h3>Elegí un sector</h3>
    <p class="mut">Los puestos con cuadradito rojo tienen ficha de control. En el almacén de MP están las cámaras; en rojo las que ven códigos en el punto de pedido.
    Las zonas verdes son del PT, con los lugares ocupados.</p></div>`;
  const g = geo[SEL], fichas = Object.entries(SECTOR_FICHA).filter(([, ss]) => ss.includes(SEL)).map(([fid]) => FORM[fid]);
  const regs = S.regs.filter((r) => fichas.some((x) => x.id === r.f)).slice(-6).reverse();
  let extra = "";
  if (SECTOR_MP.includes(SEL)) extra = `<h4 style="margin:14px 0 6px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)">Cámaras</h4><table><tbody>${ALMS.filter((a) => !/producto terminado/.test(a.alm)).map((a) => {
    const n = D.mp.filter((m) => m.alm === a.alm && ["crit", "pedir"].includes(estado(m))).length;
    return `<tr><td class="mono">${camId(a.alm)}</td><td>${esc(a.alm)}</td><td>${n ? `<span class="pill crit">${n} para pedir</span>` : ""}</td></tr>`; }).join("")}</tbody></table>
    <div class="filtros" style="margin-top:10px"><a class="btn chico" href="#mp">Kanban de MP</a><a class="btn chico" href="#camaras">Cámaras</a></div>`;
  if (SECTOR_PT[SEL]) { const zs = ZONAS.filter((z) => SECTOR_PT[SEL].includes(z.k));
    extra = `<h4 style="margin:14px 0 6px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)">Zonas de PT</h4>${zs.map((z) => `<p style="margin:0 0 4px"><b>${esc(z.t)}</b> · ${z.slots.filter((q) => S.pallets[q]).length} de ${z.slots.length} ocupados</p>`).join("")}
    <a class="btn chico" href="#pt">Kanban de PT</a>`; }
  return `<div class="cuerpo"><span class="mut" style="font-size:12.5px">SECTOR DEL PLANO</span><h3>${esc(g.nombre)}</h3>
    ${fichas.length ? `<h4 style="margin:14px 0 6px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)">Fichas de este puesto</h4>
      <div style="display:grid;gap:8px">${fichas.map((x) => `<a class="fcard" href="#f-${x.id}"><b>${x.id}</b><h3>${esc(x.nombre)}</h3><span class="mut" style="font-size:12px">${esc(x.normas.slice(0, 2).join(" · "))}</span></a>`).join("")}</div>
      <h4 style="margin:14px 0 6px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)">Últimas fichas</h4>
      ${regs.length ? `<table><tbody>${regs.map((r) => `<tr><td class="mono">${esc(r.id)}</td><td class="num">${esc(r.t.slice(5))}</td><td><span class="pill ${r.res === "Conforme" ? "ok" : "crit"}">${esc(r.res)}</span></td></tr>`).join("")}</tbody></table>` : `<div class="vacio">Sin fichas cargadas.</div>`}` : ""}
    ${extra || (!fichas.length ? `<p class="mut">Este sector no tiene ficha de control ni stock que seguir.</p>` : "")}</div>`;
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
    E.stock[m.cod] = { u, src: camId(m.alm) + " (cámara)", t: hMenos(r() * 5) };
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
  return E;
}
function bandaEjemplo() {
  return S.demo ? `<div class="banda-ejemplo"><b>Datos de ejemplo</b><span>para ver cómo funciona. Los parámetros (seguridad, punto de pedido, máximos, lugares) son los reales.</span><button class="btn chico" data-a="limpio">Empezar en limpio</button></div>` : "";
}

// ---------------------------------------------------------------- shell
const MENU = [["dashboard", "Dashboard"], ["mp", "Kanban de MP"], ["camaras", "Cámaras"], ["pt", "Kanban de PT"], ["formularios", "Fichas"], ["layout", "Layout de planta"], ["traza", "Trazabilidad"]];
function menu(actual) {
  const al = D.mp.filter((m) => ["crit", "pedir"].includes(estado(m))).length;
  const cuenta = { mp: al ? `<b class="alerta">${al}</b>` : "", pt: Object.keys(S.pallets).length ? `<b>${Object.keys(S.pallets).length}</b>` : "" };
  const activo = (k) => actual === k || (k === "formularios" && actual.startsWith("f-")) || (k === "traza" && ["marcado", "revendidos"].includes(actual));
  $("#pestanas").innerHTML = MENU.map(([k, t]) => `<a href="#${k}" ${activo(k) ? 'aria-current="page"' : ""}>${t}${cuenta[k] || ""}</a>`).join("");
  $("#menu-nuevo").innerHTML = [["fab", "Fabricación"], ["rec", "Recargas"], ["rev", "Revendidos"]].map(([l, t]) => `<h4>${t}</h4>` +
    FORMS.filter((x) => x.linea === l).map((x) => `<a href="#f-${x.id}"><b>${x.id}</b>${esc(x.nombre)}</a>`).join("")).join("");
}
function pintar() {
  let h = (location.hash || "#dashboard").slice(1) || "dashboard";
  if (h === "inicio") h = "dashboard";
  menu(h);
  const V = { dashboard: vDashboard, mp: vMP, camaras: vCamaras, pt: vPT, formularios: vFormularios, traza: vTraza, revendidos: vRevendidos, marcado: vMarcado, layout: vLayout };
  $("#vista").innerHTML = h.startsWith("f-") ? vForm(h.slice(2)) : (V[h] || vDashboard)();
  if (h.startsWith("f-")) armarForm(h.slice(2));
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
  const sec = t.closest("[data-sector]"); if (sec && $("#plano")) { SEL = sec.dataset.sector; $("#plano").innerHTML = svgPlano(); $("#lado").innerHTML = ladoLayout(); return; }
  const dq = t.closest("[data-q]"); if (dq) { ev.preventDefault(); Q = dq.dataset.q; pintar(); return; }
  const cam = t.closest("[data-cam]"); if (cam) { dlgLectura(cam.dataset.cam); return; }
  if (t.matches("[data-cerrar-velo]")) { cerrar(); return; }
  if (t.closest("[data-cerrar]")) cerrar();
  const mp = t.closest("[data-mp]"); if (mp) { detalleMP(mp.dataset.mp); return; }
  const sl = t.closest("[data-slot]"); if (sl && !t.closest(".dialogo")) { dlgSlot(sl.dataset.slot); return; }
  const a = t.closest("[data-a]"); if (!a) return;
  const k = a.dataset.a, id = a.dataset.id;
  if (k === "cerrar") cerrar();
  else if (k === "lectura") dlgLectura(id);
  else if (k === "pedir") { S.pedidos[id] = { cant: +a.dataset.cant, t: ahora() }; guardar(); cerrar(); pintar(); toast(`Pedido emitido a ${MP[id].prov}`); }
  else if (k === "anularPed") { delete S.pedidos[id]; guardar(); cerrar(); pintar(); }
  else if (k === "recibir") { cerrar(); location.hash = "f-" + (/ecargas/.test(MP[id].linea) && !/Manuales|Carros/.test(MP[id].linea) ? "REC-01" : "FAB-01"); setTimeout(() => { const s = $("#c_mp"); if (s) { s.value = id; s.dispatchEvent(new Event("change", { bubbles: true })); } }, 0); }
  else if (k === "limpio") { S = VACIO(); guardar(); pintar(); toast("Listo: sin datos de ejemplo"); }
  else if (k === "ejemplo") { S = ejemplo(); guardar(); pintar(); toast("Datos de ejemplo cargados"); }
  else if (k === "verOk") { S.verOk = true; pintar(); }
  else if (k === "arranque") { D.mp.forEach((m) => { S.stock[m.cod] = { u: m.max, src: "Arranque al stock máximo", t: ahora() }; }); guardar(); pintar(); toast("Arranque cargado: todo al stock máximo"); }
  else if (k === "borrar") { if (a.dataset.ok) { S = VACIO(); guardar(); pintar(); toast("Se borró todo lo cargado"); } else { a.dataset.ok = "1"; a.textContent = "Tocá de nuevo para confirmar"; } }
  else if (k === "csv") {
    const filas = [["registro", "formulario", "fecha_hora", "resultado", "datos"]].concat(S.regs.map((r) => [r.id, r.f, r.t, r.res, JSON.stringify(r.v)]));
    const csv = filas.map((f) => f.map((x) => `"${String(x).replace(/"/g, '""')}"`).join(";")).join("\n");
    navigator.clipboard.writeText(csv).then(() => toast(`${S.regs.length} registros copiados`)).catch(() => toast("No se pudo copiar: el navegador no lo permite"));
  }
});
document.addEventListener("change", (ev) => {
  const inp = ev.target.closest("input[data-foto]");
  if (!inp || !inp.files || !inp.files[0]) return;
  const lector = new FileReader();
  lector.onload = () => {
    const img = new Image();
    img.onload = () => {
      const k = Math.min(1, 960 / Math.max(img.width, img.height)), c = document.createElement("canvas");
      c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      S.fotos[inp.dataset.foto] = c.toDataURL("image/jpeg", 0.72);
      try { localStorage.setItem(CLAVE, JSON.stringify(S)); toast("Foto guardada"); } catch (e) { toast("La foto no entra en el almacenamiento del navegador; se ve hasta recargar"); }
      pintar();
    };
    img.src = lector.result;
  };
  lector.readAsDataURL(inp.files[0]);
});
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") cerrar(); });
window.addEventListener("hashchange", () => { cerrar(); pintar(); window.scrollTo(0, 0); });
if (!GUARDADO) S = ejemplo();
pintar();
