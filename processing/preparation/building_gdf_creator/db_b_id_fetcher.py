import json
import logging

import geopandas as gpd
import requests
from shapely.geometry import mapping, shape

from config.config import Config


class BuildingDatabaseFetcher(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.db_url = self.config.get("db_building_id_url")
        self.headers = self.config.get("database_headers", {})
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        logging.basicConfig(level=logging.INFO)

    def validate_geometries(self, buildings_gdf):
        """Validate geometries in the GeoDataFrame."""
        if buildings_gdf.empty:
            logging.warning("The input GeoDataFrame is empty.")
            return False
        if not buildings_gdf.is_valid.all():
            logging.error("Invalid geometries found in the GeoDataFrame.")
            return False
        return True

    def run(self, buildings_gdf):
        """Fetch building IDs for user-provided geometries."""
        if not self.validate_geometries(buildings_gdf):
            return gpd.GeoDataFrame(columns=["geometry", "building_id"])

        # Ensure the CRS matches the default CRS
        if buildings_gdf.crs != self.default_crs:
            logging.info(f"Reprojecting GeoDataFrame to {self.default_crs}.")
            buildings_gdf = buildings_gdf.to_crs(self.default_crs)

        payload = {
            "features": [
                {"type": "Feature", "geometry": mapping(geom)}
                for geom in buildings_gdf.geometry
            ]
        }

        logging.debug(f"Request Payload: {json.dumps(payload, indent=4)}")

        try:
            response = requests.post(self.db_url, json=payload, headers=self.headers)
            response.raise_for_status()

            logging.info(f"Response Status Code: {response.status_code}")
            results = response.json().get("results", [])

            # Validate results
            features = []
            for result in results:
                try:
                    geometry = shape(result["geometry"])
                    building_id = result["building_id"]
                    features.append({"geometry": geometry, "building_id": building_id})
                except (KeyError, TypeError, ValueError) as e:
                    logging.warning(f"Invalid result entry skipped: {result}, error: {str(e)}")

            # Ensure geometry is valid and CRS is assigned
            buildings_gdf = gpd.GeoDataFrame(features, crs=self.default_crs)
            return buildings_gdf[buildings_gdf.geometry.notnull()]  # Filter invalid geometries
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during request: {str(e)}")
            return gpd.GeoDataFrame(columns=["geometry", "building_id"])
