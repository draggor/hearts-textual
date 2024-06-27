from textual.messages import Message


class BasicMessage(Message):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__()


class ToasterMessage(Message):
    def __init__(
        self, message: str, *, title="", severity="information", timeout=None
    ) -> None:
        self.message = message
        self.title = title
        self.severity = severity
        self.timeout = timeout
        super().__init__()
