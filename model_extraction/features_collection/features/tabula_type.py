import random

import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class TabulaType(BaseFeature):
    """
    A class to assign Tabula types to buildings.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = "tabula_type"
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})
        self.tabula_types = self.feature_config.get('values', ["SFH", "TH", "MFH", "AB"])

    def run(self, gdf):
        print("Starting TabulaType assignment...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Retrieve tabula_type data if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self.assign_random_tabula_types(gdf)
        else:
            # Check for null or invalid values in the tabula_type column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: x not in self.tabula_types)

            # Assign random tabula types for invalid rows
            gdf = self.assign_random_tabula_types(gdf, invalid_rows)

        print("TabulaType assignment completed.")  # Essential print 2
        return gdf

    def assign_random_tabula_types(self, gdf, invalid_rows=None):
        """
        Assigns random Tabula types to the GeoDataFrame.
        """
        if invalid_rows is None:
            gdf[self.feature_name] = [random.choice(self.tabula_types) for _ in range(len(gdf))]
        else:
            gdf.loc[invalid_rows, self.feature_name] = pd.Series(
                [random.choice(self.tabula_types) for _ in range(invalid_rows.sum())],
                index=gdf.index[invalid_rows]
            ).astype(gdf[self.feature_name].dtype)
        return gdf
