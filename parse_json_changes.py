#!/usr/bin/env python3
import json
import subprocess
import sys
import os
from pathlib import Path
import requests
# ------------------------------
# GIT DIFF + JSON PARSING LOGIC
# ------------------------------
def parse_phase_files():
    changes = []
    phase_files = sorted(Path('sf6-tracker/src/data').glob('phase_*.json'))
    for phase_file in phase_files:
        phase_num = phase_file.stem.replace('phase_', '')
        try:
            with open(phase_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            # Get previous version from last commit
            # Convert Path to string with forward slashes for git
            git_path = str(phase_file).replace('\\', '/')
            result = subprocess.run(
                ['git', 'show', f'HEAD~1:{git_path}'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                # File is new
                player_count = len(current_data.get('players', {}))
                changes.append({
                    'phase': phase_num,
                    'type': 'new_file',
                    'player_count': player_count
                })
                continue
            previous_data = json.loads(result.stdout)
            
            # Skip if files are identical
            if current_data == previous_data:
                continue
            current_players = current_data.get('players', {})
            previous_players = previous_data.get('players', {})
            for player_id, player_data in current_players.items():
                username = player_data.get('username', player_id)
                if player_id not in previous_players:
                    changes.append({
                        'phase': phase_num,
                        'type': 'new_player',
                        'player': username,
                        'player_id': player_id
                    })
                    continue
                prev_player = previous_players[player_id]
                # Current MR
                current_mr = {c['name']: c['mr'] for c in player_data.get('current_mr', [])}
                prev_mr = {c['name']: c['mr'] for c in prev_player.get('current_mr', [])}
                for char_name, new_mr in current_mr.items():
                    old_mr = prev_mr.get(char_name, 0)
                    if new_mr != old_mr:
                        changes.append({
                            'phase': phase_num,
                            'type': 'current_mr_change',
                            'player': username,
                            'player_id': player_id,
                            'character': char_name,
                            'old_mr': old_mr,
                            'new_mr': new_mr,
                            'change': new_mr - old_mr
                        })
                # Peak MR
                current_high = {c['name']: c['mr'] for c in player_data.get('highest_mr', [])}
                prev_high = {c['name']: c['mr'] for c in prev_player.get('highest_mr', [])}
                for char_name, new_mr in current_high.items():
                    old_mr = prev_high.get(char_name, 0)
                    if new_mr != old_mr:
                        changes.append({
                            'phase': phase_num,
                            'type': 'highest_mr_change',
                            'player': username,
                            'player_id': player_id,
                            'character': char_name,
                            'old_mr': old_mr,
                            'new_mr': new_mr,
                            'change': new_mr - old_mr
                        })
        except Exception as e:
            print(f"Error processing {phase_file}: {e}", file=sys.stderr)
            continue
    return changes
# ------------------------------
# HUMAN READABLE SUMMARY
# ------------------------------
def format_changes(changes):
    if not changes:
        return "No changes detected.", {}
    output = []
    phases = {}
    for c in changes:
        phases.setdefault(c['phase'], []).append(c)
    for phase in sorted(phases.keys(), key=lambda x: int(x)):
        output.append(f"Phase {phase} Changes:")
        for c in phases[phase]:
            if "mr_change" in c["type"]:
                output.append(
                    f"- {c['player']} ({c['character']}): "
                    f"{c['old_mr']} → {c['new_mr']} ({c['change']:+})"
                )
        output.append("")
    return "\n".join(output), phases
# ------------------------------
# DISCORD EMBED BUILDER
# ------------------------------
def build_single_embed(changes_by_phase):
    """One embed, ordered by NEW MR."""
    lines = []
    for phase, changes in changes_by_phase.items():
        current = [c for c in changes if c["type"] == "current_mr_change"]
        peak =   [c for c in changes if c["type"] == "highest_mr_change"]
        # Sort by new MR (descending)
        current_sorted = sorted(current, key=lambda c: c["new_mr"], reverse=True)
        peak_sorted    = sorted(peak,    key=lambda c: c["new_mr"], reverse=True)
        if current_sorted:
            lines.append(f"**📈 Current MR Changes — Phase {phase}**")
            for c in current_sorted:
                sign = "+" if c["change"] > 0 else ""
                emoji = "🔺" if c["change"] > 0 else "🔻"
                lines.append(
                    f"• **{c['player']} ({c['character']})**: "
                    f"{c['old_mr']:,} → {c['new_mr']:,} "
                    f"({sign}{c['change']:,}) {emoji}"
                )
            lines.append("")
        if peak_sorted:
            lines.append(f"**🏆 Peak MR Changes — Phase {phase}**")
            for c in peak_sorted:
                sign = "+" if c["change"] > 0 else ""
                emoji = "🔺" if c["change"] > 0 else "🔻"
                lines.append(
                    f"• **{c['player']} ({c['character']})**: "
                    f"{c['old_mr']:,} → {c['new_mr']:,} "
                    f"({sign}{c['change']:,}) {emoji}"
                )
            lines.append("")
    description_text = "\n".join(lines)[:4000]
    return {
        "title": "📊 SF6 Tracker Update",
        "description": description_text,
        "color": 0x3498DB
    }
# ------------------------------
# SEND TO DISCORD
# ------------------------------
def send_single_embed(webhook_url, embed):
    payload = {"embeds": [embed]}
    try:
        r = requests.post(webhook_url, json=payload)
        r.raise_for_status()
        print("✓ Sent to Discord")
    except Exception as e:
        print(f"Error sending embed: {e}")
# ------------------------------
# MAIN
# ------------------------------
def main():
    print("Analyzing JSON changes...\n")
    
    # Ensure we have the latest commits
    try:
        subprocess.run(['git', 'fetch', 'origin'], check=False, capture_output=True)
        print("Fetched latest changes from origin", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Could not fetch from origin: {e}", file=sys.stderr)
    
    changes = parse_phase_files()
    summary, phases_grouped = format_changes(changes)
    print(summary)
    # Save summary for GitHub Actions
    with open('json_changes_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    # Discord webhook
    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook and changes:
        print("\nSending update to Discord...")
        embed = build_single_embed(phases_grouped)
        send_single_embed(webhook, embed)
    print(f"\nTotal changes: {len(changes)}")
if __name__ == "__main__":
    main()