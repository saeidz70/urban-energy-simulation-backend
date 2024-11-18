class DataValidation:
    def validate(self, data):
        # Check if data is None or less than or equal to zero
        # True if the data is valid, False otherwise.
        if data is None or (isinstance(data, (int, float, str)) and data <= 0):
            return False
        return True

'''

import numpy as np
import pandas as pd

class DataValidation:
    def __init__(self, config):
        self.feature_types = config.get('features_collection', {})

    def validate(self, data, feature_name):
        # Check if the feature is defined in the config file
        expected_type = self.feature_types.get(feature_name)
        if not expected_type:
            print(f"Feature '{feature_name}' type not defined in config. Validation skipped.")
            return False

        # Perform validation based on the expected data type
        if expected_type == "int":
            return self._validate_int(data)
        elif expected_type == "float":
            return self._validate_float(data)
        elif expected_type == "str":
            return self._validate_str(data)
        elif expected_type == "list":
            return self._validate_list(data)
        elif expected_type == "tuple":
            return self._validate_tuple(data)
        elif expected_type == "polygon":
            return self._validate_polygon(data)
        else:
            print(f"Unsupported data type '{expected_type}' for '{feature_name}'.")
            return False

    def _validate_int(self, data):
        # Check for valid integer values in a pandas Series
        if isinstance(data, pd.Series):
            return data.apply(lambda x: isinstance(x, int) and x > 0).all()
        return isinstance(data, int) and data > 0

    def _validate_float(self, data):
        # Check for valid float values in a pandas Series
        if isinstance(data, pd.Series):
            return data.apply(lambda x: isinstance(x, (float, int)) and not pd.isna(x) and x > 0).all()
        return isinstance(data, (float, int)) and not np.isnan(data) and data > 0

    def _validate_str(self, data):
        if isinstance(data, pd.Series):
            return data.apply(lambda x: isinstance(x, str) and bool(x.strip())).all()
        return isinstance(data, str) and bool(data.strip())

    def _validate_list(self, data):
        return isinstance(data, list) and len(data) > 0

    def _validate_tuple(self, data):
        return isinstance(data, tuple) and len(data) > 0

    def _validate_polygon(self, data):
        # Check if the data has a geom_type attribute and is a Polygon
        if isinstance(data, pd.Series):
            return data.apply(lambda x: hasattr(x, 'geom_type') and x.geom_type == 'Polygon').all()
        return hasattr(data, 'geom_type') and data.geom_type == 'Polygon'

'''
