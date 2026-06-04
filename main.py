import os
import time
import json
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
# ------------------ LOGIN ------------------
def login_manually(driver, wait):
    driver.get(LOGIN_URL)
    print("Please log in manually...")
    wait.until(lambda d: "login" not in d.current_url.lower())
    print("Login complete:", driver.current_url)
# ------------------ COOKIE POPUP ------------------
def close_cookie_popup(driver):
    try:
        btn = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonAccept")
        driver.execute_script("arguments[0].click();", btn)
    except:
        pass
# ------------------ PLATFORM SELECT ------------------
def go_to_buckler_and_handle_platform(driver, wait, platform_variable):
    driver.get(BUCKLER_LOGIN_URL)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    close_cookie_popup(driver)
    if SELECT_PLATFORM_URL_PART in driver.current_url:
        select_platform_and_submit(driver, wait, platform_variable)
def select_platform_and_submit(driver, wait, platform_variable):
    normalized_target = normalize_text(platform_variable)
    items = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "ul.selectplatform_platformarea__SHi9F li")
        )
    )
    for item in items:
        if normalized_target in normalize_text(item.text.strip()):
            driver.execute_script("arguments[0].scrollIntoView(true);", item)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", item)
            break
    submit_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    driver.execute_script("arguments[0].click();", submit_btn)
    wait.until(lambda d: SELECT_PLATFORM_URL_PART not in d.current_url)
# ------------------ SCRAPE USERNAME ------------------
def scrape_username(driver, wait):
    try:
        el = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.status_name__gXNo9"))
        )
        return el.text.strip()
    except:
        return None
# ------------------ SCRAPE PLATFORM ICON ------------------
def scrape_platform(driver, wait):
    try:
        img = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span.status_platform__Pp1nu img")
            )
        )
        src = img.get_attribute("src")
        # Convert relative URLs → full URLs
        if src.startswith("/"):
            src = "https://www.streetfighter.com" + src
        return src
    except Exception as e:
        print("Platform scrape error:", e)
        return None
# ------------------ OPEN MR TAB ------------------
def open_master_rate_tab(driver, wait):
    items = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li"))
    )
    mr_tab = None
    for li in items:
        if "master rate" in li.text.lower():
            mr_tab = li
            break
    driver.execute_script("arguments[0].scrollIntoView(true);", mr_tab)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", mr_tab)
    wait.until(lambda d: "active" in mr_tab.get_attribute("class"))
# ------------------ SCRAPE MR LIST ------------------
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
            mr_val = int(mr_text.replace("MR", "").replace(",", "").strip())
            results.append({"name": name, "mr": mr_val})
        except:
            continue
    return results
# ------------------ LOAD IDs ------------------
def load_player_ids(path="player_ids.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
# ------------------ MAIN ------------------
def main():
    platform_variable = "playstation"
    player_ids = load_player_ids()
    print(f"Loaded {len(player_ids)} IDs")
    opts = webdriver.ChromeOptions()
    opts.add_argument("--window-size=1440,1200")
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)
    wait = WebDriverWait(driver, 40)
    all_results = {}
    try:
        login_manually(driver, wait)
        go_to_buckler_and_handle_platform(driver, wait, platform_variable)
        for pid in player_ids:
            print(f"\n--- Processing {pid} ---")
            profile_url = f"https://www.streetfighter.com/6/buckler/profile/{pid}/play"
            driver.get(profile_url)
            try:
                wait.until(lambda d: pid in d.current_url)
            except:
                print("Bad profile, skipping.")
                continue
            close_cookie_popup(driver)
            username = scrape_username(driver, wait)
            platform_icon = scrape_platform(driver, wait)
            try:
                open_master_rate_tab(driver, wait)
            except:
                print("MR tab failed")
                continue
            mr_list = scrape_master_rate(driver, wait)
            all_results[pid] = {
                "username": username,
                "platform": platform_icon,
                "mr": mr_list
            }
    finally:
        driver.quit()
    with open("master_rates.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
    print("\nSaved master_rates.json")
if __name__ == "__main__":
    main()