# asset-group_bulk-dns-add.py
# Script to Batch Add Hostnames to an Asset Group by GroupID

# The Qualys web UI imposes a 20,000-character limit for bulk adding
# hostnames to asset groups, which is quite restrictive. Our use case
# involves the reorganization and addition of new departments, resulting
# in approximately 500-1,000 hosts per save (depending on the subdomain
# and hostname). This process necessitates saving the changes, re-searching
# for the asset group, adding the next batch, and saving again—leading to
# far too many clicks.

import requests
import time
import xml.etree.ElementTree as ET
from qualys_config import QUALYS_USERNAME, QUALYS_PASSWORD

# Define the Qualys API URL explicitly
QUALYS_API_URL = "https://qualysapi.qualys.com/api/2.0/fo/asset/group/"


def read_hostnames(file_path):
    """Read hostnames from the specified file and return a list."""
    with open(file_path, 'r') as file:
        hostnames = file.read().splitlines()
    return hostnames


def get_asset_group_title(asset_group_id):
    """Retrieve and return the title of the asset group by ID."""
    url = QUALYS_API_URL
    headers = {
        'X-Requested-With': 'Curl'
    }
    data = {
        'action': 'list',
        'ids': asset_group_id,
        'show_attributes': 'TITLE'  # Only fetch the TITLE attribute
    }
    try:
        response = requests.post(url, headers=headers, data=data, auth=(QUALYS_USERNAME, QUALYS_PASSWORD))

        if response.status_code == 404:
            print("404 Error: The asset group could not be found. Please check the asset group ID.")
            raise Exception("Asset group not found. Please verify the asset group ID and permissions.")

        response.raise_for_status()

        asset_group_title = parse_asset_group_title(response.text)
        if asset_group_title is None:
            raise Exception("Failed to parse the asset group title from the API response.")
        return asset_group_title
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.content.decode()}")
        raise
    except Exception as err:
        print(f"An error occurred: {err}")
        raise


def parse_asset_group_title(xml_response):
    """Parse the XML response to extract the asset group title."""
    root = ET.fromstring(xml_response)
    title_element = root.find('.//TITLE')
    if title_element is not None:
        return title_element.text
    return None


def add_hostnames_to_asset_group(asset_group_id, hostnames, batch_size=1000):
    """Add hostnames to the specified asset group in batches to reduce latency."""
    url = QUALYS_API_URL
    headers = {
        'X-Requested-With': 'Curl'
    }

    response = requests.Response()  # Initialize response with a dummy value
    response.status_code = None  # Ensure there's a status_code attribute

    for i in range(0, len(hostnames), batch_size):
        batch = hostnames[i:i + batch_size]
        data = {
            'action': 'edit',
            'id': asset_group_id,
            'add_dns_names': ','.join(batch)  # Sending multiple hostnames in a single request
        }

        attempt = 0
        while attempt < 5:
            response = requests.post(url, headers=headers, data=data, auth=(QUALYS_USERNAME, QUALYS_PASSWORD))

            if response.status_code == 200:
                print(f"Batch of hostnames successfully added to asset group: {batch}")
                break
            elif response.status_code == 429:  # Rate limit exceeded
                retry_after = int(response.headers.get('X-RateLimit-ToWait-Sec', 10))
                print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"Failed to add batch of hostnames. Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")
                break

            attempt += 1

        if response.status_code is None or response.status_code != 200:
            print("Failed to add some batches after multiple attempts.")
            break


def main():
    asset_group_id = input("Enter the Asset Group ID: ")
    try:
        asset_group_title = get_asset_group_title(asset_group_id)
        confirmation = input(f"Asset Group Title: {asset_group_title}. Is this correct? (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Exiting script.")
            return

        hostnames_file = 'hostnames.txt'
        hostnames = read_hostnames(hostnames_file)

        if hostnames:
            add_hostnames_to_asset_group(asset_group_id, hostnames)
        else:
            print("No hostnames found in the file.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
