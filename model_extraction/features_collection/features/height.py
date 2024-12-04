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
        self.feature_name = 'height'
        self.height_config = self.config.get("features", {}).get(self.feature_name, {})
        self.min_height = self.height_config.get("min", 3)
        self.max_height = self.height_config.get("max", 300)
        self.data_type = self.height_config.get("type", "float")
        self.default_crs = self.config.get('DEFAULT_CRS', 4326)
        self.kriging_filler = KrigingFiller()
        self.db_height_fetcher = DBHeightFetcher()

    def run(self, gdf):
        print(f"Starting the process to assign {self.feature_name}...")

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Check CRS and reproject if necessary
        gdf = self.check_crs_with_default_crs(gdf)

        # Retrieve height data if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or has missing values
        if gdf[self.feature_name].isnull().all():
            gdf = self.db_height_fetcher.run(gdf, self.feature_name)
            if gdf[self.feature_name].isnull().all():
                gdf = self._get_osm_data(self.feature_name, gdf)
                if gdf[self.feature_name].isnull().all():
                    gdf = self._calculate_missing_heights(gdf)
        else:
            # Check for null or invalid values in the height column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, (int, float)))

            # Calculate missing heights for invalid rows
            gdf = self._calculate_missing_heights(gdf, invalid_rows)

        # Validate and filter height values
        gdf = self._validate_and_filter_heights(gdf)

        print("Height assignment completed.")
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
        Ensure height values are within the configured limits.
        """
        print(f"Validating and filtering {self.feature_name} values.")

        # Ensure the column is numeric; invalid values are converted to NaN
        gdf.loc[:, self.feature_name] = pd.to_numeric(gdf[self.feature_name], errors="coerce")

        # Use the filter_data method from BaseFeature to filter heights within valid range
        gdf = self.filter_data(gdf, self.feature_name, self.min_height, self.max_height, self.data_type)

        return gdf
