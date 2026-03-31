import { useEffect, useMemo } from 'react'

function parseNetOption(net) {
  // Obsługa m.in. 10×10, 4,5×4,5 (przecinek dziesiętny w nazwie siatki)
  const sizeMatch = net.name.match(
    /oczko\s*((?:[0-9]+[.,][0-9]+|[0-9]+)(?:\s*[x×]\s*(?:[0-9]+[.,][0-9]+|[0-9]+))?)\s*cm/i
  )
  const thicknessMatch = net.name.match(/(?:śr\.?\s*sznurka|grubość)\s*([0-9]+(?:[.,][0-9]+)?)\s*mm/i)
  const materialMatch = net.name.match(/\b(PP|PE|PA)\b/i)

  const meshRaw = (sizeMatch?.[1] || '')
    .trim()
    .replace(/\s+/g, '')
    .replace(/x/gi, '×')
  const meshKey = meshRaw || 'inne'
  const meshLabelText = meshRaw ? meshRaw.replace(/×/g, ' × ') : 'inne'
  const thickness = thicknessMatch?.[1]?.replace(',', '.') || 'brak'
  const material = materialMatch?.[1]?.toUpperCase() || ''

  return {
    net,
    meshKey,
    meshLabel: `Rozmiar oczka ${meshLabelText} cm`,
    thicknessValue: parseFloat(thickness) || 0,
    thicknessLabel: `Grubość ${thickness} mm${material ? ` ${material}` : ''}`,
  }
}

export default function Step3Options({
  mounting,
  onMountingChange,
  nets,
  netId,
  onNetChange,
  quoteType,
  onQuoteTypeChange,
  includeMountingKit,
  onIncludeMountingKitChange,
  onBack,
  onNext,
}) {
  const parsed = useMemo(() => nets.map(parseNetOption), [nets])
  const groups = useMemo(() => {
    const map = new Map()
    parsed.forEach(p => {
      if (!map.has(p.meshKey)) map.set(p.meshKey, { meshLabel: p.meshLabel, options: [] })
      map.get(p.meshKey).options.push(p)
    })
    for (const group of map.values()) {
      group.options.sort((a, b) => a.thicknessValue - b.thicknessValue || a.thicknessLabel.localeCompare(b.thicknessLabel))
    }
    return Array.from(map.entries()).map(([meshKey, value]) => ({ meshKey, ...value }))
  }, [parsed])

  const selectedParsed = parsed.find(p => p.net.id === netId) || null
  const selectedMeshKey = selectedParsed?.meshKey || groups[0]?.meshKey || ''
  const selectedGroup = groups.find(g => g.meshKey === selectedMeshKey) || null

  useEffect(() => {
    if (!netId && groups[0]?.options?.[0]) {
      onNetChange(groups[0].options[0].net.id)
    }
  }, [groups, netId, onNetChange])

  const isValid = netId !== ''

  return (
    <div className="card space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-1">Krok 3: Opcje</h2>
        <p className="text-gray-500 text-sm">Wybierz zakres wyceny, siatkę i dodatki</p>
      </div>

      {/* Zakres wyceny */}
      <div>
        <h3 className="font-semibold text-gray-700 mb-3">Zakres wyceny</h3>
        <div className="space-y-2">
          <button
            onClick={() => onQuoteTypeChange('complete')}
            className={`w-full p-4 border-2 rounded-xl text-left transition-all ${quoteType === 'complete' ? 'border-kramer-green bg-kramer-green-light' : 'border-gray-200 hover:border-gray-300'}`}
          >
            <div className="font-semibold text-gray-800">Kompletna wycena</div>
            <div className="text-sm text-gray-500 mt-1">Słupy + zastrzały + siatka + akcesoria + transport</div>
          </button>
          <button
            onClick={() => onQuoteTypeChange('net_only')}
            className={`w-full p-4 border-2 rounded-xl text-left transition-all ${quoteType === 'net_only' ? 'border-kramer-green bg-kramer-green-light' : 'border-gray-200 hover:border-gray-300'}`}
          >
            <div className="font-semibold text-gray-800">Tylko siatka + akcesoria + dostawa</div>
            <div className="text-sm text-gray-500 mt-1">Bez słupów i zastrzałów + transport</div>
          </button>
        </div>
      </div>

      {/* Wybór siatki */}
      <div>
        <h3 className="font-semibold text-gray-700 mb-3">Wybór siatki</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
          <div>
            <label className="label">Rozmiar oczka</label>
            <select
              className="input-field"
              value={selectedMeshKey}
              onChange={e => {
                const group = groups.find(g => g.meshKey === e.target.value)
                if (group?.options?.[0]) onNetChange(group.options[0].net.id)
              }}
            >
              {groups.map(group => (
                <option key={group.meshKey} value={group.meshKey}>
                  {group.meshLabel}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Grubość / typ</label>
            <select
              className="input-field"
              value={netId}
              onChange={e => onNetChange(e.target.value)}
              disabled={!selectedGroup}
            >
              {(selectedGroup?.options || []).map(opt => (
                <option key={opt.net.id} value={opt.net.id}>
                  {opt.thicknessLabel}
                </option>
              ))}
            </select>
          </div>
        </div>
        {selectedParsed && (
          <div className="w-full p-3 border-2 border-kramer-green rounded-xl bg-kramer-green-light text-left">
            <div className="flex justify-between items-start">
              <div className="flex-1 pr-4">
                <div className="font-medium text-gray-800 text-sm">{selectedParsed.net.name}</div>
                <div className="text-xs text-gray-500 mt-0.5">{selectedParsed.net.description}</div>
              </div>
              <div className="text-kramer-green font-bold whitespace-nowrap">{selectedParsed.net.price_brutto.toFixed(2)} zł/mkw. brutto</div>
            </div>
          </div>
        )}
        {!selectedParsed && (
          <div className="text-sm text-gray-400">
            Brak dostępnych opcji siatki.
          </div>
        )}
      </div>

      {/* Zestaw montażowy */}
      <div>
        <h3 className="font-semibold text-gray-700 mb-3">Zestaw montażowy</h3>
        <label className="flex items-start gap-3 p-4 border border-gray-200 rounded-xl bg-white cursor-pointer">
          <input
            type="checkbox"
            checked={includeMountingKit}
            onChange={e => onIncludeMountingKitChange(e.target.checked)}
            className="mt-1 h-4 w-4 accent-kramer-green"
          />
          <span>
            <span className="block font-semibold text-gray-800">Doliczyć zestaw montażowy</span>
            <span className="block text-sm text-gray-500">
              Linka stalowa, śruby oczkowe, karabińczyki oraz komplet śrub rzymskich i zacisków.
            </span>
          </span>
        </label>
      </div>

      {/* Opcja montażu słupów — tylko dla kompletnej wyceny */}
      {quoteType === 'complete' && (
        <div>
          <h3 className="font-semibold text-gray-700 mb-3">Opcja montażu słupów</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              onClick={() => onMountingChange('concrete')}
              className={`p-4 border-2 rounded-xl text-left transition-all ${mounting === 'concrete' ? 'border-kramer-green bg-kramer-green-light' : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="font-semibold text-gray-800 mb-1">Montaż w betonie</div>
              <div className="text-sm text-gray-500">Trwały, rekomendowany</div>
              <div className="text-sm font-medium text-kramer-green mt-1">Bez dopłaty</div>
            </button>
            <button
              onClick={() => onMountingChange('sleeve')}
              className={`p-4 border-2 rounded-xl text-left transition-all ${mounting === 'sleeve' ? 'border-kramer-green bg-kramer-green-light' : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="font-semibold text-gray-800 mb-1">Tuleje montażowe</div>
              <div className="text-sm text-gray-500">Łatwiejszy demontaż</div>
              <div className="text-sm font-medium text-orange-600 mt-1">+233 zł brutto/szt.</div>
            </button>
          </div>
        </div>
      )}

      <div className="flex justify-between pt-2">
        <button className="btn-secondary" onClick={onBack}>← Wstecz</button>
        <button className="btn-primary" onClick={onNext} disabled={!isValid}>Dalej →</button>
      </div>
    </div>
  )
}
