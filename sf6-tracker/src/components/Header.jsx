function Header({ lastUpdated }) {
  return (
    <header className="text-center mb-4">
      <h1 className="display-4 fw-bold mb-2">
        Louisiana SF6 MR Tracker
      </h1>
      <div id="lastUpdated" className="text-muted">{lastUpdated}</div>
    </header>
  );
}

export default Header;

// Made with Bob
