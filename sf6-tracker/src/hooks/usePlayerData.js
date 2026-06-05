import { useState, useEffect } from 'react';
import { getRankIcon, getLPRankIcon, formatLastUpdated } from '../utils/rankUtils';

export function usePlayerData(masterRatesData) {
  const [rawData, setRawData] = useState(null);
  const [allRows, setAllRows] = useState([]);
  const [lastUpdated, setLastUpdated] = useState('');
  const [currentMode, setCurrentMode] = useState('highest');

  // Load data on mount
  useEffect(() => {
    const data = masterRatesData;
    if (data.last_updated && data.players) {
      setRawData(data.players);
      setLastUpdated(formatLastUpdated(data.last_updated));
    } else {
      setRawData(data);
    }
  }, [masterRatesData]);

  // Build rows from mode
  useEffect(() => {
    if (!rawData) return;

    const rows = [];
    const mrKey = currentMode === "current" ? "current_mr" : "highest_mr";

    for (const playerId in rawData) {
      const entry = rawData[playerId];
      const username = entry.username || "Unknown";
      const platform = entry.platform || null;
      const mrList = entry[mrKey] || [];
      const lpList = entry.lp || [];

      const mrMap = new Map();
      for (const mrObj of mrList) {
        mrMap.set(mrObj.name, mrObj.mr);
      }

      const fallbackMrMap = new Map();
      if (currentMode === "highest") {
        const currentMrList = entry.current_mr || [];
        for (const mrObj of currentMrList) {
          fallbackMrMap.set(mrObj.name, mrObj.mr);
        }
      }

      const lpMap = new Map();
      for (const lpObj of lpList) {
        lpMap.set(lpObj.name, lpObj.lp);
      }

      for (const lpObj of lpList) {
        const charName = lpObj.name;
        let mr = mrMap.get(charName);
        const lp = lpObj.lp;

        if (mr === undefined && currentMode === "highest") {
          mr = fallbackMrMap.get(charName);
        }

        if (mr !== undefined) {
          rows.push({
            username,
            character: charName,
            mr: mr,
            lp: lp,
            rank: getRankIcon(mr),
            platform: platform,
            hasMR: true
          });
        } else {
          rows.push({
            username,
            character: charName,
            mr: "N/A",
            lp: lp,
            rank: getLPRankIcon(lp),
            platform: platform,
            hasMR: false
          });
        }
      }
    }

    rows.sort((a, b) => {
      if (a.hasMR && b.hasMR) {
        return b.mr - a.mr;
      } else if (a.hasMR && !b.hasMR) {
        return -1;
      } else if (!a.hasMR && b.hasMR) {
        return 1;
      } else {
        return b.lp - a.lp;
      }
    });

    setAllRows(rows);
  }, [rawData, currentMode]);

  return {
    allRows,
    lastUpdated,
    currentMode,
    setCurrentMode
  };
}

// Made with Bob
