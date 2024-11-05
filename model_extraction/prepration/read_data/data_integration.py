import json

import geopandas as gpd


class DataIntegration:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.census_geojson_path = config['selected_census_sections']
        self.buildings_geojson_path = config['building_path']

    def load_geojson(self, file_path):
        return gpd.read_file(file_path)

    def check_and_align_crs(self, gdf1, gdf2):
        if gdf1.crs != gdf2.crs:
            gdf2 = gdf2.to_crs(gdf1.crs)
        return gdf2

    def integrate_buildings(self):
        boundaries = self.load_geojson(self.census_geojson_path)
        buildings = self.load_geojson(self.buildings_geojson_path)

        buildings = self.check_and_align_crs(boundaries, buildings)

        # Perform spatial join
        integrated = gpd.sjoin(buildings, boundaries, how='inner', predicate='within')

        return integrated

    def save_integrated(self, integrated_gdf):
        integrated_gdf.to_file(self.buildings_geojson_path, driver='GeoJSON')
        print(f"Integrated data saved to {self.buildings_geojson_path}.")
