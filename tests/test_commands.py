from string import Template

from rich.pretty import pprint
import pytest

from data import hashabledict
from hearts_textual.commands import run_command, Message, reset, GAME


base_template = Template('{"command": "$command", "args": $args}')
echo_template = Template(base_template.substitute(command='echo', args='{"message": "$message"}'))
join_template = Template(base_template.substitute(command='join', args='{"name": "$name"}'))
new_game_str = base_template.substitute(command='new_game', args='{}')


@pytest.fixture
def echo():
    return echo_template.substitute(message='honk')


@pytest.fixture
def join():
    def inner(name):
        return join_template.substitute(name=name)

    return inner

@pytest.fixture
def websocket():
    count = 0

    def inner():
        nonlocal count
        count += 1
        return hashabledict(_id=count)

    return inner

player_names = ['Homer', 'Goose', 'Penguin', 'Menace']
@pytest.fixture
def four_players_and_sockets(join, websocket):
    sockets = []

    for i in range(4):
        w = websocket()
        name = player_names[i]
        run_command(join(name), w)
        sockets.append(w)

    return sockets


@pytest.fixture(autouse=True)
def game_reset():
    yield None
    reset()


class TestCommands:
    def test_echo(self, echo, websocket, capsys):
        result = run_command(echo, websocket())

        captured = capsys.readouterr()

        assert captured.out == "Broadcast: honk\n"

    def test_join(self, join, websocket):
        result = run_command(join('Homer'), websocket())

        assert result.command == 'echo'
        assert result.args['message'] == 'Homer has connected!'


    def test_new_game_not_enough_players_1(self, join, websocket):
        w = websocket()
        run_command(join('A Goose'), w)
        result = run_command(new_game_str, w);

        assert result.args['message'] == 'Must have exactly 4 players!  We have 1'

    def test_new_game_not_enough_players_3(self, join, websocket):
        w1 = websocket()
        w2 = websocket()
        w3 = websocket()
        run_command(join('A Goose'), w1)
        run_command(join('A Burd'), w2)
        run_command(join('A Menace'), w3)
        result = run_command(new_game_str, w1);

        assert result.args['message'] == 'Must have exactly 4 players!  We have 3'

    def test_new_game(self, four_players_and_sockets):
        [w1, w2, w3, w4] = four_players_and_sockets
        result = run_command(new_game_str, w1)

        assert result.command == 'update'
