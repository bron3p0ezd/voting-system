export type SelectionType = 'single' | 'multiple'

export interface PollOption {
  id: string
  text: string
  position: number
}

export interface Poll {
  id: string
  question: string
  selection_type: SelectionType
  min_selections: number
  max_selections: number
  starts_at: string
  ends_at: string
  options: PollOption[]
}

export interface CreatePollPayload {
  question: string
  selection_type: SelectionType
  min_selections: number
  max_selections: number
  starts_at: string
  ends_at: string
  options: string[]
}

export interface PollResultItem {
  option_id: string
  text: string
  votes: number
  participant_percentage: number | string
}

export interface PollResults {
  poll_id: string
  total_participants: number
  results: PollResultItem[]
}

export interface VoteConfirmation {
  poll_id: string
  counted_at: string
}
