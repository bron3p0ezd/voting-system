import { useState, type FormEvent } from 'react'
import type { CreatePollPayload, Poll, SelectionType } from '../../../entities/poll/model/types'
import { HttpError } from '../../../shared/api/http'
import { toDateTimeLocal } from '../../../shared/lib/date'
import { Modal } from '../../../shared/ui/Modal'
import { createPoll } from '../api/adminPolls'

interface CreatePollModalProps { onClose: () => void; onCreated: (poll: Poll) => void; onUnauthorized: () => void }

export function CreatePollModal({ onClose, onCreated, onUnauthorized }: CreatePollModalProps) {
  const now = new Date()
  const [question, setQuestion] = useState(''); const [selectionType, setSelectionType] = useState<SelectionType>('single')
  const [minSelections, setMinSelections] = useState('1'); const [maxSelections, setMaxSelections] = useState('1')
  const [startsAt, setStartsAt] = useState(toDateTimeLocal(now)); const [endsAt, setEndsAt] = useState(toDateTimeLocal(new Date(now.getTime() + 60 * 60_000)))
  const [options, setOptions] = useState(['', '']); const [error, setError] = useState<string | null>(null); const [selectionError, setSelectionError] = useState<string | null>(null); const [isSubmitting, setIsSubmitting] = useState(false)
  const changeSelectionType = (value: SelectionType) => { setSelectionType(value); setSelectionError(null); if (value === 'single') { setMinSelections('1'); setMaxSelections('1') } }
  const changeOption = (index: number, value: string) => setOptions((current) => current.map((option, optionIndex) => optionIndex === index ? value : option))
  const removeOption = (index: number) => setOptions((current) => current.filter((_, optionIndex) => optionIndex !== index))
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(null); setSelectionError(null)
    const normalizedOptions = options.map((option) => option.trim()); const start = new Date(startsAt); const end = new Date(endsAt); const minimum = Number(minSelections); const maximum = Number(maxSelections)
    if (!question.trim()) { setError('Введите вопрос.'); return }
    if (normalizedOptions.length < 2 || normalizedOptions.some((option) => !option)) { setError('Добавьте минимум два заполненных варианта ответа.'); return }
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end <= start) { setError('Время окончания должно быть позже времени начала.'); return }
    if (selectionType === 'multiple') {
      if (!Number.isInteger(minimum) || minimum < 1) { setSelectionError('Минимум должен быть не меньше 1.'); return }
      if (!Number.isInteger(maximum) || maximum < minimum) { setSelectionError('Максимум не может быть меньше минимума.'); return }
      if (maximum > normalizedOptions.length) { setSelectionError(`Максимум не может превышать число вариантов (${normalizedOptions.length}).`); return }
    }
    const payload: CreatePollPayload = { question: question.trim(), selection_type: selectionType, min_selections: selectionType === 'single' ? 1 : minimum, max_selections: selectionType === 'single' ? 1 : maximum, starts_at: start.toISOString(), ends_at: end.toISOString(), options: normalizedOptions }
    setIsSubmitting(true)
    try { const poll = await createPoll(payload); onCreated(poll); onClose() }
    catch (requestError) { if (requestError instanceof HttpError && requestError.status === 401) { onUnauthorized(); return }; setError(requestError instanceof Error ? requestError.message : 'Не удалось создать опрос.') }
    finally { setIsSubmitting(false) }
  }
  return <Modal onClose={onClose} size="large" title="Создать опрос"><form className="space-y-4" onSubmit={submit}>
    <label className="block"><span className="mb-1 block text-sm font-medium">Вопрос</span><input autoFocus className="w-full rounded border border-neutral-400 px-3 py-2 outline-none focus:border-black" onChange={(event) => setQuestion(event.target.value)} placeholder="Введите вопрос" value={question} /></label>
    <label className="block"><span className="mb-1 block text-sm font-medium">Тип выбора</span><select className="w-full rounded border border-neutral-400 bg-white px-3 py-2" onChange={(event) => changeSelectionType(event.target.value as SelectionType)} value={selectionType}><option value="single">Один вариант</option><option value="multiple">Несколько вариантов</option></select></label>
    {selectionType === 'multiple' && <><div className="grid grid-cols-2 gap-3"><label><span className="mb-1 block text-sm font-medium">Минимум</span><input className="number-field w-full rounded border border-neutral-400 px-3 py-2" min="1" onChange={(event) => { setMinSelections(event.target.value); setSelectionError(null) }} step="1" type="number" value={minSelections} /></label><label><span className="mb-1 block text-sm font-medium">Максимум</span><input className="number-field w-full rounded border border-neutral-400 px-3 py-2" min="1" onChange={(event) => { setMaxSelections(event.target.value); setSelectionError(null) }} step="1" type="number" value={maxSelections} /></label></div>{selectionError && <p className="mt-2 text-sm text-red-700">{selectionError}</p>}</>}
    <div className="grid gap-3 sm:grid-cols-2"><label><span className="mb-1 block text-sm font-medium">Начало</span><input className="w-full rounded border border-neutral-400 px-3 py-2" onChange={(event) => setStartsAt(event.target.value)} type="datetime-local" value={startsAt} /></label><label><span className="mb-1 block text-sm font-medium">Окончание</span><input className="w-full rounded border border-neutral-400 px-3 py-2" onChange={(event) => setEndsAt(event.target.value)} type="datetime-local" value={endsAt} /></label></div>
    <fieldset><legend className="mb-2 text-sm font-medium">Варианты ответа</legend><div className="space-y-2">{options.map((option, index) => <div className="flex gap-2" key={index}><input aria-label={`Вариант ${index + 1}`} className="min-w-0 flex-1 rounded border border-neutral-400 px-3 py-2" onChange={(event) => changeOption(index, event.target.value)} placeholder={`Вариант ${index + 1}`} value={option} /><button className="rounded border border-neutral-300 px-3 disabled:cursor-not-allowed disabled:opacity-40" disabled={options.length <= 2} onClick={() => removeOption(index)} type="button">Удалить</button></div>)}</div><button className="mt-2 text-sm underline underline-offset-2" onClick={() => setOptions((current) => [...current, ''])} type="button">+ Добавить вариант</button></fieldset>
    {error && <p className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</p>}<div className="flex justify-end gap-2 border-t border-neutral-200 pt-4"><button className="rounded border border-black px-4 py-2" onClick={onClose} type="button">Отмена</button><button className="rounded bg-black px-4 py-2 text-white disabled:opacity-50" disabled={isSubmitting} type="submit">{isSubmitting ? 'Создание…' : 'Создать'}</button></div>
  </form></Modal>
}
