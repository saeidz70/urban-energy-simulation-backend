import json

import geopandas as gpd


# Class for Gross Floor Area (GFA) Calculation
class GrossFloorAreaCalculator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.building_file = self.config['building_path']

    def calculate_gfa(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Ensure 'area' and 'n_floor' columns exist
        if 'area' not in buildings_gdf.columns or 'n_floor' not in buildings_gdf.columns:
            raise ValueError("Missing 'area' or 'n_floor' column in the building data.")

        # Calculate Gross Floor Area (GFA)
        buildings_gdf['gross_floor_area'] = buildings_gdf['area'] * buildings_gdf['n_floor']

        # Reorder columns to place 'GFA' after 'area'
        columns = buildings_gdf.columns.tolist()
        area_index = columns.index('area') + 1
        columns.insert(area_index, columns.pop(columns.index('gross_floor_area')))
        buildings_gdf = buildings_gdf[columns]

        # Save the updated GeoJSON file for GFA
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"GFA data saved to {self.building_file}")

        return buildings_gdf
