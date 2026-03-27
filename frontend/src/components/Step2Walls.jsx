const SHAPE_NAMES = { line: 'Linia prosta', L: 'Kształt L', U: 'Kształt U', closed: 'Zamknięty' }
const WALL_LABELS = {
  line: ['A1'],
  L: ['A1', 'A3'],
  U: ['A1', 'A3', 'A2'],
  closed: ['A1', 'A3', 'A2', 'A4'],
}

const SECOND_NET_LABELS = {
  line: ['A2'],
  L: ['A4', 'A2'],
}

const HEIGHTS = [4, 5, 6]

function WallsForm({ walls, labels, title, onWallsChange }) {
  const updateWall = (idx, field, value) => {
    const updated = walls.map((w, i) =>
      i === idx ? { ...w, [field]: parseFloat(value) || 0 } : w
    )
    onWallsChange(updated)
  }

  return (
    <div className="space-y-5">
      {title && <h3 className="font-semibold text-gray-700">{title}</h3>}
      {walls.map((wall, idx) => (
        <div key={idx} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
          <h4 className="font-semibold text-kramer-green mb-4">
            {labels[idx] || `Ściana ${idx + 1}`}
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
  )
}

export default function Step2Walls({
  shape,
  walls,
  onWallsChange,
  netLayers,
  onNetLayersChange,
  edgeFinishing,
  onEdgeFinishingChange,
  includeMountingKit,
  onIncludeMountingKitChange,
  wallsSecondary,
  onWallsSecondaryChange,
  onBack,
  onNext,
}) {
  const labels = WALL_LABELS[shape]
  const secondaryLabels = SECOND_NET_LABELS[shape] || labels
  const supportsTwoNets = ['line', 'L'].includes(shape)
  const allValidPrimary = walls.every(w => w.length >= 3 && w.height > 0)
  const allValidSecondary = netLayers === 1 || wallsSecondary.every(w => w.length >= 3 && w.height > 0)
  const allValid = allValidPrimary && allValidSecondary

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Krok 2: Wymiary ścian</h2>
      <p className="text-gray-500 text-sm mb-6">
        Podaj długość i wysokość każdej ściany piłkochwytu
      </p>

      {supportsTwoNets && (
        <div className="mb-6">
          <h3 className="font-semibold text-gray-700 mb-3">Liczba siatek</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => onNetLayersChange(1)}
              className={`p-4 border-2 rounded-xl text-left transition-all ${netLayers === 1 ? 'border-kramer-green bg-kramer-green-light' : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="font-semibold text-gray-800">1 siatka</div>
              <div className="text-sm text-gray-500">Jeden zestaw wymiarów</div>
            </button>
            <button
              type="button"
              onClick={() => onNetLayersChange(2)}
              className={`p-4 border-2 rounded-xl text-left transition-all ${netLayers === 2 ? 'border-kramer-green bg-kramer-green-light' : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="font-semibold text-gray-800">2 siatki</div>
              <div className="text-sm text-gray-500">Osobne wymiary dla każdej</div>
            </button>
          </div>
        </div>
      )}

      <div className="mb-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label className="flex items-start gap-3 p-4 border border-gray-200 rounded-xl bg-white cursor-pointer">
          <input
            type="checkbox"
            checked={edgeFinishing}
            onChange={e => onEdgeFinishingChange(e.target.checked)}
            className="mt-1 h-4 w-4 accent-kramer-green"
          />
          <span>
            <span className="block font-semibold text-gray-800">Obszycie na brzegach</span>
            <span className="block text-sm text-gray-500">Dodaj informację o obszyciu krawędzi siatki.</span>
          </span>
        </label>

        <label className="flex items-start gap-3 p-4 border border-gray-200 rounded-xl bg-white cursor-pointer">
          <input
            type="checkbox"
            checked={includeMountingKit}
            onChange={e => onIncludeMountingKitChange(e.target.checked)}
            className="mt-1 h-4 w-4 accent-kramer-green"
          />
          <span>
            <span className="block font-semibold text-gray-800">Doliczyć zestaw montażowy</span>
            <span className="block text-sm text-gray-500">Linka, śruby oczkowe, karabińczyki i komplet śrub rzymskich.</span>
          </span>
        </label>
      </div>

      <WallsForm
        walls={walls}
        labels={labels}
        title={netLayers === 2 ? 'Siatka 1' : null}
        onWallsChange={onWallsChange}
      />

      {supportsTwoNets && netLayers === 2 && (
        <div className="mt-6">
          <WallsForm
            walls={wallsSecondary}
            labels={secondaryLabels}
            title="Siatka 2"
            onWallsChange={onWallsSecondaryChange}
          />
        </div>
      )}

      <div className="mt-8 flex justify-between">
        <button className="btn-secondary" onClick={onBack}>← Wstecz</button>
        <button className="btn-primary" onClick={onNext} disabled={!allValid}>
          Dalej →
        </button>
      </div>
    </div>
  )
}
