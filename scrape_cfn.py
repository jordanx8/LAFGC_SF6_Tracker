import time
import json
import os
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
        
        # Wait for the page to reload with new data
        # Wait for stale element to ensure DOM has updated
        time.sleep(1.5)
        
        # Wait for the list to be re-rendered with new values
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.league_point_inner__iCMYc ul li")
            )
        )
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
    
    # Wait for the list items to be present and visible
    wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.league_point_inner__iCMYc ul li")
        )
    )
    
    # Additional wait to ensure content has fully loaded
    time.sleep(2)
    
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
    
    # Wait for the list items to be present and visible
    wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.league_point_inner__iCMYc ul li")
        )
    )
    
    # Additional wait to ensure content has fully loaded
    time.sleep(2)
    
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

def load_player_ids(path="player_ids.txt"):
    """Load player IDs from a text file"""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
def main():
    """Main scraping function - loads cookies and scrapes player data"""
    ids = load_player_ids()
    print(f"Loaded {len(ids)} player IDs")
    
    # Load cookies (required for scraping)
    cookies = load_cookies()
    if not cookies:
        print("ERROR: No cookies found!")
        print("Please run refresh_cookies.py first to obtain session cookies.")
        return
    
    print(f"Loaded {len(cookies)} cookies from storage")
    
    # Setup headless browser for scraping
    print("\n=== Starting Scraping (Headless Browser) ===")
    headless_options = webdriver.ChromeOptions()
    headless_options.add_argument("--headless=new")
    headless_options.add_argument("--window-size=1440,1200")
    headless_options.add_argument("--disable-gpu")
    headless_options.add_argument("--no-sandbox")
    headless_options.add_argument("--disable-dev-shm-usage")
    # Add user agent to avoid detection
    headless_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=headless_options)
    wait = WebDriverWait(driver, 40)
    all_results = {}
    
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
            except Exception as e:
                print(f"Warning: Could not add cookie {cookie.get('name', 'unknown')}: {e}")
        
        print(f"Restored {len(cookies)} cookies")
        
        # Refresh to apply cookies
        driver.refresh()
        time.sleep(1)
        print("Session restored, starting scraping...\n")
        
        for pid in ids:
            print(f"\n--- Processing {pid} ---")
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
                driver.quit()
                raise RuntimeError("Session expired - please refresh cookies")

            print("Scraping LP per character...")
            lp_list = scrape_league_points(driver, wait)

            try:
                open_play_tab(driver, wait, "master rate")
            except Exception:
                print("Cannot open MR tab")
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
    finally:
        driver.quit()
    
    # Add timestamp to the results
    output_data = {
        "last_updated": datetime.now(ZoneInfo("America/Chicago")).isoformat(),
        "players": all_results
    }
    
    with open("sf6-tracker/src/data/phase_12.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print("\n✓ Scraping complete! Data saved to phase_12.json")

if __name__ == "__main__":
    main()