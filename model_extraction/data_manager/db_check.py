import json

import geopandas as gpd
import requests


class DatabaseCheck:
    def __init__(self, config):
        self.db_url = config['database_url']

    def get_data_from_db(self, feature, buildings_gdf):
        geojson_data = buildings_gdf.to_json()

        try:
            response = requests.post(self.db_url, json={
                "feature": feature,
                "buildings": json.loads(geojson_data)
            })

            if response.status_code == 200:
                response_geojson = response.json()
                updated_gdf = gpd.GeoDataFrame.from_features(response_geojson["features"])
                buildings_gdf = buildings_gdf.set_index('geometry').join(updated_gdf.set_index('geometry'),
                                                                         rsuffix='_updated')
                return buildings_gdf.reset_index()

            return None
        except requests.RequestException as e:
            print(f"Error querying database: {e}")
            return None
