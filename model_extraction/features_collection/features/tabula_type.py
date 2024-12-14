import random

import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class TabulaType(BaseFeature):
    """
    Assigns Tabula types to buildings.
    """

    def calculate(self, gdf, rows):
        """
        Assign Tabula types to specific rows.
        """
        if not hasattr(self, 'tabula_types') or not self.tabula_types:
            raise ValueError("Tabula types are not defined or empty.")

        gdf.loc[rows, self.feature_name] = pd.Series(
            [random.choice(self.tabula_types) for _ in range(len(rows))],
            index=rows
        ).astype(gdf[self.feature_name].dtype)

        gdf = self.validate_data(gdf, self.feature_name)

        print("TabulaType assignment completed.")
        return gdf