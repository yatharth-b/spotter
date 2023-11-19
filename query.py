from preprocessing import text_to_vector, get_descriptions
import pinecone
from dotenv import load_dotenv
# from pymongo import MongoClient
from bson.objectid import ObjectId
from preprocessing import clothes_collection
import os

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")
index = pinecone.Index("spotter")

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

if __name__ == "__main__":
    # desc = get_descriptions("https://img.hollisterco.com/is/image/anf/KIC_328-3945-0007-120_prod1?policy=product-extra-large", compress=True).choices[0].message.content
    desc = "Light gray athletic shorts with an elastic waistband. There is visible hemming along the bottom edges and at the ends of built-in slits on the sides, enhancing mobility. On the left side, a vertical zipper pocket is integrated seamlessly into the fabric. The shorts appear to be made from a lightweight, possibly moisture-wicking material, appropriate for exercise. There is a subtle logo or text on the lower left leg, indicating the brand or product line."
    print(query(desc, threshold=3))
