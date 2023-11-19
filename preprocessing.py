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
from firebase_admin import credentials, firestore
import firebase_admin

load_dotenv()

cred = credentials.Certificate("spotter-2a1c2-firebase-adminsdk-ns8jf-213c25fac2.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

collection_ref = db.collection('clothes')

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

  index = pinecone.Index("spotter")

  big_id_set = set()

  _, main_doc_ref = collection_ref.add({'recommend': [], 'link': main_link, "desc": main_desc})
  main_doc_ref = main_doc_ref.id

  for i in range(len(groups)):
    vector_group = groups[i] # Now I have multiple vectors in this. Make a row for each of them
    small_id_list = []

    for k in range(len(vector_group)):
      example_schema = {"recommend": [], "link": "", "desc": descriptions[i][k]}
      _, new_doc_ref = collection_ref.add(example_schema)
      small_id_list.append(new_doc_ref.id) 
    
    #Now add recommendatinos

    for k, small_id in enumerate(small_id_list):
      # add to pinecone as well

      index.upsert(
         [
            (str(small_id), vector_group[k])
         ]
      )

      doc_ref = collection_ref.document(small_id)
      final_answer = [i for i in small_id_list]
      final_answer.remove(small_id)
      final_answer.append(main_doc_ref)
      doc_ref.update({'recommend': final_answer})
    
    big_id_set.update(small_id_list)
  
  doc_ref = collection_ref.document(str(main_doc_ref))
  big_id_set = list(big_id_set)
  doc_ref.update({'recommend': big_id_set})

  index.upsert(
    [
      (str(main_doc_ref), main_vector)
    ]
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

