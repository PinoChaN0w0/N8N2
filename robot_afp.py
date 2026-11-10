import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()

driver = webdriver.Firefox(options=options)
url = "https://mantistcy.cl/tendenciapensiones/"
data = []

try:
    driver.get(url)
    
   
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//table//tbody/tr')))
    
   
    rows = driver.find_elements(By.XPATH, '//table//tbody/tr')
    
   
    for row in rows:
        celdas = row.find_elements(By.TAG_NAME, "td")
        if len(celdas) >= 3 :
            name = celdas[2].text.strip().replace('\n', ' ')
            peso = celdas[4].text.strip()
            rentabilidad = celdas[5].text.strip()
            fondo =celdas[0].text.strip()
            data.append({
                'fondo':fondo,
                "name": name,
                "peso": peso,
                "rentabilidad": rentabilidad
            })
            
    
    print(json.dumps(data, indent=2, ensure_ascii=False))

finally:
    driver.quit()
