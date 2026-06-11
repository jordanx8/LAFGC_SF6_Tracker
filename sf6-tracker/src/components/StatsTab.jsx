import { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

// Map rank numbers to rank names
const getRankName = (rankUrl) => {
  const rankMatch = rankUrl.match(/rank(\d+)_s\.png/);
  if (!rankMatch) return 'Unknown';
  
  const rankNum = parseInt(rankMatch[1]);
  
  if (rankNum >= 3 && rankNum <= 5) return 'Rookie';
  if (rankNum >= 6 && rankNum <= 10) return 'Iron';
  // Bronze: rank4-8
  if (rankNum >= 11 && rankNum <= 15) return 'Bronze';
  // Silver: rank9-13
  if (rankNum >= 16 && rankNum <= 20) return 'Silver';
  // Gold: rank14-18
  if (rankNum >= 21 && rankNum <= 25) return 'Gold';
  // Platinum: rank19-23
  if (rankNum >= 26 && rankNum <= 30) return 'Platinum';
  // Diamond: rank24-35
  if (rankNum >= 31 && rankNum <= 35) return 'Diamond';
  // Master: rank36-39
  if (rankNum == 36) return 'Master';
  if (rankNum == 40) return 'High Master';
  if (rankNum == 41) return 'Grand Master';
  if (rankNum == 42) return 'Ultimate Master';
  
  return 'Unknown';
};

function StatsTab({ filteredRows }) {
  // Calculate character usage statistics
  const characterStats = useMemo(() => {
    const charCount = {};
    
    filteredRows.forEach(row => {
      charCount[row.character] = (charCount[row.character] || 0) + 1;
    });
    
    return Object.entries(charCount)
      .map(([character, count]) => ({ character, count }))
      .sort((a, b) => b.count - a.count);
  }, [filteredRows]);

  // Calculate rank distribution statistics
  const rankStats = useMemo(() => {
    const rankCount = {};
    
    filteredRows.forEach(row => {
      const rankName = getRankName(row.rank);
      rankCount[rankName] = (rankCount[rankName] || 0) + 1;
    });
    
    // Define rank order for proper sorting
    const rankOrder = ['Rookie', 'Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'High Master', 'Grand Master', 'Ultimate Master'];
    
    return rankOrder
      .filter(rank => rankCount[rank])
      .map(rank => ({ rank, count: rankCount[rank] }));
  }, [filteredRows]);

  // Calculate average MR per character
  const averageMRStats = useMemo(() => {
    const charData = {};
    
    filteredRows.forEach(row => {
      // Only include rows that have MR (not "N/A")
      if (row.hasMR && typeof row.mr === 'number') {
        if (!charData[row.character]) {
          charData[row.character] = { total: 0, count: 0 };
        }
        charData[row.character].total += row.mr;
        charData[row.character].count += 1;
      }
    });
    
    const stats = Object.entries(charData)
      .map(([character, data]) => ({
        character,
        averageMR: Math.round(data.total / data.count),
        playerCount: data.count
      }))
      .sort((a, b) => b.averageMR - a.averageMR);
    
    // Calculate Y-axis domain to better show differences
    const mrValues = stats.map(s => s.averageMR);
    const maxMR = Math.max(...mrValues);
    const range = maxMR - 1400;
    const yMin = 1400;
    const yMax = Math.ceil(maxMR + range * 0.1);
    
    return { stats, yMin, yMax };
  }, [filteredRows]);

  // Color palette for bars
  const characterColors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
    '#E63946', '#A8DADC', '#457B9D', '#F1FAEE', '#E76F51',
    '#2A9D8F', '#E9C46A', '#F4A261', '#E76F51', '#264653'
  ];

  const rankColors = {
    'Rookie': '#ffffff',
    'Iron': '#5b5b5b',
    'Bronze': '#CD7F32',
    'Silver': '#C0C0C0',
    'Gold': '#FFD700',
    'Platinum': '#E5E4E2',
    'Diamond': '#9370DB',
    'Master': '#20a888',
    'High Master': '#bcbcbd',
    'Grand Master': '#dcff43',
    'Ultimate Master': '#FF1493'
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{`${payload[0].payload.character || payload[0].payload.rank}: ${payload[0].value}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="stats-container">
      <div className="stats-grid">
        {/* Character Usage Chart */}
        <div className="card stats-card">
          <div className="card-body">
            <h3 className="stats-title">Most Played Characters</h3>
            <p className="stats-subtitle">Total entries: {filteredRows.length}</p>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={characterStats} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis
                  dataKey="character"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  stroke="#fff"
                  tick={{ fill: '#fff' }}
                />
                <YAxis stroke="#fff" tick={{ fill: '#fff' }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Players" radius={[8, 8, 0, 0]}>
                  {characterStats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={characterColors[index % characterColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Rank Distribution Chart */}
        <div className="card stats-card">
          <div className="card-body">
            <h3 className="stats-title">Players Per Rank</h3>
            <p className="stats-subtitle">Total entries: {filteredRows.length}</p>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={rankStats} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis
                  dataKey="rank"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  stroke="#fff"
                  tick={{ fill: '#fff' }}
                />
                <YAxis stroke="#fff" tick={{ fill: '#fff' }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Players" radius={[8, 8, 0, 0]}>
                  {rankStats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={rankColors[entry.rank] || '#888'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Average MR per Character Chart */}
        <div className="card stats-card">
          <div className="card-body">
            <h3 className="stats-title">Average Master Rating by Character</h3>
            <p className="stats-subtitle">Only includes players with MR data</p>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={averageMRStats.stats} margin={{ top: 20, right: 30, left: 50, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis
                  dataKey="character"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  stroke="#fff"
                  tick={{ fill: '#fff' }}
                />
                <YAxis
                  stroke="#fff"
                  tick={{ fill: '#fff' }}
                  domain={[1400, 1850]}
                  ticks={[1400, 1500, 1600, 1700, 1800]}
                  interval={0}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="custom-tooltip">
                          <p className="label">{`${payload[0].payload.character}`}</p>
                          <p className="label">{`Avg MR: ${payload[0].value}`}</p>
                          <p className="label">{`Players: ${payload[0].payload.playerCount}`}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="averageMR" name="Average MR" radius={[8, 8, 0, 0]} barSize={40}>
                  {averageMRStats.stats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={characterColors[index % characterColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StatsTab;

// Made with Bob
