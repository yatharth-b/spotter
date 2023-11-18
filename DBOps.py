import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pinecone


def del_mongo():
    load_dotenv()
    client = MongoClient(os.getenv('MONGO_CONNECT_URI'))

    database = client['Spotter']  # Replace 'mydatabase' with your actual database name
    collection = database['SpotterClothesData']  # Replace 'mycollection' with your actual collection name

    # Clear all documents from the collection
    result = collection.delete_many({})

    # Print the result (number of documents deleted)
    print(f"{result.deleted_count} documents deleted from the collection.")  

def del_pinecone():
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")
    pinecone.delete_index("spotter")

def create_vector_db_index():
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")
    pinecone.create_index("spotter", dimension = 1536, metric = "cosine", pod_type="starter")

del_mongo()
del_pinecone()
create_vector_db_index()