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


async def say_after(delay, what):
    try:
        print(f"<<< begin {what} at {time_str()}")
        await asyncio.sleep(delay)
        print(f">>> end {what} at {time_str()}")
    except:
        import traceback
        traceback.print_exc()


async def eternity():
    await asyncio.sleep(5)
    print('111 yay!')


async def eternity2():
    try:
        await asyncio.sleep(5)  # Sleep for one hour
    except asyncio.CancelledError:
        print('222 cancelled!')  # container 发生 timeout，这里会抛错 CancelledError
    except asyncio.TimeoutError:
        print('222 timeout!')
    print('222 yay!')


async def main():
    try:
        await asyncio.wait_for(eternity(), timeout=1.0)  # Wait for at most 1 second
    except asyncio.TimeoutError:
        print('111 timeout!')

    try:
        await asyncio.wait_for(eternity2(), timeout=1.0)  # Wait for at most 1 second
    except asyncio.TimeoutError:
        print('222 timeout!')


# asyncio.run(main())


print(f"======= main2 =======")


async def foo():
    return 42


async def main2():
    coro = foo()
    done, pending = await asyncio.wait({coro})
    if coro in done:
        print("coro in done")  # 这个不会打印，因为 coro 会被隐式创建为 Task, 返回的也是 Task 的 set

    task = asyncio.create_task(foo())
    done, pending = await asyncio.wait({task})
    if task in done:
        print("task in done")  # 这个会打印


print(f"======= main3 =======")


async def main3():
    try:
        task1 = asyncio.create_task(say_after(1, 'hello'), name="t1")
        task2 = asyncio.create_task(say_after(5, 'world'), name="t1")
        done, pending = await asyncio.wait({task1, task2}, timeout=2)
        print("done:")
        print(t.name for t in done)
        print("pending:")
        print(t.name for t in pending)
    except:
        # timeout 时间到了，这里并不会抛 TimeoutError
        # 但是 pending 状态的 task 里会有 CancelledError
        import traceback
        traceback.print_exc()
    # 如果这里异步sleep 10s, 这个时候 pending 的 task 是会执行完的，不会有 CancelledError
    # await asyncio.sleep(10)

# asyncio.run(main3())


print(f"======= main4 =======")


async def say_twice(delay, string):
    print(delay*100, string)
    await asyncio.sleep(delay, result="111 " + string)
    print(delay*100, string)
    await asyncio.sleep(delay, result="222 " + string)
    return delay


async def main4():
    task1 = asyncio.create_task(say_twice(1, 'hello'), name="t1")
    task2 = asyncio.create_task(say_twice(2, 'world'), name="t1")
    print(" as_completed 按照返回结果的顺序，依次返回最后 return 的结果")
    for f in asyncio.as_completed({task1, task2}):
        earliest_result = await f  # 按照返回结果的顺序，依次返回最后 return 的结果
        print(earliest_result)

    try:
        task3 = asyncio.create_task(say_twice(3, 'hello'), name="t1")
        task4 = asyncio.create_task(say_twice(4, 'world'), name="t1")
        print(" as_completed 按照返回结果的顺序，依次返回最后 return 的结果, timeout 到了会抛 TimeoutError")
        for f in asyncio.as_completed({task3, task4}, timeout=7):
            earliest_result = await f  # 按照返回结果的顺序，依次返回最后 return 的结果
            print(earliest_result)
    except:
        import traceback
        traceback.print_exc()

# asyncio.run(main4())


print(f"======= main5 =======")


async def say_twice(delay, string):
    print(delay*100, string)
    await say_after(delay, string + "111")
    print(delay*100, string)
    await say_after(delay, string + "222")


async def main5():
    task1 = asyncio.create_task(say_twice(2, 'hello'), name="t1")
    await asyncio.wait_for(task1, timeout=1.0)  # Wait for at most 1 second


asyncio.run(main5())
