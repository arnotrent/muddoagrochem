/* ══════════════════════════════════════════════════════════════════
   MUDDO AGRO — ADMIN ⇄ AGENT COMMUNICATION SYSTEM  v7
   Full attachment system: real multi-file upload with progress, a
   unified viewer (image lightbox, PDF/video/audio players, download
   cards for everything else), a Shared Files panel, search, delivery
   ticks, typing indicator and drag-and-drop — all wired to the
   endpoints in apps/messaging/views.py. Original files are NEVER
   converted; the server always returns the original filename/type.
   ══════════════════════════════════════════════════════════════════ */

function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.content) return meta.content;
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

const TICK_SENT = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:.75;vertical-align:-1px"><polyline points="20 6 9 17 4 12"/></svg>';
const TICK_SEEN = '<svg class="icon msg-tick-seen" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px"><polyline points="1 13 5 17 11 9"/><polyline points="7 13 11 17 21 5"/></svg>';
const TICK_CLOCK = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:.6;vertical-align:-1px"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>';

const FILE_ICONS = {
  document: '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
  pdf: '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
  spreadsheet: '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>',
  presentation: '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="13" rx="1"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
  archive: '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5V8z"/><path d="M3 8l9 5 9-5"/></svg>',
  video: '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>',
  audio: '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
  other: '<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>',
};
function iconFor(kind){ return FILE_ICONS[kind] || FILE_ICONS.other; }

const EMOJI_SET = ['😀','😂','😊','😍','😘','🤔','😉','😅','😢','😭','😡','👍','👎','🙏','👏','💪','🤝','✅','❌','⚠️','🔥','💧','🌱','🌾','🐛','🚚','📦','📅','⏰','📍','💰','📞','✉️','😴','🎉'];

class MuddoChat {
  constructor() {
    this.currentWith  = null;  // {id, role, name}
    this.lastMsgId    = 0;
    this.pollInterval = null;
    this.csrfToken    = getCsrfToken();
    this.container    = document.getElementById('chatMessages');
    this.inputBox     = document.getElementById('chatInput');
    this.sendBtn      = document.getElementById('chatSendBtn');
    this.attachBtn    = document.getElementById('chatAttachBtn');
    this.attachInput  = document.getElementById('chatAttachInput');
    this.attachPreview= document.getElementById('chatAttachPreview');
    this.emojiBtn     = document.getElementById('chatEmojiBtn');
    this.emojiPanel   = document.getElementById('chatEmojiPanel');
    this.replyBar     = document.getElementById('chatReplyBar');
    this.backBtn      = document.getElementById('chatBackBtn');
    this.layoutEl     = document.querySelector('.chat-layout');
    this.headerName   = document.getElementById('chatHeaderName');
    this.headerStatus = document.getElementById('chatHeaderStatus');
    this.headerAvatar = document.getElementById('chatHeaderAvatar');
    this.chatMain     = document.getElementById('chatMainArea');
    this.chatEmpty    = document.getElementById('chatEmptyState');
    this.searchBtn    = document.getElementById('chatSearchBtn');
    this.searchBar    = document.getElementById('chatSearchBar');
    this.searchInput  = document.getElementById('chatSearchInput');
    this.searchResults= document.getElementById('chatSearchResults');
    this.infoBtn      = document.getElementById('chatInfoBtn');
    this.infoPanel    = document.getElementById('chatInfoPanel');
    this.infoClose    = document.getElementById('chatInfoClose');
    this.dropZone      = document.getElementById('chatDropZone');
    this.myInitial    = document.body.dataset.userInitial || 'U';
    this.myId         = parseInt(document.body.dataset.userId || '0', 10);
    this.myRole       = document.body.dataset.userRole || 'agent';

    this.lastDateKey   = null;
    this.lastSenderKey = null;
    this.lastRow       = null;
    this.pendingFiles  = [];   // {file, tempId, xhr, attachmentId, status}
    this.replyingTo    = null;
    this.sending       = false;
    this.trackIds      = [];   // my own sent message ids awaiting delivery/read ticks
    this.typingTimer   = null;
    this.lastTypingSent= 0;

    if (this.sendBtn)  this.sendBtn.addEventListener('click', () => this.sendMessage());
    if (this.inputBox) {
      this.inputBox.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.sendMessage(); }
      });
      this.inputBox.addEventListener('input', () => {
        this.inputBox.style.height = 'auto';
        this.inputBox.style.height = Math.min(this.inputBox.scrollHeight, 120) + 'px';
        this.notifyTyping();
      });
    }
    if (this.attachBtn && this.attachInput) {
      this.attachBtn.addEventListener('click', () => this.attachInput.click());
      this.attachInput.addEventListener('change', () => {
        [...(this.attachInput.files || [])].forEach(f => this.queueFile(f));
        this.attachInput.value = '';
      });
    }
    if (this.emojiBtn && this.emojiPanel) {
      if (!this.emojiPanel.dataset.built) {
        this.emojiPanel.innerHTML = EMOJI_SET.map(e => `<button type="button" class="emoji-item">${e}</button>`).join('');
        this.emojiPanel.dataset.built = '1';
      }
      this.emojiBtn.addEventListener('click', e => { e.stopPropagation(); this.emojiPanel.classList.toggle('open'); });
      this.emojiPanel.addEventListener('click', e => {
        const btn = e.target.closest('.emoji-item');
        if (!btn || !this.inputBox) return;
        const start = this.inputBox.selectionStart ?? this.inputBox.value.length;
        const end = this.inputBox.selectionEnd ?? this.inputBox.value.length;
        const val = this.inputBox.value;
        this.inputBox.value = val.slice(0, start) + btn.textContent + val.slice(end);
        const pos = start + btn.textContent.length;
        this.inputBox.setSelectionRange(pos, pos);
        this.inputBox.focus();
      });
      document.addEventListener('click', e => {
        if (!this.emojiPanel.contains(e.target) && e.target !== this.emojiBtn) this.emojiPanel.classList.remove('open');
      });
    }
    if (this.backBtn) this.backBtn.addEventListener('click', () => this.layoutEl?.classList.remove('chat-mobile-conversation-open'));

    document.querySelectorAll('.chat-contact[data-id]').forEach(el => el.addEventListener('click', () => this.selectContact(el)));

    if (this.container) {
      this.container.addEventListener('click', e => {
        const rbtn = e.target.closest('.msg-reply-btn');
        if (rbtn) { this.startReply(rbtn.dataset.id, rbtn.dataset.preview, rbtn.dataset.senderRole); return; }
        const att = e.target.closest('.msg-attachment[data-preview]');
        if (att) { e.preventDefault(); this.openViewerFromEl(att); }
      });
    }

    if (this.searchBtn) this.searchBtn.addEventListener('click', () => this.toggleSearch());
    if (this.searchInput) {
      let t;
      this.searchInput.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => this.runSearch(), 260); });
    }
    if (this.infoBtn) this.infoBtn.addEventListener('click', () => this.openInfoPanel());
    if (this.infoClose) this.infoClose.addEventListener('click', () => this.infoPanel?.classList.remove('open'));

    this.initDropZone();
    this.initViewer();

    const hash = window.location.hash.replace('#chat-', '');
    if (hash) {
      const preselect = document.querySelector(`.chat-contact[data-id="${hash}"]`);
      if (preselect) this.selectContact(preselect);
    }

    this.pollUnread();
    this.pollPresence();
    setInterval(() => this.pollUnread(), 6000);
    setInterval(() => this.pollPresence(), 15000);
  }

  // ───────────────────────── contact selection ─────────────────────────
  selectContact(el) {
    document.querySelectorAll('.chat-contact').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    el.querySelector('.chat-unread-badge')?.remove();

    this.currentWith = { id: parseInt(el.dataset.id, 10), role: el.dataset.role || 'agent', name: el.dataset.name || 'User', avatar: el.dataset.avatar || '' };
    const isBroadcast = this.currentWith.role === 'broadcast';

    if (this.headerName) this.headerName.textContent = this.currentWith.name;
    if (this.headerStatus) {
      if (isBroadcast) this.headerStatus.innerHTML = 'Everyone — admin and all field agents';
      else if (this.currentWith.role === 'admin') this.headerStatus.innerHTML = `<span class="status-dot online"></span> Head Office`;
      else {
        const online = el.dataset.status === 'online';
        const lastSeen = el.dataset.lastSeen || '';
        this.headerStatus.innerHTML = online ? `<span class="status-dot online"></span> Online now` : `<span class="status-dot offline"></span> ${lastSeen ? 'Last seen ' + lastSeen : 'Offline'}`;
      }
    }
    if (this.headerAvatar) this.headerAvatar.innerHTML = this.currentWith.avatar
      ? `<img src="${this.currentWith.avatar}" style="width:100%;height:100%;object-fit:cover;border-radius:50%">`
      : (isBroadcast ? '📢' : this.currentWith.name.charAt(0).toUpperCase());

    if (this.chatMain) this.chatMain.style.display = 'flex';
    if (this.chatEmpty) this.chatEmpty.style.display = 'none';
    this.layoutEl?.classList.add('chat-mobile-conversation-open');
    this.infoPanel?.classList.remove('open');
    this.closeSearch();

    this.lastMsgId = 0; this.lastDateKey = null; this.lastSenderKey = null; this.lastRow = null; this.trackIds = [];
    this.cancelReply();
    this.clearPendingFiles();
    this.container.innerHTML = '';
    this.loadMessages(true);

    clearInterval(this.pollInterval);
    this.pollInterval = setInterval(() => this.loadMessages(false), 3000);
    this.inputBox?.focus();
  }

  async loadMessages(scroll) {
    if (!this.currentWith) return;
    const isBroadcast = this.currentWith.role === 'broadcast';
    try {
      const track = this.trackIds.slice(-40).join(',');
      const url = isBroadcast
        ? `/api/chat/messages/?with_role=broadcast&after=${this.lastMsgId}`
        : `/api/chat/messages/?with_id=${this.currentWith.id}&with_role=${this.currentWith.role}&after=${this.lastMsgId}${track ? '&track=' + track : ''}`;
      const res = await fetch(url);
      if (!res.ok) { console.warn('Chat load failed:', res.status); return; }
      const data = await res.json();
      if (data.messages?.length) {
        data.messages.forEach(m => {
          if (m.id <= this.lastMsgId) return;
          this.lastMsgId = m.id;
          this.appendMessage(m);
          if (m.sender_id === this.myId && m.sender_role === this.myRole) this.trackIds.push(m.id);
        });
        if (scroll) this.scrollBottom();
        else {
          const atBottom = this.container.scrollHeight - this.container.scrollTop - this.container.clientHeight < 80;
          if (atBottom) this.scrollBottom();
        }
      }
      if (data.statuses) Object.entries(data.statuses).forEach(([id, status]) => this.updateTick(id, status));
      this.showTyping(!!data.typing);
      fetch(`/api/chat/mark-read/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
        body: JSON.stringify(isBroadcast ? { from_role: 'broadcast' } : { from_id: this.currentWith.id, from_role: this.currentWith.role })
      }).catch(() => {});
    } catch (e) { console.warn('Chat load error:', e); }
  }

  showTyping(on) {
    let el = document.getElementById('typingIndicatorRow');
    if (on) {
      if (!el) {
        el = document.createElement('div'); el.id = 'typingIndicatorRow'; el.className = 'typing-row';
        el.innerHTML = `<span>${this.escapeHtml(this.currentWith?.name || '')} is typing</span><span class="typing-dots"><i></i><i></i><i></i></span>`;
        this.container.appendChild(el);
        const atBottom = this.container.scrollHeight - this.container.scrollTop - this.container.clientHeight < 120;
        if (atBottom) this.scrollBottom();
      }
    } else el?.remove();
  }

  notifyTyping() {
    if (!this.currentWith || this.currentWith.role === 'broadcast') return;
    const now = Date.now();
    if (now - this.lastTypingSent < 2500) return;
    this.lastTypingSent = now;
    fetch('/api/chat/typing/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
      body: JSON.stringify({ to_id: this.currentWith.id, to_role: this.currentWith.role }) }).catch(() => {});
  }

  // ───────────────────────── rendering ─────────────────────────
  dateKeyFor(d) { return d.toDateString(); }
  dateLabelFor(d) {
    const today = new Date(); const yest = new Date(); yest.setDate(today.getDate() - 1);
    if (this.dateKeyFor(d) === this.dateKeyFor(today)) return 'Today';
    if (this.dateKeyFor(d) === this.dateKeyFor(yest)) return 'Yesterday';
    return d.toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' });
  }

  renderAttachments(m) {
    if (!m.attachments || !m.attachments.length) return '';
    const images = m.attachments.filter(a => a.preview === 'image');
    const others = m.attachments.filter(a => a.preview !== 'image');
    let html = '';
    if (images.length) {
      const cls = images.length === 1 ? 'single' : images.length === 2 ? 'two' : 'grid';
      html += `<div class="msg-img-gallery ${cls}">` + images.map((a, i) =>
        `<div class="msg-attachment" data-preview data-msg-id="${m.id}" data-att-index="${m.attachments.indexOf(a)}"><img class="msg-attachment-img" src="${a.url}" alt="${this.escapeAttr(a.name)}" loading="lazy"></div>`
      ).join('') + '</div>';
    }
    others.forEach(a => {
      html += `<a class="msg-attachment-file msg-attachment" data-preview data-msg-id="${m.id}" data-att-index="${m.attachments.indexOf(a)}" href="${a.url}" ${a.preview ? '' : 'download'}>
        <span class="maf-icon">${iconFor(a.kind)}</span>
        <span class="maf-meta"><span class="maf-name">${this.escapeHtml(a.name)}</span><span class="maf-size">${a.size_h}</span></span>
        <span class="maf-dl" title="Download">⬇</span>
      </a>`;
    });
    return html;
  }

  renderReplyQuote(m) {
    if (!m.reply_to) return '';
    const who = m.reply_to.sender_name || 'them';
    return `<div class="msg-reply-quote"><strong>${this.escapeHtml(who)}</strong>${this.escapeHtml(m.reply_to.content || '')}</div>`;
  }

  avatarHtml(url, initial) { return url ? `<img src="${url}" style="width:100%;height:100%;object-fit:cover;border-radius:50%">` : initial; }

  tickHtml(status) { return status === 'read' ? TICK_SEEN : status === 'delivered' ? TICK_SENT : TICK_CLOCK; }

  appendMessage(m) {
    const isSent = (m.sender_role === this.myRole && m.sender_id === this.myId);
    const isGroup = this.currentWith?.role === 'broadcast';
    const initial = isSent ? this.myInitial : ((m.sender_name || '?').charAt(0).toUpperCase());
    const avatarUrl = isSent ? null : m.sender_avatar_url;
    const msgDate = new Date(m.created_at);
    const dateKey = this.dateKeyFor(msgDate);
    const time = msgDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const typingRow = document.getElementById('typingIndicatorRow');
    if (dateKey !== this.lastDateKey) {
      const sep = document.createElement('div'); sep.className = 'chat-date-sep'; sep.textContent = this.dateLabelFor(msgDate);
      typingRow ? this.container.insertBefore(sep, typingRow) : this.container.appendChild(sep);
      this.lastDateKey = dateKey; this.lastSenderKey = null;
    }
    const senderKey = `${m.sender_role}:${m.sender_id}`;
    const grouped = senderKey === this.lastSenderKey;
    if (grouped && this.lastRow) { const prevSlot = this.lastRow.querySelector('.msg-avatar-slot'); if (prevSlot) prevSlot.style.visibility = 'hidden'; this.lastRow.style.marginBottom = '2px'; }

    const wrapper = document.createElement('div');
    wrapper.className = `msg-row ${isSent ? 'sent' : 'received'}`;
    wrapper.dataset.id = m.id;
    if (grouped) wrapper.style.marginTop = '2px';
    const senderLabel = (isGroup && !isSent && !grouped) ? `<div class="msg-sender-name">${this.escapeHtml(m.sender_name || '')}</div>` : '';
    const previewText = (m.content || (m.attachments?.length ? '📎 ' + m.attachments.length + ' attachment' + (m.attachments.length !== 1 ? 's' : '') : '')).substring(0, 60);

    wrapper.innerHTML = `
      <div class="msg-avatar-slot"><div class="msg-avatar ${isSent ? 'sent-avatar' : ''}">${this.avatarHtml(avatarUrl, initial)}</div></div>
      <div class="msg-hover-actions"><button class="msg-reply-btn" data-id="${m.id}" data-preview="${this.escapeAttr(previewText)}" data-sender-role="${m.sender_role}" title="Reply">${this.replyIconSvg()}</button></div>
      <div class="msg-bubble">${senderLabel}${this.renderReplyQuote(m)}${this.renderAttachments(m)}${m.content ? `<div class="msg-text">${this.escapeHtml(m.content)}</div>` : ''}<span class="msg-time">${time}${isSent ? ' ' + this.tickHtml(m.status) : ''}</span></div>
    `;
    wrapper._msg = m;
    typingRow ? this.container.insertBefore(wrapper, typingRow) : this.container.appendChild(wrapper);
    this.lastSenderKey = senderKey; this.lastRow = wrapper;
  }

  updateTick(id, status) {
    const row = this.container.querySelector(`.msg-row[data-id="${id}"]`);
    const timeEl = row?.querySelector('.msg-time');
    if (!timeEl) return;
    const timeText = timeEl.textContent.trim().split(' ')[0];
    timeEl.innerHTML = `${timeText} ${this.tickHtml(status)}`;
  }

  replyIconSvg() { return '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg>'; }

  startReply(id, preview, senderRole) {
    this.replyingTo = { id, preview, senderRole };
    if (!this.replyBar) return;
    this.replyBar.innerHTML = `<div class="reply-bar-inner"><div><strong>Replying</strong><div class="reply-bar-preview">${this.escapeHtml(preview)}</div></div><button type="button" id="chatReplyCancel">${'<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'}</button></div>`;
    this.replyBar.style.display = 'block';
    document.getElementById('chatReplyCancel')?.addEventListener('click', () => this.cancelReply());
    this.inputBox?.focus();
  }
  cancelReply() { this.replyingTo = null; if (this.replyBar) { this.replyBar.style.display = 'none'; this.replyBar.innerHTML = ''; } }

  // ───────────────────────── attachments: queue + upload ─────────────────────────
  initDropZone() {
    if (!this.chatMain) return;
    let depth = 0;
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
      this.chatMain.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); });
    });
    this.chatMain.addEventListener('dragenter', () => { depth++; if (this.currentWith) this.dropZone?.classList.add('active'); });
    this.chatMain.addEventListener('dragleave', () => { depth = Math.max(0, depth - 1); if (depth === 0) this.dropZone?.classList.remove('active'); });
    this.chatMain.addEventListener('drop', e => {
      depth = 0; this.dropZone?.classList.remove('active');
      if (!this.currentWith) return;
      [...(e.dataTransfer?.files || [])].forEach(f => this.queueFile(f));
    });
  }

  queueFile(file) {
    if (this.pendingFiles.length >= 10) { window.toast?.error?.('You can attach up to 10 files per message.'); return; }
    const tempId = 'tmp' + Math.random().toString(36).slice(2);
    const entry = { file, tempId, attachmentId: null, status: 'uploading', progress: 0, xhr: null };
    this.pendingFiles.push(entry);
    this.renderPendingFiles();
    this.uploadFile(entry);
  }

  uploadFile(entry) {
    const fd = new FormData(); fd.append('file', entry.file);
    const xhr = new XMLHttpRequest(); entry.xhr = xhr;
    xhr.open('POST', '/api/chat/upload/');
    xhr.setRequestHeader('X-CSRFToken', this.csrfToken);
    xhr.upload.onprogress = e => { if (e.lengthComputable) { entry.progress = Math.round((e.loaded / e.total) * 100); this.updatePendingProgress(entry); } };
    xhr.onload = () => {
      let data = {}; try { data = JSON.parse(xhr.responseText || '{}'); } catch (e) {}
      if (xhr.status === 201 && data.attachment) {
        entry.status = 'done'; entry.attachmentId = data.attachment.id; entry.meta = data.attachment; entry.progress = 100;
      } else {
        entry.status = 'error'; entry.error = data.error || 'Upload failed';
      }
      this.renderPendingFiles();
    };
    xhr.onerror = () => { entry.status = 'error'; entry.error = 'Network error'; this.renderPendingFiles(); };
    xhr.send(fd);
  }

  retryFile(tempId) {
    const entry = this.pendingFiles.find(e => e.tempId === tempId);
    if (!entry) return;
    entry.status = 'uploading'; entry.progress = 0; entry.error = null;
    this.renderPendingFiles(); this.uploadFile(entry);
  }

  removePendingFile(tempId) {
    const entry = this.pendingFiles.find(e => e.tempId === tempId);
    if (entry?.xhr && entry.status === 'uploading') entry.xhr.abort();
    if (entry?.attachmentId) fetch(`/api/chat/upload/${entry.attachmentId}/delete/`, { method: 'POST', headers: { 'X-CSRFToken': this.csrfToken } }).catch(() => {});
    this.pendingFiles = this.pendingFiles.filter(e => e.tempId !== tempId);
    this.renderPendingFiles();
  }

  clearPendingFiles() { this.pendingFiles = []; this.renderPendingFiles(); }

  updatePendingProgress(entry) {
    const bar = this.attachPreview?.querySelector(`[data-temp="${entry.tempId}"] .attach-progress-fill`);
    if (bar) bar.style.width = entry.progress + '%';
    const pct = this.attachPreview?.querySelector(`[data-temp="${entry.tempId}"] .attach-progress-pct`);
    if (pct) pct.textContent = entry.progress + '%';
  }

  renderPendingFiles() {
    if (!this.attachPreview) return;
    if (!this.pendingFiles.length) { this.attachPreview.style.display = 'none'; this.attachPreview.innerHTML = ''; return; }
    this.attachPreview.style.display = 'flex';
    this.attachPreview.innerHTML = this.pendingFiles.map(entry => {
      const isImg = entry.file.type.startsWith('image/');
      const thumb = isImg ? `<img class="attach-preview-thumb" src="${URL.createObjectURL(entry.file)}">` : `<span class="attach-preview-icon">${iconFor(entry.meta?.kind || 'other')}</span>`;
      let status = '';
      if (entry.status === 'uploading') status = `<div class="attach-progress"><div class="attach-progress-fill" style="width:${entry.progress}%"></div></div><span class="attach-progress-pct">${entry.progress}%</span>`;
      else if (entry.status === 'error') status = `<span class="attach-error-text">${this.escapeHtml(entry.error || 'Failed')}</span> <button type="button" class="attach-retry" data-retry="${entry.tempId}">Retry</button>`;
      else status = `<span class="attach-ok">✓</span>`;
      return `<div class="attach-preview-item" data-temp="${entry.tempId}">
        ${thumb}
        <div class="attach-preview-info"><span class="attach-preview-name">${this.escapeHtml(entry.file.name)}</span>${status}</div>
        <button type="button" class="attach-remove" data-remove="${entry.tempId}">✕</button>
      </div>`;
    }).join('');
    this.attachPreview.querySelectorAll('[data-remove]').forEach(b => b.addEventListener('click', () => this.removePendingFile(b.dataset.remove)));
    this.attachPreview.querySelectorAll('[data-retry]').forEach(b => b.addEventListener('click', () => this.retryFile(b.dataset.retry)));
  }

  // ───────────────────────── sending ─────────────────────────
  setSendingState(isSending) {
    this.sending = isSending;
    if (this.sendBtn) this.sendBtn.disabled = isSending;
  }

  async sendMessage() {
    if (this.sending) return;
    const content = this.inputBox?.value.trim() || '';
    const uploading = this.pendingFiles.some(e => e.status === 'uploading');
    if (uploading) { window.toast?.info?.('Please wait for the attachment to finish uploading…'); return; }
    const readyAttachments = this.pendingFiles.filter(e => e.status === 'done').map(e => e.attachmentId);
    const failed = this.pendingFiles.filter(e => e.status === 'error');
    if (!content && !readyAttachments.length) { if (failed.length) window.toast?.error?.('Remove or retry the failed attachment first.'); return; }
    if (!this.currentWith) return;

    const replyId = this.replyingTo?.id || null;
    const isBroadcast = this.currentWith.role === 'broadcast';
    const clientId = 'c' + Date.now() + Math.random().toString(36).slice(2, 8);
    this.setSendingState(true);
    this.inputBox.value = ''; this.inputBox.style.height = 'auto';
    this.clearPendingFiles(); this.cancelReply();

    const body = isBroadcast
      ? { broadcast: true, content, reply_to: replyId, attachment_ids: readyAttachments, client_id: clientId }
      : { to_id: this.currentWith.id, to_role: this.currentWith.role, content, reply_to: replyId, attachment_ids: readyAttachments, client_id: clientId };
    try {
      const res = await fetch('/api/chat/send/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken }, body: JSON.stringify(body) });
      const data = await res.json();
      if (!res.ok) { window.toast?.error?.(data.error || 'Message failed to send — please try again.'); return; }
      if (data.message) {
        this.appendMessage(data.message);
        if (data.message.sender_id === this.myId && data.message.sender_role === this.myRole) this.trackIds.push(data.message.id);
        this.lastMsgId = Math.max(this.lastMsgId, data.message.id);
        this.scrollBottom();
        const contactEl = document.querySelector(`.chat-contact[data-id="${this.currentWith.id}"][data-role="${this.currentWith.role}"]`);
        const preview = contactEl?.querySelector('.chat-contact-preview');
        const previewText = content || (data.message.attachments?.length ? '📎 ' + data.message.attachments.length + ' attachment' + (data.message.attachments.length !== 1 ? 's' : '') : '');
        if (preview) preview.innerHTML = '<span class="you-prefix">You: </span>' + this.escapeHtml(previewText.substring(0, 40));
        const timeEl = contactEl?.querySelector('.chat-contact-time');
        if (timeEl) timeEl.textContent = new Date(data.message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
    } catch (e) { console.error(e); window.toast?.error?.('Message failed to send — please try again.'); }
    finally { this.setSendingState(false); }
  }

  scrollBottom() { if (this.container) this.container.scrollTop = this.container.scrollHeight; }

  // ───────────────────────── search ─────────────────────────
  toggleSearch() {
    if (!this.searchBar) return;
    const open = this.searchBar.classList.toggle('open');
    if (open) this.searchInput?.focus(); else { this.searchInput.value = ''; this.searchResults.innerHTML = ''; }
  }
  closeSearch() { this.searchBar?.classList.remove('open'); if (this.searchInput) this.searchInput.value = ''; if (this.searchResults) this.searchResults.innerHTML = ''; }
  async runSearch() {
    const q = this.searchInput.value.trim();
    if (!this.currentWith || q.length < 2) { this.searchResults.innerHTML = ''; return; }
    const res = await fetch(`/api/chat/search/?with_id=${this.currentWith.id}&with_role=${this.currentWith.role}&q=${encodeURIComponent(q)}`);
    const data = await res.json();
    this.searchResults.innerHTML = (data.results || []).map(r => `<div class="chat-search-hit" data-id="${r.id}"><strong>${this.escapeHtml(r.sender_name)}</strong><span>${this.escapeHtml(r.snippet)}</span><small>${new Date(r.created_at).toLocaleDateString()}</small></div>`).join('') || '<div class="chat-search-empty">No matches.</div>';
    this.searchResults.querySelectorAll('.chat-search-hit').forEach(el => el.addEventListener('click', () => this.jumpToMessage(el.dataset.id)));
  }
  async jumpToMessage(id) {
    this.closeSearch();
    const res = await fetch(`/api/chat/messages/?with_id=${this.currentWith.id}&with_role=${this.currentWith.role}&around=${id}`);
    const data = await res.json();
    this.lastMsgId = 0; this.lastDateKey = null; this.lastSenderKey = null; this.lastRow = null;
    this.container.innerHTML = '';
    (data.messages || []).forEach(m => { this.appendMessage(m); this.lastMsgId = Math.max(this.lastMsgId, m.id); });
    const row = this.container.querySelector(`.msg-row[data-id="${id}"]`);
    if (row) { row.scrollIntoView({ block: 'center' }); row.classList.add('highlight'); setTimeout(() => row.classList.remove('highlight'), 1600); }
  }

  // ───────────────────────── info panel + shared files ─────────────────────────
  async openInfoPanel() {
    if (!this.currentWith || !this.infoPanel) return;
    this.infoPanel.classList.add('open');
    this.infoPanel.querySelector('.chat-info-body').innerHTML = '<div class="chat-info-loading">Loading…</div>';
    const [infoRes, filesRes] = await Promise.all([
      fetch(`/api/chat/info/?with_id=${this.currentWith.id}&with_role=${this.currentWith.role}`),
      fetch(`/api/chat/files/?with_id=${this.currentWith.id}&with_role=${this.currentWith.role}`),
    ]);
    const info = await infoRes.json(); const files = await filesRes.json();
    this.renderInfoPanel(info, files.files || []);
  }
  renderInfoPanel(info, files) {
    const body = this.infoPanel.querySelector('.chat-info-body');
    const accountRows = Object.entries(info.account || {}).map(([k, v]) => `<div class="ci-row"><span>${k}</span><strong>${this.escapeHtml(String(v))}</strong></div>`).join('');
    const media = files.filter(f => f.category === 'image').slice(0, 9);
    const others = files.filter(f => f.category !== 'image').slice(0, 8);
    body.innerHTML = `
      <div class="chat-info-avatar">${info.avatar_url ? `<img src="${info.avatar_url}">` : (info.name || '?').charAt(0).toUpperCase()}</div>
      <h3>${this.escapeHtml(info.name || '')}</h3>
      <p class="ci-role">${this.escapeHtml(info.role || '')}</p>
      <div class="ci-section-title">Conversation Details</div>
      <div class="ci-row"><span>Created</span><strong>${info.created_at ? new Date(info.created_at).toLocaleDateString() : '—'}</strong></div>
      <div class="ci-row"><span>Messages</span><strong>${info.message_count ?? 0}</strong></div>
      <div class="ci-row"><span>Last active</span><strong>${info.last_active ? new Date(info.last_active).toLocaleString() : '—'}</strong></div>
      ${accountRows ? `<div class="ci-section-title">Account</div>${accountRows}` : ''}
      ${media.length ? `<div class="ci-section-title">Media</div><div class="ci-media-grid">${media.map(f => `<img src="${f.url}" loading="lazy">`).join('')}</div>` : ''}
      <div class="ci-section-title">Shared Files (${files.length})</div>
      <div class="ci-files-list">${others.length ? others.map(f => `<a class="ci-file-row" href="${f.url}" download><span class="maf-icon">${iconFor(f.kind)}</span><span class="ci-file-name">${this.escapeHtml(f.name)}</span><span class="ci-file-size">${f.size_h}</span></a>`).join('') : '<div class="chat-info-empty">No shared files</div>'}</div>
      <button type="button" class="btn-admin btn-secondary-admin ci-full-width" id="ciReportBtn">${'<svg width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'} Report Issue</button>
      <button type="button" class="btn-admin btn-secondary-admin ci-full-width" id="ciClearBtn">Clear Conversation View</button>
    `;
    document.getElementById('ciReportBtn')?.addEventListener('click', () => this.reportIssue());
    document.getElementById('ciClearBtn')?.addEventListener('click', () => { this.container.innerHTML = ''; this.lastMsgId = 0; this.lastDateKey = null; this.lastSenderKey = null; this.loadMessages(true); });
  }
  async reportIssue() {
    const note = window.prompt('Briefly describe the issue with this conversation (optional):', '');
    if (note === null) return;
    const res = await fetch('/api/chat/report/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken }, body: JSON.stringify({ note }) });
    if (res.ok) window.toast?.success?.('Thanks — our team will look into it.');
    else { const d = await res.json().catch(() => ({})); window.toast?.error?.(d.error || 'Could not send the report right now.'); }
  }

  // ───────────────────────── attachment viewer ─────────────────────────
  initViewer() {
    if (document.getElementById('attViewerOverlay')) return;
    const el = document.createElement('div');
    el.id = 'attViewerOverlay'; el.className = 'att-viewer-overlay';
    el.innerHTML = `
      <div class="att-viewer-box">
        <div class="att-viewer-header">
          <div class="att-viewer-title"><span id="attViewerName"></span><small id="attViewerMeta"></small></div>
          <div class="att-viewer-actions">
            <a id="attViewerDownload" class="av-btn" download title="Download">⬇</a>
            <button type="button" id="attViewerClose" class="av-btn" title="Close">✕</button>
          </div>
        </div>
        <button type="button" id="attViewerPrev" class="av-nav av-prev">‹</button>
        <div class="att-viewer-body" id="attViewerBody"></div>
        <button type="button" id="attViewerNext" class="av-nav av-next">›</button>
        <div class="att-viewer-footer" id="attViewerFooter"></div>
      </div>`;
    document.body.appendChild(el);
    document.getElementById('attViewerClose').addEventListener('click', () => this.closeViewer());
    el.addEventListener('click', e => { if (e.target === el) this.closeViewer(); });
    document.getElementById('attViewerPrev').addEventListener('click', () => this.viewerStep(-1));
    document.getElementById('attViewerNext').addEventListener('click', () => this.viewerStep(1));
    document.addEventListener('keydown', e => {
      if (!el.classList.contains('open')) return;
      if (e.key === 'Escape') this.closeViewer();
      if (e.key === 'ArrowLeft') this.viewerStep(-1);
      if (e.key === 'ArrowRight') this.viewerStep(1);
    });
    this._viewerImages = []; this._viewerIdx = 0;
  }
  openViewerFromEl(el) {
    const msgId = el.dataset.msgId; const idx = parseInt(el.dataset.attIndex, 10);
    const row = this.container.querySelector(`.msg-row[data-id="${msgId}"]`);
    const atts = row?._msg?.attachments || [];
    if (!atts.length) return;
    const a = atts[idx]; if (!a) return;
    if (a.preview === 'image') {
      this._viewerImages = atts.filter(x => x.preview === 'image');
      this._viewerIdx = this._viewerImages.findIndex(x => x.id === a.id);
      this.renderViewer(this._viewerImages[this._viewerIdx]);
    } else { this._viewerImages = []; this.renderViewer(a); }
  }
  viewerStep(dir) {
    if (!this._viewerImages.length) return;
    this._viewerIdx = (this._viewerIdx + dir + this._viewerImages.length) % this._viewerImages.length;
    this.renderViewer(this._viewerImages[this._viewerIdx]);
  }
  renderViewer(a) {
    const overlay = document.getElementById('attViewerOverlay');
    document.getElementById('attViewerName').textContent = a.name;
    document.getElementById('attViewerMeta').textContent = `${a.size_h} · ${a.uploaded_by_name}`;
    document.getElementById('attViewerDownload').href = a.url + '?download=1';
    document.getElementById('attViewerDownload').setAttribute('download', a.name);
    document.getElementById('attViewerFooter').textContent = `Uploaded by: ${a.uploaded_by_name} — ${new Date(a.uploaded_at).toLocaleDateString()}`;
    const body = document.getElementById('attViewerBody');
    const nav = this._viewerImages.length > 1;
    document.getElementById('attViewerPrev').style.display = nav ? 'flex' : 'none';
    document.getElementById('attViewerNext').style.display = nav ? 'flex' : 'none';
    if (a.preview === 'image') body.innerHTML = `<img src="${a.url}" alt="${this.escapeAttr(a.name)}">`;
    else if (a.preview === 'pdf') body.innerHTML = `<iframe src="${a.url}" title="${this.escapeAttr(a.name)}"></iframe>`;
    else if (a.preview === 'video') body.innerHTML = `<video src="${a.url}" controls autoplay></video>`;
    else if (a.preview === 'audio') body.innerHTML = `<div class="av-audio-wrap">${iconFor('audio')}<audio src="${a.url}" controls autoplay></audio></div>`;
    else if (a.preview === 'text') { body.innerHTML = '<div class="av-text-wrap">Loading preview…</div>'; fetch(a.url).then(r => r.text()).then(t => { body.innerHTML = `<pre class="av-text-wrap">${this.escapeHtml(t.slice(0, 20000))}</pre>`; }).catch(() => { body.innerHTML = '<div class="av-fallback">Preview unavailable.<br>This file type cannot be displayed directly.</div>'; }); }
    else body.innerHTML = `<div class="av-fallback">${iconFor(a.kind)}<div>Preview unavailable</div><div class="av-fallback-sub">This file type cannot be displayed directly.</div></div>`;
    overlay.classList.add('open');
  }
  closeViewer() { document.getElementById('attViewerOverlay')?.classList.remove('open'); const body = document.getElementById('attViewerBody'); if (body) body.innerHTML = ''; }

  // ───────────────────────── presence / unread ─────────────────────────
  async pollUnread() {
    try {
      const res = await fetch('/api/chat/unread/'); if (!res.ok) return;
      const data = await res.json();
      const navBadge = document.getElementById('chatNavBadge');
      if (navBadge) { navBadge.textContent = data.total || ''; navBadge.style.display = data.total ? '' : 'none'; }
      if (data.per_contact) {
        document.querySelectorAll('.chat-contact[data-id]').forEach(contact => {
          const key = `${contact.dataset.id}_${contact.dataset.role}`;
          const count = data.per_contact[key] || 0;
          let badge = contact.querySelector('.chat-unread-badge');
          if (count > 0) { if (!badge) { badge = document.createElement('span'); badge.className = 'chat-unread-badge'; contact.appendChild(badge); } badge.textContent = count; }
          else badge?.remove();
        });
      }
    } catch (e) {}
  }
  async pollPresence() {
    try {
      const res = await fetch('/api/agents/status/'); if (!res.ok) return;
      const data = await res.json();
      let onlineCount = 0;
      document.querySelectorAll('.chat-contact[data-id][data-role="agent"]').forEach(contact => {
        const id = contact.dataset.id; const isOnline = !!data.online?.[id];
        if (isOnline) onlineCount++;
        contact.dataset.status = isOnline ? 'online' : 'offline';
        const dot = contact.querySelector('.online-dot, .offline-dot');
        if (dot) dot.className = isOnline ? 'online-dot' : 'offline-dot';
        if (this.currentWith && this.currentWith.role === 'agent' && String(this.currentWith.id) === id && this.headerStatus) {
          const lastSeen = contact.dataset.lastSeen || '';
          this.headerStatus.innerHTML = isOnline ? `<span class="status-dot online"></span> Online now` : `<span class="status-dot offline"></span> ${lastSeen ? 'Last seen ' + lastSeen : 'Offline'}`;
        }
      });
      const counter = document.getElementById('activeAgentsCount');
      if (counter) counter.textContent = onlineCount;
    } catch (e) {}
  }

  escapeHtml(str) { return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>'); }
  escapeAttr(str) { return (str || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
}

if (document.getElementById('chatMessages')) window.muddoChat = new MuddoChat();
