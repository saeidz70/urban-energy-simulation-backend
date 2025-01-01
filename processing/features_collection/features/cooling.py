import random

import pandas as pd

from processing.features_collection.base_feature import BaseFeature


class Cooling(BaseFeature):
    """ Processes and assigns cooling data to buildings. """

    def calculate(self, gdf, rows):
        """
        Assign random cooling values to specific rows.
        """
        # Ensure valid values for cooling are available
        if not hasattr(self, 'values') or not self.values:
            raise ValueError(f"No valid cooling values available for assignment in {self.feature_name}.")

        # Assign random values only to the specified rows
        gdf.loc[rows, self.feature_name] = pd.Series(
            [random.choice(self.values) for _ in range(len(rows))],
            index=rows
        ).astype(gdf[self.feature_name].dtype)

        return gdf
