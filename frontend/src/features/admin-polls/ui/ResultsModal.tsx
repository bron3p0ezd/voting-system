import type { Poll, PollResults } from '../../../entities/poll/model/types'
import { Modal } from '../../../shared/ui/Modal'

interface ResultsModalProps { error: string | null; isLoading: boolean; onClose: () => void; poll: Poll; results: PollResults | null }

export function ResultsModal({ error, isLoading, onClose, poll, results }: ResultsModalProps) {
  return <Modal onClose={onClose} title="Статистика опроса"><p className="mb-4 font-medium">{poll.question}</p>{isLoading && <p className="text-sm text-neutral-500">Загрузка статистики…</p>}{error && <p className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</p>}{results && <div><p className="mb-3 text-sm text-neutral-600">Участников: <strong className="text-black">{results.total_participants}</strong></p><ul className="divide-y divide-neutral-200 border-y border-neutral-200">{results.results.map((result) => <li className="flex items-center justify-between gap-4 py-3" key={result.option_id}><span>{result.text}</span><span className="shrink-0 text-sm">{result.votes} · {Number(result.participant_percentage).toFixed(1)}%</span></li>)}</ul></div>}</Modal>
}
