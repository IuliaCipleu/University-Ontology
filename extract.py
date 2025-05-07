import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


options = Options()
options.add_argument("--headless")

# Automatically download and use the correct ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://admitereonline.utcluj.ro/international-students/#tab-id-2")
time.sleep(5)
print(driver.page_source)

# Wait for the element to be present
wait = WebDriverWait(driver, 50)
tab_element = wait.until(EC.presence_of_element_located((By.ID, "#tab-id-2")))

# After ensuring the element is loaded, use BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# Extract the content of tab-id-2
tab = soup.find("div", id="#tab-id-2")
if tab is None:
    raise ValueError("tab is None")
text = tab.get_text(separator="\n", strip=True)

# Split by lines and process
lines = text.split("\n")

programs = []
current_level = ""

for line in lines:
    # Identify study level
    if "Study Programme B.Sc" in line:
        current_level = "Bachelor"
        continue
    elif "Study Programme M.Sc" in line:
        current_level = "Master"
        continue
    elif "Faculty" in line:
        continue  # skip header

    # Match program lines
    match = re.match(r"(.+?)\s+\((Cluj-Napoca|Satu Mare)\)\s+\((RO|EN|RO, EN|EN, RO)\)", line)
    if match:
        name = match.group(1).strip()
        location = match.group(2).strip()
        lang_codes = match.group(3).replace(" ", "").split(",")
        languages = ", ".join(["Romanian" if code == "RO" else "English" for code in lang_codes])
        programs.append((current_level, name, location, languages))

# Display results
for p in programs:
    print(f"{p[0]} | {p[1]} | {p[2]} | {p[3]}")
