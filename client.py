#!/usr/bin/env python


import json

from aioconsole import ainput
import asyncio
import websockets


async def consumer_handler(websocket):
    async for message in websocket:
        print(f"\n<<< {message}")


async def producer_handler(websocket):
    name = input("Name: ")
    await websocket.send(json.dumps({"command": "join", "args": {"name": name}}))
    while True:
        command = await ainput("Command: ")
        await websocket.send(json.dumps({"command": command}))


async def client():

    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        consumer_task = asyncio.create_task(consumer_handler(websocket))
        producer_task = asyncio.create_task(producer_handler(websocket))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            # return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()


if __name__ == "__main__":
    asyncio.run(client())
