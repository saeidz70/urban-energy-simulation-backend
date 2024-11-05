import json

import geopandas as gpd
from shapely.geometry import Polygon


class CensusSelector:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.census_path = config['census_path']
        self.polygon_coords = config['study_case']
        self.output_path = config['selected_census_sections']

        self.census_gdf = gpd.read_file(self.census_path)
        self.polygon_gdf = None
        self.selected_census_gdf = None

    def set_polygon(self):
        polygon = Polygon(self.polygon_coords)
        self.polygon_gdf = gpd.GeoDataFrame(index=[0], crs="EPSG:4326", geometry=[polygon])
        print("Polygon set successfully.")

    def select_census_sections(self):
        if self.census_gdf is None or self.polygon_gdf is None:
            raise ValueError("Census data or polygon has not been loaded.")

        # Check and align CRS
        if self.census_gdf.crs != self.polygon_gdf.crs:
            self.census_gdf = self.census_gdf.to_crs(self.polygon_gdf.crs)
            print(f"Reprojected census data to match polygon CRS: {self.polygon_gdf.crs}")

        self.selected_census_gdf = self.census_gdf[self.census_gdf.geometry.intersects(self.polygon_gdf.geometry[0])]

        if self.selected_census_gdf.empty:
            print("Warning: No census sections intersect the given polygon.")
        else:
            print("Census sections selected successfully.")

    def delete_unselected_sections(self):
        if self.selected_census_gdf is None or self.selected_census_gdf.empty:
            raise ValueError("No census sections selected. Please run select_census_sections() first.")

        self.census_gdf = self.selected_census_gdf
        print("Unselected census sections deleted successfully.")

    def save_selected_sections(self):
        if self.selected_census_gdf is None or self.selected_census_gdf.empty:
            raise ValueError("No census sections selected to save.")

        self.selected_census_gdf.to_file(self.output_path, driver='GeoJSON')
        print(f"Selected census sections successfully saved to {self.output_path}")

    def get_selected_sections(self):
        self.set_polygon()
        self.select_census_sections()

        if not self.selected_census_gdf.empty:
            self.delete_unselected_sections()
            self.save_selected_sections()

        return self.selected_census_gdf
