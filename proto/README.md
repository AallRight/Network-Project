# protobuf 消息格式模块

## 测试

Python:

```bash
protoc --python_out=. client_command.proto
python test.py
```

Native JS:

```bash
python -m http.server 5004
```

浏览器打开 http://localhost:5004/test.html，控制台检查输出