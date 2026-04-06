const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function api(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };
  const res = await fetch(url, config);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || err.message || `HTTP ${res.status}`);
  }
  return res.json();
}

export const apiClient = {
  // Profile
  getProfile: (userId) => api(`/api/v1/profile/${userId}`),
  createProfile: (data) => api('/api/v1/profile', { method: 'POST', body: JSON.stringify(data) }),
  updateProfile: (userId, data) => api(`/api/v1/profile/${userId}`, { method: 'PUT', body: JSON.stringify(data) }),

  // Weight
  getWeightHistory: (userId, days = 30) => api(`/api/v1/users/${userId}/weight-history?days=${days}`),
  logWeight: async (userId, { weight, date }) =>
    api(`/api/v1/users/${userId}/weight`, { method: 'POST', body: JSON.stringify({ weight, date }) }),

  // Meals
  logMeal: (mealData) => api('/api/v1/log-meal', { method: 'POST', body: JSON.stringify(mealData) }),

  // Daily summary
  getDailySummary: (userId, date) => {
    const qs = date ? `?date=${date}` : '';
    return api(`/api/v1/daily-summary/${userId}${qs}`);
  },

  // Meal suggestions
  getMealSuggestions: (userId, constraints = {}) => {
    const params = new URLSearchParams(
      Object.fromEntries(
        Object.entries(constraints).filter(([_, v]) => v !== null && v !== undefined && v !== '')
      )
    ).toString();
    return api(`/api/v1/meal-suggestions/${userId}?${params}`);
  },

  // Progress
  getProgressAnalysis: (userId, days = 7) => api(`/api/v1/progress-analysis/${userId}?days=${days}`),

  // Recommendations
  getRecommendations: (userId) => api(`/api/v1/progress/recommendations/${userId}`),

  // Dashboard (combined)
  getDashboard: (userId) => api(`/api/v1/dashboard/${userId}`),

  // Settings
  updateSettings: (userId, settings) => api(`/api/v1/settings/${userId}`, { method: 'POST', body: JSON.stringify(settings) }),
};
