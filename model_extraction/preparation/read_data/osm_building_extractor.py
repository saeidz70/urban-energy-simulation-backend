import os

import geopandas as gpd
import osmnx as ox


class OSMBuildingExtractor:
    def __init__(self, config):

        self.boundary_geojson_path = config['selected_boundaries']
        self.output_file_path = config['osm_building_path']
        self.boundary_polygon = self.load_boundary()

    def load_boundary(self):
        gdf = gpd.read_file(self.boundary_geojson_path)
        return gdf.unary_union

    def extract_buildings(self):
        buildings = ox.features_from_polygon(self.boundary_polygon, tags={'building': True})
        return buildings

    def filter_columns(self, buildings):
        # List of required columns
        required_columns = ['osmid', 'nodes', 'building']

        # Check which columns are actually present in the GeoDataFrame
        available_columns = [col for col in required_columns if col in buildings.columns]

        # Filter only the available required columns and ensure it remains a GeoDataFrame
        filtered_buildings = buildings[available_columns + ['geometry']].copy()
        return filtered_buildings

    def save_buildings(self, buildings):
        output_dir = os.path.dirname(self.output_file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filtered_buildings = self.filter_columns(buildings)

        # Convert unsupported data types to strings using .loc to avoid SettingWithCopyWarning
        for column in filtered_buildings.columns:
            if filtered_buildings[column].dtype == 'object':
                filtered_buildings.loc[:, column] = filtered_buildings[column].apply(
                    lambda x: str(x) if isinstance(x, list) else x)

        # Ensure that filtered_buildings is a GeoDataFrame before saving
        if not isinstance(filtered_buildings, gpd.GeoDataFrame):
            filtered_buildings = gpd.GeoDataFrame(filtered_buildings, geometry='geometry')

        filtered_buildings.to_file(self.output_file_path, driver='GeoJSON')
        print(f"Building data extracted and saved to {self.output_file_path}.")
