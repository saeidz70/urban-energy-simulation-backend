import json

import geopandas as gpd

from model_extraction.data_manager.utility import UtilityProcess


class FloorProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.input_file = self.config['Building_usage_path']
        self.output_file = self.config['n_floor_path']
        self.avg_floor_height = self.config["limits"]['avg_floor_height']
        self.utility = UtilityProcess(config_path)

    def process_floors(self):
        buildings_gdf = gpd.read_file(self.input_file)

        # Retrieve 'n_floor' data for all buildings using UtilityProcess
        n_floor_gdf = self.utility.process_feature('n_floor', buildings_gdf)

        # Check if n_floor_gdf is None (no data found), skip to height-based calculation if so
        if n_floor_gdf is not None:
            # Ensure n_floor_gdf is a GeoDataFrame if data was returned
            if isinstance(n_floor_gdf, gpd.GeoDataFrame):
                # Perform a spatial join to match buildings by geometry
                updated_gdf = buildings_gdf.sjoin(n_floor_gdf[['geometry', 'n_floor']], how='left',
                                                  predicate='intersects')
                # Fill missing 'n_floor' values with the data from the spatial join
                buildings_gdf['n_floor'] = updated_gdf['n_floor_left'].fillna(updated_gdf['n_floor_right'])

        # Calculate missing 'n_floor' for buildings without data using height
        missing_n_floor_mask = buildings_gdf['n_floor'].isnull()
        if missing_n_floor_mask.any():
            if 'height' not in buildings_gdf.columns:
                raise ValueError("'height' column must be present to calculate 'n_floor'.")
            buildings_gdf.loc[missing_n_floor_mask, 'n_floor'] = (
                    buildings_gdf.loc[missing_n_floor_mask, 'height'] / self.avg_floor_height
            ).round().astype(int)

        # Save the updated GeoJSON file
        buildings_gdf.to_file(self.output_file, driver='GeoJSON')
        return buildings_gdf
