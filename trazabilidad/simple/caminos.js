// Caminos por los pasillos del plano.
// Se arma una grilla de 25 cm sobre el layout con un costo por celda (pasillo barato, piso libre medio,
// atravesar otro puesto caro, muro casi prohibido salvo portones y puertas) y se busca el camino más
// barato con A*, penalizando cada giro para que el recorrido salga en tramos rectos, como se camina.

const CELDA = 0.25;
const COSTO = { pasillo: 2, exterior: 3, piso: 6, sector: 40, muro: 250, propio: 2 };
const GIRO = 8;
const DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1]];

export function crearCaminos({ layout, zonas, limites, puestos }) {
  const [x0, y0, ancho, alto] = limites;
  const W = Math.ceil(ancho / CELDA), H = Math.ceil(alto / CELDA), N = W * H;
  const costo = new Uint8Array(N).fill(COSTO.exterior);
  const sectorDe = new Int16Array(N).fill(-1);
  const idx = (cx, cy) => cy * W + cx;
  const celda = (x, y) => [Math.floor((x - x0) / CELDA), Math.floor((y - y0) / CELDA)];
  const centro = (cx, cy) => [x0 + (cx + 0.5) * CELDA, y0 + (cy + 0.5) * CELDA];

  // Recorre las celdas cuyo centro cae dentro del rectángulo.
  function enRect([rx, ry, rw, rh], fn) {
    const [c0, f0] = celda(rx, ry), [c1, f1] = celda(rx + rw, ry + rh);
    for (let cy = Math.max(0, f0); cy <= Math.min(H - 1, f1); cy++) {
      for (let cx = Math.max(0, c0); cx <= Math.min(W - 1, c1); cx++) {
        const [px, py] = centro(cx, cy);
        if (px >= rx && px <= rx + rw && py >= ry && py <= ry + rh) fn(idx(cx, cy));
      }
    }
  }
  function enPoligono(poly, fn) {
    const xs = poly.map((p) => p[0]), ys = poly.map((p) => p[1]);
    enRect([Math.min(...xs), Math.min(...ys), Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)], (i) => {
      const [px, py] = centro(i % W, Math.floor(i / W));
      let dentro = false;
      for (let a = 0, b = poly.length - 1; a < poly.length; b = a++) {
        const [xa, ya] = poly[a], [xb, yb] = poly[b];
        if ((ya > py) !== (yb > py) && px < ((xb - xa) * (py - ya)) / (yb - ya) + xa) dentro = !dentro;
      }
      if (dentro) fn(i);
    });
  }
  function enLinea([xa, ya], [xb, yb], ancho, fn) {
    const largo = Math.hypot(xb - xa, yb - ya);
    const pasos = Math.max(1, Math.ceil(largo / (CELDA / 2)));
    for (let k = 0; k <= pasos; k++) {
      const x = xa + ((xb - xa) * k) / pasos, y = ya + ((yb - ya) * k) / pasos;
      const [cx, cy] = celda(x, y);
      for (let dy = -ancho; dy <= ancho; dy++) for (let dx = -ancho; dx <= ancho; dx++) {
        const nx = cx + dx, ny = cy + dy;
        if (nx >= 0 && ny >= 0 && nx < W && ny < H) fn(idx(nx, ny));
      }
    }
  }

  // Piso de la nave (sin el recorte de la esquina) y sus anexos.
  const nave = [[0, 0, layout.nave.ancho, layout.nave.largo], ...layout.nave.anexos];
  for (const r of nave) enRect(r, (i) => { costo[i] = COSTO.piso; });
  if (layout.nave.recorte) enRect(layout.nave.recorte, (i) => { costo[i] = COSTO.exterior; });
  // Sectores (puestos, depósitos, servicios): se puede salir del propio, cruzar otros cuesta caro.
  const sectores = [...layout.sectores, ...zonas.map((z) => ({ ...z, externa: true }))];
  const indiceSector = new Map();
  sectores.forEach((s, k) => {
    indiceSector.set(s.id, k);
    const marcar = (i) => { sectorDe[i] = k; costo[i] = s.externa && !s.interna ? COSTO.exterior : COSTO.sector; };
    if (s.rect) enRect(s.rect, marcar); else enPoligono(s.poly, marcar);
  });
  for (const p of layout.pasillos) enRect(p.rect, (i) => { costo[i] = COSTO.pasillo; sectorDe[i] = -1; });
  for (const m of layout.muros) for (let k = 0; k < m.length - 1; k++) enLinea(m[k], m[k + 1], 0, (i) => { costo[i] = COSTO.muro; });
  for (const [a, b] of layout.divisiones) enLinea(a, b, 0, (i) => { costo[i] = COSTO.muro; });
  for (const p of layout.portones) enLinea(p.de, p.a, 1, (i) => { costo[i] = COSTO.pasillo; });
  for (const [a, b] of layout.puertas) enLinea(a, b, 1, (i) => { costo[i] = Math.min(costo[i], COSTO.piso); });

  // A* con el sentido de avance en el estado, para cobrar los giros.
  const g = new Float32Array(N * 4);
  const padre = new Int32Array(N * 4);
  function buscar(desde, hasta, sectA, sectB) {
    g.fill(Infinity);
    const [gx, gy] = [hasta % W, Math.floor(hasta / W)];
    const h = (i) => (Math.abs((i % W) - gx) + Math.abs(Math.floor(i / W) - gy)) * COSTO.pasillo;
    const pagar = (i) => (sectorDe[i] >= 0 && (sectorDe[i] === sectA || sectorDe[i] === sectB) ? COSTO.propio : costo[i]);
    const monton = [];
    const meter = (f, s) => {
      monton.push([f, s]);
      for (let k = monton.length - 1; k > 0;) {
        const p = (k - 1) >> 1;
        if (monton[p][0] <= monton[k][0]) break;
        [monton[p], monton[k]] = [monton[k], monton[p]];
        k = p;
      }
    };
    const sacar = () => {
      const top = monton[0], ult = monton.pop();
      if (monton.length) {
        monton[0] = ult;
        for (let k = 0; ;) {
          const a = 2 * k + 1, b = a + 1;
          let m = k;
          if (a < monton.length && monton[a][0] < monton[m][0]) m = a;
          if (b < monton.length && monton[b][0] < monton[m][0]) m = b;
          if (m === k) break;
          [monton[m], monton[k]] = [monton[k], monton[m]];
          k = m;
        }
      }
      return top;
    };
    for (let d = 0; d < 4; d++) { g[desde * 4 + d] = 0; padre[desde * 4 + d] = -1; meter(h(desde), desde * 4 + d); }
    while (monton.length) {
      const [f, s] = sacar();
      const i = s >> 2, d = s & 3;
      if (f - h(i) > g[s] + 1e-6) continue;
      if (i === hasta) {
        const camino = [];
        for (let e = s; e !== -1; e = padre[e]) camino.push(e >> 2);
        return camino.reverse();
      }
      const cx = i % W, cy = Math.floor(i / W);
      for (let nd = 0; nd < 4; nd++) {
        const nx = cx + DIRS[nd][0], ny = cy + DIRS[nd][1];
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        const j = idx(nx, ny);
        const ng = g[s] + pagar(j) + (nd !== d ? GIRO : 0);
        const ns = j * 4 + nd;
        if (ng < g[ns]) { g[ns] = ng; padre[ns] = s; meter(ng + h(j), ns); }
      }
    }
    return null;
  }

  // Deja solo las esquinas del camino.
  function esquinas(celdas) {
    const pts = celdas.map((i) => centro(i % W, Math.floor(i / W)));
    const r = [pts[0]];
    for (let k = 1; k < pts.length - 1; k++) {
      const [a, b, c] = [r[r.length - 1], pts[k], pts[k + 1]];
      const mismaX = Math.abs(a[0] - b[0]) < 1e-6 && Math.abs(b[0] - c[0]) < 1e-6;
      const mismaY = Math.abs(a[1] - b[1]) < 1e-6 && Math.abs(b[1] - c[1]) < 1e-6;
      if (!mismaX && !mismaY) r.push(b);
    }
    r.push(pts[pts.length - 1]);
    return r;
  }

  const cache = new Map();
  // Camino entre los puntos de dos puestos, como lista de [x, y] en metros.
  return function camino(idA, idB, a, b) {
    const clave = `${idA}|${idB}`;
    if (cache.has(clave)) return cache.get(clave);
    let r = [[a.x, a.y], [b.x, b.y]];
    const [ax, ay] = celda(a.x, a.y), [bx, by] = celda(b.x, b.y);
    if (idA !== idB && ax >= 0 && ay >= 0 && bx >= 0 && by >= 0 && ax < W && bx < W && ay < H && by < H) {
      const sa = indiceSector.get(puestos[idA]?.sector) ?? -2;
      const sb = indiceSector.get(puestos[idB]?.sector) ?? -2;
      const celdas = buscar(idx(ax, ay), idx(bx, by), sa, sb);
      // Las puntas se unen al centro exacto de cada punto (la diferencia es menor a una celda).
      if (celdas && celdas.length > 1) r = [[a.x, a.y], ...esquinas(celdas), [b.x, b.y]];
    }
    cache.set(clave, r);
    return r;
  };
}
