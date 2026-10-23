// ================================================================ arranque y eventos
cargar();
$("#periodo").textContent = `${MES_TXT[D.mes - 1][0].toUpperCase() + MES_TXT[D.mes - 1].slice(1)} ${D.anio}`;

document.addEventListener("click", e => {
  const v = e.target.closest("[data-v]");
  if (v && !v.matches("[data-a]")) { e.preventDefault(); return ir(v.dataset.v); }
  const d = e.target.closest("[data-det]");
  if (d) { e.preventDefault(); $("#resq").hidden = true; return abrirDetalle(d.dataset.det, d.dataset.det === "equipo" && /^\d+$/.test(d.dataset.id) ? +d.dataset.id : d.dataset.id); }
  const a = e.target.closest("[data-a]");
  if (a && ACC[a.dataset.a]) { if (a.tagName === "A" || a.type === "button" || a.tagName === "BUTTON") e.preventDefault(); ACC[a.dataset.a](a); guardar(); }
  if (!e.target.closest(".buscar")) $("#resq").hidden = true;
});
document.addEventListener("change", e => { const el = e.target.closest("[data-cambio]"); if (el && ACC[el.dataset.cambio]) ACC[el.dataset.cambio](el); });
let tIn;
document.addEventListener("input", e => {
  if (e.target.id === "q") return pintarBusqueda();
  const k = e.target.dataset.in; if (!k) return;
  UI.f[k] = e.target.value; UI.pag[UI.vista] = 0;
  clearTimeout(tIn); tIn = setTimeout(() => { const id = e.target.id; pintar(); const el = document.getElementById(id); if (el) { el.focus(); el.setSelectionRange(el.value.length, el.value.length); } }, 220);
});
document.addEventListener("submit", e => { const f = e.target.dataset.f; if (!f || !FORM[f]) return; e.preventDefault(); FORM[f](); guardar(); });
document.addEventListener("keydown", e => {
  if (e.key === "Escape") { if (UI.det) ACC.cerrarDetalle(); $("#resq").hidden = true; }
  if (e.key === "Enter" && e.target.id === "q" && RES[0]) { e.preventDefault(); ACC.irRes({ dataset: { i: 0 } }); }
  if (e.key === "/" && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); $("#q").focus(); }
});

// página pública del QR de la etiqueta (/m/<serie>): lo que ve quien escanea el equipo, sin datos del dueño
function paginaPublica(txt) {
  const n = numSerie(txt), e = n ? equipo(n) : null;
  document.body.innerHTML = `<main style="max-width:480px;margin:0 auto;padding:24px max(16px, env(safe-area-inset-right, 0px)) 40px max(16px, env(safe-area-inset-left, 0px));display:flex;flex-direction:column;gap:14px">
    <div style="display:flex;align-items:center;gap:10px">${logo(34)}<b style="font:800 24px/1 var(--f-display);font-style:italic;letter-spacing:.06em">FLAMA</b></div>
    ${!e ? `<div class="aviso av">No encontramos el equipo ${esc(txt)}.</div>` : !e.fab && e.estado !== "Rechazado" ? `<div class="aviso in"><b>${e.s}</b> · ${esc(e.o.modelo)}: todavía no salió de fábrica.</div>` : e.estado === "Rechazado" ? `<div class="aviso no"><b>${e.s}</b>: este número fue rechazado en fábrica y no salió a la venta. Si está instalado, no lo uses y avisá a FLAMA.</div>` :
    `<div class="panel"><div class="cuerpo" style="display:flex;flex-direction:column;gap:10px"><div style="font:700 26px/1 var(--f-mono)">${e.s}</div><div class="muted">${esc(e.o.modelo)} · fuegos A, B y C</div>
      ${pill(e.mant && new Date(e.mant) < HOY ? "Mantenimiento vencido" : "Vigente", e.mant && new Date(e.mant) < HOY ? "no" : "ok")}
      <dl class="dl"><dt>Fabricado</dt><dd>${fecha(e.fab)}</dd><dt>Mantenimiento</dt><dd>vence ${fecha(e.mant)}</dd><dt>Prueba hidráulica</dt><dd>vence ${fecha(e.phVence)}</dd><dt>Vida útil</dt><dd>hasta ${fecha(e.vida)}</dd></dl></div></div>
      <p class="muted" style="margin:0;font-size:12.5px">Revisalo cada tres meses (IRAM 3517-2 8.2): precinto y seguro puestos, aguja del manómetro en verde, sin golpes ni óxido, tarjeta oficial sana. Para servicio o reclamos, contactá a tu distribuidor o a FLAMA con este número.</p>`}</main>`;
}

const ruta = location.pathname.match(/\/m\/([^/]+)\/?$/);
if (ruta) paginaPublica(decodeURIComponent(ruta[1]));
else {
  const [v, p] = desdeHash(location.hash.slice(1));
  UI.vista = v; UI.param = p;
  window.addEventListener("hashchange", () => { const [k, q] = desdeHash(location.hash.slice(1)); if (hashDe(k, q) !== hashDe(UI.vista, UI.param)) ir(k, q); });
  pintar();
}
