# Street Fighter 6 MR Tracker - React App

This is a React conversion of the Louisiana SF6 MR Tracker application.

## Features

- View current or highest Master Rating (MR) for players
- Filter by character
- Filter to show only mains (highest MR/LP per player)
- Filter to show only Masters rank players
- Search by username
- Sortable columns
- Responsive design with mobile support

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm

### Installation

1. Navigate to the project directory:
```bash
cd sf6-tracker
```

2. Install dependencies (already done):
```bash
npm install
```

### Running the Application

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173/`

### Building for Production

To create a production build:
```bash
npm run build
```

The built files will be in the `dist` folder.

To preview the production build:
```bash
npm run preview
```

## Updating Player Data

To update the player data:

1. Run your Python script (`main.py`) in the parent directory to generate a new `master_rates.json`
2. Copy the updated `master_rates.json` to `sf6-tracker/src/master_rates.json`
3. Rebuild the app with `npm run build` (for production) or the dev server will auto-reload

## Project Structure

```
sf6-tracker/
├── src/
│   ├── App.jsx           # Main application component
│   ├── styles.css        # Custom styles (midnight theme)
│   ├── master_rates.json # Player data
│   └── main.jsx          # React entry point
├── index.html            # HTML template with Bootstrap
├── package.json          # Dependencies
└── vite.config.js        # Vite configuration
```

## Technologies Used

- **React** - UI framework
- **Vite** - Build tool and dev server
- **Bootstrap 5** - CSS framework
- **Bootstrap Icons** - Icon library

## Original HTML Version

The original HTML version is still available in the parent directory (`index.html` and `styles.css`).
