import json

import geopandas as gpd


class CensusIdCalculator:
    def __init__(self, config_path):
        # Load and parse the configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.building_file = self.config['building_path']

        # Retrieve the column name for census_id from the config
        self.census_id_column = self.config['census']['census_id']

    def calculate_census_id(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Ensure the census_id column exists in the building data
        if self.census_id_column not in buildings_gdf.columns:
            raise ValueError(f"'{self.census_id_column}' column not found in the building data.")

        # Extract census_id from the specified column
        buildings_gdf['census_id'] = buildings_gdf[self.census_id_column]

        # Correctly reorder columns to make 'census_id' the first column
        columns = ['census_id'] + [col for col in buildings_gdf.columns if col != 'census_id']
        buildings_gdf = buildings_gdf.reindex(columns=columns)

        # Save the updated GeoJSON file with census_id
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"Census ID data saved to {self.building_file}")

        return buildings_gdf
