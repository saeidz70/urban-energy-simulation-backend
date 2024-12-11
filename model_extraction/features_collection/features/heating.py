import random

import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class Heating(BaseFeature):
    """
    Assigns and validates heating values in the GeoDataFrame.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = 'heating'
        self.get_feature_config(self.feature_name)  # Dynamically retrieve and set feature configuration

    def run(self, gdf):
        """
        Main method to process and assign heating values.
        """
        print("Starting heating value assignment...")

        # Step 1: Process and initialize the feature column
        gdf = self.process_feature(gdf, self.feature_name)

        # Step 2: Handle invalid or missing heating values
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            print(f"Assigning heating values to {len(invalid_rows)} rows...")
            gdf = self._assign_random_heating_values(gdf, invalid_rows.index)

        # Step 3: Final validation
        gdf = self.validate_data(gdf, self.feature_name)

        print("Heating value assignment completed.")
        return gdf

    def _assign_random_heating_values(self, gdf, rows):
        """
        Assign random heating values to specific rows.
        """
        # Ensure valid values for heating are available
        if not hasattr(self, 'values') or not self.values:
            raise ValueError(f"No valid heating values available for assignment in {self.feature_name}.")

        # Assign random values only to the specified rows
        gdf.loc[rows, self.feature_name] = pd.Series(
            [random.choice(self.values) for _ in range(len(rows))],
            index=rows
        ).astype(gdf[self.feature_name].dtype)

        return gdf