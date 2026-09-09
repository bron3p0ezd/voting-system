import { useState } from 'react'
import { clearAdminToken, hasAdminToken } from '../features/admin-auth/model/session'
import { AdminLoginPage } from '../pages/admin/AdminLoginPage'
import { AdminPollsPage } from '../pages/admin/AdminPollsPage'
import { HomePage } from '../pages/home/HomePage'
import { NotFoundPage } from '../pages/not-found/NotFoundPage'
import { PollVotePage } from '../pages/vote/PollVotePage'

export function App() {
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(hasAdminToken)
  const path = window.location.pathname.replace(/\/+$/, '') || '/'
  const voteRoute = path.match(/^\/poll\/([^/]+)\/vote$/)
  if (path === '/admin/polls') {
    const logout = () => { clearAdminToken(); setIsAdminAuthenticated(false) }
    return isAdminAuthenticated ? <AdminPollsPage onUnauthorized={logout} /> : <AdminLoginPage onAuthenticated={() => setIsAdminAuthenticated(true)} />
  }
  if (voteRoute) return <PollVotePage pollId={voteRoute[1]} />
  if (path === '/') return <HomePage />
  return <NotFoundPage />
}
