// Service Worker - 只缓存静态资源，不拦截任何 API 请求
const CACHE = 'hot-search-v4';
const urls = ['/index.html', '/manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(urls)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// 只缓存同源静态资源，外部 API（含 newsnow.busiyi.world）一律放行
self.addEventListener('fetch', e => {
  const url = e.request.url;
  // 不拦截任何外部 API 请求
  if (url.includes('newsnow.busiyi.world') ||
      url.includes('zj.v.api.aa1.cn') ||
      url.startsWith('https://api.') ||
      url.startsWith('http://api.')) {
    return;
  }
  // 同源静态资源走缓存
  if (url.includes(self.location.origin) || url.startsWith('/')) {
    e.respondWith(
      caches.match(e.request).then(cached => cached || fetch(e.request))
    );
  }
});
