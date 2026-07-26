/* ═══════════════════════════════════════════════════════════════
   MUDDO AGRO — CONFIRM MODAL
   Replaces native confirm() with a proper on-brand modal.

   USAGE — on any form that currently has onsubmit="return confirm('...')":
     <form method="POST" action="..."
           class="js-confirm-submit"
           data-confirm-title="Delete this product?"
           data-confirm-body="This can't be undone. '{{ p.name }}' will be
             permanently removed from the catalogue.">
       {% csrf_token %}
       <button type="submit">...</button>
     </form>
   Just remove the old onsubmit="return confirm(...)" attribute and add
   class="js-confirm-submit" + the two data- attributes instead.
   ═══════════════════════════════════════════════════════════════ */

(function () {
  "use strict";

  let pendingForm = null;

  function ensureModal() {
    if (document.getElementById("confirmModalOverlay")) return;
    const el = document.createElement("div");
    el.id = "confirmModalOverlay";
    el.style.cssText = "display:none;position:fixed;inset:0;background:rgba(8,10,9,.55);z-index:5000;align-items:center;justify-content:center;padding:20px;";
    el.innerHTML = `
      <div style="background:var(--bg-card,#fff);border-radius:18px;padding:28px;max-width:420px;width:100%;box-shadow:0 24px 70px rgba(0,0,0,.3);border:1.5px solid var(--border-color,#e2e6ec);font-family:var(--font-body,'DM Sans',sans-serif)">
        <div style="width:44px;height:44px;border-radius:12px;background:#fce8e2;color:#c62828;display:flex;align-items:center;justify-content:center;font-size:1.15rem;margin-bottom:14px">
          <svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
        </div>
        <h3 id="confirmModalTitle" style="font-family:var(--font-heading,'DM Sans',sans-serif);font-size:1.05rem;font-weight:800;color:var(--text-primary,#10151a);margin:0 0 8px">Are you sure?</h3>
        <p id="confirmModalBody" style="font-size:.88rem;color:var(--text-muted,#667079);line-height:1.6;margin:0 0 22px"></p>
        <div style="display:flex;gap:10px;justify-content:flex-end">
          <button type="button" id="confirmModalCancel" style="padding:9px 18px;border-radius:10px;border:1.5px solid var(--border-color,#e2e6ec);background:transparent;color:var(--text-secondary,#33404a);font-weight:700;font-size:.87rem;cursor:pointer">Cancel</button>
          <button type="button" id="confirmModalOk" style="padding:9px 18px;border-radius:10px;border:none;background:#e53935;color:#fff;font-weight:700;font-size:.87rem;cursor:pointer">Yes, delete</button>
        </div>
      </div>`;
    document.body.appendChild(el);

    el.addEventListener("click", (e) => { if (e.target === el) closeModal(); });
    document.getElementById("confirmModalCancel").addEventListener("click", closeModal);
    document.getElementById("confirmModalOk").addEventListener("click", () => {
      const form = pendingForm;
      closeModal();
      if (form) HTMLFormElement.prototype.submit.call(form);
    });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });
  }

  function openModal(form) {
    ensureModal();
    pendingForm = form;
    document.getElementById("confirmModalTitle").textContent = form.dataset.confirmTitle || "Are you sure?";
    document.getElementById("confirmModalBody").textContent = form.dataset.confirmBody || "This action cannot be undone.";
    document.getElementById("confirmModalOverlay").style.display = "flex";
  }

  function closeModal() {
    const el = document.getElementById("confirmModalOverlay");
    if (el) el.style.display = "none";
    pendingForm = null;
  }

  document.addEventListener("submit", function (e) {
    const form = e.target;
    if (form.classList && form.classList.contains("js-confirm-submit") && !form.dataset.confirmed) {
      e.preventDefault();
      openModal(form);
    }
  }, true);
})();
