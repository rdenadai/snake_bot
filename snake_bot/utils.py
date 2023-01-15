class MockOpenAIResponse:
    __slots__ = "text"

    def __init__(self, text: str = "") -> None:
        self.text = ""
