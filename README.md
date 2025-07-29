# AstrBot Random Likes Plugin

AstrBot 随机点赞数量插件

一个用于生成随机点赞数量的AstrBot插件，同时包含完整的插件开发知识库。

## 功能特性

- 🎲 生成随机点赞数量
- ⚙️ 可配置数量范围
- 📚 完整的插件开发知识库
- 🎯 关键词触发功能
- 💾 配置持久化
- ❤️ **真实QQ点赞功能** (需要好友关系)

## 指令列表

- `/random_like` - 生成随机点赞数量(尝试真实点赞)
- `/set_range {min} {max}` - 设置点赞数量范围
- `/test_like {count}` - 测试点赞功能(1-10次)
- `/like_status` - 查看插件状态
- 消息中包含 "点赞"、"👍" 或 "赞" - 快速点赞

## 项目结构

```
├── main.py           # 插件主逻辑
├── metadata.yaml     # 插件元数据
├── document.md       # 插件开发知识库
├── README.md         # 项目说明
└── LICENSE          # 许可证文件
```

## 开发文档

详细的AstrBot插件开发知识库请查看 [document.md](./document.md)，包含：

- 插件开发概述
- 核心API使用
- 事件处理机制
- 消息组件详解
- 配置管理
- 最佳实践
- 完整示例代码

## 安装使用

1. 将插件文件夹放入AstrBot的plugins目录
2. 重启AstrBot或使用插件管理功能加载插件
3. 发送 `/random_like` 测试插件功能

## 注意事项

### 真实点赞功能
- 仅支持QQ平台 (aiocqhttp/OneBot)
- 需要机器人与用户建立好友关系
- QQ限制每日最多给同一用户点赞10次
- 如果点赞失败会自动降级为模拟点赞

### 配置说明

插件支持以下配置项：

```yaml
min_likes: 1        # 最小点赞数
max_likes: 10       # 最大点赞数  
enabled: true       # 是否启用插件
```

## 支持

- [AstrBot官方文档](https://astrbot.app)
- [插件开发指南](./document.md)
- [问题反馈](https://github.com/sora-yyds/astrbot_plugin_random_likes/issues)
