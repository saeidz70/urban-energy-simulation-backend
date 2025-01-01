import geopandas as gpd
import requests
from shapely.geometry import mapping

from config.config import Config


class BuildingDatabaseFetcher(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.db_url = self.config["db_building_id_url"]
        self.headers = self.config["database_headers"]

    def run(self, buildings_gdf):
        """Fetch building IDs for user-provided geometries."""
        if buildings_gdf.empty:
            return gpd.GeoDataFrame(columns=["geometry", "building_id"])

        payload = {
            "features": [
                {"type": "Feature", "geometry": mapping(geom)}
                for geom in buildings_gdf.geometry
            ]
        }
        try:
            response = requests.post(self.db_url, json=payload, headers=self.headers)
            response.raise_for_status()
            db_features = response.json().get("features", [])
            return gpd.GeoDataFrame.from_features(db_features, crs=buildings_gdf.crs)
        except requests.RequestException as e:
            print(f"Error fetching building IDs: {e}")
            return gpd.GeoDataFrame(columns=["geometry", "building_id"])
