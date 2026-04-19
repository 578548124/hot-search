const CACHE = 'hot-search-v1';
const urls = ['/index.html', '/manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(urls)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.url.startsWith('https://api.')) {
    e.respondWith(
      fetch(e.request).catch(() => new Response('[]', { headers: { 'Content-Type': 'application/json' } }))
    );
  }
});
