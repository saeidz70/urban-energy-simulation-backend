import uuid

import pandas as pd

from config.config import Config


class DataValidation(Config):
    def __init__(self):
        super().__init__()
        self.feature_types = self.config.get('features', {})

    def validate_and_correct(self, df, feature_name):
        """
        Validate and correct the feature column based on the expected type.
        """
        expected_type = self.feature_types.get(feature_name, {}).get('type', {})
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
        """
        Validate integers: Allow non-negative integers and convert others to 0.
        """
        return data.apply(lambda x: int(x) if isinstance(x, (int, float)) and x >= 0 else 0)

    def _validate_and_correct_float(self, data):
        """
        Validate floats: Allow positive floats or integers and set invalid values to 0.0.
        """
        return data.apply(lambda x: float(x) if isinstance(x, (float, int)) and not pd.isna(x) and x >= 0 else 0.0)

    def _validate_and_correct_str(self, data):
        """
        Validate strings: Allow non-empty, trimmed strings; replace others with an empty string.
        """
        return data.apply(lambda x: str(x).strip() if isinstance(x, str) and bool(x.strip()) else "")

    def _validate_and_correct_list(self, data):
        """
        Validate lists: Allow non-empty lists; replace others with an empty list.
        """
        return data.apply(lambda x: x if isinstance(x, list) and len(x) > 0 else [])

    def _validate_and_correct_tuple(self, data):
        """
        Validate tuples: Allow non-empty tuples; replace others with an empty tuple.
        """
        return data.apply(lambda x: x if isinstance(x, tuple) and len(x) > 0 else ())

    def _validate_and_correct_polygon(self, data):
        """
        Validate polygons: Allow objects with 'Polygon' geometry type.
        """
        return data.apply(lambda x: x if hasattr(x, 'geom_type') and x.geom_type == 'Polygon' else None)

    def _validate_and_correct_bool(self, data):
        """
        Validate booleans: Allow only boolean values; replace others with False.
        """
        return data.apply(lambda x: x if isinstance(x, bool) else False)

    def _validate_and_correct_uuid(self, data):
        """
        Validate UUIDs: Allow valid UUIDs; replace others with None.
        """
        return data.apply(lambda x: x if isinstance(x, uuid.UUID) else None)
