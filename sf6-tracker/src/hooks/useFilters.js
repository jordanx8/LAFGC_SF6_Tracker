import { useState, useEffect } from 'react';

export function useFilters(allRows) {
  const [filteredRows, setFilteredRows] = useState([]);
  const [currentCharacterFilter, setCurrentCharacterFilter] = useState('');
  const [mainsOnly, setMainsOnly] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Apply filters
  useEffect(() => {
    let filtered = [...allRows];

    if (mainsOnly) {
      const playerMainMap = new Map();
      filtered.forEach(row => {
        // Use custom name if available, otherwise CFN username
        const playerKey = row.customName || row.cfnUsername;
        const existing = playerMainMap.get(playerKey);
        if (!existing) {
          playerMainMap.set(playerKey, row);
        } else {
          const existingValue = existing.hasMR ? existing.mr : existing.lp;
          const currentValue = row.hasMR ? row.mr : row.lp;
          if (existing.hasMR === row.hasMR) {
            if (currentValue > existingValue) {
              playerMainMap.set(playerKey, row);
            }
          } else if (row.hasMR) {
            playerMainMap.set(playerKey, row);
          }
        }
      });
      filtered = Array.from(playerMainMap.values());
    }

    if (currentCharacterFilter) {
      filtered = filtered.filter(r => r.character === currentCharacterFilter);
    }

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(r => {
        // Search in custom name, CFN username, and player ID
        const customNameMatch = r.customName && r.customName.toLowerCase().includes(search);
        const cfnUsernameMatch = r.cfnUsername.toLowerCase().includes(search);
        const playerIdMatch = r.playerId.includes(search);
        return customNameMatch || cfnUsernameMatch || playerIdMatch;
      });
    }

    setFilteredRows(filtered);
  }, [allRows, mainsOnly, currentCharacterFilter, searchTerm]);

  return {
    filteredRows,
    setFilteredRows,
    currentCharacterFilter,
    setCurrentCharacterFilter,
    mainsOnly,
    setMainsOnly,
    searchTerm,
    setSearchTerm
  };
}

// Made with Bob
