# Streams

**Streams** high-level 原生支持 async/await 处理网络连接. 使用 **callbacks or low-level protocols and transports** 接受/发送数据

## Stream Functions

### asyncio.open_connection

`coroutine asyncio.open_connection(host=None, port=None, *, loop=None, limit=None, ssl=None, family=0, proto=0, flags=0, sock=None, local_addr=None, server_hostname=None, ssl_handshake_timeout=None)` => (StreamReader, StreamWriter)

建立网络连接，返回 (StreamReader, StreamWriter) .


### asyncio.start_server

`coroutine asyncio.start_server(client_connected_cb, host=None, port=None, *, loop=None, limit=None, family=socket.AF_UNSPEC, flags=socket.AI_PASSIVE, sock=None, backlog=100, ssl=None, reuse_address=None, reuse_port=None, ssl_handshake_timeout=None, start_serving=True)`

Start a socket server.

## Unix Sockets 

**socket** 通信有以下二种,

1. **Internet domain socket** 基于网络协议栈的，是网络中不同主机之间的通讯，需要明确IP和端口。
2. **unix domain socket** 同一台主机内不同应用不同进程间的通讯，不需要基于网络协议，不需要打包拆包、计算校验和、维护序号和应答等，
	只是将应用层数据从一个进程拷贝到另一个进程，主要是基于文件系统的，它可以用于同一台主机上两个没有亲缘关系的进程，并且是全双工的，
	提供可靠消息传递（消息不丢失、不重复、不错乱）的IPC机制，效率会远高于tcp短连接。
	与Internet domain socket类似，需要知道是基于哪一个文件（相同的文件路径）来通信的。

unix domain socket有2种工作模式一种是SOCK_STREAM，类似于TCP，可靠的字节流。另一种是SOCK_DGRAM，类似于UDP，不可靠的字节流。

### asyncio.open_unix_connection

`coroutine asyncio.open_unix_connection(path=None, *, loop=None, limit=None, ssl=None, sock=None, server_hostname=None, ssl_handshake_timeout=None)`

Establish a Unix socket connection and return a pair of (reader, writer).

### asyncio.start_unix_server

`coroutine asyncio.start_unix_server(client_connected_cb, path=None, *, loop=None, limit=None, sock=None, backlog=100, ssl=None, ssl_handshake_timeout=None, start_serving=True)`

Start a Unix socket server.

## StreamReader

### `class asyncio.StreamReader`

Represents a reader object that provides APIs to read data from the IO stream.

It is not recommended to instantiate StreamReader objects directly; use `open_connection()` and `start_server()` instead.

#### `coroutine read(n=-1)`

Read up to n bytes. If n is not provided, or set to -1, read until EOF and return all read bytes.

If EOF was received and the internal buffer is empty, return an empty bytes object.

#### `coroutine readline()`

Read one line, where “line” is a sequence of bytes ending with `\n`.

If EOF is received and `\n` was not found, the method returns partially read data.

If EOF is received and the internal buffer is empty, return an empty bytes object.

#### `coroutine readexactly(n)`

Read exactly n bytes.

Raise an IncompleteReadError if EOF is reached before n can be read. Use the IncompleteReadError.partial attribute to get the partially read data.

#### `coroutine readuntil(separator=b'\n')`

Read data from the stream until separator is found.

On success, the data and separator will be removed from the internal buffer (consumed). Returned data will include the separator at the end.

If the amount of data read exceeds the configured stream limit, a LimitOverrunError exception is raised, and the data is left in the internal buffer and can be read again.

If EOF is reached before the complete separator is found, an IncompleteReadError exception is raised, and the internal buffer is reset. The IncompleteReadError.partial attribute may contain a portion of the separator.

#### `at_eof()`

Return True if the buffer is empty and feed_eof() was called.

## StreamWriter

### `class asyncio.StreamWriter`

Represents a writer object that provides APIs to write data to the IO stream.

It is not recommended to instantiate StreamWriter objects directly; use open_connection() and start_server() instead.

#### `write(data)`

The method attempts to write the data to the underlying socket immediately. If that fails, the data is queued in an internal write buffer until it can be sent.

The method should be used along with the drain() method:

```python
stream.write(data)
await stream.drain()
```

#### `writelines(data)`

The method writes a list (or any iterable) of bytes to the underlying socket immediately. If that fails, the data is queued in an internal write buffer until it can be sent.

The method should be used along with the drain() method:

```python
stream.writelines(lines)
await stream.drain()
```

#### `close()`

The method closes the stream and the underlying socket.

The method should be used along with the wait_closed() method:

```python
stream.close()
await stream.wait_closed()
```

#### `can_write_eof()`

Return True if the underlying transport supports the write_eof() method, False otherwise.

#### `write_eof()`

Close the write end of the stream after the buffered write data is flushed.

#### `transport`

Return the underlying asyncio transport.

#### `get_extra_info(name, default=None)`

Access optional transport information; see BaseTransport.get_extra_info() for details.

#### `coroutine drain()`

Wait until it is appropriate to resume writing to the stream. Example:

```python
writer.write(data)
await writer.drain()
```

This is a flow control method that interacts with the underlying IO write buffer. 
When the size of the buffer reaches the high watermark, drain() blocks until the size of the buffer is drained down to the low watermark and writing can be resumed. 
When there is nothing to wait for, the drain() returns immediately.

#### `is_closing()`

Return True if the stream is closed or in the process of being closed.

#### `coroutine wait_closed()`

Wait until the stream is closed. Should be called after close() to wait until the underlying connection is closed.
