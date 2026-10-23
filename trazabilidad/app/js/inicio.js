// ================================================================ inicio: el equipo, su número grabado y las cuatro puertas
function vistaInicio() {
  const lt = lotesMes(), u = lt.reduce((a, l) => a + l.cant, 0);
  const fotos = [["chapas", "01", "La chapa", "Cada planchuela se graba con su serie y el cuño DPS antes de rolarse."], ["carro_cupulas", "02", "El lote", "Viaja en su carro con una hoja de ruta: firmas por puesto y una tilde por equipo en los ensayos."],
    ["pallets", "03", "El pallet", "Una lectura por caja; la etiqueta del pallet une los equipos a su remito."], ["despacho", "04", "El camino", "Chofer, distribuidor e instalador confirman con el celular: la custodia nunca queda en blanco."]];
  return `<section class="heroe wrap"><div class="ancho heroe-in">
    <div><div class="ceja">FLAMA S.A. · sistema de trazabilidad</div>
      <h1>Cada matafuego,<br><em>con su historia</em></h1>
      <p class="lead">Desde la chapa hasta el día que se inutiliza: quién lo hizo, con qué insumos, qué ensayos pasó, dónde está y cuándo le toca el mantenimiento. Lo ve FLAMA, el recargador, el inspector y el cliente, cada uno lo suyo.</p>
      <div class="chapa" aria-label="Grabado de la franja"><div class="grab">FLAMA S.A.&nbsp;&nbsp;N° ${esc(SERIES[0])}&nbsp;&nbsp;${AA}&nbsp;&nbsp;DPS</div><small>Así queda grabada la pollera: 130 × 12 mm, ≈ 0,22 mm de profundidad, del lado de la pared. Queda en el metal toda la vida útil del equipo.</small></div>
      <div class="cta"><a class="btn pri" href="#recorrido" data-v="recorrido">Seguir un lote real →</a><a class="btn osc" href="#clientes" data-v="clientes">Lo que ve el cliente</a></div></div>
    <div class="heroe-fig">${foto("heroe_5kg") ? `<img class="heroe-img" src="${foto("heroe_5kg")}" alt="Matafuego ABC 5 kg FLAMA visto del lado de la pared, con la franja grabada y la etiqueta de serie">` : ""}
      <div class="callout izq" style="left:2%;top:46%"><b>Etiqueta de serie</b>QR 45 × 25 · se renueva en cada servicio</div>
      <div class="callout izq" style="left:0;bottom:6%"><b>Franja grabada</b>serie + año + cuño DPS</div>
      <div class="callout der" style="right:0;top:22%"><b>Tarjeta oficial</b>DPS (PBA) o SGM (CABA) en el cuello</div></div>
  </div>
  <div class="ancho cifras"><div><b>${n0(u)}</b><span>equipos manuales en las órdenes de ${MES} ${D.anio}</span></div><div><b>${lt.length}</b><span>lotes, uno por carro</span></div><div><b>${AA}-${String(D.previas + 1).padStart(6, "0")}</b><span>primera serie del mes</span></div><div><b>≈ ${n0((284463 + 3107) * 3 / 1e6 * 10) / 10} M</b><span>eventos por año en 2035</span></div></div></section>

  <section class="sec wrap"><div class="ancho"><div class="ceja">La familia ABC</div><h2>Ocho modelos, un mismo número</h2>
    <p class="lead">Todos llevan la franja grabada y la etiqueta de serie en el mismo lugar relativo, calculado sobre el plano de cada recipiente. Los carros llevan dos renglones entre los triángulos.</p>
    <div class="familia">${foto("familia") ? `<img src="${foto("familia")}" alt="Familia de matafuegos ABC FLAMA de 1 a 50 kg a escala">` : ""}<div class="esc">${["1 kg", "2,5 kg", "5 kg", "10 kg", "25 kg", "50 · 70 · 100 kg"].map((x, k) => `<span style="left:${((IMG && IMG.familia_x) || [])[k] * 100}%">${x}</span>`).join("")}</div></div>
    <p class="nota">Renders a escala real del modelo 3D de los planos de fabricación. 70 y 100 kg usan el mismo carro que el de 50 kg.</p></div></section>

  <section class="sec wrap" style="padding-top:0"><div class="ancho"><div class="ceja">El recorrido</div><h2>Del rollo de chapa a la pared del cliente</h2>
    <div class="ruta">${fotos.map(([k, n, t, d]) => `<figure>${foto(k) ? `<img src="${foto(k)}" alt="${esc(t)}" loading="lazy">` : ""}<figcaption><span class="n">${n}</span><b>${esc(t)}</b>${esc(d)}</figcaption></figure>`).join("")}</div>
    <p class="nota">Imágenes de los documentos de proceso de FLAMA.</p></div></section>

  <section class="sec wrap" style="padding-top:0"><div class="ancho"><div class="ceja">Qué hay adentro</div><h2>Cuatro formas de verlo</h2>
    <div class="puertas">
      <a class="puerta" href="#recorrido" data-v="recorrido"><b>Recorrido</b><span>16 pasos con el lote ${esc(DEMO.op)}: cada pantalla, quién la usa, qué se escribe y qué norma aplica.</span><i>Abrir →</i></a>
      <a class="puerta" href="#clientes" data-v="clientes"><b>Atención al cliente</b><span>Portal del QR, reclamos con plazo, datos personales, baja y arrepentimiento. Matriz con cada artículo.</span><i>Abrir →</i></a>
      <a class="puerta" href="#manual" data-v="manual"><b>Manual MT-01</b><span>Responsabilidades, registros, 12 procedimientos, contingencias y un buscador de traza que funciona.</span><i>Abrir →</i></a>
      <a class="puerta" href="#desvios" data-v="desvios"><b>Desvíos</b><span>Cartas de control, Pareto de rechazos y el registro de desvíos con sus porqués.</span><i>Abrir →</i></a></div></div></section>

  <section class="sec wrap" style="padding-top:0"><div class="ancho"><div class="ceja">Base normativa</div><h2>Lo que exige cada norma, adentro del sistema</h2>
    <div class="normas">${["IRAM 3517-2", "Res. 349/07 PBA", "Dec. 4.992/90 PBA", "Res. 32-AGC/15 CABA", "Ley 24.240", "Res. SCI 424/2020", "Ley 25.326", "Ley 26.993", "IRAM-ISO 10002", "IRAM 3550", "DOC-02 FLAMA"].map(x => `<span>${x}</span>`).join("")}</div></div></section>`;
}
