import { useState, useEffect, useCallback } from 'react'
import StepIndicator from './components/StepIndicator'
import Step1Shape from './components/Step1Shape'
import Step2Walls from './components/Step2Walls'
import Step3Options from './components/Step3Options'
import Step4Customer from './components/Step4Customer'
import QuotePreview from './components/QuotePreview'
import ResultPage from './components/ResultPage'
import GeneratorCredits from './components/GeneratorCredits'
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
  const [wallsSecondary, setWallsSecondary] = useState([defaultWall()])
  const [netLayers, setNetLayers] = useState(1)
  const [edgeFinishing, setEdgeFinishing] = useState(false)
  const [includeMountingKit, setIncludeMountingKit] = useState(false)
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
    setWallsSecondary(prev => {
      if (prev.length === count) return prev
      if (prev.length < count) {
        const last = prev[prev.length - 1] || defaultWall()
        return [...prev, ...Array(count - prev.length).fill(null).map(() => defaultWall(last.height))]
      }
      return prev.slice(0, count)
    })
    if (!['line', 'L'].includes(shape)) {
      setNetLayers(1)
    }
  }, [shape])

  // Live calculation
  const runCalculation = useCallback(async () => {
    if (!netId) return
    const wallCount = SHAPE_WALLS[shape]
    if (walls.length < wallCount) return
    const wallsForCalc = walls.slice(0, wallCount)
    const allValid = wallsForCalc.every(w => w.length >= 3 && w.height > 0)
    if (!allValid) return
    const secondaryForCalc = wallsSecondary.slice(0, wallCount)
    const secondaryValid = secondaryForCalc.every(w => w.length >= 3 && w.height > 0)
    if (netLayers === 2 && !secondaryValid) return
    setCalcLoading(true)
    try {
      const res = await calculateQuote({
        shape,
        walls: wallsForCalc,
        walls_secondary: netLayers === 2 ? secondaryForCalc : undefined,
        net_layers: netLayers,
        edge_finishing: edgeFinishing,
        include_mounting_kit: includeMountingKit,
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
  }, [shape, walls, wallsSecondary, netLayers, edgeFinishing, includeMountingKit, mounting, netId, quoteType])

  useEffect(() => {
    const timeout = setTimeout(runCalculation, 400)
    return () => clearTimeout(timeout)
  }, [runCalculation])

  // iframe-resizer: wymuś ponowne liczenie wysokości po zmianie treści (krok, wynik, ładowanie)
  useEffect(() => {
    const notify = () => {
      const pf = typeof window !== 'undefined' && window.parentIFrame
      if (pf && typeof pf.size === 'function') {
        requestAnimationFrame(() => pf.size())
      }
    }
    notify()
    const t = window.setTimeout(notify, 100)
    return () => window.clearTimeout(t)
  }, [step, result, calcLoading, offerResult])

  useEffect(() => {
    const onResize = () => {
      const pf = typeof window !== 'undefined' && window.parentIFrame
      if (pf && typeof pf.size === 'function') pf.size()
    }
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  const handleGenerateOffer = async () => {
    if (!customer.name) {
      setError('Wypełnij imię i nazwisko / nazwę firmy')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const wallCount = SHAPE_WALLS[shape]
      const wallsForCalc = walls.slice(0, wallCount)
      const secondaryForCalc = wallsSecondary.slice(0, wallCount)
      const res = await generateOffer({
        calculation: {
          shape,
          walls: wallsForCalc,
          walls_secondary: netLayers === 2 ? secondaryForCalc : undefined,
          net_layers: netLayers,
          edge_finishing: edgeFinishing,
          include_mounting_kit: includeMountingKit,
          mounting,
          net_id: netId,
          quote_type: quoteType,
        },
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
    <div className="min-h-screen bg-gray-50 overflow-x-hidden">
      <div className="max-w-6xl mx-auto px-4 pt-16 pb-8 sm:pt-20">
        <StepIndicator steps={STEPS} currentStep={step} />

        <div className="mt-8 flex flex-col lg:flex-row gap-6 items-stretch lg:items-start">
          {/* Main form */}
          <div className="flex-1 min-w-0 order-1">
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
                netLayers={netLayers}
                onNetLayersChange={setNetLayers}
                edgeFinishing={edgeFinishing}
                onEdgeFinishingChange={setEdgeFinishing}
                includeMountingKit={includeMountingKit}
                onIncludeMountingKitChange={setIncludeMountingKit}
                wallsSecondary={wallsSecondary}
                onWallsSecondaryChange={setWallsSecondary}
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

          {/* Live Preview — pod formularzem na mobile, bokiem na desktop */}
          <div className="w-full lg:w-80 lg:flex-shrink-0 order-2 lg:sticky lg:top-4 lg:self-start">
            <QuotePreview result={result} loading={calcLoading} nets={nets} netId={netId} />
          </div>
        </div>

        <GeneratorCredits />
      </div>
    </div>
  )
}
