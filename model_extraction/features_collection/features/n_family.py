import geopandas as gpd
import pandas as pd

from config.config import Config
from model_extraction.features_collection.features.feature_helpers.volume import BuildingVolumeCalculator


class FamilyCalculator(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = "n_family"
        self.census_id_column = "census_id"
        self.volume_column = "volume"
        self.building_file = self.config['building_path']
        self.n_family_config = self.config['features'].get(self.feature_name, {})
        self.census_family_column = self.n_family_config.get('census_n_family', 'PF1')
        self.volume_calculator = BuildingVolumeCalculator()
        self.buildings = None

    def load_buildings(self):
        """Load building data from the GeoJSON file."""
        if self.buildings is None:
            print(f"Loading building data from {self.building_file}.")
            self.buildings = gpd.read_file(self.building_file)
        return self.buildings

    def ensure_family_column(self):
        """Ensure the census family column exists and is numeric."""
        if self.census_family_column not in self.buildings.columns:
            print(f"Initializing missing census family column '{self.census_family_column}' with 0.")
            self.buildings[self.census_family_column] = 0
        else:
            print(f"Converting column '{self.census_family_column}' to numeric.")
            self.buildings[self.census_family_column] = pd.to_numeric(
                self.buildings[self.census_family_column], errors='coerce'
            ).fillna(0)

    def ensure_volume_column(self):
        """Ensure the volume column is present by calculating it if needed."""
        if self.volume_column not in self.buildings.columns:
            print(f"Volume column '{self.volume_column}' missing. Calculating building volumes.")
            self.volume_calculator.calculate_volume()

    def calculate_family_distribution(self):
        """Distribute families among buildings proportionally based on their volume."""
        print("Calculating family distribution.")
        buildings = self.buildings.copy()

        # Aggregate total volume and families for each census section
        census_aggregated = buildings.groupby(self.census_id_column).agg(
            total_volume=(self.volume_column, 'sum'),
            total_families=(self.census_family_column, 'first')  # Use 'first' since PF1 is same for all rows in census
        )

        # Ensure valid entries (total volume > 0 and families > 0)
        census_aggregated = census_aggregated[census_aggregated["total_volume"] > 0]

        # Distribute families proportionally based on volume
        def distribute_families(row):
            census_id = row[self.census_id_column]
            if census_id in census_aggregated.index:
                total_volume = census_aggregated.loc[census_id, "total_volume"]
                total_families = census_aggregated.loc[census_id, "total_families"]
                proportional_families = (row[self.volume_column] / total_volume) * total_families
                return min(int(proportional_families), total_families)
            return 0

        buildings[self.feature_name] = buildings.apply(distribute_families, axis=1)

        # Ensure sum does not exceed PF1
        def limit_family_sum(census_id, group):
            total_families = census_aggregated.loc[census_id, "total_families"]
            while group[self.feature_name].sum() > total_families:
                # Reduce families from the building with the largest n_family
                max_family_idx = group[self.feature_name].idxmax()
                group.loc[max_family_idx, self.feature_name] -= 1
            return group

        buildings = buildings.groupby(self.census_id_column).apply(
            lambda group: limit_family_sum(group.name, group)
        ).reset_index(drop=True)

        self.buildings = buildings

    def save_results(self):
        """Save the updated GeoJSON file."""
        try:
            print(f"Saving updated data to {self.building_file}.")
            self.buildings.to_file(self.building_file, driver='GeoJSON')
        except Exception as e:
            print(f"Error saving data: {e}")
            raise

    def run(self):
        """Run the full family calculation process."""
        try:
            self.load_buildings()
            self.ensure_family_column()
            self.ensure_volume_column()
            self.calculate_family_distribution()
            self.save_results()
            print("Family calculation process completed successfully.")
        except Exception as e:
            print(f"Error during processing: {e}")
            raise
