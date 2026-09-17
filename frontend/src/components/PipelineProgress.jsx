/**
 * PipelineProgress.jsx
 * Horizontal stepper showing the 4 stages of the MedAI-OS pipeline.
 * Props:
 *  - volumes   {Array}  - list of volumes (step 1 done if length > 0)
 *  - masks     {Array}  - list of masks   (step 2 done if length > 0)
 *  - meshes    {Array}  - list of meshes  (step 3 done)
 *  - implants  {Array}  - list of implants (step 4 done)
 *  - running   {string|null} - 'segment' | 'reconstruct' | 'implant' | null
 */
export default function PipelineProgress({ volumes, masks, meshes, implants, running }) {
  const steps = [
    { key: 'upload',      label: 'Upload',   icon: '📡', done: volumes?.length > 0 },
    { key: 'segment',     label: 'Segment',  icon: '🧠', done: masks?.length > 0   },
    { key: 'reconstruct', label: '3D Mesh',  icon: '🦴', done: meshes?.length > 0  },
    { key: 'implant',     label: 'Implant',  icon: '⚙️', done: implants?.length > 0 },
  ];

  return (
    <div className="pipeline-stepper">
      {steps.map((step, idx) => {
        const isRunning = running === step.key;
        const statusClass = isRunning ? 'running' : step.done ? 'done' : '';
        return (
          <div key={step.key} style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <div className={`pipeline-step ${statusClass}`} style={{ flex: 1 }}>
              <div className="pipeline-step-dot">
                {isRunning ? (
                  <span className="spinner" style={{ width: 12, height: 12 }} />
                ) : step.done ? (
                  '✓'
                ) : (
                  step.icon
                )}
              </div>
              <span className="pipeline-step-label">{step.label}</span>
            </div>
            {idx < steps.length - 1 && (
              <div className={`pipeline-connector ${step.done ? 'done' : ''}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
