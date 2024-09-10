import json

import geojson
import geopandas as gpd
import pandas as pd


class TabulaAssigner:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.building_input_path = self.config["input_params"]["tabula"]["building_input"]
        self.tabula_input_path = self.config["input_params"]["tabula"]["tabula_input"]
        self.output_path = self.config["input_params"]["tabula"]["output"]
        self.usage_column = self.config["input_params"]["tabula"]["usage_column"]
        self.year_column = self.config["input_params"]["tabula"]["year_column"]
        self.family_number_column = self.config["input_params"]["tabula"]["family_number"]
        self.tabula_data = self.load_tabula_data()

    def load_config(self, path):
        with open(path, 'r') as file:
            return json.load(file)

    def load_tabula_data(self):
        # Read the TABULA matching data
        tabula_df = pd.read_csv(self.tabula_input_path)

        # Creating a mapping for year ranges to Tabula_id and Tabula_type
        tabula_mapping = {}
        for index, row in tabula_df.iterrows():
            years = row['YEAR'].split(' ... ')

            # Check if years[0] and years[1] are not empty before converting
            if len(years) == 2 and years[0].strip() and years[1].strip():
                start_year, end_year = int(years[0]), int(years[1])
            elif len(years) == 1 and years[0].strip():  # Only one year, open-ended range
                start_year = int(years[0])
                end_year = float('inf')  # Use infinity for open-ended ranges
            else:
                continue  # Skip if no valid year range is found

            for year in range(start_year, int(end_year) + 1):
                tabula_mapping[year] = {
                    'SFH': row['SFH'],
                    'TH': row['TH'],
                    'MFH': row['MFH'],
                    'AB': row['AB']
                }
        return tabula_mapping

    def load_buildings(self):
        with open(self.building_input_path, 'r') as file:
            return geojson.load(file)

    def assign_tabula_data(self):
        buildings = self.load_buildings()
        for feature in buildings['features']:
            building_usage = feature['properties'].get(self.usage_column)
            built_year = feature['properties'].get(self.year_column)

            if built_year is None or built_year not in self.tabula_data:
                tabula_type, tabula_id = None, None
            else:
                tabula_info = self.tabula_data[built_year]
                tabula_type = tabula_info.get(building_usage)
                tabula_id = tabula_type.split('.')[2] if tabula_type else None

            feature['properties']['Tabula_type'] = tabula_type
            feature['properties']['Tabula_id'] = tabula_id

        return buildings

    def save_output(self, buildings):
        gdf = gpd.GeoDataFrame.from_features(buildings['features'])
        gdf.to_file(self.output_path, driver='GeoJSON')

    def run(self):
        buildings = self.assign_tabula_data()
        self.save_output(buildings)
