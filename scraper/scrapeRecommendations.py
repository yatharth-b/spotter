from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_rec_images(url):
    driver = webdriver.Chrome()
    driver.get(url)
    #wait for the div id called "stylistics-widget" to load
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "stylitics-widget")))
    temp = driver.find_elements(By.CLASS_NAME, "stylitics-card")
    links = []
    for i in range(1, len(temp) + 1):
        xpath_link = f"/html/body/main/section[1]/div[2]/section/div/div/div/div[1]/div/div[{i}]/div/div[3]/div[1]"
        links.append((driver.find_element('xpath', xpath_link)).get_attribute("data-src"))        
    return links
