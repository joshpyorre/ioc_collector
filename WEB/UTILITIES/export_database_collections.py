from pymongo import MongoClient
import json
from bson import ObjectId
from datetime import datetime

# Connect to MongoDB on the current computer
client = MongoClient("mongodb://localhost:27017/")

# Access the database
db = client.geoip_db

# Define the collections
collections = {
    "geo_url_results": db.geo_url_results
}

# Custom JSON encoder to handle ObjectId and datetime
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime to string
        return super(JSONEncoder, self).default(obj)

# Function to export collection to a JSON file
def export_collection_to_json(collection_name, collection):
    data = list(collection.find())  # Retrieve all documents from the collection
    with open(f"{collection_name}.json", "w") as file:
        json.dump(data, file, indent=4, cls=JSONEncoder)
    print(f"Exported {collection_name} to {collection_name}.json")

# Export each collection
for collection_name, collection in collections.items():
    export_collection_to_json(collection_name, collection)