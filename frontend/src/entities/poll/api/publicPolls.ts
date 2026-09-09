import type { Poll, VoteConfirmation } from '../model/types'
import { request } from '../../../shared/api/http'

export function getPublicPoll(pollId: string): Promise<Poll> {
  return request<Poll>(`/polls/${pollId}`)
}

export function submitVote(pollId: string, optionIds: string[]): Promise<VoteConfirmation> {
  return request<VoteConfirmation>(`/polls/${pollId}/votes`, {
    method: 'POST',
    body: JSON.stringify({ option_ids: optionIds }),
  })
}
