import { useState, useEffect, useCallback } from 'react'
import StepIndicator from './components/StepIndicator'
import Step1Shape from './components/Step1Shape'
import Step2Walls from './components/Step2Walls'
import Step3Options from './components/Step3Options'
import Step4Customer from './components/Step4Customer'
import QuotePreview from './components/QuotePreview'
import ResultPage from './components/ResultPage'
import { fetchNets, calculateQuote, generateOffer } from './api'

const STEPS = [
  { id: 1, label: 'Kształt' },
  { id: 2, label: 'Wymiary' },
  { id: 3, label: 'Opcje' },
  { id: 4, label: 'Dane' },
]

const SHAPE_WALLS = { line: 1, L: 2, U: 3, closed: 4 }

const defaultWall = (height = 4) => ({ length: 10, height })

export default function App() {
  const [step, setStep] = useState(1)
  const [nets, setNets] = useState([])
  const [result, setResult] = useState(null)
  const [offerResult, setOfferResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [calcLoading, setCalcLoading] = useState(false)
  const [error, setError] = useState(null)

  // Form state
  const [shape, setShape] = useState('line')
  const [walls, setWalls] = useState([defaultWall()])
  const [mounting, setMounting] = useState('concrete')
  const [netId, setNetId] = useState('')
  const [quoteType, setQuoteType] = useState('complete')
  const [customer, setCustomer] = useState({ name: '', email: '', phone: '', address: '' })

  useEffect(() => {
    fetchNets().then(data => {
      setNets(data)
      if (data.length > 0) setNetId(data[0].id)
    }).catch(console.error)
  }, [])

  // Sync walls count with shape
  useEffect(() => {
    const count = SHAPE_WALLS[shape]
    setWalls(prev => {
      if (prev.length === count) return prev
      if (prev.length < count) {
        const last = prev[prev.length - 1] || defaultWall()
        return [...prev, ...Array(count - prev.length).fill(null).map(() => defaultWall(last.height))]
      }
      return prev.slice(0, count)
    })
  }, [shape])

  // Live calculation
  const runCalculation = useCallback(async () => {
    if (!netId) return
    const wallCount = SHAPE_WALLS[shape]
    if (walls.length < wallCount) return
    const wallsForCalc = walls.slice(0, wallCount)
    const allValid = wallsForCalc.every(w => w.length >= 3 && w.height > 0)
    if (!allValid) return
    setCalcLoading(true)
    try {
      const res = await calculateQuote({
        shape,
        walls: wallsForCalc,
        mounting,
        net_id: netId,
        quote_type: quoteType,
      })
      setResult(res)
    } catch (e) {
      console.error(e)
    } finally {
      setCalcLoading(false)
    }
  }, [shape, walls, mounting, netId, quoteType])

  useEffect(() => {
    const timeout = setTimeout(runCalculation, 400)
    return () => clearTimeout(timeout)
  }, [runCalculation])

  const handleGenerateOffer = async () => {
    if (!customer.name || !customer.email) {
      setError('Wypełnij imię/nazwę i adres e-mail')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const wallCount = SHAPE_WALLS[shape]
      const wallsForCalc = walls.slice(0, wallCount)
      const res = await generateOffer({
        calculation: { shape, walls: wallsForCalc, mounting, net_id: netId, quote_type: quoteType },
        customer,
      })
      setOfferResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  if (offerResult) {
    return <ResultPage offerResult={offerResult} customer={customer} onReset={() => { setOfferResult(null); setStep(1) }} />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-kramer-green text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center gap-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Siatki Kramer</h1>
            <p className="text-green-200 text-sm">Generator ofert piłkochwytów</p>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <StepIndicator steps={STEPS} currentStep={step} />

        <div className="mt-8 flex gap-6 items-start">
          {/* Main form */}
          <div className="flex-1 min-w-0">
            {step === 1 && (
              <Step1Shape
                shape={shape}
                onShapeChange={setShape}
                onNext={() => setStep(2)}
              />
            )}
            {step === 2 && (
              <Step2Walls
                shape={shape}
                walls={walls}
                onWallsChange={setWalls}
                onBack={() => setStep(1)}
                onNext={() => setStep(3)}
              />
            )}
            {step === 3 && (
              <Step3Options
                mounting={mounting}
                onMountingChange={setMounting}
                nets={nets}
                netId={netId}
                onNetChange={setNetId}
                quoteType={quoteType}
                onQuoteTypeChange={setQuoteType}
                onBack={() => setStep(2)}
                onNext={() => setStep(4)}
              />
            )}
            {step === 4 && (
              <Step4Customer
                customer={customer}
                onCustomerChange={setCustomer}
                onBack={() => setStep(3)}
                onSubmit={handleGenerateOffer}
                loading={loading}
                error={error}
              />
            )}
          </div>

          {/* Live Preview */}
          <div className="w-80 flex-shrink-0 hidden lg:block">
            <QuotePreview result={result} loading={calcLoading} nets={nets} netId={netId} />
          </div>
        </div>
      </div>
    </div>
  )
}
