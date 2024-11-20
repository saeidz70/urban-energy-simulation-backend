import geopandas as gpd

from config.config import Config


class TabulaID(Config):
    def __init__(self):
        super().__init__()
        self.building_path = self.config["building_path"]
        self.tabula_mapping = self.config["tabula_mapping"]

    def determine_tabula_id(self, year, tabula_type):
        """
        Determine the Tabula ID based on the year of construction and tabula type.
        """
        for period, mapping in self.tabula_mapping.items():
            if "+" in period and int(year) >= int(period.split("+")[0]):
                return mapping.get(tabula_type, None)
            elif "-" in period:
                start, end = map(int, period.split("-"))
                if start <= int(year) <= end:
                    return mapping.get(tabula_type, None)
        return None

    def assign_tabula_ids(self):
        # Load the building GeoDataFrame
        buildings_gdf = gpd.read_file(self.building_path)

        # Ensure necessary columns exist
        required_columns = ["year_of_construction", "tabula_type"]
        for col in required_columns:
            if col not in buildings_gdf.columns:
                raise ValueError(f"The '{col}' column is missing in the building data.")

        # Create the tabula_id column
        buildings_gdf["tabula_id"] = buildings_gdf.apply(
            lambda row: self.determine_tabula_id(row["year_of_construction"], row["tabula_type"]), axis=1
        )

        # Save the updated GeoJSON file
        self.save_output(buildings_gdf)
        return buildings_gdf

    def save_output(self, buildings_gdf):
        buildings_gdf.to_file(self.building_path, driver="GeoJSON")
        print(f"Updated buildings saved to {self.building_path}.")

    def run(self):
        print("Starting the process to assign Tabula IDs...")
        buildings_gdf = self.assign_tabula_ids()
        print("Tabula ID assignment process completed.")
        return buildings_gdf
