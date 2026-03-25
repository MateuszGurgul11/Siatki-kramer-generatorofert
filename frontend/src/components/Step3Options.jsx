export default function Step3Options({
  mounting, onMountingChange,
  nets, netId, onNetChange,
  quoteType, onQuoteTypeChange,
  onBack, onNext,
}) {
  const isValid = netId !== ''

  return (
    <div className="card space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-1">Krok 3: Opcje</h2>
        <p className="text-gray-500 text-sm">Wybierz montaż, siatkę i zakres wyceny</p>
      </div>

      {/* Montaż słupów */}
      <div>
        <h3 className="font-semibold text-gray-700 mb-3">Opcja montażu słupów</h3>
        <div className="grid grid-cols-2 gap-3">
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
            <div className="text-sm font-medium text-orange-600 mt-1">+190 zł netto/szt.</div>
          </button>
        </div>
      </div>

      {/* Wybór siatki */}
      <div>
        <h3 className="font-semibold text-gray-700 mb-3">Wybór siatki</h3>
        <div className="space-y-2">
          {nets.map(net => (
            <button
              key={net.id}
              onClick={() => onNetChange(net.id)}
              className={`w-full p-3 border-2 rounded-xl text-left transition-all ${netId === net.id ? 'border-kramer-green bg-kramer-green-light' : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1 pr-4">
                  <div className="font-medium text-gray-800 text-sm">{net.name}</div>
                  <div className="text-xs text-gray-500 mt-0.5">{net.description}</div>
                </div>
                <div className="text-kramer-green font-bold whitespace-nowrap">{net.price_netto.toFixed(2)} zł/mkw.</div>
              </div>
            </button>
          ))}
        </div>
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
            <div className="text-sm text-gray-500 mt-1">Bez słupów i zastrzałów (np. do wniosku w Gminie)</div>
          </button>
        </div>
      </div>

      <div className="flex justify-between pt-2">
        <button className="btn-secondary" onClick={onBack}>← Wstecz</button>
        <button className="btn-primary" onClick={onNext} disabled={!isValid}>Dalej →</button>
      </div>
    </div>
  )
}
