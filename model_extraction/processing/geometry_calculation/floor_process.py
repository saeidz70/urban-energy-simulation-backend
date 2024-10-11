import json

import geopandas as gpd

from model_extraction.data_manager.utility import UtilityProcess


class FloorProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.building_path = self.config['Building_usage_path']
        self.avg_floor_height = self.config["limits"]['avg_floor_height']
        self.utility = UtilityProcess(config_path)

    def process_floors(self):
        buildings_gdf = gpd.read_file(self.building_path)

        # Try retrieving 'n_floor' for each building row using UtilityProcess
        buildings_gdf['n_floor'] = buildings_gdf.apply(
            lambda row: self.utility.process_feature('n_floor', gpd.GeoDataFrame([row])), axis=1
        )

        # Identify buildings that are still missing 'n_floor'
        missing_n_floor_mask = buildings_gdf['n_floor'].isnull()

        # Calculate missing 'n_floor' using 'height'
        if missing_n_floor_mask.any():
            if 'height' not in buildings_gdf.columns:
                raise ValueError("'height' column must be present to calculate 'n_floor'.")

            # Calculate 'n_floor' using 'height' and 'avg_floor_height'
            buildings_gdf.loc[missing_n_floor_mask, 'n_floor'] = (
                    buildings_gdf.loc[missing_n_floor_mask, 'height'] / self.avg_floor_height
            ).round().astype(int)

        # Save updated GeoJSON file
        buildings_gdf.to_file(self.building_path, driver='GeoJSON')
        return buildings_gdf
