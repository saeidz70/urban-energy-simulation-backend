import osmnx as ox

from config.config import Config


class OSMBuildingExtractor(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.source_column = "building_source"
        self.source_config = self.config.get('features', {}).get(self.source_column, {}).get("sources", {})

    def run(self, boundary_polygon):
        """Extract building footprints from OSM."""
        osm_buildings = ox.features_from_polygon(boundary_polygon, tags={'building': True})
        if osm_buildings.empty:
            raise ValueError("No buildings found in the specified boundary.")
        osm_buildings[self.source_column] = self.source_config.get('osm', 'OpenStreetMap')
        return osm_buildings[['geometry', self.source_column]]
