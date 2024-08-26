import json
import os

import geopandas as gpd


class BuildingVolumeCalculator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.buildings_geojson_path = config['kriging_output_path']  # Input file path from previous processing

        # Load GeoJSON file during initialization
        self.buildings_gdf = self.load_geojson(self.buildings_geojson_path)

    def load_geojson(self, file_path):
        return gpd.read_file(file_path)

    def calculate_volume(self):
        # Check for required columns and calculate volume
        if 'area' in self.buildings_gdf.columns and 'height' in self.buildings_gdf.columns:
            # Calculate volume using area and height
            self.buildings_gdf['volume'] = (self.buildings_gdf['area'] * self.buildings_gdf['height']).round(2)

            # Reorder columns to place 'volume' after 'area'
            cols = self.buildings_gdf.columns.tolist()
            if 'area' in cols:
                area_index = cols.index('area')
                # Insert 'volume' after 'area'
                cols.insert(area_index + 1, cols.pop(cols.index('volume')))
                self.buildings_gdf = self.buildings_gdf[cols]
        else:
            raise ValueError("Required columns 'area' and 'height' are not present in the GeoDataFrame.")

    def save_volume_file(self):
        output_dir = os.path.dirname(self.buildings_geojson_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.buildings_gdf.to_file(self.buildings_geojson_path, driver='GeoJSON')
        print(f"Building data with volume saved to {self.buildings_geojson_path}.")

    def process_volume_calculation(self):
        # Calculate the volume
        self.calculate_volume()

        # Save the volume data to a new file
        self.save_volume_file()
