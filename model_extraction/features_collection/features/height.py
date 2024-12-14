import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature
from model_extraction.features_collection.features.feature_helpers.db_height_fetcher import DBHeightFetcher
from model_extraction.features_collection.features.feature_helpers.kriging_filler import KrigingFiller


class Height(BaseFeature):
    """
    Processes and assigns height data to buildings.
    """
    def __init__(self):
        super().__init__()
        self.kriging_filler = KrigingFiller()
        self.db_height_fetcher = DBHeightFetcher()

    def calculate(self, gdf, invalid_rows=None):
        """
        Handle missing or invalid height values by checking various sources sequentially.
        """
        if not invalid_rows.empty:
            print("Fetching height data from OSM...")
            osm_data = self._get_osm_data(self.feature_name, gdf)
            gdf = self.update_missing_values(gdf, osm_data, self.feature_name)
            invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
            print(f"Step 2: Invalid rows count after fetching from OSM: {len(invalid_rows)}")

        if not invalid_rows.empty:
            print("Calculating missing height values using Kriging...")
            gdf = self._calculate_missing_heights(gdf, invalid_rows.index)
            invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
            print(f"Step 2: Invalid rows count after Kriging: {len(invalid_rows)}")

        if not invalid_rows.empty:
            print(f"Warning: {len(invalid_rows)} rows still have missing height values.")

        # Validate and filter height values
        gdf = self._validate_and_filter_heights(gdf)

        return gdf

    def _calculate_missing_heights(self, gdf, invalid_rows=None):
        """
        Calculate missing height values using Kriging interpolation.
        """
        if invalid_rows is None:
            invalid_rows = gdf[self.feature_name].isnull()

        if invalid_rows.any():
            print("Filling missing height values using Kriging interpolation.")
            interpolated_values = self.kriging_filler.fill_missing_values(gdf, self.feature_name)
            if interpolated_values is not None:
                gdf.loc[invalid_rows, self.feature_name] = interpolated_values
        return gdf

    def _validate_and_filter_heights(self, gdf):
        """
        Validate and filter height values to ensure they are within the configured limits.
        """

        print(f"Validating and filtering '{self.feature_name}' values.")
        print(f"Step 3: Number of buildings before validation and filtering: {len(gdf)}")

        # Convert to numeric and round to 2 decimal places
        gdf[self.feature_name] = pd.to_numeric(gdf[self.feature_name], errors="coerce").round(2)

        print(f"Number of buildings before filtering: {len(gdf)}")
        print(f"min: {self.min}, max: {self.max}, type: {self.type}")

        # Filter values based on configuration
        gdf = self.filter_data(
            gdf,
            feature_name=self.feature_name,
            min_value=self.min,
            max_value=self.max,
            data_type=self.type
        )
        print(f"Step 3: Number of buildings after validation and filtering: {len(gdf)}")
        return gdf