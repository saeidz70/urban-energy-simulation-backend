import geopandas as gpd

from config.config import Config


class DataIntegration(Config):
    def __init__(self):
        super().__init__()
        self.buildings_geojson_path = self.config['building_path']

    def check_and_align_crs(self, gdf1, gdf2):
        if gdf1.crs != gdf2.crs:
            gdf2 = gdf2.to_crs(gdf1.crs)
        return gdf2

    def save_integrated(self, integrated_gdf):
        integrated_gdf.to_file(self.buildings_geojson_path, driver='GeoJSON')
        print(f"Integrated data saved to {self.buildings_geojson_path}.")

    def run(self, buildings_gdf, selected_census_gdf):
        boundaries = selected_census_gdf
        buildings = buildings_gdf

        buildings = self.check_and_align_crs(boundaries, buildings)

        # Perform spatial join
        integrated_gdf = gpd.sjoin(buildings, boundaries, how='inner', predicate='within')

        self.save_integrated(integrated_gdf)
        return integrated_gdf
