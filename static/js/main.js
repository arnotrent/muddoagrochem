(function () {
  "use strict";

  // ── SCROLL PROGRESS BAR ──────────────────────────────
  const prog = document.querySelector('.scroll-progress');
  if (prog) {
    window.addEventListener('scroll', () => {
      const pct = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
      prog.style.width = Math.min(100, pct) + '%';
    }, { passive: true });
  }

  // ── NAVBAR SHADOW ────────────────────────────────────
  const navbar = document.getElementById('navbar');
  if (navbar) window.addEventListener('scroll', () => navbar.classList.toggle('scrolled', window.scrollY > 20), { passive: true });

  // ── HAMBURGER / MOBILE DRAWER ────────────────────────
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  function closeMenu() {
    mobileMenu?.classList.remove('open'); hamburger?.classList.remove('open');
    hamburger?.setAttribute('aria-expanded', 'false'); document.body.style.overflow = '';
  }
  function toggleMenu() {
    const open = mobileMenu?.classList.toggle('open');
    hamburger?.classList.toggle('open', open);
    hamburger?.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  }
  hamburger?.addEventListener('click', toggleMenu);
  document.addEventListener('click', e => {
    if (mobileMenu?.classList.contains('open') && !mobileMenu.contains(e.target) && !hamburger.contains(e.target)) closeMenu();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
  window.closeMenu = closeMenu;

  // ── SCROLL REVEAL ────────────────────────────────────
  const reveals = document.querySelectorAll('[data-reveal]');
  if (reveals.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          const delay = parseInt(en.target.dataset.revealDelay || '0', 10);
          setTimeout(() => en.target.classList.add('revealed'), delay);
          io.unobserve(en.target);
        }
      });
    }, { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(el => io.observe(el));
  }

  // ── BACK TO TOP ──────────────────────────────────────
  const btt = document.getElementById('backToTop');
  if (btt) {
    window.addEventListener('scroll', () => btt.classList.toggle('show', window.scrollY > 400), { passive: true });
    btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // ── COUNT-UP STATS ───────────────────────────────────
  function animateCount(el) {
    const target = parseInt(el.dataset.target || el.textContent, 10);
    if (isNaN(target)) return;
    const start = Date.now(), duration = 1100;
    const tick = () => {
      const p = Math.min((Date.now() - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + (el.dataset.suffix || '');
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }
  document.querySelectorAll('.count-up').forEach(el => {
    const io = new IntersectionObserver(entries => { if (entries[0].isIntersecting) { animateCount(el); io.disconnect(); } }, { threshold: .5 });
    io.observe(el);
  });

  // ── GLOBAL SEARCH SUGGEST ────────────────────────────
  const searchInput = document.getElementById('globalSearchInput');
  const searchBox = document.getElementById('searchSuggestions');
  if (searchInput && searchBox) {
    let t;
    searchInput.addEventListener('input', () => {
      clearTimeout(t);
      const q = searchInput.value.trim();
      if (!q) { searchBox.innerHTML = ''; searchBox.style.display = 'none'; return; }
      t = setTimeout(() => fetch('/api/search/?q=' + encodeURIComponent(q)).then(r => r.json()).then(data => {
        if (!data.length) { searchBox.innerHTML = ''; searchBox.style.display = 'none'; return; }
        searchBox.style.display = 'block';
        searchBox.innerHTML = data.slice(0, 6).map(p =>
          `<a href="/product/${p.id}/" style="display:flex;gap:10px;padding:9px 14px;border-bottom:1px solid var(--border);text-decoration:none">
            <img src="${p.image}" style="width:34px;height:34px;border-radius:7px;object-fit:cover" onerror="this.style.display='none'">
            <div><div style="font-size:.85rem;font-weight:600;color:var(--text-1)">${p.name}</div><div style="font-size:.72rem;color:var(--text-3)">${p.category}</div></div>
          </a>`).join('');
      }).catch(() => {}), 250);
    });
    document.addEventListener('click', e => { if (!searchInput.closest('form')?.contains(e.target)) { searchBox.innerHTML = ''; searchBox.style.display = 'none'; } });
  }

  // ── QUICK VIEW MODAL (product cards) ─────────────────
  window.openModal = function (d) {
    const o = document.getElementById('modalOverlay'); if (!o) return;
    document.getElementById('modalImg').src = d.img || '';
    document.getElementById('modalName').textContent = d.name || '';
    document.getElementById('modalDesc').textContent = d.desc || '';
    document.getElementById('modalIngr').textContent = d.ingr || '—';
    document.getElementById('modalForm').textContent = d.form || '—';
    document.getElementById('modalCrops').textContent = d.crops || '—';
    document.getElementById('modalDose').textContent = d.dose || '—';
    document.getElementById('modalPack').textContent = d.pack || '—';
    document.getElementById('modalViewBtn').href = '/product/' + d.id + '/';
    document.getElementById('modalEnqBtn').href = '/contact/?subject=Product+Enquiry';
    o.classList.add('open'); document.body.style.overflow = 'hidden';
  };
  window.closeModal = function () {
    document.getElementById('modalOverlay')?.classList.remove('open');
    document.body.style.overflow = '';
  };
  document.addEventListener('click', e => {
    const btn = e.target.closest('.quick-view-btn');
    if (btn) {
      const c = btn.closest('.product-card');
      if (c) openModal({ id: c.dataset.id, name: c.dataset.name, cat: c.dataset.cat, desc: c.dataset.desc, img: c.dataset.img, ingr: c.dataset.ingr, form: c.dataset.form, crops: c.dataset.crops, dose: c.dataset.dose, pack: c.dataset.pack });
    }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') window.closeModal(); });

  // ── NEWSLETTER ───────────────────────────────────────
  function getCookie(name) { const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)')); return m ? decodeURIComponent(m[1]) : ''; }
  document.getElementById('nlForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const btn = this.querySelector('button'), email = this.querySelector('[name=email]').value;
    const orig = btn.innerHTML; btn.innerHTML = '<svg class="icon icon-spin" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" stroke-opacity=".25"/><path d="M12 2a10 10 0 0 1 10 10"/></svg>';
    try {
      const r = await fetch('/subscribe/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify({ email }) });
      const d = await r.json();
      const checkSvg = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
      const timesSvg = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
      btn.innerHTML = d.ok ? checkSvg : timesSvg;
      setTimeout(() => { btn.innerHTML = orig; }, 3000);
    } catch { btn.innerHTML = orig; }
  });

  // ── STICKY NAV SHADOW (fallback id) ──────────────────
  const nav = document.querySelector('.navbar');
  if (nav) window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 10), { passive: true });
})();
