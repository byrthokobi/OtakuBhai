from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["otaku_bhai_first"]  # Database name

# Collections
users_collection = db["users"]
conversations_collection = db["conversations"]
