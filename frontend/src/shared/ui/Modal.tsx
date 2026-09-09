import { useEffect, type ReactNode } from 'react'

interface ModalProps {
  children: ReactNode
  title: string
  onClose: () => void
  size?: 'small' | 'large'
}

export function Modal({ children, title, onClose, size = 'small' }: ModalProps) {
  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [onClose])

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4" onMouseDown={onClose} role="presentation">
      <section aria-modal="true" className={`max-h-[90vh] w-full overflow-y-auto rounded-lg bg-white p-5 shadow-xl ${size === 'large' ? 'max-w-2xl' : 'max-w-md'}`} onMouseDown={(event) => event.stopPropagation()} role="dialog">
        <header className="mb-5 flex items-start justify-between gap-4 border-b border-black pb-3">
          <h2 className="text-xl font-semibold">{title}</h2>
          <button aria-label="Закрыть" className="text-2xl leading-none text-neutral-500 hover:text-black" onClick={onClose} type="button">×</button>
        </header>
        {children}
      </section>
    </div>
  )
}
