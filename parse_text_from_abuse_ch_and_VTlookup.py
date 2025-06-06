import sys, re, requests
from urllib.parse import urlparse

VT_API_KEY = "YOUR_VIRUSTOTAL_API_KEY"  # Replace with your actual API key
VT_BASE_URL = "https://www.virustotal.com/api/v3/files/"

def extract_domain(ioc):
    if "." in ioc and not ioc.startswith(("http://", "https://")):
        ioc = "http://" + ioc
    try:
        parsed = urlparse(ioc)
        return parsed.netloc if parsed.netloc else ioc
    except Exception:
        return ioc

def is_sha256(ioc):
    return bool(re.fullmatch(r"[A-Fa-f0-9]{64}", ioc))

def get_virustotal_contacted_ips(sha256):
    url = f"{VT_BASE_URL}{sha256}/contacted_ips"
    headers = {
        "accept": "application/json",
        "x-apikey": VT_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []

        results = []
        data = response.json().get("data", [])

        for entry in data:
            ip = entry.get("id", "")
            attr = entry.get("attributes", {})
            as_owner = attr.get("as_owner", "N/A")
            country = attr.get("country", "N/A")

            # Determine IOC status from last_analysis_stats
            stats = attr.get("last_analysis_stats", {})
            if stats.get('malicious', 0) > 1:
                ioc_status = 'malicious'
            elif stats.get('harmless', 0) > 1:
                ioc_status = 'harmless'
            else:
                ioc_status = 'unknown'

            # Look for registration event in RDAP
            rdap = attr.get('rdap', {})
            event_date = None
            for event in rdap.get('events', []):
                if event.get("event_action") == "registration":
                    event_date = event.get("event_date")
                    break

            results.append({
                "ip": ip,
                "as_owner": as_owner,
                "country": country,
                "result": ioc_status,
                "event_date": event_date or "N/A"
            })

        return results

    except Exception as e:
        print(f"Error querying VirusTotal for {sha256}: {e}")
        return []

def parse_ioc_textfile(filename):
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 4:
                continue
            date = parts[0].strip()
            ioc = parts[1].strip()
            label = parts[3].strip()
            domain = extract_domain(ioc)

            print(f"{date},{ioc},{domain},{label}")

            if is_sha256(ioc):
                ip_data = get_virustotal_contacted_ips(ioc)
                for entry in ip_data:
                    ip = entry["ip"]
                    owner = entry["as_owner"]
                    country = entry["country"]
                    result = entry["result"]
                    event_date = entry["event_date"] or "N/A"
                    print(f"{date},{ip},{owner},{label},country={country},result={result},registration_date={event_date}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_iocs.py <textfile>")
    else:
        parse_ioc_textfile(sys.argv[1])