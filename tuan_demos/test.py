import requests
import json
import os
import base64
import zstandard as zstd
# --- Configuration ---
# The base URL for the Service Agent Data Hub API
BASE_URL = "http://nerds21.redmond.corp.microsoft.com:9000/api"
# The zip code to search for
SEARCH_ZIP = "02138"
# The name of the file to save the HTML content
OUTPUT_FILENAME = "restaurant_page.html"

def fetch_and_save_first_restaurant_html():
    """
    Searches for restaurants by zip code and saves the HTML of the first result.
    """
    try:
        # 1. Search for restaurants in the specified zip code
        search_url = f"{BASE_URL}/bizlist?zipcode={SEARCH_ZIP}&categorypath=[[\"Restaurants\"]]"
        print(f"Searching for restaurants at: {search_url}")
        
        search_response = requests.get(search_url)
        search_response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        restaurants = search_response.json()
        
        if not restaurants:
            print(f"No restaurants found for zip code {SEARCH_ZIP}.")
            return

        # 2. Get the ID of the first restaurant in the list
        first_restaurant = restaurants[0]
        restaurant_id = first_restaurant.get('id')

        if not restaurant_id:
            print("Could not find an 'id' for the first restaurant.")
            return

        print(f"Found restaurant: {first_restaurant.get('name')} (ID: {restaurant_id})")

        # 3. Fetch the detailed HTML content for that restaurant using its ID
        html_url = f"{BASE_URL}/bizdata/?id={restaurant_id}"
        print(f"Fetching HTML from: {html_url}")
        
        html_response = requests.get(html_url)
        html_response.raise_for_status()

        # 4. Decode the response
        response_json = html_response.json()
        base64_content = response_json.get("base64")

        if not base64_content:
            print("Could not find 'base64' content in the response.")
            return

        # Decode from base64
        decoded_bytes = base64.b64decode(base64_content)

        # Save the decoded bytes to a file for debugging
        # with open('decoded_bytes.bin', 'wb') as f:
        #     f.write(decoded_bytes)
        # print("Saved base64-decoded content to decoded_bytes.bin for debugging.")

        # Decompress using the zstandard library's streaming API
        try:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(decoded_bytes) as reader:
                decompressed_bytes = reader.read()
        except zstd.ZstdError as e:
            print(f"Error during zstd decompression: {e}")
            return

        # Decode to UTF-8, handling potential BOM
        decompressed_json_str = decompressed_bytes.decode('utf-8-sig')
        
        # Parse the inner JSON
        final_data = json.loads(decompressed_json_str)
        html_content = final_data.get("yelpHTML", "")

        # 5. Save the HTML content to a file
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Successfully saved HTML to {os.path.abspath(OUTPUT_FILENAME)}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from the search response.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure you have the 'requests' library installed:
    # pip install requests
    fetch_and_save_first_restaurant_html()