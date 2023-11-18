import openai
from PIL import Image
from io import BytesIO
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
import base64
import pickle
import os
from dotenv import load_dotenv
import pinecone
import numpy as np
from scipy.spatial.distance import cosine
import concurrent.futures

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")

def get_descriptions(link : str, compress : bool):

  prompt = "Describe every (or the only) clothing item in these image in detail, be sure to pay attention to little things in the clothing items. Do not talk about the relative positioning of the items, meaning talk about each of the items out of context of the image - as if they were a seperate image. ONLY return the descriptions of the items seperate by a new line."

  if compress:
    filename = f"{''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in link)}.png"
    bytes = download_image(link)
    compress_image(bytes, filename)

    response = openai.chat.completions.create(
      model="gpt-4-vision-preview",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": prompt },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image(filename)}",
              },
            },
          ],
        }
      ],
      max_tokens=300,
    )

    os.remove(filename)

  else:
    response = openai.chat.completions.create(
      model="gpt-4-vision-preview",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": prompt },
            {
              "type": "image_url",
              "image_url": {
                "url": link,
              },
            },
          ],
        }
      ],
      max_tokens=300,
    )

  return response

def compress_image(input_bytes, output_image_path):
  original_image = Image.open(input_bytes)

  original_width, original_height = original_image.size

  new_width = original_width // 2
  new_height = original_height // 2

  resized_image = original_image.resize((new_width, new_height))

  resized_image.save(output_image_path)

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise Exception(f"Failed to download image from {url}. Status code: {response.status_code}")
    
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def vectorize_gpt_text(text : str):
  items = text.split('\n\n')
  items = [text_to_vector(i) for i in items]
  
  if len(items) == 1:
    return items[0]
  
  return items

def text_to_vector(input):
  response = openai.embeddings.create(
      model="text-embedding-ada-002",
      input=input
  )
  # print(response)
  return response.data[0].embedding


# vector_1 = text_to_vector("This is a denim jacket with a light blue, faded wash. It features a classic collar and button-up front with metal buttons that have a weathered finish. The jacket has two buttoned flap pockets at the chest and two side pockets as well. The cuffs also have button closures for adjustability. There is yellow stitching throughout the jacket, providing a contrast to the blue denim and adding reinforcement. Inside, there is a lining made from a soft, cream-colored sherpa material, which extends to the collar, giving the jacket additional warmth and a cozy appearance. The hem of the jacket is characterized by a distinct denim pattern, indicating a separate waistband construction, and the back might have seam patterns that suggest a structured fit.")
# vector_2 = text_to_vector("The t-shirt is black with a vivid graphic print on the front, displaying colorful artwork related to Georgia Tech, which includes a stylized yellow jacket character. The overall style is reminiscent of a rock band tour shirt, with bold lettering and illustrations emblazoned across the chest area")
# vector_5 = text_to_vector("The pants are a rust-tone or reddish-brown color. They appear to be joggers, given their tapered and slim fit, as well as the visible gathered elastic at the ankles. The material seems soft and likely comfortable, hinting at a casual or athleisure style of clothing.")
# # testing("The shoes are a complex design of sneakers with a blend of earthy tones and splashes of color accents, notably black, white, and gray with hints of bright orange. They feature a mix of materials, including what appears to be mesh, suede, and rubber. The design is intricate with panels and different textures and also reveals an exposed foam tongue, which is characteristic of certain styles of performance or lifestyle sneakers. The laces are looped through a set of eyelets in a traditional fastening fashion.", "Pranay Shoes")
# vector_3 = text_to_vector("The denim jacket has a classic blue wash with a button-front closure, featuring two chest flap pockets with button closures and two side welt pockets. It has a contrasting cream-colored sherpa lining on the collar and stitching details throughout")
# vector_4 = text_to_vector("The denim jacket is a classic trucker-style garment with a light blue wash and faded details for a worn-in look. It showcases a contrasting sherpa lining at the collar, which adds a plush texture and warmth to the design. The jacket includes features like buttoned chest flap pockets, side welt pockets, buttoned cuffs, and adjustable buttoned waist tabs. The front closure is buttoned, and the jacket contains visible paneling and stitching that are characteristic of traditional denim construction")
# groups = [[vector_5, vector_2, vector_3], [vector_5, vector_4, vector_2]]


def drop_most_similar_vector(input_vector, vector_list):
  similarities = [1 - cosine(input_vector, vector) for vector in vector_list]
  most_similar_index = np.argmax(similarities)
  most_similar_vector = vector_list[most_similar_index]
  vector_list.remove(most_similar_vector)


def gpt_to_mongo(main_link, main_vector, groups):
  for group in groups:
    drop_most_similar_vector(main_vector, group)
  ## Mongo entries
  vec_list = [element for row in groups for element in row]
  vec_list.append(main_vector)
  id_list = []
  for i in range(len(vec_list)):
    id_list.append(ObjectId())

  index = pinecone.Index("spotter")
  for i in range(len(vec_list)):
    index.upsert([
    (str(id_list[i]), vec_list[i])
  ])  

  client = MongoClient(os.getenv('MONGO_CONNECT_URI'))
  collection = client.get_database("Spotter").SpotterClothesData
      
  for i in range(len(id_list)):
    collection.insert_one({"_id": id_list[i], "recommended": [k for k in id_list if k != id_list[i]], "link": ""})
  
  collection.update_one({
    "_id": id_list[-1]
    },
    {
      "$set": {
          "link": main_link
      }
    }
  )

'''
returns main_vector, [[vector_1, vector_2, ...], [vector_3, vector_4, ...]]
'''
def gpt_calls(product_link, recommendation_links, main_link):
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    # Submit API calls to the executor
    futures = [executor.submit(get_descriptions, url, True) for url in recommendation_links]
    futures.append(executor.submit(get_descriptions, main_link, True))

    # Wait for all API calls to complete
    concurrent.futures.wait(futures)

  results = [future.result().choices[0].message.content for future in futures]
  results = [vectorize_gpt_text(i) for i in results]

  # return gpt_to_mongo("https://example.com", vector_1, groups)
  # return product_link, results[-1], results[:-1]
  return gpt_to_mongo(product_link, results[-1], results[:-1])

with open("scraper/recommendation_links_dictionary.pickle", 'rb') as file:
  product_data = pickle.load(file)

for product_link in product_data:
  if len(product_data[product_link][0]) == 0:
    continue
  print(product_link)
  # gpt_calls(product_link, product_data[product_link][0], product_data[product_link][1])
  
  break



