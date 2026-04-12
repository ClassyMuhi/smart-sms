import { conversationsSeed, messagesSeed, contactsSeed } from './data.js';
import {
  loginUser,
  signupUser,
  sendMessage as sendMessageApi,
  getContacts,
  getMessages,
  clearAuthToken,
  getEmergencyContacts,
  addEmergencyContact,
  removeEmergencyContact,
  triggerEmergency,
  getActiveSOS,
  addSOSLocation,
} from './api.js';

const state = {
  currentScreen: 'splash',
  currentView: 'home',
  activeConversationId: conversationsSeed[0].id,
  conversations: structuredClone(conversationsSeed),
  messages: structuredClone(messagesSeed),
  contacts: structuredClone(contactsSeed),
  currentUser: null,
  seenMessageIds: new Set(),
  messagePollHandle: null,
  isSendingMessage: false,
  lastSentSignature: '',
  lastSentAt: 0,
  selectedMessageId: null,
  showTyping: true,
  profileStatus: 'Available for chat',
  settings: {
    theme: 'dark',
    notificationsEnabled: true,
    privacyMode: 'contacts-only',
  },
  emergencyContacts: [],
  activeSosId: '',
  sosLongPressTimer: null,
  sosHoldProgressTimer: null,
  sosCountdownTimer: null,
  sosLiveUpdateTimer: null,
  sosCountdownValue: 0,
  isHoldingSos: false,
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
  els.profileLogoutBtn = document.getElementById('profileLogoutBtn');

  els.signupPassword = document.getElementById('signupPassword');
  els.passwordStrengthBar = document.getElementById('passwordStrengthBar');
  els.passwordStrengthText = document.getElementById('passwordStrengthText');

  els.conversationSearch = document.getElementById('conversationSearch');
  els.conversationItems = document.getElementById('conversationItems');

  els.addContactForm = document.getElementById('addContactForm');
  els.contactName = document.getElementById('contactName');
  els.contactPhone = document.getElementById('contactPhone');
  els.contactEmail = document.getElementById('contactEmail');

  els.chatAvatar = document.getElementById('chatAvatar');
  els.chatName = document.getElementById('chatName');
  els.chatStatus = document.getElementById('chatStatus');
  els.chatTimeline = document.getElementById('chatTimeline');
  els.chatForm = document.getElementById('chatForm');
  els.chatInput = document.getElementById('chatInput');

  els.newChatSearch = document.getElementById('newChatSearch');
  els.newChatList = document.getElementById('newChatList');

  els.sidebarUserName = document.getElementById('sidebarUserName');
  els.sidebarUserHandle = document.getElementById('sidebarUserHandle');
  els.sidebarUserAvatar = document.getElementById('sidebarUserAvatar');

  els.profileAvatar = document.getElementById('profileAvatar');
  els.profileName = document.getElementById('profileName');
  els.profileHandle = document.getElementById('profileHandle');
  els.profileStatus = document.getElementById('profileStatus');

  els.profileEditBtn = document.getElementById('profileEditBtn');
  els.profileNotificationBtn = document.getElementById('profileNotificationBtn');
  els.profileThemeBtn = document.getElementById('profileThemeBtn');

  els.settingsAppearanceBtn = document.getElementById('settingsAppearanceBtn');
  els.settingsNotificationsBtn = document.getElementById('settingsNotificationsBtn');
  els.settingsPrivacyBtn = document.getElementById('settingsPrivacyBtn');
  els.settingsStorageBtn = document.getElementById('settingsStorageBtn');
  els.settingsAboutBtn = document.getElementById('settingsAboutBtn');

  els.appearanceToggle = document.getElementById('appearanceToggle');
  els.notificationsToggle = document.getElementById('notificationsToggle');
  els.privacyToggle = document.getElementById('privacyToggle');
  els.notificationStatus = document.getElementById('notificationStatus');
  els.privacyStatus = document.getElementById('privacyStatus');

  els.headerSearchBtn = document.getElementById('headerSearchBtn');
  els.headerNotificationBtn = document.getElementById('headerNotificationBtn');

  els.emergencyStatusText = document.getElementById('emergencyStatusText');
  els.addEmergencyContactForm = document.getElementById('addEmergencyContactForm');
  els.emergencyContactSelect = document.getElementById('emergencyContactSelect');
  els.emergencyRelationship = document.getElementById('emergencyRelationship');
  els.emergencyContactsList = document.getElementById('emergencyContactsList');
  els.smartSosButton = document.getElementById('smartSosButton');
  els.sosHoldProgressWrap = document.getElementById('sosHoldProgressWrap');
  els.sosHoldProgressBar = document.getElementById('sosHoldProgressBar');
  els.sosCountdownWrap = document.getElementById('sosCountdownWrap');
  els.sosCountdownText = document.getElementById('sosCountdownText');
  els.sosCancelBtn = document.getElementById('sosCancelBtn');

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

function currentUserIdentity() {
  if (!state.currentUser) return 'guest';
  return (state.currentUser.email || state.currentUser.phone || 'guest').trim().toLowerCase();
}

function buildHandle(value) {
  if (!value) return '@guest';
  const cleaned = value.split('@')[0].replace(/[^a-zA-Z0-9_.-]/g, '').toLowerCase();
  return `@${cleaned || 'user'}`;
}

function saveProfileState() {
  const identity = currentUserIdentity();
  if (identity === 'guest') return;

  const data = JSON.parse(localStorage.getItem('smartSmsProfileByIdentity') || '{}');
  data[identity] = {
    name: state.currentUser?.name || 'User',
    status: state.profileStatus,
  };
  localStorage.setItem('smartSmsProfileByIdentity', JSON.stringify(data));
}

function loadProfileState() {
  const theme = localStorage.getItem('smartSmsTheme');
  if (theme === 'light' || theme === 'dark') {
    state.settings.theme = theme;
  }

  const notifications = localStorage.getItem('smartSmsNotificationsEnabled');
  if (notifications !== null) {
    state.settings.notificationsEnabled = notifications === 'true';
  }

  const privacyMode = localStorage.getItem('smartSmsPrivacyMode');
  if (privacyMode === 'contacts-only' || privacyMode === 'everyone') {
    state.settings.privacyMode = privacyMode;
  }

  console.log(`📋 Loaded profile state - theme: ${state.settings.theme}, notifications: ${state.settings.notificationsEnabled}`);
  applyTheme(state.settings.theme);
}

function hydrateProfileFromStorage() {
  const identity = currentUserIdentity();
  if (identity === 'guest') return;

  const data = JSON.parse(localStorage.getItem('smartSmsProfileByIdentity') || '{}');
  const saved = data[identity];
  if (!saved) return;

  if (saved.name && state.currentUser) {
    state.currentUser.name = saved.name;
  }
  if (saved.status) {
    state.profileStatus = saved.status;
  }
}

function syncUserProfileUI() {
  const userName = state.currentUser?.name || 'Guest User';
  const identity = state.currentUser?.email || state.currentUser?.phone || 'guest';
  const handle = buildHandle(identity);
  const avatar = `https://i.pravatar.cc/120?u=${encodeURIComponent(identity)}`;

  if (els.sidebarUserName) els.sidebarUserName.textContent = userName;
  if (els.sidebarUserHandle) els.sidebarUserHandle.textContent = handle;
  if (els.sidebarUserAvatar) els.sidebarUserAvatar.src = avatar;

  if (els.profileName) els.profileName.textContent = userName;
  if (els.profileHandle) els.profileHandle.textContent = handle;
  if (els.profileAvatar) els.profileAvatar.src = avatar;
  if (els.profileStatus) els.profileStatus.textContent = state.profileStatus;
}

function refreshSettingsLabels() {
  if (els.appearanceToggle) {
    els.appearanceToggle.checked = state.settings.theme === 'dark';
  }

  if (els.notificationsToggle) {
    els.notificationsToggle.checked = state.settings.notificationsEnabled;
  }

  if (els.notificationStatus) {
    els.notificationStatus.textContent = state.settings.notificationsEnabled ? 'On' : 'Off';
  }

  if (els.privacyToggle) {
    els.privacyToggle.checked = state.settings.privacyMode === 'everyone';
  }

  if (els.privacyStatus) {
    els.privacyStatus.textContent = state.settings.privacyMode === 'contacts-only' ? 'Contacts only' : 'Everyone';
  }
}

function applyTheme(theme) {
  const normalized = theme === 'light' ? 'light' : 'dark';
  state.settings.theme = normalized;
  
  // Apply dark/light to root element for Tailwind
  if (normalized === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  
  localStorage.setItem('smartSmsTheme', normalized);
  console.log(`✅ Theme applied: ${normalized}`);
}

function toggleTheme() {
  const nextTheme = state.settings.theme === 'dark' ? 'light' : 'dark';
  console.log(`🔄 Toggling theme from ${state.settings.theme} to ${nextTheme}`);
  applyTheme(nextTheme);
  refreshSettingsLabels();
}

function toggleNotifications() {
  state.settings.notificationsEnabled = !state.settings.notificationsEnabled;
  localStorage.setItem('smartSmsNotificationsEnabled', String(state.settings.notificationsEnabled));
  refreshSettingsLabels();
}

function togglePrivacyMode() {
  state.settings.privacyMode = state.settings.privacyMode === 'contacts-only' ? 'everyone' : 'contacts-only';
  localStorage.setItem('smartSmsPrivacyMode', state.settings.privacyMode);
  refreshSettingsLabels();
}

function clearCachedChatData() {
  state.messages = {};
  state.seenMessageIds = new Set();
  state.conversations.forEach((item) => {
    item.lastMessage = '';
    item.unread = 0;
    item.time = 'now';
  });

  renderHome();
}

function setEmergencyStatus(message, isError = false) {
  if (!els.emergencyStatusText) return;
  els.emergencyStatusText.textContent = message;
  els.emergencyStatusText.className = `text-xs mb-4 ${isError ? 'text-rose-300' : 'text-emerald-300'}`;
}

function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported in this browser.'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        resolve({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          accuracy: pos.coords.accuracy,
        });
      },
      (err) => {
        reject(new Error(err.message || 'Unable to access device location.'));
      },
      { enableHighAccuracy: true, timeout: 12000 }
    );
  });
}

function renderEmergencyContactPicker() {
  if (!els.emergencyContactSelect) return;

  const usedContactIds = new Set(
    state.emergencyContacts
      .map((item) => item.contact_detail?.id || item.contact)
      .filter(Boolean)
  );

  const available = state.contacts.filter((c) => !usedContactIds.has(c.id));
  const options = ['<option value="">Select contact</option>']
    .concat(
      available.map((c) => `<option value="${c.id}">${escapeHtml(c.name)} (${escapeHtml(c.email || c.phone || '')})</option>`)
    )
    .join('');

  els.emergencyContactSelect.innerHTML = options;
}

function renderEmergencyContactsList() {
  if (!els.emergencyContactsList) return;

  if (!state.emergencyContacts.length) {
    els.emergencyContactsList.innerHTML = '<p class="text-xs text-slate-400">No emergency contacts added yet.</p>';
    return;
  }

  els.emergencyContactsList.innerHTML = state.emergencyContacts
    .map((item) => {
      const detail = item.contact_detail || {};
      const relationship = item.relationship || 'Emergency Contact';
      return `
        <div class="flex items-center justify-between rounded-lg border border-white/10 bg-white/3 px-3 py-2">
          <div class="min-w-0">
            <p class="truncate text-sm">${escapeHtml(detail.name || 'Unknown')}</p>
            <p class="truncate text-xs text-slate-400">${escapeHtml(relationship)} • ${escapeHtml(detail.email || detail.phone || '')}</p>
          </div>
          <button class="secondary-link text-xs" data-remove-emergency-id="${item.id}">Remove</button>
        </div>
      `;
    })
    .join('');
}

async function onAddEmergencyContactSubmit(event) {
  event.preventDefault();

  const contactId = (els.emergencyContactSelect?.value || '').trim();
  const relationship = (els.emergencyRelationship?.value || '').trim();

  if (!contactId) {
    setEmergencyStatus('Select a contact first.', true);
    return;
  }

  const result = await addEmergencyContact({ contact: contactId, relationship });
  if (!result.ok) {
    setEmergencyStatus(`Add emergency contact failed: ${result.error}`, true);
    return;
  }

  if (els.emergencyRelationship) {
    els.emergencyRelationship.value = '';
  }

  setEmergencyStatus('Emergency contact added.');
  await loadEmergencyData();
}

async function onEmergencyContactsListClick(event) {
  const removeId = event.target?.dataset?.removeEmergencyId;
  if (!removeId) return;

  const result = await removeEmergencyContact(removeId);
  if (!result.ok) {
    setEmergencyStatus(`Remove failed: ${result.error}`, true);
    return;
  }

  setEmergencyStatus('Emergency contact removed.');
  await loadEmergencyData();
}

async function loadEmergencyData() {
  if (!state.currentUser) return;

  const [emergencyContactsResult, activeSosResult] = await Promise.all([
    getEmergencyContacts(),
    getActiveSOS(),
  ]);

  if (emergencyContactsResult.ok) {
    state.emergencyContacts = emergencyContactsResult.contacts;
    renderEmergencyContactsList();
    renderEmergencyContactPicker();
  } else {
    setEmergencyStatus(`Failed to load emergency contacts: ${emergencyContactsResult.error}`, true);
  }

  if (!emergencyContactsResult.ok || !state.emergencyContacts.length) {
    setEmergencyStatus('Add at least one emergency contact below before sending SOS.', true);
  }

  if (activeSosResult.ok) {
    const active = activeSosResult.active[0];
    state.activeSosId = active?.id || '';
    if (state.activeSosId) {
      startLiveLocationUpdates();
    }
  }
}

function resetSosHoldVisuals() {
  state.isHoldingSos = false;
  if (state.sosHoldProgressTimer) {
    clearInterval(state.sosHoldProgressTimer);
    state.sosHoldProgressTimer = null;
  }
  if (els.sosHoldProgressBar) {
    els.sosHoldProgressBar.style.width = '0%';
  }
  if (els.sosHoldProgressWrap) {
    els.sosHoldProgressWrap.classList.add('hidden');
  }
}

function cancelSosCountdown() {
  if (state.sosCountdownTimer) {
    clearInterval(state.sosCountdownTimer);
    state.sosCountdownTimer = null;
  }
  state.sosCountdownValue = 0;
  if (els.sosCountdownWrap) {
    els.sosCountdownWrap.classList.add('hidden');
  }
  setEmergencyStatus('Emergency request cancelled.');
}

async function sendSingleLiveLocationUpdate() {
  if (!state.activeSosId) return;

  let location;
  try {
    location = await getCurrentLocation();
  } catch {
    return;
  }

  const result = await addSOSLocation(state.activeSosId, {
    latitude: location.latitude,
    longitude: location.longitude,
    accuracy: location.accuracy,
  });

  if (!result.ok) {
    setEmergencyStatus('Live update failed. Retrying on next cycle.', true);
    return;
  }

  const mapsUrl = `https://maps.google.com/?q=${location.latitude},${location.longitude}`;
  setEmergencyStatus(`Live location sent. ${mapsUrl}`);
}

function stopLiveLocationUpdates() {
  if (state.sosLiveUpdateTimer) {
    clearInterval(state.sosLiveUpdateTimer);
    state.sosLiveUpdateTimer = null;
  }
}

function startLiveLocationUpdates() {
  // Intentionally disabled for single-message SOS mode.
  // Keep function for future re-enable without changing call sites.
  stopLiveLocationUpdates();
}

async function triggerSmartSosNow() {
  cancelSosCountdown();
  setEmergencyStatus('Fetching location and sending SOS...');

  let location;
  try {
    location = await getCurrentLocation();
  } catch (error) {
    setEmergencyStatus(`Location permission required: ${error.message}`, true);
    return;
  }

  const payload = {
    user_id: state.currentUser?.id,
    latitude: location.latitude,
    longitude: location.longitude,
  };

  const result = await triggerEmergency(payload);
  if (!result.ok) {
    setEmergencyStatus(`Emergency request failed: ${result.error}`, true);
    return;
  }

  state.activeSosId = result.data?.id || '';
  const mapsUrl = `https://maps.google.com/?q=${location.latitude},${location.longitude}`;
  setEmergencyStatus(`Emergency alert sent successfully. Shared map link: ${mapsUrl}`);
}

function startSosCountdown() {
  state.sosCountdownValue = 3;
  if (els.sosCountdownWrap) {
    els.sosCountdownWrap.classList.remove('hidden');
  }
  if (els.sosCountdownText) {
    els.sosCountdownText.textContent = `Sending in ${state.sosCountdownValue}...`;
  }

  state.sosCountdownTimer = setInterval(() => {
    state.sosCountdownValue -= 1;
    if (state.sosCountdownValue <= 0) {
      clearInterval(state.sosCountdownTimer);
      state.sosCountdownTimer = null;
      triggerSmartSosNow();
      return;
    }
    if (els.sosCountdownText) {
      els.sosCountdownText.textContent = `Sending in ${state.sosCountdownValue}...`;
    }
  }, 1000);
}

function onSosHoldStart() {
  if (!state.currentUser) {
    setEmergencyStatus('Login required.', true);
    return;
  }
  if (state.isHoldingSos) return;

  state.isHoldingSos = true;
  setEmergencyStatus('Holding...');

  if (els.sosHoldProgressWrap) {
    els.sosHoldProgressWrap.classList.remove('hidden');
  }

  const holdMs = 2500;
  const startedAt = Date.now();
  state.sosHoldProgressTimer = setInterval(() => {
    const elapsed = Date.now() - startedAt;
    const pct = Math.min(100, (elapsed / holdMs) * 100);
    if (els.sosHoldProgressBar) {
      els.sosHoldProgressBar.style.width = `${pct}%`;
    }
  }, 40);

  state.sosLongPressTimer = setTimeout(() => {
    resetSosHoldVisuals();
    startSosCountdown();
  }, holdMs);
}

function onSosHoldEnd() {
  if (!state.isHoldingSos) return;
  if (state.sosLongPressTimer) {
    clearTimeout(state.sosLongPressTimer);
    state.sosLongPressTimer = null;
  }
  resetSosHoldVisuals();
  if (!state.sosCountdownTimer) {
    setEmergencyStatus('Press and hold for Emergency Help (2.5 seconds)');
  }
}

function onEditProfile() {
  if (!state.currentUser) {
    alert('Login first to edit profile.');
    return;
  }

  const newName = prompt('Enter your display name', state.currentUser.name || '');
  if (newName === null) {
    return;
  }

  const cleanedName = newName.trim();
  if (cleanedName) {
    state.currentUser.name = cleanedName;
  }

  const newStatus = prompt('Enter your profile status', state.profileStatus || '');
  if (newStatus !== null) {
    const cleanedStatus = newStatus.trim();
    if (cleanedStatus) {
      state.profileStatus = cleanedStatus;
    }
  }

  saveProfileState();
  syncUserProfileUI();
  alert('Profile updated.');
}

function onLogout() {
  stopMessagePolling();
  stopLiveLocationUpdates();
  clearAuthToken();
  state.currentUser = null;
  syncUserProfileUI();
  setScreen('login');
  closeSidebar();
}

function getActiveConversation() {
  return state.conversations.find((item) => item.id === state.activeConversationId);
}

function getMessagesForActiveConversation() {
  return state.messages[state.activeConversationId] || [];
}

function formatTimeLabel(value) {
  if (!value) return 'now';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'now';
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function displayNameFromAddress(address) {
  if (!address) return 'Unknown';
  if (address.includes('@')) {
    return address.split('@')[0];
  }
  return address;
}

function normalizeIdentity(value) {
  const raw = (value || '').toString().trim().toLowerCase();
  if (!raw) return '';
  if (raw.includes('@')) return raw;
  return raw.replace(/[^0-9]/g, '');
}

function ensureConversationForContact(contact) {
  let conversation = state.conversations.find((item) => item.id === contact.id);
  if (!conversation) {
    conversation = {
      id: contact.id,
      name: contact.name,
      phone: contact.phone || '',
      email: contact.email || '',
      avatar: contact.avatar,
      status: 'Available',
      lastMessage: '',
      time: 'now',
      unread: 0,
      typing: false,
    };
    state.conversations.unshift(conversation);
    state.messages[conversation.id] = state.messages[conversation.id] || [];
  }
  return conversation;
}

function findOrCreateContactByAddress(address) {
  let contact = state.contacts.find((item) => item.email === address || item.phone === address);
  if (!contact) {
    contact = {
      id: `msg-${address}`,
      name: displayNameFromAddress(address),
      phone: address.includes('@') ? '' : address,
      email: address.includes('@') ? address : '',
      avatar: `https://i.pravatar.cc/100?u=${address}`,
      lastMessage: '',
      time: 'now',
    };
    state.contacts.push(contact);
  }
  return contact;
}

async function syncMessagesFromServer() {
  if (!state.currentUser) return;

  const result = await getMessages();
  if (!result.ok) {
    return;
  }

  const myIdentities = new Set([
    normalizeIdentity(state.currentUser.email),
    normalizeIdentity(state.currentUser.phone),
  ].filter(Boolean));

  for (const msg of result.messages) {
    if (state.seenMessageIds.has(msg.id)) {
      continue;
    }

    const isMine = myIdentities.has(normalizeIdentity(msg.sender));
    const counterparty = isMine ? msg.recipient : msg.sender;
    const contact = findOrCreateContactByAddress(counterparty);
    const conversation = ensureConversationForContact(contact);

    const convoMessages = state.messages[conversation.id] || [];
    if (convoMessages.some((item) => item.backendId === msg.id)) {
      state.seenMessageIds.add(msg.id);
      continue;
    }

    convoMessages.push({
      id: convoMessages.length + 1,
      backendId: msg.id,
      sender: isMine ? 'me' : 'them',
      text: msg.message,
      time: formatTimeLabel(msg.created_at),
    });
    state.messages[conversation.id] = convoMessages;

    conversation.lastMessage = msg.message;
    conversation.time = formatTimeLabel(msg.created_at);

    if (!isMine && state.activeConversationId !== conversation.id) {
      conversation.unread = (conversation.unread || 0) + 1;
    }

    state.seenMessageIds.add(msg.id);
  }

  renderHome();
  renderNewChatList();
}

function startMessagePolling() {
  if (state.messagePollHandle) {
    clearInterval(state.messagePollHandle);
  }
  state.messagePollHandle = setInterval(() => {
    syncMessagesFromServer();
  }, 3000);
}

function stopMessagePolling() {
  if (state.messagePollHandle) {
    clearInterval(state.messagePollHandle);
    state.messagePollHandle = null;
  }
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

  // Opening a chat marks its unread counter as read.
  active.unread = 0;

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
            <p>${formatMessageText(msg.text)}</p>
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
      const contact = state.contacts.find((item) => item.id === button.dataset.contactId);
      if (contact) {
        const existingConversation = state.conversations.find((item) => item.id === contact.id);

        if (!existingConversation) {
          state.conversations.unshift({
            id: contact.id,
            name: contact.name,
            phone: contact.phone,
            avatar: contact.avatar,
            status: 'New contact',
            lastMessage: '',
            time: 'now',
            unread: 0,
            typing: false,
          });

          state.messages[contact.id] = [];
        }

        state.activeConversationId = contact.id;
      }

      setView('home');
      renderHome();
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
    state.currentUser = result.user;
    hydrateProfileFromStorage();
    syncUserProfileUI();
    state.seenMessageIds = new Set();
    state.conversations = [];
    state.messages = {};

    // Fetch contacts after login
    const contactsResult = await getContacts();
    if (contactsResult.ok) {
      state.contacts = contactsResult.contacts.map(c => ({
        id: c.id,
        name: c.name,
        phone: c.phone,
        email: c.email || '',
        avatar: `https://i.pravatar.cc/100?u=${c.email || c.phone}`,
        lastMessage: '',
        time: 'now',
      }));

      state.contacts.forEach((contact) => {
        ensureConversationForContact(contact);
      });
    } else {
      state.contacts = [];
    }

    await syncMessagesFromServer();
    startMessagePolling();

    if (state.conversations.length > 0) {
      state.activeConversationId = state.conversations[0].id;
    }

    await loadEmergencyData();
    
    setScreen('app');
    setView('home');
    renderHome();
  } else {
    alert('Login failed: ' + (result.error || 'Unknown error'));
    console.error('Login error:', result.error);
  }
}

async function onSignupSubmit(event) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const values = Object.fromEntries(formData.entries());

  console.log('Signup values:', values);

  // Validate passwords match
  if (values.password !== values.password_confirm) {
    alert('Passwords do not match!');
    console.error('Password mismatch');
    return;
  }

  const result = await signupUser(values);
  console.log('Signup result:', result);
  
  if (result.ok) {
    alert('Account created! Please verify with OTP');
    state.currentUser = result.user || { name: values.name, email: values.email, phone: values.phone || '' };
    hydrateProfileFromStorage();
    syncUserProfileUI();
    setScreen('app');
    setView('home');
    renderHome();
    await loadEmergencyData();
  } else {
    alert('Sign up failed: ' + (result.error || 'Unknown error'));
    console.error('Signup error:', result.error);
  }
}

async function onChatSubmit(event) {
  event.preventDefault();
  const text = (els.chatInput.value || '').trim();
  if (!text) return;

  if (state.isSendingMessage) {
    return;
  }

  const active = getActiveConversation();
  const recipientAddress = active?.email || active?.phone;
  if (!recipientAddress) {
    alert('Select a contact with email or phone from New Chat first.');
    return;
  }

  const signature = `${recipientAddress}::${text}`;
  const now = Date.now();
  if (state.lastSentSignature === signature && now - state.lastSentAt < 1200) {
    return;
  }

  state.isSendingMessage = true;
  state.lastSentSignature = signature;
  state.lastSentAt = now;

  const payload = {
    to: recipientAddress,
    text,
  };

  try {
    const apiResult = await sendMessageApi(payload);
    if (!apiResult.ok) {
      alert('Message failed: ' + (apiResult.error || 'Unknown error'));
      return;
    }

    // Add once using backend ID so polling does not duplicate it.
    const sent = apiResult.data;
    const messages = getMessagesForActiveConversation();
    if (sent?.id && !messages.some((item) => item.backendId === sent.id)) {
      const nextId = messages.length ? Math.max(...messages.map((item) => item.id)) + 1 : 1;
      messages.push({
        id: nextId,
        backendId: sent.id,
        sender: 'me',
        text: sent.message || text,
        time: formatTimeLabel(sent.created_at) || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      });
      state.seenMessageIds.add(sent.id);
    }

    active.lastMessage = text;
    active.time = 'now';
    active.unread = 0;

    els.chatInput.value = '';
    renderHome();
    await syncMessagesFromServer();
  } finally {
    state.isSendingMessage = false;
  }
}

async function onAddContactSubmit(event) {
  event.preventDefault();
  
  const { createContact } = await import('./api.js');
  
  const name = (els.contactName.value || '').trim();
  const phone = (els.contactPhone?.value || '').trim();
  const email = (els.contactEmail.value || '').trim();
  
  if (!name || (!phone && !email)) {
    alert('Name and email are required');
    return;
  }
  
  const result = await createContact({ name, phone, email: email || null });
  
  if (result.ok) {
    alert('Contact added successfully!');
    
    // Add to state
    const newContact = {
      id: result.contact.id,
      name: result.contact.name,
      phone: result.contact.phone || '',
      email: result.contact.email || '',
      avatar: `https://i.pravatar.cc/100?u=${result.contact.email || result.contact.phone || result.contact.id}`,
      lastMessage: '',
      time: 'now',
    };
    
    state.contacts.push(newContact);

    // Also show new contact in Home recents immediately
    const existingConversation = state.conversations.find((item) => item.id === newContact.id);
    if (!existingConversation) {
      state.conversations.unshift({
        id: newContact.id,
        name: newContact.name,
        phone: newContact.phone,
        email: newContact.email,
        avatar: newContact.avatar,
        status: 'Available',
        lastMessage: 'New contact added',
        time: 'now',
        unread: 0,
        typing: false,
      });
      state.messages[newContact.id] = state.messages[newContact.id] || [];
    }
    
    // Clear form and refresh list
    els.contactName.value = '';
    if (els.contactPhone) {
      els.contactPhone.value = '';
    }
    els.contactEmail.value = '';
    
    renderNewChatList();
    renderConversations();
  } else {
    alert('Failed to add contact: ' + (result.error || 'Unknown error'));
    console.error('Add contact error:', result.error);
  }
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
  try {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  } catch (err) {
    console.warn('⚠️ Icon refresh failed:', err.message);
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

function formatMessageText(value) {
  const safe = escapeHtml(value || '');
  const urlRegex = /(https?:\/\/[^\s<]+)/g;
  return safe.replace(urlRegex, (url) => {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="underline">${url}</a>`;
  });
}

function bindEvents() {
  // Transition from splash to login after 2.3 seconds
  window.setTimeout(() => {
    try {
      console.log('🔄 Transitioning from splash to login...');
      setScreen('login');
      refreshIcons();
      console.log('✅ Transitioned to login');
    } catch (err) {
      console.error('❌ Error during transition:', err);
      // Force login screen even if there's an error
      setScreen('login');
    }
  }, 2300);

  els.gotoSignupBtn.addEventListener('click', () => setScreen('signup'));
  els.gotoLoginBtn.addEventListener('click', () => setScreen('login'));

  els.loginForm.addEventListener('submit', onLoginSubmit);
  els.signupForm.addEventListener('submit', onSignupSubmit);
  els.addContactForm.addEventListener('submit', onAddContactSubmit);
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
      if (button.dataset.view === 'settings') {
        loadEmergencyData();
      }
    });
  });

  els.conversationSearch.addEventListener('input', renderConversations);
  els.newChatSearch.addEventListener('input', renderNewChatList);

  els.sidebarToggle.addEventListener('click', openSidebar);
  els.sidebarBackdrop.addEventListener('click', closeSidebar);

  els.logoutBtn.addEventListener('click', onLogout);
  if (els.profileLogoutBtn) {
    els.profileLogoutBtn.addEventListener('click', onLogout);
  }

  if (els.profileEditBtn) {
    els.profileEditBtn.addEventListener('click', onEditProfile);
  }

  if (els.profileNotificationBtn) {
    els.profileNotificationBtn.addEventListener('click', toggleNotifications);
  }

  if (els.profileThemeBtn) {
    els.profileThemeBtn.addEventListener('click', toggleTheme);
  }

  if (els.settingsAppearanceBtn) {
    els.settingsAppearanceBtn.addEventListener('click', toggleTheme);
  }

  if (els.settingsNotificationsBtn) {
    els.settingsNotificationsBtn.addEventListener('click', toggleNotifications);
  }

  if (els.settingsPrivacyBtn) {
    els.settingsPrivacyBtn.addEventListener('click', togglePrivacyMode);
  }

  // Wire toggle switches
  if (els.appearanceToggle) {
    els.appearanceToggle.addEventListener('change', (e) => {
      console.log(`👁️ Appearance toggle changed to: ${e.target.checked}`);
      toggleTheme();
    });
  }

  if (els.notificationsToggle) {
    els.notificationsToggle.addEventListener('change', () => {
      console.log('🔔 Notifications toggle changed');
      toggleNotifications();
    });
  }

  if (els.privacyToggle) {
    els.privacyToggle.addEventListener('change', () => {
      console.log('🔒 Privacy toggle changed');
      togglePrivacyMode();
    });
  }

  if (els.settingsStorageBtn) {
    els.settingsStorageBtn.addEventListener('click', clearCachedChatData);
  }

  if (els.smartSosButton) {
    els.smartSosButton.addEventListener('pointerdown', onSosHoldStart);
    els.smartSosButton.addEventListener('pointerup', onSosHoldEnd);
    els.smartSosButton.addEventListener('pointerleave', onSosHoldEnd);
    els.smartSosButton.addEventListener('pointercancel', onSosHoldEnd);
  }

  if (els.sosCancelBtn) {
    els.sosCancelBtn.addEventListener('click', cancelSosCountdown);
  }

  if (els.addEmergencyContactForm) {
    els.addEmergencyContactForm.addEventListener('submit', onAddEmergencyContactSubmit);
  }

  if (els.emergencyContactsList) {
    els.emergencyContactsList.addEventListener('click', onEmergencyContactsListClick);
  }

  if (els.headerNotificationBtn) {
    els.headerNotificationBtn.addEventListener('click', () => {
      setView('settings');
    });
  }

  if (els.headerSearchBtn) {
    els.headerSearchBtn.addEventListener('click', () => {
      if (state.currentView !== 'home') {
        setView('home');
      }
      els.conversationSearch?.focus();
    });
  }

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
  if (window.__SMART_SMS_INIT__) {
    return;
  }
  window.__SMART_SMS_INIT__ = true;

  try {
    console.log('🚀 Initializing app...');
    cacheElements();
    console.log('✅ Elements cached');

    loadProfileState();
    syncUserProfileUI();
    refreshSettingsLabels();
    
    bindEvents();
    console.log('✅ Events bound');
    
    setScreen('splash');
    console.log('✅ Splash screen shown');
    
    setView('home');
    console.log('✅ Home view set');
    
    // Don't render content on splash screen - wait until login
    renderHome();
    renderNewChatList();
    evaluatePasswordStrength('');
    
    setTimeout(() => {
      try {
        refreshIcons();
        console.log('✅ Icons refreshed');
      } catch (err) {
        console.warn('⚠️ Icon refresh failed:', err.message);
      }
    }, 100);
    
    console.log('✅ App initialized successfully');
  } catch (err) {
    console.error('❌ Initialization error:', err);
    // Force show login screen even if there's an error
    setScreen('login');
  }
}

window.addEventListener('DOMContentLoaded', init);
