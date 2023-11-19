from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import pinecone
from dotenv import load_dotenv
import os
import base64
import openai
from firebase_admin import credentials, firestore
import firebase_admin

app = Flask(__name__)
CORS(app)
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")
index = pinecone.Index("spotter")
cred = credentials.Certificate("../spotter-2a1c2-firebase-adminsdk-ns8jf-213c25fac2.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
clothes_collection = db.collection('clothes')


@app.route("/health")
def check_connectivity():
    return {"hello": "world"}

def text_to_vector(input):
  response = openai.embeddings.create(
      model="text-embedding-ada-002",
      input=input
  )
  return response.data[0].embedding

def get_matches(vector, k=5, include_string=False):
    return index.query(vector, top_k=k, include_values=include_string)

def query(input_string, threshold=5):
    vector = text_to_vector(input_string)
    res = [] # this stores links
    # res_id = [] # this stores ids of those links (not storing vector because OOM??)

    ## Following in pants matches
    matches = get_matches(vector, 5, True)
    print([match['score'] for match in matches['matches']])
    
    ids = [match["id"] for match in matches["matches"]] 
    print(ids)

    for id in ids:
        doc_ref = clothes_collection.document(id)
        print(doc_ref.get().to_dict().get("desc"))
        doc_recommendations =  doc_ref.get().to_dict().get("recommend")
        for recommend_id in doc_recommendations:
            recommendation_doc = clothes_collection.document(recommend_id)
            link = recommendation_doc.get().to_dict().get("link")
            if link != "":
                res.append(link)
    
    return res

def compress_image(input_bytes, output_image_path):
  original_image = Image.open(input_bytes)

  original_width, original_height = original_image.size

  new_width = original_width // 2
  new_height = original_height // 2

  resized_image = original_image.resize((new_width, new_height))

  resized_image.save(output_image_path)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

@app.route("/test/get_description", methods=["POST"])
def get_description():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'})
    image_base64 = data.get('base64_image')
    prompt = "Describe every (or the only) clothing item in these image in detail, be sure to pay attention to little things in the clothing items. Do not talk about the relative positioning of the items, meaning talk about each of the items out of context of the image - as if they were a seperate image. ONLY return the descriptions of the items seperate by a new line."
    # image_base64 = encode_image("../test_pants.png")

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
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    },
            },
          ],
        }
      ],
      max_tokens=300,
    )


    # print(response)
    final_list = query(response.choices[0].message.content)
    # print(final_list)

    return {"response": final_list}

