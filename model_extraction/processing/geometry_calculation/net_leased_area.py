import json

import geopandas as gpd


# Class for Net Leased Area (NLA) Calculation
class NetLeasedAreaCalculator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.building_file = self.config['building_path']

    def calculate_nla(self):
        # Load GFA data
        gfa_gdf = gpd.read_file(self.building_file)

        # Calculate Net Leased Area (NLA)
        gfa_gdf['net_leased_area'] = gfa_gdf[
                                         'gross_floor_area'] * 0.8  # Assuming 20% of GFA is taken up by common spaces

        # Reorder columns to place 'GFA' after 'area'
        columns = gfa_gdf.columns.tolist()
        area_index = columns.index('gross_floor_area') + 1
        columns.insert(area_index, columns.pop(columns.index('net_leased_area')))
        gfa_gdf = gfa_gdf[columns]

        # Save the updated GeoJSON file for NLA
        gfa_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"NLA data saved to {self.building_file}")

        return gfa_gdf
