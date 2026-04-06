const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function getUser(userId) {
  const res = await fetch(`${API_URL}/api/v1/users/${userId}`);
  return res.json();
}

export async function logMeal(mealData) {
  const res = await fetch(`${API_URL}/api/v1/meals/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(mealData),
  });
  return res.json();
}

export async function getDailyMacros(userId, date) {
  const res = await fetch(`${API_URL}/api/v1/meals/daily/${userId}/${date}`);
  return res.json();
}

export async function getProgress(userId, days = 7) {
  const res = await fetch(`${API_URL}/api/v1/progress/analysis/${userId}?days=${days}`);
  return res.json();
}

export async function getRecommendations(userId) {
  const res = await fetch(`${API_URL}/api/v1/progress/recommendations/${userId}`);
  return res.json();
}
