function PhaseFilter({
    currentPhase,
    setCurrentPhase,
    phaseList,
  }) {
    return (
        <div className="col-auto">
        <select 
          id="phaseModeSelect" 
          className="form-select form-select-sm"
          value={currentPhase}
          onChange={(e) => setCurrentPhase(e.target.value)}
        >
            {phaseList.map((phase) => (
            <option key={phase} value={phase}>
                {phase}
            </option>
            ))}
        </select>
      </div>
    );
}

export default PhaseFilter;