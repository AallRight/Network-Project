API接口使用方法
===

## 导入接口方式
首先import的方式为
```py
import os 
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = os.path.join(current_dir, "database_api")
sys.path.append(current_dir)
import database_api.database_top_api 
```

将database_api的目录导入sys.path下即可开始使用

demo见`api_test_example.py`文件