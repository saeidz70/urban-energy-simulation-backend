import geojson
import geopandas as gpd
from config.config import Config


class CensusBuiltYear(Config):
    def __init__(self):
        super().__init__()
        self.input_path = self.config["input_params"]["construction_year"]["input"]
        self.output_path = self.config["input_params"]["construction_year"]["output"]
        self.census_columns = self.config["input_params"]["construction_year"]["census_columns"]
        self.year_mapping = self.config["input_params"]["construction_year"]["year_mapping"]
        self.median_years = self.calculate_median_years()

    def calculate_median_years(self):
        median_years = {}
        for key, value in self.year_mapping.items():
            if '-' in value:
                parts = value.split('-')
                if parts[0].isdigit() and parts[1].isdigit():
                    start, end = map(int, parts)
                    median_years[key] = (start + end) // 2
                else:
                    median_years[key] = None
            elif value.startswith('-') and value[1:].isdigit():
                median_years[key] = int(value)
            elif value.endswith('-') and value[:-1].isdigit():
                median_years[key] = int(value[:-1])
            else:
                median_years[key] = None
        return median_years

    def load_buildings(self):
        with open(self.input_path, 'r') as file:
            return geojson.load(file)

    def assign_construction_year(self):
        buildings = self.load_buildings()
        for feature in buildings['features_collection']:
            census_id = feature['properties'].get(self.config["input_params"]["construction_year"]["censusID"])
            if census_id:
                building_counts = {key: int(feature['properties'].get(key, 0)) for key in self.census_columns}
                total_buildings = sum(building_counts.values())
                if total_buildings > 0:
                    weighted_sum = sum(self.median_years[key] * building_counts[key] for key in self.census_columns if
                                       self.median_years[key] is not None)
                    construction_year = round(weighted_sum / total_buildings)

                    if construction_year < 1919:
                        construction_year = 1919
                    elif construction_year > 2005:
                        construction_year = 2005

                    feature['properties']['built_year'] = construction_year
                else:
                    feature['properties']['built_year'] = None
            else:
                feature['properties']['built_year'] = None
        return buildings

    def reorder_columns(self, gdf):
        cols = list(gdf.columns)
        if 'volume' in cols and 'built_year' in cols:
            volume_index = cols.index('volume')
            cols.insert(volume_index + 1, cols.pop(cols.index('built_year')))
            gdf = gdf[cols]
        return gdf

    def save_output(self, buildings):
        gdf = gpd.GeoDataFrame.from_features(buildings['features_collection'])
        gdf = self.reorder_columns(gdf)
        gdf.to_file(self.output_path, driver='GeoJSON')

    def run(self):
        buildings = self.assign_construction_year()
        self.save_output(buildings)
