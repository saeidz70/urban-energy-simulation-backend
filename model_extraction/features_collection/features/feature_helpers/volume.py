import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class Volume(BaseFeature):
    """
    Processes and calculates the volume of buildings.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = 'volume'
        self.height_column = 'height'
        self.area_column = 'area'
        self.get_feature_config(self.feature_name)  # Dynamically retrieve and set feature configuration

    def run(self, gdf):
        print(f"Starting the process to assign {self.feature_name}...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate required columns using BaseFeature method
        if not self.validate_required_columns_exist(gdf, self.feature_name):
            return gdf

        # Retrieve volume data if it is null, some rows are null, or data type is wrong
        # gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data
        # gdf = self.validate_data(gdf, self.feature_name)

        # check if the CRS is projected
        gdf = self.check_crs_with_projected_crs(gdf)

        # Check if data returned is None or has missing values
        # if gdf[self.feature_name].isnull().all():
        gdf = self._calculate_volume(gdf)
        # else:
        #     # Check for null or invalid values in the volume column
        #     invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(lambda x: not isinstance(x, (int, float)))
        #
        #     # Calculate missing volumes for invalid rows
        #     gdf = self._calculate_volume(gdf, invalid_rows)

        # Validate and filter volume values
        gdf = self._validate_and_filter_volumes(gdf)

        print("Volume calculation completed.")  # Essential print 2
        return gdf

    def _calculate_volume(self, gdf, invalid_rows=None):
        """
        Calculate the volume of buildings using area and height.
        """
        if invalid_rows is None:
            invalid_rows = gdf[self.feature_name].isnull()

        if invalid_rows.any():
            print("Calculating volume using area and height.")
            gdf.loc[invalid_rows, self.feature_name] = (
                        gdf.loc[invalid_rows, self.area_column] * gdf.loc[invalid_rows, self.height_column]).round(2)

            # Reorder columns to place 'volume' after 'area'
            cols = gdf.columns.tolist()
            if self.area_column in cols:
                area_index = cols.index(self.area_column)
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
