import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "https://cid.capcom.com/ja/login/?guidedBy=web"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
COOKIES_FILE = "session_cookies.json"


def save_cookies(driver, filepath=COOKIES_FILE):
    cookies = driver.get_cookies()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)

    print(f"Saved {len(cookies)} cookies to {filepath}")


def login(username, password):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,1200")

    driver = webdriver.Chrome(
        service=Service(CHROMEDRIVER_PATH),
        options=options
    )

    wait = WebDriverWait(driver, 30)

    try:
        driver.get(LOGIN_URL)

        # Email / Username field
        email_box = wait.until(
            EC.element_to_be_clickable(
                (By.ID, "1-email")
            )
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            email_box
        )

        email_box.click()
        email_box.send_keys(username)

        # Password field
        password_box = driver.find_element(
            By.CSS_SELECTOR,
            "input[type='password']"
        )
        password_box.click()
        password_box.send_keys(password)

        # Submit button
        submit_button = driver.find_element(
            By.CSS_SELECTOR,
            "button[type='submit']"
        )
        submit_button.click()

        # Wait until login completes
        wait.until(
            lambda d: "login" not in d.current_url.lower()
        )

        print("Login successful")
        print(driver.current_url)

        # Give any redirects time to finish
        time.sleep(3)

        save_cookies(driver)

    finally:
        driver.quit()


if __name__ == "__main__":
    username = "your_email@example.com"
    password = "your_password"

    login(username, password)