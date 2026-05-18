import axios from 'axios';

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 15000,
});

http.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error),
);

interface ApiErrorLike {
  response?: {
    data?: {
      detail?: unknown;
      message?: unknown;
    };
  };
  message?: string;
}

export function getApiErrorMessage(error: unknown, fallback: string) {
  const apiError = error as ApiErrorLike;
  const detail = apiError.response?.data?.detail ?? apiError.response?.data?.message;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }
  if (typeof apiError.message === 'string' && apiError.message.trim()) {
    return `${fallback}（${apiError.message}）`;
  }

  return fallback;
}
