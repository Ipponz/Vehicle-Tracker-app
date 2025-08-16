const CACHE_NAME = 'vehicle-tracker-cache-v2';

const urlsToCache = [
  '/',  // homepage
  '/static/manifest.json',
  '/static/custom.css',
  '/static/icons/icon-left-192.png',
  '/static/icons/icon-left-512.png',
  '/static/icons/icon-right-192.png',
  '/static/icons/icon-right-512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install event - cache all assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('Caching app files...');
      return cache.addAll(urlsToCache);
    })
  );
});

// Fetch event - return cached files if offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

// Activate event - clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Deleting old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
});
