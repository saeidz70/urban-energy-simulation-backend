import json

import geopandas as gpd


class TotalAreaPerCensusCalculator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.building_file = self.config['building_path']

    def calculate_total_area_per_census(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Ensure 'census_id' and 'area' columns exist
        if 'census_id' not in buildings_gdf.columns or 'area' not in buildings_gdf.columns:
            raise ValueError("'census_id' or 'area' column not found in the building data.")

        # Group by 'census_id' and sum the 'area' column
        total_area_per_census = buildings_gdf.groupby('census_id')['area'].sum().reset_index()
        total_area_per_census.rename(columns={'area': 'tot_area_per_cens_id'}, inplace=True)

        # Merge the total area back into the original GeoDataFrame
        buildings_gdf = buildings_gdf.merge(total_area_per_census, on='census_id', how='left')

        # Reorder columns to place 'GFA' after 'area'
        columns = buildings_gdf.columns.tolist()
        area_index = columns.index('census_id') + 1
        columns.insert(area_index, columns.pop(columns.index('tot_area_per_cens_id')))
        buildings_gdf = buildings_gdf[columns]

        # Save the updated GeoJSON file with total area per census
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"Total area per census section data saved to {self.building_file}")

        return buildings_gdf
