import type { CreatePollPayload, Poll, PollResults } from '../types/poll'

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace(
  /\/$/,
  '',
)

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      ...init?.headers,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: unknown } | null
    const detail = typeof body?.detail === 'string' ? body.detail : null
    throw new Error(detail || `Ошибка запроса (${response.status})`)
  }

  return response.json() as Promise<T>
}

export function getPolls(): Promise<Poll[]> {
  return request<Poll[]>('/admin/polls')
}

export function createPoll(payload: CreatePollPayload): Promise<Poll> {
  return request<Poll>('/admin/polls', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getPollResults(pollId: string): Promise<PollResults> {
  return request<PollResults>(`/admin/polls/${pollId}/results`)
}
