class InvalidCellValueError(Exception):

    def __init__(self, column: str, expected_type: str, received_value: str):
        self.column = column
        self.expected_type = expected_type
        self.received_value = received_value
        self.message = (
            f"Invalid value for column '{column}'. "
            f"Expected type: '{expected_type}', but received: '{received_value}'."
        )
        super().__init__(self.message)


class CyclicLookupError(Exception):
    def __init__(self, lookup_column: str, lookup_row: str):
        self.lookup_column = lookup_column
        self.lookup_row = lookup_row
        self.message = f"Lookup ({lookup_column}, {lookup_row}) creates a cycle, which is not allowed."
        super().__init__(self.message)

