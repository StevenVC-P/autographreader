import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    print("Launching Chrome...")
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(version_main=136, options=options)
    driver.get("https://www.google.com")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    print("✅ Success: Page loaded and element found.")

except Exception as e:
    print(f"❌ Selenium test failed: {e}")

finally:
    try:
        driver.quit()
    except:
        pass
