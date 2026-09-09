import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react'
import { createPoll, getPollResults, getPolls } from './api/adminPolls'
import { loginAdmin } from './api/adminAuth'
import { clearAdminToken, hasAdminToken } from './api/adminSession'
import { HttpError } from './api/http'
import { getPublicPoll, submitVote } from './api/publicPolls'
import type { CreatePollPayload, Poll, PollResults, SelectionType } from './types/poll'

interface ModalProps {
  children: ReactNode
  title: string
  onClose: () => void
  size?: 'small' | 'large'
}

function Modal({ children, title, onClose, size = 'small' }: ModalProps) {
  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4"
      onMouseDown={onClose}
      role="presentation"
    >
      <section
        aria-modal="true"
        className={`max-h-[90vh] w-full overflow-y-auto rounded-lg bg-white p-5 shadow-xl ${
          size === 'large' ? 'max-w-2xl' : 'max-w-md'
        }`}
        onMouseDown={(event) => event.stopPropagation()}
        role="dialog"
      >
        <header className="mb-5 flex items-start justify-between gap-4 border-b border-black pb-3">
          <h2 className="text-xl font-semibold">{title}</h2>
          <button
            aria-label="Закрыть"
            className="text-2xl leading-none text-neutral-500 hover:text-black"
            onClick={onClose}
            type="button"
          >
            ×
          </button>
        </header>
        {children}
      </section>
    </div>
  )
}

function toDateTimeLocal(date: Date): string {
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000)
  return localDate.toISOString().slice(0, 16)
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

interface CreatePollModalProps {
  onClose: () => void
  onCreated: (poll: Poll) => void
  onUnauthorized: () => void
}

function CreatePollModal({ onClose, onCreated, onUnauthorized }: CreatePollModalProps) {
  const now = new Date()
  const [question, setQuestion] = useState('')
  const [selectionType, setSelectionType] = useState<SelectionType>('single')
  const [minSelections, setMinSelections] = useState('1')
  const [maxSelections, setMaxSelections] = useState('1')
  const [startsAt, setStartsAt] = useState(toDateTimeLocal(now))
  const [endsAt, setEndsAt] = useState(toDateTimeLocal(new Date(now.getTime() + 60 * 60_000)))
  const [options, setOptions] = useState(['', ''])
  const [error, setError] = useState<string | null>(null)
  const [selectionError, setSelectionError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const changeSelectionType = (value: SelectionType) => {
    setSelectionType(value)
    setSelectionError(null)
    if (value === 'single') {
      setMinSelections('1')
      setMaxSelections('1')
    }
  }

  const changeOption = (index: number, value: string) => {
    setOptions((current) =>
      current.map((option, optionIndex) => (optionIndex === index ? value : option)),
    )
  }

  const removeOption = (index: number) => {
    setOptions((current) => current.filter((_, optionIndex) => optionIndex !== index))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setSelectionError(null)

    const normalizedOptions = options.map((option) => option.trim())
    const start = new Date(startsAt)
    const end = new Date(endsAt)
    const minimum = Number(minSelections)
    const maximum = Number(maxSelections)

    if (!question.trim()) {
      setError('Введите вопрос.')
      return
    }
    if (normalizedOptions.length < 2 || normalizedOptions.some((option) => !option)) {
      setError('Добавьте минимум два заполненных варианта ответа.')
      return
    }
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end <= start) {
      setError('Время окончания должно быть позже времени начала.')
      return
    }
    if (selectionType === 'multiple') {
      if (!Number.isInteger(minimum) || minimum < 1) {
        setSelectionError('Минимум должен быть не меньше 1.')
        return
      }
      if (!Number.isInteger(maximum) || maximum < minimum) {
        setSelectionError('Максимум не может быть меньше минимума.')
        return
      }
      if (maximum > normalizedOptions.length) {
        setSelectionError(`Максимум не может превышать число вариантов (${normalizedOptions.length}).`)
        return
      }
    }

    const payload: CreatePollPayload = {
      question: question.trim(),
      selection_type: selectionType,
      min_selections: selectionType === 'single' ? 1 : minimum,
      max_selections: selectionType === 'single' ? 1 : maximum,
      starts_at: start.toISOString(),
      ends_at: end.toISOString(),
      options: normalizedOptions,
    }

    setIsSubmitting(true)
    try {
      const poll = await createPoll(payload)
      onCreated(poll)
      onClose()
    } catch (requestError) {
      if (requestError instanceof HttpError && requestError.status === 401) {
        onUnauthorized()
        return
      }
      setError(requestError instanceof Error ? requestError.message : 'Не удалось создать опрос.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal onClose={onClose} size="large" title="Создать опрос">
      <form className="space-y-4" onSubmit={submit}>
        <label className="block">
          <span className="mb-1 block text-sm font-medium">Вопрос</span>
          <input
            autoFocus
            className="w-full rounded border border-neutral-400 px-3 py-2 outline-none focus:border-black"
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Введите вопрос"
            value={question}
          />
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium">Тип выбора</span>
          <select
            className="w-full rounded border border-neutral-400 bg-white px-3 py-2"
            onChange={(event) => changeSelectionType(event.target.value as SelectionType)}
            value={selectionType}
          >
            <option value="single">Один вариант</option>
            <option value="multiple">Несколько вариантов</option>
          </select>
        </label>

        {selectionType === 'multiple' && (
          <>
            <div className="grid grid-cols-2 gap-3">
              <label>
                <span className="mb-1 block text-sm font-medium">Минимум</span>
                <input
                  className="number-field w-full rounded border border-neutral-400 px-3 py-2"
                  min="1"
                  onChange={(event) => {
                    setMinSelections(event.target.value)
                    setSelectionError(null)
                  }}
                  type="number"
                  step="1"
                  value={minSelections}
                />
              </label>
              <label>
                <span className="mb-1 block text-sm font-medium">Максимум</span>
                <input
                  className="number-field w-full rounded border border-neutral-400 px-3 py-2"
                  min="1"
                  onChange={(event) => {
                    setMaxSelections(event.target.value)
                    setSelectionError(null)
                  }}
                  type="number"
                  step="1"
                  value={maxSelections}
                />
              </label>
            </div>
            {selectionError && <p className="mt-2 text-sm text-red-700">{selectionError}</p>}
          </>
        )}

        <div className="grid gap-3 sm:grid-cols-2">
          <label>
            <span className="mb-1 block text-sm font-medium">Начало</span>
            <input
              className="w-full rounded border border-neutral-400 px-3 py-2"
              onChange={(event) => setStartsAt(event.target.value)}
              type="datetime-local"
              value={startsAt}
            />
          </label>
          <label>
            <span className="mb-1 block text-sm font-medium">Окончание</span>
            <input
              className="w-full rounded border border-neutral-400 px-3 py-2"
              onChange={(event) => setEndsAt(event.target.value)}
              type="datetime-local"
              value={endsAt}
            />
          </label>
        </div>

        <fieldset>
          <legend className="mb-2 text-sm font-medium">Варианты ответа</legend>
          <div className="space-y-2">
            {options.map((option, index) => (
              <div className="flex gap-2" key={index}>
                <input
                  aria-label={`Вариант ${index + 1}`}
                  className="min-w-0 flex-1 rounded border border-neutral-400 px-3 py-2"
                  onChange={(event) => changeOption(index, event.target.value)}
                  placeholder={`Вариант ${index + 1}`}
                  value={option}
                />
                <button
                  className="rounded border border-neutral-300 px-3 disabled:cursor-not-allowed disabled:opacity-40"
                  disabled={options.length <= 2}
                  onClick={() => removeOption(index)}
                  type="button"
                >
                  Удалить
                </button>
              </div>
            ))}
          </div>
          <button
            className="mt-2 text-sm underline underline-offset-2"
            onClick={() => setOptions((current) => [...current, ''])}
            type="button"
          >
            + Добавить вариант
          </button>
        </fieldset>

        {error && <p className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</p>}

        <div className="flex justify-end gap-2 border-t border-neutral-200 pt-4">
          <button className="rounded border border-black px-4 py-2" onClick={onClose} type="button">
            Отмена
          </button>
          <button
            className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? 'Создание…' : 'Создать'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

interface ResultsModalProps {
  error: string | null
  isLoading: boolean
  onClose: () => void
  poll: Poll
  results: PollResults | null
}

function ResultsModal({ error, isLoading, onClose, poll, results }: ResultsModalProps) {
  return (
    <Modal onClose={onClose} title="Статистика опроса">
      <p className="mb-4 font-medium">{poll.question}</p>
      {isLoading && <p className="text-sm text-neutral-500">Загрузка статистики…</p>}
      {error && <p className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {results && (
        <div>
          <p className="mb-3 text-sm text-neutral-600">
            Участников: <strong className="text-black">{results.total_participants}</strong>
          </p>
          <ul className="divide-y divide-neutral-200 border-y border-neutral-200">
            {results.results.map((result) => (
              <li className="flex items-center justify-between gap-4 py-3" key={result.option_id}>
                <span>{result.text}</span>
                <span className="shrink-0 text-sm">
                  {result.votes} · {Number(result.participant_percentage).toFixed(1)}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Modal>
  )
}

interface PollVotePageProps {
  pollId: string
}

function PollVotePage({ pollId }: PollVotePageProps) {
  const [poll, setPoll] = useState<Poll | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedOptionIds, setSelectedOptionIds] = useState<string[]>([])
  const [selectionError, setSelectionError] = useState<string | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    let isCurrent = true

    const loadPoll = async () => {
      setIsLoading(true)
      setLoadError(null)
      try {
        const publicPoll = await getPublicPoll(pollId)
        if (isCurrent) setPoll(publicPoll)
      } catch (error) {
        if (isCurrent) {
          setLoadError(error instanceof Error ? error.message : 'Не удалось загрузить опрос.')
        }
      } finally {
        if (isCurrent) setIsLoading(false)
      }
    }

    void loadPoll()
    return () => {
      isCurrent = false
    }
  }, [pollId])

  const selectOption = (optionId: string) => {
    if (!poll) return

    setSelectionError(null)
    setSubmitError(null)
    if (poll.selection_type === 'single') {
      setSelectedOptionIds([optionId])
      return
    }

    setSelectedOptionIds((current) => {
      if (current.includes(optionId)) return current.filter((id) => id !== optionId)
      if (current.length >= poll.max_selections) {
        setSelectionError(`Можно выбрать не более ${poll.max_selections} вариантов.`)
        return current
      }
      return [...current, optionId]
    })
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!poll) return

    setSelectionError(null)
    setSubmitError(null)
    if (poll.selection_type === 'single' && selectedOptionIds.length !== 1) {
      setSelectionError('Выберите один вариант ответа.')
      return
    }
    if (
      poll.selection_type === 'multiple' &&
      (selectedOptionIds.length < poll.min_selections || selectedOptionIds.length > poll.max_selections)
    ) {
      setSelectionError(
        `Выберите от ${poll.min_selections} до ${poll.max_selections} вариантов ответа.`,
      )
      return
    }

    setIsSubmitting(true)
    try {
      await submitVote(poll.id, selectedOptionIds)
      setIsComplete(true)
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Не удалось учесть голос.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return <main className="grid min-h-screen place-items-center p-6 text-neutral-500">Загрузка опроса…</main>
  }

  if (loadError || !poll) {
    return (
      <main className="grid min-h-screen place-items-center bg-white p-6 text-center text-black">
        <section className="max-w-md border border-red-300 bg-red-50 p-6">
          <h1 className="text-xl font-semibold">Опрос недоступен</h1>
          <p className="mt-2 text-red-800">{loadError || 'Опрос не найден.'}</p>
        </section>
      </main>
    )
  }

  if (isComplete) {
    return (
      <main className="grid min-h-screen place-items-center bg-white p-6 text-center text-black">
        <section className="max-w-md border-2 border-black p-8">
          <p className="text-4xl" aria-hidden="true">✓</p>
          <h1 className="mt-4 text-2xl font-bold">Спасибо за голос!</h1>
          <p className="mt-2 text-neutral-600">Ваш ответ успешно учтён.</p>
        </section>
      </main>
    )
  }

  const isMultiple = poll.selection_type === 'multiple'
  const selectionHint = isMultiple
    ? `Выберите от ${poll.min_selections} до ${poll.max_selections} вариантов.`
    : 'Выберите один вариант.'

  return (
    <main className="grid min-h-screen place-items-center bg-white p-4 text-black sm:p-8">
      <section className="w-full max-w-xl border-2 border-black p-6 sm:p-8">
        <p className="text-sm uppercase tracking-widest text-neutral-500">Голосование</p>
        <h1 className="mt-2 text-2xl font-bold sm:text-3xl">{poll.question}</h1>
        <p className="mt-3 text-sm text-neutral-600">{selectionHint}</p>

        <form className="mt-6 space-y-3" onSubmit={submit}>
          <fieldset>
            <legend className="sr-only">Варианты ответа</legend>
            <div className="space-y-2">
              {poll.options.map((option) => {
                const isSelected = selectedOptionIds.includes(option.id)

                return (
                  <label
                    className={`flex cursor-pointer items-center gap-3 border p-4 transition-colors ${
                      isSelected ? 'border-black bg-neutral-100' : 'border-neutral-300 hover:border-black'
                    }`}
                    key={option.id}
                  >
                    <input
                      checked={isSelected}
                      name="vote-option"
                      onChange={() => selectOption(option.id)}
                      type={isMultiple ? 'checkbox' : 'radio'}
                    />
                    <span>{option.text}</span>
                  </label>
                )
              })}
            </div>
          </fieldset>

          {selectionError && <p className="text-sm text-red-700">{selectionError}</p>}
          {submitError && <p className="border border-red-300 bg-red-50 p-3 text-sm text-red-700">{submitError}</p>}

          <button
            className="mt-3 w-full rounded bg-black px-5 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? 'Отправка…' : 'Отправить голос'}
          </button>
        </form>
      </section>
    </main>
  )
}

interface AdminLoginPageProps {
  onAuthenticated: () => void
}

function AdminLoginPage({ onAuthenticated }: AdminLoginPageProps) {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await loginAdmin(login, password)
      onAuthenticated()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Не удалось выполнить вход.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-white p-6 text-black">
      <section className="w-full max-w-md border-2 border-black p-6 sm:p-8">
        <p className="text-sm uppercase tracking-widest text-neutral-500">Voting System</p>
        <h1 className="mt-2 text-3xl font-bold">Вход администратора</h1>
        <p className="mt-2 text-sm text-neutral-600">Войдите, чтобы управлять опросами и видеть результаты.</p>
        <form className="mt-6 space-y-4" onSubmit={(event) => void submit(event)}>
          <label className="block" htmlFor="admin-login">
            <span className="mb-1 block text-sm font-medium">Логин</span>
            <input
              autoComplete="username"
              autoFocus
              className="w-full rounded border border-neutral-400 px-3 py-2 outline-none focus:border-black"
              id="admin-login"
              onChange={(event) => setLogin(event.target.value)}
              required
              value={login}
            />
          </label>
          <label className="block" htmlFor="admin-password">
            <span className="mb-1 block text-sm font-medium">Пароль</span>
            <input
              autoComplete="current-password"
              className="w-full rounded border border-neutral-400 px-3 py-2 outline-none focus:border-black"
              id="admin-password"
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </label>
          {error && <p className="border border-red-300 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <button
            className="w-full rounded bg-black px-5 py-3 font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? 'Вход…' : 'Войти'}
          </button>
        </form>
      </section>
    </main>
  )
}

interface AdminPollsPageProps {
  onUnauthorized: () => void
}

function AdminPollsPage({ onUnauthorized }: AdminPollsPageProps) {
  const [polls, setPolls] = useState<Poll[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [selectedPoll, setSelectedPoll] = useState<Poll | null>(null)
  const [results, setResults] = useState<PollResults | null>(null)
  const [resultsError, setResultsError] = useState<string | null>(null)
  const [areResultsLoading, setAreResultsLoading] = useState(false)
  const [currentTime, setCurrentTime] = useState(Date.now())
  const [copiedPollId, setCopiedPollId] = useState<string | null>(null)
  const resultsRequestId = useRef(0)

  const loadPolls = async () => {
    setIsLoading(true)
    setLoadError(null)
    try {
      setPolls(await getPolls())
    } catch (error) {
      if (error instanceof HttpError && error.status === 401) {
        onUnauthorized()
        return
      }
      setLoadError(error instanceof Error ? error.message : 'Не удалось загрузить опросы.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadPolls()
    const timer = window.setInterval(() => setCurrentTime(Date.now()), 30_000)
    return () => window.clearInterval(timer)
  }, [])

  const openResults = async (poll: Poll) => {
    const requestId = ++resultsRequestId.current
    setSelectedPoll(poll)
    setResults(null)
    setResultsError(null)
    setAreResultsLoading(true)

    try {
      const pollResults = await getPollResults(poll.id)
      if (resultsRequestId.current === requestId) setResults(pollResults)
    } catch (error) {
      if (error instanceof HttpError && error.status === 401) {
        onUnauthorized()
        return
      }
      if (resultsRequestId.current === requestId) {
        setResultsError(error instanceof Error ? error.message : 'Не удалось загрузить статистику.')
      }
    } finally {
      if (resultsRequestId.current === requestId) setAreResultsLoading(false)
    }
  }

  const closeResults = () => {
    resultsRequestId.current += 1
    setSelectedPoll(null)
  }

  const copyPollId = async (pollId: string) => {
    try {
      await navigator.clipboard.writeText(pollId)
      setCopiedPollId(pollId)
      window.setTimeout(() => setCopiedPollId(null), 2_000)
    } catch {
      setCopiedPollId(null)
    }
  }

  return (
    <main className="min-h-screen bg-white px-4 py-8 text-black sm:px-8">
      <div className="mx-auto max-w-5xl">
        <header className="mb-8 flex flex-col gap-4 border-b-2 border-black pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-widest text-neutral-500">Панель администратора</p>
            <h1 className="mt-1 text-3xl font-bold">Опросы</h1>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              className="rounded bg-black px-5 py-2.5 font-medium text-white hover:bg-neutral-800"
              onClick={() => setIsCreateOpen(true)}
              type="button"
            >
              Создать опрос
            </button>
            <button
              className="rounded border border-black px-5 py-2.5 font-medium hover:bg-neutral-100"
              onClick={onUnauthorized}
              type="button"
            >
              Выйти
            </button>
          </div>
        </header>

        {isLoading && <p className="py-10 text-center text-neutral-500">Загрузка опросов…</p>}
        {loadError && (
          <div className="flex items-center justify-between gap-4 border border-red-300 bg-red-50 p-4 text-red-800">
            <span>{loadError}</span>
            <button className="shrink-0 underline" onClick={() => void loadPolls()} type="button">
              Повторить
            </button>
          </div>
        )}
        {!isLoading && !loadError && polls.length === 0 && (
          <p className="border border-dashed border-neutral-400 px-4 py-12 text-center text-neutral-500">
            Опросов пока нет.
          </p>
        )}

        {!loadError && polls.length > 0 && (
          <ul className="divide-y divide-neutral-300 border-y border-neutral-300">
            {polls.map((poll) => {
              const isActive = new Date(poll.ends_at).getTime() > currentTime

              return (
                <li key={poll.id}>
                  <div className="grid gap-3 px-2 py-5 sm:grid-cols-[1fr_auto] sm:items-center">
                    <button
                      className="min-w-0 text-left hover:underline hover:underline-offset-4"
                      onClick={() => void openResults(poll)}
                      type="button"
                    >
                      <span className="block text-lg font-medium">{poll.question}</span>
                      <span className="mt-1 block text-sm text-neutral-500">
                        {formatDate(poll.starts_at)} — {formatDate(poll.ends_at)}
                      </span>
                      <span className="mt-2 block text-sm text-neutral-700">
                        Варианты: {poll.options.map((option) => option.text).join(' · ')}
                      </span>
                    </button>
                    <div className="flex flex-col items-start gap-2 sm:items-end">
                      <span
                        className={`inline-flex w-fit items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${
                          isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}
                      >
                        <span className={`h-2 w-2 rounded-full ${isActive ? 'bg-green-600' : 'bg-red-600'}`} />
                        {isActive ? 'Активный' : 'Закончен'}
                      </span>
                      <div className="flex max-w-full items-center gap-2 text-xs">
                        <code className="break-all bg-neutral-100 px-2 py-1" title={poll.id}>
                          {poll.id}
                        </code>
                        <button
                          aria-label="Скопировать UUID опроса"
                          className="shrink-0 rounded border border-neutral-400 px-2 py-1 hover:border-black"
                          onClick={() => void copyPollId(poll.id)}
                          type="button"
                        >
                          {copiedPollId === poll.id ? 'Скопировано' : 'Копировать'}
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              )
            })}
          </ul>
        )}
      </div>

      {isCreateOpen && (
        <CreatePollModal
          onClose={() => setIsCreateOpen(false)}
          onCreated={(poll) => setPolls((current) => [poll, ...current])}
          onUnauthorized={onUnauthorized}
        />
      )}
      {selectedPoll && (
        <ResultsModal
          error={resultsError}
          isLoading={areResultsLoading}
          onClose={closeResults}
          poll={selectedPoll}
          results={results}
        />
      )}
    </main>
  )
}

export function App() {
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(hasAdminToken)
  const path = window.location.pathname.replace(/\/+$/, '') || '/'
  const voteRoute = path.match(/^\/poll\/([^/]+)\/vote$/)

  if (path === '/admin/polls') {
    const logout = () => {
      clearAdminToken()
      setIsAdminAuthenticated(false)
    }
    return isAdminAuthenticated ? (
      <AdminPollsPage onUnauthorized={logout} />
    ) : (
      <AdminLoginPage onAuthenticated={() => setIsAdminAuthenticated(true)} />
    )
  }

  if (voteRoute) {
    return <PollVotePage pollId={voteRoute[1]} />
  }

  if (path === '/') {
    return (
      <main className="grid min-h-screen place-items-center bg-white p-6 text-black">
        <section className="w-full max-w-xl border-2 border-black p-6 sm:p-8">
          <p className="text-sm uppercase tracking-widest text-neutral-500">Voting System</p>
          <h1 className="mt-2 text-3xl font-bold">Добро пожаловать</h1>
          <div className="mt-8 space-y-6">
            <div>
              <h2 className="text-lg font-semibold">Для администратора</h2>
              <p className="mt-1 text-neutral-600">Создавайте опросы и просматривайте их статистику.</p>
              <a
                className="mt-3 inline-block rounded bg-black px-4 py-2 text-white hover:bg-neutral-800"
                href="/admin/polls"
              >
                Перейти к списку опросов
              </a>
            </div>
            <div className="border-t border-neutral-300 pt-6">
              <h2 className="text-lg font-semibold">Для участника</h2>
              <p className="mt-1 text-neutral-600">
                Чтобы проголосовать, откройте полученную ссылку в формате:
              </p>
              <code className="mt-3 block overflow-x-auto bg-neutral-100 px-3 py-2 text-sm">
                /poll/&lt;uuid&gt;/vote
              </code>
            </div>
          </div>
        </section>
      </main>
    )
  }

  return (
    <main className="grid min-h-screen place-items-center bg-white p-6 text-center text-black">
      <div>
        <p className="text-6xl font-bold">404</p>
        <h1 className="mt-3 text-xl font-semibold">Страница не найдена</h1>
      </div>
    </main>
  )
}
