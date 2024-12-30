# 服务器模块

## 说明

客户端和服务器通过上行消息和下行消息进行数据的交换。协议采用 WebSocket。

服务端处理上行消息类似于 RPC 的方式，controller 收到消息后交给 service，service 再调用对应的函数操作 data，然后 service 会生成下行消息，交由 controller 发送出去。上行消息分为“命令”和“请求”：命令会修改数据，对应的下行消息就是更改后的数据，会广播给所有用户；请求不会修改数据，对应的下行消息就是请求的数据，只会发送给发起请求的用户。