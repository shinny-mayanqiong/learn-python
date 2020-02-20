#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: 1-01.py.py
@create_on: 2020/2/19
@description: 
"""

import asyncio


async def main():
    print("hello")
    await asyncio.sleep(1)
    print("world")

asyncio.run(main())

# print(main)  # function
# print(main())  # main() 不会执行代码，返回的是 coroutine object

