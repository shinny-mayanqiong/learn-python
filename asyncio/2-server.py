#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: 2-01.py.py
@create_on: 2020/2/20
@description: 
"""
import asyncio

import asyncio


async def handle_echo(reader, writer):
    data = await reader.read(10)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    data = await reader.read(10)
    message2 = data.decode()

    print(f"Received {message!r} {message2!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()


async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
