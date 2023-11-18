import openai

response = openai.chat.completions.create(
  model="gpt-4-vision-preview",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Describe every (or the only) clothing item in these image in detail, be sure to pay attention to little things in the clothing items. Do not talk about the relative positioning of the items, meaning talk about each of the items out of context of the image - as if they were a seperate image. ONLY return the descriptions of the items seperate by a new line."},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://img.hollisterco.com/is/image/anf/KIC_332-3037-1777-235_prod2.jpg?policy=product-large",
          },
        },
      ],
    }
  ],
  max_tokens=300,
)

print(response)


# import requests

# print(requests.get("https://www.hollisterco.com/"))