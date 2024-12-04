import requests

from config.config import Config


class DBHeightFetcher(Config):
    def __init__(self):
        """
        Initializes the DBHeightFetcher with database configurations.
        """
        super().__init__()
        self.db_url = self.config["db_height_url"]
        self.headers = self.config["database_headers"]
        self.building_id_column = "building_id"
        self.geometry_column = "geometry"

    def fetch_heights(self, gdf, feature_name):
        """
        Fetches the data for the specified feature from a remote server.
        """
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
            return {item[self.building_id_column]: item.get(feature_name) for item in data.get("results", [])}
        except requests.RequestException as e:
            raise RuntimeError(f"Error fetching {feature_name}: {e}")

    def run(self, gdf, feature_name):
        print(f"Fetching {feature_name} from the database... PLEASE WAIT.")
        """
        Updates the GeoDataFrame with the fetched feature values.
        """
        feature_map = self.fetch_heights(gdf, feature_name)
        if not feature_map:
            print(f"No data returned for {feature_name}.")
            return gdf
        gdf[feature_name] = gdf[self.building_id_column].map(feature_map).fillna(gdf.get(feature_name))
        print(f"Successfully fetched {feature_name} from the database.")
        return gdf
