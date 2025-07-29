# AstrBot 插件开发知识库

基于AstrBot插件开发文档整理的项目知识库

## 目录

1. [插件开发概述](#插件开发概述)
2. [插件结构](#插件结构)
3. [核心API](#核心api)
4. [事件处理](#事件处理)
5. [消息组件](#消息组件)
6. [插件配置](#插件配置)
7. [最佳实践](#最佳实践)
8. [示例代码](#示例代码)

## 插件开发概述

AstrBot是一个多平台聊天机器人框架，支持通过插件系统扩展功能。每个插件都是一个独立的Python包，可以处理消息事件、注册指令、管理配置等。

### 插件的基本特征
- 基于Python开发
- 事件驱动架构
- 支持异步编程
- 插件间相互独立
- 支持热插拔

## 插件结构

### 必需文件

1. **main.py** - 插件主逻辑文件
2. **metadata.yaml** - 插件元数据配置

### metadata.yaml 结构
```yaml
name: your_plugin_name          # 插件唯一标识名
desc: 插件描述                  # 插件简短描述
version: v1.0                   # 插件版本号 (格式: v1.1.1)
author: 作者名                  # 插件作者
repo: https://github.com/...    # 插件仓库地址 (可选)
```

### 可选文件
- **README.md** - 插件说明文档
- **requirements.txt** - Python依赖列表
- **config.yaml** - 插件配置文件

## 核心API

### 基础导入
```python
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
```

### 插件注册
使用 `@register` 装饰器注册插件类：

```python
@register("插件名", "作者", "描述", "版本", "仓库地址")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
```

### 生命周期方法

#### initialize()
```python
async def initialize(self):
    """插件初始化方法，实例化后自动调用"""
    # 插件启动时的初始化逻辑
    pass
```

#### terminate()
```python
async def terminate(self):
    """插件销毁方法，卸载/停用时调用"""
    # 清理资源、保存数据等
    pass
```

## 事件处理

### 指令过滤器

#### 基础指令
```python
@filter.command("指令名")
async def handler_name(self, event: AstrMessageEvent):
    """指令处理函数"""
    yield event.plain_result("回复内容")
```

#### 带参数的指令
```python
@filter.command("指令名", ["{参数名}"])
async def handler_with_args(self, event: AstrMessageEvent):
    """带参数的指令处理"""
    args = event.get_args()
    param_value = args.get("参数名", "默认值")
    yield event.plain_result(f"参数值: {param_value}")
```

### 消息过滤器

#### 关键词过滤
```python
@filter.keyword(["关键词1", "关键词2"])
async def keyword_handler(self, event: AstrMessageEvent):
    """关键词触发处理"""
    yield event.plain_result("检测到关键词")
```

#### 正则表达式过滤
```python
@filter.regex(r"正则表达式")
async def regex_handler(self, event: AstrMessageEvent):
    """正则匹配处理"""
    match = event.get_regex_match()
    yield event.plain_result(f"匹配结果: {match.group()}")
```

#### 前缀过滤
```python
@filter.prefix("前缀")
async def prefix_handler(self, event: AstrMessageEvent):
    """前缀匹配处理"""
    content = event.message_str[len("前缀"):].strip()
    yield event.plain_result(f"去除前缀后: {content}")
```

## 消息组件

### 获取消息信息
```python
# 获取发送者信息
user_name = event.get_sender_name()
user_id = event.get_sender_id()

# 获取消息内容
message_str = event.message_str  # 纯文本消息
message_chain = event.get_messages()  # 完整消息链

# 获取群组信息（如果是群消息）
group_id = event.get_group_id()
```

### 回复消息类型

#### 纯文本回复
```python
yield event.plain_result("文本内容")
```

#### 图片回复
```python
from astrbot.api.message_components import Image

# 本地图片
yield event.result([Image(path="/path/to/image.jpg")])

# 网络图片
yield event.result([Image(url="https://example.com/image.jpg")])

# base64图片
yield event.result([Image(base64="base64编码")])
```

#### 混合消息
```python
from astrbot.api.message_components import Plain, Image

yield event.result([
    Plain("文本部分"),
    Image(path="/path/to/image.jpg"),
    Plain("更多文本")
])
```

### 其他消息组件
```python
from astrbot.api.message_components import *

# At消息（@某人）
At(target="用户ID")

# 表情
Face(face_id=123)

# 音频
Audio(path="/path/to/audio.mp3")

# 视频
Video(path="/path/to/video.mp4")
```

## 插件配置

### 配置文件管理
```python
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = self.context.get_config()  # 获取配置对象
    
    async def initialize(self):
        # 设置默认配置
        if not self.config.get("api_key"):
            self.config.set("api_key", "")
            self.config.save()
    
    def get_api_key(self):
        return self.config.get("api_key", "")
    
    def update_config(self, key, value):
        self.config.set(key, value)
        self.config.save()
```

### 配置项类型
- 字符串: `config.get("key", "default")`
- 数字: `config.get("number", 0)`
- 布尔值: `config.get("enabled", False)`
- 列表: `config.get("list", [])`
- 字典: `config.get("dict", {})`

## 最佳实践

### 1. 错误处理
```python
@filter.command("example")
async def example_handler(self, event: AstrMessageEvent):
    try:
        # 可能出错的代码
        result = some_operation()
        yield event.plain_result(f"成功: {result}")
    except Exception as e:
        logger.error(f"处理出错: {e}")
        yield event.plain_result("处理失败，请稍后重试")
```

### 2. 异步处理
```python
import asyncio
import aiohttp

@filter.command("async_example")
async def async_handler(self, event: AstrMessageEvent):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com") as resp:
            data = await resp.json()
            yield event.plain_result(f"API响应: {data}")
```

### 3. 资源管理
```python
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.session = None
    
    async def initialize(self):
        self.session = aiohttp.ClientSession()
    
    async def terminate(self):
        if self.session:
            await self.session.close()
```

### 4. 日志记录
```python
from astrbot.api import logger

# 不同级别的日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 5. 权限检查
```python
@filter.command("admin_only")
async def admin_handler(self, event: AstrMessageEvent):
    if not event.is_admin():
        yield event.plain_result("权限不足")
        return
    
    # 管理员专用功能
    yield event.plain_result("管理员操作完成")
```

## 示例代码

### 完整插件示例
```python
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Plain, Image
from astrbot.api import logger
import random
import asyncio

@register("random_likes", "作者", "随机点赞数量插件", "1.0", "https://github.com/...")
class RandomLikesPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = self.context.get_config()
    
    async def initialize(self):
        # 设置默认配置
        default_config = {
            "min_likes": 1,
            "max_likes": 100,
            "enabled": True
        }
        
        for key, value in default_config.items():
            if not self.config.get(key):
                self.config.set(key, value)
        
        self.config.save()
        logger.info("随机点赞插件初始化完成")
    
    @filter.command("random_like")
    async def random_like(self, event: AstrMessageEvent):
        """生成随机点赞数量"""
        if not self.config.get("enabled", True):
            yield event.plain_result("插件已禁用")
            return
        
        min_val = self.config.get("min_likes", 1)
        max_val = self.config.get("max_likes", 100)
        
        likes = random.randint(min_val, max_val)
        
        yield event.plain_result(f"🎉 随机点赞数量: {likes}")
    
    @filter.command("set_range", ["{min}", "{max}"])
    async def set_range(self, event: AstrMessageEvent):
        """设置点赞数量范围"""
        args = event.get_args()
        
        try:
            min_val = int(args.get("min", 1))
            max_val = int(args.get("max", 100))
            
            if min_val >= max_val:
                yield event.plain_result("最小值必须小于最大值")
                return
            
            self.config.set("min_likes", min_val)
            self.config.set("max_likes", max_val)
            self.config.save()
            
            yield event.plain_result(f"已设置范围: {min_val} - {max_val}")
            
        except ValueError:
            yield event.plain_result("请输入有效的数字")
    
    @filter.keyword(["点赞", "👍"])
    async def keyword_like(self, event: AstrMessageEvent):
        """关键词触发点赞"""
        likes = random.randint(1, 50)
        yield event.plain_result(f"👍 +{likes}")
    
    async def terminate(self):
        logger.info("随机点赞插件已卸载")
```

### 配置管理示例
```python
# config.yaml 示例
api_settings:
  timeout: 30
  retries: 3

features:
  auto_reply: true
  debug_mode: false

user_limits:
  daily_usage: 100
  rate_limit: 10
```

## 调试技巧

### 1. 启用调试模式
```python
@filter.command("debug")
async def debug_handler(self, event: AstrMessageEvent):
    logger.debug(f"事件详情: {event}")
    logger.debug(f"消息链: {event.get_messages()}")
    logger.debug(f"发送者: {event.get_sender_id()}")
```

### 2. 测试插件功能
```python
@filter.command("test")
async def test_handler(self, event: AstrMessageEvent):
    """测试插件基本功能"""
    tests = [
        "✅ 插件加载正常",
        f"✅ 配置读取: {self.config.get('enabled')}",
        f"✅ 用户信息: {event.get_sender_name()}",
        "✅ 消息处理正常"
    ]
    
    yield event.plain_result("\n".join(tests))
```

---

*此文档基于AstrBot官方插件开发指南整理，如有更新请参考最新官方文档。*