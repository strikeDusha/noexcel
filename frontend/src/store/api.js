export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

// Здесь будут универсальные функции для запросов
export async function apiRequest(endpoint, options = {}) {
  const res = await fetch(`${API_URL}${endpoint}`, options);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
