// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';
const REQUEST_TIMEOUT = 10000; // 10 seconds

// Store auth token in localStorage
let authToken = localStorage.getItem('authToken');

/**
 * Fetch with timeout
 */
function fetchWithTimeout(url, options = {}) {
  return Promise.race([
    fetch(url, options),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout - backend not responding')), REQUEST_TIMEOUT)
    ),
  ]);
}

/**
 * Login user with phone and password
 */
export async function loginUser(payload) {
  try {
    console.log('🔄 Logging in...');
    const response = await fetchWithTimeout(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone_or_email: payload.phone || payload.email,
        password: payload.password,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      authToken = data.access;
      localStorage.setItem('authToken', authToken);
      console.log('✅ Login successful');
      return {
        ok: true,
        user: {
          id: data.user.id,
          name: data.user.full_name || data.user.phone,
          phone: data.user.phone,
          email: data.user.email,
        },
      };
    } else {
      const error = await response.json();
      console.error('❌ Login error:', error);
      return { ok: false, error: error.error || 'Login failed' };
    }
  } catch (err) {
    console.error('❌ Login exception:', err.message);
    return { ok: false, error: err.message };
  }
}

/**
 * Signup new user
 */
export async function signupUser(payload) {
  try {
    console.log('🔄 Signing up...');
    const response = await fetchWithTimeout(`${API_BASE_URL}/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: payload.phone,
        email: payload.email,
        full_name: payload.name,
        password: payload.password,
        password_confirm: payload.password,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ Signup successful');
      return {
        ok: true,
        user: { id: data.user_id, name: payload.name, phone: payload.phone, email: payload.email },
        user_id: data.user_id,
      };
    } else {
      const error = await response.json();
      // Handle field-specific errors (e.g., {"email": ["already exists"]})
      let errorMessage = error.error || 'Signup failed';
      
      if (typeof error === 'object' && !error.error) {
        const errorFields = Object.keys(error);
        const errorTexts = errorFields.map(field => {
          const messages = Array.isArray(error[field]) ? error[field] : [error[field]];
          return `${field}: ${messages.join(', ')}`;
        });
        errorMessage = errorTexts.join('\n');
      }
      
      console.error('❌ Signup error:', errorMessage);
      return { ok: false, error: errorMessage };
    }
  } catch (err) {
    console.error('❌ Signup exception:', err.message);
    return { ok: false, error: err.message };
  }
}

/**
 * Send message
 */
export async function sendMessage(payload) {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    console.log('🔄 Sending message...');
    const response = await fetchWithTimeout(`${API_BASE_URL}/messaging/messages/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        recipient: payload.to,
        message: payload.text,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ Message sent');
      return { ok: true, data };
    } else {
      const error = await response.json();
      console.error('❌ Send message error:', error);
      return { ok: false, error: error.detail || error.error || 'Message send failed' };
    }
  } catch (err) {
    console.error('❌ Send message exception:', err.message);
    return { ok: false, error: err.message };
  }
}

/**
 * Get message history for the logged-in user
 */
export async function getMessages() {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/messaging/messages/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      return { ok: true, messages: data.results || data || [] };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || 'Failed to fetch messages' };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Clear auth token from memory and localStorage
 */
export function clearAuthToken() {
  authToken = null;
  localStorage.removeItem('authToken');
}

/**
 * Get all contacts
 */
export async function getContacts() {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    console.log('🔄 Fetching contacts...');
    const response = await fetchWithTimeout(`${API_BASE_URL}/contacts/contacts/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ Contacts fetched:', data.results?.length || 0);
      return { ok: true, contacts: data.results || [] };
    } else {
      console.error('❌ Failed to fetch contacts');
      return { ok: false, error: 'Failed to fetch contacts' };
    }
  } catch (err) {
    console.error('❌ GetContacts exception:', err.message);
    return { ok: false, error: err.message };
  }
}

/**
 * Create a new contact
 */
export async function createContact(payload) {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    console.log('🔄 Creating contact...');
    const response = await fetchWithTimeout(`${API_BASE_URL}/contacts/contacts/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: payload.name,
        phone: payload.phone,
        email: payload.email,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ Contact created');
      return { ok: true, contact: data };
    } else {
      const error = await response.json();
      let errorMessage = 'Failed to create contact';
      
      if (typeof error === 'object' && !error.error) {
        const errorFields = Object.keys(error);
        const errorTexts = errorFields.map(field => {
          const messages = Array.isArray(error[field]) ? error[field] : [error[field]];
          return `${field}: ${messages.join(', ')}`;
        });
        errorMessage = errorTexts.join('\n');
      }
      
      console.error('❌ CreateContact error:', errorMessage);
      return { ok: false, error: errorMessage };
    }
  } catch (err) {
    console.error('❌ CreateContact exception:', err.message);
    return { ok: false, error: err.message };
  }
}

/**
 * Get emergency contacts linked to current user.
 */
export async function getEmergencyContacts() {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/contacts/emergency-contacts/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      return { ok: true, contacts: data.results || data || [] };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || error.error || 'Failed to fetch emergency contacts' };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Add a contact as emergency contact.
 */
export async function addEmergencyContact(payload) {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/contacts/emergency-contacts/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contact: payload.contact,
        relationship: payload.relationship || '',
      }),
    });

    if (response.ok) {
      return { ok: true, data: await response.json() };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || error.error || JSON.stringify(error) };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Remove emergency contact by emergency-contact ID.
 */
export async function removeEmergencyContact(emergencyContactId) {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/contacts/emergency-contacts/${emergencyContactId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok || response.status === 204) {
      return { ok: true };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || error.error || 'Failed to remove emergency contact' };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Trigger emergency SOS.
 */
export async function triggerSOS(payload) {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/emergency/sos/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      return { ok: true, data: await response.json() };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || error.error || JSON.stringify(error) };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Smart SOS trigger endpoint requiring only authenticated user
 * (optional user_id, latitude, longitude).
 */
export async function triggerEmergency(payload = {}) {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/emergency/trigger/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      return { ok: true, data: await response.json() };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || error.error || JSON.stringify(error) };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * List SOS history for current user.
 */
export async function getSOSList() {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/emergency/sos/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      return { ok: true, sos: data.results || data || [] };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || error.error || 'Failed to fetch SOS list' };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Get active SOS entries.
 */
export async function getActiveSOS() {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/emergency/sos/active/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      return { ok: true, active: data.active_emergencies || [] };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || error.error || 'Failed to fetch active SOS' };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Add live location update to a specific SOS.
 */
export async function addSOSLocation(sosId, payload) {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/emergency/sos/${sosId}/add_location/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      return { ok: true, data: await response.json() };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || error.error || JSON.stringify(error) };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Resolve or cancel an SOS.
 */
export async function updateSOSStatus(sosId, statusValue) {
  try {
    if (!authToken) {
      return { ok: false, error: 'Not authenticated' };
    }

    const response = await fetchWithTimeout(`${API_BASE_URL}/emergency/sos/${sosId}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: statusValue }),
    });

    if (response.ok) {
      return { ok: true, data: await response.json() };
    }

    const error = await response.json();
    return { ok: false, error: error.detail || error.error || JSON.stringify(error) };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}
