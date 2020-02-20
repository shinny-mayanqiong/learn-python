#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: 1-03.py.py
@create_on: 2020/2/20
@description: 
"""
import asyncio
import datetime

async def display_date():
    loop = asyncio.get_running_loop()
    print("loop.time()", loop.time())
    end_time = loop.time() + 5.0
    while True:
        print(datetime.datetime.now())
        print("loop.time()", loop.time())
        if (loop.time() + 1.0) >= end_time:
            break
        t = await asyncio.sleep(1, result=loop.time())
        print(t)

asyncio.run(display_date())
