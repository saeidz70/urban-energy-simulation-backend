import json

import geopandas as gpd

from model_extraction.data_manager.utility import UtilityProcess


class FloorProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.input_file = self.config['kriging_output_path']
        self.output_file = self.config['n_floor_path']
        self.avg_floor_height = self.config["limits"]['avg_floor_height']
        self.utility = UtilityProcess(config_path)

    def process_floors(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.input_file)

        # Ensure 'n_floor' column exists in buildings_gdf, initialize if not
        if 'n_floor' not in buildings_gdf.columns:
            buildings_gdf['n_floor'] = None

        # Retrieve 'n_floor' data using UtilityProcess
        n_floor_gdf = self.utility.process_feature('n_floor', buildings_gdf)

        if n_floor_gdf is not None and not n_floor_gdf.empty:
            # Update 'n_floor' in buildings_gdf
            buildings_gdf = buildings_gdf.merge(
                n_floor_gdf[['geometry', 'n_floor']], on='geometry', how='left', suffixes=('', '_updated')
            )
            # Fill missing values
            buildings_gdf['n_floor'] = buildings_gdf['n_floor'].fillna(buildings_gdf['n_floor_updated'])
            buildings_gdf.drop(columns=['n_floor_updated'], inplace=True)

        # Calculate missing 'n_floor' values using the 'height' column
        if 'height' in buildings_gdf.columns:
            missing_n_floor = buildings_gdf['n_floor'].isnull()
            if missing_n_floor.any():
                # Calculate the number of floors from height
                buildings_gdf.loc[missing_n_floor, 'n_floor'] = (
                        buildings_gdf.loc[missing_n_floor, 'height'] / self.avg_floor_height
                ).round().astype(int)

        # Save the updated GeoJSON file
        buildings_gdf.to_file(self.output_file, driver='GeoJSON')
        return buildings_gdf
