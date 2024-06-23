#!/usr/bin/env python


from dataclasses import dataclass

import asyncio
import websockets
from rich.pretty import pprint
import simple_parsing

from hearts_textual.commands import (
    run_command,
    GAME,
    PLAYERS_TO_SOCKETS,
    SOCKETS_TO_PLAYERS,
)

connected = set()


async def handler(websocket):
    # Register.
    connected.add(websocket)
    try:
        async for message in websocket:
            result = run_command(message, websocket)
            pprint(result)
            websockets.broadcast(connected, result.to_json())
    finally:
        # Unregister.
        connected.remove(websocket)
        player = SOCKETS_TO_PLAYERS.pop(websocket)
        PLAYERS_TO_SOCKETS.pop(player)
        pprint(player)


async def server():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


@dataclass
class Options:
    bots: bool = False


def main():
    options, _ = simple_parsing.parse_known_args(Options)
    GAME.bots = options.bots
    asyncio.run(server())


if __name__ == "__main__":
    main()
