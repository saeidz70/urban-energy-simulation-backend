import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class NeighboursIds(BaseFeature):
    """
    Calculates and assigns the IDs of neighboring buildings within a specified radius.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = "neighbours_ids"
        self.building_id_column = "building_id"
        self.get_feature_config(self.feature_name)  # Dynamically set configuration for the feature

    def run(self, gdf):
        """
        Main method to calculate and assign neighbor IDs.
        """
        print("Running NeighboursIds feature calculation...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate required columns
        if not self.validate_required_columns_exist(gdf, self.feature_name):
            return gdf

        # Handle invalid or missing neighbor IDs
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)

        if not invalid_rows.empty:
            # Calculate neighbours_ids for invalid rows
            gdf = self.calculate_neighbours_ids(gdf, invalid_rows.index)

        # Validate the final data
        gdf = self.validate_data(gdf, self.feature_name)

        print("NeighboursIds feature calculation completed.")  # Essential print 2
        return gdf

    def calculate_neighbours_ids(self, gdf, invalid_indices=None):
        """
        Calculates the neighbor IDs for buildings within a specified radius.
        """
        if invalid_indices is not None:
            gdf.loc[invalid_indices, self.feature_name] = self._add_neighbour_ids(gdf.loc[invalid_indices])
        else:
            gdf[self.feature_name] = self._add_neighbour_ids(gdf)
        return gdf

    def _add_neighbour_ids(self, gdf):
        """
        Adds neighbor IDs to the GeoDataFrame and ensures CRS consistency.
        """
        # Ensure the GeoDataFrame has the projected CRS for distance calculations
        gdf = self.check_crs_with_projected_crs(gdf)

        # Initialize spatial index
        spatial_index = gdf.sindex

        # Dictionary to store neighbor ids for each building
        neighbours_dict = {}

        # Find neighbors for each building
        for idx, building in gdf.iterrows():
            # Buffer the building geometry for the search radius
            buffer_geom = building.geometry.buffer(self.radius)

            # Find potential neighbors using spatial index
            possible_matches_index = list(spatial_index.intersection(buffer_geom.bounds))
            possible_matches = gdf.iloc[possible_matches_index]

            # Filter the neighbors based on actual distance and exclude self
            neighbors = possible_matches[
                (possible_matches[self.building_id_column] != building[self.building_id_column]) &
                (possible_matches.geometry.distance(building.geometry) <= self.radius)
            ]

            # Format neighboring building IDs in the desired format "[4 1 2 3]"
            neighbours_dict[idx] = f"[{' '.join(map(str, neighbors[self.building_id_column].tolist()))}]"

        # Convert neighbor IDs to a Series and assign it back to the feature column
        gdf[self.feature_name] = pd.Series(neighbours_dict, index=gdf.index)

        # Ensure the GeoDataFrame is in the default CRS after processing
        return self.check_crs_with_default_crs(gdf)
