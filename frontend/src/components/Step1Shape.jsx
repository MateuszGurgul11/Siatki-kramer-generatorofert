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

/** Pełnoekranowy, czytelny podgląd po kliknięciu ikony powiększenia */
function ShapePreviewModal({ shape, onClose }) {
  useEffect(() => {
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const onKey = e => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => {
      document.body.style.overflow = prev
      window.removeEventListener('keydown', onKey)
    }
  }, [onClose])

  if (typeof document === 'undefined') return null

  return createPortal(
    <div
      className="fixed inset-0 z-[300] flex items-center justify-center p-3 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="shape-preview-title"
    >
      <button
        type="button"
        className="absolute inset-0 bg-gray-900/55 backdrop-blur-[2px] transition-opacity"
        aria-label="Zamknij podgląd"
        onClick={onClose}
      />
      <div className="relative z-10 flex w-full max-w-4xl max-h-[min(92vh,900px)] flex-col overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-black/5">
        <div className="flex items-start justify-between gap-3 border-b border-gray-100 px-4 py-3 sm:px-5 sm:py-4">
          <div className="min-w-0 pr-2">
            <h3 id="shape-preview-title" className="text-base font-semibold text-gray-900 sm:text-lg">
              {shape.label}
            </h3>
            <p className="mt-0.5 text-sm text-gray-500">
              {shape.description} · {shape.braces}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-800"
            aria-label="Zamknij"
          >
            <CloseIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-auto bg-gradient-to-b from-gray-50 to-gray-100/80 p-4 sm:p-6">
          <div className="mx-auto flex max-h-[min(70vh,720px)] items-center justify-center">
            <ShapeImage
              src={shape.image}
              alt={`Powiększony widok: ${shape.label}`}
              className="max-h-full w-full max-w-full object-contain"
              priority
            />
          </div>
        </div>
      </div>
    </div>,
    document.body,
  )
}

function ShapeOptionCard({ shape: s, selected, onShapeChange, onOpenPreview }) {
  const select = () => onShapeChange(s.id)

  return (
    <div
      role="button"
      tabIndex={0}
      aria-pressed={selected}
      aria-label={`Wybierz kształt: ${s.label}`}
      onClick={select}
      onKeyDown={e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          select()
        }
      }}
      className={`
        w-full border-2 rounded-xl p-4 text-left transition-all hover:shadow-md cursor-pointer outline-none
        focus-visible:ring-2 focus-visible:ring-kramer-green focus-visible:ring-offset-2
        ${selected
          ? 'border-kramer-green bg-kramer-green-light shadow-md'
          : 'border-gray-200 bg-white hover:border-gray-300'
        }
      `}
    >
      <div className="relative mb-3 h-36 overflow-hidden rounded-lg bg-gray-50 sm:h-40">
        <ShapeImage
          src={s.image}
          alt=""
          className="h-full w-full object-contain pointer-events-none"
        />
        <div
          className="absolute inset-0 bg-gradient-to-t from-black/5 to-transparent pointer-events-none rounded-lg"
          aria-hidden
        />
        <button
          type="button"
          className="absolute right-2 top-2 z-10 flex h-9 w-9 items-center justify-center rounded-lg border border-white/80 bg-white/95 text-kramer-green shadow-md transition hover:bg-kramer-green hover:text-white hover:border-kramer-green focus:outline-none focus:ring-2 focus:ring-kramer-green focus:ring-offset-2"
          aria-label={`Powiększ podgląd: ${s.label}`}
          onClick={e => {
            e.stopPropagation()
            onOpenPreview(s)
          }}
        >
          <ZoomInIcon className="h-5 w-5" />
        </button>
      </div>
      <div className="font-semibold text-gray-800">{s.label}</div>
      <div className="text-sm text-gray-500">
        {s.description} · {s.braces}
      </div>
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
        w rogu grafiki otwiera większy podgląd.
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
