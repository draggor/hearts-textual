import pytest

from hearts_textual.commands import run_command, Message


@pytest.fixture
def echo():
    return '{"command": "echo", "args": {"message": "honk"}}'


@pytest.fixture
def websocket():
    return {}


class TestCommands:
    def test_run_echo(self, echo, websocket, capsys):
        result = run_command(echo, websocket)

        captured = capsys.readouterr()

        assert captured.out == "Broadcast: honk\n"
