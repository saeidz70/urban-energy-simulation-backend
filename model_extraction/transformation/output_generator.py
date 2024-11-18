import json

import geopandas as gpd
from shapely.geometry import Polygon

from config.config import Config


class OutputFileGenerator(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config.get('building_path')
        self.output_file = self.config.get('output_path')
        self.default_crs = self.config.get('DEFAULT_CRS', 4326)
        self.features = set(self.config["features"].keys())
        self.project_info = self.config.get('project_info', {})
        self.user_polygon_file = self.config.get('polygon_from_building')

    def validate_crs(self, gdf):
        if gdf.crs is None:
            print("No CRS found in building data; setting to default CRS.")
            gdf.set_crs(self.default_crs, inplace=True)
        elif gdf.crs.to_string() != f"EPSG:{self.default_crs}":
            print(f"CRS mismatch. Reprojecting to EPSG:{self.default_crs}.")
            gdf = gdf.to_crs(epsg=self.default_crs)
        return gdf

    def filter_columns(self, gdf):
        matching_columns = self.features.intersection(gdf.columns)
        return gdf[list(matching_columns)]

    def filter_by_polygon(self, gdf):
        self.user_polygon = gpd.read_file(self.user_polygon_file).geometry[0]
        if self.user_polygon is not None:
            polygon_geom = Polygon(self.user_polygon)
            gdf = self.validate_crs(gdf)
            # Directly filter by intersecting with polygon_geom
            gdf = gdf[gdf.intersects(polygon_geom)]
            print("Filtered user_building_file based on the user's polygon.")
        return gdf

    def generate_output_file(self):
        # Load user_building_file data
        buildings_gdf = gpd.read_file(self.building_file)

        # Ensure CRS is validated
        buildings_gdf = self.validate_crs(buildings_gdf)

        # Filter columns based on config features
        filtered_gdf = self.filter_columns(buildings_gdf)

        # Filter by user's polygon
        filtered_gdf = self.filter_by_polygon(filtered_gdf)

        # Drop 'id' column if it exists to prevent conflicts with building_id
        if 'id' in filtered_gdf.columns:
            filtered_gdf = filtered_gdf.drop(columns='id')

        # Convert to GeoJSON structure without 'id' using drop_id=True
        json_result = json.loads(filtered_gdf.to_json(drop_id=True))

        # Add project info to the JSON structure
        json_result['project_info'] = self.project_info

        # Save the JSON result to a file
        with open(self.output_file, 'w') as f:
            json.dump(json_result, f, indent=4)

        print(f"Output file generated and saved to {self.output_file}")

