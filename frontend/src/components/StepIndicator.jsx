import { Fragment } from 'react'

/** Pasek na pełną szerokość kontenera (jak łącznie obie kolumny: formularz + podgląd). */
export default function StepIndicator({ steps, currentStep }) {
  return (
    <div className="w-full min-w-0 flex items-center">
      {steps.map((step, idx) => (
        <Fragment key={step.id}>
          <div className="flex items-center gap-1 sm:gap-2 shrink-0">
            <div
              className={`
              w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs sm:text-sm font-bold transition-colors shrink-0
              ${currentStep === step.id ? 'bg-kramer-green text-white shadow-md' :
                currentStep > step.id ? 'bg-green-200 text-kramer-green' :
                'bg-gray-200 text-gray-500'}
            `}
            >
              {currentStep > step.id ? '✓' : step.id}
            </div>
            <span
              className={`text-sm font-medium hidden sm:inline whitespace-nowrap ${currentStep === step.id ? 'text-kramer-green' : 'text-gray-500'}`}
            >
              {step.label}
            </span>
          </div>
          {idx < steps.length - 1 && (
            <div
              className={`flex-1 min-w-[0.5rem] h-0.5 mx-1.5 sm:mx-3 ${currentStep > step.id ? 'bg-kramer-green' : 'bg-gray-200'}`}
            />
          )}
        </Fragment>
      ))}
    </div>
  )
}
