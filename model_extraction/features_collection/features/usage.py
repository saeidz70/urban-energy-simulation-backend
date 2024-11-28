import geopandas as gpd

from config.config import Config
from model_extraction.data_manager.utility import UtilityProcess


class BuildingUsageProcessor(Config):
    """Processes and filters building usage data based on allowed usage types."""

    def __init__(self):
        super().__init__()
        self.feature_name = 'usage'
        self.building_file = self.config.get('building_path')
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})
        self.allowed_usages = {
            usage.lower() for usage in self.feature_config.get('allowed_values', ["residential", "non residential"])
        }
        print(f"Allowed usage types: {self.allowed_usages}")
        self.utility = UtilityProcess()

    def run(self):
        """Runs the building usage processing pipeline."""
        try:
            print("Starting building usage processing...")
            buildings_gdf = self._load_building_data()
            usage_gdf = self._fetch_usage_data(buildings_gdf)
            # TODO: add census usage if there is no utility data

            if usage_gdf is not None:
                buildings_gdf = self._merge_usage_data(buildings_gdf, usage_gdf)

            filtered_gdf = buildings_gdf
            # filtered_gdf = self._filter_usage(buildings_gdf)
            self._save_filtered_data(filtered_gdf)
            print("Building usage processing completed.")
            return filtered_gdf
        except Exception as e:
            print(f"Error during processing: {e}")
            raise

    def _load_building_data(self):
        """Loads the building data and initializes usage column if missing."""
        try:
            gdf = gpd.read_file(self.building_file)
            if 'usage' not in gdf.columns:
                gdf['usage'] = None
            print(f"Loaded building data with {len(gdf)} records.")
            return gdf
        except Exception as e:
            raise RuntimeError(f"Error loading building data: {e}")

    def _fetch_usage_data(self, buildings_gdf):
        """Retrieves usage data using the UtilityProcess."""
        try:
            usage_gdf = self.utility.process_feature(self.feature_name, buildings_gdf)
            if usage_gdf is not None and not usage_gdf.empty:
                if usage_gdf.crs != buildings_gdf.crs:
                    usage_gdf = usage_gdf.to_crs(buildings_gdf.crs)
                    print("CRS aligned between building and usage data.")
            return usage_gdf
        except Exception as e:
            print(f"Error fetching usage data: {e}")
            return None

    def _merge_usage_data(self, buildings_gdf, usage_gdf):
        """Merges fetched usage data into the building dataset."""
        try:
            merged_gdf = buildings_gdf.merge(
                usage_gdf[['geometry', self.feature_name]],
                on='geometry',
                how='left',
                suffixes=('', '_updated')
            )
            merged_gdf[self.feature_name] = merged_gdf[self.feature_name].fillna(
                merged_gdf[f'{self.feature_name}_updated'])
            merged_gdf.drop(columns=[f'{self.feature_name}_updated'], inplace=True)
            print(f"Usage data merged. Total records: {len(merged_gdf)}.")
            return merged_gdf
        except Exception as e:
            raise RuntimeError(f"Error merging usage data: {e}")

    def _filter_usage(self, buildings_gdf):
        """Filters building data based on allowed usage types."""
        buildings_gdf[self.feature_name] = buildings_gdf[self.feature_name].apply(
            lambda x: x.strip().lower() if isinstance(x, str) else None
        )
        filtered_gdf = buildings_gdf[buildings_gdf[self.feature_name].isin(self.allowed_usages)]
        print(f"Filtered records: {len(filtered_gdf)} out of {len(buildings_gdf)}.")
        return filtered_gdf

    def _save_filtered_data(self, filtered_gdf):
        """Saves the filtered building data to a GeoJSON file."""
        if not filtered_gdf.empty:
            try:
                filtered_gdf.to_file(self.building_file, driver='GeoJSON')
                print(f"Filtered data saved to {self.building_file}.")
            except Exception as e:
                raise RuntimeError(f"Error saving filtered data: {e}")
        else:
            print("No records to save; all data was filtered out.")
