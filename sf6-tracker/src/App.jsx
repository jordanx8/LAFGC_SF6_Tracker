import { useState } from 'react';
import './styles.css';
import masterRatesData from './master_rates.json';
import Header from './components/Header';
import FilterControls from './components/FilterControls';
import SearchBox from './components/SearchBox';
import PlayerTable from './components/PlayerTable';
import { usePlayerData } from './hooks/usePlayerData';
import { useFilters } from './hooks/useFilters';

function App() {
  const [sortDirection, setSortDirection] = useState(1);

  // Custom hooks for data and filtering
  const { allRows, lastUpdated, currentMode, setCurrentMode } = usePlayerData(masterRatesData);
  const {
    filteredRows,
    setFilteredRows,
    currentCharacterFilter,
    setCurrentCharacterFilter,
    mainsOnly,
    setMainsOnly,
    searchTerm,
    setSearchTerm
  } = useFilters(allRows);

  // Get unique characters for dropdown
  const characters = [...new Set(allRows.map(row => row.character))].sort();

  const handleCharacterImageClick = (character) => {
    setCurrentCharacterFilter(character);
  };

  const handleSort = (key) => {
    const newDirection = sortDirection * -1;
    setSortDirection(newDirection);
    
    const sorted = [...filteredRows].sort((a, b) => {
      if (key === "mr") {
        const aVal = a.hasMR ? a.mr : (a.lp || 0);
        const bVal = b.hasMR ? b.mr : (b.lp || 0);
        if (a.hasMR === b.hasMR) {
          return (aVal - bVal) * newDirection;
        }
        if (newDirection > 0) {
          return a.hasMR ? 1 : -1;
        } else {
          return a.hasMR ? -1 : 1;
        }
      }
      if (key === "rank") return 0;
      if (key === "platform") return ((a.platform || "").localeCompare(b.platform || "")) * newDirection;
      return a[key].localeCompare(b[key]) * newDirection;
    });
    
    setFilteredRows(sorted);
  };

  return (
    <div className="container-fluid py-4">
      <Header lastUpdated={lastUpdated} />

      <FilterControls
        currentMode={currentMode}
        setCurrentMode={setCurrentMode}
        currentCharacterFilter={currentCharacterFilter}
        setCurrentCharacterFilter={setCurrentCharacterFilter}
        characters={characters}
        mainsOnly={mainsOnly}
        setMainsOnly={setMainsOnly}
      />

      <SearchBox searchTerm={searchTerm} setSearchTerm={setSearchTerm} />

      <PlayerTable
        filteredRows={filteredRows}
        handleCharacterImageClick={handleCharacterImageClick}
        handleSort={handleSort}
        setSearchTerm={setSearchTerm}
      />
    </div>
  );
}

export default App;
