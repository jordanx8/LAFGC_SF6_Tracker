import { useState, useEffect } from 'react';
import { getRankIcon, getLPRankIcon, formatLastUpdated } from '../utils/rankUtils';
import playersData from '../data/players.json';

const PEAK_PHASE_OPTION = 'Peak MR (All Phases)';

function getPhaseEntries(files) {
  return Object.keys(files)
    .map(file => {
      const match = file.match(/phase_(\d+)\.json$/);

      if (!match) {
        return null;
      }

      return {
        file,
        num: Number(match[1]),
        name: `Phase ${match[1]}`
      };
    })
    .filter(Boolean)
    .sort((a, b) => b.num - a.num);
}

async function getPhases() {
    try {
      const files = import.meta.glob('/src/data/phase_*.json');
      const phases = getPhaseEntries(files).map(x => x.name);

      return [PEAK_PHASE_OPTION, ...phases];

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
  const [isPeakPhaseView, setIsPeakPhaseView] = useState(false);

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
      const phaseEntries = getPhaseEntries(files);

      if (currentPhase === PEAK_PHASE_OPTION) {
        const loadedPhases = await Promise.all(
          phaseEntries.map(async ({ file, num, name }) => {
            const module = await files[file]();
            const data = module.default;

            return {
              phaseNum: num,
              phaseName: name,
              data
            };
          })
        );

        loadedPhases.sort((a, b) => b.phaseNum - a.phaseNum);

        const aggregatedPlayers = {};
        const playerNameMap = createPlayerNameMap();

        loadedPhases.forEach(({ phaseName, data }) => {
          Object.entries(data.players).forEach(([playerId, entry]) => {
            const aggregateKey = playerNameMap.get(playerId) || playerId;

            if (!aggregatedPlayers[aggregateKey]) {
              aggregatedPlayers[aggregateKey] = {
                playerId,
                username: playerNameMap.get(playerId) || entry.username,
                platform: entry.platform,
                highest_mr: [],
                current_mr: [],
                lp: [],
                peak_phase_by_character: {},
                peak_lp_by_character: {}
              };
            }

            const aggregatedEntry = aggregatedPlayers[aggregateKey];

            if (!aggregatedEntry.username) {
              aggregatedEntry.username = playerNameMap.get(playerId) || entry.username;
            }

            if (!aggregatedEntry.platform && entry.platform) {
              aggregatedEntry.platform = entry.platform;
            }

            (entry.lp || []).forEach(lpObj => {
              const existingLp = aggregatedEntry.peak_lp_by_character[lpObj.name];
              const existingMr = aggregatedEntry.peak_phase_by_character[lpObj.name];

              if (existingMr) {
                return;
              }

              if (!existingLp || lpObj.lp > existingLp.lp) {
                aggregatedEntry.peak_lp_by_character[lpObj.name] = {
                  lp: lpObj.lp,
                  phase: phaseName,
                  playerId,
                  username: entry.username
                };
              }
            });

            (entry.highest_mr || []).forEach(mrObj => {
              const existing = aggregatedEntry.peak_phase_by_character[mrObj.name];
              if (!existing || mrObj.mr > existing.mr) {
                aggregatedEntry.peak_phase_by_character[mrObj.name] = {
                  mr: mrObj.mr,
                  phase: phaseName,
                  playerId,
                  username: entry.username
                };
              }
            });

            (entry.current_mr || []).forEach(mrObj => {
              const existing = aggregatedEntry.peak_phase_by_character[mrObj.name];
              if (!existing || mrObj.mr > existing.mr) {
                aggregatedEntry.peak_phase_by_character[mrObj.name] = {
                  mr: mrObj.mr,
                  phase: phaseName,
                  playerId,
                  username: entry.username
                };
              }
            });
          });
        });

        Object.values(aggregatedPlayers).forEach(entry => {
          entry.highest_mr = Object.entries(entry.peak_phase_by_character).map(([name, value]) => ({
            name,
            mr: value.mr,
            phase: value.phase,
            playerId: value.playerId,
            username: value.username
          }));
          entry.current_mr = [...entry.highest_mr];
          entry.lp = Object.entries(entry.peak_lp_by_character)
            .filter(([name]) => !entry.peak_phase_by_character[name])
            .map(([name, value]) => ({
              name,
              lp: value.lp,
              phase: value.phase,
              playerId: value.playerId,
              username: value.username
            }));
        });

        setRawData(aggregatedPlayers);
        setIsPeakPhaseView(true);
        setLastUpdated(formatLastUpdated(loadedPhases[0]?.data?.last_updated || ''));
        setTotalPlayers(
          new Set(
            Object.entries(aggregatedPlayers)
          ).size
        );
        return;
      }

      const selectedPhase = phaseEntries.find(phase => phase.name === currentPhase);
      const importer = selectedPhase ? files[selectedPhase.file] : null;

      if (!importer) {
        console.error(`Could not find data for ${currentPhase}`);
        return;
      }

      const module = await importer();
      const data = module.default;

      setRawData(data.players);
      setIsPeakPhaseView(false);
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
      const defaultCfnUsername = entry.username || "Unknown";
      const customName = isPeakPhaseView ? (entry.username || null) : (playerNameMap.get(playerId) || null);
      const platform = entry.platform || null;
      const mrList = entry[mrKey] || [];
      const lpList = entry.lp || [];

      const mrMap = new Map();
      const mrPhaseMap = new Map();
      const mrUsernameMap = new Map();
      const mrPlayerIdMap = new Map();
      for (const mrObj of mrList) {
        mrMap.set(mrObj.name, mrObj.mr);
        if (mrObj.phase) {
          mrPhaseMap.set(mrObj.name, mrObj.phase);
        }
        if (mrObj.username) {
          mrUsernameMap.set(mrObj.name, mrObj.username);
        }
        if (mrObj.playerId) {
          mrPlayerIdMap.set(mrObj.name, mrObj.playerId);
        }
      }

      const fallbackMrMap = new Map();
      const fallbackMrPhaseMap = new Map();
      const fallbackMrUsernameMap = new Map();
      const fallbackMrPlayerIdMap = new Map();
      if (currentMode === "highest") {
        const currentMrList = entry.current_mr || [];
        for (const mrObj of currentMrList) {
          fallbackMrMap.set(mrObj.name, mrObj.mr);
          if (mrObj.phase) {
            fallbackMrPhaseMap.set(mrObj.name, mrObj.phase);
          }
          if (mrObj.username) {
            fallbackMrUsernameMap.set(mrObj.name, mrObj.username);
          }
          if (mrObj.playerId) {
            fallbackMrPlayerIdMap.set(mrObj.name, mrObj.playerId);
          }
        }
      }

      const lpMap = new Map();
      const lpPhaseMap = new Map();
      const lpUsernameMap = new Map();
      const lpPlayerIdMap = new Map();
      for (const lpObj of lpList) {
        lpMap.set(lpObj.name, lpObj.lp);
        if (lpObj.phase) {
          lpPhaseMap.set(lpObj.name, lpObj.phase);
        }
        if (lpObj.username) {
          lpUsernameMap.set(lpObj.name, lpObj.username);
        }
        if (lpObj.playerId) {
          lpPlayerIdMap.set(lpObj.name, lpObj.playerId);
        }
      }

      const characterNames = new Set([
        ...lpList.map(lpObj => lpObj.name),
        ...mrList.map(mrObj => mrObj.name),
        ...(currentMode === "highest" ? (entry.current_mr || []).map(mrObj => mrObj.name) : [])
      ]);

      for (const charName of characterNames) {
        let mr = mrMap.get(charName);
        const lp = lpMap.get(charName);

        let sourcePhase = mrPhaseMap.get(charName) || lpPhaseMap.get(charName) || null;
        let sourceCfnUsername = mrUsernameMap.get(charName) || lpUsernameMap.get(charName) || defaultCfnUsername;
        let sourcePlayerId = mrPlayerIdMap.get(charName) || lpPlayerIdMap.get(charName) || playerId;

        if (mr === undefined && currentMode === "highest") {
          mr = fallbackMrMap.get(charName);
          sourcePhase = fallbackMrPhaseMap.get(charName) || lpPhaseMap.get(charName) || null;
          sourceCfnUsername = fallbackMrUsernameMap.get(charName) || lpUsernameMap.get(charName) || defaultCfnUsername;
          sourcePlayerId = fallbackMrPlayerIdMap.get(charName) || lpPlayerIdMap.get(charName) || playerId;
        }

        if (mr !== undefined) {
          rows.push({
            playerId: sourcePlayerId,
            cfnUsername: sourceCfnUsername,
            customName,
            character: charName,
            mr: mr,
            lp: lp,
            rank: getRankIcon(mr),
            platform: platform,
            hasMR: true,
            sourcePhase: sourcePhase
          });
        } else if (lp !== undefined) {
          rows.push({
            playerId: sourcePlayerId,
            cfnUsername: sourceCfnUsername,
            customName,
            character: charName,
            mr: "N/A",
            lp: lp,
            rank: getLPRankIcon(lp),
            platform: platform,
            hasMR: false,
            sourcePhase: sourcePhase
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
    setCurrentPhase,
    isPeakPhaseView
  };
}
