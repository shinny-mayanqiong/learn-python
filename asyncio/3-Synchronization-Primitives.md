# Synchronization Primitives 同步原语

`asyncio` 同步原语的设计类似于线程模块的原语，但有两个重要的注意事项：

* `asyncio` 同步原语不是线程安全的，因此它们不应该用于操作系统线程同步（应该使用线程）
* `asyncio` 同步原语的方法不接受 timeout 超时参数；请使用 `asyncio.wait_for()` 函数执行超时操作

`asyncio` has the following basic synchronization primitives:

1. Lock 锁
2. Event 事件
3. Condition 条件
4. Semaphore 信号量
5. BoundedSemaphore 边界信号量

## Lock

### `class asyncio.Lock(*, loop=None)`

为 `asyncio tasks` 实现互斥锁。不是线程安全的。

锁 (`asyncio tasks`) 可用于保证对共享资源的独占访问。

使用锁的首选方法是 `async with` 语句：

```python
lock = asyncio.Lock()

# ... later
async with lock:
    # access shared state
```

等价于

```python
lock = asyncio.Lock()

# ... later
await lock.acquire()
try:
    # access shared state
finally:
    lock.release()
```

#### `coroutine acquire()`

获取锁。此方法等待锁解除锁定，将其设置为 `locked` 并返回 `True`。

当在 `acquire()` 中有多个协程被阻塞，等待解锁锁时，最终只会运行一个协程。

获取一个锁是公平的: 获得的协程是第一个开始等待锁的协程。

#### `release()`

Release the lock.

When the lock is locked, reset it to unlocked and return.

If the lock is unlocked, a RuntimeError is raised.

#### `locked()`

Return True if the lock is locked.

## Event

### `class asyncio.Event(*, loop=None)`

事件对象。不是线程安全的。

`asyncio.Event` 可以用于通知多个 asyncio tasks 发生了某个事件.

事件对象管理一个内部标志，可以使用 `set()` 方法将其设置为 `true`，使用 `clear()` 方法将其重置为 `false`。 

`wait()` 方法将阻塞，直到标志设置为 `true`。标志最初值为 `false`。

```python
async def waiter(event):
    print('waiting for it ...')
    await event.wait()
    print('... got it!')

async def main():
    # Create an Event object.
    event = asyncio.Event()

    # Spawn a Task to wait until 'event' is set.
    waiter_task = asyncio.create_task(waiter(event))

    # Sleep for 1 second and set the event.
    await asyncio.sleep(1)
    event.set()

    # Wait until the waiter task is finished.
    await waiter_task

asyncio.run(main())
```

#### `coroutine wait()`

等待事件 `event` 被设为 `true`。

如果事件调用过 `set()`，请立即返回 `true`。否则阻塞，直到另一个任务调用 `set()`。

#### `set()`

设置事件。设事件内部标志为 `true`。所有等待事件 `await event.wait()` 设置的任务将立即被唤醒。

#### `clear()`

清除（取消设置）事件，内部标志重新设为 `false`。等待 `wait()` 的任务现在将阻塞，直到再次调用 `set()` 方法。

#### `is_set()`

是否已设置。如果设置了事件，则返回 `true`。

## Condition

### `class asyncio.Condition(lock=None, *, loop=None)`

条件对象。不是线程安全的。

任务 (asyncio.task) 可以使用 asyncio 条件原语等待某个事件发生，然后以独占方式访问共享资源。

本质上，条件对象结合了事件 (Event) 和锁 (Lock) 的功能。可以让多个条件对象共享一个锁，这允许在对共享资源的特定状态感兴趣的不同任务之间协调对共享资源的独占访问。

which allows coordinating exclusive access to a shared resource between different tasks interested in particular states of that shared resource.

参数: lock = lock 对象 或 None (自动创建新的 Lock)

推荐用法:

```python
cond = asyncio.Condition()

# ... later
async with cond:
    await cond.wait()
```

等价于：

```python
cond = asyncio.Condition()

# ... later
await cond.acquire()
try:
    await cond.wait()
finally:
    cond.release()
```

#### `coroutine acquire()`

获取底层锁。此方法等待底层锁解除锁定，将其设置为 `locked` 并返回 `true`

#### `notify(n=1)`

在此条件下最多唤醒 n 个等待的任务（默认为1个）。如果没有任务在等待，则方法为 noop。

必须在调用此方法之前获取锁，并在之后不久释放。如果使用未锁定的锁调用，则会引发运行时错误 `RuntimeError`。

#### `locked()`

Return True if the underlying lock is acquired. 如果底层锁被获取了，则返回 True。

#### `notify_all()`

唤醒在此条件下等待的所有任务。

此方法的行为类似于 `notify()`，但会唤醒所有等待的任务。

必须在调用此方法之前获取锁，并在之后不久释放。如果使用未锁定的锁调用，则会引发运行时错误。

#### `release()`

释放底层锁。在未解锁的锁上调用此方法时，将引发运行时错误 `RuntimeError`。

#### `coroutine wait()`

等待直到 `Lock` 被释放。

当前执行的 task 在调用此方法时，如果尚未获取锁。则会引发运行时错误 RuntimeError。

此方法释放底层锁，然后阻塞，直到被 `notify()` 或 `notify_all()` 调用唤醒为止。一旦唤醒，`Condition` 将重新获取其锁，此方法将返回 True。

#### `coroutine wait_for(predicate)`

等到 `predicate` 变为 true。

`predicate` 必须是可调用的，其返回值为 bool 类型。

## Semaphore

### `class asyncio.Semaphore(value=1, *, loop=None)`

信号量对象。不是线程安全的。

信号量管理一个内部计数器(对于可用资源计数)，该计数器由每个 `acquire()` 调用递减，并由每个 `release()` 调用递增。计数器永远不能低于零；当 `acquire()` 发现它为零时，它将阻塞，直到某些任务调用 `release()` 为止。

可选值参数 `value` 提供内部计数器的初始值（默认为1）。如果给定值小于 0，则会引发值错误 ValueError。

推荐用法：

```python
sem = asyncio.Semaphore(10)

# ... later
async with sem:
    # work with shared resource
```

等价于

```python
sem = asyncio.Semaphore(10)

# ... later
await sem.acquire()
try:
    # work with shared resource
finally:
    sem.release()
```

#### `coroutine acquire()`

获取信号量。

如果内部计数器大于0，则将其减1并立即返回 true。如果为零，则等待调用 `release()` 并返回 true。

If the internal counter is greater than zero, decrement it by one and return True immediately. If it is zero, wait until a release() is called and return True.

#### `locked()`

如果无法立即获取信号量，则返回 True。

#### `release()`

释放一个信号量，使内部计数器递增一个。可以唤醒等待获取信号量的任务。

与 BoundedSemaphore 不同，Semaphore 允许进行更多的 release() 调用比 acquire() 调用多。

## BoundedSemaphore

### `class asyncio.BoundedSemaphore(value=1, *, loop=None)`

有界信号量对象。不是线程安全的。

有界信号量是信号量的另一个版本，如果它将内部计数器增加到初始值以上，则会在 `release()` 中引发 ValueError。
