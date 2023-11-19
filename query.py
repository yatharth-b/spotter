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
# client = MongoClient(os.getenv('MONGO_CONNECT_URI'))
# collection = client.get_database("Spotter").SpotterClothesData


def get_matches(vector, k=5, include_string=False):
    return index.query(vector, top_k=k, include_values=include_string)

def query(input_string, threshold=5):
    vector = text_to_vector(input_string)
    res = [] # this stores links
    res_id = [] # this stores ids of those links (not storing vector because OOM??)

    ## Following in pants matches
    matches = get_matches(vector, 5, True)
    print([match['score'] for match in matches['matches']])
    
    ids = [match["id"] for match in matches["matches"]] 
    print(ids)

    for id in ids:
        doc_ref = clothes_collection.document(id)
        print(doc_ref.get().to_dict().get("desc"))

    # for id in ids:
    #     row = collection.find_one({"_id": ObjectId(id)}).get('desc')
    #     print(row)
    #     print("\n\n")
    

    # # Now looking to the recommendation of pant ids in mongodb
    # for main_item_id in ids:
    #     row = collection.find_one({"_id": ObjectId(main_item_id)})
    #     recommendations = row.get("recommended")
    #     for rec_id in recommendations:
    #         # check if link exists
    #         link = collection.find_one({"_id": rec_id}).get("link")
    #         if link != "":
    #             res.append(link)
    #             res_id.append(rec_id)
    
    # res_index = 0

    # while len(res_id) < threshold:
    #     # Now search database for similar shirts using res shirts
    #     vector = ""
    #     for map in index.fetch([str(res_id[res_index])])['vectors']:
    #         vector = index.fetch([str(res_id[res_index])])['vectors'][map]['values']
    #         break

    #     # matches = index.query(vector = vector, top_k = 3, include_values=False)
    #     matches = get_matches(vector, 3, False)
    #     ids = [match["id"] for match in matches["matches"]]

    #     for id in ids:
    #         link = collection.find_one({"_id": ObjectId(id)}).get("link")
    #         if link:
    #             res.append(link)
    #             res_id.append(id)

    #     res_index += 1

    # return res

if __name__ == "__main__":
# print(get_descriptions("https://img.hollisterco.com/is/image/anf/KIC_330-1504-1117-475_prod1?policy=product-extra-large", compress=True))
    desc = "The clothing item is a pair of men's jogger pants in a solid khaki color. The waistband is elasticated and features a contrasting black drawstring for adjustable fit. There are two slant pockets on either side, and the back appears to be clean without any visible pockets from this angle. The pants have a relaxed fit through the hips and thighs, tapering down to the ankles, where they are finished with elasticated cuffs, giving them a slight ruched effect. The fabric appears to be a soft, lightweight cotton blend, suitable for casual wear. There is a small, rectangular black label stitched on the right-hand side at the waistband, possibly indicating the brand or size. The stitching is neat, with a vertical seam running down the middle of each leg, contributing to the overall structured look of the joggers."
    print(query(desc, threshold=3))
