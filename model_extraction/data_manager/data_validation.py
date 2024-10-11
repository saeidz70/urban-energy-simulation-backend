class DataValidation:
    def validate(self, data):
        # Check if data is None or less than or equal to zero
        # True if the data is valid, False otherwise.
        if data is None or (isinstance(data, (int, float)) and data <= 0):
            return False
        return True
