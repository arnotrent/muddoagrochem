const CACHE_NAME = 'muddo-agro-v2';
const STATIC_CACHE = 'muddo-static-v2';

const PRECACHE = [
  '/', '/pesticides/', '/herbicides/', '/fungicides/', '/other-products/',
  '/distributors/', '/contact/',
  '/static/css/theme_vars.css', '/static/css/style.css', '/static/css/typography.css',
  '/static/css/responsive.css', '/static/css/animations.css',
  '/static/js/main.js', '/static/js/modal.js', '/static/js/theme.js',
  '/static/images/logo_full.png', '/static/manifest.json',
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(STATIC_CACHE).then(cache => cache.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME && k !== STATIC_CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  if (request.method !== 'GET') return;
  if (['/admin-panel', '/agent', '/api/', '/django-admin'].some(p => url.pathname.startsWith(p))) return;

  event.respondWith(
    fetch(request).then(response => {
      if (response.ok) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
      }
      return response;
    }).catch(() => caches.match(request).then(cached => cached || (request.headers.get('accept')?.includes('text/html') ? caches.match('/') : undefined)))
  );
});
