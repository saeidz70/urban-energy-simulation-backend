import geopandas as gpd

from config.config import Config


class NeighboursIds(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config['building_path']
        self.radius = 100  # Radius in meters for finding neighbors
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.metric_crs = f"EPSG:{self.config.get('DEFAULT_EPSG_CODE', 3395)}"

    def add_neighbour_ids(self):
        """Add a 'neighbours_ids' column with IDs of user_building_file within a specified radius."""
        buildings_gdf = gpd.read_file(self.building_file)

        # Ensure 'building_id' exists in buildings_gdf
        if 'building_id' not in buildings_gdf.columns:
            raise ValueError("The GeoDataFrame must contain a 'building_id' column.")

        # Project to metric CRS for accurate distance calculations
        buildings_gdf = buildings_gdf.to_crs(self.metric_crs)

        # Initialize spatial index
        spatial_index = buildings_gdf.sindex

        # Dictionary to store neighbor ids for each building
        neighbours_dict = {}

        # Find neighbors for each building
        for idx, building in buildings_gdf.iterrows():
            # Buffer the building geometry for the search radius
            buffer_geom = building.geometry.buffer(self.radius)

            # Find potential neighbors using spatial index
            possible_matches_index = list(spatial_index.intersection(buffer_geom.bounds))
            possible_matches = buildings_gdf.iloc[possible_matches_index]

            # Filter the neighbors based on actual distance and exclude self
            neighbors = possible_matches[
                (possible_matches['building_id'] != building['building_id']) &
                (possible_matches.geometry.distance(building.geometry) <= self.radius)
                ]

            # Format neighboring building IDs in the desired format "[4 1 2 3]"
            neighbours_dict[idx] = f"[{' '.join(map(str, neighbors['building_id'].tolist()))}]"

        # Assign formatted neighbor ids back to the GeoDataFrame
        buildings_gdf['neighbours_ids'] = buildings_gdf.index.map(neighbours_dict)

        # Convert back to the default CRS
        buildings_gdf = buildings_gdf.to_crs(self.default_crs)

        # Save the updated GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"Filtered data saved to {self.building_file}")

        return buildings_gdf
