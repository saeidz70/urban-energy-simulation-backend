import os

import geopandas as gpd

from config.config import Config


class BuildingVolumeCalculator(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'volume'
        self.height_column = 'height'
        self.area_column = 'area'
        self.buildings_geojson_path = self.config['building_path']
        # Load GeoJSON file during initialization
        self.buildings_gdf = gpd.read_file(self.buildings_geojson_path)


    def calculate_volume(self):
        # Check for required columns and calculate volume
        if self.area_column in self.buildings_gdf.columns and self.height_column in self.buildings_gdf.columns:
            # Calculate volume using area and height
            self.buildings_gdf[self.feature_name] = (
                        self.buildings_gdf[self.area_column] * self.buildings_gdf[self.height_column]).round(2)

            # Reorder columns to place 'volume' after 'area'
            cols = self.buildings_gdf.columns.tolist()
            if self.area_column in cols:
                area_index = cols.index(self.area_column)
                # Insert 'volume' after 'area'
                cols.insert(area_index + 1, cols.pop(cols.index(self.feature_name)))
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
