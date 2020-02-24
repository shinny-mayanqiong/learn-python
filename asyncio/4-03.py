#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: 4-03.py
@create_on: 2020/2/24
@description: 
"""

import asyncio
import sys

async def run_code(code):
    # Create the subprocess; redirect the standard output
    # into a pipe.
    print(sys.executable)

    proc = await asyncio.create_subprocess_exec(
        sys.executable, '-c', code,
        stdout=asyncio.subprocess.PIPE)

    # Read one line of output.
    data = await proc.stdout.readline()
    line = data.decode('ascii').rstrip()

    # Wait for the subprocess exit.
    await proc.wait()

    return line

code = 'import datetime; print(datetime.datetime.now())'
date = asyncio.run(run_code(code))
print(f"Current date: {date}")
