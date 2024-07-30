from textual.messages import Message


class BasicMessage(Message):
    def __init__(self, message: str, game=None) -> None:
        self.message = message
        self.game = game
        super().__init__()


class FooterMessage(Message):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__()


class UpdateMessage(Message):
    def __init__(self, game) -> None:
        self.game = game
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


class CommandMessage(Message):
    commands = None

    # TODO: type this
    def __init__(
        self, command_full=None, *, command=None, args=None, commands=None
    ) -> None:
        if command_full is not None:
            self.command = command_full
        elif commands is not None:
            self.commands = commands
        elif command is not None and args is not None:
            self.command = {"command": command, "args": args}
        else:
            raise Exception(
                "Must have either command_full or both command and args or list of full commands"
            )
        super().__init__()
