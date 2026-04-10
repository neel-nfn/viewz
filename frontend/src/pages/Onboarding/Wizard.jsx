import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StepConnect from '../../components/Onboarding/StepConnect';
import StepPersona from '../../components/Onboarding/StepPersona';
import StepFirstTask from '../../components/Onboarding/StepFirstTask';

export default function Wizard() {
  const [step, setStep] = useState(1);
  const [data, setData] = useState({
    channelConnected: false,
    persona: null,
    firstTaskCreated: false
  });
  const navigate = useNavigate();

  function handleNext() {
    if (step < 3) {
      setStep(step + 1);
    } else {
      // Onboarding complete
      navigate('/app');
    }
  }

  function handleSkip() {
    navigate('/app');
  }

  return (
    <div className="min-h-screen bg-base-100 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full">
        <div className="card bg-base-200 p-8">
          {/* Progress indicator */}
          <div className="flex justify-between mb-6">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex-1 flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  s <= step ? 'bg-primary text-primary-content' : 'bg-base-300'
                }`}>
                  {s < step ? '✓' : s}
                </div>
                {s < 3 && (
                  <div className={`flex-1 h-1 mx-2 ${
                    s < step ? 'bg-primary' : 'bg-base-300'
                  }`} />
                )}
              </div>
            ))}
          </div>

          {/* Steps */}
          {step === 1 && (
            <StepConnect
              onNext={() => {
                setData({...data, channelConnected: true});
                handleNext();
              }}
              onSkip={handleSkip}
            />
          )}
          {step === 2 && (
            <StepPersona
              selected={data.persona}
              onSelect={(p) => setData({...data, persona: p})}
              onNext={handleNext}
              onSkip={handleSkip}
            />
          )}
          {step === 3 && (
            <StepFirstTask
              persona={data.persona}
              onComplete={() => {
                setData({...data, firstTaskCreated: true});
                setTimeout(() => navigate('/app'), 2000);
              }}
              onSkip={handleSkip}
            />
          )}
        </div>
      </div>
    </div>
  );
}

