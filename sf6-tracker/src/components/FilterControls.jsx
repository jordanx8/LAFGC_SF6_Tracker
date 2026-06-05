function FilterControls({
  currentMode,
  setCurrentMode,
  currentCharacterFilter,
  setCurrentCharacterFilter,
  characters,
  mainsOnly,
  setMainsOnly,
}) {
  return (
    <div className="card controls-card mb-4">
      <div className="card-body">
        <div className="row g-3 align-items-center justify-content-center">
          <div className="col-auto">
            <label htmlFor="mrModeSelect" className="form-label mb-0">MR Mode:</label>
          </div>
          <div className="col-auto">
            <select 
              id="mrModeSelect" 
              className="form-select form-select-sm"
              value={currentMode}
              onChange={(e) => setCurrentMode(e.target.value)}
            >
              <option value="current">Current MR</option>
              <option value="highest">Highest MR</option>
            </select>
          </div>

          <div className="col-auto">
            <label htmlFor="characterFilter" className="form-label mb-0">Character:</label>
          </div>
          <div className="col-auto">
            <div className="input-group input-group-sm">
              <select 
                id="characterFilter" 
                className="form-select form-select-sm"
                value={currentCharacterFilter}
                onChange={(e) => setCurrentCharacterFilter(e.target.value)}
              >
                <option value="">All Characters</option>
                {characters.map(char => (
                  <option key={char} value={char}>{char}</option>
                ))}
              </select>
              <button 
                id="resetCharacterFilter" 
                className="input-group-text reset-button" 
                title="Reset to All Characters"
                onClick={() => setCurrentCharacterFilter('')}
              >
                <i className="bi bi-arrow-counterclockwise"></i>
              </button>
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

// Made with Bob
