import random

import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class TabulaType(BaseFeature):
    """
    Assigns Tabula types to buildings.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = "tabula_type"
        self.get_feature_config(self.feature_name)  # Dynamically set configuration for the feature

    def run(self, gdf):
        """
        Main method to assign Tabula types to the GeoDataFrame.
        """
        print("Starting TabulaType assignment...")

        # Process feature
        gdf = self.process_feature(gdf, self.feature_name)

        # Handle invalid or missing Tabula types
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            gdf = self.assign_tabula_types(gdf, invalid_rows.index)

        gdf = self.validate_data(gdf, self.feature_name)

        print("TabulaType assignment completed.")
        return gdf

    def assign_tabula_types(self, gdf, rows):
        """
        Assign Tabula types to specific rows.
        """
        if not hasattr(self, 'tabula_types') or not self.tabula_types:
            raise ValueError("Tabula types are not defined or empty.")

        gdf.loc[rows, self.feature_name] = pd.Series(
            [random.choice(self.tabula_types) for _ in range(len(rows))],
            index=rows
        ).astype(gdf[self.feature_name].dtype)
        return gdf