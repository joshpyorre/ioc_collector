from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB connection string
db = client.geoip_db  # Replace with your database name
collection = db.geo_url_results  # Replace with your collection name

# Remove all entries from the collection
result = collection.delete_many({})

# Print the number of deleted documents
print(f"Deleted {result.deleted_count} documents from the geo_url_results collection.")

# Close the connection
client.close()
