from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random

@register("astrbot_plugin_random_likes", "--sora--", "随机点赞数量插件", "1.0", "https://github.com/sora-yyds/astrbot_plugin_random_likes")
class RandomLikesPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = self.context.get_config()

    async def initialize(self):
        """插件初始化方法，设置默认配置"""
        default_config = {
            "min_likes": 1,
            "max_likes": 100,
            "enabled": True
        }
        
        for key, value in default_config.items():
            if self.config.get(key) is None:
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
        user_name = event.get_sender_name()
        
        yield event.plain_result(f"🎉 {user_name} 获得了 {likes} 个点赞！")

    @filter.command("set_range", ["{min}", "{max}"])
    async def set_range(self, event: AstrMessageEvent):
        """设置点赞数量范围 /set_range 最小值 最大值"""
        args = event.get_args()
        
        try:
            min_val = int(args.get("min", 1))
            max_val = int(args.get("max", 100))
            
            if min_val >= max_val:
                yield event.plain_result("❌ 最小值必须小于最大值")
                return
            
            if min_val < 0:
                yield event.plain_result("❌ 最小值不能小于0")
                return
            
            self.config.set("min_likes", min_val)
            self.config.set("max_likes", max_val)
            self.config.save()
            
            yield event.plain_result(f"✅ 已设置点赞范围: {min_val} - {max_val}")
            
        except ValueError:
            yield event.plain_result("❌ 请输入有效的数字")

    @filter.regex(r".*(点赞|👍|赞).*")
    async def keyword_like(self, event: AstrMessageEvent):
        """关键词触发快速点赞"""
        if not self.config.get("enabled", True):
            return
            
        likes = random.randint(1, 50)
        yield event.plain_result(f"👍 +{likes}")

    @filter.command("like_status")
    async def like_status(self, event: AstrMessageEvent):
        """查看插件状态和配置"""
        min_val = self.config.get("min_likes", 1)
        max_val = self.config.get("max_likes", 100)
        enabled = self.config.get("enabled", True)
        
        status = "启用" if enabled else "禁用"
        
        status_msg = f"""
📊 随机点赞插件状态

状态: {status}
点赞范围: {min_val} - {max_val}

可用指令:
• /random_like - 生成随机点赞
• /set_range 最小值 最大值 - 设置范围
• /like_status - 查看状态
• 发送包含"点赞"、"👍"、"赞"的消息触发快速点赞
        """.strip()
        
        yield event.plain_result(status_msg)

    async def terminate(self):
        """插件销毁方法"""
        logger.info("随机点赞插件已卸载")
