const adminTokenKey = 'admin_access_token'

export function getAdminToken(): string | null {
  return sessionStorage.getItem(adminTokenKey)
}

export function hasAdminToken(): boolean {
  return getAdminToken() !== null
}

export function clearAdminToken(): void {
  sessionStorage.removeItem(adminTokenKey)
}

export function saveAdminToken(token: string): void {
  sessionStorage.setItem(adminTokenKey, token)
}
