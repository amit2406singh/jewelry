// API wrapper to communicate with Python Flask server
// Using relative URLs so the Vite dev server proxy forwards them to Flask at port 5000.
// In production, configure your reverse proxy (nginx/etc.) to forward /api to Flask.
const BASE_URL = '/api';

/**
 * Custom fetch wrapper to handle errors
 * @param {string} endpoint 
 * @param {object} options 
 */
async function fetchJson(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      throw new Error(data.message || `Server responded with status ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error(`API Error in ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  async getAll() {
    return fetchJson('/jewelry');
  },

  async getJewelry(huid) {
    // URL-encode HUID to prevent injection or query issues
    return fetchJson(`/jewelry/${encodeURIComponent(huid.toUpperCase().trim())}`);
  },

  async registerJewelry(data) {
    return fetchJson('/jewelry/register', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async loginOwner(huid, passcode) {
    return fetchJson('/auth/owner', {
      method: 'POST',
      body: JSON.stringify({
        huid: huid.toUpperCase().trim(),
        passcode: passcode.trim()
      })
    });
  },

  async updateStatus(huid, status, passcode, theftDetails = '') {
    return fetchJson(`/jewelry/${encodeURIComponent(huid.toUpperCase().trim())}/status`, {
      method: 'PUT',
      body: JSON.stringify({
        status,
        passcode,
        theftDetails
      })
    });
  },

  async getStats() {
    return fetchJson('/stats');
  },

  async getLogs() {
    return fetchJson('/logs');
  },

  /** Health check – returns true if the Flask server is reachable */
  async healthCheck() {
    try {
      const res = await fetch('/api/health');
      return res.ok;
    } catch {
      return false;
    }
  }
};
