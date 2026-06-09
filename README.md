# LAFGC Street Fighter 6 CFN Tracker

A web application that tracks Street Fighter 6 player statistics from the Capcom Fighters Network (CFN) for Louisiana's playerbase. Automatically scrapes and displays League Points (LP) and Master Rate (MR) data across all competitive phases.

## Features

- Track LP and MR for all characters across multiple players
- View historical data from all competitive phases (Phase 1-12)
- Filter by character, search by name, or view mains only
- Automated updates every 12 hours via GitHub Actions

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Chrome/ChromeDriver (for scraping)

### Installation

```bash
# Clone and install dependencies
git clone https://github.com/yourusername/CFN_Scraper.git
cd CFN_Scraper
pip install -r requirements.txt

# Run frontend
cd sf6-tracker
npm install
npm run dev
```

## Adding Players to the Tracker

### Step 1: Find Your CFN Player ID

1. Go to [Street Fighter 6 Buckler](https://www.streetfighter.com/6/buckler/)
2. Search for your Fighter ID
3. Click your profile and look at the URL: `https://www.streetfighter.com/6/buckler/profile/1234567890/play`
4. Your Player ID is the number after `/profile/` (e.g., `1234567890`)

### Step 2: Edit players.json

Open `sf6-tracker/src/data/players.json` and add your entry:

**Single account:**
```json
{"name": "YourName", "id": "1234567890"}
```

**Multiple accounts:**
```json
{"name": "YourName", "id": ["1234567890", "0987654321"]}
```

**Complete example:**
```json
[
    {"name": "FroggyAirplane", "id": "4000629934"},
    {"name": "ReTr0", "id": "4092075827"},
    {"name": "YourName", "id": "1234567890"}
]
```
### Step 3: Submit Changes

**Option A: Pull Request**
```bash
git checkout -b add-player-yourname
# Edit players.json
git commit -m "Add player: YourName"
git push origin add-player-yourname
# Open PR on GitHub
```

**Option B: Open an Issue**
- Create a GitHub issue with your Player ID and display name
- A maintainer will add you

## Manual Scraping

### Setup Authentication
```bash
export CAPCOM_USERNAME="your_email@example.com"
export CAPCOM_PASSWORD="your_password"
python refresh_cookies.py
```

### Scraping Commands
```bash
# Scrape all players (latest phase)
python scrape_cfn.py

# Scrape specific players
python scrape_cfn.py 1234567890,0987654321

# Scrape specific phase
python scrape_cfn.py --phase 11

# Scrape all phases
python scrape_cfn.py --phase all
```

## GitHub Actions Setup

Add these secrets to your repository (Settings → Secrets):

- `SESSION_COOKIES` - CFN session cookies (JSON)
- `CAPCOM_USERNAME` - Your Capcom ID email
- `CAPCOM_PASSWORD` - Your Capcom ID password
- `GH_TOKEN` - GitHub token with `repo` and `workflow` permissions

## Tech Stack

- **Frontend:** React 19, Vite
- **Scraping:** Python, Selenium, ChromeDriver
- **Automation:** GitHub Actions

## Project Structure

```
CFN_Scraper/
├── sf6-tracker/              # React frontend
│   └── src/data/
│       ├── players.json      # Player IDs (edit this!)
│       └── phase_*.json      # Scraped data
├── scrape_cfn.py            # Main scraper
├── refresh_cookies.py       # Auth helper
└── .github/workflows/       # Automation
```

## Contact

**Issues?** Contact [@FroggyAirplane](https://discord.com/users/FroggyAirplane)

**Louisiana FGC:**
- [Discord](https://discord.gg/MeXsRzt5R)
- [Twitter](https://x.com/LAFGCTV)
- [YouTube](https://youtube.com/@lafgctv2096)
