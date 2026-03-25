import { resolveApiUrl } from '../api'

export default function ResultPage({ offerResult, customer, onReset }) {
  const pdfUrl = resolveApiUrl(offerResult.pdf_url)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-kramer-green text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-xl font-bold">Siatki Kramer — Generator Ofert</h1>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-4 py-16">
        <div className="card text-center">
          {/* Sukces ikona */}
          <div className="w-20 h-20 bg-kramer-green-light rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-kramer-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
            </svg>
          </div>

          <h2 className="text-2xl font-bold text-gray-800 mb-2">Oferta wygenerowana!</h2>
          <p className="text-gray-500 mb-6">
            Numer oferty: <strong className="text-kramer-green">{offerResult.offer_number}</strong>
          </p>

          <div className="bg-kramer-green-light rounded-xl p-6 mb-6 text-left">
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-600">Wartość brutto:</span>
              <span className="text-2xl font-bold text-kramer-green">{offerResult.total_brutto?.toFixed(2)} zł</span>
            </div>
            <div className="flex justify-between text-sm text-gray-500">
              <span>Adres e-mail:</span>
              <span>{customer.email}</span>
            </div>
          </div>

          {offerResult.email_sent ? (
            <p className="text-sm text-green-700 mb-6 bg-green-50 rounded-lg p-3">
              ✓ Oferta została wysłana na adres e-mail {customer.email}
            </p>
          ) : (
            <p className="text-sm text-orange-700 mb-6 bg-orange-50 rounded-lg p-3">
              ⚠ Nie udało się wysłać e-maila — pobierz PDF ręcznie poniżej
            </p>
          )}

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a
              href={pdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary inline-flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              </svg>
              Pobierz PDF
            </a>
            <button onClick={onReset} className="btn-secondary">
              Nowa wycena
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-gray-400 mt-8">
          Wycena jest orientacyjna i nie stanowi oferty w rozumieniu przepisów prawa.
        </p>
      </div>
    </div>
  )
}
