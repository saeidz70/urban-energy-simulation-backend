import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class NumberOfFloors(BaseFeature):
    """
    Assigns and validates the number of floors for buildings in a GeoDataFrame.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = "n_floor"
        self.height_column = "height"
        self.get_feature_config(self.feature_name)  # Dynamically set configuration for the feature

    def run(self, gdf):
        """
        Main method to assign and validate the number of floors.
        """
        print(f"Starting the process to assign '{self.feature_name}'...")

        # Step 1: Process the feature
        gdf = self.process_feature(gdf, self.feature_name)

        # Step 2: Handle missing or invalid floor values
        gdf = self._fill_missing_floors(gdf)

        # Step 3: Validate and filter the floor values
        gdf = self._validate_floor_values(gdf)

        print("Number of floors assignment completed.")
        return gdf

    def _fill_missing_floors(self, gdf):
        """
        Fill missing or invalid floor values using various sources.
        """
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)

        if not invalid_rows.empty:
            print("Fetching data from OSM to fill missing floor values...")
            osm_data = self._get_osm_data(self.feature_name, gdf)
            gdf = self.update_missing_values(gdf, osm_data, self.feature_name)

        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)

        if not invalid_rows.empty:
            print("Calculating floors based on height...")
            self._assign_floors_from_height(gdf, invalid_rows.index)

        return gdf

    def _assign_floors_from_height(self, gdf, rows):
        """
        Assign the number of floors to rows based on building height.
        """
        if self.height_column in gdf.columns:
            gdf.loc[rows, self.feature_name] = (
                    gdf.loc[rows, self.height_column] / self.avg_floor_height
            ).round(0).fillna(0).astype(int)

    def _validate_floor_values(self, gdf):
        """
        Validate and filter the number of floors to ensure correctness.
        """
        print(f"Validating '{self.feature_name}' values between {self.min} and {self.max}.")

        # Ensure the column is numeric
        gdf[self.feature_name] = pd.to_numeric(gdf[self.feature_name], errors="coerce")

        # Replace NaN with the minimum allowed value
        gdf[self.feature_name] = gdf[self.feature_name].fillna(self.min)

        # Filter and enforce value limits
        gdf = self.filter_data(
            gdf,
            self.feature_name,
            min_value=self.min,
            max_value=self.max,
            data_type=self.type
        )

        return gdf
