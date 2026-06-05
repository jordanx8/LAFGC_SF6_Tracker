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
        const existing = playerMainMap.get(row.username);
        if (!existing) {
          playerMainMap.set(row.username, row);
        } else {
          const existingValue = existing.hasMR ? existing.mr : existing.lp;
          const currentValue = row.hasMR ? row.mr : row.lp;
          if (existing.hasMR === row.hasMR) {
            if (currentValue > existingValue) {
              playerMainMap.set(row.username, row);
            }
          } else if (row.hasMR) {
            playerMainMap.set(row.username, row);
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
      filtered = filtered.filter(r => r.username.toLowerCase().includes(search));
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
