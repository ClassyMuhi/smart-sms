/*
  API integration placeholder.
  Replace these with real backend calls to your Django endpoints.
*/

export async function loginUser(payload) {
  return Promise.resolve({ ok: true, user: { name: payload.email || 'User' } });
}

export async function signupUser(payload) {
  return Promise.resolve({ ok: true, user: { name: payload.name || 'User' } });
}

export async function sendMessage(payload) {
  return Promise.resolve({ ok: true, data: payload });
}
