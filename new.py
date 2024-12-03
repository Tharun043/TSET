from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

chrome_version = "131.0.6778.86"  # Replace with your Chrome version, e.g., "117.0.5938.88"
options = Options()
options.headless = False
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager(version=chrome_version).install()),
    options=options
)

driver.get("https://www.google.com")
input("Press Enter to close the browser...")
driver.quit()
