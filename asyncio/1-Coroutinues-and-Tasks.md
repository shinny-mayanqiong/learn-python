# Coroutines

**Coroutines** are a more generalized form of subroutines. Subroutines are entered at one point and exited at another point. Coroutines can be entered, exited, and resumed at many different points. They can be implemented with the `async def` statement.
对子程序的概括的说法，`async def` statement

**coroutine function** A function which returns a coroutine object. A coroutine function may be defined with the async def statement, and may contain await, async for, and async with keywords. 

run a coroutine 3种执行方法：(1-02.py)
1. `asyncio.run()`
2. 在另一个 coroutine 里面
3. `asyncio.create_task()`

# Awaitables

**awaitable** object 可以用在 `await` 表达式里的对象。

1. coroutines (coroutine object)
2. Tasks: 用于安排 coroutines 并行执行，尽快执行
3. Futures (low-level awaitable object): **eventual result** of an asynchronous operation 代表一个异步操作的最终结果

# Running an asyncio Program

`asyncio.run(coro, *, debug=False)` 管理调度 asyncio event loop 并执行异步代码

只能运行在主程序中，`asyncio.run` 会 creates a new event loop and closes it at the end，
`asyncio.run` 不能运行在另一个 asyncio running event loop。

# Creating Tasks

`asyncio.create_task(coro, *, name=None)` => `Task object`
The task is executed in the loop returned by get_running_loop(), `RuntimeError` is raised if there is no running loop in current thread.

# Sleeping

`coroutine asyncio.sleep(delay, result=None, *, loop=None)` ( 1-03.py)
 
`sleep()` always suspends the current task, allowing other tasks to run. 挂起当前 task 去执行另一个 task

*Deprecated* since version 3.8, will be *removed* in version 3.10: The loop parameter.

# Running Tasks Concurrently

`awaitable asyncio.gather(*aws, loop=None, return_exceptions=False)` (1-02.py)

并行运行 `awaitable objects`(aws) 他们会依次开始运行，到 yield / await 异步代码时，会将执行权交给下一个 awaitable object

如果 aws 中 awaitable 是一个普通的 coroutine，它也会像 Task 一样安排执行顺序。

return_exceptions is False (default) : 在遇到第一个 exception 就会立马返回，其他的 awaitables 还是会继续执行，不会 cancalled，但是有没有执行结果是看情况的。

return_exceptions is True: 会忽略 exceptions 返回全部的 the result list.

aws 中任意一个 `Task or Future` cancelled，对于 asyncio.gather 会当作 task raise CancelledError，处理方式按照 return_exceptions 参数设置执行。

如果 gather() is cancelled, all submitted awaitables (that have not completed yet) are also cancelled.

# Shielding From Cancellation

`awaitable asyncio.shield(aw, *, loop=None)` 1-02.py

Protect an `awaitable object` from being cancelled. If aw is a coroutine it is automatically scheduled as a Task.

container task 被 cancel 时，container task 中内部的 task 会抛出 `CancelledError`

# Timeouts

`coroutine asyncio.wait_for(aw, timeout, *, loop=None)`  1-04.py

`timeout` (seconds):  None or a float or int number. If timeout is None, block until the future completes.

Wait for the aw awaitable to complete with a timeout. If aw is a coroutine it is automatically scheduled as a Task.

If a timeout occurs, it cancels the task and raises asyncio.TimeoutError.

To avoid the task cancellation, wrap it in shield().

The function will wait until the future is actually cancelled, so the total wait time may exceed the timeout.

If the wait is cancelled, the future aw is also cancelled.

# Waiting Primitives

`coroutine asyncio.wait(aws, *, loop=None, timeout=None, return_when=ALL_COMPLETED)` => (DoneSet<Tasks|Futures>, PendingSet<Tasks|Futures>). 1-04.py

`return_when`: asyncio.wait 一直并行执行 aws, 直到 return_when 设置的条件

+ `FIRST_COMPLETED`: return when any future finishes or is cancelled.
+ `FIRST_EXCEPTION`: return when any future finishes by raising an exception. If no future raises an exception then it is equivalent to ALL_COMPLETED.
+ `ALL_COMPLETED`: return when all futures finish or are cancelled.

`timeout` (int|float): control the maximum number of seconds to wait before returning. 不会抛 TimeoutError 的错误

tips:
    `wait_for()` if timeout occurs, will cancel the task and raises asyncio.TimeoutError.
    `wait_for()` timeout 时间到了，会抛 TimeoutError, 并且 cancel task
    `wait()` does not cancel the futures when a timeout occurs.
    `wait()` timeout 时间到了，不会抛 TimeoutError 的错误，不会 cancel futures


`asyncio.as_completed(aws, *, loop=None, timeout=None)` =>  [Future objects]  1-04.py

同步的运行 aws. 返回的 Future objects 会依次等到执行结束的 awaitables.

Raises asyncio.TimeoutError if the timeout occurs before all Futures are done.

# Scheduling From Other Threads

`asyncio.run_coroutine_threadsafe(coro, loop)` => concurrent.futures.Future  1-05.py

Submit a coroutine to the given event loop. Thread-safe. Return a concurrent.futures.Future to wait for the result from another OS thread.

# Introspection

`asyncio.current_task(loop=None)` => None | currently running Task instance 

`asyncio.all_tasks(loop=None)` =>  set of not yet finished Task objects

If loop is None, get_running_loop() is used for getting current loop.

# [Task Object](https://docs.python.org/3/library/asyncio-task.html#task-object)

##`class asyncio.Task(coro, *, loop=None, name=None)`

A Future-like object that runs a Python coroutine. Not thread-safe.

Tasks 用来在 event_loop 中运行协程代码，当协程代码运行到 await a Future，Task 会挂起当前执行的协程，等到 the Future 执行完成。当 the Future 执行结束, event_loop 会继续运行接下去的协程代码。

**Event loops** use cooperative scheduling: **an event loop runs one Task at a time**. 一个 event loop 一次只能运行一个 Task。

当一个 Task 在等到 Future 完成时, the event loop 回去运行其他的 Tasks, callbacks, or performs IO operations.

怎样创建 Task:

+ the high-level asyncio.create_task() 
+ the low-level loop.create_task() or ensure_future() functions.

To cancel a running Task use the cancel() method. Calling it will cause the Task to throw a CancelledError exception into the wrapped coroutine. 

如果一个协程在被 cancel 的时候政治等待一个 Future object，等待的这个 Future object 会被 cancelled.

cancelled() can be used to check if the Task was cancelled. The method returns True if the wrapped coroutine did not suppress the CancelledError exception and was actually cancelled.

asyncio.Task inherits from Future all of its APIs except Future.set_result() and Future.set_exception().

Tasks support the contextvars module. When a Task is created it copies the current context and later runs its coroutine in the copied context.

### `cancel()`

`Task.cancel() ` 会 raise CancelledError（在 event loop 中下一次循环到这个 Task 的时候），可以确保 Task cancelled，`Future.cancel()` 并不能保证。

### `cancelled()` => bool

Return True if the Task is cancelled.

The Task is cancelled when the cancellation was **requested with cancel()** and the **wrapped coroutine** propagated the CancelledError exception thrown into it.

### `done()` => bool
Return True if the Task is done.

A Task is done when the wrapped coroutine either **returned a value**, **raised an exception**, or the Task was **cancelled**.

### `result()` => the result of the Task

If the Task is done, the result of the wrapped coroutine is returned (or if the coroutine raised an exception, that exception is re-raised.)

If the Task has been cancelled, this method raises a **CancelledError** exception.

If the Task’s result isn’t yet available, this method raises a **InvalidStateError** exception.

### `exception()` => the exception of the Task

If the wrapped coroutine raised an exception that exception is returned. 

If the wrapped coroutine returned normally this method returns **None**.

If the Task has been cancelled, this method raises a **CancelledError** exception.

If the Task isn’t done yet, this method raises an **InvalidStateError** exception.

### `add_done_callback(callback, *, context=None)`

Add a callback to be run when the Task is done. This method should only be used in low-level callback-based code.

See the documentation of Future.add_done_callback() for more details.

### `remove_done_callback(callback)`

Remove callback from the callbacks list. This method should only be used in low-level callback-based code.

See the documentation of Future.remove_done_callback() for more details.

### `get_stack(*, limit=None)`

Return the list of stack frames for this Task. The frames are always ordered from oldest to newest. Only one stack frame is returned for a suspended coroutine.

If the wrapped coroutine is not done, this returns the stack where it is suspended. 

If the coroutine has completed successfully or was cancelled, this returns an empty list. 

If the coroutine was terminated by an exception, this returns the list of traceback frames.

The optional limit argument sets the maximum number of frames to return; by default all available frames are returned. The ordering of the returned list differs depending on whether a stack or a traceback is returned: the newest frames of a stack are returned, but the oldest frames of a traceback are returned. (This matches the behavior of the traceback module.)

### `print_stack(*, limit=None, file=None)`

Print the stack or traceback for this Task.

This produces output similar to that of the traceback module for the frames retrieved by get_stack().

The limit argument is passed to get_stack() directly.

The file argument is an I/O stream to which the output is written; by default output is written to sys.stderr.

### `get_coro()`

Return the coroutine object wrapped by the Task. New in version 3.8.

### `get_name()`

Return the name of the Task. New in version 3.8.

### `set_name(value)`

Set the name of the Task. The value argument can be any object, which is then converted to a string. New in version 3.8.

### classmethod `all_tasks(loop=None)` => a set of all tasks for an event loop

**Deprecated** Use the asyncio.all_tasks()

### classmethod `current_task(loop=None)` => the currently running task | None

**Deprecated** Use the asyncio.current_task()

# Generator-based Coroutines 1-06.py

旧的协程语法, 在 Python 中对协程的支持是通过generator实现的。

在generator中，我们不但可以通过for循环来迭代，还可以不断调用next()函数获取由yield语句返回的下一个值。

但是Python的yield不但可以返回一个值，它还可以接收调用者发出的参数。

```python
# 传统的生产者-消费者模型是一个线程写消息，一个线程取消息，通过锁机制控制队列和等待，但一不小心就可能死锁。
# 如果改用协程，生产者生产消息后，直接通过yield跳转到消费者开始执行，待消费者执行完毕后，切换回生产者继续生产，效率极高：
def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'

def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()

c = consumer()
produce(c)
```


`@asyncio.coroutine` 装饰器，支持旧的 generator 语法

```python
@asyncio.coroutine
def old_style_coroutine():
    yield from asyncio.sleep(1)

async def main():
    await old_style_coroutine()
```

`asyncio.iscoroutine(obj)` => bool

Return True if obj is a coroutine object.

This method is different from inspect.iscoroutine() because it returns True for generator-based coroutines.

`asyncio.iscoroutinefunction(func)`

Return True if func is a coroutine function.

This method is different from inspect.iscoroutinefunction() because it returns True for generator-based coroutine functions decorated with @coroutine.


