#!/usr/bin/env python3
"""
Parse JSON changes from git diff and create a human-readable summary.
Focuses on MR (Master Rate) changes for players and characters.
"""
import json
import subprocess
import sys
from pathlib import Path

def get_json_diff():
    """Get the git diff for phase JSON files"""
    try:
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', '--', 'sf6-tracker/src/data/phase_*.json'],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout
    except Exception as e:
        print(f"Error getting git diff: {e}")
        return ""

def parse_phase_files():
    """Parse current phase files and compare with previous commit"""
    changes = []
    
    # Get list of phase files
    phase_files = sorted(Path('sf6-tracker/src/data').glob('phase_*.json'))
    
    for phase_file in phase_files:
        phase_num = phase_file.stem.replace('phase_', '')
        
        try:
            # Get current version
            with open(phase_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            # Get previous version
            result = subprocess.run(
                ['git', 'show', f'HEAD~1:{phase_file}'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                # File didn't exist in previous commit
                player_count = len(current_data.get('players', {}))
                changes.append({
                    'phase': phase_num,
                    'type': 'new_file',
                    'player_count': player_count
                })
                continue
            
            previous_data = json.loads(result.stdout)
            
            # Compare players
            current_players = current_data.get('players', {})
            previous_players = previous_data.get('players', {})
            
            for player_id, player_data in current_players.items():
                username = player_data.get('username', player_id)
                
                # Check if player is new
                if player_id not in previous_players:
                    changes.append({
                        'phase': phase_num,
                        'type': 'new_player',
                        'player': username,
                        'player_id': player_id
                    })
                    continue
                
                prev_player = previous_players[player_id]
                
                # Check for MR changes (current_mr)
                current_mr = {char['name']: char['mr'] for char in player_data.get('current_mr', [])}
                prev_mr = {char['name']: char['mr'] for char in prev_player.get('current_mr', [])}
                
                for char_name, mr_value in current_mr.items():
                    prev_value = prev_mr.get(char_name, 0)
                    if mr_value != prev_value:
                        changes.append({
                            'phase': phase_num,
                            'type': 'current_mr_change',
                            'player': username,
                            'player_id': player_id,
                            'character': char_name,
                            'old_mr': prev_value,
                            'new_mr': mr_value,
                            'change': mr_value - prev_value
                        })
                
                # Check for highest MR changes
                current_highest = {char['name']: char['mr'] for char in player_data.get('highest_mr', [])}
                prev_highest = {char['name']: char['mr'] for char in prev_player.get('highest_mr', [])}
                
                for char_name, mr_value in current_highest.items():
                    prev_value = prev_highest.get(char_name, 0)
                    if mr_value != prev_value:
                        changes.append({
                            'phase': phase_num,
                            'type': 'highest_mr_change',
                            'player': username,
                            'player_id': player_id,
                            'character': char_name,
                            'old_mr': prev_value,
                            'new_mr': mr_value,
                            'change': mr_value - prev_value
                        })
                
        
        except Exception as e:
            print(f"Error processing {phase_file}: {e}", file=sys.stderr)
            continue
    
    return changes

def format_changes(changes):
    """Format changes into a readable summary"""
    if not changes:
        return "No changes detected."
    
    output = []
    output.append("# 📊 SF6 Tracker Changes Summary\n")
    
    # Group by phase
    phases = {}
    for change in changes:
        phase = change['phase']
        if phase not in phases:
            phases[phase] = []
        phases[phase].append(change)
    
    for phase in sorted(phases.keys(), key=lambda x: int(x)):
        phase_changes = phases[phase]
        output.append(f"## 🎮 Phase {phase}\n")
        
        # Group by type
        new_files = [c for c in phase_changes if c['type'] == 'new_file']
        new_players = [c for c in phase_changes if c['type'] == 'new_player']
        current_mr_changes = [c for c in phase_changes if c['type'] == 'current_mr_change']
        highest_mr_changes = [c for c in phase_changes if c['type'] == 'highest_mr_change']
        
        if new_files:
            output.append(f"### 📄 New Phase File")
            output.append(f"- Created with **{new_files[0]['player_count']} players**\n")
        
        if new_players:
            output.append(f"### 👤 New Players ({len(new_players)})")
            for change in new_players[:5]:  # Show first 5
                output.append(f"- {change['player']}")
            if len(new_players) > 5:
                output.append(f"- *...and {len(new_players) - 5} more*")
            output.append("")
        
        # Current MR Changes
        if current_mr_changes:
            output.append(f"### 📈 Current MR Changes ({len(current_mr_changes)})")
            
            # Group by player
            by_player = {}
            for change in current_mr_changes:
                player = change['player']
                if player not in by_player:
                    by_player[player] = []
                by_player[player].append(change)
            
            for player, player_changes in sorted(by_player.items()):
                output.append(f"\n**{player}**")
                for change in player_changes:
                    sign = "+" if change['change'] > 0 else ""
                    emoji = "🔺" if change['change'] > 0 else "🔻"
                    output.append(
                        f"- {emoji} **{change['character']}**: "
                        f"{change['old_mr']:,} → {change['new_mr']:,} "
                        f"({sign}{change['change']:,})"
                    )
            output.append("")
        
        # Highest MR Changes
        if highest_mr_changes:
            output.append(f"### 🏆 Peak MR Changes ({len(highest_mr_changes)})")
            
            # Group by player
            by_player = {}
            for change in highest_mr_changes:
                player = change['player']
                if player not in by_player:
                    by_player[player] = []
                by_player[player].append(change)
            
            for player, player_changes in sorted(by_player.items()):
                output.append(f"\n**{player}**")
                for change in player_changes:
                    sign = "+" if change['change'] > 0 else ""
                    emoji = "🔺" if change['change'] > 0 else "🔻"
                    output.append(
                        f"- {emoji} **{change['character']}**: "
                        f"{change['old_mr']:,} → {change['new_mr']:,} "
                        f"({sign}{change['change']:,})"
                    )
            output.append("")
        
        output.append("---\n")
    
    return "\n".join(output)

def main():
    """Main function"""
    print("Analyzing JSON changes...\n")
    
    changes = parse_phase_files()
    summary = format_changes(changes)
    
    print(summary)
    
    # Write to file for GitHub Actions
    with open('json_changes_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n\nTotal changes: {len(changes)}")

if __name__ == '__main__':
    main()

# Made with Bob
