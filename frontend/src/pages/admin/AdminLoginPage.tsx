import { AdminLoginForm } from '../../features/admin-auth/ui/AdminLoginForm'

interface AdminLoginPageProps { onAuthenticated: () => void }
export function AdminLoginPage({ onAuthenticated }: AdminLoginPageProps) {
  return <main className="grid min-h-screen place-items-center bg-white p-6 text-black"><section className="w-full max-w-md border-2 border-black p-6 sm:p-8"><p className="text-sm uppercase tracking-widest text-neutral-500">Voting System</p><h1 className="mt-2 text-3xl font-bold">Вход администратора</h1><p className="mt-2 text-sm text-neutral-600">Войдите, чтобы управлять опросами и видеть результаты.</p><AdminLoginForm onAuthenticated={onAuthenticated} /></section></main>
}
