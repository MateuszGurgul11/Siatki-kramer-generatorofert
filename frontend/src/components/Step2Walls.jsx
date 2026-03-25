const SHAPE_NAMES = { line: 'Linia prosta', L: 'Kształt L', U: 'Kształt U', closed: 'Zamknięty' }
const WALL_LABELS = {
  line: ['Ściana'],
  L: ['Ściana lewa (pionowa)', 'Ściana dolna (pozioma)'],
  U: ['Ściana lewa', 'Ściana dolna', 'Ściana prawa'],
  closed: ['Ściana lewa', 'Ściana dolna', 'Ściana prawa', 'Ściana górna'],
}

const HEIGHTS = [4, 5, 6]

export default function Step2Walls({ shape, walls, onWallsChange, onBack, onNext }) {
  const labels = WALL_LABELS[shape]

  const updateWall = (idx, field, value) => {
    const updated = walls.map((w, i) =>
      i === idx ? { ...w, [field]: parseFloat(value) || 0 } : w
    )
    onWallsChange(updated)
  }

  const allValid = walls.every(w => w.length >= 3 && w.height > 0)

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Krok 2: Wymiary ścian</h2>
      <p className="text-gray-500 text-sm mb-6">
        Podaj długość i wysokość każdej ściany piłkochwytu
      </p>

      <div className="space-y-5">
        {walls.map((wall, idx) => (
          <div key={idx} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <h3 className="font-semibold text-kramer-green mb-4">
              {labels[idx] || `Ściana ${idx + 1}`}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Długość [m]</label>
                <input
                  type="number"
                  min="3"
                  max="200"
                  step="0.5"
                  value={wall.length}
                  onChange={e => updateWall(idx, 'length', e.target.value)}
                  className="input-field"
                  placeholder="np. 18"
                />
                {wall.length < 3 && <p className="text-red-500 text-xs mt-1">Minimalna długość: 3 m</p>}
              </div>
              <div>
                <label className="label">Wysokość [m]</label>
                <div className="flex gap-2">
                  {HEIGHTS.map(h => (
                    <button
                      key={h}
                      onClick={() => updateWall(idx, 'height', h)}
                      className={`flex-1 py-2.5 rounded-lg text-sm font-semibold border-2 transition-colors
                        ${wall.height === h
                          ? 'border-kramer-green bg-kramer-green text-white'
                          : 'border-gray-300 bg-white text-gray-700 hover:border-kramer-green'
                        }`}
                    >
                      {h} m
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 flex justify-between">
        <button className="btn-secondary" onClick={onBack}>← Wstecz</button>
        <button className="btn-primary" onClick={onNext} disabled={!allValid}>
          Dalej →
        </button>
      </div>
    </div>
  )
}
