import json

import geopandas as gpd
import requests


class OSMCheck:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.osm_overpass_url = self.config['osm_overpass_url']
        self.tags = self.config['OSM_tags']
        self.user_polygon = self.config['study_case']

        # Load the selected boundaries GeoJSON if specified
        selected_boundaries_path = self.config.get('selected_boundaries', None)
        if selected_boundaries_path:
            self.selected_boundaries = gpd.read_file(selected_boundaries_path)
        else:
            self.selected_boundaries = None

    def get_data_from_osm(self, feature):
        feature_tag = self.tags.get(feature)
        if not feature_tag:
            print(f"No OSM tag found for feature: {feature}")
            return None

        polygon = self.get_polygon()
        query = f"""
        [out:json];
        (
          way["building"](poly:"{self.format_polygon_for_osm(polygon)}")["{feature_tag}"];
        );
        out body;
        >;
        out skel qt;
        """
        response = requests.post(self.osm_overpass_url, data={'data': query})
        if response.status_code == 200:
            return response.json()
        return None

    def format_polygon_for_osm(self, polygon_geojson):
        coordinates = polygon_geojson['coordinates'][0]
        formatted_coords = " ".join(f"{lon} {lat}" for lon, lat in coordinates)
        return formatted_coords

    def get_polygon(self):
        if self.selected_boundaries is not None:
            # Extracting first polygon from the GeoDataFrame
            return self.selected_boundaries.iloc[0].geometry.__geo_interface__
        return {"type": "Polygon", "coordinates": [self.user_polygon]}
