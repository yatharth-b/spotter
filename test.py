import pinecone
import os
from dotenv import load_dotenv

load_dotenv()

index_name = "Spotter"
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"),environment="gcp-starter")

index = pinecone.Index(index_name)
index.delete(delete_all=True)
