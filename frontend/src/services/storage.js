const USER_KEY = 'user'

export const getStoredUser = () => {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (err) {
    console.warn('Failed to parse stored user:', err)
    return null
  }
}

export const setStoredUser = (user) => {
  try {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    } else {
      localStorage.removeItem(USER_KEY)
    }
  } catch (err) {
    console.warn('Failed to persist user:', err)
  }
}

export const clearStoredUser = () => {
  try {
    localStorage.removeItem(USER_KEY)
  } catch (err) {
    console.warn('Failed to clear stored user:', err)
  }
}
