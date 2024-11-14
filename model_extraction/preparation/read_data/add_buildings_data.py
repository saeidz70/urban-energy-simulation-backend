import json

import geopandas as gpd


class BuildingData:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.building_file_path = config["building_file_path"]
        self.selected_shapefile_path = config["selected_shapefile_path"]
        self.output_path = config["added_buildings_file_path"]
        self.buildings_file = gpd.read_file(self.building_file_path)
        self.selected_gdf = gpd.read_file(self.selected_shapefile_path)

    def check_and_reproject_crs(self):
        """Check CRS and reproject if necessary."""
        if self.buildings_file.crs != self.selected_gdf.crs:
            print(
                f"CRS mismatch: \nbuildings_file CRS: {self.buildings_file.crs}\nselected_shapefile CRS: {self.selected_gdf.crs}")
            # Reproject selected_gdf to match buildings_file CRS
            self.selected_gdf = self.selected_gdf.to_crs(self.buildings_file.crs)
            print(f"Reprojected selected_shapefile to CRS: {self.selected_gdf.crs}")
        else:
            print("Both GeoDataFrames have the same CRS.")

    def perform_spatial_join(self):
        """Perform the spatial join based on location."""
        self.result_gdf = gpd.sjoin(self.selected_gdf, self.buildings_file[['geometry', 'EDIFC_USO']], how='left',
                                    op='intersects')

    def save_result(self):
        """Save the result to a new GeoJSON file."""
        self.result_gdf.to_file(self.output_path, driver='GeoJSON')
        print(f"Spatial join complete. The results have been saved to '{self.output_path}'.")

    def run(self):
        """Run the spatial join process."""
        self.check_and_reproject_crs()
        self.perform_spatial_join()
        self.save_result()
