from model_extraction.features_collection.base_feature import BaseFeature

class ConstructionType(BaseFeature):

    def calculate(self, gdf, rows):
        """
        Assign construction types to specific rows based on year of construction.
        """
        if rows.empty:
            print(f"No rows to process for {self.feature_name}.")
            return gdf

        gdf.loc[rows, self.feature_name] = gdf.loc[rows].apply(
            lambda row: self.determine_construction_type(
                row.get(self.required_features[0], None)
            ),
            axis=1
        )
        return gdf

    def determine_construction_type(self, year):
        """
        Determine the construction type based on the year of construction.
        """
        if year is None:
            print("Year of construction is missing.")
            return None
        try:
            year = int(year)
            for period, construction_type in self.construction_period.items():
                start_year, end_year = map(int, period.split('-'))
                if start_year <= year <= end_year:
                    return construction_type
        except (ValueError, TypeError) as e:
            print(f"Error determining construction type for year '{year}': {e}")
            return None
