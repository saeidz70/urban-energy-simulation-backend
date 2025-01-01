import pandas as pd

from processing.features_collection.base_feature import BaseFeature


class NumberOfFloors(BaseFeature):
    """
    Assigns and validates the number of floors for buildings in a GeoDataFrame.
    """

    def calculate(self, gdf, invalid_rows):
        """
        Fill missing or invalid floor values using various sources.
        """

        if not invalid_rows.empty:
            print("Fetching data from OSM to fill missing floor values...")
            osm_data = self._get_osm_data(self.feature_name, gdf)
            gdf = self.update_missing_values(gdf, osm_data, self.feature_name)

        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)

        if not invalid_rows.empty:
            print("Calculating floors based on height...")
            self._assign_floors_from_height(gdf, invalid_rows.index)

        gdf = self._validate_floor_values(gdf)

        print("Number of floors assignment completed.")
        return gdf

    def _assign_floors_from_height(self, gdf, rows):
        """
        Assign the number of floors to rows based on building height.
        """
        if self.required_features[0] in gdf.columns:
            gdf.loc[rows, self.feature_name] = (
                    gdf.loc[rows, self.required_features[0]] / self.avg_floor_height
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
