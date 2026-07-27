/* ═══════════════════════════════════════════════════════════════
   MUDDO AGRO — CHAT SYSTEM  v3
   Fixes vs v2:
   - Every fetch() now hits the EXACT url from urls.py (trailing
     slash included). v2 called e.g. /api/chat/send (no slash) while
     urls.py defines api/chat/send/ — in production (DEBUG=False)
     Django's APPEND_SLASH redirect turns that POST into a GET on
     redirect, silently dropping the message body + CSRF token. This
     was the actual reason sends/mark-read looked broken.
   - Added broadcast support ("All Agents" thread, admin-only).
   ═══════════════════════════════════════════════════════════════ */

function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.content) return meta.content;
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

class MuddoChat {
  constructor() {
    this.currentWith  = null;  // {id, role, name}
    this.lastMsgId    = 0;
    this.pollInterval = null;
    this.csrfToken    = getCsrfToken();
    this.container    = document.getElementById('chatMessages');
    this.inputBox     = document.getElementById('chatInput');
    this.sendBtn      = document.getElementById('chatSendBtn');
    this.headerName   = document.getElementById('chatHeaderName')   || document.getElementById('chatHdrName');
    this.headerStatus = document.getElementById('chatHeaderStatus') || document.getElementById('chatHdrStatus');
    this.headerAvatar = document.getElementById('chatHeaderAvatar') || document.getElementById('chatHdrAvatar');
    this.chatMain     = document.getElementById('chatMainArea')     || document.getElementById('chatMain');
    this.chatEmpty    = document.getElementById('chatEmptyState')   || document.getElementById('chatEmpty');
    this.myInitial    = document.body.dataset.userInitial || 'U';
    this.myId         = parseInt(document.body.dataset.userId || '0', 10);
    this.myRole       = document.body.dataset.userRole || 'agent';

    this.lastDateKey   = null;
    this.lastSenderKey = null;
    this.lastRow       = null;

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

    document.querySelectorAll('.chat-contact[data-id]').forEach(el => {
      el.addEventListener('click', () => this.selectContact(el));
    });

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
      id:   parseInt(el.dataset.id, 10),
      role: el.dataset.role || 'agent',
      name: el.dataset.name || 'User',
    };
    const isBroadcast = this.currentWith.role === 'broadcast';

    if (this.headerName)   this.headerName.textContent = this.currentWith.name;
    if (this.headerStatus) {
      this.headerStatus.innerHTML = isBroadcast
        ? 'Sends to every active field agent at once'
        : `<span class="status-dot ${el.dataset.status || 'offline'}"></span> ${el.dataset.status === 'online' ? 'Online now' : 'Offline'}`;
    }
    if (this.headerAvatar) this.headerAvatar.textContent = isBroadcast ? '📢' : this.currentWith.name.charAt(0).toUpperCase();
    if (this.chatMain)     this.chatMain.style.display  = 'flex';
    if (this.chatEmpty)    this.chatEmpty.style.display = 'none';

    this.lastMsgId = 0;
    this.lastDateKey = null;
    this.lastSenderKey = null;
    this.lastRow = null;
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
      if (!data.messages?.length) return;

      data.messages.forEach(m => {
        if (m.id <= this.lastMsgId) return;
        this.lastMsgId = m.id;
        this.appendMessage(m);
      });
      if (scroll) this.scrollBottom();
      else {
        const container = this.container;
        const atBottom  = container.scrollHeight - container.scrollTop - container.clientHeight < 80;
        if (atBottom) this.scrollBottom();
      }
      if (!isBroadcast) {
        fetch(`/api/chat/mark-read/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
          body: JSON.stringify({ from_id: this.currentWith.id, from_role: this.currentWith.role })
        }).catch(() => {});
      }
    } catch(e) { console.warn('Chat load error:', e); }
  }

  dateKeyFor(dateObj) { return dateObj.toDateString(); }

  dateLabelFor(dateObj) {
    const today = new Date(); const yest = new Date(); yest.setDate(today.getDate() - 1);
    if (this.dateKeyFor(dateObj) === this.dateKeyFor(today)) return 'Today';
    if (this.dateKeyFor(dateObj) === this.dateKeyFor(yest)) return 'Yesterday';
    return dateObj.toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' });
  }

  appendMessage(m) {
    const isSent = (m.sender_role === this.myRole && m.sender_id === this.myId);
    const initial = isSent ? this.myInitial : (m.is_broadcast ? '📢' : (this.currentWith?.name?.charAt(0) || '?'));
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

    const senderKey = `${m.sender_role}:${m.sender_id}:${m.is_broadcast ? 'b' : 'd'}`;
    const grouped = senderKey === this.lastSenderKey;

    if (grouped && this.lastRow) {
      const prevSlot = this.lastRow.querySelector('.msg-avatar-slot');
      if (prevSlot) prevSlot.style.visibility = 'hidden';
      this.lastRow.style.marginBottom = '2px';
    }

    const wrapper = document.createElement('div');
    wrapper.className = `msg-row ${isSent ? 'sent' : 'received'}`;
    if (grouped) wrapper.style.marginTop = '2px';
    const broadcastTag = (m.is_broadcast && !isSent) ? '<span class="msg-broadcast-tag">Broadcast</span><br>' : '';
    wrapper.innerHTML = `
      <div class="msg-avatar-slot"><div class="msg-avatar ${isSent ? 'sent-avatar' : ''}">${initial}</div></div>
      <div class="msg-bubble">${broadcastTag}${this.escapeHtml(m.content)}<span class="msg-time">${time}${isSent ? ' <svg class="icon" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:.8;vertical-align:-1px"><polyline points="1 13 5 17 11 9"/><polyline points="7 13 11 17 21 5"/></svg>' : ''}</span></div>
    `;
    this.container.appendChild(wrapper);

    this.lastSenderKey = senderKey;
    this.lastRow = wrapper;
  }

  async sendMessage() {
    const content = this.inputBox?.value.trim();
    if (!content || !this.currentWith) return;
    this.inputBox.value = '';
    this.inputBox.style.height = 'auto';
    const isBroadcast = this.currentWith.role === 'broadcast';

    const body = isBroadcast
      ? { broadcast: true, content }
      : { to_id: this.currentWith.id, to_role: this.currentWith.role, content };

    try {
      const res = await fetch('/api/chat/send/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
        body: JSON.stringify(body)
      });
      if (!res.ok) {
        console.error('Send failed:', res.status);
        this.inputBox.value = content;
        window.toast?.error?.('Message failed to send — please try again.');
        return;
      }
      const data = await res.json();
      if (data.message) {
        this.appendMessage(data.message);
        this.scrollBottom();
        const contactEl = document.querySelector(`.chat-contact[data-id="${this.currentWith.id}"][data-role="${this.currentWith.role}"]`);
        const preview = contactEl?.querySelector('.chat-contact-preview');
        if (preview) preview.innerHTML = '<span class="you-prefix">You: </span>' + this.escapeHtml(content.substring(0, 40));
        const timeEl = contactEl?.querySelector('.chat-contact-time');
        if (timeEl) timeEl.textContent = new Date(data.message.created_at).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
      }
    } catch(e) { this.inputBox.value = content; }
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
      const bell = document.getElementById('notifCount');
      if (bell) bell.textContent = data.total || 0;

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
          this.headerStatus.innerHTML = `<span class="status-dot ${isOnline ? 'online' : 'offline'}"></span> ${isOnline ? 'Online now' : 'Offline'}`;
        }
      });
      const counter = document.getElementById('activeAgentsCount');
      if (counter) counter.textContent = onlineCount;
    } catch(e) { /* silent */ }
  }

  escapeHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
  }
}

if (document.getElementById('chatMessages')) {
  window.muddoChat = new MuddoChat();
}
