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
from selenium.common.exceptions import TimeoutException
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
    print("Please log in manually in Chrome.")
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
        allow_btn.click()
        print("Closed cookie popup.")
        time.sleep(1)
    except:
        pass
# -------------------------------------------------------
# PLATFORM SELECTION
# -------------------------------------------------------
def go_to_buckler_and_handle_platform(driver, wait, platform_variable):
    driver.get(BUCKLER_LOGIN_URL)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(2)
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
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.selectplatform_platformarea__SHi9F li"))
    )
    matched_item = None
    for item in platform_items:
        if normalized_target in normalize_text(item.text.strip()):
            matched_item = item
            break
    if matched_item is None:
        available = [item.text.strip() for item in platform_items]
        raise RuntimeError("Platform not found on selection page.")
    driver.execute_script("arguments[0].scrollIntoView(true);", matched_item)
    time.sleep(0.3)
    wait.until(EC.element_to_be_clickable(matched_item))
    matched_item.click()
    print("Selected platform:", matched_item.text.strip())
    submit_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    submit_button.click()
    print("Platform submitted.")
    wait.until(lambda d: SELECT_PLATFORM_URL_PART not in d.current_url)
# -------------------------------------------------------
# OPEN MR TAB
# -------------------------------------------------------
def open_master_rate_tab(driver, wait):
    nav_items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li")))
    mr_tab = None
    for li in nav_items:
        if "master rate" in li.text.strip().lower():
            mr_tab = li
            break
    if mr_tab is None:
        raise RuntimeError("Could not find MR tab.")
    driver.execute_script("arguments[0].scrollIntoView(true);", mr_tab)
    time.sleep(0.3)
    wait.until(EC.element_to_be_clickable(mr_tab))
    mr_tab.click()
    print("Clicked MR tab.")
    wait.until(lambda d: "active" in mr_tab.get_attribute("class"))
    print("MR tab active.")
# -------------------------------------------------------
# SCRAPE MR LIST
# -------------------------------------------------------
def scrape_master_rate(driver, wait):
    container = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.league_point_inner__iCMYc ul"))
    )
    items = container.find_elements(By.TAG_NAME, "li")
    results = []
    for item in items:
        try:
            name = item.find_element(By.CSS_SELECTOR, "p.league_point_name__ZjWgb").text.strip()
            mr_text = item.find_element(By.CSS_SELECTOR, "p.league_point_mr__WaC1_").text.strip()
            if mr_text.startswith("---"):
                mr_value = None
            else:
                mr_value = int(mr_text.replace("MR", "").replace(",", "").strip())
            results.append({"name": name, "mr": mr_value})
        except:
            continue
    return results
# -------------------------------------------------------
# MAIN SCRIPT
# -------------------------------------------------------
def main():
    platform_variable = "playstation"
    target_player_id = "4000629934"
    target_profile_url = f"https://www.streetfighter.com/6/buckler/profile/{target_player_id}/play"
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1200")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 40)
    try:
        login_manually(driver, wait)
        go_to_buckler_and_handle_platform(driver, wait, platform_variable)
        print("Navigating to target profile:", target_profile_url)
        driver.get(target_profile_url)
        wait.until(lambda d: target_player_id in d.current_url and "/play" in d.current_url)
        print("Arrived at player profile:", driver.current_url)
        close_cookie_popup(driver, wait)
        open_master_rate_tab(driver, wait)
        mr_list = scrape_master_rate(driver, wait)
        print("MR Results:")
        print(mr_list)
        output_file = f"master_rate_{target_player_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(mr_list, f, indent=4)
        print("Saved JSON:", output_file)
    finally:
        driver.quit()
if __name__ == "__main__":
    main()