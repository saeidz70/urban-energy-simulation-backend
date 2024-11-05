import numpy as np
from pykrige.ok import OrdinaryKriging


class KrigingFiller:
    def __init__(self, variogram_model='linear'):
        self.variogram_model = variogram_model

    def fill_missing_values(self, gdf, feature):
        """Fills missing values for a given feature in a GeoDataFrame using Ordinary Kriging.
        If Kriging is not possible, falls back to mean imputation."""
        # Extract non-null values for Kriging
        valid_data = gdf.dropna(subset=[feature])

        if valid_data.empty or len(valid_data) < 3:
            print("Not enough valid data points for Kriging interpolation.")
            # Fallback to mean imputation
            mean_value = gdf[feature].mean()
            gdf[feature].fillna(mean_value, inplace=True)
            print(f"Filled missing values using mean imputation: {mean_value}")
            return gdf

        # Extract coordinates and feature values
        x = valid_data.geometry.centroid.x.values
        y = valid_data.geometry.centroid.y.values
        z = valid_data[feature].values

        # Check if coordinates are valid
        if len(x) < 3 or len(y) < 3:
            print("Insufficient spatial data points for Kriging.")
            mean_value = gdf[feature].mean()
            gdf[feature].fillna(mean_value, inplace=True)
            print(f"Filled missing values using mean imputation: {mean_value}")
            return gdf

        # Set up Ordinary Kriging
        try:
            kriging_model = OrdinaryKriging(
                x, y, z,
                variogram_model=self.variogram_model,
                verbose=False,
                enable_plotting=False
            )
        except Exception as e:
            print(f"Error initializing Kriging model: {e}")
            mean_value = gdf[feature].mean()
            gdf[feature].fillna(mean_value, inplace=True)
            print(f"Filled missing values using mean imputation: {mean_value}")
            return gdf

        # Prepare the grid for prediction
        missing_data = gdf[gdf[feature].isnull()]
        if missing_data.empty:
            print("No missing values to fill.")
            return gdf

        # Extract coordinates for missing data
        grid_x = missing_data.geometry.centroid.x.values
        grid_y = missing_data.geometry.centroid.y.values

        # Perform Kriging interpolation
        try:
            predicted_values, _ = kriging_model.execute('points', grid_x, grid_y)
            # Round the predicted values
            rounded_values = np.round(predicted_values, decimals=2)
            gdf.loc[gdf[feature].isnull(), feature] = rounded_values
            print("Kriging interpolation completed successfully with rounded values.")
        except Exception as e:
            print(f"Error during Kriging execution: {e}")
            mean_value = gdf[feature].mean()
            gdf[feature].fillna(mean_value, inplace=True)
            print(f"Filled missing values using mean imputation: {mean_value}")

        return gdf
