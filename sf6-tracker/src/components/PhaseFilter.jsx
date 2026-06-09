import React from 'react';
import Select from 'react-select';

function PhaseFilter({
    currentPhase,
    setCurrentPhase,
    phaseList,
  }) {
    const phaseOptions = phaseList.map(phase => ({
      value: phase,
      label: phase
    }));

    const selectedOption = phaseOptions.find(option => option.value === currentPhase);

    return (
        <div className="col-auto">
        <Select
          options={phaseOptions}
          value={selectedOption}
          onChange={(selected) => setCurrentPhase(selected.value)}
          classNamePrefix="rs"
          className="react-select-bootstrap"
          isSearchable={false}
        />
      </div>
    );
}

export default PhaseFilter;