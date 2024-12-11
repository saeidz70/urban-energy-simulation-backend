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
        self.volume_column = "volume"
        self.census_id_column = "census_id"

        self.get_feature_config(self.feature_name)  # Dynamically set configuration for the feature
        self.volume_calculator = Volume()

    def run(self, gdf):
        """
        Main method to process and assign number of families data.
        """
        print(f"Starting the process to assign '{self.feature_name}'...")

        # Step 1: Initialize and validate the feature
        gdf = self.process_feature(gdf, self.feature_name)

        # Step 2: Ensure required columns are present
        gdf = self._ensure_required_columns(gdf)

        # Step 3: Handle missing or invalid family values
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            print(f"Calculating family distribution for {len(invalid_rows)} rows...")
            gdf = self._calculate_family_distribution(gdf)

        # Ensure no null values remain and convert to int
        gdf[self.feature_name] = gdf[self.feature_name].fillna(0).astype(int)

        # Step 4: Final validation and filtering
        gdf = self.validate_data(gdf, self.feature_name)

        print("Family assignment completed.")
        return gdf

    def _ensure_required_columns(self, gdf):
        """
        Ensure the required columns ('census_family_column' and 'volume_column') are present and valid.
        """
        # Ensure the census family column is numeric
        if self.census_family_column not in gdf.columns:
            print(f"Initializing missing column '{self.census_family_column}' with 0.")
            gdf[self.census_family_column] = 0
        else:
            print(f"Converting column '{self.census_family_column}' to numeric.")
            gdf[self.census_family_column] = pd.to_numeric(
                gdf[self.census_family_column], errors='coerce'
            ).fillna(0).astype(int)

        # Ensure the volume column is present
        if self.volume_column not in gdf.columns:
            print(f"Column '{self.volume_column}' missing. Calculating building volumes.")
            gdf = self.volume_calculator.run(gdf)

        # Fill missing census_id values with a default placeholder (-1)
        if self.census_id_column not in gdf.columns:
            print(f"Initializing missing column '{self.census_id_column}' with default value -1.")
            gdf[self.census_id_column] = -1
        gdf[self.census_id_column] = gdf[self.census_id_column].fillna(-1).astype(int)

        return gdf

    def _calculate_family_distribution(self, gdf):
        """
        Distribute families among buildings proportionally based on their volume.
        """
        # Aggregate total volume and families for each census section
        census_aggregated = gdf.groupby(self.census_id_column).agg(
            total_volume=(self.volume_column, 'sum'),
            total_families=(self.census_family_column, 'first')  # Use 'first' since PF1 is consistent for each census
        )

        # Ensure valid entries (total volume > 0 and families > 0)
        census_aggregated = census_aggregated[census_aggregated["total_volume"] > 0]

        # Function to distribute families proportionally
        def distribute_families(row):
            census_id = row[self.census_id_column]
            if census_id in census_aggregated.index:
                total_volume = census_aggregated.loc[census_id, "total_volume"]
                total_families = census_aggregated.loc[census_id, "total_families"]
                if total_volume > 0:  # Prevent division by zero
                    proportional_families = (row[self.volume_column] / total_volume) * total_families
                    return max(0, min(int(proportional_families), total_families))
            return 0  # Assign 0 if no census data or volume is missing

        # Apply proportional distribution
        gdf[self.feature_name] = gdf.apply(distribute_families, axis=1)

        # Ensure sum does not exceed PF1
        def limit_family_sum(census_id, group):
            total_families = census_aggregated.loc[census_id, "total_families"]
            while group[self.feature_name].sum() > total_families:
                # Reduce families from the building with the largest n_family
                max_family_idx = group[self.feature_name].idxmax()
                group.loc[max_family_idx, self.feature_name] -= 1
            return group

        # Apply adjustment to ensure constraints are met
        gdf = (
            gdf.groupby(self.census_id_column, group_keys=False, as_index=False)
            .apply(lambda group: limit_family_sum(group.name, group.drop(columns=[self.census_id_column])))
        )

        return gdf
