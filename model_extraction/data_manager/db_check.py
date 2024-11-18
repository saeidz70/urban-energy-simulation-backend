import json

import geopandas as gpd
import requests


class DatabaseCheck:
    def __init__(self, config):
        self.db_url = config['database_url']

    def get_data_from_db(self, feature, buildings_gdf):
        # Convert user_building_file GeoDataFrame to GeoJSON format
        geojson_data = buildings_gdf.to_json()

        try:
            # Send request to the database with the feature and building geometries
            response = requests.post(self.db_url, json={
                "feature": feature,
                "user_building_file": json.loads(geojson_data)
            })

            # Check for a successful response
            if response.status_code == 200:
                # Convert response JSON to GeoDataFrame
                response_geojson = response.json()
                updated_gdf = gpd.GeoDataFrame.from_features(response_geojson["features_collection"])

                # Perform a spatial join to match geometries
                matched_gdf = gpd.sjoin(buildings_gdf[['geometry']], updated_gdf[['geometry', feature]],
                                        how='inner', predicate='intersects')

                # Drop unnecessary columns and keep only geometry and feature
                matched_gdf = matched_gdf[['geometry', feature]]
                return matched_gdf

            return None
        except requests.RequestException as e:
            print(f"Error querying database: {e}")
            return None
