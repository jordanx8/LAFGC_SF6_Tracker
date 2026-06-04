import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
LOGIN_URL = "https://cid.capcom.com/ja/login/?guidedBy=web"
BUCKLER_LOGIN_URL = "https://www.streetfighter.com/6/buckler/auth/loginep?redirect_url=/"
SELECT_PLATFORM_URL_PART = "/auth/select-platform"
CHROMEDRIVER_PATH = r"C:\WebDriver\chromedriver.exe"
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
    except:
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
    except:
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
        if src.startswith("/"):
            src = "https://www.streetfighter.com" + src
        return src
    except:
        return None
# -------------------------------------------------------
# OPEN MASTER RATE TAB
# -------------------------------------------------------
def open_master_rate_tab(driver, wait):
    tabs = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li"))
    )
    mr_tab = None
    for tab in tabs:
        if "master rate" in tab.text.lower():
            mr_tab = tab
            break
    if not mr_tab:
        raise RuntimeError("Master Rate tab not found")
    driver.execute_script("arguments[0].scrollIntoView(true);", mr_tab)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", mr_tab)
    wait.until(lambda d: "active" in mr_tab.get_attribute("class"))
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
        time.sleep(0.3)
        dropdown.click()
        time.sleep(0.3)
        highest_option = dropdown.find_element(By.CSS_SELECTOR, "option[value='2']")
        highest_option.click()
        # Trigger React refresh
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            dropdown
        )
        print("MR dropdown set to Highest")
        time.sleep(1)
    except Exception as e:
        print("Failed to switch MR dropdown:", e)
# -------------------------------------------------------
# SCRAPE MR LIST
# -------------------------------------------------------
def scrape_master_rate(driver, wait):
    container = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.league_point_inner__iCMYc ul")
        )
    )
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
        except:
            continue
    return results
# -------------------------------------------------------
# COOKIE MANAGEMENT
# -------------------------------------------------------
def save_cookies(cookies, filepath=COOKIES_FILE):
    """Save cookies to a JSON file"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=4)
    print(f"Saved {len(cookies)} cookies to {filepath}")

def load_cookies(filepath=COOKIES_FILE):
    """Load cookies from a JSON file if it exists"""
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
        time.sleep(2)
        
        # Check if we need to select platform or if we're already logged in
        if SELECT_PLATFORM_URL_PART in driver.current_url:
            select_platform_and_submit(driver, wait, platform_variable)
        
        # Verify we're logged in by checking if we can access a profile page
        driver.get("https://www.streetfighter.com/6/buckler")
        time.sleep(2)
        
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
        time.sleep(1)
        
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
        time.sleep(2)
        print("Session restored, starting scraping...")
        for pid in ids:
            print(f"\n--- Processing {pid} ---")
            profile_url = (
                f"https://www.streetfighter.com/6/buckler/profile/{pid}/play"
            )
            driver.get(profile_url)
            try:
                wait.until(lambda d: pid in d.current_url)
            except:
                print("Profile load failed")
                continue
            close_cookie_popup(driver)
            username = scrape_username(driver, wait)
            platform_icon = scrape_platform(driver, wait)
            try:
                open_master_rate_tab(driver, wait)
            except:
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
                "current_mr": current_mr_list,
                "highest_mr": highest_mr_list
            }
    finally:
        driver.quit()
    with open("master_rates.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
    print("Saved master_rates.json")
if __name__ == "__main__":
    main()