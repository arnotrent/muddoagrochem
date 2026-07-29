(function () {
  'use strict';
  const KEY = 'muddo-theme';
  function getStored() { try { return localStorage.getItem(KEY) || 'light'; } catch { return 'light'; } }
  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem(KEY, theme); } catch {}
    document.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
  }
  function toggle() {
    const next = getStored() === 'dark' ? 'light' : 'dark';
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;inset:0;z-index:99999;pointer-events:none;background:' + (next === 'dark' ? '#0F172A' : '#F8FAFC') + ';opacity:0;transition:opacity 180ms ease;';
    document.body.appendChild(overlay);
    requestAnimationFrame(() => {
      overlay.style.opacity = '.35';
      setTimeout(() => { apply(next); overlay.style.opacity = '0'; setTimeout(() => overlay.remove(), 220); }, 80);
    });
  }
  if (getStored() === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
  function init() {
    document.querySelectorAll('.theme-toggle, .theme-toggle-nav, [data-theme-toggle]').forEach(btn => {
      btn.addEventListener('click', e => { e.preventDefault(); toggle(); });
    });
    apply(getStored());
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  window.toggleTheme = toggle;
  window.getCurrentTheme = getStored;

  // ── MOBILE SIDEBAR TOGGLE (admin panel + agent portal) ───────────
  // Both use the shared `.admin-sidebar` component, which is hidden by
  // default under ~767px (see responsive.css). Any element carrying
  // [data-sidebar-toggle] flips it open as a slide-over panel.
  function initSidebarToggle() {
    document.querySelectorAll('[data-sidebar-toggle]').forEach(btn => {
      btn.addEventListener('click', e => {
        e.preventDefault();
        document.querySelector('.admin-sidebar')?.classList.toggle('mobile-open');
      });
    });
    document.addEventListener('click', e => {
      const sb = document.querySelector('.admin-sidebar.mobile-open');
      if (sb && !sb.contains(e.target) && !e.target.closest('[data-sidebar-toggle]')) {
        sb.classList.remove('mobile-open');
      }
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') document.querySelector('.admin-sidebar.mobile-open')?.classList.remove('mobile-open');
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initSidebarToggle); else initSidebarToggle();
})();
