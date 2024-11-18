import geopandas as gpd

from config.config import Config
from model_extraction.data_manager.utility import UtilityProcess


class BuildingUsageProcessor(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config['building_path']
        # Normalize allowed usages to lowercase for case-insensitive comparison
        self.allowed_usages = {usage.lower() for usage in self.config["limits"]['usage']}
        self.utility = UtilityProcess()

    def process(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)
        print("Initial buildings_gdf loaded:", buildings_gdf.head())

        # Ensure 'usage' column exists in buildings_gdf, initialize if not
        if 'usage' not in buildings_gdf.columns:
            buildings_gdf['usage'] = None

        # Retrieve 'usage' data using UtilityProcess
        usage_gdf = self.utility.process_feature('usage', buildings_gdf)
        print("Retrieved usage data from utility:", usage_gdf.head())

        # Ensure CRS alignment before merging
        if usage_gdf is not None and not usage_gdf.empty:
            if usage_gdf.crs != buildings_gdf.crs:
                print(f"Aligning CRS from {usage_gdf.crs} to {buildings_gdf.crs}")
                usage_gdf = usage_gdf.to_crs(buildings_gdf.crs)

            # Merge the 'usage' data into buildings_gdf
            buildings_gdf = buildings_gdf.merge(
                usage_gdf[['geometry', 'usage']], on='geometry', how='left', suffixes=('', '_updated')
            )
            # Fill missing values and remove temporary '_updated' column
            buildings_gdf['usage'] = buildings_gdf['usage'].fillna(buildings_gdf['usage_updated'])
            buildings_gdf.drop(columns=['usage_updated'], inplace=True)
            print("After merging usage data:", buildings_gdf[['geometry', 'usage']].head())

        # Log unique usage values before filtering
        unique_usages = buildings_gdf['usage'].unique()
        print(f"Unique 'usage' values before filtering: {unique_usages}")

        # Normalize 'usage' column to lowercase for filtering, handling only non-null values
        buildings_gdf['usage'] = buildings_gdf['usage'].apply(lambda x: x.lower() if isinstance(x, str) else x)

        # Log allowed usages and filter user_building_file
        print(f"Allowed 'usage' values for filtering: {self.allowed_usages}")
        initial_count = len(buildings_gdf)
        buildings_gdf = buildings_gdf[buildings_gdf['usage'].isin(self.allowed_usages)]
        filtered_count = len(buildings_gdf)
        print(f"Filtered user_building_file by usage: {initial_count} -> {filtered_count}")

        # Only save to file if there are remaining user_building_file after filtering
        if filtered_count > 0:
            # Reorder columns to make 'usage' the first column
            columns = ['usage'] + [col for col in buildings_gdf.columns if col != 'usage']
            buildings_gdf = buildings_gdf.reindex(columns=columns)

            # Save the updated GeoJSON file
            buildings_gdf.to_file(self.building_file, driver='GeoJSON')
            print(f"Filtered data saved to {self.building_file}")
        else:
            print("No user_building_file match the allowed usage types; file was not saved.")

        return buildings_gdf
