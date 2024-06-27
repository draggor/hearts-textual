#!/usr/bin/env python


import json

from aioconsole import ainput
import asyncio
import websockets

from hearts_textual.commands import run_command


class Message():
    def __init__(self, message: str) -> None:
        self.message = message


async def consumer_handler(websocket, app):
    async for message in websocket:
        app.handle_message(Message(message))
        response = run_command(message, websocket)
        # app.handle_server_response(response)


async def producer_handler(websocket, app, name):
    # name = await ainput("Name: ")
    await websocket.send(json.dumps({"command": "join", "args": {"name": name}}))
    await asyncio.Future()  # run forever
    # while True:
    #    command = await ainput("Command: ")
    #    await websocket.send(json.dumps({"command": command}))


async def client(app, name):

    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        if app is not None:
            app.websocket = websocket
        consumer_task = asyncio.create_task(consumer_handler(websocket, app))
        producer_task = asyncio.create_task(producer_handler(websocket, app, name))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            # return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()


if __name__ == "__main__":
    asyncio.run(client(None, "Homer"))
