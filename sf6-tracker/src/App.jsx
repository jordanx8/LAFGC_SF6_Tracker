import { useState } from 'react';
import './styles.css';
import Header from './components/Header';
import FilterControls from './components/FilterControls';
import SearchBox from './components/SearchBox';
import PlayerTable from './components/PlayerTable';
import ScrollToTop from './components/ScrollToTop';
import { usePlayerData } from './hooks/usePlayerData';
import { useFilters } from './hooks/useFilters';

function App() {
  const [sortDirection, setSortDirection] = useState(1);

  // Custom hooks for data and filtering
  const { allRows, lastUpdated, totalPlayers, currentMode, setCurrentMode, phaseList, currentPhase, setCurrentPhase } = usePlayerData();
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
      if (key === "customName") {
        // Sort by custom name if available, otherwise by CFN username
        const aName = a.customName || a.cfnUsername;
        const bName = b.customName || b.cfnUsername;
        return aName.localeCompare(bName) * newDirection;
      }
      return a[key].localeCompare(b[key]) * newDirection;
    });
    
    setFilteredRows(sorted);
  };

  return (
    <div className="container-fluid py-4">
      <Header lastUpdated={lastUpdated} totalPlayers={totalPlayers} />

      <FilterControls
        currentMode={currentMode}
        setCurrentMode={setCurrentMode}
        currentCharacterFilter={currentCharacterFilter}
        setCurrentCharacterFilter={setCurrentCharacterFilter}
        characters={characters}
        mainsOnly={mainsOnly}
        setMainsOnly={setMainsOnly}
        phaseList={phaseList}
        setCurrentPhase={setCurrentPhase}
        currentPhase={currentPhase}
      />
      {parseInt(currentPhase.replace("Phase ", ""), 10) >= 11 ? <></> : <div className='player-id unavailable'>*Highest MR data unavailable pre-Phase 11</div>}

      <SearchBox searchTerm={searchTerm} setSearchTerm={setSearchTerm} />

      <PlayerTable
        filteredRows={filteredRows}
        handleCharacterImageClick={handleCharacterImageClick}
        handleSort={handleSort}
        setSearchTerm={setSearchTerm}
      />

      <footer className="footer mt-5">
        <div className="footer-content">
          <p className="footer-text footer-community">
            <span className="footer-community-name">Louisiana FGC Community</span>
          </p>
          <div className="footer-links">
            <a href="https://discord.gg/MeXsRzt5R" target="_blank" rel="noopener noreferrer" className="footer-link" aria-label="LAFGC Discord">
              <i className="bi bi-discord"></i>
            </a>
            <a href="https://x.com/LAFGCTV" target="_blank" rel="noopener noreferrer" className="footer-link" aria-label="LAFGC X (Twitter)">
              <i className="bi bi-twitter-x"></i>
            </a>
            <a href="https://youtube.com/@lafgctv2096" target="_blank" rel="noopener noreferrer" className="footer-link" aria-label="LAFGC YouTube">
              <i className="bi bi-youtube"></i>
            </a>
          </div>
          
          <div className="footer-divider"></div>
          
          <p className="footer-text">
            Issues? Contact <span className="footer-handle">@FroggyAirplane</span>
          </p>
          <div className="footer-links">
            <a href="https://discord.com/users/FroggyAirplane" target="_blank" rel="noopener noreferrer" className="footer-link" aria-label="Discord">
              <i className="bi bi-discord"></i>
            </a>
            <a href="https://x.com/FroggyAirplane" target="_blank" rel="noopener noreferrer" className="footer-link" aria-label="X (Twitter)">
              <i className="bi bi-twitter-x"></i>
            </a>
            <a href="https://youtube.com/@froggyairplane" target="_blank" rel="noopener noreferrer" className="footer-link" aria-label="LAFGC YouTube">
              <i className="bi bi-youtube"></i>
            </a>
          </div>
        </div>
      </footer>

      <ScrollToTop />
    </div>
  );
}

export default App;
