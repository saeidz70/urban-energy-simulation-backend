import pandas as pd
import requests

from config.config import Config


class DatabaseCheck(Config):
    """
    Fetches data from a database for specific building IDs and features.
    """

    def __init__(self):
        super().__init__()
        self.db_url = self.config['database_url']

    def get_data_from_db(self, feature_name, buildings_gdf):
        """
        Retrieve a feature for buildings with building_source as "Database".
        """
        # Filter buildings with source "Database"
        database_buildings = buildings_gdf[buildings_gdf['building_source'] == "Database"]

        if database_buildings.empty:
            print("No buildings with source 'Database' to query.")
            return pd.DataFrame(columns=["building_id", feature_name])

        # Extract building IDs
        building_ids = database_buildings['building_id'].tolist()

        try:
            # Send request to the database with building IDs and feature name
            response = requests.post(
                self.db_url,
                json={"building_ids": building_ids},
                params={"feature_name": feature_name}
            )
            response.raise_for_status()

            # Parse the response JSON
            data = response.json()
            return pd.DataFrame(data)  # Expected: [{"building_id": "db123", "n_floors": 3}, ...]

        except requests.RequestException as e:
            print(f"Error querying database: {e}")
            return pd.DataFrame(columns=["building_id", feature_name])
