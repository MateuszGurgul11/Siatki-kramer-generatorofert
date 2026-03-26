import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import imgLine from '../assets/drawings/drawing-lines.png'
import imgL from '../assets/drawings/drawing-typeL.png'
import imgU from '../assets/drawings/drawing-typeU.png'
import imgClosed from '../assets/drawings/drawing-closed.png'

const SHAPES = [
  {
    id: 'line',
    label: 'Linia prosta',
    description: '1 ściana',
    braces: '2+ zastrzały',
    image: imgLine,
  },
  {
    id: 'L',
    label: 'Kształt L',
    description: '2 ściany',
    braces: '4+ zastrzały',
    image: imgL,
  },
  {
    id: 'U',
    label: 'Kształt U',
    description: '3 ściany',
    braces: '6+ zastrzałów',
    image: imgU,
  },
  {
    id: 'closed',
    label: 'Zamknięty',
    description: '4 ściany',
    braces: '8+ zastrzałów',
    image: imgClosed,
  },
]

function ShapeImage({ src, alt, className, priority = false }) {
  const [failed, setFailed] = useState(false)
  if (failed) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 text-gray-400 text-xs text-center p-2 ${className}`}>
        Brak grafiki
      </div>
    )
  }
  return (
    <img
      src={src}
      alt={alt}
      className={className}
      loading={priority ? 'eager' : 'lazy'}
      decoding="async"
      draggable={false}
      fetchPriority={priority ? 'high' : 'auto'}
      onError={() => setFailed(true)}
    />
  )
}

function ZoomInIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4.35-4.35" />
      <path d="M11 8v6M8 11h6" />
    </svg>
  )
}

function CloseIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden>
      <path d="M18 6L6 18M6 6l12 12" />
    </svg>
  )
}

/** Modal: X przyklejony do rogu ekranu (fixed + safe-area), treść przewijalna — działa na telefonie w iframe. */
function ShapePreviewModal({ shape, onClose }) {
  useEffect(() => {
    const prev = document.body.style.overflow
    const prevTouchAction = document.body.style.touchAction
    document.body.style.overflow = 'hidden'
    document.body.style.touchAction = 'none'
    const onKey = e => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => {
      document.body.style.overflow = prev
      document.body.style.touchAction = prevTouchAction
      window.removeEventListener('keydown', onKey)
    }
  }, [onClose])

  if (typeof document === 'undefined') return null

  return createPortal(
    <div
      className="fixed inset-0 z-[9999] flex min-h-[100dvh] flex-col bg-gray-900/75"
      style={{ WebkitTapHighlightColor: 'transparent' }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="shape-preview-title"
    >
      {/* Zamknięcie tłem — poniżej przycisku X (niższy z-index) */}
      <button
        type="button"
        className="absolute inset-0 z-0 cursor-default"
        aria-label="Zamknij podgląd"
        onClick={onClose}
      />

      {/* X zawsze widoczny w rogu — fixed, nie przewija się z treścią */}
      <button
        type="button"
        onClick={onClose}
        className="fixed z-[10001] flex h-12 w-12 items-center justify-center rounded-full border border-white/30 bg-white text-gray-800 shadow-lg transition active:scale-95 sm:h-11 sm:w-11"
        style={{
          top: 'max(0.75rem, env(safe-area-inset-top, 0px))',
          right: 'max(0.75rem, env(safe-area-inset-right, 0px))',
        }}
        aria-label="Zamknij"
      >
        <CloseIcon className="h-6 w-6 sm:h-5 sm:w-5" />
      </button>

      {/* Przewijalna treść — pod spodem, z paddingiem od „góry” pod X */}
      <div className="relative z-[10000] mx-auto flex w-full max-w-4xl flex-1 flex-col overflow-y-auto overscroll-contain px-4 pb-8 pt-[4.25rem] sm:px-6 sm:pb-10 sm:pt-16">
        <div className="mb-4 shrink-0 rounded-2xl bg-white/95 px-4 py-3 shadow-sm ring-1 ring-black/5 sm:px-5">
          <h3 id="shape-preview-title" className="text-base font-semibold text-gray-900 sm:text-lg">
            {shape.label}
          </h3>
          <p className="mt-0.5 text-sm text-gray-500">
            {shape.description} · {shape.braces}
          </p>
        </div>
        <div className="flex min-h-0 flex-1 items-start justify-center rounded-2xl bg-white/10 p-3 sm:p-4">
          <ShapeImage
            src={shape.image}
            alt={`Powiększony widok: ${shape.label}`}
            className="max-h-[min(72vh,800px)] w-full object-contain"
            priority
          />
        </div>
      </div>
    </div>,
    document.body,
  )
}

function ShapeOptionCard({ shape: s, selected, onShapeChange, onOpenPreview }) {
  const select = () => onShapeChange(s.id)

  const openPreview = e => {
    e.preventDefault()
    e.stopPropagation()
    onOpenPreview(s)
  }

  return (
    <div
      className={`
        w-full border-2 rounded-xl p-4 text-left outline-none transition-all hover:shadow-md
        focus-visible:ring-2 focus-visible:ring-kramer-green focus-visible:ring-offset-2
        ${selected
          ? 'border-kramer-green bg-kramer-green-light shadow-md'
          : 'border-gray-200 bg-white hover:border-gray-300'
        }
      `}
      tabIndex={0}
      role="group"
      aria-label={`Karta kształtu: ${s.label}`}
      onKeyDown={e => {
        if (e.key === 'Enter' || e.key === ' ') {
          if (e.target.closest('[data-loupe]')) return
          e.preventDefault()
          select()
        }
      }}
    >
      <div className="relative mb-3 h-36 overflow-hidden rounded-lg bg-gray-50 sm:h-40">
        <ShapeImage
          src={s.image}
          alt=""
          className="relative z-0 h-full w-full object-contain pointer-events-none"
        />
        <div
          className="pointer-events-none absolute inset-0 z-[1] bg-gradient-to-t from-black/5 to-transparent rounded-lg"
          aria-hidden
        />
        {/* Warstwa wyboru kształtu — pod lupą */}
        <button
          type="button"
          className="absolute inset-0 z-[2] cursor-pointer rounded-lg border-0 bg-transparent p-0 text-left"
          aria-label={`Wybierz kształt: ${s.label}`}
          onClick={select}
        />
        {/* Lupa zawsze nad warstwą wyboru — duży cel dotykowy (min. 44px) */}
        <button
          type="button"
          data-loupe
          className="absolute right-1 top-1 z-[3] flex min-h-[44px] min-w-[44px] items-center justify-center rounded-lg border border-white/90 bg-white text-kramer-green shadow-md touch-manipulation [-webkit-tap-highlight-color:transparent] sm:right-2 sm:top-2 sm:min-h-0 sm:min-w-0 sm:h-9 sm:w-9"
          aria-label={`Powiększ podgląd: ${s.label}`}
          onClick={openPreview}
          onPointerDown={e => e.stopPropagation()}
        >
          <ZoomInIcon className="h-6 w-6 sm:h-5 sm:w-5" />
        </button>
      </div>
      <button
        type="button"
        className="w-full border-0 bg-transparent p-0 text-left"
        onClick={select}
      >
        <span className="block font-semibold text-gray-800">{s.label}</span>
        <span className="mt-0.5 block text-sm text-gray-500">
          {s.description} · {s.braces}
        </span>
      </button>
    </div>
  )
}

export default function Step1Shape({ shape, onShapeChange, onNext }) {
  const [previewShape, setPreviewShape] = useState(null)

  return (
    <div className="card overflow-visible">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Krok 1: Kształt piłkochwytu</h2>
      <p className="text-gray-500 text-sm mb-6">
        Wybierz układ ścian siatkowych (widok z góry). Ikona{' '}
        <span className="inline-flex h-5 w-5 align-middle items-center justify-center rounded border border-gray-200 bg-white text-kramer-green mx-0.5">
          <ZoomInIcon className="h-3 w-3" />
        </span>{' '}
        w rogu grafiki otwiera większy podgląd (na telefonie stuknij ikonę).
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-6 sm:pt-8">
        {SHAPES.map(s => (
          <ShapeOptionCard
            key={s.id}
            shape={s}
            selected={shape === s.id}
            onShapeChange={onShapeChange}
            onOpenPreview={setPreviewShape}
          />
        ))}
      </div>

      {previewShape && <ShapePreviewModal shape={previewShape} onClose={() => setPreviewShape(null)} />}

      <p className="text-xs text-gray-400 mt-4">
        * Liczba zastrzałów bazowa; dodatkowe +2 szt. za każde przekroczone 30 m długości ściany.
      </p>

      <div className="mt-6 flex justify-end">
        <button type="button" className="btn-primary" onClick={onNext}>
          Dalej →
        </button>
      </div>
    </div>
  )
}
