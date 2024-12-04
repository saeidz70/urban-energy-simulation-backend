import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature
from model_extraction.features_collection.features.feature_helpers.volume import Volume


class NumberOfFamily(BaseFeature):
    """
    Processes and assigns the number of families to buildings.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = "n_family"
        self.census_id_column = "census_id"
        self.volume_column = "volume"
        self.n_family_config = self.config['features'].get(self.feature_name, {})
        self.census_family_column = self.n_family_config.get('census_n_family', 'PF1')
        self.volume_calculator = Volume()

    def run(self, gdf):
        print(f"Starting the process to assign {self.feature_name}...")

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate required columns using BaseFeature method
        if not self._validate_required_columns_exist(gdf, [self.census_id_column]):
            return gdf

        # Retrieve family data if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Ensure the census family column exists and is numeric
        gdf = self._ensure_family_column(gdf)

        # Ensure the volume column is present by calculating it if needed
        gdf = self._ensure_volume_column(gdf)

        # Check if data returned is None or has missing values
        if gdf[self.feature_name].isnull().all():
            gdf = self._calculate_family_distribution(gdf)
        else:
            # Check for null or invalid values in the family column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, (int, float)))

            # Calculate missing families for invalid rows
            gdf = self._calculate_family_distribution(gdf, invalid_rows)

        # Validate and filter family values
        gdf = self._validate_and_filter_families(gdf)

        print("Family assignment completed.")
        return gdf

    def _ensure_family_column(self, gdf):
        """
        Ensure the census family column exists and is numeric.
        """
        if self.census_family_column not in gdf.columns:
            print(f"Initializing missing census family column '{self.census_family_column}' with 0.")
            gdf[self.census_family_column] = 0
        else:
            print(f"Converting column '{self.census_family_column}' to numeric.")
            gdf[self.census_family_column] = pd.to_numeric(
                gdf[self.census_family_column], errors='coerce'
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

    def _calculate_family_distribution(self, gdf, invalid_rows=None):
        """
        Distribute families among buildings proportionally based on their volume.
        """
        if invalid_rows is None:
            invalid_rows = gdf[self.feature_name].isnull()

        if invalid_rows.any():
            print("Calculating family distribution.")
            buildings = gdf.copy()

            # Aggregate total volume and families for each census section
            census_aggregated = buildings.groupby(self.census_id_column).agg(
                total_volume=(self.volume_column, 'sum'),
                total_families=(self.census_family_column, 'first')
                # Use 'first' since PF1 is same for all rows in census
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

            buildings = buildings.groupby(self.census_id_column, group_keys=False).apply(
                lambda group: limit_family_sum(group.name, group)
            ).reset_index(drop=True)

            gdf.loc[invalid_rows, self.feature_name] = buildings.loc[invalid_rows, self.feature_name]
        return gdf

    def _validate_and_filter_families(self, gdf):
        """
        Ensure family values are within the allowed limits.
        """
        print(f"Validating and filtering {self.feature_name} values.")
        gdf[self.feature_name] = gdf[self.feature_name].apply(lambda x: max(0, int(x)) if pd.notnull(x) else 0)
        return gdf
