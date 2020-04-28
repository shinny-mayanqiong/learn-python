# Event Loop

前言

`event loop` 是 `asyncio` 的核心。`Event loops` 可以运行异步 tasks ， callbacks，运行网络IO操作，运行子进程。

 such as asyncio.run(), and should rarely need to reference the loop object or call its methods. This section is intended mostly for authors of lower-level code, libraries, and frameworks, who need finer control over the event loop behavior.
