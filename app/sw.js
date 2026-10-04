/* Generado al construir. No editar a mano. */
const CACHE = "miku-casa-20261002a";
const ARCHIVOS = ["/assets/index-DNSr63o3.js","/assets/index-KNGioBNV.css","/extras.js","/extras.css","/assets/live2d-DRgFClZN.js","/assets/nunito-latin-400-normal-DKg4f3fz.woff","/assets/nunito-latin-400-normal-r8SDr6Up.woff2","/assets/nunito-latin-700-normal-Dort48En.woff2","/assets/nunito-latin-700-normal-OcDqTBcA.woff","/assets/nunito-latin-800-normal-D-J0wlBY.woff","/assets/nunito-latin-800-normal-Dz8SOQK_.woff2","/assets/nunito-latin-ext-400-normal-CjMJVfGn.woff","/assets/nunito-latin-ext-400-normal-i-8OOpdj.woff2","/assets/nunito-latin-ext-700-normal-BWeMsAzO.woff2","/assets/nunito-latin-ext-700-normal-D4woHhbd.woff","/assets/nunito-latin-ext-800-normal-CDcxIxx8.woff","/assets/nunito-latin-ext-800-normal-CtU8tJOV.woff2","/dias/2026-09-25.json","/dias/manifiesto.json","/fondos/01-puerro.png","/fondos/02-coletas-estrellas.png","/fondos/03-concierto.png","/fondos/04-cyber.png","/fondos/05-snow.png","/icons/favicon.png","/icons/icon-192.png","/icons/icon-512-maskable.png","/icons/icon-512.png","/index.html","/manifest.webmanifest","/mikuverse.json","/sprites/01-pixel.png","/sprites/02-chibi.png","/sprites/03-samurai.png","/sprites/04-cyberpunk.png","/sprites/05-bruja.png","/sprites/06-sakura.png","/sprites/07-carreras.png","/sprites/08-sirena.png","/sprites/09-astronauta.png","/sprites/10-colombiana.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ARCHIVOS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const claves = await caches.keys();
    await Promise.all(
      claves
        .filter((clave) => clave.startsWith("miku-casa-") && clave !== CACHE)
        .map((clave) => caches.delete(clave)),
    );
    await self.clients.claim();
    const clientes = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const cliente of clientes) {
      cliente.postMessage({ tipo: "actualizada" });
    }
  })());
});

async function redLuegoCache(request, nombre) {
  const cache = await caches.open(nombre);
  try {
    const fresco = await fetch(request);
    if (fresco && fresco.ok) await cache.put(request, fresco.clone());
    return fresco;
  } catch (error) {
    const guardado = await cache.match(request);
    if (guardado) return guardado;
    return new Response("Sin conexión", { status: 503, headers: { "Content-Type": "text/plain; charset=utf-8" } });
  }
}

async function cacheLuegoRed(request, nombre) {
  const cache = await caches.open(nombre);
  const guardado = await cache.match(request);
  if (guardado) return guardado;
  const fresco = await fetch(request);
  if (fresco && (fresco.ok || fresco.type === "opaque")) {
    await cache.put(request, fresco.clone());
  }
  return fresco;
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  const ruta = url.pathname;
  if (ruta.startsWith("/live2d/") || ruta.startsWith("/cubism/")) {
    event.respondWith(cacheLuegoRed(request, "miku-modelo-v1"));
    return;
  }
  if (
    ruta === "/mikuverse.json" ||
    ruta.startsWith("/sprites/") ||
    ruta.startsWith("/fondos/") ||
    ruta.startsWith("/dias/") ||
    ruta.startsWith("/frases/") ||
    ruta.startsWith("/accesorios/")
  ) {
    event.respondWith(redLuegoCache(request, CACHE));
    return;
  }
  if (request.mode === "navigate") {
    event.respondWith(redLuegoCache(new Request("/index.html"), CACHE));
    return;
  }
  event.respondWith(cacheLuegoRed(request, CACHE));
});
