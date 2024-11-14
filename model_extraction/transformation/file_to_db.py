import requests
import json
from config.config import Config


class DBServerUploader(Config):
    def __init__(self):
        super().__init__()
        self.url = "http://172.25.13.5:8000/api/new_validated_building_scenario/"
        self.headers = {
            "Authorization": "Token 4680411d9eab0c3e0ef167f9f8ed80424dc5ce33",
            "Content-Type": "application/json"
        }
        # Retrieve the output path from the config file
        self.geojson_path = self.config.get("output_path")
        if not self.geojson_path:
            raise ValueError("Output path is not specified in the config file.")

    def load_geojson(self):
        # Load the GeoJSON file
        try:
            with open(self.geojson_path, 'r') as file:
                geojson_data = json.load(file)
            return geojson_data
        except FileNotFoundError:
            print(f"Error: File {self.geojson_path} not found.")
            return None
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON from the GeoJSON file.")
            return None

    def upload_geojson(self):
        # Load the GeoJSON data
        geojson_data = self.load_geojson()
        if geojson_data is None:
            print("GeoJSON data could not be loaded. Upload aborted.")
            return None

        # Send the POST request
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
