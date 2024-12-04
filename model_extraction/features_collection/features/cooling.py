import random

import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class Cooling(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'cooling'
        self.cooling_config = self.config.get('features', {}).get('cooling', {})
        self.cooling_value = self.cooling_config.get('values', None)

    def run(self, gdf):
        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Retrieve cooling data if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self.assign_random_cooling_values(gdf)
        else:
            # Count and print the number of rows with a non-null cooling value
            non_null_count = gdf[self.feature_name].notnull().sum()
            print(f"Number of rows with a non-null cooling value received from sources: {non_null_count}")
            null_count = gdf[self.feature_name].isnull().sum()
            print(f"Number of rows with a null cooling value received from sources: {null_count}")

            # Check for null or invalid values in the cooling column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: x not in self.cooling_value)

            # Assign random cooling values for invalid rows
            gdf.loc[invalid_rows, self.feature_name] = pd.Series(
                [random.choice(self.cooling_value) for _ in range(invalid_rows.sum())],
                index=gdf.index[invalid_rows]
            ).astype(gdf[self.feature_name].dtype)

        return gdf

    def assign_random_cooling_values(self, gdf):
        """Assign random cooling values to the GeoDataFrame."""
        gdf[self.feature_name] = [random.choice(self.cooling_value) for _ in range(len(gdf))]
        return gdf
