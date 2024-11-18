import geopandas as gpd

from config.config import Config


class YearOfConstruction(Config):
    def __init__(self):
        super().__init__()
        self.building_path = self.config["building_path"]
        self.census_columns = self.config["census"]["built_year"].keys()
        self.year_mapping = self.config["census"]["built_year"]
        self.median_years = self.calculate_median_years()

    def calculate_median_years(self):
        """Calculate median years for each census period based on the config mapping."""
        median_years = {}
        for key, value in self.year_mapping.items():
            if '-' in value:
                start, end = map(int, value.split('-'))
                median_years[key] = (start + end) // 2
            elif value.startswith('-'):
                median_years[key] = int(value)
            elif value.endswith('-'):
                median_years[key] = int(value[:-1])
            else:
                median_years[key] = None
        return median_years

    def assign_construction_year(self):
        """Assign 'year_of_construction' to user_building_file based on census data."""
        buildings_gdf = gpd.read_file(self.building_path)

        # List to store calculated construction years
        construction_years = []

        # Iterate over each building row
        for _, row in buildings_gdf.iterrows():
            census_id = row.get("census_id")  # Directly using 'census_id' column

            if census_id:
                # Fetch building counts for each census period
                building_counts = {key: int(row.get(key, 0)) for key in self.census_columns}
                total_buildings = sum(building_counts.values())

                if total_buildings > 0:
                    # Calculate weighted construction year
                    weighted_sum = sum(
                        self.median_years[key] * building_counts[key]
                        for key in self.census_columns
                        if self.median_years[key] is not None
                    )
                    construction_year = round(weighted_sum / total_buildings)

                    # Clamp year within the bounds if necessary
                    construction_year = min(max(construction_year, 1919), 2005)
                else:
                    construction_year = None
            else:
                construction_year = None

            construction_years.append(construction_year)

        # Add the 'year_of_construction' column to the GeoDataFrame
        buildings_gdf['year_of_construction'] = construction_years
        self.save_output(buildings_gdf)
        return buildings_gdf

    def reorder_columns(self, gdf):
        """Reorder columns to place 'year_of_construction' after 'tot_area_per_cens_id', if both exist."""
        columns = list(gdf.columns)
        if 'tot_area_per_cens_id' in columns and 'year_of_construction' in columns:
            tot_area_per_cens_idx = columns.index('tot_area_per_cens_id')
            columns.insert(tot_area_per_cens_idx + 1, columns.pop(columns.index('year_of_construction')))
            gdf = gdf[columns]
        return gdf

    def save_output(self, buildings_gdf):
        """Save the updated GeoDataFrame to a GeoJSON file."""
        buildings_gdf = self.reorder_columns(buildings_gdf)
        buildings_gdf.to_file(self.building_path, driver='GeoJSON')
