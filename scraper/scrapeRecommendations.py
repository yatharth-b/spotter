from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import defaultdict
from selenium.webdriver.chrome.options import Options
from requests_html import HTMLSession

import pickle

chrome_options = Options()
# chrome_options.add_argument("--headless")

session = HTMLSession()

product_list = []

scraped = defaultdict(list)

for i in range(6):
  r = session.get(f'https://www.hollisterco.com/shop/us/mens-tops?filtered=true&rows=90&start={i * 90}')

  product_list.extend([i for i in list(r.html.links) if i.startswith("/shop/us/p/")])

def get_rec_images(url):
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "stylitics-widget")))
        temp = driver.find_elements(By.CLASS_NAME, "stylitics-card")
        links = []
        for i in range(1, len(temp) + 1):
            xpath_link = f"/html/body/main/section[1]/div[2]/section/div/div/div/div[1]/div/div[{i}]/div/div[3]/div[1]"
            links.append((driver.find_element('xpath', xpath_link)).get_attribute("data-src"))
            
        meta_tag = driver.find_element('css selector', 'meta[property="og:image"]')

        # Get the content attribute value
        og_image_content = meta_tag.get_attribute("content")      
        return links, og_image_content
    except Exception as e:
        print(e)

j = 0

for i in product_list:
    x = get_rec_images('https://www.hollisterco.com/' + i)
    scraped[i] = x
    with open("recommendation_links_dictionary.pickle", 'wb') as file:
        pickle.dump(scraped, file)
        
    print(j)
    j += 1

print(f'Dictionary saved to recommendation_links_dictionary.pickle')