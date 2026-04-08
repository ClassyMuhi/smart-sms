import { conversationsSeed, messagesSeed, contactsSeed } from './data.js';
import { loginUser, signupUser, sendMessage as sendMessageApi } from './api.js';

const state = {
  currentScreen: 'splash',
  currentView: 'home',
  activeConversationId: conversationsSeed[0].id,
  conversations: structuredClone(conversationsSeed),
  messages: structuredClone(messagesSeed),
  contacts: structuredClone(contactsSeed),
  selectedMessageId: null,
  showTyping: true,
};

const els = {};

function cacheElements() {
  els.screens = {
    splash: document.getElementById('screen-splash'),
    login: document.getElementById('screen-login'),
    signup: document.getElementById('screen-signup'),
    app: document.getElementById('screen-app'),
  };

  els.views = {
    home: document.getElementById('view-home'),
    profile: document.getElementById('view-profile'),
    'new-chat': document.getElementById('view-new-chat'),
    settings: document.getElementById('view-settings'),
  };

  els.sidebar = document.getElementById('appSidebar');
  els.sidebarBackdrop = document.getElementById('sidebarBackdrop');
  els.sidebarToggle = document.getElementById('sidebarToggle');
  els.navButtons = Array.from(document.querySelectorAll('.nav-btn[data-view]'));

  els.viewTitle = document.getElementById('viewTitle');
  els.viewSubtitle = document.getElementById('viewSubtitle');

  els.loginForm = document.getElementById('loginForm');
  els.signupForm = document.getElementById('signupForm');
  els.gotoSignupBtn = document.getElementById('gotoSignupBtn');
  els.gotoLoginBtn = document.getElementById('gotoLoginBtn');
  els.logoutBtn = document.getElementById('logoutBtn');

  els.signupPassword = document.getElementById('signupPassword');
  els.passwordStrengthBar = document.getElementById('passwordStrengthBar');
  els.passwordStrengthText = document.getElementById('passwordStrengthText');

  els.conversationSearch = document.getElementById('conversationSearch');
  els.conversationItems = document.getElementById('conversationItems');

  els.chatAvatar = document.getElementById('chatAvatar');
  els.chatName = document.getElementById('chatName');
  els.chatStatus = document.getElementById('chatStatus');
  els.chatTimeline = document.getElementById('chatTimeline');
  els.chatForm = document.getElementById('chatForm');
  els.chatInput = document.getElementById('chatInput');

  els.newChatSearch = document.getElementById('newChatSearch');
  els.newChatList = document.getElementById('newChatList');

  els.reactionMenu = document.getElementById('reactionMenu');
}

function setScreen(screenName) {
  state.currentScreen = screenName;
  Object.entries(els.screens).forEach(([key, node]) => {
    node.classList.toggle('is-active', key === screenName);
  });
}

function setView(viewName) {
  state.currentView = viewName;
  Object.entries(els.views).forEach(([key, node]) => {
    node.classList.toggle('is-active', key === viewName);
  });

  els.navButtons.forEach((button) => {
    button.classList.toggle('is-active', button.dataset.view === viewName);
  });

  const metaMap = {
    home: ['Conversations', 'Your messaging hub'],
    profile: ['Profile', 'Manage your identity and status'],
    'new-chat': ['New Chat', 'Start a new conversation'],
    settings: ['Settings', 'Customize your app experience'],
  };

  const meta = metaMap[viewName] || metaMap.home;
  els.viewTitle.textContent = meta[0];
  els.viewSubtitle.textContent = meta[1];

  if (window.innerWidth < 1024) closeSidebar();
}

function openSidebar() {
  els.sidebar.classList.add('open');
  els.sidebar.classList.remove('-translate-x-full');
  els.sidebarBackdrop.classList.remove('hidden');
  document.body.classList.add('sidebar-open');
}

function closeSidebar() {
  els.sidebar.classList.remove('open');
  if (window.innerWidth < 1024) {
    els.sidebar.classList.add('-translate-x-full');
  }
  els.sidebarBackdrop.classList.add('hidden');
  document.body.classList.remove('sidebar-open');
}

function getActiveConversation() {
  return state.conversations.find((item) => item.id === state.activeConversationId);
}

function getMessagesForActiveConversation() {
  return state.messages[state.activeConversationId] || [];
}

function renderConversations() {
  const query = (els.conversationSearch.value || '').trim().toLowerCase();

  const filtered = state.conversations.filter((item) => {
    return [item.name, item.lastMessage].some((field) => field.toLowerCase().includes(query));
  });

  els.conversationItems.innerHTML = filtered
    .map((item) => {
      return `
        <button class="conversation-item ${item.id === state.activeConversationId ? 'is-active' : ''}" data-conversation-id="${item.id}">
          <img src="${item.avatar}" alt="${item.name}" class="h-11 w-11 rounded-2xl" />
          <div class="min-w-0 flex-1">
            <div class="flex items-center justify-between gap-2">
              <p class="truncate text-sm font-semibold">${item.name}</p>
              <span class="text-[11px] text-slate-500">${item.time}</span>
            </div>
            <p class="truncate text-xs text-slate-400 mt-0.5">${item.typing ? 'Typing...' : item.lastMessage}</p>
          </div>
          ${item.unread ? `<span class="unread-badge">${item.unread}</span>` : ''}
        </button>
      `;
    })
    .join('');

  els.conversationItems.querySelectorAll('[data-conversation-id]').forEach((button) => {
    button.addEventListener('click', () => {
      state.activeConversationId = button.dataset.conversationId;
      renderHome();
    });
  });
}

function renderMessages() {
  const active = getActiveConversation();
  if (!active) return;

  els.chatAvatar.src = active.avatar;
  els.chatAvatar.alt = active.name;
  els.chatName.textContent = active.name;
  els.chatStatus.textContent = active.typing ? 'Typing...' : active.status;

  const messages = getMessagesForActiveConversation();

  const items = messages
    .map((msg) => {
      const bubbleClass = msg.sender === 'me' ? 'sent' : 'received';
      const rowClass = msg.sender === 'me' ? 'mine' : 'their';
      const reactionHtml = msg.reaction ? `<div class="reaction-chip">${msg.reaction}</div>` : '';

      return `
        <div class="message-row ${rowClass}" data-message-id="${msg.id}">
          <div class="message-bubble ${bubbleClass}">
            <p>${escapeHtml(msg.text)}</p>
            ${reactionHtml}
            <div class="message-meta">${msg.time}</div>
          </div>
        </div>
      `;
    })
    .join('');

  const typingBlock = active.typing
    ? `
      <div class="message-row their">
        <div class="typing-indicator">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    `
    : '';

  els.chatTimeline.innerHTML = `${items}${typingBlock}`;

  els.chatTimeline.querySelectorAll('.message-row').forEach((row) => {
    row.addEventListener('contextmenu', (event) => {
      event.preventDefault();
      const id = Number(row.dataset.messageId);
      openReactionMenu(event.clientX, event.clientY, id);
    });

    row.addEventListener('mouseenter', () => {
      row.classList.add('hovered');
    });
  });

  scrollChatToBottom();
}

function renderNewChatList() {
  const query = (els.newChatSearch.value || '').trim().toLowerCase();
  const filtered = state.contacts.filter((item) => item.name.toLowerCase().includes(query));

  els.newChatList.innerHTML = filtered
    .map((item) => {
      return `
        <button class="contact-item" data-contact-id="${item.id}">
          <div class="flex items-center gap-3">
            <img src="${item.avatar}" alt="${item.name}" class="h-10 w-10 rounded-2xl" />
            <span class="text-sm font-medium">${item.name}</span>
          </div>
          <i data-lucide="message-circle" class="h-4 w-4"></i>
        </button>
      `;
    })
    .join('');

  els.newChatList.querySelectorAll('[data-contact-id]').forEach((button) => {
    button.addEventListener('click', () => {
      setView('home');
    });
  });
}

function renderHome() {
  renderConversations();
  renderMessages();
  refreshIcons();
}

function openReactionMenu(x, y, messageId) {
  state.selectedMessageId = messageId;
  els.reactionMenu.style.left = `${Math.min(x, window.innerWidth - 180)}px`;
  els.reactionMenu.style.top = `${Math.min(y, window.innerHeight - 80)}px`;
  els.reactionMenu.classList.remove('hidden');
}

function closeReactionMenu() {
  els.reactionMenu.classList.add('hidden');
  state.selectedMessageId = null;
}

function addReaction(reaction) {
  const messages = getMessagesForActiveConversation();
  const message = messages.find((item) => item.id === state.selectedMessageId);
  if (!message) return;
  message.reaction = reaction;
  closeReactionMenu();
  renderMessages();
  refreshIcons();
}

async function onLoginSubmit(event) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const values = Object.fromEntries(formData.entries());

  const result = await loginUser(values);
  if (result.ok) {
    setScreen('app');
    setView('home');
    renderHome();
  }
}

async function onSignupSubmit(event) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const values = Object.fromEntries(formData.entries());

  const result = await signupUser(values);
  if (result.ok) {
    setScreen('app');
    setView('home');
    renderHome();
  }
}

async function onChatSubmit(event) {
  event.preventDefault();
  const text = (els.chatInput.value || '').trim();
  if (!text) return;

  const payload = {
    conversationId: state.activeConversationId,
    message: text,
  };

  await sendMessageApi(payload);

  const messages = getMessagesForActiveConversation();
  const nextId = messages.length ? Math.max(...messages.map((item) => item.id)) + 1 : 1;

  messages.push({
    id: nextId,
    sender: 'me',
    text,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  });

  const active = getActiveConversation();
  active.lastMessage = text;
  active.unread = 0;

  els.chatInput.value = '';
  renderHome();
}

function evaluatePasswordStrength(value) {
  let score = 0;
  if (value.length >= 8) score += 1;
  if (/[A-Z]/.test(value)) score += 1;
  if (/[a-z]/.test(value)) score += 1;
  if (/\d/.test(value)) score += 1;
  if (/[^A-Za-z0-9]/.test(value)) score += 1;

  const percent = Math.min(100, score * 20);
  els.passwordStrengthBar.style.width = `${percent}%`;

  if (score <= 2) {
    els.passwordStrengthBar.className = 'h-full rounded-full bg-rose-400 transition-all duration-300';
    els.passwordStrengthText.textContent = 'Password strength: low';
  } else if (score <= 4) {
    els.passwordStrengthBar.className = 'h-full rounded-full bg-amber-400 transition-all duration-300';
    els.passwordStrengthText.textContent = 'Password strength: medium';
  } else {
    els.passwordStrengthBar.className = 'h-full rounded-full bg-emerald-400 transition-all duration-300';
    els.passwordStrengthText.textContent = 'Password strength: strong';
  }
}

function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function scrollChatToBottom() {
  requestAnimationFrame(() => {
    els.chatTimeline.scrollTop = els.chatTimeline.scrollHeight;
  });
}

function escapeHtml(value) {
  const div = document.createElement('div');
  div.textContent = value;
  return div.innerHTML;
}

function bindEvents() {
  window.setTimeout(() => {
    setScreen('login');
    refreshIcons();
  }, 2300);

  els.gotoSignupBtn.addEventListener('click', () => setScreen('signup'));
  els.gotoLoginBtn.addEventListener('click', () => setScreen('login'));

  els.loginForm.addEventListener('submit', onLoginSubmit);
  els.signupForm.addEventListener('submit', onSignupSubmit);
  els.chatForm.addEventListener('submit', onChatSubmit);

  els.signupPassword.addEventListener('input', (event) => {
    evaluatePasswordStrength(event.target.value);
  });

  els.navButtons.forEach((button) => {
    button.addEventListener('click', () => {
      setView(button.dataset.view);
      if (button.dataset.view === 'new-chat') {
        renderNewChatList();
      }
    });
  });

  els.conversationSearch.addEventListener('input', renderConversations);
  els.newChatSearch.addEventListener('input', renderNewChatList);

  els.sidebarToggle.addEventListener('click', openSidebar);
  els.sidebarBackdrop.addEventListener('click', closeSidebar);

  els.logoutBtn.addEventListener('click', () => {
    setScreen('login');
    closeSidebar();
  });

  els.reactionMenu.querySelectorAll('[data-reaction]').forEach((button) => {
    button.addEventListener('click', () => {
      addReaction(button.dataset.reaction);
    });
  });

  document.addEventListener('click', (event) => {
    if (!els.reactionMenu.contains(event.target)) {
      closeReactionMenu();
    }

    if (window.innerWidth < 1024) {
      if (!els.sidebar.contains(event.target) && event.target !== els.sidebarToggle) {
        closeSidebar();
      }
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeReactionMenu();
      closeSidebar();
    }
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth >= 1024) {
      els.sidebar.classList.remove('-translate-x-full');
      els.sidebarBackdrop.classList.add('hidden');
      document.body.classList.remove('sidebar-open');
    } else if (!els.sidebar.classList.contains('open')) {
      els.sidebar.classList.add('-translate-x-full');
    }
  });
}

function init() {
  cacheElements();
  bindEvents();
  setScreen('splash');
  setView('home');
  renderHome();
  renderNewChatList();
  evaluatePasswordStrength('');
  refreshIcons();
}

window.addEventListener('DOMContentLoaded', init);
