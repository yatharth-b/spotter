import openai
from dotenv import load_dotenv
import pinecone
from pymongo import MongoClient
import os
from bson.objectid import ObjectId
from example import vector_1

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")
openai.api_key = os.getenv("OPENAI_API_KEY") 


def main_image_scraper(chatgpt_main_image_description, id, scraped_main_image_link=None):
    main_image_vector = text_to_vector(chatgpt_main_image_description)
    index = pinecone.Index("spotter")
    index.upsert([
        {
            'id': id,
            'values': main_image_vector
        }
    ])
    # store main_image_vector with its link in redis
    # store in vector database



def text_to_vector(input):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=input
    )
    return response.data[0]['embedding']

def recommendation_image_scraper(input_string):
    reccomendations = input_string.split('\n\n')
    index = pinecone.Index("spotter")
    for rec in reccomendations:
        rec_vector = text_to_vector(rec)
        index.upsert([
        ("A", rec)
    ])
        
def query(input_string, threshold=5):
    # vector = text_to_vector(input_string)
    vector = vector_1
    index = pinecone.Index("spotter")
    res = [] # this stores links
    res_id = [] # this stores ids of those links (not storing vector because OOM??)

    ## Following in pants matches
    matches = index.query(
        vector=vector,
        top_k=5,
        include_values=True
        )
    ids = []
    for match in matches["matches"]:
        ids.append(match["id"])

    # Now looking to the recommendation of pant ids in mongodb
    client = MongoClient(os.getenv('MONGO_CONNECT_URI'))
    collection = client.get_database("Spotter").SpotterClothesData

    for main_item_id in ids:
        row = collection.find_one({"_id": ObjectId(main_item_id)})
        recommendations = row.get("recommended")
        for rec_id in recommendations:
            # check if link exists
            link = collection.find_one({"_id": rec_id}).get("link")
            if link != "":
                res.append(link)
                res_id.append(rec_id)
    
    res_index = 0

    while len(res_id) < threshold:
        # Now search database for similar shirts using res shirts
        vector = ""
        for map in index.fetch([str(res_id[res_index])])['vectors']:
            vector = index.fetch([str(res_id[res_index])])['vectors'][map]['values']
            break

        matches = index.query(vector = vector, top_k = 3, include_values=False)

        for match in matches["matches"]:
            id = match["id"]
            
            link = collection.find_one({"_id": ObjectId(id)}).get("link")
            if link:
                res.append(link)
                res_id.append(id)

    return res

# def testing(input_string, id):
#     # main_image_scraper(input_string, id)
#     return 

# print(query("This is a denim jacket with a light blue, faded wash. It features a classic collar and button-up front with metal buttons that have a weathered finish. The jacket has two buttoned flap pockets at the chest and two side pockets as well. The cuffs also have button closures for adjustability. There is yellow stitching throughout the jacket, providing a contrast to the blue denim and adding reinforcement. Inside, there is a lining made from a soft, cream-colored sherpa material, which extends to the collar, giving the jacket additional warmth and a cozy appearance. The hem of the jacket is characterized by a distinct denim pattern, indicating a separate waistband construction, and the back might have seam patterns that suggest a structured fit."))
# testing("The t-shirt is black with a vivid graphic print on the front, displaying colorful artwork related to Georgia Tech, which includes a stylized yellow jacket character. The overall style is reminiscent of a rock band tour shirt, with bold lettering and illustrations emblazoned across the chest area", "Georgia Tech Shirt")
# testing("The pants are a rust-tone or reddish-brown color. They appear to be joggers, given their tapered and slim fit, as well as the visible gathered elastic at the ankles. The material seems soft and likely comfortable, hinting at a casual or athleisure style of clothing.", "Red Pants")
# testing("The shoes are a complex design of sneakers with a blend of earthy tones and splashes of color accents, notably black, white, and gray with hints of bright orange. They feature a mix of materials, including what appears to be mesh, suede, and rubber. The design is intricate with panels and different textures and also reveals an exposed foam tongue, which is characteristic of certain styles of performance or lifestyle sneakers. The laces are looped through a set of eyelets in a traditional fastening fashion.", "Pranay Shoes")
# testing("The denim jacket has a classic blue wash with a button-front closure, featuring two chest flap pockets with button closures and two side welt pockets. It has a contrasting cream-colored sherpa lining on the collar and stitching details throughout", "Another denim jacket")
# print(query("The denim jacket is a classic trucker-style garment with a light blue wash and faded details for a worn-in look. It showcases a contrasting sherpa lining at the collar, which adds a plush texture and warmth to the design. The jacket includes features like buttoned chest flap pockets, side welt pockets, buttoned cuffs, and adjustable buttoned waist tabs. The front closure is buttoned, and the jacket contains visible paneling and stitching that are characteristic of traditional denim construction"))