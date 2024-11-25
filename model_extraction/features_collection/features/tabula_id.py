import geopandas as gpd

from config.config import Config


class TabulaID(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = "tabula_id"
        self.year_of_construction_column = "year_of_construction"
        self.tabula_type_column = "tabula_type"
        self.building_path = self.config.get("building_path")
        self.feature_config = self.config.get("features", {}).get(self.feature_name, {})
        self.tabula_mapping = self.feature_config.get("tabula_mapping", {})

    def determine_tabula_id(self, year, tabula_type):
        """Determine the Tabula ID based on year and tabula type."""
        try:
            year = int(year)
            for period, mapping in self.tabula_mapping.items():
                if "+" in period and year >= int(period.split("+")[0]):
                    return mapping.get(tabula_type)
                elif "-" in period:
                    start, end = map(int, period.split("-"))
                    if start <= year <= end:
                        return mapping.get(tabula_type)
        except (ValueError, TypeError):
            return None

    def check_columns(self, gdf):
        """Ensure required columns exist in the DataFrame."""
        if self.year_of_construction_column not in gdf.columns:
            raise ValueError(f"Missing required column: {self.year_of_construction_column}")
        if self.tabula_type_column not in gdf.columns:
            raise ValueError(f"Missing required column: {self.tabula_type_column}")

    def assign_tabula_ids(self):
        """Assign Tabula IDs to buildings based on year and type."""
        buildings_gdf = gpd.read_file(self.building_path)

        # Validate required columns
        self.check_columns(buildings_gdf)

        # Apply Tabula ID assignment logic
        buildings_gdf[self.feature_name] = buildings_gdf.apply(
            lambda row: self.determine_tabula_id(
                row[self.year_of_construction_column],
                row[self.tabula_type_column]
            ),
            axis=1
        )

        # Warn if any Tabula IDs could not be assigned
        unassigned_count = buildings_gdf[self.feature_name].isna().sum()
        if unassigned_count > 0:
            print(f"Warning: {unassigned_count} rows could not be assigned a Tabula ID.")

        return buildings_gdf

    def save_output(self, buildings_gdf):
        """Save updated GeoDataFrame to file."""
        buildings_gdf.to_file(self.building_path, driver="GeoJSON")
        print(f"Updated buildings saved to {self.building_path}.")

    def run(self):
        """Execute the Tabula ID assignment process."""
        print("Starting Tabula ID assignment...")
        buildings_gdf = self.assign_tabula_ids()
        self.save_output(buildings_gdf)
        print("Tabula ID assignment completed.")
        return buildings_gdf
