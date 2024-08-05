import requests
from requests.auth import HTTPBasicAuth
import csv
import xml.etree.ElementTree as ET
import qualys_config


def get_asset_group_details(asset_group_id):
    url = "https://qualysapi.qualys.com/api/2.0/fo/asset/group/"
    headers = {
        'X-Requested-With': 'QualysAPI'
    }
    data = {
        'action': 'list',
        'ids': asset_group_id,  # Note the parameter should be 'ids'
        'show_attributes': 'ALL'
    }
    try:
        response = requests.post(url, headers=headers, data=data,
                                 auth=HTTPBasicAuth(qualys_config.QUALYS_USERNAME, qualys_config.QUALYS_PASSWORD))
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching asset group details: {e}")
        if e.response:
            print(f"Response content: {e.response.content.decode()}")
        return None


def parse_assets(asset_group_xml):
    assets = {'dns': [], 'domains': [], 'ips': []}
    try:
        root = ET.fromstring(asset_group_xml)
        for asset_group in root.findall('.//ASSET_GROUP'):
            for dns in asset_group.findall('.//DNS'):
                assets['dns'].append(dns.text)
            for domain in asset_group.findall('.//DOMAIN'):
                assets['domains'].append(domain.text)
            for ip in asset_group.findall('.//IP'):
                assets['ips'].append(ip.text)
            for ip_range in asset_group.findall('.//IP_RANGE'):
                assets['ips'].append(ip_range.text)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    return assets


def save_assets_to_csv(assets, filename):
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Type', 'Value'])
            for dns in assets['dns']:
                writer.writerow(['DNS', dns])
            for domain in assets['domains']:
                writer.writerow(['Domain', domain])
            for ip in assets['ips']:
                writer.writerow(['IP', ip])
        print(f"Assets saved to {filename}")
    except IOError as e:
        print(f"Error saving assets to file: {e}")


def main():
    asset_group_id = input("Enter the Asset Group ID: ")
    filename = input("Enter the filename to save the results (with .csv extension): ")
    asset_group_xml = get_asset_group_details(asset_group_id)
    if asset_group_xml:
        print("Asset group XML successfully retrieved.")
        print(asset_group_xml)  # Print the raw XML response for debugging
        assets = parse_assets(asset_group_xml)
        if any(assets.values()):  # Check if there are any assets
            save_assets_to_csv(assets, filename)
        else:
            print("No assets found in the specified asset group.")
    else:
        print("Failed to retrieve asset group details.")


if __name__ == "__main__":
    main()
