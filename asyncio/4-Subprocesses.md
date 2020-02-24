# Subprocesses

asyncio 在启动 shell 子进程，获取运行结果：(4-01.py)

```python
import asyncio

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')

asyncio.run(run('ls /zzz'))
```

## Creating Subprocesses

### `coroutine asyncio.create_subprocess_exec(program, *args, stdin=None, stdout=None, stderr=None, loop=None, limit=None, **kwds)`

Create a subprocess.

The limit argument sets the buffer limit for StreamReader wrappers for Process.stdout and Process.stderr (if subprocess.PIPE is passed to stdout and stderr arguments).

Return a Process instance.

See the documentation of loop.subprocess_exec() for other parameters.

### `coroutine asyncio.create_subprocess_shell(cmd, stdin=None, stdout=None, stderr=None, loop=None, limit=None, **kwds)`

Run the cmd shell command.

The limit argument sets the buffer limit for StreamReader wrappers for Process.stdout and Process.stderr (if subprocess.PIPE is passed to stdout and stderr arguments).

Return a Process instance.

### Tips

1. 应用本身需要检查 shell 执行的内容的正确性， python 中的 `shlex.quote()` 可以用于构造shell命令中的转义空格和特殊字符
2. 默认的 event loop (`SelectorEventLoop`) 在 windows 上不支持子进程。
    Subprocesses are available for Windows if a `ProactorEventLoop` is used. See Subprocess Support on Windows for details.
3. asyncio 还有 low-level APIs 可以运行子进程: `loop.subprocess_exec()`, `loop.subprocess_shell()`, `loop.connect_read_pipe()`, `loop.connect_write_pipe()`, as well as the `Subprocess Transports` and `Subprocess Protocols`.

## Constants

### `asyncio.subprocess.PIPE`

Can be passed to the stdin, stdout or stderr parameters.

If PIPE is passed to stdin argument, the Process.stdin attribute will point to a StreamWriter instance.

If PIPE is passed to stdout or stderr arguments, the Process.stdout and Process.stderr attributes will point to StreamReader instances.

### `asyncio.subprocess.STDOUT`

Special value that can be used as the stderr argument and indicates that standard error should be redirected into standard output.

### `asyncio.subprocess.DEVNULL`

Special value that can be used as the stdin, stdout or stderr argument to process creation functions. It indicates that the special file os.devnull will be used for the corresponding subprocess stream.

## Interacting with Subprocesses

### `class asyncio.subprocess.Process`

不是线程安全的

`create_subprocess_exec()` 或 `create_subprocess_shell()` 返回的操作系统进程实例。

其 API 与 python 中 `subprocess.Popen` 类设计的类似，但是有一些不同：

1. 不像 `Popen`, `Process` 实例没有等价于 `poll()` 的方法;
2. `communicate()` 和 `wait()` 方法没有 `timeout` 超时参数: 需要使用 `wait_for()`;
3. `Process.wait()` 是异步方法, 而 `subprocess.Popen.wait()` 方法的实现会阻塞进程;
4. 不支持 `universal_newlines` 参数.

#### `coroutine wait()`

等待子进程结束。返回 returncode

Note: 这个方法可能会造成死锁，当使用 stdout=PIPE or stderr=PIPE 并且子进程产生了大量输出以致阻塞掉等待的 OS pipe buffer，不能接受更多数据。

当需要使用 pipes 时，用 `communicate()` 方法可以避免上面的情况。

#### `coroutine communicate(input=None)`

* `input` (optional`[bytes object]`): sent to the child process.
* return a tuple (stdout_data, stderr_data)

与子进程交互:

* send data to stdin (if input is not None);
* read data from stdout and stderr, until EOF is reached;
* wait for process to terminate.

在将输入写入 stdin 时，如果发生 `BrokenPipeError` 或者 `ConnectionResetError`, exception 会被忽略。当进程在所有数据写入stdin之前退出，就会发生这种情况。

如果需要将数据发送到进程的stdin，则需要使用 stdin=PIPE 创建进程。类似地，要在结果元组中获取除 None 以外的任何内容，必须使用 stdout=PIPE or stderr=PIPE 参数创建进程。

请注意，读取的数据是在内存中缓冲的，因此如果数据大小很大或不受限制，请不要使用此方法。

#### `send_signal(signal)`  4-02.py

向子进程发送信号 signal

Note: 在 Windows 上, `SIGTERM` 是 `terminate()` 的别名

向子进程发送信号信号。注意：在 Windows 上，SIGTERM 是 terminate() 的别名。

可以将 `CTRL_C_EVENT` 和 `CTRL_BREAK_EVENT` 发送到使用 creationflags 参数启动的进程，该参数包括 CREATE_NEW_PROCESS_GROUP。

 `CTRL_C_EVENT` 和 `CTRL_BREAK_EVENT` 只支持 Windows

#### `terminate()`

停止子进程。

在 POSIX 系统上，此方法向子进程发送 `signal.SIGTERM`。

在 Windows 上，调用 Win32 API 函数 TerminateProcess() 来停止子进程。

#### `kill()`

杀掉子进程。

在 POSIX 系统上，此方法将 SIGKILL 发送给子进程。

在 Windows 上，此方法是 terminate() 的别名。

ps: 

`SIGTERM` 也可以称为软终止，因为接收 SIGTERM 信号的进程可以选择忽略它。这是杀死进程的一种礼貌方式。
    `kill <pid>`
    
`SIGKILL` 用于立即终止进程。此信号不可忽略或阻止。该进程及其线程（如果有）将终止。这是杀死进程的一种残酷方式，应仅用作最后的手段。假设您要关闭一个无响应的进程。在这种情况下可以使用SIGKILL。
    `kill -9 <pid>`

SIGKILL vs SIGTERM
* SIGTERM 正常终止进程，而 SIGKILL 立即终止进程。
* 程序可以处理，忽略和阻止 SIGTERM 信号，但是不能处理或阻止 SIGKILL。
* SIGTERM 不会终止子进程。SIGKILL 也会杀死子进程。

#### `stdin`

Standard input stream 标准输入流 (StreamWriter) or None.

#### `stdout`

Standard output stream 标准输出流 (StreamReader) or None.

#### `stderr`

Standard error stream 标准错误流 (StreamReader) or None.

使用 communicate() 方法而不是 `process.stdin.write()`、`await process.stdout.read()`、`await process.stderr.read`. 

这样可以避免 由于流停下来读或写并阻塞子进程 而导致的死锁。

#### `pid`

Process identification number (PID) 进程唯一ID.

注：对于由 `create_subprocess_shell` 创建进程，此属性是 shell 进程的 id。

#### `returncode`

进程退出时的返回代码。

None 表示进程尚未终止。

负值 表示子进程被信号 N 终止（仅限POSIX）。

## Subprocess and Threads

默认情况下，标准 asyncio event loop 支持从不同线程运行子进程。

在 Windows 上，子进程仅由 ProactorEventLoop 提供（默认），SelectorEventLoop 不支持子进程。

在 UNIX 上，子监视程序用于子进程完成等待，参阅进程监视程序 [asyncio-watchers](https://docs.python.org/3/library/asyncio-policy.html#asyncio-watchers)。

使用非活动的当前子观察程序生成子进程会引发运行时错误 RuntimeError。

注意: 替代的事件循环实现可能有自己的限制；请参阅它们的文档。


