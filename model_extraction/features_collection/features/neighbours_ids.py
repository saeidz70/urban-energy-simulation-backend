from model_extraction.features_collection.base_feature import BaseFeature


class NeighboursIds(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = "neighbours_ids"
        self.building_id_column = "building_id"
        self.feature_config = self.config['features'].get(self.feature_name, {})
        self.radius = self.feature_config.get('radius', 100)  # Radius in meters for finding neighbors

    def run(self, gdf):
        print("Running NeighboursIds feature calculation...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate required columns
        if not self._validate_required_columns_exist(gdf, [self.building_id_column]):
            return gdf

        # Retrieve neighbours_ids if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self.calculate_neighbours_ids(gdf)
        else:
            # Check for null or invalid values in the neighbours_ids column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, str))

            # Calculate neighbours_ids for invalid rows
            gdf = self.calculate_neighbours_ids(gdf, invalid_rows)

        print("NeighboursIds feature calculation completed.")  # Essential print 2
        return gdf

    def calculate_neighbours_ids(self, gdf, invalid_rows=None):
        """
        Calculates the neighbor IDs for buildings within a specified radius.
        """
        if invalid_rows is None:
            gdf = self._add_neighbour_ids(gdf)
        else:
            gdf.loc[invalid_rows, self.feature_name] = self._add_neighbour_ids(gdf.loc[invalid_rows])
        return gdf

    def _add_neighbour_ids(self, gdf):
        """
        Adds neighbor IDs to the GeoDataFrame.
        """
        # Ensure the GeoDataFrame has the projected CRS
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

        # Assign formatted neighbor ids back to the GeoDataFrame
        gdf[self.feature_name] = gdf.index.map(neighbours_dict)

        # Convert back to the default CRS
        gdf = self.check_crs_with_default_crs(gdf)

        return gdf
