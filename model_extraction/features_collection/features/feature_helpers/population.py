import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature
from model_extraction.features_collection.features.feature_helpers.volume import Volume


class Population(BaseFeature):
    """
    Processes and assigns the population to buildings.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = "population"
        self.census_id_column = "census_id"
        self.volume_column = "volume"
        self.population_column = "P1"
        self.volume_calculator = Volume()

    def run(self, gdf, feature_name):


        print(f"Starting the process to assign {self.feature_name}...")  # Essential print 1

        # Validate required columns using BaseFeature method
        self.validate_required_columns_exist(gdf, [self.census_id_column])

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Ensure the population column exists and is numeric
        gdf = self._ensure_population_column(gdf)

        # Ensure the volume column is present by calculating it if needed
        gdf = self._ensure_volume_column(gdf)

        # Retrieve population data if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Check if data returned is None or has missing values
        if gdf[self.feature_name].isnull().all():
            gdf = self._calculate_population_distribution(gdf)
        else:
            # Check for null or invalid values in the population column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, (int, float)))

            # Calculate missing populations for invalid rows
            gdf = self._calculate_population_distribution(gdf, invalid_rows)

        # Validate and filter population values
        gdf = self._validate_and_filter_population(gdf)

        print("Population assignment completed.")  # Essential print 2
        return gdf

    def _ensure_population_column(self, gdf):
        """
        Ensure the census population column exists and is numeric.
        """
        if self.population_column not in gdf.columns:
            print(f"Initializing missing census population column '{self.population_column}' with 0.")
            gdf[self.population_column] = 0
        else:
            print(f"Converting column '{self.population_column}' to numeric.")
            gdf[self.population_column] = pd.to_numeric(
                gdf[self.population_column], errors='coerce'
            ).fillna(0)
        return gdf

    def _ensure_volume_column(self, gdf):
        """
        Ensure the volume column is present by calculating it if needed.
        """
        if self.volume_column not in gdf.columns:
            print(f"Volume column '{self.volume_column}' missing. Calculating building volumes.")
            gdf = self.volume_calculator.run(gdf)
        return gdf

    def _calculate_population_distribution(self, gdf, invalid_rows=None):
        """
        Distribute population among buildings proportionally based on their volume.
        """
        if invalid_rows is None:
            invalid_rows = gdf[self.feature_name].isnull()

        if invalid_rows.any():
            print("Calculating population distribution.")
            buildings = gdf.copy()

            # Aggregate total volume and population for each census section
            census_aggregated = buildings.groupby(self.census_id_column).agg(
                total_volume=(self.volume_column, 'sum'),
                total_population=(self.population_column, 'first')
                # Use 'first' since P1 is same for all rows in census
            )

            # Ensure valid entries (total volume > 0 and population > 0)
            census_aggregated = census_aggregated[census_aggregated["total_volume"] > 0]

            # Distribute population proportionally based on volume
            def distribute_population(row):
                census_id = row[self.census_id_column]
                if census_id in census_aggregated.index:
                    total_volume = census_aggregated.loc[census_id, "total_volume"]
                    total_population = census_aggregated.loc[census_id, "total_population"]
                    proportional_population = (row[self.volume_column] / total_volume) * total_population
                    return min(int(proportional_population), total_population)
                return 0

            buildings[self.feature_name] = buildings.apply(distribute_population, axis=1)

            # Ensure sum does not exceed P1
            def limit_population_sum(census_id, group):
                total_population = census_aggregated.loc[census_id, "total_population"]
                while group[self.feature_name].sum() > total_population:
                    # Reduce population from the building with the largest population
                    max_population_idx = group[self.feature_name].idxmax()
                    group.loc[max_population_idx, self.feature_name] -= 1
                return group

            buildings = buildings.groupby(self.census_id_column).apply(
                lambda group: limit_population_sum(group.name, group)
            ).reset_index(drop=True)

            gdf.loc[invalid_rows, self.feature_name] = buildings.loc[invalid_rows, self.feature_name]
        return gdf

    def _validate_and_filter_population(self, gdf):
        """
        Ensure population values are within the allowed limits.
        """
        print(f"Validating and filtering {self.feature_name} values.")
        gdf[self.feature_name] = gdf[self.feature_name].apply(lambda x: max(0, int(x)) if pd.notnull(x) else 0)
        return gdf
