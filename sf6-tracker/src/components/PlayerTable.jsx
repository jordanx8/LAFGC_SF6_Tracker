import { characterImageURL } from '../utils/rankUtils';

function PlayerTable({ filteredRows, handleCharacterImageClick, handleSort }) {
  return (
    <div className="card table-card">
      <div className="card-body p-0">
        <div className="table-responsive">
          <table id="mrTable" className="table table-hover table-dark mb-0">
            <thead className="table-header">
              <tr>
                <th scope="col" className="text-center">#</th>
                <th scope="col" onClick={() => handleSort('username')} style={{cursor: 'pointer'}}>Username</th>
                <th scope="col" onClick={() => handleSort('platform')} className="text-center" style={{cursor: 'pointer'}}>Platform</th>
                <th scope="col" onClick={() => handleSort('character')} style={{cursor: 'pointer'}}>Character</th>
                <th scope="col" onClick={() => handleSort('mr')} className="text-center" style={{cursor: 'pointer'}}>MR</th>
                <th scope="col" onClick={() => handleSort('rank')} className="text-center" style={{cursor: 'pointer'}}>Rank</th>
              </tr>
            </thead>
            <tbody>
              {filteredRows.map((row, index) => (
                <tr key={`${row.username}-${row.character}-${index}`}>
                  <td>{index + 1}</td>
                  <td>{row.username}</td>
                  <td>
                    {row.platform && (
                      <img 
                        className="platform-icon" 
                        src={row.platform} 
                        alt="Platform"
                        onError={(e) => e.target.style.display = 'none'}
                      />
                    )}
                  </td>
                  <td>
                    <img 
                      className="char-img clickable-char-img" 
                      src={characterImageURL(row.character)}
                      alt={row.character}
                      onClick={() => handleCharacterImageClick(row.character)}
                      onError={(e) => e.target.style.display = 'none'}
                    />
                    {row.character}
                  </td>
                  <td>{row.mr}</td>
                  <td>
                    <img className="rank-icon" src={row.rank} alt="Rank" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default PlayerTable;

// Made with Bob
