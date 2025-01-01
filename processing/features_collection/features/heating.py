import random

import pandas as pd

from processing.features_collection.base_feature import BaseFeature


class Heating(BaseFeature):

    def calculate(self, gdf, rows):
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