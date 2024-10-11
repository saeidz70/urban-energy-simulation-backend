import json

import geopandas as gpd


class DataCheck:
    def __init__(self, config_path):
        # Load the config from the given path
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.building_path = self.config['Building_path']
        self.buildings_gdf = gpd.read_file(self.building_path)
        self.user_polygon = self.config['study_case']

        # Load the selected boundaries GeoJSON if specified
        selected_boundaries_path = self.config.get('selected_boundaries', None)
        if selected_boundaries_path:
            self.selected_boundaries = gpd.read_file(selected_boundaries_path)
        else:
            self.selected_boundaries = None

    def get_data_from_user(self, feature, buildings_gdf=None):
        # Get polygon as a GeoDataFrame
        polygon_gdf = self.get_polygon()

        if buildings_gdf is None:
            # Filter the buildings that are inside the polygon area
            filtered_buildings = gpd.sjoin(self.buildings_gdf, polygon_gdf, op='within')
        else:
            filtered_buildings = buildings_gdf

        # Check if the feature is available in the filtered dataset
        if feature in filtered_buildings.columns:
            return filtered_buildings[feature]
        return None

    def get_polygon(self):
        if self.selected_boundaries is not None:
            return self.selected_boundaries
        # Convert the user polygon to a GeoDataFrame
        polygon_gdf = gpd.GeoDataFrame(geometry=[gpd.GeoSeries.from_wkt(self.user_polygon)], crs="EPSG:4326")
        return polygon_gdf
