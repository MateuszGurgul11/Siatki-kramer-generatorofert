import { useState, useRef, useLayoutEffect, useCallback, useEffect } from 'react'
import { createPortal } from 'react-dom'
// Własne wizualizacje: podmień pliki w src/assets/shapes/ (line.png, L.png, U.png); kształt zamknięty → grafika-zamknieta.png
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

function ShapeImage({ src, alt, className }) {
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
      onError={() => setFailed(true)}
    />
  )
}

const POPUP_MARGIN = 10
const CURSOR_OFFSET = 14
/** Maks. szerokość podglądu (px); ~32rem */
const POPUP_MAX_W = 512

function clampNearCursor(clientX, clientY, popupW, popupH, vw, vh, margin) {
  let left = clientX + CURSOR_OFFSET
  let top = clientY + CURSOR_OFFSET
  if (left + popupW > vw - margin) left = clientX - popupW - CURSOR_OFFSET
  if (left < margin) left = margin
  if (left + popupW > vw - margin) left = vw - popupW - margin
  if (top + popupH > vh - margin) top = clientY - popupH - CURSOR_OFFSET
  if (top < margin) top = margin
  if (top + popupH > vh - margin) top = vh - popupH - margin
  return { left, top }
}

/** Portal + position:fixed — przy hover podąża za kursorem; na dotykach kotwica przy karcie. */
function ShapeVisualPopup({
  shape,
  open,
  anchorRef,
  followCursor,
  pointer,
  onPopupMouseEnter,
  onPopupMouseLeave,
}) {
  const popupRef = useRef(null)
  const [box, setBox] = useState({ top: 0, left: 0, width: POPUP_MAX_W, visible: false })

  const updatePosition = useCallback(() => {
    const anchor = anchorRef?.current
    const el = popupRef.current
    if (!open || !el) return

    const vw = window.innerWidth
    const vh = window.innerHeight
    const margin = POPUP_MARGIN

    const popupW = Math.min(POPUP_MAX_W, vw - 2 * margin)
    el.style.width = `${popupW}px`

    let popupH = el.getBoundingClientRect().height
    if (popupH < 40) popupH = 320

    if (followCursor && pointer) {
      const { left, top } = clampNearCursor(pointer.x, pointer.y, popupW, popupH, vw, vh, margin)
      setBox({ top, left, width: popupW, visible: true })
      return
    }

    if (!anchor) return

    const anchorRect = anchor.getBoundingClientRect()

    let left = anchorRect.left + anchorRect.width / 2 - popupW / 2
    left = Math.max(margin, Math.min(left, vw - popupW - margin))

    let top = anchorRect.top - popupH - margin
    if (top < margin) {
      top = anchorRect.bottom + margin
    }
    if (top + popupH > vh - margin) {
      top = Math.max(margin, vh - popupH - margin)
    }
    if (top < margin) {
      top = margin
    }

    setBox({ top, left, width: popupW, visible: true })
  }, [open, anchorRef, shape, followCursor, pointer])

  useLayoutEffect(() => {
    if (!open) {
      setBox(b => ({ ...b, visible: false }))
      return
    }
    updatePosition()
    const el = popupRef.current
    const ro = el ? new ResizeObserver(() => updatePosition()) : null
    if (el && ro) ro.observe(el)
    window.addEventListener('resize', updatePosition)
    window.addEventListener('scroll', updatePosition, true)
    return () => {
      ro?.disconnect()
      window.removeEventListener('resize', updatePosition)
      window.removeEventListener('scroll', updatePosition, true)
    }
  }, [open, updatePosition])

  if (!open || typeof document === 'undefined') return null

  const node = (
    <div
      ref={popupRef}
      role="dialog"
      aria-label={`Powiększenie: ${shape.label}`}
      className="fixed z-[200] bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden flex flex-col max-h-[min(85vh,calc(100vh-2rem))]"
      style={{
        top: box.visible ? box.top : -9999,
        left: box.visible ? box.left : 0,
        width: box.width,
        opacity: box.visible ? 1 : 0,
        pointerEvents: box.visible ? 'auto' : 'none',
        transition: 'opacity 80ms ease-out',
      }}
      onMouseEnter={onPopupMouseEnter}
      onMouseLeave={onPopupMouseLeave}
    >
      <div className="bg-gray-100 w-full h-72 sm:h-96 min-h-[14rem] flex items-center justify-center relative overflow-hidden shrink-0">
        <ShapeImage
          src={shape.image}
          alt={`Wizualizacja: ${shape.label}`}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="px-3 py-2.5 border-t border-gray-100 shrink-0">
        <div className="font-semibold text-gray-800 text-sm">{shape.label}</div>
        <div className="text-xs text-gray-500">
          {shape.description} · {shape.braces}
        </div>
      </div>
    </div>
  )

  return createPortal(node, document.body)
}

function ShapeOptionCard({ shape: s, selected, onShapeChange, hoveredId, setHoveredId, mobilePreviewId, setMobilePreviewId }) {
  const anchorRef = useRef(null)
  const leaveTimerRef = useRef(null)
  const moveRafRef = useRef(null)
  const pendingPointerRef = useRef(null)
  const [pointer, setPointer] = useState(null)

  const showPreview = hoveredId === s.id || mobilePreviewId === s.id

  const canHover =
    typeof window !== 'undefined' && window.matchMedia('(hover: hover)').matches
  const followCursor =
    canHover && hoveredId === s.id && mobilePreviewId !== s.id

  const clearLeaveTimer = () => {
    if (leaveTimerRef.current) {
      window.clearTimeout(leaveTimerRef.current)
      leaveTimerRef.current = null
    }
  }

  const scheduleHideHover = () => {
    clearLeaveTimer()
    leaveTimerRef.current = window.setTimeout(() => setHoveredId(null), 180)
  }

  const queuePointer = e => {
    pendingPointerRef.current = { x: e.clientX, y: e.clientY }
    if (moveRafRef.current) return
    moveRafRef.current = requestAnimationFrame(() => {
      moveRafRef.current = null
      const p = pendingPointerRef.current
      if (p) setPointer(p)
    })
  }

  useEffect(() => () => clearLeaveTimer(), [])

  return (
    <div ref={anchorRef} className="relative z-10">
      <ShapeVisualPopup
        shape={s}
        open={showPreview}
        anchorRef={anchorRef}
        followCursor={followCursor}
        pointer={followCursor ? pointer : null}
        onPopupMouseEnter={clearLeaveTimer}
        onPopupMouseLeave={scheduleHideHover}
      />
      <button
        type="button"
        onClick={() => {
          onShapeChange(s.id)
          if (typeof window !== 'undefined' && window.matchMedia('(hover: none)').matches) {
            setMobilePreviewId(prev => (prev === s.id ? null : s.id))
          }
        }}
        onMouseEnter={e => {
          clearLeaveTimer()
          if (typeof window !== 'undefined' && window.matchMedia('(hover: hover)').matches) {
            setHoveredId(s.id)
            setPointer({ x: e.clientX, y: e.clientY })
          }
        }}
        onMouseMove={e => {
          if (typeof window !== 'undefined' && window.matchMedia('(hover: hover)').matches) {
            queuePointer(e)
          }
        }}
        onMouseLeave={() => {
          if (moveRafRef.current) {
            cancelAnimationFrame(moveRafRef.current)
            moveRafRef.current = null
          }
          setPointer(null)
          scheduleHideHover()
        }}
        className={`
                w-full border-2 rounded-xl p-4 text-left transition-all hover:shadow-md
                ${selected
                  ? 'border-kramer-green bg-kramer-green-light shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300'
                }
              `}
      >
        <div className="h-36 sm:h-40 mb-3 rounded-lg overflow-hidden bg-gray-50 flex items-center justify-center">
          <ShapeImage
            src={s.image}
            alt={s.label}
            className="max-h-full max-w-full w-full h-full object-contain"
          />
        </div>
        <div className="font-semibold text-gray-800">{s.label}</div>
        <div className="text-sm text-gray-500">
          {s.description} · {s.braces}
        </div>
      </button>
    </div>
  )
}

export default function Step1Shape({ shape, onShapeChange, onNext }) {
  const [hoveredId, setHoveredId] = useState(null)
  const [mobilePreviewId, setMobilePreviewId] = useState(null)

  return (
    <div className="card overflow-visible">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Krok 1: Kształt piłkochwytu</h2>
      <p className="text-gray-500 text-sm mb-6">
        Wybierz układ ścian siatkowych (widok z góry). Na ekranie z myszą najedź na kartę, aby zobaczyć powiększenie;
        na urządzeniu dotykowym stuknij kartę, aby je pokazać lub ukryć.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-6 sm:pt-8">
        {SHAPES.map(s => (
          <ShapeOptionCard
            key={s.id}
            shape={s}
            selected={shape === s.id}
            onShapeChange={onShapeChange}
            hoveredId={hoveredId}
            setHoveredId={setHoveredId}
            mobilePreviewId={mobilePreviewId}
            setMobilePreviewId={setMobilePreviewId}
          />
        ))}
      </div>

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
