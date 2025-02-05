import logging

import pandas as pd

from processing.features_collection.base_feature import BaseFeature
from processing.features_collection.features.feature_helpers.db_height_fetcher import DBHeightFetcher
from processing.features_collection.features.feature_helpers.kriging_filler import KrigingFiller


class Height(BaseFeature):
    """
    Processes and assigns height data to buildings.
    """

    def __init__(self):
        super().__init__()
        self.kriging_filler = KrigingFiller()
        self.db_height_fetcher = DBHeightFetcher()

        # Configure logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def calculate(self, gdf, invalid_rows=None):
        """
        Handle missing or invalid height values by checking various sources sequentially.
        """
        total_missing = len(invalid_rows)
        self.logger.info(f"🚀 Starting height calculation: {total_missing} missing values detected.")

        if not invalid_rows.empty:
            self.logger.info("🔍 Fetching height data from DB...")
            db_data = self.db_height_fetcher.run(gdf, self.feature_name)
            gdf = self.update_missing_values(gdf, db_data, self.feature_name)
            invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
            self.logger.info(f"✅ Step 1: {len(invalid_rows)} values still missing after DB fetch.")

        if not invalid_rows.empty:
            self.logger.info("🌍 Fetching height data from OSM...")
            osm_data = self._get_osm_data(self.feature_name, gdf)

            # Convert OSM data to numeric to avoid type issues
            if not osm_data.empty:
                osm_data[self.feature_name] = pd.to_numeric(
                    osm_data[self.feature_name], errors="coerce"
                )
                print(f"Converted OSM data for height: {osm_data[self.feature_name].unique()}")

            gdf = self.update_missing_values(gdf, osm_data, self.feature_name)
            invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
            self.logger.info(f"✅ Step 2: {len(invalid_rows)} values still missing after OSM fetch.")

        if not invalid_rows.empty:
            self.logger.info("📊 Calculating missing height values using Kriging interpolation...")
            gdf = self._calculate_missing_heights(gdf, invalid_rows.index)
            invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
            self.logger.info(f"✅ Step 3: {len(invalid_rows)} values still missing after Kriging.")

        if not invalid_rows.empty:
            self.logger.warning(f"⚠️ Warning: {len(invalid_rows)} rows still have missing height values.")

        # Validate and filter height values
        gdf = self._validate_and_filter_heights(gdf)

        self.logger.info("🎯 Height calculation completed successfully.")
        return gdf

    def _calculate_missing_heights(self, gdf, invalid_rows=None):
        """
        Calculate missing height values using Kriging interpolation.
        """
        if invalid_rows is None:
            invalid_rows = gdf[self.feature_name].isnull()

        if invalid_rows.any():
            self.logger.info("📡 Applying Kriging interpolation for missing height values...")
            interpolated_values = self.kriging_filler.fill_missing_values(gdf, self.feature_name)
            if interpolated_values is not None:
                gdf.loc[invalid_rows, self.feature_name] = interpolated_values
                self.logger.info("✅ Kriging interpolation completed successfully.")

        return gdf

    def _validate_and_filter_heights(self, gdf):
        """
        Validate and filter height values to ensure they are within the configured limits.
        """
        self.logger.info(f"🛠 Validating and filtering '{self.feature_name}' values.")
        self.logger.info(f"📊 Step 4: Number of buildings before filtering: {len(gdf)}")
        self.logger.info(f"🔎 Min: {self.min}, Max: {self.max}, Type: {self.type}")

        # Convert to numeric and round to 2 decimal places
        gdf[self.feature_name] = pd.to_numeric(gdf[self.feature_name], errors="coerce").round(2)

        # Filter values based on configuration
        gdf = self.filter_data(
            gdf,
            feature_name=self.feature_name,
            min_value=self.min,
            max_value=self.max,
            data_type=self.type
        )

        self.logger.info(f"✅ Step 5: Number of buildings after validation and filtering: {len(gdf)}")
        return gdf
