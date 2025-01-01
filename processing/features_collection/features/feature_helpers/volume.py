import pandas as pd

from processing.features_collection.base_feature import BaseFeature


class Volume(BaseFeature):
    """
    Processes and calculates the volume of buildings.
    """

    def run(self, gdf, feature_name):
        self.feature_name = feature_name
        self.get_feature_config(self.feature_name)  # Dynamically retrieve and set feature configuration

        print(f"Starting the process to assign {self.feature_name}...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate required columns using BaseFeature method
        if not self.validate_required_columns_exist(gdf, self.feature_name):
            return gdf

        # check if the CRS is projected
        gdf = self.check_crs_with_projected_crs(gdf)

        # Handle invalid or missing
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        print(f"Invalid rows count: {len(invalid_rows)} for {self.feature_name}")
        if not invalid_rows.empty:
            gdf = self.calculate(gdf, invalid_rows.index)

        # Validate and filter volume values
        gdf = self._validate_and_filter_volumes(gdf)

        print("Volume calculation completed.")  # Essential print 2
        return gdf

    def calculate(self, gdf, invalid_rows=None):
        """
        Calculate the volume of buildings using area and height.
        """
        print("Calculating volume using area and height.")
        gdf.loc[invalid_rows, self.feature_name] = (
                gdf.loc[invalid_rows, self.required_features[1]] * gdf.loc[invalid_rows, self.required_features[0]]
        ).round(2)

        # Reorder columns to place 'volume' after 'area'
        cols = gdf.columns.tolist()
        if self.required_features[1] in cols:
            area_index = cols.index(self.required_features[1])
            # Insert 'volume' after 'area'
            cols.insert(area_index + 1, cols.pop(cols.index(self.feature_name)))
            gdf = gdf[cols]
        return gdf

    def _validate_and_filter_volumes(self, gdf):
        """
        Ensure volume values are valid.
        """
        print(f"Validating and filtering {self.feature_name} values.")
        gdf[self.feature_name] = gdf[self.feature_name].apply(lambda x: max(0, x) if pd.notnull(x) else 0)
        return gdf