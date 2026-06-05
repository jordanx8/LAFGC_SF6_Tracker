# SF6 Tracker - Architecture Documentation

## Project Structure

```
sf6-tracker/
├── src/
│   ├── components/          # React components
│   │   ├── Header.jsx       # App header with title and last updated
│   │   ├── FilterControls.jsx  # All filter controls (mode, character, checkboxes)
│   │   ├── SearchBox.jsx    # Username search input
│   │   └── PlayerTable.jsx  # Main data table with sortable columns
│   ├── hooks/               # Custom React hooks
│   │   ├── usePlayerData.js # Data loading and processing logic
│   │   └── useFilters.js    # Filtering logic (mains, masters, character, search)
│   ├── utils/               # Utility functions
│   │   └── rankUtils.js     # Character mapping, rank icons, image URLs
│   ├── App.jsx              # Main app component (orchestrates everything)
│   ├── main.jsx             # React entry point
│   ├── styles.css           # Custom styles (midnight theme)
│   └── master_rates.json    # Player data
├── index.html               # HTML template with Bootstrap
└── package.json             # Dependencies
```

## Component Breakdown

### App.jsx (Main Component)
**Purpose:** Orchestrates the entire application
**Responsibilities:**
- Imports and uses custom hooks for data and filtering
- Manages sorting state and logic
- Renders all child components
- Passes props down to children

**State:**
- `sortDirection`: Tracks current sort direction for table columns

**Custom Hooks Used:**
- `usePlayerData`: Handles data loading and mode switching
- `useFilters`: Manages all filtering logic

### Components

#### Header.jsx
**Purpose:** Display app title and last updated timestamp
**Props:**
- `lastUpdated` (string): Formatted timestamp

**Features:**
- Simple presentational component
- No internal state

#### FilterControls.jsx
**Purpose:** All filter controls in one card
**Props:**
- `currentMode`, `setCurrentMode`: MR mode (current/highest)
- `currentCharacterFilter`, `setCurrentCharacterFilter`: Selected character
- `characters`: Array of available characters
- `mainsOnly`, `setMainsOnly`: Mains filter state

**Features:**
- MR mode selector (Current/Highest)
- Character dropdown with reset button
- Mains Only checkbox
- Masters Only checkbox
- Responsive layout (2-column grid on mobile)

#### SearchBox.jsx
**Purpose:** Username search functionality
**Props:**
- `searchTerm`, `setSearchTerm`: Search input state

**Features:**
- Real-time search as you type
- Search icon indicator
- Centered layout

#### PlayerTable.jsx
**Purpose:** Display player data in sortable table
**Props:**
- `filteredRows`: Array of player data to display
- `handleCharacterImageClick`: Function to filter by character
- `handleSort`: Function to sort table columns

**Features:**
- Sortable columns (click headers)
- Character images (clickable to filter)
- Platform icons
- Rank icons
- Responsive design (hides columns on mobile)
- Hover effects

## Custom Hooks

### usePlayerData.js
**Purpose:** Handle data loading and processing based on MR mode
**Parameters:**
- `masterRatesData`: Imported JSON data

**Returns:**
- `allRows`: Processed array of all player/character combinations
- `lastUpdated`: Formatted timestamp
- `currentMode`: Current MR mode (current/highest)
- `setCurrentMode`: Function to change mode

**Logic:**
1. Loads data on mount
2. Processes data based on current mode
3. Creates rows for each player/character combination
4. Assigns MR or LP-based rank icons
5. Sorts rows (MR first, then LP)

### useFilters.js
**Purpose:** Apply all filters to the data
**Parameters:**
- `allRows`: Array of all player data

**Returns:**
- `filteredRows`: Filtered array
- `setFilteredRows`: Direct setter (used for sorting)
- `currentCharacterFilter`, `setCurrentCharacterFilter`
- `mainsOnly`, `setMainsOnly`
- `searchTerm`, `setSearchTerm`

**Logic:**
1. Applies Mains Only filter (one character per player)
2. Applies Masters Only filter (only MR players)
3. Applies character filter
4. Applies username search
5. Updates filtered rows whenever any filter changes

## Utility Functions

### rankUtils.js
**Exports:**
- `toImageName(charName)`: Converts character name to image filename
- `characterImageURL(name)`: Returns full URL for character image
- `getRankIcon(mr)`: Returns rank icon URL for MR value
- `getLPRankIcon(lp)`: Returns rank icon URL for LP value
- `formatLastUpdated(isoTimestamp)`: Formats timestamp for display

**Character Mapping:**
Handles special cases like:
- AKUMA → gouki
- DEE JAY → deejay
- E. HONDA → honda
- A.K.I. → aki
- M. BISON → vega
- C. VIPER → cviper

## Data Flow

```
master_rates.json
    ↓
usePlayerData hook
    ↓
allRows (processed data)
    ↓
useFilters hook
    ↓
filteredRows (filtered data)
    ↓
PlayerTable component
    ↓
Rendered table
```

## State Management

**Global State (via hooks):**
- Player data processing (usePlayerData)
- Filtering logic (useFilters)

**Local State (in App.jsx):**
- Sort direction

**Component State:**
- None (all state lifted to App.jsx or hooks)

## Benefits of This Architecture

1. **Separation of Concerns:**
   - Components handle UI only
   - Hooks handle business logic
   - Utils handle pure functions

2. **Reusability:**
   - Components can be reused in other projects
   - Hooks can be shared across components
   - Utils are pure functions

3. **Testability:**
   - Each component can be tested in isolation
   - Hooks can be tested independently
   - Utils are easy to unit test

4. **Maintainability:**
   - Clear file structure
   - Single responsibility principle
   - Easy to locate and modify code

5. **Performance:**
   - React hooks optimize re-renders
   - Memoization opportunities
   - Efficient filtering logic

## Future Enhancements

Potential improvements:
- Add PropTypes or TypeScript for type safety
- Implement React.memo for performance optimization
- Add loading states and error handling
- Create a context for global state if needed
- Add unit tests for components and hooks
- Implement virtualization for large datasets