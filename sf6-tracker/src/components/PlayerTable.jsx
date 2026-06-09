import { useState } from 'react';
import { characterImageURL } from '../utils/rankUtils';

function PlayerTable({ filteredRows, handleCharacterImageClick, handleSort, setSearchTerm }) {
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  // Calculate pagination
  const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
  const startIndex = (currentPage - 1) * rowsPerPage;
  const endIndex = startIndex + rowsPerPage;
  const currentRows = filteredRows.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  useState(() => {
    setCurrentPage(1);
  }, [filteredRows.length]);

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRowsPerPageChange = (e) => {
    setRowsPerPage(Number(e.target.value));
    setCurrentPage(1);
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;
    
    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        pages.push(currentPage - 1);
        pages.push(currentPage);
        pages.push(currentPage + 1);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    return pages;
  };

  return (
    <>
      <div className="card table-card">
        <div className="card-body p-0">
          <div className="table-responsive">
            <table id="mrTable" className="table table-hover table-dark mb-0">
              <thead className="table-header">
                <tr>
                  <th scope="col" className="text-center">#</th>
                  <th scope="col" onClick={() => handleSort('customName')} style={{cursor: 'pointer'}}>Username</th>
                  <th scope="col" onClick={() => handleSort('platform')} className="text-center" style={{cursor: 'pointer'}}>Platform</th>
                  <th scope="col" onClick={() => handleSort('character')} style={{cursor: 'pointer'}}>Character</th>
                  <th scope="col" onClick={() => handleSort('mr')} className="text-center" style={{cursor: 'pointer'}}>MR</th>
                  <th scope="col" onClick={() => handleSort('rank')} className="text-center" style={{cursor: 'pointer'}}>Rank</th>
                </tr>
              </thead>
              <tbody>
                {currentRows.map((row, index) => (
                  <tr key={`${row.cfnUsername}-${row.character}-${index}`}>
                    <td>{startIndex + index + 1}</td>
                    <td>
                      <div>
                        {row.customName ? (
                          <>
                            <span
                              className="clickable-username"
                              onClick={() => setSearchTerm(row.customName)}
                            >
                              {row.customName}
                            </span>
                            <div className="player-id">
                              CFN: {row.cfnUsername}
                            </div>
                            <div className="player-id">{row.playerId}</div>
                          </>
                        ) : (
                          <>
                            <span
                              className="clickable-username"
                              onClick={() => setSearchTerm(row.cfnUsername)}
                            >
                              {row.cfnUsername}
                            </span>
                            <div className="player-id">ID: {row.playerId}</div>
                          </>
                        )}
                      </div>
                    </td>
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

      {/* Pagination Controls */}
      <div className="card mt-3">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-4 mb-3 mb-md-0">
              <div className="d-flex align-items-center gap-2">
                <label className="form-label mb-0">Rows per page:</label>
                <select
                  className="form-select form-select-sm"
                  style={{width: 'auto'}}
                  value={rowsPerPage}
                  onChange={handleRowsPerPageChange}
                >
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={200}>200</option>
                </select>
              </div>
            </div>
            
            <div className="col-md-4 text-center mb-3 mb-md-0">
              <span style={{color: "white"}}>
                Showing {startIndex + 1}-{Math.min(endIndex, filteredRows.length)} of {filteredRows.length}
              </span>
            </div>

            <div className="col-md-4">
              <nav>
                <ul className="pagination pagination-sm justify-content-center justify-content-md-end mb-0">
                  <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                    <button
                      className="page-link"
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </button>
                  </li>
                  
                  {getPageNumbers().map((page, idx) => (
                    page === '...' ? (
                      <li key={`ellipsis-${idx}`} className="page-item disabled">
                        <span className="page-link">...</span>
                      </li>
                    ) : (
                      <li key={page} className={`page-item ${currentPage === page ? 'active' : ''}`}>
                        <button
                          className="page-link"
                          onClick={() => handlePageChange(page)}
                        >
                          {page}
                        </button>
                      </li>
                    )
                  ))}
                  
                  <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                    <button
                      className="page-link"
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default PlayerTable;

// Made with Bob

