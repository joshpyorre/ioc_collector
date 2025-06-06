# database utilities

from pymongo import MongoClient
import warnings
from bson import ObjectId
from datetime import datetime
import os

geoip_data_path = 'lib/GeoLite2-City.mmdb'

client = MongoClient("mongodb://localhost:27017/")
db = client.geoip_db
collection_geo = db.geo_url_results