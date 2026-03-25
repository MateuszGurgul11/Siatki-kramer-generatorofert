export default function StepIndicator({ steps, currentStep }) {
  return (
    <div className="flex items-center gap-0">
      {steps.map((step, idx) => (
        <div key={step.id} className="flex items-center flex-1">
          <div className="flex items-center gap-2">
            <div className={`
              w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors
              ${currentStep === step.id ? 'bg-kramer-green text-white shadow-md' :
                currentStep > step.id ? 'bg-green-200 text-kramer-green' :
                'bg-gray-200 text-gray-500'}
            `}>
              {currentStep > step.id ? '✓' : step.id}
            </div>
            <span className={`text-sm font-medium hidden sm:block ${currentStep === step.id ? 'text-kramer-green' : 'text-gray-500'}`}>
              {step.label}
            </span>
          </div>
          {idx < steps.length - 1 && (
            <div className={`flex-1 h-0.5 mx-2 ${currentStep > step.id ? 'bg-kramer-green' : 'bg-gray-200'}`} />
          )}
        </div>
      ))}
    </div>
  )
}
