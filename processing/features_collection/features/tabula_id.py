from processing.features_collection.base_feature import BaseFeature


class TabulaID(BaseFeature):

    def calculate(self, gdf, rows):
        """
        Assign Tabula IDs to specific rows based on year and type.
        """
        gdf.loc[rows, self.feature_name] = gdf.loc[rows].apply(
            lambda row: self.determine_tabula_id(
                row.get(self.required_features[0]),
                row.get(self.required_features[1])
            ),
            axis=1
        )

        gdf = self.validate_data(gdf, self.feature_name)

        print("Tabula ID assignment completed.")
        return gdf

    def determine_tabula_id(self, year, tabula_type):
        """
        Determine the Tabula ID based on year and tabula type.
        """
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