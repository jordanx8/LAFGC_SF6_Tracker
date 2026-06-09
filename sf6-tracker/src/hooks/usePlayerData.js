import { useState, useEffect } from 'react';
import { getRankIcon, getLPRankIcon, formatLastUpdated } from '../utils/rankUtils';
import playersData from '../data/players.json';

async function getPhases() {
    try {
      const files = import.meta.glob('/src/data/phase_*.json');

      return Object.keys(files)
        .map(file => {
          const match = file.match(/phase_(\d+)\.json$/);
          return {
            num: Number(match[1]),
            name: `Phase ${match[1]}`
          };
        })
        .sort((a, b) => b.num - a.num)
        .map(x => x.name);

    } catch (err) {
        console.error('Error reading directory:', err);
        return [];
    }
}

// Create a mapping of player IDs to custom names
function createPlayerNameMap() {
  const nameMap = new Map();
  
  for (const player of playersData) {
    const customName = player.name;
    const playerId = player.id;
    
    // Handle both single ID and array of IDs
    if (Array.isArray(playerId)) {
      for (const pid of playerId) {
        nameMap.set(pid, customName);
      }
    } else {
      nameMap.set(playerId, customName);
    }
  }
  
  return nameMap;
}

export function usePlayerData() {
  const [rawData, setRawData] = useState(null);
  const [allRows, setAllRows] = useState([]);
  const [lastUpdated, setLastUpdated] = useState('');
  const [totalPlayers, setTotalPlayers] = useState(0);
  const [currentMode, setCurrentMode] = useState('highest');
  const [currentPhase, setCurrentPhase] = useState('');
  const [phaseList, setPhaseList] = useState([]);

  // Load data on mount
  // Load available phases once
  useEffect(() => {
    async function loadPhases() {
      const phases = await getPhases();

      setPhaseList(phases);

      if (phases.length > 0) {
        setCurrentPhase(phases[0]);
      }
    }

    loadPhases();
  }, []);

  // Load data whenever currentPhase changes
  useEffect(() => {
    async function loadData() {
      if (!currentPhase) return;

      const files = import.meta.glob('/src/data/phase_*.json');

      const phaseFile =
        `/src/data/${currentPhase.toLowerCase().replace(/\s+/g, "_")}.json`;

      console.log("Loading:", phaseFile);
      console.log(Object.keys(files));

      const importer = files[phaseFile];

      if (!importer) {
        console.error(`Could not find ${phaseFile}`);
        return;
      }

      const module = await importer();
      const data = module.default;

      setRawData(data.players);
      setLastUpdated(formatLastUpdated(data.last_updated));
      setTotalPlayers(
        new Set(
          Object.values(data.players)
            .filter(player => player.lp && player.lp.length > 0)
            .map(player => player.username)
        ).size
      );
    }

    loadData();
  }, [currentPhase]);

  // Build rows from mode
  useEffect(() => {
    if (!rawData) return;

    const rows = [];
    const mrKey = currentMode === "current" ? "current_mr" : "highest_mr";
    const playerNameMap = createPlayerNameMap();

    for (const playerId in rawData) {
      const entry = rawData[playerId];
      const cfnUsername = entry.username || "Unknown";
      const customName = playerNameMap.get(playerId) || null;
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
            playerId,
            cfnUsername,
            customName,
            character: charName,
            mr: mr,
            lp: lp,
            rank: getRankIcon(mr),
            platform: platform,
            hasMR: true
          });
        } else {
          rows.push({
            playerId,
            cfnUsername,
            customName,
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
  }, [rawData, currentMode, currentPhase]);

  return {
    allRows,
    lastUpdated,
    totalPlayers,
    currentMode,
    setCurrentMode,
    phaseList,
    currentPhase,
    setCurrentPhase
  };
}

// Made with Bob
