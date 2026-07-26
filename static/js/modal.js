/* Kept for backward compatibility with any template still linking modal.js.
   The actual quick-view modal logic now lives in main.js (openModal/closeModal).
   This file only adds left/right keyboard navigation between product cards
   when the modal is open. */
(function () {
  let cards = [];
  let idx = 0;
  function collect() { cards = [...document.querySelectorAll('.product-card[data-id]')]; }
  document.addEventListener('DOMContentLoaded', collect);
  document.addEventListener('click', e => {
    const btn = e.target.closest('.quick-view-btn');
    if (btn) { collect(); idx = cards.indexOf(btn.closest('.product-card')); }
  });
  document.addEventListener('keydown', e => {
    const overlay = document.getElementById('modalOverlay');
    if (!overlay || !overlay.classList.contains('open') || !cards.length) return;
    if (e.key === 'ArrowRight') { idx = (idx + 1) % cards.length; cards[idx].querySelector('.quick-view-btn')?.click(); }
    if (e.key === 'ArrowLeft')  { idx = (idx - 1 + cards.length) % cards.length; cards[idx].querySelector('.quick-view-btn')?.click(); }
  });
})();
