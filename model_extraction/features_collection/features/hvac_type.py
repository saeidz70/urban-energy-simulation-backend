import random

import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class HVACType(BaseFeature):
    """
    A class to assign HVAC types to buildings.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = 'hvac_type'
        self.hvac_types_config = self.config.get('features', {}).get(self.feature_name, {})
        self.hvac_types = self.hvac_types_config.get("values", ["gb", "hp"])

    def run(self, gdf):
        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Retrieve hvac_type if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self.assign_random_hvac_types(gdf)
        else:
            # Count and print the number of rows with a non-null hvac_type value
            non_null_count = gdf[self.feature_name].notnull().sum()
            print(f"Number of rows with a non-null hvac_type value received from sources: {non_null_count}")
            null_count = gdf[self.feature_name].isnull().sum()
            print(f"Number of rows with a null hvac_type value received from sources: {null_count}")

            # Check for null or invalid values in the hvac_type column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: x not in self.hvac_types)

            # Assign random HVAC types for invalid rows
            gdf = self.assign_random_hvac_types(gdf, invalid_rows)

        return gdf

    def assign_random_hvac_types(self, gdf, invalid_rows=None):
        """
        Assigns random HVAC types to the GeoDataFrame.
        """
        if invalid_rows is None:
            gdf[self.feature_name] = [random.choice(self.hvac_types) for _ in range(len(gdf))]
        else:
            gdf.loc[invalid_rows, self.feature_name] = pd.Series(
                [random.choice(self.hvac_types) for _ in range(invalid_rows.sum())],
                index=gdf.index[invalid_rows]
            ).astype(gdf[self.feature_name].dtype)
        return gdf
