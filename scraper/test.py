# import openai

# openai.api_key = "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"

# # client = OpenAI()s

# response = openai.chat.completions.create(
#   model="gpt-4-vision-preview",
#   messages=[
#     {
#       "role": "user",
#       "content": [
#         {"type": "text", "text": "Describe every (or the only) clothing item in this image in detail, be sure to pay attention to little things in the clothing items. Do not talk about the relative positioning of the items, meaning talk about each of the items out of context of the image - as if they were a seperate image. ONLY return the descriptions of the items seperate by a new line."},
#         {
#           "type": "image_url",
#           "image_url": {
#             "url": "https://cdn.discordapp.com/attachments/588057941714927625/1175276045558108262/IMG20231117222716.jpg?ex=656aa41c&is=65582f1c&hm=9516bb3c9e4a521e54b4fefc3d2a7f5eb1ada2129952d8baf6a350268cacfa08&",
#           },
#         },
#       ],
#     }
#   ],
#   max_tokens=300,
# )

# print(response.choices[0])


import requests

print(requests.get("https://www.hollisterco.com/"))