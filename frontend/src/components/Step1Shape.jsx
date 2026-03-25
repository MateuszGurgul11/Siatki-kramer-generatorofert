import { useState } from 'react'

const SHAPES = [
  {
    id: 'line',
    label: 'Linia prosta',
    description: '1 ściana',
    braces: '2+ zastrzały',
    // Zastąp ścieżkę plikiem wizualizacji dla linii prostej
    visualImage: '/images/shapes/linia-prosta.jpg',
    icon: (
      <svg viewBox="0 0 80 40" className="w-full h-full">
        <line x1="10" y1="20" x2="70" y2="20" stroke="#1a5c2a" strokeWidth="3" strokeLinecap="round"/>
        <circle cx="10" cy="20" r="4" fill="#1a5c2a"/>
        <circle cx="70" cy="20" r="4" fill="#1a5c2a"/>
        <line x1="10" y1="20" x2="18" y2="32" stroke="#4caf50" strokeWidth="2"/>
        <line x1="70" y1="20" x2="62" y2="32" stroke="#4caf50" strokeWidth="2"/>
      </svg>
    ),
  },
  {
    id: 'L',
    label: 'Kształt L',
    description: '2 ściany',
    braces: '4+ zastrzały',
    // Zastąp ścieżkę plikiem wizualizacji dla kształtu L
    visualImage: '/images/shapes/ksztalt-l.jpg',
    icon: (
      <svg viewBox="0 0 80 60" className="w-full h-full">
        <polyline points="10,10 10,50 70,50" fill="none" stroke="#1a5c2a" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
        <circle cx="10" cy="10" r="4" fill="#1a5c2a"/>
        <circle cx="10" cy="50" r="4" fill="#1a5c2a"/>
        <circle cx="70" cy="50" r="4" fill="#1a5c2a"/>
        <line x1="10" y1="10" x2="22" y2="16" stroke="#4caf50" strokeWidth="2"/>
        <line x1="70" y1="50" x2="62" y2="38" stroke="#4caf50" strokeWidth="2"/>
      </svg>
    ),
  },
  {
    id: 'U',
    label: 'Kształt U',
    description: '3 ściany',
    braces: '6+ zastrzałów',
    // Zastąp ścieżkę plikiem wizualizacji dla kształtu U
    visualImage: '/images/shapes/ksztalt-u.jpg',
    icon: (
      <svg viewBox="0 0 80 60" className="w-full h-full">
        <polyline points="10,10 10,50 70,50 70,10" fill="none" stroke="#1a5c2a" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
        <circle cx="10" cy="10" r="4" fill="#1a5c2a"/>
        <circle cx="10" cy="50" r="4" fill="#1a5c2a"/>
        <circle cx="70" cy="50" r="4" fill="#1a5c2a"/>
        <circle cx="70" cy="10" r="4" fill="#1a5c2a"/>
        <line x1="10" y1="10" x2="22" y2="15" stroke="#4caf50" strokeWidth="2"/>
        <line x1="70" y1="10" x2="58" y2="15" stroke="#4caf50" strokeWidth="2"/>
      </svg>
    ),
  },
  {
    id: 'closed',
    label: 'Zamknięty',
    description: '4 ściany',
    braces: '8+ zastrzałów',
    // Zastąp ścieżkę plikiem wizualizacji dla układu zamkniętego
    visualImage: '/images/shapes/zamkniety.jpg',
    icon: (
      <svg viewBox="0 0 80 60" className="w-full h-full">
        <rect x="10" y="10" width="60" height="40" fill="none" stroke="#1a5c2a" strokeWidth="3" rx="1"/>
        <circle cx="10" cy="10" r="3" fill="#1a5c2a"/>
        <circle cx="70" cy="10" r="3" fill="#1a5c2a"/>
        <circle cx="70" cy="50" r="3" fill="#1a5c2a"/>
        <circle cx="10" cy="50" r="3" fill="#1a5c2a"/>
      </svg>
    ),
  },
]

function ShapeVisualPopup({ shape, anchorRef }) {
  return (
    <div
      className="absolute z-50 bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden"
      style={{ width: 280, bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: 8 }}
    >
      <div className="bg-gray-100 w-full h-44 flex items-center justify-center relative overflow-hidden">
        <img
          src={shape.visualImage}
          alt={`Wizualizacja: ${shape.label}`}
          className="w-full h-full object-cover"
          onError={e => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex' }}
        />
        {/* Placeholder gdy brak zdjęcia */}
        <div
          className="absolute inset-0 bg-gray-100 hidden items-center justify-center flex-col gap-2"
          style={{ display: 'none' }}
        >
          <div className="text-4xl opacity-30">🏟️</div>
          <span className="text-xs text-gray-400 text-center px-4">
            Wstaw zdjęcie wizualizacji do:<br/>
            <code className="text-gray-500 text-xs">public{shape.visualImage}</code>
          </span>
        </div>
      </div>
      <div className="px-3 py-2 border-t border-gray-100">
        <div className="font-semibold text-gray-800 text-sm">{shape.label}</div>
        <div className="text-xs text-gray-500">{shape.description} · {shape.braces}</div>
      </div>
      {/* Strzałka */}
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
    <div className="card">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Krok 1: Kształt piłkochwytu</h2>
      <p className="text-gray-500 text-sm mb-6">
        Wybierz układ ścian siatkowych (widok z góry) · najedź kursorem, aby zobaczyć wizualizację
      </p>

      <div className="grid grid-cols-2 gap-4">
        {SHAPES.map(s => (
          <div key={s.id} className="relative">
            {hoveredId === s.id && <ShapeVisualPopup shape={s} />}
            <button
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
              <div className="h-20 mb-3">
                {s.icon}
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
        <button className="btn-primary" onClick={onNext}>
          Dalej →
        </button>
      </div>
    </div>
  )
}
