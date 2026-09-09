import { request } from '../../../shared/api/http'
import { saveAdminToken } from '../model/session'

interface AdminTokenResponse {
  access_token: string
  expires_in: number
  token_type: 'bearer'
}

export async function loginAdmin(login: string, password: string): Promise<void> {
  const token = await request<AdminTokenResponse>('/auth/admin/login', {
    method: 'POST',
    body: JSON.stringify({ login, password }),
  })
  saveAdminToken(token.access_token)
}
