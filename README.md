# K-song allright


## 目录树预设（可忽略）
这部分只是一个参考，具体文件夹和内容可以忽略，可以当作一个全览
<br>
具体内容请参见下面几个标题的内容
```
k-song-server/
├── app/                      # 核心业务逻辑目录
│   ├── controllers/          # 控制器层，处理请求并调用服务
│   │   ├── authController.js
│   │   ├── userController.js
│   │   └── songController.js
│   ├── services/             # 服务层，处理业务逻辑
│   │   ├── authService.js
│   │   ├── userService.js
│   │   └── songService.js
│   ├── models/               # 数据模型（如数据库表结构）
│   │   ├── userModel.js
│   │   ├── songModel.js
│   │   └── sessionModel.js
│   └── middlewares/          # 中间件目录
│       ├── authMiddleware.js
│       └── errorHandler.js
├── config/                   # 配置文件目录
│   ├── database.js           # 数据库配置
│   ├── server.js             # 服务器配置
│   └── auth.js               # 身份验证配置
├── routes/                   # 路由目录
│   ├── authRoutes.js         # 身份验证相关路由
│   ├── userRoutes.js         # 用户相关路由
│   └── songRoutes.js         # 歌曲相关路由
├── utils/                    # 工具函数目录
│   ├── logger.js             # 日志工具
│   ├── fileUploader.js       # 文件上传工具
│   └── audioProcessor.js     # 音频处理工具
├── tests/                    # 测试目录
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── e2e/                  # 端到端测试
├── public/                   # 公共文件目录（静态资源）
│   ├── uploads/              # 上传的用户文件（如音频）
│   └── images/               # 用户头像等图片文件
├── scripts/                  # 脚本目录（如自动化任务）
│   ├── migrate.js            # 数据库迁移脚本
│   └── seed.js               # 测试数据填充脚本
├── .env                      # 环境变量配置文件
├── .gitignore                # Git 忽略规则
├── package.json              # 项目描述文件，包含依赖
├── server.js                 # 服务器入口文件
└── README.md                 # 项目说明文档
```


## 代码目录逻辑
`.\database-api`是代码模块，存放代码模块
`.\data\music_file`