import uuid

import pandas as pd

from config.config import Config


class DataValidation(Config):
    def __init__(self):
        super().__init__()
        self.feature_types = self.config.get('features', {})

    def validate_and_correct(self, df, feature_name):
        expected_type = self.feature_types.get(feature_name).get('type', {})
        if not expected_type:
            print(f"Feature '{feature_name}' type not defined in config. Validation skipped.")
            return df

        data = df[feature_name]
        if expected_type == "int":
            df[feature_name] = self._validate_and_correct_int(data)
        elif expected_type == "float":
            df[feature_name] = self._validate_and_correct_float(data)
        elif expected_type == "str":
            df[feature_name] = self._validate_and_correct_str(data)
        elif expected_type == "list":
            df[feature_name] = self._validate_and_correct_list(data)
        elif expected_type == "tuple":
            df[feature_name] = self._validate_and_correct_tuple(data)
        elif expected_type == "polygon":
            df[feature_name] = self._validate_and_correct_polygon(data)
        elif expected_type == "bool":
            df[feature_name] = self._validate_and_correct_bool(data)
        elif expected_type == "UUID":
            df[feature_name] = self._validate_and_correct_uuid(data)
        else:
            print(f"Unsupported data type '{expected_type}' for '{feature_name}'.")
        return df

    def _validate_and_correct_int(self, data):
        return data.apply(lambda x: x if isinstance(x, int) and x > 0 else None)

    def _validate_and_correct_float(self, data):
        return data.apply(lambda x: x if isinstance(x, (float, int)) and not pd.isna(x) and x > 0 else None)

    def _validate_and_correct_str(self, data):
        return data.apply(lambda x: x if isinstance(x, str) and bool(x.strip()) else None)

    def _validate_and_correct_list(self, data):
        return data.apply(lambda x: x if isinstance(x, list) and len(x) > 0 else None)

    def _validate_and_correct_tuple(self, data):
        return data.apply(lambda x: x if isinstance(x, tuple) and len(x) > 0 else None)

    def _validate_and_correct_polygon(self, data):
        return data.apply(lambda x: x if hasattr(x, 'geom_type') and x.geom_type == 'Polygon' else None)

    def _validate_and_correct_bool(self, data):
        return data.apply(lambda x: x if isinstance(x, bool) else None)

    def _validate_and_correct_uuid(self, data):
        return data.apply(lambda x: x if isinstance(x, uuid.UUID) else None)
