class SheetValuesJsonEncoder:
    @staticmethod
    def encode(obj):
        if isinstance(obj, dict):
            # Convert tuple keys to strings
            return {str(k): v for k, v in obj.items()}
        return obj

