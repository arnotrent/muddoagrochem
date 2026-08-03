/* ═══════════════════════════════════════════════════════════════
   MUDDO AGRO — CHAT SYSTEM  v6
   Fixes vs v5:
   - DUPLICATE ATTACHMENT MESSAGES: sendMessage() had no "in flight" guard
     and the send button stayed enabled the whole time a file was
     uploading. A second click (or a second Enter) while the first
     upload was still in progress fired a second real POST — two
     genuinely separate messages, not a rendering glitch. Now the
     button disables and Enter is ignored until the first send finishes.
   - Scrolling: see static/css/admin.css / responsive.css for the
     min-height:0 flex fix that was the real cause of messages being
     stuck below the visible area.
   New:
   - Emoji picker (🙂 button next to the attach button).
   ═══════════════════════════════════════════════════════════════ */

function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.content) return meta.content;
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

const TICK_SENT = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:.75;vertical-align:-1px"><polyline points="20 6 9 17 4 12"/></svg>';
const TICK_SEEN = '<svg class="icon msg-tick-seen" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px"><polyline points="1 13 5 17 11 9"/><polyline points="7 13 11 17 21 5"/></svg>';

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
    this.myInitial    = document.body.dataset.userInitial || 'U';
    this.myId         = parseInt(document.body.dataset.userId || '0', 10);
    this.myRole       = document.body.dataset.userRole || 'agent';

    this.lastDateKey   = null;
    this.lastSenderKey = null;
    this.lastRow       = null;
    this.pendingFile   = null;
    this.replyingTo    = null; // { id, preview, senderRole }
    this.sending       = false; // guards against double-submit

    if (this.sendBtn)  this.sendBtn.addEventListener('click', () => this.sendMessage());
    if (this.inputBox) {
      this.inputBox.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.sendMessage(); }
      });
      this.inputBox.addEventListener('input', () => {
        this.inputBox.style.height = 'auto';
        this.inputBox.style.height = Math.min(this.inputBox.scrollHeight, 120) + 'px';
      });
    }
    if (this.attachBtn && this.attachInput) {
      this.attachBtn.addEventListener('click', () => this.attachInput.click());
      this.attachInput.addEventListener('change', () => {
        const f = this.attachInput.files && this.attachInput.files[0];
        if (f) this.setPendingFile(f);
      });
    }
    if (this.emojiBtn && this.emojiPanel) {
      if (!this.emojiPanel.dataset.built) {
        this.emojiPanel.innerHTML = EMOJI_SET.map(e => `<button type="button" class="emoji-item">${e}</button>`).join('');
        this.emojiPanel.dataset.built = '1';
      }
      this.emojiBtn.addEventListener('click', e => {
        e.stopPropagation();
        this.emojiPanel.classList.toggle('open');
      });
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
        if (!this.emojiPanel.contains(e.target) && e.target !== this.emojiBtn) {
          this.emojiPanel.classList.remove('open');
        }
      });
    }
    if (this.backBtn) {
      this.backBtn.addEventListener('click', () => this.layoutEl?.classList.remove('chat-mobile-conversation-open'));
    }

    document.querySelectorAll('.chat-contact[data-id]').forEach(el => {
      el.addEventListener('click', () => this.selectContact(el));
    });

    if (this.container) {
      this.container.addEventListener('click', e => {
        const btn = e.target.closest('.msg-reply-btn');
        if (btn) this.startReply(btn.dataset.id, btn.dataset.preview, btn.dataset.senderRole);
      });
    }

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

  selectContact(el) {
    document.querySelectorAll('.chat-contact').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    el.querySelector('.chat-unread-badge')?.remove();

    this.currentWith = {
      id:     parseInt(el.dataset.id, 10),
      role:   el.dataset.role || 'agent',
      name:   el.dataset.name || 'User',
      avatar: el.dataset.avatar || '',
    };
    const isBroadcast = this.currentWith.role === 'broadcast';

    if (this.headerName)   this.headerName.textContent = this.currentWith.name;
    if (this.headerStatus) {
      if (isBroadcast) {
        this.headerStatus.innerHTML = 'Everyone — admin and all field agents';
      } else if (this.currentWith.role === 'admin') {
        this.headerStatus.innerHTML = `<span class="status-dot online"></span> Head Office`;
      } else {
        const online = el.dataset.status === 'online';
        const lastSeen = el.dataset.lastSeen || '';
        this.headerStatus.innerHTML = online
          ? `<span class="status-dot online"></span> Online now`
          : `<span class="status-dot offline"></span> ${lastSeen ? 'Last seen ' + lastSeen : 'Offline'}`;
      }
    }
    if (this.headerAvatar) {
      this.headerAvatar.innerHTML = this.currentWith.avatar
        ? `<img src="${this.currentWith.avatar}" style="width:100%;height:100%;object-fit:cover;border-radius:50%">`
        : (isBroadcast ? '📢' : this.currentWith.name.charAt(0).toUpperCase());
    }
    if (this.chatMain)     this.chatMain.style.display  = 'flex';
    if (this.chatEmpty)    this.chatEmpty.style.display = 'none';
    this.layoutEl?.classList.add('chat-mobile-conversation-open');

    this.lastMsgId = 0;
    this.lastDateKey = null;
    this.lastSenderKey = null;
    this.lastRow = null;
    this.cancelReply();
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
      const url = isBroadcast
        ? `/api/chat/messages/?with_role=broadcast&after=${this.lastMsgId}`
        : `/api/chat/messages/?with_id=${this.currentWith.id}&with_role=${this.currentWith.role}&after=${this.lastMsgId}`;
      const res  = await fetch(url);
      if (!res.ok) { console.warn('Chat load failed:', res.status); return; }
      const data = await res.json();
      if (data.messages?.length) {
        data.messages.forEach(m => {
          if (m.id <= this.lastMsgId) return;
          this.lastMsgId = m.id;
          this.appendMessage(m);
        });
        if (scroll) this.scrollBottom();
        else {
          const atBottom = this.container.scrollHeight - this.container.scrollTop - this.container.clientHeight < 80;
          if (atBottom) this.scrollBottom();
        }
      }
      fetch(`/api/chat/mark-read/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
        body: JSON.stringify(isBroadcast ? { from_role: 'broadcast' } : { from_id: this.currentWith.id, from_role: this.currentWith.role })
      }).catch(() => {});
    } catch(e) { console.warn('Chat load error:', e); }
  }

  dateKeyFor(dateObj) { return dateObj.toDateString(); }

  dateLabelFor(dateObj) {
    const today = new Date(); const yest = new Date(); yest.setDate(today.getDate() - 1);
    if (this.dateKeyFor(dateObj) === this.dateKeyFor(today)) return 'Today';
    if (this.dateKeyFor(dateObj) === this.dateKeyFor(yest)) return 'Yesterday';
    return dateObj.toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' });
  }

  renderAttachment(m) {
    if (!m.attachment_url) return '';
    if (m.attachment_is_image) {
      return `<a href="${m.attachment_url}" target="_blank" rel="noopener"><img class="msg-attachment-img" src="${m.attachment_url}" alt="attachment" loading="lazy"></a>`;
    }
    const name = m.attachment_name || 'file';
    return `<a class="msg-attachment-file" href="${m.attachment_url}" target="_blank" rel="noopener" download>
      <svg class="icon" width="1.1em" height="1.1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      <span>${this.escapeHtml(name)}</span>
    </a>`;
  }

  renderReplyQuote(m) {
    if (!m.reply_to) return '';
    const who = m.reply_to.sender_name || 'them';
    return `<div class="msg-reply-quote"><strong>${this.escapeHtml(who)}</strong>${this.escapeHtml(m.reply_to.content || '')}</div>`;
  }

  avatarHtml(url, initial) {
    return url ? `<img src="${url}" style="width:100%;height:100%;object-fit:cover;border-radius:50%">` : initial;
  }

  appendMessage(m) {
    const isSent = (m.sender_role === this.myRole && m.sender_id === this.myId);
    const isGroup = this.currentWith?.role === 'broadcast';
    const initial = isSent ? this.myInitial : ((m.sender_name || '?').charAt(0).toUpperCase());
    const avatarUrl = isSent ? null : m.sender_avatar_url;
    const msgDate = new Date(m.created_at);
    const dateKey = this.dateKeyFor(msgDate);
    const time = msgDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (dateKey !== this.lastDateKey) {
      const sep = document.createElement('div');
      sep.className = 'chat-date-sep';
      sep.textContent = this.dateLabelFor(msgDate);
      this.container.appendChild(sep);
      this.lastDateKey = dateKey;
      this.lastSenderKey = null;
    }

    const senderKey = `${m.sender_role}:${m.sender_id}`;
    const grouped = senderKey === this.lastSenderKey;

    if (grouped && this.lastRow) {
      const prevSlot = this.lastRow.querySelector('.msg-avatar-slot');
      if (prevSlot) prevSlot.style.visibility = 'hidden';
      this.lastRow.style.marginBottom = '2px';
    }

    const wrapper = document.createElement('div');
    wrapper.className = `msg-row ${isSent ? 'sent' : 'received'}`;
    wrapper.dataset.id = m.id;
    if (grouped) wrapper.style.marginTop = '2px';

    const senderLabel = (isGroup && !isSent && !grouped) ? `<div class="msg-sender-name">${this.escapeHtml(m.sender_name || '')}</div>` : '';
    const previewText = (m.content || (m.attachment_name ? '📎 ' + m.attachment_name : '')).substring(0, 60);

    wrapper.innerHTML = `
      <div class="msg-avatar-slot"><div class="msg-avatar ${isSent ? 'sent-avatar' : ''}">${this.avatarHtml(avatarUrl, initial)}</div></div>
      <div class="msg-hover-actions"><button class="msg-reply-btn" data-id="${m.id}" data-preview="${this.escapeAttr(previewText)}" data-sender-role="${m.sender_role}" title="Reply">${this.replyIconSvg()}</button></div>
      <div class="msg-bubble">${senderLabel}${this.renderReplyQuote(m)}${this.renderAttachment(m)}${m.content ? this.escapeHtml(m.content) : ''}<span class="msg-time">${time}${isSent ? ' ' + (m.read ? TICK_SEEN : TICK_SENT) : ''}</span></div>
    `;
    this.container.appendChild(wrapper);

    this.lastSenderKey = senderKey;
    this.lastRow = wrapper;
  }

  replyIconSvg() {
    return '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg>';
  }

  startReply(id, preview, senderRole) {
    this.replyingTo = { id, preview, senderRole };
    if (!this.replyBar) return;
    this.replyBar.innerHTML = `<div class="reply-bar-inner"><div><strong>Replying</strong><div class="reply-bar-preview">${this.escapeHtml(preview)}</div></div><button type="button" id="chatReplyCancel">${'<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'}</button></div>`;
    this.replyBar.style.display = 'block';
    document.getElementById('chatReplyCancel')?.addEventListener('click', () => this.cancelReply());
    this.inputBox?.focus();
  }

  cancelReply() {
    this.replyingTo = null;
    if (this.replyBar) { this.replyBar.style.display = 'none'; this.replyBar.innerHTML = ''; }
  }

  setPendingFile(file) {
    this.pendingFile = file;
    if (!this.attachPreview) return;
    const isImage = file.type.startsWith('image/');
    this.attachPreview.style.display = 'flex';
    const cancelSvg = '<svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
    if (isImage) {
      const reader = new FileReader();
      reader.onload = e => {
        this.attachPreview.innerHTML = `<img src="${e.target.result}" class="attach-preview-thumb"><span class="attach-preview-name">${this.escapeHtml(file.name)}</span><button type="button" id="chatAttachCancel">${cancelSvg}</button>`;
        document.getElementById('chatAttachCancel')?.addEventListener('click', () => this.clearPendingFile());
      };
      reader.readAsDataURL(file);
    } else {
      this.attachPreview.innerHTML = `<span class="attach-preview-name">📎 ${this.escapeHtml(file.name)}</span><button type="button" id="chatAttachCancel">${cancelSvg}</button>`;
      document.getElementById('chatAttachCancel')?.addEventListener('click', () => this.clearPendingFile());
    }
  }

  clearPendingFile() {
    this.pendingFile = null;
    if (this.attachInput) this.attachInput.value = '';
    if (this.attachPreview) { this.attachPreview.style.display = 'none'; this.attachPreview.innerHTML = ''; }
  }

  setSendingState(isSending) {
    this.sending = isSending;
    if (this.sendBtn) this.sendBtn.disabled = isSending;
    if (this.attachBtn) this.attachBtn.disabled = isSending;
  }

  async sendMessage() {
    if (this.sending) return; // guards against double-click / double-Enter while a send is still in flight
    const content = this.inputBox?.value.trim() || '';
    if (!content && !this.pendingFile) return;
    if (!this.currentWith) return;
    const file = this.pendingFile;
    const replyId = this.replyingTo?.id || null;
    this.setSendingState(true);
    this.inputBox.value = '';
    this.inputBox.style.height = 'auto';
    this.clearPendingFile();
    this.cancelReply();
    const isBroadcast = this.currentWith.role === 'broadcast';

    try {
      let res;
      if (file) {
        const fd = new FormData();
        fd.append('content', content);
        if (isBroadcast) fd.append('broadcast', 'true');
        else { fd.append('to_id', this.currentWith.id); fd.append('to_role', this.currentWith.role); }
        if (replyId) fd.append('reply_to', replyId);
        fd.append('attachment', file);
        res = await fetch('/api/chat/send/', { method: 'POST', headers: { 'X-CSRFToken': this.csrfToken }, body: fd });
      } else {
        const body = isBroadcast
          ? { broadcast: true, content, reply_to: replyId }
          : { to_id: this.currentWith.id, to_role: this.currentWith.role, content, reply_to: replyId };
        res = await fetch('/api/chat/send/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
          body: JSON.stringify(body)
        });
      }
      if (!res.ok) {
        console.error('Send failed:', res.status);
        window.toast?.error?.('Message failed to send — please try again.');
        return;
      }
      const data = await res.json();
      if (data.message) {
        this.appendMessage(data.message);
        this.lastMsgId = Math.max(this.lastMsgId, data.message.id);
        this.scrollBottom();
        const contactEl = document.querySelector(`.chat-contact[data-id="${this.currentWith.id}"][data-role="${this.currentWith.role}"]`);
        const preview = contactEl?.querySelector('.chat-contact-preview');
        const previewText = content || (data.message.attachment_name ? '📎 ' + data.message.attachment_name : '');
        if (preview) preview.innerHTML = '<span class="you-prefix">You: </span>' + this.escapeHtml(previewText.substring(0, 40));
        const timeEl = contactEl?.querySelector('.chat-contact-time');
        if (timeEl) timeEl.textContent = new Date(data.message.created_at).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
      }
    } catch(e) { console.error(e); }
    finally { this.setSendingState(false); }
  }

  scrollBottom() {
    if (this.container) this.container.scrollTop = this.container.scrollHeight;
  }

  async pollUnread() {
    try {
      const res  = await fetch('/api/chat/unread/');
      if (!res.ok) return;
      const data = await res.json();
      const navBadge = document.getElementById('chatNavBadge');
      if (navBadge) { navBadge.textContent = data.total || ''; navBadge.style.display = data.total ? '' : 'none'; }

      if (data.per_contact) {
        document.querySelectorAll('.chat-contact[data-id]').forEach(contact => {
          const key = `${contact.dataset.id}_${contact.dataset.role}`;
          const count = data.per_contact[key] || 0;
          let badge = contact.querySelector('.chat-unread-badge');
          if (count > 0) {
            if (!badge) { badge = document.createElement('span'); badge.className = 'chat-unread-badge'; contact.appendChild(badge); }
            badge.textContent = count;
          } else { badge?.remove(); }
        });
      }
    } catch(e) { /* silent */ }
  }

  async pollPresence() {
    try {
      const res = await fetch('/api/agents/status/');
      if (!res.ok) return;
      const data = await res.json();
      let onlineCount = 0;
      document.querySelectorAll('.chat-contact[data-id][data-role="agent"]').forEach(contact => {
        const id = contact.dataset.id;
        const isOnline = !!data.online?.[id];
        if (isOnline) onlineCount++;
        contact.dataset.status = isOnline ? 'online' : 'offline';
        const dot = contact.querySelector('.online-dot, .offline-dot');
        if (dot) { dot.className = isOnline ? 'online-dot' : 'offline-dot'; }
        if (this.currentWith && this.currentWith.role === 'agent' && String(this.currentWith.id) === id && this.headerStatus) {
          const lastSeen = contact.dataset.lastSeen || '';
          this.headerStatus.innerHTML = isOnline
            ? `<span class="status-dot online"></span> Online now`
            : `<span class="status-dot offline"></span> ${lastSeen ? 'Last seen ' + lastSeen : 'Offline'}`;
        }
      });
      const counter = document.getElementById('activeAgentsCount');
      if (counter) counter.textContent = onlineCount;
    } catch(e) { /* silent */ }
  }

  escapeHtml(str) {
    return (str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
  }
  escapeAttr(str) {
    return (str || '').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }
}

if (document.getElementById('chatMessages')) {
  window.muddoChat = new MuddoChat();
}
