window.toast = (function () {
  let container = null;
  function getContainer() {
    if (!container) { container = document.createElement('div'); container.className = 'flash-wrap'; document.body.appendChild(container); }
    return container;
  }
  const SVG_CHECK_CIRCLE = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>';
  const SVG_EXCLAMATION_CIRCLE = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
  const SVG_INFO_CIRCLE = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
  const SVG_TIMES = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

  function show(message, type = 'info', duration = 3500) {
    const c = getContainer();
    const el = document.createElement('div');
    el.className = `flash-msg ${type}`;
    const icon = type === 'success' ? SVG_CHECK_CIRCLE : type === 'error' ? SVG_EXCLAMATION_CIRCLE : SVG_INFO_CIRCLE;
    el.innerHTML = `${icon}<span style="flex:1">${message}</span><button style="background:none;border:none;cursor:pointer;color:var(--text-3)" onclick="this.closest('.flash-msg').remove()">${SVG_TIMES}</button>`;
    c.appendChild(el);
    setTimeout(() => { el.style.transition = 'opacity .3s,transform .3s'; el.style.opacity = '0'; el.style.transform = 'translateX(30px)'; setTimeout(() => el.remove(), 320); }, duration);
  }
  return { show, success: m => show(m, 'success'), error: m => show(m, 'error'), info: m => show(m, 'info') };
})();

// Lazy image fade-in
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        const img = en.target;
        img.addEventListener('load', () => img.classList.add('loaded'), { once: true });
        io.unobserve(img);
      }
    });
  }, { rootMargin: '100px' });
  document.querySelectorAll('img[loading="lazy"]').forEach(img => io.observe(img));
}

// Native form validation → shake + red border instead of silent failure
document.querySelectorAll('form:not([novalidate])').forEach(form => {
  form.addEventListener('submit', e => {
    const invalids = form.querySelectorAll(':invalid');
    if (invalids.length) {
      invalids[0].focus();
      invalids.forEach(el => {
        el.classList.add('error');
        el.addEventListener('input', () => el.classList.remove('error'), { once: true });
      });
    }
  });
});

document.querySelectorAll('.print-btn').forEach(btn => btn.addEventListener('click', () => window.print()));
