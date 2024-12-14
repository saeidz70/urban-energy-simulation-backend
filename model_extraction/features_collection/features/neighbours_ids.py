import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class NeighboursIds(BaseFeature):
    """
    Calculates and assigns the IDs of neighboring buildings within a specified radius.
    """

    def calculate(self, gdf, rows=None):
        """
        Calculates the neighbor IDs for buildings within a specified radius.
        """
        if rows is not None:
            gdf.loc[rows, self.feature_name] = self._add_neighbour_ids(gdf.loc[rows])
        else:
            gdf[self.feature_name] = self._add_neighbour_ids(gdf)

        gdf = self.validate_data(gdf, self.feature_name)

        print("NeighboursIds feature calculation completed.")
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
                (possible_matches[self.required_features[0]] != building[self.required_features[0]]) &
                (possible_matches.geometry.distance(building.geometry) <= self.radius)
            ]

            # Format neighboring building IDs in the desired format "[4 1 2 3]"
            neighbours_dict[idx] = f"[{' '.join(map(str, neighbors[self.required_features[0]].tolist()))}]"

        # Convert neighbor IDs to a Series and assign it back to the feature column
        gdf[self.feature_name] = pd.Series(neighbours_dict, index=gdf.index)

        # Ensure the GeoDataFrame is in the default CRS after processing
        return self.check_crs_with_default_crs(gdf)
