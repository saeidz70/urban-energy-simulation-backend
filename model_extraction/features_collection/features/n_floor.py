import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class NumberOfFloors(BaseFeature):
    """
    Assigns number of floors to buildings.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = 'n_floor'
        self.height_column = 'height'
        n_floor_config = self.config.get('features', {}).get(self.feature_name, {})
        self.avg_floor_height = n_floor_config.get("avg_floor_height", 3.3)
        self.min_n_floor = n_floor_config.get("min", 1)
        self.max_n_floor = n_floor_config.get("max", 100)
        self.data_type = n_floor_config.get("type", "int")

    def run(self, gdf):
        print(f"Starting the process to assign {self.feature_name}...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate required columns using BaseFeature method
        if not self._validate_required_columns_exist(gdf, [self.height_column]):
            return gdf

        # Retrieve n_floor data if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Check if data returned is None or has missing values
        if gdf[self.feature_name].isnull().all():
            gdf = self._get_osm_data(self.feature_name, gdf)
            if gdf[self.feature_name].isnull().all():
                gdf = self._calculate_missing_floors(gdf)
        else:
            # Check for null or invalid values in the n_floor column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, int))

            # Calculate missing floors for invalid rows
            gdf = self._calculate_missing_floors(gdf, invalid_rows)

        # Validate floor values
        gdf = self._validate_floor_values(gdf)

        print("Number of floors assignment completed.")  # Essential print 2
        return gdf

    def _calculate_missing_floors(self, gdf, invalid_rows=None):
        """
        Calculate missing n_floor values using the height column.
        """
        if self.height_column in gdf.columns:
            if invalid_rows is None:
                missing_floors = gdf[self.feature_name].isnull()
            else:
                missing_floors = invalid_rows

            if missing_floors.any():
                print(f"Calculating missing {self.feature_name} values from {self.height_column}.")
                gdf.loc[missing_floors, self.feature_name] = (
                        gdf.loc[missing_floors, self.height_column] / self.avg_floor_height
                ).round().fillna(0).astype(int)
        return gdf

    def _validate_floor_values(self, gdf):
        """
        Ensure n_floor values are within the configured limits.
        """
        print(f"Validating {self.feature_name} values between {self.min_n_floor} and {self.max_n_floor}.")

        # Ensure the column is numeric, coercing invalid values to NaN
        gdf[self.feature_name] = pd.to_numeric(gdf[self.feature_name], errors="coerce")

        # Replace NaN with the minimum floor value to avoid errors
        gdf[self.feature_name] = gdf[self.feature_name].fillna(self.min_n_floor)

        # Clip values within the range and ensure correct data type
        gdf[self.feature_name] = gdf[self.feature_name].clip(self.min_n_floor, self.max_n_floor).astype(self.data_type)

        return gdf
