#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: 1-05.py.py
@create_on: 2020/2/20
@description: 
"""
import asyncio, concurrent
import time, threading

# 新线程执行的代码:
async def sub_main():
    print('thread %s is running...' % threading.current_thread().name)
    n = 0
    while n < 5:
        n = n + 1
        print('thread %s >>> %s' % (threading.current_thread().name, n))
        await asyncio.sleep(1)
    print('thread %s ended.' % threading.current_thread().name)

def sub(loop):
    asyncio.set_event_loop(loop)
    loop.create_task(sub_main())
    loop.run_forever()

def time_str():
    ct = time.time()
    ms = (ct - int(ct)) * 10000000
    return "%s%03d" % (time.strftime("%H:%M:%S."), ms)


async def say_after(delay, what):
    # print(f"<<< begin {what} at {time_str()}")
    # await asyncio.sleep(delay)
    # print(f">>> end {what} at {time_str()}")
    # return delay * 100
    try:
        print(f"<<< begin {what} at {time_str()}")
        await asyncio.sleep(delay)
        print(f">>> end {what} at {time_str()}")
        return delay * 100
    except asyncio.exceptions.CancelledError as e:
        print("except CancelledError")
    except:
        import traceback
        traceback.print_exc()


async def main():
    # Submit the coroutine to a given loop
    loop_b = asyncio.new_event_loop()
    print('thread %s is running...' % threading.current_thread().name)
    t = threading.Thread(target=sub, args=(loop_b,), name='SubThread')
    t.start()
    # t.join()
    print('thread %s ended.' % threading.current_thread().name)

    future = asyncio.run_coroutine_threadsafe(say_after(2, "hello"), loop_b)
    try:
        result = future.result(3)  # future.result(timeout) timeout 可以设置超时时间
    except concurrent.futures._base.TimeoutError:  # 使用 except asyncio.TimeoutError 捕获不到这里，会到下一个 except 里
        print('The coroutine took too long, cancelling the task...')
        future.cancel()
    except Exception as exc:
        print(f'The coroutine raised an exception: {exc!r}')
    else:
        print(f'The coroutine returned: {result!r}')

    # Wait for the result with an optional timeout argument
    # assert future.result(timeout) == 3


asyncio.run(main())
