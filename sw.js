const CACHE = 'hot-search-v2';
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

// 关键修复：不再拦截外部 API 请求，让 JSONP 正常执行
self.addEventListener('fetch', e => {
  const url = e.request.url;
  // 只缓存同源静态资源，不碰外部 API 请求
  if (!url.startsWith('https://zj.v.api.aa1.cn') &&
      !url.startsWith('https://zj.v.api.aa1.cn')) {
    e.respondWith(
      caches.match(e.request).then(cached => cached || fetch(e.request))
    );
  }
  // 外部 API（JSONP）直接放行，不拦截
});
