import os

import geopandas as gpd

from config.config import Config


class CensusSelector(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.census_path = self.config['census_path']
        self.polygon_file = self.config['polygon_from_building']
        self.output_path = self.config['db_census_sections']

    def load_initial_data(self, polygon_gdf):
        # Load Census GeoDataFrame
        self.census_gdf = gpd.read_file(self.census_path)
        # Load and set Polygon GeoDataFrame
        polygon_from_building = polygon_gdf
        polygon = polygon_from_building.geometry[0]
        self.polygon_gdf = gpd.GeoDataFrame(index=[0], crs=polygon_from_building.crs, geometry=[polygon])
        print("Initial data loaded and polygon set successfully.")

    def select_census_sections(self, polygon_gdf):
        self.load_initial_data(polygon_gdf)
        if self.census_gdf.empty or self.polygon_gdf.empty:
            raise ValueError("Census data or polygon has not been loaded.")

        # Ensure both geodataframes have the same CRS
        if self.census_gdf.crs != self.polygon_gdf.crs:
            self.census_gdf = self.census_gdf.to_crs(self.polygon_gdf.crs)
            print(f"Reprojected census data to match polygon CRS: {self.polygon_gdf.crs}")

        # Select intersecting census sections
        self.selected_census_gdf = self.census_gdf[self.census_gdf.intersects(self.polygon_gdf.geometry[0])]

        if self.selected_census_gdf.empty:
            print("Warning: No census sections intersect the given polygon.")
        else:
            print("Census sections selected successfully.")
            return self.selected_census_gdf

    def save_selected_sections(self):
        if self.selected_census_gdf is None or self.selected_census_gdf.empty:
            raise ValueError("No census sections selected to save.")

        # Keep only the specified columns and geometry
        columns_to_keep = ['geometry', 'SEZ2011', 'E3', 'E4', 'E8', 'E9', 'E10', 'E11', 'E12', 'E13', 'E14', 'E15',
                           'E16', 'PF1', 'P1']
        self.selected_census_gdf = self.selected_census_gdf[columns_to_keep]

        # Ensure the output directory exists
        output_dir = os.path.dirname(self.output_path)
        if not os.path.exists(output_dir):
            print(f"Directory {output_dir} does not exist. Creating it now.")
            os.makedirs(output_dir, exist_ok=True)

        self.selected_census_gdf.to_file(self.output_path, driver='GeoJSON')
        print(f"Selected census sections successfully saved to {self.output_path}")
        return self.selected_census_gdf

    def run(self, polygon_gdf):
        self.select_census_sections(polygon_gdf)
        if not self.selected_census_gdf.empty:
            self.save_selected_sections()
            return self.selected_census_gdf
