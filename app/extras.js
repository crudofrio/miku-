/* Miku en casa — extras sin compilar (no hace falta npm):
 *  1. Accesorios por variante en modo Live2D (sombrero de bruja, vueltiao…),
 *     pegados a la cabeza del modelo. No toca los archivos del modelo.
 *  2. Ambiente de octubre (Halloween) todo el mes.
 * Formato documentado en el README («Accesorios por variante»).
 */
const AJUSTES = "miku-en-casa-ajustes";
const ROTACION = "miku-en-casa-rotacion";
const ELECCION = "miku-en-casa-accesorio"; // "auto" | "ninguno" | id
const RUTA_OK = /^(accesorios|dias)\/[A-Za-z0-9._\/-]+\.png$/;

const params = new URLSearchParams(location.search);
const hoy = new Date();
const esOctubre = params.get("temporada") === "octubre" || (params.get("temporada") !== "normal" && hoy.getMonth() === 9);

let catalogo = {};      // id -> {nombre, archivo, ancho, dx, dy, giro, ancla}
let deOctubre = "";
let vivo = null;        // {app, modelo, interno}
let indicesCara = null;
let img = null;
let actualId = "";
let tick = null;

function leerJSON(clave) {
  try { return JSON.parse(localStorage.getItem(clave) || "null"); } catch { return null; }
}

function limpiarAcc(id, a) {
  if (!a || typeof a !== "object" || typeof a.archivo !== "string") return null;
  const archivo = a.archivo.trim().replace(/^\/+/, "");
  if (!RUTA_OK.test(archivo) || archivo.includes("..")) return null;
  const n = (v, d, min, max) => (typeof v === "number" && Number.isFinite(v) ? Math.min(max, Math.max(min, v)) : d);
  const ancla = Array.isArray(a.ancla) && a.ancla.length === 2 ? [n(a.ancla[0], 0.5, 0, 1), n(a.ancla[1], 0.8, 0, 1)] : [0.5, 0.8];
  return {
    id,
    nombre: typeof a.nombre === "string" ? a.nombre.slice(0, 60) : id,
    archivo: "/" + archivo,
    ancho: n(a.ancho, 1.8, 0.2, 6),
    dx: n(a.dx, 0, -3, 3),
    dy: n(a.dy, -0.6, -3, 3),
    giro: n(a.giro, 0, -90, 90),
    ancla,
  };
}

function sumar(mapa) {
  if (!mapa || typeof mapa !== "object") return;
  for (const [id, a] of Object.entries(mapa)) {
    if (!/^[a-z0-9][a-z0-9-]{0,40}$/.test(id)) continue;
    const limpio = limpiarAcc(id, a);
    if (limpio) catalogo[id] = limpio;
  }
}

async function cargarCatalogo() {
  catalogo = {};
  try {
    const r = await fetch("/accesorios/accesorios.json", { cache: "no-store" });
    if (r.ok) {
      const j = await r.json();
      sumar(j.accesorios);
      if (typeof j.octubre === "string") deOctubre = j.octubre;
    }
  } catch {}
  // Los paquetes del día pueden traer "accesorios": { "<variante>": {...} }
  try {
    const r = await fetch("/dias/manifiesto.json", { cache: "no-store" });
    if (r.ok) {
      const lista = ((await r.json()).paquetes || []).filter((x) => /^\d{4}-\d{2}-\d{2}\.json$/.test(x)).sort();
      for (const nombre of lista) {
        try {
          const p = await (await fetch(`/dias/${nombre}`, { cache: "no-store" })).json();
          sumar(p.accesorios);
        } catch {}
      }
    }
  } catch {}
  llenarSelector();
}

function varianteActual() {
  const url = params.get("variante");
  if (url) return url;
  const a = leerJSON(AJUSTES);
  if (a && typeof a.variante === "string" && a.variante && a.variante !== "rotar") return a.variante;
  const r = leerJSON(ROTACION);
  return (r && typeof r.varianteId === "string" && r.varianteId) || "";
}

function elegido() {
  const url = params.get("accesorio");
  const eleccion = url || localStorage.getItem(ELECCION) || "auto";
  if (eleccion === "ninguno") return null;
  if (eleccion !== "auto") return catalogo[eleccion] || null;
  const v = varianteActual();
  if (catalogo[v]) return catalogo[v];
  if (esOctubre && catalogo[deOctubre]) return catalogo[deOctubre];
  return null;
}

/* ---------- cabeza del modelo ---------- */
function buscarCara(interno) {
  try {
    const core = interno.coreModel.getModel();
    const partes = core.parts;
    const ids = partes.ids;
    const objetivo = ["PARTS_01_FACE_001", "PartFace", "Face"].map((x) => x.toLowerCase());
    let cara = ids.findIndex((id) => objetivo.includes(String(id).toLowerCase()));
    if (cara < 0) cara = ids.findIndex((id) => /face|kao|顔/i.test(String(id)));
    const dentro = (i) => {
      for (let p = i, vueltas = 0; p >= 0 && vueltas < 30; p = partes.parentIndices[p], vueltas++) if (p === cara) return true;
      return false;
    };
    const out = [];
    const d = core.drawables;
    for (let i = 0; i < d.count; i++) {
      if (cara >= 0 && dentro(d.parentPartIndices[i])) out.push(i);
      else if (cara < 0 && /face/i.test(String(d.ids[i]))) out.push(i);
    }
    return out;
  } catch {
    return [];
  }
}

function cajaCara() {
  const { modelo, interno } = vivo;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  const pt = { x: 0, y: 0 };
  const ver = (x, y) => {
    pt.x = x; pt.y = y;
    const a = interno.localTransform.apply(pt);
    const g = modelo.toGlobal(a);
    if (g.x < minX) minX = g.x; if (g.x > maxX) maxX = g.x;
    if (g.y < minY) minY = g.y; if (g.y > maxY) maxY = g.y;
  };
  if (indicesCara && indicesCara.length) {
    for (const i of indicesCara) {
      const v = interno.getDrawableVertices(i);
      for (let k = 0; k < v.length; k += 8) ver(v[k], v[k + 1]); // muestreo: basta para la caja
    }
  }
  if (!Number.isFinite(minX)) {
    // Sin parte de cara: estimar desde la caja del modelo completo.
    const b = modelo.getBounds();
    const w = b.width * 0.22;
    return { x: b.x + b.width / 2 - w / 2, y: b.y + b.height * 0.06, w, h: w };
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

// Los parámetros se restauran al final de cada cuadro, así que se leen
// justo antes de que el modelo se actualice (evento beforeModelUpdate).
const angulos = {};
const IDS_ANGULO = ["PARAM_ANGLE_Z", "ParamAngleZ", "PARAM_BODY_ANGLE_Z", "ParamBodyAngleZ"];
function capturarAngulos() {
  try {
    const core = vivo.interno.coreModel;
    for (const id of IDS_ANGULO) angulos[id] = core.getParameterValueById(id) || 0;
  } catch {}
}
function angulo(id) {
  return angulos[id] || 0;
}

function pintar() {
  if (!vivo || !img) return;
  const lienzo = document.getElementById("lienzo");
  const acc = elegido();
  const visible = acc && lienzo && !lienzo.hidden && !document.hidden;
  if (!visible) { img.hidden = true; return; }
  if (acc.id !== actualId) {
    actualId = acc.id;
    img.src = acc.archivo;
    img.alt = acc.nombre;
  }
  const c = cajaCara();
  const r = lienzo.getBoundingClientRect();
  const ancho = c.w * acc.ancho;
  // ANGLE_Z positivo inclina la cabeza en sentido horario en pantalla (probado con el sample).
  const giro = (angulo("PARAM_ANGLE_Z") + angulo("ParamAngleZ")) * 0.9
             + (angulo("PARAM_BODY_ANGLE_Z") + angulo("ParamBodyAngleZ")) * 0.5 + acc.giro;
  const cx = r.left + c.x + c.w / 2 + acc.dx * c.w;
  const cy = r.top + c.y + acc.dy * c.w;
  img.style.width = `${ancho}px`;
  img.style.transformOrigin = `${acc.ancla[0] * 100}% ${acc.ancla[1] * 100}%`;
  img.style.transform =
    `translate(${cx - ancho * acc.ancla[0]}px, ${cy - ancho * acc.ancla[1]}px) rotate(${giro}deg)`;
  img.hidden = false;
  if (params.has("depurar")) {
    let caja = document.getElementById("accesorio-caja");
    if (!caja) { caja = document.createElement("div"); caja.id = "accesorio-caja"; caja.style.cssText = "position:fixed;z-index:9;border:2px solid red;pointer-events:none"; document.body.appendChild(caja); }
    Object.assign(caja.style, { left: `${r.left + c.x}px`, top: `${r.top + c.y}px`, width: `${c.w}px`, height: `${c.h}px` });
  }
  if (params.has("depurar")) document.documentElement.dataset.cara = JSON.stringify({ x: Math.round(c.x), y: Math.round(c.y), w: Math.round(c.w), h: Math.round(c.h), n: indicesCara.length, giro: Math.round(giro), z: angulo("PARAM_ANGLE_Z") });
}

function conectar(detalle) {
  if (vivo && tick) { try { vivo.app.ticker.remove(tick); } catch {} }
  vivo = detalle;
  tick = null;
  if (!vivo) { if (img) img.hidden = true; return; }
  indicesCara = buscarCara(vivo.interno);
  if (!img) {
    img = document.createElement("img");
    img.id = "accesorio";
    img.className = "accesorio";
    img.hidden = true;
    img.decoding = "async";
    img.setAttribute("aria-hidden", "true");
    const lienzo = document.getElementById("lienzo");
    lienzo.insertAdjacentElement("afterend", img);
  }
  if (params.has("depurar") && params.get("z")) {
    const z = Number(params.get("z")) || 0;
    vivo.interno.on("beforeModelUpdate", () => { try { vivo.interno.coreModel.setParameterValueById("PARAM_ANGLE_Z", z); } catch {} });
  }
  vivo.interno.on("beforeModelUpdate", capturarAngulos);
  tick = () => pintar();
  vivo.app.ticker.add(tick);
}

window.addEventListener("miku-live2d", (e) => conectar(e.detail));
if (window.__mikuLive2D) conectar(window.__mikuLive2D);

/* ---------- selector en Ajustes ---------- */
function llenarSelector() {
  let sel = document.getElementById("accesorio-elegir");
  if (!sel) {
    const variante = document.getElementById("variante");
    const fieldset = variante && variante.closest("fieldset");
    if (!fieldset) return;
    const label = document.createElement("label");
    label.textContent = "Accesorio en Live2D ";
    sel = document.createElement("select");
    sel.id = "accesorio-elegir";
    label.appendChild(sel);
    fieldset.appendChild(label);
    sel.addEventListener("change", () => {
      localStorage.setItem(ELECCION, sel.value);
      actualId = "";
      pintar();
    });
  }
  sel.replaceChildren(new Option("Automático (según variante y temporada)", "auto"), new Option("Ninguno", "ninguno"));
  for (const a of Object.values(catalogo)) sel.add(new Option(a.nombre, a.id));
  const guardado = localStorage.getItem(ELECCION) || "auto";
  sel.value = [...sel.options].some((o) => o.value === guardado) ? guardado : "auto";
}

/* ---------- octubre ---------- */
function ambienteOctubre() {
  if (!esOctubre) return;
  document.documentElement.classList.add("octubre");
  const capa = document.createElement("div");
  capa.className = "octubre-capa";
  capa.setAttribute("aria-hidden", "true");
  const cosas = ["🦇", "🦇", "🎃", "🦇", "✨", "🕸️"];
  cosas.forEach((c, i) => {
    const s = document.createElement("span");
    s.textContent = c;
    s.style.setProperty("--i", String(i));
    capa.appendChild(s);
  });
  const app = document.getElementById("app");
  const fondos = app && app.querySelector(".fondos");
  if (fondos) fondos.insertAdjacentElement("afterend", capa);
  const marca = document.querySelector(".marca");
  if (marca && !marca.querySelector(".chip-octubre")) {
    const chip = document.createElement("span");
    chip.className = "chip chip-octubre";
    chip.textContent = "🎃 Octubre";
    marca.appendChild(chip);
  }
}

ambienteOctubre();
cargarCatalogo();
window.setInterval(cargarCatalogo, 30 * 60e3);
