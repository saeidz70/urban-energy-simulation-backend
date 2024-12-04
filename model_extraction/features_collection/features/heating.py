import random

import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class Heating(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'heating'
        self.heating_config = self.config.get('features', {}).get('heating', {})
        self.heating_value = self.heating_config.get('values', None)

    def run(self, gdf):
        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Retrieve heating data if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self.assign_random_heating_values(gdf)

        else:
            # Check for null or invalid values in the heating column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: x not in self.heating_value)

            # Assign random heating values for invalid rows
            gdf.loc[invalid_rows, self.feature_name] = pd.Series(
                [random.choice(self.heating_value) for _ in range(invalid_rows.sum())],
                index=gdf.index[invalid_rows]
            ).astype(gdf[self.feature_name].dtype)

        return gdf

    def assign_random_heating_values(self, gdf):
        """Assign random heating values to the GeoDataFrame."""
        gdf[self.feature_name] = [random.choice(self.heating_value) for _ in range(len(gdf))]
        return gdf
