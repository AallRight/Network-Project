# proto 消息格式模块

## 编译

```bash
protoc --python_out=. message.proto
protoc --pyi_out=. message.proto
mv message_pb2.pyi message.pyi
mv message_pb2.py message.py
cp message.proto ../static/message.proto
```

## 说明

message.proto 定义了上行和下行消息的格式，message.py 和 message.pyi 是编译出来给 python 程序调用的文件。message.proto 还要复制一份放到 static/ 路径下，让客户端能够访问。

command id 类似于 commit id，它与数据版本和更改双重绑定，它的值是从 1 开始的自然数，多个客户端和服务端本地都会存一个 command id，保证多个客户端和服务端的数据一致性。

command id 在上行消息中的作用：让服务端得知客户端是否已经收到了最新的更改。收到的 command id 应该等于本地的 command id + 1，否则报错。当然这里可以作更多的处理，因为有一些更改是可交换的。

command id 在下行消息中的作用：让客户端得知客户端发来的数据对应的 command id。如果是主动请求的数据，那么 command id 应该等于本地的 command id，否则报错；如果是更新的数据，那么 command id 应该等于本地的 command id + 1，否则报错，然后修改本地的 command_id 为 command id + 1。如果报错，那么这个下行消息无效，重新请求。
