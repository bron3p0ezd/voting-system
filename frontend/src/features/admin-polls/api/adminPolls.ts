import type { CreatePollPayload, Poll, PollResults } from '../../../entities/poll/model/types'
import { request } from '../../../shared/api/http'
import { getAdminToken } from '../../admin-auth/model/session'

function adminRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAdminToken()
  return request<T>(path, {
    ...init,
    headers: token ? { ...init?.headers, Authorization: `Bearer ${token}` } : init?.headers,
  })
}

export function getPolls(): Promise<Poll[]> {
  return adminRequest<Poll[]>('/admin/polls')
}

export function createPoll(payload: CreatePollPayload): Promise<Poll> {
  return adminRequest<Poll>('/admin/polls', { method: 'POST', body: JSON.stringify(payload) })
}

export function getPollResults(pollId: string): Promise<PollResults> {
  return adminRequest<PollResults>(`/admin/polls/${pollId}/results`)
}
