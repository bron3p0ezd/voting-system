import { useState, type FormEvent } from 'react'
import { loginAdmin } from '../api/loginAdmin'

interface AdminLoginFormProps { onAuthenticated: () => void }

export function AdminLoginForm({ onAuthenticated }: AdminLoginFormProps) {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(null); setIsSubmitting(true)
    try { await loginAdmin(login, password); onAuthenticated() }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'Не удалось выполнить вход.') }
    finally { setIsSubmitting(false) }
  }
  return <form className="mt-6 space-y-4" onSubmit={(event) => void submit(event)}>
    <label className="block" htmlFor="admin-login"><span className="mb-1 block text-sm font-medium">Логин</span><input autoComplete="username" autoFocus className="w-full rounded border border-neutral-400 px-3 py-2 outline-none focus:border-black" id="admin-login" onChange={(event) => setLogin(event.target.value)} required value={login} /></label>
    <label className="block" htmlFor="admin-password"><span className="mb-1 block text-sm font-medium">Пароль</span><input autoComplete="current-password" className="w-full rounded border border-neutral-400 px-3 py-2 outline-none focus:border-black" id="admin-password" onChange={(event) => setPassword(event.target.value)} required type="password" value={password} /></label>
    {error && <p className="border border-red-300 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
    <button className="w-full rounded bg-black px-5 py-3 font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-50" disabled={isSubmitting} type="submit">{isSubmitting ? 'Вход…' : 'Войти'}</button>
  </form>
}
