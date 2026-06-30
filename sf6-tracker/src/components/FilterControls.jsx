import PhaseFilter from "./PhaseFilter";
import Select from 'react-select';

function FilterControls({
  currentMode,
  setCurrentMode,
  currentCharacterFilter,
  setCurrentCharacterFilter,
  characters,
  mainsOnly,
  setMainsOnly,
  phaseList,
  currentPhase,
  setCurrentPhase
}) {
  const char_options = characters.map(char => ({value: char, label: char}));
  
  const selectedCharacter = currentCharacterFilter
    ? { value: currentCharacterFilter, label: currentCharacterFilter }
    : null;

  const modeOptions = [
    {
      value: 'highest',
      label: parseInt(currentPhase.replace("Phase ", ""), 10) < 11 ? "Highest MR*" : "Highest MR"
    },
    { value: 'current', label: 'Current MR' }
  ];

  const selectedMode = modeOptions.find(option => option.value === currentMode);

  return (
    <div className="card controls-card mb-4">
      <div className="card-body">
        <div className="row align-items-center justify-content-center g-2">
          <div className="col-auto">
            <div className="d-flex flex-row align-items-center gap-2">
              <label htmlFor="phaseModeSelect" className="form-label mb-0 text-nowrap">Phase:</label>
              <PhaseFilter
                currentPhase={currentPhase}
                setCurrentPhase={setCurrentPhase}
                phaseList={phaseList}
              />
            </div>
          </div>
          
          <div className="col-auto">
            <div className="d-flex flex-row align-items-center gap-2">
              <label htmlFor="mrModeSelect" className="form-label mb-0 text-nowrap">Mode:</label>
              <Select
                options={modeOptions}
                value={selectedMode}
                onChange={(selected) => setCurrentMode(selected.value)}
                classNamePrefix="rs"
                className="react-select-bootstrap"
                isSearchable={false}
              />
            </div>
          </div>
          
          <div className="col-auto">
            <div className="d-flex flex-row align-items-center gap-2">
              <label className="form-label mb-0 text-nowrap">Character:</label>
              <Select
                options={char_options}
                value={selectedCharacter}
                onChange={(selected) => {
                  setCurrentCharacterFilter(selected ? selected.value : null);
                }}
                classNamePrefix="rs"
                className="react-select-bootstrap"
                placeholder="All Characters"
                isClearable
                isSearchable
              />
            </div>
          </div>

          <div className="col-auto">
            <div className="form-check">
              <input
                type="checkbox"
                id="mainsFilter"
                className="form-check-input"
                checked={mainsOnly}
                onChange={(e) => setMainsOnly(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="mainsFilter">
                Mains Only
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FilterControls;
