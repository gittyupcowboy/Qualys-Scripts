import requests
import os
from xml.etree.ElementTree import fromstring, ParseError, tostring
import logging
import re
from qualys_config import QUALYS_USERNAME, QUALYS_PASSWORD, QUALYS_FO_API_URL

# Configuration Variables
SCAN_PROFILE_ENDPOINT = f"{QUALYS_FO_API_URL}/api/2.0/fo/subscription/option_profile/"
OUTPUT_DIRECTORY = "scan_profiles"

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIRECTORY):
    try:
        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
        print(f"Created output directory: {OUTPUT_DIRECTORY}")
    except OSError as e:
        print(f"Error creating output directory: {e}")
        exit(1)

# Configure logging
logging.basicConfig(filename='scan_profiles_export.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# API Request Configuration
headers = {
    'X-Requested-With': 'QualysAPI'
}

# Data parameters to export all profiles
export_data = {
    'action': 'export',
    'output_format': 'XML',
    'include_system_option_profiles': '1'  # Include all system profiles
}


def sanitize_filename(filename):
    """
    Sanitize a filename by removing or replacing invalid characters.
    :param filename: Original filename.
    :return: Sanitized filename.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def save_scan_profile(profile_id, profile_name, content):
    """
    Save a scan profile to a file, each profile in a separate file.
    :param profile_id: Profile ID for naming purposes.
    :param profile_name: Profile Name for filename.
    :param content: The XML content to save.
    """
    safe_name = sanitize_filename(f"profile_{profile_id}_{profile_name}.xml")
    file_path = os.path.join(OUTPUT_DIRECTORY, safe_name)

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Saved profile {profile_name} to {file_path}")
        logging.info(f"Saved profile {profile_name} to {file_path}")
    except Exception as err:
        print(f"Failed to save profile {profile_name}. Error: {err}")
        logging.error(f"Failed to save profile {profile_name}. Error: {err}")


def main():
    # API Request to export all scan profiles
    response = requests.get(SCAN_PROFILE_ENDPOINT, headers=headers, params=export_data,
                            auth=(QUALYS_USERNAME, QUALYS_PASSWORD))

    if response.status_code == 404:
        print("404 - Endpoint not found. Please verify the QUALYS_FO_API_URL and the endpoint path.")
        return
    elif response.status_code != 200:
        print(f"Failed to get scan profiles. Status Code: {response.status_code}, Response: {response.text}")
        return

    # Parse the response and save each scan profile
    response_xml = response.text

    try:
        root = fromstring(response_xml)

        for profile in root.findall(".//OPTION_PROFILE"):  # Assuming OPTION_PROFILE is the tag to extract
            basic_info = profile.find('BASIC_INFO')
            if basic_info is None:
                print(f"Skipping profile due to missing BASIC_INFO: {tostring(profile, encoding='unicode')}")
                logging.warning(
                    f"Skipping profile due to missing BASIC_INFO: {tostring(profile, encoding='unicode')}")
                continue

            profile_id_elem = basic_info.find('ID')
            profile_name_elem = basic_info.find('GROUP_NAME')

            if profile_id_elem is None or profile_name_elem is None:
                print(f"Skipping profile due to missing ID or GROUP_NAME: {tostring(profile, encoding='unicode')}")
                logging.warning(
                    f"Skipping profile due to missing ID or GROUP_NAME: {tostring(profile, encoding='unicode')}")
                continue

            profile_id = profile_id_elem.text
            profile_name = profile_name_elem.text

            # Save each scan profile directly
            save_scan_profile(profile_id, profile_name, tostring(profile, encoding='unicode'))
    except ParseError as err:
        print(f"Error parsing XML response: {err}")
        logging.error(f"Error parsing XML response: {err}")


if __name__ == "__main__":
    main()
