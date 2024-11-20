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
        """Processes building usage data and filters based on allowed usages."""
        buildings_gdf = self._load_building_data()
        usage_gdf = self._retrieve_usage_data(buildings_gdf)

        if usage_gdf is not None:
            buildings_gdf = self._merge_usage_data(buildings_gdf, usage_gdf)

        self._filter_and_save(buildings_gdf)
        return buildings_gdf

    def _load_building_data(self):
        """Loads building data from the configured file path."""
        buildings_gdf = gpd.read_file(self.building_file)
        print("Initial buildings_gdf loaded:", buildings_gdf.head())

        if 'usage' not in buildings_gdf.columns:
            buildings_gdf['usage'] = None

        return buildings_gdf

    def _retrieve_usage_data(self, buildings_gdf):
        """Retrieves usage data from UtilityProcess."""
        usage_gdf = self.utility.process_feature('usage', buildings_gdf)
        if usage_gdf is not None and not usage_gdf.empty and usage_gdf.crs != buildings_gdf.crs:
            print(f"Aligning CRS from {usage_gdf.crs} to {buildings_gdf.crs}")
            usage_gdf = usage_gdf.to_crs(buildings_gdf.crs)
        return usage_gdf

    def _merge_usage_data(self, buildings_gdf, usage_gdf):
        """Merges usage data into the main GeoDataFrame."""
        buildings_gdf = buildings_gdf.merge(
            usage_gdf[['geometry', 'usage']], on='geometry', how='left', suffixes=('', '_updated')
        )
        buildings_gdf['usage'] = buildings_gdf['usage'].fillna(buildings_gdf['usage_updated'])
        buildings_gdf.drop(columns=['usage_updated'], inplace=True)
        print("After merging usage data:", buildings_gdf[['geometry', 'usage']].head())
        return buildings_gdf

    def _filter_and_save(self, buildings_gdf):
        """Filters the GeoDataFrame based on allowed usages and saves the results."""
        print(f"Unique 'usage' values before filtering: {buildings_gdf['usage'].unique()}")

        # Normalize and clean usage column
        buildings_gdf['usage'] = buildings_gdf['usage'].apply(
            lambda x: x.strip().lower() if isinstance(x, str) else x
        )

        print(f"Allowed 'usage' values for filtering: {self.allowed_usages}")
        initial_count = len(buildings_gdf)
        # buildings_gdf = buildings_gdf[buildings_gdf['usage'].isin(self.allowed_usages)]
        filtered_count = len(buildings_gdf)

        print(f"Filtered user_building_file by usage: {initial_count} -> {filtered_count}")

        if filtered_count > 0:
            buildings_gdf = self._reorder_columns(buildings_gdf, 'usage')
            buildings_gdf.to_file(self.building_file, driver='GeoJSON')
            print(f"Filtered data saved to {self.building_file}")
        else:
            print("No user_building_file match the allowed usage types; file was not saved.")

    @staticmethod
    def _reorder_columns(gdf, first_column):
        """Reorders columns to place the specified column first."""
        columns = [first_column] + [col for col in gdf.columns if col != first_column]
        return gdf.reindex(columns=columns)
