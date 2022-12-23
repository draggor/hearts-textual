#!/usr/bin/env python


import asyncio
import websockets

from .commands import run_command, PLAYERS_TO_SOCKETS, SOCKETS_TO_PLAYERS

connected = set()


async def handler(websocket):
    # Register.
    connected.add(websocket)
    try:
        async for message in websocket:
            result = run_command(message, websocket)
            websockets.broadcast(connected, result.to_json())
    finally:
        # Unregister.
        connected.remove(websocket)
        player = SOCKETS_TO_PLAYERS.pop(websocket)
        PLAYERS_TO_SOCKETS.remove(player)


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
