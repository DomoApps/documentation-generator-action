class LineComment:

    def __init__(self, line: int, text: str):
        self.line = line
        self.text = text

    def __eq__(self, other):
        if not isinstance(other, LineComment):
            return False
        return self.line == other.line and self.text == other.text
