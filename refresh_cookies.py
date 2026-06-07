import json
import time
import os
import base64
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

LOGIN_URL = "https://cid.capcom.com/ja/login/?guidedBy=web"
BUCKLER_LOGIN_URL = "https://www.streetfighter.com/6/buckler/auth/loginep?redirect_url=/"
SELECT_PLATFORM_URL_PART = "/auth/select-platform"
# Use environment variable if available, otherwise use default Windows path
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', r"C:\WebDriver\chromedriver.exe")
COOKIES_FILE = "session_cookies.json"


def normalize_text(value: str) -> str:
    """Normalize text for comparison"""
    return " ".join(value.strip().lower().split())


def close_cookie_popup(driver):
    """Close cookie consent popup if present"""
    try:
        btn = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonAccept")
        driver.execute_script("arguments[0].click();", btn)
    except (NoSuchElementException, Exception):
        pass


def select_platform_and_submit(driver, wait, platform_variable):
    """Select platform (e.g., PlayStation) and submit"""
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


def login(username, password, platform="playstation"):
    """Login to Capcom ID, navigate to Buckler, select platform, and save cookies"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1440,1200")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Additional options for stability
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(CHROMEDRIVER_PATH),
        options=options
    )

    wait = WebDriverWait(driver, 60)  # Increased timeout to 60 seconds

    try:
        # Step 1: Login to Capcom ID
        print("Step 1: Logging in to Capcom ID...")
        driver.get(LOGIN_URL)
        
        # Wait for page to fully load
        print("Waiting for page to load...")
        time.sleep(5)  # Give page time to start loading
        
        # Wait for document ready
        for i in range(30):  # Try for up to 30 seconds
            try:
                if driver.execute_script("return document.readyState") == "complete":
                    print("Page loaded successfully")
                    break
            except:
                pass
            time.sleep(1)
            print(f"Still waiting... ({i+1}s)")
        
        # Additional wait for Auth0 widget to initialize
        time.sleep(5)
        
        print("Looking for Auth0 iframe...")
        print(f"Current URL: {driver.current_url}")
        
        # Auth0 login is typically in an iframe, try to switch to it
        email_box = None
        iframe_found = False
        
        for attempt in range(10):
            try:
                # Look for Auth0 iframe
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                print(f"Found {len(iframes)} iframes on page")
                
                for idx, iframe in enumerate(iframes):
                    try:
                        driver.switch_to.frame(iframe)
                        # Try to find the email field in this iframe
                        email_box = driver.find_element(By.ID, "1-email")
                        if email_box.is_displayed():
                            print(f"Email field found in iframe {idx} on attempt {attempt + 1}")
                            iframe_found = True
                            break
                    except:
                        driver.switch_to.default_content()
                        continue
                
                if iframe_found:
                    break
                    
                # If not in iframe, try in main content
                driver.switch_to.default_content()
                email_box = driver.find_element(By.ID, "1-email")
                if email_box.is_displayed():
                    print(f"Email field found in main content on attempt {attempt + 1}")
                    iframe_found = True
                    break
                    
            except:
                driver.switch_to.default_content()
                pass
            
            time.sleep(2)
            print(f"Email field not found yet, attempt {attempt + 1}/10")
        
        if not iframe_found or email_box is None:
            # Save screenshot for debugging
            driver.save_screenshot("login_page_error.png")
            print("Saved screenshot to login_page_error.png")
            print(f"Page source length: {len(driver.page_source)}")
            raise RuntimeError("Could not find email field after 10 attempts")
        
        print("Email field found, entering username...")
        
        # Clear any existing value first
        email_box.clear()
        time.sleep(0.5)
        
        # Enter email using send_keys (more reliable than JavaScript)
        email_box.click()
        time.sleep(0.5)
        email_box.send_keys(username)
        time.sleep(0.5)
        
        # Verify the value was entered
        entered_value = email_box.get_attribute('value')
        print(f"Email entered: {entered_value}")
        
        if entered_value != username:
            print("Email not entered correctly, trying JavaScript method...")
            driver.execute_script(f"arguments[0].value = '{username}';", email_box)
            # Trigger input event to ensure Auth0 recognizes the change
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_box)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", email_box)
            time.sleep(0.5)

        # Password field
        print("Looking for password field...")
        password_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        password_box.click()
        time.sleep(0.5)
        password_box.send_keys(password)
        time.sleep(0.5)

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

        print("Login successful!")
        print(f"Current URL: {driver.current_url}")

        # Step 2: Navigate to Buckler and handle platform selection
        print("\nStep 2: Navigating to Buckler...")
        driver.get(BUCKLER_LOGIN_URL)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
        # Close cookie popup if present
        close_cookie_popup(driver)
        
        # Step 3: Select platform if needed
        if SELECT_PLATFORM_URL_PART in driver.current_url:
            print(f"\nStep 3: Selecting {platform} platform...")
            select_platform_and_submit(driver, wait, platform)
            print("Platform selected successfully!")
        else:
            print("\nStep 3: Platform selection not required (already set)")
        
        # Give the page time to fully load after platform selection
        time.sleep(2)
        
        print(f"Final URL: {driver.current_url}")
        
        # Step 4: Save cookies
        print("\nStep 4: Saving session cookies...")
        cookies = driver.get_cookies()
        save_cookies(cookies)
        print("\n✓ Login complete! Cookies saved successfully.")

    except Exception as e:
        print(f"\n✗ Login failed: {e}")
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    # Use environment variables for credentials
    username = "your_email@example.com"
    password = "your_password"
    platform = os.getenv('PLATFORM', 'playstation')
    
    if not username or not password:
        print("Error: CAPCOM_USERNAME and CAPCOM_PASSWORD environment variables must be set")
        exit(1)

    login(username, password, platform)

# Made with Bob
