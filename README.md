# AstrBot Random Likes Plugin

AstrBot 随机点赞数量插件

一个用于生成随机点赞数量的AstrBot插件

## 功能特性

- 🎯 智能关键词检测点赞
- ⚙️ 可配置点赞数量范围
- 📚 完整的插件开发知识库
- 💾 配置持久化
- ❤️ **QQ点赞功能** (需要好友关系)
- 📅 **每日点赞限制** (每人每天只能点赞一次)
- 📊 **点赞统计功能** (查看今日和历史数据)

## 指令列表

- `/设置点赞范围 {min} {max}` - 设置点赞数量范围 **(仅管理员)**
- `/点赞状态` - 查看插件状态
- `/点赞统计` - 查看点赞统计信息
- 消息中包含 "点赞" - 自动触发点赞功能

## 项目结构

```
astrbot_plugin_random_likes/
├── main.py                # 插件主逻辑
├── metadata.yaml          # 插件元数据
├── config.example.yaml    # 配置示例文件
├── document.md            # 插件开发知识库
├── README.md              # 项目说明
├── requirements.txt       # 依赖列表
├── LICENSE               # 许可证文件
└── .gitignore            # Git忽略文件

plugin_data/astrbot_plugin_random_likes/  (自动创建)
├── plugin_config.json    # 插件配置文件
└── like_records.json     # 点赞记录文件
```

## 安装使用

1. 将插件文件夹放入AstrBot的plugins目录
2. 重启AstrBot或使用插件管理功能加载插件
3. 插件会自动在 `plugin_data/astrbot_plugin_random_likes/` 目录创建配置和数据文件
4. 发送 "点赞" 或使用 `/点赞状态` 测试插件功能

## 文件存储说明

### 数据文件位置
- **配置文件**: `plugin_data/astrbot_plugin_random_likes/plugin_config.json`
- **点赞记录**: `plugin_data/astrbot_plugin_random_likes/like_records.json`
- **优势**: 插件更新时不会丢失配置和数据

### 配置系统
- **优先级**: 优先使用 AstrBot 的配置系统
- **备用方案**: 配置系统不可用时自动使用本地配置文件
- **自动创建**: 所有必要的目录和文件都会自动创建

## 注意事项

### 点赞限制机制
- **每日限制**: 每个用户每天只能点赞一次
- **自动记录**: 插件会自动记录每个用户的点赞状态
- **智能提示**: 重复请求时会友好提示"今天已经点过赞了"
- **数据清理**: 自动清理7天前的历史记录，节省存储空间

### 点赞功能
- 仅支持QQ平台 (aiocqhttp/OneBot)
- 需要机器人与用户建立好友关系
- QQ限制每日最多给同一用户点赞10次
- 如果点赞失败会直接提示失败信息

### 配置说明

插件支持以下配置项：

```yaml
min_likes: 1        # 最小点赞数
max_likes: 10       # 最大点赞数  
enabled: true       # 是否启用插件
```

### 权限管理
- **管理员指令**: `/设置点赞范围` 指令仅限管理员使用
- **权限检查**: 插件会自动从AstrBot配置中获取管理员列表
- **安全保护**: 防止普通用户随意修改插件配置

## 支持

- [AstrBot官方文档](https://docs.astrbot.app/)
- [问题反馈](https://github.com/sora-yyds/astrbot_plugin_random_likes/issues)

