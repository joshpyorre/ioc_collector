from pymongo import MongoClient
import json
from bson import ObjectId

# Connect to MongoDB on the new computer
client = MongoClient("mongodb://localhost:27017/")

# Access the target database
db = client.geoip_db

# Define the collections to import into
collections = {
    "geo_url_results": db.geo_url_results,
}

# Custom function to convert any '_id' back to ObjectId if it's a valid ObjectId string
def convert_to_objectid(data):
    if isinstance(data, str) and len(data) == 24:
        try:
            return ObjectId(data)
        except Exception:
            return data  # Return as is if conversion fails
    return data

# Function to import JSON data into a MongoDB collection
def import_json_to_collection(collection_name, collection):
    with open(f"{collection_name}.json", "r") as file:
        data = json.load(file)
        for doc in data:
            if "_id" in doc:
                doc["_id"] = convert_to_objectid(doc["_id"])  # Convert '_id' back to ObjectId
        collection.insert_many(data)
    print(f"Imported {collection_name}.json into {collection_name} collection")

# Import each collection from the corresponding JSON file
for collection_name, collection in collections.items():
    import_json_to_collection(collection_name, collection)