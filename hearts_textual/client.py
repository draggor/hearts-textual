#!/usr/bin/env python


import json

from aioconsole import ainput
import asyncio
import websockets

from hearts_textual.commands import run_command
from tui.messages import BasicMessage, ToasterMessage


async def consumer_handler(websocket, app):
    async for message in websocket:
        response = run_command(message, websocket)
        if type(response) is list:
            for resp in response:
                app.post_message(BasicMessage(resp))
        else:
            app.post_message(BasicMessage(response))


async def producer_handler(websocket, app, name):
    await websocket.send(json.dumps({"command": "join", "args": {"name": name}}))
    while True:
        command = await app.command_queue.get()
        await websocket.send(json.dumps(command))
        app.command_queue.task_done()


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
