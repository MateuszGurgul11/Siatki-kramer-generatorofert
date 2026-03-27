export default function QuotePreview({ result, loading, nets, netId }) {
  const net = nets.find(n => n.id === netId)

  return (
    <div className="card static lg:sticky lg:top-6 !p-4 sm:!p-6">
      <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
        <span className="w-2 h-2 bg-kramer-green rounded-full"></span>
        Podgląd wyceny
      </h3>

      {loading && (
        <div className="flex items-center justify-center py-8 text-gray-400">
          <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          Obliczanie...
        </div>
      )}

      {!loading && result && (
        <div>
          {/* Stats */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-kramer-green">{result.poles_count}</div>
              <div className="text-xs text-gray-500">Słupów</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-kramer-green">{result.braces_count}</div>
              <div className="text-xs text-gray-500">Zastrzałów</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center col-span-2">
              <div className="text-2xl font-bold text-kramer-green">{result.net_area.toFixed(1)} mkw.</div>
              <div className="text-xs text-gray-500">Powierzchnia siatki</div>
            </div>
          </div>

          {/* Items */}
          <div className="space-y-1 mb-4">
            {result.items.map((item, i) => (
              <div key={i} className="flex justify-between text-xs py-1.5 border-b border-gray-100 last:border-0 gap-3">
                <span className="text-gray-600 flex-1 pr-2 leading-tight">
                  {item.name}
                  {item.unit === 'info' && item.quantity_desc ? (
                    <span className="block mt-0.5 text-[11px] text-gray-500 leading-snug">{item.quantity_desc}</span>
                  ) : null}
                </span>
                <span className="font-medium text-gray-800 whitespace-nowrap">
                  {item.unit === 'info'
                    ? '—'
                    : `${(item.value_brutto ?? (item.value_netto * 1.23)).toFixed(2)} zł`}
                </span>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="bg-gray-50 rounded-lg p-3 space-y-1">
            <div className="flex justify-between font-bold text-kramer-green border-t border-gray-200 pt-2 mt-1 text-sm">
              <span>Razem brutto</span>
              <span>{result.total_brutto.toFixed(2)} zł</span>
            </div>
          </div>
        </div>
      )}

      {!loading && !result && (
        <p className="text-sm text-gray-400 text-center py-6">
          Uzupełnij dane, aby zobaczyć podgląd wyceny
        </p>
      )}
    </div>
  )
}
