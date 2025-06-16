import sys, re, requests, ipaddress, csv
from urllib.parse import urlparse

VT_API_KEY = "your_VT_api_key"  # Replace with your actual API key
VT_FILES_URL = "https://www.virustotal.com/api/v3/files/"
VT_IP_URL = "https://www.virustotal.com/api/v3/ip_addresses/"
VT_DOMAIN_URL = "https://www.virustotal.com/api/v3/domains/"

def extract_domain(ioc):
    if "." in ioc and not ioc.startswith(("http://", "https://")):
        ioc = "http://" + ioc
    try:
        parsed = urlparse(ioc)
        return parsed.netloc if parsed.netloc else ioc
    except Exception:
        return ioc

# def is_sha256(ioc):
#     return bool(re.fullmatch(r"[A-Fa-f0-9]{64}", ioc))

def is_hash(ioc):
    if re.fullmatch(r"[A-Fa-f0-9]{32}", ioc):  # MD5 (32 hex)
        return "md5"
    elif re.fullmatch(r"[A-Fa-f0-9]{40}", ioc):  # SHA1 (40 hex)
        return "sha1"
    elif re.fullmatch(r"[A-Fa-f0-9]{64}", ioc):  # SHA256 (64 hex)
        return "sha256"
    else:
        return False


def extract_ip(ioc):
    return ioc.split(":")[0] # Strip port if present

def is_ip_address(ioc):
    try:
        ipaddress.ip_address(ioc)
        return True
    except ValueError:
        return False

def get_virustotal_domain_info(domain):
    
    url = f"{VT_DOMAIN_URL}{domain}"
    headers = {
        "accept": "application/json",
        "x-apikey": VT_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []

        data = response.json().get("data", {})
        attr = data.get("attributes", {})
        dns_records = attr.get("last_dns_records", [])

        a_records = [record["value"] for record in dns_records if record.get("type") == "A"]
        return a_records

    except Exception as e:
        print(f"Error querying VirusTotal for domain {domain}: {e}")
        return []


def get_virustotal_ip_info(ip):
    url = f"{VT_IP_URL}{ip}"
    headers = {
        "accept": "application/json",
        "x-apikey": VT_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None

        data = response.json().get("data", {})
        attr = data.get("attributes", {})
        as_owner = attr.get("as_owner", "N/A")
        country = attr.get("country", "N/A")

        # IOC status calculation from last_analysis_stats (same logic as SHA256 version)
        stats = attr.get('last_analysis_stats', {})
        if stats.get('malicious', 0) > 1:
            ioc_status = 'malicious'
        elif stats.get('harmless', 0) > 1:
            ioc_status = 'harmless'
        else:
            ioc_status = 'unknown'

        # Extract registration event_date from RDAP (same as SHA256 version)
        rdap = attr.get('rdap', {})
        event_date = None
        for event in rdap.get('events', []):
            if event.get("event_action") == "registration":
                event_date = event.get("event_date")
                break

        return {
            "ip": data.get("id", ip),
            "as_owner": as_owner,
            "country": country,
            "result": ioc_status,
            "event_date": event_date or "N/A"
        }

    except Exception as e:
        print(f"Error querying VirusTotal for IP {ip}: {e}")
        return None

        
def get_virustotal_contacted_ips(sha256):
    url = f"{VT_FILES_URL}{sha256}/contacted_ips"
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

def parse_ioc_textfile(filename, output_csv):
    output_rows = []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 4:
                continue
            date = parts[0].strip()
            ioc = parts[1].strip()
            label = parts[3].strip()
            domain = extract_domain(ioc)

            # if is_sha256(ioc):
            hash_type = is_hash(ioc)
            if hash_type:
                ip_data = get_virustotal_contacted_ips(ioc)
                for entry in ip_data:
                    print(hash_type + ":\t", date, ioc, hash_type, entry["ip"], entry["as_owner"], label, entry["country"], entry["result"], entry["event_date"])
                    output_rows.append([
                        date, ioc, hash_type, entry["ip"], entry["as_owner"], label, entry["country"],
                        entry["result"], entry["event_date"]
                    ])
            else:
                ip_candidate = extract_ip(ioc)
                if is_ip_address(ip_candidate):
                    entry = get_virustotal_ip_info(ip_candidate)
                    if entry:
                        print("IP:\t", date, ioc, "ip", entry["ip"], entry["as_owner"], label, entry["country"],entry["result"], entry["event_date"])
                        output_rows.append([
                            date, ioc, "ip", entry["ip"], entry["as_owner"], label, entry["country"],
                            entry["result"], entry["event_date"]
                        ])

                else:
                    # Handle domain
                    domain_name = extract_domain(ioc)
                    a_records = get_virustotal_domain_info(domain_name)
                    for a_ip in a_records:
                        entry = get_virustotal_ip_info(a_ip)
                        if entry:
                            print("DOMAIN:\t", date, ioc, "domain", entry["ip"], entry["as_owner"], label, entry["country"], entry["result"], entry["event_date"])
                            output_rows.append([
                                date, ioc, "domain", entry["ip"], entry["as_owner"], label, entry["country"],
                                entry["result"], entry["event_date"]
                            ])

    # Write to CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["date", "ioc_input", "ioc_type", "ip", "as_owner", "label", "country", "result", "registration_date"])
        writer.writerows(output_rows)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_iocs.py <textfile>")
    else:
        input_file = sys.argv[1]
        # output_file = str(input_file).split("/")[1].split("_")[0].split('.txt')[0] + "_parsed.csv"
        output_file = "output_parsed.csv"
        parse_ioc_textfile(input_file, output_file)