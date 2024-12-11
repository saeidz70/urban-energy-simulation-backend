import requests

from config.config import Config


class DBServerUploader(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.url = self.config["database_url"]
        self.headers = self.config["database_headers"]

    def validate_geojson(self, geojson_data):
        """Validate the GeoJSON data structure."""
        if not isinstance(geojson_data, dict):
            print("Invalid GeoJSON: Data is not a dictionary.")
            return False
        if "type" not in geojson_data or "features" not in geojson_data:
            print("Invalid GeoJSON: Missing 'type' or 'features' keys.")
            return False
        return True

    def upload_geojson(self, geojson_data):
        """Upload the GeoJSON data to the server."""
        if not self.validate_geojson(geojson_data):
            print("GeoJSON data validation failed. Upload aborted.")
            return None

        try:
            response = requests.post(self.url, headers=self.headers, json=geojson_data)
            response.raise_for_status()  # Raise an error for bad responses
            print("GeoJSON data uploaded successfully.")
            return response.json()  # Return server's response as a JSON object
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as err:
            print(f"Error occurred: {err}")
        return None