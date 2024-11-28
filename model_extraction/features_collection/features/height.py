import os

import geopandas as gpd

from config.config import Config
from model_extraction.data_manager.utility import UtilityProcess
from model_extraction.features_collection.features.feature_helpers.db_height_fetcher import DBHeightFetcher
from model_extraction.features_collection.features.feature_helpers.kriging_filler import KrigingFiller


class HeightProcess(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'height'
        self.building_file = self.config.get('building_path')
        self.height_config = self.config.get("features", {}).get("height", {})
        self.min_height = self.height_config.get("min", 3)
        self.max_height = self.height_config.get("max", 300)
        self.data_type = self.height_config.get("type", "float")
        self.default_crs = self.config.get('DEFAULT_CRS', 4326)
        self.utility = UtilityProcess()
        self.kriging_filler = KrigingFiller()
        self.height_updater = DBHeightFetcher()

    def process_heights(self):
        """Main method to process building heights."""
        buildings_gdf = self._load_building_data()
        buildings_gdf = self._initialize_height_column(buildings_gdf)

        # Reproject if CRS mismatch
        if buildings_gdf.crs.to_string() != f"EPSG:{self.default_crs}":
            print(f"CRS mismatch. Reprojecting to EPSG:{self.default_crs}.")
            buildings_gdf = buildings_gdf.to_crs(epsg=self.default_crs)

        # Update heights using DBHeightFetcher
        buildings_gdf = self.height_updater.update_heights(buildings_gdf, self.feature_name)
        print(f"Height updated from database: {self.feature_name}", buildings_gdf.head())

        # Fill missing heights with Kriging interpolation if needed
        self._fill_missing_heights(buildings_gdf)

        # Validate and filter heights
        buildings_gdf = self._validate_and_filter_heights(buildings_gdf)

        # Save updated building data
        self._save_building_data(buildings_gdf)

        return buildings_gdf

    def _load_building_data(self):
        if not os.path.exists(self.building_file):
            raise FileNotFoundError(f"Building file not found: {self.building_file}")
        print(f"Loading building data from {self.building_file}")
        return gpd.read_file(self.building_file)

    def _initialize_height_column(self, gdf):
        if self.feature_name not in gdf.columns:
            print(f"Initializing {self.feature_name} column.")
            gdf[self.feature_name] = None
        return gdf

    def _fill_missing_heights(self, gdf):
        if gdf[self.feature_name].isnull().any():
            print("Filling missing height values using Kriging interpolation.")
            interpolated_values = self.kriging_filler.fill_missing_values(gdf, self.feature_name)
            if interpolated_values is not None:
                gdf.loc[gdf[self.feature_name].isnull(), self.feature_name] = interpolated_values

    def _validate_and_filter_heights(self, gdf):
        print(f"Validating and filtering {self.feature_name} column.")
        if self.min_height is not None and self.max_height is not None:
            gdf = gdf[(gdf[self.feature_name] >= self.min_height) & (gdf[self.feature_name] <= self.max_height)]
        gdf[self.feature_name] = gdf[self.feature_name].round(2).astype(self.data_type)
        return gdf

    def _save_building_data(self, gdf):
        try:
            print(f"Saving processed building data to {self.building_file}.")
            columns = [self.feature_name] + [col for col in gdf.columns if col != self.feature_name]
            gdf = gdf[columns]
            gdf.to_file(self.building_file, driver='GeoJSON')
        except Exception as e:
            print(f"Error saving building data: {e}")
            raise
