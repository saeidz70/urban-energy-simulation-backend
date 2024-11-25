import os

import geopandas as gpd

from config.config import Config
from model_extraction.data_manager.utility import UtilityProcess
from model_extraction.features_collection.features.feature_helpers.dsm_height_calculator import DtmDsmHeightCalculator
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
        self.utility = UtilityProcess()
        self.kriging_filler = KrigingFiller()

    def process_heights(self):
        """Main method to process building heights."""
        buildings_gdf = self._load_building_data()
        buildings_gdf = self._initialize_height_column(buildings_gdf)

        # if self._is_baseline_scenario():
        #     buildings_gdf = self._process_dtm_dsm_height(buildings_gdf)

        if buildings_gdf[self.feature_name].isnull().any():
            height_gdf = self.utility.process_feature(self.feature_name, buildings_gdf)
            if height_gdf is not None and not height_gdf.empty:
                buildings_gdf = self._update_height_column(buildings_gdf, height_gdf)

        self._fill_missing_heights(buildings_gdf)
        buildings_gdf = self._validate_and_filter_heights(buildings_gdf)
        self._save_building_data(buildings_gdf)

        return buildings_gdf

    def _load_building_data(self):
        """Load building data and validate the file path."""
        if not os.path.exists(self.building_file):
            raise FileNotFoundError(f"Building file not found: {self.building_file}")
        print(f"Loading building data from {self.building_file}")
        return gpd.read_file(self.building_file)

    def _initialize_height_column(self, gdf):
        """Ensure 'height' column exists in the GeoDataFrame."""
        if self.feature_name not in gdf.columns:
            print(f"Initializing {self.feature_name} column.")
            gdf[self.feature_name] = None
        return gdf

    def _is_baseline_scenario(self):
        """Check if the baseline scenario is active."""
        scenario_list = self.config.get("project_info", {}).get("scenarioList", [])
        return "baseline" in scenario_list

    def _process_dtm_dsm_height(self, gdf):
        """Calculate heights using DTM and DSM data."""
        dtm_file = self.config.get("dtm_path")
        dsm_file = self.config.get("dsm_path")

        if os.path.exists(dtm_file) and os.path.exists(dsm_file):
            print("Processing heights using DTM and DSM files.")
            dtm_dsm_calculator = DtmDsmHeightCalculator()
            dtm_dsm_calculator.load_data()
            return dtm_dsm_calculator.calculate_building_heights(gdf)
        print("DTM or DSM files not found; skipping height processing.")
        return gdf

    def _update_height_column(self, gdf, height_gdf):
        """Merge height data from UtilityProcess into the GeoDataFrame."""
        print(f"Updating {self.feature_name} column with UtilityProcess data.")
        gdf = gdf.merge(
            height_gdf[['geometry', 'height']], on='geometry', how='left', suffixes=('', '_updated')
        )
        gdf[self.feature_name] = gdf[self.feature_name].fillna(gdf['height_updated'])
        gdf.drop(columns=['height_updated'], inplace=True)
        return gdf

    def _fill_missing_heights(self, gdf):
        """Fill missing height values using Kriging interpolation."""
        if gdf[self.feature_name].isnull().any():
            print("Filling missing height values using Kriging interpolation.")
            interpolated_values = self.kriging_filler.fill_missing_values(gdf, self.feature_name)
            if interpolated_values is not None:
                gdf.loc[gdf[self.feature_name].isnull(), self.feature_name] = interpolated_values

    def _validate_and_filter_heights(self, gdf):
        """Validate, filter, and convert 'height' column."""
        print(f"Validating and filtering {self.feature_name} column.")
        # Filter heights within limits
        if self.min_height is not None and self.max_height is not None:
            gdf = gdf[(gdf[self.feature_name] >= self.min_height) & (gdf[self.feature_name] <= self.max_height)]
        # Convert data type and round to two decimal places
        gdf[self.feature_name] = gdf[self.feature_name].round(2).astype(self.data_type)
        return gdf

    def _save_building_data(self, gdf):
        """Save the processed building data to the output file."""
        print(f"Saving processed building data to {self.building_file}.")
        columns = [self.feature_name] + [col for col in gdf.columns if col != self.feature_name]
        gdf = gdf[columns]
        gdf.to_file(self.building_file, driver='GeoJSON')
