import type { Poll } from '../../../entities/poll/model/types'
import { formatDate } from '../../../shared/lib/date'

interface PollsListProps { polls: Poll[]; currentTime: number; copiedPollId: string | null; onCopy: (pollId: string) => void; onOpenResults: (poll: Poll) => void }

export function PollsList({ polls, currentTime, copiedPollId, onCopy, onOpenResults }: PollsListProps) {
  return <ul className="divide-y divide-neutral-300 border-y border-neutral-300">{polls.map((poll) => {
    const isActive = new Date(poll.ends_at).getTime() > currentTime
    return <li key={poll.id}><div className="grid gap-3 px-2 py-5 sm:grid-cols-[1fr_auto] sm:items-center"><button className="min-w-0 text-left hover:underline hover:underline-offset-4" onClick={() => void onOpenResults(poll)} type="button"><span className="block text-lg font-medium">{poll.question}</span><span className="mt-1 block text-sm text-neutral-500">{formatDate(poll.starts_at)} — {formatDate(poll.ends_at)}</span><span className="mt-2 block text-sm text-neutral-700">Варианты: {poll.options.map((option) => <span className="mr-2 inline-block" key={option.id}>{option.text} <code className="bg-neutral-100 px-1 text-xs" title={option.id}>ID: {option.id}</code></span>)}</span></button><div className="flex flex-col items-start gap-2 sm:items-end"><span className={`inline-flex w-fit items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}><span className={`h-2 w-2 rounded-full ${isActive ? 'bg-green-600' : 'bg-red-600'}`} />{isActive ? 'Активный' : 'Закончен'}</span><div className="flex max-w-full items-center gap-2 text-xs"><code className="break-all bg-neutral-100 px-2 py-1" title={poll.id}>{poll.id}</code><button aria-label="Скопировать UUID опроса" className="shrink-0 rounded border border-neutral-400 px-2 py-1 hover:border-black" onClick={() => void onCopy(poll.id)} type="button">{copiedPollId === poll.id ? 'Скопировано' : 'Копировать'}</button></div></div></div></li>
  })}</ul>
}
