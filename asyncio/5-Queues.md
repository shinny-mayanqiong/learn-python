# Queues 队列

asyncio `Queues` 和 python `queue` 模块相似，因为 asyncio `queues` 不是线程安全的, 所有他们一定要用 async/await.

注意：asyncio queues 的方法没有 timeout 超时参数; 使用 asyncio.wait_for() 方法去给 queue 的操作增加超时限制。

## Queue

### `class asyncio.Queue(maxsize=0, *, loop=None)`

先进先出 (FIFO) 队列。不是线程安全的。

* maxsize：
    - maxsize <= 0 : 队列无限大小
    - maxsize > 0 : 当队列超过限制，await put() 会阻塞，直到某个元素通过 get() 方法被删除掉

python 标准的包 queue， 队列大小在任何时候都可以通过调用 qsize() 方法得到。但是 `asyncio.Queue` 不可以。

#### `maxsize`

队列允许的最大长度。

#### `empty()`

返回队列是否为空

#### `full()`

返回队列是否有 maxsize 个元素。

如果 queue 初始化时 maxsize=0，则 `full()` 永远都返回 `true`

#### `coroutine get()`

从队列中删除并返回一个元素，如果队列为空，会等待有元素可用

#### `get_nowait()`

从队列中 **马上** 删除并返回一个元素，如果没有元素，抛错 QueueEmpty

#### `coroutine put(item)`

添加一个元素到队列中，如果队列满了，等到队列可以加入元素。

#### `put_nowait(item)`

**马上** 添加一个元素到队列中，如果队列满了，抛错 QueueFull

#### `qsize()`

返回队列中的元素个数

#### `coroutine join()`

一直等待，直到队列中的所有项目都已接收和处理完毕。

每将一个 item 添加到队列中时，未完成任务的计数就会增加。每当使用者协同程序调用 `task_done()` 来指示项已被检索并且所有相关工作都已完成时，计数就会下降。当未完成任务的计数降至零时，`join()` 取消阻塞。

#### `task_done()`

表示前面的队列排的任务已经完成。

queue 的消费者调用。对于每个 `get()` 获取一个 task, 在后续调用 `task_done()` 会告诉队列任务已经都处理完

如果 `join()` 当前处于阻塞状态，则它将在处理完所有项后恢复（这意味着对已放入队列中的每个项都接收到 `task_done()` 调用）。

如果调用的次数超过队列中放置的项的次数，则引发 ValueError。

## Priority Queue

### `class asyncio.PriorityQueue`

Queue 的一个变种; 按优先级顺序检索加入的元素（小的优先）

加入的元素格式 **tuple** `(priority_number, data)`

## LIFO Queue

### `class asyncio.LifoQueue`

Queue 的一个变种, 后进先出队列

## Exceptions

### `exception asyncio.QueueEmpty`

This exception is raised when the get_nowait() method is called on an empty queue.

### `exception asyncio.QueueFull`

Exception raised when the put_nowait() method is called on a queue that has reached its maxsize.
