import logging

import requests

from config.config import Config


class DBHeightFetcher(Config):
    """
    Fetches height data from a remote database and updates a GeoDataFrame.
    """

    def __init__(self):
        """
        Initializes the DBHeightFetcher with database configurations.
        """
        super().__init__()
        self.db_url = self.config["db_height_url"]
        self.headers = self.config["database_headers"]
        self.building_id_column = "building_id"
        self.geometry_column = "geometry"

        # Configure logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def fetch_heights(self, gdf, feature_name):
        """
        Fetches height values from the remote database for the given GeoDataFrame.
        """
        self.logger.info(f"🚀 Sending request to fetch {feature_name} for {len(gdf)} buildings...")

        features = [
            {
                "type": "Feature",
                "properties": {self.building_id_column: row[self.building_id_column]},
                "geometry": row[self.geometry_column].__geo_interface__,
            }
            for _, row in gdf.iterrows()
        ]
        payload = {"type": "FeatureCollection", "features": features}

        try:
            response = requests.post(self.db_url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            if not results:
                self.logger.warning(f"⚠️ No height data returned for {feature_name}.")
                return {}

            self.logger.info(f"✅ Successfully retrieved height data for {len(results)} buildings.")
            return {item[self.building_id_column]: item.get(feature_name) for item in results}

        except requests.RequestException as e:
            self.logger.error(f"🚨 Error fetching {feature_name}: {e}")
            return {}

    def run(self, gdf, feature_name):
        """
        Updates the GeoDataFrame with the fetched height values.
        """
        self.logger.info(f"📡 Fetching {feature_name} from the database... PLEASE WAIT.")

        feature_map = self.fetch_heights(gdf, feature_name)

        if not feature_map:
            self.logger.warning(f"⚠️ No height data found for {feature_name}. Returning original GeoDataFrame.")
            return gdf

        # Update the feature in the GeoDataFrame
        gdf[feature_name] = gdf[self.building_id_column].map(feature_map).fillna(gdf.get(feature_name))

        self.logger.info(f"✅ Successfully updated {feature_name} for {len(feature_map)} buildings.")
        return gdf
