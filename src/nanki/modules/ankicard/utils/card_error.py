class CardError(Exception):
    """Errors related to the parsing of the card."""

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
