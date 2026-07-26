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
})();
