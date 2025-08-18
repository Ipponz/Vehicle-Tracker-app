const CACHE_NAME = "vehicle-tracker-v1";
const STATIC_ASSETS = [
  "/static/custom.css",
  "/static/manifest.json",
  "/static/icons/icon-left-192.png",
  "/static/icons/icon-left-512.png",
  "/static/icons/icon-right-192.png",
  "/static/icons/icon-right-512.png"
];

// Install event - cache static assets
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

// Activate event - cleanup old caches
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
});

// Fetch event - only serve cached static files
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);

  // Only cache files inside /static/
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      caches.match(event.request).then(resp => {
        return resp || fetch(event.request);
      })
    );
  } else {
    // Always go to network for everything else (Flask routes)
    event.respondWith(fetch(event.request));
  }
});
