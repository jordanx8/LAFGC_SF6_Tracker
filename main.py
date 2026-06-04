import os
import sys
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
LOGIN_URL = "https://cid.capcom.com/ja/login/?guidedBy=web"
BUCKLER_LOGIN_URL = "https://www.streetfighter.com/6/buckler/auth/loginep?redirect_url=/"
SELECT_PLATFORM_URL_PART = "/auth/select-platform"
CHROMEDRIVER_PATH = r"C:\WebDriver\chromedriver.exe"
def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())
# -------------------------------------------------------
# MANUAL LOGIN
# -------------------------------------------------------
def login_manually(driver, wait):
    driver.get(LOGIN_URL)
    print("Please log in manually in Chrome...")
    wait.until(lambda d: "login" not in d.current_url.lower())
    print("Manual login complete:", driver.current_url)
# -------------------------------------------------------
# COOKIE POPUP CLOSE
# -------------------------------------------------------
def close_cookie_popup(driver, wait):
    try:
        wait_short = WebDriverWait(driver, 5)
        allow_btn = wait_short.until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonAccept"))
        )
        driver.execute_script("arguments[0].click();", allow_btn)
        print("Closed cookie popup.")
    except:
        pass
# -------------------------------------------------------
# PLATFORM SELECTION
# -------------------------------------------------------
def go_to_buckler_and_handle_platform(driver, wait, platform_variable):
    driver.get(BUCKLER_LOGIN_URL)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(1)
    close_cookie_popup(driver, wait)
    current_url = driver.current_url
    print("Arrived at:", current_url)
    if SELECT_PLATFORM_URL_PART in current_url:
        print("Platform selection required.")
        select_platform_and_submit(driver, wait, platform_variable)
    else:
        print("No platform selection needed.")
def select_platform_and_submit(driver, wait, platform_variable):
    close_cookie_popup(driver, wait)
    normalized_target = normalize_text(platform_variable)
    platform_items = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "ul.selectplatform_platformarea__SHi9F li")
        )
    )
    matched_item = None
    for item in platform_items:
        if normalized_target in normalize_text(item.text.strip()):
            matched_item = item
            break
    if matched_item is None:
        available = [item.text.strip() for item in platform_items]
        raise RuntimeError(f"Platform not found. Available: {available}")
    driver.execute_script("arguments[0].scrollIntoView(true);", matched_item)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", matched_item)
    submit_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    driver.execute_script("arguments[0].click();", submit_button)
    wait.until(lambda d: SELECT_PLATFORM_URL_PART not in d.current_url)
    print("Platform linked.")
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
# OPEN MR TAB
# -------------------------------------------------------
def open_master_rate_tab(driver, wait):
    nav_items = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li"))
    )
    mr_tab = None
    for li in nav_items:
        if "master rate" in li.text.strip().lower():
            mr_tab = li
            break
    if mr_tab is None:
        raise RuntimeError("Could not find MR tab.")
    driver.execute_script("arguments[0].scrollIntoView(true);", mr_tab)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", mr_tab)
    print("Clicked MR tab.")
    wait.until(lambda d: "active" in mr_tab.get_attribute("class"))
    print("MR tab active.")
# -------------------------------------------------------
# SCRAPE MR LIST (FILTER MR != None)
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
                continue  # Skip MR=None
            mr_value = int(mr_text.replace("MR", "").replace(",", "").strip())
            results.append({"name": name, "mr": mr_value})
        except:
            continue
    return results
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
    # Read player IDs from file
    player_ids = load_player_ids()
    print(f"Loaded {len(player_ids)} player IDs.")
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1200")
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
    wait = WebDriverWait(driver, 40)
    all_results = {}
    try:
        # Login & platform linking once
        login_manually(driver, wait)
        go_to_buckler_and_handle_platform(driver, wait, platform_variable)
        # Process multiple player IDs
        for player_id in player_ids:
            print("\n----------------------------------------")
            print(f"Processing player ID: {player_id}")
            print("----------------------------------------")
            profile_url = f"https://www.streetfighter.com/6/buckler/profile/{player_id}/play"
            driver.get(profile_url)
            try:
                wait.until(lambda d: player_id in d.current_url and "/play" in d.current_url)
            except:
                print(f"Failed to load profile for {player_id}. Skipping.")
                continue
            close_cookie_popup(driver, wait)
            # Scrape username
            username = scrape_username(driver, wait)
            print("Username:", username)
            # Open MR tab
            try:
                open_master_rate_tab(driver, wait)
            except Exception as e:
                print(f"MR tab error for {player_id}: {e}")
                continue
            # Scrape MR list
            mr_list = scrape_master_rate(driver, wait)
            all_results[player_id] = {
                "username": username,
                "mr": mr_list
            }
            print(f"Saved {len(mr_list)} MR entries for {player_id}")
        # Save final combined JSON
        with open("master_rates.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=4)
        print("\n=====================================")
        print("All results saved to master_rates.json")
        print("=====================================")
    finally:
        driver.quit()
if __name__ == "__main__":
    main()