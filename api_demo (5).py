import requests
import json
import os
import base64
import zstandard as zstd

# --- Configuration ---
# The base URL for the Service Agent Data Hub API
BASE_URL = "http://nerds21.redmond.corp.microsoft.com:9000/api"
# The zip codes to search for (always a list)
SEARCH_ZIPS = ["02138","02139","02140","02141","02142","02238"]
# The category path to filter by
CATEGORY_PATH = [["Food"]]
# The name of the file to save the HTML content
OUTPUT_FILENAME = "business_page.html"

def fetch_and_save_first_business_html():
    """
    Searches for businesses and saves the HTML of the first result.
    """
    try:
        # 1. Build the search URL
        category_param = json.dumps(CATEGORY_PATH)
        zip_param = json.dumps(SEARCH_ZIPS)
        search_url = f"{BASE_URL}/bizlist?zipcodes={zip_param}&categorypath={category_param}"
        
        print(f"Searching for businesses in zip codes: {SEARCH_ZIPS}")
        if CATEGORY_PATH:
            print(f"Filtering by category: {CATEGORY_PATH}")
        print(f"Calling API: {search_url}")
        
        search_response = requests.get(search_url)
        search_response.raise_for_status()  # Raises an HTTPError for bad responses

        businesses = search_response.json()
        
        if not businesses:
            print(f"No businesses found for the specified criteria.")
            return

        # 2. Get the ID of the first business
        first_business = businesses[0]
        business_id = first_business.get('id')

        if not business_id:
            print("Could not find an 'id' for the first business.")
            return

        print(f"Found business: {first_business.get('name')} (ID: {business_id})")

        # 3. Fetch the detailed HTML content for that business
        html_url = f"{BASE_URL}/bizdata?id={business_id}"
        print(f"Fetching details from: {html_url}")
        
        html_response = requests.get(html_url)
        html_response.raise_for_status()

        # 4. Decode the base64, zstd-compressed response
        response_json = html_response.json()
        base64_content = response_json.get("base64")

        if not base64_content:
            print("Could not find 'base64' content in the response.")
            return

        # Decode from base64
        base64_bytes = base64.b64decode(base64_content)

        # Decompress using the zstandard library
        try:
            dctx = zstd.ZstdDecompressor()
            decompressed_bytes = dctx.decompress(base64_bytes)
        except zstd.ZstdError as e:
            print(f"Error during zstd decompression: {e}")
            return

        # Decode to UTF-8 and parse the inner JSON
        final_data = json.loads(decompressed_bytes.decode('utf-8'))
        html_content = final_data.get("yelpHTML", "")

        # 5. Save the HTML content to a file
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Successfully saved HTML to {os.path.abspath(OUTPUT_FILENAME)}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from the response.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure you have the 'requests' and 'zstandard' libraries installed:
    # pip install requests zstandard
    fetch_and_save_first_business_html()