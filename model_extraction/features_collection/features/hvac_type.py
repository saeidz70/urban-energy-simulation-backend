import random

import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class HVACType(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'hvac_type'
        self.get_feature_config(self.feature_name)  # Dynamically set configuration for the feature

    def run(self, gdf):
        """
        Main method to assign HVAC types to the GeoDataFrame.
        """
        print("Starting HVAC type assignment...")

        # Process feature
        gdf = self.process_feature(gdf, self.feature_name)

        # Handle invalid or missing HVAC types
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            gdf = self.assign_hvac_types(gdf, invalid_rows.index)

        print("HVAC type assignment completed.")
        return gdf

    def assign_hvac_types(self, gdf, rows):
        """
        Assign HVAC types to specific rows.
        """
        gdf.loc[rows, self.feature_name] = pd.Series(
            [random.choice(self.hvac_types) for _ in range(len(rows))],
            index=rows
        ).astype(gdf[self.feature_name].dtype)
        return gdf