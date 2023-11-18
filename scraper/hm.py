from requests_html import HTMLSession

session = HTMLSession()

res = []

for i in range(6):
  r = session.get(f'https://www2.hm.com/en_us/men/new-arrivals/clothes.html?sort=stock&image-size=small&image=model&offset=0&page-size=180')

  # res.extend([i for i in list(r.html.links) if i.startswith("/shop/us/p/")])
  print(r.html.links)  
print(len(res))