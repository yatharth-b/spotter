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
  items = text.split('\n')
  items = [i for i in items if i != ""]
  items = [text_to_vector(i) for i in items]
  if len(items) == 1:
    return items[0]
  
  return items

def description_split(text : str):
    items = text.split('\n')
    items = [i for i in items if i != ""]

    if len(items) == 1:
      return items[0]
    
    return items

def text_to_vector(input):
  response = openai.embeddings.create(
      model="text-embedding-ada-002",
      input=input
  )
  return response.data[0].embedding

def get_most_similar_index(input_vector, vector_list):
    ## error comes when vector_list is 
    similarities = [1 - cosine(input_vector, vector) for vector in vector_list]
    most_similar_index = np.argmax(similarities)
    return most_similar_index

def gpt_to_mongo(main_link, main_vector, groups, descriptions, main_desc):
  for i in range(len(groups)):
    index = get_most_similar_index(main_vector, groups[i])
    descriptions[i].pop(index)
    groups[i].pop(index)
    ## Mongo entries
  vec_list = [element for row in groups for element in row]
  desc_list = [element for row in descriptions for element in row]
  vec_list.append(main_vector)
  desc_list.append(main_desc)
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
    collection.insert_one({"_id": id_list[i], "recommended": [k for k in id_list if k != id_list[i]], "link": "", "desc": desc_list[i]})
  
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
  # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
  #   # Submit API calls to the executor
  #   futures = [executor.submit(get_descriptions, url, True) for url in recommendation_links]
  #   futures.append(executor.submit(get_descriptions, main_link, True))

  #   # Wait for all API calls to complete
  #   concurrent.futures.wait(futures)

  with open("temp_test.pickle", 'rb') as file:
     results = pickle.load(file)
  
  # results = [future.result().choices[0].message.content for future in futures]

  # with open("temp_test.pickle", 'wb') as file:
  #   pickle.dump(results, file)

  results_descs = [description_split(i) for i in results]
  results_vectors = [vectorize_gpt_text(i) for i in results]
  
  # main_link, main_vector, groups, descriptions, main_desc
  return gpt_to_mongo(product_link, results_vectors[-1], results_vectors[:-1], results_descs[:-1], results_descs[-1])

with open("scraper/recommendation_links_dictionary.pickle", 'rb') as file:
  product_data = pickle.load(file)

count = 0
for product_link in product_data:
  if len(product_data[product_link][0]) == 0:
    continue
  count += 1
  gpt_calls(product_link, product_data[product_link][0], product_data[product_link][1])
  if count == 3:
      break
#   break

# gpt_to_mongo(main_link="http://example.com", main_vector=vector_1, groups=groups, descriptions=descs, main_desc=desc_1)

