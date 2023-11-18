from requests_html import HTMLSession

session = HTMLSession()

res = []

for i in range(6):
  r = session.get(f'https://www.hollisterco.com/shop/us/mens-tops?filtered=true&rows=90&start={i * 90}')

  res.extend([i for i in list(r.html.links) if i.startswith("/shop/us/p/")])
  
print(len(res))
