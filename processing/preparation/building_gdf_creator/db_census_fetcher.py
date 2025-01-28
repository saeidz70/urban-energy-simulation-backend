import json
import os

import geopandas as gpd
import requests
from shapely.geometry import mapping

from config.config import Config


class DbCensusFetcher(Config):
    def __init__(self):
        super().__init__()
        self.headers = self.config["database_headers"]
        self.db_server_url = self.config.get('db_census_url')
        self.user_polygon_file = self.config.get('polygon_from_building')
        self.census_data = self.config["db_census_sections"]
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"

    def prepare_payload(self, polygon_gdf):
        """Prepare the payload with the user's polygon."""
        try:
            # Load the GeoDataFrame
            user_polygon = polygon_gdf

            # Ensure it has features
            if user_polygon.empty:
                raise ValueError("GeoJSON file is empty or contains no valid features.")

            # Ensure CRS compatibility
            if user_polygon.crs is None:
                raise ValueError("CRS information is missing from the GeoJSON file.")
            if user_polygon.crs.to_string() != self.default_crs:
                print(f"projecting to default CRS: {self.default_crs}")
                user_polygon = user_polygon.to_crs(self.default_crs)

            # Extract the first geometry
            user_polygon = user_polygon.geometry[0]

            # Check the geometry type
            if user_polygon.geom_type not in ["Polygon", "MultiPolygon"]:
                raise ValueError(f"Invalid geometry type: {user_polygon.geom_type}")

            # Convert the geometry to a GeoJSON-like dictionary
            payload = {
                "type": "Feature",
                "geometry": mapping(user_polygon)  # Use `mapping` to convert to GeoJSON format
            }
            return payload
        except Exception as e:
            raise RuntimeError(f"Error preparing payload: {e}")

    def fetch_census_data(self, polygon_gdf):
        """Send a POST request to the database server and fetch census information."""
        payload = self.prepare_payload(polygon_gdf)

        try:
            response = requests.post(
                self.db_server_url,
                data=json.dumps(payload),
                headers=self.headers
            )

            if response.status_code == 200:
                # Parse the response as GeoDataFrame
                self.selected_census_gdf = gpd.GeoDataFrame.from_features(response.json())
                return True
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching census data: {e}")
            return None

    def check_and_save_geojson(self):
        """Check the CRS and save the GeoDataFrame as GeoJSON."""
        if not self.selected_census_gdf.crs:
            # Set CRS if not already set
            self.selected_census_gdf.set_crs(self.default_crs, inplace=True)
        print(f"CRS is set to: {self.default_crs}")

        # Ensure the output directory exists
        output_dir = os.path.dirname(self.census_data)
        if not os.path.exists(output_dir):
            print(f"Directory {output_dir} does not exist. Creating it now.")
            os.makedirs(output_dir, exist_ok=True)

        self.selected_census_gdf.to_file(self.census_data, driver='GeoJSON')
        print(f"Census data saved to {self.census_data}.")
        return self.selected_census_gdf

    def run(self, polygon_gdf):
        """Run the process to fetch and save census data."""
        if self.fetch_census_data(polygon_gdf):
            print("Successfully retrieved census data.")
            self.check_and_save_geojson()
            return self.selected_census_gdf
        else:
            print("Failed to retrieve census data.")
