/* Study Hall service worker: network first, so updates show up right away;
   falls back to the last saved copy when the phone is offline.
   Data files named by a content hash (e.g. vocab/data.0123abcdef.json) never change, so they come from
   the saved copy first; saving a new version of one drops the older versions.
   Only this site's own files are cached. Sign-in, progress and AI calls always go to the network. */
const CACHE = "studyhall-v1";
const HASHED = /\.[0-9a-f]{10}\.json$/;
self.addEventListener("install", e => { self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k !== CACHE) await caches.delete(k);
    await self.clients.claim();
  })());
});
self.addEventListener("fetch", e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== self.location.origin) return;
  e.respondWith(HASHED.test(url.pathname) ? cacheFirst(req, url.pathname) : networkFirst(req));
});
async function networkFirst(req) {
  try {
    const res = await fetch(req);
    if (res.ok) { const c = await caches.open(CACHE); c.put(req, res.clone()); }
    return res;
  } catch (err) {
    const hit = await caches.match(req, { ignoreSearch: true });
    if (hit) return hit;
    throw err;
  }
}
async function cacheFirst(req, path) {
  const hit = await caches.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (res.ok) {
    const c = await caches.open(CACHE), stem = path.replace(HASHED, "");
    for (const k of await c.keys()) { const p = new URL(k.url).pathname; if (p !== path && HASHED.test(p) && p.replace(HASHED, "") === stem) await c.delete(k); }
    await c.put(req, res.clone());
  }
  return res;
}
