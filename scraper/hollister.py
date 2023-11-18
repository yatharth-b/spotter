from selenium import webdriver

from selenium.webdriver.chrome.service import Service

service = Service(executable_path='./chromedriver.exe')

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

driver.get('https://www.hollisterco.com/')