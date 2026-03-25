import { useState } from 'react'
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

function ShapeVisualPopup({ shape }) {
  return (
    <div
      className="absolute z-50 w-[min(100vw-2rem,22rem)] max-w-[22rem] bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden"
      style={{ bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: 8 }}
    >
      <div className="bg-gray-100 w-full h-56 sm:h-64 flex items-center justify-center relative overflow-hidden">
        <ShapeImage
          src={shape.image}
          alt={`Wizualizacja: ${shape.label}`}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="px-3 py-2 border-t border-gray-100">
        <div className="font-semibold text-gray-800 text-sm">{shape.label}</div>
        <div className="text-xs text-gray-500">{shape.description} · {shape.braces}</div>
      </div>
      <div
        className="absolute w-3 h-3 bg-white border-b border-r border-gray-200 rotate-45"
        style={{ bottom: -7, left: '50%', transform: 'translateX(-50%) rotate(45deg)' }}
      />
    </div>
  )
}

export default function Step1Shape({ shape, onShapeChange, onNext }) {
  const [hoveredId, setHoveredId] = useState(null)

  return (
    <div className="card overflow-visible">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Krok 1: Kształt piłkochwytu</h2>
      <p className="text-gray-500 text-sm mb-6">
        Wybierz układ ścian siatkowych (widok z góry) · najedź kursorem, aby zobaczyć powiększenie
      </p>

      <div className="grid grid-cols-2 gap-4 pt-6 sm:pt-8">
        {SHAPES.map(s => (
          <div key={s.id} className="relative z-10">
            {hoveredId === s.id && <ShapeVisualPopup shape={s} />}
            <button
              type="button"
              onClick={() => onShapeChange(s.id)}
              onMouseEnter={() => setHoveredId(s.id)}
              onMouseLeave={() => setHoveredId(null)}
              className={`
                w-full border-2 rounded-xl p-4 text-left transition-all hover:shadow-md
                ${shape === s.id
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
              <div className="text-sm text-gray-500">{s.description} · {s.braces}</div>
            </button>
          </div>
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
