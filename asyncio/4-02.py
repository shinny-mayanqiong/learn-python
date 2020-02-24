#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: 4-01.py.py
@create_on: 2020/2/24
@description: 
"""
import asyncio
import signal

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    proc.send_signal(signal.SIGTERM)

    returncode = await proc.wait()

    print("subprocess returncode:", returncode) # -15 被信号 N 终止
    out = await proc.stdout.read()
    print(out.decode())


asyncio.run(run('ls *.md'))


# asyncio.run(run('sleep 2; echo "hello"'))

# async def main():
#     await asyncio.gather(
#         run('ls /zzz'),
#         run('sleep 1; echo "hello"'))
#
# asyncio.run(main())
