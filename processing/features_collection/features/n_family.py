import pandas as pd

from processing.features_collection.base_feature import BaseFeature
from processing.features_collection.features.feature_helpers.volume import Volume


class NumberOfFamily(BaseFeature):
    """
    Processes and assigns the number of families to buildings.
    """
    def __init__(self):
        super().__init__()
        self.volume_calculator = Volume()

    def calculate(self, gdf, rows):
        """
        Calculate the number of families for buildings based on their volume and census data.
        """
        # Ensure required columns are present
        gdf = self._ensure_required_columns(gdf)

        # Aggregate census data
        census_aggregated = gdf.groupby(self.required_features[0]).agg(
            total_volume=(self.required_features[1], 'sum'),
            total_families=(self.census_family_column, 'first')  # Assume consistency for each census ID
        ).query("total_volume > 0")  # Filter out invalid census data

        # Proportionally distribute families
        gdf[self.feature_name] = gdf.apply(
            lambda row: self._distribute_families(row, census_aggregated), axis=1
        )

        # Adjust family counts to respect census constraints
        gdf = gdf.groupby(self.required_features[0], group_keys=False, as_index=False).apply(
            lambda group: self._limit_family_sum(
                group, census_aggregated.loc[group.name, "total_families"]
            )
        )

        # Ensure no null values and convert to integer
        gdf[self.feature_name] = gdf[self.feature_name].fillna(0).astype(int)

        # Validate and filter data
        gdf = self.validate_data(gdf, self.feature_name)

        return gdf

    def _ensure_required_columns(self, gdf):
        """
        Ensure required columns ('census_family_column', 'volume_column', 'census_id_column') are present and valid.
        """
        # Initialize or validate the census family column
        if self.census_family_column not in gdf.columns:
            print(f"Initializing missing column '{self.census_family_column}' with 0.")
            gdf[self.census_family_column] = 0
        else:
            print(f"Converting column '{self.census_family_column}' to numeric.")
            gdf[self.census_family_column] = (
                pd.to_numeric(gdf[self.census_family_column], errors='coerce')
                .fillna(0).astype(int)
            )

        # Initialize or calculate the volume column
        if self.required_features[1] not in gdf.columns:
            print(f"Column '{self.required_features[1]}' missing. Calculating building volumes.")
            gdf = self.volume_calculator.run(gdf)

        # Initialize or validate the census ID column
        if self.required_features[0] not in gdf.columns:
            print(f"Initializing missing column '{self.required_features[0]}' with default value -1.")
            gdf[self.required_features[0]] = -1
        gdf[self.required_features[0]] = gdf[self.required_features[0]].fillna(-1).astype(int)

        return gdf

    def _distribute_families(self, row, census_aggregated):
        """
        Distribute families among buildings proportionally based on volume.
        """
        census_id = row[self.required_features[0]]
        if census_id in census_aggregated.index:
            total_volume = census_aggregated.loc[census_id, "total_volume"]
            total_families = census_aggregated.loc[census_id, "total_families"]
            if total_volume > 0:
                proportional_families = (row[self.required_features[1]] / total_volume) * total_families
                return max(0, min(int(proportional_families), total_families))
        return 0

    def _limit_family_sum(self, group, total_families):
        """
        Adjust family assignments to ensure the total does not exceed the census total families.
        """
        while group[self.feature_name].sum() > total_families:
            max_family_idx = group[self.feature_name].idxmax()
            group.loc[max_family_idx, self.feature_name] -= 1
        return group
