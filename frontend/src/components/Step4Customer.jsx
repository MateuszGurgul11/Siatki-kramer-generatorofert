export default function Step4Customer({ customer, onCustomerChange, onBack, onSubmit, loading, error }) {
  const update = (field, value) => onCustomerChange({ ...customer, [field]: value })
  const isValid = customer.name.trim() && customer.email.trim()

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-800 mb-1">Krok 4: Dane kontaktowe</h2>
      <p className="text-gray-500 text-sm mb-6">
        Oferta zostanie wysłana na podany adres e-mail
      </p>

      <div className="space-y-4">
        <div>
          <label className="label">Imię i nazwisko / Nazwa firmy *</label>
          <input
            type="text"
            value={customer.name}
            onChange={e => update('name', e.target.value)}
            className="input-field"
            placeholder="np. Jan Kowalski lub Gmina Przykładowa"
          />
        </div>
        <div>
          <label className="label">Adres e-mail *</label>
          <input
            type="email"
            value={customer.email}
            onChange={e => update('email', e.target.value)}
            className="input-field"
            placeholder="np. jan@przyklad.pl"
          />
        </div>
        <div>
          <label className="label">Numer telefonu (opcjonalnie)</label>
          <input
            type="tel"
            value={customer.phone}
            onChange={e => update('phone', e.target.value)}
            className="input-field"
            placeholder="np. +48 600 000 000"
          />
        </div>
        <div>
          <label className="label">Adres / miejscowość (opcjonalnie)</label>
          <input
            type="text"
            value={customer.address}
            onChange={e => update('address', e.target.value)}
            className="input-field"
            placeholder="np. Warszawa, ul. Przykładowa 1"
          />
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <p className="mt-4 text-xs text-gray-400">
        * Pola wymagane. Dane służą wyłącznie do wystawienia oferty.
      </p>

      <div className="mt-6 flex justify-between">
        <button className="btn-secondary" onClick={onBack} disabled={loading}>← Wstecz</button>
        <button className="btn-primary" onClick={onSubmit} disabled={!isValid || loading}>
          {loading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Generowanie...
            </span>
          ) : 'Generuj ofertę PDF'}
        </button>
      </div>
    </div>
  )
}
