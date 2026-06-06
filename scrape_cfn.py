import time
import json
import os
import base64
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

LOGIN_URL = "https://cid.capcom.com/ja/login/?guidedBy=web"
BUCKLER_LOGIN_URL = "https://www.streetfighter.com/6/buckler/auth/loginep?redirect_url=/"
SELECT_PLATFORM_URL_PART = "/auth/select-platform"
# Use environment variable if available, otherwise use default Windows path
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', r"C:\WebDriver\chromedriver.exe")
COOKIES_FILE = "session_cookies.json"
def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())
# -------------------------------------------------------
# MANUAL LOGIN
# -------------------------------------------------------
def login_manually(driver, wait):
    driver.get(LOGIN_URL)
    print("Please log in manually...")
    wait.until(lambda d: "login" not in d.current_url.lower())
    print("Login complete:", driver.current_url)
# -------------------------------------------------------
# CLOSE COOKIE POPUP
# -------------------------------------------------------
def close_cookie_popup(driver):
    try:
        btn = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonAccept")
        driver.execute_script("arguments[0].click();", btn)
    except (NoSuchElementException, Exception):
        pass
# -------------------------------------------------------
# PLATFORM SELECTION
# -------------------------------------------------------
def go_to_buckler_and_handle_platform(driver, wait, platform_variable):
    driver.get(BUCKLER_LOGIN_URL)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    close_cookie_popup(driver)
    if SELECT_PLATFORM_URL_PART in driver.current_url:
        select_platform_and_submit(driver, wait, platform_variable)
def select_platform_and_submit(driver, wait, platform_variable):
    platform_variable = normalize_text(platform_variable)
    items = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "ul.selectplatform_platformarea__SHi9F li")
        )
    )
    target_item = None
    for item in items:
        if platform_variable in normalize_text(item.text.strip()):
            target_item = item
            break
    if not target_item:
        raise RuntimeError("Platform option not found.")
    driver.execute_script("arguments[0].scrollIntoView(true);", target_item)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", target_item)
    submit_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    driver.execute_script("arguments[0].click();", submit_btn)
    wait.until(lambda d: SELECT_PLATFORM_URL_PART not in d.current_url)
# -------------------------------------------------------
# SCRAPE USERNAME
# -------------------------------------------------------
def scrape_username(driver, wait):
    try:
        el = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.status_name__gXNo9"))
        )
        return el.text.strip()
    except (TimeoutException, Exception):
        return None
# -------------------------------------------------------
# SCRAPE PLATFORM ICON
# -------------------------------------------------------
def scrape_platform(driver, wait):
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
# -------------------------------------------------------
# OPEN PLAY TAB
# -------------------------------------------------------
def open_play_tab(driver, wait, tab_text):
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
# -------------------------------------------------------
# SELECT "HIGHEST" MODE  (Correct dropdown!)
# -------------------------------------------------------
def select_highest_mode(driver, wait):
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
# -------------------------------------------------------
# SCRAPE LP LIST
# -------------------------------------------------------
def scrape_league_points(driver, wait):
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
# -------------------------------------------------------
# SCRAPE MR LIST
# -------------------------------------------------------
def scrape_master_rate(driver, wait):
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
# -------------------------------------------------------
# COOKIE MANAGEMENT
# -------------------------------------------------------
def update_github_secret(secret_name, secret_value):
    """Update a GitHub repository secret using GitHub API"""
    try:
        github_token = os.getenv('GH_TOKEN')
        github_repo = os.getenv('GITHUB_REPOSITORY')
        
        if not github_token or not github_repo:
            print("GitHub token or repository not available, skipping secret update")
            return False
        
        # Get the repository public key
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        key_url = f'https://api.github.com/repos/{github_repo}/actions/secrets/public-key'
        key_response = requests.get(key_url, headers=headers)
        key_response.raise_for_status()
        key_data = key_response.json()
        
        public_key = key_data['key']
        key_id = key_data['key_id']
        
        # Encrypt the secret value
        from nacl import encoding, public as nacl_public
        public_key_obj = nacl_public.PublicKey(public_key.encode(), encoding.Base64Encoder())
        sealed_box = nacl_public.SealedBox(public_key_obj)
        encrypted = sealed_box.encrypt(secret_value.encode())
        encrypted_value = base64.b64encode(encrypted).decode()
        
        # Update the secret
        secret_url = f'https://api.github.com/repos/{github_repo}/actions/secrets/{secret_name}'
        secret_data = {
            'encrypted_value': encrypted_value,
            'key_id': key_id
        }
        
        secret_response = requests.put(secret_url, headers=headers, json=secret_data)
        secret_response.raise_for_status()
        
        print(f"Successfully updated GitHub secret: {secret_name}")
        return True
        
    except Exception as e:
        print(f"Failed to update GitHub secret: {e}")
        return False

def save_cookies(cookies, filepath=COOKIES_FILE):
    """Save cookies to GitHub secret or JSON file"""
    cookies_json = json.dumps(cookies)
    
    # If running in GitHub Actions, update the secret
    if os.getenv('GITHUB_ACTIONS'):
        # Store cookies as plain JSON (no base64 encoding)
        update_github_secret('SESSION_COOKIES', cookies_json)
    else:
        # Save to file for local use
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
        print(f"Saved {len(cookies)} cookies to {filepath}")

def load_cookies(filepath=COOKIES_FILE):
    """Load cookies from GitHub secret or JSON file"""
    # First, try to load from GitHub secret
    cookies_secret = os.getenv('SESSION_COOKIES')
    if cookies_secret:
        try:
            # Parse JSON directly (no base64 decoding needed)
            cookies = json.loads(cookies_secret)
            print(f"Loaded {len(cookies)} cookies from GitHub secret")
            return cookies
        except Exception as e:
            print(f"Failed to load cookies from secret: {e}")
    
    # Fall back to file if secret not available
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        print(f"Loaded {len(cookies)} cookies from {filepath}")
        return cookies
    return None

def test_cookies(driver, wait, cookies, platform_variable):
    """Test if saved cookies are still valid"""
    try:
        print("Testing saved cookies...")
        driver.get("https://www.streetfighter.com")
        time.sleep(1)
        
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
        
        # Try to access buckler
        driver.get(BUCKLER_LOGIN_URL)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1)
        
        # Check if we need to select platform or if we're already logged in
        if SELECT_PLATFORM_URL_PART in driver.current_url:
            select_platform_and_submit(driver, wait, platform_variable)
        
        # Verify we're logged in by checking if we can access a profile page
        driver.get("https://www.streetfighter.com/6/buckler")
        time.sleep(1)
        
        # If we're on login page, cookies are invalid
        if "login" in driver.current_url.lower():
            print("Cookies are invalid or expired")
            return False
        
        print("Cookies are valid!")
        return True
        
    except Exception as e:
        print(f"Cookie test failed: {e}")
        return False

# -------------------------------------------------------
# LOAD PLAYER IDs
# -------------------------------------------------------
def load_player_ids(path="player_ids.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
# -------------------------------------------------------
# MAIN SCRIPT
# -------------------------------------------------------
def main():
    platform_variable = "playstation"
    ids = load_player_ids()
    print(f"Loaded {len(ids)} IDs")
    
    # Try to load saved cookies first
    cookies = load_cookies()
    cookies_valid = False
    
    if cookies:
        print("\n=== Testing Saved Cookies (Headless) ===")
        test_options = webdriver.ChromeOptions()
        test_options.add_argument("--headless=new")
        test_options.add_argument("--window-size=1440,1200")
        test_options.add_argument("--disable-gpu")
        test_options.add_argument("--no-sandbox")
        test_options.add_argument("--disable-dev-shm-usage")
        test_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=test_options)
        wait = WebDriverWait(driver, 40)
        
        try:
            cookies_valid = test_cookies(driver, wait, cookies, platform_variable)
            driver.quit()
        except Exception as e:
            print(f"Cookie test error: {e}")
            driver.quit()
            cookies_valid = False
    
    # If cookies are invalid or don't exist, do manual login
    if not cookies_valid:
        print("\n=== STEP 1: Manual Login Required (Visible Browser) ===")
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1440,1200")
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
        wait = WebDriverWait(driver, 40)
        
        try:
            login_manually(driver, wait)
            go_to_buckler_and_handle_platform(driver, wait, platform_variable)
            
            # Save cookies after successful login
            cookies = driver.get_cookies()
            save_cookies(cookies)
            
            # Close the visible browser
            driver.quit()
            print("Closed visible browser\n")
            
        except Exception as e:
            print(f"Login failed: {e}")
            driver.quit()
            return
    else:
        print("Using saved cookies, skipping manual login\n")
    
    # Step 2: Continue with headless browser
    print("=== STEP 2: Scraping (Headless Browser) ===")
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
        
        # Add cookies (they should exist at this point)
        if cookies:
            for cookie in cookies:
                try:
                    # Remove domain-specific fields that might cause issues
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                        cookie['sameSite'] = 'Lax'
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Warning: Could not add cookie {cookie.get('name', 'unknown')}: {e}")
            
            print(f"Restored {len(cookies)} cookies in headless browser")
        else:
            print("ERROR: No cookies available for scraping!")
            driver.quit()
            return
        
        # Refresh to apply cookies
        driver.refresh()
        time.sleep(1)
        print("Session restored, starting scraping...")
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
                print("The script will now close and you need to re-run it to login again.")
                driver.quit()
                
                # Delete the invalid cookies
                if os.path.exists(COOKIES_FILE):
                    os.remove(COOKIES_FILE)
                    print(f"Deleted invalid cookies file: {COOKIES_FILE}")
                
                # Exit with error to signal failure
                raise RuntimeError("Session expired - please re-run the script to login again")

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
    
    with open("sf6-tracker/src/master_rates.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print("Saved master_rates.json with timestamp")
if __name__ == "__main__":
    main()