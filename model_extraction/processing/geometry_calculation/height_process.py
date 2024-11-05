import json

import geopandas as gpd

from model_extraction.data_manager.utility import UtilityProcess
from model_extraction.processing.geometry_calculation.kriging_filler import KrigingFiller


class HeightProcess:
    def __init__(self, config_path):
        # Load and parse configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.building_file = self.config['building_path']
        self.utility = UtilityProcess(config_path)
        self.kriging_filler = KrigingFiller()

    def process_heights(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Ensure 'height' column exists in buildings_gdf, initialize if not
        if 'height' not in buildings_gdf.columns:
            buildings_gdf['height'] = None

        # Retrieve 'height' data using UtilityProcess
        height_gdf = self.utility.process_feature('height', buildings_gdf)

        if height_gdf is not None and not height_gdf.empty:
            # Update 'height' in buildings_gdf
            buildings_gdf = buildings_gdf.merge(
                height_gdf[['geometry', 'height']], on='geometry', how='left', suffixes=('', '_updated')
            )
            # Fill missing values
            buildings_gdf['height'] = buildings_gdf['height'].fillna(buildings_gdf['height_updated'])
            buildings_gdf.drop(columns=['height_updated'], inplace=True)

        # Check for missing 'height' values and fill using KrigingFiller
        missing_height_mask = buildings_gdf['height'].isnull()
        if missing_height_mask.any():
            print("Filling missing height values using Kriging interpolation...")
            interpolated_values = self.kriging_filler.fill_missing_values(buildings_gdf, 'height')
            if interpolated_values is not None:
                # Update missing height values with the interpolated results
                buildings_gdf.loc[missing_height_mask, 'height'] = interpolated_values

        # Correctly reorder columns to make 'height' the first column
        columns = ['height'] + [col for col in buildings_gdf.columns if col != 'height']
        buildings_gdf = buildings_gdf.reindex(columns=columns)

        # Save the updated GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"Height data processed and saved to {self.building_file}.")
        return buildings_gdf
