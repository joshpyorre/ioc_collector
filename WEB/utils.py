# various utiliity functions
import socket, multiprocessing, tldextract,imagehash, os, Levenshtein, json, ipaddress
from threading import Lock
from geoip2.database import Reader
import pandas as pd
from collections import Counter
from PIL import Image

from models import collection_geo

geoip_data_path = 'lib/GeoLite2-City.mmdb'

def normalize_input(entry):
    entry = entry.strip()
    try:
        ipaddress.ip_address(entry)
        return entry  # It's an IP address
    except ValueError:
        if "." in entry and not entry.startswith(("http://", "https://")):
            entry = "http://" + entry
        try:
            parsed = urlparse(entry)
            return parsed.netloc if parsed.netloc else entry
        except Exception:
            return entry

def ip_to_location(ip): 
    try:
        with Reader(geoip_data_path) as reader:
            response = reader.city(ip)
            lat, lon = response.location.latitude, response.location.longitude
            return lat, lon
    except Exception:
        return None, None
    
def get_a_record_and_location(domain_or_ip):
    # Avoid reprocessing
    existing_entry = collection_geo.find_one({"domain": domain_or_ip})
    if existing_entry:
        return existing_entry if existing_entry.get('status') == 'success' else None

    try:
        # Handle IP directly
        ipaddress.ip_address(domain_or_ip)
        ip_address = domain_or_ip
        domain = None
    except ValueError:
        # Not an IP, resolve as domain
        try:
            ip_address = socket.gethostbyname(domain_or_ip)
            domain = domain_or_ip
        except Exception:
            collection_geo.insert_one({"domain": domain_or_ip, "status": "failure"})
            return None

    try:
        with Reader(geoip_data_path) as reader:
            response = reader.city(ip_address)
            result = {
                'domain': domain_or_ip,
                'a_record': ip_address,
                'city': response.city.name or "Unknown City",
                'country': response.country.name or "Unknown Country",
                'status': 'success'
            }
            collection_geo.insert_one(result)
            return result
    except Exception:
        collection_geo.insert_one({
            'domain': domain_or_ip,
            'status': 'failure'
        })
        return None
    
def generate_map_data_and_statistics(results):
    lats, lons, descriptions = [], [], []
    country_counts = Counter()

    for result in results:
        lat, lon = ip_to_location(result['a_record'])
        if lat is not None and lon is not None:
            lats.append(lat)
            lons.append(lon)
            descriptions.append(f"{result['city']}, {result['country']} (Domain: {result['domain']})")
            country_counts[result['country']] += 1

    map_data_df = pd.DataFrame({'description': descriptions, 'lat': lats, 'lon': lons})
    map_data = map_data_df.to_dict(orient='records')
    return map_data, country_counts

def process_urls_multiprocessing(inputs):
    normalized = list(set(normalize_input(i) for i in inputs if i.strip()))
    total = len(normalized)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(get_a_record_and_location, normalized)
    successful = [res for res in results if res]
    failures = total - len(successful)
    return successful, failures
