# Qualys Script Collection

&nbsp; 

### Overview

This repository contains a collection of scripts designed to interact with the Qualys API for various security and compliance tasks. These scripts can faciliate the automation of tasks such as fetching vulnerability reports, managing assets, and other common operations to enhance workflows (assuming I ever upload the rest).  

---

&nbsp; 

### asset-group_bulk-dns-add.py

&nbsp;

**Script to Batch Add Hostnames to an Asset Group by GroupID**

This script is designed to efficiently add large numbers of DNS entries to a Qualys asset group via the Qualys API, bypassing the limitations of the Qualys web UI. It’s particularly useful in scenarios where you need to reorganize or expand asset groups across departments or projects. The script handles batching, API rate limits, and includes error handling mechanisms to ensure reliable execution.

#### Key Functions:

- **read_hostnames(file_path):**
  - Reads hostnames from a specified file (`hostnames.txt` by default) and returns them as a list. This allows for easy bulk input, facilitating batch processing.

- **get_asset_group_title(asset_group_id):**
  - Fetches and returns the title of the asset group by its GroupID. This is used to verify that the correct asset group is being modified, preventing potential errors from modifying the wrong group.

- **parse_asset_group_title(xml_response):**
  - Parses the XML response from the Qualys API to extract and return the asset group title. This function ensures the script interacts with the correct asset group and is used internally by `get_asset_group_title()`.

- **add_hostnames_to_asset_group(asset_group_id, hostnames, batch_size=1000):**
  - Adds DNS hostnames to the specified asset group in batches, reducing latency and minimizing the risk of exceeding API rate limits. The default batch size is set to 1,000 hostnames but can be adjusted as needed. 

  - **Error Handling & Retry Logic:**
    - If an API request fails due to rate limiting (HTTP 429), the script automatically waits for the specified time (`Retry-After` header or a default of 10 seconds) before retrying. This prevents unnecessary API throttling and ensures that all batches are eventually processed.
    - The script allows up to 5 retries per batch. If the script cannot successfully add a batch after 5 attempts, it reports a failure and moves on to the next batch, ensuring the process continues as smoothly as possible.

- **main():**
  - The entry point for the script. It prompts the user for the Asset Group ID, retrieves and confirms the asset group title, reads the hostnames from `hostnames.txt`, and initiates the batch addition process.
  
  - **Execution Flow:**
    - Prompts for Asset Group ID and confirms the title.
    - Reads the hostnames from a specified file.
    - Handles the addition of hostnames in batches, incorporating error handling, retries, and delays where necessary.
    - Provides feedback on the success or failure of each batch, ensuring transparency in the process.

---
&nbsp;

### asset-group_details_to_csv.py

&nbsp;
**Script to Retrieve and Save Asset Group Details to CSV by GroupID**

This script interacts with the Qualys API to retrieve detailed information about a specific asset group, including DNS entries, domains, and IP addresses. The retrieved data is then parsed and saved into a CSV file for easy reference and further processing. The script is designed to handle large datasets, XML parsing, and potential errors during API communication.

#### Key Functions:

- **get_asset_group_details(asset_group_id):**
  - Sends a request to the Qualys API to retrieve all details of the specified asset group by GroupID. The API response is returned in XML format, which includes DNS names, domains, IPs, and IP ranges.
  - **Error Handling**: The function includes robust error handling to manage issues like network errors or authentication failures. If an error occurs, the response content is printed for debugging.

- **parse_assets(asset_group_xml):**
  - Parses the XML response from the Qualys API to extract DNS names, domains, IPs, and IP ranges. The function returns a dictionary containing lists of each type of asset, organized by their respective categories.
  - **XML Parsing**: The function uses Python's `xml.etree.ElementTree` module to parse the XML, and includes error handling for XML parsing errors, ensuring that any issues are reported.

- **save_assets_to_csv(assets, filename):**
  - Takes the parsed assets and writes them into a CSV file, with each asset type labeled accordingly. This allows for easy export and review of the asset group’s contents.
  - **CSV Output**: The CSV file contains two columns: "Type" and "Value", making it straightforward to distinguish between different types of assets (DNS, Domain, IP).
  - **Error Handling**: The function includes error handling to manage file I/O errors, ensuring that issues like permission errors or disk space issues are reported.

- **main():**
  - The entry point of the script. It prompts the user for the Asset Group ID and the filename where the results should be saved. The function orchestrates the retrieval, parsing, and saving of asset group details.
  
  - **Execution Flow**:
    - Prompts the user for necessary inputs (Asset Group ID and output filename).
    - Retrieves the asset group details via the Qualys API.
    - Parses the retrieved XML to extract DNS names, domains, and IP addresses.
    - Saves the parsed assets into a CSV file for easy reference.
    - Provides feedback on the success of each operation, including error messages if something goes wrong.

#### Additional Considerations:
- **Debugging**: The script prints the raw XML response from the Qualys API for debugging purposes, helping to verify the correct data is being retrieved.
- **Flexibility**: The script is adaptable to different asset group configurations and can handle a variety of asset types efficiently.

&nbsp;
