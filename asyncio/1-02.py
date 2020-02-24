#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: 1-02.py.py
@create_on: 2020/2/19
@description: 
"""
import asyncio
import time

def time_str():
    ct = time.time()
    ms = (ct - int(ct)) * 10000000
    return "%s%03d" % (time.strftime("%H:%M:%S."), ms)


import types
@types.coroutine
def mysleep(delay):
    for i in range(10):
        print("mysleep", delay, i)
        if( i % 2): yield

@types.coroutine
def __mysleep0():
    """Skip one event loop run cycle.

    This is a private helper for 'asyncio.sleep()', used
    when the 'delay' is set to 0.  It uses a bare 'yield'
    expression (which Task.__step knows how to handle)
    instead of creating a Future object.
    """
    yield

async def say_after(delay, what):
    try:
        print(f"<<< begin say_after {what} at {time_str()}")
        await asyncio.sleep(delay)
        # await mysleep(delay)
        print(f">>>  end say_after {what} at {time_str()}")
    except Exception as e:
        print("Exception", e)
        raise e


async def main():
    print(f"started main at {time_str()}")
    await say_after(1, 'hello')
    await say_after(2, 'world')
    print(f"finished main at {time_str()}")

# asyncio.run(main())

print(f"======= task =======")


async def main2():
    task1 = asyncio.create_task(say_after(1, 'hello'))
    task2 = asyncio.create_task(say_after(2, 'world'))
    # print(f"started main2 at {time_str()}")
    # await say_after(1, "yanqiong")
    # await mysleep()
    # await asyncio.sleep(1)
    # print(f"started main2 at {time_str()}")
    # Wait until both tasks are completed (should take around 2 seconds.)
    await task1
    await task2

    # 或者
    await asyncio.gather(task1, task2, say_after(3, 'world'))  # task 和
    # asyncio.run(main())  # RuntimeError: asyncio.run() cannot be called from a running event loop
    # print(f"finished main2 at {time_str()}")

# asyncio.run(main2())

print(f"======= main3 =======")
async def main3():
    task1 = asyncio.create_task(say_after(1, 'hello'))
    task2 = asyncio.create_task(say_after(2, 'world'))
    await asyncio.gather(task1, task2, say_after(3, 'world'))
    await say_after(1, 'world')
    # say_after(3, 'world') 会当作 Task 安排在 asyncio 执行流程，
    # 如果都放在 await 后面，coroutine 会在上一行返回结果之后，开始顺序
    """
    await task1
    await say_after(3, 'world') # 会在 task1 返回时，才开始这个 coroutine
    await task2
    """

# asyncio.run(main3())

print(f"======= main4 =======")

async def err_say_after(delay):
    print("begin err_say")
    await asyncio.sleep(delay)
    raise TypeError

async def main4():
    task1 = asyncio.create_task(say_after(1, 'hello'))
    task2 = asyncio.create_task(say_after(2, 'world'))
    try:
        await asyncio.gather(task1, task2, say_after(3, 'world3'), err_say_after(1), return_exceptions=False)
        # result_list = await asyncio.gather(task1, task2, say_after(3, 'world3'), err_say_after(1), return_exceptions=True) # 内部的 task 不会抛错，一定会等到所有的 task 执行完
        # print(result_list)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        pass
    await say_after(5, 'yanqiong')  # 是都会执行

    # err_say_after(1) 抛错，其他的 task 都还会执行，但是没有对象等待他们执行了
    # 但是分两种情况
    # 1 最后一个 await say_after(1, 'yanqiong') 如果设置 1s, 1s 后整个 main 函数返回，
    #   asyncio.gather 中未执行完的 task 不会继续打印结果了，因为 asyncio.gather 已经报错抛出了
    # 2 最后一个 await say_after(1, 'yanqiong') 如果设置 5s, 5s 后整个 main 函数返回，
    #   asyncio.gather 中所有 task 都执行完打印出结果了，

# asyncio.run(main4())

print(f"======= main5 =======")

async def say_pre(delay, what):
    # print(f"<<< begin pre {what} at {time_str()}")
    await say_after(delay, what)
    # await asyncio.shield(say_after(delay, what))  # 在执行的时候，如果 say_pre 的 task 被 cancel，那么这个与上面是等价的

    # try:
    #     await say_after(delay, what)
    #     # await asyncio.shield(say_after(delay, what))
    # except asyncio.CancelledError as e:
    #     print("CancelledError", time_str())
    #     # 虽然 say_after 没有被 cancel，但是 say_pre 的 task 被 cancel, 这里也会抛出 CancelledError 的 Exception
    #     # 这样的代码可以完全忽略掉 CancelledError，但是 say_after 已经被 cancel ，不会继续执行下去
    #     # 不推荐这样的用法
    #     res = None
    # print(f">>> end pre {what} at {time_str()}")

async def cancel_task(delay, task):
    await asyncio.sleep(delay)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("cancel: task is cancelled now")
    print(task.cancelled())


async def sleep_wait(delay):
    print("before time.sleep(", delay, ")")
    time.sleep(delay)
    print("end time.sleep(", delay, ")")

async def init():
    task1 = asyncio.create_task(say_pre(1, '111'))
    task2 = asyncio.create_task(say_pre(6, '222'))
    task3 = asyncio.create_task(say_pre(2, '333'))
    task4 = asyncio.create_task(say_pre(2, '444'))
    task5 = asyncio.create_task(say_pre(2, '555'))
    task5 = asyncio.create_task(sleep_wait(1))  # 如果这个 task 会同步执行的时间超过了下面 cancel task 的时间，那么task就无效了
    await asyncio.gather(task1, task2, task3, task4, task5, cancel_task(1.5, task2))


async def main5():
    await init()
    # try:
    #     await asyncio.shield(init())
    # except Exception as e:
    #     import traceback
    #     traceback.print_exc()

asyncio.run(main5())
