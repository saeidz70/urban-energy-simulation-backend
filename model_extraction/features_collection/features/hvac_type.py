import random

import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class HVACType(BaseFeature):

    def calculate(self, gdf, rows):
        """
        Assign HVAC types to specific rows.
        """
        gdf.loc[rows, self.feature_name] = pd.Series(
            [random.choice(self.hvac_types) for _ in range(len(rows))],
            index=rows
        ).astype(gdf[self.feature_name].dtype)
        return gdf