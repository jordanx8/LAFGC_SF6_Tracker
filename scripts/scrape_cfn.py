import time
import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Use environment variable if available, otherwise use default Windows path
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', r"C:\WebDriver\chromedriver.exe")

# Change-detection settings (see wait_for_data_refresh below).
# The play page shows a single loader element while it fetches new data after a
# dropdown change; it carries a "*_disp_*" modifier class only while loading.
LOADER_CSS = "div[class*='play_loader']"
LOADER_LOADING_CLASS = "play_disp"          # modifier present only while fetching
LOADER_APPEAR_TIMEOUT = float(os.getenv("LOADER_APPEAR_TIMEOUT", "4"))
# Tiny pause after a render completes so React can paint before we read text.
PAINT_SETTLE = float(os.getenv("PAINT_SETTLE", "0.2"))


def _loader_is_active(driver):
    """True while the play page is fetching/rendering new data."""
    try:
        el = driver.find_element(By.CSS_SELECTOR, LOADER_CSS)
        return LOADER_LOADING_CLASS in (el.get_attribute("class") or "")
    except Exception:
        return False


def wait_for_data_refresh(driver, wait):
    """Wait for a dropdown-triggered data fetch to finish.

    Phase and MR-mode dropdown changes fire an async API request and update the
    list text in place (the DOM nodes are reused, and the new values are often
    identical to the old ones), so staleness/value-diff checks are unreliable.
    The loader's modifier class is the authoritative signal: it appears when the
    fetch starts and clears when the new data is rendered.
    """
    # Wait briefly for the loader to appear. Poll fast because it shows within
    # ~30-80ms. If it never appears (e.g. a cached response), fall through.
    try:
        WebDriverWait(driver, LOADER_APPEAR_TIMEOUT, poll_frequency=0.1).until(
            _loader_is_active
        )
    except TimeoutException:
        pass
    # Wait for the loader to clear, i.e. the new data has rendered.
    wait.until(lambda d: not _loader_is_active(d))
    time.sleep(PAINT_SETTLE)

def close_cookie_popup(driver):
    """Close cookie consent popup if present"""
    try:
        btn = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonAccept")
        driver.execute_script("arguments[0].click();", btn)
    except (NoSuchElementException, Exception):
        pass

def scrape_username(driver, wait):
    """Scrape the username from the profile page"""
    try:
        el = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.status_name__gXNo9"))
        )
        return el.text.strip()
    except (TimeoutException, Exception):
        return None
def scrape_platform(driver, wait):
    """Scrape the platform icon URL from the profile page"""
    try:
        img = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span.status_platform__Pp1nu img")
            )
        )
        src = img.get_attribute("src")
        if src and src.startswith("/"):
            src = "https://www.streetfighter.com" + src
        return src
    except (TimeoutException, Exception):
        return None
def open_play_tab(driver, wait, tab_text):
    """Open a specific tab (e.g., 'league points' or 'master rate')"""
    tabs = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li"))
    )
    target_tab = None
    target_text = tab_text.lower()
    for tab in tabs:
        if target_text in tab.text.lower():
            target_tab = tab
            break
    if not target_tab:
        raise RuntimeError(f"{tab_text} tab not found")
    driver.execute_script("arguments[0].scrollIntoView(true);", target_tab)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", target_tab)
    wait.until(lambda d: "active" in target_tab.get_attribute("class"))
def select_phase(driver, wait, phase_number):
    """Select a specific phase from the Phase dropdown"""
    try:
        # Phase dropdown = first <dd> inside filter_nav_filter_nav__*
        dropdown = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "aside.filter_nav_filter_nav__6P1ya dd:nth-of-type(1) select"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        time.sleep(0.2)
        dropdown.click()
        time.sleep(0.2)
        phase_option = dropdown.find_element(By.CSS_SELECTOR, f"option[value='{phase_number}']")
        phase_option.click()
        # Trigger React refresh
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            dropdown
        )
        print(f"Phase dropdown set to Phase {phase_number}")

        # Wait for the async fetch + in-place re-render to finish.
        wait_for_data_refresh(driver, wait)
        print(f"Page reloaded with Phase {phase_number} data")
        
    except Exception as e:
        print(f"Failed to switch to Phase {phase_number}:", e)
        raise

def select_highest_mode(driver, wait):
    """Select 'Highest' mode from the MR dropdown"""
    try:
        # MR dropdown = second <dd> inside filter_nav_filter_nav__*
        dropdown = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "aside.filter_nav_filter_nav__6P1ya dd:nth-of-type(2) select"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        time.sleep(0.2)
        dropdown.click()
        time.sleep(0.2)
        highest_option = dropdown.find_element(By.CSS_SELECTOR, "option[value='2']")
        highest_option.click()
        # Trigger React refresh
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            dropdown
        )
        print("MR dropdown set to Highest")

        # Highest re-renders the MR values in place (same nodes, sometimes the
        # same numbers), so rely on the loader signal rather than node/value
        # changes to know the new data has arrived.
        wait_for_data_refresh(driver, wait)
        print("Page reloaded with highest MR data")
        
    except Exception as e:
        print("Failed to switch MR dropdown:", e)
def scrape_league_points(driver, wait):
    """Scrape league points for all characters"""
    # Wait for container to be present
    container = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.league_point_inner__iCMYc ul")
        )
    )
    
    # The LP value element only exists on the League Points tab (the MR tab uses
    # a different, mutually exclusive selector), so waiting for it guarantees the
    # correct tab has rendered without reading stale cross-tab data.
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "p.league_point_lp__viByb")
        )
    )
    time.sleep(PAINT_SETTLE)

    items = container.find_elements(By.TAG_NAME, "li")
    results = []
    for item in items:
        try:
            name = item.find_element(
                By.CSS_SELECTOR, "p.league_point_name__ZjWgb"
            ).text.strip()
            lp_text = item.find_element(
                By.CSS_SELECTOR, "p.league_point_lp__viByb"
            ).text.strip()
            if lp_text.startswith("---"):
                continue
            lp_value = int(
                lp_text.replace("LP", "").replace(",", "").strip()
            )
            results.append({"name": name, "lp": lp_value})
        except (ValueError, NoSuchElementException, Exception):
            continue
    return results
def scrape_master_rate(driver, wait):
    """Scrape master rate for all characters"""
    # Wait for container to be present
    container = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.league_point_inner__iCMYc ul")
        )
    )
    
    # The MR value element only exists on the Master Rate tab (mutually exclusive
    # with the LP tab's selector), so waiting for it guarantees the correct tab
    # has rendered. For the Highest pass, select_highest_mode has already waited
    # on the loader, so this returns immediately.
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "p.league_point_mr__WaC1_")
        )
    )
    time.sleep(PAINT_SETTLE)

    items = container.find_elements(By.TAG_NAME, "li")
    results = []
    for item in items:
        try:
            name = item.find_element(
                By.CSS_SELECTOR, "p.league_point_name__ZjWgb"
            ).text.strip()
            mr_text = item.find_element(
                By.CSS_SELECTOR, "p.league_point_mr__WaC1_"
            ).text.strip()
            if mr_text.startswith("---"):
                continue
            mr_value = int(
                mr_text.replace("MR", "").replace(",", "").strip()
            )
            results.append({"name": name, "mr": mr_value})
        except (ValueError, NoSuchElementException, Exception):
            continue
    return results
def load_cookies():
    """Load cookies from GitHub secret"""
    cookies_secret = os.getenv('SESSION_COOKIES')
    if not cookies_secret:
        return None
    
    try:
        # Parse JSON directly (no base64 decoding needed)
        cookies = json.loads(cookies_secret)
        print(f"Loaded {len(cookies)} cookies from GitHub secret")
        return cookies
    except Exception as e:
        print(f"Failed to load cookies from secret: {e}")
        return None

def load_player_ids(path="sf6-tracker/src/data/players.json"):
    """Load player IDs from players.json file"""
    with open(path, "r", encoding="utf-8") as f:
        players = json.load(f)
    
    player_ids = []
    for player in players:
        player_id = player["id"]
        
        # Handle both single ID and array of IDs
        if isinstance(player_id, list):
            player_ids.extend(player_id)
        else:
            player_ids.append(player_id)
    
    return player_ids

def parse_arguments():
    """
    Parse command-line arguments for player IDs and phases.
    
    Usage:
        python scrape_cfn.py [player_ids] [--phase PHASE]
        
    Args:
        player_ids: Comma-separated player IDs (optional, defaults to all from file)
        --phase: Phase number (1-12) or 'all' (optional, defaults to latest phase only)
    
    Returns:
        tuple: (player_ids_list, phases_list)
    """
    player_ids = None
    phases = [12]  # Default to latest phase only
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--phase':
            if i + 1 < len(args):
                phase_arg = args[i + 1]
                if phase_arg.lower() == 'all':
                    phases = list(range(1, 13))  # All phases 1-12
                else:
                    try:
                        phase_num = int(phase_arg)
                        if 1 <= phase_num <= 12:
                            phases = [phase_num]
                        else:
                            print(f"Warning: Phase {phase_num} out of range (1-12), using default")
                    except ValueError:
                        print(f"Warning: Invalid phase '{phase_arg}', using default")
                i += 2
            else:
                print("Warning: --phase requires a value")
                i += 1
        else:
            # Assume it's player IDs
            if player_ids is None:
                player_ids = args[i]
            i += 1
    
    # Get player IDs
    if player_ids:
        ids = [pid.strip() for pid in player_ids.split(',') if pid.strip()]
        print(f"Using {len(ids)} player ID(s) from command-line: {', '.join(ids)}")
    else:
        ids = load_player_ids()
        print(f"Using all {len(ids)} player IDs from player_ids.txt")
    
    print(f"Scraping phase(s): {', '.join(map(str, phases))}")
    
    return ids, phases

def scrape_phase(driver, wait, ids, phase_number):
    """
    Scrape data for a specific phase.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        ids: List of player IDs to scrape
        phase_number: Phase number to scrape
    
    Returns:
        dict: Scraped player data
    """
    output_file = f"sf6-tracker/src/data/phase_{phase_number}.json"
    
    # Load existing data if doing a partial scrape
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                file_data = json.load(f)
                existing_data = file_data.get("players", {})
            print(f"Loaded existing data for {len(existing_data)} players from phase_{phase_number}.json")
        except Exception as e:
            print(f"Warning: Could not load existing data: {e}")
            print("Will create new file instead")
    
    all_results = {}
    
    for pid in ids:
        print(f"\n--- Processing {pid} (Phase {phase_number}) ---")
        profile_url = (
            f"https://www.streetfighter.com/6/buckler/profile/{pid}/play"
        )
        driver.get(profile_url)
        try:
            wait.until(lambda d: pid in d.current_url)
        except TimeoutException:
            print("Profile load failed")
            continue
        close_cookie_popup(driver)
        username = scrape_username(driver, wait)
        platform_icon = scrape_platform(driver, wait)
        
        try:
            open_play_tab(driver, wait, "league points")
        except Exception as e:
            print(f"Cannot open LP tab - cookies likely invalid: {e}")
            print("\n!!! AUTHENTICATION FAILED !!!")
            print("Your session cookies are no longer valid.")
            print("Please run refresh_cookies.py to obtain new cookies.")
            raise RuntimeError("Session expired - please refresh cookies")
        
        # Select the phase if not the default (12)
        if phase_number != 12:
            try:
                select_phase(driver, wait, phase_number)
            except Exception as e:
                print(f"Failed to select phase {phase_number}: {e}")
                continue

        print("Scraping LP per character...")
        lp_list = scrape_league_points(driver, wait)

        try:
            open_play_tab(driver, wait, "master rate")
        except Exception:
            print("Cannot open MR tab")
            continue
        
        # Select the phase again for MR tab if not default
        if phase_number != 12:
            try:
                select_phase(driver, wait, phase_number)
            except Exception as e:
                print(f"Failed to select phase {phase_number} on MR tab: {e}")
                continue
        
        # Scrape CURRENT MR first (before changing dropdown)
        print("Scraping current MR...")
        current_mr_list = scrape_master_rate(driver, wait)
        
        # Now switch to HIGHEST mode
        select_highest_mode(driver, wait)
        
        # Scrape HIGHEST MR
        print("Scraping highest MR...")
        highest_mr_list = scrape_master_rate(driver, wait)
        
        all_results[pid] = {
            "username": username,
            "platform": platform_icon,
            "lp": lp_list,
            "current_mr": current_mr_list,
            "highest_mr": highest_mr_list
        }
    
    # Smart merge: only update fields that have data, preserve existing data otherwise
    if existing_data:
        print(f"\nMerging {len(all_results)} scraped player(s) with existing data...")
        for pid, new_data in all_results.items():
            if pid in existing_data:
                # Player exists - merge intelligently
                existing_player = existing_data[pid]
                merged_player = {}
                
                # Update username and platform if present
                merged_player["username"] = new_data.get("username") or existing_player.get("username")
                merged_player["platform"] = new_data.get("platform") or existing_player.get("platform")
                
                # For data arrays, only update if new data is not empty
                # Otherwise keep existing data to prevent data loss
                merged_player["lp"] = new_data.get("lp") if new_data.get("lp") else existing_player.get("lp", [])
                merged_player["current_mr"] = new_data.get("current_mr") if new_data.get("current_mr") else existing_player.get("current_mr", [])
                
                # Special handling for highest_mr: ensure values never decrease
                new_highest = new_data.get("highest_mr", [])
                existing_highest = existing_player.get("highest_mr", [])
                
                if new_highest and existing_highest:
                    # Both exist - merge by taking maximum MR for each character
                    merged_highest = {}
                    
                    # Add all existing highest MR values
                    for char_data in existing_highest:
                        char_name = char_data.get("name")
                        if char_name:
                            merged_highest[char_name] = char_data.get("mr", 0)
                    
                    # Update with new values only if they're higher
                    updated_chars = []
                    for char_data in new_highest:
                        char_name = char_data.get("name")
                        new_mr = char_data.get("mr", 0)
                        if char_name:
                            existing_mr = merged_highest.get(char_name, 0)
                            if new_mr > existing_mr:
                                merged_highest[char_name] = new_mr
                                updated_chars.append(f"{char_name}({existing_mr}→{new_mr})")
                            elif new_mr < existing_mr:
                                # Keep existing higher value
                                pass
                            else:
                                # Same value, update anyway to ensure it's in the list
                                merged_highest[char_name] = new_mr
                    
                    # Convert back to list format
                    merged_player["highest_mr"] = [
                        {"name": name, "mr": mr}
                        for name, mr in merged_highest.items()
                    ]
                    
                    if updated_chars:
                        print(f"  📈 {pid}: Updated highest_mr for {', '.join(updated_chars)}")
                    
                elif new_highest:
                    # Only new data exists
                    merged_player["highest_mr"] = new_highest
                else:
                    # Only existing data exists or both empty
                    merged_player["highest_mr"] = existing_highest
                
                existing_data[pid] = merged_player
                
                # Log if we preserved any data
                preserved = []
                if not new_data.get("lp") and existing_player.get("lp"):
                    preserved.append("lp")
                if not new_data.get("current_mr") and existing_player.get("current_mr"):
                    preserved.append("current_mr")
                if not new_highest and existing_highest:
                    preserved.append("highest_mr")
                if preserved:
                    print(f"  ⚠️  {pid}: Preserved existing data for {', '.join(preserved)} (new scrape was empty)")
            else:
                # New player - add directly
                existing_data[pid] = new_data
        
        final_results = existing_data
    else:
        final_results = all_results
    
    # Add timestamp to the results
    output_data = {
        "last_updated": datetime.now(ZoneInfo("America/Chicago")).isoformat(),
        "players": final_results
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Phase {phase_number} complete! Updated {len(all_results)} player(s) in phase_{phase_number}.json")
    
    return final_results

def main():
    """Main scraping function - loads cookies and scrapes player data"""
    ids, phases = parse_arguments()
    print(f"Scraping {len(ids)} player ID(s) across {len(phases)} phase(s)")
    
    # Load cookies (required for scraping)
    cookies = load_cookies()
    if not cookies:
        raise RuntimeError("No cookies found.")
    
    print(f"Loaded {len(cookies)} cookies from storage")
    
    # Setup headless browser for scraping
    print("\n=== Starting Scraping (Headless Browser) ===")
    headless_options = webdriver.ChromeOptions()
    headless_options.add_argument("--headless=new")
    headless_options.add_argument("--window-size=1440,1200")
    headless_options.add_argument("--disable-gpu")
    headless_options.add_argument("--no-sandbox")
    headless_options.add_argument("--disable-dev-shm-usage")
    # Skip downloading images: we only read the platform icon's src attribute,
    # which is present in the DOM whether or not the image is fetched.
    headless_options.add_argument("--blink-settings=imagesEnabled=false")
    # Return control at DOMContentLoaded instead of waiting for every asset;
    # the explicit element waits after each navigation cover SPA rendering.
    headless_options.page_load_strategy = "eager"
    # Add user agent to avoid detection
    headless_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=headless_options)
    wait = WebDriverWait(driver, 40)
    
    try:
        # Navigate to the site and restore cookies
        print("Loading base site to set cookies...")
        driver.get("https://www.streetfighter.com")
        time.sleep(0.5)
        
        # Add cookies
        for cookie in cookies:
            try:
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])
                if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                    cookie['sameSite'] = 'Lax'
                driver.add_cookie(cookie)
            except Exception:
                print("Warning: Could not add one cookie entry; skipping.")
        
        print(f"Restored {len(cookies)} cookies")
        
        # Refresh to apply cookies
        driver.refresh()
        time.sleep(1)
        print("Session restored, starting scraping...\n")
        
        # Scrape each phase
        for phase in phases:
            print(f"\n{'='*60}")
            print(f"SCRAPING PHASE {phase}")
            print(f"{'='*60}")
            scrape_phase(driver, wait, ids, phase)
        
        print(f"\n{'='*60}")
        print(f"✓ ALL SCRAPING COMPLETE!")
        print(f"Scraped {len(ids)} player(s) across {len(phases)} phase(s)")
        print(f"{'='*60}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()