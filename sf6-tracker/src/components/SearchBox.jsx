function SearchBox({ searchTerm, setSearchTerm }) {
  return (
    <div className="row justify-content-center mb-4">
      <div className="col-md-6 col-lg-4">
        <div className="input-group">
          <span className="input-group-text bg-transparent border-accent">
            <i className="bi bi-search"></i>
          </span>
          <input 
            type="text" 
            id="searchBox" 
            className="form-control" 
            placeholder="Search by username..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}

export default SearchBox;

// Made with Bob
