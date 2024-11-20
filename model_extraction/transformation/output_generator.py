import json
import os

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
        self.user_building_file = self.config.get('user_building_file')

        # Check if user_building_file exists and delete it
        self._check_and_delete_user_file()

    def _check_and_delete_user_file(self):
        """Check if the user_building_file exists and delete it."""
        if os.path.exists(self.user_building_file):
            try:
                os.remove(self.user_building_file)
                print(f"Deleted existing user building file: {self.user_building_file}")
            except Exception as e:
                print(f"Error deleting user building file: {e}")
        else:
            print(f"No user building file found at: {self.user_building_file}")

    def validate_crs(self, gdf):
        """Validate and reproject the CRS of the GeoDataFrame if necessary."""
        if gdf.crs is None:
            print("No CRS found in building data; setting to default CRS.")
            gdf.set_crs(epsg=self.default_crs, inplace=True)
        elif gdf.crs.to_string() != f"EPSG:{self.default_crs}":
            print(f"CRS mismatch. Reprojecting to EPSG:{self.default_crs}.")
            gdf = gdf.to_crs(epsg=self.default_crs)
        return gdf

    def filter_columns(self, gdf):
        """Filter columns based on the features specified in the config."""
        matching_columns = self.features.intersection(gdf.columns)
        return gdf[list(matching_columns)]

    def filter_by_polygon(self, gdf):
        """Filter buildings GeoDataFrame by the user's polygon."""
        user_polygon_gdf = gpd.read_file(self.user_polygon_file)
        user_polygon = user_polygon_gdf.geometry[0]

        if user_polygon is not None:
            gdf = self.validate_crs(gdf)
            polygon_geom = Polygon(user_polygon)
            gdf = gdf[gdf.intersects(polygon_geom)]
            print("Filtered buildings data based on the user's polygon.")
        return gdf

    def generate_output_file(self):
        """Generate the final output file based on filters and user inputs."""
        try:
            # Load building data
            buildings_gdf = gpd.read_file(self.building_file)
            print(f"Loaded building data from: {self.building_file}")

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

        except Exception as e:
            print(f"Error generating output file: {e}")
