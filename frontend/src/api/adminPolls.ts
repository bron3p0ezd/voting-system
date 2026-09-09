import type { CreatePollPayload, Poll, PollResults } from '../types/poll'
import { request } from './http'

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
