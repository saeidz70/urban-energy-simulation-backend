import pandas as pd
import requests

from config.config import Config


class OsmBuiltYear(Config):
    def __init__(self):
        super().__init__()

        self.base_url = "https://www.openstreetmap.org/api/0.6/way/"
        self.building_file = self.config['building_path']
        self.df = None

    def load_building_data(self):
        # Load building data from file
        self.df = pd.read_json(self.building_file)

        if 'osm_id' not in self.df.columns:
            raise KeyError("The building file does not contain the required 'osm_id' column.")

        print("Building data loaded successfully.")

    def fetch_construction_year(self, osm_id):
        # Fetch construction year from OSM API
        url = f"{self.base_url}{osm_id}.json"
        print(f"Fetching data from URL: {url}")
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'elements' in data and len(data['elements']) > 0:
                element = data['elements'][0]
                tags = element.get('tags', {})
                built_year = (
                        tags.get('start_date') or
                        tags.get('building:year') or
                        tags.get('construction') or
                        tags.get('year_built') or
                        tags.get('completed') or
                        tags.get('opening_date') or
                        tags.get('date')
                )
                return built_year
        else:
            print(f"Failed to fetch data for OSM ID: {osm_id}, Status Code: {response.status_code}")

        return None

    def add_built_year_to_dataframe(self):
        # Add built year to the DataFrame
        if 'osm_id' in self.df.columns:
            self.df['osm_built_year'] = self.df['osm_id'].apply(self.fetch_construction_year)
            print("Built years added to DataFrame.")
        else:
            print("osm_id is not present in the DataFrame. Unable to fetch construction years.")

    def save_updated_data(self):
        # Save the updated DataFrame back to the file
        self.df.to_json(self.building_file, orient='records', indent=4)
        print(f"Updated data saved to {self.building_file}.")

    def run(self):
        # Execute the entire process
        self.load_building_data()
        self.add_built_year_to_dataframe()
        self.save_updated_data()
