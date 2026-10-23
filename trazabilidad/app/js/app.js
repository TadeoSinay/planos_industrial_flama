// ================================================================ app: vistas, enlaces con #, eventos delegados y tooltip
const VISTAS = { inicio: vistaInicio, recorrido: vistaRecorrido, clientes: vistaClientes, manual: vistaManual, desvios: vistaDesvios };
function marcarHash(id) { try { history.replaceState(null, "", "#" + id); } catch (e) {} }
function pintar() {
  if (S.vista === "recorrido") { if (!$("#escenario")) $("#vista").innerHTML = vistaRecorrido(); pintarRecorrido(); }
  else $("#vista").innerHTML = VISTAS[S.vista]();
  document.querySelectorAll(".vistas a").forEach(a => { if (a.dataset.v === S.vista) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
}
function abrir(v, paso) {
  S.vista = VISTAS[v] ? v : "inicio";
  $("#vista").innerHTML = "";
  if (paso != null) { const i = PASOS.findIndex(p => p.id === paso); if (i >= 0) S.paso = i; }
  marcarHash(S.vista === "recorrido" ? PASOS[S.paso].id : S.vista);
  try { localStorage.setItem("flama-vista", S.vista); } catch (e) {}
  pintar(); window.scrollTo({ top: 0 });
}

document.addEventListener("click", async e => {
  const v = e.target.closest("[data-v]");
  if (v) { e.preventDefault(); if (v.dataset.ct) S.cli.tab = v.dataset.ct; return abrir(v.dataset.v, v.dataset.paso); }
  const m = e.target.closest("[data-m]");
  if (m) { e.preventDefault(); const s = document.getElementById("m-" + m.dataset.m); if (s) s.scrollIntoView({ behavior: "smooth" }); return; }
  const p = e.target.closest("[data-p]"); if (p) return ir(+p.dataset.p);
  const t = e.target.closest("[data-t]"); if (t) { const [s, k] = t.dataset.t.split("|"); S.tildes[s][k] = !S.tildes[s][k]; return pintar(); }
  const a = e.target.closest("[data-a]");
  if (a && ACC[a.dataset.a] && a.type !== "file") { if (a.type !== "checkbox") e.preventDefault(); return ACC[a.dataset.a](a); }
});
document.addEventListener("keydown", e => { const t = e.target.closest("[data-t]"); if (t && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); t.click(); } });
document.addEventListener("change", e => {
  if (e.target.id === "foto" && e.target.files[0]) { S.foto = e.target.files[0].name; pintar(); return; }
  const k = e.target.dataset.i; if (k && e.target.tagName === "SELECT" && INPUT[k]) { INPUT[k](e.target.value); pintar(); }
});
document.addEventListener("input", e => {
  const k = e.target.dataset.i; if (!k || !INPUT[k] || e.target.tagName === "SELECT") return;
  if (INPUT[k](e.target.value)) { const id = e.target.id; pintar(); const el = document.getElementById(id); if (el) { el.focus(); const val = el.value; el.value = ""; el.value = val; } }
});
document.addEventListener("submit", e => {
  const f = e.target.dataset.f; if (!f) return; e.preventDefault();
  if (f === "leer") { const v = $("#lectura").value; if (v) leer(v); }
  else if (FORM[f]) FORM[f]();
});

// tooltip para las marcas de los gráficos
const tip = document.createElement("div");
tip.setAttribute("role", "tooltip");
tip.style.cssText = "position:fixed;z-index:20;pointer-events:none;background:var(--ink);color:var(--bg);font:600 12.5px/1.35 var(--f-body);padding:7px 10px;border-radius:6px;max-width:280px;box-shadow:var(--shadow);display:none";
document.body.appendChild(tip);
document.addEventListener("pointermove", e => {
  const g = e.target.closest && e.target.closest("[data-tip]");
  if (!g) { tip.style.display = "none"; return; }
  tip.textContent = g.dataset.tip; tip.style.display = "block";
  const x = Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 8), y = Math.max(8, e.clientY - tip.offsetHeight - 12);
  tip.style.left = x + "px"; tip.style.top = y + "px";
});

// arranque: el # elige la vista (o el paso del recorrido); si no hay, la última vista usada
document.getElementById("logoTop").innerHTML = logo(38);
document.getElementById("logoPie").innerHTML = logo(22);
function desdeHash(inicio) {
  const h = location.hash.slice(1);
  if (VISTAS[h]) S.vista = h;
  else if (PASOS.some(p => p.id === h)) { S.vista = "recorrido"; S.paso = PASOS.findIndex(p => p.id === h); }
  else if (inicio) { try { const v = localStorage.getItem("flama-vista"); if (VISTAS[v]) S.vista = v; } catch (e) {} }
  $("#vista").innerHTML = ""; pintar();
}
window.addEventListener("hashchange", () => desdeHash(false));
pintarRegistro(); desdeHash(true);
