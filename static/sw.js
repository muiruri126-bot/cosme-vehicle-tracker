/*
 * Service Worker – Vehicle Request Tracker PWA
 * Enables offline support and "Install App" capability.
 */

const CACHE_NAME = "vrt-cache-v1";

// Core assets to cache for offline use
const PRECACHE_URLS = [
  "/",
  "/login",
  "/static/style.css",
  "/static/validate.js",
  "/static/icons/icon-192x192.png",
  "/static/icons/icon-512x512.png",
  "/static/manifest.json",
  "/offline",
];

/* ── Install: pre-cache core assets ─────────────────────────────── */
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[SW] Pre-caching core assets");
      return cache.addAll(PRECACHE_URLS);
    })
  );
  self.skipWaiting();
});

/* ── Activate: clean up old caches ──────────────────────────────── */
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    )
  );
  self.clients.claim();
});

/* ── Fetch: network-first with cache fallback ───────────────────── */
self.addEventListener("fetch", (event) => {
  const request = event.request;

  // Skip non-GET requests (form submissions, API calls)
  if (request.method !== "GET") return;

  // Skip browser-extension and chrome-extension requests
  if (!request.url.startsWith("http")) return;

  event.respondWith(
    fetch(request)
      .then((response) => {
        // Cache successful responses for static assets
        if (
          response.ok &&
          (request.url.includes("/static/") ||
            request.url.endsWith("/login") ||
            request.url.endsWith("/"))
        ) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Offline: try cache first, then show offline page
        return caches.match(request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;

          // For HTML page requests, show the offline page
          if (request.headers.get("accept")?.includes("text/html")) {
            return caches.match("/offline");
          }
        });
      })
  );
});
